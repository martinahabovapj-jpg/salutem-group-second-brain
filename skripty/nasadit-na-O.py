# -*- coding: utf-8 -*-
"""
nasadit-na-O.py - prenese upravenou verzi behu z repa na disk O:.

Spousti Martina Habova, ne kolega. Kopiruje se JEN JEDNIM SMEREM: repo -> O:.
Nikdy opacne - jinak vzniknou dve ruzne verze skriptu a nikdo nepozna, ktera
plati. Presne to, co se stalo master sesitu.

Cilova slozka se NEZADAVA - odvodi se z cesty k masteru v konfiguraci.
Diky tomu je cesta na jednom miste a v .cmd souboru nemusi byt diakritika.

Zamerne se NEKOPIRUJE:
    financovani-beh.stav.json     pamet mezi behy - patri k datum na O:
    stranky/ zalohy/ k-precteni/  provozni slozky, vznikaji za behu
"""

import hashlib
import io
import json
import os
import shutil
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "financovani-beh.config.json")

DO_BEHU = ["financovani-beh.py", "financovani-beh.config.json",
           "financovani-objevy.py", "financovani-objevy.zadani.md",
           "kontrola-prostredi.py", "kontrola-prostredi.texty.json",
           "KONTROLA.cmd", "refresh.cmd", "ZAPSAT.cmd", "OBJEVY.cmd"]
VEDLE_MASTERU = ["ZACNI-TADY.md"]


def vypis(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def otisk(cesta):
    with open(cesta, "rb") as f:
        return hashlib.sha256(f.read()).hexdigest()


def main():
    with io.open(CONFIG, "r", encoding="utf-8-sig") as f:
        cfg = json.load(f)
    master = cfg["master"]
    cil = os.path.dirname(master)
    cil_beh = os.path.join(cil, "beh")

    if not os.path.isdir(cil):
        vypis("")
        vypis("  Cilova slozka neexistuje - je disk O: pripojeny?")
        vypis("  %s" % cil)
        vypis("")
        return 1

    if not os.path.isdir(cil_beh):
        os.makedirs(cil_beh)

    vypis("")
    vypis("  Nasazuji z repa na:")
    vypis("  %s" % cil)
    vypis("")

    zmeneno = 0
    for jmeno, kam in ([(j, cil_beh) for j in DO_BEHU] +
                       [(j, cil) for j in VEDLE_MASTERU]):
        zdroj = os.path.join(HERE, jmeno)
        if not os.path.isfile(zdroj):
            vypis("    CHYBI v repu: %s" % jmeno)
            continue
        cilovy = os.path.join(kam, jmeno)
        stejne = os.path.isfile(cilovy) and otisk(zdroj) == otisk(cilovy)
        if stejne:
            vypis("    beze zmeny  %s" % jmeno)
            continue
        shutil.copy2(zdroj, cilovy)
        zmeneno += 1
        vypis("    NASAZENO    %s" % jmeno)

    vypis("")
    if zmeneno:
        vypis("  Hotovo, souboru zmeneno: %d." % zmeneno)
    else:
        vypis("  Na O: uz byla stejna verze, nic se nemenilo.")
    vypis("  Pamet mezi behy ani provozni slozky se nepresouvaly.")
    vypis("")
    return 0


if __name__ == "__main__":
    sys.exit(main())
