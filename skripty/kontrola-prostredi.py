# -*- coding: utf-8 -*-
"""
kontrola-prostredi.py - projde, jestli na tomhle pocitaci pobezi mesicni beh.

Duvod, proc to existuje: v srpnu 2026 se osm dni vedlo jako blokujici, ze ARES
a ISIR jsou nedostupne. Nebyly - jen se to testovalo v jinem prostredi, nez
ve kterem to melo bezet. Dostupnost zdroje se ma overit tam, kde to pobezi.

Pouziti:
    dvojklik na KONTROLA.cmd
    nebo: python kontrola-prostredi.py

Vsechny ceske texty jsou v kontrola-prostredi.texty.json, aby tenhle soubor
zustal ciste ASCII a neprosypalo se kodovani pri prenosu.
"""

import io
import json
import os
import socket
import ssl
import sys
import urllib.error
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
TEXTY = os.path.join(HERE, "kontrola-prostredi.texty.json")
CONFIG = os.path.join(HERE, "financovani-beh.config.json")

SIRKA = 66


def nacti(path):
    with io.open(path, "r", encoding="utf-8-sig") as f:
        return json.load(f)


def vypis(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


class Prehled(object):
    """Sbira vysledky. Chyba = neprojde to. Varovani = projde, ale slepe."""

    def __init__(self, T):
        self.T = T
        self.chyby = 0
        self.varovani = 0

    def _radek(self, znacka, text):
        prvni = True
        for r in text.split("\n"):
            vypis("  %-6s %s" % (znacka if prvni else "", r))
            prvni = False

    def ok(self, text):
        self._radek("[" + self.T["ok"] + "]", text)

    def chyba(self, text):
        self.chyby += 1
        self._radek("[" + self.T["chyba"] + "]", text)

    def varuj(self, text):
        self.varovani += 1
        self._radek("[" + self.T["varovani"] + "]", text)


def zkus_sit(p, T, jmeno, funkce):
    try:
        funkce()
        p.ok(T["sit_ok"].format(jmeno=jmeno))
        return True
    except Exception as e:
        duvod = type(e).__name__
        if isinstance(e, urllib.error.HTTPError):
            duvod = "HTTP %s" % e.code
        p.chyba(T["sit_chyba"].format(jmeno=jmeno, duvod=duvod))
        return False


def main():
    T = nacti(TEXTY)
    p = Prehled(T)

    vypis("")
    vypis("=" * SIRKA)
    vypis("  " + T["nadpis"])
    vypis("=" * SIRKA)
    vypis("  " + T["podnadpis"])
    vypis("")

    # 1 - Python
    v = "%d.%d.%d" % sys.version_info[:3]
    if sys.version_info[:2] >= (3, 8):
        p.ok(T["python_verze"].format(verze=v))
    else:
        p.chyba(T["python_stary"].format(verze=v))

    # 2, 3 - knihovny
    for jmeno in ("openpyxl", "certifi"):
        try:
            __import__(jmeno)
            p.ok(T["knihovna_ok"].format(jmeno=jmeno))
        except ImportError:
            p.chyba(T["knihovna_chybi"].format(jmeno=jmeno))

    # 4 - master sesit
    cfg = None
    try:
        cfg = nacti(CONFIG)
    except Exception:
        p.chyba("financovani-beh.config.json chybi nebo je poskozeny")

    if cfg:
        cesta = cfg["master"]
        if not os.path.isfile(cesta):
            p.chyba(T["master_chybi"].format(cesta=cesta))
        else:
            try:
                import openpyxl
                wb = openpyxl.load_workbook(cesta, read_only=True, data_only=True)
                nazev = cfg["listy"]["subjekty"]
                ws = wb[nazev]
                pocet = sum(1 for r in ws.iter_rows(min_row=2, values_only=True)
                            if r and r[0] is not None)
                wb.close()
                p.ok(T["master_ok"].format(pocet=pocet, list=nazev))
            except PermissionError:
                p.chyba(T["master_zamceny"])
            except Exception as e:
                p.chyba("Master sesit se nepodarilo nacist: %s" % type(e).__name__)

    # 5 - zapis do slozky behu
    zkusebni = os.path.join(HERE, "_zkouska-zapisu.tmp")
    try:
        with io.open(zkusebni, "w", encoding="utf-8") as f:
            f.write("test")
        os.remove(zkusebni)
        p.ok(T["zapis_ok"])
    except Exception:
        p.chyba(T["zapis_chyba"].format(cesta=HERE))

    # 6 az 9 - sit. Tohle je ta cast, kvuli ktere kontrola existuje.
    try:
        import certifi
        ctx = ssl.create_default_context(cafile=certifi.where())
    except ImportError:
        ctx = ssl.create_default_context()
    socket.setdefaulttimeout(20)
    ua = {"User-Agent": "Mozilla/5.0 salutem-kontrola/1.0"}

    def get(url, data=None, hlavicky=None):
        h = dict(ua)
        if hlavicky:
            h.update(hlavicky)
        req = urllib.request.Request(url, data=data, headers=h)
        return urllib.request.urlopen(req, timeout=20, context=ctx).read()

    ep = (cfg or {}).get("endpointy", {})

    def ares():
        telo = get(ep.get("ares", "").format(ico="03328074"))
        if b"obchodniJmeno" not in telo:
            raise ValueError("neocekavana odpoved")

    def isir():
        zprava = (
            '<soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" '
            'xmlns:typ="http://isirws.cca.cz/types/"><soapenv:Header/><soapenv:Body>'
            "<typ:getIsirWsCuzkDataRequest><ic>08670994</ic>"
            "<maxPocetVysledku>5</maxPocetVysledku>"
            "<filtrAktualniRizeni>F</filtrAktualniRizeni>"
            "</typ:getIsirWsCuzkDataRequest></soapenv:Body></soapenv:Envelope>"
        ).encode("utf-8")
        telo = get(ep.get("isir"), data=zprava,
                   hlavicky={"Content-Type": "text/xml;charset=UTF-8", "SOAPAction": ""})
        if b"getIsirWsCuzkDataResponse" not in telo:
            raise ValueError("neocekavana odpoved")

    def rpo():
        telo = get(ep.get("rpo_sk_hledani", "").format(ico="35842369"))
        if b"results" not in telo:
            raise ValueError("neocekavana odpoved")

    def web():
        get("https://www.cnb.cz/cs/")

    if cfg:
        zkus_sit(p, T, T["ares_jmeno"], ares)
        zkus_sit(p, T, T["isir_jmeno"], isir)
        # RPO neni blokujici - bez nej se jen nezkontroluji slovenske subjekty
        pred = p.chyby
        if not zkus_sit(p, T, T["rpo_jmeno"], rpo):
            p.chyby = pred
            p.varovani += 1
            vypis("         " + T["rpo_varovani"])
        zkus_sit(p, T, T["web_jmeno"], web)

    vypis("")
    vypis("=" * SIRKA)
    if p.chyby:
        vypis("  " + T["vysledek_chyba"])
    elif p.varovani:
        vypis("  " + T["vysledek_varovani"])
    else:
        vypis("  " + T["vysledek_ok"])
    vypis("=" * SIRKA)
    vypis("")
    return 1 if p.chyby else 0


if __name__ == "__main__":
    sys.exit(main())
