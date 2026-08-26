@echo off
REM ============================================================
REM  Zapise zmeny do master sesitu.
REM  Spoustej az potom, co refresh.cmd ukazal, co se zmenilo.
REM
REM  Pred zapisem si skript sam udela zalohu sesitu do slozky zalohy\.
REM  Cokoli, co zapise automat, jde vratit jednim prikazem - viz ZACNI-TADY.md
REM ============================================================

chcp 65001 > nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 (
  echo.
  echo   Na tomhle pocitaci neni Python - viz hlaska v refresh.cmd
  echo.
  pause
  exit /b 1
)

echo.
echo   POZOR: tenhle krok ZAPISUJE do master sesitu.
echo   Musi byt zavreny v Excelu, jinak zapis neprojde.
echo.
set /p ODPOVED="   Pokracovat? (a/n): "
if /i not "%ODPOVED%"=="a" goto konec

python financovani-beh.py --zapis
if errorlevel 1 goto chyba

echo.
echo   Zapsano. Zaloha puvodniho sesitu je ve slozce zalohy\
echo.
pause
exit /b 0

:chyba
echo.
echo   ZAPIS SKONCIL CHYBOU - viz vypis vyse. Sesit zustal beze zmeny.
echo.
pause
exit /b 1

:konec
echo   Zruseno, nic se nezmenilo.
pause
exit /b 0
