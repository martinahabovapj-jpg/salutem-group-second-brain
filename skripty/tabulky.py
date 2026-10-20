# -*- coding: utf-8 -*-
"""Vypis vsech tabulek z .docx."""
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


LIMIT = int(os.environ.get("LIMIT", "160"))

for arg in sys.argv[1:]:
    print("\n############ %s ############" % os.path.basename(arg))
    with zipfile.ZipFile(dlouha_cesta(arg)) as z:
        root = ET.fromstring(z.read("word/document.xml"))
    for i, tbl in enumerate(root.iter(W + "tbl"), 1):
        print("=== TABULKA %d ===" % i)
        for tr in tbl.findall(W + "tr"):
            cells = []
            for tc in tr.findall(W + "tc"):
                txt = " ".join(
                    "".join(t.text or "" for t in p.iter(W + "t")).strip()
                    for p in tc.iter(W + "p")
                ).strip()
                cells.append(txt[:LIMIT])
            if any(cells):
                print(" | ".join(cells))
