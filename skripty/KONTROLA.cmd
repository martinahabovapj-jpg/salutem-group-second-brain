@echo off
REM ============================================================
REM  Spust tohle jako PRVNI VEC na novem pocitaci.
REM  Overi, jestli tady mesicni refresh vubec pobezi.
REM
REM  Soubor je zamerne cele v ASCII - batch cte soubor v OEM kodovani
REM  a cestina by se v nem rozsypala. Ceske texty vypisuje python.
REM ============================================================

chcp 65001 > nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 goto nenipython

echo.
echo   Doinstaluji knihovny, ktere beh potrebuje (nepotrebuje prava spravce)...
python -m pip install --quiet --disable-pip-version-check openpyxl certifi

python kontrola-prostredi.py
set VYSLEDEK=%errorlevel%

echo.
pause
exit /b %VYSLEDEK%

:nenipython
echo.
echo   Na tomhle pocitaci neni nainstalovany Python - bez nej se nic nespusti.
echo.
echo   Instaluje se z python.org, volba "Install for me only" (nepotrebuje
echo   pravo spravce). Pri instalaci zaskrtnout "Add python.exe to PATH"
echo   a po instalaci zavrit a znovu otevrit toto okno.
echo.
echo   Kdyz si nevis rady, ozvi se Martine Habove.
echo.
pause
exit /b 1
