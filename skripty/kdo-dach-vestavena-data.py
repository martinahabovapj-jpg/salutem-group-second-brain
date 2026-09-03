# -*- coding: utf-8 -*-
"""Obnovi vestavena data ve vyhledavaci Kdo_mi_to_zafinancuje_DACH.html z DACH sesitu.

Vyhledavac (SheetJS v prohlizeci) si sesit nacita zivé, ale bez pripojeneho souboru
ukazuje vestavenou zalohu - literal VESTAVENA_JSON v HTML. Tenhle skript ji prepocita
stejne, jako to dela funkce parseWorkbook v HTML (stejna pole, stejne sloupce), a
prepise literal. Nic jineho v HTML nemeni.

DACH verze vyhledavace se od ceske (_LIVE.html, kolegu, NESAHAT) lisi tim, ze skryva
radky s PRAZDNOU "Role: financovani" (cisti investori) a pocita v EUR.

  python kdo-dach-vestavena-data.py                     # cte sesit z konfigurace, prepise HTML na O:
  python kdo-dach-vestavena-data.py --html cesta.html   # jiny cil (test)
"""
import argparse, io, json, os, re, datetime
import openpyxl

HERE = os.path.dirname(os.path.abspath(__file__))
COL2FLAG = {"Senior": "senior", "Whole loan": "whole_loan", "Junior": "junior", "Mezzanine": "mezzanine",
            "Bridge": "bridge", "Pref. equity": "preferred_equity", "Development": "development_finance",
            "Akviziční": "acquisition_finance", "Refinancování": "refinancing", "NAV lending": "nav_lending",
            "Financuje SPV": "financuje_spv", "Financuje fondy": "financuje_fondy"}


def num(v):
    if v in (None, ""): return None
    if isinstance(v, (int, float)): return v
    s = str(v).lower(); mld = bool(re.search(r"mld|miliard", s)); mil = bool(re.search(r"mil|milion", s))
    m = re.search(r"(\d[\d\s.,]*)", s)
    if not m: return None
    x = re.sub(r"\.(?=\d{3}\b)", "", m.group(1).replace(" ", "")).replace(",", ".")
    try: n = float(x)
    except ValueError: return None
    return n * 1e9 if mld else n * 1e6 if mil else n


def pct(v):
    if v in (None, ""): return None
    m = re.search(r"(\d{1,3})", str(v)); return int(m.group(1)) if m else None


def data(cesta):
    wb = openpyxl.load_workbook(cesta, read_only=True, data_only=True)
    def rows(name):
        ws = wb[name]; r = list(ws.iter_rows(values_only=True)); h = [str(x).strip() if x is not None else "" for x in r[0]]
        return [{h[i]: ("" if v is None else v) for i, v in enumerate(x) if i < len(h)} for x in r[1:] if any(c not in (None, "") for c in x)]
    S, K, F, Z = rows("1 Subjekty"), rows("2 Kontakty"), rows("3 Role Financování"), rows("4 Zdroje")
    by = {}
    for r in S:
        sid = str(r.get("ID", "")).strip()
        if not sid or not str(r.get("Název", "")).strip(): continue
        fin = str(r.get("Role: financování", "")).strip().upper()
        vyr = str(r.get("Stav", "")).strip().upper() == "VYŘAZEN" or fin in ("NE", "")
        pozn = str(r.get("Poznámka", ""))
        by[sid] = {"id": sid, "nazev": str(r["Název"]).strip(), "ico": str(r.get("IČO", "")).strip(), "zeme": str(r.get("Země", "")).strip(),
                   "skupina": str(r.get("Skupina", "")).strip(), "typ": str(r.get("Typ subjektu", "")).strip(), "web": str(r.get("Web", "")).strip(),
                   "stav": str(r.get("Stav", "")).strip(), "confidence": "A" if str(r.get("Doložení", "B")).strip().upper() == "A" else "B",
                   "overeno": str(r.get("Ověřeno", "")).strip()[:10], "poznamka": pozn.strip(),
                   "vyrad": ("investor bez doložené role poskytovatele financování" if fin == "" else (pozn.split(" | ")[0] or "vyřazen")) if vyr else "",
                   "flagy": {f: "NEZNAMO" for f in COL2FLAG.values()}, "citace": [], "osoba": "", "tel": "", "email": "",
                   "tmin": None, "tmax": None, "tmin_txt": "", "tmax_txt": "", "ltv": None, "ltv_txt": "", "ac": [], "aktivita": "", "aktivita_url": ""}
    for r in K:
        s = by.get(str(r.get("ID subjektu", "")).strip())
        if not s: continue
        for src, dst in (("Jméno a pozice", "osoba"), ("Telefon", "tel"), ("E-mail", "email")):
            if not s[dst] and str(r.get(src, "")).strip(): s[dst] = str(r[src]).strip()
    for r in F:
        s = by.get(str(r.get("ID", "")).strip())
        if not s: continue
        for col, f in COL2FLAG.items():
            if str(r.get(col, "")).strip().upper() == "ANO": s["flagy"][f] = "ANO"
        s["tmin_txt"] = str(r.get("Ticket od", "")).strip(); s["tmax_txt"] = str(r.get("Ticket do", "")).strip()
        s["tmin"] = num(s["tmin_txt"]); s["tmax"] = num(s["tmax_txt"])
        s["ltv_txt"] = str(r.get("LTV max", "")).strip(); s["ltv"] = pct(s["ltv_txt"])
        s["ac"] = [x.strip() for x in str(r.get("Typy aktiv", "")).split(",") if x.strip()]
        s["aktivita"] = str(r.get("Poslední doložená aktivita", "")).strip()
    for r in Z:
        s = by.get(str(r.get("ID subjektu", "")).strip())
        if not s: continue
        lbl = str(r.get("K čemu se váže", "")).strip()
        if lbl == "aktivita":
            if not s["aktivita_url"]: s["aktivita_url"] = str(r.get("URL", "")).strip()
            continue
        f = COL2FLAG.get(lbl)
        if f and str(r.get("Doslovná citace", "")).strip() and str(r.get("URL", "")).strip():
            s["citace"].append({"f": f, "t": str(r["Doslovná citace"]).strip(), "u": str(r["URL"]).strip()})
    return list(by.values())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="financovani-beh-dach.config.json")
    ap.add_argument("--html", default=None)
    a = ap.parse_args()
    with io.open(os.path.join(HERE, a.config), encoding="utf-8") as f: cfg = json.load(f)
    html = a.html or os.path.join(os.path.dirname(cfg["master"]), "Kdo_mi_to_zafinancuje_DACH.html")
    d = data(cfg["master"]); akt = [x for x in d if not x["vyrad"]]
    t = io.open(html, encoding="utf-8").read()
    m = re.search(r"(const|let|var)\s+VESTAVENA_JSON\s*=", t); s0 = m.end(); e = t.find("];", s0) + 1
    t = t[:s0] + " " + json.dumps(d, ensure_ascii=False) + t[e:]
    dnes = datetime.date.today(); t = re.sub(r"\d{1,2}\. \d{1,2}\. 2026", "%d. %d. %d" % (dnes.day, dnes.month, dnes.year), t)
    io.open(html, "w", encoding="utf-8", newline="\n").write(t)
    print("Vestavena data: %d subjektu, %d veritelu, ticket u %d, LTV u %d -> %s" % (
        len(d), len(akt), sum(1 for x in akt if x["tmin"] or x["tmax"]), sum(1 for x in akt if x["ltv"]), html))


if __name__ == "__main__":
    main()
