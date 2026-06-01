#!/usr/bin/env bash
#
# install.sh — nainstaluje skilly z tohoto repa do Claude Code.
#
# Co skript dělá:
#   1. Projde složku skills/ a najde každý skill (složku se souborem SKILL.md).
#   2. Nasype ho do ~/.claude/skills/ — buď kopií, nebo symlinkem.
#   3. Pokud složka ~/.claude/skills/ neexistuje, vytvoří ji.
#
# Použití:
#   bash install.sh            # zkopíruje skilly (výchozí)
#   bash install.sh --symlink  # vytvoří symlinky (po `git pull` máš rovnou aktuální verzi)
#
# Po instalaci RESTARTUJ session Claude Code, ať se skilly načtou.

set -euo pipefail

# Složka, kam Claude Code ukládá osobní skilly
CILOVA_SLOZKA="$HOME/.claude/skills"

# Složka se skilly v tomto repu (relativně ke skriptu)
ZDROJ="$(cd "$(dirname "$0")" && pwd)/skills"

# Režim: kopie (výchozí) nebo symlink
REZIM="kopie"
if [[ "${1:-}" == "--symlink" ]]; then
  REZIM="symlink"
fi

# Cílová složka nemusí existovat — vytvoříme ji
mkdir -p "$CILOVA_SLOZKA"

echo "Instaluji skilly do: $CILOVA_SLOZKA  (režim: $REZIM)"

# Projdeme každou složku se SKILL.md
for skill_md in "$ZDROJ"/*/SKILL.md; do
  [[ -e "$skill_md" ]] || { echo "Žádné skilly k instalaci."; exit 0; }

  skill_dir="$(dirname "$skill_md")"
  nazev="$(basename "$skill_dir")"
  cil="$CILOVA_SLOZKA/$nazev"

  # Starou verzi odstraníme, ať je instalace čistá
  rm -rf "$cil"

  if [[ "$REZIM" == "symlink" ]]; then
    ln -s "$skill_dir" "$cil"
    echo "  ✓ $nazev (symlink)"
  else
    cp -r "$skill_dir" "$cil"
    echo "  ✓ $nazev (kopie)"
  fi
done

echo "Hotovo. Restartuj session Claude Code, ať se skilly načtou."
