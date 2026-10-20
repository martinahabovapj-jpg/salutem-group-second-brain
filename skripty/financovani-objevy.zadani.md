# Zadání pro posouzení nových subjektů

V `kandidati.md` je seznam subjektů, které od minule přibyly do rejstříku
a v naší databázi zatím nejsou. **Registr je našel, ale nedokáže je
kvalifikovat** — u NACE 64310 je poměr použitelných k vyřazeným 22:17
a u 68200 dokonce 14:15. Z kódu se nepozná nic.

Tvoje úloha: u každého rozhodnout jednu ze tří věcí.

| Verdikt | Kdy |
|---|---|
| `zaradit` | poskytuje financování **třetím stranám** — úvěr, mezanin, bridge, whole loan, development, akviziční, refinancování, NAV lending, financování SPV nebo fondů |
| `zamitnout` | kaptivní fond půjčující jen uvnitř skupiny · zprostředkovatel bez vlastní bilance · výkupčí pohledávek · equity investor bez úvěrové strategie · fond fondů · spotřebitelské úvěry |
| `nevim` | z veřejných zdrojů to nejde rozhodnout |

> **Polovina subjektů, které se tváří jako private debt, jím není.** Přesně
> tenhle poměr vyšel při prvním mapování: ze 123 kandidátů prošlo 62.
> Když si nejsi jistý, správná odpověď je `nevim`, ne `zaradit`.

## Pravidlo, které se neporušuje

Ke každému verdiktu `zaradit` i `zamitnout` musíš dodat **doslovnou citaci**
a **URL**. Když neumíš citovat, verdikt je `nevim` — skript verdikty bez
citace sám zahodí, ale to je pojistka, ne postup.

## Na co si dát pozor u podfondů

Většina přírůstků jsou **podfondy SICAV**, které vznikly před pár týdny.
Vlastní web zpravidla nemají. Hledej:

1. stránku **mateřského fondu** (název před slovem „podfond")
2. **statut nebo sdělení klíčových informací** — tam bývá investiční strategie
3. seznam ČNB

Když ani tam není nic o poskytování financování, je to `nevim`. Název sám
o sobě nestačí ani pro zařazení, ani pro zamítnutí: „LOAN" v názvu ještě
neznamená, že půjčuje třetím stranám, a neutrální název neznamená, že nepůjčuje.

## Co si zapsat u zamítnutí

Důvod zamítnutí se pamatuje natrvalo a **subjekt se už nikdy nenabídne znovu**.
Piš ho tak, aby za rok dával smysl někomu, kdo tenhle běh neviděl — tedy
„kaptivní, financuje jen projekty vlastní skupiny", ne „nehodí se".

## Výstup

Zapiš `objevy.json` vedle skriptu:

```json
[
  {
    "ico": "75166828",
    "nazev": "ČNFE LOAN podfond",
    "verdikt": "zaradit",
    "duvod": "úvěrový podfond poskytující financování třetím stranám",
    "citace": "doslovná věta ze zdroje",
    "zdroj": "https://..."
  }
]
```

Pak spusť:

```
python financovani-objevy.py --verdikty objevy.json --zapis
```

Zařazené jdou do listu „5 Návrhy změn" jako pruh B — tedy ke schválení
člověkem, ne rovnou do databáze. Zamítnuté se zapamatují.
