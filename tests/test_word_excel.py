# -*- coding: utf-8 -*-
"""اختبار تحويل PDF إلى Word وExcel وعمليات الملفات"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    import pymupdf as fitz  # PyMuPDF >= 2.0
except ImportError:
    import fitz  # إصدارات أقدم
from ajoubi import pdf_ops  # noqa: E402

tmp = tempfile.mkdtemp()

# إنشاء PDF بفقرات
pdf_path = os.path.join(tmp, "src.pdf")
d = fitz.open()
p1 = d.new_page(width=500, height=700)
p1.insert_text((50, 80), "First paragraph about Ajouby PDF.", fontsize=14)
p1.insert_text((50, 120), "Second paragraph with details.", fontsize=14)
p1.insert_text((50, 160), "Third paragraph ends page one.", fontsize=14)
p2 = d.new_page(width=500, height=700)
p2.insert_text((50, 80), "Page two starts here.", fontsize=14)
d.save(pdf_path)
d.close()

# --- عمليات الملفات ---
out_merge = os.path.join(tmp, "merged.pdf")
pdf_ops.merge_pdfs([pdf_path, pdf_path], out_merge)
print("MERGE pages:", fitz.open(out_merge).page_count)

n = pdf_ops.split_pdf(pdf_path, os.path.join(tmp, "split"), ranges_text="1-2")
print("SPLIT files:", n)

# الأرقام العربية والفارسية مقبولة في النطاقات
n_ar = pdf_ops.split_pdf(pdf_path, os.path.join(tmp, "split_ar"),
                         ranges_text="١-٢")
print("SPLIT with Arabic digits:", n_ar)
assert n_ar == 1
try:
    pdf_ops.parse_ranges("5-1", 2)
    raise AssertionError("invalid range accepted")
except ValueError:
    print("INVALID RANGE correctly rejected")

pdf_ops.compress_pdf(pdf_path, os.path.join(tmp, "comp.pdf"))
print("COMPRESS OK:", os.path.exists(os.path.join(tmp, "comp.pdf")))

pdf_ops.encrypt_pdf(pdf_path, os.path.join(tmp, "enc.pdf"), "1234")
enc = fitz.open(os.path.join(tmp, "enc.pdf"))
print("ENCRYPT needs_pass:", enc.needs_pass)
enc.close()
try:
    pdf_ops.decrypt_pdf(os.path.join(tmp, "enc.pdf"), os.path.join(tmp, "dec.pdf"), "bad")
    print("DECRYPT wrong-pass: FAIL")
except PermissionError:
    print("DECRYPT wrong-pass: correctly rejected")
pdf_ops.decrypt_pdf(os.path.join(tmp, "enc.pdf"), os.path.join(tmp, "dec.pdf"), "1234")
print("DECRYPT ok-pass pages:", fitz.open(os.path.join(tmp, "dec.pdf")).page_count)

n = pdf_ops.pdf_to_images(pdf_path, os.path.join(tmp, "imgs"), fmt="png", dpi=72)
print("PDF->IMAGES:", n)

pdf_ops.extract_text(pdf_path, os.path.join(tmp, "out.txt"))
print("EXTRACT TEXT contains Hello:", "First paragraph" in open(os.path.join(tmp, "out.txt"), encoding="utf-8").read())

# --- Word ---
docx_path = os.path.join(tmp, "out.docx")
pdf_ops.pdf_to_word(pdf_path, docx_path)
import docx  # noqa: E402
wd = docx.Document(docx_path)
paras = [p.text for p in wd.paragraphs if p.text.strip()]
print("WORD paragraphs:", len(paras))
print("  contains p1:", any("First paragraph" in t for t in paras))
print("  contains p2:", any("Page two starts" in t for t in paras))

# --- Excel ---
xlsx_path = os.path.join(tmp, "out.xlsx")
pdf_ops.pdf_to_excel(pdf_path, xlsx_path)
import openpyxl  # noqa: E402
wb = openpyxl.load_workbook(xlsx_path)
print("EXCEL sheets:", wb.sheetnames)
rows = [c[0].value for c in wb["Page 1"].iter_rows() if c[0].value]
print("  sheet1 rows:", len(rows))
print("  contains line:", any("Second paragraph" in r for r in rows))

print("ALL PDF_OPS TESTS PASSED")
