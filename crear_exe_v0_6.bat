@echo off
cd /d "%~dp0"
if not exist ".venv\Scripts\python.exe" (
    echo No se encontro .venv\Scripts\python.exe
    echo Copia estos archivos en tu carpeta principal MusicDesk junto a .venv
    pause
    exit /b 1
)
".venv\Scripts\python.exe" -m pip show pyinstaller >nul 2>&1
if errorlevel 1 (
    echo Instalando PyInstaller dentro de .venv...
    ".venv\Scripts\python.exe" -m pip install pyinstaller
    if errorlevel 1 (
        echo La instalacion de PyInstaller fallo.
        pause
        exit /b 1
    )
)
".venv\Scripts\python.exe" compilar_v0_6.py
pause
