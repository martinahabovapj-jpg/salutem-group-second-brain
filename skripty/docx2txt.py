"""Prevod .docx na cisty text.

Proc existuje: prepisy hovoru v `99 Archiv zdroju/prepisy` jsou .docx a agenti
v nich potrebuji hledat. Bez tohohle skriptu si kazdy bezh psal vlastni prevod
znovu a stalo ho to tretinu rozpoctu na hledani (doloz. 14. 8. 2026, dva behy).

Pouziti:
    python docx2txt.py <soubor.docx>              # vypise text na stdout
    python docx2txt.py <slozka> --do <cilova>     # prevede vsechny .docx ve slozce
    python docx2txt.py <slozka> --do <cilova> --prepsat   # prepise i existujici

Zavislosti: zadne. .docx je ZIP s XML, cte se standardni knihovnou.
"""
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

W = "{http://schemas.openxmlformats.org/wordprocessingml/2006/main}"


def dlouha_cesta(cesta):
    """Prefix pro obejiti limitu 260 znaku na Windows.

    Proc: `Alfa/47 standardizace vstupu/Knihovna dokumentu/...` ma pres 260
    znaku a `open()` na nem hlasi "neexistuje", i kdyz soubor existuje
    (dolozeno 4. 9. 2026 - 12 z 31 popisu se timhle tise ztratilo).
    Mimo Windows se nedela nic.
    """
    if os.name != "nt":
        return cesta
    p = os.path.abspath(cesta)
    prefix = chr(92) * 2 + "?" + chr(92)
    return p if p.startswith(prefix) else prefix + p


def docx_na_text(cesta):
    """Vrati text .docx souboru. Odstavce oddelene novym radkem."""
    with zipfile.ZipFile(dlouha_cesta(cesta)) as z:
        # hlavni telo dokumentu; hlavicky a zapati zamerne ignorujeme
        with z.open("word/document.xml") as f:
            strom = ET.parse(f)

    radky = []
    for odstavec in strom.iter(W + "p"):
        kusy = []
        for uzel in odstavec.iter():
            if uzel.tag == W + "t" and uzel.text:
                kusy.append(uzel.text)
            elif uzel.tag == W + "tab":
                kusy.append("\t")
            elif uzel.tag in (W + "br", W + "cr"):
                kusy.append("\n")
        radek = "".join(kusy).strip()
        if radek:
            radky.append(radek)
    return "\n".join(radky)


def slug(nazev):
    """Nazev souboru bez diakritiky a mezer - aby se dal grepovat."""
    mapa = str.maketrans(
        "áčďéěíňóřšťúůýžÁČĎÉĚÍŇÓŘŠŤÚŮÝŽ",
        "acdeeinorstuuyzACDEEINORSTUUYZ",
    )
    n = nazev.translate(mapa)
    n = re.sub(r"[^A-Za-z0-9._-]+", "-", n).strip("-")
    return n


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 1

    zdroj = sys.argv[1]
    cil = None
    if "--do" in sys.argv:
        cil = sys.argv[sys.argv.index("--do") + 1]
    prepsat = "--prepsat" in sys.argv

    if os.path.isfile(dlouha_cesta(zdroj)):
        sys.stdout.reconfigure(encoding="utf-8")
        print(docx_na_text(zdroj))
        return 0

    if not os.path.isdir(dlouha_cesta(zdroj)):
        print(f"CHYBA: {zdroj} neexistuje", file=sys.stderr)
        return 1
    if not cil:
        print("CHYBA: u slozky je potreba --do <cilova slozka>", file=sys.stderr)
        return 1

    os.makedirs(cil, exist_ok=True)
    prevedeno = preskoceno = chyb = 0

    for dp, _, soubory in os.walk(zdroj):
        for fn in sorted(soubory):
            # ~$ jsou docasne zamky Wordu, ne dokumenty
            if not fn.lower().endswith(".docx") or fn.startswith("~$"):
                continue
            vstup = os.path.join(dp, fn)
            vystup = os.path.join(cil, slug(os.path.splitext(fn)[0]) + ".txt")
            if os.path.exists(vystup) and not prepsat:
                preskoceno += 1
                continue
            try:
                text = docx_na_text(vstup)
            except Exception as e:
                print(f"CHYBA {fn}: {e}", file=sys.stderr)
                chyb += 1
                continue
            # prvni radek nese cestu k originalu, aby slo citovat zdroj
            hlavicka = f"# ZDROJ: {os.path.relpath(vstup, zdroj)}\n\n"
            with open(vystup, "w", encoding="utf-8") as f:
                f.write(hlavicka + text)
            prevedeno += 1

    print(f"prevedeno {prevedeno}, preskoceno {preskoceno} (uz existuje), chyb {chyb}")
    print(f"cil: {cil}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
