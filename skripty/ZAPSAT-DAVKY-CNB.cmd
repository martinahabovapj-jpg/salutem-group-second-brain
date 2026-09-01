@echo off
REM ============================================================
REM  Zapise posouzene davky investoru ze seznamu CNB do masteru.
REM
REM  PROC TENHLE SOUBOR EXISTUJE
REM  Davky 06 az 13 (nemovitostni fondy ze seznamu CNB, 95 skupin)
REM  byly posouzeny 1. 9. 2026, ale disk O: byl v tu chvili odpojeny,
REM  takze se nedaly zapsat. Tohle je dopise, az disk pobezi.
REM
REM  Davky 06 a 07 uz zapsane JSOU - v seznamu nejsou schvalne.
REM
REM  CO TO UDELA
REM  Pro kazdou davku spusti financovani-zapis-investoru.py --zapis.
REM  Skript sam parvuje na uz existujici subjekty podle ICO, domeny
REM  a nazvu, takze opakovane spusteni nic nezduplikuje - jen znovu
REM  prepise tytez hodnoty. Verdikt "nevim" jde do listu 8,
REM  "zamitnout" do listu 7.
REM
REM  Master sesit musi byt ZAVRENY v Excelu, jinak zapis neprojde.
REM
REM  Soubor je zamerne cele v ASCII, ceske texty vypisuje python.
REM ============================================================

cd /d "%~dp0"

echo.
echo   Zapisuji davky 08 az 13 do master sesitu.
echo   Master sesit musi byt zavreny v Excelu.
echo.
pause

for %%D in (08 09 10 11 12 13) do (
    echo.
    echo   ---- davka %%D ----
    python financovani-zapis-investoru.py davka-cnb-investor-%%D.json --zapis
    if errorlevel 1 goto chyba
)

echo.
echo   HOTOVO. Vsech sest davek zapsano.
echo   Novi investori jsou v listu 6, zamitnuti v listu 7,
echo   nerozhodnuti v listu 8.
echo.
pause
exit /b 0

:chyba
echo.
echo   ZAPIS SKONCIL CHYBOU - viz vypis vyse.
echo   Nejcastejsi duvody: disk O: neni pripojeny, nebo je
echo   master sesit otevreny v Excelu.
echo.
pause
exit /b 1
