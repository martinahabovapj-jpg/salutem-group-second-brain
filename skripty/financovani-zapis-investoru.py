# -*- coding: utf-8 -*-
"""Zapise posouzenou davku investoru do masteru (listy 1, 2, 4, 6).

PROC NEJDE PRES FRONTU V LISTU 5
Frontu ma smysl plnit tim, co vzniklo automaticky a co ma nekdo zkontrolovat.
Tohle je jednorazove zarazeni davky, kterou uz nekdo posoudil a schvalil -
osmdesat radku ve fronte by z ni udelalo seznam, ktery se schvalovatel nauci
preskakovat. Stopa presto zustava: kazda zapsana hodnota ma v listu 4
doslovnou citaci a URL, a v poznamce subjektu je datum a zdroj.

CO ZAPISUJE
  list 1  radek subjektu: nazev, web, typ, stav, Role: investor = ANO
  list 2  kontakt, kdyz je znamy
  list 4  doslovna citace + URL ke kazdemu zaznamu
  list 6  segment (ciho kapitalu se tyka), AUM, gatekeeper

CO NEZAPISUJE
Verdikt 'nevim'. Ten se schvalne nikam neuklada - neni to zamitnuti a ma
se dat posoudit znovu, az bude vic informaci.

VSTUP
JSON pole zaznamu:
  {"ico": "24814326",          # smi byt prazdne
   "nazev": "Verdi Capital s.r.o.",
   "web": "https://verdicapital.cz/",
   "typ": "Family office",
   "verdikt": "zaradit",       # zaradit | zamitnout | nevim
   "segment": "vlastni a rodinny kapital - nemovitosti",
   "aum": "",
   "gatekeeper": "",
   "telefon": "", "email": "",
   "duvod": "...",
   "citace": "doslovna veta ze stranky",
   "zdroj": "https://..."}

POUZITI
    python financovani-zapis-investoru.py davka1.json           # nanecisto
    python financovani-zapis-investoru.py davka1.json --zapis   # zapise
"""

import argparse
import io
import json
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "financovani-beh.config.json")
STATE = os.path.join(HERE, "financovani-beh.stav.json")

T = {}


def vypis(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def kontext(cesta_cfg=None):
    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "financovani_beh", os.path.join(HERE, "financovani-beh.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    cfg = json.load(io.open(cesta_cfg or CONFIG, encoding="utf-8"))
    T.update(cfg["texty"])
    modul.T.update(cfg["texty"])
    return cfg, modul


def zapis_davku(zaznamy, cfg, m, opravdu):
    sesit = m.Sesit(cfg)
    m.zajisti_list(sesit, "zamitnuto")
    stav = m.load_json(STATE, {"behy": [], "subjekty": {}, "log": []})
    pamet = stav.setdefault("objevy_investor", {})

    ws1 = sesit.ws("subjekty")
    i_id = sesit.sl("subjekty", "id")

    # parovani na uz existujici subjekty: ICO, domena webu, nazev
    podle_ica, podle_dom, podle_nazvu = {}, {}, {}
    nejvyssi = 0
    for r, d in sesit.radky("subjekty"):
        sid = m.norm(d.get("id"))
        c = m.cislo(sid)
        if c and c > nejvyssi:
            nejvyssi = c
        for kus in re.findall(r"\d{8}", str(d.get("ico") or "")):
            podle_ica.setdefault(kus, (r, sid))
        dm = domena(d.get("web"))
        if dm and not domena_spravce(d.get("web"), cfg):
            podle_dom.setdefault(dm, (r, sid))
        podle_nazvu.setdefault(m.norm(d.get("nazev")).lower(), (r, sid))

    zapsano, doplneno, zamitnuto, preskoceno = [], [], [], []
    zmena_stavu = []
    slaba_shoda = []
    do7 = []
    do8 = []

    for z in zaznamy:
        verdikt = (z.get("verdikt") or "").lower()
        nazev = m.norm(z.get("nazev"))
        ico = m.norm(z.get("ico"))
        web = m.norm(z.get("web"))
        citace = m.norm(z.get("citace"))
        zdroj = m.norm(z.get("zdroj"))

        if verdikt == "nevim":
            # nevim se NEZAHAZUJE - jde do listu 8, aby to clovek videl
            preskoceno.append((nazev, m.norm(z.get("duvod"))))
            do8.append({"datum": m.DNES, "ico": ico, "nazev": nazev, "web": web,
                        "co_vime": m.norm(z.get("segment")) or m.norm(z.get("typ")),
                        "duvod": m.norm(z.get("duvod"))})
            continue
        if verdikt not in ("zaradit", "zamitnout") or not (citace and zdroj):
            preskoceno.append((nazev, "chybi citace, URL nebo neplatny verdikt"))
            continue

        klic = "ico:%s" % ico if ico else "nazev:%s" % nazev.lower()
        pamet[klic] = {"datum": m.DNES, "verdikt": verdikt, "nazev": nazev,
                       "duvod": m.norm(z.get("duvod")), "zdroj": zdroj}

        if opravdu:
            m.vyres_nerozhodnute(sesit, ico, nazev)

        if verdikt == "zamitnout":
            zamitnuto.append(nazev)
            do7.append({"datum": m.DNES, "ico": ico or "-", "nazev": nazev,
                        "duvod": m.norm(z.get("duvod")), "citace": citace,
                        "zdroj": zdroj})
            continue

        # --- zaradit
        radek, sid = None, None
        if ico and ico in podle_ica:
            radek, sid = podle_ica[ico]
        elif (domena(web) and not domena_spravce(web, cfg)
              and domena(web) in podle_dom):
            radek, sid = podle_dom[domena(web)]
        elif nazev.lower() in podle_nazvu:
            radek, sid = podle_nazvu[nazev.lower()]

        # Jak silne je sparovani rozhoduje o tom, jestli se smi zapsat ICO.
        # Shoda pres ICO je doklad totoznosti. Shoda pres domenu nebo nazev
        # je jen indicie: skupina a jeji fond casto sdileji web, takze by se
        # na radek skupiny zapsalo ICO fondu - a mesicni beh by se pak ptal
        # rejstriku na jiny subjekt, nez ktery na tom radku stoji.
        slabe = radek is not None and not (ico and ico in podle_ica)
        if slabe and ico:
            # Zaznam ma ICO, ale radek se nasel jen podle webu nebo nazvu.
            # Skupina a jeji fond sdileji web, takze tohle NEJSOU tytez
            # subjekty - Conseq Investment Management vs Conseq Venture Debt.
            # Drive se to slilo do jednoho radku: fond dostal roli i segment
            # spravcovske firmy. Zaklada se proto novy radek a blizka shoda
            # se hlasi, aby to clovek mohl spojit, kdyz to tataz firma je.
            slaba_shoda.append((sid, nazev, ico))
            radek, sid = None, None

        novy = radek is None
        if novy:
            nejvyssi += 1
            sid = int(nejvyssi)
            if opravdu:
                radek = m.zaloz_radek(sesit, "subjekty", sid, nazev)

        if opravdu:
            # VYRAZEN nebo nenalezeno znamenalo "nepujcuje z vlastni bilance",
            # coz je odpoved na JINOU otazku. Pro roli investora je to casto
            # presne ten hledany profil - a kdyby stav zustal, mesicni beh by
            # radek preskakoval a zarazeni by bylo jen naoko.
            i_stav = sesit.sl("subjekty", "stav")
            bylo_stav = m.norm(ws1.cell(row=radek, column=i_stav).value) if (i_stav and not novy) else ""
            ozivene = bylo_stav and bylo_stav != cfg["stavy"]["aktivni"]
            # Zeme se bere ze zaznamu. U ceske davky chybela a radky pak beh
            # preskakoval, protoze nevedel, ktereho registru se zeptat.
            # U DACH je to jedina cesta, jak ji vyplnit - dohledavac zeme
            # umi jen CZ podle ICO.
            hodnoty = {"ico": ico,
                       "web": web, "typ": m.norm(z.get("typ")),
                       "zeme": m.norm(z.get("zeme")),
                       "stav": cfg["stavy"]["aktivni"], "overeno": m.DNES,
                       "role_investor": T["ano"]}
            if ozivene:
                zmena_stavu.append((sid, nazev, bylo_stav))
            for pole, val in hodnoty.items():
                if not val:
                    continue
                i = sesit.sl("subjekty", pole)
                if i and (novy or pole in ("role_investor", "overeno")
                          or (pole == "stav" and ozivene)
                          or m.prazdne(ws1.cell(row=radek, column=i).value)):
                    ws1.cell(row=radek, column=i).value = val
            m.pripis_poznamku(sesit, radek, T["aplikovano_pozn"].format(
                datum=m.DNES, co=T["role_investor_co"], detail=citace, zdroj=zdroj))

            # list 6
            r6 = m.najdi_radek(sesit, "investor", sid)
            if not r6:
                r6 = m.zaloz_radek(sesit, "investor", sid, nazev)
            ws6 = sesit.ws("investor")
            for pole in ("segment", "aum", "gatekeeper"):
                val = m.norm(z.get(pole))
                if not val:
                    continue
                i = sesit.sl("investor", pole)
                if i:
                    ws6.cell(row=r6, column=i).value = val
            i = sesit.sl("investor", "poznamka")
            if i and m.norm(z.get("duvod")):
                ws6.cell(row=r6, column=i).value = m.norm(z.get("duvod"))

            # list 2 kontakty
            if m.norm(z.get("telefon")) or m.norm(z.get("email")):
                r2 = m.najdi_radek(sesit, "kontakty", sid)
                if not r2:
                    r2 = m.zaloz_radek(sesit, "kontakty", sid, nazev)
                ws2 = sesit.ws("kontakty")
                for pole in ("telefon", "email"):
                    val = m.norm(z.get(pole))
                    i = sesit.sl("kontakty", pole)
                    if i and val:
                        ws2.cell(row=r2, column=i).value = val
                i = sesit.sl("kontakty", "overeno")
                if i:
                    ws2.cell(row=r2, column=i).value = m.DNES

            m.zapis_zdroj(sesit, sid, nazev, T["role_investor_co"], citace, zdroj)

        (zapsano if novy else doplneno).append((sid, nazev))

    pocet8 = 0
    if opravdu and do7:
        m.zapis_zamitnute(sesit, do7, T["zamitnuto_kde_inv"])
    if opravdu and do8:
        pocet8 = m.zapis_nerozhodnute(sesit, do8, T["nerozhodnuto_kde_inv"])

    vypis("")
    vypis("=" * 64)
    vypis("  Novych subjektu v listu 1:      %d" % len(zapsano))
    for sid, nazev in zapsano:
        vypis("     #%s %s" % (sid, nazev[:50]))
    vypis("  Role investor doplnena stavajicim: %d" % len(doplneno))
    for sid, nazev in doplneno:
        vypis("     #%s %s" % (sid, nazev[:50]))
    if zmena_stavu:
        vypis("  Stav vracen na aktivni u %d subjektu (byly vyrazene pro roli"
              " financovani, pro roli investora se hledaji):" % len(zmena_stavu))
        for sid, nazev, bylo in zmena_stavu:
            vypis("     #%s %-40s bylo '%s'" % (sid, nazev[:40], bylo))
    if slaba_shoda:
        vypis("  BLIZKA SHODA u %d zaznamu - podobny radek uz v databazi je,"
              " ale ma jine ICO. Zalozil jsem novy radek:" % len(slaba_shoda))
        for sid, nazev, ico in slaba_shoda:
            vypis("     %-42s (podobny radek #%s)" % (nazev[:42], sid))
        vypis("     Kdyz je to tataz firma, radky spoj rucne.")
    vypis("  Zamitnuto (do listu 7):         %d" % len(zamitnuto))
    for nazev in zamitnuto:
        vypis("     %s" % nazev[:50])
    vypis("  Nerozhodnuto - do listu '%s': %d"
          % (sesit.listy["nerozhodnuto"], len(preskoceno)))
    for nazev, duvod in preskoceno:
        vypis("     %-40s %s" % (nazev[:40], duvod[:60]))
    if pocet8 != len(preskoceno) and opravdu:
        vypis("     (z toho %d uz v listu 8 bylo, radky se nezdvojuji)"
              % (len(preskoceno) - pocet8))
    vypis("=" * 64)

    if opravdu:
        sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
        m.save_json(STATE, stav)
        vypis("Zapsano do %s" % cfg["master"])
    else:
        vypis("NANECISTO - nic nezapsano. Ostry zapis: --zapis")


def domena(url):
    u = re.sub(r"\s+", " ", str(url or "")).strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = u.split()[0] if u else ""
    u = re.sub(r"^www\.", "", u)
    return u.split("/")[0].strip().strip(".")


def domena_spravce(url, cfg):
    """Je to domena spravce fondu, a ne fondu samotneho?

    Na avantfunds.cz nebo amista.cz sedi desitky ruznych fondu. Shoda takove
    domeny neznamena tentyz subjekt - kdyz se na ni paruje, prilepi se novy
    fond na cizi radek a nikdo si toho nevsimne. Seznam je v konfiguraci,
    sekce "spravci".
    """
    dm = domena(url)
    if not dm:
        return False
    for d in (cfg.get("spravci") or {}).get("domeny") or []:
        d = str(d).lower().strip()
        if d and (dm == d or dm.endswith("." + d)):
            return True
    return False



def main():
    ap = argparse.ArgumentParser(description="Zapise posouzenou davku investoru")
    ap.add_argument("soubor", help="JSON s posouzenou davkou")
    ap.add_argument("--zapis", action="store_true", help="opravdu zapsat")
    ap.add_argument("--master", help="jina cesta k sesitu (test)")
    ap.add_argument("--config", help="jina konfigurace, tedy jina databaze (napr. financovani-beh-dach.config.json)")
    args = ap.parse_args()

    cfg, m = kontext(os.path.join(HERE, args.config) if args.config else None)
    global STATE
    if cfg.get("stav"):
        STATE = os.path.join(HERE, cfg["stav"])
    if args.master:
        cfg["master"] = args.master
        vypis("POZOR: bezi proti jinemu sesitu - %s" % args.master)
    zaznamy = json.load(io.open(args.soubor, encoding="utf-8"))
    vypis("Davka: %d zaznamu" % len(zaznamy))
    zapis_davku(zaznamy, cfg, m, args.zapis)


if __name__ == "__main__":
    main()
