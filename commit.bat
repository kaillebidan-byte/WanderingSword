@echo off
chcp 65001 >nul
cd /d "%~dp0"
set "MSG=%~1"
if "%MSG%"=="" set "MSG=update %DATE% %TIME%"
git add -A
git commit -m "%MSG%"
echo.
echo ==== recent history ====
git log --oneline -5
echo.
pause
