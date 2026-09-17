@echo off
setlocal
cd /d "%~dp0.."
if not exist "dist\GujaratiLegacyFontConverter\GujaratiLegacyFontConverter.exe" (
  echo Build the EXE first with build_windows.bat
  exit /b 1
)
where ISCC.exe >nul 2>nul
if errorlevel 1 (
  echo Inno Setup compiler ISCC.exe was not found.
  echo Install Inno Setup 6, then run this file again.
  exit /b 1
)
ISCC.exe build\installer.iss
if errorlevel 1 exit /b 1
echo Installer build complete. Check the Output folder.
