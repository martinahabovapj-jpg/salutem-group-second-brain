# Dvanáct diagnóz (A1 až A12)

Do těchhle dvanácti diagnóz spadne skoro každá bolest. Stanov **jednu jako hlavní**; ostatní můžou být uvedené jako důsledky. Kódy neměň — právě ony dělají bolesti sčítatelnými napříč odděleními.

Rychlá orientace:
- **A1, A2** — chybí rozhodnutí nebo chybí zdroj informací
- **A3, A4, A5** — data se nedají spojit, nekontrolují se, nebo pravidla nejsou zapsaná
- **A6, A7, A8, A9** — postupy a systémy nejsou propojené
- **A10, A11** — chybí dohoda o odpovědnosti a citlivosti
- **A12** — všechno drží a je to opravdu práce pro AI

---

## A1 — Měříme něco, co nikde nevzniká

**Slabé místo:** vznik informace · **Zásah:** změnit postup (začít to zapisovat), pak zapsat pravidla

**Poznáš to podle:** „nejaktuálnější to vím z telefonu", „skládám to z mailů", „to nikde není, to mám v hlavě". Pravidelný report, který nemá zdrojový systém.

**Proč to bolí:** Ta práce je navždy ruční a to číslo se nedá ověřit. Nespraví to žádný nástroj — musí začít vznikat záznam.

**Příklad:** Finanční reporting skládaný z telefonátů s bankéři a z mailů, dvě hodiny týdně. Kvartální tabulka pro banky, kde se stav úvěrů ručně přepisuje mezi tabulkami, tři až čtyři hodiny na jednu.

---

## A2 — Není dohodnuté, kde je pravda

**Slabé místo:** domov informace · **Zásah:** rozhodnout o systémech a propojit je (nejdřív rozhodnout, teprve pak propojovat)

**Poznáš to podle:** „to máme na dvou místech", „záleží, komu věříš", „radši si to vedu po svém". Spory o to, čí číslo platí.

**Proč to bolí:** Nedá se to vyřešit technicky, jen rozhodnutím. Dokud nepadne, každé další propojení i každá AI jen rychleji rozšíří nejistotu. **Tohle je nejčastější skrytá příčina — bolest se projeví jako ruční přepisování (A7), ale opravovat se musí tady.**

**Příklad:** Dva systémy pro správu nemovitostí, kde u téže nemovitosti není řečeno, který je hlavní. Obchodní případ vedený zároveň v CRM, v podnikové aplikaci, ve sdílené tabulce a na SharePointu.

---

## A3 — Nejde poznat, že jde o tu samou věc

**Slabé místo:** rozpoznání věci · **Zásah:** uklidit data (doplnit společná čísla), pak propojit

**Poznáš to podle:** párování podle adresy nebo podle jména, „to musím dohledat", ruční kontrola, jestli jde opravdu o tentýž objekt.

**Proč to bolí:** Bez společného čísla se data napříč systémy nespojí vůbec. Je to předpoklad všeho ostatního, nikoli poslední fáze projektu — což je chyba, kterou dělá skoro každý integrační plán.

**Příklad:** Tatáž nemovitost ve dvou systémech, v CRM a v tabulkách, bez společného identifikátoru. Tentýž list vlastnictví existující zvlášť jako záznam v CRM a zvlášť jako soubor na SharePointu.

---

## A4 — Chyby se nechytají tam, kde vznikají

**Slabé místo:** vznik informace · **Zásah:** změnit postup (povinná pole, kontrola při zadání, definice hotového zadání)

**Poznáš to podle:** „dostávám to nekompletní", „musím to po nich dodělávat", vracení práce, chybějící přílohy.

**Proč to bolí:** Náklad se přesune na příjemce, který nemá mandát to změnit. Řešení není schopnější příjemce, ale kontrola v momentě zadání.

**Příklad:** Právní oddělení dostávající nekompletní a chybná zadání od obchodníků. Podklady od účtárny, ve kterých chybí klienti, a odhalí to až kontrola dalšího člověka.

---

## A5 — Pravidlo má jen jeden člověk v hlavě

**Slabé místo:** zápis pravidel · **Zásah:** zapsat pravidla a významy, dohodnout, kdo o nich rozhoduje

**Poznáš to podle:** „to ví jen on", „má to svoje pravidla", význam nesený barvou nebo formátováním, manuál k tabulce, nastavení, které umí změnit jen externí dodavatel.

**Proč to bolí:** Firma umí data používat jen tak dlouho, dokud jsou ti lidé přítomní. A blokuje to jakoukoli automatizaci, protože pravidlo není zapsané ve tvaru, který systém přečte.

**Příklad:** Kolega po sedmnácti letech ve firmě jako „živá databáze". Tabulka s manuálem barev a formátování. Mapování polí do reportovacího nástroje, které umí změnit jen dodavatel na základě zadání.

---

## A6 — Důležitý okamžik se nikde nezapíše

**Slabé místo:** vznik informace · **Zásah:** změnit postup a upravit systém tak, aby po tom okamžiku zůstal záznam s datem

**Poznáš to podle:** klíčový moment existuje jen jako ranní rutina člověka; nikde není datum a čas; nelze spočítat, jak dlouho co trvalo ani jak velké je zpoždění.

**Rozdíl proti A1:** A1 je o chybějícím čísle do reportu. A6 je o chybějícím okamžiku v procesu, na který má někdo reagovat.

**Proč to bolí:** Bez záznamu okamžiku nelze měřit průběh procesu ani na cokoli automaticky reagovat. Často jde přitom o moment s velkou hodnotou pro peněžní tok.

**Příklad:** Denní ruční hlídání vkladů v katastru, kde okamžik zápisu nikde nevzniká jako záznam s časem. Postup, který se po personální změně přestal dělat, takže data z toho období prostě nejsou.

---

## A7 — Člověk je propojka mezi dvěma systémy

**Slabé místo:** domov informace · **Zásah:** rozhodnout o systémech a propojit je — **a ne AI**

**Poznáš to podle:** „exportuju to a nahraju tam", „přepisuju to z jedné tabulky do druhé", kopírování mezi dvěma systémy, přičemž na obou stranách jsou hotové strukturované údaje.

**Proč to bolí:** Je to nejlevnější opravitelná věc a zároveň ta, na kterou se nejčastěji chybně navrhuje AI. Přenos hotových údajů je práce pro propojení systémů.

**Než to označíš jako A7, zkontroluj A2:** pokud není dohodnuto, který systém je hlavní, je propojka jen důsledek a příčina je A2.

**Příklad:** Ruční přepisování plateb z účtárny do klientské aplikace. Zakládání téže nemovitosti zvlášť ve dvou systémech po akvizici.

---

## A8 — Lidé si vedou vlastní tabulky mimo systémy

**Slabé místo:** domov informace · **Zásah:** rozhodnout o systémech a dohodnout, kdo o tom rozhoduje — a hlavně odstranit důvod, proč tabulky vznikají

**Poznáš to podle:** vlastní tabulky, „takhle je to nejrychlejší", desítky nových evidencí za pár měsíců, sdílení odkazem místo přes oprávnění.

**Proč to bolí:** Roste to rychleji, než se to uklízí. Zakazování nefunguje: dokud je oficiální cesta pomalá, tabulky se vrátí. Proto rozbor musí obsahovat, **co bylo na oficiální cestě nepohodlné.**

**Příklad:** Přes sto sdílených tabulek, z toho několik desítek nových během tří měsíců, co je někdo sbíral — s poctivým vysvětlením, že je to důležité a v tabulce se pracuje rychle.

---

## A9 — Živá data a archiv leží na jedné hromadě

**Slabé místo:** domov informace · **Zásah:** rozhodnout o systémech (oddělit aktivní data od archivu), zapsat pravidla o tom, jak dlouho se co drží

**Poznáš to podle:** narážení na limity a cenu úložiště, ukládání do starého i nového místa, archiv na drahé aktivní infrastruktuře.

**Proč to bolí:** Platí se aktivní cena za mrtvá data a přehled se rozpadá historickými kopiemi, u kterých nikdo neví, která platí.

**Příklad:** Firemní úložiště plněné jako archiv, přičemž je určené pro aktivní data, a naráží se na limity licencí. Ukládání do starého i nového úložiště z historických důvodů.

---

## A10 — Nikdo neřekl, jak citlivá ta data jsou

**Slabé místo:** zápis pravidel · **Zásah:** zapsat pravidla (jednotné posuzování citlivosti), dohodnout, kdo schvaluje přístupy

**Poznáš to podle:** citlivost se posuzuje dohadem („asi tam nic není"), sdílení odkazem, osobní údaje v tabulkách bez označení, prázdné kolonky pro citlivost v evidenci.

**Proč to bolí:** Bez jednotného posuzování se u každého nového nápadu řeší compliance od nuly a odpověď záleží na tom, koho se zeptáš.

**Příklad:** Citlivost dat určovaná ad hoc během rozhovoru. Evidenční kolonky pro citlivost a vlastníka, které jsou navržené, ale prázdné.

---

## A11 — Celá agenda visí na jednom člověku

**Slabé místo:** odpovědnost · **Zásah:** dohodnout, kdo rozhoduje (vlastník, správce, zástup)

**Poznáš to podle:** jeden člověk drží celou agendu, urguje a dotahuje; zástup neexistuje; vykonavatel, správce i ten, kdo rozhoduje, je tatáž osoba. Ostatní na něj čekají, aby mohli začít.

**Proč to bolí:** Riziko není v čase, ale v přerušení. A bez vlastníka nelze uzavřít žádnou definici, takže tahle diagnóza blokuje A1 i A5.

**Příklad:** Jediný vlastník obchodního procesu držící evidenci, urgence a inventuru bez zástupu; účtárna čeká na jeho potvrzení, aby mohla vyplatit. Jeden člověk v roli komunikace s dodavateli, řízení vývoje i podpory.

---

## A12 — Práce, kterou opravdu má dělat AI

**Slabé místo:** žádné, cesta k datům je celá · **Zásah:** AI nebo automatizace

**Poznáš to podle:** práce je čtení, porovnávání, posuzování, vytěžování z dokumentů, generování textu nebo hledání v nepřehledném obsahu. Data existují a je jasné, co je pravda.

**Co znamená, že slabé místo žádné není:** cesta od rozhodnutí až ke konkrétnímu údaji je celá — data existují, je jasné, co je pravda, a pravidla jsou zapsaná. Ta bolest tedy nevznikla z žádné mezery. Ta práce je prostě práce a jediné, co s ní jde udělat, je nechat ji dělat stroj.

**Rozdíl proti A7:** A7 přenáší hotové údaje (to je propojení). A12 rozumí obsahu (to je AI).

**Pozor na obtok:** i když je to čistý AI case, ověř, jestli ta práce neexistuje jen proto, že něco výš v procesu ničí informaci. Pak je AI legitimní obtok, ale je třeba to napsat.

**Příklad:** Porovnávání verzí smluv odstavec po odstavci, tři a půl hodiny na jeden případ. Vyplňování údajů nájemníků do vzorových dokumentů. Denní sledování cen konkurenčního ubytování v okolí. Vytěžování údajů ze smluv a dokladů.

---

## Nejčastější záměny

Když si nejsi jistá, rozhodni tuhle jednu otázku:

| Vypadá to jako | Ale je to | Rozhodni podle |
| --- | --- | --- |
| A12 (AI vytěží dokumenty) | A7 (chybí propojení) | Jsou na obou stranách hotové strukturované údaje? |
| A12 (AI složí report) | A1 (nikde to nevzniká) | Existují ta data vůbec někde? |
| A7 (člověk to přepisuje) | A2 (není dohodnuto, kde je pravda) | Je řečeno, který systém je hlavní? Kdyby ano, šlo by propojení zadat hned? |
| A8 (lidi si dělají tabulky) | A2 (není dohodnuto, kde je pravda) | Proč to nevedou v systému — není důvod ten, že mu nevěří? |
| A4 (chodí špatná zadání) | A11 (chybí vlastník) | Kdo má mandát říct, co je hotové zadání? |
| A5 (nikdo tomu nerozumí) | A2 (dva zdroje pravdy) | Je problém neznalost pravidla, nebo že pravidla jsou dvě? |
| A3 (nejde to spojit) | A9 (staré kopie) | Je to chybějící společné číslo, nebo historický duplikát? |
