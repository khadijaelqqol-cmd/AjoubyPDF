# -*- coding: utf-8 -*-
"""محتوى دليل الاستخدام — مصدر واحد للدليل داخل البرنامج وللملفات النصية.

البلوكات المدعومة:
    ("p", text)          فقرة
    ("steps", [texts])   خطوات مرقّمة
    ("list", [texts])    نقاط
    ("note", text)       صندوق نصيحة
    ("table", rows)      جدول (الصف الأول عناوين)
"""

import html as _html
import re

GUIDE_LANGS = ("ar", "en")


def language_for(code):
    """لغة الدليل: العربية للعربية، والإنجليزية لبقية اللغات"""
    return "ar" if code == "ar" else "en"


# ======================================================================
# العربية
# ======================================================================
_AR = {
    "title": "دليل الاستخدام",
    "subtitle": "كل ما تحتاجه خطوة بخطوة — ببساطة تامة",
    "sections": [
        {
            "id": "open",
            "title": "١. افتح ملفك",
            "blocks": [
                ("p", "هناك ثلاث طرق سهلة لفتح ملف PDF:"),
                ("steps", [
                    "اضغط زر «فتح» الكبير في الأعلى، ثم اختر الملف من جهازك.",
                    "أو اسحب الملف بملف الفأرة وأفلته في منتصف النافذة.",
                    "أو اختر الملف من قائمة «آخر الملفات» في الشاشة الرئيسية.",
                ]),
                ("p", "إذا كان الملف محمياً بكلمة مرور، سيسألك البرنامج عنها مرة واحدة."),
                ("note", "تلميح: يمكنك أيضاً سحب عدة صور وإفلاتها لتحويلها إلى ملف PDF واحد."),
            ],
        },
        {
            "id": "navigate",
            "title": "٢. تنقّل بين الصفحات",
            "blocks": [
                ("p", "استخدم الأزرار «السابق» و«التالي» في شريط الأدوات، أو اكتب رقم الصفحة في المربع الصغير ثم اضغط Enter."),
                ("list", [
                    "الصور المصغرة على الجانب: انقر على أي صفحة للانتقال إليها فوراً.",
                    "عجلة الفأرة: تمرير لأعلى ولأسفل.",
                    "لوحة المفاتيح: Page Down وPage Up للتنقل، وCtrl+Home وCtrl+End للبداية والنهاية.",
                ]),
                ("note", "الصور المصغرة تُرسم عند الحاجة فقط، لذلك يبقى البرنامج خفيفاً حتى مع الملفات الكبيرة."),
            ],
        },
        {
            "id": "zoom",
            "title": "٣. التكبير والتصغير",
            "blocks": [
                ("p", "استخدم زرّي «تكبير» و«تصغير»، أو اضغط Ctrl مع عجلة الفأرة."),
                ("list", [
                    "«ملاءمة العرض»: يجعل عرض الصفحة يناسب النافذة.",
                    "«ملاءمة الصفحة»: يعرض الصفحة كاملة على الشاشة.",
                    "نسبة التكبير تظهر أسفل النافذة على اليسار.",
                ]),
            ],
        },
        {
            "id": "annotate",
            "title": "٤. ظلّل واكتب ملاحظات",
            "blocks": [
                ("p", "أولاً اختر أداة «تظليل» من شريط الأدوات، ثم اسحب بالفأرة فوق النص الذي تريد تظليله."),
                ("p", "أداة «ملاحظة» تُضيف ملاحظة لاصقة: اختر الأداة ثم انقر على المكان المناسب واكتب نص الملاحظة."),
                ("list", [
                    "«تحديد»: للعودة إلى الوضع العادي (قراءة فقط).",
                    "كل إضافة تُحفظ داخل الملف بعد الضغط على «حفظ».",
                ]),
                ("note", "إذا أخطأت، يمكنك التراجع بالخروج دون حفظ (سيُسألك البرنامج)."),
            ],
        },
        {
            "id": "draw",
            "title": "٥. ارسم بيدك",
            "blocks": [
                ("p", "اختر أداة «رسم حر»، ثم اضغط واسحب على الصفحة لرسم خط أحمر. ارفع إصبعك أو زر الفأرة لإنهاء الرسم."),
                ("p", "مفيدة للتوقيع السريع أو وضع دائرة حول معلومة مهمة."),
            ],
        },
        {
            "id": "text_sign",
            "title": "٦. أضف نصاً أو توقيعك",
            "blocks": [
                ("p", "أداة «نص»: اخترها، انقر على الصفحة، اكتب النص وحدّد حجم الخط. يدعم البرنامج العربية بشكل صحيح (اتجاه من اليمين إلى اليسار)."),
                ("p", "أداة «توقيع»: اختر صورة توقيعك (PNG بخلفية شفافة)، ثم انقر على الصفحة لوضعها. يُحافظ البرنامج على نسبة الصورة."),
                ("note", "تلميح: صوّر توقيعك على ورقة بيضاء، ثم أزل الخلفية بأي أداة مجانية لتحصل على PNG شفاف."),
            ],
        },
        {
            "id": "pages",
            "title": "٧. رتّب الصفحات",
            "blocks": [
                ("p", "افتح قائمة «الصفحة» في شريط الأدوات:"),
                ("list", [
                    "«تدوير يميناً» و«تدوير يساراً»: لتصحيح اتجاه الصفحة.",
                    "«حذف الصفحة»: يحذف الصفحة الحالية.",
                    "«إدراج صفحات من ملف»: يضيف صفحات ملف آخر بعد الصفحة الحالية أو في النهاية.",
                ]),
                ("note", "لا يُحفظ أي تغيير إلا بعد الضغط على «حفظ»."),
            ],
        },
        {
            "id": "files",
            "title": "٨. أدوات الملفات",
            "blocks": [
                ("p", "من قائمة «أدوات الملف» أو قائمة «أدوات»:"),
                ("list", [
                    "«دمج ملفات»: يجمع عدة ملفات PDF في ملف واحد.",
                    "«تقسيم ملف»: يقسّم الملف إلى ملفات صغيرة (كل عدد من الصفحات أو بنطاقات مثل 1-3,5).",
                    "«ضغط الملف»: يقلّل حجم الملف مع الحفاظ على المحتوى.",
                    "«حماية بكلمة مرور»: يشفّر الملف بكلمة مرور قوية.",
                    "«إزالة الحماية»: يزيل كلمة المرور من ملف تعرفه.",
                ]),
                ("note", "هذه الأدوات تحتاج ملفاً محفوظاً على القرص؛ إذا لم تحفظ بعد فاستخدم «حفظ باسم» أولاً."),
            ],
        },
        {
            "id": "convert",
            "title": "٩. التحويل والتصدير",
            "blocks": [
                ("p", "من قائمة «ملف» يمكنك:"),
                ("list", [
                    "تصدير الصفحات كصور PNG أو JPG بدقة تختارها.",
                    "تصدير النص إلى ملف نصي.",
                    "تصدير إلى Word أو Excel.",
                    "تحويل صور إلى PDF.",
                    "التعرّف الضوئي OCR لملف ممسوح (يتطلب تثبيت Tesseract).",
                ]),
                ("note", "التحويل إلى Word وExcel يصدّر النص فقط؛ الصور والتنسيق المعقّد قد لا تنتقل كما هي."),
            ],
        },
        {
            "id": "search",
            "title": "١٠. ابحث وغيّر اللغة",
            "blocks": [
                ("p", "اكتب كلمة في مربع البحث واضغط Enter. سينتقل البرنامج إلى أول صفحة تحتوي النتائج ويظلّلها بالأصفر."),
                ("p", "لتغيير اللغة: قائمة «اللغة» ثم اختر لغتك. تتحول الواجهة كاملة إلى اليمين لليسار عند العربية والفارسية، ويُحفظ اختيارك تلقائياً."),
            ],
        },
        {
            "id": "shortcuts",
            "title": "١١. اختصارات لوحة المفاتيح",
            "blocks": [
                ("table", [
                    ["للقيام بـ", "اضغط"],
                    ["فتح ملف", "Ctrl + O"],
                    ["حفظ", "Ctrl + S"],
                    ["حفظ باسم", "Ctrl + Shift + S"],
                    ["تكبير / تصغير", "Ctrl + + / Ctrl + -"],
                    ["ملاءمة العرض / الصفحة", "Ctrl + 1 / Ctrl + 0"],
                    ["الصفحة التالية / السابقة", "Page Down / Page Up"],
                    ["أول / آخر صفحة", "Ctrl + Home / Ctrl + End"],
                    ["دليل الاستخدام", "F1"],
                    ["إغلاق البرنامج", "Ctrl + Q"],
                ]),
            ],
        },
        {
            "id": "faq",
            "title": "١٢. أسئلة شائعة",
            "blocks": [
                ("table", [
                    ["المشكلة", "الحل"],
                    ["البرنامج يطلب كلمة مرور", "الملف محمي؛ أدخل كلمة المرور الصحيحة أو اطلبها من مالك الملف."],
                    ["«افتح ملفاً أولاً»", "اضغط «فتح» واختر ملف PDF."],
                    ["«احفظ الملف أولاً»", "استخدم «حفظ باسم» ثم أعد المحاولة."],
                    ["OCR لا يعمل", "ثبّت Tesseract وأضفه إلى PATH، ثم أعد تشغيل البرنامج."],
                    ["مضاد الفيروسات ينبّه", "هذا خطأ شائع في ملفات PyInstaller؛ أضف مجلد البرنامج للاستثناءات."],
                    ["الخط العربي لا يظهر", "تأكد من تثبيت الخطوط العربية في ويندوز (Segoe UI أو Tahoma)."],
                ]),
                ("note", "نصيحة أخيرة: ابدأ بملف صغير للتجربة، ثم جرّب الأدوات واحدة واحدة. لا يوجد ما يمكن أن تخسره — التغييرات لا تُحفظ إلا عندما تضغط «حفظ»."),
            ],
        },
    ],
}


# ======================================================================
# English
# ======================================================================
_EN = {
    "title": "User Guide",
    "subtitle": "Everything you need, step by step — nice and easy",
    "sections": [
        {
            "id": "open",
            "title": "1. Open your file",
            "blocks": [
                ("p", "There are three easy ways to open a PDF:"),
                ("steps", [
                    "Click the big “Open” button at the top, then pick the file.",
                    "Or drag the file with your mouse and drop it in the middle of the window.",
                    "Or choose it from “Recent files” on the home screen.",
                ]),
                ("p", "If the file is password-protected, the app asks for the password once."),
                ("note", "Tip: you can also drop several pictures to turn them into a single PDF."),
            ],
        },
        {
            "id": "navigate",
            "title": "2. Move between pages",
            "blocks": [
                ("p", "Use “Previous” and “Next” in the toolbar, or type a page number in the small box and press Enter."),
                ("list", [
                    "Thumbnails on the side: click any page to jump to it.",
                    "Mouse wheel: scroll up and down.",
                    "Keyboard: Page Down / Page Up, and Ctrl + Home / Ctrl + End for first and last page.",
                ]),
                ("note", "Thumbnails are drawn only when needed, so the app stays light even with big files."),
            ],
        },
        {
            "id": "zoom",
            "title": "3. Zoom in and out",
            "blocks": [
                ("p", "Use the “Zoom in” and “Zoom out” buttons, or Ctrl + mouse wheel."),
                ("list", [
                    "“Fit width”: the page width matches the window.",
                    "“Fit page”: the whole page fits on screen.",
                    "The zoom percentage appears at the bottom-left of the window.",
                ]),
            ],
        },
        {
            "id": "annotate",
            "title": "4. Highlight and add notes",
            "blocks": [
                ("p", "Pick the “Highlight” tool, then drag the mouse over the text you want to highlight."),
                ("p", "The “Note” tool adds a sticky note: pick the tool, click a spot, and type your note."),
                ("list", [
                    "“Select”: back to normal reading mode.",
                    "Every addition is stored in the file after you press “Save”.",
                ]),
                ("note", "If you make a mistake, close without saving — the app will ask you."),
            ],
        },
        {
            "id": "draw",
            "title": "5. Draw by hand",
            "blocks": [
                ("p", "Pick the “Draw” tool, then press and drag on the page to draw a red line. Release to finish."),
                ("p", "Great for a quick signature or for circling something important."),
            ],
        },
        {
            "id": "text_sign",
            "title": "6. Add text or your signature",
            "blocks": [
                ("p", "“Text” tool: pick it, click the page, type your text and choose a font size. Arabic and right-to-left text are supported correctly."),
                ("p", "“Signature” tool: choose a signature image (transparent PNG), then click the page to place it. The aspect ratio is preserved."),
                ("note", "Tip: photograph your signature on white paper, then remove the background with any free tool to get a transparent PNG."),
            ],
        },
        {
            "id": "pages",
            "title": "7. Organise pages",
            "blocks": [
                ("p", "Open the “Page” menu in the toolbar:"),
                ("list", [
                    "“Rotate right” / “Rotate left”: fix the page orientation.",
                    "“Delete current page”: removes the current page.",
                    "“Insert pages from file”: adds pages after the current page or at the end.",
                ]),
                ("note", "Nothing is saved until you press “Save”."),
            ],
        },
        {
            "id": "files",
            "title": "8. File tools",
            "blocks": [
                ("p", "From the “File tools” menu or the “Tools” menu:"),
                ("list", [
                    "“Merge files”: join several PDFs into one.",
                    "“Split file”: cut a file into smaller files (every N pages, or ranges like 1-3,5).",
                    "“Compress”: reduce file size while keeping the content.",
                    "“Protect with password”: encrypt the file with a strong password.",
                    "“Remove protection”: remove the password from a file you know.",
                ]),
                ("note", "These tools need the file saved on disk; if you have not saved yet, use “Save As” first."),
            ],
        },
        {
            "id": "convert",
            "title": "9. Convert and export",
            "blocks": [
                ("p", "From the “File” menu you can:"),
                ("list", [
                    "Export pages as PNG or JPG images at a chosen resolution.",
                    "Export the text to a text file.",
                    "Export to Word or Excel.",
                    "Turn images into a PDF.",
                    "OCR a scanned file (requires Tesseract).",
                ]),
                ("note", "Word and Excel export copies the text only; complex images and layout may not carry over."),
            ],
        },
        {
            "id": "search",
            "title": "10. Search and change language",
            "blocks": [
                ("p", "Type a word in the search box and press Enter. The app jumps to the first matching page and highlights matches in yellow."),
                ("p", "To change the language, open the “Language” menu and pick one. The whole interface flips to right-to-left for Arabic and Persian, and your choice is remembered."),
            ],
        },
        {
            "id": "shortcuts",
            "title": "11. Keyboard shortcuts",
            "blocks": [
                ("table", [
                    ["Action", "Press"],
                    ["Open a file", "Ctrl + O"],
                    ["Save", "Ctrl + S"],
                    ["Save as", "Ctrl + Shift + S"],
                    ["Zoom in / out", "Ctrl + + / Ctrl + -"],
                    ["Fit width / page", "Ctrl + 1 / Ctrl + 0"],
                    ["Next / previous page", "Page Down / Page Up"],
                    ["First / last page", "Ctrl + Home / Ctrl + End"],
                    ["User guide", "F1"],
                    ["Quit", "Ctrl + Q"],
                ]),
            ],
        },
        {
            "id": "faq",
            "title": "12. Common questions",
            "blocks": [
                ("table", [
                    ["Problem", "Solution"],
                    ["The app asks for a password", "The file is protected; enter the correct password or ask the file owner."],
                    ["“Open a PDF first”", "Click “Open” and pick a PDF file."],
                    ["“Save the file first”", "Use “Save As”, then try again."],
                    ["OCR does not work", "Install Tesseract and add it to PATH, then restart the app."],
                    ["Antivirus warning", "A common false positive with PyInstaller apps; add the app folder to exclusions."],
                    ["Arabic text is not shown", "Make sure Arabic fonts are installed on Windows (Segoe UI or Tahoma)."],
                ]),
                ("note", "Last tip: start with a small file, then try the tools one by one. Nothing can be lost — changes are only saved when you press “Save”."),
            ],
        },
    ],
}


_CONTENT = {"ar": _AR, "en": _EN}


def content(lang="en"):
    return _CONTENT.get(language_for(lang), _EN)


# ======================================================================
# تحويل المحتوى إلى HTML للعرض داخل البرنامج
# ======================================================================
def html(lang="en"):
    g = content(lang)
    rtl = language_for(lang) == "ar"
    direction = "rtl" if rtl else "ltr"
    align = "right" if rtl else "left"

    parts = [
        '<html><head><meta charset="utf-8"></head>',
        '<body style="font-family:\'Segoe UI\',\'Tahoma\'; font-size:10.5pt; '
        'color:#26313c; direction:%s; text-align:%s;">' % (direction, align),
        '<p style="margin:0 0 4px 0;"><b>المحتويات</b></p>' if rtl
        else '<p style="margin:0 0 4px 0;"><b>Contents</b></p>',
    ]
    # فهرس مضغوط في سطر واحد (يلتف تلقائياً) — لا يستهلك ارتفاعاً كبيراً
    links = " &nbsp;·&nbsp; ".join(
        '<a href="#%s" style="color:#2f7de1; text-decoration:none;">%s</a>'
        % (sec["id"], _esc(sec["title"]))
        for sec in g["sections"])
    parts.append('<p style="font-size:9.5pt; line-height:150%%;">%s</p>' % links)

    for sec in g["sections"]:
        parts.append('<a name="%s"></a>' % sec["id"])
        parts.append('<h2 style="font-size:14pt; color:#1f66c0; margin:20px 0 6px 0;">%s</h2>'
                     % _esc(sec["title"]))
        for kind, payload in sec["blocks"]:
            if kind == "p":
                parts.append('<p style="margin:6px 0;">%s</p>' % _esc(payload))
            elif kind == "steps":
                parts.append('<ol style="margin:6px 0 6px 20px;">')
                for item in payload:
                    parts.append('<li style="margin-bottom:4px;">%s</li>' % _esc(item))
                parts.append("</ol>")
            elif kind == "list":
                parts.append('<ul style="margin:6px 0 6px 20px;">')
                for item in payload:
                    parts.append('<li style="margin-bottom:4px;">%s</li>' % _esc(item))
                parts.append("</ul>")
            elif kind == "note":
                parts.append(
                    '<table width="100%%" cellpadding="8" cellspacing="0" '
                    'style="margin:10px 0;"><tr><td bgcolor="#f2f8ff">'
                    '<span style="color:#1f66c0;">💡</span> %s</td></tr></table>'
                    % _esc(payload))
            elif kind == "table":
                parts.append('<table width="100%" cellpadding="7" cellspacing="0" '
                             'border="1" style="border-collapse:collapse; '
                             'border-color:#dfe6ee; margin:8px 0;">')
                for r, row in enumerate(payload):
                    parts.append("<tr>")
                    for cell in row:
                        if r == 0:
                            parts.append('<td bgcolor="#eef4fb"><b>%s</b></td>' % _esc(cell))
                        else:
                            parts.append('<td>%s</td>' % _esc(cell))
                    parts.append("</tr>")
                parts.append("</table>")

    parts.append('<p style="color:#8a97a6; font-size:9pt; margin-top:22px;">'
                 "اجوبي PDF — دليل الاستخدام</p>" if rtl else
                 '<p style="color:#8a97a6; font-size:9pt; margin-top:22px;">'
                 "Ajouby PDF — User Guide</p>")
    parts.append("</body></html>")
    return "".join(parts)


def markdown(lang="en"):
    """نسخة Markdown تُستخدم لتوليد ملفات الدليل"""
    g = content(lang)
    out = ["# %s" % g["title"], "", "*%s*" % g["subtitle"], "", "---", ""]
    for i, sec in enumerate(g["sections"], 1):
        out.append("## %s" % sec["title"])
        out.append("")
        for kind, payload in sec["blocks"]:
            if kind == "p":
                out.append(payload)
                out.append("")
            elif kind == "steps":
                for n, item in enumerate(payload, 1):
                    out.append("%d. %s" % (n, item))
                out.append("")
            elif kind == "list":
                for item in payload:
                    out.append("- %s" % item)
                out.append("")
            elif kind == "note":
                out.append("> 💡 %s" % payload)
                out.append("")
            elif kind == "table":
                header = payload[0]
                out.append("| " + " | ".join(header) + " |")
                out.append("|" + "|".join(["---"] * len(header)) + "|")
                for row in payload[1:]:
                    out.append("| " + " | ".join(row) + " |")
                out.append("")
    out.append("---")
    out.append("")
    out.append("*اجوبي PDF — دليل الاستخدام*" if language_for(lang) == "ar"
               else "*Ajouby PDF — User Guide*")
    out.append("")
    return "\n".join(out)


_BIDI_TOKENS = re.compile(
    r"(?:Ctrl|Alt|Shift)(?:\s*\+\s*(?:Ctrl|Alt|Shift|[A-Za-z0-9+/])+)*"
    r"|Page Down|Page Up|Home|End|Enter|Esc|F1|PNG|JPG|PDF|OCR"
    r"|Word|Excel|Tesseract|PyInstaller|Segoe UI|Tahoma|PATH"
)


def _esc(text):
    """تهريب HTML مع عزل الكلمات اللاتينية/الاختصارات داخل النص العربي"""
    value = _html.escape(str(text))
    return _BIDI_TOKENS.sub(
        lambda m: "\u200e" + m.group(0) + "\u200e", value)
