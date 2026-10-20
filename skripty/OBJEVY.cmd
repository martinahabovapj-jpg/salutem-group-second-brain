@echo off
REM ============================================================
REM  Hledani novych subjektu, ktere na trhu pribyly.
REM  Jina uloha nez refresh.cmd: ten se pta znamych subjektu,
REM  jestli se u nich neco zmenilo. Tohle hleda ty, o kterych nevime.
REM
REM  Nic nezapisuje. Pripravi slozku k-posouzeni, ve ktere je seznam
REM  kandidatu - ty pak posoudi Claude Code (skill financovani-mesicni-beh).
REM
REM  Soubor je zamerne cele v ASCII, ceske texty vypisuje python.
REM ============================================================

chcp 65001 > nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 (
  echo.
  echo   Na tomhle pocitaci neni Python - viz hlaska v KONTROLA.cmd
  echo.
  pause
  exit /b 1
)

echo.
echo   Hledam nove subjekty v obchodnim rejstriku...
echo   Chvili to potrva, prochazi se cely rejstrik po kombinacich.
echo.

python financovani-objevy.py
if errorlevel 1 goto chyba

echo.
echo   Hotovo. Seznam kandidatu je ve slozce k-posouzeni.
echo   Posoudit je musi clovek nebo Claude - registr sam nepozna,
echo   jestli subjekt pujcuje tretim stranam, nebo jen uvnitr skupiny.
echo.
pause
exit /b 0

:chyba
echo.
echo   HLEDANI SKONCILO CHYBOU - viz vypis vyse.
echo.
pause
exit /b 1
