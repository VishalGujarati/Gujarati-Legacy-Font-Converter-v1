@echo off
setlocal
cd /d "%~dp0.."

where py >nul 2>nul
if errorlevel 1 (
  echo Python launcher was not found. Install Python 3.8 x64 first.
  exit /b 1
)

py -3.8 -m venv .venv-win38
if errorlevel 1 exit /b 1
call .venv-win38\Scripts\activate.bat
python -m pip install --upgrade "pip<24.1" "setuptools<70" wheel
python -m pip install "pyinstaller==5.13.2"
python -m PyInstaller --clean --noconfirm build\GujaratiLegacyFontConverter.spec
if errorlevel 1 exit /b 1

echo.
echo EXE build complete:
echo dist\GujaratiLegacyFontConverter\GujaratiLegacyFontConverter.exe
exit /b 0
