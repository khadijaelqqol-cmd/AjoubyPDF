# -*- coding: utf-8 -*-
"""الثيم: ألوان مريحة، أيقونات مرسومة (بدون صور خارجية لتوفير الرام)، وأنماط QSS"""

from .qt_compat import (
    Qt, QColor, QPainter, QPixmap, QIcon, QPen, QFont, QPolygonF, QPointF,
    QPainterPath, QRectF, QSize,
)

# ---------------- لوحة الألوان ----------------
COLORS = {
    "bg":         "#eef2f7",   # خلفية النافذة
    "surface":    "#ffffff",   # الأسطح البيضاء
    "border":     "#dfe6ee",
    "text":       "#26313c",
    "text_soft":  "#667485",
    "accent":     "#2f7de1",   # الأزرق الأساسي
    "accent_hi":  "#4a91ea",
    "accent_lo":  "#1f66c0",
    "accent_soft": "#e7f0fd",
    "success":    "#2e9e5b",
    "warn":       "#f2a33c",
    "danger":     "#dc4b4b",
    "sidebar":    "#f6f9fc",
}

ICON_COLOR = QColor("#3b4757")
ICON_SIZE = 24

# ألوان أيقونات بطاقات الشاشة الرئيسية
CARD_COLORS = {
    "open":   "#2f7de1",
    "images": "#2e9e5b",
    "merge":  "#8a5cd6",
    "guide":  "#e59a24",
}


# ======================================================================
# مصنع الأيقونات: كل الرسم في إحداثيات 22x22 ثم يُقاس لأي حجم
# ======================================================================
def _tri(p, points, fill=True):
    if fill:
        p.setBrush(p.pen().color())
    p.drawPolygon(QPolygonF([QPointF(x, y) for x, y in points]))
    p.setBrush(Qt.NoBrush)


def _arrow_head(p, cx, cy, direction):
    d = 2.4
    y = [cy - d, cy, cy + d]
    xs = [cx + d * direction, cx, cx + d * direction]
    _tri(p, list(zip(xs, y)))


def _draw_open(p):
    p.drawRoundedRect(QRectF(3, 7, 15, 11), 1.5, 1.5)
    p.drawLine(3, 7, 3, 5.5)
    p.drawLine(3, 5.5, 8, 5.5)
    p.drawLine(8, 5.5, 10, 7.5)
    p.drawLine(10, 7.5, 21, 7.5)
    _tri(p, [(6.5, 18), (21, 18), (18.5, 11), (4.5, 11)])


def _draw_save(p):
    p.drawRoundedRect(QRectF(4, 4, 16, 16), 2, 2)
    p.drawLine(8, 4, 8, 8.5)
    p.drawLine(16, 4, 16, 8.5)
    p.drawLine(8, 4, 16, 4)
    p.drawRect(QRectF(8, 13, 8, 6))
    p.drawLine(10, 6.5, 14, 6.5)


def _draw_recent(p):
    p.drawEllipse(QRectF(5, 4.5, 14, 14))
    p.drawLine(12, 8, 12, 11.8)
    p.drawLine(12, 11.8, 15, 13.6)
    # سهم صغير للأعلى
    p.drawLine(18.5, 4.5, 18.5, 8)
    p.drawLine(18.5, 4.5, 15.5, 4.5)


def _draw_home(p):
    p.drawLine(3.5, 10.5, 11, 4)
    p.drawLine(11, 4, 18.5, 10.5)
    p.drawLine(5.5, 9.2, 5.5, 19)
    p.drawLine(16.5, 9.2, 16.5, 19)
    p.drawLine(5.5, 19, 16.5, 19)
    p.drawRect(QRectF(9.2, 13.5, 3.6, 5.5))


def _draw_guide(p):
    # كتاب مفتوح
    p.drawRoundedRect(QRectF(3.5, 5, 15, 13), 2, 2)
    p.drawLine(11, 6.2, 11, 17)
    p.drawLine(6, 8.5, 9, 8.5)
    p.drawLine(6, 11, 9, 11)
    p.drawLine(13, 8.5, 16, 8.5)
    p.drawLine(13, 11, 16, 11)


def _draw_help(p):
    p.drawEllipse(QRectF(3.5, 3.5, 15, 15))
    f = QFont("Segoe UI", 10)
    f.setBold(True)
    p.setFont(f)
    p.drawText(QRectF(3.5, 3.2, 15, 15), Qt.AlignCenter, "?")


def _draw_images(p):
    p.drawRoundedRect(QRectF(3, 5, 16, 13), 2, 2)
    p.drawEllipse(QRectF(6.2, 7.6, 3.1, 3.1))
    path = QPainterPath()
    path.moveTo(4.5, 16.5)
    path.lineTo(9.5, 11.5)
    path.lineTo(13, 15)
    path.lineTo(15.5, 12.5)
    path.lineTo(19, 16.5)
    p.drawPath(path)


def _draw_merge(p):
    p.drawRoundedRect(QRectF(3, 4, 9, 14), 1.5, 1.5)
    p.drawRoundedRect(QRectF(10, 4, 9, 14), 1.5, 1.5)
    p.drawLine(11, 4, 11, 18)
    p.drawLine(8, 8, 14, 8)
    p.drawLine(8, 12, 14, 12)


def _draw_split(p):
    p.drawRoundedRect(QRectF(3, 4, 16, 14), 1.5, 1.5)
    p.drawLine(11, 4, 11, 18)
    _tri(p, [(8.5, 8.5), (8.5, 13.5), (5.5, 11)])
    _tri(p, [(13.5, 8.5), (13.5, 13.5), (16.5, 11)])


def _draw_compress(p):
    p.drawRoundedRect(QRectF(4, 4, 14, 14), 2, 2)
    p.drawLine(11, 3.5, 11, 8)
    p.drawLine(11, 8, 8.5, 5.5)
    p.drawLine(11, 8, 13.5, 5.5)
    p.drawLine(11, 18.5, 11, 14)
    p.drawLine(11, 14, 8.5, 16.5)
    p.drawLine(11, 14, 13.5, 16.5)


def _draw_lock(p, locked=True):
    p.drawRoundedRect(QRectF(5, 10, 12, 8.5), 1.8, 1.8)
    if locked:
        p.drawArc(QRectF(7, 4, 8, 11), 0, 180 * 16)
    else:
        p.drawArc(QRectF(7, 3.5, 8, 11), 30 * 16, 150 * 16)
    p.drawLine(11, 13, 11, 15.5)


def _draw_export(p):
    p.drawRoundedRect(QRectF(3, 5, 12, 12), 2, 2)
    p.drawLine(9, 11, 12, 11)
    p.drawLine(15.5, 4, 15.5, 11)
    p.drawLine(15.5, 4, 12.5, 7)
    p.drawLine(15.5, 4, 18.5, 7)


def _draw_text(p):
    f = QFont("Segoe UI", 12)
    f.setBold(True)
    p.setFont(f)
    p.drawText(QRectF(2, 3, 20, 18), Qt.AlignCenter, "A")


def _draw_rotate(p):
    p.drawArc(QRectF(5, 5, 12, 12), 40 * 16, 270 * 16)
    _tri(p, [(16.2, 4.2), (19.5, 6.3), (16.2, 8.4)])


def _draw_delete(p):
    p.drawLine(5, 7, 17, 7)
    p.drawLine(9, 5, 13, 5)
    p.drawRoundedRect(QRectF(7, 7, 8, 11), 1.5, 1.5)
    p.drawLine(9.5, 9.5, 9.5, 15.5)
    p.drawLine(12.5, 9.5, 12.5, 15.5)


def _draw_sidebar(p):
    p.drawRoundedRect(QRectF(3.5, 4.5, 15, 13), 2, 2)
    p.drawLine(9, 4.5, 9, 17.5)
    p.drawLine(5.5, 8, 7, 8)
    p.drawLine(5.5, 11, 7, 11)


def _draw_close(p):
    p.drawLine(6, 6, 16, 16)
    p.drawLine(16, 6, 6, 16)


def _draw_search(p):
    p.drawEllipse(QRectF(4, 4, 11, 11))
    p.drawLine(15.5, 15.5, 20.5, 20.5)


def _draw_sliders(p):
    p.drawLine(4, 7, 18, 7)
    p.drawLine(4, 12, 18, 12)
    p.drawLine(4, 17, 18, 17)
    p.drawEllipse(QRectF(7.5, 5.2, 3.5, 3.5))
    p.drawEllipse(QRectF(12.5, 10.2, 3.5, 3.5))
    p.drawEllipse(QRectF(6.5, 15.2, 3.5, 3.5))


def _draw_page(p):
    path = QPainterPath()
    path.moveTo(6, 3.5)
    path.lineTo(13, 3.5)
    path.lineTo(17, 7.5)
    path.lineTo(17, 18.5)
    path.lineTo(6, 18.5)
    path.closeSubpath()
    p.drawPath(path)
    p.drawLine(13, 3.5, 13, 7.5)
    p.drawLine(13, 7.5, 17, 7.5)


def _draw_pointer(p):
    _tri(p, [(6, 3.5), (6, 17.5), (10, 14), (12.8, 19.5), (15.2, 18.4),
             (12.4, 13), (17.5, 12.5)])


def _draw_highlight(p):
    path = QPainterPath()
    path.moveTo(14.5, 4.5)
    path.lineTo(10.5, 10.5)
    p.drawPath(path)
    _tri(p, [(10.5, 10.5), (14.5, 4.5), (16.5, 8.5), (12.5, 12.0)])
    p.drawLine(4, 19.5, 20, 19.5)


def _draw_note(p):
    p.drawRoundedRect(QRectF(4, 4, 16, 11), 2.5, 2.5)
    _tri(p, [(8.5, 15), (8.5, 19.5), (12.5, 15)])


def _draw_freehand(p):
    path = QPainterPath()
    path.moveTo(4, 18)
    path.cubicTo(8, 4, 11, 24, 14.5, 11)
    path.cubicTo(16.5, 4, 19, 8, 20, 6.5)
    p.drawPath(path)


def _draw_sign(p):
    path = QPainterPath()
    path.moveTo(3, 15)
    path.cubicTo(6, 8, 9, 20, 12, 13)
    path.cubicTo(13.5, 9.5, 15, 14, 17, 12.5)
    p.drawPath(path)
    p.drawLine(4, 19, 20, 19)


def _draw_zoom(p, plus=True):
    p.drawEllipse(QRectF(4, 4, 11.5, 11.5))
    p.drawLine(15.5, 15.5, 20.5, 20.5)
    p.drawLine(6.8, 9.75, 12.8, 9.75)
    if plus:
        p.drawLine(9.8, 6.75, 9.8, 12.75)


def _draw_fit_width(p):
    p.drawLine(5.5, 12, 16.5, 12)
    _arrow_head(p, 3.5, 12, -1)
    _arrow_head(p, 18.5, 12, 1)


def _draw_fit_page(p):
    p.drawRoundedRect(QRectF(5, 5, 12, 12), 1.5, 1.5)
    p.drawLine(6.5, 8, 8.5, 8)
    p.drawLine(6.5, 16, 8.5, 16)
    p.drawLine(15.5, 8, 13.5, 8)
    p.drawLine(15.5, 16, 13.5, 16)


def _draw_first(p):
    p.drawLine(6, 5, 6, 19)
    _tri(p, [(18.5, 5.5), (18.5, 18.5), (8.5, 12)])


def _draw_prev(p):
    _tri(p, [(16.5, 5.5), (16.5, 18.5), (7.5, 12)])


def _draw_next(p):
    _tri(p, [(7.5, 5.5), (7.5, 18.5), (16.5, 12)])


def _draw_last(p):
    p.drawLine(18, 5, 18, 19)
    _tri(p, [(5.5, 5.5), (5.5, 18.5), (15.5, 12)])


_ICONS = {
    "open": _draw_open, "save": _draw_save, "recent": _draw_recent,
    "home": _draw_home, "guide": _draw_guide, "help": _draw_help,
    "images": _draw_images, "merge": _draw_merge, "split": _draw_split,
    "compress": _draw_compress,
    "protect": lambda p: _draw_lock(p, True),
    "unlock": lambda p: _draw_lock(p, False),
    "export": _draw_export, "text": _draw_text, "rotate": _draw_rotate,
    "delete": _draw_delete, "sidebar": _draw_sidebar, "close": _draw_close,
    "search": _draw_search, "sliders": _draw_sliders, "page": _draw_page,
    "pointer": _draw_pointer, "highlight": _draw_highlight,
    "note": _draw_note, "freehand": _draw_freehand, "sign": _draw_sign,
    "zoom_in": lambda p: _draw_zoom(p, True),
    "zoom_out": lambda p: _draw_zoom(p, False),
    "fit_width": _draw_fit_width, "fit_page": _draw_fit_page,
    "first": _draw_first, "prev": _draw_prev,
    "next": _draw_next, "last": _draw_last,
}


def pixmap(name, size=ICON_SIZE, color=None, mirror=False):
    """يرسم أيقونة بحجم دقيق (mirror يقلبها أفقياً لواجهات RTL)"""
    draw = _ICONS.get(name)
    if not draw:
        return QPixmap()
    scale = 2.0
    px = max(8, int(round(size * scale)))
    pm = QPixmap(px, px)
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(px / 22.0, px / 22.0)
    if mirror:
        p.translate(22.0, 0.0)
        p.scale(-1.0, 1.0)
    pen = QPen(color if color is not None else ICON_COLOR, 1.8)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    p.setPen(pen)
    p.setBrush(Qt.NoBrush)
    draw(p)
    p.end()
    return pm


def icon(name, size=ICON_SIZE, color=None, mirror=False):
    """أيقونة جاهزة بالاسم"""
    pm = pixmap(name, size, color, mirror)
    return QIcon(pm) if not pm.isNull() else QIcon()


def card_icon(name, bg_color, size=46):
    """أيقونة بطاقة: مربع ملوّن بزوايا دائرية + الرمز بالأبيض (QPixmap)"""
    pm = QPixmap(int(size * 2), int(size * 2))
    pm.fill(Qt.transparent)
    p = QPainter(pm)
    p.setRenderHint(QPainter.Antialiasing)
    p.scale(2.0, 2.0)
    p.setPen(Qt.NoPen)
    p.setBrush(QColor(bg_color))
    p.drawRoundedRect(QRectF(0, 0, size, size), size * 0.30, size * 0.30)
    p.end()
    glyph = pixmap(name, size * 0.58, QColor("#ffffff"))
    painter = QPainter(pm)
    painter.setRenderHint(QPainter.SmoothPixmapTransform)
    offset = (size * 2 - glyph.width()) / 2.0
    painter.drawPixmap(QPointF(offset, offset), glyph)
    painter.end()
    return pm


def icon_size(size):
    return QSize(int(size), int(size))


# ======================================================================
# ورقة الأنماط QSS — ثيم فاتح بسيط ومريح
# ======================================================================
def build_qss():
    c = COLORS
    return f"""
* {{
    font-family: "Segoe UI", "Tahoma", "Arial";
    font-size: 10pt;
    color: {c['text']};
}}
QMainWindow, QDialog {{ background: {c['bg']}; }}

/* ---------- شريط القوائم ---------- */
QMenuBar {{
    background: {c['surface']};
    border-bottom: 1px solid {c['border']};
    padding: 2px 8px;
}}
QMenuBar::item {{ padding: 6px 12px; border-radius: 6px; }}
QMenuBar::item:selected {{ background: {c['accent_soft']}; }}
QMenu {{
    background: {c['surface']}; border: 1px solid {c['border']};
    border-radius: 8px; padding: 6px;
}}
QMenu::item {{ padding: 7px 30px 7px 14px; border-radius: 6px; margin: 1px 2px; }}
QMenu::item:selected {{ background: {c['accent']}; color: white; }}
QMenu::item:disabled {{ color: #a9b4c1; }}
QMenu::separator {{ height: 1px; background: {c['border']}; margin: 5px 8px; }}
QMenu::icon {{ padding-right: 6px; }}

/* ---------- أشرطة الأدوات ---------- */
QToolBar {{
    background: {c['surface']};
    border: none;
    border-bottom: 1px solid {c['border']};
    padding: 3px 8px;
    spacing: 2px;
}}
QToolBar::separator {{
    width: 1px; background: {c['border']}; margin: 8px 7px;
}}
QToolBar QToolButton {{
    background: transparent; border: 1px solid transparent;
    border-radius: 8px; padding: 4px 7px;
    font-size: 9pt; color: {c['text']};
    min-width: 50px;
}}
QToolBar QToolButton:hover {{ background: {c['accent_soft']}; }}
QToolBar QToolButton:pressed {{ background: #d8e7fb; }}
QToolBar QToolButton:checked {{
    background: {c['accent_soft']};
    border: 1px solid {c['accent']};
    color: {c['accent_lo']};
}}
QToolBar QToolButton:checked:hover {{ background: #dbeafc; }}
QToolBar QToolButton:disabled {{ color: #a9b4c1; }}

/* ---------- الحقول ---------- */
QLineEdit, QSpinBox {{
    background: white; border: 1px solid #cfd8e3;
    border-radius: 8px; padding: 5px 9px;
    selection-background-color: {c['accent']};
}}
QLineEdit:focus, QSpinBox:focus {{ border: 1px solid {c['accent']}; }}
QLineEdit:disabled {{ background: #f4f6f9; color: #a9b4c1; }}
QSpinBox::up-button, QSpinBox::down-button {{
    width: 15px; border: none; background: transparent;
}}
QSpinBox::up-button:hover, QSpinBox::down-button:hover {{
    background: {c['accent_soft']}; border-radius: 4px;
}}
QToolTip {{
    background: {c['text']}; color: white; border: none;
    padding: 6px 10px; border-radius: 6px; font-size: 9pt;
}}

/* ---------- منطقة العرض ---------- */
QScrollArea {{ border: none; background: {c['bg']}; }}
QWidget#canvas {{ background: {c['bg']}; }}
QLabel#pageLabel {{
    background: white;
    border: 1px solid #dbe3ec;
}}
QWidget#homePanel {{ background: {c['bg']}; }}

/* ---------- الشاشة الرئيسية ---------- */
QLabel#homeTitle {{
    font-size: 25pt; font-weight: 600; color: {c['text']};
    background: transparent;
}}
QLabel#homeSubtitle {{
    font-size: 11.5pt; color: {c['text_soft']}; background: transparent;
}}
QFrame#homeCard {{
    background: {c['surface']};
    border: 1px solid {c['border']};
    border-radius: 14px;
}}
QFrame#homeCard:hover {{
    border: 1px solid {c['accent']};
    background: #f7fbff;
}}
QLabel#homeCardTitle {{
    font-size: 10.5pt; font-weight: 600; color: {c['text']};
    background: transparent;
}}
QLabel#homeCardHint {{
    font-size: 9pt; color: {c['text_soft']};
    background: transparent;
}}
QToolButton#homeCard:pressed {{ background: {c['accent_soft']}; }}
QLabel#dropHint {{
    font-size: 10.5pt; color: {c['text_soft']};
    border: 2px dashed #c8d4e2; border-radius: 14px;
    padding: 14px 26px; background: #f8fafd;
}}
QLabel#dropHint[dragActive="true"] {{
    border: 2px dashed {c['accent']};
    background: {c['accent_soft']};
    color: {c['accent_lo']};
}}
QLabel#recentTitle {{
    font-size: 10pt; font-weight: 600; color: {c['text_soft']};
    background: transparent;
}}
QToolButton#recentItem {{
    background: transparent; border: none; color: {c['accent_lo']};
    padding: 5px 10px; border-radius: 6px; text-align: left;
    font-size: 10pt;
}}
QToolButton#recentItem:hover {{ background: {c['accent_soft']}; }}
QLabel#recentEmpty {{ color: {c['text_soft']}; font-size: 9.5pt; background: transparent; }}

/* ---------- لوحة الصور المصغرة ---------- */
QListWidget#sidebar {{
    background: {c['sidebar']}; border: none; outline: 0;
    padding: 6px 2px;
}}
QListWidget#sidebar::item {{
    margin: 5px 6px; border-radius: 10px; padding: 2px;
    color: {c['text_soft']};
}}
QListWidget#sidebar::item:hover {{ background: {c['accent_soft']}; }}
QListWidget#sidebar::item:selected {{
    background: transparent;
    border: 2px solid {c['accent']};
}}

/* ---------- أشرطة التمرير ---------- */
QScrollBar:vertical {{ background: transparent; width: 11px; margin: 2px; }}
QScrollBar::handle:vertical {{
    background: #c3ccd8; border-radius: 5px; min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: #9fb0c2; }}
QScrollBar:horizontal {{ background: transparent; height: 11px; margin: 2px; }}
QScrollBar::handle:horizontal {{
    background: #c3ccd8; border-radius: 5px; min-width: 30px;
}}
QScrollBar::handle:horizontal:hover {{ background: #9fb0c2; }}
QScrollBar::add-line, QScrollBar::sub-line {{ width: 0; height: 0; }}
QScrollBar::add-page, QScrollBar::sub-page {{ background: transparent; }}

/* ---------- شريط الحالة ---------- */
QStatusBar {{
    background: {c['surface']}; color: {c['text_soft']};
    border-top: 1px solid {c['border']};
}}
QStatusBar::item {{ border: none; }}
QStatusBar QLabel {{ color: {c['text_soft']}; padding: 0 8px; }}

/* ---------- الأزرار ---------- */
QPushButton {{
    background: {c['accent']}; color: white; border: none;
    border-radius: 8px; padding: 8px 22px; font-weight: 600;
}}
QPushButton:hover {{ background: {c['accent_hi']}; }}
QPushButton:pressed {{ background: {c['accent_lo']}; }}
QPushButton:disabled {{ background: #b9c6d4; }}
QPushButton#flatButton {{
    background: white; color: {c['text']};
    border: 1px solid {c['border']};
}}
QPushButton#flatButton:hover {{ background: {c['accent_soft']}; }}

/* ---------- الجداول والحوارات ---------- */
QTableWidget {{
    background: white; border: 1px solid {c['border']};
    border-radius: 8px; gridline-color: {c['border']};
}}
QHeaderView::section {{
    background: {c['sidebar']}; border: none;
    border-bottom: 1px solid {c['border']};
    padding: 7px; font-weight: 600;
}}
QRadioButton {{ spacing: 6px; padding: 3px; }}
QSplitter::handle {{ background: {c['border']}; width: 1px; }}
QDialogButtonBox QPushButton {{ min-width: 84px; }}

/* ---------- دليل الاستخدام ---------- */
QDialog#guideDialog {{ background: {c['surface']}; }}
QLabel#guideTitle {{
    font-size: 18pt; font-weight: 600; color: {c['text']};
    background: transparent;
}}
QLabel#guideSubtitle {{
    font-size: 10pt; color: {c['text_soft']}; background: transparent;
}}
QTextBrowser#guideView {{
    background: white; border: 1px solid {c['border']};
    border-radius: 10px; padding: 6px;
}}
"""
