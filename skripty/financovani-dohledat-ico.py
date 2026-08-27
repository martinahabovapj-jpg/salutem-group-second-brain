# -*- coding: utf-8 -*-
"""Dohleda ICO subjektum, ktere ho v databazi nemaji.

PROC EXISTUJE
Subjekt bez ICO se v rejstriku nezkontroluje - neni se na co zeptat. Web mu
mesicni beh hlida, ale insolvenci, zanik ani likvidaci nepozna. Vsech 26
takovych subjektu v databazi prislo z rucni reserse, kde ICO nebylo, a
z ARESu se nedohledalo podle jmena: na "PKF APOGEO" vraci tricet firem
a prirazeni spatne by znamenalo, ze se beh pta rejstriku na cizi subjekt.

JAK TO OBCHAZI
Nehleda podle jmena, ale podle WEBU. Firmy uvadeji ICO v paticce, na
strance kontaktu nebo v obchodnich podminkach. Nalezene cislo se pak overi
proti ARESu - a teprve kdyz sedi i NAZEV, povazuje se za dolozene.

TRI VYSLEDKY
  JISTE     ICO z webu, ARES ho zna a nazev odpovida        -> da se zapsat
  NEJISTE   ICO z webu, ARES ho zna, ale nazev nesedi       -> rozhodne clovek
  NENALEZENO na webu zadne ICO neni                         -> zustava prazdne

Nikdy se nehada. Radeji prazdne ICO nez cizi firma - tahle chyba v projektu
uz dvakrat nastala (radek #143 dostal ICO fondu, radek #26 roli cizi firmy).

POUZITI
    python financovani-dohledat-ico.py            # jen vypise, co nasel
    python financovani-dohledat-ico.py --zapis    # zapise jen JISTE nalezy
"""

import argparse
import io
import json
import os
import re
import socket
import ssl
import time
import unicodedata
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "financovani-beh.config.json")
ARES_DETAIL = "https://ares.gov.cz/ekonomicke-subjekty-v-be/rest/ekonomicke-subjekty/%s"

T = {}


def vypis(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def norm(v):
    if v is None:
        return ""
    return re.sub(r"\s+", " ", str(v)).strip()


def zjednodus(jmeno):
    """Nazev bez pravni formy, diakritiky a interpunkce, pro porovnavani."""
    t = unicodedata.normalize("NFKD", norm(jmeno))
    t = "".join(c for c in t if not unicodedata.combining(c)).lower()
    t = re.sub(r"\b(a\.?\s?s\.?|s\.?\s?r\.?\s?o\.?|spol\.?\s?s\s?r\.?\s?o\.?|se|"
               r"k\.?s\.?|v\.?o\.?s\.?|sicav|o\.?c\.?p\.?|z\.?s\.?|group|holding|"
               r"investicni spolecnost|podfond|fond)\b", " ", t)
    t = re.sub(r"[^a-z0-9]+", " ", t)
    return re.sub(r"\s+", " ", t).strip()


def podobnost(a, b):
    """Podil spolecnych slov k tomu kratsimu z nazvu. 0 az 1."""
    sa, sb = set(zjednodus(a).split()), set(zjednodus(b).split())
    if not sa or not sb:
        return 0.0
    return len(sa & sb) / float(min(len(sa), len(sb)))


# ---------------------------------------------------------------- web

# vzory a podstranky jsou v konfiguraci (sekce dohledani_ica) - v .py zdrojaku
# diakritika byt nesmi a "ICO" bez ni na ceskych webech nenajde nic
ICO_VZOR = None
DIC_VZOR = None
PODSTRANKY = ()


def nacti_vzory(cfg):
    global ICO_VZOR, DIC_VZOR, PODSTRANKY
    d = cfg["dohledani_ica"]
    ICO_VZOR = re.compile(d["vzor_ico"], re.I)
    DIC_VZOR = re.compile(d["vzor_dic"])
    PODSTRANKY = tuple(d["podstranky"])


def stahni(url, ua, ctx):
    try:
        req = urllib.request.Request(url, headers={"User-Agent": ua,
                                                   "Accept-Language": "cs,en"})
        telo = urllib.request.urlopen(req, timeout=20, context=ctx).read()
    except Exception:
        return ""
    for kod in ("utf-8", "cp1250", "iso-8859-2"):
        try:
            return telo.decode(kod)
        except UnicodeDecodeError:
            continue
    return telo.decode("utf-8", "replace")


def ica_z_webu(web, ua, ctx):
    """Vraci [(ico, kde_to_bylo)] serazene podle duveryhodnosti nalezu."""
    zaklad = norm(web).rstrip("/")
    if not zaklad.startswith("http"):
        zaklad = "https://" + zaklad
    nalezy = []
    videna = set()
    for cesta in PODSTRANKY:
        h = stahni(zaklad + cesta, ua, ctx)
        if not h:
            continue
        # text bez znacek, aby ICO rozdelene do <span> slo najit taky
        cisty = re.sub(r"<[^>]+>", " ", h)
        for vzor, popis in ((ICO_VZOR, "u popisku ICO"), (DIC_VZOR, "z DIC")):
            for m in vzor.finditer(cisty):
                ico = m.group(1)
                if ico in videna:
                    continue
                videna.add(ico)
                nalezy.append((ico, "%s%s (%s)" % (cesta or "/", "", popis)))
        if nalezy:
            break          # kdyz uz neco mame, dalsi podstranky nejsou treba
        time.sleep(0.2)
    return nalezy


def ares_detail(ico, ua, ctx):
    try:
        req = urllib.request.Request(ARES_DETAIL % ico,
                                     headers={"Accept": "application/json", "User-Agent": ua})
        return json.load(urllib.request.urlopen(req, timeout=25, context=ctx))
    except Exception:
        return None


# ---------------------------------------------------------------- main

def main():
    ap = argparse.ArgumentParser(description="Dohleda ICO podle webu subjektu")
    ap.add_argument("--zapis", action="store_true", help="zapsat jen jiste nalezy")
    ap.add_argument("--master", help="jina cesta k sesitu (test)")
    ap.add_argument("--vynech", default="",
                    help="ID subjektu, ktere se nemaji zapsat, oddelena carkou")
    ap.add_argument("--prah", type=float,
                    help="od jake shody nazvu se nalez povazuje za jisty (0-1)")
    args = ap.parse_args()

    import importlib.util
    spec = importlib.util.spec_from_file_location(
        "financovani_beh", os.path.join(HERE, "financovani-beh.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cfg = json.load(io.open(CONFIG, encoding="utf-8"))
    T.update(cfg["texty"])
    m.T.update(cfg["texty"])
    nacti_vzory(cfg)
    prah = args.prah if args.prah else cfg["dohledani_ica"]["prah_shody"]
    if args.master:
        cfg["master"] = args.master
    sesit = m.Sesit(cfg)

    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    ua = cfg["sit"]["user_agent"]
    socket.setdefaulttimeout(cfg["sit"]["timeout_s"])

    vyrazen = cfg["stavy"]["vyrazen"]
    chybi = [(r, d) for r, d in sesit.radky("subjekty")
             if norm(d.get("stav")) != vyrazen
             and not re.search(r"\d{8}", str(d.get("ico") or ""))
             and norm(d.get("web"))]
    vypis("Subjektu bez ICO, ktere maji web: %d" % len(chybi))
    vypis("")

    jiste, nejiste, nenalezeno = [], [], []
    for radek, d in chybi:
        sid, nazev, web = norm(d.get("id")), norm(d.get("nazev")), norm(d.get("web"))
        nalezy = ica_z_webu(web, ua, ctx)
        if not nalezy:
            nenalezeno.append((radek, sid, nazev, web))
            vypis("  #%-4s %-32s -- na webu zadne ICO" % (sid, nazev[:32]))
            continue
        nejlepsi = None
        for ico, kde in nalezy:
            det = ares_detail(ico, ua, ctx)
            if not det:
                continue
            ares_nazev = norm(det.get("obchodniJmeno"))
            sh = podobnost(nazev, ares_nazev)
            if nejlepsi is None or sh > nejlepsi[2]:
                nejlepsi = (ico, ares_nazev, sh, kde)
            time.sleep(0.1)
        if nejlepsi is None:
            nenalezeno.append((radek, sid, nazev, web))
            vypis("  #%-4s %-32s -- ICO na webu je, ARES ho nezna" % (sid, nazev[:32]))
            continue
        ico, ares_nazev, sh, kde = nejlepsi
        if sh >= prah:
            jiste.append((radek, sid, nazev, ico, ares_nazev, sh, web))
            vypis("  #%-4s %-32s OK  %s  %s (shoda %.0f%%)"
                  % (sid, nazev[:32], ico, ares_nazev[:34], sh * 100))
        else:
            nejiste.append((radek, sid, nazev, ico, ares_nazev, sh, web))
            vypis("  #%-4s %-32s ??  %s  %s (shoda %.0f%%)"
                  % (sid, nazev[:32], ico, ares_nazev[:34], sh * 100))
        time.sleep(0.15)

    vypis("")
    vypis("=" * 68)
    vypis("  JISTE (nazev sedi, da se zapsat):  %d" % len(jiste))
    vypis("  NEJISTE (rozhodne clovek):         %d" % len(nejiste))
    vypis("  NENALEZENO:                        %d" % len(nenalezeno))
    vypis("=" * 68)
    if nejiste:
        vypis("K rozhodnuti:")
        for radek, sid, nazev, ico, an, sh, web in nejiste:
            vypis("  #%s  v databazi '%s'" % (sid, nazev))
            vypis("       na webu ICO %s = '%s' (shoda %.0f%%)" % (ico, an, sh * 100))

    if not args.zapis:
        vypis("")
        vypis("Nic nezapsano. Pro zapis JISTYCH nalezu pridej --zapis")
        return

    vynechat = set(x.strip() for x in args.vynech.split(",") if x.strip())
    if vynechat:
        drzene = [z for z in jiste if z[1] in vynechat]
        jiste = [z for z in jiste if z[1] not in vynechat]
        for radek, sid, nazev, ico, an, sh, web in drzene:
            vypis("  VYNECHANO na pokyn: #%s %s (nabizene ICO %s = '%s')"
                  % (sid, nazev, ico, an))

    ws = sesit.ws("subjekty")
    i_ico = sesit.sl("subjekty", "ico")
    for radek, sid, nazev, ico, ares_nazev, sh, web in jiste:
        ws.cell(row=radek, column=i_ico).value = ico
        m.pripis_poznamku(sesit, radek, T["ico_dohledano"].format(
            datum=m.DNES, ico=ico, nazev=ares_nazev, web=web))
        m.zapis_zdroj(sesit, sid, nazev, T["pole_ico"],
                      T["ico_citace"].format(ico=ico, nazev=ares_nazev), web)
    sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
    vypis("Zapsano ICO u %d subjektu." % len(jiste))


if __name__ == "__main__":
    main()
