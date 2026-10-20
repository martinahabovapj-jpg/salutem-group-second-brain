@echo off
REM ============================================================
REM  Kontrola proti seznamu investicnich fondu CNB.
REM
REM  Treti zdroj vedle refresh.cmd (znami) a OBJEVY.cmd (novi
REM  z obchodniho rejstriku). Tenhle se pta REGULATORA.
REM
REM  CNB u kazdeho fondu vede KATEGORII podle skutecne investicni
REM  strategie - vcetne kategorie "uverovy". To ARES neumi: tam
REM  maji vsechny fondy tyz kod 64310 a nerozlisi se nic.
REM
REM  Vypise, ktere uverove fondy v databazi CHYBI. V cele CR jich
REM  je radove deset, takze je to seznam, ktery jde projit cely.
REM
REM  Nic nezapisuje. Pripravi slozku k-posouzeni-cnb.
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
echo   Stahuji seznam investicnich fondu z CNB a porovnavam s databazi...
echo.

python financovani-cnb.py --kandidati
if errorlevel 1 goto chyba

echo.
echo   Hotovo. Chybejici fondy jsou ve slozce k-posouzeni-cnb.
echo   Kategorie od CNB je silny doklad, ale porad to musi posoudit
echo   clovek - fond, ktery uveruje jen vlastni skupinu, je pro CNB
echo   taky "uverovy", ale do databaze nepatri.
echo.
pause
exit /b 0

:chyba
echo.
echo   KONTROLA SKONCILA CHYBOU - viz vypis vyse.
echo.
pause
exit /b 1
