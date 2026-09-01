# Databáze poskytovatelů financování — návod

Tenhle nástroj hlídá, jestli údaje v databázi pořád platí, a hledá subjekty,
které do ní ještě nepatří. Běží nad jedním souborem — **master sešitem** —
a všechno, co udělá, je v něm vidět.

**Tvoje práce se vejde do dvou dvojkliků měsíčně a jednoho sloupce v Excelu.**
Zbytek téhle stránky je proto, aby bylo jasné, co se děje kolem.

---

## Nejdřív to hlavní: co si udělá sám a co čeká na tebe

| | Kdo to dělá |
|---|---|
| Zjistit, jestli firma nezanikla, není v insolvenci nebo v likvidaci | **nástroj sám** |
| Zjistit, jestli firmě funguje web | **nástroj sám** |
| Všimnout si, že se firmě změnila stránka | **nástroj sám** |
| Rozhodnout, jestli ta změna něco znamená | **ty** — v listu „5 Návrhy změn" |
| Zapsat schválené změny do databáze | **nástroj sám**, až mu to řekneš |
| Hledat nové firmy na trhu a posuzovat je | **Martina s Claudem** — tobě dorazí až výsledek |

Jinými slovy: **rejstříkové věci si nástroj opraví sám. Všechno ostatní ti jen
navrhne a čeká.**

---

## Tvoje měsíční rutina

### Krok 1 — spusť kontrolu

Dvojklik na **`beh\refresh.cmd`**.

Obchází ARES, insolvenční rejstřík a weby všech firem, takže to trvá
**pět až deset minut**. Nic přitom nezapisuje. Na konci uvidíš:

```
Pruh A (aplikovano automaticky): 2     <- rejstříkové věci, projdou samy
Pruh B (ceka na schvaleni):      7     <- tohle rozhodneš ty
Pruh C (jen do logu):            3     <- drobnosti bez dopadu
```

Zajímá tě jen prostřední řádek.

> **Když je všude nula, je to v pořádku a je to normální.** Nástroj napíše
> „Zkontrolováno, nic ke schválení" i tehdy, když se nic nezměnilo — schválně,
> protože z mlčení se nepozná klid od spadlého běhu.

### Krok 2 — rozhodni v listu „5 Návrhy změn"

Otevři master sešit, list **„5 Návrhy změn"**. Každý řádek je jeden návrh:

| Sloupec | Co v něm je |
|---|---|
| Co | které pole se mění |
| Bylo → Navrženo | stará a nová hodnota |
| Zdroj (URL) | odkaz, ze kterého to je — klikni a ověř |
| Poznámka schvalovatele | doslovná citace ze stránky |
| **Schválit** | **klikni do buňky a vyber z roletky** |
| Vyřízeno | datum, kdy to nástroj zapsal. Prázdné = pořád čeká |

Ve sloupci **Schválit** je rozbalovací seznam se dvěma možnostmi:
**přijmout** nebo **zamítnout**. Nic se nepíše, jen se vybírá.

Sloupec je **schválně prázdný** — dokud v něm nic nevybereš, nic se nestane.
Řádky, které necháš prázdné, počkají do příště.

> **Bez odkazu a citace se návrh vůbec neobjeví.** Když nástroj neumí doložit,
> odkud to má, návrh nevytvoří. Takže u každého řádku si můžeš ověřit, odkud to je.

### Krok 3 — zapiš

Dvojklik na **`beh\ZAPSAT.cmd`**. Zeptá se, jestli to myslíš vážně, a pak:

1. **vyřídí frontu** — zapíše, co jsi schválil, a zapamatuje si, co jsi zamítl
2. **spustí kontrolu znovu** a zapíše, co našla

Vypíše ti, co kam šlo. **Master sešit přitom musí být zavřený v Excelu**, jinak
zápis neprojde — Excel si soubor zamyká pro sebe. Nic se nerozbije, jen se nic
nezapíše a nástroj ti to řekne.

Před zápisem si sám udělá záložní kopii sešitu do složky `beh\zalohy\`.

**A to je celé.** Zbytek si přečti, až budeš něco potřebovat.

---

## Co znamenají jednotlivé listy

Sešit má úvodní přehled a osm očíslovaných listů. Pracovní jsou pro tebe dva —
list 5, kde rozhoduješ, a list 2, kde vybíráš z roletky. Zbytek jsou data.

| List | Co v něm je | Sáháš na něj? |
|---|---|---|
| **1 Subjekty** | hlavní seznam firem — kdo, IČO, web, stav, jaké má role | čteš |
| **2 Kontakty** | jména, telefony, maily — a **kdo z nás s kým komunikuje** | **vybíráš z roletky** |
| 3 Role Financování | kdo co půjčuje — typy financování, ticket, LTV | čteš |
| 4 Zdroje | **doslovné citace a odkazy ke každému údaji** | čteš, když něčemu nevěříš |
| **5 Návrhy změn** | **fronta, ve které rozhoduješ** | **tady pracuješ** |
| 6 Role Investor | kdo do projektů investuje — family office, fondy | čteš |
| **7 Zamítnuto při hledání** | firmy, které se posuzovaly a nezařadily, i s důvodem | čteš |
| **8 K ověření** | firmy, u kterých se **nepodařilo rozhodnout** | čteš, když máš čas |

### Sloupec „Kdo komunikuje“ v listu 2

Poslední sloupec listu **„2 Kontakty“** je roletka se jmény kolegů — dnes
**Dudjak** a **Nečas**. Vybírá se v ní, kdo z nás je s tím konkrétním člověkem
v komunikaci, aby ho neoslovili dva lidé nezávisle na sobě.

**Prázdné znamená „zatím nikdo“**, ne chybu. Nástroj do toho sloupce sám nikdy
nic nezapíše ani nic nepřepíše — je celý tvůj.

Přibyde další kolega? Neopravuje se to v Excelu, ale v konfiguraci
(`beh\financovani-beh.config.json`, sekce `komunikace`) — jinak by se jméno
při dalším zápisu z roletky ztratilo. Řekni Martině.

### Proč jsou listy 7 a 8 dva, a ne jeden

Když se posuzuje nová firma, jsou tři možné konce:

- **zařadit** → přibude do listu 1 a dostane citaci do listu 4
- **zamítnout** → jde do listu **7**. Rozhodnuto natrvalo, znovu se nenabídne
- **nevím** → jde do listu **8**. **Není to zamítnutí** — jen se nepodařilo nic doložit

Ten třetí se snadno přehlédne, a je důležitý. **K 1. 9. 2026 je v listu 8
šestaosmdesát řádků** a naprostá většina jich pochází z posuzování investorů.
Jsou to jednotlivé podfondy bez vlastní stránky — spravuje je za ně AVANT,
AMISTA nebo DELTA a o sobě nezveřejňují nic než to, že existují. Mezi nimi
jsou firmy, které do databáze nejspíš patří.

U každé je vidět **proč se nerozhodlo**. Když si s některou poradíš, řekni
Martině — a **řádek z listu 8 pak zmizí sám**, jakmile se firma zařadí nebo
zamítne. Nic odtud nemažeš ručně.

### Proč je list 7 užitečný, i když jsou to „odpadky"

Není. Bez něj by se tytéž firmy nabízely znovu každý měsíc a na otázku
„koukali jsme někdy na tuhle firmu?" by v databázi nebyla odpověď.

---

## Co pouští Martina, ne ty

Tři dvojkliky ve složce `beh\` jsou na hledání nových firem. **Nic nezapisují** —
vyrobí seznam kandidátů, které pak musí někdo posoudit, a to dělá Martina
s Claudem. K tobě dorazí až výsledek, do listu „5 Návrhy změn".

| Dvojklik | Co hledá |
|---|---|
| `OBJEVY.cmd` | firmy nově zapsané do obchodního rejstříku |
| `FONDY-CNB.cmd` | investiční fondy, které ČNB vede jako **úvěrové** — těch je v celé ČR kolem deseti, takže je to seznam, co jde projít celý |
| `INVESTORI.cmd` | investorskou stranu — family office a wealth management |

Spustit je můžeš, nic tím nepokazíš. Jen z toho sám nic nevyčteš.

---

## Když se něco pokazí

**Nástroj něco zapsal a nemělo se to stát.**
Otevři složku `beh`, klikni do adresního řádku nahoře, napiš `cmd` a odentruj.
Do černého okna vlož:

```
python financovani-beh.py --vrat 2026-09-01 --zapis
```

Datum nahraď dnem toho běhu. Vrátí všechny změny z toho dne.

Dvě věci nevrátí: **nově založený řádek** a **připsanou poznámku**. Mazat řádky
z databáze kvůli kroku zpět je horší než je tam nechat — řekne ti o nich nahlas
a záloha sešitu je ve složce `beh\zalohy\`.

**Nástroj hlásí totéž každý měsíc a nic to neznamená.**
Některé weby se mění při každém načtení. Řekni to Martině, dá se to u konkrétní
firmy vypnout.

**Zápis neprojde a píše, že je sešit zamčený.**
Máš ho otevřený v Excelu. Zavři ho a spusť znovu. Nic se nezapsalo.

**Disk O: není vidět.**
Otevři Průzkumník, klikni na O: a zkus znovu. Nástroj to pozná a řekne ti to —
**nesnaž se opravovat cesty v konfiguraci**, ty jsou v pořádku.

> Stává se to opakovaně — v srpnu a v září 2026 se disk sám odpojil čtyřikrát
> a pokaždé se po chvíli vrátil sám. Když se O: neobjeví ani po chvíli, není
> to nic, co bys spravil ty: server prostě neběží. Zkus to za hodinu a když
> to trvá, řekni Martině.

**Něco vypadá divně.**
Nástroj nikdy nemaže řádky. Cokoli udělal, je v listu 1 ve sloupci Poznámka
s datem a odkazem, a citace je v listu 4.

---

## Co nástroj nedělá

- **Nerozhoduje za tebe.** Typy financování, tickety, LTV a kontakty zapíše jen
  tehdy, když je v listu 5 označíš jako „přijmout".
- **Nehlídá slovenskou insolvenci.** Českou ano, slovenskou ne — vede ji jiný
  registr, který zatím není napojený. Týká se to 10 aktivních firem (1. 9. 2026).
- **Nekontroluje dvě firmy vůbec** — Evropskou investiční banku (LU) a CVI Dom
  Maklerski (PL). Nemají české ani slovenské IČO a jejich země nemá napojený
  registr. Běh to pokaždé napíše.
- **Nekontroluje v rejstříku firmy bez IČO ani bez vyplněné země.** Web jim hlídá,
  rejstřík ne — není se čeho ani koho zeptat. **K 1. 9. 2026 je aktivních firem
  bez IČO 41 a řádků, které běh přeskočí kvůli chybějící zemi, 48.** Vyskočilo to
  proto, že v srpnu a v září přibylo přes čtyřicet nových investorů ze seznamu ČNB
  a zapisovací skript zemi ani IČO nevyplňuje — dohledávají se zvlášť. Běh je
  vypíše jako „ZEMĚ NENÍ VYPLNĚNA" a jakmile někdo IČO a zemi doplní, začnou se
  hlídat samy. Je to jediná díra, kterou jde zavřít bez programování.
- **Nesmaže vyřazené firmy.** Zůstávají v listu 1 se stavem VYŘAZEN i s důvodem,
  aby je za půl roku nikdo neprověřoval znovu.
- **Nenajde všechno.** Dvě kombinace v obchodním rejstříku jsou tak široké, že je
  ARES odmítá prohledat. Nástroj to při každém hledání napíše, místo aby dělal,
  že je hotovo.

---

## Co je ve složce

| Soubor | K čemu je |
|---|---|
| `Master_databaze_financovani_*.xlsx` | **hlavní soubor. Tenhle jediný platí** |
| `Kdo_mi_to_zafinancuje_LIVE.html` | vyhledávač — otevři v prohlížeči a načti si sešit |
| `beh\refresh.cmd` | **spustí kontrolu** (tvoje) |
| `beh\ZAPSAT.cmd` | **zapíše, co jsi schválil** (tvoje) |
| `beh\KONTROLA.cmd` | jednou na začátku — projde to na tomhle počítači vůbec? |
| `beh\OBJEVY.cmd` | hledá nové firmy v rejstříku (Martiny) |
| `beh\FONDY-CNB.cmd` | hledá úvěrové fondy podle ČNB (Martiny) |
| `beh\INVESTORI.cmd` | hledá investory a family office (Martiny) |
| `beh\zalohy\` | zálohy sešitu před každým zápisem |
| `beh\stranky\`, `beh\k-*\` | pracovní soubory nástroje. **Nesahat** |

> **Jedno pravidlo, na kterém všechno stojí: master sešit existuje jednou.**
> Když si ho někdo zkopíruje k sobě a bude upravovat kopii, za měsíc nikdo
> nepozná, která verze platí. Komu ho potřebuješ poslat, pošli odkaz sem —
> ne přílohu.

Něco nesedí nebo to hlásí nesmysl? **Martina Habová.**
