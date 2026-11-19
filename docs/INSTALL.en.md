# Ajouby PDF — Installation Guide

This guide walks through installing **Ajouby PDF 1.2.0** on Windows, including the language choices at the start of setup.

---

## Before you start

| Windows version | Requirements | Notes |
|---|---|---|
| Windows 10 / 11 | 64-bit | Full build |
| Windows 7 / 8 | 64-bit (Win7 needs SP1) | Requires [KB2999226](https://support.microsoft.com/help/2999226) (Universal C Runtime) |
| Windows XP | — | Not supported |

- The installers are not code-signed yet, so Windows **SmartScreen** may warn you.
- The Windows 10/11 installer is about **102 MB**; the Windows 7/8 installer is about **46 MB**.

---

## 1. Download

Open the repository's **Releases** page and download the build for your system:

- **Windows 10 / 11**: `AjoubyPDF_Setup_win10.exe`
- **Windows 7 / 8**: `AjoubyPDF_Setup_win7.exe`

Verify the download in PowerShell:

```powershell
Get-FileHash .\AjoubyPDF_Setup_win10.exe -Algorithm SHA256
```

Compare the value with [SHA256SUMS.txt](../release/SHA256SUMS.txt).

---

## 2. Choose the setup language

When you run the installer, a **Select Setup Language** dialog appears first:

1. Open the drop-down and choose **English** (or العربية).
2. Click **OK**.

This only controls the language of the setup wizard texts and buttons. You can choose Arabic even if Windows is in another language.

> If SmartScreen appears, click **More info** → **Run anyway**.

---

## 3. Choose the application language

The next page is **“Application language”** and lists all **19 languages**:

- Arabic, English, Français, Español, Deutsch, Italiano, Português, Türkçe, Русский, 中文, 日本語, 한국어, हिन्दी, Nederlands, Polski, Svenska, Ελληνικά, فارسی, Українська.
- The default follows the setup language, then the Windows UI language, then English.
- Your choice becomes the application UI language on first launch and is stored in `language.txt` inside the install folder.

You can change it later from the **Language** menu in the app, without reinstalling.

> **Note:** If you already have the app installed and changed its language inside the app, an upgrade keeps your choice unless you pick a different language on this page.

---

## 4. Finish the wizard

1. **Install folder**:
   - Per-machine install (admin rights): `C:\Program Files\AjoubyPDF`
   - Per-user install: `%LOCALAPPDATA%\Programs\AjoubyPDF`
2. **Optional tasks**:
   - Create a desktop shortcut.
   - Add Ajouby PDF to the PDF “Open with” menu (does not change your default reader).
   - Launch Ajouby PDF after setup.
3. Click **Install** and wait for the files to be copied.

---

## 5. First launch

- Open the app from the Start menu or the desktop shortcut.
- It starts in the language you chose during setup.
- The **Guide** button or **F1** opens the built-in user guide.
- Drag any PDF into the window, or use the **Open a file** card.

To change the language later: **Language** menu → pick a language. It applies immediately and is saved.

---

## Silent installation

For system administrators and mass deployment:

```bat
REM Arabic, current user, no interaction
AjoubyPDF_Setup_win10.exe /SILENT /CURRENTUSER /APPLANG=ar

REM English, all users (admin required)
AjoubyPDF_Setup_win10.exe /SILENT /APPLANG=en

REM Fully silent
AjoubyPDF_Setup_win10.exe /VERYSILENT /SUPPRESSMSGBOXES /NORESTART /APPLANG=ja
```

| Parameter | Meaning |
|---|---|
| `/SILENT` | No user interaction, with a progress bar |
| `/VERYSILENT` | No UI at all |
| `/CURRENTUSER` | Per-user install without admin rights |
| `/DIR="D:\Apps\AjoubyPDF"` | Custom install folder |
| `/LANG=arabic` or `/LANG=english` | Setup UI language |
| `/APPLANG=ar` | Application language (19 codes) |

`/APPLANG` codes: `ar, en, fr, es, de, it, pt, tr, ru, zh, ja, ko, hi, nl, pl, sv, el, fa, uk`.

---

## Upgrading

- Run the new installer over the old version; no need to uninstall first.
- Your settings (window geometry, sidebar, recent files, language) live in `HKCU\Software\Ajouby\Ajouby PDF` and are preserved.
- If you pick a new language on the installer page, the app switches to it. Otherwise your previous choice stays.

---

## Uninstalling

1. **Settings** → **Apps** → **Ajouby PDF** → **Uninstall**.
2. Or run `unins000.exe` from the install folder.

The uninstaller removes the program files, `language.txt`, and shortcuts. User settings stay in the registry on purpose (window geometry, recent files, language). To remove them completely:

```bat
reg delete "HKCU\Software\Ajouby\Ajouby PDF" /f
```

---

## Portable use

After installation you can copy the whole program folder to a USB drive and run `AjoubyPDF.exe` directly. Everything works, and settings are stored in the current Windows account. The `language.txt` file in the folder sets the first-run language.

---

## Troubleshooting

| Problem | Fix |
|---|---|
| SmartScreen warning | **More info** → **Run anyway** (the installer is not signed yet) |
| Antivirus deletes the file | Add the install folder to exclusions; false positives are common with PyInstaller |
| App does not start on Windows 7 | Check SP1, KB2999226, and that the build is 64-bit |
| Arabic letters show as boxes | Install an Arabic font such as Segoe UI or Tahoma |
| OCR does not work | Install [Tesseract](https://github.com/UB-Mannheim/tesseract/wiki) and add it to `PATH` |
| “Save failed” | Make sure the file is not open in another program and that you can write to its folder |

---

[Back to README](../README.en.md) · [User guide](USER_GUIDE.md)
