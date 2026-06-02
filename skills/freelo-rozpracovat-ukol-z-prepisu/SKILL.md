---
name: freelo-rozpracovat-ukol-z-prepisu
description: Použij tento skill VŽDY, když máš rozpracovat JEDEN existující úkol ve Freelu na podúkoly (a případně checklisty) na základě přepisu callu / schůzky a nahrávky z Teams. Spouštěj ho, když uživatel řekne něco jako "dopracuj tenhle úkol", "doplň podúkoly k úkolu z callu", "rozpracuj úkol podle přepisu", "naplánuj kroky k tomuhle úkolu" apod. — i když to neřekne přesně takhle. Na rozdíl od skillu freelo-projekt-z-prepisu tady NEZAKLÁDÁŠ nový projekt ani nové úkoly — pracuješ uvnitř jednoho konkrétního, již existujícího úkolu. Skill určuje JAK rozpracovat; samotné zakládání přes Freelo API řeší existující skript.
---

# Rozpracování existujícího úkolu ve Freelu z přepisu callu

Tento skill říká, jak vzít **jeden konkrétní, už existující úkol** ve Freelu a na základě přepisu callu (+ nahrávky z Teams) k němu dopracovat podúkoly tak, aby z toho byla jasná, kompletní cesta k cíli — jako by ji rozkreslil zkušený projektový manažer, který byl na tom callu.

Sdílí filozofii se skillem `freelo-projekt-z-prepisu` (věrnost přepisu, lidské názvosloví, transparentní nejasnosti). Liší se **rozsahem**: nezakládáš projekt ani neplníš víc to-do listů — soustředíš se dovnitř jednoho úkolu.

Skill řeší jen **obsah a strukturu**. Samotné zakládání přes Freelo API obstará existující skript — tím se nezabývej.

## Typická situace

Někdo nám dal zadání → z něj vznikl jeden úkol ve Freelu → my si s tím člověkem voláme, abychom zjistili detaily. Jsme tedy skoro vždy **na úplném začátku**: existuje jen ten jeden úkol a k němu je potřeba rozkreslit kroky. Prakticky nikdy není nic z toho hotové — nepředpokládej tedy splněné kroky a neřeš „co už je vyřešené".

## Hlavní princip: věrnost před vynalézavostí

Stejný princip jako u tvorby projektu. Uživatel se na výstup potřebuje **spolehnout** — že je tam všechno tak, jak na callu zaznělo, a nic není tiše domyšlené ani vynechané.

- **Zachyť vše konkrétní z přepisu** — jména, termíny, čísla, konkrétní rozhodnutí, připomínky, insighty, varování. Když na callu padlo "tohle ještě musí schválit Milada", je z toho podúkol "Odsouhlasit návrh s Miladou", ne obecné "schválit".
- **Nic si nevymýšlej.** Co v přepisu nezaznělo, do úkolu nepatří jako fakt.
- **Co je nejasné, jde transparentně nahoru** (viz "Práce s nejasnostmi"), nikdy se neschovává do domyšleného podúkolu.

Skill řídí *formu*, přepis řídí *obsah*. Když na callu zaznělo hodně, podúkolů bude víc — úplnost má přednost před stručností.

## Rozsah: zůstáváš uvnitř jednoho úkolu

**Defaultně přidáváš výhradně podúkoly do toho jednoho konkrétního existujícího úkolu.** Nezakládáš nové úkoly ani nesaháš do jiných úkolů v projektu.

**Výjimka — když z briefu logicky vyvstane potřeba úplně nového úkolu:** nezakládej ho sám. Nejdřív ho **navrhni** (název + proč by měl vzniknout + co by obsahoval) a **počkej na schválení**, jestli ho založit. Teprve po odsouhlasení.

## Hierarchie a kdy jít do hloubky

Pracuješ ve struktuře: **úkol → podúkoly → (výjimečně) checklist uvnitř podúkolu.**

### Podúkoly (běžná úroveň)

Hlavní výstup skillu. Rozkresli cestu k cíli úkolu na konkrétní podúkoly v lidské češtině. Použij podúkol vždy, když krok:
- potřebuje vlastní odpovědnou osobu nebo vlastní termín, nebo
- chceš u něj vidět postup (že se logicky kráčí k cíli).

Drž selský rozum: podúkol = smysluplný krok, ne mechanické drobení. Orientačně **3–7 podúkolů** bývá tak akorát; když ti vychází výrazně víc než ~10, je to signál, že úkol je ve skutečnosti spíš projekt — pak to vyřeš návrhem nového úkolu (viz výjimka výše), ne nekonečným seznamem.

### Checklist uvnitř podúkolu (třetí úroveň — výjimka)

Checklist použij **jen tehdy**, když platí všechno z tohoto:
- jde o **drobné krok-za-krokem položky**, které dělá **tatáž osoba** jako podúkol,
- položky **nepotřebují vlastní termín ani přiřazení jiné osobě**,
- slouží jako „na nic nezapomenout" nebo jako definice hotovo (např. před nasazením textu projít: gramatika, tón, soulad se zadáním).

**Jakmile krok potřebuje jiného člověka, vlastní deadline, nebo chceš vidět jeho postup v přehledu → je to podúkol, ne položka checklistu.** (Příklad: „Odsouhlasit text s marketingem" vtahuje jiný tým → patří to jako podúkol, ne jako položka checklistu.)

Ve sporu volit jednodušší variantu — radši žádný checklist. Největší chyba je překomplikovat strukturu tak, že správa zabere víc času než práce. Nejdeš nikdy hlouběji než tři úrovně; potřeba čtvrté úrovně je signál pro návrh samostatného úkolu.

## Existující úkol: název a popis

Úkol už pojmenoval a popsal někdo jiný. Přesto:

- **Smíš navrhnout přejmenování úkolu** do našeho jednotného stylu (lidská spisovná čeština, neutrální infinitiv, krátké, úderné, bez odborností) — kvůli konzistentnímu názvosloví napříč firmou. Ale jen jako **návrh ke schválení**, původní název nikdy nepřepisuj potichu.
- **Smíš navrhnout doplnění popisu úkolu**, když z přepisu vyplyne důležitý kontext, který v popisu chybí — opět jako návrh, ne tiše.

Příklady názvosloví (stejná logika jako u projektů):
- Dobře: `Sestavit seznam konkurenčních objektů`, `Ověřit ceny na vlastních webech klienta`, `Odsouhlasit návrh řešení s Miladou`
- Špatně: `[Příprava] Competitor list task`, `Client materials preparation` (fáze v názvu, cizí jazyk, neosobní)

## Reference na nahrávku z Teams

Vstupem je přepis (doc) a obvykle i odkaz na nahrávku schůzky z Teams. **S obsahem pracuj z přepisu** — interní Teams/SharePoint odkaz je chráněný přihlášením a neslouží jako zdroj dat.

Odkaz na nahrávku ale **vlož do úkolu jako dohledatelnou referenci** tam, kde to logicky sedí — typicky do popisu úkolu nebo jako úvodní podúkol/poznámku „Zdroj: nahrávka z Teams (datum callu)". Ať se k originálu kdokoli časem proklikne.

## Práce s nejasnostmi

Přepisy bývají věcné, ale ne vždy. Když něčemu nerozumíš, něco si protiřečí, nebo si nejsi jistý — **finální slovo má vždy člověk.**

- **Nejasnosti neschovávej do domyšleného podúkolu.**
- **Posbírej je viditelně** — buď jako zvlášť označené podúkoly `⚠️ K vyjasnění: …` přímo v úkolu, nebo do souhrnné poznámky na konci. Formuluj je jako konkrétní dotazy: „Na callu nezaznělo, kdo schvaluje finální verzi — doplnit", „Padlo řešení A i B, není jasné, pro co jste se rozhodli — rozhodnout".
- **Drobnosti smíš navrhnout** podle nejlepšího úsudku, ale viditelně označené jako návrh (např. „(návrh – ověřit)"), ať je jasné, že to není z callu a člověk to potvrdí nebo smaže.

## Postup práce

1. **Přečti existující úkol** (název, popis) a **celý přepis**. Udělej si obraz: jaký je cíl úkolu, co k němu na callu zaznělo — kroky, jména, termíny, čísla, rozhodnutí, připomínky, insighty.
2. **Rozkresli podúkoly** — konkrétní kroky vedoucí k cíli úkolu, v lidské spisovné češtině, neutrální infinitiv, se všemi konkrétními detaily z callu.
3. **Kde dává smysl, přidej checklist** dovnitř podúkolu (jen podle pravidel výše).
4. **Vlož referenci na nahrávku z Teams** na logické místo.
5. **Případně navrhni úpravu názvu / popisu úkolu** do jednotného stylu (jako návrh).
6. **Posbírej nejasnosti** a chybějící informace viditelně.
7. **Pokud z briefu vyplývá potřeba úplně nového úkolu**, připrav jeho návrh (nezakládej).
8. **Ukaž uživateli náhradem celý návrh a počkej na schválení**, teprve pak zakládej ve Freelu.

## Obsah náhledu před založením

Ukaž uživateli vždy:
- navržený (pře)název úkolu, je-li nějaký,
- případnou navrženou úpravu popisu úkolu,
- seznam podúkolů (a v nich checklisty, kde dávají smysl),
- referenci na nahrávku z Teams a kam ji vkládáš,
- zvlášť vypíchnuté nejasnosti k doplnění,
- případný návrh nového samostatného úkolu (pokud vznikl).

## Rychlý kontrolní seznam před založením

- Zůstal jsem uvnitř toho jednoho úkolu (nezaložil jsem svévolně nové úkoly)?
- Jsou podúkoly v lidské spisovné češtině, neutrální infinitiv?
- Jsou v podúkolech všechny konkrétní věci z callu (jména, termíny, čísla, připomínky)?
- Podúkoly nedrobím mechanicky; není jich výrazně přes ~10 (jinak → návrh nového úkolu)?
- Checklist je jen tam, kde jsou drobné kroky téže osoby bez vlastního termínu/přiřazení?
- Nejdu hlouběji než tři úrovně?
- Je v úkolu reference na nahrávku z Teams?
- Jsou nejasnosti a chybějící informace viditelně označené, ne tiše domyšlené?
- Případné přejmenování/úprava popisu i nový úkol jsou jen návrhem ke schválení, ne provedené potichu?
