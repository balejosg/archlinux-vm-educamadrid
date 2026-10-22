@echo off
chcp 65001 >nul
title OpenCode v2 - EducaMadrid

echo ========================================================
echo   OpenCode v2 - Entorno Docente EducaMadrid
echo ========================================================
echo.
echo Conectando con la Maquina Virtual EducaMadrid...

:: Verificar si el ejecutable GUI portable esta presente
if exist "%~dp0OpenCode-EducaMadrid.exe" (
    start "" "%~dp0OpenCode-EducaMadrid.exe"
    exit /b 0
)

:: Busqueda automatica de Microsoft Edge
set "EDGE_EXE="
if exist "%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe" set "EDGE_EXE=%ProgramFiles(x86)%\Microsoft\Edge\Application\msedge.exe"
if not defined EDGE_EXE if exist "%ProgramFiles%\Microsoft\Edge\Application\msedge.exe" set "EDGE_EXE=%ProgramFiles%\Microsoft\Edge\Application\msedge.exe"
if not defined EDGE_EXE if exist "%LocalAppData%\Microsoft\Edge\Application\msedge.exe" set "EDGE_EXE=%LocalAppData%\Microsoft\Edge\Application\msedge.exe"

set "TARGET_URL=http://127.0.0.1:49374/?auth_token=educamadrid"
set "USER_DIR=%LocalAppData%\OpenCodeEducaMadrid\profile"

if defined EDGE_EXE (
    echo Iniciando interfaz de OpenCode en modo aplicacion dedicada...
    start "" "%EDGE_EXE%" --app="%TARGET_URL%" --user-data-dir="%USER_DIR%" --window-size=1400,900
) else (
    echo Abriendo OpenCode en tu navegador predeterminado...
    start "" "%TARGET_URL%"
)
