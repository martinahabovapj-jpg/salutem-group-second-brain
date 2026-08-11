# -*- coding: utf-8 -*-
"""Prevede Claude data export (ZIP z claude.ai) na markdown soubory v SharePointu.

Bere projects.json z exportu a z kazdeho projektu vytahne "project knowledge"
(nahrane soubory a texty). Chaty ignoruje - ty resi jiny beh.

Pouziti:
    python claude-export-do-sharepointu.py                  # nahled, nic nezapisuje
    python claude-export-do-sharepointu.py --zapis          # zapise do SharePointu
    python claude-export-do-sharepointu.py --zip C:\\...\\x.zip --out C:\\tmp --zapis
"""
from __future__ import annotations

import argparse
import json
import re
import sys
import unicodedata
import zipfile
from datetime import date
from pathlib import Path

NAZVY_DOKUMENTU = ("filename", "file_name", "name", "title")
NAZVY_OBSAHU = ("content", "text", "body", "extracted_content")
NAZVY_KOLEKCI = ("docs", "knowledge", "documents", "files")


def slug(text: str, max_len: int = 60) -> str:
    """Nazev na male pismena s pomlckami bez diakritiky (konvence second brainu)."""
    text = unicodedata.normalize("NFKD", text or "")
    text = "".join(c for c in text if not unicodedata.combining(c))
    text = text.encode("ascii", "ignore").decode("ascii").lower()
    text = re.sub(r"[^a-z0-9]+", "-", text).strip("-")
    return (text[:max_len].rstrip("-")) or "bez-nazvu"


def najdi_zip(downloads: Path) -> Path | None:
    """Nejnovejsi ZIP, ktery vypada jako Claude data export."""
    kandidati = [
        z for z in downloads.glob("*.zip")
        if any(k in z.name.lower() for k in ("claude", "data-export", "data_export", "export"))
    ]
    if not kandidati:
        kandidati = list(downloads.glob("*.zip"))
    return max(kandidati, key=lambda p: p.stat().st_mtime) if kandidati else None


def cti_projekty(zip_path: Path) -> list[dict]:
    """Vytahne projects.json ze ZIPu, na jakekoli urovni."""
    with zipfile.ZipFile(zip_path) as z:
        jmena = [n for n in z.namelist() if Path(n).name == "projects.json"]
        if not jmena:
            raise SystemExit(
                f"V {zip_path.name} neni projects.json. Obsahuje: "
                + ", ".join(sorted({Path(n).name for n in z.namelist()})[:20])
            )
        data = json.loads(z.read(jmena[0]).decode("utf-8"))
    if isinstance(data, dict):
        data = data.get("projects", [data])
    return [p for p in data if isinstance(p, dict)]


def prvni(d: dict, klice: tuple[str, ...], vychozi: str = "") -> str:
    for k in klice:
        v = d.get(k)
        if isinstance(v, str) and v.strip():
            return v
    return vychozi


def dokumenty(projekt: dict) -> list[dict]:
    for k in NAZVY_KOLEKCI:
        v = projekt.get(k)
        if isinstance(v, list) and v:
            return [d for d in v if isinstance(d, dict)]
    return []


def cil_sharepoint() -> Path:
    base = Path.home() / "P&J Capital s.r.o" / "AI - Dokumenty"
    archiv = next(iter(sorted(base.glob("99 Archiv*"))), None)
    if archiv is None:
        raise SystemExit(f"Nenasel jsem '99 Archiv*' v {base}")
    return archiv / "claude-projekty"


def unikatni(jmeno: str, obsazena: set[str]) -> str:
    kandidat, i = jmeno, 2
    while kandidat in obsazena:
        kandidat, i = f"{jmeno}-{i}", i + 1
    obsazena.add(kandidat)
    return kandidat


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--zip", type=Path, help="cesta k ZIPu (jinak nejnovejsi z Downloads)")
    ap.add_argument("--out", type=Path, help="cilova slozka (jinak SharePoint archiv)")
    ap.add_argument("--zapis", action="store_true", help="skutecne zapsat soubory")
    args = ap.parse_args()

    zip_path = args.zip or najdi_zip(Path.home() / "Downloads")
    if not zip_path or not zip_path.exists():
        raise SystemExit("Nenasel jsem zadny ZIP v Downloads. Predej cestu pres --zip.")

    projekty = cti_projekty(zip_path)
    cil = args.out or cil_sharepoint()
    dnes = date.today().isoformat()

    print(f"ZIP:  {zip_path}")
    print(f"Cil:  {cil}")
    print(f"Rezim: {'ZAPIS' if args.zapis else 'NAHLED (nic se nezapisuje)'}")
    print(f"Projektu v exportu: {len(projekty)}\n")

    radky, zapsano, prazdne = [], 0, []
    obsazene_projekty: set[str] = set()

    for p in sorted(projekty, key=lambda x: prvni(x, ("name",), "").lower()):
        nazev = prvni(p, ("name",), "bez-nazvu")
        docs = dokumenty(p)
        if not docs:
            prazdne.append(nazev)
            continue

        slug_projektu = unikatni(slug(nazev), obsazene_projekty)
        slozka = cil / slug_projektu
        obsazene_docs: set[str] = set()
        vypis_docs = []

        for d in docs:
            doc_nazev = prvni(d, NAZVY_DOKUMENTU, d.get("uuid", "dokument"))
            obsah = prvni(d, NAZVY_OBSAHU)
            zaklad = slug(Path(doc_nazev).stem or doc_nazev)
            jmeno = unikatni(zaklad, obsazene_docs) + ".md"
            vypis_docs.append((doc_nazev, jmeno, len(obsah)))

            if args.zapis:
                slozka.mkdir(parents=True, exist_ok=True)
                hlavicka = "\n".join([
                    "---",
                    f"zdroj: claude.ai project knowledge",
                    f"projekt: {nazev}",
                    f"dokument: {doc_nazev}",
                    f"exportovano: {dnes}",
                    "---",
                    "",
                ])
                (slozka / jmeno).write_text(hlavicka + obsah + "\n", encoding="utf-8")
                zapsano += 1

        print(f"{nazev}  ->  {slug_projektu}/  ({len(docs)} dok.)")
        for doc_nazev, jmeno, velikost in vypis_docs:
            print(f"    {jmeno:<45} {velikost:>8} znaku   <- {doc_nazev}")

        radky.append(f"| [{nazev}]({slug_projektu}/) | {len(docs)} | {prvni(p, ('description',), '-')} |")

        if args.zapis:
            popis = prvni(p, ("description",), "")
            seznam = "\n".join(f"- [{dn}]({jm})" for dn, jm, _ in vypis_docs)
            (slozka / "_prehled.md").write_text(
                f"# {nazev}\n\n{popis}\n\n"
                f"Project knowledge z claude.ai, export {dnes}.\n\n{seznam}\n",
                encoding="utf-8",
            )

    if prazdne:
        print(f"\nBez project knowledge (preskoceno): {', '.join(prazdne)}")

    if args.zapis:
        cil.mkdir(parents=True, exist_ok=True)
        (cil / "_prehled.md").write_text(
            "# Claude projekty - project knowledge\n\n"
            f"Export z claude.ai ze dne {dnes}. Surovy material, ne hotova znalost -\n"
            "co z toho plati, patri do prislusne sekce second brainu.\n\n"
            "| Projekt | Dokumentu | Popis |\n|---|---|---|\n" + "\n".join(radky) + "\n",
            encoding="utf-8",
        )
        print(f"\nZapsano {zapsano} dokumentu do {cil}")
    else:
        print("\nNic nezapsano. Pro skutecny zapis pridej --zapis")
    return 0


if __name__ == "__main__":
    sys.exit(main())
