---
name: financovani-mesicni-beh
description: Použij tento skill VŽDY, když se má spustit nebo dokončit měsíční běh nad databází poskytovatelů financování — tedy kontrola, co se u subjektů změnilo (insolvence, zánik, nedostupný web, nové typy financování, ticket, LTV, kontaktní osoby). Spouštěj ho, když uživatel řekne „pusť měsíční běh", „zkontroluj databázi financování", „co se změnilo u poskytovatelů", „přečti změněné stránky", „co je ke schválení" a podobně. Skill určuje, co dělá skript a co model, a hlavně čím model NESMÍ rozhodovat.
---

# Měsíční běh nad databází poskytovatelů financování

Databáze se sama neudrží. Ale hlavní problém není detekce — změny se dají
najít levně a hodně. **Vzácné jsou minuty, které jim někdo věnuje.**
Celý běh je proto postavený tak, aby se před schvalovatele dostalo jen to,
o čem musí rozhodnout on. Cíl je **10–20 položek měsíčně a ~10 minut práce**.

> **Zásada, na které to stojí:** model navrhuje, skript vykonává.
> Model nikdy nezapisuje do sešitu a nikdy nerozhoduje o tom, do kterého
> pruhu jeho návrh půjde. Kdyby o svém pruhu rozhodoval sám, odsouhlasil by
> si, co ho napadne — a databáze by podruhé obsahovala vymyšlená data.

## Rozdělení práce

| Fáze | Co se děje | Kdo |
|---|---|---|
| 0 | načtení master sešitu | skript |
| 1 | ARES + ISIR podle IČO | skript |
| 2 | HTTP status webu, DNS mailové domény | skript |
| 3 | otisk stránek, porovnání s minulým během | skript |
| **4** | **čtení změněných stránek** | **model (ty)** |
| 5 | routování do pruhů a zápis | skript |

Fáze 3 je to, co drží náklady dole: ze 142 subjektů se měsíčně reálně změní
odhadem 15–25 stránek. Jen ty jdou modelu — a i z nich jen **rozdíl** proti
minulému běhu, ne celá stránka.

## Postup

### 1. Spusť běh nanečisto

```
cd C:\Users\habova\salutem-group-second-brain\skripty
python financovani-beh.py
```

Nic nezapíše. Vypíše, co našel, a připraví složku `k-precteni/`.

### 2. Přečti, co skript připravil

V `k-precteni/` je jeden soubor na každý subjekt, jehož web se změnil.
Zadání je v `k-precteni/_ZADANI.md` — **řiď se jím doslova**.

Sleduješ jen pět polí: typ financování · ticket · LTV · kontaktní osoba ·
doložená transakce. Většina změn na webech neznamená nic (nový článek, jiná
fotka, přeházené odstavce) a **správná odpověď je „nic"**.

> **Pravidlo, které se neporušuje:** ke každému návrhu musíš dodat
> **doslovnou citaci** ze stránky a **URL**. Když neumíš citovat, návrh
> nevzniká. Skript návrhy bez citace sám zahodí — ale to je pojistka,
> ne postup.

Výstup zapiš do `navrhy.json` (tvar je v zadání).

> **Když u stejného subjektu řekneš „nic" podruhé, není to jeho chyba, ale
> naše.** Některé weby mění při každém načtení počítací captchu nebo pořadí
> polí ve formuláři — stránka pak hlásí změnu každý měsíc a nikdy to nic
> neznamená. Příčinu dopiš jako regulární výraz do `financovani-beh.config.json`,
> sekce `otisk_ignoruj`. Levný detektor se seřizuje, ne obchází.

### 3. Vrať návrhy skriptu a zapiš

```
python financovani-beh.py --navrhy navrhy.json --zapis
```

### 4. Napiš přehled člověku

Krátce, jednou kartou na subjekt: co se změnilo · bylo → navrženo ·
odkaz s citací. Rozhodnutí je předvyplněné, schvalovatel má jen projet
seznam a u dvou tří přepsat default.

**Zprávu pošli i když se nic nezměnilo.** „Zkontrolováno 142 subjektů,
3 změny aplikovány automaticky, nic ke schválení." Ticho je dvojznačné —
nepozná se, jestli je klid, nebo běh spadl.

## Tři pruhy

Pruh **není systém**. Je to hodnota ve sloupci listu *Návrhy změn*.
Routuje se podle toho, **které pole se mění a odkud informace přišla** —
nikdy podle obsahu změny.

| Co se změnilo | Odkud to víme | Pruh |
|---|---|---|
| Insolvence | ISIR podle IČO (+ potvrzení v ARESu) | **A** — projde samo |
| Zánik, likvidace, změna názvu či sídla | ARES podle IČO | **A** |
| Web nedostupný dva běhy po sobě | HTTP status | **A** (jen příznak) |
| E-mailová doména neexistuje | DNS záznam | **A** |
| IČO, které ARES nezná | ARES vrátil 404 | **B** — 404 ≠ zaniklá firma |
| Nový typ financování · ticket · LTV | web subjektu, model | **B** |
| Kontaktní osoba · nový subjekt · transakce | web, LinkedIn, média | **B** |
| Změna textu bez dopadu na pole | otisk stránky | **C** — jen do logu |

Pravidla jsou v `financovani-beh.config.json`, sekce `pruhy`. **Když se
ukáže, že něco chodí do špatného pruhu, přehodí se to tam — ne v kódu.**

## Čtyři pojistky pruhu A

Automatický zápis bez člověka je odvážná část, takže:

1. **Dvojí potvrzení.** Síťové věci musí selhat dvakrát po sobě — jeden
   výpadek není fakt. Insolvence musí sedět v ARESu (`stavZdrojeIr`)
   **i** v ISIRu.
2. **Nikdy nemaže.** Pruh A mění jen pole *Stav* a připíše poznámku
   s odkazem na rejstřík. Řádek zůstává, historie taky.
3. **Log se starou hodnotou.** Vrácení je jeden krok:
   `python financovani-beh.py --vrat 2026-09-01 --zapis`
4. **Strop 10 %.** Kdyby pruh A chtěl v jednom běhu změnit víc než desetinu
   řádků, zastaví se a pošle vše do pruhu B. Chytá scénář „rozbil se parser"
   nebo „rejstřík vrátil nesmysl" — přesně tu situaci, kdy by automat tiše
   rozbil databázi.

## Co hlídat na sobě samém

| Signál | Co znamená | Co udělat |
|---|---|---|
| Fronta pruhu B > 25 položek | prahy jsou moc citlivé | přitvrdit `prahy` v konfiguraci |
| Zamítá se víc než třetina návrhů | detektor je rozladěný | seřídit, ne ignorovat |
| Běh hlásí useknutí dávky | část změn se nezpracovala | **řekni to** — mlčení by četlo jako „pokryto vše" |
| Sešit je zamčený | někdo ho má otevřený v Excelu | běh v noci, jinak zkusit znovu |

Jednou za čtvrtletí: vezmi náhodných 5 % automaticky aplikovaných změn
z logu a ověř je ručně.

## Čeho se nedotýkat

- **Do sešitu nezapisuje nic než skript.** Ani ty, ani vyhledávač
  „Kdo mi to zafinancuje" — ten sešit jen čte.
- **Struktura sloupců se nemění.** Přidávat lze, přejmenovat a přesouvat ne —
  skript sloupce hledá podle názvu z konfigurace.
- **Vyřazené subjekty se nemažou.** Drží se v databázi včetně důvodu
  vyřazení, aby je za půl roku nikdo neprověřoval znovu.

Znalostní zápis k celému use casu je v second brainu:
`AI - Dokumenty / 02 Use casy / databaze-poskytovatelu-financovani.md`.
