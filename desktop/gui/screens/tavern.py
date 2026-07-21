"""
The Tavern (Dashboard)
======================
Kayıtlı karakterleri görsel kartlar halinde listeler.
SQLite'tan okuma ve silme işlemleri backend üzerinden yapılır.
"""

from __future__ import annotations

from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QScrollArea, QFrame, QGridLayout, QLineEdit, QComboBox,
)

from utils.storage import list_characters, delete_character, CharacterRecord

SYSTEM_BADGES = {
    "DND5E": "D&D 5e", "PATHFINDER_1E": "PF 1e", "PATHFINDER1E": "PF 1e",
    "MM3E": "M&M 3e",
}


class CharacterCard(QFrame):
    """Tek bir karakter için görsel kart."""

    load_requested = Signal(int)
    delete_requested = Signal(int)

    def __init__(self, record: CharacterRecord, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self.setObjectName("Card")
        self.setFixedHeight(160)
        self._record = record
        self._build()

    def _build(self) -> None:
        layout = QVBoxLayout(self)
        layout.setSpacing(4)

        data = self._record.data
        system_label = SYSTEM_BADGES.get(self._record.system, self._record.system)

        badge = QLabel(system_label)
        badge.setStyleSheet(
            "background-color: #c9a84c; color: #0f0f1a; font-weight: bold; "
            "font-size: 10px; padding: 2px 8px; border-radius: 4px;"
        )
        badge.setFixedWidth(badge.fontMetrics().horizontalAdvance(system_label) + 20)

        name_lbl = QLabel(self._record.name)
        name_lbl.setStyleSheet("font-size: 16px; font-weight: bold; color: #c9a84c;")

        race = data.get("race", data.get("clan", ""))
        cls = data.get("class", data.get("archetype", ""))
        level = data.get("level", data.get("pl_value", ""))
        detail_text = " | ".join(filter(None, [race, cls, f"Lv {level}" if level else ""]))
        detail_lbl = QLabel(detail_text)
        detail_lbl.setStyleSheet("color: #d4c5a9; font-size: 12px;")

        date_lbl = QLabel(f"Son güncelleme: {(self._record.updated_at or '')[:16]}")
        date_lbl.setStyleSheet("color: #8b949e; font-size: 10px;")

        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)

        load_btn = QPushButton("Yükle")
        load_btn.setCursor(Qt.PointingHandCursor)
        load_btn.clicked.connect(lambda: self.load_requested.emit(self._record.id))

        del_btn = QPushButton("Sil")
        del_btn.setObjectName("DangerButton")
        del_btn.setCursor(Qt.PointingHandCursor)
        del_btn.clicked.connect(lambda: self.delete_requested.emit(self._record.id))

        btn_row.addWidget(load_btn)
        btn_row.addWidget(del_btn)
        btn_row.addStretch()

        layout.addWidget(badge)
        layout.addWidget(name_lbl)
        layout.addWidget(detail_lbl)
        layout.addStretch()
        layout.addWidget(date_lbl)
        layout.addLayout(btn_row)


class TavernPage(QWidget):
    """Dashboard: kayıtlı karakterlerin kart listesi."""

    character_selected = Signal(int)

    def __init__(self, db_path: Path, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._db_path = db_path
        self._build()

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)

        title = QLabel("The Tavern")
        title.setObjectName("PageTitle")

        toolbar = QHBoxLayout()
        self._search = QLineEdit()
        self._search.setPlaceholderText("Karakter ara...")
        self._search.setMaximumWidth(260)
        self._search.textChanged.connect(self._on_filter)

        self._system_filter = QComboBox()
        self._system_filter.addItem("Tüm Sistemler", "")
        for key, label in SYSTEM_BADGES.items():
            self._system_filter.addItem(label, key)
        self._system_filter.setMaximumWidth(160)
        self._system_filter.currentIndexChanged.connect(self._on_filter)

        refresh_btn = QPushButton("Yenile")
        refresh_btn.clicked.connect(self.refresh)

        toolbar.addWidget(self._search)
        toolbar.addWidget(self._system_filter)
        toolbar.addStretch()
        toolbar.addWidget(refresh_btn)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self._grid_widget = QWidget()
        self._grid_layout = QGridLayout(self._grid_widget)
        self._grid_layout.setSpacing(16)
        self._grid_layout.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        scroll.setWidget(self._grid_widget)

        self._empty_label = QLabel("Henüz karakter yok. The Forge'a gidip ilk karakterini oluştur!")
        self._empty_label.setStyleSheet("color: #8b949e; font-size: 14px; padding: 40px;")
        self._empty_label.setAlignment(Qt.AlignCenter)
        self._empty_label.hide()

        root.addWidget(title)
        root.addLayout(toolbar)
        root.addWidget(scroll, stretch=1)
        root.addWidget(self._empty_label)

    def refresh(self) -> None:
        """Karakter listesini SQLite'tan yenile."""
        self._on_filter()

    def showEvent(self, event) -> None:
        super().showEvent(event)
        self.refresh()

    def _on_filter(self) -> None:
        from desktop import local_db
        search_text = self._search.text().strip()
        system_key = self._system_filter.currentData() or None

        local_recs = local_db.list_local_characters(self._db_path, system=system_key)
        records = []
        for lr in local_recs:
            dirty_badge = " 🔄" if lr.is_dirty else ""
            records.append(CharacterRecord(
                id=lr.id, system=lr.system, name=f"{lr.name}{dirty_badge}", data=lr.data,
                created_at=lr.created_at, updated_at=lr.updated_at
            ))

        if search_text:
            search_lower = search_text.lower()
            records = [r for r in records if search_lower in r.name.lower()]

        while self._grid_layout.count():
            item = self._grid_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        self._empty_label.setVisible(len(records) == 0)

        cols = max(1, self.width() // 300)
        for i, rec in enumerate(records):
            card = CharacterCard(rec)
            card.load_requested.connect(self.character_selected.emit)
            card.delete_requested.connect(self._on_delete)
            self._grid_layout.addWidget(card, i // cols, i % cols)

    def _on_delete(self, record_id: int) -> None:
        from PySide6.QtWidgets import QMessageBox
        from desktop import local_db
        reply = QMessageBox.question(
            self, "Onay", "Bu karakter kalıcı olarak silinecek. Emin misin?",
            QMessageBox.Yes | QMessageBox.No, QMessageBox.No,
        )
        if reply == QMessageBox.Yes:
            local_db.delete_local_character(self._db_path, record_id)
            self.refresh()
