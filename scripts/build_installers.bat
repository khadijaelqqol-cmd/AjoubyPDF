@echo off
REM ============================================================
REM  Ajouby PDF - compile both installers with Inno Setup 6
REM  Output: dist\installers\AjoubyPDF_Setup_win10.exe
REM          dist\installers\AjoubyPDF_Setup_win7.exe
REM  Requires both application folders in dist\ to exist.
REM ============================================================
setlocal
cd /d "%~dp0.."

set "ISCC=C:\InnoSetup6\ISCC.exe"
if not exist "%ISCC%" set "ISCC=ISCC.exe"

if not exist "dist\AjoubyPDF_win10\AjoubyPDF.exe" (
  echo Missing dist\AjoubyPDF_win10 - run scripts\build_win10.bat first.
  exit /b 1
)
if not exist "dist\AjoubyPDF_win7\AjoubyPDF_win7.exe" (
  echo Missing dist\AjoubyPDF_win7 - run scripts\build_win7.bat first.
  exit /b 1
)

echo [1/2] Compiling the Windows 10/11 installer...
"%ISCC%" "installer\installer_win10.iss"
if errorlevel 1 exit /b 1

echo [2/2] Compiling the Windows 7/8 installer...
"%ISCC%" "installer\installer_win7.iss"
if errorlevel 1 exit /b 1

echo.
echo Done: dist\installers
exit /b 0
