---
name: freelo-projekt-z-prepisu
description: Použij tento skill VŽDY, když máš z přepisu callu (porady, schůzky, hovoru s kolegy) vytvořit projekt ve Freelu — tedy projekt, to-do listy, úkoly a podúkoly. Spouštěj ho kdykoli uživatel zmíní přepis, zápis z hovoru, "založ projekt", "udělej z toho projekt ve Freelu", "vytvoř to-do listy z callu" a podobně, i když to neřekne přesně takhle. Skill určuje, JAK se má projekt strukturovat, pojmenovat a jak věrně přepsat realitu z callu — samotné zakládání přes Freelo API řeší existující skript.
---

# Tvorba projektu ve Freelu z přepisu callu

Tento skill říká, jak z přepisu callu postavit projekt ve Freelu tak, aby vypadal, jako by ho založil zkušený projektový manažer, který na tom callu seděl — na míru našemu kontextu, kompletní, přehledný a okamžitě pochopitelný i pro člověka, který na callu nebyl.

Skill řeší jen **obsah a strukturu** projektu (jak přemýšlet, pojmenovávat, kolik toho dělat, jak věrně zachytit realitu). Samotné zakládání přes Freelo API obstará existující skript — tím se nezabývej.

## Hlavní princip: věrnost před vynalézavostí

Nejdůležitější pravidlo celého skillu. Uživatel se na výstup potřebuje **spolehnout** — že je v projektu všechno tak, jak to na callu zaznělo, a že nic není tiše domyšlené nebo vynechané.

Z toho plyne:

- **Zachyť vše konkrétní z přepisu.** Jména lidí, termíny, čísla, konkrétní rozhodnutí, připomínky, insighty, varování — to všechno patří do projektu, ne jen obecná kostra. Když na callu padlo "tohle musí schválit Milada do pátku", výstupem je úkol "Odsouhlasit návrh s Miladou" s termínem, ne obecné "Schválit návrh".
- **Nic si nevymýšlej.** Co v přepisu nezaznělo, do projektu nepatří jako fakt. Raději úplný a o něco delší projekt než krátký a osekaný — strop počtu úkolů (viz níže) nikdy nesmí jít proti úplnosti.
- **Co je nejasné, jde transparentně nahoru** (viz sekce "Práce s nejasnostmi"). Nejistota se nikdy neschovává do domyšleného textu úkolu.

Když přepis odporuje tomuto skillu jen zdánlivě (např. na callu zaznělo hodně věcí → vznikne hodně úkolů), má přednost věrnost přepisu. Skill řídí *formu*, přepis řídí *obsah*.

## Struktura projektu

Postupuj vždy podle této logiky:

**Projekt = jedna iniciativa z callu.** Co se na callu řešilo jako jeden celek, je jeden projekt.

**To-do listy = fáze.** Projekt vždy rozděl do logických fází a každá fáze je samostatný to-do list. Fáze odvoď z toho, co dává smysl pro daný projekt — nemáme pevné checklisty. U většiny projektů přirozeně vyjde něco jako Příprava → Realizace → Testování/Pilot → Nasazení/Předání, ale neber to jako šablonu k vyplnění: pojmenuj a poskládej fáze podle reality konkrétního projektu. U menšího projektu klidně stačí méně fází.

**Úkoly = konkrétní kroky uvnitř fáze.** Do každého to-do listu patří konkrétní, srozumitelné úkoly. Fázi už nese název seznamu, takže **nikdy nedávej fázi do názvu úkolu** — žádné `[Příprava] Sestavit seznam`. To je přesně ten nelidský styl, kterému se vyhýbáme. Správně je seznam "Příprava" a v něm úkol "Sestavit seznam konkurenčních objektů".

**Podúkoly = jen tam, kde to dává smysl.** Selský rozum: když je úkol velký blok práce a chceš v něm vidět, že postupně logicky kráčíte k cíli, rozpad ho na pár podúkolů. U jednoduchého úkolu, který se udělá najednou, žádné podúkoly nedělej. Nedrob mechanicky.

## Granularita

Cílem je přehlednost. Orientačně:

- **Na jeden to-do list (fázi) maximálně ~5–7 úkolů.** Když ti vychází víc, nejspíš jde o dvě fáze, nebo některé "úkoly" jsou ve skutečnosti podúkoly jednoho většího úkolu.
- **Podúkoly dělej jen u velkých bloků** a i tam střídmě — pár kroků, které ukazují postup, ne vyčerpávající rozpis.
- **Pozor na opačný extrém:** dřív vznikaly projekty s 15+ úkoly v jednom seznamu a fází nacpanou do názvů. Tomu se vyhýbáme strukturou (fáze = seznamy), ne tím, že bychom zahazovali obsah z callu.

Pokud je toho z callu opravdu hodně, projekt bude větší — ale pořád čistě rozdělený do fází se zvládnutelnými seznamy. Úplnost a přehlednost jdou ruku v ruce, ne proti sobě.

## Pojmenování

**Název projektu** má fungovat jako okamžitý kontext. Řešíme hodně věcí napříč oblastmi a člověk si potřebuje hned vybavit, o co jde. Proto:

- Krátký, lidský, úderný. Každý, kdo si ho přečte, hned ví, co se v projektu řeší.
- Žádná fancy slova, žádné odbornosti, žádný akademický jazyk. Čistá lidština, k věci.
- Klidně oblast/štítek na začátek pro rychlou orientaci, když to pomůže (např. "Pronájmy – Ceny pokojů podle konkurence").

**Příklady:**

- Dobře: `Ceny pokojů podle konkurence`
- Dobře: `Pronájmy – Automatický sběr recenzí`
- Špatně: `Implementace systému dynamické cenotvorby na bázi konkurenční analýzy` (akademické, dlouhé)

**Názvy úkolů** — neutrální infinitiv, spisovná čeština, lidská a srozumitelná. Tak, jak by úkol napsal kolega, ne stroj.

- Dobře: `Sestavit seznam konkurenčních objektů`
- Dobře: `Ověřit, že objekty mají ceny na vlastních webech`
- Dobře: `Odsouhlasit návrh řešení s Miladou`
- Špatně: `Client materials preparation` (cizí jazyk, neosobní)
- Špatně: `[Příprava] Competitor objects list assembly task` (fáze v názvu, nelidské, anglicky)

## Onboarding brief (shrnutí projektu)

K projektu vždy připoj stručné shrnutí, podle kterého se za půl minuty naloďuje i člověk, který na callu nebyl. Umísti ho na začátek — buď do popisu projektu, nebo jako první to-do list pojmenovaný např. "Shrnutí projektu" / "O co jde".

Brief je věcný, žádná vata. Obsahuje (jen to, co z callu skutečně zaznělo):

- **Proč** — důvod a motivace, co se má vyřešit.
- **Co teď bolí** — současný problém / bolístka, kterou to má odstranit.
- **Cíl** — čeho chceme dosáhnout.
- **Kdo to chce / kdo to řeší** — zadavatel a lidé zapojení do realizace.
- **Timeline** — termíny, milníky, deadline, pokud zazněly.

Když některý z těchto bodů na callu nezazněl, **nevymýšlej ho** — uveď ho s poznámkou, že chybí a je potřeba doplnit (viz dál). Lepší přiznané "timeline na callu nezazněl, doplnit" než smyšlené datum.

## Práce s nejasnostmi

Přepisy bývají věcné, ale ne vždy. Lidé myslí nahlas, odbíhají, něco řeknou a zase zavrhnou. Když něčemu nerozumíš, něco si v přepisu protiřečí, nebo si nejsi jistý — **finální slovo má vždy člověk, ne ty.** Princip:

- **Nejasnosti nikdy neschovávej do domyšleného úkolu.** Když nevíš, co přesně bylo myšleno, neudělej z toho sebejistě znějící úkol.
- **Vytvoř sběrný to-do list** pojmenovaný např. `⚠️ K vyjasnění / doplnit`. Sem dej všechno, co jsi nepochytil, čemu jsi nerozuměl, co si protiřečilo nebo co v briefu chybí. Formuluj to jako konkrétní dotazy: "Na callu nezaznělo, kdo realizaci schvaluje — doplnit", "Padlo API i scraping, není jasné, pro co jste se rozhodli — rozhodnout". Uživatel pak na jednom místě vidí, kde rozhodnout, místo aby to lovil napříč úkoly.
- **Drobnosti smíš navrhnout** podle nejlepšího úsudku zkušeného PM — ale viditelně označené jako návrh (např. úkol s poznámkou "(návrh – ověřit)"), ať je jasné, že to není z callu a člověk to má potvrdit nebo smazat.

## Postup práce

1. **Přečti celý přepis** a udělej si obraz: o co jde, proč, kdo, jaké padly konkrétní věci, rozhodnutí, termíny, jména, insighty.
2. **Sestav onboarding brief** (proč / co bolí / cíl / kdo / timeline) z toho, co reálně zaznělo.
3. **Navrhni fáze** projektu (= to-do listy) odvozené z reality projektu.
4. **Naplň fáze úkoly** — konkrétními, v lidské češtině, neutrální infinitiv, se všemi konkrétními detaily z callu (jména, termíny, čísla, připomínky). U velkých bloků přidej pár podúkolů na sledování postupu.
5. **Posbírej nejasnosti** do listu `⚠️ K vyjasnění / doplnit`.
6. **Navrhni krátký, úderný název projektu.**
7. **Ukaž uživateli návrh celé struktury a počkej na schválení**, teprve pak zakládej ve Freelu. Tím se předejde tomu, že vznikne projekt, který se pak pracně upravuje. Při náhledu uveď: název, fáze (to-do listy), úkoly a podúkoly v nich, brief a seznam nejasností.

## Rychlý kontrolní seznam před založením

- Název je krátký, lidský, úderný, bez odborností?
- Fáze jsou to-do listy a žádná fáze není v názvu úkolu?
- Úkoly jsou v lidské spisovné češtině, neutrální infinitiv?
- Jsou v úkolech všechny konkrétní věci z callu (jména, termíny, čísla, připomínky)?
- Podúkoly jen u velkých bloků, ne mechanicky všude?
- Žádný seznam nemá výrazně přes ~7 úkolů?
- Je v projektu onboarding brief pro člověka, který na callu nebyl?
- Jsou všechny nejasnosti a chybějící informace v listu `⚠️ K vyjasnění / doplnit`, a ne tiše domyšlené?
