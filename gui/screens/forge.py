"""
The Forge (Creation Wizard)
===========================
Adım adım karakter oluşturma sihirbazı.
  Step 1: Sistem + İsim
  Step 2: Irk / Clan / Arketip
  Step 3: Sınıf (d20 sistemler için)
  Step 4: Yetenek Puanları
  Step 5: Özet + Kaydet

İş mantığı kesinlikle backend modüllerine (creators/, utils/) delege edilir.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, Optional

from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QStackedWidget, QFrame,
    QGridLayout, QTextEdit, QMessageBox, QGroupBox, QFormLayout,
    QListWidget, QListWidgetItem, QAbstractItemView,
)

from creators import CreatorFactory
from creators.base_creator import BaseCharacterCreator
from utils.storage import save_character, CharacterRecord
from utils.soft_validation import (
    validate_character_soft,
    mark_homebrew,
    format_warning_message,
)

logger = logging.getLogger(__name__)

SYSTEM_MAP = {
    "pathfinder1e": "Pathfinder 1st Edition",
    "dnd5e": "D&D 5th Edition",
    "mm3e": "Mutants & Masterminds 3e",
}

D20_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]


class ForgePage(QWidget):
    """Adım adım karakter oluşturma ekranı."""

    character_created = Signal(int)

    def __init__(self, db_path: Path, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._db_path = db_path
        self._creator: Optional[BaseCharacterCreator] = None
        self._build()

    # ------------------------------------------------------------------
    # UI Build
    # ------------------------------------------------------------------

    def _build(self) -> None:
        root = QVBoxLayout(self)
        root.setContentsMargins(24, 16, 24, 16)

        title = QLabel("The Forge")
        title.setObjectName("PageTitle")
        root.addWidget(title)

        self._steps = QStackedWidget()
        root.addWidget(self._steps, stretch=1)

        self._build_step1()
        self._build_step2()
        self._build_step3()
        self._build_step4()
        self._build_step5()

        nav = QHBoxLayout()
        self._back_btn = QPushButton("Geri")
        self._back_btn.clicked.connect(self._go_back)
        self._next_btn = QPushButton("İleri")
        self._next_btn.clicked.connect(self._go_next)

        nav.addWidget(self._back_btn)
        nav.addStretch()

        self._step_label = QLabel("Adım 1 / 5")
        self._step_label.setStyleSheet("color: #8b949e; font-size: 12px;")
        nav.addWidget(self._step_label)

        nav.addStretch()
        nav.addWidget(self._next_btn)
        root.addLayout(nav)

        self._update_nav()

    # ---- Step 1: System + Name ----
    def _build_step1(self) -> None:
        page = QFrame()
        page.setObjectName("StepPanel")
        lay = QFormLayout(page)
        lay.setSpacing(12)

        lay.addRow(QLabel("Sistem ve isim seçimi"))

        self._sys_combo = QComboBox()
        for key, label in SYSTEM_MAP.items():
            self._sys_combo.addItem(label, key)
        lay.addRow("TTRPG Sistemi:", self._sys_combo)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Karakterinin adını gir...")
        lay.addRow("Karakter Adı:", self._name_edit)

        self._steps.addWidget(page)

    # ---- Step 2: Race / Clan ----
    def _build_step2(self) -> None:
        page = QFrame()
        page.setObjectName("StepPanel")
        lay = QVBoxLayout(page)

        self._race_title = QLabel("Irk / Clan Seçimi")
        self._race_title.setObjectName("SectionHeader")
        lay.addWidget(self._race_title)

        self._race_combo = QComboBox()
        lay.addWidget(self._race_combo)

        self._race_info = QTextEdit()
        self._race_info.setReadOnly(True)
        self._race_info.setMaximumHeight(120)
        lay.addWidget(self._race_info)
        lay.addStretch()

        self._steps.addWidget(page)

    # ---- Step 3: Class ----
    def _build_step3(self) -> None:
        page = QFrame()
        page.setObjectName("StepPanel")
        lay = QVBoxLayout(page)

        self._class_title = QLabel("Sınıf Seçimi")
        self._class_title.setObjectName("SectionHeader")
        lay.addWidget(self._class_title)

        self._class_combo = QComboBox()
        lay.addWidget(self._class_combo)

        self._class_info = QTextEdit()
        self._class_info.setReadOnly(True)
        self._class_info.setMaximumHeight(120)
        lay.addWidget(self._class_info)

        self._spell_group = QGroupBox("Büyüler (opsiyonel — çoklu seçim)")
        spell_lay = QVBoxLayout(self._spell_group)
        self._spell_filter = QLineEdit()
        self._spell_filter.setPlaceholderText("Büyü ara...")
        self._spell_filter.textChanged.connect(self._filter_spells)
        spell_lay.addWidget(self._spell_filter)
        self._spell_list = QListWidget()
        self._spell_list.setSelectionMode(QAbstractItemView.MultiSelection)
        self._spell_list.setMaximumHeight(140)
        spell_lay.addWidget(self._spell_list)
        self._all_spell_names: list[str] = []
        lay.addWidget(self._spell_group)
        self._spell_group.hide()

        lay.addStretch()

        self._steps.addWidget(page)

    # ---- Step 4: Abilities ----
    def _build_step4(self) -> None:
        page = QFrame()
        page.setObjectName("StepPanel")
        lay = QVBoxLayout(page)

        header = QLabel("Yetenek Puanları")
        header.setObjectName("SectionHeader")
        lay.addWidget(header)

        self._roll_btn = QPushButton("4d6 Drop Lowest ile At")
        self._roll_btn.setObjectName("SuccessButton")
        self._roll_btn.clicked.connect(self._roll_abilities)
        lay.addWidget(self._roll_btn)

        self._ability_grid = QGridLayout()
        self._ability_grid.setSpacing(8)
        self._ability_spins: Dict[str, QSpinBox] = {}

        for i, ability in enumerate(D20_ABILITIES):
            lbl = QLabel(ability.title())
            lbl.setMinimumWidth(100)
            spin = QSpinBox()
            spin.setRange(3, 20)
            spin.setValue(10)
            self._ability_spins[ability] = spin
            self._ability_grid.addWidget(lbl, i, 0)
            self._ability_grid.addWidget(spin, i, 1)
            mod_lbl = QLabel("+0")
            mod_lbl.setObjectName("StatValue")
            mod_lbl.setFixedWidth(40)
            self._ability_grid.addWidget(mod_lbl, i, 2)
            spin.valueChanged.connect(lambda v, ml=mod_lbl: ml.setText(f"{(v-10)//2:+d}"))

        lay.addLayout(self._ability_grid)
        lay.addStretch()
        self._steps.addWidget(page)

    # ---- Step 5: Summary ----
    def _build_step5(self) -> None:
        page = QFrame()
        page.setObjectName("StepPanel")
        lay = QVBoxLayout(page)

        header = QLabel("Karakter Özeti")
        header.setObjectName("SectionHeader")
        lay.addWidget(header)

        self._summary_text = QTextEdit()
        self._summary_text.setReadOnly(True)
        lay.addWidget(self._summary_text, stretch=1)

        save_btn = QPushButton("Karakteri Kaydet")
        save_btn.setObjectName("SuccessButton")
        save_btn.setMinimumHeight(40)
        save_btn.clicked.connect(self._save_character)
        lay.addWidget(save_btn)

        self._steps.addWidget(page)

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _update_nav(self) -> None:
        idx = self._steps.currentIndex()
        total = self._steps.count()
        self._back_btn.setEnabled(idx > 0)
        self._next_btn.setEnabled(idx < total - 1)
        self._next_btn.setText("Önizleme" if idx == total - 2 else "İleri")
        self._step_label.setText(f"Adım {idx + 1} / {total}")

    def _go_back(self) -> None:
        self._steps.setCurrentIndex(max(0, self._steps.currentIndex() - 1))
        self._update_nav()

    def _go_next(self) -> None:
        idx = self._steps.currentIndex()
        if idx == 0:
            self._on_system_selected()
        elif idx == 3:
            self._generate_summary()
        self._steps.setCurrentIndex(min(self._steps.count() - 1, idx + 1))
        self._update_nav()

    # ------------------------------------------------------------------
    # Logic (backend'e delege)
    # ------------------------------------------------------------------

    def _on_system_selected(self) -> None:
        """Seçilen sisteme göre race/class combobox'larını doldur."""
        sys_key = self._sys_combo.currentData()
        try:
            self._creator = CreatorFactory.create(sys_key)
        except ValueError:
            return

        self._race_combo.clear()
        self._class_combo.clear()

        if sys_key in ("dnd5e", "pathfinder1e"):
            self._race_title.setText("Irk Seçimi")
            self._class_title.setText("Sınıf Seçimi")
            for r in self._creator.list_available_races():
                self._race_combo.addItem(r, r)
            for c in self._creator.list_available_classes():
                self._class_combo.addItem(c, c)
            self._populate_spell_list()
            self._spell_group.show()
            self._roll_btn.show()
            for spin in self._ability_spins.values():
                spin.setRange(3, 20)

        elif sys_key == "mm3e":
            self._spell_group.hide()
            self._race_title.setText("Arketip Seçimi")
            self._class_title.setText("Origin (opsiyonel)")
            archetypes = self._creator.data.get("archetypes", {})
            for arch in sorted(archetypes.keys()):
                self._race_combo.addItem(arch, arch)
            self._class_combo.addItem("—", "")
            self._roll_btn.hide()
            for spin in self._ability_spins.values():
                spin.setRange(0, 20)
                spin.setValue(2)

    def _populate_spell_list(self) -> None:
        """SQLite/JSON'dan büyü listesini doldur."""
        self._spell_list.clear()
        self._all_spell_names = []
        if not self._creator:
            return
        spells = self._creator.data.get("spells", {})
        self._all_spell_names = sorted(spells.keys())
        for name in self._all_spell_names[:500]:
            self._spell_list.addItem(QListWidgetItem(name))

    def _filter_spells(self, text: str) -> None:
        query = text.strip().lower()
        self._spell_list.clear()
        for name in self._all_spell_names:
            if not query or query in name.lower():
                self._spell_list.addItem(QListWidgetItem(name))

    def _selected_spells(self) -> list[str]:
        return [item.text() for item in self._spell_list.selectedItems()]

    def _roll_abilities(self) -> None:
        """4d6 drop lowest ile yetenek puanlarını at."""
        for spin in self._ability_spins.values():
            score = BaseCharacterCreator.roll_4d6_drop_lowest()
            spin.setValue(score)

    def _generate_summary(self) -> None:
        """Karakter özetini oluştur."""
        char = self._build_character_dict()
        if not self._creator:
            return

        stats = self._creator.calculate_stats(char)
        char.update(stats)
        errors = self._creator.validate_character(char)

        lines = [
            f"Sistem: {self._creator.get_system_name()}",
            f"İsim: {char.get('name', '?')}",
            f"Irk/Clan: {char.get('race', char.get('clan', '?'))}",
            f"Sınıf: {char.get('class', char.get('archetype', '—'))}",
            "",
            "═══ Yetenek Puanları ═══",
        ]
        for k, v in char.get("abilities", {}).items():
            mod = (v - 10) // 2 if isinstance(v, int) else 0
            lines.append(f"  {k.title():15s} {v:3d}  ({mod:+d})")

        spells = char.get("spells", [])
        if spells:
            lines.append("")
            lines.append(f"═══ Büyüler ({len(spells)}) ═══")
            for sp in spells[:20]:
                lines.append(f"  • {sp}")
            if len(spells) > 20:
                lines.append(f"  ... ve {len(spells) - 20} tane daha")

        if stats:
            lines.append("")
            lines.append("═══ Türetilmiş İstatistikler ═══")
            for k in ("hit_points", "armor_class", "initiative", "proficiency_bonus"):
                if k in stats:
                    lines.append(f"  {k:25s} {stats[k]}")

        if errors:
            lines.append("")
            lines.append("═══ Doğrulama Uyarıları ═══")
            for e in errors:
                lines.append(f"  ⚠ {e}")

        self._summary_text.setPlainText("\n".join(lines))

    def _build_character_dict(self) -> Dict[str, Any]:
        """Mevcut form verilerinden karakter dict'i oluştur."""
        sys_key = self._sys_combo.currentData()
        name = self._name_edit.text().strip() or "İsimsiz Kahraman"
        abilities = {k: spin.value() for k, spin in self._ability_spins.items()}

        if sys_key in ("dnd5e", "pathfinder1e"):
            char: Dict[str, Any] = {
                "system": sys_key.upper(),
                "name": name,
                "race": self._race_combo.currentData() or "",
                "class": self._class_combo.currentData() or "",
                "level": 1,
                "abilities": abilities,
                "modifiers": {k: (v - 10) // 2 for k, v in abilities.items()},
                "spells": self._selected_spells(),
            }
            if sys_key == "pathfinder1e":
                char["bab"] = 1
                char["saves"] = {"fortitude": 2, "reflex": 0, "will": 0}
        elif sys_key == "mm3e":
            char = {
                "system": "MM3E",
                "name": name,
                "power_level": "PL10",
                "pl_value": 10,
                "total_power_points": 150,
                "remaining_power_points": 150,
                "abilities": abilities,
                "archetype": self._race_combo.currentData() or "",
                "powers": {},
                "defenses": {},
            }
        else:
            char = {"system": sys_key.upper(), "name": name, "level": 1, "abilities": abilities}

        return char

    def _save_character(self) -> None:
        """Karakteri SQLite'a kaydet (backend üzerinden)."""
        char = self._build_character_dict()
        if not self._creator:
            return

        stats = self._creator.calculate_stats(char)
        char.update(stats)

        sys_key = self._sys_combo.currentData() or ""
        soft = validate_character_soft(char, sys_key, self._creator.data)
        if soft.has_warnings:
            reply = QMessageBox.question(
                self,
                "Uyarı — Kural Dışı Seçim",
                format_warning_message(soft.warnings),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                char = mark_homebrew(char, soft.warnings)
            elif reply == QMessageBox.No:
                return

        record = CharacterRecord(
            id=None,
            system=char.get("system", "UNKNOWN"),
            name=char.get("name", "İsimsiz"),
            data=char,
        )
        try:
            new_id = save_character(self._db_path, record)
            QMessageBox.information(self, "Başarılı", f"'{record.name}' kaydedildi! (ID: {new_id})")
            self.character_created.emit(new_id)
            self.reset()
        except Exception as exc:
            logger.exception("Karakter kayıt hatası")
            QMessageBox.critical(self, "Hata", str(exc))

    def reset(self) -> None:
        """Formu sıfırla."""
        self._name_edit.clear()
        for spin in self._ability_spins.values():
            spin.setValue(10)
        self._summary_text.clear()
        self._steps.setCurrentIndex(0)
        self._update_nav()
