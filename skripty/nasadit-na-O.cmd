@echo off
REM ============================================================
REM  Nasadi upravenou verzi behu z repa na disk O:.
REM  Spousti Martina Habova, ne kolega.
REM
REM  Kopiruje se JEN JEDNIM SMEREM: repo -> O:. Nikdy opacne.
REM  Cilovou cestu si odvodi python z financovani-beh.config.json,
REM  aby v tomhle souboru nemusela byt diakritika - batch ji cte
REM  v OEM kodovani a rozsypala by se.
REM ============================================================

chcp 65001 > nul
set PYTHONIOENCODING=utf-8
cd /d "%~dp0"

where python > nul 2>&1
if errorlevel 1 (
  echo.
  echo   Na tomhle pocitaci neni Python.
  echo.
  pause
  exit /b 1
)

python nasadit-na-O.py
pause
exit /b %errorlevel%
