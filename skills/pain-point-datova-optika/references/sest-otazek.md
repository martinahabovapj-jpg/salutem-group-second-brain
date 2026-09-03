# Šest otázek podrobně

Ke každé otázce najdeš: co se tím vlastně ptáme, jak se tomu říká v oboru (kdybys potřebovala hledat literaturu nebo mluvit s IT), co se typicky pokazí a co se doptat.

Krátké jméno za pomlčkou v nadpisu používej, když na to místo odkazuješ (například „slabé místo: domov informace"). Otázku používej, když se ptáš.

Celý model se čte dvěma směry:

- **Když něco navrhujeme:** chci se o něčem rozhodovat → potřebuju k tomu číslo → to číslo musí vzniknout v nějakém kroku práce → ten krok musí běžet v nějakém systému → tam vznikne konkrétní údaj → a někde musí být zapsané, co ten údaj znamená.
- **Když něco ověřujeme:** číslo je divné → jdu zpátky, ze kterého systému je → který krok práce ho vyrobil → kdo ho tam zadává → a kdo za to odpovídá.

---

## 1. KDO ROZHODUJE — odpovědnost

**Ptáme se:** Kdo má právo říct, co je v téhle věci pravda? Kdo rozhoduje, co daný údaj znamená, kdo ho smí vidět a jak přesný má být?

**Odborně:** *data owner* je ten, kdo o datech rozhoduje a nese odpovědnost (je to člověk z byznysu, ne z IT). *Data steward* je ten, kdo se o ně denně stará: hlídá definice, řeší duplicity a výjimky. *Data custodian* je IT, které je technicky provozuje — a **neurčuje, co znamenají**. *Process owner* je vlastník postupu, což není totéž jako vlastník dat.

**Co se typicky pokazí:** Vlastník neexistuje a IT ho nahrazuje, takže o obchodních definicích rozhoduje ten, kdo na to nemá mandát ani znalost. Druhá varianta: vlastník, správce i vykonavatel je jeden člověk bez zástupu — pak riziko není v čase, ale v tom, že ta osoba onemocní.

**Doptej se:**
- Kdo má právo rozhodnout, co je v téhle věci pravda?
- Kdo to dnes reálně dělá — a je to tentýž člověk?
- Kdo tu agendu převezme, když ten člověk týden chybí?
- Kdo dnes rozhoduje o tom, kdo se k těm datům dostane?

---

## 2. CO TÍM TRPÍ — k čemu to je

**Ptáme se:** Které konkrétní rozhodnutí nebo které číslo je kvůli téhle bolesti špatné, chybějící nebo pozdě? A co se stane, když je špatné?

**Odborně:** metriky se dělí na *input* (kolik jsme toho nasypali dovnitř), *output* (co vypadlo), *outcome* (co se změnilo v chování) a *business impact* (peníze). Každé číslo, o které se firma opírá, potřebuje jednu závaznou definici — ta se zapisuje do *business glossary*, tedy podnikového slovníku pojmů.

**Co se typicky pokazí:** Číslo nemá jednu definici, takže každé oddělení spočítá jiné a porada se pak baví o tom, čí tabulka má pravdu, místo o rozhodnutí. Druhá varianta: číslo nemá zdroj, tedy měříme něco, co v žádném systému nevzniká — pak je jeho výroba navždy ruční.

**Doptej se:**
- Které rozhodnutí tímhle trpí? Co se stane, když je informace špatná nebo přijde pozdě?
- Existuje pro to číslo jedna závazná definice, a kdo ji vlastní?
- Spočítali by dva lidé nezávisle to samé?
- Kdyby se to přestalo dělat, kdo by to jako první poznal? (Když nikdo, dělá se to ze zvyku.)

---

## 3. KDE TO VZNIKÁ — vznik informace

**Ptáme se:** V jakém okamžiku ta informace poprvé existuje, kdo ji zadává, a zůstane po tom okamžiku záznam?

**Odborně:** *kvalita na vstupu* (data quality at the point of capture) znamená, že kvalitu dat nelze vyrobit dodatečně čištěním — dá se vyrobit jen při zadávání. Proto kontroly patří na vstup, ne do reportu na konci. *Událost* (event) je krok práce, po kterém zůstane záznam s datem a časem; bez událostí nelze spočítat, jak dlouho co trvá, tedy většinu provozních čísel. *Lidský most* je člověk, který ručně přenáší data mezi dvěma systémy, protože nejsou propojené.

**Co se typicky pokazí:** Práce se udělá, ale nikde po ní nezůstane záznam, takže se čísla dopočítávají v Excelu. Nebo se úplnost kontroluje až u příjemce, který dostává nekompletní zadání a nemá mandát to změnit.

**Doptej se:**
- Kdy a kde přesně ta informace vzniká, a kdo ji zadává?
- Zůstane po tom záznam s datem, nebo to ví jen člověk?
- Kontroluje se úplnost v momentě zadání, nebo až u toho, kdo to přebírá?
- Kolik ručních přenosů je na té cestě?
- Běží ten postup pořád, nebo se po nějaké personální změně přestal dělat?

---

## 4. KDE TO BYDLÍ — domov informace

**Ptáme se:** Ve kterém systému je ta informace uložená tak, že se tomu dá věřit? A kolik dalších míst ji drží taky?

**Odborně:** *system of record* je pro každou věc právě jeden autoritativní systém; ostatní mají jen kopii, ne pravdu. *Master data management* je správa základních údajů (o nemovitostech, klientech, jednotkách) napříč systémy. Přenos dat může být *okamžitý* (změna se hned pošle dál) nebo *dávkový* (jednou denně se pošle vše). *Shadow IT* jsou evidence a nástroje, které vznikají mimo řízenou architekturu, protože oficiální cesta je pomalá. *Životní cyklus dat* znamená, že aktivní data a archiv patří na jinak drahou infrastrukturu.

**Co se typicky pokazí:** Dva systémy jsou oba „ten hlavní" pro tu samou věc. To se nedá vyřešit technicky, jen dohodou — a dokud nepadne, lidé si zakládají vlastní tabulky, čímž se problém prohloubí. Zásadní je, že **propojení systémů nelze zadat, dokud není řečeno, který z nich je autoritativní.**

**Doptej se:**
- Který systém je pro tuhle věc autoritativní, a kdo to takhle rozhodl?
- Kolik dalších míst tu samou informaci drží?
- Jak se data mezi systémy dostávají: automaticky, dávkou, nebo člověkem?
- Je potřeba mít to hned, nebo stačí jednou denně?
- Vzniklo to mimo oficiální systémy? Pokud ano, **co bylo na oficiální cestě nepohodlné?** (Bez téhle odpovědi se tabulky vrátí.)
- Jsou to aktivní data, nebo archiv, který leží na drahém místě?

---

## 5. O CO VLASTNĚ JDE — rozpoznání věci

**Ptáme se:** O jakou věc se jedná, a dá se poznat, že ve dvou systémech jde o tu samou?

**Odborně:** *základní údaje* (master data) jsou věci, které se mění málo a používají se všude: nemovitost, klient, jednotka, dodavatel. *Transakční data* vznikají průběžně: platba, smlouva, ticket. *Referenční data* jsou číselníky, sazby a stavy. Nejdražší problém základních údajů je *identita*: bez společného jednoznačného čísla nelze data napříč systémy spojit vůbec — a žádná AI to neobejde.

**Co se typicky pokazí:** Tatáž nemovitost existuje v pěti systémech pod pěti různými označeními a lidé ji párují podle adresy. Nebo se něco ukládá na dvě místa z historických důvodů a není řečeno, které platí.

**Doptej se:**
- O jakou věc vlastně jde, a je to údaj základní, transakční, nebo číselník?
- Existuje pro ni jednoznačné číslo, které mají oba systémy?
- Podle čeho se to dnes páruje, když to číslo chybí?
- Ukládá se to duplicitně, a je řečeno, které místo platí?
- Je to strukturovaný záznam, nebo obsah dokumentu, ze kterého se to musí vytěžit? (To rozhoduje, jestli je to práce pro propojení, nebo pro AI.)

---

## 6. JE TO ZAPSANÉ — zápis pravidel

**Ptáme se:** Existuje pravidlo, definice a informace o citlivosti někde jinde než v hlavě člověka nebo v barvě buňky? A víme, odkud kam data tečou?

**Odborně:** tomuhle všemu se říká *metadata*, tedy informace o datech. Má pět druhů:

| Druh | Co obsahuje |
| --- | --- |
| významová | definice pojmu, kdo ji vlastní, pravidla výpočtu |
| technická | tabulky, pole, typy, propojení |
| provozní | kdy se to naposledy načetlo, kolik řádků, kolik chyb |
| cesta dat (lineage) | odkud kam data tečou |
| citlivost | osobní údaje, jak dlouho se to smí držet, kdo se k tomu dostane |

Dál: *podnikový slovník* (business glossary) je závazný seznam pojmů a jejich významů. *Katalog dat* je seznam datových aktiv s jejich vlastníky. *Metadatový dluh* nastane, když tyhle informace existují jen v nastavení u dodavatele nebo v hlavě jednoho člověka — pak je každá nová otázka od byznysu externí projekt, ne dotaz.

**Co se typicky pokazí:** Význam je zapsaný ve vizuálu (barva buňky nese informaci), v manuálu nebo v hlavě. Z ničeho z toho se nedá reportovat a nedá se to zautomatizovat, protože pravidlo není ve tvaru, který systém přečte. Druhá varianta: citlivost dat se posuzuje případ od případu dohadem, protože chybí závazné pravidlo.

**Doptej se:**
- Je to pravidlo zapsané někde mimo hlavu člověka a mimo formátování tabulky?
- Víme, odkud kam ta data tečou a kdo tu cestu umí změnit?
- Jsou tam osobní nebo citlivé údaje, a podle čeho se to určilo?
- Kdo pozná, že se přenos nepovedl, a za jak dlouho?
- Kdyby ten člověk zítra odešel, co přesně přestane být dohledatelné?

---

## Jak z odpovědí složit rozbor

1. Vypiš místa, kde byla odpověď `CHYBÍ`.
2. Projdi kaskádu z kroku 3 v SKILL.md odshora a zastav se u prvního bodu, který platí. To je slabé místo.
3. Slabému místu stanov diagnózu z `archetypy.md` a přelož ji na typ zásahu.
4. Ostatní chybějící místa popiš jako důsledky — jsou to argumenty pro naléhavost, ne samostatné úkoly.
