@echo off
REM ============================================================
REM  Zapise zmeny do master sesitu. Dva kroky za sebou:
REM
REM   1) VYRIDI FRONTU - projde list "5 Navrhy zmen" a co je ve
REM      sloupci Schvalit oznacene jako "prijmout", zapise tam,
REM      kam to patri (listy 1-3). Co je "zamitnout", zapamatuje
REM      si natrvalo, aby to priste uz nenabizel.
REM
REM   2) SPUSTI KONTROLU a zapise, co nasla.
REM
REM  Spoustej az potom, co refresh.cmd ukazal, co se zmenilo,
REM  a co jsi v listu 5 rozhodl.
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

echo.
echo   [1/2] Vyrizuji frontu schvalenych navrhu...
echo.
python financovani-beh.py --aplikovat --zapis
if errorlevel 1 goto chyba

echo.
echo   [2/2] Spoustim kontrolu a zapisuji, co najde...
echo.
python financovani-beh.py --zapis
if errorlevel 1 goto chyba

echo.
echo   Zapsano. Zaloha puvodniho sesitu je ve slozce zalohy\
echo.
pause
exit /b 0

:chyba
echo.
echo   ZAPIS SKONCIL CHYBOU - viz vypis vyse.
echo   Zaloha sesitu pred zapisem je ve slozce zalohy\
echo.
pause
exit /b 1

:konec
echo   Zruseno, nic se nezmenilo.
pause
exit /b 0
