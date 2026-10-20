# -*- coding: utf-8 -*-
"""Uplny vypis hlidaneho zdroje - soubor po souboru.

Proc to existuje: sync-zdroju.py hlida PRIRUSTKY. Soubor, ktery se nikdy
nezmenil, se v nem neobjevi nikdy. Doloženo 9. 9. 2026 na Alfe: cela slozka
'12 AI Roadmapa' je ze 16. 6. 2026 a devet syncu ji minulo, protoze se od te
doby nezmenila. Lezel v ni souhrnny service dokument, definice vsech tri
vetvi sluzby a tri otevrena compliance rozhodnuti.

Pravidlo: raz za kvartal projit hlidany zdroj CELY timhle skriptem
a porovnat s logem vytezeni.

Pouziti:
    python inventura.py                        # Alfa (vychozi)
    python inventura.py --zdroj "Podklady"     # jiny zdroj z konfigurace
    python inventura.py --cesta "C:\\..."      # libovolna cesta
    python inventura.py --od 2026-06-01        # jen soubory zmenene od data
    python inventura.py --slozky               # jen souhrn po slozkach

Dlouhe cesty: kazda cesta jde pres prefix \\\\?\\, protoze ve firemnich
slozkach se prekracuje limit 260 znaku. Necitelny soubor se VYPISE,
nikdy nepreskoci - hlidac, ktery vrati mene a nic nerekne, je horsi
nez hlidac, ktery spadne.
"""
import argparse
import collections
import datetime
import io
import json
import os
import re
import sys

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")

ZDE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(ZDE, "sync-zdroju.config.json")

IGNORE_NAMES = {"desktop.ini", "Thumbs.db", ".DS_Store"}


def dlouha_cesta(p):
    r"""Prefix \\?\ obchazi limit MAX_PATH. Bez toho os.stat na hlubokych
    slozkach selze a soubor se tvari jako neexistujici."""
    p = os.path.abspath(p)
    if p.startswith("\\\\?\\"):
        return p
    if p.startswith("\\\\"):
        return "\\\\?\\UNC" + p[1:]
    return "\\\\?\\" + p


def nacti_zdroj(nazev):
    with io.open(CONFIG, encoding="utf-8") as f:
        cfg = json.load(f)
    zdroje = cfg["zdroje"]
    for k, v in zdroje.items():
        if k.lower().startswith(nazev.lower()):
            return k, v
    print("Zdroj '%s' v konfiguraci neni. Mam: %s" % (nazev, ", ".join(zdroje)))
    sys.exit(1)


def projdi(root, ignorovat=None):
    ignorovat = [i.replace("/", os.sep).rstrip(os.sep).lower() for i in (ignorovat or [])]
    prefix = dlouha_cesta(root)
    radky, nectene = [], []
    for dirpath, dirnames, filenames in os.walk(prefix):
        dirnames.sort()
        rel_dir = os.path.relpath(dirpath, prefix)
        if ignorovat and rel_dir != ".":
            low = rel_dir.lower()
            if any(low == i or low.startswith(i + os.sep) for i in ignorovat):
                dirnames[:] = []
                continue
        for fn in sorted(filenames):
            if fn in IGNORE_NAMES or fn.startswith("~$"):
                continue
            full = os.path.join(dirpath, fn)
            rel = os.path.relpath(full, prefix)
            try:
                st = os.stat(full)
            except OSError as e:
                nectene.append((rel, str(e)))
                continue
            radky.append((rel, datetime.datetime.fromtimestamp(st.st_mtime), st.st_size))
    return radky, nectene


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--zdroj", default="Alfa", help="nazev zdroje z konfigurace")
    ap.add_argument("--cesta", default=None, help="cesta misto zdroje z konfigurace")
    ap.add_argument("--od", default=None, help="jen soubory zmenene od data RRRR-MM-DD")
    ap.add_argument("--slozky", action="store_true", help="jen souhrn po slozkach prvni urovne")
    a = ap.parse_args()

    if a.cesta:
        nazev, root, ignorovat = a.cesta, a.cesta, None
    else:
        nazev, cfg = nacti_zdroj(a.zdroj)
        root, ignorovat = cfg["cesta"], cfg.get("ignorovat")

    if not os.path.isdir(dlouha_cesta(root)):
        print("Cesta neexistuje: %s" % root)
        sys.exit(1)

    radky, nectene = projdi(root, ignorovat)

    od = None
    if a.od:
        od = datetime.datetime.strptime(a.od, "%Y-%m-%d")
        radky = [r for r in radky if r[1] >= od]

    print("ZDROJ: %s" % nazev)
    print("CESTA: %s" % root)
    print("SOUBORU: %d%s" % (len(radky), (" (od %s)" % a.od) if a.od else ""))
    print("NECITELNYCH: %d" % len(nectene))
    for rel, err in nectene:
        print("  !! nelze precist: %s  (%s)" % (rel, err))
    print()

    if a.slozky:
        souhrn = collections.Counter()
        nejnovejsi = {}
        for rel, mtime, _ in radky:
            top = rel.split(os.sep)[0] if os.sep in rel else "(koren)"
            souhrn[top] += 1
            if top not in nejnovejsi or mtime > nejnovejsi[top]:
                nejnovejsi[top] = mtime
        for top in sorted(souhrn):
            print("%-62s %4d  posledni zmena %s" % (
                top[:62], souhrn[top], nejnovejsi[top].strftime("%Y-%m-%d")))
        return

    for rel, mtime, size in radky:
        print("%s | %9d | %s" % (mtime.strftime("%Y-%m-%d"), size, rel))

    # Fazove slozky se v Alfe jmenuji sedmi zpusoby (30 Realizace, Realizace,
    # 30 Etapa 3 - Realizace, 20_Realizace, 30_ Realizace, 20_ Realizace).
    # Proto se hleda regularnim vyrazem na slovo, ne presnym nazvem.
    faze = collections.Counter()
    for rel, _, _ in radky:
        parts = rel.split(os.sep)
        if len(parts) >= 2 and re.search(r"realizace", parts[1], re.I):
            faze[(parts[0], parts[1])] += 1
    if faze:
        print("\nFAZE 'REALIZACE' (regularnim vyrazem, ne presnym nazvem):")
        for (proj, slozka), n in sorted(faze.items()):
            print("  %-52s %-24s %d" % (proj[:52], slozka, n))


if __name__ == "__main__":
    main()
