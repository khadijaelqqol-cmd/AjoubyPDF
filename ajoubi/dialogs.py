# -*- coding: utf-8 -*-
"""نوافذ حوار مساعدة: التقسيم، تعبئة النماذج، ودليل الاستخدام"""

import os

from .qt_compat import (
    Qt, QDialog, QVBoxLayout, QHBoxLayout, QRadioButton, QSpinBox, QLineEdit,
    QLabel, QDialogButtonBox, QTableWidget, QTableWidgetItem, QHeaderView,
    QButtonGroup, QTextBrowser, QPixmap,
)

from . import i18n, guide


class SplitDialog(QDialog):
    """حوار تقسيم الملف: كل N صفحة أو نطاقات يدوية"""

    def __init__(self, page_count, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.tr("tools_menu") + " - " + i18n.tr("split"))
        self.setMinimumWidth(430)
        self.setMinimumHeight(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 18, 20, 16)
        layout.setSpacing(10)

        intro = QLabel(i18n.tr("split_mode"))
        intro.setStyleSheet("font-size:11pt; font-weight:600;")
        layout.addWidget(intro)

        total = QLabel(i18n.tr("page_status").format(1, page_count))
        total.setStyleSheet("color:#667485;")
        layout.addWidget(total)

        self.radio_every = QRadioButton(i18n.tr("split_every").format(0))
        self.radio_ranges = QRadioButton(i18n.tr("split_ranges"))

        row_every = QHBoxLayout()
        row_every.addWidget(self.radio_every, 1)
        self.spin = QSpinBox()
        self.spin.setRange(1, max(1, page_count))
        self.spin.setValue(1)
        self.spin.setFixedWidth(90)
        row_every.addWidget(self.spin)
        layout.addLayout(row_every)

        row_ranges = QHBoxLayout()
        self.edit_ranges = QLineEdit()
        self.edit_ranges.setPlaceholderText("1-3,5,8-10")
        self.edit_ranges.setEnabled(False)
        row_ranges.addWidget(self.radio_ranges)
        row_ranges.addWidget(self.edit_ranges, 1)
        layout.addLayout(row_ranges)

        layout.addStretch(1)

        self.group = QButtonGroup(self)
        self.group.addButton(self.radio_every)
        self.group.addButton(self.radio_ranges)
        self.radio_every.setChecked(True)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

        self.radio_every.toggled.connect(self._sync_mode)
        self.radio_ranges.toggled.connect(self._sync_mode)
        self.retranslate_spin()
        self.spin.valueChanged.connect(self.retranslate_spin)
        self._sync_mode()

    def _sync_mode(self, *_args):
        every = self.radio_every.isChecked()
        self.spin.setEnabled(every)
        self.edit_ranges.setEnabled(not every)
        if not every:
            self.edit_ranges.setFocus()

    def retranslate_spin(self):
        self.radio_every.setText(i18n.tr("split_every").format(self.spin.value()))

    def get_result(self):
        if self.radio_every.isChecked():
            return "every", self.spin.value()
        return "ranges", self.edit_ranges.text().strip()


class FormsDialog(QDialog):
    """حوار عرض وتعبئة حقول النماذج (حقول النص قابلة للتحرير)"""

    def __init__(self, doc, parent=None):
        super().__init__(parent)
        self.setWindowTitle(i18n.tr("forms"))
        self.setMinimumSize(560, 400)
        self.widgets = []  # قائمة حقول النص القابلة للتعديل

        layout = QVBoxLayout(self)
        layout.setContentsMargins(18, 16, 18, 14)
        layout.setSpacing(10)

        self.table = QTableWidget(0, 2, self)
        self.table.setHorizontalHeaderLabels([i18n.tr("form_name"), i18n.tr("form_value")])
        self.table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.Stretch)
        self.table.verticalHeader().setVisible(False)
        layout.addWidget(self.table)

        for page in doc:
            try:
                widgets = list(page.widgets() or [])
            except Exception:
                widgets = []
            for w in widgets:
                row = self.table.rowCount()
                self.table.insertRow(row)
                name_item = QTableWidgetItem(w.field_name or "")
                name_item.setFlags(name_item.flags() & ~Qt.ItemIsEditable)
                self.table.setItem(row, 0, name_item)
                if w.field_type_string == "Text":
                    self.table.setItem(row, 1, QTableWidgetItem(w.field_value or ""))
                    self.widgets.append((w, row))
                else:
                    info = QTableWidgetItem(
                        f"[{w.field_type_string}] {w.field_value if w.field_value is not None else ''}"
                    )
                    info.setFlags(info.flags() & ~Qt.ItemIsEditable)
                    self.table.setItem(row, 1, info)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def apply_values(self, doc):
        """يكتب القيم إلى المستند - يرجع عدد الحقول المعدلة"""
        changed = 0
        for w, row in self.widgets:
            item = self.table.item(row, 1)
            new_val = item.text() if item else ""
            try:
                w.field_value = new_val
                w.update()
                changed += 1
            except Exception:
                pass
        return changed


class GuideDialog(QDialog):
    """دليل الاستخدام داخل البرنامج: نص منسّق خفيف بلا صور ثقيلة"""

    def __init__(self, parent=None, lang=None):
        super().__init__(parent)
        code = lang or i18n.get_language()
        self.setObjectName("guideDialog")
        self.setWindowTitle(i18n.tr("guide"))
        self.resize(840, 660)
        self.setMinimumSize(560, 420)

        root = QVBoxLayout(self)
        root.setContentsMargins(18, 16, 18, 14)
        root.setSpacing(10)

        header = QHBoxLayout()
        header.setSpacing(12)
        from .qt_compat import app_icon_path
        icon_path = app_icon_path()
        if os.path.exists(icon_path):
            pm = QPixmap(icon_path)
            if not pm.isNull():
                logo = QLabel()
                logo.setPixmap(pm.scaled(44, 44, Qt.KeepAspectRatio,
                                         Qt.SmoothTransformation))
                header.addWidget(logo, 0, Qt.AlignTop)

        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel(i18n.tr("guide"))
        title.setObjectName("guideTitle")
        subtitle = QLabel(guide.content(code)["subtitle"])
        subtitle.setObjectName("guideSubtitle")
        subtitle.setWordWrap(True)
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header.addLayout(titles, 1)
        root.addLayout(header)

        self.view = QTextBrowser()
        self.view.setObjectName("guideView")
        self.view.setOpenExternalLinks(False)
        self.view.setHtml(guide.html(code))
        self.view.setFocusPolicy(Qt.StrongFocus)
        root.addWidget(self.view, 1)

        buttons = QDialogButtonBox(QDialogButtonBox.Close)
        close_btn = buttons.button(QDialogButtonBox.Close)
        if close_btn is not None:
            close_btn.setText(i18n.tr("close"))
        buttons.rejected.connect(self.reject)
        root.addWidget(buttons)
