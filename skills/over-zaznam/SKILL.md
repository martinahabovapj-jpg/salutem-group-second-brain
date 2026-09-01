---
name: over-zaznam
description: >
  Použij tento skill vždy, když se má ověřit obsah jednoho záznamu ve second
  brainu — tedy najít v něm tvrzení, která stojí jako fakt, ale nikdo je
  neověřil. Spouštěj ho, když uživatel řekne „ověř tenhle záznam", „projdi, co
  v tom je pravda", „audit záznamu", „nesedí mi to", nebo když se má na noc
  rozjet dávka agentů nad starými záznamy. Na rozdíl od skillu `zavri-otazku`,
  který řeší PŘIZNANOU neznalost (otázky v „Co zatím nevíme"), tenhle hledá
  NEPŘIZNANOU: věty, které znějí samozřejmě a nikdo za nimi nemá doklad.
  Jeden běh = jeden záznam, nejvýš osm tvrzení.
---

# Ověřovač záznamu

Zavírač otázek řeší **přiznanou** neznalost — otázku, u které všichni vědí, že
odpověď chybí. Tenhle skill hledá **nepřiznanou**: tvrzení, která v záznamu stojí
jako fakt, znějí samozřejmě a nikdo je nikdy neověřil.

> **Nebezpečná tvrzení nejsou ta s varováním. Jsou to ta bez něj.**
> Ke 13. 8. 2026 je v bázi 124 varování `⚠️` a jen 11 explicitních „neověřeno".
> Čtyři chyby nalezené toho dne byly všechny ve větách, které žádné varování
> neměly.

## 🔴 Do provozních systémů nemáš přístup. Je to záměr.

**Freelo, Make, Raynet ani tokeny v `settings.json` nečti** a nepokoušej se o to.
Provozní systémy nesou klientská a osobní data a ta se posílat nemají.

Pro ověřovače to má jeden konkrétní důsledek: **tvrzení o schopnostech živých
systémů nemůžeš ověřit.** Nedohaduj se — vydej k nim verdikt
*K OVĚŘENÍ V SYSTÉMU* s hotovým dotazem pro člověka.

## Zadání jednoho běhu

Dostaneš **cestu k jednomu záznamu**. Vybereš z něj **nejvýš osm nosných
tvrzení** a ke každému vydáš verdikt.

**Jeden záznam na jeden běh.** Bez toho se z auditu stane přepisování báze.

## Krok 1 — vyber nosná tvrzení. Ne ta nejzajímavější

Auditovat všech dvě stě vět v záznamu je k ničemu. **Cílem není stoprocentní
provenience, ale najít tvrzení, která by něco stála, kdyby byla špatně.**

### Test nosnosti — stačí jedna splněná podmínka

- je to **číslo**, které se objevuje v plánu, business casu nebo na AI Hubu
- je to tvrzení použité **jako důvod** („proto", „protože", „z toho plyne")
- říká, **co budeme nebo nebudeme stavět**
- kdyby bylo **nepravdivé, změní to rozhodnutí, které už padlo**

Když tvrzení nesplňuje ani jedno, **nech ho být**, i když u něj není zdroj. Není
chyba, že záznam něco tvrdí bez citace — chyba je, když se podle toho rozhoduje.

### Kde je hledat

Záznam si svá nosná tvrzení **označuje sám.** Nejvyšší výnos mají:

- věty v **tučném písmu** a v **blokových citacích**
- řádky v **tabulkách** (tam bývají čísla)
- odstavce uvedené slovy **„Nejdůležitější", „Klíčové", „Zásadní", „Nález"**
- sekce **„Co si z toho odnést"** — tam se z tvrzení dělají pravidla

### Pět typů, a v tomhle pořadí je ber

| # | Typ | Příklad z provozu | Čím se ověřuje |
|---|---|---|---|
| 1 | **Číslo** | „pool má 28 obchodníků", „zbývá 108 tis. operací" | dopočítat ze zdroje, nikdy nepřebírat |
| 2 | **Negativní existence** | „brand manuál neexistuje", „retence nikde stanovená není" | 🔴 **nejdražší typ** — vyvrátí ho jediný nález. Platí pro něj povinný postup níž |
| 3 | **Schopnost živého systému** | „Raynet umí založit koncept", „Make má modul" | **nemůžeš** → K OVĚŘENÍ V SYSTÉMU |
| 4 | **Přiřazení** | „vlastní to IT", „dodal to X", „rozhodl Y" | primární zdroj, kde to padlo |
| 5 | **Stav vydávaný za znalost** | „běží", „je nasazené", „používá se" | ⏳ patří do Freela, ne do báze |

## Krok 2 — pořadí zdrojů a co čím dokládáš

| # | Zdroj | Co dokládá |
|---|---|---|
| 1 | **Artefakt sám** — soubor existuje, obsahuje X, má datum | **skutečnost** |
| 2 | **Dokument s datem** | skutečnost **ke svému datu** |
| 3 | **Přepis hovoru** | **co kdo řekl**, ne jak to je |
| 4 | **AI výstup** (shrnutí, návrh) | jen **co model napsal** |
| 5 | Jiný záznam v bázi | **vodítko — nikdy doklad** |

### 🔴 Pojistka číslo jedna: shoda mezi záznamy není ověření

U auditu je tahle past **horší než u zavírače**, protože nalezená shoda vypadá
jako potvrzení. Není.

> Když totéž tvrdí tři záznamy, má to nejčastěji **jeden zdroj** — a ten se musí
> najít. „Brand manuál firma nemá" bylo zapsané konzistentně na třech místech
> a všude špatně; kompletní sada ležela v `IT Governance - Dokumenty\AI\brandguide`.
> Číslo „28 obchodníků" bylo taky na třech místech a vzniklo jednou.

**Když najdeš tvrzení potvrzené jen jinými záznamy, je to NEDOLOŽENO** —
a napiš, že se opakuje, protože to je samo o sobě nález.

### 🔴 Pojistka číslo dvě: rekurzivní hledání ti tiše zamlčí celé knihovny

**Doložený případ 13. 8. 2026:** agent hledal rekurzivně od kořene
`C:\Users\habova\P&J Capital s.r.o` a **celý strom `Salutem - Dokumenty` se ve
výsledcích neobjevil.** Cílené hledání přímo v té knihovně soubory našlo. Žádná
chyba se nevypsala — hledání prostě vrátilo méně, než existuje.

To je nejhorší možná porucha právě pro tenhle skill: **vyrábí falešná tvrzení
o neexistenci** — tedy přesně ten typ chyby, kvůli kterému vznikl.

Proto u **každého** tvrzení typu „X neexistuje" nebo „nikde není" platí:

1. projdi **každou knihovnu zvlášť**, jmenovitě — ne jedním rekurzivním záběrem;
   knihovny jsou `AI - Dokumenty`, `Salutem - Dokumenty`, `IT Governance -
   Dokumenty`, `SReal - Dokumenty`, `OneDrive - P&J Capital s.r.o`
2. do reportu vypiš, **které knihovny jsi opravdu prošel** a kterou ne
3. knihovnu, ke které se nedostaneš, uveď v řádku „Zdroje, které jsem NEMĚL"

**Nenapiš „hledal jsem v celé složce".** Napiš, ve kterých knihovnách — jinak
nikdo nepozná, jestli je negativní nález nález, nebo slepé místo nástroje.

#### 🔴 Timeout není slepé místo. Nepleť si to

Vyžádal si to agent, který na tom 14. 8. 2026 spálil 34 hledání místo dvaceti.

**Fulltext přes `Salutem - Dokumenty`, `IT Governance - Dokumenty` a `OneDrive`
spadne na 20s timeout.** Vypadá to úplně stejně jako „nic tam není" — a když si
to spleteš, vyrobíš falešné „neexistuje" v knihovně, která to hledané obsahuje.

Jmenovitý průchod velké knihovny se proto **musí dělat jinou technikou:**

1. **hledej podle jmen souborů**, ne podle obsahu (`Get-ChildItem -Recurse |
   Where-Object { $_.Name -like ... }` — ne `-Include`, ten tiše nefiltruje)
2. **`.docx` si nejdřív převeď** přes `skripty\docx2txt.py` a grepuj text
3. teprve pak fulltext, a to **po podsložkách**, ne přes celou knihovnu

Doložený výnos: takhle se ve druhém, jmenovitém průchodu `IT Governance` našel
`Interface ADOL.docx` — firemní analýza rozhraní, bez které by z celého tvrzení
vyšlo jen prázdné „nedoloženo".

**Konkrétní past, potvrzená dvakrát 13. 8. 2026:** `Get-ChildItem -Recurse
-Include` umí **tiše nefiltrovat** a vrátit méně, než existuje. Žádná chyba se
nevypíše. Když na výsledku něco stojí, **zopakuj hledání jinak** — např.
`-Recurse | Where-Object { $_.Name -like ... }`. V jednom běhu se tím našel
doklad, na kterém stál celý verdikt; bez druhého pokusu by vyšel opačný.

### 🔴 Pojistka číslo tři: knihovny se prohledávají u KAŽDÉHO tvrzení

Pojistka číslo dvě výš platila jen pro tvrzení typu „X neexistuje". **To je moc
úzké a 14. 8. 2026 se tím propadly dva nálezy ze tří.**

Ani jeden z nich nebyl formulovaný jako negativní existence — byly to nálezy
typu *„záznam staví argument na něčem, co doklad nemá"*. Agent knihovnu
`Salutem - Dokumenty` nehledal, protože pravidlo mu to nenařizovalo, a vydal
VYVRÁCENO. Druhý průchod v té knihovně našel **21 typových smluv s poli
`[DOPLNIT]`**, tedy přesně ten artefakt, který nález rušil. Navržená revize by
do báze vepsala novou chybu.

**Nové pravidlo: kdykoli hledáš doklad nebo protidoklad, projdi knihovny
jmenovitě** — ne jen u „neexistuje". Knihovny jsou `AI - Dokumenty`,
`Salutem - Dokumenty`, `IT Governance - Dokumenty`, `SReal - Dokumenty`,
`OneDrive - P&J Capital s.r.o`. Do reportu vypiš, které jsi opravdu prošel.

**A jedna konkrétní záměna, která se stala:** `03 SReal` **není** podsložka
`AI - Dokumenty`, ale `Salutem - Dokumenty`. Než napíšeš cestu do reportu,
ověř, ve které knihovně ten soubor leží.

### 🔴 Pojistka číslo čtyři: protidoklad musí pokrýt celý rozsah tvrzení

Druhý propad ze 14. 8. 2026. Tvrzení mluvilo o **„API katastru"** obecně; první
průchod prověřil **WSDP**, zjistil, že je celá placená, a vydal VYVRÁCENO.
Jenže ČÚZK má paralelně **bezúplatné REST API KN** (`api-kn.cuzk.gov.cz`,
v provozu od 1. 7. 2024), jehož podmínky doslova říkají *„Využívání API je
bezplatné"* a stanovují limit volání za časový úsek. Model „zdarma do limitu"
tedy existuje — revize by zapsala nepravdu.

Než vydáš VYVRÁCENO, odpověz si: **je protidoklad o celém tom, o čem je
tvrzení, nebo jen o jedné jeho části?** Když tvrzení mluví obecně a ty jsi
prověřil jednu konkrétní službu, produkt nebo variantu, **nemáš vyvrácení** —
máš NEDOLOŽENO k tomu číslu a DOLOŽITELNÉ upřesnění k tomu, co jsi našel.

### 🔴 Pojistka číslo pět: u přepisu ověř, komu ta věta patří

Automatické přepisy často **nemají označené mluvčí** a v hlavičce na to samy
varují. 14. 8. 2026 na tom padl nález: první průchod jeden řádek diskvalifikoval
jako repliku tazatelky, a jiný řádek — taky tazatelčin — citoval jako slova
dotazované právničky. Vynechal přitom řádky, kde dotazovaná říká opak toho, co
jí nález přisuzoval (*„kdybychom to měli, tak to by bylo supr"*).

Postup: **než připíšeš citát člověku, přečti si dvacet řádků kolem** a urči, kdo
mluví, z průběhu dialogu. Když to určit nejde, napiš to — přepis pak dokládá,
**že něco padlo**, ne kdo to řekl. A pozor na řádky, které začínají přitakáním
(*„Já to taky."*): to není odklon od tvrzení, ale souhlas s ním.

### 🔴 Pojistka číslo šest: grepni formulaci tvrzení, ne jeho citovaný zdroj

Nejjemnější past z celé dávky 14. 8. 2026, a stála o vlásek za zápisem nepravdy
do báze.

Záznam tvrdil, že *„jediným schváleným prostředím pro firemní data je Copilot"*,
a jmenoval u toho směrnici. První průchod směrnici přečetl, zjistil, že tam
Copilot je jen jako **příklad**, a vydal VYVRÁCENO. Udělal to i den předtím jiný
běh — **shodně, a oba se mýlili stejně.**

Ta věta totiž stojí **doslova** v jiném dokumentu: `06 Standardy a šablony\
📘 Strategický manuál Tone of Voice_ Salutem AI (v3.md`, §4. Chybná byla
**adresa**, ne tvrzení. Revize by přitom smazala doložený compliance rozpor.

> **Když je chybou atribuce, kontrola jmenovaného zdroje ji najít nemůže.**
> Grepuj **charakteristickou formulaci samotného tvrzení** napříč všemi
> knihovnami, ne jen zdroj, na který se záznam odvolává. Jedno takové hledání
> tenhle doklad našlo.

A pozor na to, co z toho plyne pro pojistku číslo jedna: **shoda dvou reportů
ověřovače taky není potvrzení.** Když oba prověřovaly jmenovaný zdroj, mají
stejnou slepotu — ne nezávislý souhlas.

### Rozdíl v definici není chyba v tvrzení

Třetí propad ze 14. 8. 2026, a je to jiný druh chyby než ty dva výš. Nález
tvrdil, že číslo v záznamu je špatně. Druhý průchod ho nezávisle přepočítal —
**sedělo do posledního čísla**. Rozdíl vznikl ve třech nepřiznaných volbách:
jak se zachází s „Nevím", jestli „polovina" znamená medián nebo podíl, a jestli
pásmo „pod tři hodiny" zahrnuje hranici.

**Když se výsledek rozejde kvůli definici, a ne kvůli součtu, není to
VYVRÁCENO — je to DOLOŽITELNÉ:** číslo platí, chybí u něj metodika. Vyvrácení
si nech na případ, kdy artefakt říká něco jiného.

A hledej **vlastní příčinu**: v tom případě to bylo tím, že jedna sekce
používala vedle sebe **tři různé jmenovatele (61, 64, 65)** a ani jeden
nepřiznávala. To je silnější nález než spor o jedno číslo.

### Časové značky souborů nejsou datum vzniku

`CreationTime` na Windows je u kopírovaného souboru **čas kopie** — umí být
i *pozdější* než `LastWriteTime`. Sada souborů s časem zápisu ve čtyřech
sekundách je stažená kopie, ne originál.

Když má tvrzení stát na tom, **odkdy něco existovalo**, `CreationTime` to
nedokládá. Doklad dává `LastWriteTime` **plus nezávislá druhá kopie jinde**,
nejlépe s totožným hashem (`Get-FileHash`). Doložený případ: nález se opřel
o `CreationTime` 12. 3. 2026 a měl pravdu, ale ze špatného důvodu — skutečný
doklad byl bit po bitu totožný soubor v jiné knihovně se zápisem 28. 8. 2024.

### Nedatovaný zdroj se dá často datovat zvnitřku

Nepiš „přepis bez data, nelze použít". Hledej v textu **den v týdnu, termín,
událost, jméno, které se objevilo jen v určitém období**. Doložený případ:
přepis s hlavičkou „Invalid Date" se datoval na 14.–16. 1. 2026 podle zmínky
„do pátku 16." a podle onboardingu — a tím se rozhodlo mezi VYVRÁCENO
a ZASTARALÉ.

### Umíš čist .docx, neumíš .pdf

Přepisy jsou `.docx` a ty se čtou přes `skripty\docx2txt.py`. **PDF přečíst
neumíš** (chybí poppler), takže část archivu je pro tebe nedostupná. Když nosné
tvrzení stojí na PDF, není to NEDOLOŽENO — je to řádek do „Zdroje, které jsem
NEMĚL" s cestou k tomu souboru.

### Kontrola hlavičky: sirotčí tvrzení

Levná kontrola s dobrým výnosem. Hlavička záznamu má pole `zdroj:` a to je
**kontrakt**: záznam říká, z čeho vznikl.

**Když tvrzení nemůže pocházet ani z jednoho uvedeného zdroje**, někdo ho dopsal
později a zdroj nedoplnil. Nahlas to — i když se tvrzení nakonec potvrdí.

### Kontrola data u každého tvrzení

**Pravdivé tvrzení může být prošlé.** „Cowork je dostupný" byla v červnu pravda.
U každého tvrzení se ptej nejen *je to pravda*, ale *je to pravda dnes*.

### Nedotažená oprava — nejvýnosnější místo v celém záznamu

Když v záznamu **najdeš datovanou revizi nebo přeškrtnutý text**, nepřeskoč to
jako „tohle už je vyřešené". Naopak: **je to nejpravděpodobnější místo, kde je
chyba pořád.** Opravit se totiž musí dvě věci a obvykle se opraví jen jedna:

1. samotné tvrzení
2. **důsledek, který z něj plynul** — doporučení, návrh, číslo v business casu

**Doložený případ 13. 8. 2026:** tvrzení „brand manuál firma nemá" bylo opravené
téhož dne, ale věta o tom, že *„pokaždé, když má cokoli držet brand, začíná to
ručním dolováním barev pipetou"*, zůstala stát — přitom vektorová loga nesou
přesné kódy (`#25db7a`). Oprava tvrzení, doporučení dál špatné.

Postup: u každé revize dohledej, **co ze původního tvrzení plynulo**, a ověř to
zvlášť. A **kontroluj i data v revizích samotných** — ve stejném záznamu byla
v opravě věta „o dva dny později (19. 6.)", přičemž 19. 6. je čtyři dny **před**
uvedeným 23. 6. Text, který někdo psal ve spěchu jako opravu, prochází kontrolou
nejmíň.

## Krok 3 — verdikty

| Verdikt | Kdy | Co z toho plyne |
|---|---|---|
| **DOLOŽENO** | záznam sám nese citaci nebo cestu | nic — jen se **spočítá**, do reportu se nevypisuje |
| **DOLOŽITELNÉ** | citace chybí, ale zdroj jsi našel teď | navrhni doplnit citaci |
| **NEDOLOŽENO** | zdroj se nenašel a tvrzení je nosné | označit; napiš, kde jsi hledal |
| 🔴 **VYVRÁCENO** | našel jsi zdroj, který říká něco jiného | **datovaná revize** — původní text se nepřepisuje |
| ⏳ **ZASTARALÉ** | bylo pravdivé, když se to psalo, dnes už ne | datovaná revize s datem, odkdy neplatí |
| **K OVĚŘENÍ V SYSTÉMU** | tvrzení o schopnosti nebo stavu živého systému | hotový dotaz pro člověka |

**Rozdíl mezi VYVRÁCENO a ZASTARALÉ je podstatný**, protože oprava vypadá jinak:
u vyvráceného se tvrzení opravuje, u zastaralého se **připisuje revize s datem**
a původní tvrzení zůstává jako historie.

### Kalibrace — pojistka proti vyrábění nálezů

**Do reportu napiš, kolik tvrzení jsi prověřil a kolik z nich bylo v pořádku.**

Agent, který má hledat problémy, je najde. **Report, kde je 8 z 8 tvrzení
nálezem, je podezřelý** — a stejně tak report, kde není nic. Když ti vyjde
všechno jako nález, vrať se a zkontroluj, jestli neaplikuješ přísnější kritérium,
než říká test nosnosti.

## Krok 4 — co nikdy neděláš s obsahem

🔴 **Nepřepisuješ argument. Připojuješ doklad.**

Nejjemnější škoda, kterou audit umí udělat, je **zploštění rozlišení**, které
někoho stálo práci. Doložený případ z 13. 8. 2026: tvrzení „tabulka pro právní se
nepoužívá" se ukázalo jako **dvě tvrzení** — formulář na obsah smlouvy se
používá a je verzovaný, evidence úkolů se nepoužívá. **Správný výstup bylo
rozdělení, ne oprava ani smazání.**

Proto: když tvrzení míchá dvě věci, **rozděl ho a vydej dva verdikty.**

A dál platí totéž co u zavírače:

- **do záznamů v `01`–`08` nezapisuješ** — report s navrženou revizí
- **na jiné záznamy nesaháš**, i když v nich vidíš tentýž problém; nahlásíš je
  s vlastníkem a akcí

## Krok 5 — výstup

Ulož jako **vlastní soubor**:

```
99 Archiv zdrojů\_overovani-zaznamu\<RRRR-MM-DD>\<slug-zaznamu>.md
```

Formát:

```markdown
# Ověření: 05 Nástroje a systémy/co-jsme-vyzkouseli.md
**Datum:** 14. 8. 2026 · **Prověřeno tvrzení:** 8 · **V pořádku:** 4 · **Nálezů:** 4
**Zdroje, které jsem NEMĚL:** Freelo, Make, Raynet (provozní systémy — záměr)

## 🔴 VYVRÁCENO — „brand manuál firma nemá"
**Kde:** sekce „Nález, který u toho vyplaval", ř. 542
**Nosné proto, že:** z toho tvrzení plyne doporučení dolovat barvy pipetou
**Protidoklad:** `IT Governance - Dokumenty\AI\brandguide\Salutem Real - logo manuál.pdf`
(12. 3. 2026) + sady log pro tři značky + font Sora
**Navrhovaná revize (původní text nepřepisovat):**
> 🔴 **OPRAVENO 14. 8. 2026: brand manuály existují.** Platí z toho jen to, že
> o nich nikdo nevěděl. Sada je v `IT Governance\AI\brandguide`.

## ⏳ ZASTARALÉ — „Cowork je dostupný"
**Kde:** ř. 200 · **Platilo do:** 21. 7. 2026, kdy se vypnul kvůli ceně
**Navrhovaná revize:** doplnit datum platnosti, text nechat

## NEDOLOŽENO — „odhad 4–6 volání na jeden call"
**Nosné proto, že:** stojí na tom rozpočet kreditů a rozhodnutí o rolloutu
**Kde jsem hledal:** blueprinty v mapě Make, popis use casu, přepisy 6.–11. 8.
**Poznámka:** tvrzení se opakuje ve dvou záznamech, ale zdroj má jen jeden
(= není to potvrzení)

## K OVĚŘENÍ V SYSTÉMU — „Make AI modul stojí víc kreditů než běžný"
**Dotaz pro člověka:** Make → Usage → porovnat spotřebu scénáře s AI modulem
proti běžnému za stejný počet běhů

## Nálezy pro jiné záznamy
- `02 Use casy/ecomail-nastaveni.md` — tvrdí totéž o brand manuálu. **Rozpor**,
  ne vodítko. Akce: převzít stejnou revizi. Nesahal jsem tam.

**Kolik to stálo:** 12 hledání
```

Řádek **„Zdroje, které jsem NEMĚL" je povinný.** Bez něj se nepozná, jestli
verdikty vznikly z plného obrazu.

## Druhý průchod — jen na VYVRÁCENO

**Každé VYVRÁCENO ověřuje druhý agent.** Je to nejrizikovější výstup tohoto
skillu: tvrdí, že existující záznam je špatně, a spouští tím editaci.

Druhý agent má jediný úkol: **pokusit se ten protidoklad zneplatnit.** Ptá se:

1. Mluví protidoklad skutečně o tomtéž, nebo jen o něčem podobném?
2. **Pokrývá protidoklad celý rozsah tvrzení**, nebo jen jednu jeho část? (WSDP
   není „API katastru"; jedna služba není celá platforma.)
3. Je protidoklad artefakt, nebo přepis / jiný záznam / AI výstup? U přepisu:
   **má označené mluvčí?**
4. **Prošel první průchod všechny knihovny jmenovitě?** Když ne, dohledej to sám —
   14. 8. 2026 tudy padly dva nálezy ze tří.
5. Není původní tvrzení pravdivé **ke svému datu** — tedy ZASTARALÉ, ne VYVRÁCENO?
6. **U čísel: přepočítej to nezávisle, než se podíváš na jeho výpočet.** Když
   sedí a rozdíl je v definici, je to DOLOŽITELNÉ, ne VYVRÁCENO.
7. **Dá se navržená oprava provést doslova, aniž by poškodila správný text?**
   Je u ní citace původního znění?

Pětka je nejčastější záměna a plete se nejvíc. **Čtyřka je nejčastější příčina
propadu** — a je to porucha nástroje, ne úsudku, takže ji nepozná nikdo, kdo se
na ni nezaměří.

> **Druhý průchod neověřuje, jestli je nález pravdivý.** Ověřuje, jestli
> **verdikt, odůvodnění a navržená oprava** odpovídají tomu, co se doložilo.
>
> Doložený případ 13. 8. 2026: nález „datum 19. 6. je špatně" byl věcně správný,
> ale druhý průchod shodil jeho odůvodnění (na tom datu nestál žádný argument,
> takže to nebylo VYVRÁCENO, ale oprava pěti slov), zablokoval navrženou revizi
> (*„přeformulovat nadpis"* u řádku, kde nadpis není — provedení doslova by
> přepsalo správný nadpis na chybný) a našel citaci vydávanou za doslovnou
> z textu, která byla z názvu souboru. **Pravdivý nález v příliš silném verdiktu
> je pořád škoda.**

## Do `_bilance.md` nezapisuj

Bilance se vede v `99 Archiv zdrojů\_overovani-zaznamu\_bilance.md` — ale
**zapisuje do ní ten, kdo tě spustil, ne ty.** Běhů jde na jeden záznam víc
paralelně a společný soubor si navzájem přepíšou.

Doložený případ 13. 8. 2026: ze tří paralelních běhů zapsal do bilance jeden,
druhý si problém uvědomil a řádek nechal ve svém reportu, třetí ho nechal taky.
Výsledek: bilance ukazovala jeden ověřený záznam ze tří.

**Ty místo toho dej na konec svého reportu hotový řádek k překopírování:**

```
| 13. 8. 2026 | `05 Nástroje a systémy/roztristenost-uloziste.md` | 8 / 3 / 5 | — | nespouštěn |
```

## Best practice

- **Začni čísly.** Jsou falzifikovatelná a chyba v nich je nejdražší.
- **U „neexistuje" se aktivně snaž najít protipříklad**, ne potvrzení. Tři měsíce
  dolování barev pipetou vznikly z jednoho nevyvráceného „nemáme".
- **Chyba, která nemá vysvětlení, je nález, ne překážka.** `Duplicate key error`
  odhalil, že tabulka obchodníků má 14 lidí, ne 28.
- **Nevěř polím, která vypadají autoritativně.** `license.operations` v Make API
  hlásilo hodnotu, ze které vyšel trojnásobně nadsazený rozpočet; autoritativní
  byla obrazovka Usage.
- **Když je zdroj AI výstup, označ celý řetěz.** A pozor: i lidsky vypadající
  dokument může být AI koncept — provenience má víc než jeden krok.
- **„Systém to umí" a „u nás je to nastavené" jsou dvě různá tvrzení.**
- **Jedno tvrzení bývají dvě.** Když se dá rozdělit, rozděl ho.
- **Cituj krátce a přesně.** Jedna věta ze zdroje je silnější než odstavec
  parafráze.
- **Pozor na termín, který nikdo nikdy neřekl.** Slovo, které se v bázi tváří
  jako firemní pojem, ale v žádném přepisu není a v AI výstupech má **různé
  autory**, bývá zkomolenina z jednoho hovoru. Doložený případ: „Paspil" bylo
  „paskvil", jedno slovo jednoho člověka o IT infrastruktuře — a v bázi z toho
  byl termín, název záznamu a název projektu za milion. Signál je právě ta
  **rozcházející se atribuce**: kdyby to byl pojem, autor by byl jeden.
- **Počítej s tím, že jsi drahý.** Reálná spotřeba prvních tří běhů byla
  **22, 20 a 32 hledání** (zavírač měl 8–14). Rozpočet je měkký, ale když
  překročíš 30, dopiš do reportu, **na čem se to protočilo** — ať se pozná,
  jestli to byl záznam, nebo nástroj.

## Co nikdy nedělat

- **Nečti tokeny ani provozní systémy.**
- **Neber shodu mezi záznamy jako ověření.**
- **Nepřepisuj argument** ani nemazej rozlišení, které v záznamu je.
- **Nezapisuj do záznamů v `01`–`08`.**
- **Nesahej na jiný záznam**, i když v něm vidíš tentýž problém.
- **Neoznačuj za NEDOLOŽENO tvrzení, které neprojde testem nosnosti** — to je
  šum, ve kterém se utopí skutečné nálezy.
- **Nevydávej VYVRÁCENO bez artefaktu.** Přepis proti přepisu není vyvrácení,
  je to rozpor mezi tvrzeními a hlásí se jako NEDOLOŽENO.
- **Nedělej víc než jeden záznam a osm tvrzení** na běh.
- **Nezapisuj do `_bilance.md`** — ten soubor patří tomu, kdo tě spustil.
- **Nenavrhuj editaci bez citace textu, kterého se týká.** „Přeformulovat
  nadpis", „změnit tu větu", „upravit odstavec" se nedá provést, aniž by to
  někdo uhádl — a když to uhádne špatně, poškodí správný text. Vždy uveď
  **původní znění** a **nové znění**.
- **Netvrď „neexistuje" po jednom rekurzivním hledání.** Knihovny jmenovitě,
  jinak je to slepé místo nástroje vydávané za nález. A **platí to u každého
  tvrzení**, ne jen u těch, která jsou formulovaná negativně.
- **Nevydávej VYVRÁCENO, když jsi prověřil jen část toho, o čem tvrzení mluví.**
- **Nepřipisuj citát člověku z přepisu, který nemá označené mluvčí**, dokud ho
  neurčíš z průběhu dialogu.
- **Nevydávej VYVRÁCENO, když ti číslo sedí a rozchází se jen definice.**

## Proč to vzniklo

13. 8. 2026 se při běžné práci našly čtyři chyby v bázi — a všechny byly
v tvrzeních, která zněla samozřejmě a neměla u sebe varování:

| Tvrzení v bázi | Skutečnost |
|---|---|
| „brand manuál firma nemá" | existoval tři měsíce v `IT Governance\AI\brandguide` |
| „pool má 28 obchodníků" | má 14; každý je v něm dvakrát |
| „zbývá ~108 tis. operací v Make" | zbývalo 37 tis. — chyba vznikla z jednoho pole v API |
| „existující tabulka pro právní se nepoužívá" | formulář se používá a je verzovaný; nepoužívá se evidence úkolů |

Žádná z nich nebyla nová informace. Všechny byly dohledatelné — jen se nikdo
neptal, čím je to tvrzení doložené.

**Ověřovač je proto dražší než zavírač a zároveň cennější:** zavírač doplňuje,
co nevíme. Ověřovač hledá, o čem si myslíme, že to víme.
