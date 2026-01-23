from __future__ import annotations

from typing import Iterable, List, Optional, Union
from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QListWidget, QListWidgetItem, QPushButton, QHBoxLayout
)


class SubclassSelectionDialog(QDialog):
    """Multi or single selection dialog for choosing subclasses/archetypes."""

    def __init__(self, subclasses: Iterable[str], multi: bool = True, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Subclass / Archetype Seçimi")
        self.resize(420, 320)

        layout = QVBoxLayout(self)

        self.list_widget = QListWidget(self)
        mode = QListWidget.MultiSelection if multi else QListWidget.SingleSelection
        self.list_widget.setSelectionMode(mode)
        for name in subclasses:
            item = QListWidgetItem(name)
            self.list_widget.addItem(item)
        if self.list_widget.count() > 0:
            self.list_widget.setCurrentRow(0)
        layout.addWidget(self.list_widget)

        btn_layout = QHBoxLayout()
        self.ok_btn = QPushButton("Seç", self)
        self.cancel_btn = QPushButton("İptal", self)
        btn_layout.addWidget(self.ok_btn)
        btn_layout.addWidget(self.cancel_btn)
        layout.addLayout(btn_layout)

        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)

    def selected(self) -> List[str]:
        return [item.text() for item in self.list_widget.selectedItems()]

    @staticmethod
    def select_subclass(parent, subclasses: Iterable[str], multi: bool = True) -> Union[Optional[str], List[str]]:
        dlg = SubclassSelectionDialog(subclasses, multi=multi, parent=parent)
        if dlg.exec() == QDialog.Accepted:
            selected = dlg.selected()
            if multi:
                return selected
            return selected[0] if selected else None
        return [] if multi else None
