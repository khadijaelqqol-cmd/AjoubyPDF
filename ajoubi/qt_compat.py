# -*- coding: utf-8 -*-
"""طبقة توافق Qt: PySide6 (ويندوز 10+) أو PySide2 (ويندوز 7/8)
الاستيراد دائماً من هذه الوحدة بدلاً من PySide مباشرة"""

try:
    # ---------- Qt 6 (PySide6) ----------
    IS_QT6 = True

    from PySide6.QtCore import (
        Qt, QSettings, QRectF, QSize, QPointF, QTimer, QUrl, QEvent,
    )
    from PySide6.QtGui import (
        QAction, QActionGroup, QImage, QPixmap, QPainter, QColor, QKeySequence,
        QIcon, QPixmapCache, QPen, QBrush, QFont, QPolygonF, QPainterPath,
    )
    from PySide6.QtWidgets import (
        QMainWindow, QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout,
        QHBoxLayout, QGridLayout, QListWidget, QListWidgetItem, QToolBar,
        QStatusBar, QFileDialog, QMessageBox, QInputDialog, QSpinBox, QLineEdit,
        QToolButton, QSizePolicy, QSplitter, QDialog, QDialogButtonBox,
        QRadioButton, QTableWidget, QTableWidgetItem, QHeaderView, QButtonGroup,
        QPushButton, QTextBrowser, QFrame, QMenu,
    )

    def app_exec(app):
        return app.exec()

    def dialog_exec(dlg):
        return dlg.exec()


except ImportError:
    # ---------- Qt 5 (PySide2) - ويندوز 7/8 ----------
    IS_QT6 = False

    from PySide2.QtCore import (
        Qt, QSettings, QRectF, QSize, QPointF, QTimer, QUrl, QEvent,
    )
    from PySide2.QtGui import (
        QImage, QPixmap, QPainter, QColor, QKeySequence, QIcon, QPixmapCache,
        QPen, QBrush, QFont, QPolygonF, QPainterPath,
    )
    from PySide2.QtWidgets import (
        QMainWindow, QApplication, QWidget, QLabel, QScrollArea, QVBoxLayout,
        QHBoxLayout, QGridLayout, QListWidget, QListWidgetItem, QToolBar,
        QStatusBar, QFileDialog, QMessageBox, QInputDialog, QSpinBox, QLineEdit,
        QToolButton, QSizePolicy, QSplitter, QDialog, QDialogButtonBox,
        QRadioButton, QTableWidget, QTableWidgetItem, QHeaderView, QButtonGroup,
        QPushButton, QTextBrowser, QFrame, QMenu,
        QAction, QActionGroup,  # في Qt5 هذه في QtWidgets
    )

    def app_exec(app):
        return app.exec_()

    def dialog_exec(dlg):
        return dlg.exec_()


def enable_high_dpi():
    """تمكين دقة الشاشات العالية (ضروري على Qt5، افتراضي في Qt6)"""
    if not IS_QT6:
        QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
        QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)


def _base_dir():
    import os
    import sys
    if getattr(sys, "frozen", False):
        return getattr(sys, "_MEIPASS", os.path.dirname(sys.executable))
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def app_icon_path():
    """مسار أيقونة البرنامج (يعمل في التطوير وفي الملف المجمّع)"""
    import os
    return os.path.join(_base_dir(), "assets", "ajouby.ico")


def app_png_path():
    """مسار نسخة PNG من الأيقونة (لشاشة الترحيب)"""
    import os
    return os.path.join(_base_dir(), "assets", "ajouby.png")
