# -*- coding: utf-8 -*-
"""Vytezi seznam FINMA (bewilligte Fondsleitungen a Verwalter) z PDF do JSON.

PROC EXISTUJE
Pro region DACH je to jediny enumerovatelny zdroj, ktery se podarilo najit.
BaFin ani rakouska FMA seznam ke stazeni nenabizeji - overeno zivym dotazem
1. 9. 2026. FINMA ho zverejnuje jako PDF, a to se precist da.

JAK TO CTE
Ne prostym extract_text - ten vrati jmeno, misto a par kriziku pod sebou
a neni poznat, do ktereho sloupce krizek patri. Cte se proto po SOURADNICICH:
x kolem 87 je nazev, 372 misto, 473 Fondsleitung, 507 Vertreter, 539 Verwalter
von Kollektivvermoegen. Role se bere z pozice krizku, ne z poradi.

POUZITI
    stahni flvervt.pdf z finma.ch a spust vedle nej:
    python financovani-finma.py
"""
# -*- coding: utf-8 -*-
import json, io, pypdf, collections

def radky_pdf(cesta):
    r = pypdf.PdfReader(cesta)
    out = []
    for p in r.pages:
        kusy = []
        def v(text, cm, tm, font, size):
            t = (text or "").strip()
            if t:
                kusy.append((round(tm[5]), round(tm[4]), t))
        p.extract_text(visitor_text=v)
        podle_y = collections.defaultdict(list)
        for y, x, t in kusy:
            podle_y[y].append((x, t))
        for y in sorted(podle_y, reverse=True):
            out.append(sorted(podle_y[y]))
    return out

SLOUPCE = [(455, 495, "fondsleitung"), (495, 525, "vertreter"), (525, 570, "verwalter")]
zaznamy, preskoceno = [], 0
for radek in radky_pdf("flvervt.pdf"):
    d = dict(radek)
    nazev = next((t for x, t in radek if 80 <= x <= 120), "")
    misto = next((t for x, t in radek if 360 <= x <= 400), "")
    if not nazev or not misto or nazev.startswith(("Liste der", "Name", "Vertreter von")):
        preskoceno += 1
        continue
    role = [jm for a, b, jm in SLOUPCE if any(a <= x < b for x, t in radek if t == "X")]
    zaznamy.append({"nazev": nazev, "misto": misto, "role": role})

print("zaznamu:", len(zaznamy), "| preskocenych radku (hlavicky):", preskoceno)
c = collections.Counter()
for z in zaznamy:
    for r in z["role"] or ["(bez role)"]:
        c[r] += 1
print("podle role:", dict(c))
print()
verw = [z for z in zaznamy if "verwalter" in z["role"]]
print("Verwalter von Kollektivvermoegen (sprava kolektivniho majetku):", len(verw))
fl = [z for z in zaznamy if "fondsleitung" in z["role"]]
print("Fondsleitung (spravci fondu):", len(fl))
json.dump(zaznamy, io.open("finma-flvervt.json", "w", encoding="utf-8"),
          ensure_ascii=False, indent=1)
print()
print("ukazka Fondsleitung:")
for z in fl[:8]:
    print("   %-46s %-16s %s" % (z["nazev"][:46], z["misto"], ",".join(z["role"])))
