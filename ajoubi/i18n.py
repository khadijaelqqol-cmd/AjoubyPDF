# -*- coding: utf-8 -*-
"""نظام تعدد اللغات - 19 لغة مع دعم RTL للعربية والفارسية"""

from .translations_1 import PART1
from .translations_2 import PART2
from .translations_ui import UI_TRANSLATIONS

# ملاحظة: بدون إيموجي الأعلام لأن ويندوز لا يدعمها (تظهر حروفاً مثل SA/GB)
LANGUAGES = {
    "ar": ("العربية (Arabic)", True),
    "en": ("English", False),
    "fr": ("Français (French)", False),
    "es": ("Español (Spanish)", False),
    "de": ("Deutsch (German)", False),
    "it": ("Italiano (Italian)", False),
    "pt": ("Português (Portuguese)", False),
    "tr": ("Türkçe (Turkish)", False),
    "ru": ("Русский (Russian)", False),
    "zh": ("中文（简体）(Chinese)", False),
    "ja": ("日本語 (Japanese)", False),
    "ko": ("한국어 (Korean)", False),
    "hi": ("हिन्दी (Hindi)", False),
    "nl": ("Nederlands (Dutch)", False),
    "pl": ("Polski (Polish)", False),
    "sv": ("Svenska (Swedish)", False),
    "el": ("Ελληνικά (Greek)", False),
    "fa": ("فارسی (Persian)", True),
    "uk": ("Українська (Ukrainian)", False),
}


def _merge(*layers):
    """دمج قواميس اللغات طبقة فوق طبقة (دون استبدال جدول اللغة كاملاً)"""
    out = {}
    for layer in layers:
        for code, table in layer.items():
            out.setdefault(code, {}).update(table)
    return out


TRANSLATIONS = _merge(PART1, PART2, UI_TRANSLATIONS)

_current = "ar"


def set_language(code):
    global _current
    if code in TRANSLATIONS:
        _current = code


def get_language():
    return _current


def is_rtl(code=None):
    return LANGUAGES.get(code or _current, (None, False))[1]


def available_languages():
    return list(LANGUAGES.keys())


def tr(key, *args):
    """ترجمة مفتاح مع fallback إلى الإنجليزية ثم المفتاح نفسه"""
    s = TRANSLATIONS.get(_current, {}).get(key)
    if s is None:
        s = TRANSLATIONS.get("en", {}).get(key, key)
    if args:
        try:
            return s.format(*args)
        except Exception:
            return s
    return s
