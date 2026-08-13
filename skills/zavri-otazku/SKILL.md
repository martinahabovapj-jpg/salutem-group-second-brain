---
name: zavri-otazku
description: >
  Použij tento skill vždy, když se má zavřít otevřená otázka ze second brainu —
  tedy položka ze sekce „Co zatím nevíme" v některém záznamu. Spouštěj ho, když
  uživatel řekne „zavři otázky", „projdi, co nevíme", „ověř tenhle bod", „dá se
  na to najít odpověď", nebo když se má na noc rozjet dávka agentů nad otevřenými
  otázkami. Skill určuje, co je platný doklad, kdy se otázka zavřít NESMÍ, a jak
  vypadá výstup, který jde ráno přečíst na jeden pohled. Jeden běh = jedna otázka.
---

# Zavírač otázek

Second brain má ke 13. 8. 2026 **119 záznamů a ~350 otevřených otázek** v sekcích
„Co zatím nevíme". Podstatná část z nich je **zodpověditelná ze zdrojů, které už
máme** — jen to nikdo neprošel. Tenhle skill je na to.

> **Nejcennější výstup není nový záznam. Je to zavřená smyčka s dokladem.**

## Zadání jednoho běhu

Dostaneš **cestu k záznamu** a **doslovný text jedné otázky**. Text doslovně
proto, že otázky nemají čísla — a čísla by se rozešla. (Doložené: procesní krok
se 13. 8. 2026 přečísloval ze 143 na 142. Na pořadí se nedá spoléhat.)

**Jedna otázka na jeden běh.** Nic víc. Bez tohohle pravidla se z toho stane
přepisování záznamu.

## Krok 0 — triáž. Nejdřív se rozhodni, jestli to jde vůbec zjistit

Tohle je pojistka, která šetří nejvíc času. Přečti otázku a zařaď ji:

| Typ otázky | Poznáš podle | Co s tím |
|---|---|---|
| **Zodpověditelná ze zdrojů** | „existuje X?", „jaká je hodnota Y?", „co obsahuje Z?", „udělalo se to?" | pokračuj |
| **Otázka na stav** | „jestli to běží", „jestli se to udrželo", „jestli se rozhodlo", „jestli to lidé používají" | ⏳ **nezavírej** — viz níž |
| **Otázka na člověka** | „proč se to nepoužívá", „jestli o tom někdo ví", „co si o tom myslí" | ⏳ napiš, na koho se má zeptat, a skonči |

### ⏳ Otázky na stav se nezavírají jako znalost

Stav žije ve Freelu, ne tady — to je pravidlo 2 z rozcestníku. Kdybys stav zapsal
do báze, vyrobíš tvrzení, které za měsíc neplatí.

**Co udělej:** označ otázku jako otázku na stav a **dopiš, kde se odpověď hledá** —
konkrétní Freelo úkol, nebo jméno člověka. Otázka v záznamu **zůstává**, ale
přestane vypadat jako mezera ve znalosti. Nic se nemaže.

Navrhovaný tvar zápisu:

```
- Jestli agent od června běží v provozu
  → ⏳ **otázka na stav, ne na znalost.** Patří do Freela (úkol 30081048).
```

## Krok 1 — ověř, že otázka je ještě otevřená

Přečti v záznamu celou sekci „Co zatím nevíme" **a okolní text**. Stává se, že
odpověď už v záznamu je, jen výš a jinými slovy — nebo že otázku někdo zavřel
a přeškrtl. Když je zavřená, skonči a řekni to.

## Krok 2 — hledej doklad, a v tomhle pořadí

| # | Zdroj | Kde |
|---|---|---|
| 1 | **Živý systém** | Make (čtecí token `MAKE_*`), Freelo API (`FREELO_*`) — nejsilnější doklad |
| 2 | **Přepisy a podklady** | `99 Archiv zdrojů/prepisy`, `.../podklady` |
| 3 | **Projektová složka Alfa** | `Salutem - Dokumenty\01 SG\Projekty\Alfa` |
| 4 | **Firemní knihovny** | SReal manuály, IT Governance (např. `IT Governance - Dokumenty\AI\brandguide`) |
| 5 | Jiný záznam v bázi | **jen jako vodítko, kam jít — ne jako doklad** |

### 🔴 Pojistka číslo jedna: doklad musí vést k primárnímu zdroji

Když záznam A tvrdí X, protože to tvrdí záznam B, **není to ověření — je to kruh.**

Doložený případ, proč to je pravidlo: v bázi tři měsíce stálo „brand manuál firma
nemá". Bylo to zapsané, citované a špatné — kompletní sada logo manuálů ležela
v `IT Governance - Dokumenty\AI\brandguide`. Nikdo tam nešel, protože „to už je
zapsané".

**Platný doklad je:** citace z přepisu nebo dokumentu · cesta k souboru
s datem · odpověď z API živého systému.

### Strop na hledání

Po **~10 hledáních bez dokladu** skonči verdiktem OTEVŘENO a napiš, co by
odpověď dalo. Nečti víc než ~15 souborů. Jinak se noc utratí na jednu větu.

## Krok 3 — verdikt. Jsou čtyři, ne dva

| Verdikt | Kdy |
|---|---|
| **ZAVŘENO** | máš primární zdroj, citaci a cestu |
| **ČÁSTEČNĚ** | část odpovědi máš, zbytek pojmenuj jako novou, konkrétnější otázku |
| **OTEVŘENO** | nenašel jsi — **a napiš, co by odpověď dalo**: který dokument, kdo, jaký dotaz |
| **NEPLATNÁ** | otázka už nemá smysl (ptá se na nástroj nebo variantu, kterou jsme opustili). **Musíš doložit, čím to přestalo platit** |

**Bez citace se nezavírá.** „Pravděpodobně", „vypadá to, že", „dá se předpokládat"
= OTEVŘENO. V noci se nemáš koho zeptat, takže domýšlení se nepozná.

## Krok 4 — výstup. Nepíšeš do záznamů, píšeš report

🔴 **Do záznamů v `01`–`08` nezapisuj.** Ani do Freela, ani do Make, ani do
Raynetu. Čtecí přístup je záměr, ne omezení, které se má obcházet.

**Výstup ulož jako vlastní soubor** (ne do společného — víc agentů by si přepsalo
navzájem):

```
99 Archiv zdrojů\_zavirani-otazek\<RRRR-MM-DD>\<slug-zaznamu>--<poradi>.md
```

Formát, ať se to ráno čte na jeden pohled:

```markdown
## [ZAVŘENO] 02 Use casy/databaze-realitnich-kancelari.md

**Otázka (doslovně):** Jestli se šablony na oslovení připravily a jestli se KzK databáze používá

**Doklad:** 99 Archiv zdrojů/prepisy/KzK aktuální stav.docx (19. 5. 2026)
**Citace:** „šablony se připraví předem a obsluha je pak Ctrl+C / Ctrl+V"

**Navrhovaný zápis do „Co zatím nevíme":**
- ~~Jestli se šablony na oslovení připravily~~ — **připravily se**, doloženo
  v přepisu z 19. 5. 2026. Jestli se databáze používá, zůstává otevřené.

**Nálezy pro jiné záznamy:** žádné
**Kolik to stálo:** 4 hledání
```

### Nález pro jiný záznam se hlásí, neopravuje

Když při hledání zjistíš, že **jiný záznam tvrdí něco jiného**, napiš to do
sekce „Nálezy pro jiné záznamy" — a **nesahej tam.**

Doložený důvod: 13. 8. 2026 se totéž zadání na registr aplikací napsalo do dvou
záznamů naráz (`architektura-internich-systemu` a `mapa-systemu`) a duplicitu
odchytila až kontrola. To se stalo člověku, který u toho byl. Noční agent, který
upraví pět záznamů, vyrobí rozpory, které nikdo nenajde.

## Best practice — všechno doložené z provozu

- **Čti dál než první nález.** Jeden nález umí vést ke špatnému závěru, který
  jiný soubor vyvrací. („Každý obchodník má svůj účet" znamenalo kalendář pro
  nahrávacího bota, ne třicet scénářů.)
- **Chyba, která nemá vysvětlení, je nález, ne překážka.** `Duplicate key error`
  odhalil, že tabulka obchodníků má 14 lidí, ne 28, jak stálo na třech místech.
- **„Systém to umí" a „u nás je to nastavené" jsou dvě různá tvrzení.**
  Ověřuje se to druhé.
- **Jedna otázka bývají dvě.** „Tabulka pro právní se nepoužívá" se rozpadlo na
  formulář (používá se, verzovaný) a evidenci úkolů (nepoužívá se). Když otázka
  míchá dvě věci, rozděl ji a odpověz zvlášť.
- **Když je zdrojem AI výstup, musíš to říct.** AI shrnutí hovoru podalo čísla,
  která model na callu vypsal, jako „diskutovaný potenciál". Kdo čte jen
  shrnutí, vezme odhad za fakt.
- **Cituj krátce a přesně.** Jedna věta ze zdroje je silnější než odstavec
  parafráze.
- **Zkomolené přepisy označ.** Automatické přepisy z Teams mají chyby ve jménech,
  číslech i názvech nástrojů. Číslo z nich neciteuj bez druhého zdroje — a když
  ho použiješ, napiš `⚠️ neověřeno`.

## Co nikdy nedělat

- **Nezavírej bez citace.**
- **Necituj bázi jako doklad** — jen jako vodítko, kam jít.
- **Nezapisuj do záznamů, do Freela, do Make ani do Raynetu.**
- **Nesahej na jiný záznam**, i když v něm vidíš chybu. Nahlas ji.
- **Nezavírej otázku na stav** jako znalost.
- **Neber víc než jednu otázku** na běh.
- **Nepiš, že něco „neexistuje"**, když jsi to jen nenašel. To je OTEVŘENO.

## Proč to vzniklo

13. 8. 2026 se ručně zavíralo osm otázek. **Čtyři z nich měly odpověď v bázi nebo
v archivu celou dobu** — jen to nikdo neprošel:

- brand manuály existovaly tři měsíce, zatímco báze tvrdila, že ne
- skórování use casů proběhlo, jen výsledek žil na webu, ne v tabulce
- tabulka „Urgence KN" je Google Sheet, což šlo přečíst z přílohy popisu kroku
- popsaná je jen jedna varianta obchodního procesu z pěti — stačilo se podívat
  do složky

Ke stejnému datu jsou v bázi **124 varování** a jen **11 explicitních
„neověřeno"** — takže nebezpečná tvrzení jsou ta, která žádné varování nemají
a znějí samozřejmě.

**Zavírání otázek je proto cennější než přidávání záznamů.** A protože se každá
otázka dá řešit samostatně, jde to dělat paralelně a přes noc.
