# -*- coding: utf-8 -*-
"""Doplni financovaci kriteria veritelu do listu 3 (Role Financovani) z posouzene davky.

PROC SAMOSTATNY NASTROJ. financovani-zapis-investoru.py zapisuje list 3 jen pri zalozeni
subjektu a neprazdna pole nikdy neprepisuje. Kriteria (ticket, LTV, produkty, typy aktiv)
se ale dohledavaji AZ POTE, co subjekt v databazi je - a sloupec "Typy aktiv" se musi
prepsat na slovnik vyhledavace (rezidencni, kancelare, logistika, retail, hotely,
mixed-use, pozemky, korporatni), jinak nastroj "Kdo mi to zafinancuje" typ aktiva nepozna.

Co dela:
  - Ticket od / Ticket do / LTV max: doplni jen PRAZDNE bunky (zverejnene cislo se nesmi
    tise prepsat jinym; kdyz se lisi, vypise to a necha na cloveku).
  - Produktove sloupce (Senior ... Financuje fondy): "ANO" jen kde je v davce "ANO".
    Nikdy nemaze ANO, ktere uz v sesitu je.
  - Typy aktiv: PREPISE na kody ze slovniku (--prepsat-aktiva), jinak jen doplni prazdne.
  - Posledni dolozena aktivita: doplni prazdne.
  - Poznamka v listu 1: pripise datovany radek s geografii a popisem aktiv.
  - List 4 Zdroje: hlavni citace s popiskem "Kritéria financování" + kazdy dalsi doklad
    s vlastnim popiskem (napr. "Senior", "Ticket od"), URL posledni aktivity s popiskem
    "aktivita" (tak ji cte vyhledavac).

Pouziti:
  python financovani-kriteria.py kriteria.json --config financovani-beh-dach.config.json            # nanecisto
  python financovani-kriteria.py kriteria.json --config financovani-beh-dach.config.json --zapis --prepsat-aktiva
"""
import argparse
import importlib.util
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
PRODUKTY = ["senior", "whole_loan", "junior", "mezzanine", "bridge", "pref_equity", "development",
            "akvizicni", "refinancovani", "nav_lending", "financuje_spv", "financuje_fondy"]
SLOVNIK = {"rezidenční", "kanceláře", "logistika", "retail", "hotely", "mixed-use", "pozemky", "korporátní"}


def main():
    ap = argparse.ArgumentParser(description="Doplni kriteria veritelu do listu 3")
    ap.add_argument("soubor")
    ap.add_argument("--config", default="financovani-beh.config.json")
    ap.add_argument("--master")
    ap.add_argument("--zapis", action="store_true")
    ap.add_argument("--prepsat-aktiva", action="store_true", dest="prepsat_aktiva",
                    help="prepsat sloupec Typy aktiv kody ze slovniku i tam, kde uz neco je")
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location("fb", os.path.join(HERE, "financovani-beh.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    with io.open(os.path.join(HERE, args.config), encoding="utf-8") as f:
        cfg = json.load(f)
    m.T.update(cfg.get("texty", {}))
    if args.master:
        cfg["master"] = args.master
    sesit = m.Sesit(cfg)
    with io.open(args.soubor, encoding="utf-8") as f:
        davka = json.load(f)
    mapa = cfg["sloupce"]["financovani"]
    labels = {k: mapa[k] for k in PRODUKTY if k in mapa}

    ws3 = sesit.ws("financovani")
    doplneno = konflikty = citaci = 0
    for z in davka:
        sid = str(z.get("id", "")).strip()
        r = m.najdi_radek(sesit, "financovani", sid)
        if not r:
            print("  #%-4s %-40s -- v listu 3 neni, preskoceno" % (sid, z.get("nazev", "")[:40])); continue
        zmeny = []
        # ticket / LTV / aktivita: jen prazdne
        for klic in ("ticket_od", "ticket_do", "ltv", "posledni_aktivita"):
            nova = m.norm(z.get(klic, ""))
            if not nova:
                continue
            i = sesit.sl("financovani", klic)
            if not i:
                continue
            stara = m.norm(ws3.cell(row=r, column=i).value)
            if stara and stara != nova:
                konflikty += 1
                print("  #%-4s %-40s !! %s: v sesitu '%s', davka '%s' - NEPREPISUJI" % (sid, z["nazev"][:40], klic, stara[:40], nova[:40]))
                continue
            if not stara:
                zmeny.append((i, nova, klic))
        # produkty: jen ANO, nikdy nemazat
        for klic, nazev in labels.items():
            if m.norm(z.get(klic, "")).upper() == "ANO":
                i = sesit.sl("financovani", klic)
                if i and m.norm(ws3.cell(row=r, column=i).value).upper() != "ANO":
                    zmeny.append((i, "ANO", klic))
        # typy aktiv: kody
        kody = [k.strip() for k in m.norm(z.get("typy_aktiv_kod", "")).split(",") if k.strip()]
        spatne = [k for k in kody if k not in SLOVNIK]
        if spatne:
            print("  #%-4s %-40s !! typy aktiv mimo slovnik: %s (vynechano)" % (sid, z["nazev"][:40], spatne))
            kody = [k for k in kody if k in SLOVNIK]
        if kody:
            i = sesit.sl("financovani", "typy_aktiv")
            stara = m.norm(ws3.cell(row=r, column=i).value) if i else ""
            nova = ", ".join(kody)
            if i and (not stara or (args.prepsat_aktiva and stara != nova)):
                zmeny.append((i, nova, "typy_aktiv"))
        print("  #%-4s %-40s -> %s" % (sid, z["nazev"][:40], ", ".join("%s=%s" % (k, str(v)[:22]) for _, v, k in zmeny) or "nic noveho"))
        if not args.zapis:
            continue
        for i, v, _ in zmeny:
            ws3.cell(row=r, column=i).value = v
        doplneno += len(zmeny)
        # poznamka do listu 1
        r1 = m.najdi_radek(sesit, "subjekty", sid)
        popis = "; ".join(x for x in (m.norm(z.get("geografie", "")) and "geografie: " + m.norm(z.get("geografie", "")),
                                     m.norm(z.get("typy_aktiv_text", ""))) if x)
        if r1 and popis:
            m.pripis_poznamku(sesit, r1, "[%s kritéria financování] %s" % (m.DNES, popis))
        # citace
        if m.norm(z.get("citace", "")) and m.norm(z.get("zdroj", "")).startswith("http"):
            m.zapis_zdroj(sesit, sid, z["nazev"], "Kritéria financování", z["citace"], z["zdroj"]); citaci += 1
        for d in z.get("dalsi_doklady", []) or []:
            if m.norm(d.get("citace", "")) and m.norm(d.get("url", "")).startswith("http"):
                m.zapis_zdroj(sesit, sid, z["nazev"], m.norm(d.get("co", "")) or "Kritéria financování", d["citace"], d["url"]); citaci += 1
        if m.norm(z.get("aktivita_url", "")).startswith("http") and m.norm(z.get("posledni_aktivita", "")):
            m.zapis_zdroj(sesit, sid, z["nazev"], "aktivita", z["posledni_aktivita"], z["aktivita_url"]); citaci += 1

    print("=" * 70)
    print("  konflikty (nezapsano, k rozhodnuti): %d" % konflikty)
    if not args.zapis:
        print("NANECISTO - nic nezapsano. Ostry zapis: --zapis (a --prepsat-aktiva pro slovnik)"); return
    sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
    print("Zapsano: %d hodnot v listu 3, %d citaci v listu 4." % (doplneno, citaci))


if __name__ == "__main__":
    main()
