# Funnel na AI Hubu — jak ho obnovit

Sekce **Funnel** na `salutem-ai-hub.vercel.app/prioritizacni-mapa` ukazuje, kde
co je: 41 zadání rozložených do fází od nápadu do provozu, a k tomu dva
průřezy — jestli k tomu existuje business case a na čem to stojí.

Data v ní jsou **snímek**, ne živé napojení. Když se má snímek obnovit, pustí
se jeden skript.

## Obnova

```
cd ~/salutem-group-second-brain/skripty
python funnel-ai-hub.py
```

Skript udělá celý řetěz: stáhne živé úkoly z Freela → vytěží z popisů šablonu
v2 → přepočítá fáze → vloží nový blok dat do `prioritizacni-mapa.html` →
zkontroluje, že všechna čísla sedí. **Když čísla nesedí, do stránky nezapíše.**

Trvá to asi minutu (mezi dotazy na Freelo dělá pauzy, aby nenarazil na limit).

Pak se to musí nasadit:

```
cd ~/salutem-ai-hub
git add prioritizacni-mapa.html
git commit -m "Funnel: obnoveny snimek"
git push origin main
```

> ⚠️ **Push sám nasazení nezaručí.** Vercel umí deploy tiše zablokovat
> (párování e-mailu commitu na GitHub účet). Po pushi je proto potřeba
> zkontrolovat, že se na stránce objevilo nové datum „Stav k …" — a když ne,
> podívat se do Vercelu na status deploye.

## Dva režimy, když nechceš zapisovat

| Příkaz | Co udělá |
|---|---|
| `python funnel-ai-hub.py --nahled` | spočítá a vypíše, do stránky **nezapíše**; data uloží do `funnel-ai-hub.nahled.json` |
| `python funnel-ai-hub.py --overit` | jen zkontroluje čísla, která už na stránce jsou |

`--nahled` je dobrý, když chceš jen vidět, co by se změnilo, nebo si přečíst
seznam úkolů bez štítku.

## Co skript vypíše a co s tím

Kromě rozdělení do fází vypíše tři seznamy, které jsou **návod na úklid ve
Freelu**:

- **Bez štítku pipeline** — tyto úkoly funnel neumí zařadit a drží je ve
  sloupci *Bez stavu*. Řešení: dát jim štítek.
- **Dva štítky naráz** — porušuje pravidlo „poptávka má právě jeden štítek".
  Funnel je řadí podle pozdějšího a v tabulce je označí.
- **Nezapsáno** u „na čem to stojí" — místa, kde vlastně nevíme, čí je další
  krok.

## Kde co leží

| Soubor | Co to je |
|---|---|
| `skripty/funnel-ai-hub.py` | celý řetěz v jednom skriptu |
| `skripty/funnel-ai-hub.popisky.json` | **všechny české texty sekce** — názvy fází, jejich kritéria, popisky |
| `skripty/funnel-ai-hub/funnel.css` | styly sekce |
| `skripty/funnel-ai-hub/funnel.html` | struktura sekce (prázdné kontejnery) |
| `skripty/funnel-ai-hub/funnel.js` | vykreslení grafu a tabulek v prohlížeči |

**Když chceš změnit text na stránce** — přejmenovat fázi, přepsat kritérium,
jinak popsat kategorii — uprav `funnel-ai-hub.popisky.json` a pusť skript.
Do `.py` se diakritika nepíše, na Windows z ní vzniká mojibake.

## Druhý skript na téže stránce: vlastníci podnětů

`skripty/vlastnici-podnetu.py` dopisuje do tabulky všech 125 podnětů sloupec
**Vlastník**. Je to samostatná věc od funnelu a pouští se jen když se změní
vazby v Airtable:

```
python ~/salutem-group-second-brain/skripty/vlastnici-podnetu.py --nahled
python ~/salutem-group-second-brain/skripty/vlastnici-podnetu.py
```

> ⚠️ **Airtable tady nemá API klíč** — jde jen přes MCP konektor v Claude Code.
> Vazby se proto nedají stáhnout automaticky a záznamem *je*
> `skripty/vlastnici-podnetu.json`. Když se v Airtable něco změní, musí se
> dopsat tam ručně (nebo si o to říct Claudovi, ten na Airtable dosáhne).

Vlastník má tři úrovně průkaznosti a ta úroveň je na stránce vidět: *řekl to
sám* (člověk podnět vyslovil v rozhovoru), *pravděpodobný* (z role, která to má
rozhodnout) a *jen role* (roli neodpovídá právě jeden člověk). Jména se
k rolím vedoucí IT, vedoucí právního a CFO vědomě nedopisují.

Oba skripty sahají na jinou část stránky, takže si navzájem nepřepisují práci:
funnel na `fn-data` a sekci Funnel, vlastníci na `pm-data` a tabulku 125 podnětů.

## Proč to není živý dashboard

Sekce „AI agenda" na hlavní stránce Hubu živě čte Freelo přes
`api/dashboard.js`. Funnel záměrně ne, ze dvou důvodů:

1. **Odolnost.** Živý dashboard už jednou zmizel, když Freelo vrátilo rate
   limit a prázdná odpověď se zacachovala. Snímek tenhle problém nemá.
2. **Funnel má něco, co v Freelu není** — mapování štítků na fáze, kategorie
   „na čem to stojí" a zásobník podnětů z prioritizační mapy. To se počítá,
   ne čte.

Definice fází a nálezy z prvního snímku (7. 9. 2026) jsou v second brainu
v `03 Jak pracujeme/zivotni-cyklus-poptavky.md`, sekce „Funnel: štítky složené
do fází".
