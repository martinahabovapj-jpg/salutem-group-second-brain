# -*- coding: utf-8 -*-
"""Oprava jednoho pole v listu 1 Subjekty - s dokladem.

PROC TENHLE NASTROJ EXISTUJE. Zapisovaci skripty NEPREPISUJI neprazdna pole -
je to pojistka, aby davka nikomu tise nezmenila IČO nebo web. Dusledek: kdyz
je v sesitu od zacatku spatna hodnota (HIH s domenou hih.de misto hih-invest.de,
Empira se zemi DE, i kdyz sedi v Zugu), zadny beh ji neopravi a oprava zustava
"na cloveku". Rucni prepis v Excelu ale nenese doklad ani datum.

Tenhle nastroj udela presne jednu vec: prepise jedno pole u jednoho subjektu,
puvodni hodnotu zachova v Poznamce s datem, a do listu 4 zapise doslovnou
citaci a URL, ze kterych oprava vychazi. Bez citace a URL odmitne zapsat -
stejne pravidlo jako u kazde jine hodnoty v sesitu.

Pouziti (nejdriv nanecisto, pak s --zapis):

  python financovani-oprav-pole.py --config financovani-beh-dach.config.json \
      --id 40 --pole web --hodnota https://www.hih-invest.de \
      --citace "HIH Invest Real Estate GmbH Ericusspitze 1 20457 Hamburg" \
      --zdroj https://www.hih-invest.de/impressum \
      --duvod "kontakty i tiraz jsou na hih-invest.de, hih.de je holding" --zapis

Pole se zadava logickym nazvem z konfigurace (sekce sloupce.subjekty):
web, zeme, ico, nazev, typ, stav. Pole role_* a poznamka se timhle NEMENI -
role ma vlastni cestu pres davku (financovani-zapis-investoru.py), poznamka
se jen pripisuje.
"""
import argparse
import importlib.util
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
POVOLENA = ("web", "zeme", "ico", "nazev", "typ", "stav")


def main():
    ap = argparse.ArgumentParser(description="Opravi jedno pole u jednoho subjektu, s dokladem")
    ap.add_argument("--config", default="financovani-beh.config.json")
    ap.add_argument("--master", help="jina cesta k sesitu (test)")
    ap.add_argument("--id", required=True, help="ID subjektu v listu 1")
    ap.add_argument("--pole", required=True, choices=POVOLENA)
    ap.add_argument("--hodnota", required=True, help="nova hodnota")
    ap.add_argument("--citace", required=True, help="doslovna citace z primarniho zdroje")
    ap.add_argument("--zdroj", required=True, help="URL stranky s citaci")
    ap.add_argument("--duvod", required=True, help="jedna veta pro cloveka, proc se to meni")
    ap.add_argument("--zapis", action="store_true", help="opravdu zapsat")
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location(
        "financovani_beh", os.path.join(HERE, "financovani-beh.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    with open(os.path.join(HERE, args.config), encoding="utf-8") as f:
        cfg = json.load(f)
    m.T.update(cfg.get("texty", {}))
    if args.master:
        cfg["master"] = args.master
    sesit = m.Sesit(cfg)

    if not args.citace.strip() or not args.zdroj.strip().startswith("http"):
        raise SystemExit("Bez doslovne citace a URL se nic neprepisuje - to je pravidlo celeho sesitu.")

    r = m.najdi_radek(sesit, "subjekty", args.id)
    if not r:
        raise SystemExit("Subjekt #%s v listu 1 neni." % args.id)
    ws = sesit.ws("subjekty")
    i_pole = sesit.sl("subjekty", args.pole)
    if not i_pole:
        raise SystemExit("Pole '%s' neni v konfiguraci listu 1 namapovane na sloupec." % args.pole)
    i_naz = sesit.sl("subjekty", "nazev")
    nazev = m.norm(ws.cell(row=r, column=i_naz).value) if i_naz else ""
    stara = m.norm(ws.cell(row=r, column=i_pole).value)
    nova = args.hodnota.strip()

    print("Subjekt #%s %s" % (args.id, nazev))
    print("  pole:   %s (sloupec '%s')" % (args.pole, cfg["sloupce"]["subjekty"][args.pole]))
    print("  bylo:   %s" % (stara or "(prazdne)"))
    print("  bude:   %s" % nova)
    print("  duvod:  %s" % args.duvod)
    print("  doklad: \"%s\"" % args.citace)
    print("          %s" % args.zdroj)
    if stara == nova:
        print("Hodnota uz v sesitu je. Nic k zapsani.")
        return
    if not args.zapis:
        print("\nNANECISTO - nic nezapsano. Ostry zapis: --zapis")
        return

    ws.cell(row=r, column=i_pole).value = nova
    i_over = sesit.sl("subjekty", "overeno")
    if i_over:
        ws.cell(row=r, column=i_over).value = m.DNES
    m.pripis_poznamku(sesit, r, "[%s opraveno] %s: '%s' -> '%s'. %s Zdroj: %s" % (
        m.DNES, cfg["sloupce"]["subjekty"][args.pole], stara or "-", nova, args.duvod, args.zdroj))
    m.zapis_zdroj(sesit, args.id, nazev, cfg["sloupce"]["subjekty"][args.pole],
                  args.citace, args.zdroj)
    sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
    print("\nZapsano do %s" % cfg["master"])


if __name__ == "__main__":
    main()
