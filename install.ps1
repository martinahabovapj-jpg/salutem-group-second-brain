# install.ps1 — nainstaluje skilly z tohoto repa do Claude Code (Windows).
#
# Proc existuje: install.sh potrebuje bash, ktery na Windows neni na PATH
# (Git for Windows ho ma schovany ve svem adresari). Tenhle skript dela totez
# v PowerShellu, aby na Windows stacilo:
#
#     powershell -ExecutionPolicy Bypass -File install.ps1
#
# Volby:
#     -Symlink    misto kopie vytvori symlinky (po `git pull` mas rovnou
#                 aktualni verzi; vyzaduje spusteni jako administrator
#                 nebo zapnuty Developer Mode)
#
# Po instalaci RESTARTUJ session Claude Code, at se skilly nactou.

param([switch]$Symlink)

$ErrorActionPreference = "Stop"

$cilova = Join-Path $env:USERPROFILE ".claude\skills"
$zdroj  = Join-Path $PSScriptRoot "skills"

if (-not (Test-Path $zdroj)) {
    Write-Host "CHYBA: nenalezena slozka $zdroj" -ForegroundColor Red
    exit 1
}
if (-not (Test-Path $cilova)) {
    New-Item -ItemType Directory -Path $cilova -Force | Out-Null
}

# PowerShell 5.1 neumi if jako vyraz, proto klasicky if/else
if ($Symlink) { $rezim = "symlink" } else { $rezim = "kopie" }
Write-Host "Instaluji skilly do: $cilova  (rezim: $rezim)"

$pocet = 0
Get-ChildItem $zdroj -Directory | ForEach-Object {
    $skill = $_
    $manifest = Join-Path $skill.FullName "SKILL.md"
    if (-not (Test-Path $manifest)) {
        Write-Host "  - $($skill.Name) preskoceno (chybi SKILL.md)" -ForegroundColor DarkGray
        return
    }

    $cil = Join-Path $cilova $skill.Name
    if (Test-Path $cil) { Remove-Item $cil -Recurse -Force }

    if ($Symlink) {
        New-Item -ItemType SymbolicLink -Path $cil -Target $skill.FullName | Out-Null
    } else {
        Copy-Item $skill.FullName $cil -Recurse -Force
    }
    Write-Host "  OK $($skill.Name) ($rezim)" -ForegroundColor Green
    $pocet++
}

Write-Host ""
Write-Host "Hotovo — nainstalovano $pocet skillu. Restartuj session Claude Code."

# Kontrola na caste zakopnuti: SKILL.md musi lezet PRIMO ve slozce skillu.
Get-ChildItem $cilova -Directory | ForEach-Object {
    if (-not (Test-Path (Join-Path $_.FullName "SKILL.md"))) {
        Write-Host "POZOR: $($_.Name) nema SKILL.md primo ve slozce — Claude ho nenajde." -ForegroundColor Yellow
    }
}

