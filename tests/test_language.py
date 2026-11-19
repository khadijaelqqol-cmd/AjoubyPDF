# -*- coding: utf-8 -*-
"""اختبار اختيار اللغة الأولي القادم من المثبّت (language.txt)"""
import os
import shutil
import sys
import tempfile

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import initial_language  # noqa: E402
from ajoubi import i18n  # noqa: E402


class FakeSettings:
    """بديل بسيط عن QSettings لتتبّع القيم المكتوبة."""

    def __init__(self, values=None):
        self.values = dict(values or {})
        self.writes = {}

    def contains(self, key):
        return key in self.values

    def value(self, key, default=None):
        return self.values.get(key, default)

    def setValue(self, key, value):
        self.values[key] = value
        self.writes[key] = value


base = tempfile.mkdtemp(prefix="ajouby_lang_")
lang_file = os.path.join(base, "language.txt")


def write_lang(code, encoding="utf-8"):
    with open(lang_file, "w", encoding=encoding) as fh:
        fh.write(code)


def remove_lang():
    try:
        os.remove(lang_file)
    except OSError:
        pass


try:
    # 1) لا إعدادات ولا ملف → العربية، دون كتابة أي شيء
    s = FakeSettings()
    assert initial_language(s, base) == "ar"
    assert s.writes == {}, s.writes

    # 2) اللغة المحفوظة داخل البرنامج تُحترم عند غياب ملف المثبّت
    s = FakeSettings({"language": "fr"})
    assert initial_language(s, base) == "fr"
    assert s.writes == {}, s.writes

    # 3) اختيار المثبّت يُقرأ ويُحفظ عند أول تشغيل
    write_lang("ja\n")
    s = FakeSettings()
    assert initial_language(s, base) == "ja"
    assert s.writes == {"language": "ja", "installer_language": "ja"}, s.writes

    # 4) رمز غير مدعوم → العربية
    write_lang("xx")
    s = FakeSettings()
    assert initial_language(s, base) == "ar"
    assert s.writes == {}, s.writes

    # 5) ملف بترميز UTF-8 مع BOM (كما يكتبه المثبّت)
    write_lang("ar", encoding="utf-8-sig")
    s = FakeSettings()
    assert initial_language(s, base) == "ar"
    assert s.writes == {"language": "ar", "installer_language": "ar"}

    # 6) كل لغات البرنامج الـ19 مقبولة
    for code in i18n.LANGUAGES:
        write_lang(code)
        s = FakeSettings()
        assert initial_language(s, base) == code, code
        assert s.writes == {"language": code, "installer_language": code}, code

    # 7) تثبيت جديد فوق إعدادات قديمة: اختيار المثبّت الجديد له الأولوية
    write_lang("ja")
    s = FakeSettings({"language": "fr"})
    assert initial_language(s, base) == "ja"
    assert s.writes == {"language": "ja", "installer_language": "ja"}

    # 8) إعادة تثبيت باللغة نفسها: اختيار المستخدم داخل البرنامج يبقى
    write_lang("ar")
    s = FakeSettings({"language": "en", "installer_language": "ar"})
    assert initial_language(s, base) == "en"
    assert s.writes == {}, s.writes

    # 9) ترقية تختار لغة مختلفة: تُطبَّق مرة واحدة
    write_lang("fr")
    s = FakeSettings({"language": "en", "installer_language": "ar"})
    assert initial_language(s, base) == "fr"
    assert s.writes == {"language": "fr", "installer_language": "fr"}

    # 10) ملف تالف لا يطمس اللغة المحفوظة
    write_lang("zz")
    s = FakeSettings({"language": "de", "installer_language": "de"})
    assert initial_language(s, base) == "de"
    assert s.writes == {}, s.writes

    # 11) لا ملف ولا إعدادات لكن مجلد غير موجود → العربية
    assert initial_language(FakeSettings(), os.path.join(base, "missing")) == "ar"

    print("INITIAL LANGUAGE TESTS PASSED "
          "(installer choice, upgrades, 19 codes)")
finally:
    remove_lang()
    shutil.rmtree(base, ignore_errors=True)
