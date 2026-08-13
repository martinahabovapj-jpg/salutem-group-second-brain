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
máme** — jen to nikdo neprošel.

> **Nejcennější výstup není nový záznam. Je to zavřená smyčka s dokladem.**
> A druhý nejcennější je **hotová otázka pro člověka**, u které je předchroustané
> všechno kromě jednoho kliknutí.

## 🔴 Do provozních systémů nemáš přístup. Je to záměr, ne chyba.

**Freelo, Make, Raynet ani tokeny v `settings.json` nečti.** Ani se o to
nepokoušej — je to vědomé rozhodnutí firmy: **provozní systémy nesou klientská
a osobní data** a ta se posílat nemají.

Dvě věci, které z toho plynou:

1. **Nemarni rozpočet na zablokovaná volání.** V prvním ostrém běhu 13. 8. 2026
   se dva agenti ze tří pokoušeli přečíst tokeny, dostali zamítnutí, a ještě jim
   to ukrojilo z rozpočtu na hledání.
2. **Tvoje síla je archiv a firemní knihovny.** Když otázka potřebuje aktuální
   stav systému, tvým výstupem **není dohad, ale připravený dotaz** — viz verdikt
   *K OVĚŘENÍ V SYSTÉMU*.

## Zadání jednoho běhu

Dostaneš **cestu k záznamu** a **doslovný text jedné otázky**. Doslovně proto, že
otázky nemají čísla — a čísla by se rozešla. (Doložené: procesní krok se 13. 8.
přečísloval ze 143 na 142.)

**Jedna otázka na jeden běh.** Bez toho se z toho stane přepisování záznamu.

## Krok 0 — triáž. Čtyři možnosti, ne dvě

| Typ otázky | Poznáš podle | Kam to vede |
|---|---|---|
| **Zodpověditelná z dokumentů** | „existuje X?", „co obsahuje Z?", „jaká je hodnota Y?" | pokračuj hledáním |
| **Jednorázová změna, doklad je v systému** | „dostal to OCR?", „nasadilo se to?", „doplnila se ta pole?" | **K OVĚŘENÍ V SYSTÉMU** — připrav dotaz |
| **Průběžný stav** | „běží to?", „používají to lidé?", „udrželo se to?" | ⏳ **STAV** — nezavírá se nikdy |
| **Otázka na člověka** | „proč to nepoužívá?", „co si o tom myslí?" | ⏳ napiš **jméno**, na koho se zeptat |

### Rozdíl mezi jednorázovou změnou a průběžným stavem

Tenhle rozdíl je nový a je důležitý — původní pravidlo „otázky na stav se
nezavírají" bylo moc tupé a zakázalo by i užitečná zavření.

- **Jednorázová změna se nemůže odestát.** „Dostal PDF agent OCR?" — když se
  doplnilo, doplnilo se. Odpověď je **datovaný fakt** a patří do báze.
- **Průběžný stav se mění každý týden.** „Běží to v provozu?", „používají to
  lidé?" — to patří do Freela. Kdybys to zapsal do báze, vyrobíš tvrzení, které
  za měsíc neplatí.

## Krok 1 — než začneš hledat

1. **Přečti celou sekci „Co zatím nevíme" a okolní text.** Stává se, že odpověď
   už v záznamu je, jen výš a jinými slovy. Nebo že otázku někdo zavřel a
   přeškrtl — pak skonči a řekni to.
2. **Zkontroluj, jestli tatáž otázka není i v jiném záznamu.** Jeden grep.
   V prvním běhu se ukázalo, že otázka o OCR je ve dvou záznamech
   (`katastralni-agent` i `pdf-agent`). Když to nezjistíš, dva agenti udělají
   tutéž práci — a v nejhorším případě **dojdou k jinému verdiktu o témže faktu**.
3. **Není to náhodou složená otázka?** Řádek „jestli se šablony připravily
   a jestli se databáze používá" jsou **dvě otázky** — jedna zodpověditelná,
   druhá stav. Rozděl je a odpověz zvlášť.

## Krok 2 — pořadí zdrojů

Bez provozních systémů se hierarchie mění. **Tohle je nové a je to jádro skillu:**

| # | Zdroj | Co dokládá |
|---|---|---|
| 1 | **Artefakt sám** — soubor existuje, obsahuje X, má datum | **skutečnost.** Nejsilnější, co archivní agent umí |
| 2 | **Dokument s datem** — popis procesu, směrnice, business case, manuál | skutečnost **ke svému datu** |
| 3 | **Přepis hovoru** | **co kdo řekl**, ne jak to je |
| 4 | **AI výstup** (shrnutí, návrh) | jen **co model napsal** |
| 5 | Jiný záznam v bázi | **vodítko, kam jít — ne doklad** |

### 🔴 Pojistka: „primární zdroj" není totéž co „doklad skutečnosti"

Tohle je nejjemnější past v celém skillu.

**Přepis je primární doklad toho, že něco padlo — ne toho, že to je pravda.**
Doložené 12. 8. 2026: na hovoru vypsal model odhad velikosti trhu (2 500–3 500
kanceláří) a AI shrnutí ho podalo jako *„diskutovaný potenciál"*. Přepis
dokládá, že to na callu zaznělo. **Nedokládá, že to tak je.**

U faktické otázky je tedy citace z přepisu **vodítko, ne závěr.** Fakt musí
doložit artefakt.

### 🔴 Pojistka: dokument dokládá stav ke svému datu, ne dnešní

Nejdražší chyba, kterou archivní agent umí udělat — a v prvním běhu se ukázalo,
jak blízko byla:

> Poslední zmínka o OCR v přepisech je z **19. 6. 2026**: *„potřebuji tam dodat
> OCR."* Kdo by z toho uzavřel „OCR chybí", zavře otázku špatně — nástroj je
> v provozu od 08/2026.

**Když je nejnovější doklad starší než pár týdnů a otázka se ptá na něco, co se
mohlo změnit, nezavírej.** Vydej *K OVĚŘENÍ V SYSTÉMU* a napiš, kde se to pozná.

### 🔴 Pojistka: konzistence napříč záznamy není doklad

Když totéž tvrdí tři záznamy, má to nejčastěji **jeden zdroj** — a ten se musí
najít. „Brand manuál firma nemá" bylo zapsané konzistentně na třech místech
a všude špatně; sada ležela v `IT Governance - Dokumenty\AI\brandguide`.

### Rozpočet na hledání

**Orientačně 15 hledání.** Je to signál, ne zeď: po patnácti napiš, co máš, a
rozhodni, jestli pokračovat. Do rozpočtu **se nepočítá**:

- zablokované volání (to není práce)
- čtení samotného záznamu a jeho okolí

Nečti víc než ~15 souborů. V prvním běhu byla reálná spotřeba 8, 10 a 14
hledání — a **nejvíc nuancí našel ten, který šel nejdál**, takže tvrdý strop na
desítce by trestal důkladnost.

## Krok 3 — verdikt. Je jich pět a jeden příznak

| Verdikt | Kdy |
|---|---|
| **ZAVŘENO** | máš doklad ze zdroje 1–2, citaci, cestu a datum |
| **ČÁSTEČNĚ** | část odpovědi máš, zbytek pojmenuj jako novou, konkrétnější otázku |
| **K OVĚŘENÍ V SYSTÉMU** | odpověď skoro jistě existuje v provozním systému. **Napiš hotový dotaz** — který systém, kde se to pozná, co má člověk hledat |
| **OTEVŘENO** | nenašel jsi a nevíš, kde hledat — napiš, co by odpověď dalo |
| **NEPLATNÁ** | otázka už nemá smysl. **Musíš doložit, čím to přestalo platit** |
| ⏳ **STAV** | průběžný stav nebo otázka na člověka. Nezavírá se, jen se přesměruje |

### Verdikt *K OVĚŘENÍ V SYSTÉMU* je plnohodnotný výsledek, ne selhání

Není to „nezvládl jsem to". Je to **rozdělení práce**: ty uděláš drahou část
(najít, kde se to pozná), člověk udělá levnou (podívat se). Dobrý zápis vypadá
takhle:

```
K OVĚŘENÍ V SYSTÉMU — Freelo, projekt 561017
Hledej úkol o PDF agentovi. Ověř pole „V PROVOZU OD" a jestli je v popisu
zmíněné OCR. Archiv k 19. 6. 2026 říká, že OCR ještě chybělo.
```

### Povinná věta „proto to zavírá"

**Ke každému ZAVŘENO napiš jednu větu, jak citace odpovídá na otázku.** Mezi
citací a závěrem je vždycky úsudek a ten musí být vidět, aby ho šlo ráno
zkontrolovat.

Tohle pravidlo vzniklo z chyby v tomhle skillu: první verze měla v ukázce
zavření opřené o citaci, která byla **parafráze z báze** (kruh) a **v budoucím
čase** (nedokládá, že se něco stalo). Našel to agent při prvním běhu.

### Čas a modalita

**„Připravíme", „mělo by", „plánuje se", „nabídli jsme" nedokládají, že se něco
stalo.** Budoucí čas a podmiňovací způsob = OTEVŘENO nebo ČÁSTEČNĚ, nikdy
ZAVŘENO.

### Negativní nález není doklad neexistence

Když jsi nic nenašel, **napiš, kde jsi hledal** — „nenašel jsem" je silné jen
tak, jak široké bylo hledání. Nikdy nepiš „X neexistuje", když jsi to jen
nenašel.

## Krok 4 — výstup

🔴 **Do záznamů v `01`–`08` nezapisuj.** Report s navrženým zápisem; do báze to
přepíše člověk po kontrole.

Ulož jako **vlastní soubor** (víc agentů by si společný přepsalo):

```
99 Archiv zdrojů\_zavirani-otazek\<RRRR-MM-DD>\<slug-zaznamu>--<poradi>.md
```

Formát — příklad je **reálný**, takhle vypadal první ostrý běh:

```markdown
## [ZAVŘENO] 02 Use casy/katastralni-agent.md

**Otázka (doslovně):** Jestli PDF agent dostal OCR

**Doklad:** Freelo, projekt 561017, úkol 30522280, popis editovaný 13. 8. 2026
**Citace:** „…včetně rozpoznávání textu ze skenů (OCR)…" · „V PROVOZU OD: 08/2026"
**Proto to zavírá:** popis nástroje uvádí OCR jako součást funkcí a datum
uvedení do provozu, tedy odpovídá přímo na to, jestli OCR přišlo.

**Navrhovaný zápis do „Co zatím nevíme":**
- ~~Jestli PDF agent dostal OCR~~ — **ano**, v provozu od 08/2026, OCR je
  součástí funkcí. V provozu se nástroj jmenuje **PDFTOOL**.

**Zdroje, které jsem NEMĚL:** žádné (Freelo bylo v tomto běhu dostupné)
**Nálezy pro jiné záznamy:** `02 Use casy/pdf-agent.md` — tentýž doklad zavírá
i jeho otázku o OCR. Nesahal jsem tam.
**Kolik to stálo:** 8 hledání

⚠️ **V přepisech odpověď NENÍ** — poslední zmínka z 19. 6. 2026 je „potřebuji
tam dodat OCR", tedy stav před doplněním.
```

**Řádek „Zdroje, které jsem NEMĚL" je povinný v každém reportu.** Bez něj se
nepozná, jestli verdikt vznikl z plného obrazu, nebo z poloviny.

### Nález pro jiný záznam se hlásí, neopravuje — a dostane vlastníka

Když zjistíš, že **jiný záznam tvrdí něco jiného**, napiš to do sekce „Nálezy pro
jiné záznamy" a **nesahej tam.** Doložený důvod: 13. 8. 2026 se totéž zadání
napsalo do dvou záznamů naráz a duplicitu odchytila až kontrola.

Ale sama zmínka nestačí — v prvním běhu vyrobili nález pro jiný záznam **všichni
tři agenti**. Proto ke každému nálezu napiš:

- **který záznam** a **které tvrzení** se to týká
- **co s tím** (doplnit citaci / rozdělit tvrzení / ověřit v systému)
- jestli je to **rozpor** (někdo se mýlí), nebo jen **vodítko** (existuje zdroj,
  o kterém záznam neví)

Bez toho se z pojistky stane fronta bez příjemce — a to je selhání, které máme
v bázi popsané: *odrážka nemá vlastníka, podúkol má.*

## Druhý průchod — jen na ZAVŘENO

**Každé ZAVŘENO ověřuje druhý agent**, a ověřuje **jen to zavření**, ne celé
hledání. Dostane otázku, citaci, cestu ke zdroji a větu „proto to zavírá" — a má
jediný úkol: **pokusit se to vyvrátit.**

Ptá se na tři věci:

1. Odpovídá citace na tu otázku, nebo jen vypadá podobně?
2. Je zdroj artefakt, nebo je to přepis / jiný záznam / AI výstup?
3. Není doklad starší než změna, na kterou se otázka ptá?

Když neprojde, verdikt padá na ČÁSTEČNĚ nebo K OVĚŘENÍ V SYSTÉMU.

**Proč to tam je:** bez toho si agent známkuje sám — verdikt, kvalitu dokladu
i spotřebu hlásí tentýž, kdo chce skončit. Že první běh odhalil chybu ve skillu,
byla náhoda, ne návrh.

## Počítadlo chybných zavření

V `99 Archiv zdrojů\_zavirani-otazek\_bilance.md` se vede jednoduchá tabulka:
datum · záznam · verdikt · **obstálo / neobstálo při ranní kontrole**.

Bez počítadla by kritérium pro přepnutí na přímý zápis bylo nefalzifikovatelné —
chybné zavření by se poznalo až tím, že se podle něj někdo rozhodne.

**Rozhodnuto 13. 8. 2026:** zkušební doba je **15 zavření**, a i po ní se
odemkne přímý zápis **jen pro zavření doložená artefaktem nebo datovaným
dokumentem**, po druhém průchodu. Zavření opřené o **přepis a úsudek** zůstává
návrhem natrvalo. **NEPLATNÁ se nikdy nezapisuje automaticky** — ruší otázku,
a když se to splete, mezera v poznání zmizí ze seznamu.

Úvaha za tím rozhodnutím (včetně toho, proč vysoké číslo bezpečí nekoupí)
i **předem domluvené čtení výsledků** jsou v `_bilance.md`. Kdo bude branku
posouvat, ať si to přečte — je tam napsané, co má z jakého pozorování vyplynout.

## Best practice — všechno doložené z provozu

- **Čti dál než první nález.** Jeden nález umí vést ke špatnému závěru, který
  jiný soubor vyvrací. („Každý obchodník má svůj účet" znamenalo kalendář pro
  nahrávacího bota, ne třicet scénářů.)
- **Chyba, která nemá vysvětlení, je nález, ne překážka.** `Duplicate key error`
  odhalil, že tabulka obchodníků má 14 lidí, ne 28, jak stálo na třech místech.
- **U „neexistuje" se aktivně snaž najít protipříklad**, ne potvrzení.
- **„Systém to umí" a „u nás je to nastavené" jsou dvě různá tvrzení.**
- **Nevěř polím, která vypadají autoritativně.** `license.operations` v Make API
  hlásilo hodnotu, která znamenala trojnásobný rozdíl v rozpočtu.
- **Cituj krátce a přesně.** Jedna věta ze zdroje je silnější než odstavec
  parafráze.
- **Zkomolené přepisy označ.** Automatické přepisy z Teams mají chyby ve jménech,
  číslech i názvech nástrojů. Číslo z nich neciteuj bez druhého zdroje; když ho
  použiješ, napiš `⚠️ neověřeno`.
- **Když najdeš jméno nástroje nebo cestu, kterou báze nezná, napiš to.** V prvním
  běhu se takhle zjistilo, že PDF agent se v provozu jmenuje PDFTOOL.

## Co nikdy nedělat

- **Nečti tokeny ani provozní systémy.** Není to omezení k obejití.
- **Nezavírej bez citace a bez věty „proto to zavírá".**
- **Necituj bázi jako doklad** — jen jako vodítko, kam jít.
- **Nezavírej podle dokumentu, který je starší než změna, na kterou se ptáš.**
- **Nezapisuj do záznamů v 01–08.**
- **Nesahej na jiný záznam**, i když v něm vidíš chybu. Nahlas ji s vlastníkem.
- **Nezavírej průběžný stav** jako znalost.
- **Neber víc než jednu otázku** na běh.
- **Nepiš, že něco „neexistuje"**, když jsi to jen nenašel.

## Proč to vzniklo

13. 8. 2026 se ručně zavíralo osm otázek. **Čtyři měly odpověď v archivu celou
dobu** — brand manuály existovaly tři měsíce, zatímco báze tvrdila, že ne;
skórování use casů proběhlo, jen výsledek žil na webu; tabulka „Urgence KN" je
Google Sheet, což šlo přečíst z přílohy popisu kroku; popsaná je jen jedna
varianta obchodního procesu z pěti.

Ke stejnému datu je v bázi **124 varování** a jen **11 explicitních „neověřeno"**
— takže nebezpečná jsou tvrzení, která žádné varování nemají a znějí samozřejmě.

**První ostrý běh (13. 8., tři agenti) přinesl tři poučení, která jsou výš
zapracovaná:** archiv sám nestačí u věcí, které se mohly změnit · citace může
být pravdivá a přitom nedokládat nic · a agent, který si známkuje sám, potřebuje
druhý průchod.
