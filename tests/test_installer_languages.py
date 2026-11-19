# -*- coding: utf-8 -*-
"""التحقق من أن المثبّتين يعرضان صفحة اللغة وأن قائمة اللغات مطابقة للبرنامج."""
import os
import re
import sys

try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, root)

from ajoubi import i18n  # noqa: E402

installer_dir = os.path.join(root, "installer")
page_path = os.path.join(installer_dir, "language_page.iss")
with open(page_path, "r", encoding="utf-8") as fh:
    page = fh.read()

codes = re.findall(r"AddLanguage\('([a-z]{2})'", page)
assert len(codes) == len(set(codes)), "تكرار في قائمة لغات المثبّت"
assert set(codes) == set(i18n.LANGUAGES), (
    sorted(set(codes) ^ set(i18n.LANGUAGES)))
assert len(codes) == 19, len(codes)

assert "SaveStringToFile(ExpandConstant('{app}\\language.txt'), Code, False)" in page
assert "GetUserDefaultUILanguage" in page
assert "{param:APPLANG|}" in page
assert "UninstallDelete" in page
assert 'language.txt' in page
assert "CreateCustomPage(wpWelcome" in page

for name in ("installer_win10.iss", "installer_win7.iss"):
    with open(os.path.join(installer_dir, name), "r", encoding="utf-8") as fh:
        text = fh.read()
    assert '#include "language_page.iss"' in text, name
    assert "DisableWelcomePage=yes" in text, name
    assert 'Name: "english"' in text and 'Name: "arabic"' in text, name
    assert "AppVersion=1.2.0" in text, name
    assert "SourceDir=" in text, name
    assert "OutputDir=" in text, name

print("INSTALLER LANGUAGE TESTS PASSED (19 languages, both installers)")
