# Salutem Group — Second Brain

Tohle je **firemní „second brain"** — jedno sdílené místo pravdy (single
source of truth) pro celou firmu. Najdeš tu jak věci pro práci s umělou
inteligencí (Claude), tak běžnou firemní dokumentaci pro lidi.

## Proč to máme

Řešíme spoustu věcí napříč různými oblastmi a potřebujeme se v nich rychle
zorientovat. Nemáme dedikovaného projektového manažera — proto osvědčené
postupy zapisujeme do skillů a dokumentace. Díky tomu kvalita nestojí na
jednom člověku a každý si dokáže vybavit potřebný kontext.

## Z čeho se repo skládá

Repo má dvě vrstvy:

### 🤖 AI vrstva — pro práci s Claude

- **[`skills/`](skills/)** — skilly pro Claude Code (hotové postupy, které Claude umí spustit)
- **[`prompts/`](prompts/)** — znovupoužitelné prompty a šablony
- **[`kontext/`](kontext/)** — firemní kontext, který se přikládá Claude (slovník pojmů, o firmě, styl komunikace)

### 👥 Lidská vrstva — pro lidi

- **[`dokumentace/`](dokumentace/)** — procesy, onboarding a návody k nástrojům. Čteme ji bez ohledu na AI.

## Jak začít

1. **Naklonuj repo:**
   ```bash
   git clone https://github.com/martinahabovapj-jpg/salutem-group-second-brain.git
   ```
2. **Nainstaluj skilly do Claude Code** (zkopíruje je do `~/.claude/skills/`):
   ```bash
   bash install.sh
   ```
3. **Restartuj session Claude Code**, aby se nové skilly načetly.

## Jak přispívat

Než něco přidáš nebo změníš, koukni do [CONTRIBUTING.md](CONTRIBUTING.md).
Změny posíláme přes pull request, ať si je někdo přečte dřív, než se rozšíří
k celému týmu.
