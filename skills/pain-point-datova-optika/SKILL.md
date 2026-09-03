---
name: pain-point-datova-optika
description: Použij tento skill VŽDY, když máš u nějaké bolesti, problému nebo požadavku určit, v čem je vlastně skutečná příčina a co s tím udělat. Spouštěj ho, když uživatel řekne něco jako "co je tady vlastně problém", "projeď mi tenhle pain point", "je to case pro AI?", "proč to nefunguje", "zanalyzuj těchhle 20 bolestí z rozhovorů", "seskup mi to podle příčiny", "co máme udělat dřív", ale i když jen vloží přepis rozhovoru nebo tabulku pain pointů — i když to neřekne přesně takhle. Skill se na každou bolest podívá šesti stejnými otázkami (kdo rozhoduje, co tím trpí, kde informace vzniká, kde bydlí, o jaká data jde, je pravidlo zapsané), najde slabé místo, stanoví diagnózu, ověří třemi otázkami, jestli je to práce pro AI, a navrhne zásah včetně toho, co musí být hotové dřív. Cílem je, aby se všechny bolesti daly srovnávat mezi sebou a aby se AI nepoužila jako náplast na chybějící proces nebo chybějící dohodu.
---

# Jak se dívat na každou bolest stejnou optikou

Tenhle skill dělá jednu věc: vezme jakoukoli bolest, kterou někdo popsal (v rozhovoru, v tabulce, v požadavku), a projde ji **šesti stejnými otázkami**. Když se dvě bolesti popíšou takhle, dají se poprvé porovnat, i když jedna je z účtárny a druhá z právního oddělení.

Výstupem **není řešení**. Výstupem je **rozbor**: co se ve skutečnosti děje, jakou to má diagnózu, jaký typ zásahu jí odpovídá a co musí být hotové dřív.

Navazuje na skill `freelo-triage-poptavky`, ale nepřekrývá se s ním. **Tady se ptáme „v čem je příčina a co s tím", tam „jakou dráhou to pošleme a za kolik".** Návratnost ani dráhu tady nepočítej.

---

## Než začneš: co které slovo znamená

Celý skill stojí na několika pojmech. Tady je jejich lidský význam. Podrobněji, včetně toho, jak se jim říká v oboru, je v `references/sest-otazek.md`.

| Pojem | Co to znamená |
| --- | --- |
| **Bolest (pain point)** | To, co člověk popsal jako svůj problém. Typicky ve formě „tohle mě zdržuje" nebo „tohle mě štve". |
| **Symptom** | Jak se ta bolest projevuje. Skoro vždycky je to spotřeba času: „přepisuju to dvě hodiny týdně". |
| **Co se děje** | Vysvětlení, proč ta práce vůbec musí existovat. To je to, co hledáme. Symptom a tohle jsou vždycky dvě různé věty. |
| **Šest otázek** | Šest míst, kterými musí projít cesta od člověka až ke konkrétnímu údaji v systému. Když jedno z nich chybí, vzniká ruční práce. |
| **Slabé místo** | To z těch šesti míst, kde se cesta trhá jako první. Zásah patří sem, ne o dva kroky výš. |
| **Diagnóza** | Pojmenování toho, co se děje, z pevného seznamu dvanácti (A1 až A12). Vždycky právě jedna. Díky pevnému seznamu se bolesti dají sčítat a seskupovat. |
| **Rozbor** | Celý výstup u jedné bolesti: symptom, šest otázek, slabé místo, diagnóza, zásah, předpoklady a otevřené otázky. Diagnóza je jedna jeho položka, ne totéž. |
| **Předpoklad** | Co musí být hotové dřív, aby zásah vůbec mohl fungovat. |
| **Obtok** | Zásah, který příčinu neopravuje, jen ji obchází. Někdy je to správná volba, ale musí se to říct nahlas. |

---

## Základní myšlenka, na které to stojí

**Data jsou zachycený odpad procesu.** Když nějaká práce neběží v systému, nezůstane po ní žádný záznam — a co nezůstalo, to už žádný report ani žádná AI nevykouzlí.

Z toho plyne věta, kterou se řídí celý skill: **každé číslo, o které se někdo opírá, musí být dohledatelné až k okamžiku v procesu a k člověku, který za ten okamžik odpovídá.** Když ta cesta chybí, číslo není fakt, ale odhad — a práce, která ho vyrábí, je nezrušitelná.

Tři pravidla, která z toho vycházejí:

1. **Nevymýšlej si.** Co v podkladech není, napiš `TOHLE NEVÍM` a přidej otázku pro člověka, který to ví. Domyšlená odpověď je horší než přiznaná neznalost, protože se podle ní pak rozhoduje.
2. **Hledej, kde se to trhá jako první.** Ne kde to nejvíc bolí — bolí to obvykle až na konci, u toho, kdo to zachraňuje ručně.
3. **Zásah patří na slabé místo.** Oprava vedle něj nedrží: report postavený na datech, u kterých není dohodnuto, co je pravda, se rozpadne při první nesrovnalosti.

---

## Postup u jedné bolesti

### Krok 1 — Napiš symptom jednou větou

Kdo, co dělá, jak často, kolik času to bere. Čísla ber z podkladů. Když číslo nikde není, napiš `neuvedeno` a nedoplňuj vlastní odhad.

Příklad: *„Šiška dvakrát měsíčně ručně přenáší výplaty klientům z tabulky od účtárny do své tabulky; jedna dávka měla 280 řádků a zabrala 1,5 hodiny."*

### Krok 2 — Projdi šest otázek

Ke každé otázce napiš, co v téhle bolesti platí. Když odpověď v podkladech není, napiš `TOHLE NEVÍM`. Když odpověď je „nic takového neexistuje", napiš `CHYBÍ` — to je nález, ne mezera.

Každá otázka má i krátké jméno (v závorce). Otázku používej, když se ptáš; jméno, když na to místo odkazuješ. Podrobné doptávací otázky jsou v `references/sest-otazek.md`.

**1. KDO ROZHODUJE** *(odpovědnost)* — Kdo má právo říct, co je v téhle věci pravda?
Pozor, není to totéž jako „kdo to dělá". Ten, kdo agendu vykonává, obvykle nemá mandát rozhodnout, jak se to má dělat. Zajímá nás ten, kdo rozhoduje.

**2. CO TÍM TRPÍ** *(k čemu to je)* — Které rozhodnutí nebo které číslo je kvůli tomu špatné nebo pozdě?
Když na tuhle otázku není odpověď, může to znamenat, že se ta práce dělá jen ze zvyku. To je samostatný a velmi hodnotný nález.

**3. KDE TO VZNIKÁ** *(vznik informace)* — V jakém okamžiku ta informace poprvé existuje a kdo ji zadává?
A hlavně: zůstane po tom okamžiku záznam s datem a časem, nebo to ví jen člověk? Bez záznamu nelze spočítat, jak dlouho co trvá.

**4. KDE TO BYDLÍ** *(domov informace)* — Ve kterém systému je ta informace uložená tak, že se tomu dá věřit?
A kolik dalších míst tu samou informaci drží? Pokud ji drží dvě místa a není řečeno, které platí, je to nález.

**5. O CO VLASTNĚ JDE** *(rozpoznání věci)* — O jakou věc se jedná (nemovitost, klient, platba, smlouva) a dá se poznat, že jde v obou systémech o tu samou věc?
Když se dvě evidence párují podle adresy nebo podle jména, protože chybí společné číslo, je to nález.

**6. JE TO ZAPSANÉ** *(zápis pravidel)* — Existuje pravidlo, definice a informace o citlivosti někde jinde než v hlavě člověka nebo v barvě buňky?
A víme, odkud kam ta data tečou a kdo tu cestu umí změnit?

### Krok 3 — Najdi slabé místo

Označ všechna místa, kde odpověď byla `CHYBÍ`. Pak jdi **tímto seznamem odshora a zastav se u prvního bodu, který platí** — to je slabé místo. Ostatní chybějící místa jsou důsledky, ne samostatné problémy.

1. **Není nikdo, kdo by o téhle věci mohl rozhodnout** → slabé místo je **odpovědnost**.
   Poznáš to tak, že kdybys chtěla zásah zadat, nemáš komu. Bez toho nelze uzavřít nic dalšího.
2. **Záznam nevzniká vůbec** → slabé místo je **vznik informace**.
   Informace existuje jen v hovoru, mailu nebo v hlavě. Tady se často mylně navrhuje nástroj, ale chybí krok zápisu.
3. **Záznam vzniká, ale není dohodnuto, kde je pravda** → slabé místo je **domov informace**.
   Dvě místa drží totéž a lidé se hádají, čí číslo platí.
4. **Pravda je dohodnutá, ale data nejde spojit** → slabé místo je **rozpoznání věci**.
   Chybí společné číslo, takže se páruje ručně podle jména nebo adresy.
5. **Data jde spojit, ale význam, pravidlo nebo citlivost nejsou zapsané** → slabé místo je **zápis pravidel**.
6. **Zvláštní případ:** když ta věc má existující zdroj i systém, ale chybí závazná definice čísla (dva lidé spočítají různě), slabé místo je **k čemu to je**.
7. **Nic z toho neplatí** → slabé místo žádné, cesta k datům je celá. To je diagnóza A12, viz krok 4.

**Když víc věcí spadne na totéž místo, přednost má ta rozhodovací před přenosovou.** Konkrétně: dokud není dohodnuto, kde je pravda, nelze zadat propojení systémů — takže „chybí dohoda" je příčina a „člověk to přepisuje" je důsledek, ne naopak.

Nakonec slabé místo pojmenuj jednou **diagnózou z `references/archetypy.md`** (A1 až A12). Když se ti zdá, že žádná nesedí, projdi tabulku záměn na konci toho souboru — obvykle jde o tu samou věc pod jiným jménem. Novou diagnózu nevymýšlej, rozbila by srovnatelnost všech ostatních bolestí.

### Krok 4 — Ověř třemi otázkami, jestli je to práce pro AI

Tohle je nejdůležitější brzda celého skillu. Brání tomu, aby se AI navrhla na něco, co AI vyřešit nemůže. Musí projít **všechny tři**:

1. **Existují vůbec data, na kterých by AI pracovala?**
   Když informace nikde nevzniká, není co zpracovávat. Nejdřív musí začít vznikat.
2. **Je jednoznačné, co je pravda?**
   Když dva systémy tvrdí každý něco jiného a není dohodnuto, který platí, AI ten spor jen zrychlí.
3. **Je ta práce opravdu myšlenková?**
   Tedy čtení, porovnávání, posuzování, vytěžování z dokumentů, generování textu, hledání v nepřehledném obsahu. **Pokud je to jen přenos hotových údajů z jednoho systému do druhého, není to práce pro AI, ale pro propojení systémů.** Tohle je nejčastější chyba v celém oboru.

Když projdou všechny tři a zároveň v kroku 3 nevyšlo žádné slabé místo, znamená to, že **cesta od rozhodnutí až ke konkrétnímu údaji je celá: data existují, je jasné, co je pravda, a pravidla jsou zapsaná.** Ta bolest tedy nevznikla z žádné mezery — ta práce je prostě práce a jediné, co s ní jde udělat, je nechat ji dělat stroj. To je diagnóza A12.

Výsledek napiš jako `AI: ano` / `AI: ne, protože…` / `AI: až po…`.

### Krok 5 — Navrhni zásah

Použij **jen těchto šest typů**, jinak se výstupy nedají skládat dohromady. V závorce je odborný název, kdybys ho potřebovala použít venku:

| Typ zásahu | Co to znamená v praxi |
| --- | --- |
| **dohodnout, kdo rozhoduje** (governance) | Určit vlastníka věci a jeho zástup, dát mu mandát rozhodnout o definicích a přístupech. |
| **změnit postup** (proces) | Přidat krok zápisu, povinná pole, kontrolu na vstupu, definici hotového zadání. |
| **rozhodnout o systémech a propojit je** (architektura) | Říct, který systém je pro tuhle věc autoritativní, a teprve pak postavit přenos dat. |
| **uklidit data** (datová práce) | Doplnit společná čísla, spojit duplicity, přenést historii. |
| **zapsat pravidla a významy** (metadata) | Sepsat definice, pravidla, citlivost dat a cestu, kudy data tečou. |
| **AI nebo automatizace** | Nechat stroj dělat myšlenkovou nebo mechanickou práci, která zbyla. |

K tomu vždycky doplň:

- **Předpoklady** — co musí být hotové dřív, jmenovitě. Když žádné nejsou, napiš proč (dá se to řešit samostatně).
- **Kdo o tom rozhodne** — konkrétní role nebo jméno. „Management" není odpověď; když to nevíš, je to otázka.
- **Obtok, nebo oprava** — viz níže.
- **Úroveň v pyramidě L0 až L3** — diagnózy, kde je slabé místo v datech, dohodách nebo zápisu, jsou typicky L0. Zbytek podle toho, koho to zasahuje: jeden člověk L3, oddělení L2, byznysová změna L1.

### Krok 5b — Obtok, nebo oprava?

Někdy je správné příčinu neopravovat. Když je náprava pomalá a drahá, ale existuje rychlý způsob, jak bolest odstranit, je legitimní jít obtokem. Pravidlo: **obtok se smí navrhnout, ale musí být pojmenovaný**, jinak se automatizací sníží tlak na to, aby se příčina vůbec někdy spravila.

Napiš tedy `oprava` (zásah míří na slabé místo) nebo `obtok` (bolest zmizí, příčina zůstává) a u obtoku jednu větu, **co zůstává nespravené**.

### Krok 6 — Sepiš, co zbývá vyjasnit

Každé `TOHLE NEVÍM` z kroků 2 až 5 má právě jednu otázku, napsanou lidsky a připravenou k odeslání konkrétnímu člověku. Na konci si to zkontroluj oběma směry: žádné `TOHLE NEVÍM` bez otázky a žádná otázka, která by v rozboru neměla oporu.

---

## Jak má rozbor vypadat

```
**[název bolesti]**
Diagnóza: [A#: lidský název] · slabé místo: [jméno místa] · zásah: [typ] · AI: [ano/ne/až po] · [oprava|obtok]

Symptom: [kdo, co, jak často, kolik času]
Co se děje: [1–2 věty, srozumitelné i pro toho, kdo o datech nic neví]

Šest otázek:
• Kdo rozhoduje — …
• Co tím trpí — …
• Kde to vzniká — …
• Kde to bydlí — …
• O co vlastně jde — …
• Je to zapsané — …

Zásah: [typ] — [co konkrétně udělat, 1–2 věty]
Předpoklady: [co musí být dřív / žádné, protože …]
Zůstává nespravené: [jen u obtoku]
Rozhodne: [role/jméno] · Pyramida: [L0–L3]

Zbývá vyjasnit:
1. [otázka] → [komu ji poslat] (→ k čemu odpověď poslouží)
```

---

## Vyplněný rozbor (takhle to má vypadat)

```
**Přepisování výplat klientům z účtárny (Šiška)**
Diagnóza: A2 – Není dohodnuté, kde je pravda · slabé místo: domov informace
Zásah: rozhodnout o systémech a propojit je · AI: ne · oprava
Důsledky: A7 (člověk je propojka), A4 (chyby se nechytají u zdroje), A11 (visí to na jednom člověku)

Symptom: Dvakrát měsíčně ručně přenáší výplaty klientům z excelové tabulky od účtárny do své
zamčené záložky; jedna dávka měla 280 řádků a zabrala 1,5 hodiny. Z její tabulky pak data putují
do klientské aplikace a znovu ručně do Raynetu.

Co se děje: To, co klient uvidí v aplikaci, se dnes bere ze zamčené záložky v tabulce jedné osoby.
Účetní systém je zdroj, aplikace je spotřebitel, ale pravda leží mezi nimi v Excelu. Dokud není
řečeno, který systém je autoritativní, nedá se zadat ani propojení, ani zástup.

Šest otázek:
• Kdo rozhoduje — vlastníkem procesu je ona; kdo rozhoduje o datech o výplatách, TOHLE NEVÍM
• Co tím trpí — správnost a včasnost výplat a to, co klient vidí v aplikaci
• Kde to vzniká — účtárna vyplácí a posílá Excel; její kontrola odhalí chybějící klienty, takže
  kontrola u zdroje CHYBÍ; účtárna čeká na její „je to OK", takže cyklus stojí na jedné osobě
• Kde to bydlí — účetní systém, sdílená tabulka, Raynet, klientská aplikace, SharePoint;
  autoritativní místo pro výplatu CHYBÍ
• O co vlastně jde — jednotlivé platby (úrok, nájem) párované na klienta a obchodní případ
• Je to zapsané — formát dohodnutý neformálně; její kontrolní pravidla nejsou zapsaná nikde

Zásah: rozhodnout o systémech a propojit je — určit, že autoritativním místem pro výplaty je účetní
systém, aplikace bere data odtud, a kontrolu převést na kontrolu u zdroje.
Předpoklady: 1) rozhodnutí, který systém je autoritativní; 2) sepsat její kontrolní pravidla —
bez toho propojení tiše ztratí to jediné, co dnes chyby zachytává.
Rozhodne: hlavní účetní nebo CFO + IT + vlastník procesu · Pyramida: L0, dopad L2

Zbývá vyjasnit:
1. Který systém má být zdrojem pravdy pro výplatu klientovi? → CFO a IT
2. Podle jakých pravidel poznáš, že v podkladu od účtárny někdo chybí? → Šiška
   (→ tato pravidla se musí zapsat, jinak je propojení zahodí)
3. Umí účetní systém předat data do aplikace přímo? → IT
4. Kdo tuhle agendu dělá, když týden chybíš? → vlastník procesu
```

Všimni si tří věcí, které dělají rozbor použitelným: „co se děje" je napsané lidsky a je jinou větou než symptom · předpoklady jsou konkrétní a jeden z nich je netechnický (sepsat pravidla z hlavy člověka) · otázky jsou adresované jmenovitě.

---

## Když projíždíš víc bolestí najednou

Tady má optika největší cenu. Čtyřicet bolestí vypadá jako čtyřicet problémů; po stanovení diagnóz jich zbyde pět.

1. **Každou bolest proženeš kroky 1 až 5** a z jejího rozboru vyplníš jeden řádek tabulky. Hlavičku vezmi z `assets/tabulka-sablona.csv`.
2. **Seskup podle diagnózy, ne podle oddělení.** Ke každé skupině sečti čas z podkladů. To je první tvrdý argument, protože to říká, kolik hodin týdně visí na jedné jediné příčině.
3. **Najdi rozhodnutí, která odblokují nejvíc.** Vypiš, která jednotlivá rozhodnutí (obvykle „který systém je pro tuhle věc autoritativní" nebo „kdo o tom rozhoduje") odblokují nejvíc bolestí. Formát: `[rozhodnutí] → odblokuje N bolestí, X hodin týdně`. **Tohle je hlavní výstup dávky** — je to jediná forma, ve které se s tím dá jít za majitelem.
4. **Odděl, co jde hned, od toho, co na něco čeká.** Dvě krátké skupiny. Nezakrývej, že druhá je obvykle větší.
5. Nad ~25 bolestí to řekni a navrhni rozdělení do dávek.

U dávky **nepiš plný rozbor ke každé bolesti**, pokud si ho uživatel nevyžádá. Stačí tabulka, skupiny a odblokovávající rozhodnutí; plné rozbory nabídni k vybraným.

---

## Časté chyby

- **Skok na řešení.** Když se při druhém kroku objeví „na tohle stačí udělat agenta", vrať se ke krokům 3 a 4. Tohle není brainstorming nástrojů.
- **Zaměnit toho, kdo rozhoduje, s tím, kdo to dělá.** Když je to tentýž člověk a nemá zástup, je to samostatná diagnóza (A11), ne detail.
- **Vydávat spotřebu času za příčinu.** „Zabere to tři hodiny" je vstup do prioritizace, ne vysvětlení, proč ta práce vůbec musí existovat.
- **Nafouknout slabé místo na „je to celé špatně".** Slabé místo je jedno a diagnóza je jedna. Když to nejde omezit, je to obvykle víc bolestí slepených do jedné — rozděl je a řekni to.
- **Tiše srovnat rozpor.** Když jeden člověk tvrdí, že autoritativní je systém, a druhý přitom pracuje v tabulce, ten rozpor pojmenuj. Právě on je často ta příčina.
- **Zapomenout na to, co drží v hlavě člověk.** Když se ruční krok ruší, jeho nezapsaná kontrolní pravidla musí někdo nejdřív sepsat, jinak se automatizací ztratí kvalita.

---

## Kontrola před odevzdáním

- Má každá bolest symptom **a** „co se děje", a jsou to dvě různé věty?
- Prošla všech šest otázek, a je u chybějících `CHYBÍ` nebo `TOHLE NEVÍM` místo domyšlené odpovědi?
- Je slabé místo jedno, určené kaskádou z kroku 3 (a ne prostě to, kde to nejvíc bolí)?
- Má slabé místo diagnózu ze seznamu A1–A12? U A12 je napsáno, že cesta k datům je celá?
- Prošly všechny tři otázky o AI, a je u „až po" jmenovaný předpoklad?
- Je typ zásahu z těch šesti (žádné vlastní kategorie)?
- Je označeno `oprava` nebo `obtok`, a u obtoku napsané, co zůstává nespravené?
- Má každé `TOHLE NEVÍM` svou otázku, adresovanou konkrétnímu člověku?
- Je „co se děje" napsané tak, že tomu rozumí i někdo, kdo o datech nic neví?
- U dávky: seskupeno podle diagnózy (ne oddělení), sečtený čas na skupinu, vypsaná odblokovávající rozhodnutí?
- Nepočítám tady návratnost ani dráhu (to je `freelo-triage-poptavky`)?
