# Fanel na AI Hubu — jak ho obnovit

Sekce **Fanel** na `salutem-ai-hub.vercel.app/prioritizacni-mapa` ukazuje, kde
co je: 41 zadání rozložených do fází od nápadu do provozu, a k tomu dva
průřezy — jestli k tomu existuje business case a na čem to stojí.

Data v ní jsou **snímek**, ne živé napojení. Když se má snímek obnovit, pustí
se jeden skript.

## Obnova

```
cd ~/salutem-group-second-brain/skripty
python fanel-ai-hub.py
```

Skript udělá celý řetěz: stáhne živé úkoly z Freela → vytěží z popisů šablonu
v2 → přepočítá fáze → vloží nový blok dat do `prioritizacni-mapa.html` →
zkontroluje, že všechna čísla sedí. **Když čísla nesedí, do stránky nezapíše.**

Trvá to asi minutu (mezi dotazy na Freelo dělá pauzy, aby nenarazil na limit).

Pak se to musí nasadit:

```
cd ~/salutem-ai-hub
git add prioritizacni-mapa.html
git commit -m "Fanel: obnoveny snimek"
git push origin main
```

> ⚠️ **Push sám nasazení nezaručí.** Vercel umí deploy tiše zablokovat
> (párování e-mailu commitu na GitHub účet). Po pushi je proto potřeba
> zkontrolovat, že se na stránce objevilo nové datum „Stav k …" — a když ne,
> podívat se do Vercelu na status deploye.

## Dva režimy, když nechceš zapisovat

| Příkaz | Co udělá |
|---|---|
| `python fanel-ai-hub.py --nahled` | spočítá a vypíše, do stránky **nezapíše**; data uloží do `fanel-ai-hub.nahled.json` |
| `python fanel-ai-hub.py --overit` | jen zkontroluje čísla, která už na stránce jsou |

`--nahled` je dobrý, když chceš jen vidět, co by se změnilo, nebo si přečíst
seznam úkolů bez štítku.

## Co skript vypíše a co s tím

Kromě rozdělení do fází vypíše tři seznamy, které jsou **návod na úklid ve
Freelu**:

- **Bez štítku pipeline** — tyto úkoly fanel neumí zařadit a drží je ve
  sloupci *Bez stavu*. Řešení: dát jim štítek.
- **Dva štítky naráz** — porušuje pravidlo „poptávka má právě jeden štítek".
  Fanel je řadí podle pozdějšího a v tabulce je označí.
- **Nezapsáno** u „na čem to stojí" — místa, kde vlastně nevíme, čí je další
  krok.

## Kde co leží

| Soubor | Co to je |
|---|---|
| `skripty/fanel-ai-hub.py` | celý řetěz v jednom skriptu |
| `skripty/fanel-ai-hub.popisky.json` | **všechny české texty sekce** — názvy fází, jejich kritéria, popisky |
| `skripty/fanel-ai-hub/fanel.css` | styly sekce |
| `skripty/fanel-ai-hub/fanel.html` | struktura sekce (prázdné kontejnery) |
| `skripty/fanel-ai-hub/fanel.js` | vykreslení grafu a tabulek v prohlížeči |

**Když chceš změnit text na stránce** — přejmenovat fázi, přepsat kritérium,
jinak popsat kategorii — uprav `fanel-ai-hub.popisky.json` a pusť skript.
Do `.py` se diakritika nepíše, na Windows z ní vzniká mojibake.

## Proč to není živý dashboard

Sekce „AI agenda" na hlavní stránce Hubu živě čte Freelo přes
`api/dashboard.js`. Fanel záměrně ne, ze dvou důvodů:

1. **Odolnost.** Živý dashboard už jednou zmizel, když Freelo vrátilo rate
   limit a prázdná odpověď se zacachovala. Snímek tenhle problém nemá.
2. **Fanel má něco, co v Freelu není** — mapování štítků na fáze, kategorie
   „na čem to stojí" a zásobník bolestí z prioritizační mapy. To se počítá,
   ne čte.

Definice fází a nálezy z prvního snímku (7. 9. 2026) jsou v second brainu
v `03 Jak pracujeme/zivotni-cyklus-poptavky.md`, sekce „Fanel: štítky složené
do fází".
