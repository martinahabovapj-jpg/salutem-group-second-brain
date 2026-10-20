# -*- coding: utf-8 -*-
"""Kolik času stála práce v session: měří interakci, ne délku session.

    python vykaz_casu.py                           aktuální (nejnovější) session, celý dnešek
    python vykaz_casu.py --od 2026-10-08T13:26     jen od daného času (UTC, jak je v transkriptu)
    python vykaz_casu.py --session <id> --datum 2026-10-08

Pravidlo (Martina, 8. 10. 2026):
- práce Clauda  = každá mezera, po které následuje událost Clauda nebo nástroje
                  (myšlení, psaní, běh skriptů)
- čas Martiny   = mezera před její zprávou, ale jen do 10 minut (čte a odpovídá)
- pauza         = mezera před její zprávou nad 10 minut → NEPOČÍTÁ se
                  (byla pryč nebo zařizovala něco mimo konverzaci)
Výsledek se zaokrouhlí nahoru na 5 minut a vykáže na HLAVNÍ úkol use casu.
Martině se vždy ukáže rozpad, včetně vynechaných pauz — ona rozhodne,
jestli některá pauza byla práce na úkolu (např. dohledávání podkladů).

Časy v transkriptu jsou v UTC; místní čas = UTC + 2 (léto) / + 1 (zima).
"""
import argparse
import glob
import json
import math
import os
import sys
from datetime import datetime, timezone

PROJEKT = os.path.expanduser(r"~/.claude/projects/C--Users-habova")
PRAH_PAUZY = 600  # s


def je_zprava_cloveka(o):
    if o.get("type") != "user":
        return False
    c = (o.get("message") or {}).get("content")
    if isinstance(c, str):
        return True
    return isinstance(c, list) and any(x.get("type") == "text" for x in c)


def main():
    sys.stdout.reconfigure(encoding="utf-8")
    ap = argparse.ArgumentParser()
    ap.add_argument("--session", help="id session (výchozí: naposledy změněný transkript)")
    ap.add_argument("--datum", default=datetime.now(timezone.utc).strftime("%Y-%m-%d"))
    ap.add_argument("--od", help="počítat až od tohoto času UTC, např. 2026-10-08T13:26")
    a = ap.parse_args()

    if a.session:
        soubor = os.path.join(PROJEKT, a.session + ".jsonl")
    else:
        soubor = max(glob.glob(os.path.join(PROJEKT, "*.jsonl")), key=os.path.getmtime)

    udalosti = []
    for radek in open(soubor, encoding="utf-8"):
        try:
            o = json.loads(radek)
        except ValueError:
            continue
        ts = o.get("timestamp") or ""
        if not ts.startswith(a.datum) or (a.od and ts < a.od):
            continue
        # queue-operation = zpráva poslaná během práce Clauda; čas jí patří, ale
        # mezeru před ní nepočítáme jako Martinino čtení (Claude v tu chvíli pracoval)
        druh = "H" if je_zprava_cloveka(o) else "M"
        udalosti.append((datetime.fromisoformat(ts[:19]), druh))
    udalosti.sort()
    if len(udalosti) < 2:
        print("V transkriptu pro zadané období nic není.")
        return

    claude = clovek = 0
    pauzy = []
    for (t1, _), (t2, druh) in zip(udalosti, udalosti[1:]):
        mezera = (t2 - t1).total_seconds()
        if druh == "H":
            if mezera <= PRAH_PAUZY:
                clovek += mezera
            else:
                pauzy.append((t1.strftime("%H:%M"), round(mezera / 60)))
        else:
            claude += mezera

    celkem = (claude + clovek) / 60
    print(f"transkript: {os.path.basename(soubor)}")
    print(f"období (UTC): {udalosti[0][0]:%H:%M} – {udalosti[-1][0]:%H:%M}")
    print(f"práce Clauda:        {claude / 60:5.0f} min")
    print(f"čtení a odpovědi:    {clovek / 60:5.0f} min")
    print(f"celkem:              {celkem:5.0f} min → k vykázání {math.ceil(celkem / 5) * 5} min")
    if pauzy:
        print("nezapočtené pauzy (UTC začátek, min): " + ", ".join(f"{z} ({m})" for z, m in pauzy))


if __name__ == "__main__":
    main()
