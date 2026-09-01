# -*- coding: utf-8 -*-
"""Vyprazdni pole Web tam, kde v nem je domena SPRAVCE fondu, ne fondu.

PROC TO NEJDE PODLE SEZNAMU DOMEN
Sekce "spravci" v konfiguraci je delana pro PAROVANI - tam je spravne, ze je
siroka, protoze shoda takove domeny nikdy nesmi sparovat dva ruzne fondy.
Jako filtr na mazani je ale prilis siroka: conseq.cz je pro fond
"Conseq privatniho financovani podfond" jeho VLASTNI stranka, ne cizi adresa.
Radky se proto vyjmenovavaji rucne, at se nesmaze neco, co plati.

Prazdne pole Web je poctivejsi nez cizi adresa - mesicni beh pak u radku web
nehlida a rekne to nahlas, misto aby hlasil zmeny na strance AVANTu.

POUZITI
    python vycisti-web-spravcu.py           # nanecisto
    python vycisti-web-spravcu.py --zapis
"""
import importlib.util, io, json, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))

# Radky, u kterych je v poli Web adresa spravce nebo agregatoru, ne fondu.
# Overeno rucne 1. 9. 2026. Conseq (#26, #27, #190) tu SCHVALNE neni - tam je
# conseq.cz vlastni stranka fondu i spravce.
RADKY = {
    "6":   "codyainvest.cz - stranka spravce CODYA, fond vlastni web nema",
    "15":  "fki-fondy.cz - agregator fondu, ne stranka fondu",
    "33":  "amista.cz/statutory-information - povinne informace spravce AMISTA",
    "198": "amista.cz - homepage spravce AMISTA, ne fondu",
}

spec = importlib.util.spec_from_file_location(
    "financovani_beh", os.path.join(HERE, "financovani-beh.py"))
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
cfg = json.load(io.open(os.path.join(HERE, "financovani-beh.config.json"), encoding="utf-8"))
m.T.update(cfg["texty"])

opravdu = "--zapis" in sys.argv
sesit = m.Sesit(cfg)
ws = sesit.ws("subjekty")
i_web = sesit.sl("subjekty", "web")
i_id = sesit.sl("subjekty", "id")
i_naz = sesit.sl("subjekty", "nazev")

POZN = ("[{datum} oprava] Web vyprazdnen - byla v nem adresa spravce fondu "
        "({web}), ne fondu, a mesicni beh by hlidal cizi stranku. Duvod: {duvod}. "
        "Adresa spravce patri do listu 6, sloupec Gatekeeper.")

dotcene, nesedi = [], []
for r in range(2, ws.max_row + 1):
    sid = m.norm(ws.cell(row=r, column=i_id).value)
    if sid not in RADKY:
        continue
    w = m.norm(ws.cell(row=r, column=i_web).value)
    naz = m.norm(ws.cell(row=r, column=i_naz).value)
    if not w:
        nesedi.append((sid, naz, "pole Web uz je prazdne"))
        continue
    dotcene.append((sid, naz, w))
    if opravdu:
        ws.cell(row=r, column=i_web).value = None
        m.pripis_poznamku(sesit, r, POZN.format(
            datum=m.DNES, web=w, duvod=RADKY[sid]))

for sid, naz, w in dotcene:
    m.vypis("  #%-5s %-45s %s" % (sid, naz[:45], w[:55]))
for sid, naz, proc in nesedi:
    m.vypis("  PRESKOCENO #%-5s %-38s %s" % (sid, naz[:38], proc))
m.vypis("  vyprazdneno: %d ze %d vyjmenovanych" % (len(dotcene), len(RADKY)))
if opravdu:
    sesit.uloz(os.path.join(HERE, cfg["zalohy"]))
    m.vypis("  Zapsano.")
else:
    m.vypis("  NANECISTO - nic nezapsano. Ostry zapis: --zapis")
