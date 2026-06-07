"""
Active Character Sheet
======================
Seçilen bir karakterin tüm bilgilerini sekmeli (tabbed) bir
dashboard'da gösterir.

Sekmeler:
  - Overview  : Temel bilgiler + yetenek puanları
  - Combat    : AC, HP, initiative, saving throws
  - Skills    : Beceri listesi + modifier'lar
  - Inventory : Ekipman tablosu
  - Export    : PDF / JSON dışa aktarma

Hesaplamalar doğrudan backend modüllerine (creators/, utils/) delege edilir.
"""

from __future__ import annotations

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QTabWidget, QGroupBox, QGridLayout, QFormLayout, QTextEdit,
    QTableWidget, QTableWidgetItem, QHeaderView, QFileDialog, QMessageBox,
)

from creators import CreatorFactory
from creators.base_creator import BaseCharacterCreator
from utils.storage import load_character, CharacterRecord

logger = logging.getLogger(__name__)


class CharacterSheetPage(QWidget):
    """Karakter detay sayfası: sekmeli dashboard."""

    def __init__(self, db_path: Path, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._db_path = db_path
        self._record: Optional[CharacterRecord] = None
        self._char: Dict[str, Any] = {}
        self._creator: Optional[BaseCharacterCreator] = None
        self._build()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def load_character(self, record_id: int) -> None:
        """Bir karakteri yükle ve göster."""
        rec = load_character(self._db_path, record_id)
        if not rec:
            return
        self._record = rec
        self._char = rec.data

        sys_key = rec.system.lower().replace("_", "")
        try:
            self._creator = CreatorFactory.create(sys_key)
            stats = self._creator.calculate_stats(self._char)
            self._char.update(stats)
        except ValueError:
            self._creator = None

        self._refresh_all()

    # ------------------------------------------------------------------
    # UI Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)

        self._title = QLabel("Karakter Sayfası")
        self._title.setObjectName("PageTitle")
        root.addWidget(self._title)

        self._tabs = QTabWidget()
        root.addWidget(self._tabs, stretch=1)

        self._overview_tab = QWidget()
        self._combat_tab = QWidget()
        self._skills_tab = QWidget()
        self._inventory_tab = QWidget()
        self._export_tab = QWidget()

        self._tabs.addTab(self._overview_tab, "Genel Bakış")
        self._tabs.addTab(self._combat_tab, "Savaş")
        self._tabs.addTab(self._skills_tab, "Beceriler")
        self._tabs.addTab(self._inventory_tab, "Envanter")
        self._tabs.addTab(self._export_tab, "Dışa Aktar")

        self._build_overview()
        self._build_combat()
        self._build_skills()
        self._build_inventory()
        self._build_export()

        self._empty = QLabel("Tavern'den bir karakter seçin veya Forge'da yeni bir karakter oluşturun.")
        self._empty.setAlignment(Qt.AlignCenter)
        self._empty.setStyleSheet("color: #8b949e; font-size: 14px; padding: 40px;")
        root.addWidget(self._empty)
        self._tabs.hide()

    def _build_overview(self) -> None:
        lay = QVBoxLayout(self._overview_tab)
        self._info_form = QFormLayout()
        self._info_labels: Dict[str, QLabel] = {}
        for key, label_text in [
            ("name", "İsim"), ("system", "Sistem"), ("race", "Irk / Clan"),
            ("class", "Sınıf"), ("level", "Seviye"), ("background", "Arka Plan"),
        ]:
            lbl = QLabel("—")
            self._info_labels[key] = lbl
            self._info_form.addRow(f"{label_text}:", lbl)
        lay.addLayout(self._info_form)

        ability_group = QGroupBox("Yetenek Puanları")
        self._ability_grid = QGridLayout(ability_group)
        self._ability_labels: Dict[str, tuple] = {}
        abilities = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
        for i, ab in enumerate(abilities):
            name_lbl = QLabel(ab.title())
            score_lbl = QLabel("—")
            score_lbl.setObjectName("StatValue")
            mod_lbl = QLabel("")
            mod_lbl.setStyleSheet("color: #d4c5a9;")
            col = (i % 3) * 3
            row = i // 3
            self._ability_grid.addWidget(name_lbl, row, col)
            self._ability_grid.addWidget(score_lbl, row, col + 1)
            self._ability_grid.addWidget(mod_lbl, row, col + 2)
            self._ability_labels[ab] = (score_lbl, mod_lbl)
        lay.addWidget(ability_group)
        lay.addStretch()

    def _build_combat(self) -> None:
        lay = QVBoxLayout(self._combat_tab)
        self._combat_labels: Dict[str, QLabel] = {}

        stats_group = QGroupBox("Savaş İstatistikleri")
        grid = QGridLayout(stats_group)
        combat_fields = [
            ("hit_points", "HP"), ("armor_class", "AC"),
            ("initiative", "İnisiyatif"), ("proficiency_bonus", "Proficiency"),
            ("movement_speed", "Hız"), ("hit_dice", "Can Zarı"),
        ]
        for i, (key, label_text) in enumerate(combat_fields):
            title_lbl = QLabel(label_text)
            title_lbl.setStyleSheet("font-weight: bold; color: #d4c5a9;")
            val_lbl = QLabel("—")
            val_lbl.setObjectName("StatValue")
            self._combat_labels[key] = val_lbl
            col = (i % 3) * 2
            row = i // 3
            grid.addWidget(title_lbl, row, col)
            grid.addWidget(val_lbl, row, col + 1)
        lay.addWidget(stats_group)

        saves_group = QGroupBox("Saving Throws")
        self._saves_form = QFormLayout(saves_group)
        self._save_labels: Dict[str, QLabel] = {}
        for ab in ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]:
            lbl = QLabel("—")
            self._save_labels[ab] = lbl
            self._saves_form.addRow(f"{ab}:", lbl)
        lay.addWidget(saves_group)
        lay.addStretch()

    def _build_skills(self) -> None:
        lay = QVBoxLayout(self._skills_tab)
        self._skills_table = QTableWidget()
        self._skills_table.setColumnCount(2)
        self._skills_table.setHorizontalHeaderLabels(["Beceri", "Modifier"])
        self._skills_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._skills_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._skills_table.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._skills_table)

    def _build_inventory(self) -> None:
        lay = QVBoxLayout(self._inventory_tab)
        self._inv_table = QTableWidget()
        self._inv_table.setColumnCount(4)
        self._inv_table.setHorizontalHeaderLabels(["Eşya", "Tür", "Adet", "Ağırlık"])
        self._inv_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._inv_table.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._inv_table)

    def _build_export(self) -> None:
        lay = QVBoxLayout(self._export_tab)
        lay.setSpacing(16)

        info = QLabel("Karakterini farklı formatlarda dışa aktar.")
        info.setStyleSheet("color: #d4c5a9; font-size: 13px;")
        lay.addWidget(info)

        pdf_btn = QPushButton("PDF Karakter Kağıdı")
        pdf_btn.setMinimumHeight(40)
        pdf_btn.clicked.connect(self._export_pdf)
        lay.addWidget(pdf_btn)

        json_btn = QPushButton("JSON Dışa Aktar")
        json_btn.setMinimumHeight(40)
        json_btn.clicked.connect(self._export_json)
        lay.addWidget(json_btn)

        lay.addStretch()

    # ------------------------------------------------------------------
    # Refresh
    # ------------------------------------------------------------------

    def _refresh_all(self) -> None:
        if not self._record:
            return

        self._empty.hide()
        self._tabs.show()
        self._title.setText(f"{self._record.name}")

        c = self._char

        for key, lbl in self._info_labels.items():
            val = c.get(key, "—")
            if key == "race":
                val = c.get("race", c.get("clan", "—"))
            elif key == "class":
                val = c.get("class", c.get("archetype", "—"))
            lbl.setText(str(val) if val else "—")

        abilities = c.get("abilities", {})
        for ab, (score_lbl, mod_lbl) in self._ability_labels.items():
            score = abilities.get(ab, abilities.get(ab.title(), ""))
            if isinstance(score, (int, float)):
                mod = (int(score) - 10) // 2
                score_lbl.setText(str(int(score)))
                mod_lbl.setText(f"({mod:+d})")
            else:
                score_lbl.setText("—")
                mod_lbl.setText("")

        for key, lbl in self._combat_labels.items():
            val = c.get(key, "—")
            lbl.setText(str(val) if val is not None else "—")

        saves = c.get("saving_throws", {})
        for ab, lbl in self._save_labels.items():
            val = saves.get(ab, "—")
            lbl.setText(f"{val:+d}" if isinstance(val, int) else str(val))

        skills = c.get("skills", {})
        if isinstance(skills, dict) and all(isinstance(v, (int, float)) for v in skills.values()):
            self._skills_table.setRowCount(len(skills))
            for row, (sk, val) in enumerate(sorted(skills.items())):
                self._skills_table.setItem(row, 0, QTableWidgetItem(sk))
                self._skills_table.setItem(row, 1, QTableWidgetItem(f"{val:+d}" if isinstance(val, int) else str(val)))
        else:
            self._skills_table.setRowCount(0)

        equipment = c.get("equipment", [])
        self._inv_table.setRowCount(len(equipment))
        for row, item in enumerate(equipment):
            if isinstance(item, str):
                self._inv_table.setItem(row, 0, QTableWidgetItem(item))
            elif isinstance(item, dict):
                self._inv_table.setItem(row, 0, QTableWidgetItem(item.get("name", "")))
                self._inv_table.setItem(row, 1, QTableWidgetItem(item.get("type", "")))
                self._inv_table.setItem(row, 2, QTableWidgetItem(str(item.get("quantity", 1))))
                self._inv_table.setItem(row, 3, QTableWidgetItem(str(item.get("weight", ""))))

    # ------------------------------------------------------------------
    # Export (backend'e delege)
    # ------------------------------------------------------------------

    def _export_pdf(self) -> None:
        if not self._char:
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "PDF Kaydet", f"{self._char.get('name', 'karakter')}.pdf", "PDF (*.pdf)",
        )
        if not filepath:
            return
        try:
            system = self._char.get("system", "").upper()
            out = Path(filepath)
            if "DND" in system:
                from utils.export_pdf import export_dnd_character_pdf
                export_dnd_character_pdf(self._char, out)
            elif "MM" in system:
                from utils.export_pdf import export_mm_character_pdf
                export_mm_character_pdf(self._char, out)
            else:
                from utils.export_pdf import export_dnd_character_pdf
                export_dnd_character_pdf(self._char, out)
            QMessageBox.information(self, "Başarılı", f"PDF kaydedildi:\n{filepath}")
        except Exception as exc:
            logger.exception("PDF export hatası")
            QMessageBox.critical(self, "Hata", str(exc))

    def _export_json(self) -> None:
        if not self._char or not self._creator:
            return
        filepath, _ = QFileDialog.getSaveFileName(
            self, "JSON Kaydet", f"{self._char.get('name', 'karakter')}.json", "JSON (*.json)",
        )
        if not filepath:
            return
        try:
            exported = self._creator.export_data(self._char)
            with open(filepath, "w", encoding="utf-8") as fh:
                json.dump(exported, fh, indent=2, ensure_ascii=False, default=str)
            QMessageBox.information(self, "Başarılı", f"JSON kaydedildi:\n{filepath}")
        except Exception as exc:
            logger.exception("JSON export hatası")
            QMessageBox.critical(self, "Hata", str(exc))
