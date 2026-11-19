; ============================================================
;  اجوبي PDF - مثبّت ويندوز 7/8
;  Ajouby PDF - installer for Windows 7/8
;
;  Compile from the project root:
;    "C:\InnoSetup6\ISCC.exe" "installer\installer_win7.iss"
; ============================================================

#define ProjectRoot AddBackslash(SourcePath) + ".."

[Setup]
AppId={{DE803BB5-074B-445C-9631-7C10310ECAC1}
AppName=Ajouby PDF
AppVersion=1.2.0
AppVerName=Ajouby PDF 1.2.0
AppPublisher=Ajouby
DefaultDirName={autopf}\AjoubyPDF
DefaultGroupName=Ajouby PDF
UninstallDisplayName=Ajouby PDF (Windows 7/8)
UninstallDisplayIcon={app}\AjoubyPDF_win7.exe
SourceDir={#ProjectRoot}
OutputDir={#ProjectRoot}\dist\installers
OutputBaseFilename=AjoubyPDF_Setup_win7
SetupIconFile=assets\ajouby.ico
Compression=lzma2/max
SolidCompression=yes
WizardStyle=modern
DisableWelcomePage=yes
ShowLanguageDialog=yes
UsePreviousLanguage=no
ArchitecturesAllowed=x64compatible
ArchitecturesInstallIn64BitMode=x64compatible
ChangesAssociations=yes
CloseApplications=yes
MinVersion=6.1sp1
PrivilegesRequiredOverridesAllowed=commandline
VersionInfoVersion=1.2.0.0
VersionInfoCompany=Ajouby
VersionInfoDescription=Ajouby PDF Setup (Windows 7/8)
VersionInfoProductName=Ajouby PDF
VersionInfoProductVersion=1.2.0

[Languages]
Name: "english"; MessagesFile: "compiler:Default.isl"
Name: "arabic"; MessagesFile: "compiler:Languages\Arabic.isl"

[CustomMessages]
english.CreateDesktopIcon=Create a &desktop shortcut
arabic.CreateDesktopIcon=إنشاء اختصار على &سطح المكتب
english.AdditionalIcons=Additional icons:
arabic.AdditionalIcons=أيقونات إضافية:
english.PdfAssoc=PDF file association:
arabic.PdfAssoc=ربط ملفات PDF:
english.PdfOpenWith=Add Ajouby PDF to the "Open with" menu of PDF files (does not change your default reader)
arabic.PdfOpenWith=إضافة Ajouby PDF إلى قائمة «فتح باستخدام» لملفات PDF (دون تغيير القارئ الافتراضي)
english.LaunchApp=Launch Ajouby PDF
arabic.LaunchApp=تشغيل Ajouby PDF

[Tasks]
Name: "desktopicon"; Description: "{cm:CreateDesktopIcon}"; \
    GroupDescription: "{cm:AdditionalIcons}"
Name: "pdfopenwith"; Description: "{cm:PdfOpenWith}"; \
    GroupDescription: "{cm:PdfAssoc}"; \
    Flags: unchecked

[Files]
Source: "dist\AjoubyPDF_win7\*"; DestDir: "{app}"; \
    Flags: recursesubdirs ignoreversion createallsubdirs

[Icons]
Name: "{group}\Ajouby PDF"; Filename: "{app}\AjoubyPDF_win7.exe"
Name: "{group}\Uninstall Ajouby PDF"; Filename: "{uninstallexe}"
Name: "{autodesktop}\Ajouby PDF"; Filename: "{app}\AjoubyPDF_win7.exe"; \
    Tasks: desktopicon

[Registry]
Root: HKA; Subkey: "Software\Classes\Applications\AjoubyPDF_win7.exe\shell\open\command"; \
    ValueType: string; ValueData: """{app}\AjoubyPDF_win7.exe"" ""%1"""; \
    Tasks: pdfopenwith; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\Applications\AjoubyPDF_win7.exe\DefaultIcon"; \
    ValueType: string; ValueData: "{app}\AjoubyPDF_win7.exe,0"; \
    Tasks: pdfopenwith; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\AjoubyPDF.Document"; \
    ValueType: string; ValueData: "Ajouby PDF Document"; \
    Tasks: pdfopenwith; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\AjoubyPDF.Document\DefaultIcon"; \
    ValueType: string; ValueData: "{app}\AjoubyPDF_win7.exe,0"; \
    Tasks: pdfopenwith; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\AjoubyPDF.Document\shell\open\command"; \
    ValueType: string; ValueData: """{app}\AjoubyPDF_win7.exe"" ""%1"""; \
    Tasks: pdfopenwith; Flags: uninsdeletekey
Root: HKA; Subkey: "Software\Classes\.pdf\OpenWithProgids"; \
    ValueType: string; ValueName: "AjoubyPDF.Document"; ValueData: ""; \
    Tasks: pdfopenwith; Flags: uninsdeletevalue

[Run]
Filename: "{app}\AjoubyPDF_win7.exe"; Description: "{cm:LaunchApp}"; \
    Flags: nowait postinstall skipifsilent

#include "language_page.iss"
