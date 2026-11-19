# -*- coding: utf-8 -*-
"""النافذة الرئيسية لبرنامج اجوبي PDF

واجهة بسيطة وديناميكية:
  • شاشة رئيسية كبيرة بأزرار واضحة عند عدم وجود ملف.
  • شريط أدوات أساسي دائماً + شريط أدوات الرسم يظهر عند فتح ملف فقط.
  • صور مصغرة تُرسم عند الحاجة فقط (توفير للرام والسرعة).
  • عرض كسول لصفحات المستند (الصفحات المرئية فقط).
"""

import os
from contextlib import contextmanager
from html import escape as html_escape

try:
    import pymupdf as fitz  # PyMuPDF >= 2.0
except ImportError:
    import fitz  # إصدارات أقدم

from .qt_compat import (
    Qt, QSettings, QRectF, QSize, QAction, QActionGroup, QImage, QPixmap,
    QPainter, QColor, QKeySequence, QIcon, QPixmapCache, QPen, QTimer, QEvent,
    QMainWindow, QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout,
    QGridLayout, QListWidget, QListWidgetItem, QToolBar, QStatusBar,
    QFileDialog, QMessageBox, QInputDialog, QSpinBox, QLineEdit, QToolButton,
    QSizePolicy, QSplitter, QDialog, dialog_exec, QFrame, QMenu,
    app_png_path,
)

from . import i18n, pdf_ops
from . import __version__, APP_NAME, ORG_NAME
from .dialogs import SplitDialog, FormsDialog, GuideDialog
from .theme import icon as theme_icon, card_icon, CARD_COLORS

PDF_FILTER = "PDF (*.pdf)"
IMG_FILTER = "Images (*.png *.jpg *.jpeg *.bmp *.gif *.webp)"
IMG_EXTS = (".png", ".jpg", ".jpeg", ".bmp", ".gif", ".webp")

# الحد الأقصى لبكسلات الصفحة الواحدة عند العرض (حماية الرام عند التكبير الكبير)
MAX_RENDER_PIXELS = 12_000_000
MIN_ZOOM, MAX_ZOOM = 0.1, 5.0
THUMB_WIDTH = 104
RECENT_MAX = 6

# مفاتيح الترجمة لأدوات التعليق (إصلاح: المفتاح الصحيح tool_signature)
TOOL_KEYS = {
    "pointer": "tool_pointer",
    "highlight": "tool_highlight",
    "note": "tool_note",
    "freehand": "tool_freehand",
    "text": "tool_text",
    "sign": "tool_signature",
}
TOOL_MODES = tuple(TOOL_KEYS.keys())


def _clamp(value, low, high):
    return max(low, min(high, value))


# ======================================================================
# بطاقة في الشاشة الرئيسية
# ======================================================================
class HomeCard(QFrame):
    """بطاقة كبيرة قابلة للنقر: أيقونة + عنوان + شرح قصير"""

    def __init__(self, icon_name, color, title, hint, callback, parent=None):
        super().__init__(parent)
        self.setObjectName("homeCard")
        self.setFrameShape(QFrame.NoFrame)
        self.setCursor(Qt.PointingHandCursor)
        self.setMinimumSize(158, 148)
        self.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.setToolTip(hint)
        self._callback = callback

        layout = QVBoxLayout(self)
        layout.setContentsMargins(14, 12, 14, 10)
        layout.setSpacing(5)

        self.icon_label = QLabel(self)
        self.icon_label.setPixmap(card_icon(icon_name, color, 40))
        self.icon_label.setAlignment(Qt.AlignCenter)
        self.icon_label.setStyleSheet("background: transparent;")
        self.icon_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.title_label = QLabel(title, self)
        self.title_label.setObjectName("homeCardTitle")
        self.title_label.setAlignment(Qt.AlignCenter)
        self.title_label.setWordWrap(True)
        self.title_label.setMinimumHeight(20)
        self.title_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        self.hint_label = QLabel(hint, self)
        self.hint_label.setObjectName("homeCardHint")
        self.hint_label.setAlignment(Qt.AlignCenter)
        self.hint_label.setWordWrap(True)
        self.hint_label.setMinimumHeight(38)
        self.hint_label.setAttribute(Qt.WA_TransparentForMouseEvents, True)

        layout.addWidget(self.icon_label, 0, Qt.AlignHCenter)
        layout.addWidget(self.title_label)
        layout.addWidget(self.hint_label)
        layout.addStretch(1)

    def set_texts(self, title, hint):
        self.title_label.setText(title)
        self.hint_label.setText(hint)
        self.setToolTip(hint)

    def mouseReleaseEvent(self, ev):
        if ev.button() == Qt.LeftButton and self.rect().contains(ev.pos()):
            self._callback()
            return
        super().mouseReleaseEvent(ev)


# ======================================================================
# الشاشة الرئيسية (تظهر عند عدم فتح ملف)
# ======================================================================
class HomeWidget(QWidget):
    """شاشة ترحيب ديناميكية: تتكيّف البطاقات مع عرض النافذة"""

    def __init__(self, handlers, parent=None):
        super().__init__(parent)
        self.setObjectName("homePanel")
        self._handlers = handlers
        self._cols = 0
        self._recent_paths = []

        outer = QVBoxLayout(self)
        outer.setContentsMargins(26, 8, 26, 8)
        outer.setSpacing(0)
        outer.addStretch(1)

        self.logo = QLabel(self)
        self.logo.setAlignment(Qt.AlignCenter)
        pm = QPixmap(app_png_path())
        if not pm.isNull():
            self.logo.setPixmap(pm.scaled(72, 72, Qt.KeepAspectRatio,
                                          Qt.SmoothTransformation))

        self.title = QLabel(self)
        self.title.setObjectName("homeTitle")
        self.title.setAlignment(Qt.AlignCenter)
        self.title.setMinimumHeight(48)
        self.title.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.subtitle = QLabel(self)
        self.subtitle.setObjectName("homeSubtitle")
        self.subtitle.setAlignment(Qt.AlignCenter)
        self.subtitle.setMinimumHeight(28)
        self.subtitle.setMaximumWidth(700)
        self.subtitle.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Minimum)

        self.cards_host = QWidget(self)
        self.cards_host.setMaximumWidth(1000)
        self.cards_host.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
        self.grid = QGridLayout(self.cards_host)
        self.grid.setContentsMargins(0, 0, 0, 0)
        self.grid.setHorizontalSpacing(14)
        self.grid.setVerticalSpacing(14)

        self.cards = []
        card_defs = (
            ("open", CARD_COLORS["open"], "home_open", "home_open_hint",
             handlers["open"]),
            ("images", CARD_COLORS["images"], "home_images", "home_images_hint",
             handlers["images"]),
            ("merge", CARD_COLORS["merge"], "home_merge", "home_merge_hint",
             handlers["merge"]),
            ("guide", CARD_COLORS["guide"], "home_guide", "home_guide_hint",
             handlers["guide"]),
        )
        for icon_name, color, title_key, hint_key, callback in card_defs:
            card = HomeCard(icon_name, color, i18n.tr(title_key),
                            i18n.tr(hint_key), callback, self.cards_host)
            card._title_key = title_key
            card._hint_key = hint_key
            self.cards.append(card)

        self.drop = QLabel(self)
        self.drop.setObjectName("dropHint")
        self.drop.setAlignment(Qt.AlignCenter)
        self.drop.setMinimumHeight(54)
        self.drop.setMaximumWidth(700)
        self.drop.setSizePolicy(QSizePolicy.Preferred, QSizePolicy.Fixed)

        self.recent_title = QLabel(self)
        self.recent_title.setObjectName("recentTitle")
        self.recent_title.setAlignment(Qt.AlignCenter)
        self.recent_title.setMinimumHeight(20)

        self.recent_host = QWidget(self)
        self.recent_host.setMaximumWidth(620)
        self.recent_layout = QVBoxLayout(self.recent_host)
        self.recent_layout.setContentsMargins(0, 0, 0, 0)
        self.recent_layout.setSpacing(2)

        outer.addWidget(self.logo, 0, Qt.AlignHCenter)
        outer.addSpacing(6)
        outer.addWidget(self.title, 0, Qt.AlignHCenter)
        outer.addWidget(self.subtitle, 0, Qt.AlignHCenter)
        outer.addSpacing(16)
        outer.addWidget(self.cards_host, 0, Qt.AlignHCenter)
        outer.addSpacing(14)
        outer.addWidget(self.drop, 0, Qt.AlignHCenter)
        outer.addSpacing(16)
        outer.addWidget(self.recent_title, 0, Qt.AlignHCenter)
        outer.addSpacing(2)
        outer.addWidget(self.recent_host, 0, Qt.AlignHCenter)
        outer.addStretch(1)

        self.retranslate()

    # ------------------------------------------------------------------
    def retranslate(self):
        self.title.setText(i18n.tr("home_welcome"))
        self.subtitle.setText(i18n.tr("home_subtitle"))
        self.drop.setText(i18n.tr("home_drop"))
        self.recent_title.setText(i18n.tr("home_recent"))
        for card in self.cards:
            card.set_texts(i18n.tr(card._title_key), i18n.tr(card._hint_key))
        self.set_recent(self._recent_paths)

    def set_recent(self, paths):
        self._recent_paths = list(paths or [])
        while self.recent_layout.count():
            item = self.recent_layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.hide()
                widget.setParent(None)
                widget.deleteLater()

        valid = [p for p in self._recent_paths if os.path.exists(p)][:3]
        if not valid:
            empty = QLabel(i18n.tr("home_no_recent"), self.recent_host)
            empty.setObjectName("recentEmpty")
            empty.setAlignment(Qt.AlignCenter)
            empty.setMinimumHeight(30)
            self.recent_layout.addWidget(empty)
            return

        for path in valid:
            btn = QToolButton(self.recent_host)
            btn.setObjectName("recentItem")
            btn.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
            btn.setIcon(theme_icon("page", 18))
            btn.setText(os.path.basename(path))
            btn.setToolTip(path)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.clicked.connect(
                lambda *a, p=path: self._handlers["recent"](p))
            self.recent_layout.addWidget(btn)

    def reflow(self, width):
        """إعادة ترتيب البطاقات حسب العرض: 4 أو 2 أو 1 في الصف"""
        avail = max(300, int(width) - 90)
        cols = 4 if avail >= 700 else (2 if avail >= 380 else 1)
        if cols == self._cols:
            return
        self._cols = cols
        for card in self.cards:
            self.grid.removeWidget(card)
        for i, card in enumerate(self.cards):
            self.grid.addWidget(card, i // cols, i % cols)
        for col in range(4):
            self.grid.setColumnStretch(col, 1 if col < cols else 0)

    def set_drag_active(self, active):
        self.drop.setProperty("dragActive", bool(active))
        self.drop.style().unpolish(self.drop)
        self.drop.style().polish(self.drop)

    def set_compact(self, compact):
        """في النوافذ القصيرة نخفي الشعار لتظهر كل البطاقات دون تمرير"""
        compact = bool(compact)
        if getattr(self, "_compact", None) == compact:
            return
        self._compact = compact
        self.logo.setVisible(not compact)


# ======================================================================
# عنصر صفحة: يعرض الصورة ويتعامل مع نقرات/سحب المستخدم حسب الأداة النشطة
# ======================================================================
class PageLabel(QLabel):
    def __init__(self, index, window, parent=None):
        super().__init__(parent)
        self.index = index
        self.win = window
        self.zoom = 1.0
        self._drag_pts = []
        self._rubber = None
        self.setObjectName("pageLabel")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Fixed)
        self.setAlignment(Qt.AlignCenter)
        self.setScaledContents(True)

    def _page_pt(self, ev):
        # توافق Qt5/Qt6: position() غير موجودة في PySide2
        try:
            p = ev.position()
        except AttributeError:
            p = ev.localPos()
        return fitz.Point(p.x() / self.zoom, p.y() / self.zoom)

    def mousePressEvent(self, ev):
        mode = self.win.tool_mode
        if ev.button() == Qt.LeftButton and self.win.doc:
            if mode in ("note", "text", "sign"):
                self.win.on_page_click(self.index, self._page_pt(ev))
                return
            if mode in ("highlight", "freehand"):
                self._drag_pts = [self._page_pt(ev)]
                self._rubber = None
                return
        super().mousePressEvent(ev)

    def mouseMoveEvent(self, ev):
        if self._drag_pts:
            pt = self._page_pt(ev)
            if self.win.tool_mode == "freehand":
                self._drag_pts.append(pt)
            else:
                self._rubber = (self._drag_pts[0], pt)
            self.update()
            return
        super().mouseMoveEvent(ev)

    def mouseReleaseEvent(self, ev):
        if self._drag_pts:
            pts = self._drag_pts
            rect = self._rubber
            self._drag_pts = []
            self._rubber = None
            self.update()
            if self.win.tool_mode == "highlight" and rect:
                self.win.on_highlight(self.index, rect)
            elif self.win.tool_mode == "freehand" and len(pts) > 1:
                self.win.on_freehand(self.index, pts)
            return
        super().mouseReleaseEvent(ev)

    def paintEvent(self, ev):
        super().paintEvent(ev)
        if not self._drag_pts:
            return
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        if self.win.tool_mode == "freehand":
            pen = QPen(QColor(200, 30, 30), 2)
            painter.setPen(pen)
            pts = [pt * self.zoom for pt in self._drag_pts]
            for a, b in zip(pts, pts[1:]):
                painter.drawLine(a.x, a.y, b.x, b.y)
        else:
            painter.setPen(QPen(QColor(30, 120, 220), 1, Qt.DashLine))
            painter.setBrush(QColor(255, 230, 0, 60))
            r0, r1 = self._rubber or (self._drag_pts[0], self._drag_pts[0])
            x0, x1 = sorted((r0.x * self.zoom, r1.x * self.zoom))
            y0, y1 = sorted((r0.y * self.zoom, r1.y * self.zoom))
            painter.drawRect(QRectF(x0, y0, x1 - x0, y1 - y0))
        painter.end()


# ======================================================================
# النافذة الرئيسية
# ======================================================================
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings(ORG_NAME, APP_NAME)

        self.doc = None
        self.file_path = None
        self.dirty = False
        self.zoom = 1.2
        self.zoom_mode = "fit_width"
        self.tool_mode = "pointer"
        self.sign_path = None
        self._password = None
        self.search_hits = {}
        self.page_labels = []
        self._page_sizes = []
        self._thumb_cache = {}
        self._thumb_loaded = set()
        self._thumb_item_h = 154
        self._sidebar_user_visible = self._setting_bool("sidebar_visible", True)
        self._sidebar_forced = False
        self._sidebar_auto_hidden = False
        self._searching = False
        self._first_show = True
        self.recent = self._load_recent()

        QPixmapCache.setCacheLimit(32768)  # 32 MB — يقلّل استهلاك الرام
        self.setAcceptDrops(True)
        self.setMinimumSize(820, 560)
        self.resize(1180, 780)

        self._refit_timer = QTimer(self)
        self._refit_timer.setSingleShot(True)
        self._refit_timer.timeout.connect(self._apply_fit)

        self._build_widgets()
        self._build_toolbar()
        self._build_shortcuts()
        self._retranslate()
        self._restore_state()
        self._show_document(False)
        self._update_title()
        self._update_actions_enabled()

    # ------------------------------------------------------------------
    # إعدادات محفوظة
    # ------------------------------------------------------------------
    def _setting_bool(self, key, default):
        value = self.settings.value(key, default)
        if isinstance(value, bool):
            return value
        return str(value).strip().lower() not in ("false", "0", "", "none")

    def _restore_state(self):
        geo = self.settings.value("geometry")
        if geo:
            try:
                self.restoreGeometry(geo)
            except Exception:
                pass
        self.act_sidebar.setChecked(self._sidebar_user_visible)
        self._update_sidebar()

    # ------------------------------------------------------------------
    # بناء الواجهة
    # ------------------------------------------------------------------
    def _build_widgets(self):
        self.splitter = QSplitter(Qt.Horizontal, self)
        self.setCentralWidget(self.splitter)

        # لوحة الصور المصغرة (تظهر فقط عند فتح ملف)
        self.thumb_list = QListWidget(self)
        self.thumb_list.setObjectName("sidebar")
        self.thumb_list.setIconSize(QSize(THUMB_WIDTH, 140))
        self.thumb_list.setFixedWidth(146)
        self.thumb_list.setUniformItemSizes(True)
        self.thumb_list.setSpacing(2)
        self.thumb_list.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.thumb_list.currentRowChanged.connect(self._goto_row)
        self.thumb_list.verticalScrollBar().valueChanged.connect(
            self._on_thumb_scroll)
        self.splitter.addWidget(self.thumb_list)

        # منطقة العرض
        self.scroll = QScrollArea(self)
        self.scroll.setWidgetResizable(True)
        self.scroll.setAlignment(Qt.AlignHCenter)
        self.scroll.setFrameShape(QFrame.NoFrame)
        self.canvas = QWidget(self)
        self.canvas.setObjectName("canvas")
        self.canvas_layout = QVBoxLayout(self.canvas)
        self.canvas_layout.setContentsMargins(18, 18, 18, 18)
        self.canvas_layout.setSpacing(16)

        self.home = HomeWidget({
            "open": self.open_file,
            "images": self.images_to_pdf,
            "merge": self.merge_files,
            "guide": self.show_guide,
            "recent": self._open_recent,
        }, self.canvas)
        self.canvas_layout.addWidget(self.home)
        self.canvas_layout.addStretch(1)

        self.scroll.setWidget(self.canvas)
        self.scroll.verticalScrollBar().valueChanged.connect(
            self._on_scroll_changed)
        # تكبير بعجلة الفأرة مع Ctrl (حتى فوق الصفحة أو الهامش)
        self.scroll.viewport().installEventFilter(self)
        self.canvas.installEventFilter(self)
        self.splitter.addWidget(self.scroll)
        self.splitter.setStretchFactor(1, 1)
        self.splitter.setSizes([146, 1034])
        self.splitter.setCollapsible(0, True)

        # شريط الحالة
        self.status = QStatusBar(self)
        self.setStatusBar(self.status)
        self.page_label = QLabel(self)
        self.zoom_label = QLabel(self)
        self.status.addPermanentWidget(self.page_label)
        self.status.addPermanentWidget(self.zoom_label)
        self.status.showMessage(i18n.tr("status_ready"), 4000)

    def _build_toolbar(self):
        toolbar = QToolBar(self)
        toolbar.setObjectName("mainToolBar")
        toolbar.setMovable(False)
        toolbar.setFloatable(False)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        toolbar.setIconSize(QSize(26, 26))
        self.addToolBar(Qt.TopToolBarArea, toolbar)
        self.toolbar = toolbar
        self._toolbar_texts = []
        self._main_doc_actions = []
        self._main_separators = []

        def add(icon_name, text_key, slot, checkable=False, needs_doc=True,
                mirror=False):
            act = QAction(theme_icon(icon_name, 26, None, mirror),
                          i18n.tr(text_key), self)
            act.setCheckable(checkable)
            act.triggered.connect(lambda *a, s=slot: s())
            if needs_doc:
                act.setData("doc")
            toolbar.addAction(act)
            self._toolbar_texts.append((act, text_key))
            return act

        def separator():
            sep = toolbar.addSeparator()
            self._main_separators.append(sep)
            return sep

        self.act_open = add("open", "open", self.open_file, needs_doc=False)
        self.act_save = add("save", "save", self.save)

        separator()
        self.act_zoom_in = add("zoom_in", "zoom_in", self.zoom_in)
        self.act_zoom_out = add("zoom_out", "zoom_out", self.zoom_out)
        self.act_fit_width = add("fit_width", "fit_width", self.fit_width)
        self.act_fit_page = add("fit_page", "fit_page", self.fit_page)

        separator()
        self.act_prev = add("prev", "prev_page",
                            lambda: self.goto_page(self.current_page() - 1),
                            mirror=i18n.is_rtl())
        self.page_spin = QSpinBox(self)
        self.page_spin.setRange(1, 1)
        self.page_spin.setFixedWidth(54)
        self.page_spin.setAlignment(Qt.AlignCenter)
        self.page_spin.setKeyboardTracking(False)
        self.page_spin.valueChanged.connect(self._spin_goto)
        self._page_spin_action = toolbar.addWidget(self.page_spin)
        self.page_total_label = QLabel(self)
        self.page_total_label.setMinimumWidth(28)
        self._page_total_action = toolbar.addWidget(self.page_total_label)
        self.act_next = add("next", "next_page",
                            lambda: self.goto_page(self.current_page() + 1),
                            mirror=i18n.is_rtl())

        separator()
        self.find_edit = QLineEdit(self)
        self.find_edit.setFixedWidth(190)
        self.find_edit.setClearButtonEnabled(True)
        self.find_edit.setPlaceholderText(i18n.tr("find"))
        self.find_edit.returnPressed.connect(self.do_search)
        self._find_action = toolbar.addWidget(self.find_edit)

        separator()
        self.act_sidebar = QAction(theme_icon("sidebar", 26), "", self)
        self.act_sidebar.setCheckable(True)
        self.act_sidebar.setChecked(self._sidebar_user_visible)
        self.act_sidebar.setToolTip(i18n.tr("sidebar_toggle"))
        self.act_sidebar.setData("doc")
        self.act_sidebar.triggered.connect(
            lambda *a: self._toggle_sidebar(self.act_sidebar.isChecked()))
        toolbar.addAction(self.act_sidebar)

        self.act_guide = add("guide", "guide_short", self.show_guide,
                             needs_doc=False)

        self._main_doc_actions = [
            self.act_save, self.act_zoom_in, self.act_zoom_out,
            self.act_fit_width, self.act_fit_page, self.act_prev,
            self.act_next, self.act_sidebar,
        ]

        # ---------- شريط أدوات الرسم (يظهر عند فتح ملف) ----------
        tools = QToolBar(self)
        tools.setObjectName("toolsToolBar")
        tools.setMovable(False)
        tools.setFloatable(False)
        tools.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        tools.setIconSize(QSize(26, 26))
        self.addToolBarBreak(Qt.TopToolBarArea)
        self.addToolBar(Qt.TopToolBarArea, tools)
        self.tools_bar = tools

        self.annot_group = QActionGroup(self)
        self.annot_group.setExclusive(True)
        self.tool_actions = {}
        for mode in TOOL_MODES:
            key = TOOL_KEYS[mode]
            act = QAction(theme_icon(mode, 26), i18n.tr(key), self)
            act.setCheckable(True)
            act.setData("doc")
            act.triggered.connect(lambda *a, m=mode: self.set_tool(m))
            self.annot_group.addAction(act)
            tools.addAction(act)
            self._toolbar_texts.append((act, key))
            self.tool_actions[mode] = act

        tools.addSeparator()

        # قائمة الصفحة
        self.page_menu_btn = QToolButton(self)
        self.page_menu_btn.setPopupMode(QToolButton.InstantPopup)
        self.page_menu_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.page_menu_btn.setIcon(theme_icon("page", 26))
        self.page_menu_btn.setMenu(QMenu(self.page_menu_btn))
        tools.addWidget(self.page_menu_btn)
        self.page_menu = self.page_menu_btn.menu()

        # قائمة أدوات الملف
        self.file_menu_btn = QToolButton(self)
        self.file_menu_btn.setPopupMode(QToolButton.InstantPopup)
        self.file_menu_btn.setToolButtonStyle(Qt.ToolButtonTextUnderIcon)
        self.file_menu_btn.setIcon(theme_icon("sliders", 26))
        self.file_menu_btn.setMenu(QMenu(self.file_menu_btn))
        tools.addWidget(self.file_menu_btn)
        self.file_menu = self.file_menu_btn.menu()

        tools.addSeparator()
        act = QAction(theme_icon("close", 26), i18n.tr("close_file"), self)
        act.setData("doc")
        act.triggered.connect(lambda *a: self.close_file())
        tools.addAction(act)
        self._toolbar_texts.append((act, "close_file"))

        self.set_tool("pointer")

    def _build_shortcuts(self):
        self.act_focus_find = QAction(self)
        self.act_focus_find.setShortcut(QKeySequence("Ctrl+F"))
        self.act_focus_find.triggered.connect(self._focus_search)
        self.addAction(self.act_focus_find)

        self.act_escape = QAction(self)
        self.act_escape.setShortcut(QKeySequence("Escape"))
        self.act_escape.triggered.connect(lambda *a: self.set_tool("pointer"))
        self.addAction(self.act_escape)

    # ------------------------------------------------------------------
    # القوائم
    # ------------------------------------------------------------------
    def _menu_action(self, menu, key, slot, icon_name=None,
                     shortcut=None, needs_doc=False, needs_file=False,
                     checkable=False, checked=False):
        if icon_name:
            act = QAction(theme_icon(icon_name), i18n.tr(key), menu)
        else:
            act = QAction(i18n.tr(key), menu)
        if shortcut is not None:
            act.setShortcut(shortcut)
        act.setCheckable(checkable)
        if checkable:
            act.setChecked(checked)
        if needs_doc:
            act.setData("doc")
        elif needs_file:
            act.setData("file")
        act.triggered.connect(lambda *a, s=slot: s())
        menu.addAction(act)
        return act

    def _build_menus(self):
        bar = self.menuBar()
        bar.clear()

        # --- ملف ---
        m_file = bar.addMenu(i18n.tr("file_menu"))
        self._menu_action(m_file, "open", self.open_file, "open",
                          QKeySequence.Open)
        self.recent_menu = m_file.addMenu(theme_icon("recent"),
                                          i18n.tr("open_recent"))
        self._rebuild_recent_menu()
        m_file.addSeparator()
        self._menu_action(m_file, "save", self.save, "save",
                          QKeySequence.Save, needs_doc=True)
        self._menu_action(m_file, "save_as", self.save_as, "save",
                          QKeySequence.SaveAs, needs_doc=True)
        self._menu_action(m_file, "close_file", self.close_file, "close",
                          QKeySequence("Ctrl+W"), needs_doc=True)
        m_file.addSeparator()
        self._menu_action(m_file, "export_images", self.export_images,
                          "images", needs_file=True)
        self._menu_action(m_file, "export_text", self.export_text, "text",
                          needs_file=True)
        self._menu_action(m_file, "export_word", self.export_word, "export",
                          needs_file=True)
        self._menu_action(m_file, "export_excel", self.export_excel, "export",
                          needs_file=True)
        self._menu_action(m_file, "images_to_pdf", self.images_to_pdf, "images")
        m_file.addSeparator()
        self._menu_action(m_file, "exit", self.close, "close",
                          QKeySequence("Ctrl+Q"))

        # --- تحرير ---
        m_edit = bar.addMenu(i18n.tr("edit_menu"))
        self._menu_action(m_edit, "insert_pages", self.insert_pages, "page",
                          needs_doc=True)
        self._menu_action(m_edit, "delete_page", self.delete_page, "delete",
                          needs_doc=True)
        self._menu_action(m_edit, "rotate_cw", lambda: self.rotate_page(90),
                          "rotate", needs_doc=True)
        self._menu_action(m_edit, "rotate_ccw", lambda: self.rotate_page(-90),
                          "rotate", needs_doc=True)
        m_edit.addSeparator()
        self._menu_action(m_edit, "forms", self.fill_forms, "text",
                          needs_doc=True)

        # --- أدوات ---
        m_tools = bar.addMenu(i18n.tr("tools_menu"))
        self._menu_action(m_tools, "merge", self.merge_files, "merge")
        self._menu_action(m_tools, "split", self.split_file, "split",
                          needs_file=True)
        self._menu_action(m_tools, "compress", self.compress_file, "compress",
                          needs_file=True)
        self._menu_action(m_tools, "protect", self.protect_file, "protect",
                          needs_file=True)
        self._menu_action(m_tools, "unlock", self.unlock_file, "unlock",
                          needs_file=True)
        self._menu_action(m_tools, "ocr", self.run_ocr, "text",
                          needs_file=True)

        # --- عرض ---
        m_view = bar.addMenu(i18n.tr("view_menu"))
        self._menu_action(m_view, "zoom_in", self.zoom_in, "zoom_in",
                          QKeySequence.ZoomIn, needs_doc=True)
        self._menu_action(m_view, "zoom_out", self.zoom_out, "zoom_out",
                          QKeySequence.ZoomOut, needs_doc=True)
        self._menu_action(m_view, "fit_width", self.fit_width, "fit_width",
                          QKeySequence("Ctrl+1"), needs_doc=True)
        self._menu_action(m_view, "fit_page", self.fit_page, "fit_page",
                          QKeySequence("Ctrl+0"), needs_doc=True)
        m_view.addSeparator()
        self._menu_action(m_view, "first_page", lambda: self.goto_page(0),
                          "first", QKeySequence("Ctrl+Home"), needs_doc=True)
        self._menu_action(m_view, "prev_page",
                          lambda: self.goto_page(self.current_page() - 1),
                          "prev", QKeySequence.MoveToPreviousPage,
                          needs_doc=True)
        self._menu_action(m_view, "next_page",
                          lambda: self.goto_page(self.current_page() + 1),
                          "next", QKeySequence.MoveToNextPage,
                          needs_doc=True)
        self._menu_action(m_view, "last_page",
                          lambda: self.goto_page(self.page_count() - 1),
                          "last", QKeySequence("Ctrl+End"),
                          needs_doc=True)
        m_view.addSeparator()
        act = QAction(theme_icon("sidebar"), i18n.tr("sidebar_toggle"), m_view)
        act.setCheckable(True)
        act.setChecked(self._sidebar_user_visible)
        act.setData("doc")
        act.triggered.connect(lambda checked=False: self._toggle_sidebar(checked))
        m_view.addAction(act)
        self.act_sidebar_menu = act

        # --- اللغة ---
        m_lang = bar.addMenu(i18n.tr("language_menu"))
        self.lang_actions = {}
        for code in i18n.available_languages():
            name, _rtl = i18n.LANGUAGES[code]
            act = m_lang.addAction(name)
            act.setCheckable(True)
            act.setChecked(code == i18n.get_language())
            act.triggered.connect(
                lambda _checked=False, c=code: self.change_language(c))
            self.lang_actions[code] = act

        # --- مساعدة ---
        m_help = bar.addMenu(i18n.tr("help_menu"))
        self._menu_action(m_help, "guide", self.show_guide, "guide",
                          QKeySequence("F1"))
        self._menu_action(m_help, "about", self.show_about, "help")

    def _rebuild_recent_menu(self):
        if not hasattr(self, "recent_menu"):
            return
        self.recent_menu.clear()
        valid = [p for p in self.recent if os.path.exists(p)]
        if not valid:
            empty = self.recent_menu.addAction(i18n.tr("home_no_recent"))
            empty.setEnabled(False)
            return
        for path in valid[:5]:
            act = self.recent_menu.addAction(
                theme_icon("page"), os.path.basename(path))
            act.setToolTip(path)
            act.triggered.connect(
                lambda *a, p=path: self._open_recent(p))
        self.recent_menu.addSeparator()
        clear = self.recent_menu.addAction(i18n.tr("clear_recent"))
        clear.triggered.connect(lambda *a: self._clear_recent())

    def _fill_page_menu(self):
        self.page_menu.clear()
        for key, icon_name, slot in (
            ("rotate_cw", "rotate", lambda: self.rotate_page(90)),
            ("rotate_ccw", "rotate", lambda: self.rotate_page(-90)),
            ("delete_page", "delete", self.delete_page),
            ("insert_pages", "page", self.insert_pages),
        ):
            act = QAction(theme_icon(icon_name), i18n.tr(key), self.page_menu)
            act.setData("doc")
            act.triggered.connect(lambda *a, s=slot: s())
            self.page_menu.addAction(act)
        self.page_menu_btn.setText(i18n.tr("page_tools"))

    def _fill_file_menu(self):
        self.file_menu.clear()
        entries = (
            ("merge", "merge", self.merge_files, None),
            ("split", "split", self.split_file, "file"),
            ("compress", "compress", self.compress_file, "file"),
            ("protect", "protect", self.protect_file, "file"),
            ("unlock", "unlock", self.unlock_file, "file"),
            ("ocr", "text", self.run_ocr, "file"),
            ("export_images", "images", self.export_images, "file"),
            ("export_word", "export", self.export_word, "file"),
        )
        for key, icon_name, slot, req in entries:
            act = QAction(theme_icon(icon_name), i18n.tr(key), self.file_menu)
            if req:
                act.setData(req)
            act.triggered.connect(lambda *a, s=slot: s())
            self.file_menu.addAction(act)
        self.file_menu_btn.setText(i18n.tr("file_tools"))

    # ------------------------------------------------------------------
    # تحديث النصوص بعد تغيير اللغة
    # ------------------------------------------------------------------
    def _retranslate(self):
        self._build_menus()
        self._fill_page_menu()
        self._fill_file_menu()
        for act, key in self._toolbar_texts:
            if key:
                act.setText(i18n.tr(key))
        self.act_sidebar.setToolTip(i18n.tr("sidebar_toggle"))
        self.find_edit.setPlaceholderText(i18n.tr("find"))
        self.find_edit.setToolTip(i18n.tr("find"))
        self.page_menu_btn.setToolTip(i18n.tr("page_tools"))
        self.file_menu_btn.setToolTip(i18n.tr("file_tools"))
        self.home.retranslate()
        self.home.reflow(self.scroll.viewport().width())
        self._update_title()
        if self.doc:
            self.page_spin.setRange(1, self.page_count())
            self.page_spin.blockSignals(True)
            self.page_spin.setValue(self.current_page() + 1)
            self.page_spin.blockSignals(False)
        self._update_page_label()
        self._update_zoom_label()
        self._update_actions_enabled()

    # ------------------------------------------------------------------
    # أدوات مساعدة
    # ------------------------------------------------------------------
    def page_count(self):
        return self.doc.page_count if self.doc else 0

    def current_page(self):
        if not self.doc or self.page_count() == 0:
            return 0
        return min(max(1, self.page_spin.value()), self.page_count()) - 1

    def _page_status_text(self):
        if not self.doc:
            return ""
        return i18n.tr("page_status").format(
            self.page_spin.value(), self.page_count())

    def _update_page_label(self):
        if hasattr(self, "page_label"):
            self.page_label.setText(self._page_status_text())
        if hasattr(self, "page_total_label"):
            self.page_total_label.setText(
                "/ %d" % self.page_count() if self.doc else "")

    def _update_zoom_label(self):
        if hasattr(self, "zoom_label"):
            self.zoom_label.setText("%d%%" % int(round(self.zoom * 100)))

    def _update_title(self):
        name = os.path.basename(self.file_path) if self.file_path else ""
        star = " •" if self.dirty else ""
        self.setWindowTitle(
            f"{name}{star} — {i18n.tr('app_title')}" if name
            else i18n.tr("app_title"))

    def _update_actions_enabled(self):
        has_doc = self.doc is not None
        has_file = bool(has_doc and self.file_path
                        and os.path.exists(self.file_path))
        for act in self.findChildren(QAction):
            req = act.data()
            if req == "doc":
                act.setEnabled(has_doc)
            elif req == "file":
                act.setEnabled(has_file)
        for attr in ("page_spin", "find_edit", "act_sidebar", "act_focus_find"):
            widget = getattr(self, attr, None)
            if widget is not None:
                widget.setEnabled(has_doc)
        if hasattr(self, "toolbar"):
            for mode, act in getattr(self, "tool_actions", {}).items():
                act.setEnabled(has_doc)

    def _need_doc(self):
        if not self.doc:
            QMessageBox.information(self, i18n.tr("app_title"),
                                    i18n.tr("no_document"))
        return bool(self.doc)

    def _need_file(self):
        """للعمليات التي تقرأ الملف من القرص (يجب أن يكون محفوظاً)"""
        if not self._need_doc():
            return False
        if not self.file_path or not os.path.exists(self.file_path):
            QMessageBox.information(self, i18n.tr("app_title"),
                                    i18n.tr("need_save_first"))
            return False
        return True

    def _mark_dirty(self):
        self.dirty = True
        self._update_title()

    def _info(self, key):
        """رسالة نجاح غير مقيّدة بنافذة (أسهل للأطفال وأقل إزعاجاً)"""
        self.status.showMessage(i18n.tr(key), 5000)

    def _error(self, detail=""):
        QMessageBox.critical(self, i18n.tr("error_title"),
                             detail or i18n.tr("error_title"))

    @contextmanager
    def _busy(self, label=""):
        QApplication.setOverrideCursor(Qt.WaitCursor)
        if label:
            self.status.showMessage(label)
        try:
            yield
        finally:
            QApplication.restoreOverrideCursor()
            self.status.clearMessage()

    def _dialog_dir(self):
        return self.settings.value("last_dir", "")

    def _remember_dir(self, path):
        if path:
            self.settings.setValue("last_dir", os.path.dirname(path))

    def _out_save_path(self, suggest="output.pdf"):
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.tr("output_pdf"),
            os.path.join(self._dialog_dir(), suggest), PDF_FILTER)
        if path:
            self._remember_dir(path)
        return path

    def _out_folder(self):
        path = QFileDialog.getExistingDirectory(
            self, i18n.tr("output_folder"), self._dialog_dir())
        if path:
            self._remember_dir(path)
        return path

    # ------------------------------------------------------------------
    # ملفات حديثة
    # ------------------------------------------------------------------
    def _load_recent(self):
        value = self.settings.value("recent_files", [])
        if isinstance(value, str):
            value = [value]
        if not value:
            return []
        return [str(p) for p in value if p][:RECENT_MAX]

    def _add_recent(self, path):
        path = os.path.abspath(path)
        seen = set()
        ordered = []
        for item in [path] + list(self.recent):
            key = os.path.normcase(os.path.abspath(item))
            if key in seen:
                continue
            seen.add(key)
            ordered.append(item)
        self.recent = ordered[:RECENT_MAX]
        self.settings.setValue("recent_files", self.recent)
        self._rebuild_recent_menu()
        self.home.set_recent(self.recent)

    def _clear_recent(self):
        self.recent = []
        self.settings.setValue("recent_files", [])
        self._rebuild_recent_menu()
        self.home.set_recent([])

    def _open_recent(self, path):
        if not os.path.exists(path):
            self._error(i18n.tr("recent_missing"))
            self.recent = [p for p in self.recent if p != path]
            self.settings.setValue("recent_files", self.recent)
            self._rebuild_recent_menu()
            return
        self.load_file(path)

    # ------------------------------------------------------------------
    # فتح / حفظ / إغلاق
    # ------------------------------------------------------------------
    def _confirm_discard(self):
        if not self.dirty:
            return True
        ret = QMessageBox.question(
            self, i18n.tr("unsaved_title"), i18n.tr("unsaved_text"),
            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Save:
            self.save()
            return not self.dirty
        return ret == QMessageBox.Discard

    def open_file(self):
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.tr("open"), self._dialog_dir(), PDF_FILTER)
        if path:
            self.load_file(path)

    def load_file(self, path):
        if not path or not os.path.exists(path):
            self._error(i18n.tr("recent_missing"))
            return
        if not self._confirm_discard():
            return
        try:
            doc = fitz.open(path)
        except Exception as e:
            self._error(str(e))
            return

        # كلمة المرور
        password = None
        while doc.needs_pass:
            pw, ok = QInputDialog.getText(
                self, i18n.tr("app_title"), i18n.tr("enter_password"),
                QLineEdit.Password)
            if not ok:
                doc.close()
                return
            if doc.authenticate(pw):
                password = pw
                break
            QMessageBox.warning(self, i18n.tr("app_title"),
                                i18n.tr("wrong_password"))

        old = self.doc
        self.doc = doc
        self.file_path = path
        self.dirty = False
        self.search_hits = {}
        self.sign_path = None
        self._password = password
        self.zoom_mode = "fit_width"
        self._remember_dir(path)

        if old is not None:
            try:
                old.close()
            except Exception:
                pass
        self._clear_pages()
        self._cache_page_sizes()
        self._rebuild_thumb_items()
        if hasattr(self, "find_edit"):
            self.find_edit.clear()
        self._update_title()
        self._show_document(True)
        self.page_spin.setRange(1, max(1, self.page_count()))
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(1)
        self.page_spin.blockSignals(False)
        self.zoom = self._compute_fit_width()
        self.render_all()
        if self.page_count():
            self.goto_page(0)
        self._add_recent(path)
        self._update_page_label()
        self._update_zoom_label()
        self._update_actions_enabled()
        self.status.showMessage(i18n.tr("status_ready"), 3500)
        self._schedule_refit()
        # ملاءمة دقيقة بعد أن يستقر التخطيط (شريط الصفحات المصغّرة/أشرطة التمرير)
        QTimer.singleShot(0, self._apply_fit)

    def _reopen_saved(self):
        """إعادة فتح الملف بعد الحفظ مع إعادة توثيق كلمة المرور إن وجدت"""
        doc = fitz.open(self.file_path)
        if doc.needs_pass and self._password:
            doc.authenticate(self._password)
        return doc

    def save(self):
        if not self.doc:
            return False
        if not self.file_path:
            return self.save_as()
        tmp = self.file_path + ".ajouby_tmp"
        try:
            self.doc.save(tmp, garbage=3, deflate=True)
            self.doc.close()
            try:
                os.replace(tmp, self.file_path)
            except Exception:
                # إعادة فتح النسخة الأصلية حتى لا يبقى المستند مغلقاً
                self.doc = self._reopen_saved()
                raise
            self.doc = self._reopen_saved()
            self._cache_page_sizes()
            self.dirty = False
            self._update_title()
            self._info("saved")
            return True
        except Exception as e:
            if os.path.exists(tmp):
                try:
                    os.remove(tmp)
                except OSError:
                    pass
            if self.doc is None or self.doc.is_closed:
                try:
                    self.doc = self._reopen_saved()
                except Exception:
                    self.doc = None
            self._error(str(e))
            return False

    def save_as(self):
        if not self.doc:
            return False
        suggest = (os.path.basename(self.file_path)
                   if self.file_path else "document.pdf")
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.tr("save_as"),
            os.path.join(self._dialog_dir(), suggest), PDF_FILTER)
        if not path:
            return False
        try:
            with self._busy(i18n.tr("save")):
                self.doc.save(path, garbage=3, deflate=True)
            self.file_path = path
            self.dirty = False
            self._remember_dir(path)
            self._add_recent(path)
            self._update_title()
            self._update_actions_enabled()
            self._info("saved")
            return True
        except Exception as e:
            self._error(str(e))
            return False

    def close_file(self):
        if not self.doc:
            return
        if not self._confirm_discard():
            return
        try:
            self.doc.close()
        except Exception:
            pass
        self.doc = None
        self.file_path = None
        self.dirty = False
        self.search_hits = {}
        self._password = None
        if hasattr(self, "find_edit"):
            self.find_edit.clear()
        self._page_sizes = []
        self._clear_pages()
        self._rebuild_thumb_items()
        self._show_document(False)
        self.page_spin.setRange(1, 1)
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(1)
        self.page_spin.blockSignals(False)
        self.zoom = 1.2
        self._update_title()
        self._update_page_label()
        self._update_zoom_label()
        self._update_actions_enabled()
        self.status.showMessage(i18n.tr("status_ready"), 3000)

    # ------------------------------------------------------------------
    # إظهار/إخفاء الأجزاء حسب الحالة
    # ------------------------------------------------------------------
    def _show_document(self, has_doc):
        self.home.setVisible(not has_doc)
        if hasattr(self, "tools_bar"):
            self.tools_bar.setVisible(bool(has_doc))
        # شريط البداية يعرض زرّي «فتح» و«دليل» فقط — أبسط ما يمكن
        for act in getattr(self, "_main_doc_actions", []):
            act.setVisible(bool(has_doc))
        for sep in getattr(self, "_main_separators", []):
            sep.setVisible(bool(has_doc))
        for widget in (self.page_spin, self.page_total_label, self.find_edit):
            widget.setVisible(bool(has_doc))
        for action in (self._page_spin_action, self._page_total_action,
                       self._find_action):
            action.setVisible(bool(has_doc))
        self.page_spin.setEnabled(has_doc)
        self.find_edit.setEnabled(has_doc)
        self.page_label.setVisible(bool(has_doc))
        self.zoom_label.setVisible(bool(has_doc))
        if hasattr(self, "act_sidebar"):
            self.act_sidebar.setToolTip(i18n.tr("sidebar_toggle"))
        self._update_sidebar()
        self._update_actions_enabled()

    def _update_sidebar(self):
        if not hasattr(self, "thumb_list"):
            return
        if not self.doc:
            self.thumb_list.hide()
            return
        if self._sidebar_forced:
            self.thumb_list.setVisible(self._sidebar_user_visible)
            return
        narrow = self.width() < 880
        if narrow:
            self.thumb_list.hide()
            self._sidebar_auto_hidden = True
        else:
            self.thumb_list.setVisible(self._sidebar_user_visible)
            if self._sidebar_user_visible:
                self._sidebar_auto_hidden = False

    def _toggle_sidebar(self, visible):
        self._sidebar_user_visible = bool(visible)
        self._sidebar_forced = True
        self.act_sidebar.setChecked(self._sidebar_user_visible)
        if getattr(self, "act_sidebar_menu", None) is not None:
            self.act_sidebar_menu.setChecked(self._sidebar_user_visible)
        self.settings.setValue("sidebar_visible", self._sidebar_user_visible)
        self._update_sidebar()
        self._schedule_refit()

    # ------------------------------------------------------------------
    # العرض الكسول
    # ------------------------------------------------------------------
    def _cache_page_sizes(self):
        self._page_sizes = []
        if not self.doc:
            return
        for i in range(self.page_count()):
            try:
                rect = self.doc[i].rect
                self._page_sizes.append((rect.width, rect.height))
            except Exception:
                self._page_sizes.append((595.0, 842.0))

    def _clear_pages(self):
        for lbl in self.page_labels:
            self.canvas_layout.removeWidget(lbl)
            lbl.hide()
            lbl.setParent(None)
            lbl.deleteLater()
        self.page_labels = []

    def render_all(self):
        """يبني عناصر الصفحات بأحجامها لكن يرسم المرئي فقط (توفير الرام)"""
        if not self.doc:
            return
        count = self.page_count()
        if len(self.page_labels) != count:
            self._clear_pages()
            for i in range(count):
                lbl = PageLabel(i, self, self.canvas)
                self.canvas_layout.insertWidget(
                    self.canvas_layout.count() - 1, lbl, 0, Qt.AlignHCenter)
                self.page_labels.append(lbl)
        for i, lbl in enumerate(self.page_labels):
            w, h = self._page_sizes[i] if i < len(self._page_sizes) else (595, 842)
            size = QSize(max(1, int(w * self.zoom)), max(1, int(h * self.zoom)))
            if lbl.size() != size:
                lbl.setFixedSize(size)
            lbl.zoom = self.zoom
            current = lbl.pixmap()
            if current is not None and not current.isNull():
                if current.size() != size:
                    lbl.clear()
        self.update_visible_pages()

    def _pix_to_qimage(self, pix):
        """تحويل مباشر من ذاكرة MuPDF إلى QImage (أسرع وأخف من PNG)"""
        fmt = QImage.Format_RGBA8888 if pix.alpha else QImage.Format_RGB888
        # مهم جداً: pix.samples كائن مؤقت. يجب إبقاء مرجع حيّ طوال النسخ،
        # وإلا يُحرَّر المخزن قبل img.copy() فينهار البرنامج (use-after-free).
        samples = pix.samples
        img = QImage(samples, pix.width, pix.height, pix.stride, fmt)
        return img.copy()  # نسخ حتى لا يُحتفظ بذاكرة MuPDF

    def render_page(self, i):
        if not self.doc or i >= self.page_count() or i >= len(self.page_labels):
            return
        lbl = self.page_labels[i]
        if lbl.height() <= 1:
            return
        try:
            page = self.doc[i]
            rect = page.rect
            scale = self.zoom
            if rect.width and rect.height:
                pixels = rect.width * rect.height * scale * scale
                if pixels > MAX_RENDER_PIXELS:
                    scale = (MAX_RENDER_PIXELS /
                             (rect.width * rect.height)) ** 0.5
            pix = page.get_pixmap(matrix=fitz.Matrix(scale, scale),
                                  alpha=False)
            pm = QPixmap.fromImage(self._pix_to_qimage(pix))
            del pix
            if pm.isNull() or pm.width() < 2:
                return

            # رسم نتائج البحث (بمقياس الصورة الفعلي)
            hits = self.search_hits.get(i)
            if hits and rect.width and rect.height:
                painter = QPainter(pm)
                painter.setBrush(QColor(255, 230, 0, 130))
                painter.setPen(Qt.NoPen)
                sx = pm.width() / rect.width
                sy = pm.height() / rect.height
                for r in hits:
                    painter.drawRect(QRectF(
                        r.x0 * sx, r.y0 * sy,
                        (r.x1 - r.x0) * sx, (r.y1 - r.y0) * sy))
                painter.end()

            lbl.zoom = self.zoom
            lbl.setPixmap(pm)
        except Exception:
            lbl.clear()

    def _on_scroll_changed(self, _value):
        self.update_visible_pages()

    def update_visible_pages(self):
        """يرسم الصفحات المرئية + هامش صغير، ويحرر البعيدة من الذاكرة."""
        if not self.doc or not self.page_labels:
            return
        sb = self.scroll.verticalScrollBar()
        top = sb.value() - 300
        bottom = sb.value() + self.scroll.viewport().height() + 300

        margins = self.canvas_layout.contentsMargins()
        y = margins.top()
        spacing = self.canvas_layout.spacing()

        for i, lbl in enumerate(self.page_labels):
            y0 = y
            y1 = y0 + lbl.height()
            y = y1 + spacing
            near = y1 >= top and y0 <= bottom
            has_pm = lbl.pixmap() is not None and not lbl.pixmap().isNull()
            if near and not has_pm:
                self.render_page(i)
            elif not near and has_pm:
                lbl.clear()

    # ------------------------------------------------------------------
    # الصور المصغرة (تُرسم عند الحاجة فقط)
    # ------------------------------------------------------------------
    def _rebuild_thumb_items(self):
        self.thumb_list.blockSignals(True)
        self.thumb_list.clear()
        self._thumb_cache = {}
        self._thumb_loaded = set()
        if self.doc:
            self._thumb_item_h = int(THUMB_WIDTH * 1.32) + 18
            for i in range(self.page_count()):
                item = QListWidgetItem()
                item.setSizeHint(QSize(THUMB_WIDTH + 12, self._thumb_item_h))
                item.setTextAlignment(Qt.AlignCenter)
                item.setToolTip(str(i + 1))
                item.setData(Qt.UserRole, i)
                self.thumb_list.addItem(item)
        self.thumb_list.blockSignals(False)
        self._update_thumbs_visible()

    def _thumb_pixmap(self, index):
        cached = self._thumb_cache.get(index)
        if cached is not None:
            return cached
        page = self.doc[index]
        z = THUMB_WIDTH / max(1.0, page.rect.width)
        pix = page.get_pixmap(matrix=fitz.Matrix(z, z), alpha=False)
        pm = QPixmap.fromImage(self._pix_to_qimage(pix))
        del pix

        # شارة رقم الصفحة
        painter = QPainter(pm)
        painter.setRenderHint(QPainter.Antialiasing)
        label = str(index + 1)
        font = painter.font()
        font.setPointSize(8)
        painter.setFont(font)
        width = max(22, painter.fontMetrics().horizontalAdvance(label) + 14)
        rect = QRectF((pm.width() - width) / 2.0, pm.height() - 20, width, 16)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(38, 49, 60, 210))
        painter.drawRoundedRect(rect, 8, 8)
        painter.setPen(QColor(255, 255, 255))
        painter.drawText(rect, Qt.AlignCenter, label)
        painter.end()

        if len(self._thumb_cache) >= 40:
            self._thumb_cache.pop(next(iter(self._thumb_cache)), None)
        self._thumb_cache[index] = pm
        return pm

    def _thumb_icon(self, index):
        """أيقونة مع أوضاع Normal/Selected مطابقة حتى لا تُلوَّن عند التحديد"""
        pm = self._thumb_pixmap(index)
        ic = QIcon()
        ic.addPixmap(pm, QIcon.Normal, QIcon.Off)
        ic.addPixmap(pm, QIcon.Selected, QIcon.Off)
        ic.addPixmap(pm, QIcon.Active, QIcon.Off)
        return ic

    def _update_thumbs_visible(self):
        if not self.doc or self.thumb_list.count() == 0:
            return
        sb = self.thumb_list.verticalScrollBar()
        row_h = max(1, self._thumb_item_h)
        top = sb.value() // row_h
        visible = self.thumb_list.viewport().height() // row_h + 2
        start = max(0, top - 2)
        end = min(self.thumb_list.count(), top + visible + 2)

        for i in range(start, end):
            if i in self._thumb_loaded:
                continue
            item = self.thumb_list.item(i)
            if item is None:
                continue
            try:
                item.setIcon(self._thumb_icon(i))
            except Exception:
                pass
            self._thumb_loaded.add(i)

        # تحرير صور الصفحات البعيدة عن الشاشة
        for i in list(self._thumb_loaded):
            if i < start - 25 or i > end + 25:
                item = self.thumb_list.item(i)
                if item is not None:
                    item.setIcon(QIcon())
                self._thumb_loaded.discard(i)

    def _on_thumb_scroll(self, _value):
        self._update_thumbs_visible()

    def _goto_row(self, row):
        if row < 0 or row >= len(self.page_labels):
            return
        self.page_spin.blockSignals(True)
        self.page_spin.setValue(row + 1)
        self.page_spin.blockSignals(False)
        self._update_page_label()
        self.scroll.ensureWidgetVisible(self.page_labels[row], 0, 0)
        self.update_visible_pages()
        if row < self.thumb_list.count():
            self.thumb_list.blockSignals(True)
            self.thumb_list.setCurrentRow(row)
            self.thumb_list.blockSignals(False)

    def goto_page(self, n):
        if not self.doc or self.page_count() == 0:
            return
        n = max(0, min(n, self.page_count() - 1))
        self._goto_row(n)

    def _spin_goto(self, val):
        if self.doc and self.page_count():
            self._goto_row(_clamp(val - 1, 0, self.page_count() - 1))
        self._update_page_label()

    # ------------------------------------------------------------------
    # التكبير والملاءمة
    # ------------------------------------------------------------------
    def zoom_in(self):
        if not self.doc:
            return
        self.set_zoom(min(MAX_ZOOM, self.zoom * 1.25))

    def zoom_out(self):
        if not self.doc:
            return
        self.set_zoom(max(MIN_ZOOM, self.zoom / 1.25))

    def set_zoom(self, z):
        if not self.doc:
            return
        self.zoom_mode = "custom"
        self.zoom = _clamp(z, MIN_ZOOM, MAX_ZOOM)
        self.render_all()
        self._update_zoom_label()

    def fit_width(self):
        if not self.doc:
            return
        self.zoom_mode = "fit_width"
        self._apply_fit()

    def fit_page(self):
        if not self.doc:
            return
        self.zoom_mode = "fit_page"
        self._apply_fit()

    def _compute_fit_width(self):
        if not self._page_sizes:
            return self.zoom
        max_w = max(w for w, _h in self._page_sizes)
        viewport = self.scroll.viewport().width() or self.width()
        return _clamp((viewport - 50) / max(1.0, max_w), MIN_ZOOM, MAX_ZOOM)

    def _compute_fit_page(self):
        if not self._page_sizes:
            return self.zoom
        max_w = max(w for w, _h in self._page_sizes)
        max_h = max(h for _w, h in self._page_sizes)
        viewport = self.scroll.viewport()
        vw = (viewport.width() or self.width()) - 50
        vh = (viewport.height() or self.height()) - 50
        return _clamp(min(vw / max(1.0, max_w), vh / max(1.0, max_h)),
                      MIN_ZOOM, MAX_ZOOM)

    def _apply_fit(self):
        if not self.doc:
            return
        if self.zoom_mode == "fit_page":
            self.zoom = self._compute_fit_page()
        else:
            self.zoom = self._compute_fit_width()
        self.render_all()
        self._update_zoom_label()

    def _schedule_refit(self):
        if self.zoom_mode in ("fit_width", "fit_page") and self.doc:
            self._refit_timer.start(140)

    # ------------------------------------------------------------------
    # أدوات التعليق التوضيحي
    # ------------------------------------------------------------------
    def set_tool(self, mode):
        if mode not in TOOL_MODES:
            return  # تجاهل الوسائط غير الصحيحة
        self.tool_mode = mode
        for m, act in getattr(self, "tool_actions", {}).items():
            act.setChecked(m == mode)
        cursor = Qt.ArrowCursor if mode == "pointer" else Qt.CrossCursor
        if hasattr(self, "canvas"):
            self.canvas.setCursor(cursor)
        if self.doc and mode != "pointer":
            self.status.showMessage(i18n.tr(TOOL_KEYS[mode]), 4000)

    def on_page_click(self, idx, pt):
        if not self._need_doc():
            return
        page = self.doc[idx]
        mode = self.tool_mode
        try:
            if mode == "note":
                text, ok = QInputDialog.getMultiLineText(
                    self, i18n.tr("tool_note"), i18n.tr("note_text"))
                if not ok or not text.strip():
                    return
                page.add_text_annot(pt, text)
                self.status.showMessage(i18n.tr("annot_added"), 3000)
            elif mode == "text":
                text, ok = QInputDialog.getMultiLineText(
                    self, i18n.tr("tool_text"), i18n.tr("text_content"))
                if not ok or not text.strip():
                    return
                size, ok = QInputDialog.getInt(
                    self, i18n.tr("font_size"), i18n.tr("font_size"), 14, 6, 96)
                if not ok:
                    return
                self._insert_text(page, pt, text, size)
                self.status.showMessage(i18n.tr("annot_added"), 3000)
            elif mode == "sign":
                if not self.sign_path:
                    path, _ = QFileDialog.getOpenFileName(
                        self, i18n.tr("signature_pick"), self._dialog_dir(),
                        IMG_FILTER)
                    if not path:
                        return
                    self.sign_path = path
                    self._remember_dir(path)
                # حجم منطقي: عرض 140 نقطة مع الحفاظ على النسبة
                img = QImage(self.sign_path)
                if img.isNull():
                    raise ValueError(i18n.tr("signature_pick"))
                ratio = img.height() / max(1, img.width())
                w = 140.0
                h = min(220.0, w * ratio)
                rect = fitz.Rect(pt.x, pt.y, pt.x + w, pt.y + h)
                page.insert_image(rect, filename=self.sign_path)
                self.status.showMessage(i18n.tr("annot_added"), 3000)
            self._mark_dirty()
            self.render_page(idx)
        except Exception as e:
            self._error(str(e))

    def _insert_text(self, page, pt, text, size):
        """إدراج نص مع دعم كامل للعربية (تشكيل الحروف واتجاه RTL)"""
        if any(ord(c) > 127 for c in text):
            # insert_htmlbox يدعم العربية/RTL والتشكيل الصحيح
            try:
                lines = max(1, text.count("\n") + 1)
                rect = fitz.Rect(pt.x, pt.y, pt.x + 350,
                                 pt.y + size * 1.8 * lines + 10)
                escaped = html_escape(text).replace("\n", "<br>")
                page.insert_htmlbox(
                    rect,
                    f'<div style="font-size:{size}px" dir="auto">{escaped}</div>')
                return
            except Exception:
                pass  # fallback أدناه
        # fallback: خط لاتيني أو إخفاق htmlbox
        fontfile = None
        fontname = "helv"
        if any(ord(c) > 127 for c in text):
            cand = r"C:\Windows\Fonts\arial.ttf"
            if os.path.exists(cand):
                fontfile = cand
                fontname = "AjoubyFont"
        page.insert_text(pt, text, fontsize=size, fontname=fontname,
                         fontfile=fontfile, color=(0, 0, 0))

    def on_highlight(self, idx, rect_pair):
        if not self._need_doc():
            return
        r0, r1 = rect_pair
        rect = fitz.Rect(min(r0.x, r1.x), min(r0.y, r1.y),
                         max(r0.x, r1.x), max(r0.y, r1.y))
        if rect.is_empty or rect.is_infinite:
            return
        try:
            page = self.doc[idx]
            annot = page.add_highlight_annot(rect)
            if annot:
                annot.set_colors(stroke=(1.0, 0.85, 0.1))
                annot.update()
            self._mark_dirty()
            self.render_page(idx)
            self.status.showMessage(i18n.tr("annot_added"), 3000)
        except Exception as e:
            self._error(str(e))

    def on_freehand(self, idx, pts):
        if not self._need_doc():
            return
        try:
            page = self.doc[idx]
            # إصلاح: add_freehand_annot غير موجودة في PyMuPDF الحديثة
            annot = page.add_ink_annot([list(pts)])
            if annot:
                annot.set_colors(stroke=(0.8, 0.12, 0.12))
                try:
                    annot.set_border(width=1.6)
                except Exception:
                    pass
                annot.update()
            self._mark_dirty()
            self.render_page(idx)
            self.status.showMessage(i18n.tr("annot_added"), 3000)
        except Exception as e:
            self._error(str(e))

    # ------------------------------------------------------------------
    # البحث
    # ------------------------------------------------------------------
    def _focus_search(self):
        if not self.doc:
            return
        self.find_edit.setFocus()
        self.find_edit.selectAll()

    def do_search(self):
        if not self.doc:
            return
        text = self.find_edit.text().strip()
        self.search_hits = {}
        if not text:
            self.render_all()
            return
        if self._searching:
            return
        self._searching = True
        total = 0
        QApplication.setOverrideCursor(Qt.WaitCursor)
        self.status.showMessage(i18n.tr("searching"))
        self.find_edit.setEnabled(False)
        try:
            for i in range(self.page_count()):
                if self.doc is None:
                    break
                try:
                    hits = self.doc[i].search_for(text)
                except Exception:
                    hits = []
                if hits:
                    self.search_hits[i] = hits
                    total += len(hits)
                if i % 20 == 0:
                    QApplication.processEvents()
        finally:
            self._searching = False
            QApplication.restoreOverrideCursor()
            self.find_edit.setEnabled(True)

        if self.search_hits:
            self.goto_page(min(self.search_hits))
            self.status.showMessage(
                i18n.tr("search_results").format(total), 5000)
        else:
            self.status.showMessage(i18n.tr("find_none"), 4000)
        self.render_all()

    # ------------------------------------------------------------------
    # عمليات المستند
    # ------------------------------------------------------------------
    def rotate_page(self, delta):
        if not self._need_doc():
            return
        idx = self.current_page()
        try:
            page = self.doc[idx]
            page.set_rotation((page.rotation + delta) % 360)
            self._mark_dirty()
            self._cache_page_sizes()
            self.render_all()
            self._rebuild_thumb_items()
            self._goto_row(idx)
            self.status.showMessage(i18n.tr("page_rotated"), 3000)
        except Exception as e:
            self._error(str(e))

    def delete_page(self):
        if not self._need_doc() or self.page_count() <= 1:
            return
        idx = self.current_page()
        try:
            self.doc.delete_page(idx)
            self.search_hits = {}
            self._mark_dirty()
            self._cache_page_sizes()
            self.render_all()
            self._rebuild_thumb_items()
            self.page_spin.setRange(1, self.page_count())
            self.goto_page(min(idx, self.page_count() - 1))
            self.status.showMessage(i18n.tr("page_deleted"), 3000)
        except Exception as e:
            self._error(str(e))

    def insert_pages(self):
        if not self._need_doc():
            return
        path, _ = QFileDialog.getOpenFileName(
            self, i18n.tr("source_file"), self._dialog_dir(), PDF_FILTER)
        if not path:
            return
        choice, ok = QInputDialog.getItem(
            self, i18n.tr("insert_pages"), i18n.tr("target_position"),
            [i18n.tr("after_current"), i18n.tr("at_end")], 0, False)
        if not ok:
            return
        try:
            start_at = (self.current_page() + 1 if choice == i18n.tr("after_current")
                        else self.page_count())
            with fitz.open(path) as src:
                self.doc.insert_pdf(src, start_at=start_at)
            self._mark_dirty()
            self._cache_page_sizes()
            self.render_all()
            self._rebuild_thumb_items()
            self.page_spin.setRange(1, self.page_count())
            self.goto_page(min(start_at, self.page_count() - 1))
            self._remember_dir(path)
            self.status.showMessage(i18n.tr("pages_inserted"), 3000)
        except Exception as e:
            self._error(str(e))

    def fill_forms(self):
        if not self._need_doc():
            return
        dlg = FormsDialog(self.doc, self)
        if dialog_exec(dlg) == QDialog.Accepted:
            try:
                changed = dlg.apply_values(self.doc)
                if changed:
                    self._mark_dirty()
                    self.render_all()
                self._info("forms_saved")
            except Exception as e:
                self._error(str(e))

    # ------------------------------------------------------------------
    # أدوات الملفات
    # ------------------------------------------------------------------
    def merge_files(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, i18n.tr("select_pdf"), self._dialog_dir(), PDF_FILTER)
        if paths:
            self._merge_paths(paths)

    def _merge_paths(self, paths):
        out = self._out_save_path("merged.pdf")
        if not out:
            return
        try:
            with self._busy(i18n.tr("merge")):
                pdf_ops.merge_pdfs(paths, out)
            self._remember_dir(out)
            self._info("merged")
            # من الشاشة الرئيسية: افتح الناتج مباشرة ليراه المستخدم
            if self.doc is None and os.path.exists(out):
                self.load_file(out)
        except Exception as e:
            self._error(str(e))

    def split_file(self):
        if not self._need_file():
            return
        dlg = SplitDialog(self.page_count(), self)
        if dialog_exec(dlg) != QDialog.Accepted:
            return
        mode, value = dlg.get_result()
        if mode == "ranges" and not value:
            self._error(i18n.tr("invalid_ranges"))
            return
        out_dir = self._out_folder()
        if not out_dir:
            return
        try:
            with self._busy(i18n.tr("split")):
                pdf_ops.split_pdf(
                    self.file_path, out_dir,
                    every=value if mode == "every" else None,
                    ranges_text=value if mode == "ranges" else None,
                    base_name=os.path.basename(self.file_path))
            self._info("split_done")
        except ValueError:
            self._error(i18n.tr("invalid_ranges"))
        except Exception as e:
            self._error(str(e))

    def compress_file(self):
        if not self._need_file():
            return
        out = self._out_save_path("compressed.pdf")
        if not out:
            return
        try:
            with self._busy(i18n.tr("compress")):
                pdf_ops.compress_pdf(self.file_path, out)
            self._info("compressed")
        except Exception as e:
            self._error(str(e))

    def protect_file(self):
        if not self._need_file():
            return
        pw, ok = QInputDialog.getText(
            self, i18n.tr("protect"), i18n.tr("password"), QLineEdit.Password)
        if not ok or not pw:
            return
        pw2, ok = QInputDialog.getText(
            self, i18n.tr("protect"), i18n.tr("confirm_password"),
            QLineEdit.Password)
        if not ok or pw != pw2:
            self._error(i18n.tr("wrong_password"))
            return
        out = self._out_save_path("protected.pdf")
        if not out:
            return
        try:
            with self._busy(i18n.tr("protect")):
                pdf_ops.encrypt_pdf(self.file_path, out, pw)
            self._info("protected")
        except Exception as e:
            self._error(str(e))

    def unlock_file(self):
        if not self._need_file():
            return
        pw, ok = QInputDialog.getText(
            self, i18n.tr("unlock"), i18n.tr("password"), QLineEdit.Password)
        if not ok:
            return
        out = self._out_save_path("unlocked.pdf")
        if not out:
            return
        try:
            with self._busy(i18n.tr("unlock")):
                pdf_ops.decrypt_pdf(self.file_path, out, pw)
            self._info("unlocked")
        except PermissionError:
            self._error(i18n.tr("wrong_password"))
        except Exception as e:
            self._error(str(e))

    def export_images(self):
        if not self._need_file():
            return
        dpi_s, ok = QInputDialog.getItem(
            self, i18n.tr("export_images"), i18n.tr("dpi"),
            ["72", "150", "300"], 1, False)
        if not ok:
            return
        fmt, ok = QInputDialog.getItem(
            self, i18n.tr("export_images"), i18n.tr("image_format"),
            ["png", "jpg"], 0, False)
        if not ok:
            return
        out_dir = self._out_folder()
        if not out_dir:
            return
        try:
            with self._busy(i18n.tr("export_images")):
                pdf_ops.pdf_to_images(self.file_path, out_dir,
                                      fmt=fmt, dpi=int(dpi_s))
            self._info("images_exported")
        except Exception as e:
            self._error(str(e))

    def export_text(self):
        if not self._need_file():
            return
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.tr("export_text"),
            os.path.join(self._dialog_dir(), "document.txt"), "Text (*.txt)")
        if not path:
            return
        try:
            with self._busy(i18n.tr("export_text")):
                pdf_ops.extract_text(self.file_path, path)
            self._remember_dir(path)
            self._info("text_exported")
        except Exception as e:
            self._error(str(e))

    def export_word(self):
        if not self._need_file():
            return
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.tr("export_word"),
            os.path.join(self._dialog_dir(), "document.docx"), "Word (*.docx)")
        if not path:
            return
        try:
            with self._busy(i18n.tr("export_word")):
                pdf_ops.pdf_to_word(self.file_path, path)
            self._remember_dir(path)
            self._info("saved")
        except Exception as e:
            self._error(str(e))

    def export_excel(self):
        if not self._need_file():
            return
        path, _ = QFileDialog.getSaveFileName(
            self, i18n.tr("export_excel"),
            os.path.join(self._dialog_dir(), "document.xlsx"), "Excel (*.xlsx)")
        if not path:
            return
        try:
            with self._busy(i18n.tr("export_excel")):
                pdf_ops.pdf_to_excel(self.file_path, path)
            self._remember_dir(path)
            self._info("saved")
        except Exception as e:
            self._error(str(e))

    def images_to_pdf(self):
        paths, _ = QFileDialog.getOpenFileNames(
            self, i18n.tr("select_images"), self._dialog_dir(), IMG_FILTER)
        if paths:
            self._images_to_pdf_paths(paths)

    def _images_to_pdf_paths(self, paths):
        out = self._out_save_path("images.pdf")
        if not out:
            return
        try:
            with self._busy(i18n.tr("images_to_pdf")):
                pdf_ops.images_to_pdf(paths, out)
            self._remember_dir(out)
            self._info("saved")
            if self.doc is None and os.path.exists(out):
                self.load_file(out)
        except Exception as e:
            self._error(str(e))

    def run_ocr(self):
        if not self._need_file():
            return
        try:
            import pytesseract  # noqa: F401
        except ImportError:
            QMessageBox.warning(self, i18n.tr("ocr"),
                                i18n.tr("ocr_not_installed"))
            return
        langs = list(pdf_ops.OCR_LANG_CODES.values())
        lang_name, ok = QInputDialog.getItem(
            self, i18n.tr("ocr"), i18n.tr("ocr_lang"), langs, 0, False)
        if not ok:
            return
        code = next(k for k, v in pdf_ops.OCR_LANG_CODES.items()
                    if v == lang_name)
        out = self._out_save_path("ocr.pdf")
        if not out:
            return
        try:
            with self._busy(i18n.tr("ocr")):
                pdf_ops.ocr_pdf(self.file_path, out, code)
            self._info("ocr_done")
        except Exception as e:
            self._error(str(e))

    # ------------------------------------------------------------------
    # اللغة والمساعدة
    # ------------------------------------------------------------------
    def change_language(self, code):
        i18n.set_language(code)
        self.settings.setValue("language", code)
        app = QApplication.instance()
        if app is not None:
            app.setLayoutDirection(
                Qt.RightToLeft if i18n.is_rtl(code) else Qt.LeftToRight)
        self._retranslate()
        self.status.showMessage(i18n.tr("language_changed"), 3000)

    def show_guide(self):
        dlg = GuideDialog(self)
        dialog_exec(dlg)

    def show_about(self):
        QMessageBox.about(self, i18n.tr("about"),
                          i18n.tr("about_text") + f"\n\nv{__version__}")

    # ------------------------------------------------------------------
    # السحب والإفلات
    # ------------------------------------------------------------------
    def _drop_paths(self, paths):
        pdfs = [p for p in paths if p.lower().endswith(".pdf")]
        images = [p for p in paths if p.lower().endswith(IMG_EXTS)]
        if len(pdfs) == 1:
            self.load_file(pdfs[0])
        elif len(pdfs) > 1:
            self._merge_paths(pdfs)
        elif images:
            self._images_to_pdf_paths(images)

    def dragEnterEvent(self, ev):
        urls = ev.mimeData().urls() if ev.mimeData() else []
        for url in urls:
            if url.isLocalFile():
                path = url.toLocalFile().lower()
                if path.endswith(".pdf") or path.endswith(IMG_EXTS):
                    ev.acceptProposedAction()
                    self.home.set_drag_active(True)
                    return
        ev.ignore()

    def dragMoveEvent(self, ev):
        ev.acceptProposedAction()

    def dragLeaveEvent(self, ev):
        self.home.set_drag_active(False)
        super().dragLeaveEvent(ev)

    def dropEvent(self, ev):
        self.home.set_drag_active(False)
        urls = ev.mimeData().urls() if ev.mimeData() else []
        paths = [u.toLocalFile() for u in urls if u.isLocalFile()]
        if paths:
            ev.acceptProposedAction()
            self._drop_paths(paths)

    # ------------------------------------------------------------------
    # أحداث النافذة
    # ------------------------------------------------------------------
    def eventFilter(self, obj, ev):
        """Ctrl + عجلة الفأرة = تكبير/تصغير"""
        try:
            if (self.doc is not None and ev.type() == QEvent.Wheel
                    and ev.modifiers() & Qt.ControlModifier):
                delta = ev.angleDelta().y()
                if delta > 0:
                    self.zoom_in()
                elif delta < 0:
                    self.zoom_out()
                ev.accept()
                return True
        except Exception:
            pass
        return super().eventFilter(obj, ev)

    def resizeEvent(self, ev):
        super().resizeEvent(ev)
        if hasattr(self, "home"):
            self.home.set_compact(self.height() < 660)
            self.home.reflow(self.scroll.viewport().width())
        self._update_sidebar()
        self._update_thumbs_visible()
        self._schedule_refit()

    def showEvent(self, ev):
        super().showEvent(ev)
        if self._first_show:
            self._first_show = False
            self.home.set_compact(self.height() < 660)
            self.home.reflow(self.scroll.viewport().width())
            self._schedule_refit()

    def closeEvent(self, ev):
        if not self._confirm_discard():
            ev.ignore()
            return
        self.settings.setValue("geometry", self.saveGeometry())
        self.settings.setValue("sidebar_visible", self._sidebar_user_visible)
        if self.doc:
            try:
                self.doc.close()
            except Exception:
                pass
            self.doc = None
        ev.accept()
