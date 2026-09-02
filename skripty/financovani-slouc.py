# -*- coding: utf-8 -*-
"""Slouci dva radky masteru, ktere jsou tentyz subjekt.

PROC TO NEDELA MESICNI BEH
Pojistka "nikdy_nemaze" plati a plati dobre: automat, ktery smi mazat radky,
je automat, po kterem se jednou rano neco nenajde. Ochrana proti slabe shode
proto duplicitu NAHLASI a necha ji lezet - viz #80 a #192 Trigea, kde stejne
cislice v ICO byly posunute o jednu pozici a ARES znal jen jedno z nich.
Slouceni je tedy vedoma jednorazova operace spoustena na jmeno, ne uklid,
ktery probehne mimochodem.

CO DELA
  1. Zalohu - pres Sesit.uloz, tedy jedna na den, stejne jako kazdy jiny beh.
  2. Prepoji radky v podrizenych listech (2, 3, 4, 6) z ruseneho ID na
     zustavajici.
  3. Slouci radek subjektu v listu 1 podle pravidel nize.
  4. Az nakonec smaze radek ruseneho subjektu v listu 1.

PRAVIDLA SLOUCENI RADKU SUBJEKTU
  prazdne u zustavajiciho  doplni se z ruseneho
  Poznamka                 obe se spoji, nic se nezahodi
  Overeno                  vitezi pozdejsi datum
  Stav                     kdyz je jeden z nich aktivni, vysledek je aktivni.
                           VYRAZEN byl odpovedi na otazku "pujcuje z vlastni
                           bilance?", ne na otazku "existuje?". Kdyby zustal,
                           mesicni beh by radek preskakoval a slouceni by bylo
                           jen naoko.
  sloupce, kde se obe
  neprazdne hodnoty LISI   KONFLIKT. Nezapise se NIC a skript rozdil vypise.
                           Rozhodnuti patri clovku: --prepis pole=hodnota.

DUPLICITY V PODRIZENYCH LISTECH
Kdyz po prepojeni vzniknou dva radky teze veci, neprazdna pole se doplni do
prvniho a druhy se smaze; jeho Poznamka se pripoji, aby neztratila stopu,
odkud udaj je. Listy se pritom nikdy nepretrizuji - maze se odspodu.

POUZITI
    python financovani-slouc.py --do 80 --z 192                      # nanecisto
    python financovani-slouc.py --do 80 --z 192 --prepis ico=07973179 --zapis
"""

import argparse
import io
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "financovani-beh.config.json")

# Sloupce, ktere se pri hledani duplicit v podrizenych listech neporovnavaji:
# ID se prave prepsalo, datum a poznamka jsou stopa, ne obsah.
IGNORUJ_PRI_SROVNANI = ("id", "subjekt", "overeno", "poznamka")


def vypis(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def stejny_web(a, b):
    """Adresy, ktere se lisi jen lomitkem na konci, schematem nebo www."""
    def klic(u):
        u = (u or "").strip().lower().rstrip("/")
        for p in ("https://", "http://"):
            if u.startswith(p):
                u = u[len(p):]
        if u.startswith("www."):
            u = u[4:]
        return u
    return klic(a) == klic(b)


def kontext(cesta_cfg=None):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "financovani_beh", os.path.join(HERE, "financovani-beh.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    cfg = json.load(io.open(cesta_cfg or CONFIG, encoding="utf-8"))
    modul.T.update(cfg["texty"])
    return cfg, modul


def najdi(sesit, m, sid):
    """(cislo radku, {pole: hodnota}) subjektu s danym ID, jinak None."""
    for r, d in sesit.radky("subjekty"):
        if m.cislo(m.norm(d.get("id"))) == sid:
            return r, d
    return None, None


def slouc_subjekt(sesit, m, cfg, r_do, d_do, d_z, prepis):
    """Vrati (zmeny, konflikty). Zmeny jsou {pole: (bylo, bude, proc)}."""
    zmeny, konflikty = {}, []
    aktivni = cfg["stavy"]["aktivni"]
    for pole in cfg["sloupce"]["subjekty"]:
        if pole == "id":
            continue
        a, b = m.norm(d_do.get(pole)), m.norm(d_z.get(pole))
        if pole in prepis:
            if m.norm(prepis[pole]) != a:
                zmeny[pole] = (a, m.norm(prepis[pole]), "rozhodl clovek (--prepis)")
            continue
        if not b or a == b:
            continue
        # Lomitko na konci URL a http versus https nejsou rozdil v obsahu.
        # Bez tohohle by kazde slouceni hlasilo konflikt na sloupci Web
        # a clovek by ho odklikaval, aniz by se na cokoli podival.
        if pole == "web" and stejny_web(a, b):
            continue
        if not a:
            zmeny[pole] = (a, b, "u zustavajiciho prazdne, doplneno z ruseneho")
        elif pole == "poznamka":
            zmeny[pole] = (a, a + " | " + b, "spojeno, nic se nezahodilo")
        elif pole == "overeno":
            zmeny[pole] = (a, max(a, b), "pozdejsi datum")
        elif pole == "stav" and aktivni in (a, b):
            if a != aktivni:
                zmeny[pole] = (a, aktivni, "jeden z radku je aktivni")
        else:
            konflikty.append((pole, a, b))
    return zmeny, konflikty


def prepoj(sesit, m, klic, sid_do, sid_z, nazev_do):
    """Prepoji radky z ruseneho ID na zustavajici. Vrati (prepojene, k_smazani)."""
    i_id = sesit.sl(klic, "id")
    i_sub = sesit.sl(klic, "subjekt")
    if not i_id:
        return [], []
    ws = sesit.ws(klic)
    mapa = cfg_sloupce = sesit.cfg["sloupce"][klic]
    prepojene = []
    for r, d in sesit.radky(klic):
        if m.cislo(m.norm(d.get("id"))) != sid_z:
            continue
        prepojene.append((r, d))
    # duplicity: radek, ktery se po prepojeni krysi s existujicim radkem
    stavajici = [(r, d) for r, d in sesit.radky(klic)
                 if m.cislo(m.norm(d.get("id"))) == sid_do]
    k_smazani, doplneni = [], []
    for r, d in prepojene:
        # Duplicita neni "radek se rovna radku", ale "radek nic nepridava":
        # kazde jeho NEPRAZDNE pole uz na cilovem radku stoji stejne. Radek
        # #192 Trigea mel jen info@trigea.cz, ktery #80 uz mel - a k tomu
        # #80 vedel i jmeno reditele. Prepojit ho by znamenalo vyrobit v listu
        # kontaktu druhy, chudsi radek teze adresy.
        dvojnik = None
        porovnavana = [p for p in mapa if p not in IGNORUJ_PRI_SROVNANI]
        neprazdna = [p for p in porovnavana if not m.prazdne(d.get(p))]
        if neprazdna:
            for r0, d0 in stavajici:
                if all(m.norm(d.get(p)) == m.norm(d0.get(p)) for p in neprazdna):
                    dvojnik = (r0, d0)
                    break
        if dvojnik:
            r0, d0 = dvojnik
            for p in mapa:
                if p in ("id", "subjekt"):
                    continue
                if m.prazdne(d.get(p)):
                    continue
                if m.prazdne(d0.get(p)):
                    doplneni.append((r0, p, m.norm(d.get(p))))
                elif p == "poznamka" and m.norm(d0.get(p)) != m.norm(d.get(p)):
                    # Poznamka je stopa, odkud udaj je. Mazany radek ji ma
                    # svou, takze se pripoji - jinak by po slouceni nikdo
                    # nezjistil, ze cast udaju prisla z jineho radku.
                    doplneni.append((r0, p, m.norm(d0.get(p)) + " | " + m.norm(d.get(p))))
            k_smazani.append((r, d))
        else:
            doplneni.append((r, "id", sid_do))
            if i_sub and nazev_do:
                doplneni.append((r, "subjekt", nazev_do))
    return doplneni, k_smazani


def main():
    ap = argparse.ArgumentParser(description="Slouci dva radky teze firmy do jednoho")
    ap.add_argument("--do", type=int, required=True, help="ID, ktere zustane")
    ap.add_argument("--z", type=int, required=True, help="ID, ktere se zrusi")
    ap.add_argument("--prepis", action="append", default=[],
                    help="vedome rozhodnuti o sloupci, napr. --prepis ico=07973179")
    ap.add_argument("--zapis", action="store_true", help="opravdu zapsat")
    ap.add_argument("--master", help="jina cesta k sesitu (test)")
    ap.add_argument("--config", help="jina konfigurace, tedy jina databaze")
    args = ap.parse_args()

    if args.do == args.z:
        raise SystemExit("--do a --z jsou tentyz radek, neni co slucovat.")

    cfg, m = kontext(os.path.join(HERE, args.config) if args.config else None)
    if args.master:
        cfg["master"] = args.master
        vypis("POZOR: bezi proti jinemu sesitu - %s" % args.master)
    prepis = {}
    for kus in args.prepis:
        if "=" not in kus:
            raise SystemExit("--prepis se pise jako pole=hodnota, dostal jsem: %s" % kus)
        pole, hodnota = kus.split("=", 1)
        if pole not in cfg["sloupce"]["subjekty"]:
            raise SystemExit("Sloupec '%s' v listu subjektu neni. Znam: %s"
                             % (pole, ", ".join(cfg["sloupce"]["subjekty"])))
        prepis[pole] = hodnota

    sesit = m.Sesit(cfg)
    r_do, d_do = najdi(sesit, m, args.do)
    r_z, d_z = najdi(sesit, m, args.z)
    if not r_do:
        raise SystemExit("ID %d v listu subjektu neni." % args.do)
    if not r_z:
        raise SystemExit("ID %d v listu subjektu neni." % args.z)

    vypis("")
    vypis("ZUSTAVA  #%-4d %s" % (args.do, m.norm(d_do.get("nazev"))))
    vypis("RUSI SE  #%-4d %s" % (args.z, m.norm(d_z.get("nazev"))))
    if m.norm(d_do.get("nazev")).lower() != m.norm(d_z.get("nazev")).lower():
        vypis("")
        vypis("  POZOR: nazvy se nerovnaji. Zkontroluj, ze je to opravdu tataz firma.")

    zmeny, konflikty = slouc_subjekt(sesit, m, cfg, r_do, d_do, d_z, prepis)

    vypis("")
    vypis("--- LIST 1, RADEK SUBJEKTU ---")
    if not zmeny:
        vypis("  zadna zmena - zustavajici radek uz ma vsechno")
    for pole, (bylo, bude, proc) in sorted(zmeny.items()):
        vypis("  %-18s %s" % (pole, proc))
        vypis("      bylo: %s" % (bylo or "(prazdne)"))
        vypis("      bude: %s" % bude)

    if konflikty:
        vypis("")
        vypis("=" * 70)
        vypis("  KONFLIKT - nic se nezapsalo. Oba radky maji jinou hodnotu a")
        vypis("  skript nema podle ceho rozhodnout. Vyber rucne pres --prepis.")
        vypis("=" * 70)
        for pole, a, b in konflikty:
            vypis("  %-18s #%d: %s" % (pole, args.do, a))
            vypis("  %-18s #%d: %s" % ("", args.z, b))
            vypis("      --prepis %s=..." % pole)
        raise SystemExit(1)

    nazev_do = m.norm(d_do.get("nazev"))
    vsechna_doplneni, vsechna_smazani = [], []
    for klic in ("kontakty", "financovani", "zdroje", "investor"):
        if klic not in cfg["listy"]:
            continue
        doplneni, smazani = prepoj(sesit, m, klic, args.do, args.z, nazev_do)
        if doplneni or smazani:
            vypis("")
            vypis("--- LIST '%s' ---" % cfg["listy"][klic])
            radky_prepojene = sorted({r for r, p, v in doplneni if p == "id"})
            if radky_prepojene:
                vypis("  prepojeno na #%d: radky %s"
                      % (args.do, ", ".join(str(r) for r in radky_prepojene)))
            for r, p, v in doplneni:
                if p not in ("id", "subjekt"):
                    vypis("  radek %d: %s <- %s" % (r, p, str(v)[:60]))
            for r, d in smazani:
                vypis("  radek %d SMAZAT jako duplicitu teze veci" % r)
        vsechna_doplneni += [(klic, r, p, v) for r, p, v in doplneni]
        vsechna_smazani += [(klic, r) for r, d in smazani]

    vypis("")
    vypis("--- LIST 1 ---")
    vypis("  radek %d (#%d) SMAZAT" % (r_z, args.z))

    if not args.zapis:
        vypis("")
        vypis("NANECISTO - nic nezapsano. Ostry zapis: --zapis")
        return

    for pole, (bylo, bude, proc) in zmeny.items():
        i = sesit.sl("subjekty", pole)
        if i:
            sesit.ws("subjekty").cell(row=r_do, column=i).value = bude
    for klic, r, pole, v in vsechna_doplneni:
        i = sesit.sl(klic, pole)
        if i:
            sesit.ws(klic).cell(row=r, column=i).value = v
    # Maze se odspodu, aby se cisla radku nad mazanym radkem neposunula.
    for klic, r in sorted(vsechna_smazani, key=lambda x: -x[1]):
        sesit.ws(klic).delete_rows(r)
    sesit.ws("subjekty").delete_rows(r_z)

    sesit.uloz(os.path.join(HERE, cfg["zalohy"]) if cfg.get("zalohy") else None)
    vypis("")
    vypis("Zapsano do %s" % cfg["master"])
    vypis("Slouceno: #%d pohltilo #%d." % (args.do, args.z))


if __name__ == "__main__":
    main()
