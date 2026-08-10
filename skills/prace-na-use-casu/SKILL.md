---
name: prace-na-use-casu
description: Použij tento skill VŽDY, když se začíná nebo pokračuje v práci na AI use casu pro Salutem — návrh řešení, stavba automatizace (Make, agenti, skripty), revize zadání, doplňování dokumentace. Spouštěj ho kdykoli uživatel řekne „pojďme stavět", „navrhni řešení", „pokračujeme na use casu", „co dneska s tím use casem", „rozpracuj zadání" a podobně. Skill určuje POŘADÍ ÚKONŮ — co se musí přečíst, než se cokoli navrhne, a co se musí zapsat, než se práce ukončí.
---

# Práce na use casu

Tenhle skill neříká, **co** navrhnout. Říká, **v jakém pořadí** pracovat — a to
pořadí je jediná věc, která nás opakovaně stála přepsané návrhy.

> **Pravidlo o pořadí:** dokumentace není výstup, kterým se práce uzavírá.
> Je to **vstup**, kterým se práce začíná.

## Vstupní rituál — než navrhneš cokoli

Projdi tato místa. Nepřeskakuj je proto, že „zadání je jasné" — právě když
zadání vypadá hotově, jsou nálezy nejdražší.

**1. Soubor use casu v second brainu.**
`C:\Users\habova\P&J Capital s.r.o\AI - Dokumenty\02 Use casy\`
Pokud neexistuje, po prvním čtení ho zakládáš ty.

**2. Freelo úkol use casu — včetně VŠECH komentářů.**
Ne jen popis. Starší komentáře běžně obsahují odpovědi na otázky, které nový
návrh otevírá jako nové, a rozhodnutí, která návrh nevědomky obchází.
Endpoint: `GET /v1/task/{id}` (pole `comments`) a `GET /v1/task/{id}/subtasks`.
Podúkoly mají vlastní komentáře — přečti i je.

**3. `05 Nástroje a systémy`** — co už je postavené a co se dá znovu použít.

**4. `04 Pravidla a governance`** — jaká brána se na use case vztahuje.
Tohle se vynechává nejčastěji a bolí to nejpozději. U AI use casů platí
**povinná posuzovací brána** (klasifikace rizika + zápis do inventáře AI
systémů) před nasazením.

**5. `06 Standardy a šablony`** — texty, formuláře a šablony e-mailů či SMS
bývají hotové, jen s nimi nikdo nepočítal.

**6. Živý systém.** To, co reálně běží, nebývá zapsané nikde.
U Make je čtecí API token v `~/.claude/settings.json` (`MAKE_*`) — mapa účtu je
v `05 Nástroje a systémy/make-co-uz-mame.md`, do ní nahlédni vždy první.

Až potom navrhuj.

### Přečti víc než první nález

Jeden nález umí vést ke špatnému závěru, který jiný soubor vyvrací. Reálný
případ: z poznámky „každý obchodník má svůj účet" vznikl závěr, že místo jednoho
scénáře bude potřeba třicet. Vysvětlení bylo v jiném souboru — šlo o napojení
kalendáře pro nahrávacího bota, ne o propojení na osobu.

## Výstupní rituál — na konci každé práce

Dvě věci, obě krátké, obě povinné.

**1. Komentář do Freelo úkolu.** Struktura:

- `Kde jsme skončili — <datum>`
- **Další krok** — konkrétně, ideálně jedna věc
- Co se udělalo
- Co se změnilo v návrhu a proč
- Otevřené body a jejich vlastníci

Freelo je stav. Tam se ráno kouká. Bez tohohle komentáře stojí příští ráno
40 minut rozpomínání.

**2. Datovaný záznam do sekce „Průběh stavby"** v souboru use casu.
Sem jde, **co jsme se dozvěděli a proč se něco změnilo** — ne stav.

### Kam co patří

| Kam | Co |
|---|---|
| **Freelo** | stav, termíny, kdo na tom dělá, další krok, otevřené body |
| **SharePoint (second brain)** | jak to funguje, proč tak, co jsme se naučili, revize s důvody |

Nikdy neduplikuj stavy a termíny do SharePointu.

### Otevřené body zakládej jako podúkoly

Ne jako odrážky v komentáři. Podúkol má vlastníka a termín, odrážka ne.
Do popisu podúkolu dej **hotový text ke zkopírování**, pokud jde o žádost na
kolegu — ať se to ráno dá poslat bez psaní.
Termín dávej jen tam, kde je závazek reálný. Fiktivní termíny u všech položek
udělají ze seznamu šum.

## Jak zapisovat revize

Když nález změní návrh, **nepřepisuj původní text.** Připiš revizi s datem
a důvodem:

> 🔶 **Revize 10. 8. 2026.** Návrh v1.0 počítal s X. Podle
> `05 Nástroje a systémy/pravidla-pro-raynet` platí Y, proto se mění na Z.

Kdo to bude číst za rok, potřebuje vidět, že se rozhodnutí měnilo — a proč.
Přepsaný text vypadá, jako by to tak bylo od začátku, a tím se ztrácí to
nejcennější, co dokumentace umí: historie omylů.

## Co nikdy nedělat

- **Nezakládej duplikát.** Než navrhneš novou tabulku, seznam nebo scénář, ověř,
  že už neexistuje. Chyba, která tohle pravidlo vyrobila: chystali jsme se
  zakládat tabulku obchodníků, která už existovala včetně 28 řádků dat.
- **Nezadávej kolegovi zjišťování něčeho, co je zapsané.** Než napíšeš „zjisti
  X", zkus X najít.
- **Nezapisuj stav do SharePointu** ani **znalost do Freela**.
- **Neměň stavy úkolů ve Freelu** bez pokynu.
- **Nepiš do provozních systémů**, pokud k nim máš jen čtecí přístup — to je
  záměr, ne omezení, které se má obcházet.

## Proč to vzniklo

Use case „follow-up e-mail po callech" měl 6. 8. 2026 hotový návrh: sedm kroků,
architektura, prompt, metriky. Vypadal připravený ke stavbě.

10. 8. se před stavbou prošel Make účet a second brain — necelá hodina čtení.
Osm nálezů, **čtyři z nich změnily architekturu**. Dvě otevřené otázky se
zodpověděly bez dotazování. Jedna tabulka se nezaložila podruhé. Jedna šablona
se nemusela psát — a odhalila, že prompt je navržený na jiný e-mail, než obchod
reálně posílá.

**Ani jeden z těch nálezů nebyl nová informace.** Všechny byly dostupné už
6. srpna. Nešlo o smůlu, šlo o pořadí úkonů.

Delší zápis je v second brainu: `03 Jak pracujeme/jak-zacinat-use-case.md`.
