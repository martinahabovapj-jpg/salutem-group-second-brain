# -*- coding: utf-8 -*-
"""Doplni zemi CZ tam, kde ji subjekt nema, ale ma overitelne ceske ICO.

PROC
Bez vyplnene zeme beh nevi, ktereho registru se zeptat, a subjekt v rejstriku
nekontroluje vubec - nepozna zanik, insolvenci ani likvidaci. Hlida mu jen web.
Pribytkem investoru ze seznamu CNB takovych radku naskocilo pres ctyricet.

NA CEM TO STOJI
Osmimistne ICO je ceske identifikacni cislo. Skript si ho navic OVERI proti
ARESu a zemi zapise, jen kdyz ARES subjekt pod tim cislem opravdu vede.
Nehada se: kde ICO neni nebo ho ARES nezna, zeme zustane prazdna a rekne se to.

Do listu 4 se ke kazdemu zapisu ulozi citace a odkaz na ARES, stejne jako
u vseho ostatniho v tehle databazi.

POUZITI
    python doplnit-zeme.py            # jen vypise, co by udelal
    python doplnit-zeme.py --zapis
"""
import argparse, importlib.util, io, json, os, re, ssl, sys, time, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "financovani-beh.config.json")
TEXTY = os.path.join(HERE, "doplnit-zeme.texty.json")
ARES = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/%s"


def main():
    ap = argparse.ArgumentParser(description="Doplni zemi CZ podle overeneho ceskeho ICO")
    ap.add_argument("--zapis", action="store_true")
    ap.add_argument("--master", help="jina cesta k sesitu (test)")
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location(
        "financovani_beh", os.path.join(HERE, "financovani-beh.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cfg = json.load(io.open(CONFIG, encoding="utf-8"))
    T = json.load(io.open(TEXTY, encoding="utf-8"))
    m.T.update(cfg["texty"])
    if args.master:
        cfg["master"] = args.master
    sesit = m.Sesit(cfg)

    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    ua = cfg["sit"]["user_agent"]

    vyrazen = cfg["stavy"]["vyrazen"]
    i_zeme = sesit.sl("subjekty", "zeme")
    if not i_zeme:
        raise SystemExit("V listu 1 chybi sloupec Zeme.")

    kandidati, bez_ica = [], []
    for r, d in sesit.radky("subjekty"):
        if m.norm(d.get("stav")) == vyrazen or m.norm(d.get("zeme")):
            continue
        ico = re.search(r"\b(\d{8})\b", str(d.get("ico") or ""))
        if ico:
            kandidati.append((r, m.norm(d.get("id")), m.norm(d.get("nazev")), ico.group(1)))
        else:
            bez_ica.append((m.norm(d.get("id")), m.norm(d.get("nazev"))))

    m.vypis("Aktivnich radku bez zeme: %d" % (len(kandidati) + len(bez_ica)))
    m.vypis("  s osmimistnym ICO (da se overit): %d" % len(kandidati))
    m.vypis("  bez ICO (zeme zustane prazdna):   %d" % len(bez_ica))
    m.vypis("")

    potvrzeno, nezname = [], []
    for radek, sid, nazev, ico in kandidati:
        try:
            req = urllib.request.Request(ARES % ico, headers={
                "Accept": "application/json", "User-Agent": ua})
            det = json.load(urllib.request.urlopen(req, timeout=25, context=ctx))
        except Exception:
            det = None
        if det and m.norm(det.get("obchodniJmeno")):
            potvrzeno.append((radek, sid, nazev, ico, m.norm(det.get("obchodniJmeno"))))
            m.vypis("  #%-5s %-42s OK  %s  %s" % (sid, nazev[:42], ico,
                                                  m.norm(det.get("obchodniJmeno"))[:32]))
        else:
            nezname.append((sid, nazev, ico))
            m.vypis("  #%-5s %-42s -- ARES ICO %s nezna" % (sid, nazev[:42], ico))
        time.sleep(0.15)

    m.vypis("")
    m.vypis("=" * 68)
    m.vypis("  POTVRZENO ARESem (zapise se CZ): %d" % len(potvrzeno))
    m.vypis("  ARES ICO nezna (nechavam):       %d" % len(nezname))
    m.vypis("  bez ICO (nechavam):              %d" % len(bez_ica))
    m.vypis("=" * 68)
    if bez_ica:
        m.vypis("Bez ICO, tedy i bez zeme - tyhle beh dal preskakuje:")
        for sid, nazev in bez_ica:
            m.vypis("  #%-5s %s" % (sid, nazev[:60]))

    if not args.zapis:
        m.vypis("")
        m.vypis("Nic nezapsano. Pro zapis pridej --zapis")
        return

    ws = sesit.ws("subjekty")
    for radek, sid, nazev, ico, ares_nazev in potvrzeno:
        zdroj = T["ares_url"].format(ico=ico)
        ws.cell(row=radek, column=i_zeme).value = "CZ"
        m.pripis_poznamku(sesit, radek, T["zeme_doplneno"].format(
            datum=m.DNES, ico=ico, nazev=ares_nazev, zdroj=zdroj))
        m.zapis_zdroj(sesit, sid, nazev, T["pole_zeme"],
                      T["zeme_citace"].format(ico=ico, nazev=ares_nazev), zdroj)
    sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
    m.vypis("Zapsana zeme CZ u %d subjektu." % len(potvrzeno))


if __name__ == "__main__":
    main()
