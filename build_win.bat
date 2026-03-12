@echo off
REM ----------------------------------------------------------
REM Build ChatBot.exe for Windows
REM Usage:  build_win.bat
REM ----------------------------------------------------------

echo Building ChatBot for Windows...
echo ---------------------------------

REM Activate venv (create if missing)
if not exist "venv" (
    echo Creating virtual environment...
    python -m venv venv
)
call venv\Scripts\activate.bat

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt
pip install pyinstaller

REM Clean previous builds
if exist "build" rmdir /s /q build
if exist "dist" rmdir /s /q dist

REM Build with PyInstaller
echo Running PyInstaller...
pyinstaller build_windows.spec --noconfirm

REM Copy config.json next to the .exe
copy config.json dist\config.json >nul 2>&1

echo.
echo ---------------------------------
echo Build complete!
echo.
echo EXE location:
echo    dist\ChatBot.exe
echo.
echo To run:
echo    dist\ChatBot.exe
echo.
echo To distribute:
echo    Share the dist\ChatBot.exe and dist\config.json together
echo ---------------------------------
pause
