# Zadání pro posouzení švýcarské strany ze seznamu FINMA

V `kandidati.md` je **424 subjektů**, které FINMA vede jako správce fondů,
správce kolektivního majetku nebo zástupce zahraničních fondů. Je to jediný
enumerovatelný zdroj, který se v celém regionu DACH podařilo najít.

> **Proč jen Švýcarsko.** Ověřeno živým dotazem 1. 9. 2026: BaFin ani
> rakouská FMA seznam ke stažení nenabízejí — mají jen interaktivní
> vyhledávání a FMA navíc blokuje strojový přístup (HTTP 403). Kandidáti
> pro DE a AT musí přijít z pojmenované rešerše, ne z registru. Stejně jako
> u české investorské strany, kde jména padla od Martiny a teprve pak se
> ověřovala.

> **Tohle je investorská strana, ne financování.** Správce kolektivního
> majetku alokuje kapitál, nepůjčuje z vlastní bilance. Patří do listu 6,
> ne do listu 3. Výjimkou jsou ti, kdo výslovně dělají *real estate debt* —
> u těch to řekni v důvodu nahlas, ať se posoudí i pro list 3.

## Co u každého zjistit

1. **Do čeho konkrétně investuje** — rezidence, komerce, logistika, půda,
   infrastruktura. Většina jmen na seznamu jsou správci majetku bohatých
   klientů, ne nemovitostní investoři. To rozhoduje o zařazení.
2. **Jestli dělá dluh, nebo jen vlastní kapitál.** Real estate debt je pro nás
   zajímavější než nákup hotové budovy.
3. **Objem** (AuM), pokud je zveřejněný.
4. **Kdo je protistrana k oslovení** — u skupin je to správcovská firma, ne
   jednotlivý fond.

## Rozhodnutí

| Verdikt | Kdy |
|---|---|
| `zaradit` | alokuje kapitál do nemovitostí a dá se doložit, do čeho |
| `zamitnout` | správce cizího portfolia bez nemovitostní strategie · kaptivní struktura · v likvidaci |
| `nevim` | subjekt existuje, ale nic dalšího se nedá doložit z primárního zdroje |

**Role od FINMA nestačí k zařazení**, stačí ale k tomu, aby se subjekt
neztratil. Sloupec Priorita v `kandidati.md` je jen předfiltr podle slov
v názvu — 38 jmen z 424. Není to odpověď, jen pořadí.

## Pravidlo, které se neporušuje

Ke každému verdiktu `zaradit` i `zamitnout` musíš dodat **doslovnou citaci**
a **URL**, a to z **primárního zdroje** — webu subjektu, ne z profilu na
Moneyhouse nebo PitchBooku. Ty se dají použít jako vodítko, kam se podívat,
ne jako doklad.

## Výstup

Dávku zapiš do JSON ve tvaru pro `financovani-zapis-investoru.py`, s poli
`skupina`, `ico`, `zeme`, `nazev`, `web`, `typ`, `verdikt`, `segment`, `aum`,
`gatekeeper`, `duvod`, `citace`, `zdroj`. **Pole `zeme` vyplňuj vždy** (CH, DE
nebo AT) — dohledávač země umí odvodit jen české IČO, takže u DACH je zápis
z dávky jediná cesta, jak zemi do sešitu dostat. Bez ní běh subjekt přeskočí.

```
python financovani-zapis-investoru.py davka-dach-02.json --config financovani-beh-dach.config.json --zapis
```

Vzor je `davka-dach-01.json`.
