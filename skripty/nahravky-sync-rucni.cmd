@echo off
REM Rucni beh bez limitu: prepise VSECHNY cekajici nahravky se zvukem najednou.
REM Spousti se rucne (nebo z Claude Code), kdyz automat nestihl nebo ho nekdo zabil.
REM Log: %LOCALAPPDATA%\nahravky-sync.log

set PY=%LOCALAPPDATA%\Programs\Python\Python312\python.exe
set SKRIPT=%~dp0nahravky-sync.py
set LOG=%LOCALAPPDATA%\nahravky-sync.log
set PYTHONIOENCODING=utf-8

echo. >> "%LOG%"
echo ===== %DATE% %TIME% (rucni beh, bez limitu) ===== >> "%LOG%"

if not exist "%PY%" (
  echo CHYBA: nenalezen python na %PY% >> "%LOG%"
  exit /b 1
)

REM Bez limitu; -u = nebufferovany vystup. Dalsi parametry se predaji skriptu (napr. --jen Treasury).
"%PY%" -u "%SKRIPT%" --prepis %* >> "%LOG%" 2>&1

echo (konec, exit=%ERRORLEVEL%) >> "%LOG%"
exit /b %ERRORLEVEL%
