# Jak přispívat do Second Brain

Díky, že rozšiřuješ naši společnou znalostní bázi! Pár jednoduchých pravidel,
ať se v repu i nadále všichni vyznáme.

## Obecné konvence

- **Jazyk:** čeština — spisovná, lidská, srozumitelná, k věci, bez zbytečných odborností.
- **Názvy souborů a složek:** malá písmena, slova oddělená pomlčkami, bez diakritiky a mezer.
  - ✅ `tvorba-projektu.md`, `styl-komunikace.md`
  - ❌ `Tvorba Projektu.md`, `styl_komunikace.md`
- **Změny posílej přes pull request.** Než se nový standard rozšíří k týmu,
  ať si ho někdo přečte a odsouhlasí.

## Jak přidat nový skill

1. Ve složce `skills/` vytvoř **vlastní složku** pojmenovanou podle skillu.
2. Dovnitř dej soubor **`SKILL.md`** (přímo, nezanořovat o úroveň hloub!).
3. **Název složky = pole `name`** v hlavičce skillu. Musí sedět.
4. Přidej skill do tabulky v [`skills/README.md`](skills/README.md).

Struktura hlavičky `SKILL.md`:

```
---
name: nazev-skillu
description: Kdy a k čemu se skill používá (podle toho ho Claude pozná a spustí).
---

# Obsah skillu...
```

## Jak přidat dokument

- Lidskou dokumentaci dávej do `dokumentace/` do správné podsložky
  (`procesy/`, `onboarding/`, `nastroje/`).
- Prompty pro Claude do `prompts/`, firemní kontext do `kontext/`.
- Pojmenuj soubor výstižně podle konvence výše a, kde to dává smysl,
  ho zmiň v `README.md` dané složky.
