# -*- coding: utf-8 -*-
"""Dohleda kontakt subjektum, ktere v databazi zadny nemaji.

PROC EXISTUJE
Databaze investoru, na kterou neni koho zavolat, je jen seznam. K 1. 9. 2026
nema ani jeden kontakt 108 aktivnich subjektu ze 168 - vetsinu z nich pribyla
investorska strana ze seznamu CNB, kde se sbiralo, do CEHO fond investuje,
ne KOMU napsat.

JAK TO HLEDA
Stejnym zpusobem jako dohledavani ICO: cte web subjektu. Prochazi hlavni
stranku a podstranky s kontakty, sbira odkazy mailto: a tel: a k tomu adresy
psane v textu.

CO JE DOKLAD TOTOZNOSTI
U ICO je to shoda nazvu proti ARESu. Tady je to DOMENA: adresa na vlastni
domene subjektu je prokazatelne jeho. Adresa na cizi domene - typicky spravce
fondu (avantfunds.cz, amista.cz) - je kontakt na nekoho jineho, i kdyz stoji
na jeho strance. Proto:

  JISTE      e-mail na vlastni domene subjektu           -> da se zapsat
  NEJISTE    e-mail nalezen, ale na cizi domene          -> rozhodne clovek
  NENALEZENO na webu zadny kontakt neni                  -> zustava prazdne

Nikdy se nehada a NIKDY se nedoplnuje jmeno osoby. Skript zapisuje jen to,
co je na strance cerne na bilem - e-mail a telefon. Sloupec "Jmeno a pozice"
zustava prazdny pro cloveka; tvarit se, ze vime, s kym mluvime, by bylo horsi
nez prazdno.

TELEFON se bere jen z odkazu tel: nebo kdyz ma predvolbu +420 / +421.
Osmiciferne cislo v textu muze byt ICO, datum i cislo uctu.

POUZITI
    python financovani-dohledat-kontakt.py            # jen vypise, co nasel
    python financovani-dohledat-kontakt.py --zapis    # zapise jen JISTE nalezy
    python financovani-dohledat-kontakt.py --limit 10 # jen prvnich N (zkouska)
"""

import argparse
import html
import importlib.util
import io
import json
import os
import re
import socket
import ssl
import time
import urllib.parse
import urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
CONFIG = os.path.join(HERE, "financovani-beh.config.json")
TEXTY = os.path.join(HERE, "financovani-dohledat-kontakt.texty.json")

T = {}
VZ = {}


def vypis(text):
    try:
        print(text)
    except UnicodeEncodeError:
        print(text.encode("ascii", "replace").decode("ascii"))


def nacti_vzory(cfg):
    d = cfg["dohledani_kontaktu"]
    VZ["email"] = re.compile(d["vzor_email"], re.I)
    VZ["tel_odkaz"] = re.compile(d["vzor_telefon_odkaz"], re.I)
    VZ["tel_text"] = re.compile(d["vzor_telefon_text"])
    VZ["podstranky"] = d["podstranky"]
    VZ["obecne"] = set(x.lower() for x in d["obecne_schranky"])
    VZ["nezajimave"] = tuple(x.lower() for x in d["nezajimave_pripony"])


def domena(url):
    u = re.sub(r"\s+", " ", str(url or "")).strip().lower()
    u = re.sub(r"^https?://", "", u)
    u = u.split()[0] if u else ""
    u = re.sub(r"^www\.", "", u)
    return u.split("/")[0].strip().strip(".")


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


def uklid_mail(m):
    """Z odkazu leze mailto: a %20 - to nejsou soucasti adresy."""
    m = urllib.parse.unquote(html.unescape(str(m or ""))).strip()
    m = re.sub(r"^\s*mailto:\s*", "", m, flags=re.I)
    m = m.strip().strip(".,;:<>()[]\"'").strip()
    m = m.replace("[at]", "@").replace("(at)", "@").replace("[zavinac]", "@")
    return m.lower()


def uklid_tel(t):
    """Normalizuje na +420/+421. Cislo bez predvolby nezapisujeme.

    Z webu leze 00420..., ++800..., 420224931617 i holych devet cislic.
    Zapsat takovy tvar do databaze znamena, ze na nej jednou nekdo vytoci
    a bude si myslet, ze cislo neplati. Radeji prazdno.
    """
    c = re.sub(r"[^\d+]", "", str(t or ""))
    if c.startswith("++"):
        return ""       # dve plus je preklep na strance, ne predvolba
    if c.startswith("00"):
        c = "+" + c[2:]
    if not c.startswith("+"):
        if re.match(r"^42[01]\d{9}$", c):
            c = "+" + c
        else:
            return ""   # bez predvolby nevime, do jake zeme cislo patri
    cislice = re.sub(r"\D", "", c)
    if len(cislice) < 9 or len(cislice) > 15:
        return ""       # 9 cislic je nejkratsi rozumne mezinarodni cislo
    return c


def kontakty_ze_stranky(h):
    """Vraci (maily, telefony) z jedne stranky. Odkazy maji prednost."""
    maily, tel = [], []
    for m in re.finditer(r'mailto:([^"\'>\s?]+)', h, re.I):
        maily.append(uklid_mail(m.group(1)))
    for m in VZ["tel_odkaz"].finditer(h):
        tel.append(re.sub(r"[^\d+]", "", html.unescape(m.group(1))))
    cisty = html.unescape(re.sub(r"<[^>]+>", " ", h))
    for m in VZ["email"].finditer(cisty):
        maily.append(uklid_mail(m.group(0)))
    for m in VZ["tel_text"].finditer(cisty):
        tel.append(re.sub(r"[^\d+]", "", m.group(0)))
    cist_m, videno = [], set()
    for x in maily:
        if not x or "@" not in x or x in videno:
            continue
        if x.rsplit(".", 1)[-1] in ("png", "jpg", "jpeg", "gif", "webp", "svg"):
            continue
        if x.endswith(VZ["nezajimave"]):
            continue
        videno.add(x)
        cist_m.append(x)
    cist_t, videno = [], set()
    for x in tel:
        x = uklid_tel(x)
        if not x or x in videno:
            continue
        videno.add(x)
        cist_t.append(x)
    return cist_m, cist_t


def prohledej(web, ua, ctx):
    zaklad = str(web or "").strip().rstrip("/")
    if not zaklad.startswith("http"):
        zaklad = "https://" + zaklad
    maily, tel, kde = [], [], ""
    for cesta in VZ["podstranky"]:
        h = stahni(zaklad + cesta, ua, ctx)
        if not h:
            continue
        m, t = kontakty_ze_stranky(h)
        if m or t:
            maily, tel, kde = m, t, (zaklad + cesta)
            if m:
                break          # mail je cil, telefon sam o sobe nestaci
        time.sleep(0.2)
    return maily, tel, kde


def vyber_mail(maily, dom):
    """Vraci (vlastni, cizi). Vlastni = na domene subjektu, tedy doklad."""
    vlastni = [m for m in maily
               if m.split("@")[-1] == dom or m.split("@")[-1].endswith("." + dom)]
    cizi = [m for m in maily if m not in vlastni]
    # Poradi: osobni adresa, pak obecna schranka, pak oddelenska.
    # Prvni verze radila jen "neobecna napred" a tim vytahla nahoru hr@,
    # poland@ nebo penze@ - oddeleni, ktera s nami mluvit nebudou. Obecne
    # info@ je proti nim lepsi vychozi adresa.
    def poradi(mail):
        lok = mail.split("@")[0].lower()
        if "." in lok:
            return 0        # jmeno.prijmeni@ - konkretni clovek
        if lok in VZ["obecne"]:
            return 1        # info@, office@ - podatelna, ale spravna
        return 2            # hr@, poland@, penze@ - jine oddeleni
    vlastni.sort(key=poradi)
    return vlastni, cizi


def main():
    ap = argparse.ArgumentParser(description="Dohleda kontakt podle webu subjektu")
    ap.add_argument("--zapis", action="store_true", help="zapsat jen jiste nalezy")
    ap.add_argument("--master", help="jina cesta k sesitu (test)")
    ap.add_argument("--limit", type=int, help="jen prvnich N subjektu")
    ap.add_argument("--vynech", default="", help="ID subjektu, ktere nezapisovat")
    args = ap.parse_args()

    spec = importlib.util.spec_from_file_location(
        "financovani_beh", os.path.join(HERE, "financovani-beh.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    cfg = json.load(io.open(CONFIG, encoding="utf-8"))
    T.update(json.load(io.open(TEXTY, encoding="utf-8")))
    m.T.update(cfg["texty"])
    nacti_vzory(cfg)
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

    maji = set(m.norm(d.get("id")) for _, d in sesit.radky("kontakty"))
    vyrazen = cfg["stavy"]["vyrazen"]
    chybi = [(r, d) for r, d in sesit.radky("subjekty")
             if m.norm(d.get("stav")) != vyrazen
             and m.norm(d.get("id")) not in maji
             and m.norm(d.get("web"))]
    bez_webu = [d for _, d in sesit.radky("subjekty")
                if m.norm(d.get("stav")) != vyrazen
                and m.norm(d.get("id")) not in maji
                and not m.norm(d.get("web"))]
    if args.limit:
        chybi = chybi[:args.limit]

    vypis("Aktivnich subjektu bez kontaktu, ktere maji web: %d" % len(chybi))
    vypis("Bez webu (timhle zpusobem nedohledatelne): %d" % len(bez_webu))
    vypis("")

    jiste, nejiste, nenalezeno = [], [], []
    for radek, d in chybi:
        sid, nazev, web = m.norm(d.get("id")), m.norm(d.get("nazev")), m.norm(d.get("web"))
        dom = domena(web)
        maily, tel, kde = prohledej(web, ua, ctx)
        vlastni, cizi = vyber_mail(maily, dom)
        telefon = tel[0] if tel else ""
        if vlastni:
            jiste.append((sid, nazev, vlastni[0], telefon, kde, dom))
            znak = "OK" if vlastni[0].split("@")[0].lower() not in VZ["obecne"] else "ok"
            vypis("  #%-5s %-38s %s  %-34s %s"
                  % (sid, nazev[:38], znak, vlastni[0][:34], telefon))
        elif cizi or telefon:
            nejiste.append((sid, nazev, cizi[0] if cizi else "", telefon, kde, dom))
            vypis("  #%-5s %-38s ??  %-34s %s"
                  % (sid, nazev[:38], (cizi[0] if cizi else "(jen telefon)")[:34], telefon))
        else:
            nenalezeno.append((sid, nazev, web))
            vypis("  #%-5s %-38s --  na webu zadny kontakt" % (sid, nazev[:38]))
        time.sleep(0.15)

    vypis("")
    vypis("=" * 74)
    vypis("  JISTE (adresa na vlastni domene, da se zapsat): %d" % len(jiste))
    vypis("  NEJISTE (cizi domena nebo jen telefon):         %d" % len(nejiste))
    vypis("  NENALEZENO:                                     %d" % len(nenalezeno))
    vypis("=" * 74)
    if nejiste:
        vypis("K rozhodnuti (adresa nesedi na domenu subjektu):")
        for sid, nazev, mail, tel_, kde, dom in nejiste:
            vypis("  #%s  %s  (domena %s)" % (sid, nazev, dom))
            vypis("       nalezeno: %s %s   zdroj: %s" % (mail or "-", tel_ or "", kde))

    if not args.zapis:
        vypis("")
        vypis("Nic nezapsano. Pro zapis JISTYCH nalezu pridej --zapis")
        return

    vynechat = set(x.strip() for x in args.vynech.split(",") if x.strip())
    if vynechat:
        drzene = [z for z in jiste if z[0] in vynechat]
        jiste = [z for z in jiste if z[0] not in vynechat]
        for sid, nazev, mail, tel_, kde, dom in drzene:
            vypis("  VYNECHANO na pokyn: #%s %s (%s)" % (sid, nazev, mail))

    ws = sesit.ws("kontakty")
    i_mail = sesit.sl("kontakty", "email")
    i_tel = sesit.sl("kontakty", "telefon")
    i_over = sesit.sl("kontakty", "overeno")
    for sid, nazev, mail, tel_, kde, dom in jiste:
        r = m.najdi_radek(sesit, "kontakty", sid) or m.zaloz_radek(
            sesit, "kontakty", sid, nazev)
        if i_mail:
            ws.cell(row=r, column=i_mail).value = mail
        if i_tel and tel_:
            ws.cell(row=r, column=i_tel).value = tel_
        if i_over:
            ws.cell(row=r, column=i_over).value = m.DNES
        i_pozn = sesit.sl("kontakty", "poznamka")
        if i_pozn:
            ws.cell(row=r, column=i_pozn).value = T["kontakt_poznamka"].format(
                datum=m.DNES, zdroj=kde)
        m.zapis_zdroj(sesit, sid, nazev, T["pole_kontakt"],
                      T["kontakt_citace"].format(mail=mail, dom=dom), kde)
    sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
    vypis("Zapsano kontaktu: %d." % len(jiste))


if __name__ == "__main__":
    main()
