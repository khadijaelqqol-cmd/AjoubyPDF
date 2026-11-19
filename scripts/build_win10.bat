@echo off
REM ============================================================
REM  Ajouby PDF - build the Windows 10/11 application folder
REM  Output: dist\AjoubyPDF_win10\AjoubyPDF.exe
REM  Requirements: Python 3.10+ with requirements.txt installed
REM ============================================================
setlocal
cd /d "%~dp0.."

set "PY=python"
set "STAGE=dist\_new_win10"
set "FINAL=dist\AjoubyPDF_win10"
set "OLD=dist\_old_win10"

echo [1/2] Running PyInstaller...
%PY% -m PyInstaller --noconfirm --clean --windowed ^
  --name AjoubyPDF ^
  --icon "assets\ajouby.ico" ^
  --add-data "assets\ajouby.ico;assets" ^
  --add-data "assets\ajouby.png;assets" ^
  --hidden-import pymupdf --hidden-import docx --hidden-import openpyxl ^
  --distpath "%STAGE%" --workpath "build" ^
  main.py
if errorlevel 1 goto :failed
if not exist "%STAGE%\AjoubyPDF\AjoubyPDF.exe" goto :failed

echo [2/2] Installing the new build...
if exist "%OLD%" rmdir /s /q "%OLD%"
if exist "%FINAL%" move "%FINAL%" "%OLD%" >nul
move "%STAGE%\AjoubyPDF" "%FINAL%" >nul
if not exist "%FINAL%\AjoubyPDF.exe" goto :restore
rmdir /s /q "%OLD%" 2>nul
rmdir "%STAGE%" 2>nul
echo.
echo Built: %FINAL%\AjoubyPDF.exe
exit /b 0

:restore
echo Build failed while installing the new files.
if exist "%OLD%" move "%OLD%" "%FINAL%" >nul
exit /b 1

:failed
echo Build failed.
exit /b 1
