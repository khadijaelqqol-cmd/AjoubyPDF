# -*- coding: utf-8 -*-
"""اختبارات الواجهة الجديدة: الشاشة الرئيسية، الصور المصغرة الكسولة، الدليل، الترجمات"""
import os
import sys
import tempfile
import weakref

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ajoubi.qt_compat import QApplication, QMessageBox, QSettings, Qt  # noqa: E402

QMessageBox.information = staticmethod(lambda *a, **k: None)
QMessageBox.critical = staticmethod(lambda *a, **k: None)
QMessageBox.warning = staticmethod(lambda *a, **k: None)
QMessageBox.question = staticmethod(lambda *a, **k: QMessageBox.Discard)

QSettings.setDefaultFormat(QSettings.IniFormat)
QSettings.setPath(QSettings.IniFormat, QSettings.UserScope,
                  tempfile.mkdtemp())

try:
    import pymupdf as fitz  # noqa: E402
except ImportError:
    import fitz  # noqa: E402

from ajoubi import i18n, guide  # noqa: E402
from ajoubi.main_window import MainWindow  # noqa: E402
from ajoubi.dialogs import GuideDialog  # noqa: E402
from ajoubi.translations_ui import UI_TRANSLATIONS  # noqa: E402

app = QApplication([])

tmp = tempfile.mkdtemp()
pdf_path = os.path.join(tmp, "sample.pdf")
d = fitz.open()
for i in range(6):
    p = d.new_page(width=400, height=600)
    p.insert_text((40, 60), "Page %d" % (i + 1), fontsize=18)
d.save(pdf_path)
d.close()

# ---------- 1) الترجمات ----------
codes = i18n.available_languages()
assert len(codes) == 19, codes
ui_keys = sorted(UI_TRANSLATIONS["en"].keys())
assert len(ui_keys) == 24, len(ui_keys)
for code in codes:
    table = i18n.TRANSLATIONS.get(code, {})
    missing = [k for k in ui_keys if not str(table.get(k, "")).strip()]
    assert not missing, (code, missing)
print("TRANSLATIONS OK: 19 languages x %d new keys" % len(ui_keys))

# مفتاح التوقيع الصحيح (كان يظهر كنص خام tool_sign)
i18n.set_language("ar")
assert i18n.tr("tool_signature") != "tool_signature"
print("SIGNATURE KEY OK:", i18n.tr("tool_signature"))


# ---------- 2) الشاشة الرئيسية ----------
w = MainWindow()
w.resize(1200, 800)
assert not w.home.isHidden()
visible = [a for a in w.toolbar.actions()
           if a.isVisible() and not a.isSeparator()]
assert len(visible) == 2, "welcome toolbar should be minimal, got %d" % len(visible)
assert w.tools_bar.isHidden(), "drawing toolbar must be hidden with no document"

# تكيّف البطاقات مع العرض
w.home.reflow(1100)
assert w.home._cols == 4
w.home.reflow(700)
assert w.home._cols == 2
w.home.reflow(420)
assert w.home._cols == 1
w.home.reflow(1100)
assert w.home._cols == 4
print("HOME RESPONSIVE OK: 4 / 2 / 1 columns")

# ---------- 3) فتح ملف: الأدوات تظهر والصور المصغرة كسولة ----------
w.load_file(pdf_path)
app.processEvents()
assert w.home.isHidden()
assert not w.tools_bar.isHidden()
assert w.thumb_list.count() == 6
# لا تُرسم كل الصور المصغرة دفعة واحدة
assert len(w._thumb_loaded) <= 8, len(w._thumb_loaded)
assert w.page_spin.maximum() == 6
print("OPEN + LAZY THUMBS OK: items=%d loaded=%d"
      % (w.thumb_list.count(), len(w._thumb_loaded)))

# ---------- 4) إخفاء/إظهار الشريط الجانبي حسب العرض ----------
w._sidebar_forced = False
w.resize(760, 640)
app.processEvents()
w._update_sidebar()  # نافذة الاختبار غير معروضة، فنستدعي نفس منطق resizeEvent
assert w.width() < 880
assert w.thumb_list.isHidden(), "sidebar should auto-hide on narrow window"
w.resize(1200, 800)
app.processEvents()
w._update_sidebar()
assert not w.thumb_list.isHidden(), "sidebar should return on wide window"
print("RESPONSIVE SIDEBAR OK")

# ---------- 5) الرسم الحر (إصلاح add_ink_annot) ----------
before = len(list(w.doc[0].annots() or []))
w.set_tool("freehand")
w.on_freehand(0, [fitz.Point(20 + i, 30 + i % 5) for i in range(12)])
after = len(list(w.doc[0].annots() or []))
assert after == before + 1, (before, after)
print("FREEHAND INK OK: annots", after)

# ---------- 6) الدليل ----------
html_ar = guide.html("ar")
html_en = guide.html("en")
assert "دليل الاستخدام" in html_ar
assert "User Guide" in html_en
assert 'href="#faq"' in html_ar
assert guide.markdown("ar").startswith("# دليل الاستخدام")
assert guide.markdown("en").startswith("# User Guide")

dlg = GuideDialog(w)
assert "افتح ملفك" in dlg.view.toPlainText()
assert "أسئلة شائعة" in dlg.view.toPlainText()
dlg.close()
print("GUIDE DIALOG OK (ar/en content + anchors)")

# ---------- 7) تغيير اللغة يعيد النصوص ----------
w.change_language("en")
assert w.home.title.text() == "Welcome to Ajouby PDF"
assert w.page_spin.maximum() == 6
w.change_language("ar")
assert w.home.title.text() == i18n.tr("home_welcome")
print("LANGUAGE SWITCH OK")

# ---------- 8) حفظ آمن: فشل الحفظ لا يُغلق المستند ----------
w.dirty = True
w.file_path = os.path.join(tmp, "missing_folder", "out.pdf")
ok = w.save()
assert ok is False
assert w.doc is not None and not w.doc.is_closed
print("SAFE SAVE FAILURE OK (document stays open)")

# ---------- 9) سلامة حياة pix.samples أثناء التحويل إلى QImage ----------
from ajoubi import main_window as mw  # noqa: E402


class _FakeSamples:
    """كائن نحوّل له بدل bytes حتى يمكن تتبّع حياته بمرجع ضعيف"""


class _FakePix:
    alpha = False
    width = 8
    height = 8
    stride = 24

    @property
    def samples(self):
        return _FakeSamples()


class _FakeImage:
    """محاكاة PySide2: QImage لا يحتفظ بمرجع للمخزن الخارجي"""
    last_ref = None
    copied = False

    def __init__(self, data, w, h, stride, fmt):
        _FakeImage.last_ref = weakref.ref(data)

    def copy(self):
        assert _FakeImage.last_ref() is not None, \
            "pix.samples حُرِّر قبل QImage.copy() — use-after-free"
        _FakeImage.copied = True
        return self


_orig_qimage = mw.QImage
_FakeImage.Format_RGB888 = _orig_qimage.Format_RGB888
_FakeImage.Format_RGBA8888 = _orig_qimage.Format_RGBA8888
mw.QImage = _FakeImage
try:
    w._pix_to_qimage(_FakePix())
finally:
    mw.QImage = _orig_qimage
assert _FakeImage.copied
print("PIX SAMPLE LIFETIME OK (no use-after-free)")

w.close()
print("ALL NEW UI TESTS PASSED")
