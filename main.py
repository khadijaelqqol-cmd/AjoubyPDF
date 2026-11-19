# -*- coding: utf-8 -*-
"""اجوبي PDF - نقطة تشغيل البرنامج"""

import os
import sys

from ajoubi.qt_compat import (
    Qt, QSettings, QTimer, QApplication, QIcon, app_exec, enable_high_dpi,
    app_icon_path,
)
from ajoubi import i18n, APP_NAME, ORG_NAME
from ajoubi.theme import build_qss
from ajoubi.main_window import MainWindow


def _installer_language(base_dir):
    """قراءة اللغة التي كتبها المثبّت في ``language.txt`` (أو نص فارغ)."""
    if base_dir is None:
        if getattr(sys, "frozen", False):
            base_dir = os.path.dirname(sys.executable)
        else:
            base_dir = os.path.dirname(os.path.abspath(__file__))
    try:
        with open(os.path.join(base_dir, "language.txt"),
                  "r", encoding="utf-8-sig") as fh:
            code = fh.read().strip()
    except OSError:
        return ""
    return code if code in i18n.LANGUAGES else ""


def initial_language(settings, base_dir=None):
    """لغة البداية: اختيار المثبّت، ثم المحفوظ في البرنامج، ثم العربية.

    يكتب المثبّت رمز اللغة في ``language.txt`` بجانب البرنامج. يُطبَّق
    الاختيار عند أول تشغيل، أو عند تثبيت/ترقية يختار فيها المثبّت لغة
    مختلفة. وإذا أعاد المستخدم التثبيت باللغة نفسها يبقى اختياره داخل
    البرنامج كما هو.
    """
    code = _installer_language(base_dir)
    if code:
        previous = settings.value("installer_language", "")
        if not settings.contains("language") or previous != code:
            settings.setValue("language", code)
            settings.setValue("installer_language", code)
            return code

    if settings.contains("language"):
        return settings.value("language", "ar")
    return "ar"


def main():
    enable_high_dpi()
    app = QApplication(sys.argv)
    app.setApplicationName(APP_NAME)
    app.setOrganizationName(ORG_NAME)
    # نمط Fusion يعطي مظهراً متطابقاً على ويندوز 7 و10 و11
    app.setStyle("Fusion")
    app.setStyleSheet(build_qss())

    # أيقونة البرنامج
    icon_path = app_icon_path()
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    # استرجاع اللغة المحفوظة أو اللغة التي اختارها المستخدم أثناء التثبيت
    settings = QSettings(ORG_NAME, APP_NAME)
    lang = initial_language(settings)
    i18n.set_language(lang)

    # اتجاه الواجهة: من اليمين لليسار للعربية والفارسية
    if i18n.is_rtl(lang):
        app.setLayoutDirection(Qt.RightToLeft)

    window = MainWindow()
    window.show()

    # فتح الملف مباشرة عند التشغيل عبر «فتح باستخدام» أو سطر الأوامر
    for candidate in sys.argv[1:]:
        if (not candidate.startswith("-")
                and candidate.lower().endswith(".pdf")
                and os.path.exists(candidate)):
            QTimer.singleShot(0, lambda p=candidate: window.load_file(p))
            break

    sys.exit(app_exec(app))


if __name__ == "__main__":
    main()
