# Skilly pro Claude Code

Skilly jsou hotové, opakovaně použitelné postupy, které **Claude Code umí sám
spustit**, když narazí na odpovídající situaci. Každý skill žije ve vlastní
složce a má soubor `SKILL.md` s hlavičkou (`name`, `description`) a návodem.

## Dostupné skilly

| Skill | K čemu slouží | Kdy se spustí |
|-------|---------------|---------------|
| [`freelo-projekt-z-prepisu`](freelo-projekt-z-prepisu/SKILL.md) | Z přepisu callu (porady, schůzky) postaví projekt ve Freelu — projekt, to-do listy, úkoly a podúkoly. Určuje, jak projekt strukturovat, pojmenovat a věrně zachytit realitu z callu. | Když zmíníš přepis/zápis z hovoru nebo řekneš „založ z toho projekt ve Freelu", „vytvoř to-do listy z callu" apod. |
| [`freelo-rozpracovat-ukol-z-prepisu`](freelo-rozpracovat-ukol-z-prepisu/SKILL.md) | Vezme **jeden existující úkol** ve Freelu a z přepisu callu (+ nahrávky z Teams) k němu dopracuje podúkoly, výjimečně checklisty — kompletní cestu k cíli. Nezakládá nový projekt ani nové úkoly, pracuje uvnitř jednoho úkolu. | Když řekneš „dopracuj tenhle úkol", „doplň podúkoly k úkolu z callu", „rozpracuj úkol podle přepisu", „naplánuj kroky k tomuhle úkolu" apod. |

## Jak skilly nainstalovat do Claude Code

Skill musí být tam, kde ho Claude Code hledá. Máš dvě možnosti:

- **Osobní** (dostupný všude u tebe): `~/.claude/skills/<nazev>/SKILL.md`
- **Projektový** (jen v daném projektu): `.claude/skills/<nazev>/SKILL.md`

> ⚠️ **Pozor na zanoření.** Soubor `SKILL.md` musí ležet **přímo** ve složce
> skillu — `~/.claude/skills/freelo-projekt-z-prepisu/SKILL.md`. Když ho
> omylem zanoříš o úroveň hloub, Claude skill nenajde.

Nejjednodušší je použít skript [`install.sh`](../install.sh) z kořene repa —
projde tuhle složku a všechny skilly nasype do `~/.claude/skills/`:

```bash
bash install.sh
```

**Po instalaci restartuj session Claude Code**, aby se nové skilly načetly.
