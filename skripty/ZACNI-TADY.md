# Měsíční refresh databáze poskytovatelů financování

Tenhle nástroj hlídá, jestli údaje v databázi pořád platí. Jednou za měsíc
projde všechny subjekty, podívá se do rejstříků a na jejich weby a řekne,
co se změnilo.

**Není to robot, který si dělá, co chce.** Sám opraví jen věci, které se dají
ověřit v rejstříku — insolvenci, zánik firmy, nefunkční web. Všechno ostatní
ti jen navrhne a čeká, až to odsouhlasíš.

---

## Jak se to používá

### 0. Jednou na začátku: `KONTROLA.cmd`

Dvojklik na **`beh\KONTROLA.cmd`**. Trvá pár vteřin a ověří devět věcí —
jestli máš Python, knihovny, jestli vidíš na master sešit a jestli se z tvého
počítače dá dosáhnout na rejstříky.

Když něco neprojde, napíše ti to česky i s tím, co s tím udělat.

> Proč to existuje: osm dní se u tohohle projektu vedlo jako blokující, že
> rejstříky nejsou dostupné. Byly — jen se to zkoušelo na jiném počítači.
> **Dostupnost se ověřuje tam, kde to poběží.**

### 1. Spusť kontrolu

Dvojklik na **`refresh.cmd`**.

Chvíli to trvá — obchází se ARES, insolvenční rejstřík a weby všech subjektů.
Počítej s pěti až deseti minutami. Nic se přitom nezapisuje.

Na konci uvidíš přehled:

```
Pruh A (aplikovano automaticky): 2     <- rejstříkové věci, projdou samy
Pruh B (ceka na schvaleni):      7     <- tohle rozhodneš ty
Pruh C (jen do logu):            3     <- drobnosti bez dopadu
```

### 2. Podívej se, co je ke schválení

Otevři master sešit, list **„5 Návrhy změn"**. Každý řádek říká:

| Sloupec | Co v něm je |
|---|---|
| Co | které pole se mění |
| Bylo → Navrženo | stará a nová hodnota |
| Zdroj (URL) | odkaz, ze kterého to je |
| Poznámka schvalovatele | doslovná citace ze stránky |
| **Schválit** | **tady rozhoduješ ty — klikni do buňky a vyber z roletky** |
| Vyřízeno | datum, kdy to skript zapsal. Prázdné = pořád ve frontě |

Ve sloupci **Schválit** je rozbalovací seznam se dvěma možnostmi:
**přijmout** nebo **zamítnout**. Nic se nepíše, jen se vybírá. Cokoli jiného
skript nepřečte a řádek nechá ve frontě.

Sloupec je **schválně prázdný**. Dřív býval předvyplněný, ale to bylo v době,
kdy byl jen na okrasu — dnes je to spouštěč: co je označené jako „přijmout",
to `ZAPSAT.cmd` **opravdu zapíše** do listů 1–3. Kdo se na frontu nepodívá,
ten by ji tím odsouhlasil.

- **přijmout** → hodnota se zapíše tam, kam patří (ticket a LTV do listu 3,
  kontakt do listu 2, nový subjekt jako nový řádek v listu 1), doplní se
  datum ověření a do listu „4 Zdroje" přibude citace s odkazem
- **zamítnout** → skript si to **zapamatuje natrvalo** a příští měsíc už to
  nenabídne. Zamítnuté nové subjekty navíc přistanou v listu
  „7 Zamítnuto při hledání", aby se za rok dalo dohledat proč

Řádek, který vyřídíš, dostane datum ve sloupci **Vyřízeno** a víc se ho nikdo
nedotkne. Fronta se tím vyprazdňuje — nezůstane v ní sto řádků, u kterých
nikdo nepozná, které už jsou hotové.

> **Bez odkazu a citace se návrh vůbec neobjeví.** Když nástroj neumí doložit,
> odkud to má, návrh nevytvoří. To je záměr, ne chyba.

### 3. Zapiš

Dvojklik na **`ZAPSAT.cmd`**. Zeptá se, jestli to myslíš vážně, a pak udělá
dvě věci za sebou:

1. **vyřídí frontu** — zapíše, co jsi schválil, a zapamatuje si, co jsi zamítl
2. **spustí kontrolu** a zapíše, co našla

Na konci ti vypíše, co kam šlo. Když si s něčím neví rady — třeba proto, že
je ve sloupci Schválit překlep — **nechá ten řádek ve frontě a řekne to
nahlas**. Nikdy nehádá.

**Master sešit musí být zavřený v Excelu**, jinak zápis neprojde — Excel si
soubor zamyká pro sebe. Nic se nerozbije, jen se nic nezapíše.

Před zápisem se sám udělá záložní kopie sešitu do složky `zalohy\`.

---

## Druhá věc: nové subjekty

`refresh.cmd` hlídá subjekty, které v databázi **už jsou**. Nenajde toho,
kdo do ní ještě nepatří.

Na to je **`OBJEVY.cmd`** — projde obchodní rejstřík a vypíše subjekty, které
od minule vznikly a my o nich nevíme. Stačí pouštět jednou za měsíc nebo za
čtvrtletí, přírůstek je zhruba **čtrnáct subjektů měsíčně**.

Nic nezapisuje. Vyrobí seznam kandidátů ve složce `k-posouzeni`, u kterých
musí někdo rozhodnout, jestli patří do databáze. **Rejstřík to sám nepozná** —
u fondů vychází poměr použitelných k nepoužitelným zhruba půl na půl a rozhoduje
to, co subjekt reálně dělá, ne pod jakým kódem je zapsaný.

To posouzení dělá Martina s Claudem. Ty pak uvidíš jen výsledek v listu
„5 Návrhy změn" jako řádek „nový subjekt".

Ty, které posouzením neprošly, skončí v listu **„7 Zamítnuto při hledání"** —
s datem, důvodem a odkazem. Ten seznam je aktivum, ne odpad: bez něj by se
tytéž fondy nabízely znovu každý měsíc a na otázku „koukali jsme někdy na
Satoshi Bridge?" by v databázi nebyla odpověď.

## Třetí věc: kontrola proti ČNB

`refresh.cmd` se ptá subjektů, které známe. `OBJEVY.cmd` se ptá obchodního
rejstříku. **`FONDY-CNB.cmd` se ptá regulátora** — a ten ví něco, co ARES neví.

ČNB vede u každého investičního fondu **kategorii podle skutečné investiční
strategie**, a jedna z nich je přímo **„úvěrový"**. V ARESu mají všechny fondy
týž kód 64310 a nerozliší se nic.

Těch úvěrových je v celé republice **řádově deset**, takže je to seznam, který
jde projít celý — a hned je vidět, které v databázi chybí.

> **Kategorie sama k zařazení nestačí.** Fond, který úvěruje výhradně projekty
> vlastní skupiny, je pro ČNB pořád „úvěrový", ale pro nás je kaptivní a do
> databáze nepatří. Rozhodnout to musí člověk s citací.

Pouštět stačí jednou měsíčně — ČNB seznam v té kadenci vydává. Nic nezapisuje,
připraví složku `k-posouzeni-cnb`.

## Čtvrtá věc: investorská strana (list 6)

Databáze má **dvě role, ne dvě databáze**. Listy 1 a 2 jsou společný registr —
subjekty a kontakty. Na něm stojí dvě různé otázky:

| List | Otázka |
|---|---|
| **3 Role Financování** | kdo mi to **půjčí** z vlastní bilance |
| **6 Role Investor** | kdo do toho **investuje** — family office, wealth management |

**Jeden subjekt může mít obě role.** Když ho zařadíš jako investora, přibude
mu v listu 1 ve sloupci „Role: investor" hodnota ANO a v listu 6 vlastní řádek.
Zůstává to jeden řádek v jednom registru — proto ho **měsíční kontrola hlídá
úplně stejně** jako všechny ostatní: rejstřík, insolvence, funkční web, změny
na stránkách. Nic navíc se pro to spouštět nemusí.

Rozdíl je jen v tom, **co se na jeho webu sleduje**: u investora navíc segment
(do čeho investuje), AUM a gatekeeper. Skript to pozná sám podle role
zapsané v listu 1.

Hledání nových je **`INVESTORI.cmd`**. Nejde přes rejstříkové kódy jako
`OBJEVY.cmd` — family office nemá vlastní NACE a v ARESu vypadá jako běžné
s.r.o. Hledá se **podle jmen** ze seznamu v konfiguraci: ARES ke jménu dohledá
celý firemní trs (často několik entit na jedné adrese, což je samo o sobě
signál) a teprve web s citací rozhodne. Máš nové jméno? Přidej ho do seznamu.

> **Pozor na dvě věci.** Shoda jména sama o sobě neznamená nic — v dávce budou
> i spolky a cestovky. A family office o sobě záměrně mnoho nepíše, takže
> „nevím" je u nich častá a správná odpověď.

## Kde se co ukládá — tři různé osudy

Když se posuzuje nový subjekt, jsou tři možné konce a **každý má svoje místo**:

| Verdikt | Kam to jde | Co to znamená |
|---|---|---|
| **zařadit** | list 1 + role, k tomu citace do listu 4 | patří do databáze |
| **zamítnout** | list **„7 Zamítnuto při hledání"** | rozhodnuto natrvalo, znovu se nenabídne |
| **nevím** | list **„8 K ověření"** | **nerozhodnuto** — nedalo se nic doložit |

Ten třetí je důležitý a snadno se přehlédne. **„Nevím" není zamítnutí.** Nejčastěji
znamená jen, že subjektu nefunguje web nebo o sobě nic nezveřejňuje — z 46 řádků,
které v listu 8 leží dnes, je většina z toho důvodu.

V listu 8 je u každého vidět **proč se nerozhodlo**, takže se dá projít a rozhodnout
ručně. **Jakmile se subjekt zařadí nebo zamítne, řádek z listu 8 zmizí sám** — nemusí
se odtud nic mazat.

> Dřív se „nevím" zahazovalo a nikdo se k takovému subjektu už nevrátil. To byla
> chyba: mezi nimi jsou i firmy, které do databáze patří, jen se to zrovna
> nepodařilo doložit.

## Když se něco pokazí

**Nástroj něco zapsal a nemělo se to stát.** Vrátit to je jeden příkaz.
Otevři složku `beh`, klikni do adresního řádku, napiš `cmd` a odentruj.
Pak vlož:

```
python financovani-beh.py --vrat 2026-09-01 --zapis
```

Datum nahraď dnem toho běhu. Vrátí se všechny automatické změny z toho dne.

**Nástroj hlásí totéž každý měsíc a nic to neznamená.** Některé weby se mění
při každém načtení (ochrana proti robotům). Řekni to Martině — dá se to
vypnout u konkrétního subjektu.

**Něco vypadá divně.** Nástroj nikdy nemaže řádky. Cokoli udělal, je vidět
ve sloupci Poznámka s datem a odkazem, a záloha sešitu je ve složce `zalohy\`.

---

## Co nástroj nedělá

- **Nerozhoduje.** Nové typy financování, tickety, LTV a kontaktní osoby zapíše
  jen tehdy, když je v listu 5 označíš jako „přijmout". Sám od sebe opraví
  jen to, co se dá ověřit v rejstříku — insolvenci, zánik, nefunkční web.
- **Nevrátí nový řádek.** Příkaz `--vrat` umí vzít zpátky přepsané hodnoty,
  ale nově založený subjekt nesmaže a připsanou poznámku neodmaže — mazat
  řádky z databáze kvůli kroku zpět je horší než je tam nechat. Řekne o tom
  nahlas a záloha sešitu je ve složce `zalohy\`.
- **Nehlídá slovenskou insolvenci.** České ano, slovenské ne — vede je jiný
  registr, který zatím není napojený. Týká se to 13 subjektů.
- **Nesmaže vyřazené subjekty.** Zůstávají v databázi i s důvodem vyřazení,
  aby je za půl roku nikdo neprověřoval znovu.
- **Nekontroluje dva subjekty vůbec** — Evropskou investiční banku (LU)
  a CVI Dom Maklerski (PL). Nemají české ani slovenské IČO. Běh to pokaždé
  napíše, aby se na to nezapomnělo.

---

## Když ticho, tak proč

Nástroj napíše přehled, i když se nic nezměnilo:

> „Zkontrolováno 142 subjektů, nic ke schválení."

Je to schválně. Mlčení je dvojznačné — nepoznalo by se, jestli je klid,
nebo jestli to prostě nedoběhlo.

---

## Co je v téhle složce

| Soubor | K čemu je |
|---|---|
| `Master_databaze_financovani_*.xlsx` | **hlavní soubor.** Tenhle jediný platí |
| `Kdo_mi_to_zafinancuje_LIVE.html` | vyhledávač — otevři v prohlížeči, načti si sešit |
| `beh\KONTROLA.cmd` | jednou na začátku — projde na tomhle počítači vůbec? |
| `beh\OBJEVY.cmd` | hledání nových subjektů, které na trhu přibyly |
| `beh\FONDY-CNB.cmd` | kontrola proti seznamu fondů ČNB — najde úvěrové fondy, které nemáme |
| `beh\INVESTORI.cmd` | hledání na investorské straně — family office, wealth management |
| `beh\refresh.cmd` | spustí kontrolu |
| `beh\ZAPSAT.cmd` | zapíše schválené změny |
| `beh\zalohy\` | zálohy sešitu před každým zápisem |
| `beh\stranky\` | pracovní kopie webů, ať se pozná, co se změnilo. Nesahat |

> **Jedno pravidlo, na kterém všechno stojí:** master sešit existuje **jednou**.
> Když si ho někdo zkopíruje k sobě a bude upravovat kopii, za měsíc nikdo
> nepozná, která verze platí. Komu ho potřebuješ poslat, pošli odkaz sem —
> ne přílohu.

Potřebuješ něco změnit nebo to hlásí nesmysl? Martina Habová.
