# مجلد الإصدار / Release assets

هذا المجلد جاهز لرفع البرنامج إلى GitHub. يحتوي على:

- `installers/` — نسخ ملفات التثبيت (محلية، غير مرفوعة إلى Git).
- `SHA256SUMS.txt` — بصمات SHA-256 للتحقق من سلامة الملفات.

---

## لماذا لا تُرفع ملفات EXE إلى Git؟

- المستودع يجب أن يبقى خفيفاً وسريع التنزيل.
- GitHub يعطي تحذيراً للملفات التي تتجاوز **50 MiB**، ويمنع الملفات التي تتجاوز **100 MiB**.
- ملف تثبيت ويندوز 10/11 حجمه نحو **96.8 MiB (101.5 MB)**، أي قريب من الحد.
- الطريقة القياسية هي إرفاق الملفات بصفحة **Releases**، وهي أسهل للزوار أيضاً.

---

## طريقة النشر على GitHub

### رفع المشروع أول مرة

من مجلد المشروع:

```bat
git init
git add .
git commit -m "Ajouby PDF 1.2.0"
git branch -M main
git remote add origin https://github.com/USERNAME/REPO.git
git push -u origin main
```

ملف `.gitignore` يستثني تلقائياً:

- `build/` و`dist/` و`Python38/` ومجلدات `tmp*`.
- ملفات التثبيت `release/installers/*.exe`.

لذلك لن يدخل إلى المستودع سوى الكود والتوثيق والصور. إذا استخدمت **GitHub Desktop**، أضف المجلد كمستودع محلي ثم ارفع التغييرات؛ سيحترم `.gitignore` أيضاً.

**بدون Git (رفع من موقع GitHub):**

```bat
python scripts\make_source_zip.py
```

1. فك ضغط `dist\AjoubyPDF-1.2.0-source.zip`.
2. افتح المستودع ← **Add file** ← **Upload files**.
3. اسحب محتويات مجلد `AjoubyPDF-1.2.0` (وليس المجلد نفسه إن أردت أن تكون الملفات في الجذر).
4. اكتب رسالة الحفظ واضغط **Commit changes**.

الأرشيف لا يحتوي على `build/` أو `dist/` أو `Python38/` أو ملفات EXE، وحجمه أقل من 1 MB.

### إنشاء الإصدار وإرفاق الملفات

1. افتح المستودع على GitHub.
2. اضغط **Releases** في الشريط الجانبي، ثم **Draft a new release**.
3. املأ:
   - **Tag**: `v1.2.0`
   - **Release title**: `Ajouby PDF 1.2.0`
   - **Description**: انسخ محتوى `SHA256SUMS.txt` وأضف سطراً تعريفياً:
     ```
     تحميل اجوبي PDF 1.2.0 — Windows 10/11 و Windows 7/8 (64-bit)
     ```
4. اسحب الملفين من `release/installers/` إلى خانة **Attach binaries**:
   - `AjoubyPDF_Setup_win10.exe`
   - `AjoubyPDF_Setup_win7.exe`
5. اضغط **Publish release**.

بعد النشر ستعمل روابط README تلقائياً:
`../../releases/latest` ← صفحة أحدث إصدار.

### باستخدام GitHub CLI (اختياري)

```bat
gh release create v1.2.0 ^
  release\installers\AjoubyPDF_Setup_win10.exe ^
  release\installers\AjoubyPDF_Setup_win7.exe ^
  --title "Ajouby PDF 1.2.0" ^
  --notes-file release\SHA256SUMS.txt
```

---

## تحديث الإصدار

بعد بناء نسخة جديدة:

```bat
scripts\build_win10.bat
scripts\build_win7.bat
scripts\build_installers.bat
python scripts\package_release.py
```

ثم أنشئ إصداراً جديداً (مثلاً `v1.2.1`) وأرفق الملفين الجديدين. لا تعِد استخدام وسم إصدار قديم؛ أنشئ وسمًا جديدًا حتى يبقى السجل واضحاً.

---

## التحقق من الملفات

```powershell
Get-FileHash .\AjoubyPDF_Setup_win10.exe -Algorithm SHA256
Get-FileHash .\AjoubyPDF_Setup_win7.exe -Algorithm SHA256
```

قارن الناتج مع `SHA256SUMS.txt`.

---

## بديل: Git LFS

إذا أردت وضع الملفات داخل المستودع نفسه بدلاً من Releases، استخدم Git LFS:

```bat
git lfs install
git lfs track "release/installers/*.exe"
git add .gitattributes
```

ثم أزل سطر الاستثناء من `.gitignore`. لكن **Releases أنسب للزوار** لأنهم يستطيعون التنزيل بنقرة واحدة دون تنزيل المستودع كاملاً.
