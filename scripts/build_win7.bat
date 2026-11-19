@echo off
REM ============================================================
REM  Ajouby PDF - build the Windows 7/8 application folder
REM  Output: dist\AjoubyPDF_win7\AjoubyPDF_win7.exe
REM  Requirements: Python 3.8 64-bit + requirements-win7.txt
REM  Uses Python38\python.exe when present, otherwise py -3.8.
REM ============================================================
setlocal
cd /d "%~dp0.."

set "PY=Python38\python.exe"
if not exist "%PY%" set "PY=py -3.8"
set "STAGE=dist\_new_win7"
set "FINAL=dist\AjoubyPDF_win7"
set "OLD=dist\_old_win7"

echo [1/2] Running PyInstaller with Python 3.8...
%PY% -m PyInstaller --noconfirm --clean --windowed ^
  --name AjoubyPDF_win7 ^
  --icon "assets\ajouby.ico" ^
  --add-data "assets\ajouby.ico;assets" ^
  --add-data "assets\ajouby.png;assets" ^
  --hidden-import fitz --hidden-import pymupdf ^
  --hidden-import docx --hidden-import openpyxl ^
  --distpath "%STAGE%" --workpath "build" ^
  main.py
if errorlevel 1 goto :failed
if not exist "%STAGE%\AjoubyPDF_win7\AjoubyPDF_win7.exe" goto :failed

echo [2/2] Installing the new build...
if exist "%OLD%" rmdir /s /q "%OLD%"
if exist "%FINAL%" move "%FINAL%" "%OLD%" >nul
move "%STAGE%\AjoubyPDF_win7" "%FINAL%" >nul
if not exist "%FINAL%\AjoubyPDF_win7.exe" goto :restore
rmdir /s /q "%OLD%" 2>nul
rmdir "%STAGE%" 2>nul
echo.
echo Built: %FINAL%\AjoubyPDF_win7.exe
exit /b 0

:restore
echo Build failed while installing the new files.
if exist "%OLD%" move "%OLD%" "%FINAL%" >nul
exit /b 1

:failed
echo Build failed.
exit /b 1
