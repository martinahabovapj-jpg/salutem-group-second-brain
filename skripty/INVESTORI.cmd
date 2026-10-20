@echo off
REM ============================================================
REM  Hledani na INVESTORSKE strane - do listu "6 Role Investor".
REM  Family office, wealth management, spravci rodinneho majetku.
REM
REM  Jina otazka nez refresh.cmd a OBJEVY.cmd. Ty se ptaji, kdo
REM  PUJCUJE z vlastni bilance. Tohle hleda toho, kdo INVESTUJE.
REM  Jeden subjekt muze byt oboji - listy 1 a 2 jsou spolecne,
REM  list 3 nese roli poskytovatele, list 6 roli investora.
REM
REM  POZOR: nejde to pres NACE. Family office nema vlastni kod a
REM  v rejstriku je k nerozeznani od bezne s.r.o. Hleda se podle
REM  JMEN ze seznamu v konfiguraci (sekce objevy_investor) - ARES
REM  k jmenu dohleda cely firemni trs a teprve web s citaci
REM  rozhodne. Kdyz mas nove jmeno, pridej ho do toho seznamu.
REM
REM  Nic nezapisuje. Pripravi slozku k-posouzeni-investor.
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
echo   Hledam kandidaty na investorskou stranu...
echo.

python financovani-objevy.py --investor
if errorlevel 1 goto chyba

echo.
echo   Hotovo. Seznam kandidatu je ve slozce k-posouzeni-investor.
echo   Posoudit je musi clovek nebo Claude - shoda jmena sama o sobe
echo   nic neznamena, v davce jsou i spolky a cestovky.
echo.
pause
exit /b 0

:chyba
echo.
echo   HLEDANI SKONCILO CHYBOU - viz vypis vyse.
echo.
pause
exit /b 1
