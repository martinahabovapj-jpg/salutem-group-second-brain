# -*- coding: utf-8 -*-
"""
sync-zdroju.py — co v hlidanych zdrojich pribylo od posledniho syncu.

Pouziti:
    python sync-zdroju.py                  # co je noveho (nic nemeni)
    python sync-zdroju.py --commit         # zapise dnesni datum jako novy sync
    python sync-zdroju.py --dny 14         # rucne: co je novejsi nez 14 dni
    python sync-zdroju.py --root Alfa      # jen jeden hlidany zdroj

Stav si drzi v sousednim souboru sync-zdroju.stav.json (par radku, cteci pro
cloveka). Nedrzi seznam vsech souboru zamerne — staci datum posledniho syncu
a pocet souboru, aby se poznalo i mazani.

Konfigurace hlidanych zdroju je v sync-zdroju.config.json (aby v tomhle
skriptu nemusely byt cesty s diakritikou).
"""

import argparse
import datetime as dt
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "sync-zdroju.config.json")
STATE = os.path.join(HERE, "sync-zdroju.stav.json")

# sum, ktery nechceme videt jako "novy zdroj"
SKIP_EXT = {".tmp", ".lnk", ".ini", ".db"}
SKIP_PREFIX = ("~$", ".~")
BIG_MEDIA = {".mp4", ".mov", ".wav", ".m4a", ".mp3"}

# kolik zmen se vypise na jeden zdroj (vic = zdroj je zabrany moc siroko)
MAX_VYPIS = 40

# nad tolik zmen na jeden zdroj to skript oznaci za prilis siroky zaber
PRILIS_SIROKO = 200


def load_json(path, default):
    if not os.path.isfile(path):
        return default
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def walk(root):
    """Vrati (soubory, slozky). Soubor = (relativni cesta, mtime, velikost)."""
    files, folders = [], []
    for dirpath, dirnames, filenames in os.walk(root):
        rel_dir = os.path.relpath(dirpath, root)
        if rel_dir != ".":
            folders.append(rel_dir)
        for name in filenames:
            if name.startswith(SKIP_PREFIX):
                continue
            ext = os.path.splitext(name)[1].lower()
            if ext in SKIP_EXT:
                continue
            full = os.path.join(dirpath, name)
            try:
                st = os.stat(full)
            except OSError:
                continue
            rel = os.path.relpath(full, root)
            files.append((rel, st.st_mtime, st.st_size, ext))
    return files, folders


def fmt(ts):
    return dt.datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def report_root(name, cfg, state, dny, sirka=110):
    path = cfg["cesta"]
    if not os.path.isdir(path):
        print("  !! cesta neexistuje: %s" % path)
        return None

    st = state.get(name, {})
    if dny is not None:
        hranice = dt.datetime.now() - dt.timedelta(days=dny)
        od_popis = "poslednich %d dni" % dny
    elif st.get("posledni_sync"):
        hranice = dt.datetime.strptime(st["posledni_sync"], "%Y-%m-%d")
        od_popis = "syncu %s" % st["posledni_sync"]
    else:
        hranice = dt.datetime(2000, 1, 1)
        od_popis = "zacatku (jeste nikdy nesyncovano)"

    files, folders = walk(path)
    hranice_ts = hranice.timestamp()
    nove = [f for f in files if f[1] > hranice_ts]
    nove.sort(key=lambda f: -f[1])

    predtim = st.get("pocet_souboru")
    print("\n=== %s  (%d souboru, zmeny od %s)" % (name, len(files), od_popis))
    if predtim is not None and predtim != len(files):
        rozdil = len(files) - predtim
        print("    pocet souboru: %+d proti poslednimu syncu (bylo %d)" % (rozdil, predtim))
        if rozdil < 0:
            print("    POZOR: neco zmizelo nebo se prejmenovalo — projdi rucne")

    if not nove:
        print("    nic noveho")
    else:
        media = [f for f in nove if f[3] in BIG_MEDIA]
        obsah = [f for f in nove if f[3] not in BIG_MEDIA]
        print("    NOVE / ZMENENE: %d (z toho nahravek %d)" % (len(nove), len(media)))
        if len(nove) > PRILIS_SIROKO:
            print("    !! Zmen je pres %d — tenhle zdroj je pravdepodobne zabrany moc siroko." % PRILIS_SIROKO)
            print("       Zvaz zuzeni cesty v sync-zdroju.config.json.")
        if len(nove) > MAX_VYPIS:
            print("    (vypisuji %d nejnovejsich)" % MAX_VYPIS)
        for rel, mtime, size, ext in obsah[:MAX_VYPIS]:
            print("    %s | %8d B | %s" % (fmt(mtime), size, rel))
        zbyva = max(0, len(obsah) - MAX_VYPIS)
        if zbyva:
            print("    ... a dalsich %d souboru" % zbyva)
        for rel, mtime, size, ext in media[:10]:
            print("    %s | NAHRAVKA    | %s" % (fmt(mtime), rel))
        if len(media) > 10:
            print("    ... a dalsich %d nahravek" % (len(media) - 10))

    return {"pocet_souboru": len(files), "novych": len(nove)}


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    ap = argparse.ArgumentParser()
    ap.add_argument("--commit", action="store_true", help="zapsat dnesni datum jako novy sync")
    ap.add_argument("--dny", type=int, default=None, help="ignorovat stav a vzit poslednich N dni")
    ap.add_argument("--root", default=None, help="jen jeden hlidany zdroj (cast nazvu)")
    args = ap.parse_args()

    config = load_json(CONFIG, None)
    if config is None:
        print("Chybi %s — vytvor ho podle README ve skills/sync-zdroju." % CONFIG)
        sys.exit(1)
    state = load_json(STATE, {})

    print("SYNC ZDROJU  —  %s" % dt.datetime.now().strftime("%Y-%m-%d %H:%M"))

    vysledky = {}
    for name, cfg in config["zdroje"].items():
        if args.root and args.root.lower() not in name.lower():
            continue
        v = report_root(name, cfg, state, args.dny)
        if v:
            vysledky[name] = v

    celkem = sum(v["novych"] for v in vysledky.values())
    print("\n--- souhrn: %d novych nebo zmenenych souboru napric %d zdroji" % (celkem, len(vysledky)))

    if args.commit:
        dnes = dt.date.today().isoformat()
        for name, v in vysledky.items():
            state[name] = {"posledni_sync": dnes, "pocet_souboru": v["pocet_souboru"]}
        save_json(STATE, state)
        print("--- zapsano do %s (posledni_sync = %s)" % (os.path.basename(STATE), dnes))
    else:
        print("--- stav NEZMENEN. Az bude vytezeno, spust znovu s --commit")


if __name__ == "__main__":
    main()
