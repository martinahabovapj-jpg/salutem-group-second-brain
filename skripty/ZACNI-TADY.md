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
| **Schválit** | **předvyplněné rozhodnutí — přepiš, když nesouhlasíš** |

Rozhodnutí je předvyplněné schválně. Nemáš dělat deset rozhodnutí — máš
projet seznam a u dvou tří přepsat, co ti nesedí.

> **Bez odkazu a citace se návrh vůbec neobjeví.** Když nástroj neumí doložit,
> odkud to má, návrh nevytvoří. To je záměr, ne chyba.

### 3. Zapiš

Dvojklik na **`ZAPSAT.cmd`**. Zeptá se, jestli to myslíš vážně.

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

To posouzení dělá Martina s Claudem. Ty se pak uvidíš jen výsledek v listu
„5 Návrhy změn" jako řádek „nový subjekt".

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

- **Nepíše nic sám do sešitu kromě rejstříkových věcí.** Nové typy financování,
  tickety, LTV a kontaktní osoby jdou vždycky přes tebe.
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
| `beh\refresh.cmd` | spustí kontrolu |
| `beh\ZAPSAT.cmd` | zapíše schválené změny |
| `beh\zalohy\` | zálohy sešitu před každým zápisem |
| `beh\stranky\` | pracovní kopie webů, ať se pozná, co se změnilo. Nesahat |

> **Jedno pravidlo, na kterém všechno stojí:** master sešit existuje **jednou**.
> Když si ho někdo zkopíruje k sobě a bude upravovat kopii, za měsíc nikdo
> nepozná, která verze platí. Komu ho potřebuješ poslat, pošli odkaz sem —
> ne přílohu.

Potřebuješ něco změnit nebo to hlásí nesmysl? Martina Habová.
