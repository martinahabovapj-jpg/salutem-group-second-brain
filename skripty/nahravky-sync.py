# -*- coding: utf-8 -*-
"""
nahravky-sync.py — z nahravek schuzek udela prepisy a rekne, co jeste chybi.

Proc existuje: nahravky schuzek v OneDrive/Nahravky maji dve podoby.
  * "...-Zaznam schuzky.mp4"  = skutecna nahravka se zvukem -> prepis umime
                                udelat lokalne (Whisper), bez cloudu.
  * "...-Prepis schuzky.mp4"  = cerny placeholder BEZ zvuku (v Teams se
                                zapnul jen prepis, ne nahravani). Text prepisu
                                existuje jen v Teams/Streamu a musi se stahnout
                                rucne jako .docx. Lokalne z nej nic nedostaneme.

Teams navic nahravky po ~120 dnech maze i s prepisem. Co se do te doby
nestahne, je nenavratne pryc — proto skript hlasi i blizici se expiraci.

Pouziti:
    python nahravky-sync.py                 # report, nic nemeni
    python nahravky-sync.py --prepis        # + prepise nove zaznamy Whisperem
    python nahravky-sync.py --prepis --limit 2   # nejvys 2 prepisy za beh
    python nahravky-sync.py --model small   # rychleji, mene presne

Stav si drzi v nahravky-sync.stav.json (ktere mp4 uz jsou vyresene a jak).
Report zapisuje do prepisy/_nove-k-vytezeni.md. Soubor _prehled.md needituje —
to je rucni mapa vyteizeni a patri do ni az vysledek vytezeni.
"""

import argparse
import datetime as dt
import difflib
import json
import os
import re
import subprocess
import sys
import unicodedata
import urllib.parse

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "nahravky-sync.config.json")
STATE = os.path.join(HERE, "nahravky-sync.stav.json")
REPORT_NAME = "_nove-k-vytezeni.md"

PREPIS_EXT = (".docx", ".md", ".txt", ".pdf")


# ---------------------------------------------------------------- pomocne

def load_json(path, default):
    if not os.path.isfile(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def norm(s):
    """Nazev na porovnatelnou podobu: bez diakritiky, bez interpunkce."""
    s = unicodedata.normalize("NFKD", s.lower())
    s = "".join(c for c in s if not unicodedata.combining(c))
    return " ".join(re.sub(r"[^a-z0-9]+", " ", s).split())


def parse_nazev(name):
    """'Tema-20260806_132908-Zaznam schuzky.mp4' -> (tema, datetime, druh)."""
    stem = os.path.splitext(name)[0]
    m = re.search(r"^(.*?)-(\d{8})_(\d{6})-(\w+) schůzky$", stem)
    if not m:
        return stem, None, "?"
    tema, d, t, druh = m.group(1), m.group(2), m.group(3), m.group(4)
    try:
        kdy = dt.datetime(int(d[:4]), int(d[4:6]), int(d[6:8]),
                          int(t[:2]), int(t[2:4]), int(t[4:6]))
    except ValueError:
        kdy = None
    if druh.startswith("Z"):
        kind = "zaznam"
    elif druh.startswith("P"):
        kind = "placeholder"
    else:
        kind = "?"
    return tema, kdy, kind


def delka_minut(path):
    """Delka mp4 z atomu moov/mvhd. None, kdyz to nejde precist."""
    import struct

    def atoms(f, end):
        while f.tell() + 8 <= end:
            start = f.tell()
            hdr = f.read(8)
            if len(hdr) < 8:
                return
            size = struct.unpack(">I", hdr[:4])[0]
            typ = hdr[4:8].decode("latin-1")
            hs = 8
            if size == 1:
                size = struct.unpack(">Q", f.read(8))[0]
                hs = 16
            elif size == 0:
                size = end - start
            if size < hs:
                return
            yield typ, start + hs, start + size
            f.seek(start + size)

    try:
        fsize = os.path.getsize(path)
        with open(path, "rb") as f:
            for typ, ps, pe in atoms(f, fsize):
                if typ != "moov":
                    continue
                f.seek(ps)
                for t2, p2s, p2e in atoms(f, pe):
                    if t2 != "mvhd":
                        continue
                    f.seek(p2s)
                    d = f.read(p2e - p2s)
                    if d[0] == 1:
                        ts = struct.unpack(">I", d[20:24])[0]
                        du = struct.unpack(">Q", d[24:32])[0]
                    else:
                        ts = struct.unpack(">I", d[12:16])[0]
                        du = struct.unpack(">I", d[16:20])[0]
                    return (du / ts / 60.0) if ts else None
    except (OSError, IndexError, struct.error):
        return None
    return None


def existujici_prepisy(prepisy_dir):
    """[(normalizovany nazev, soubor)] vsech prepisu vcetne podslozek."""
    out = []
    for root, _dirs, files in os.walk(prepisy_dir):
        for f in files:
            if f.startswith(("_", "~$")):
                continue
            if os.path.splitext(f)[1].lower() in PREPIS_EXT:
                out.append((norm(os.path.splitext(f)[0]), f))
    return out


def skore(tema, ne):
    nt = norm(tema)
    r = difflib.SequenceMatcher(None, nt, ne).ratio()
    if nt and len(nt) > 8 and (nt in ne or ne in nt):
        r = max(r, 0.90)
    return r


def sparuj(schuzky, existing, prah=0.86):
    """Priradi kazde schuzce nejvys jeden existujici prepis (1:1).

    Duvod pro 1:1: opakujici se schuzky maji stejny nazev a lisi se jen datem
    ("Projekt Alfa" 4x, "Hovor s Petr Suchy" 4x). Kdyby jeden .docx mohl
    pokryt vic nahravek, chybejici prepisy by se schovaly za ten jediny,
    ktery existuje. Datum v nazvu .docx neni, takze nevime KTERA schuzka je
    pokryta — ale kolik jich pokryto neni, vime spolehlive.

    Vraci {klic schuzky: nazev prepisu}.
    """
    pary = []
    for key, s in schuzky.items():
        for ne, orig in existing:
            r = skore(s["tema"], ne)
            if r >= prah:
                pary.append((r, key, orig))
    pary.sort(key=lambda p: -p[0])

    prirazeno, obsazene = {}, set()
    for r, key, orig in pary:
        if key in prirazeno or orig in obsazene:
            continue
        prirazeno[key] = orig
        obsazene.add(orig)
    return prirazeno


# ---------------------------------------------------------------- prepis

def prepis_whisper(src, outdir, model_name):
    """Prepise jeden mp4. Vraci cestu k .txt nebo None."""
    try:
        import imageio_ffmpeg
        from faster_whisper import WhisperModel
    except ImportError as e:
        print("     CHYBI knihovna (%s). Nainstaluj:" % e)
        print("     python -m pip install faster-whisper imageio-ffmpeg")
        return None

    import tempfile
    import time

    os.makedirs(outdir, exist_ok=True)
    base = os.path.splitext(os.path.basename(src))[0]
    out_txt = os.path.join(outdir, base + ".txt")
    wav = os.path.join(tempfile.gettempdir(), "nahr_%d.wav" % os.getpid())

    t0 = time.time()
    ff = imageio_ffmpeg.get_ffmpeg_exe()
    rc = subprocess.call([ff, "-y", "-loglevel", "error", "-i", src,
                          "-vn", "-ac", "1", "-ar", "16000",
                          "-c:a", "pcm_s16le", wav])
    if rc != 0 or not os.path.exists(wav):
        print("     nepodarilo se vytahnout zvuk (rc=%d)" % rc)
        return None

    model = WhisperModel(model_name, device="cpu", compute_type="int8")
    segments, _info = model.transcribe(
        wav, language="cs", vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=700),
        beam_size=5, condition_on_previous_text=False,
    )

    n = 0
    with open(out_txt, "w", encoding="utf-8") as fh:
        fh.write("# %s\n\n" % base)
        fh.write("> Automaticky prepis (Whisper %s), neopraveny. "
                 "Jmena, cisla a nazvy nastroju jsou casto zkomolene — "
                 "necituj je bez overeni.\n\n" % model_name)
        for seg in segments:
            m, s = divmod(int(seg.start), 60)
            fh.write("[%02d:%02d] %s\n" % (m, s, seg.text.strip()))
            n += 1
    try:
        os.remove(wav)
    except OSError:
        pass
    print("     hotovo: %d useku, %.0f min prace" % (n, (time.time() - t0) / 60))
    return out_txt


# ---------------------------------------------------------------- report

def zapis_report(path, hotove, ceka, kratke, dnes):
    lines = []
    lines.append("---")
    lines.append("oblast: Meta")
    lines.append("aktualizovano: %s" % dnes.isoformat())
    lines.append("zdroj: OneDrive/Nahrávky (automat nahravky-sync.py)")
    lines.append("---")
    lines.append("")
    lines.append("# Nové nahrávky — co čeká na vytěžení")
    lines.append("")
    lines.append("Tenhle soubor **píše skript**, needituj ho ručně. Až se něco vytěží,")
    lines.append("zapiš to do `_prehled.md` a odsud to při dalším běhu zmizí.")
    lines.append("")

    if hotove:
        lines.append("## ⬜ Přepsáno automaticky — čeká na vytěžení")
        lines.append("")
        lines.append("Přepisy leží v `auto-whisper/`. Jsou z Whisperu, tedy **zkomolené**")
        lines.append("podobně jako ty z Teams — čísla a jména ověřuj (`⚠️ neověřeno`).")
        lines.append("")
        lines.append("| Datum | Schůzka | Délka | Přepis |")
        lines.append("|---|---|---|---|")
        for r in hotove:
            lines.append("| %s | %s | %s | %s |" % (
                r["datum"], r["tema"], r["delka"], r["txt"]))
        lines.append("")
        lines.append("> Pozn.: párování s ručně stahovanými `.docx` jde podle názvu —")
        lines.append("> ten ale datum neobsahuje. U opakujících se schůzek (`Projekt Alfa`,")
        lines.append("> `30 min s AI`, `Hovor s …`) proto může být posunuté o jeden termín.")
        lines.append("> Než začneš vytěžovat, zkontroluj, že totéž už není v `_prehled.md`.")
        lines.append("")

    if ceka:
        lines.append("## ⚠️ Čeká na stažení ze Streamu (jinak se ztratí)")
        lines.append("")
        lines.append("U těchto schůzek se v Teams zapnul **jen přepis, ne nahrávání** —")
        lines.append("lokálně je prázdný placeholder bez zvuku. Text existuje jen v Teams")
        lines.append("a **s expirací nahrávky zmizí i on**.")
        lines.append("")
        lines.append("**Kde přepis hledat** (odkaz níž vede do přehrávače, ne na stažení —")
        lines.append("pokud ti prohlížeč přesto nabídne jen *Stáhnout video*, jdi cestou 2):")
        lines.append("")
        lines.append("1. **Přes odkaz:** otevřít → v přehrávači záložka/panel *Přepis*")
        lines.append("   → `...` → *Stáhnout*.")
        lines.append("2. **Přes Teams (spolehlivější):** Teams → *Kalendář* → najít schůzku")
        lines.append("   → otevřít → záložka *Přepis* nebo *Rekapitulace* → *Stáhnout*.")
        lines.append("   Přepis patří ke schůzce, ne k souboru — proto tam bývá i tehdy,")
        lines.append("   když u videa není.")
        lines.append("")
        lines.append("Stažené `.docx` ulož do `prepisy\\` (ne do podsložky). Při dalším")
        lines.append("pondělním běhu položka z tohoto seznamu zmizí sama.")
        lines.append("")
        lines.append("| Vyprší | Datum | Schůzka | Délka | Odkaz |")
        lines.append("|---|---|---|---|---|")
        for r in ceka:
            lines.append("| %s | %s | %s | %s | [otevřít](%s) |" % (
                r["vyprsi"], r["datum"], r["tema"], r["delka"], r["url"]))
        lines.append("")

    if kratke:
        lines.append("## Krátké, pravděpodobně bez obsahu")
        lines.append("")
        lines.append("Kratší než limit v configu — nejčastěji omylem spuštěné nahrávání.")
        lines.append("Evidují se, ale nedoporučuje se s nimi nic dělat.")
        lines.append("")
        for r in kratke:
            lines.append("- %s — %s (%s)" % (r["datum"], r["tema"], r["delka"]))
        lines.append("")

    if not (hotove or ceka or kratke):
        lines.append("Nic nového. Všechny nahrávky mají přepis.")
        lines.append("")

    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--prepis", action="store_true",
                    help="skutecne prepsat nove zaznamy Whisperem (jinak jen report)")
    ap.add_argument("--limit", type=int, default=0,
                    help="nejvys N prepisu za beh (0 = bez limitu)")
    ap.add_argument("--model", default=None, help="whisper model (prebije config)")
    args = ap.parse_args()

    cfg = load_json(CONFIG, None)
    if cfg is None:
        print("Chybi %s" % CONFIG)
        return 1
    state = load_json(STATE, {"vyresene": {}, "posledni_beh": None})
    vyresene = state.setdefault("vyresene", {})

    nahr = cfg["nahravky"]
    prepisy = cfg["prepisy"]
    if not os.path.isdir(nahr):
        print("Slozka s nahravkami neni dostupna: %s" % nahr)
        print("(OneDrive nemusi byt nasynchronizovany.)")
        return 1

    outdir = os.path.join(prepisy, cfg.get("auto_podslozka", "auto-whisper"))
    model_name = args.model or cfg.get("model", "medium")
    retence = int(cfg.get("retence_dnu", 120))
    varovat = int(cfg.get("varovat_dnu", 30))
    min_minut = float(cfg.get("min_minut", 5))
    dnes = dt.date.today()

    existing = existujici_prepisy(prepisy)
    mp4s = sorted(f for f in os.listdir(nahr) if f.lower().endswith(".mp4"))

    # --- 1) mp4 -> schuzky. Teams u jedne schuzky casto ulozi dva soubory
    #        (Zaznam i Prepis, casovy stopky se lisi o minuty). Naopak stejne
    #        pojmenovana schuzka dopoledne a odpoledne jsou DVE schuzky.
    #        Proto: stejne tema + odstup do TOLERANCE_MIN = jedna schuzka.
    TOLERANCE_MIN = 30
    schuzky = {}
    podle_tematu = {}
    for name in mp4s:
        podle_tematu.setdefault(norm(parse_nazev(name)[0]), []).append(name)

    for nt, jmena in podle_tematu.items():
        jmena.sort(key=lambda n: parse_nazev(n)[1] or dt.datetime.min)
        aktualni = None
        for name in jmena:
            tema, kdy, kind = parse_nazev(name)
            novy = True
            if aktualni is not None and kdy and aktualni["kdy"]:
                odstup = abs((kdy - aktualni["kdy"]).total_seconds()) / 60.0
                novy = odstup > TOLERANCE_MIN
            if novy:
                key = (nt, kdy.isoformat() if kdy else name)
                aktualni = {"tema": tema, "kdy": kdy, "datum": kdy.date() if kdy else None,
                            "soubor": name, "kind": kind, "soubory": []}
                schuzky[key] = aktualni
            aktualni["soubory"].append(name)
            # ze skupiny si drzime ten se zvukem — z nej umime prepis sami
            if kind == "zaznam" and aktualni["kind"] != "zaznam":
                aktualni["soubor"], aktualni["kind"] = name, "zaznam"

    # --- 2) 1:1 parovani s existujicimi prepisy
    prirazeno = sparuj(schuzky, existing)

    hotove, ceka, kratke = [], [], []
    k_prepisu = []
    n_pokryto = 0
    delky = state.setdefault("delky", {})

    for key in sorted(schuzky, key=lambda k: schuzky[k]["kdy"] or dt.datetime.min):
        s = schuzky[key]
        name, tema, datum, kind = s["soubor"], s["tema"], s["datum"], s["kind"]

        # uz vyresene v predchozim behu (prepsano nebo vedome preskoceno)?
        zapis = vyresene.get(name)
        if zapis and zapis.get("stav") in ("prepis-existuje", "whisper", "preskocit"):
            n_pokryto += 1
            continue

        # ma prepis (rucne stazeny .docx z Teams nebo nas .txt z Whisperu)?
        if key in prirazeno:
            vyresene[name] = {"stav": "prepis-existuje", "kam": prirazeno[key],
                              "kdy": dnes.isoformat()}
            n_pokryto += 1
            continue

        # delku cachujeme — cteni moov atomu stahuje soubor z OneDrive
        if name in delky:
            mins = delky[name]
        else:
            mins = delka_minut(os.path.join(nahr, name))
            delky[name] = mins

        delka = ("%d min" % round(mins)) if mins else "?"
        vyprsi = (datum + dt.timedelta(days=retence)).isoformat() if datum else "?"
        rec = {
            "soubor": name,
            "tema": tema,
            "datum": datum.isoformat() if datum else "?",
            "delka": delka,
            "vyprsi": vyprsi,
            "url": "%s/%s%s" % (cfg.get("stream_base", ""),
                                urllib.parse.quote(name),
                                cfg.get("stream_suffix", "")),
        }

        if mins is not None and mins < min_minut:
            kratke.append(rec)
            vyresene[name] = {"stav": "preskocit", "duvod": "kratka",
                              "kdy": dnes.isoformat()}
            continue

        if kind == "zaznam":
            k_prepisu.append(rec)
        else:
            ceka.append(rec)

    # 3) prepis zaznamu
    if args.prepis and k_prepisu:
        davka = k_prepisu[:args.limit] if args.limit else k_prepisu
        print("Prepisuji %d nahravek (model %s)...\n" % (len(davka), model_name))
        for i, rec in enumerate(davka, 1):
            print("[%d/%d] %s (%s)" % (i, len(davka), rec["tema"], rec["delka"]))
            txt = prepis_whisper(os.path.join(nahr, rec["soubor"]), outdir, model_name)
            if txt:
                rec["txt"] = os.path.join(cfg.get("auto_podslozka", "auto-whisper"),
                                          os.path.basename(txt))
                hotove.append(rec)
                vyresene[rec["soubor"]] = {"stav": "whisper", "kam": rec["txt"],
                                           "kdy": dnes.isoformat()}
        # co se do davky neveslo, zustava jako cekajici na dalsi beh
        for rec in k_prepisu[len(davka):]:
            rec["txt"] = "— čeká na další běh"
            hotove.append(rec)
    else:
        for rec in k_prepisu:
            rec["txt"] = "**ještě nepřepsáno** — spusť s `--prepis`"
            hotove.append(rec)

    ceka.sort(key=lambda r: r["vyprsi"])
    state["posledni_beh"] = dnes.isoformat()
    save_json(STATE, state)

    report = os.path.join(prepisy, REPORT_NAME)
    zapis_report(report, hotove, ceka, kratke, dnes)

    # ---- souhrn na obrazovku
    print("")
    print("Nahravek celkem: %d  |  prepis uz maji: %d" % (len(mp4s), n_pokryto))
    print("Prepsano/k prepisu (maji zvuk): %d" % len(hotove))
    print("Ceka na stazeni ze Streamu (placeholdery): %d" % len(ceka))
    print("Kratke bez obsahu: %d" % len(kratke))
    urgent = [r for r in ceka
              if r["vyprsi"] != "?"
              and dt.date.fromisoformat(r["vyprsi"]) - dnes <= dt.timedelta(days=varovat)]
    if urgent:
        print("")
        print("!! %d z nich vyprsi do %d dni — stahni je driv, jinak jsou pryc:" % (
            len(urgent), varovat))
        for r in urgent[:10]:
            print("   %s  %s" % (r["vyprsi"], r["tema"]))
    print("")
    print("Report: %s" % report)
    return 0


if __name__ == "__main__":
    sys.exit(main())
