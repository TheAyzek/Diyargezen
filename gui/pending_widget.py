from __future__ import annotations

from typing import List, Callable, Optional
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QLabel, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout
)


class PendingChoicesWidget(QWidget):
    """A small side-panel widget that shows pending choices and allows apply/clear."""

    def __init__(self, on_apply: Optional[Callable[[List[str]], None]] = None,
                 on_clear: Optional[Callable[[], None]] = None, parent=None):
        super().__init__(parent)
        self.on_apply = on_apply
        self.on_clear = on_clear

        self.setMinimumWidth(260)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(6, 6, 6, 6)

        self.title = QLabel("Bekleyen Seçimler")
        layout.addWidget(self.title)

        self.list_widget = QListWidget(self)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.apply_btn = QPushButton("Uygula")
        self.clear_btn = QPushButton("Temizle")
        btn_layout.addWidget(self.apply_btn)
        btn_layout.addWidget(self.clear_btn)
        layout.addLayout(btn_layout)

        self.apply_btn.clicked.connect(self._on_apply)
        self.clear_btn.clicked.connect(self._on_clear)

    def set_pending(self, items: List[str]):
        self.list_widget.clear()
        for it in items:
            QListWidgetItem(it, self.list_widget)

    def _on_apply(self):
        items = [self.list_widget.item(i).text() for i in range(self.list_widget.count())]
        if self.on_apply:
            self.on_apply(items)

    def _on_clear(self):
        if self.on_clear:
            self.on_clear()
        self.list_widget.clear()
