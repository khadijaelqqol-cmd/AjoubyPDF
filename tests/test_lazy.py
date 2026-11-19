# -*- coding: utf-8 -*-
"""Lazy rendering + memory test (Qt5/Qt6 compatible)"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ajoubi.qt_compat import QMessageBox, QApplication, QSettings
QMessageBox.information = staticmethod(lambda *a, **k: None)
QMessageBox.critical = staticmethod(lambda *a, **k: None)

QSettings.setDefaultFormat(QSettings.IniFormat)
QSettings.setPath(QSettings.IniFormat, QSettings.UserScope,
                  tempfile.mkdtemp())

try:
    import pymupdf as fitz  # PyMuPDF >= 2.0
except ImportError:
    import fitz  # older versions (Python 3.8)

app = QApplication([])

tmp = tempfile.mkdtemp()
pdf_path = os.path.join(tmp, "big.pdf")

d = fitz.open()
for i in range(100):
    p = d.new_page(width=500, height=700)
    p.insert_text((50, 80), "Page %d content" % (i + 1), fontsize=16)
d.save(pdf_path)
d.close()

from ajoubi.main_window import MainWindow

w = MainWindow()
# لا حاجة لإظهار النافذة على المنصة الافتراضية (تسبب انهياراً في PySide2)
w.resize(1000, 700)
app.processEvents()

w.load_file(pdf_path)
app.processEvents()


def rendered_count():
    return sum(1 for lbl in w.page_labels
               if lbl.pixmap() is not None and not lbl.pixmap().isNull())


r = rendered_count()
print("PAGES:", w.page_count())
print("RENDERED at start (should be small):", r)
assert r <= 8, "too many rendered: %d" % r

w.goto_page(49)
app.processEvents()
r2 = rendered_count()
print("RENDERED at page 50 (should stay small):", r2)
assert r2 <= 10, "too many rendered: %d" % r2

w.goto_page(0)
app.processEvents()
r3 = rendered_count()
print("RENDERED back at page 1:", r3)
assert r3 <= 10

w.zoom_in()
app.processEvents()
print("ZOOM OK, rendered:", rendered_count())

print("LAZY RENDERING TESTS PASSED - memory stays low")
