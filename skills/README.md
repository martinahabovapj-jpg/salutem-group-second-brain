# Skilly pro Claude Code

Skilly jsou hotové, opakovaně použitelné postupy, které **Claude Code umí sám
spustit**, když narazí na odpovídající situaci. Každý skill žije ve vlastní
složce a má soubor `SKILL.md` s hlavičkou (`name`, `description`) a návodem.

## Dostupné skilly

| Skill | K čemu slouží | Kdy se spustí |
|-------|---------------|---------------|
| [`freelo-projekt-z-prepisu`](freelo-projekt-z-prepisu/SKILL.md) | Z přepisu callu (porady, schůzky) postaví projekt ve Freelu — projekt, to-do listy, úkoly a podúkoly. Určuje, jak projekt strukturovat, pojmenovat a věrně zachytit realitu z callu. | Když zmíníš přepis/zápis z hovoru nebo řekneš „založ z toho projekt ve Freelu", „vytvoř to-do listy z callu" apod. |
| [`freelo-rozpracovat-ukol-z-prepisu`](freelo-rozpracovat-ukol-z-prepisu/SKILL.md) | Vezme **jeden existující úkol** ve Freelu a rozpracuje ho na podúkoly (případně checklisty) podle přepisu callu. Nezakládá projekt ani nové úkoly — pracuje uvnitř jednoho konkrétního úkolu. | Když řekneš „dopracuj tenhle úkol", „doplň podúkoly k úkolu z callu", „rozpracuj úkol podle přepisu", „naplánuj kroky k tomuhle úkolu" apod. |
| [`sync-zdroju`](sync-zdroju/SKILL.md) | Pravidelné **dobírání nových zdrojů** do second brainu: zjistí, co v hlídaných složkách (Alfa, přepisy, podklady, SReal, IT Governance) přibylo od posledního syncu, roztřídí to na znalost × pracovní soubor × stav a řekne, kam se zapisuje, že je to vytěžené. Používá skript [`skripty/sync-zdroju.py`](../skripty/sync-zdroju.py). | Sám od sebe na začátku práce se second brainem a na konci session; nebo když řekneš „co je nového", „přibylo něco", „projdi Alfu", „doplň second brain". |
| [`prace-na-use-casu`](prace-na-use-casu/SKILL.md) | Určuje **pořadí úkonů** při práci na AI use casu: co všechno se musí přečíst (second brain, Freelo úkol včetně komentářů, governance, šablony, živý systém), než se cokoli navrhne — a co se musí zapsat, než se práce ukončí (handoff komentář do Freela + datovaný záznam do second brainu). | Když řekneš „pojďme stavět", „navrhni řešení", „pokračujeme na use casu", „co dneska s tím use casem", „rozpracuj zadání" apod. |
| `freelo-triage-poptavky` — **žije v repu `salutem-ai-adopce`, ne tady** (viz varování pod tabulkou) | Vezme **jednu nebo více poptávek** (use-casů na AI automatizaci) a provede každou celou kvalifikací podle operačního modelu produkční větve: checklist „patří to nám?", devět otázek, compliance brána, ROI výpočet, verdikt dráhy a analýza podílníků. Výstup je triage report u poptávky (+ souhrnná prioritizační tabulka u dávky). | Když řekneš „vyhodnoť tuhle poptávku", „projeď triage", „kvalifikuj požadavek", „patří to nám?", „spočítej business case", „projeď těchhle 5 poptávek", „srovnej požadavky podle priority" apod. |
| [`pain-point-datova-optika`](pain-point-datova-optika/SKILL.md) | Vezme **bolest popsanou uživatelem** (z rozhovoru, tabulky, požadavku) a projde ji šesti stejnými otázkami: najde slabé místo, stanoví diagnózu z pevného seznamu A1–A12, ověří třemi otázkami, jestli je to práce pro AI, a navrhne typ zásahu a předpoklady. Výstupem není řešení, ale rozbor — u dávky navíc seskupení podle příčiny a seznam rozhodnutí, která odblokují nejvíc bolestí. **Předchází triage:** tady se řeší „v čem je příčina", tam „jakou dráhou a za kolik". Návratnost ani dráhu nepočítá. | Když řekneš „co je tady vlastně problém", „projeď mi tenhle pain point", „je to case pro AI?", „zanalyzuj těchhle 20 bolestí z rozhovorů", „seskup mi to podle příčiny" — nebo jen vložíš přepis rozhovoru či tabulku pain pointů. |

> ⚠️ **`freelo-triage-poptavky` tady záměrně není. Nezakládej ho sem znovu.**
>
> Jeho domov je `salutem-ai-adopce/skills/freelo-triage-poptavky/` — tam leží
> vedle masterů v `docs/`, ze kterých za běhu čte pravidla, a vedle
> `scripts/business_case.py`, který je jediný výpočetní engine služby.
>
> Doložený omyl (15. 7. – 3. 9. 2026): kopie skillu se sem odštěpila
> **15. 7. v 15:30** a do masteru pak přišel v 15:46 nový format reportu
> a v 16:06 navrhování štítku. Kopie se už neaktualizovala, ale **byla to
> ona, co se instalovala** — takže triage sedm týdnů běžela bez navrhování
> štítku a bez plnění polí šablony use casu, i když to schválený
> `zivotni-cyklus-poptavky` vyžaduje. Naposledy takhle proběhla 2. 9. 2026.
> Opraveno 3. 9. 2026 smazáním téhle kopie.
>
> **Proč to `install` neodhalil:** kontroluje chybějící `SKILL.md`, ne to,
> jestli obsah odpovídá masteru. Kopie navíc vypadala novější, protože
> instalace přepsala datum souboru.
>
> Triage se instaluje z jeho vlastního repa:
>
> ```powershell
> Copy-Item -Recurse -Force $HOME\salutem-ai-adopce\salutem-ai-adopce\skills\freelo-triage-poptavky $HOME\.claude\skills\
> ```
>
> Ta dvojitá složka v cestě je opravdu tam — repo je vnořené o úroveň hloub
> (`salutem-ai-adopce\salutem-ai-adopce`), vedle rozbaleného zipu.

## Jak skilly nainstalovat do Claude Code

Skill musí být tam, kde ho Claude Code hledá. Máš dvě možnosti:

- **Osobní** (dostupný všude u tebe): `~/.claude/skills/<nazev>/SKILL.md`
- **Projektový** (jen v daném projektu): `.claude/skills/<nazev>/SKILL.md`

> ⚠️ **Pozor na zanoření.** Soubor `SKILL.md` musí ležet **přímo** ve složce
> skillu — `~/.claude/skills/freelo-projekt-z-prepisu/SKILL.md`. Když ho
> omylem zanoříš o úroveň hloub, Claude skill nenajde.

> ⚠️ **Nový skill = nová složka. Nikdy nepřepisuj obsah existující složky
> jiným skillem.** Název složky musí odpovídat poli `name` v `SKILL.md`.
>
> Doložený omyl (červen–srpen 2026): obsah nového skillu na rozpracování
> úkolu se vložil do složky `freelo-projekt-z-prepisu`. Tím **zmizel skill
> na zakládání projektu z přepisu**, složka přestala odpovídat svému
> `name:` a otevřený pull request se stejným obsahem zůstal dva měsíce
> viset. Opraveno 11. 8. 2026 — obsah se přesunul do vlastní složky
> a původní skill se vrátil z historie.
>
> **Kontrola, která to odchytí:** po každé změně projdi složky a porovnej
> název s polem `name`. `install.ps1` na konci hlásí chybějící `SKILL.md`,
> nesoulad názvu ale neodhalí.

Nejjednodušší je použít skript [`install.sh`](../install.sh) z kořene repa —
projde tuhle složku a všechny skilly nasype do `~/.claude/skills/`:

```bash
bash install.sh
```

**Na Windows** není `bash` na PATH (Git for Windows ho má schovaný ve svém
adresáři), takže použij PowerShellovou verzi:

```powershell
powershell -ExecutionPolicy Bypass -File install.ps1
```

Oba skripty dělají totéž. `-Symlink` (resp. `--symlink`) vytvoří místo kopií
symlinky — po `git pull` máš rovnou aktuální verzi.

**Po instalaci restartuj session Claude Code**, aby se nové skilly načetly.

> ⚠️ **Skill, který je jen na nemergnuté branch, `install` nenajde** — bere
> jen to, co je v tvém working tree. Když ho potřebuješ hned, dotáhni si ho
> bez přepínání branchí:
>
> ```
> git show origin/<branch>:skills/<nazev>/SKILL.md
> ```
