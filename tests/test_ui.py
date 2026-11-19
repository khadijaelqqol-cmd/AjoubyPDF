# -*- coding: utf-8 -*-
"""اختبار وظيفي شامل لواجهة اجوبي PDF (بدون عرض) - متوافق Qt5/Qt6"""
import os
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# تعطيل الحوارات الحوارية أثناء الاختبار
from ajoubi.qt_compat import QMessageBox, QApplication, QSettings
QMessageBox.information = staticmethod(lambda *a, **k: None)
QMessageBox.critical = staticmethod(lambda *a, **k: None)
QMessageBox.about = staticmethod(lambda *a, **k: None)

# إعدادات معزولة حتى لا تتلوّث قائمة «آخر الملفات» الحقيقية
QSettings.setDefaultFormat(QSettings.IniFormat)
QSettings.setPath(QSettings.IniFormat, QSettings.UserScope,
                  tempfile.mkdtemp())

import fitz  # noqa: E402
from ajoubi.qt_compat import Qt  # noqa: E402

app = QApplication([])

tmp = tempfile.mkdtemp()

# ملف بصفحتين
d = fitz.open()
d.new_page(width=400, height=300)
d.new_page(width=400, height=300)
test_pdf = os.path.join(tmp, "test.pdf")
d.save(test_pdf)
d.close()

# ملف فيه نص
d = fitz.open()
page = d.new_page(width=400, height=300)
page.insert_text((50, 100), "Hello Ajouby", fontsize=20)
text_pdf = os.path.join(tmp, "text.pdf")
d.save(text_pdf)
d.close()

from ajoubi.main_window import MainWindow  # noqa: E402

w = MainWindow()
print("WINDOW OK")

w.load_file(test_pdf)
print("OPEN pages:", w.page_count(), "labels:", len(w.page_labels))

w.goto_page(1)
print("GOTO spin:", w.page_spin.value())
w.zoom_in(); w.zoom_out(); w.fit_width(); w.fit_page()
print("ZOOM OK, zoom =", round(w.zoom, 2))

w.find_edit.setText("Hello")
w.do_search()
print("SEARCH OK")

w.rotate_page(90)
print("ROTATE OK")

w.goto_page(1)
w.delete_page()
print("DELETE pages now:", w.page_count())

# ===== اختبار الإصلاح الحرج: تفعيل الأدوات من شريط الأدوات =====
# نحاكي نقر المستخدم: trigger() يبث triggered(checked) — يجب أن يصل الاسم الصحيح
for mode in ("highlight", "note", "freehand", "text", "sign", "pointer"):
    w.tool_actions[mode].trigger()
    assert w.tool_mode == mode, f"TOOL BUG: trigger {mode} -> {w.tool_mode}"
print("TOOLBAR TRIGGER FIX OK (all 6 tools activate correctly)")

# التعليقات التوضيحية على ملف النص
w2 = MainWindow()
w2.load_file(text_pdf)
w2.set_tool("highlight")
w2.on_highlight(0, (fitz.Point(40, 85), fitz.Point(180, 105)))
w2.set_tool("freehand")
w2.on_freehand(0, [fitz.Point(30 + i, 50 + i * 0.5) for i in range(20)])
annots = list(w2.doc[0].annots() or [])
print("ANNOT count:", len(annots))

# إدراج نص عربي (عبر insert_htmlbox مع fallback)
w2.set_tool("text")
from ajoubi.qt_compat import QInputDialog  # noqa: E402
QInputDialog.getMultiLineText = staticmethod(lambda *a, **k: ("نص تجربة", True))
QInputDialog.getInt = staticmethod(lambda *a, **k: (14, True))
import fitz as _f  # noqa: E402
w2.on_page_click(0, fitz.Point(50, 200))
print("ARABIC TEXT INSERT OK")

# الحفظ
w2.file_path = text_pdf
w2.dirty = True
w2.save()
print("SAVE OK, still open:", w2.doc is not None)

# إعادة الفتح والتأكد من الحفظ
w3 = MainWindow()
w3.load_file(text_pdf)
annots2 = list(w3.doc[0].annots() or [])
print("SAVED annots visible after reload:", len(annots2))

# ===== تغيير اللغة مع مفتوح: نطاق الصفحة يجب أن يبقى صحيحاً =====
w3.change_language("en")
assert w3.page_spin.maximum() == w3.page_count(), "SPIN RANGE BUG after lang change"
print("LANG CHANGE + SPIN RANGE OK, max =", w3.page_spin.maximum())

# اللغات الـ 19
from ajoubi import i18n  # noqa: E402
for code in i18n.available_languages():
    w.change_language(code)
w.change_language("ar")
print("ALL 19 LANGS OK, RTL:", app.layoutDirection() == Qt.RightToLeft)
print("ALL UI TESTS PASSED")
