@echo off
REM Tydenni beh: nove nahravky schuzek -> prepisy -> report do second brainu.
REM Spousti to naplanovana uloha "Second brain - prepisy nahravek".
REM Log: %LOCALAPPDATA%\nahravky-sync.log

set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
set SKRIPT=%~dp0nahravky-sync.py
set LOG=%LOCALAPPDATA%\nahravky-sync.log
set PYTHONIOENCODING=utf-8

echo. >> "%LOG%"
echo ===== %DATE% %TIME% ===== >> "%LOG%"

if not exist "%PY%" (
  echo CHYBA: nenalezen python na %PY% >> "%LOG%"
  exit /b 1
)

REM --limit 3: nejvys tri prepisy za beh, aby jeden beh netrval hodiny.
"%PY%" "%SKRIPT%" --prepis --limit 3 >> "%LOG%" 2>&1

echo (konec, exit=%ERRORLEVEL%) >> "%LOG%"
exit /b %ERRORLEVEL%
