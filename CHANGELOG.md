# سجل التغييرات / Changelog

## 1.2.0 — 2026-11-19

### العربية

**المثبّت واللغات**

- المثبّت يسأل عن اللغة عند البدء: نافذة لغة واجهة التثبيت (العربية/الإنجليزية)، ثم صفحة **لغة البرنامج** بكل اللغات الـ19.
- اختيار اللغة يُكتب في `{app}\language.txt` ويُقرأ عند أول تشغيل.
- عند ترقية البرنامج بلغة مختلفة تُطبّق اللغة الجديدة؛ وإلا يبقى اختيار المستخدم المحفوظ في البرنامج.
- معامل `/APPLANG=` للتثبيت الصامت، و`/LANG=` للغة واجهة التثبيت.
- إزالة `language.txt` تلقائياً عند إلغاء التثبيت.
- توحيد قائمة لغات المثبّت مع قائمة لغات البرنامج، واختبار آلي يمنع اختلافهما.

**الإصلاحات**

- إصلاح انهيار ويندوز 7 عند فتح ملف PDF (عمر كائن الصورة في `_pix_to_qimage`).
- إصلاح الرسم الحر: استبدال `add_freehand_annot` غير الموجودة بـ `add_ink_annot`.
- إصلاح اسم أداة التوقيع الذي كان يظهر كنص خام `tool_sign`.
- حفظ آمن: إذا فشل الحفظ لا يُغلق المستند، وتُعاد فتح النسخة الأصلية، مع إعادة توثيق الملفات المحمية بكلمة مرور.
- سؤال قبل فتح ملف جديد أو إغلاق البرنامج مع تغييرات غير محفوظة.
- إعادة حساب «ملاءمة العرض» بعد استقرار التخطيط، فلا تظهر أشرطة تمرير أفقية غير ضرورية.
- تنظيف أزرار القوائم عند تغيير اللغة (لا تراكم في الذاكرة)، وإغلاق كل ملفات PDF حتى عند حدوث خطأ.
- دعم الأرقام العربية/الفارسية في نطاقات التقسيم (`١-٣`).
- لون الصورة المصغّرة لم يعد يتغير عند تحديدها.

**الواجهة والأداء**

- شاشة بداية جديدة بأربع بطاقات كبيرة، وشريط أدوات يظهر تدريجياً حسب الحالة.
- صور مصغّرة كسولة (حد أقصى ~40 صورة محفوظة) وتُخفى عند ضيق النافذة.
- دليل استخدام داخل البرنامج (F1) بفهرس قابل للنقر، بالعربية والإنجليزية.
- حد أقصى للتكبير 12 مليون بكسل وذاكرة مؤقتة للصور 32 MB.
- استعادة الجلسة: اللغة، حجم النافذة، الشريط الجانبي، وآخر الملفات.

### English

**Installer and languages**

- Setup now asks for the language first: a setup-UI dialog (Arabic/English), then an **Application language** page with all 19 languages.
- The choice is written to `{app}\language.txt` and read on first launch.
- Upgrading with a different installer language applies it; otherwise the user's saved in-app choice is preserved.
- `/APPLANG=` for silent installs and `/LANG=` for the setup UI language.
- `language.txt` is removed automatically on uninstall.
- Installer language list and app language list are kept in sync by an automated test.

**Fixes**

- Fixed the Windows 7 crash when opening a PDF (image object lifetime in `_pix_to_qimage`).
- Fixed freehand drawing by replacing the missing `add_freehand_annot` with `add_ink_annot`.
- Fixed the signature tool label showing the raw `tool_sign` key.
- Safe saving: a failed save keeps the document open, reopens the original, and restores password protection.
- Confirmation before opening another file or closing with unsaved changes.
- “Fit width” is recalculated after the layout settles, removing unnecessary horizontal scrollbars.
- Menu actions are rebuilt cleanly on language changes (no memory growth), and all PDFs are closed even after an error.
- Arabic/Persian digits are accepted in split ranges (`١-٣`).
- Thumbnail colour no longer changes when selected.

**UI and performance**

- New home screen with four large cards and a toolbar that appears progressively.
- Lazy thumbnails (about 40 cached) that hide automatically in narrow windows.
- Built-in user guide (F1) with a clickable index, in Arabic and English.
- 12-megapixel zoom cap and a 32 MB image cache.
- Session restore: language, window geometry, sidebar, and recent files.
