# -*- coding: utf-8 -*-
"""عمليات PDF الأساسية: دمج، تقسيم، ضغط، حماية، تحويل، OCR

ملاحظات:
  • تُغلق كل الملفات المفتوحة حتى عند حدوث خطأ (لا تسريب مقابض ملفات).
  • أرقام الصفحات تقبل الأرقام العربية/الفارسية أيضاً (١-٣).
"""

import os

try:
    import pymupdf as fitz  # PyMuPDF >= 2.0
except ImportError:
    import fitz  # إصدارات أقدم

# أرقام عربية-هندية وفارسية -> أرقام لاتينية
_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")


def normalize_digits(text):
    return str(text).translate(_DIGITS)


# ---------------------- دمج ----------------------
def merge_pdfs(paths, out_path):
    if not paths:
        raise ValueError("no files")
    doc = fitz.open()
    try:
        for path in paths:
            with fitz.open(path) as src:
                if src.needs_pass:
                    raise PermissionError("encrypted: %s" % os.path.basename(path))
                doc.insert_pdf(src)
        if doc.page_count == 0:
            raise ValueError("empty document")
        doc.save(out_path)
    finally:
        doc.close()


# ---------------------- تقسيم ----------------------
def parse_ranges(text, page_count):
    """نص مثل '1-3,5,8-10' -> قائمة قوائم من أرقام الصفحات (0-based)"""
    groups = []
    text = normalize_digits(text).replace(" ", "").replace("،", ",")
    if not text:
        raise ValueError("empty")
    for part in text.split(","):
        if not part:
            raise ValueError("empty part")
        if "-" in part:
            pieces = part.split("-")
            if len(pieces) != 2:
                raise ValueError("range")
            a, b = int(pieces[0]) - 1, int(pieces[1]) - 1
            if a < 0 or b < a or b >= page_count:
                raise ValueError("range")
            groups.append(list(range(a, b + 1)))
        else:
            n = int(part) - 1
            if n < 0 or n >= page_count:
                raise ValueError("range")
            groups.append([n])
    if not groups:
        raise ValueError("empty")
    return groups


def split_pdf(src_path, out_dir, every=None, ranges_text=None, base_name="part"):
    """يرجع عدد الملفات الناتجة"""
    doc = fitz.open(src_path)
    try:
        n = doc.page_count
        if n == 0:
            raise ValueError("empty document")
        os.makedirs(out_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(base_name))[0] or "part"

        if every:  # كل N صفحة في ملف
            every = max(1, int(every))
            count = 0
            for start in range(0, n, every):
                chunk = list(range(start, min(start + every, n)))
                _save_pages(doc, chunk,
                            os.path.join(out_dir, f"{stem}_{count + 1}.pdf"))
                count += 1
            return count

        # نطاقات يدوية
        groups = parse_ranges(ranges_text, n)
        for i, chunk in enumerate(groups):
            _save_pages(doc, chunk,
                        os.path.join(out_dir, f"{stem}_{i + 1}.pdf"))
        return len(groups)
    finally:
        doc.close()


def _save_pages(doc, page_numbers, out_path):
    new_doc = fitz.open()
    try:
        for pn in page_numbers:
            new_doc.insert_pdf(doc, from_page=pn, to_page=pn)
        new_doc.save(out_path)
    finally:
        new_doc.close()


# ---------------------- ضغط ----------------------
def compress_pdf(src_path, out_path):
    doc = fitz.open(src_path)
    try:
        doc.save(out_path, garbage=4, deflate=True, clean=True)
    finally:
        doc.close()


# ---------------------- حماية ----------------------
def encrypt_pdf(src_path, out_path, password):
    if not password:
        raise ValueError("empty password")
    doc = fitz.open(src_path)
    try:
        perms = (fitz.PDF_PERM_ACCESSIBILITY | fitz.PDF_PERM_PRINT
                 | fitz.PDF_PERM_COPY | fitz.PDF_PERM_ANNOTATE)
        doc.save(out_path, encryption=fitz.PDF_ENCRYPT_AES_256,
                 owner_pw=password, user_pw=password, permissions=perms)
    finally:
        doc.close()


def decrypt_pdf(src_path, out_path, password):
    doc = fitz.open(src_path)
    try:
        if doc.needs_pass and not doc.authenticate(password):
            raise PermissionError("wrong password")
        doc.save(out_path, encryption=fitz.PDF_ENCRYPT_NONE)
    finally:
        doc.close()


# ---------------------- تحويل ----------------------
def pdf_to_images(src_path, out_dir, fmt="png", dpi=150):
    fmt = fmt if fmt in ("png", "jpg", "jpeg") else "png"
    doc = fitz.open(src_path)
    try:
        os.makedirs(out_dir, exist_ok=True)
        stem = os.path.splitext(os.path.basename(src_path))[0]
        count = 0
        for i, page in enumerate(doc):
            pix = page.get_pixmap(dpi=dpi)
            try:
                out_file = os.path.join(out_dir, f"{stem}_p{i + 1}.{fmt}")
                pix.save(out_file)
            finally:
                pix = None
            count += 1
        return count
    finally:
        doc.close()


def images_to_pdf(paths, out_path):
    doc = fitz.open()
    try:
        for path in paths:
            with fitz.open(path) as img:
                pdf_bytes = img.convert_to_pdf()
            with fitz.open("pdf", pdf_bytes) as src:
                doc.insert_pdf(src)
        if doc.page_count == 0:
            raise ValueError("no images")
        doc.save(out_path)
    finally:
        doc.close()


def extract_text(src_path, out_txt_path):
    doc = fitz.open(src_path)
    try:
        parts = []
        for i, page in enumerate(doc):
            parts.append(f"----- [{i + 1}] -----\n" + page.get_text())
        with open(out_txt_path, "w", encoding="utf-8") as f:
            f.write("\n".join(parts))
    finally:
        doc.close()


# ---------------------- تحويل إلى Word / Excel ----------------------
def pdf_to_word(src_path, out_docx_path, page_sep=True):
    """تصدير نص PDF إلى ملف Word مع الحفاظ على ترتيب الصفحات والفقرات"""
    import docx
    from docx.enum.text import WD_ALIGN_PARAGRAPH

    doc = fitz.open(src_path)
    try:
        wd = docx.Document()
        for i, page in enumerate(doc):
            if page_sep and i > 0:
                wd.add_page_break()
            for block in page.get_text("blocks"):
                text = block[4].strip()
                if not text:
                    continue
                p = wd.add_paragraph(text)
                # كشف RTL: نسبة كبيرة من أحرف عربية/فارسية/عبرانية
                rtl_chars = sum(1 for c in text if "\u0600" <= c <= "\u06FF"
                                or "\u0750" <= c <= "\u077F"
                                or "\u0590" <= c <= "\u05FF")
                if rtl_chars > len(text) * 0.3:
                    p.alignment = WD_ALIGN_PARAGRAPH.RIGHT
        wd.save(out_docx_path)
    finally:
        doc.close()


def pdf_to_excel(src_path, out_xlsx_path):
    """تصدير نص PDF إلى Excel: ورقة لكل صفحة، كل سطر نص في صف"""
    import openpyxl

    doc = fitz.open(src_path)
    try:
        wb = openpyxl.Workbook()
        wb.remove(wb.active)
        for i, page in enumerate(doc):
            ws = wb.create_sheet(title=f"Page {i + 1}")
            row_num = 1
            for block in page.get_text("blocks"):
                for line in block[4].strip().splitlines():
                    if line.strip():
                        ws.cell(row=row_num, column=1, value=line.strip())
                        row_num += 1
            ws.column_dimensions["A"].width = 100
        if not wb.sheetnames:
            wb.create_sheet(title="Page 1")
        wb.save(out_xlsx_path)
    finally:
        doc.close()


# ---------------------- OCR ----------------------
# أكواد Tesseract المقابلة للغات البرنامج
OCR_LANG_CODES = {
    "ara": "العربية", "eng": "English", "fra": "Français", "spa": "Español",
    "deu": "Deutsch", "ita": "Italiano", "por": "Português", "tur": "Türkçe",
    "rus": "Русский", "chi_sim": "中文", "jpn": "日本語", "kor": "한국어",
    "hin": "हिन्दी", "nld": "Nederlands", "pol": "Polski", "swe": "Svenska",
    "ell": "Ελληνικά", "fas": "فارسی", "ukr": "Українська",
}


def ocr_pdf(src_path, out_path, lang_code):
    """إنشاء PDF قابل للبحث عبر Tesseract"""
    from PIL import Image
    import pytesseract

    doc = fitz.open(src_path)
    out_doc = fitz.open()
    try:
        for page in doc:
            pix = page.get_pixmap(dpi=200)
            img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
            pix = None
            pdf_bytes = pytesseract.image_to_pdf_or_hocr(img, lang=lang_code)
            tmp = fitz.open("pdf", pdf_bytes)
            try:
                out_doc.insert_pdf(tmp)
            finally:
                tmp.close()
        out_doc.save(out_path)
    finally:
        out_doc.close()
        doc.close()
