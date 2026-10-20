@echo off
REM ============================================================
REM  Mesicni refresh databaze poskytovatelu financovani.
REM  Dvojklik = kontrola. Nic se nezapise, jen se ukaze, co se zmenilo.
REM
REM  Soubor je zamerne cele v ASCII. Batch cte soubor v OEM kodovani
REM  a cestina v nem by se rozsypala na paskvil. Vsechny ceske texty
REM  vypisuje python, ktery je posle v UTF-8 (viz chcp a PYTHONIOENCODING).
REM ============================================================

chcp 65001 > nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 goto nenipython

echo.
echo   Kontroluji databazi poskytovatelu financovani...
echo   Chvili to potrva - obchazi se rejstriky a weby vsech subjektu.
echo.

python financovani-beh.py
if errorlevel 1 goto chyba

echo.
echo   Hotovo. Nic nebylo zapsano.
echo   Kdyz je vysledek v poradku, spust ZAPSAT.cmd
echo.
pause
exit /b 0

:chyba
echo.
echo   BEH SKONCIL CHYBOU - viz vypis vyse.
echo   Nejcastejsi pricina: sesit ma nekdo otevreny v Excelu. Zavri ho a zkus znovu.
echo.
pause
exit /b 1

:nenipython
echo.
echo   Na tomhle pocitaci neni nainstalovany Python - bez nej se kontrola spustit neda.
echo.
echo   Instaluje se z python.org, volba "Install for me only" (nepotrebuje
echo   pravo spravce). Pri instalaci zaskrtnout "Add python.exe to PATH".
echo   Potom jeste jednou v prikazovem radku:
echo.
echo       python -m pip install openpyxl certifi
echo.
echo   Kdyz si nevis rady, ozvi se Martine Habove.
echo.
pause
exit /b 1
