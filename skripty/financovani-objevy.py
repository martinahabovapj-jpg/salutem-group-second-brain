# -*- coding: utf-8 -*-
"""
financovani-objevy.py - hledani NOVYCH subjektu, o kterych zatim nevime.

Jina uloha nez mesicni beh. Ten se pta znamych subjektu, jestli se u nich neco
zmenilo. Tohle hleda ty, kteri v databazi vubec nejsou.

Co se zmerilo 27. 8. 2026 a proc to skript dela zrovna takhle
--------------------------------------------------------------
1) NACE NEODLISUJE pouzitelneho poskytovatele od vyrazeneho. U 107 ceskych
   subjektu v databazi ma kod 64310 pomer 22:17 ve prospech pouzitelnych,
   68200 dokonce 14:15. Registr tedy umi najit PRIRUSTEK, ale neumi rict,
   jestli stoji za zarazeni. To musi rozhodnout model z webu, s citaci.

2) UZKE UVEROVE KODY JSOU PRAZDNE. Kody 6492x, 64999 a 66190 daly za dvanact
   mesicu tri nove subjekty. Kdyby se hlidaly jen ony, beh by kazdy mesic
   hlasil nulu a vypadalo by to, ze se na trhu nic nedeje. Skutecny prirustek
   je pod kodem 64310 (trusty a fondy) - 164 subjektu za rok, prevazne
   podfondy SICAV. Mezi nimi jsou i uverove: "CNFE LOAN podfond",
   "AMBER BRIDGE, podfond Opportunity".

Faze
----
    1  ARES sweep    kombinace NACE x pravni forma, vse s datem vzniku od meze
    2  odecteni      pryc vsechno, co uz v databazi je - VCETNE VYRAZENYCH
    3  priprava      kandidati do slozky k-posouzeni pro model
    4  verdikty      model vrati objevy.json; zarazene jdou do pruhu B,
                     zamitnute se zapamatuji, aby se priste nevracely

Pouziti
-------
    python financovani-objevy.py                       # najde a pripravi
    python financovani-objevy.py --verdikty objevy.json --zapis
    python financovani-objevy.py --dnu 90              # jen posledni ctvrtleti

Seznam zamitnutych je aktivum, ne odpad. Bez nej by kazdy beh nabizel tychz
sto fondu znovu a schvalovatel by se naucil seznam preskakovat.
"""

import argparse
import datetime as dt
import io
import json
import os
import re
import socket
import ssl
import sys
import time
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "financovani-beh.config.json")
STATE = os.path.join(HERE, "financovani-beh.stav.json")
URL_HLEDAT = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/vyhledat"

T = {}


def load_json(path, default):
    if not os.path.isfile(path):
        return default
    with io.open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def save_json(path, data):
    with io.open(path, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=2))


def vypis(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def norm(v):
    return re.sub(r"\s+", " ", str(v or "")).strip()


def kontext():
    """Nacte config, texty a tridu Sesit ze sousedniho skriptu."""
    import importlib.util
    cfg = load_json(CONFIG, None)
    if cfg is None:
        raise SystemExit("Chybi %s" % CONFIG)
    T.update(cfg["texty"])
    spec = importlib.util.spec_from_file_location(
        "financovani_beh", os.path.join(HERE, "financovani-beh.py"))
    modul = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(modul)
    modul.T.update(cfg["texty"])
    return cfg, modul


# ---------------------------------------------------------------- faze 1

def ares_hledat(nace, pf, ctx, ua):
    """Vsechny subjekty dane kombinace. ARES nema filtr na datum vzniku,
    takze se stahne cela mnozina a datum se filtruje az tady."""
    out, start = [], 0
    while True:
        telo = {"start": start, "pocet": 200, "czNace": [nace], "pravniForma": [pf]}
        req = urllib.request.Request(URL_HLEDAT, data=json.dumps(telo).encode("utf-8"),
                                     headers={"Content-Type": "application/json",
                                              "Accept": "application/json",
                                              "User-Agent": ua})
        try:
            d = json.load(urllib.request.urlopen(req, timeout=30, context=ctx))
        except urllib.error.HTTPError as e:
            # 400 = kombinace vraci pres 1000 vysledku; ARES vic nepusti
            return out, "kombinace je prilis siroka (HTTP %s)" % e.code
        except Exception as e:
            return out, type(e).__name__
        davka = d.get("ekonomickeSubjekty", [])
        out += davka
        start += len(davka)
        if not davka or start >= (d.get("pocetCelkem") or 0):
            return out, None
        time.sleep(0.2)


def najdi(cfg, mez):
    o = cfg["objevy"]
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    ua = cfg["sit"]["user_agent"]
    socket.setdefaulttimeout(cfg["sit"]["timeout_s"])

    nalezeno = {}
    prilis_siroke = []
    for nace in o["nace"]:
        for pf in o["pravni_formy"]:
            subj, chyba = ares_hledat(nace, pf, ctx, ua)
            if chyba:
                prilis_siroke.append((nace, pf, chyba))
                continue
            for z in subj:
                if (z.get("datumVzniku") or "") >= mez:
                    nalezeno[z.get("ico")] = {
                        "ico": z.get("ico"),
                        "nazev": norm(z.get("obchodniJmeno")),
                        "vznik": z.get("datumVzniku"),
                        "nace": nace,
                        "pravni_forma": pf,
                        "sidlo": norm((z.get("sidlo") or {}).get("textovaAdresa")),
                    }
            time.sleep(0.2)
    return nalezeno, prilis_siroke


# ---------------------------------------------------------------- faze 2

def znama_ica(sesit, cfg):
    """ICO vsech subjektu v databazi - VCETNE vyrazenych.

    Vyrazene se odecitaji schvalne: jsou zdokumentovane a znovu prosetrovat
    se nemaji. Presne proto se v databazi drzi."""
    ica = set()
    for _, d in sesit.radky("subjekty"):
        for kus in re.findall(r"\d{8}", str(d.get("ico") or "")):
            ica.add(kus)
    return ica


# ---------------------------------------------------------------- faze 3

def priprav(kandidati, cfg, stav):
    d = os.path.join(HERE, "k-posouzeni")
    if os.path.isdir(d):
        import shutil
        shutil.rmtree(d)
    os.makedirs(d)

    napovedy = [n.lower() for n in cfg["objevy"]["napovedy_v_nazvu"]]

    def skore(k):
        jm = k["nazev"].lower()
        return (0 if any(n in jm for n in napovedy) else 1, k["vznik"] or "")

    serazeni = sorted(kandidati.values(), key=skore)
    strop = cfg["objevy"]["max_kandidatu"]
    davka, mimo = serazeni[:strop], serazeni[strop:]

    radky = [T["objevy_nadpis_souboru"], "",
             T["objevy_hlavicka"], "|---|---|---|---|---|"]
    for k in davka:
        radky.append("| %s | %s | %s | %s | %s |"
                     % (k["ico"], k["nazev"], k["vznik"], k["nace"], k["sidlo"]))
    with io.open(os.path.join(d, "kandidati.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(radky))

    # zadani pro model je samostatny soubor, ne retezec v kodu - je to
    # dokument v cestine a tenhle zdrojak zustava ciste ASCII
    zdroj_zadani = os.path.join(HERE, "financovani-objevy.zadani.md")
    with io.open(zdroj_zadani, "r", encoding="utf-8-sig") as f:
        zadani = f.read()
    if mimo:
        zadani += T["objevy_useknuto"].format(
            celkem=len(serazeni), davka=len(davka),
            ica=", ".join(k["ico"] for k in mimo))
    with io.open(os.path.join(d, "_ZADANI.md"), "w", encoding="utf-8") as f:
        f.write(zadani)
    return len(davka), len(mimo)





# ---------------------------------------------------------------- faze 4

def verdikty(cesta, cfg, modul, sesit, stav, opravdu):
    vstup = load_json(cesta, [])
    pamet = stav.setdefault("objevy", {})
    navrhy, zahozeno = [], []

    for v in vstup:
        ico = str(v.get("ico") or "").strip()
        verdikt = (v.get("verdikt") or "").lower()
        if not ico or verdikt not in ("zaradit", "zamitnout", "nevim"):
            zahozeno.append(v)
            continue
        if verdikt in ("zaradit", "zamitnout") and not (v.get("citace") and v.get("zdroj")):
            # bez doslovne citace a URL verdikt nevznika
            zahozeno.append(v)
            continue
        pamet[ico] = {"datum": dt.date.today().isoformat(),
                      "verdikt": verdikt,
                      "nazev": norm(v.get("nazev")),
                      "duvod": norm(v.get("duvod")),
                      "zdroj": norm(v.get("zdroj"))}
        if verdikt == "zaradit":
            navrhy.append(modul.navrh(
                ico, norm(v.get("nazev")), "novy_subjekt", T["pole_stav"],
                "", T["objevy_zaradit"], v.get("zdroj"),
                citace=norm(v.get("citace")), jistota=""))

    if zahozeno:
        vypis("Zahozeno %d verdiktu - chybi citace, URL nebo neplatny verdikt."
              % len(zahozeno))

    # zamitnuti patri i do sesitu - stroj si je pamatuje v JSONu, ale clovek
    # se na ne musi dostat taky. Jinak na otazku "koukali jsme na X?" neni
    # v databazi odpoved a subjekt se posoudi znovu od nuly.
    do_listu7 = [{"datum": pamet[i]["datum"], "ico": i, "nazev": pamet[i]["nazev"],
                  "duvod": pamet[i]["duvod"], "citace": pamet[i]["duvod"],
                  "zdroj": pamet[i]["zdroj"]}
                 for i in pamet if pamet[i]["verdikt"] == "zamitnout"]
    if opravdu and do_listu7:
        modul.zajisti_list(sesit, "zamitnuto")
        pribylo = modul.zapis_zamitnute(sesit, do_listu7, T["zamitnuto_kde_obj"])
        if pribylo:
            vypis("Do listu '%s' pribylo %d zamitnutych."
                  % (sesit.listy["zamitnuto"], pribylo))

    zamitnuto = sum(1 for v in pamet.values() if v["verdikt"] == "zamitnout")
    vypis("Zapamatovano verdiktu celkem: %d (z toho zamitnutych %d - ti se uz "
          "nabizet nebudou)." % (len(pamet), zamitnuto))

    if navrhy:
        vysledek = modul.zapis(sesit, navrhy, cfg, stav, opravdu)
        vypis("K zarazeni jde do pruhu B: %d" % len(vysledek["B"]))
    else:
        vypis("Nic k zarazeni.")
    return navrhy


# ------------------------------------------------------- investorska strana
# Hledani do listu 6. Nejde pres NACE: family office nema vlastni kod a v
# rejstriku je k nerozeznani od bezne s.r.o. Postup je proto opacny nez u
# financovani - vyjde se ze jmena, ARES dohleda cely firemni trs (obvykle
# nekolik entit na jedne adrese) a teprve web s citaci rozhodne.


def ares_podle_jmena(jmeno, ctx, ua, pocet=50):
    telo = {"obchodniJmeno": jmeno, "start": 0, "pocet": pocet}
    req = urllib.request.Request(URL_HLEDAT, data=json.dumps(telo).encode("utf-8"),
                                 headers={"Content-Type": "application/json",
                                          "Accept": "application/json",
                                          "User-Agent": ua})
    try:
        d = json.load(urllib.request.urlopen(req, timeout=30, context=ctx))
    except Exception as e:
        return [], type(e).__name__
    return d.get("ekonomickeSubjekty", []), None


def najdi_investory(cfg, sesit, stav):
    """Vraci (kandidati, chyby). Kandidat nese bud ICO (novy), nebo ID
    subjektu, ktery uz v listu 1 je a jen se prehodnocuje."""
    o = cfg["objevy_investor"]
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    ua = cfg["sit"]["user_agent"]
    socket.setdefaulttimeout(cfg["sit"]["timeout_s"])

    znama = znama_ica(sesit, cfg)
    pamet = stav.setdefault("objevy_investor", {})

    kandidati, chyby = [], []
    videna = set()

    # --- a) subjekty, ktere v listu 1 uz jsou a maji se prehodnotit
    chci = set(str(x) for x in o.get("prehodnotit", []))
    if chci:
        for _, d in sesit.radky("subjekty"):
            sid = str(d.get("id"))
            if sid not in chci:
                continue
            kandidati.append({
                "klic": "id:%s" % sid,
                "id": sid,
                "ico": norm(d.get("ico")),
                "nazev": norm(d.get("nazev")),
                "web": norm(d.get("web")),
                "sidlo": "",
                "duvod_zarazeni": "prehodnoceni - v listu 1 veden jako %s"
                                  % norm(d.get("stav")),
            })
            videna.add(sid)

    # --- b) jmena: ARES dohleda cely trs
    for jmeno in o.get("jmena", []):
        subj, chyba = ares_podle_jmena(jmeno, ctx, ua)
        if chyba:
            chyby.append((jmeno, chyba))
            continue
        for z in subj:
            ico = str(z.get("ico") or "")
            if not ico or ico in videna:
                continue
            videna.add(ico)
            if ico in znama:
                continue           # uz ho v databazi mame
            if ico in pamet:
                continue           # uz jsme o nem jednou rozhodli
            kandidati.append({
                "klic": "ico:%s" % ico,
                "id": "",
                "ico": ico,
                "nazev": norm(z.get("obchodniJmeno")),
                "web": "",
                "sidlo": norm((z.get("sidlo") or {}).get("textovaAdresa")),
                "duvod_zarazeni": "hledano podle jmena '%s'" % jmeno,
            })
        time.sleep(0.2)

    # trs na jedne adrese je silny signal - stejne sidlo u vic entit napred
    podle_adresy = {}
    for k in kandidati:
        if k["sidlo"]:
            podle_adresy.setdefault(k["sidlo"], []).append(k)
    for k in kandidati:
        k["_trs"] = len(podle_adresy.get(k["sidlo"], [])) if k["sidlo"] else 0
    kandidati.sort(key=lambda k: (not k["id"], -k["_trs"], k["nazev"]))
    return kandidati, chyby


def priprav_investor(kandidati, cfg, stav):
    d = os.path.join(HERE, cfg["objevy_investor"].get("k_posouzeni", "k-posouzeni-investor"))
    if os.path.isdir(d):
        import shutil
        shutil.rmtree(d)
    os.makedirs(d)

    strop = cfg["objevy_investor"].get("max_kandidatu", 40)
    davka = kandidati[:strop]
    mimo = kandidati[strop:]

    radky = [T["investor_nadpis_souboru"], "", T["investor_hlavicka"],
             "|---|---|---|---|---|"]
    for k in davka:
        radky.append("| %s | %s | %s | %s | %s |" % (
            k["id"] or "-", k["ico"] or "-", k["nazev"],
            k["sidlo"] or "-", k["duvod_zarazeni"]))
    with io.open(os.path.join(d, "kandidati.md"), "w", encoding="utf-8") as f:
        f.write("\n".join(radky) + "\n")

    zadani = T["investor_zadani"]
    if mimo:
        zadani += T["objevy_useknuto"].format(
            celkem=len(kandidati), davka=len(davka),
            ica=", ".join(k["ico"] or k["id"] for k in mimo))
    with io.open(os.path.join(d, "_ZADANI.md"), "w", encoding="utf-8") as f:
        f.write(zadani)
    return len(davka), len(mimo)


def verdikty_investor(cesta, cfg, modul, sesit, stav, opravdu):
    vstup = load_json(cesta, [])
    pamet = stav.setdefault("objevy_investor", {})
    navrhy, zahozeno, do7 = [], [], []

    for v in vstup:
        klic = norm(v.get("klic"))
        verdikt = (v.get("verdikt") or "").lower()
        if not klic or verdikt not in ("zaradit", "zamitnout", "nevim"):
            zahozeno.append(v)
            continue
        if verdikt in ("zaradit", "zamitnout") and not (v.get("citace") and v.get("zdroj")):
            zahozeno.append(v)
            continue
        pamet[klic] = {"datum": dt.date.today().isoformat(),
                       "verdikt": verdikt,
                       "nazev": norm(v.get("nazev")),
                       "duvod": norm(v.get("duvod")),
                       "zdroj": norm(v.get("zdroj"))}
        if verdikt == "zaradit":
            # klic rozhoduje, jestli jde o novy subjekt, nebo o roli navic
            # u subjektu, ktery v listu 1 uz je
            if klic.startswith("id:"):
                druh, ident = "role_investor", klic[3:]
            else:
                druh, ident = "novy_investor", klic[4:]
            navrhy.append(modul.navrh(
                ident, norm(v.get("nazev")), druh, T["pole_stav"],
                "", T["investor_zaradit"], v.get("zdroj"),
                citace=norm(v.get("citace")), jistota=""))
        elif verdikt == "zamitnout":
            do7.append({"datum": pamet[klic]["datum"],
                        "ico": klic.split(":", 1)[1],
                        "nazev": norm(v.get("nazev")),
                        "duvod": norm(v.get("duvod")),
                        "citace": norm(v.get("citace")),
                        "zdroj": norm(v.get("zdroj"))})

    if zahozeno:
        vypis("Zahozeno %d verdiktu - chybi citace, URL nebo neplatny verdikt."
              % len(zahozeno))
    if opravdu and do7:
        modul.zajisti_list(sesit, "zamitnuto")
        pribylo = modul.zapis_zamitnute(sesit, do7, T["zamitnuto_kde_inv"])
        if pribylo:
            vypis("Do listu '%s' pribylo %d zamitnutych."
                  % (sesit.listy["zamitnuto"], pribylo))

    if navrhy:
        vysledek = modul.zapis(sesit, navrhy, cfg, stav, opravdu)
        vypis("K zarazeni jde do pruhu B: %d" % len(vysledek["B"]))
    else:
        vypis(T["investor_zadny"])
    return navrhy


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Hledani novych subjektu do databaze financovani")
    ap.add_argument("--dnu", type=int, help="jak daleko zpet hledat (default z konfigurace)")
    ap.add_argument("--verdikty", help="soubor objevy.json od modelu")
    ap.add_argument("--zapis", action="store_true", help="opravdu zapsat")
    ap.add_argument("--master", help="jina cesta k sesitu (test, kdyz je disk O: pryc)")
    ap.add_argument("--investor", action="store_true",
                    help="hleda na investorske strane (list 6) - podle jmen, ne podle NACE")
    ap.add_argument("--verdikty-investor", dest="verdikty_investor",
                    help="soubor objevy-investor.json od modelu")
    args = ap.parse_args()

    cfg, modul = kontext()
    if args.master:
        cfg["master"] = args.master
        vypis("POZOR: bezi proti jinemu sesitu nez podle konfigurace - %s" % args.master)
    stav = load_json(STATE, {"behy": [], "subjekty": {}, "log": []})
    sesit = modul.Sesit(cfg)

    if args.verdikty_investor:
        verdikty_investor(args.verdikty_investor, cfg, modul, sesit, stav, args.zapis)
        if args.zapis:
            sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
        save_json(STATE, stav)
        return

    if args.investor:
        vypis("=" * 62)
        vypis("  " + T["nadpis_investor"])
        vypis("=" * 62)
        kandidati, chyby = najdi_investory(cfg, sesit, stav)
        for jmeno, chyba in chyby:
            vypis("  ARES neodpovedel na jmeno '%s': %s" % (jmeno, chyba))
        if not kandidati:
            vypis(T["investor_zadny"])
            save_json(STATE, stav)
            return
        davka, mimo = priprav_investor(kandidati, cfg, stav)
        vypis("Kandidatu celkem: %d" % len(kandidati))
        vypis("Pripraveno k posouzeni: %d (slozka %s)"
              % (davka, cfg["objevy_investor"].get("k_posouzeni", "k-posouzeni-investor")))
        if mimo:
            vypis("POZOR: %d kandidatu se do davky neveslo - neni to "
                  "'nic dalsiho neni'." % mimo)
        save_json(STATE, stav)
        return

    if args.verdikty:
        verdikty(args.verdikty, cfg, modul, sesit, stav, args.zapis)
        if args.zapis:
            sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
        save_json(STATE, stav)
        return

    dnu = args.dnu or cfg["objevy"]["dnu_zpet"]
    mez = (dt.date.today() - dt.timedelta(days=dnu)).isoformat()

    vypis("")
    vypis("=" * 62)
    vypis("  " + T["objevy_nadpis"] + "  (vznik od %s)" % mez)
    vypis("=" * 62)

    nalezeno, siroke = najdi(cfg, mez)
    vypis("V rejstriku pribylo od meze: %d" % len(nalezeno))
    for nace, pf, chyba in siroke:
        vypis("  NEPROHLEDANO %s x %s - %s" % (nace, pf, chyba))

    znama = znama_ica(sesit, cfg)
    pamet = stav.get("objevy", {})
    kandidati = {i: k for i, k in nalezeno.items()
                 if i not in znama and i not in pamet}
    vypis("Uz v databazi (vcetne vyrazenych): %d" % sum(1 for i in nalezeno if i in znama))
    vypis("Uz jednou posouzeno drive:         %d" % sum(1 for i in nalezeno if i in pamet))
    vypis("ZBYVA POSOUDIT:                    %d" % len(kandidati))

    if not kandidati:
        vypis("")
        vypis(T["objevy_zadny"])
        return

    davka, mimo = priprav(kandidati, cfg, stav)
    vypis("")
    vypis("Pripraveno k posouzeni: %d (slozka k-posouzeni)" % davka)
    if mimo:
        vypis("POZOR: %d kandidatu se do davky neveslo - neni to 'nic dalsiho neni'."
              % mimo)
    save_json(STATE, stav)


if __name__ == "__main__":
    main()
