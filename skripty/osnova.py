# -*- coding: utf-8 -*-
"""Osnova .docx: nadpisy podle stylu + zkracene odstavce, at se velky dokument
da porovnat proti zaznamu bez cteni cele latky."""
import io
import os
import sys
import zipfile
import xml.etree.ElementTree as ET

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8", errors="replace")
W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def dlouha_cesta(p):
    p = os.path.abspath(p)
    if p.startswith("\\\\?\\"):
        return p
    return "\\\\?\\" + p


LIMIT = int(os.environ.get("LIMIT", "140"))

for arg in sys.argv[1:]:
    print("\n############ %s ############" % os.path.basename(arg))
    try:
        with zipfile.ZipFile(dlouha_cesta(arg)) as z:
            root = ET.fromstring(z.read("word/document.xml"))
    except Exception as e:
        print("!! %s: %s" % (type(e).__name__, e))
        continue
    body = root.find(W + "body")
    n_tbl = 0
    for el in body:
        if el.tag == W + "tbl":
            n_tbl += 1
            rows = el.findall(W + "tr")
            first = rows[0] if rows else None
            hlavicka = ""
            if first is not None:
                cells = []
                for tc in first.findall(W + "tc"):
                    cells.append("".join(t.text or "" for t in tc.iter(W + "t")).strip())
                hlavicka = " | ".join(c[:28] for c in cells if c)
            print("  [TABULKA %d: %d radku]  %s" % (n_tbl, len(rows), hlavicka[:150]))
            continue
        if el.tag != W + "p":
            continue
        txt = "".join(t.text or "" for t in el.iter(W + "t")).strip()
        if not txt:
            continue
        style = ""
        ppr = el.find(W + "pPr")
        if ppr is not None:
            ps = ppr.find(W + "pStyle")
            if ps is not None:
                style = ps.get(W + "val") or ""
        mark = ""
        if style.lower().startswith("heading") or style.lower().startswith("nadpis"):
            mark = "## "
        elif style.lower().startswith("title") or style.lower().startswith("nazev"):
            mark = "# "
        elif style.lower().startswith("listparagraph") or style.lower().startswith("odstavecseznamu"):
            mark = "  - "
        print("%s%s" % (mark, txt[:LIMIT] + ("…" if len(txt) > LIMIT else "")))
