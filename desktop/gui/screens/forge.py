"""
The Forge (Creation Wizard) - Scrollable Single Page
===================================================
A scrollable, real-time character creation page.
All 6 blocks are laid out vertically inside a QScrollArea.
Calculations and database entities are managed dynamically in real-time.
"""

from __future__ import annotations

import logging
from pathlib import Path
from typing import Any, Dict, List, Optional

import random
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QLineEdit, QComboBox, QSpinBox, QFrame, QGridLayout, 
    QTextEdit, QMessageBox, QGroupBox, QListWidget, QTableWidget, 
    QTableWidgetItem, QHeaderView, QScrollArea, QFormLayout,
    QFileDialog
)

def get_dnd5e_point_cost(score: int) -> int:
    costs = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}
    return costs.get(score, 0)

def get_pf1e_point_cost(score: int) -> int:
    costs = {
        7: -4, 8: -2, 9: -1, 10: 0, 11: 1, 12: 2, 13: 3, 
        14: 5, 15: 7, 16: 10, 17: 13, 18: 17
    }
    return costs.get(score, 0)

def get_mm3e_point_cost(score: int) -> int:
    return score * 2

def roll_4d6_drop_lowest() -> int:
    rolls = [random.randint(1, 6) for _ in range(4)]
    rolls.sort()
    return sum(rolls[1:])


from rules.character_manager import CharacterManager
from utils.storage import CharacterRecord, save_character
from utils.soft_validation import validate_character_soft, mark_homebrew, format_warning_message

logger = logging.getLogger(__name__)

SYSTEM_MAP = {
    "dnd5e": "D&D 5th Edition",
    "pathfinder1e": "Pathfinder 1st Edition",
    "mm3e": "Mutants & Masterminds 3e",
}

D20_ABILITIES = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
MM3E_ABILITIES = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]


class ForgePage(QWidget):
    """Scrollable character forge creation screen."""

    character_created = Signal(int)

    def __init__(self, db_path: Path, parent: Optional[QWidget] = None):
        super().__init__(parent)
        self._db_path = db_path
        self.manager = CharacterManager(db_path)
        self._prev_ability_values: Dict[str, int] = {}
        self._build_ui()
        self.reset()

    def _build_ui(self) -> None:
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)

        # Header Title
        title_lbl = QLabel("  The Forge — Character Creator")
        title_lbl.setObjectName("PageTitle")
        title_lbl.setStyleSheet("font-size: 24px; font-weight: bold; padding: 12px; color: #d4c5a9;")
        main_layout.addWidget(title_lbl)

        # Scroll Area Setup
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.NoFrame)
        main_layout.addWidget(scroll)

        # Container Widget inside Scroll
        container = QWidget()
        container.setObjectName("ForgeContainer")
        self.container_layout = QVBoxLayout(container)
        self.container_layout.setSpacing(20)
        self.container_layout.setContentsMargins(24, 16, 24, 24)
        scroll.setWidget(container)

        # Build blocks
        self._build_block1_identity()
        self._build_block1b_flavor_portrait()
        self._build_block2_race_class()
        self._build_block3_abilities_stats()
        self._build_block4_skills()
        self._build_block5_feats_powers()
        self._build_block6_inventory()
        self._build_block7_spellbook()   # ADIM 3: Büyü Kitabı

        # Save Button at the bottom
        self._save_btn = QPushButton("Karakteri Kaydet")
        self._save_btn.setObjectName("SuccessButton")
        self._save_btn.setMinimumHeight(45)
        self._save_btn.clicked.connect(self._save_character)
        self.container_layout.addWidget(self._save_btn)

        # Sub-blocks to hide/show for progressive disclosure
        # NOT: _block7_group burada YOK — sadece büyücü sınıflarda gösterilir
        self._sub_blocks = [
            self._block1b_details_group,
            self._block2_group,
            self._block3_group,
            self._block4_group,
            self._block5_group,
            self._block6_group,
            self._save_btn
        ]

    # ------------------------------------------------------------------
    # BLOCK 1: System & Identity
    # ------------------------------------------------------------------
    def _build_block1_identity(self) -> None:
        group = QGroupBox("Blok 1: Sistem ve Kimlik")
        lay = QFormLayout(group)
        lay.setSpacing(10)

        self._name_edit = QLineEdit()
        self._name_edit.setPlaceholderText("Karakterinizin adını yazın...")
        self._name_edit.textChanged.connect(self._on_identity_changed)
        lay.addRow("Karakter Adı:", self._name_edit)

        self._sys_combo = QComboBox()
        self._sys_combo.addItem("— Sistem Seçiniz —", "")
        for key, val in SYSTEM_MAP.items():
            self._sys_combo.addItem(val, key)
        self._sys_combo.currentIndexChanged.connect(self._on_system_changed)
        lay.addRow("TTRPG Sistemi:", self._sys_combo)

        self.container_layout.addWidget(group)

    # ------------------------------------------------------------------
    # BLOCK 1B: Flavor & Portrait Details
    # ------------------------------------------------------------------
    def _build_block1b_flavor_portrait(self) -> None:
        self._block1b_details_group = QGroupBox("Blok 1B: Karakter Detayları & Portre")
        layout = QHBoxLayout(self._block1b_details_group)
        layout.setSpacing(15)

        # Left Side: Portrait Area
        port_lay = QVBoxLayout()
        port_lay.setSpacing(5)
        self._portrait_lbl = QLabel("Görsel Yok")
        self._portrait_lbl.setFixedSize(120, 150)
        self._portrait_lbl.setAlignment(Qt.AlignCenter)
        self._portrait_lbl.setStyleSheet(
            "border: 2px dashed #d4c5a9; border-radius: 4px; background-color: #1a1a1a; color: #888;"
        )
        port_lay.addWidget(self._portrait_lbl)

        self._select_portrait_btn = QPushButton("Portre Seç")
        self._select_portrait_btn.clicked.connect(self._on_select_portrait_clicked)
        port_lay.addWidget(self._select_portrait_btn)
        layout.addLayout(port_lay)

        # Right Side: Details Form
        form_lay = QFormLayout()
        form_lay.setSpacing(8)

        self._alignment_edit = QLineEdit()
        self._alignment_edit.setPlaceholderText("Örn: Lawful Good")
        self._alignment_edit.textChanged.connect(self._on_details_changed)
        form_lay.addRow("Yönelim (Alignment):", self._alignment_edit)

        self._deity_edit = QLineEdit()
        self._deity_edit.setPlaceholderText("Örn: Lathander")
        self._deity_edit.textChanged.connect(self._on_details_changed)
        form_lay.addRow("Tanrı (Deity):", self._deity_edit)

        self._age_edit = QLineEdit()
        self._age_edit.setPlaceholderText("Örn: 25")
        self._age_edit.textChanged.connect(self._on_details_changed)
        form_lay.addRow("Yaş (Age):", self._age_edit)

        self._bg_edit = QTextEdit()
        self._bg_edit.setPlaceholderText("Karakterinizin özgeçmişi ve arka plan hikayesi...")
        self._bg_edit.setMaximumHeight(60)
        self._bg_edit.textChanged.connect(self._on_details_changed)
        form_lay.addRow("Arka Plan (Background):", self._bg_edit)

        layout.addLayout(form_lay, stretch=1)
        self.container_layout.addWidget(self._block1b_details_group)

    # ------------------------------------------------------------------
    # BLOCK 2: Race & Class
    # ------------------------------------------------------------------
    def _build_block2_race_class(self) -> None:
        self._block2_group = QGroupBox("Blok 2: Irk & Sınıf Seçimi")
        lay = QFormLayout(self._block2_group)
        lay.setSpacing(10)

        # Parent Race dropdown
        self._race_combo = QComboBox()
        self._race_combo.currentIndexChanged.connect(self._on_race_selected)
        lay.addRow("Irk / Arketip:", self._race_combo)

        # Subrace dropdown (hidden until a race with subraces is selected)
        self._subrace_label = QLabel("Alt Irk (Subrace):")
        self._subrace_combo = QComboBox()
        self._subrace_combo.currentIndexChanged.connect(self._on_subrace_selected)
        lay.addRow(self._subrace_label, self._subrace_combo)
        self._subrace_label.hide()
        self._subrace_combo.hide()

        # Class dropdown
        self._class_combo = QComboBox()
        self._class_combo.currentIndexChanged.connect(self._on_class_selected)
        lay.addRow("Sınıf / Origin:", self._class_combo)

        # Description info panel
        self._desc_box = QTextEdit()
        self._desc_box.setReadOnly(True)
        self._desc_box.setPlaceholderText("Seçilen ırk veya sınıfın açıklaması burada gösterilecektir...")
        self._desc_box.setMaximumHeight(120)
        lay.addRow("Bilgi Paneli:", self._desc_box)

        self.container_layout.addWidget(self._block2_group)

    # ------------------------------------------------------------------
    # BLOCK 3: Abilities & Derived Stats
    # ------------------------------------------------------------------
    def _build_block3_abilities_stats(self) -> None:
        self._block3_group = QGroupBox("Blok 3: Yetenek Puanları ve Canlı İstatistikler")
        grid = QGridLayout(self._block3_group)
        grid.setSpacing(10)

        # Left Column: Stat Entry Spinboxes
        self._abilities_group = QGroupBox("Yetenek Puanları (Basic Stats)")
        ab_group_layout = QVBoxLayout(self._abilities_group)

        # Method Selection Layout (Top part of abilities group)
        method_layout = QFormLayout()
        method_layout.setSpacing(8)

        self._stat_method_combo = QComboBox()
        self._stat_method_combo.addItem("Manuel Giriş", "manual")
        self._stat_method_combo.addItem("4d6 Drop Lowest (Zar At)", "roll_4d6")
        self._stat_method_combo.addItem("Point Buy (Puan Satın Alma)", "point_buy")
        self._stat_method_combo.currentIndexChanged.connect(self._on_stat_method_changed)
        method_layout.addRow("Belirleme Yöntemi:", self._stat_method_combo)

        self._roll_stats_btn = QPushButton("Zarları At")
        self._roll_stats_btn.clicked.connect(self._on_roll_stats_clicked)
        self._roll_stats_btn.hide()
        method_layout.addRow("", self._roll_stats_btn)

        self._point_buy_label = QLabel("Kalan Puan: —")
        self._point_buy_label.setObjectName("PointBuyLabel")
        self._point_buy_label.hide()
        method_layout.addRow("", self._point_buy_label)

        ab_group_layout.addLayout(method_layout)

        # Abilities Spinboxes Form Layout (Bottom part of abilities group)
        self._ab_layout = QFormLayout()
        self._ab_layout.setSpacing(8)
        self._ability_spins: Dict[str, QSpinBox] = {}
        ab_group_layout.addLayout(self._ab_layout)

        grid.addWidget(self._abilities_group, 0, 0)

        # Right Column: Derived Live Indicators
        self._derived_group = QGroupBox("Derived Statistics (Canlı Hesaplama)")
        self._derived_layout = QFormLayout(self._derived_group)
        
        self._ac_lbl = QLabel("—")
        self._ac_lbl.setObjectName("StatValue")
        self._derived_layout.addRow("Zırh Sınıfı (AC):", self._ac_lbl)

        self._hp_lbl = QLabel("—")
        self._hp_lbl.setObjectName("StatValue")
        self._derived_layout.addRow("Can Puanı (HP):", self._hp_lbl)

        self._init_lbl = QLabel("—")
        self._init_lbl.setObjectName("StatValue")
        self._derived_layout.addRow("İnisiyatif (Initiative):", self._init_lbl)

        self._prof_lbl = QLabel("—")
        self._prof_lbl.setObjectName("StatValue")
        self._derived_layout.addRow("Bonus (BAB / Prof):", self._prof_lbl)

        grid.addWidget(self._derived_group, 0, 1)
        self.container_layout.addWidget(self._block3_group)

    # ------------------------------------------------------------------
    # BLOCK 4: Skills
    # ------------------------------------------------------------------
    def _build_block4_skills(self) -> None:
        self._block4_group = QGroupBox("Blok 4: Beceriler (Skills)")
        lay = QVBoxLayout(self._block4_group)

        self._skills_table = QTableWidget()
        self._skills_table.setColumnCount(2)
        self._skills_table.setHorizontalHeaderLabels(["Beceri Adı", "Bonus"])
        self._skills_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._skills_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._skills_table.setMinimumHeight(200)
        self._skills_table.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._skills_table)

        self.container_layout.addWidget(self._block4_group)

    # ------------------------------------------------------------------
    # BLOCK 5: Features & Feats
    # ------------------------------------------------------------------
    def _build_block5_feats_powers(self) -> None:
        # ── Block 5A: Feats / Powers ──────────────────────────────────────
        self._block5a_group = QGroupBox("Blok 5A: Yetenek Seçimi (Feats / Powers)")
        lay5a = QFormLayout(self._block5a_group)
        lay5a.setSpacing(10)

        self._feat_combo = QComboBox()
        self._feat_combo.currentIndexChanged.connect(self._on_feat_selected)
        lay5a.addRow("Seçilebilir Yetenek (Feat):", self._feat_combo)

        # Fighting Style option for DND5e Fighter
        self._style_lbl = QLabel("Dövüş Stili:")
        self._style_combo = QComboBox()
        self._style_combo.addItems(["Defense (+1 AC)", "Archery (+2 to hit)", "Great Weapon Fighting"])
        self._style_combo.currentIndexChanged.connect(self._on_style_selected)
        lay5a.addRow(self._style_lbl, self._style_combo)
        self._style_lbl.hide()
        self._style_combo.hide()

        self.container_layout.addWidget(self._block5a_group)

        # ── Block 5B: Traits (PF1e only) ──────────────────────────────────
        self._block5b_group = QGroupBox("Blok 5B: Karakter Özelliği Seçimi (Traits — PF1e)")
        lay5b = QFormLayout(self._block5b_group)
        lay5b.setSpacing(10)

        self._trait_combo = QComboBox()
        self._trait_combo.currentIndexChanged.connect(self._on_trait_selected)
        lay5b.addRow("Karakter Özelliği (Trait):", self._trait_combo)

        self._trait_desc_box = QTextEdit()
        self._trait_desc_box.setReadOnly(True)
        self._trait_desc_box.setPlaceholderText("Seçilen özelliğin açıklaması...")
        self._trait_desc_box.setMaximumHeight(80)
        lay5b.addRow("Trait Bilgisi:", self._trait_desc_box)

        self.container_layout.addWidget(self._block5b_group)
        self._block5b_group.hide()   # hidden until PF1e is selected

        # Keep backward-compat alias for reset logic
        self._block5_group = self._block5a_group

    # ------------------------------------------------------------------
    # BLOCK 6: Inventory & Equipment
    # ------------------------------------------------------------------
    def _build_block6_inventory(self) -> None:
        self._block6_group = QGroupBox("Blok 6: Envanter & Ekipman")
        lay = QVBoxLayout(self._block6_group)

        search_lay = QHBoxLayout()
        self._inv_search = QLineEdit()
        self._inv_search.setPlaceholderText("Ekipman ara...")
        self._inv_search.textChanged.connect(self._on_item_search_changed)
        self._add_item_btn = QPushButton("Karaktere Ekle")
        self._add_item_btn.clicked.connect(self._on_add_item_clicked)
        search_lay.addWidget(self._inv_search)
        search_lay.addWidget(self._add_item_btn)
        lay.addLayout(search_lay)

        self._search_results_combo = QComboBox()
        lay.addWidget(self._search_results_combo)

        lay.addWidget(QLabel("Mevcut Envanter:"))
        self._inventory_table = QTableWidget()
        self._inventory_table.setColumnCount(2)
        self._inventory_table.setHorizontalHeaderLabels(["Eşya Adı", "Kategori"])
        self._inventory_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._inventory_table.setMinimumHeight(150)
        self._inventory_table.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._inventory_table)

        self.container_layout.addWidget(self._block6_group)

    # ------------------------------------------------------------------
    # BLOCK 7: Büyü Kitabı (Spellbook) — sadece büyücü sınıflarda görünür
    # ------------------------------------------------------------------
    def _build_block7_spellbook(self) -> None:
        self._block7_group = QGroupBox("Blok 7: Büyü Kitabı (Spellcasting)")
        lay = QVBoxLayout(self._block7_group)
        lay.setSpacing(10)

        # Üst satır: Büyü istatistikleri (DC, Attack Bonus, CL/Concentration)
        stats_frame = QFrame()
        stats_frame.setFrameShape(QFrame.StyledPanel)
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setSpacing(20)

        def _make_stat_pair(label_text: str) -> tuple:
            col = QVBoxLayout()
            lbl = QLabel(label_text)
            lbl.setAlignment(Qt.AlignCenter)
            lbl.setStyleSheet("color: #888; font-size: 10px;")
            val = QLabel("—")
            val.setObjectName("StatValue")
            val.setAlignment(Qt.AlignCenter)
            val.setStyleSheet("font-size: 18px; font-weight: bold; color: #c09b5a;")
            col.addWidget(lbl)
            col.addWidget(val)
            stats_layout.addLayout(col)
            return val

        self._spell_dc_lbl        = _make_stat_pair("Büyü Zorluğu (DC)")
        self._spell_atk_lbl       = _make_stat_pair("Büyü Atk Bonus")
        self._spell_cl_lbl        = _make_stat_pair("Büyücü Seviyesi (CL)")
        self._spell_conc_lbl      = _make_stat_pair("Konsantrasyon")
        self._spell_ability_lbl   = _make_stat_pair("Büyü Yeteneği")
        lay.addWidget(stats_frame)

        # Slot tablosu
        lay.addWidget(QLabel("Büyü Slotları:"))
        self._spell_slots_table = QTableWidget()
        self._spell_slots_table.setColumnCount(2)
        self._spell_slots_table.setHorizontalHeaderLabels(["Büyü Seviyesi", "Slot Sayısı"])
        self._spell_slots_table.horizontalHeader().setSectionResizeMode(0, QHeaderView.Stretch)
        self._spell_slots_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeToContents)
        self._spell_slots_table.setMaximumHeight(220)
        self._spell_slots_table.setEditTriggers(QTableWidget.NoEditTriggers)
        lay.addWidget(self._spell_slots_table)

        # Bonus slot bilgisi (PF1e)
        self._bonus_slots_lbl = QLabel("")
        self._bonus_slots_lbl.setWordWrap(True)
        self._bonus_slots_lbl.setStyleSheet("color: #a9c4ff; font-size: 11px;")
        self._bonus_slots_lbl.hide()
        lay.addWidget(self._bonus_slots_lbl)

        # Büyü listesi
        lay.addWidget(QLabel("Sınıf Büyü Listesi (ilk 30):"))
        self._spell_list_widget = QListWidget()
        self._spell_list_widget.setMaximumHeight(180)
        self._spell_list_widget.setToolTip("Büyüye tıklayarak açıklamasını görebilirsiniz.")
        self._spell_list_widget.currentTextChanged.connect(self._on_spell_selected)
        lay.addWidget(self._spell_list_widget)

        # Büyü açıklama kutusu
        self._spell_desc_box = QTextEdit()
        self._spell_desc_box.setReadOnly(True)
        self._spell_desc_box.setPlaceholderText("Bir büyüye tıklayarak açıklamasını görüntüleyin...")
        self._spell_desc_box.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        lay.addWidget(self._spell_desc_box)

        # 1. UI Eklemesi (Büyü Öğrenme Bloğu)
        self._add_spell_btn = QPushButton("Seçili Büyüyü Öğren")
        self._add_spell_btn.clicked.connect(self.add_spell_to_book)
        lay.addWidget(self._add_spell_btn)

        lay.addWidget(QLabel("Öğrenilen Büyüler:"))
        self._learned_spells_list = QListWidget()
        self._learned_spells_list.setMaximumHeight(100)
        lay.addWidget(self._learned_spells_list)

        self.container_layout.addWidget(self._block7_group)
        self._block7_group.hide()   # Başlangıçta gizli — büyücü sınıf seçilince açılır
        self._spell_data_cache: list = []  # Açıklama araması için önbellek

    # ------------------------------------------------------------------
    # Signal Listeners & Database Triggers
    # ------------------------------------------------------------------

    def _on_identity_changed(self) -> None:
        self.manager.active_character["name"] = self._name_edit.text().strip()

    def _on_system_changed(self) -> None:
        sys_key = self._sys_combo.currentData()
        
        # Progressive disclosure toggle
        if not sys_key:
            for block in self._sub_blocks:
                block.hide()
            return
        
        for block in self._sub_blocks:
            block.show()

        self.manager.active_character = {
            "system": sys_key.upper(),
            "name": self._name_edit.text().strip(),
            "level": 1,
            "abilities": {},
            "equipment": [],
            "feats": [],
            "alignment": self._alignment_edit.text().strip(),
            "deity": self._deity_edit.text().strip(),
            "age": self._age_edit.text().strip(),
            "background": self._bg_edit.toPlainText().strip()
        }

        # Clear and build ability spinboxes dynamically based on system rules
        for i in reversed(range(self._ab_layout.count())):
            item = self._ab_layout.itemAt(i)
            if item and item.widget():
                item.widget().setParent(None)
        self._ability_spins.clear()
        self._prev_ability_values.clear()

        abilities_list = MM3E_ABILITIES if sys_key == "mm3e" else D20_ABILITIES
        for ab in abilities_list:
            spin = QSpinBox()
            spin.valueChanged.connect(self._on_ability_changed)
            self._ability_spins[ab] = spin
            self._ab_layout.addRow(f"{ab}:", spin)

        # Update ability ranges/defaults based on method & system
        self._update_ability_ranges()

        # Query and populate races/classes comboboxes
        # For races: only show top-level (parent) races; subraces appear dynamically.
        # MnM3e: race/subrace is not applicable, disable those combos.
        if sys_key == "mm3e":
            self._race_combo.clear()
            self._race_combo.addItem("— Irk yok (MnM3e) —", None)
            self._race_combo.setEnabled(False)
            self._subrace_label.hide()
            self._subrace_combo.hide()
        else:
            self._race_combo.setEnabled(True)
            races = self.manager.get_top_level_races(sys_key)
            if not races and sys_key == "pathfinder1e":
                from models.entity import DiyargezenEntity
                fallback_race_names = [
                    "Human", "Elf", "Dwarf", "Gnome", "Halfling", "Half-Elf", "Half-Orc",
                    "Aasimar", "Tiefling", "Ifrit", "Oread", "Sylph", "Undine", "Catfolk",
                    "Tengu", "Ratfolk", "Fetchling", "Dhampir", "Drow", "Goblin", "Hobgoblin",
                    "Kobold", "Orc", "Kitsune", "Changeling", "Wayang", "Nagaji", "Samsaran",
                    "Vishkanya", "Grippli", "Merfolk", "Strix", "Svirfneblin", "Vanara"
                ]
                races = [
                    DiyargezenEntity(
                        isim=r_name,
                        sistem="pathfinder1e",
                        kategori="race",
                        aciklama=f"{r_name} (PF1e Brute-Force Fallback)",
                        sistem_verisi={"synthesised": True}
                    )
                    for r_name in fallback_race_names
                ]
            self._race_combo.clear()
            self._race_combo.addItem("— Irk Seçiniz —", None)
            for r in races:
                self._race_combo.addItem(r.isim, r)

        # ── Classes (filtered — no NPC/creature types) ───────────────────
        classes = self.manager.get_clean_classes(sys_key)
        self._class_combo.clear()
        self._class_combo.addItem("— Sınıf Seçiniz —", None)
        for c in classes:
            self._class_combo.addItem(c.isim, c)

        # ── Feats ────────────────────────────────────────────────────────
        feats = self.manager.get_entities_by_category(sys_key, "feat")
        self._feat_combo.clear()
        self._feat_combo.addItem("— Yetenek Seçiniz —", None)
        for f in feats:
            self._feat_combo.addItem(f.isim, f)

        # ── Traits (PF1e only) ───────────────────────────────────────────
        if sys_key == "pathfinder1e":
            traits = self.manager.get_traits(sys_key)
            if not traits:
                from models.entity import DiyargezenEntity
                fallback_trait_names = [
                    "Reactionary (Combat)", "Armor Expert (Combat)", "Courageous (Combat)",
                    "Magical Knack (Magic)", "Focused Mind (Magic)", "Student of Philosophy (Social)",
                    "Fast-Talker (Social)", "Fate's Favored (Faith)", "Birthmark (Faith)",
                    "Deft Dodger (Combat)", "Resilient (Combat)"
                ]
                traits = [
                    DiyargezenEntity(
                        isim=t_name,
                        sistem="pathfinder1e",
                        kategori="trait",
                        aciklama=f"{t_name} (PF1e Brute-Force Fallback)",
                        sistem_verisi={}
                    )
                    for t_name in fallback_trait_names
                ]
            self._trait_combo.clear()
            self._trait_combo.addItem("— Trait Seçiniz —", None)
            for t in traits:
                self._trait_combo.addItem(t.isim, t)
            self._block5b_group.show()
            self._block5b_group.setEnabled(True)
        else:
            self._trait_combo.clear()
            self._block5b_group.hide()

        # Trigger search refresh
        self._on_item_search_changed()
        
        # Reset method selection to manual on system change
        self._stat_method_combo.setCurrentIndex(0)
        self._on_stat_method_changed()

    def _on_select_portrait_clicked(self) -> None:
        if not hasattr(self, "manager") or not self.manager.active_character:
            return
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Portre Görseli Seç", "", "Resim Dosyaları (*.png *.jpg *.jpeg)"
        )
        if file_path:
            self.manager.active_character["portrait_path"] = file_path
            pixmap = QPixmap(file_path)
            if not pixmap.isNull():
                self._portrait_lbl.setPixmap(pixmap.scaled(
                    self._portrait_lbl.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation
                ))
            else:
                self._portrait_lbl.setText("Görsel Yüklenemedi")

    def _on_details_changed(self) -> None:
        if not hasattr(self, "manager") or not self.manager.active_character:
            return
        char = self.manager.active_character
        char["alignment"] = self._alignment_edit.text().strip()
        char["deity"] = self._deity_edit.text().strip()
        char["age"] = self._age_edit.text().strip()
        char["background"] = self._bg_edit.toPlainText().strip()

    def _on_stat_method_changed(self) -> None:
        sys_key = self._sys_combo.currentData()
        method = self._stat_method_combo.currentData()
        
        # Toggle visibility of helpers
        if method == "roll_4d6":
            self._roll_stats_btn.show()
            self._point_buy_label.hide()
        elif method == "point_buy":
            self._roll_stats_btn.hide()
            self._point_buy_label.show()
            # Set to initial values when switching to point buy
            if sys_key == "dnd5e":
                for spin in self._ability_spins.values():
                    spin.setValue(8)
            elif sys_key == "pathfinder1e":
                for spin in self._ability_spins.values():
                    spin.setValue(10)
            elif sys_key == "mm3e":
                for spin in self._ability_spins.values():
                    spin.setValue(0)
        else:
            self._roll_stats_btn.hide()
            self._point_buy_label.hide()
            
        self._update_ability_ranges()
        self._on_ability_changed()

    def _update_ability_ranges(self) -> None:
        sys_key = self._sys_combo.currentData()
        method = self._stat_method_combo.currentData()
        if not sys_key:
            return
            
        for ab, spin in self._ability_spins.items():
            spin.blockSignals(True)
            if sys_key == "mm3e":
                spin.setRange(0, 20)
            else:
                if method == "point_buy":
                    if sys_key == "dnd5e":
                        spin.setRange(8, 15)
                        if spin.value() < 8 or spin.value() > 15:
                            spin.setValue(8)
                    else:  # pathfinder1e
                        spin.setRange(7, 18)
                        if spin.value() < 7 or spin.value() > 18:
                            spin.setValue(10)
                else:
                    spin.setRange(3, 20)
            spin.blockSignals(False)

    def _on_roll_stats_clicked(self) -> None:
        sys_key = self._sys_combo.currentData()
        if not sys_key:
            return
            
        for spin in self._ability_spins.values():
            spin.blockSignals(True)
            
        if sys_key == "mm3e":
            for ab, spin in self._ability_spins.items():
                score = roll_4d6_drop_lowest()
                rank = max(0, (score - 10) // 2)
                spin.setValue(rank)
        else:
            for ab, spin in self._ability_spins.items():
                spin.setValue(roll_4d6_drop_lowest())
                
        for spin in self._ability_spins.values():
            spin.blockSignals(False)
            
        self._on_ability_changed()

    def _update_point_buy_budget(self) -> None:
        sys_key = self._sys_combo.currentData()
        method = self._stat_method_combo.currentData()
        if method != "point_buy" or not sys_key:
            self._point_buy_label.hide()
            return
            
        self._point_buy_label.show()
        budget = 27 if sys_key == "dnd5e" else (20 if sys_key == "pathfinder1e" else 150)
        cost_func = get_dnd5e_point_cost if sys_key == "dnd5e" else (get_pf1e_point_cost if sys_key == "pathfinder1e" else get_mm3e_point_cost)
        
        total_cost = 0
        for ab, spin in self._ability_spins.items():
            total_cost += cost_func(spin.value())
            
        remaining = budget - total_cost
        self._point_buy_label.setText(f"Kalan Puan: {remaining} / {budget}")
        if remaining < 0:
            self._point_buy_label.setStyleSheet("color: #ff6b6b; font-weight: bold;")
        else:
            self._point_buy_label.setStyleSheet("color: #a9ffb4; font-weight: bold;")

    def _on_race_selected(self) -> None:
        """Handles race selection: updates character state and populates subrace dropdown."""
        entity = self._race_combo.currentData()
        race_name = self._race_combo.currentText() if entity else ""
        self.manager.active_character["race"] = race_name
        self.manager.active_character["race_data"] = entity.sistem_verisi if entity and hasattr(entity, "sistem_verisi") else {}
        # Clear subrace when race changes
        self.manager.active_character["subrace"] = ""

        if entity and hasattr(entity, "aciklama"):
            self._desc_box.setHtml(entity.aciklama)
        else:
            self._desc_box.clear()

        # Populate subraces dynamically
        sys_key = self._sys_combo.currentData()
        if entity and sys_key and sys_key != "mm3e":
            subraces = self.manager.get_subraces_for_race(sys_key, race_name)
        else:
            subraces = []

        # Block signals while repopulating so we don't trigger _on_subrace_selected prematurely
        self._subrace_combo.blockSignals(True)
        self._subrace_combo.clear()
        if subraces:
            self._subrace_combo.addItem("— Alt Irk Seçiniz —", None)
            for sr in subraces:
                self._subrace_combo.addItem(sr.isim, sr)
            self._subrace_label.show()
            self._subrace_combo.show()
        else:
            self._subrace_label.hide()
            self._subrace_combo.hide()
        self._subrace_combo.blockSignals(False)

        self._recalculate_and_refresh()

    def _on_subrace_selected(self) -> None:
        """Handles subrace selection: updates character state."""
        entity = self._subrace_combo.currentData()
        if entity is None:
            self.manager.active_character["subrace"] = ""
            self.manager.active_character["subrace_data"] = {}
        else:
            self.manager.active_character["subrace"] = entity.isim
            self.manager.active_character["subrace_data"] = entity.sistem_verisi
            if hasattr(entity, "aciklama") and entity.aciklama:
                self._desc_box.setHtml(entity.aciklama)
        self._recalculate_and_refresh()

    def _on_class_selected(self) -> None:
        selected_class = self._class_combo.currentText()
        self.manager.active_character["class"] = selected_class
        
        # Add class data requirements
        entity = self._class_combo.currentData()
        if entity and hasattr(entity, "sistem_verisi"):
            class_data = entity.sistem_verisi
            self._desc_box.setHtml(entity.aciklama)
        else:
            class_data = {}
        self.manager.active_character["class_data"] = class_data
        
        # Show Fighting Style dropdown if D&D 5e Fighter is selected
        sys_key = self._sys_combo.currentData()
        if sys_key == "dnd5e" and selected_class == "Fighter":
            self._style_lbl.show()
            self._style_combo.show()
        else:
            self._style_lbl.hide()
            self._style_combo.hide()

        # ADIM 3: Büyücü sınıf tespiti — Progressive disclosure
        is_caster = bool(class_data.get("spellcasting_ability", ""))
        if is_caster:
            self._block7_group.show()
        else:
            self._block7_group.hide()
            self._spell_slots_table.setRowCount(0)
            self._spell_list_widget.clear()
            self._spell_desc_box.clear()
            self._bonus_slots_lbl.hide()

        self._recalculate_and_refresh()

    def _on_ability_changed(self) -> None:
        sys_key = self._sys_combo.currentData()
        method = self._stat_method_combo.currentData()
        
        if method == "point_buy" and sys_key:
            budget = 27 if sys_key == "dnd5e" else (20 if sys_key == "pathfinder1e" else 150)
            cost_func = get_dnd5e_point_cost if sys_key == "dnd5e" else (get_pf1e_point_cost if sys_key == "pathfinder1e" else get_mm3e_point_cost)
            
            total_cost = 0
            for ab, spin in self._ability_spins.items():
                total_cost += cost_func(spin.value())
                
            if total_cost > budget:
                # Find which spinbox exceeded budget
                for ab, spin in self._ability_spins.items():
                    prev = self._prev_ability_values.get(ab, spin.value())
                    if spin.value() != prev:
                        spin.blockSignals(True)
                        spin.setValue(prev)
                        spin.blockSignals(False)
                        break
                QMessageBox.warning(self, "Bütçe Sınırı", "Yetenek Puanı bütçesini aştınız!")
                
        # Update previous values dictionary
        for ab, spin in self._ability_spins.items():
            self._prev_ability_values[ab] = spin.value()
            
        # Update character stats
        abilities = {k: spin.value() for k, spin in self._ability_spins.items()}
        self.manager.active_character["abilities"] = abilities
        
        self._update_point_buy_budget()
        self._recalculate_and_refresh()

    def _on_feat_selected(self) -> None:
        entity = self._feat_combo.currentData()
        feat_name = self._feat_combo.currentText()
        if feat_name and feat_name != "— Yetenek Seçiniz —":
            current_feats = self.manager.active_character.get("feats", [])
            if feat_name not in current_feats:
                self.manager.active_character["feats"] = current_feats + [feat_name]
            if entity and hasattr(entity, "aciklama") and entity.aciklama:
                self._desc_box.setHtml(entity.aciklama)

    def _on_trait_selected(self) -> None:
        """Handles PF1e trait selection."""
        entity = self._trait_combo.currentData()
        if entity is None:
            self.manager.active_character["traits"] = []
            self._trait_desc_box.clear()
            return
        trait_name = self._trait_combo.currentText()
        if trait_name and trait_name != "— Trait Seçiniz —":
            self.manager.active_character["traits"] = [trait_name]
            if hasattr(entity, "aciklama") and entity.aciklama:
                self._trait_desc_box.setHtml(entity.aciklama)

    def _on_style_selected(self) -> None:
        style = self._style_combo.currentText()
        if "AC" in style:
            self.manager.active_character["armor_bonus"] = self.manager.active_character.get("armor_bonus", 0) + 1
            self._recalculate_and_refresh()

    def _on_item_search_changed(self) -> None:
        query = self._inv_search.text().strip()
        sys_key = self._sys_combo.currentData()
        # Use clean equipment query to filter template/index garbage
        items = self.manager.get_clean_equipment(sys_key or "", query)
        self._search_results_combo.clear()
        for item in items:
            self._search_results_combo.addItem(item.isim, item)

    def _on_add_item_clicked(self) -> None:
        item_entity = self._search_results_combo.currentData()
        if not item_entity:
            return
        
        # Recalculates internally
        self.manager.add_item_to_inventory(item_entity)
        self._refresh_inventory_ui()
        self._recalculate_and_refresh()

    def _recalculate_and_refresh(self) -> None:
        """Runs rule engine calculators and updates all GUI derived widgets."""
        char = self.manager.recalculate_character()
        
        # Update derived fields labels
        self._ac_lbl.setText(str(char.get("armor_class", "—")))
        self._hp_lbl.setText(str(char.get("hit_points", "—")))
        self._init_lbl.setText(f"{char.get('initiative', 0):+d}" if isinstance(char.get('initiative'), int) else str(char.get('initiative', '—')))
        
        sys_key = self._sys_combo.currentData()
        if sys_key == "mm3e":
            self._prof_lbl.setText(f"PL {char.get('pl_value', 10)}")
        elif sys_key == "pathfinder1e":
            self._prof_lbl.setText(f"BAB +{char.get('bab', 0)}")
        else:
            self._prof_lbl.setText(f"Prof +{char.get('proficiency_bonus', 2)}")

        # Update skills table widget
        skills = char.get("skills", {})
        self._skills_table.setRowCount(0)
        self._skills_table.setRowCount(len(skills))
        for row, (sk, bonus) in enumerate(sorted(skills.items())):
            # snake_case → Title Case (acrobatics → Acrobatics, sleight_of_hand → Sleight Of Hand)
            display_name = sk.replace("_", " ").title()
            self._skills_table.setItem(row, 0, QTableWidgetItem(display_name))
            self._skills_table.setItem(row, 1, QTableWidgetItem(f"{bonus:+d}" if isinstance(bonus, int) else str(bonus)))

        # ADIM 3: Büyü Kitabı UI güncellemesi (Graceful Fail — hata fırlatmaz)
        self._refresh_spellbook_ui(char, sys_key)

    def _refresh_inventory_ui(self) -> None:
        inventory = self.manager.active_character.get("equipment", [])
        self._inventory_table.setRowCount(0)
        self._inventory_table.setRowCount(len(inventory))
        for row, item in enumerate(inventory):
            name = item.get("name", "")
            itype = item.get("type", "")
            self._inventory_table.setItem(row, 0, QTableWidgetItem(name))
            self._inventory_table.setItem(row, 1, QTableWidgetItem(itype))

    def _refresh_spellbook_ui(self, char: Dict[str, Any], sys_key: Optional[str]) -> None:
        """Blok 7 UI'ını calculate_spells() sonucuyla günceller.
        Graceful Fail: herhangi bir hata sessizce yutulur, mevcut UI bozulmaz."""
        try:
            if self._block7_group.isHidden():
                return  # Büyücü değil — hiç dokunma

            from rules.calculators import DND5e_Calculator, PF1e_Calculator

            active_char = self.manager.active_character
            if sys_key == "pathfinder1e":
                spell_data = PF1e_Calculator(self._db_path).calculate_spells(active_char)
            else:
                spell_data = DND5e_Calculator(self._db_path).calculate_spells(active_char)

            if not spell_data.get("is_spellcaster"):
                return

            # -- İstatistik etiketleri --
            ability_str = spell_data.get("spellcasting_ability", "—")
            self._spell_ability_lbl.setText(ability_str)

            if sys_key == "pathfinder1e":
                self._spell_dc_lbl.setText(
                    f"{spell_data.get('spell_save_dc_base', 0)} + büyü seviyesi"
                )
                self._spell_atk_lbl.setText("—")  # PF1e'de saldırı rulları farklı
                self._spell_cl_lbl.setText(str(spell_data.get("caster_level", "—")))
                self._spell_conc_lbl.setText(
                    f"+{spell_data.get('concentration_bonus', 0)}"
                )
                # Bonus slot bilgisi
                bonus = spell_data.get("bonus_slots", {})
                if bonus:
                    bonus_text = "  |  ".join(
                        f"Seviye {k}: +{v} slot" for k, v in sorted(bonus.items())
                    )
                    self._bonus_slots_lbl.setText(
                        f"Yüksek {ability_str} bonusu: {bonus_text}"
                    )
                    self._bonus_slots_lbl.show()
                else:
                    self._bonus_slots_lbl.hide()
            else:
                self._spell_dc_lbl.setText(str(spell_data.get("spell_save_dc", "—")))
                atk = spell_data.get("spell_attack_bonus", 0)
                self._spell_atk_lbl.setText(f"+{atk}" if atk >= 0 else str(atk))
                self._spell_cl_lbl.setText(str(active_char.get("level", 1)))
                self._spell_conc_lbl.setText("—")  # 5e'de Concentration farklı
                self._bonus_slots_lbl.hide()

            # -- Slot tablosu --
            slots = spell_data.get("slots", {})
            self._spell_slots_table.setRowCount(0)

            if "pact_slots" in slots:  # Warlock: Pact Magic
                self._spell_slots_table.setRowCount(1)
                self._spell_slots_table.setItem(
                    0, 0,
                    QTableWidgetItem(
                        f"Pakt Slotu (Seviye {slots['pact_slot_level']})"
                    )
                )
                self._spell_slots_table.setItem(
                    0, 1, QTableWidgetItem(str(slots["pact_slots"]))
                )
            else:
                self._spell_slots_table.setRowCount(len(slots))
                for row, (lv, count) in enumerate(
                    sorted(slots.items(), key=lambda x: int(x[0]))
                ):
                    self._spell_slots_table.setItem(
                        row, 0, QTableWidgetItem(f"{lv}. Seviye")
                    )
                    self._spell_slots_table.setItem(
                        row, 1, QTableWidgetItem(str(count))
                    )

            # -- Büyü listesi --
            known = spell_data.get("known_spells", [])
            self._spell_data_cache = known
            self._spell_list_widget.clear()
            for sp in known:
                lv_tag = f"[{sp['level']}]" if sp.get("level") else ""
                self._spell_list_widget.addItem(f"{lv_tag} {sp['name']}")
            if not known:
                self._spell_list_widget.addItem("(Bu sınıf için büyü bulunamadı)")

        except Exception as exc:
            # Graceful fail — büyü bloğu bozulsa bile geri kalan UI sağlamlığını korur
            logger.warning("Spellbook UI refresh failed (graceful): %s", exc)

    def _on_spell_selected(self, text: str) -> None:
        """Listedeki bir büyüye tıklandığında açıklamasını gösterir."""
        import re
        try:
            idx = self._spell_list_widget.currentRow()
            if 0 <= idx < len(self._spell_data_cache):
                desc = self._spell_data_cache[idx].get("description", "")
                
                if desc:
                    desc = desc.replace("<br>", "\n").replace("<br/>", "\n").replace("<p>", "\n").replace("</p>", "\n")
                    desc = re.sub(r'<[^>]+>', '', desc)
                    desc = desc.strip()
                    
                self._spell_desc_box.setPlainText(desc or "Açıklama mevcut değil.")
                
                # Dinamik boyutlandırma (Min 50px, Max 250px)
                doc_height = int(self._spell_desc_box.document().size().height()) + 15
                new_height = max(50, min(doc_height, 250))
                self._spell_desc_box.setMinimumHeight(new_height)
                self._spell_desc_box.setMaximumHeight(new_height)
        except Exception:
            pass

    def add_spell_to_book(self) -> None:
        idx = self._spell_list_widget.currentRow()
        if 0 <= idx < len(self._spell_data_cache):
            spell = self._spell_data_cache[idx]
            spell_name = spell.get("name", "")
            
            # Use active_character state from manager directly since we use manager.active_character
            if "spells" not in self.manager.active_character:
                self.manager.active_character["spells"] = []
                
            if spell_name not in self.manager.active_character["spells"]:
                self.manager.active_character["spells"].append(spell_name)
                self._learned_spells_list.addItem(f"Lvl {spell.get('level', 0)} - {spell_name}")

    def reset(self) -> None:
        """Reset the scrollable creation layout."""
        self._name_edit.clear()
        self._alignment_edit.clear()
        self._deity_edit.clear()
        self._age_edit.clear()
        self._bg_edit.clear()
        self._desc_box.clear()
        self._portrait_lbl.setText("Görsel Yok")
        self._portrait_lbl.setPixmap(QPixmap())
        # Hide and clear subrace combo
        self._subrace_combo.clear()
        self._subrace_label.hide()
        self._subrace_combo.hide()
        # Hide and clear spellbook block
        self._block7_group.hide()
        self._spell_slots_table.setRowCount(0)
        self._spell_list_widget.clear()
        self._spell_desc_box.clear()
        self._bonus_slots_lbl.hide()
        self._spell_data_cache = []
        self._sys_combo.setCurrentIndex(0)
        self._on_system_changed()

    def _save_character(self) -> None:
        from desktop.api_client import api_client
        char = self.manager.active_character
        sys_key = self._sys_combo.currentData()
        
        # Build proper validation dictionary for soft validation
        races_list = self.manager.get_entities_by_category(sys_key, "race")
        classes_list = self.manager.get_entities_by_category(sys_key, "class")
        validation_data = {
            "races": [r.isim for r in races_list],
            "classes": [c.isim for c in classes_list]
        }
        
        soft = validate_character_soft(char, sys_key, validation_data)
        warnings = soft.warnings.copy()
        
        if warnings:
            reply = QMessageBox.question(
                self,
                "Uyarı",
                format_warning_message(warnings),
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No,
            )
            if reply == QMessageBox.Yes:
                char = mark_homebrew(char, warnings)
            elif reply == QMessageBox.No:
                return

        from desktop import local_db
        try:
            local_rec = local_db.save_local_character(self._db_path, char)
            new_id = local_rec.id
            QMessageBox.information(self, "Başarılı (Çevrimdışı/Lokal)", f"'{local_rec.name}' yerel veritabanına kaydedildi! Otomatik senkronize edilecek. (ID: {new_id})")
        except Exception as exc:
            logger.exception("Karakter kayıt hatası")
            QMessageBox.critical(self, "Hata", str(exc))
            new_id = None

        if new_id:
            self.character_created.emit(new_id)
            self.reset()
