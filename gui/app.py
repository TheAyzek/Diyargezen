import sys
import json
import base64
import time
from pathlib import Path
from typing import Optional
from PySide6 import QtWidgets
from PySide6.QtWidgets import *
from PySide6.QtCore import *
from PySide6.QtGui import *

# PyInstaller i├ğin ├ğal─▒┼şt─▒rma dizini: frozen ise _MEIPASS, de─şilse repo k├Âk├╝
if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
    APP_BASE_DIR = Path(sys._MEIPASS)
else:
    APP_BASE_DIR = Path(__file__).resolve().parents[1]

if str(APP_BASE_DIR) not in sys.path:
    sys.path.insert(0, str(APP_BASE_DIR))

from utils.data_loader import load_mm_data, load_vtm_data
from utils.storage import (
    CharacterRecord,
    init_db,
    list_characters,
    save_character,
)
from utils.export_pdf import (
    export_dnd_character_pdf,
    export_mm_character_pdf,
    export_vtm_character_pdf,
)
from utils.export_formats import (
    export_character_html,
    export_character_json,
    export_character_csv,
)
from utils.character_versioning import (
    save_character_version,
    load_character_version,
    list_character_versions,
    restore_character_version,
    delete_character_version,
    compare_versions,
)
from utils.character_statistics import analyze_character
from utils.recent_files import (
    add_recent_character,
    load_recent_characters,
    clear_recent_characters,
    get_recent_templates,
)
from utils.batch_operations import (
    batch_export_characters,
    batch_delete_characters,
    batch_analyze_characters,
    batch_create_templates,
    get_characters_from_directory,
)
from utils.performance import (
    monitor_performance,
    get_performance_stats,
    clear_performance_stats,
    get_cache_stats,
    clear_cache,
    MemoryManager,
)
from utils.template_manager import (
    save_template,
    load_template,
    list_templates,
    delete_template,
    create_character_from_template,
)
from utils.character_comparator import compare_characters
from utils.rule_extractor import extract_rules_from_file
from utils.rule_storage import save_rules, load_rules, list_available_rules
from utils.rule_validator import validate_rules, format_validation_report
from utils.rule_preview import format_rule_preview
try:
    from utils.rule_extractor_nlp import get_nlp_status, is_nlp_available
    NLP_MODULE_AVAILABLE = True
except ImportError:
    NLP_MODULE_AVAILABLE = False
    def get_nlp_status():
        return {"available": False, "library": None, "model_loaded": False}
    def is_nlp_available():
        return False
from utils.rule_versioning import (
    load_versions_list,
    load_version,
    restore_version,
    delete_version,
    format_version_info,
    save_version,
)
from utils.dynamic_calculator import (
    calculate_dynamic_proficiency_bonus,
    calculate_dynamic_armor_class,
    calculate_dynamic_hit_points,
    calculate_dynamic_power_points,
    calculate_dynamic_health,
    calculate_dynamic_willpower,
    load_rules_for_system,
)
from utils.calculations import (
    calculate_all_dnd_stats,
    calculate_proficiency_bonus,
    calculate_armor_class,
    calculate_hit_points,
    calculate_spell_slots,
    calculate_spell_save_dc,
    calculate_spell_attack_bonus,
    calculate_saving_throws,
    calculate_passive_perception,
    calculate_all_mm_stats,
    calculate_mm_power_points,
    calculate_mm_ability_modifier,
    calculate_mm_defense_limits,
    calculate_all_vtm_stats,
    calculate_vtm_health,
    calculate_vtm_willpower,
    calculate_vtm_dice_pool,
)


def _ensure_characters_dir() -> Path:
    characters_dir = APP_BASE_DIR / "characters"
    characters_dir.mkdir(parents=True, exist_ok=True)
    return characters_dir


def _ensure_images_dir() -> Path:
    """Karakter resimleri klas├Âr├╝n├╝ olu┼ştur ve d├Ând├╝r"""
    images_dir = APP_BASE_DIR / "characters" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    return images_dir


def _load_image_to_base64(image_path: Path) -> Optional[str]:
    """
    Resim dosyas─▒n─▒ base64 string'e ├ğevir
    
    Args:
        image_path: Resim dosyas─▒ yolu
    
    Returns:
        Base64 encoded string veya None
    """
    try:
        if not image_path.exists():
            return None
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            # MIME type'─▒ belirle
            suffix = image_path.suffix.lower()
            mime_types = {
                '.png': 'image/png',
                '.jpg': 'image/jpeg',
                '.jpeg': 'image/jpeg',
                '.gif': 'image/gif',
                '.bmp': 'image/bmp',
                '.webp': 'image/webp'
            }
            mime_type = mime_types.get(suffix, 'image/png')
            return f"data:{mime_type};base64,{base64_str}"
    except Exception:
        return None


def _get_image_from_character(character: dict) -> Optional[QPixmap]:
    """
    Karakter verisinden resmi y├╝kle ve QPixmap olarak d├Ând├╝r
    
    Args:
        character: Karakter verisi
    
    Returns:
        QPixmap veya None
    """
    image_data = character.get("image")
    if not image_data:
        return None
    
    try:
        if isinstance(image_data, str) and image_data.startswith('data:'):
            # Base64 string
            header, data = image_data.split(',', 1)
            image_bytes = base64.b64decode(data)
            pixmap = QPixmap()
            pixmap.loadFromData(image_bytes)
            return pixmap if not pixmap.isNull() else None
        elif isinstance(image_data, str):
            # Dosya yolu (geriye uyumluluk)
            image_path = Path(image_data)
            if image_path.exists():
                return QPixmap(str(image_path))
    except Exception:
        pass
    
    return None


def _save_character_via_dialog(parent: QWidget, character: dict, dialog_title: str, default_name: str) -> None:
    characters_dir = _ensure_characters_dir()
    safe_name = default_name.replace(" ", "_") or "karakter"
    default_path = characters_dir / f"{safe_name}.json"
    file_path, _ = QFileDialog.getSaveFileName(
        parent,
        dialog_title,
        str(default_path),
        "JSON Dosyalar─▒ (*.json)"
    )
    if not file_path:
        return
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(character, f, ensure_ascii=False, indent=2)
        QMessageBox.information(parent, "Ba┼şar─▒l─▒", f"Karakter kaydedildi:\n{file_path}")
    except Exception as exc:
        QMessageBox.critical(parent, "Hata", f"Karakter kaydedilemedi:\n{exc}")


class SqliteCharacterDialog(QDialog):
    """SQLite veritaban─▒ndan karakter se├ğmek i├ğin geli┼şmi┼ş dialog"""
    
    def __init__(self, parent: QWidget, db_path: Path, system_filter: str | None = None):
        super().__init__(parent)
        self.db_path = db_path
        self.system_filter = system_filter
        self.selected_record: CharacterRecord | None = None
        self._init_ui()
        self._load_characters()
    
    def _init_ui(self):
        self.setWindowTitle("SQLite Karakter Listesi")
        self.setMinimumSize(600, 500)
        layout = QVBoxLayout(self)
        
        # Sistem filtresi
        filter_layout = QHBoxLayout()
        filter_layout.addWidget(QLabel("Sistem Filtresi:"))
        self.system_combo = QComboBox()
        self.system_combo.addItem("T├╝m Sistemler", None)
        self.system_combo.addItem("D&D 5e", "DND5E")
        self.system_combo.addItem("M&M", "MUTANTS_AND_MASTERMINDS")
        self.system_combo.addItem("VtM", "VAMPIRE_THE_MASQUERADE")
        if self.system_filter:
            index = self.system_combo.findData(self.system_filter)
            if index >= 0:
                self.system_combo.setCurrentIndex(index)
        self.system_combo.currentIndexChanged.connect(self._load_characters)
        filter_layout.addWidget(self.system_combo)
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Ara:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Karakter ad─▒ ile ara...")
        self.search_edit.textChanged.connect(self._filter_characters)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Karakter listesi
        list_label = QLabel("Karakterler:")
        layout.addWidget(list_label)
        
        self.character_list = QListWidget()
        self.character_list.itemDoubleClicked.connect(self._on_double_click)
        self.character_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.character_list)
        
        # ├ûnizleme alan─▒
        preview_label = QLabel("├ûnizleme:")
        layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        layout.addWidget(self.preview_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("Y├╝kle")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("─░ptal")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def _load_characters(self):
        self.character_list.clear()
        self.all_records: list[CharacterRecord] = []
        
        try:
            all_recs = list_characters(self.db_path)
            system_filter = self.system_combo.currentData()
            if system_filter:
                all_recs = [r for r in all_recs if r.system == system_filter]
            self.all_records = all_recs
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakterler y├╝klenemedi:\n{e}")
            return
        
        for rec in self.all_records:
            item_text = f"#{rec.id or '-'} - {rec.name} ({rec.system})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, rec)
            self.character_list.addItem(item)
        
        if not self.all_records:
            self.character_list.addItem("Karakter bulunamad─▒")
    
    def _filter_characters(self):
        search_text = self.search_edit.text().lower()
        for i in range(self.character_list.count()):
            item = self.character_list.item(i)
            if item:
                item.setHidden(search_text not in item.text().lower())
    
    def _on_selection_changed(self):
        current = self.character_list.currentItem()
        if not current:
            self.load_btn.setEnabled(False)
            self.preview_text.clear()
            return
        
        rec = current.data(Qt.UserRole)
        if not rec or not isinstance(rec, CharacterRecord):
            self.load_btn.setEnabled(False)
            self.preview_text.clear()
            return
        
        self.selected_record = rec
        self.load_btn.setEnabled(True)
        
        # ├ûnizleme olu┼ştur
        preview_lines = [
            f"ID: {rec.id}",
            f"─░sim: {rec.name}",
            f"Sistem: {rec.system}",
            "",
            "Karakter Bilgileri:"
        ]
        
        data = rec.data
        if isinstance(data, dict):
            if data.get("race"):
                preview_lines.append(f"Irk/Klan: {data.get('race', data.get('clan', '-'))}")
            if data.get("class"):
                preview_lines.append(f"S─▒n─▒f/Arketip: {data.get('class', data.get('archetype', '-'))}")
            if data.get("level"):
                preview_lines.append(f"Seviye: {data.get('level', '-')}")
            if data.get("power_level"):
                preview_lines.append(f"Power Level: {data.get('power_level', '-')}")
        
        self.preview_text.setPlainText("\n".join(preview_lines))
    
    def _on_double_click(self):
        if self.load_btn.isEnabled():
            self.accept()
    
    def get_selected_record(self) -> CharacterRecord | None:
        return self.selected_record


class CharacterListDialog(QDialog):
    """JSON karakter dosyalar─▒n─▒ listeleyen ve filtreleyen diyalog"""
    
    def __init__(self, parent: QWidget, expected_system: str | None = None):
        super().__init__(parent)
        self.expected_system = expected_system
        self.selected_character_data = None
        self.selected_file_path = None
        self.all_characters: list[dict] = []
        self._init_ui()
        self._load_characters()
    
    def _init_ui(self):
        self.setWindowTitle("Karakter Listesi")
        self.setMinimumSize(700, 600)
        layout = QVBoxLayout(self)
        
        # Filtreler
        filter_layout = QHBoxLayout()
        
        # Sistem filtresi
        filter_layout.addWidget(QLabel("Sistem:"))
        self.system_combo = QComboBox()
        self.system_combo.addItem("T├╝m├╝", None)
        self.system_combo.addItem("D&D 5e", "DND5E")
        self.system_combo.addItem("M&M", "MUTANTS_AND_MASTERMINDS")
        self.system_combo.addItem("VtM", "VTM5E")
        if self.expected_system:
            index = self.system_combo.findData(self.expected_system)
            if index >= 0:
                self.system_combo.setCurrentIndex(index)
        self.system_combo.currentIndexChanged.connect(self._filter_characters)
        filter_layout.addWidget(self.system_combo)
        
        # Irk filtresi (D&D i├ğin)
        filter_layout.addWidget(QLabel("Irk:"))
        self.race_combo = QComboBox()
        self.race_combo.addItem("T├╝m├╝", None)
        self.race_combo.currentIndexChanged.connect(self._filter_characters)
        filter_layout.addWidget(self.race_combo)
        
        # S─▒n─▒f filtresi (D&D i├ğin)
        filter_layout.addWidget(QLabel("S─▒n─▒f:"))
        self.class_combo = QComboBox()
        self.class_combo.addItem("T├╝m├╝", None)
        self.class_combo.currentIndexChanged.connect(self._filter_characters)
        filter_layout.addWidget(self.class_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("­şöı Ara:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Karakter ad─▒na g├Âre ara...")
        self.search_edit.textChanged.connect(self._filter_characters)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Karakter listesi
        list_label = QLabel("Karakterler:")
        layout.addWidget(list_label)
        
        self.character_list = QListWidget()
        self.character_list.itemDoubleClicked.connect(self._on_double_click)
        self.character_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.character_list)
        
        # ├ûnizleme alan─▒
        preview_label = QLabel("├ûnizleme:")
        layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        layout.addWidget(self.preview_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("Y├╝kle")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("─░ptal")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def _load_characters(self):
        """T├╝m karakter dosyalar─▒n─▒ y├╝kle (optimize edilmi┼ş)"""
        self.character_list.clear()
        self.all_characters = []
        
        characters_dir = _ensure_characters_dir()
        if not characters_dir.exists():
            self.character_list.addItem("Karakter klas├Âr├╝ bulunamad─▒")
            return
        
        # Performans izleme
        start_time = time.time()
        
        # T├╝m JSON dosyalar─▒n─▒ y├╝kle (batch processing ile)
        json_files = [f for f in characters_dir.glob("*.json") if "images" not in str(f)]
        
        # B├╝y├╝k listeler i├ğin batch processing
        batch_size = 50
        for i in range(0, len(json_files), batch_size):
            batch = json_files[i:i + batch_size]
            for filepath in batch:
                try:
                    with open(filepath, "r", encoding="utf-8") as f:
                        data = json.load(f)
                        if isinstance(data, dict) and "name" in data:
                            data["_file_path"] = str(filepath)
                            self.all_characters.append(data)
                except Exception:
                    continue
            
            # GUI'yi g├╝ncelle (her batch'te)
            if i + batch_size < len(json_files):
                QApplication.processEvents()
        
        # Irk ve s─▒n─▒f listelerini g├╝ncelle
        self._update_filter_lists()
        
        # Karakterleri filtrele ve g├Âster
        self._filter_characters()
        
        # Performans log (debug i├ğin)
        load_time = time.time() - start_time
        if load_time > 0.5:  # 0.5 saniyeden uzun s├╝rerse log
            print(f"CharacterListDialog: {len(self.all_characters)} karakter {load_time:.2f}s'de y├╝klendi")
    
    def _update_filter_lists(self):
        """Irk ve s─▒n─▒f filtre listelerini g├╝ncelle"""
        races = set()
        classes = set()
        
        for char in self.all_characters:
            if char.get("system") == "DND5E":
                race = char.get("race", "")
                if race:
                    races.add(race)
                char_class = char.get("class", "")
                if char_class:
                    classes.add(char_class)
        
        # Irk combo box'─▒n─▒ g├╝ncelle
        self.race_combo.clear()
        self.race_combo.addItem("T├╝m├╝", None)
        for race in sorted(races):
            self.race_combo.addItem(race, race)
        
        # S─▒n─▒f combo box'─▒n─▒ g├╝ncelle
        self.class_combo.clear()
        self.class_combo.addItem("T├╝m├╝", None)
        for char_class in sorted(classes):
            self.class_combo.addItem(char_class, char_class)
    
    def _filter_characters(self):
        """Karakterleri filtrele ve listele"""
        self.character_list.clear()
        
        search_text = self.search_edit.text().lower()
        system_filter = self.system_combo.currentData()
        race_filter = self.race_combo.currentData()
        class_filter = self.class_combo.currentData()
        
        filtered = []
        for char in self.all_characters:
            # Sistem filtresi
            if system_filter and char.get("system") != system_filter:
                continue
            
            # Beklenen sistem kontrol├╝
            if self.expected_system and char.get("system") != self.expected_system:
                continue
            
            # Arama filtresi
            if search_text:
                name = char.get("name", "").lower()
                if search_text not in name:
                    continue
            
            # Irk filtresi (sadece D&D i├ğin)
            if race_filter and char.get("system") == "DND5E":
                if char.get("race") != race_filter:
                    continue
            
            # S─▒n─▒f filtresi (sadece D&D i├ğin)
            if class_filter and char.get("system") == "DND5E":
                if char.get("class") != class_filter:
                    continue
            
            filtered.append(char)
        
        # Karakterleri listele (batch processing ile)
        batch_size = 100
        for i in range(0, len(filtered), batch_size):
            batch = filtered[i:i + batch_size]
            for char in batch:
                name = char.get("name", "─░simsiz")
                system = char.get("system", "Bilinmeyen")
                system_display = {
                    "DND5E": "D&D 5e",
                    "MUTANTS_AND_MASTERMINDS": "M&M",
                    "VTM5E": "VtM"
                }.get(system, system)
                
                # D&D i├ğin ek bilgiler
                if system == "DND5E":
                    race = char.get("race", "")
                    char_class = char.get("class", "")
                    level = char.get("level", 1)
                    item_text = f"{name} - {system_display} | {race} {char_class} (Seviye {level})"
                elif system == "MUTANTS_AND_MASTERMINDS":
                    pl = char.get("power_level", "")
                    codename = char.get("codename", "")
                    item_text = f"{name} - {system_display} | PL {pl}"
                    if codename:
                        item_text += f" ({codename})"
                elif system == "VTM5E":
                    clan = char.get("clan", "")
                    item_text = f"{name} - {system_display} | {clan}"
                else:
                    item_text = f"{name} - {system_display}"
                
                item = QListWidgetItem(item_text)
                item.setData(Qt.UserRole, char)
                self.character_list.addItem(item)
            
            # GUI'yi g├╝ncelle (her batch'te)
            if i + batch_size < len(filtered):
                QApplication.processEvents()
        
        if not filtered:
            self.character_list.addItem("Karakter bulunamad─▒")
    
    def _on_selection_changed(self):
        """Se├ğim de─şi┼şti─şinde ├Ânizlemeyi g├╝ncelle"""
        selected_items = self.character_list.selectedItems()
        if not selected_items:
            self.load_btn.setEnabled(False)
            self.preview_text.clear()
            return
        
        item = selected_items[0]
        char = item.data(Qt.UserRole)
        if not char or not isinstance(char, dict):
            self.load_btn.setEnabled(False)
            return
        
        self.selected_character_data = char
        self.selected_file_path = char.get("_file_path")
        self.load_btn.setEnabled(True)
        
        # ├ûnizleme olu┼ştur
        preview_lines = []
        preview_lines.append(f"─░sim: {char.get('name', '─░simsiz')}")
        preview_lines.append(f"Sistem: {char.get('system', 'Bilinmeyen')}")
        
        if char.get("system") == "DND5E":
            preview_lines.append(f"Irk: {char.get('race', '')}")
            preview_lines.append(f"S─▒n─▒f: {char.get('class', '')}")
            preview_lines.append(f"Seviye: {char.get('level', 1)}")
        elif char.get("system") == "MUTANTS_AND_MASTERMINDS":
            preview_lines.append(f"Power Level: {char.get('power_level', '')}")
            preview_lines.append(f"Arketip: {char.get('archetype', '')}")
        elif char.get("system") == "VTM5E":
            preview_lines.append(f"Clan: {char.get('clan', '')}")
            preview_lines.append(f"Concept: {char.get('concept', '')}")
        
        self.preview_text.setPlainText("\n".join(preview_lines))
    
    def _on_double_click(self):
        """├çift t─▒klama ile h─▒zl─▒ y├╝kleme"""
        if self.load_btn.isEnabled():
            self.accept()
    
    def get_selected_character(self) -> tuple[dict | None, str | None]:
        """Se├ğili karakteri d├Ând├╝r"""
        if self.selected_character_data and self.selected_file_path:
            return self.selected_character_data, self.selected_file_path
        return None, None


class TemplateManagerDialog(QDialog):
    """┼Şablon y├Ânetimi diyalo─şu"""
    
    def __init__(self, parent: QWidget, system_filter: str | None = None):
        from datetime import datetime  # Lazy import
        super().__init__(parent)
        self.system_filter = system_filter
        self.selected_template = None
        self._init_ui()
        self._load_templates()
    
    def _init_ui(self):
        self.setWindowTitle("Karakter ┼Şablonlar─▒")
        self.setMinimumSize(700, 600)
        layout = QVBoxLayout(self)
        
        # Butonlar (├╝stte)
        button_layout = QHBoxLayout()
        
        save_template_btn = QPushButton("­şÆ¥ Mevcut Karakteri ┼Şablon Olarak Kaydet")
        save_template_btn.setToolTip("A├ğ─▒k olan karakteri ┼şablon olarak kaydet")
        save_template_btn.clicked.connect(self._save_current_as_template)
        button_layout.addWidget(save_template_btn)
        
        refresh_btn = QPushButton("­şöä Yenile")
        refresh_btn.clicked.connect(self._load_templates)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("­şöı Ara:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("┼Şablon ad─▒na g├Âre ara...")
        self.search_edit.textChanged.connect(self._filter_templates)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # ┼Şablon listesi
        list_label = QLabel("┼Şablonlar:")
        layout.addWidget(list_label)
        
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self._on_double_click)
        self.template_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.template_list)
        
        # ├ûnizleme alan─▒
        preview_label = QLabel("├ûnizleme:")
        layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        layout.addWidget(self.preview_text)
        
        # Butonlar (altta)
        button_layout2 = QHBoxLayout()
        self.use_btn = QPushButton("Kullan")
        self.use_btn.setEnabled(False)
        self.use_btn.clicked.connect(self.accept)
        
        delete_btn = QPushButton("­şùæ´©Å Sil")
        delete_btn.setEnabled(False)
        delete_btn.clicked.connect(self._delete_template)
        self.delete_btn = delete_btn
        
        cancel_btn = QPushButton("─░ptal")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout2.addWidget(delete_btn)
        button_layout2.addStretch()
        button_layout2.addWidget(self.use_btn)
        button_layout2.addWidget(cancel_btn)
        layout.addLayout(button_layout2)
    
    def _load_templates(self):
        """T├╝m ┼şablonlar─▒ y├╝kle"""
        self.template_list.clear()
        self.all_templates = list_templates(APP_BASE_DIR, self.system_filter)
        self._filter_templates()
    
    def _filter_templates(self):
        """┼Şablonlar─▒ filtrele ve listele"""
        from datetime import datetime
        
        self.template_list.clear()
        
        search_text = self.search_edit.text().lower()
        
        for template in self.all_templates:
            template_name = template.get("template_name", "").lower()
            if search_text and search_text not in template_name:
                continue
            
            # ┼Şablon bilgilerini g├Âster
            system = template.get("system", "Bilinmeyen")
            system_display = {
                "DND5E": "D&D 5e",
                "MUTANTS_AND_MASTERMINDS": "M&M",
                "VTM5E": "VtM"
            }.get(system, system)
            
            description = template.get("description", "")
            created_at = template.get("created_at", "")
            
            # Tarihi formatla
            try:
                dt = datetime.fromisoformat(created_at)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
            except:
                date_str = created_at
            
            item_text = f"{template.get('template_name', '─░simsiz')} - {system_display}"
            if description:
                item_text += f" | {description}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, template)
            self.template_list.addItem(item)
        
        if not self.template_list.count():
            self.template_list.addItem("┼Şablon bulunamad─▒")
    
    def _on_selection_changed(self):
        """Se├ğim de─şi┼şti─şinde ├Ânizlemeyi g├╝ncelle"""
        selected_items = self.template_list.selectedItems()
        if not selected_items:
            self.use_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            self.preview_text.clear()
            return
        
        item = selected_items[0]
        template = item.data(Qt.UserRole)
        if not template or not isinstance(template, dict):
            self.use_btn.setEnabled(False)
            self.delete_btn.setEnabled(False)
            return
        
        self.selected_template = template
        self.use_btn.setEnabled(True)
        self.delete_btn.setEnabled(True)
        
        # ├ûnizleme olu┼ştur
        preview_lines = []
        preview_lines.append(f"┼Şablon Ad─▒: {template.get('template_name', '─░simsiz')}")
        preview_lines.append(f"Sistem: {template.get('system', 'Bilinmeyen')}")
        
        description = template.get("description", "")
        if description:
            preview_lines.append(f"A├ğ─▒klama: {description}")
        
        created_at = template.get("created_at", "")
        if created_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
                preview_lines.append(f"Olu┼şturulma: {date_str}")
            except:
                pass
        
        template_data = template.get("template_data", {})
        if template_data:
            preview_lines.append("")
            preview_lines.append("┼Şablon ─░├ğeri─şi:")
            
            if template.get("system") == "DND5E":
                if template_data.get("race"):
                    preview_lines.append(f"  Irk: {template_data.get('race')}")
                if template_data.get("class"):
                    preview_lines.append(f"  S─▒n─▒f: {template_data.get('class')}")
                if template_data.get("level"):
                    preview_lines.append(f"  Seviye: {template_data.get('level')}")
            elif template.get("system") == "MUTANTS_AND_MASTERMINDS":
                if template_data.get("power_level"):
                    preview_lines.append(f"  Power Level: {template_data.get('power_level')}")
                if template_data.get("archetype"):
                    preview_lines.append(f"  Arketip: {template_data.get('archetype')}")
            elif template.get("system") == "VTM5E":
                if template_data.get("clan"):
                    preview_lines.append(f"  Clan: {template_data.get('clan')}")
        
        self.preview_text.setPlainText("\n".join(preview_lines))
    
    def _on_double_click(self):
        """├çift t─▒klama ile h─▒zl─▒ kullanma"""
        if self.use_btn.isEnabled():
            self.accept()
    
    def _save_current_as_template(self):
        """Mevcut karakteri ┼şablon olarak kaydet"""
        # Parent'tan mevcut karakteri al
        parent = self.parent()
        if not hasattr(parent, 'current_character') or not parent.current_character:
            QMessageBox.warning(self, "Uyar─▒", "├ûnce bir karakter olu┼şturman─▒z gerekiyor.")
            return
        
        # ┼Şablon ad─▒ ve a├ğ─▒klamas─▒ al
        template_name, ok = QInputDialog.getText(
            self,
            "┼Şablon Olarak Kaydet",
            "┼Şablon ad─▒:"
        )
        if not ok or not template_name.strip():
            return
        
        description, ok = QInputDialog.getText(
            self,
            "┼Şablon A├ğ─▒klamas─▒",
            "┼Şablon a├ğ─▒klamas─▒ (opsiyonel):"
        )
        if not ok:
            description = ""
        
        try:
            template_path = save_template(
                parent.current_character,
                APP_BASE_DIR,
                template_name.strip(),
                description.strip()
            )
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"┼Şablon kaydedildi:\n{template_path}")
            self._load_templates()  # Listeyi yenile
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"┼Şablon kaydedilemedi:\n{str(e)}")
    
    def _delete_template(self):
        """Se├ğili ┼şablonu sil"""
        if not self.selected_template:
            return
        
        template_name = self.selected_template.get("template_name", "Bu ┼şablon")
        reply = QMessageBox.question(
            self,
            "┼Şablonu Sil",
            f"'{template_name}' ┼şablonunu silmek istedi─şinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            file_path = self.selected_template.get("_file_path")
            if file_path:
                if delete_template(Path(file_path)):
                    QMessageBox.information(self, "Ba┼şar─▒l─▒", "┼Şablon silindi.")
                    self._load_templates()  # Listeyi yenile
                else:
                    QMessageBox.warning(self, "Hata", "┼Şablon silinemedi.")
    
    def get_selected_template(self) -> dict | None:
        """Se├ğili ┼şablonu d├Ând├╝r"""
        return self.selected_template


class ExportFormatDialog(QDialog):
    """Export format se├ğimi diyalo─şu"""
    
    def __init__(self, parent: QWidget, character: dict):
        super().__init__(parent)
        self.character = character
        self.selected_format = None
        self.selected_path = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("Export Format─▒ Se├ğ")
        self.setMinimumSize(500, 400)
        layout = QVBoxLayout(self)
        
        # Ba┼şl─▒k
        title = QLabel("Karakter Export Format─▒ Se├ğin")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Format se├ğimi
        format_group = QGroupBox("Format")
        format_layout = QVBoxLayout()
        
        self.format_buttons = {}
        formats = [
            ("PDF", "­şôä PDF - Yazd─▒r─▒labilir format"),
            ("HTML", "­şîÉ HTML - Web g├Âr├╝nt├╝leme"),
            ("JSON", "­şôï JSON - Veri aktar─▒m─▒"),
            ("CSV", "­şôè CSV - Tablo format─▒"),
        ]
        
        for format_type, label in formats:
            btn = QRadioButton(label)
            btn.setStyleSheet("font-size: 12px; padding: 5px;")
            format_layout.addWidget(btn)
            self.format_buttons[format_type] = btn
        
        # ─░lk se├ğene─şi varsay─▒lan yap
        if "PDF" in self.format_buttons:
            self.format_buttons["PDF"].setChecked(True)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Dosya yolu
        path_group = QGroupBox("Kay─▒t Konumu")
        path_layout = QVBoxLayout()
        
        path_layout_widget = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        browse_btn = QPushButton("­şôü G├Âzat")
        browse_btn.clicked.connect(self._browse_file)
        path_layout_widget.addWidget(self.path_edit)
        path_layout_widget.addWidget(browse_btn)
        path_layout.addLayout(path_layout_widget)
        
        # Format de─şi┼şti─şinde dosya yolunu g├╝ncelle
        for btn in self.format_buttons.values():
            btn.toggled.connect(self._update_path)
        
        path_group.setLayout(path_layout)
        layout.addWidget(path_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        export_btn = QPushButton("Export")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        export_btn.clicked.connect(self.accept)
        
        cancel_btn = QPushButton("─░ptal")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(export_btn)
        layout.addLayout(button_layout)
        
        # ─░lk path g├╝ncellemesi
        self._update_path()
    
    def _update_path(self):
        """Se├ğili formata g├Âre dosya yolunu g├╝ncelle"""
        selected_format = None
        for format_type, btn in self.format_buttons.items():
            if btn.isChecked():
                selected_format = format_type
                break
        
        if selected_format:
            safe_name = "".join(c for c in self.character.get("name", "karakter") if c.isalnum() or c in (' ', '-', '_')).rstrip() or "karakter"
            default_path = _ensure_characters_dir() / f"{safe_name}.{selected_format.lower()}"
            self.path_edit.setText(str(default_path))
    
    def _browse_file(self):
        """Dosya kay─▒t konumu se├ğ"""
        selected_format = None
        for format_type, btn in self.format_buttons.items():
            if btn.isChecked():
                selected_format = format_type
                break
        
        if not selected_format:
            QMessageBox.warning(self, "Uyar─▒", "L├╝tfen bir format se├ğin.")
            return
        
        safe_name = "".join(c for c in self.character.get("name", "karakter") if c.isalnum() or c in (' ', '-', '_')).rstrip() or "karakter"
        default_path = _ensure_characters_dir() / f"{safe_name}.{selected_format.lower()}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Karakteri {selected_format} olarak kaydet",
            str(default_path),
            f"{selected_format} Dosyalar─▒ (*.{selected_format.lower()})"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def get_selected_format(self) -> tuple[str | None, str | None]:
        """Se├ğili format ve dosya yolunu d├Ând├╝r"""
        selected_format = None
        for format_type, btn in self.format_buttons.items():
            if btn.isChecked():
                selected_format = format_type
                break
        
        file_path = self.path_edit.text()
        if not file_path:
            return None, None
        
        return selected_format, file_path


class CharacterComparisonDialog(QDialog):
    """Karakter kar┼ş─▒la┼şt─▒rma diyalo─şu"""
    
    def __init__(self, parent: QWidget, system_filter: str | None = None):
        super().__init__(parent)
        self.system_filter = system_filter
        self.char1_data = None
        self.char2_data = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("Karakter Kar┼ş─▒la┼şt─▒rma")
        self.setMinimumSize(1000, 700)
        layout = QVBoxLayout(self)
        
        # Karakter se├ğimi
        selection_layout = QHBoxLayout()
        
        # Karakter 1
        char1_group = QGroupBox("Karakter 1")
        char1_layout = QVBoxLayout()
        self.char1_label = QLabel("Karakter se├ğilmedi")
        self.char1_label.setStyleSheet("font-weight: bold; padding: 5px;")
        char1_btn = QPushButton("­şôï Karakter Se├ğ")
        char1_btn.clicked.connect(lambda: self._select_character(1))
        char1_layout.addWidget(self.char1_label)
        char1_layout.addWidget(char1_btn)
        char1_group.setLayout(char1_layout)
        
        # Karakter 2
        char2_group = QGroupBox("Karakter 2")
        char2_layout = QVBoxLayout()
        self.char2_label = QLabel("Karakter se├ğilmedi")
        self.char2_label.setStyleSheet("font-weight: bold; padding: 5px;")
        char2_btn = QPushButton("­şôï Karakter Se├ğ")
        char2_btn.clicked.connect(lambda: self._select_character(2))
        char2_layout.addWidget(self.char2_label)
        char2_layout.addWidget(char2_btn)
        char2_group.setLayout(char2_layout)
        
        selection_layout.addWidget(char1_group)
        selection_layout.addWidget(char2_group)
        layout.addLayout(selection_layout)
        
        # Kar┼ş─▒la┼şt─▒r butonu
        compare_btn = QPushButton("­şöı Kar┼ş─▒la┼şt─▒r")
        compare_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        compare_btn.clicked.connect(self._compare_characters)
        self.compare_btn = compare_btn
        layout.addWidget(compare_btn)
        
        # Sonu├ğlar (tab widget)
        self.results_tabs = QTabWidget()
        layout.addWidget(self.results_tabs)
        
        # ├ûzet sekmesi
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        self.results_tabs.addTab(self.summary_tab, "­şôè ├ûzet")
        
        # Farklar sekmesi
        self.differences_tab = QWidget()
        differences_layout = QVBoxLayout(self.differences_tab)
        self.differences_text = QTextEdit()
        self.differences_text.setReadOnly(True)
        differences_layout.addWidget(self.differences_text)
        self.results_tabs.addTab(self.differences_tab, "ÔÜá´©Å Farklar")
        
        # Benzerlikler sekmesi
        self.similarities_tab = QWidget()
        similarities_layout = QVBoxLayout(self.similarities_tab)
        self.similarities_text = QTextEdit()
        self.similarities_text.setReadOnly(True)
        similarities_layout.addWidget(self.similarities_text)
        self.results_tabs.addTab(self.similarities_tab, "Ô£à Benzerlikler")
        
        # Butonlar
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # Ba┼şlang─▒├ğta sonu├ğlar─▒ gizle
        self.results_tabs.setVisible(False)
        self.compare_btn.setEnabled(False)
    
    def _select_character(self, char_num: int):
        """Karakter se├ğ"""
        dialog = CharacterListDialog(self, self.system_filter)
        dialog.setWindowTitle(f"Karakter {char_num} Se├ğ")
        
        if dialog.exec() == QDialog.Accepted:
            data, path = dialog.get_selected_character()
            if data:
                if char_num == 1:
                    self.char1_data = data
                    self.char1_label.setText(f"Ô£à {data.get('name', '─░simsiz')} ({data.get('system', 'Unknown')})")
                else:
                    self.char2_data = data
                    self.char2_label.setText(f"Ô£à {data.get('name', '─░simsiz')} ({data.get('system', 'Unknown')})")
                
                # Her iki karakter se├ğildiyse kar┼ş─▒la┼şt─▒r butonunu etkinle┼ştir
                if self.char1_data and self.char2_data:
                    self.compare_btn.setEnabled(True)
    
    def _compare_characters(self):
        """Karakterleri kar┼ş─▒la┼şt─▒r"""
        if not self.char1_data or not self.char2_data:
            QMessageBox.warning(self, "Uyar─▒", "L├╝tfen her iki karakteri de se├ğin.")
            return
        
        try:
            result = compare_characters(self.char1_data, self.char2_data)
            
            if "error" in result:
                QMessageBox.warning(self, "Hata", result["error"])
                return
            
            # Sonu├ğlar─▒ g├Âster
            self._display_results(result)
            self.results_tabs.setVisible(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Kar┼ş─▒la┼şt─▒rma s─▒ras─▒nda hata olu┼ştu:\n{str(e)}")
    
    def _display_results(self, result: dict):
        """Kar┼ş─▒la┼şt─▒rma sonu├ğlar─▒n─▒ g├Âster"""
        system = result.get("system", "Unknown")
        char1_name = result.get("char1_name", "Unknown")
        char2_name = result.get("char2_name", "Unknown")
        differences = result.get("differences", [])
        similarities = result.get("similarities", [])
        summary = result.get("summary", {})
        
        # ├ûzet
        summary_lines = []
        summary_lines.append(f"­şôè Karakter Kar┼ş─▒la┼şt─▒rma ├ûzeti")
        summary_lines.append(f"{'=' * 50}")
        summary_lines.append(f"")
        summary_lines.append(f"Karakter 1: {char1_name}")
        summary_lines.append(f"Karakter 2: {char2_name}")
        summary_lines.append(f"Sistem: {system}")
        summary_lines.append(f"")
        summary_lines.append(f"­şôê ─░statistikler:")
        summary_lines.append(f"  ÔÇó Toplam Fark: {summary.get('total_differences', 0)}")
        summary_lines.append(f"  ÔÇó Toplam Benzerlik: {summary.get('total_similarities', 0)}")
        
        if "level_difference" in summary:
            level_diff = summary["level_difference"]
            if level_diff > 0:
                summary_lines.append(f"  ÔÇó Seviye Fark─▒: {char1_name} {level_diff} seviye daha y├╝ksek")
            elif level_diff < 0:
                summary_lines.append(f"  ÔÇó Seviye Fark─▒: {char2_name} {abs(level_diff)} seviye daha y├╝ksek")
            else:
                summary_lines.append(f"  ÔÇó Seviye: Ayn─▒")
        
        self.summary_text.setPlainText("\n".join(summary_lines))
        
        # Farklar
        if differences:
            diff_lines = []
            diff_lines.append(f"ÔÜá´©Å Karakterler Aras─▒ndaki Farklar")
            diff_lines.append(f"{'=' * 50}")
            diff_lines.append("")
            
            for diff in differences:
                field = diff.get("field", "Unknown")
                diff_type = diff.get("type", "unknown")
                
                if diff_type == "basic":
                    diff_lines.append(f"­şôØ {field.replace('_', ' ').title()}:")
                    diff_lines.append(f"   {char1_name}: {diff.get('char1', 'N/A')}")
                    diff_lines.append(f"   {char2_name}: {diff.get('char2', 'N/A')}")
                    diff_lines.append("")
                
                elif diff_type in ["ability", "attribute", "defense", "skill", "power_points", "humanity", "health", "willpower"]:
                    diff_val = diff.get("difference", 0)
                    if diff_val > 0:
                        diff_lines.append(f"­şôê {field.replace('_', ' ').title()}: {char1_name} +{diff_val} daha y├╝ksek")
                    else:
                        diff_lines.append(f"­şôë {field.replace('_', ' ').title()}: {char2_name} +{abs(diff_val)} daha y├╝ksek")
                    diff_lines.append(f"   {char1_name}: {diff.get('char1', 0)}")
                    diff_lines.append(f"   {char2_name}: {diff.get('char2', 0)}")
                    diff_lines.append("")
                
                elif diff_type in ["skills", "spells", "feats", "powers", "disciplines"]:
                    diff_lines.append(f"­şôï {field.replace('_', ' ').title()}:")
                    diff_diffs = diff.get("differences", {})
                    if isinstance(diff_diffs, dict):
                        if "only_char1" in diff_diffs and diff_diffs["only_char1"]:
                            diff_lines.append(f"   Sadece {char1_name}: {', '.join(map(str, diff_diffs['only_char1']))}")
                        if "only_char2" in diff_diffs and diff_diffs["only_char2"]:
                            diff_lines.append(f"   Sadece {char2_name}: {', '.join(map(str, diff_diffs['only_char2']))}")
                        if "common" in diff_diffs and diff_diffs["common"]:
                            diff_lines.append(f"   Ortak: {', '.join(map(str, diff_diffs['common']))}")
                    diff_lines.append("")
            
            self.differences_text.setPlainText("\n".join(diff_lines))
        else:
            self.differences_text.setPlainText("­şÄë Hi├ğ fark yok! Karakterler tamamen ayn─▒.")
        
        # Benzerlikler
        if similarities:
            sim_lines = []
            sim_lines.append(f"Ô£à Ortak ├ûzellikler")
            sim_lines.append(f"{'=' * 50}")
            sim_lines.append("")
            
            for sim in similarities:
                field = sim.get("field", "Unknown")
                value = sim.get("value", "N/A")
                sim_type = sim.get("type", "unknown")
                
                if sim_type == "basic":
                    sim_lines.append(f"­şôØ {field.replace('_', ' ').title()}: {value}")
                elif sim_type in ["ability", "attribute"]:
                    sim_lines.append(f"­şôè {field.replace('_', ' ').title()}: {value}")
            
            self.similarities_text.setPlainText("\n".join(sim_lines))
        else:
            self.similarities_text.setPlainText("Ôä╣´©Å Ortak ├Âzellik bulunamad─▒.")


def _load_character_via_dialog(parent: QWidget, dialog_title: str, expected_system: str) -> tuple[dict | None, str | None]:
    """Karakter y├╝kleme diyalo─şu - eski y├Ântem (dosya se├ğimi)"""
    # Yeni karakter listesi diyalo─şunu kullan
    dialog = CharacterListDialog(parent, expected_system)
    dialog.setWindowTitle(dialog_title)
    
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_selected_character()
    
    return None, None

def _select_template_character(parent: QWidget, system_name: str) -> tuple[dict | None, str | None]:
    """┼Şablon se├ğimi sonras─▒ karakter verisini d├Ând├╝r"""
    dialog = TemplateManagerDialog(parent, system_name)
    if dialog.exec() != QDialog.Accepted:
        return None, None

    template = dialog.get_selected_template()
    if not template:
        QMessageBox.warning(parent, "Uyar─▒", "Bir ┼şablon se├ğmediniz.")
        return None, None

    default_name = template.get("template_name", "Yeni Karakter")
    character_name, ok = QInputDialog.getText(
        parent,
        "┼Şablonu Kullan",
        "Yeni karakter ad─▒:",
        QLineEdit.Normal,
        default_name
    )
    if not ok or not character_name.strip():
        return None, None

    character_name = character_name.strip()
    character = create_character_from_template(template, character_name)
    character["system"] = system_name
    return character, character_name


class RuleEditorDialog(QDialog):
    """Kural d├╝zenleme diyalo─şu"""
    
    def __init__(self, parent: QWidget, system_name: str, base_dir: Path):
        super().__init__(parent)
        self.system_name = system_name
        self.base_dir = base_dir
        self.rules = None
        self._init_ui()
        self._load_rules()
    
    def _init_ui(self):
        self.setWindowTitle(f"Kural D├╝zenle - {self.system_name}")
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        
        # Bilgi etiketi
        info_label = QLabel(
            "Kurallar─▒ JSON format─▒nda d├╝zenleyebilirsiniz. "
            "De─şi┼şiklikleri kaydetmek i├ğin 'Kaydet' butonuna t─▒klay─▒n."
        )
        info_label.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # JSON edit├Âr├╝
        self.json_editor = QTextEdit()
        self.json_editor.setFont(QFont("Consolas", 10))
        self.json_editor.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: 1px solid #3c3f41;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.json_editor)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        # Yeniden y├╝kle butonu
        reload_btn = QPushButton("­şöä Yeniden Y├╝kle")
        reload_btn.setToolTip("Orijinal kurallar─▒ y├╝kle (de─şi┼şiklikler kaybolur)")
        reload_btn.clicked.connect(self._load_rules)
        button_layout.addWidget(reload_btn)
        
        # JSON do─şrula butonu
        validate_json_btn = QPushButton("Ô£ô JSON Do─şrula")
        validate_json_btn.setToolTip("JSON format─▒n─▒ kontrol et")
        validate_json_btn.clicked.connect(self._validate_json)
        button_layout.addWidget(validate_json_btn)
        
        # Kural do─şrulama butonu
        validate_rules_btn = QPushButton("­şöı Kurallar─▒ Do─şrula")
        validate_rules_btn.setToolTip("Kural yap─▒s─▒n─▒, eksiklikleri ve ├ğeli┼şkileri kontrol et")
        validate_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        validate_rules_btn.clicked.connect(self._validate_rules)
        button_layout.addWidget(validate_rules_btn)
        
        button_layout.addStretch()
        
        # ─░ptal butonu
        cancel_btn = QPushButton("─░ptal")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Kaydet butonu
        save_btn = QPushButton("­şÆ¥ Kaydet")
        save_btn.setDefault(True)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self._save_rules)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
    
    def _load_rules(self):
        """Mevcut kurallar─▒ y├╝kle"""
        rules = load_rules(self.base_dir, self.system_name)
        if rules:
            self.rules = rules
            rules_text = json.dumps(rules, ensure_ascii=False, indent=2)
            self.json_editor.setPlainText(rules_text)
        else:
            # Varsay─▒lan bo┼ş kural yap─▒s─▒
            default_rules = {
                "system": self.system_name,
                "rules": {}
            }
            self.rules = default_rules
            rules_text = json.dumps(default_rules, ensure_ascii=False, indent=2)
            self.json_editor.setPlainText(rules_text)
            QMessageBox.information(
                self,
                "Bilgi",
                "Hen├╝z kural y├╝klenmemi┼ş. Yeni kural olu┼şturabilirsiniz."
            )
    
    def _validate_json(self):
        """JSON format─▒n─▒ do─şrula"""
        text = self.json_editor.toPlainText()
        try:
            json.loads(text)
            QMessageBox.information(
                self,
                "Ba┼şar─▒l─▒",
                "JSON format─▒ ge├ğerli!"
            )
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "JSON Hatas─▒",
                f"JSON format─▒ ge├ğersiz:\n\n{str(e)}\n\n"
                "L├╝tfen JSON s├Âzdizimini d├╝zeltin."
            )
    
    def _validate_rules(self):
        """Kurallar─▒ do─şrula"""
        text = self.json_editor.toPlainText()
        
        # ├ûnce JSON format─▒n─▒ kontrol et
        try:
            rules = json.loads(text)
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "JSON Hatas─▒",
                f"JSON format─▒ ge├ğersiz:\n\n{str(e)}\n\n"
                "L├╝tfen ├Ânce JSON format─▒n─▒ d├╝zeltin."
            )
            return
        
        # Kural do─şrulama
        is_valid, issues = validate_rules(rules)
        report = format_validation_report(issues)
        
        # Sonu├ğlar─▒ g├Âster
        dialog = QDialog(self)
        dialog.setWindowTitle("Kural Do─şrulama Raporu")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout(dialog)
        
        # Ba┼şl─▒k
        if is_valid:
            title_label = QLabel("Ô£à Kurallar Ge├ğerli")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60; padding: 10px;")
        else:
            title_label = QLabel("ÔØî Kurallarda Hatalar Bulundu")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #e74c3c; padding: 10px;")
        layout.addWidget(title_label)
        
        # Rapor
        report_text = QTextEdit()
        report_text.setPlainText(report)
        report_text.setReadOnly(True)
        report_text.setFont(QFont("Consolas", 10))
        report_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: 1px solid #3c3f41;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(report_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(dialog.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.exec()
    
    def _save_rules(self):
        """D├╝zenlenen kurallar─▒ kaydet"""
        text = self.json_editor.toPlainText()
        
        # JSON do─şrulama
        try:
            rules = json.loads(text)
        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self,
                "JSON Hatas─▒",
                f"JSON format─▒ ge├ğersiz:\n\n{str(e)}\n\n"
                "L├╝tfen JSON s├Âzdizimini d├╝zeltin ve tekrar deneyin."
            )
            return
        
        # Sistem kontrol├╝
        if rules.get("system") != self.system_name:
            reply = QMessageBox.question(
                self,
                "Sistem Uyar─▒s─▒",
                f"Kural sistem ad─▒ '{rules.get('system')}' mevcut sistem '{self.system_name}' ile e┼şle┼şmiyor.\n\n"
                "Yine de kaydetmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Kurallar─▒ do─şrula
        is_valid, issues = validate_rules(rules)
        if issues:
            report = format_validation_report(issues)
            if not is_valid:
                # Kritik hatalar varsa kullan─▒c─▒ya sor
                reply = QMessageBox.question(
                    self,
                    "Kural Do─şrulama Hatas─▒",
                    f"Kurallarda kritik hatalar bulundu:\n\n{report[:300]}...\n\n"
                    "Yine de kaydetmek istiyor musunuz? (├ûnerilmez)",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            else:
                # Sadece uyar─▒lar varsa bilgi ver
                QMessageBox.information(
                    self,
                    "Kural Do─şrulama Uyar─▒lar─▒",
                    f"Kurallarda baz─▒ uyar─▒lar bulundu:\n\n{report[:300]}...\n\n"
                    "Kurallar kaydedilecek."
                )
        
        # Kurallar─▒ kaydet
        try:
            saved_path = save_rules(rules, self.base_dir, self.system_name)
            QMessageBox.information(
                self,
                "Ba┼şar─▒l─▒",
                f"Kurallar kaydedildi:\n{saved_path}\n\n"
                "De─şi┼şikliklerin etkili olmas─▒ i├ğin uygulamay─▒ yeniden ba┼şlatman─▒z gerekebilir."
            )
            self.rules = rules
            self.accept()
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Kurallar kaydedilemedi:\n{str(e)}"
            )


class RulePreviewDialog(QDialog):
    """Kural ├Ânizleme diyalo─şu"""
    
    def __init__(self, parent: QWidget, system_name: str, base_dir: Path):
        super().__init__(parent)
        self.system_name = system_name
        self.base_dir = base_dir
        self._init_ui()
        self._load_preview()
    
    def _init_ui(self):
        self.setWindowTitle(f"Kural ├ûnizleme - {self.system_name}")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)
        
        # Ba┼şl─▒k
        title_label = QLabel("­şôÜ Kural ├ûnizleme")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # ├ûnizleme metni
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setFont(QFont("Consolas", 10))
        self.preview_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: 1px solid #3c3f41;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(self.preview_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        # Yenile butonu
        refresh_btn = QPushButton("­şöä Yenile")
        refresh_btn.setToolTip("Kurallar─▒ yeniden y├╝kle")
        refresh_btn.clicked.connect(self._load_preview)
        button_layout.addWidget(refresh_btn)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _load_preview(self):
        """Kurallar─▒ y├╝kle ve ├Ânizle"""
        from utils.rule_storage import load_rules
        
        rules = load_rules(self.base_dir, self.system_name)
        preview_text = format_rule_preview(rules) if rules else "ÔØî Kural y├╝klenmemi┼ş."
        self.preview_text.setPlainText(preview_text)


class RuleVersionDialog(QDialog):
    """Kural versiyon y├Ânetimi diyalo─şu"""
    
    def __init__(self, parent: QWidget, system_name: str, base_dir: Path):
        super().__init__(parent)
        self.system_name = system_name
        self.base_dir = base_dir
        self._init_ui()
        self._load_versions()
    
    def _init_ui(self):
        self.setWindowTitle(f"Kural Versiyon Y├Ânetimi - {self.system_name}")
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        
        # Ba┼şl─▒k
        title_label = QLabel("­şôĞ Kural Versiyon Y├Ânetimi")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # Bilgi etiketi
        info_label = QLabel(
            "Kurallar─▒n─▒z─▒n versiyon ge├ğmi┼şi. Bir versiyonu geri y├╝kleyebilir veya silebilirsiniz."
        )
        info_label.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Versiyon listesi
        list_label = QLabel("Versiyonlar (en yeni ├Ânce):")
        list_label.setStyleSheet("font-weight: bold; padding: 5px;")
        layout.addWidget(list_label)
        
        self.version_list = QListWidget()
        self.version_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #3c3f41;
                border-radius: 4px;
                padding: 5px;
            }
        """)
        self.version_list.itemDoubleClicked.connect(self._show_version_details)
        layout.addWidget(self.version_list)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        # Yenile butonu
        refresh_btn = QPushButton("­şöä Yenile")
        refresh_btn.clicked.connect(self._load_versions)
        button_layout.addWidget(refresh_btn)
        
        # Detaylar butonu
        details_btn = QPushButton("­şôï Detaylar")
        details_btn.clicked.connect(self._show_selected_version_details)
        button_layout.addWidget(details_btn)
        
        button_layout.addStretch()
        
        # Geri y├╝kle butonu
        restore_btn = QPushButton("Ôå®´©Å Geri Y├╝kle")
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        restore_btn.clicked.connect(self._restore_selected_version)
        button_layout.addWidget(restore_btn)
        
        # Sil butonu
        delete_btn = QPushButton("­şùæ´©Å Sil")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                font-weight: bold;
                padding: 8px 20px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(self._delete_selected_version)
        button_layout.addWidget(delete_btn)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _load_versions(self):
        """Versiyon listesini y├╝kle"""
        self.version_list.clear()
        versions = load_versions_list(self.base_dir, self.system_name)
        
        if not versions:
            item = QListWidgetItem("Versiyon bulunamad─▒")
            item.setFlags(Qt.NoItemFlags)
            self.version_list.addItem(item)
            return
        
        for version_meta in versions:
            version_info = format_version_info(version_meta)
            item = QListWidgetItem(version_info)
            item.setData(Qt.UserRole, version_meta["version_id"])
            self.version_list.addItem(item)
    
    def _get_selected_version_id(self) -> Optional[str]:
        """Se├ğili versiyon ID'sini d├Ând├╝r"""
        current_item = self.version_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
    
    def _show_version_details(self, item: QListWidgetItem):
        """Versiyon detaylar─▒n─▒ g├Âster"""
        version_id = item.data(Qt.UserRole)
        if not version_id:
            return
        self._show_version_details_by_id(version_id)
    
    def _show_selected_version_details(self):
        """Se├ğili versiyonun detaylar─▒n─▒ g├Âster"""
        version_id = self._get_selected_version_id()
        if not version_id:
            QMessageBox.warning(self, "Uyar─▒", "L├╝tfen bir versiyon se├ğin.")
            return
        self._show_version_details_by_id(version_id)
    
    def _show_version_details_by_id(self, version_id: str):
        """Belirli bir versiyonun detaylar─▒n─▒ g├Âster"""
        version = load_version(self.base_dir, self.system_name, version_id)
        if not version:
            QMessageBox.warning(self, "Hata", "Versiyon y├╝klenemedi.")
            return
        
        # Detay diyalo─şu
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Versiyon Detaylar─▒ - {version_id}")
        dialog.setMinimumSize(600, 500)
        layout = QVBoxLayout(dialog)
        
        # Versiyon bilgisi
        info_text = f"Versiyon ID: {version.version_id}\n"
        info_text += f"Tarih: {version.timestamp}\n"
        info_text += f"A├ğ─▒klama: {version.description or '(A├ğ─▒klama yok)'}\n"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(info_label)
        
        # Kural ├Ânizleme
        preview_text = format_rule_preview(version.rules)
        preview_edit = QTextEdit()
        preview_edit.setPlainText(preview_text)
        preview_edit.setReadOnly(True)
        preview_edit.setFont(QFont("Consolas", 10))
        preview_edit.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #a9b7c6;
                border: 1px solid #3c3f41;
                border-radius: 4px;
                padding: 10px;
            }
        """)
        layout.addWidget(preview_edit)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(dialog.accept)
        layout.addWidget(close_btn)
        
        dialog.exec()
    
    def _restore_selected_version(self):
        """Se├ğili versiyonu geri y├╝kle"""
        version_id = self._get_selected_version_id()
        if not version_id:
            QMessageBox.warning(self, "Uyar─▒", "L├╝tfen bir versiyon se├ğin.")
            return
        
        reply = QMessageBox.question(
            self,
            "Versiyon Geri Y├╝kle",
            "Bu versiyonu geri y├╝klemek istedi─şinizden emin misiniz?\n\n"
            "Mevcut kurallar otomatik olarak yedeklenecektir.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if restore_version(self.base_dir, self.system_name, version_id):
                    QMessageBox.information(
                        self,
                        "Ba┼şar─▒l─▒",
                        "Versiyon geri y├╝klendi!\n\n"
                        "De─şi┼şikliklerin etkili olmas─▒ i├ğin uygulamay─▒ yeniden ba┼şlatman─▒z gerekebilir."
                    )
                    self._load_versions()
                else:
                    QMessageBox.warning(self, "Hata", "Versiyon geri y├╝klenemedi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Versiyon geri y├╝kleme hatas─▒:\n{str(e)}")
    
    def _delete_selected_version(self):
        """Se├ğili versiyonu sil"""
        version_id = self._get_selected_version_id()
        if not version_id:
            QMessageBox.warning(self, "Uyar─▒", "L├╝tfen bir versiyon se├ğin.")
            return
        
        reply = QMessageBox.question(
            self,
            "Versiyon Sil",
            "Bu versiyonu silmek istedi─şinizden emin misiniz?\n\n"
            "Bu i┼şlem geri al─▒namaz!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if delete_version(self.base_dir, self.system_name, version_id):
                    QMessageBox.information(self, "Ba┼şar─▒l─▒", "Versiyon silindi.")
                    self._load_versions()
                else:
                    QMessageBox.warning(self, "Hata", "Versiyon silinemedi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Versiyon silme hatas─▒:\n{str(e)}")


class CharacterIntroDialog(QDialog):
    def __init__(self, parent, classes):
        super().__init__(parent)
        self.setWindowTitle("Yeni Karakter")
        self.setModal(True)
        layout = QVBoxLayout(self)

        form = QFormLayout()
        self.name_edit = QLineEdit()
        self.name_edit.setPlaceholderText("Karakter ismi...")
        self.class_combo = QComboBox()
        self.class_combo.addItems(classes)

        form.addRow("─░sim:", self.name_edit)
        form.addRow("S─▒n─▒f:", self.class_combo)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Uyar─▒", "L├╝tfen karakter ismi girin.")
            return
        self.accept()

    def get_values(self):
        return self.name_edit.text().strip(), self.class_combo.currentText()


class DndPage(QWidget):
    SYSTEM_NAME = "DND5E"
    def __init__(self):
        super().__init__()
        self.data = self._load_dnd_data()
        self.current_character = None
        self.inventory_items = []
        self._rules_cache = None  # Kural cache
        self.current_character_image_data = None  # Resim verisi (base64)
        self.current_step = 0  # Mevcut ad─▒m indeksi
        self._current_race_bonus: dict[str, int] = {}  # Son uygulanan ─▒rk bonuslar─▒
        self.steps = [
            {"name": "─░sim ve S─▒n─▒f", "description": "Karakterinizin ismini ve s─▒n─▒f─▒n─▒ se├ğin"},
            {"name": "Irk", "description": "Karakterinizin ─▒rk─▒n─▒ se├ğin"},
            {"name": "Arka Plan", "description": "Karakterinizin arka plan─▒n─▒ se├ğin"},
            {"name": "Yetenek Puanlar─▒", "description": "Point-buy sistemi ile yetenek puanlar─▒n─▒z─▒ da─ş─▒t─▒n"},
            {"name": "S─▒n─▒f Becerileri", "description": "S─▒n─▒f─▒n─▒za ├Âzel becerileri se├ğin"},
            {"name": "B├╝y├╝ler", "description": "B├╝y├╝c├╝ s─▒n─▒flar i├ğin b├╝y├╝ se├ğimi"},
            {"name": "Feat'ler", "description": "─░ste─şe ba─şl─▒ feat'leri se├ğin"},
            {"name": "Ekipman", "description": "Ba┼şlang─▒├ğ ekipman─▒n─▒z─▒ se├ğin"},
            {"name": "Ki┼şilik", "description": "Karakterinizin ki┼şilik ve fiziksel ├Âzelliklerini belirleyin"},
            {"name": "├ûzet", "description": "Karakterinizin ├Âzetini g├Âr├╝nt├╝leyin ve tamamlay─▒n"}
        ]
        self._init_ui()

    def _load_dnd_data(self) -> dict:
        """D&D verisini y├╝kle - cache ile optimize edilmi┼ş"""
        if not hasattr(self.__class__, '_data_cache'):
            data_file = APP_BASE_DIR / "data" / "dnd_data.json"
            with open(data_file, 'r', encoding='utf-8') as f:
                self.__class__._data_cache = json.load(f)
        return self.__class__._data_cache

    def _load_logo(self) -> QPixmap:
        """Logoyu y├╝kle - k├╝├ğ├╝lt├╝lm├╝┼ş boyutta"""
        logo_path = APP_BASE_DIR / "Gemini_Generated_Image_c510m9c510m9c510.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            # Logoyu k├╝├ğ├╝lt (maksimum 150x150, aspect ratio korunarak)
            if not pixmap.isNull():
                scaled = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                return scaled
        return QPixmap()  # Bo┼ş pixmap d├Ând├╝r

    def _init_ui(self):
        # Ana layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)  # Spacing'i azalt
        
        # Header k─▒sm─▒ - Logo ve ba┼şl─▒k
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #34495e; border-radius: 10px; margin: 5px;")
        header_widget.setMaximumHeight(140)  # Header maksimum y├╝kseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Sol taraf i├ğin bo┼ş alan
        header_layout.addStretch()
        
        # Ba┼şl─▒k (logo kald─▒r─▒ld─▒)
        title_label = QLabel("Diyargezer - D&D 5e Karakter Olu┼şturucu")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)  # Uzun metinler i├ğin kelime kayd─▒rma
        header_layout.addWidget(title_label)
        
        # Sa─ş taraf i├ğin bo┼ş alan
        header_layout.addStretch()
        
        layout.addWidget(header_widget)
        
        # Toolbar ekle
        toolbar_widget = self._build_toolbar()
        toolbar_widget.setMaximumHeight(40)  # Toolbar y├╝ksekli─şini s─▒n─▒rla
        layout.addWidget(toolbar_widget)
        
        # Tab widget olu┼ştur
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tab_widget, 1)  # Stretch factor = 1 (kalan alan─▒ kapla)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                margin-top: -2px;
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34495e, stop: 1 #2c3e50);
                color: #ecf0f1;
                padding: 12px 24px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
                border: 1px solid #34495e;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-bottom: 2px solid #3498db;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5dade2, stop: 1 #3498db);
            }
            QTabBar::tab:!selected {
                margin-top: 3px;
            }
        """)
        layout.addWidget(self.tab_widget, 1)  # Stretch factor = 1 (kalan alan─▒ kapla)
        
        # Karakter Olu┼şturma sekmesi
        self.character_tab = QWidget()
        self.character_layout = QVBoxLayout(self.character_tab)
        self.character_layout.setContentsMargins(0, 0, 0, 0)  # Margin'leri kald─▒r
        self.character_layout.setSpacing(0)  # Spacing'i kald─▒r
        self.tab_widget.addTab(self.character_tab, "­şÄ¡ Karakter")
        
        # B├╝y├╝ y├Ânetimi sekmesi
        self.spells_tab = QWidget()
        self.spells_layout = QVBoxLayout(self.spells_tab)
        self.spells_tab_index = self.tab_widget.addTab(self.spells_tab, "­şö« B├╝y├╝ler")
        
        # Seviye atlama sekmesi
        self.levelup_tab = QWidget()
        self.levelup_layout = QVBoxLayout(self.levelup_tab)
        self.levelup_tab_index = self.tab_widget.addTab(self.levelup_tab, "­şôê Level Up")
        
        # Envanter sekmesi
        self.inventory_tab = QWidget()
        self.inventory_layout = QVBoxLayout(self.inventory_tab)
        self.inventory_tab_index = self.tab_widget.addTab(self.inventory_tab, "­şÄÆ Envanter")
        
        # Dice Roller sekmesi
        self.dice_tab = QWidget()
        self.dice_layout = QVBoxLayout(self.dice_tab)
        self._init_dice_ui()
        self.dice_tab_index = self.tab_widget.addTab(self.dice_tab, "­şÄ▓ Dice")
        
        # Geli┼şmi┼ş sekmesi (opsiyonel ├Âzellikler)
        self.advanced_tab = QWidget()
        self.advanced_layout = QVBoxLayout(self.advanced_tab)
        self._init_advanced_ui()
        self.advanced_tab_index = self.tab_widget.addTab(self.advanced_tab, "ÔÜÖ´©Å Geli┼şmi┼ş")
        
        # Ba┼şlang─▒├ğta sadece Karakter sekmesi g├Âr├╝n├╝r olsun
        self.tab_widget.setTabVisible(self.spells_tab_index, False)
        self.tab_widget.setTabVisible(self.levelup_tab_index, False)
        self.tab_widget.setTabVisible(self.inventory_tab_index, False)
        self.tab_widget.setTabVisible(self.dice_tab_index, False)
        self.tab_widget.setTabVisible(self.advanced_tab_index, False)
        
        # Karakter olu┼şturma UI's─▒n─▒ olu┼ştur
        self._init_character_ui()
        
        # B├╝y├╝ y├Ânetimi UI's─▒n─▒ olu┼ştur
        self._init_spells_ui()
        
        # Seviye atlama UI's─▒n─▒ olu┼ştur
        self._init_levelup_ui()
        
        # Envanter UI's─▒n─▒ olu┼ştur
        self._init_inventory_ui()

        # Ba┼şlang─▒├ğta b├╝y├╝ sekmesi durumunu g├╝ncelle
        self._update_spell_tab_visibility()

    def _build_toolbar(self) -> QWidget:
        """Toolbar olu┼ştur"""
        widget = QWidget()
        bar = QHBoxLayout(widget)
        bar.setContentsMargins(0, 0, 0, 0)

        new_btn = QPushButton("Yeni Karakter")
        new_btn.setIcon(QIcon.fromTheme("document-new"))
        new_btn.clicked.connect(self._start_new_character)

        load_btn = QPushButton("Karakter Y├╝kle")
        load_btn.setIcon(QIcon.fromTheme("document-open"))
        load_btn.clicked.connect(self._load_existing_character)
        
        browse_btn = QPushButton("­şôï Karakterleri Listele")
        browse_btn.setToolTip("T├╝m karakterleri g├Âr├╝nt├╝le, ara ve filtrele")
        browse_btn.clicked.connect(self._browse_characters)
        
        template_btn = QPushButton("­şôØ ┼Şablonlar")
        template_btn.setToolTip("Karakter ┼şablonlar─▒n─▒ y├Ânet")
        template_btn.clicked.connect(self._manage_templates)
        
        version_btn = QPushButton("­şô£ Versiyonlar")
        version_btn.setToolTip("Karakter versiyon ge├ğmi┼şini g├Âr├╝nt├╝le ve y├Ânet")
        version_btn.clicked.connect(self._manage_versions)

        save_btn = QPushButton("Kaydet")
        save_btn.setIcon(QIcon.fromTheme("document-save"))
        save_btn.clicked.connect(self._manual_save_character)

        pdf_btn = QPushButton("PDF Export")
        pdf_btn.clicked.connect(self._export_to_pdf_from_toolbar)
        pdf_btn.setToolTip("Karakteri PDF olarak d─▒┼şa aktar")

        compare_btn = QPushButton("ÔÜû´©Å Kar┼ş─▒la┼şt─▒r")
        compare_btn.setToolTip("─░ki karakteri kar┼ş─▒la┼şt─▒r")
        compare_btn.clicked.connect(self._compare_characters)

        bar.addWidget(new_btn)
        bar.addWidget(load_btn)
        bar.addWidget(browse_btn)
        bar.addWidget(template_btn)
        bar.addWidget(version_btn)
        bar.addWidget(compare_btn)
        bar.addWidget(save_btn)
        bar.addWidget(pdf_btn)
        bar.addStretch()

        return widget

    def _compare_characters(self):
        """Karakter kar┼ş─▒la┼şt─▒rma diyalo─şunu a├ğ"""
        dialog = CharacterComparisonDialog(self, self.SYSTEM_NAME)
        dialog.exec()

    def _start_new_character(self):
        """Yeni karakter yaratmaya ba┼şla - ilk ├Ânce isim sor"""
        classes = sorted(self.data.get("classes", {}).keys())
        if not classes:
            QMessageBox.warning(self, "Uyar─▒", "Herhangi bir s─▒n─▒f verisi bulunamad─▒.")
            return
        
        dialog = CharacterIntroDialog(self, classes)
        if dialog.exec() != QDialog.Accepted:
            return
        
        character_name, class_name = dialog.get_values()
        if not character_name:
            return
        
        # Karakter verisi olu┼ştur
        self.current_character = {
            "system": self.SYSTEM_NAME,
            "name": character_name,
            "race": "",
            "class": class_name,
            "background": "",
            "level": 1,
            "abilities": {},
            "skills": {},
            "equipment": [],
            "spells": {},
            "feats": [],
            "languages": [],
            "personality": {},
            "physical": {},
            "appearance": {}
        }
        
        # Karakter formunu g├╝ncelle
        self._load_character_to_gui(self.current_character)
        
        # Ad─▒m widget'lar─▒n─▒ g├╝ncelle (karakter bilgilerini y├╝kle)
        if hasattr(self, '_populate_step_widgets'):
            self._populate_step_widgets()
        
        # Karakter sayfalar─▒na ge├ğ
        self.tab_widget.setCurrentIndex(0)
        
        self.current_character_file = str(_ensure_characters_dir() / f"{character_name}_karakter.json")
        self._save_character_to_file()

        # B├╝y├╝ sekmesi g├Âr├╝n├╝rl├╝─ş├╝n├╝ g├╝ncelle
        self._update_spell_tab_visibility()
        
        # T├╝m sekmeleri g├Âr├╝n├╝r yap (karakter olu┼şturuldu─şu i├ğin)
        self._show_all_tabs()

        # Level up sekmesinde bu karakteri otomatik se├ğ
        self._focus_current_character_in_levelup()
        
        # ─░lk ad─▒ma git (─░sim ve S─▒n─▒f ad─▒m─▒ zaten tamamland─▒, Irk ad─▒m─▒na ge├ğ)
        if hasattr(self, 'step_stack'):
            self._go_to_step(1)  # Irk ad─▒m─▒na ge├ğ
        
        QMessageBox.information(self, "Ba┼şar─▒l─▒", f"'{character_name}' karakteri olu┼şturuldu!\nArt─▒k karakterinizi ├Âzelle┼ştirebilirsiniz.")

    def _focus_current_character_in_levelup(self):
        """Level Up sekmesinde mevcut karakteri otomatik se├ğ"""
        try:
            if not hasattr(self, 'levelup_character_combo'):
                return
            if not getattr(self, "current_character_file", None):
                return

            # Listeyi yenile (diskteki son durumu al)
            self._refresh_levelup_character_list()

            # Combo i├ğinde current_character_file'a kar┼ş─▒l─▒k gelen girdiyi bul
            target_path = str(self.current_character_file)
            for i in range(self.levelup_character_combo.count()):
                data = self.levelup_character_combo.itemData(i)
                if data and str(data) == target_path:
                    self.levelup_character_combo.setCurrentIndex(i)
                    break
        except Exception as e:
            print(f"Level up karakter oda─ş─▒ ayarlan─▒rken hata: {e}")

    def _save_character_to_file(self, change_note: str = ""):
        """Mevcut karakteri dosyaya kaydet ve versiyon olu┼ştur"""
        if not hasattr(self, 'current_character') or not self.current_character:
            return
        
        if not getattr(self, "current_character_file", None):
            return

        try:
            path = Path(self.current_character_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Mevcut dosyay─▒ kaydet (varsa)
            old_character = None
            if path.exists():
                try:
                    with path.open("r", encoding="utf-8") as f:
                        old_character = json.load(f)
                except Exception:
                    pass
            
            # Yeni versiyonu kaydet (de─şi┼şiklik varsa)
            if old_character:
                save_character_version(
                    old_character,
                    APP_BASE_DIR,
                    self.current_character_file,
                    change_note
                )
            
            # Karakteri kaydet
            with path.open("w", encoding="utf-8") as f:
                json.dump(self.current_character, f, ensure_ascii=False, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter kaydedilemedi:\n{str(e)}")

    def _auto_save_character(self):
        """Her de─şi┼şiklikte otomatik kaydet"""
        if hasattr(self, 'current_character') and self.current_character:
            self.current_character["system"] = self.SYSTEM_NAME
            # Mevcut se├ğimleri karakter verisine g├╝ncelle
            self.current_character["race"] = self.race_cb.currentText()
            self.current_character["class"] = self.class_cb.currentText()
            self.current_character["background"] = self.bg_cb.currentText()
            
            # Yetenek puanlar─▒n─▒ g├╝ncelle
            for ability, spin in self.ability_spins.items():
                self.current_character["abilities"][ability] = spin.value()
            
            # Resmi g├╝ncelle (varsa)
            if hasattr(self, 'current_character_image_data'):
                if self.current_character_image_data:
                    self.current_character["image"] = self.current_character_image_data
                elif "image" in self.current_character:
                    del self.current_character["image"]
            
            # Dosyaya kaydet
            self._save_character_to_file()
            
            # Ad─▒m listesini g├╝ncelle
            if hasattr(self, '_update_step_list'):
                self._update_step_list()

    def _manual_save_character(self):
        """Karakteri se├ğilen bir dosyaya kaydet"""
        if not hasattr(self, "current_character") or not self.current_character:
            QMessageBox.warning(self, "Uyar─▒", "├ûnce bir karakter olu┼şturman─▒z gerekiyor.")
            return
        self._auto_save_character()
        default_name = self.current_character.get("name") or "dnd_karakter"
        _save_character_via_dialog(
            self,
            self.current_character,
            "D&D Karakterini Kaydet",
            default_name,
        )

    def _load_existing_character(self):
        """Haz─▒r karakter dosyas─▒n─▒ y├╝kle"""
        data, path = _load_character_via_dialog(self, "D&D Karakteri Y├╝kle", self.SYSTEM_NAME)
        if not data:
            return
        self._load_character_to_gui(data)
        self.current_character = data
        self.current_character_file = path
        
        # Son a├ğ─▒lanlara ekle
        if path:
            add_recent_character(APP_BASE_DIR, path, data.get("name", ""))
        
        # T├╝m sekmeleri g├Âr├╝n├╝r yap
        self._show_all_tabs()

        # Level up sekmesinde bu karakteri otomatik se├ğ
        self._focus_current_character_in_levelup()
        
        QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{data.get('name', 'Karakter')} y├╝klendi!")

    def _browse_characters(self):
        """Karakter listesi diyalo─şunu a├ğ ve D&D karakteri se├ğ"""
        dialog = CharacterListDialog(self, None)
        dialog.setWindowTitle("Karakter Listesi - T├╝m Sistemler")
        if dialog.exec() != QDialog.Accepted:
            return

        data, path = dialog.get_selected_character()
        if not data:
            return

        system = data.get("system")
        if system == self.SYSTEM_NAME:
            self._load_character_to_gui(data)
            self.current_character = data
            self.current_character_file = path
            if path:
                add_recent_character(APP_BASE_DIR, path, data.get("name", ""))
            # T├╝m sekmeleri g├Âr├╝n├╝r yap
            self._show_all_tabs()

            # Level up sekmesinde bu karakteri otomatik se├ğ
            self._focus_current_character_in_levelup()

            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{data.get('name', 'Karakter')} y├╝klendi!")
        else:
            QMessageBox.information(
                self,
                "Bilgi",
                f"Bu karakter {system} sistemine ait.\nL├╝tfen ilgili sekmeden y├╝kleyin."
            )

    def _manage_templates(self):
        """┼Şablon y├Ânetim diyalo─şunu a├ğ"""
        character, character_name = _select_template_character(self, self.SYSTEM_NAME)
        if not character:
            return

        self._load_character_to_gui(character)
        safe_name = "".join(c for c in character_name if c.isalnum() or c in (" ", "-", "_")).strip()
        if not safe_name:
            safe_name = "dnd_karakter"
        safe_name = safe_name.replace(" ", "_")
        self.current_character_file = str(_ensure_characters_dir() / f"{safe_name}_karakter.json")
        self._save_character_to_file("┼Şablondan olu┼şturuldu")

        # Sekmeleri g├Âster ve level up sekmesinde bu karakteri se├ğ
        self._show_all_tabs()
        self._focus_current_character_in_levelup()

        QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{character_name} ┼şablondan olu┼şturuldu.")

    def _export_to_pdf_from_toolbar(self):
        """Toolbar'dan PDF export"""
        if not hasattr(self, "current_character") or not self.current_character:
            QMessageBox.warning(self, "Uyar─▒", "├ûnce bir karakter olu┼şturman─▒z gerekiyor.")
            return
        self._export_to_pdf(self.current_character)

    def _load_character_to_gui(self, character):
        """Karakteri GUI'ye y├╝kle"""
        try:
            # Mevcut karakteri g├╝ncelle
            self.current_character = character
            
            # ─░sim alan─▒n─▒ g├╝ncelle
            if hasattr(self, 'character_name_edit') and self.character_name_edit:
                self.character_name_edit.setText(character.get("name", ""))
                self.character_name_edit.setReadOnly(True)
            
            # Race se├ğimi
            race = character.get("race", "")
            if race and hasattr(self, 'race_cb') and self.race_cb:
                index = self.race_cb.findText(race)
                if index >= 0:
                    self.race_cb.setCurrentIndex(index)
            
            # Class se├ğimi
            char_class = character.get("class", "")
            if char_class and hasattr(self, 'class_cb') and self.class_cb:
                index = self.class_cb.findText(char_class)
                if index >= 0:
                    self.class_cb.setCurrentIndex(index)
            
            # Background se├ğimi
            background = character.get("background", "")
            if background and hasattr(self, 'bg_cb') and self.bg_cb:
                index = self.bg_cb.findText(background)
                if index >= 0:
                    self.bg_cb.setCurrentIndex(index)
            
            # Yetenek puanlar─▒
            abilities = character.get("abilities", {})
            if hasattr(self, 'ability_spins'):
                for ability, score in abilities.items():
                    if ability in self.ability_spins:
                        self.ability_spins[ability].setValue(score)
            
            # S─▒n─▒f se├ğimlerini g├╝ncelle (widget'lar varsa)
            if hasattr(self, '_refresh_class_options'):
                self._refresh_class_options()
            if hasattr(self, '_refresh_class_features'):
                self._refresh_class_features()
            if hasattr(self, '_refresh_feats'):
                self._refresh_feats()
            
            # Karakter olu┼şturma sekmesine ge├ğ
            self.tab_widget.setCurrentIndex(0)
            
            # B├╝y├╝ listesini g├╝ncelle
            self._update_spells_list()
            
            # Envanteri yenile
            if hasattr(self, '_load_current_character_inventory'):
                self._load_current_character_inventory()
            
            # Resmi y├╝kle
            self._load_character_image_to_gui(character)

            self._update_spell_tab_visibility()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter GUI'ye y├╝klenemedi:\n{str(e)}")

    def _init_character_ui(self):
        """Karakter olu┼şturma UI's─▒n─▒ olu┼ştur - Ad─▒m bazl─▒ yap─▒"""
        # Ana splitter olu┼ştur (sol: ad─▒m listesi, orta: i├ğerik, sa─ş: a├ğ─▒klama)
        main_splitter = QtWidgets.QSplitter(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # T├╝m alan─▒ kapla
        
        # Sol panel: Ad─▒m listesi
        self.step_list_widget = QWidget()
        step_list_layout = QVBoxLayout(self.step_list_widget)
        step_list_layout.setContentsMargins(10, 10, 10, 10)
        
        step_list_title = QLabel("Ad─▒mlar")
        step_list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        step_list_layout.addWidget(step_list_title)
        
        # Ad─▒m listesi
        self.step_list = QListWidget()
        self.step_list.setMaximumWidth(200)
        self.step_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #dee2e6;
                border-radius: 5px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #dee2e6;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
            QListWidget::item:hover {
                background-color: #e9ecef;
            }
        """)
        self.step_items = []  # Ad─▒m item'lar─▒n─▒ sakla
        for i, step in enumerate(self.steps):
            item_text = f"{i+1}. {step['name']}"
            item = QListWidgetItem(item_text)
            self.step_list.addItem(item)
            self.step_items.append(item)
        self.step_list.setCurrentRow(0)
        self.step_list.currentRowChanged.connect(self._on_step_changed)
        step_list_layout.addWidget(self.step_list)
        
        # Orta panel: Ad─▒m i├ğeri─şi (StackedWidget)
        self.step_stack = QStackedWidget()
        self.step_widgets = []  # Her ad─▒m i├ğin widget'lar─▒ sakla
        
        # Her ad─▒m i├ğin widget olu┼ştur
        for i, step in enumerate(self.steps):
            step_widget = QWidget()
            step_layout = QVBoxLayout(step_widget)
            step_layout.setContentsMargins(10, 10, 10, 10)
            
            # Scroll area i├ğinde
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(15)
            
            # Ad─▒m ba┼şl─▒─ş─▒
            step_title = QLabel(step['name'])
            step_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
            content_layout.addWidget(step_title)
            
            # Ad─▒m a├ğ─▒klamas─▒
            step_desc = QLabel(step['description'])
            step_desc.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 15px;")
            step_desc.setWordWrap(True)
            content_layout.addWidget(step_desc)
            
            # Placeholder - ger├ğek i├ğerik _build_step_widgets'te olu┼şturulacak
            placeholder = QLabel(f"{step['name']} i├ğeri─şi buraya gelecek")
            placeholder.setStyleSheet("color: #95a5a6; font-style: italic;")
            content_layout.addWidget(placeholder)
            content_layout.addStretch()
            
            scroll.setWidget(content_widget)
            step_layout.addWidget(scroll)
            
            # ─░leri/Geri butonlar─▒
            nav_layout = QHBoxLayout()
            back_btn = QPushButton("ÔåÉ Geri")
            back_btn.setEnabled(i > 0)
            back_btn.clicked.connect(lambda checked, idx=i: self._go_to_step(idx - 1))
            next_btn = QPushButton("─░leri ÔåÆ")
            if i == len(self.steps) - 1:
                next_btn.setText("Tamamla")
                next_btn.clicked.connect(self._complete_character)
            else:
                next_btn.clicked.connect(lambda checked, idx=i: self._go_to_step(idx + 1))
            
            nav_layout.addWidget(back_btn)
            nav_layout.addStretch()
            nav_layout.addWidget(next_btn)
            step_layout.addLayout(nav_layout)
            
            self.step_stack.addWidget(step_widget)
            self.step_widgets.append(content_widget)
        
        # Sa─ş panel: A├ğ─▒klama paneli
        self.info_panel = QWidget()
        info_layout = QVBoxLayout(self.info_panel)
        
        # A├ğ─▒klama paneli ba┼şl─▒─ş─▒
        info_title = QLabel("Se├ğim A├ğ─▒klamas─▒")
        info_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ecf0f1; margin: 10px;")
        info_title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_title)
        
        # A├ğ─▒klama metni
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        self.info_text.setStyleSheet("""
            QTextEdit {
                background-color: #2c3e50;
                color: #ecf0f1;
                border: 2px solid #34495e;
                border-radius: 5px;
                padding: 10px;
                font-size: 14px;
                line-height: 1.4;
            }
        """)
        self.info_text.setPlaceholderText("Bir se├ğim yap─▒n, a├ğ─▒klamas─▒ burada g├Âr├╝necek...")
        info_layout.addWidget(self.info_text)
        
        # Splitter'a panelleri ekle
        main_splitter.addWidget(self.step_list_widget)
        main_splitter.addWidget(self.step_stack)
        main_splitter.addWidget(self.info_panel)
        
        # Splitter oranlar─▒ (sol: 200px, orta: esnek, sa─ş: 300px)
        main_splitter.setSizes([200, 600, 300])
        main_splitter.setChildrenCollapsible(False)
        
        # G├Âr├╝nmez bir container olu┼ştur (widget'lar─▒ olu┼şturmak i├ğin)
        self.character_form_container = QWidget()
        self.character_form_container.setVisible(False)
        self.character_form_container.setMaximumSize(0, 0)
        
        # Character form widget'lar─▒n─▒ olu┼ştur (eski yap─▒y─▒ koruyoruz ama ad─▒m bazl─▒ g├Âsteriyoruz)
        self._build_character_form_widgets()
        
        # Ad─▒m widget'lar─▒n─▒ doldur
        self._populate_step_widgets()
        
        # Character tab'a splitter'─▒ ekle
        toolbar = self._build_character_toolbar()
        toolbar.setMaximumHeight(40)  # Toolbar y├╝ksekli─şini s─▒n─▒rla
        self.character_layout.addWidget(toolbar)
        self.character_layout.addWidget(main_splitter, 1)  # Stretch factor = 1 (t├╝m kalan alan─▒ kapla)
        
        # ─░lk ad─▒m─▒ g├Âster
        self._go_to_step(0)

    def _build_character_toolbar(self) -> QWidget:
        widget = QWidget()
        widget.setMaximumHeight(35)  # Toolbar y├╝ksekli─şini s─▒n─▒rla
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)  # Margin'leri azalt
        layout.setSpacing(5)
        save_btn = QPushButton("­şÆ¥ Farkl─▒ Kaydet")
        save_btn.setToolTip("Karakteri farkl─▒ bir JSON dosyas─▒na kaydet")
        save_btn.setMaximumHeight(30)  # Buton y├╝ksekli─şini s─▒n─▒rla
        save_btn.clicked.connect(self._manual_save_character)
        layout.addWidget(save_btn)
        layout.addStretch()
        return widget
    
    def _on_step_changed(self, new_index: int):
        """Ad─▒m listesinden ad─▒m de─şi┼şti─şinde ├ğa─şr─▒l─▒r"""
        if 0 <= new_index < len(self.steps):
            self._go_to_step(new_index)
    
    def _go_to_step(self, step_index: int):
        """Belirtilen ad─▒ma git"""
        if step_index < 0 or step_index >= len(self.steps):
            return
        
        # Widget'lar─▒n varl─▒─ş─▒n─▒ kontrol et
        if not hasattr(self, 'step_stack') or not hasattr(self, 'step_list') or not hasattr(self, 'info_text'):
            return
        
        # Validasyon yap (e─şer ileri gidiyorsak)
        if step_index > self.current_step:
            if not self._validate_current_step():
                return
        
        self.current_step = step_index
        
        # G├╝venli widget eri┼şimi
        try:
            if self.step_stack.count() > step_index:
                self.step_stack.setCurrentIndex(step_index)
            if self.step_list.count() > step_index:
                self.step_list.setCurrentRow(step_index)
            
            # Ad─▒m a├ğ─▒klamas─▒n─▒ g├╝ncelle
            step = self.steps[step_index]
            self.info_text.setText(f"<b>{step['name']}</b><br><br>{step['description']}")
        except (AttributeError, RuntimeError) as e:
            # Widget hen├╝z haz─▒r de─şil veya silinmi┼ş
            return
        
        # ├ûzet ve B├╝y├╝ler ad─▒mlar─▒na gelindi─şinde ilgili g├╝ncellemeleri yap
        try:
            if step['name'] == "├ûzet":
                self._update_summary_step()
            
            # B├╝y├╝ler ad─▒m─▒n─▒n g├Âr├╝n├╝rl├╝─ş├╝n├╝ kontrol et
            if step['name'] == "B├╝y├╝ler":
                self._update_spells_step_visibility()
        except (AttributeError, RuntimeError):
            pass
        
        # S─▒n─▒f Becerileri ad─▒m─▒na gelindi─şinde becerileri yenile
        if step['name'] == "S─▒n─▒f Becerileri":
            try:
                # S─▒n─▒f bilgisini current_character'dan al ve class_cb'yi ayarla
                if hasattr(self, 'current_character') and self.current_character:
                    class_name = self.current_character.get('class', '')
                    if class_name and hasattr(self, 'class_cb'):
                        idx = self.class_cb.findText(class_name)
                        if idx >= 0:
                            self.class_cb.setCurrentIndex(idx)
                        else:
                            # class_cb listesinde yoksa, yine de becerileri yenilemek i├ğin ad─▒ aktar
                            self.class_cb.addItem(class_name)
                            self.class_cb.setCurrentText(class_name)
                # Becerileri yenile
                if hasattr(self, 'class_cb') and self.class_cb.currentText():
                    self._refresh_class_options()
            except (AttributeError, RuntimeError):
                pass
        
        # ─░leri/Geri butonlar─▒n─▒ g├╝ncelle
        try:
            self._update_navigation_buttons()
        except (AttributeError, RuntimeError):
            pass
        
        # Ad─▒m listesini g├╝ncelle (tamamlanan ad─▒mlar─▒ i┼şaretle)
        try:
            self._update_step_list()
        except (AttributeError, RuntimeError):
            pass
    
    def _update_summary_step(self):
        """├ûzet ad─▒m─▒ndaki i├ğeri─şi g├╝ncelle"""
        if not hasattr(self, 'step_widgets') or len(self.step_widgets) < 10:
            return
        
        summary_layout = self.step_widgets[9].layout()
        if not summary_layout:
            return
        
        # ├ûzet widget'─▒n─▒ bul
        summary_text = None
        for i in range(summary_layout.count()):
            item = summary_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QGroupBox) and widget.title() == "Karakter ├ûzeti":
                    inner_layout = widget.layout()
                    if inner_layout and inner_layout.count() > 0:
                        text_item = inner_layout.itemAt(0)
                        if text_item and text_item.widget() and isinstance(text_item.widget(), QTextEdit):
                            summary_text = text_item.widget()
                            break
        
        if summary_text and hasattr(self, 'current_character') and self.current_character:
            char = self.current_character
            summary_html = f"""
            <h2 style='color: #2c3e50;'>{char.get('name', '─░simsiz')}</h2>
            <hr>
            <p><b>S─▒n─▒f:</b> {char.get('class', 'Se├ğilmedi')}</p>
            <p><b>Irk:</b> {char.get('race', 'Se├ğilmedi')}</p>
            <p><b>Arka Plan:</b> {char.get('background', 'Se├ğilmedi')}</p>
            <p><b>Seviye:</b> {char.get('level', 1)}</p>
            """
            
            # Yetenek puanlar─▒
            if hasattr(self, 'ability_spins'):
                summary_html += "<h3 style='color: #3498db; margin-top: 15px;'>Yetenek Puanlar─▒:</h3><ul>"
                for ability in self.abilities:
                    value = self.ability_spins[ability].value()
                    modifier = (value - 10) // 2
                    mod_str = f"+{modifier}" if modifier >= 0 else str(modifier)
                    summary_html += f"<li><b>{ability}:</b> {value} ({mod_str})</li>"
                summary_html += "</ul>"
            
            # Beceriler
            if char.get('skills'):
                summary_html += "<h3 style='color: #3498db; margin-top: 15px;'>Beceriler:</h3><ul>"
                for skill, prof in char['skills'].items():
                    prof_text = "Ô£ô Uzman" if prof else "Normal"
                    summary_html += f"<li>{skill}: {prof_text}</li>"
                summary_html += "</ul>"
            
            # B├╝y├╝ler
            if char.get('spells'):
                summary_html += "<h3 style='color: #3498db; margin-top: 15px;'>B├╝y├╝ler:</h3><ul>"
                for level, spells in char['spells'].items():
                    if spells:
                        summary_html += f"<li><b>Seviye {level}:</b> {', '.join(spells)}</li>"
                summary_html += "</ul>"
            
            # Feat'ler
            if char.get('feats'):
                summary_html += f"<h3 style='color: #3498db; margin-top: 15px;'>Feat'ler:</h3><ul>"
                for feat in char['feats']:
                    summary_html += f"<li>{feat}</li>"
                summary_html += "</ul>"
            
            # Ekipman
            if char.get('equipment'):
                summary_html += f"<h3 style='color: #3498db; margin-top: 15px;'>Ekipman:</h3><ul>"
                for item in char['equipment']:
                    summary_html += f"<li>{item}</li>"
                summary_html += "</ul>"
            
            summary_text.setHtml(summary_html)
    
    def _update_spells_step_visibility(self):
        """B├╝y├╝ler ad─▒m─▒n─▒n g├Âr├╝n├╝rl├╝─ş├╝n├╝ kontrol et"""
        if not hasattr(self, 'current_character') or not self.current_character:
            return
        
        class_name = self.current_character.get('class', '')
        if not class_name:
            return
        
        # S─▒n─▒f─▒n b├╝y├╝ kullan─▒p kullanmad─▒─ş─▒n─▒ kontrol et
        class_data = self.data.get('classes', {}).get(class_name, {})
        is_spellcaster = class_data.get('spellcasting', False) or class_name.lower() in ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard', 'ranger', 'paladin']
        
        # B├╝y├╝ler ad─▒m─▒n─▒n widget'─▒n─▒ bul ve g├╝ncelle
        spells_step_index = None
        for i, step in enumerate(self.steps):
            if step['name'] == "B├╝y├╝ler":
                spells_step_index = i
                break
        
        if spells_step_index is not None and spells_step_index < len(self.step_widgets):
            spells_layout = self.step_widgets[spells_step_index].layout()
            if spells_layout:
                # Placeholder'─▒ kontrol et
                for i in range(spells_layout.count()):
                    item = spells_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        if isinstance(widget, QLabel) and "Bu s─▒n─▒f b├╝y├╝ kullanmaz" in widget.text():
                            # B├╝y├╝ kullan─▒yorsa placeholder'─▒ gizle
                            widget.setVisible(not is_spellcaster)
                        elif isinstance(widget, QGroupBox) and widget.title() == "B├╝y├╝ Se├ğimi":
                            # B├╝y├╝ kullanm─▒yorsa widget'─▒ gizle
                            widget.setVisible(is_spellcaster)
    
    def _validate_current_step(self) -> bool:
        """Mevcut ad─▒m─▒n ge├ğerli olup olmad─▒─ş─▒n─▒ kontrol et"""
        step = self.steps[self.current_step]
        
        if step['name'] == "─░sim ve S─▒n─▒f":
            # Karakter olu┼şturulmu┼ş mu kontrol et
            if not hasattr(self, 'current_character') or not self.current_character:
                # E─şer karakter yoksa, karakter olu┼şturma diyalo─şunu a├ğ
                self._start_new_character()
                return False
            # ─░sim ve s─▒n─▒f kontrol├╝
            if not self.current_character.get('name') or not self.current_character.get('class'):
                # E─şer isim veya s─▒n─▒f yoksa, karakter olu┼şturma diyalo─şunu a├ğ
                self._start_new_character()
                return False
            # Karakter olu┼şturulmu┼ş ve isim/s─▒n─▒f var, ge├ğerli
            return True
        elif step['name'] == "Irk":
            if not self.current_character or not self.current_character.get('race'):
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen bir ─▒rk se├ğin.")
                return False
        elif step['name'] == "Arka Plan":
            if not self.current_character or not self.current_character.get('background'):
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen bir arka plan se├ğin.")
                return False
        elif step['name'] == "Yetenek Puanlar─▒":
            # Point-buy kontrol├╝
            if hasattr(self, 'ability_spins'):
                total_points = sum(self.ability_spins[ability].value() - 8 for ability in self.abilities)
                if total_points > 27:
                    QMessageBox.warning(self, "Uyar─▒", "Toplam point-buy puan─▒ 27'yi ge├ğemez!")
                    return False
        elif step['name'] == "S─▒n─▒f Becerileri":
            # S─▒n─▒f becerileri se├ğim kontrol├╝ (opsiyonel - s─▒n─▒fa g├Âre de─şi┼şir)
            if hasattr(self, 'wiz_skills') and hasattr(self, 'current_character'):
                class_name = self.current_character.get('class', '')
                if class_name:
                    class_data = self.data.get('classes', {}).get(class_name, {})
                    skill_choices = class_data.get('skill_choices', 0)
                    selected_count = len(self.wiz_skills.selectedItems())
                    if skill_choices > 0 and selected_count < skill_choices:
                        QMessageBox.warning(self, "Uyar─▒", f"L├╝tfen {skill_choices} beceri se├ğin.")
                        return False
        elif step['name'] == "B├╝y├╝ler":
            # B├╝y├╝ler opsiyonel - sadece b├╝y├╝c├╝ s─▒n─▒flar i├ğin kontrol
            if hasattr(self, 'current_character') and self.current_character:
                class_name = self.current_character.get('class', '')
                class_data = self.data.get('classes', {}).get(class_name, {})
                is_spellcaster = class_data.get('spellcasting', False)
                if is_spellcaster and hasattr(self, 'wiz_cantrips'):
                    # Cantrip se├ğimi kontrol├╝
                    cantrip_choices = class_data.get('cantrip_choices', 0)
                    selected_cantrips = len(self.wiz_cantrips.selectedItems())
                    if cantrip_choices > 0 and selected_cantrips < cantrip_choices:
                        QMessageBox.warning(self, "Uyar─▒", f"L├╝tfen {cantrip_choices} cantrip se├ğin.")
                        return False
        
        return True
    
    def _update_step_list(self):
        """Ad─▒m listesini g├╝ncelle - tamamlanan ad─▒mlar─▒ i┼şaretle"""
        if not hasattr(self, 'step_items') or not self.step_items:
            return
        
        if len(self.step_items) != len(self.steps):
            return
        
        try:
            for i, item in enumerate(self.step_items):
                if i >= len(self.steps):
                    break
                step = self.steps[i]
                is_completed = self._is_step_completed(i)
                is_current = i == self.current_step
                
                # Ad─▒m metnini olu┼ştur
                if is_completed:
                    item_text = f"Ô£ô {i+1}. {step['name']}"
                    item.setForeground(QColor("#27ae60"))  # Ye┼şil renk
                else:
                    item_text = f"{i+1}. {step['name']}"
                    item.setForeground(QColor("#2c3e50"))  # Normal renk
                
                if is_current:
                    item.setForeground(QColor("#ffffff"))  # Se├ğili ad─▒m beyaz
                
                item.setText(item_text)
        except (AttributeError, RuntimeError, IndexError):
            # Widget hen├╝z haz─▒r de─şil veya silinmi┼ş
            return
    
    def _is_step_completed(self, step_index: int) -> bool:
        """Bir ad─▒m─▒n tamamlan─▒p tamamlanmad─▒─ş─▒n─▒ kontrol et"""
        if not hasattr(self, 'current_character') or not self.current_character:
            return False
        
        step = self.steps[step_index]
        char = self.current_character
        
        if step['name'] == "─░sim ve S─▒n─▒f":
            return bool(char.get('name') and char.get('class'))
        elif step['name'] == "Irk":
            return bool(char.get('race'))
        elif step['name'] == "Arka Plan":
            return bool(char.get('background'))
        elif step['name'] == "Yetenek Puanlar─▒":
            if hasattr(self, 'ability_spins'):
                # En az bir yetenek puan─▒ ayarlanm─▒┼şsa tamamlanm─▒┼ş say─▒l─▒r
                return any(spin.value() > 8 for spin in self.ability_spins.values())
            return False
        elif step['name'] == "S─▒n─▒f Becerileri":
            # Beceriler se├ğilmi┼şse tamamlanm─▒┼ş say─▒l─▒r (opsiyonel)
            return bool(char.get('skills'))
        elif step['name'] == "B├╝y├╝ler":
            # B├╝y├╝c├╝ de─şilse veya b├╝y├╝ler se├ğilmi┼şse tamamlanm─▒┼ş say─▒l─▒r
            class_name = char.get('class', '')
            class_data = self.data.get('classes', {}).get(class_name, {})
            is_spellcaster = class_data.get('spellcasting', False)
            if not is_spellcaster:
                return True  # B├╝y├╝c├╝ de─şilse atlanabilir
            return bool(char.get('spells'))
        elif step['name'] == "Feat'ler":
            # Feat'ler opsiyonel, se├ğilmi┼şse tamamlanm─▒┼ş say─▒l─▒r
            return True  # Her zaman tamamlanm─▒┼ş say─▒l─▒r (opsiyonel)
        elif step['name'] == "Ekipman":
            # Ekipman opsiyonel
            return True  # Her zaman tamamlanm─▒┼ş say─▒l─▒r (opsiyonel)
        elif step['name'] == "Ki┼şilik":
            # Ki┼şilik ├Âzellikleri opsiyonel
            return True  # Her zaman tamamlanm─▒┼ş say─▒l─▒r (opsiyonel)
        elif step['name'] == "├ûzet":
            # ├ûzet her zaman eri┼şilebilir
            return True
        
        return False
    
    def _update_navigation_buttons(self):
        """─░leri/Geri butonlar─▒n─▒ g├╝ncelle"""
        # Widget'lar─▒n varl─▒─ş─▒n─▒ kontrol et
        if not hasattr(self, 'step_stack') or not self.step_stack:
            return
        
        # T├╝m ad─▒m widget'lar─▒ndaki butonlar─▒ bul ve g├╝ncelle
        try:
            for i in range(self.step_stack.count()):
                step_widget = self.step_stack.widget(i)
                if not step_widget or not step_widget.layout():
                    continue
                nav_layout_item = step_widget.layout().itemAt(step_widget.layout().count() - 1)
                if not nav_layout_item or not nav_layout_item.layout():
                    continue
                nav_layout = nav_layout_item.layout()
                
                # Butonlar─▒ bul
                back_btn = None
                next_btn = None
                for j in range(nav_layout.count()):
                    item = nav_layout.itemAt(j)
                    if item and item.widget():
                        widget = item.widget()
                        if isinstance(widget, QPushButton):
                            if "Geri" in widget.text():
                                back_btn = widget
                            elif "─░leri" in widget.text() or "Tamamla" in widget.text():
                                next_btn = widget
                
                if back_btn:
                    back_btn.setEnabled(i > 0)
                if next_btn:
                    if i == len(self.steps) - 1:
                        next_btn.setText("Tamamla")
                        # Son ad─▒mdaki butonun ba─şlant─▒s─▒n─▒ kontrol et
                        try:
                            next_btn.clicked.disconnect()
                        except TypeError:
                            pass  # Ba─şlant─▒ yoksa devam et
                        next_btn.clicked.connect(self._complete_character)
                    else:
                        next_btn.setText("─░leri ÔåÆ")
                        # Di─şer ad─▒mlardaki butonlar─▒n ba─şlant─▒s─▒n─▒ kontrol et
                        try:
                            next_btn.clicked.disconnect()
                        except TypeError:
                            pass  # Ba─şlant─▒ yoksa devam et
                        next_btn.clicked.connect(lambda checked, idx=i: self._go_to_step(idx + 1))
        except (AttributeError, RuntimeError):
            # Widget hen├╝z haz─▒r de─şil veya silinmi┼ş
            return
    
    def _populate_step_widgets(self):
        """Her ad─▒m i├ğin widget i├ğeri─şini doldur"""
        # ├ûnce mevcut widget'lar─▒ olu┼ştur (e─şer yoksa)
        if not hasattr(self, 'character_name_edit'):
            # character_form_container'─▒ olu┼ştur (g├Âr├╝nmez olarak)
            self.character_form_container = QWidget()
            self._build_character_form_widgets()
        
        # Her ad─▒m i├ğin i├ğeri─şi doldur
        for i, step in enumerate(self.steps):
            if i >= len(self.step_widgets):
                continue
            
            layout = self.step_widgets[i].layout()

            # Mevcut i├ğeri─şi temizle (tekrarl─▒ g├Âr├╝n├╝m├╝ engellemek i├ğin)
            self._clear_layout(layout)
            
            # Placeholder'─▒ kald─▒r
            widgets_to_remove = []
            for j in reversed(range(layout.count())):
                item = layout.itemAt(j)
                if item:
                    widget = item.widget()
                    if widget and isinstance(widget, QLabel):
                        try:
                            if "i├ğeri─şi buraya gelecek" in widget.text() or "yak─▒nda eklenecek" in widget.text():
                                widgets_to_remove.append((j, widget))
                        except RuntimeError:
                            # Widget zaten silinmi┼ş, devam et
                            continue
            
            # Widget'lar─▒ g├╝venli ┼şekilde kald─▒r
            for j, widget in widgets_to_remove:
                layout.removeWidget(widget)
                widget.deleteLater()
            
            # Ad─▒m 0: ─░sim ve S─▒n─▒f
            if step['name'] == "─░sim ve S─▒n─▒f":
                name_class_group = QGroupBox("Karakter Bilgileri")
                name_class_layout = QVBoxLayout()
                name_class_layout.setContentsMargins(5, 5, 5, 5)
                name_class_layout.setSpacing(6)
                name_label = QLabel("─░sim:")
                name_edit = QLineEdit()
                name_edit.setMaximumHeight(32)  # Daha kompakt g├Âr├╝n├╝m
                # Bu ad─▒m sadece bilgiyi g├Âstermek i├ğin; tekrar giri┼ş istememek ad─▒na placeholder kald─▒r─▒ld─▒
                name_edit.setPlaceholderText("")
                # Karakter bilgilerini y├╝kle
                if hasattr(self, 'current_character') and self.current_character:
                    name_edit.setText(self.current_character.get('name', ''))
                elif hasattr(self, 'character_name_edit'):
                    name_edit.setText(self.character_name_edit.text())
                # Signal ba─şlant─▒s─▒
                if hasattr(self, 'character_name_edit'):
                    def update_name(text):
                        if hasattr(self, 'character_name_edit'):
                            self.character_name_edit.setText(text)
                        if hasattr(self, 'current_character') and self.current_character:
                            self.current_character['name'] = text
                            self.current_character['system'] = self.SYSTEM_NAME
                            self._auto_save_character()
                    # Bu ad─▒mda kullan─▒c─▒dan ikinci kez giri┼ş istenmesin diye alan─▒ sadece-okunur yap─▒yoruz
                    name_edit.setReadOnly(True)
                    # Yine de programatik g├╝ncelleme i├ğin sinyal ba─şl─▒ kalabilir
                    name_edit.textChanged.connect(update_name)
                name_class_layout.addWidget(name_label)
                name_class_layout.addWidget(name_edit)
                
                class_label = QLabel("S─▒n─▒f:")
                class_combo = QComboBox()
                class_combo.addItems(sorted(self.data.get("classes", {}).keys()))
                # Karakter bilgilerini y├╝kle
                if hasattr(self, 'current_character') and self.current_character:
                    char_class = self.current_character.get('class', '')
                    if char_class:
                        idx = class_combo.findText(char_class)
                        if idx >= 0:
                            class_combo.setCurrentIndex(idx)
                elif hasattr(self, 'class_cb'):
                    idx = class_combo.findText(self.class_cb.currentText())
                    if idx >= 0:
                        class_combo.setCurrentIndex(idx)
                # Signal ba─şlant─▒s─▒
                if hasattr(self, 'class_cb'):
                    def update_class(text):
                        if hasattr(self, 'class_cb'):
                            self.class_cb.setCurrentText(text)
                        if hasattr(self, 'current_character') and self.current_character:
                            self.current_character['class'] = text
                            self.current_character['system'] = self.SYSTEM_NAME
                            self._auto_save_character()
                    # Kullan─▒c─▒dan tekrar se├ğim istememek i├ğin combobox'─▒ pasif hale getiriyoruz
                    class_combo.setEnabled(False)
                    class_combo.currentTextChanged.connect(update_class)
                class_combo.setMaximumHeight(32)  # Daha kompakt g├Âr├╝n├╝m
                name_class_layout.addWidget(class_label)
                name_class_layout.addWidget(class_combo)
                name_class_group.setLayout(name_class_layout)
                name_class_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                name_class_group.setMaximumHeight(180)
                layout.insertWidget(2, name_class_group)
            
            # Ad─▒m 1: Irk
            elif step['name'] == "Irk":
                race_group = QGroupBox("Irk Se├ğimi")
                race_layout = QVBoxLayout()
                race_layout.setContentsMargins(5, 5, 5, 5)
                race_layout.setSpacing(6)
                race_label = QLabel("Irk:")
                race_combo = QComboBox()
                race_combo.setMaximumHeight(32)  # Daha kompakt g├Âr├╝n├╝m
                race_combo.addItems(sorted(self.data.get("races", {}).keys()))
                if hasattr(self, 'race_cb'):
                    idx = race_combo.findText(self.race_cb.currentText())
                    if idx >= 0:
                        race_combo.setCurrentIndex(idx)
                    race_combo.currentTextChanged.connect(self.race_cb.setCurrentText)
                race_layout.addWidget(race_label)
                race_layout.addWidget(race_combo)
                race_group.setLayout(race_layout)
                race_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                race_group.setMaximumHeight(170)
                layout.insertWidget(2, race_group)
            
            # Ad─▒m 2: Arka Plan
            elif step['name'] == "Arka Plan":
                bg_group = QGroupBox("Arka Plan Se├ğimi")
                bg_layout = QVBoxLayout()
                bg_layout.setContentsMargins(5, 5, 5, 5)
                bg_layout.setSpacing(6)
                bg_label = QLabel("Arka Plan:")
                bg_combo = QComboBox()
                bg_combo.setMaximumHeight(32)  # Daha kompakt g├Âr├╝n├╝m
                bg_combo.addItems(sorted(self.data.get("backgrounds", {}).keys()))
                if hasattr(self, 'bg_cb'):
                    idx = bg_combo.findText(self.bg_cb.currentText())
                    if idx >= 0:
                        bg_combo.setCurrentIndex(idx)
                    bg_combo.currentTextChanged.connect(self.bg_cb.setCurrentText)
                bg_layout.addWidget(bg_label)
                bg_layout.addWidget(bg_combo)
                bg_group.setLayout(bg_layout)
                bg_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                bg_group.setMaximumHeight(170)
                layout.insertWidget(2, bg_group)
            
            # Ad─▒m 3: Yetenek Puanlar─▒
            elif step['name'] == "Yetenek Puanlar─▒":
                if hasattr(self, 'ability_spins'):
                    pb_group = QGroupBox("Yetenek Puanlar─▒ (Point-Buy)")
                    pb_layout = QVBoxLayout()
                    pb_grid = QGridLayout()
                    pb_grid.setHorizontalSpacing(12)
                    pb_grid.setVerticalSpacing(10)
                    for idx, ability in enumerate(self.abilities):
                        label = QLabel(ability)
                        spin = self.ability_spins[ability]
                        row = idx // 3
                        col = (idx % 3) * 2
                        pb_grid.addWidget(label, row, col)
                        pb_grid.addWidget(spin, row, col + 1)
                    # Mevcut pb_info'yu kullan
                    if hasattr(self, 'pb_info'):
                        pb_grid.addWidget(self.pb_info, (len(self.abilities) + 2) // 3, 0, 1, 6)
                    else:
                        pb_info = QLabel("Kalan puan: 27")
                        pb_info.setStyleSheet("font-weight: bold; color: #e74c3c;")
                        pb_grid.addWidget(pb_info, (len(self.abilities) + 2) // 3, 0, 1, 6)
                    pb_layout.addLayout(pb_grid)
                    pb_group.setLayout(pb_layout)
                    layout.insertWidget(2, pb_group)
            
            # Ad─▒m 4: S─▒n─▒f Becerileri
            elif step['name'] == "S─▒n─▒f Becerileri":
                if hasattr(self, 'wiz_skills'):
                    skills_group = QGroupBox("S─▒n─▒f Becerileri")
                    skills_layout = QVBoxLayout()
                    if hasattr(self, 'wiz_skills_label'):
                        skills_layout.addWidget(self.wiz_skills_label)
                    if hasattr(self, 'wiz_skills'):
                        skills_layout.addWidget(self.wiz_skills)
                    # Expertise i├ğin (Rogue vb.)
                    if hasattr(self, 'wiz_expertise_label') and hasattr(self, 'wiz_expertise'):
                        skills_layout.addWidget(self.wiz_expertise_label)
                        skills_layout.addWidget(self.wiz_expertise)
                    skills_group.setLayout(skills_layout)
                    layout.insertWidget(2, skills_group)
                    
                    # S─▒n─▒f se├ğilmi┼şse becerileri yenile
                    class_name = None
                    if hasattr(self, 'current_character') and self.current_character:
                        class_name = self.current_character.get('class', '')
                    elif hasattr(self, 'class_cb') and self.class_cb.currentText():
                        class_name = self.class_cb.currentText()
                    
                    if class_name:
                        # Ge├ğici olarak class_cb'yi ayarla (e─şer yoksa)
                        if not hasattr(self, 'class_cb') or not self.class_cb.currentText():
                            if hasattr(self, 'class_cb'):
                                idx = self.class_cb.findText(class_name)
                                if idx >= 0:
                                    self.class_cb.setCurrentIndex(idx)
                        self._refresh_class_options()
                    else:
                        # S─▒n─▒f se├ğilmemi┼şse uyar─▒ g├Âster
                        warning_label = QLabel("ÔÜá´©Å L├╝tfen ├Ânce bir s─▒n─▒f se├ğin (─░sim ve S─▒n─▒f ad─▒m─▒na d├Ân├╝n).")
                        warning_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 10px;")
                        skills_layout.insertWidget(0, warning_label)
                else:
                    placeholder = QLabel("L├╝tfen ├Ânce bir s─▒n─▒f se├ğin.")
                    placeholder.setStyleSheet("color: #95a5a6; font-style: italic; padding: 20px;")
                    layout.insertWidget(2, placeholder)
            
            # Ad─▒m 5: B├╝y├╝ler
            elif step['name'] == "B├╝y├╝ler":
                if hasattr(self, 'wiz_cantrips') and hasattr(self, 'wiz_level1'):
                    spells_group = QGroupBox("B├╝y├╝ Se├ğimi")
                    spells_layout = QVBoxLayout()
                    if hasattr(self, 'wiz_cantrips_label'):
                        spells_layout.addWidget(self.wiz_cantrips_label)
                    if hasattr(self, 'wiz_cantrips'):
                        spells_layout.addWidget(self.wiz_cantrips)
                    if hasattr(self, 'wiz_level1_label'):
                        spells_layout.addWidget(self.wiz_level1_label)
                    if hasattr(self, 'wiz_level1'):
                        spells_layout.addWidget(self.wiz_level1)
                    spells_group.setLayout(spells_layout)
                    layout.insertWidget(2, spells_group)
                else:
                    placeholder = QLabel("Bu s─▒n─▒f b├╝y├╝ kullanmaz. Bu ad─▒m─▒ atlayabilirsiniz.")
                    placeholder.setStyleSheet("color: #95a5a6; font-style: italic; padding: 20px;")
                    layout.insertWidget(2, placeholder)
            
            # Ad─▒m 6: Feat'ler
            elif step['name'] == "Feat'ler":
                if hasattr(self, 'feats_group'):
                    feats_group = QGroupBox("Feat Se├ğimi")
                    feats_layout = QVBoxLayout()
                    if hasattr(self, 'feats_label'):
                        feats_layout.addWidget(self.feats_label)
                    if hasattr(self, 'feats_list'):
                        feats_layout.addWidget(self.feats_list)
                    feats_group.setLayout(feats_layout)
                    layout.insertWidget(2, feats_group)
            
            # Ad─▒m 7: Ekipman
            elif step['name'] == "Ekipman":
                equipment_group = QGroupBox("Ba┼şlang─▒├ğ Ekipman─▒")
                equipment_layout = QVBoxLayout()
                equipment_info = QLabel("Ekipman se├ğimi i├ğin 'Envanter' sekmesini kullanabilirsiniz.\nVeya s─▒n─▒f─▒n─▒z─▒n ba┼şlang─▒├ğ ekipman─▒n─▒ se├ğebilirsiniz.")
                equipment_info.setWordWrap(True)
                equipment_info.setStyleSheet("color: #7f8c8d; padding: 10px;")
                equipment_layout.addWidget(equipment_info)
                
                # S─▒n─▒f ekipman se├ğeneklerini g├Âster (e─şer varsa)
                if hasattr(self, 'current_character') and self.current_character:
                    class_name = self.current_character.get('class', '')
                    if class_name and class_name in self.data.get('classes', {}):
                        class_data = self.data['classes'][class_name]
                        equipment_options = class_data.get('starting_equipment', {})
                        if equipment_options:
                            options_label = QLabel("S─▒n─▒f Ekipman Se├ğenekleri:")
                            options_label.setStyleSheet("font-weight: bold; margin-top: 10px;")
                            equipment_layout.addWidget(options_label)
                            
                            for category, items in equipment_options.items():
                                cat_label = QLabel(f"{category}:")
                                cat_label.setStyleSheet("font-weight: bold; color: #2c3e50; margin-top: 5px;")
                                equipment_layout.addWidget(cat_label)
                                items_text = ", ".join(items) if isinstance(items, list) else str(items)
                                items_label = QLabel(items_text)
                                items_label.setWordWrap(True)
                                items_label.setStyleSheet("padding-left: 15px;")
                                equipment_layout.addWidget(items_label)
                
                equipment_group.setLayout(equipment_layout)
                layout.insertWidget(2, equipment_group)
            
            # Ad─▒m 8: Ki┼şilik
            elif step['name'] == "Ki┼şilik":
                personality_container = QWidget()
                personality_layout = QVBoxLayout(personality_container)
                
                # Diller ve Ki┼şilik
                if hasattr(self, 'extra_lang_edit'):
                    misc_group = QGroupBox("Diller ve Ki┼şilik")
                    misc_layout = QVBoxLayout()
                    misc_layout.addWidget(QLabel("Ek Diller"))
                    misc_layout.addWidget(self.extra_lang_edit)
                    misc_layout.addWidget(self.trait_edit)
                    misc_layout.addWidget(self.ideal_edit)
                    misc_layout.addWidget(self.bond_edit)
                    misc_layout.addWidget(self.flaw_edit)
                    misc_group.setLayout(misc_layout)
                    personality_layout.addWidget(misc_group)
                
                # Ki┼şisel ├ûzellikler
                if hasattr(self, 'height_edit'):
                    personal_group = QGroupBox("Fiziksel ve G├Âr├╝n├╝m ├ûzellikleri")
                    personal_layout = QVBoxLayout()
                    
                    # Fiziksel ├Âzellikler
                    physical_group = QGroupBox("Fiziksel ├ûzellikler")
                    physical_layout = QGridLayout()
                    physical_layout.addWidget(QLabel("Boy:"), 0, 0)
                    physical_layout.addWidget(self.height_edit, 0, 1)
                    physical_layout.addWidget(QLabel("Kilo:"), 1, 0)
                    physical_layout.addWidget(self.weight_edit, 1, 1)
                    physical_layout.addWidget(QLabel("Ya┼ş:"), 2, 0)
                    physical_layout.addWidget(self.age_edit, 2, 1)
                    physical_layout.setColumnStretch(1, 1)
                    physical_group.setLayout(physical_layout)
                    personal_layout.addWidget(physical_group)
                    
                    # G├Âr├╝n├╝m ├Âzellikleri
                    appearance_group = QGroupBox("G├Âr├╝n├╝m ├ûzellikleri")
                    appearance_layout = QGridLayout()
                    appearance_layout.addWidget(QLabel("Sa├ğ:"), 0, 0)
                    appearance_layout.addWidget(self.hair_color_edit, 0, 1)
                    appearance_layout.addWidget(QLabel("G├Âz:"), 1, 0)
                    appearance_layout.addWidget(self.eye_color_edit, 1, 1)
                    appearance_layout.addWidget(QLabel("Ten:"), 2, 0)
                    appearance_layout.addWidget(self.skin_color_edit, 2, 1)
                    appearance_layout.setColumnStretch(1, 1)
                    appearance_group.setLayout(appearance_layout)
                    personal_layout.addWidget(appearance_group)
                    
                    # Alignment
                    alignment_group = QGroupBox("Alignment")
                    alignment_layout = QHBoxLayout()
                    alignment_layout.addWidget(QLabel("Alignment:"))
                    alignment_layout.addWidget(self.alignment_cb)
                    alignment_group.setLayout(alignment_layout)
                    personal_layout.addWidget(alignment_group)
                    
                    # G├Âr├╝n├╝m a├ğ─▒klamas─▒
                    if hasattr(self, 'appearance_desc_edit'):
                        desc_group = QGroupBox("G├Âr├╝n├╝m A├ğ─▒klamas─▒")
                        desc_layout = QVBoxLayout()
                        desc_layout.addWidget(self.appearance_desc_edit)
                        desc_group.setLayout(desc_layout)
                        personal_layout.addWidget(desc_group)
                    
                    # Karakter resmi
                    if hasattr(self, 'character_image_label'):
                        image_group = QGroupBox("­şû╝´©Å Karakter Resmi")
                        image_layout = QVBoxLayout()
                        image_layout.addWidget(self.character_image_label)
                        
                        image_buttons = QHBoxLayout()
                        load_btn = QPushButton("­şôÀ Resim Y├╝kle")
                        load_btn.clicked.connect(self._load_character_image)
                        remove_btn = QPushButton("­şùæ´©Å Resmi Kald─▒r")
                        remove_btn.clicked.connect(self._remove_character_image)
                        image_buttons.addWidget(load_btn)
                        image_buttons.addWidget(remove_btn)
                        image_layout.addLayout(image_buttons)
                        image_group.setLayout(image_layout)
                        personal_layout.addWidget(image_group)
                    
                    personal_group.setLayout(personal_layout)
                    personality_layout.addWidget(personal_group)
                
                layout.insertWidget(2, personality_container)
            
            # Ad─▒m 9: ├ûzet
            elif step['name'] == "├ûzet":
                summary_group = QGroupBox("Karakter ├ûzeti")
                summary_layout = QVBoxLayout()
                
                summary_text = QTextEdit()
                summary_text.setReadOnly(True)
                summary_text.setStyleSheet("""
                    QTextEdit {
                        background-color: #f8f9fa;
                        border: 1px solid #dee2e6;
                        border-radius: 5px;
                        padding: 10px;
                        font-size: 12px;
                    }
                """)
                
                # ├ûzet metnini olu┼ştur
                if hasattr(self, 'current_character') and self.current_character:
                    char = self.current_character
                    summary_html = f"""
                    <h2>{char.get('name', '─░simsiz')}</h2>
                    <p><b>S─▒n─▒f:</b> {char.get('class', 'Se├ğilmedi')}</p>
                    <p><b>Irk:</b> {char.get('race', 'Se├ğilmedi')}</p>
                    <p><b>Arka Plan:</b> {char.get('background', 'Se├ğilmedi')}</p>
                    <p><b>Seviye:</b> {char.get('level', 1)}</p>
                    """
                    
                    # Yetenek puanlar─▒
                    if hasattr(self, 'ability_spins'):
                        summary_html += "<h3>Yetenek Puanlar─▒:</h3><ul>"
                        for ability in self.abilities:
                            value = self.ability_spins[ability].value()
                            summary_html += f"<li>{ability}: {value}</li>"
                        summary_html += "</ul>"
                    
                    # Beceriler
                    if char.get('skills'):
                        summary_html += "<h3>Beceriler:</h3><ul>"
                        for skill, prof in char['skills'].items():
                            summary_html += f"<li>{skill}: {'Uzman' if prof else 'Normal'}</li>"
                        summary_html += "</ul>"
                    
                    # B├╝y├╝ler
                    if char.get('spells'):
                        summary_html += "<h3>B├╝y├╝ler:</h3><ul>"
                        for level, spells in char['spells'].items():
                            if spells:
                                summary_html += f"<li>Seviye {level}: {', '.join(spells)}</li>"
                        summary_html += "</ul>"
                    
                    # Feat'ler
                    if char.get('feats'):
                        summary_html += f"<h3>Feat'ler:</h3><ul>"
                        for feat in char['feats']:
                            summary_html += f"<li>{feat}</li>"
                        summary_html += "</ul>"
                    
                    summary_text.setHtml(summary_html)
                else:
                    summary_text.setText("Hen├╝z bir karakter olu┼şturulmad─▒.")
                
                summary_layout.addWidget(summary_text)
                summary_group.setLayout(summary_layout)
                layout.insertWidget(2, summary_group)
            
            # Bilinmeyen ad─▒mlar i├ğin placeholder
            else:
                placeholder = QLabel(f"{step['name']} i├ğeri─şi yak─▒nda eklenecek")
                placeholder.setStyleSheet("color: #95a5a6; font-style: italic; padding: 20px;")
                layout.insertWidget(2, placeholder)

    def _build_character_form(self):
        """Karakter formu widget'lar─▒n─▒ olu┼ştur"""
        # Se├ğimler: Irk, S─▒n─▒f, Arka plan
        sel_group = QGroupBox("Se├ğimler")
        sel_layout = QGridLayout()
        sel_layout.setHorizontalSpacing(12)
        sel_layout.setVerticalSpacing(8)
        self.character_name_edit = QLineEdit()
        self.character_name_edit.setPlaceholderText("Karakter ismini girin...")
        self.race_cb = QComboBox(); self.race_cb.addItems(sorted(self.data.get("races", {}).keys()))
        self.class_cb = QComboBox(); self.class_cb.addItems(sorted(self.data.get("classes", {}).keys()))
        self.bg_cb = QComboBox(); self.bg_cb.addItems(sorted(self.data.get("backgrounds", {}).keys()))
        
        # Event handler'lar─▒ ekle
        self.race_cb.currentTextChanged.connect(self._show_race_info)
        self.race_cb.currentTextChanged.connect(self._update_ability_scores)
        self.race_cb.currentTextChanged.connect(self._auto_save_character)
        self.class_cb.currentTextChanged.connect(self._show_class_info)
        self.class_cb.currentTextChanged.connect(self._refresh_class_features)
        self.class_cb.currentTextChanged.connect(self._auto_save_character)
        self.class_cb.currentTextChanged.connect(self._update_character_stats)
        self.class_cb.currentTextChanged.connect(self._update_spell_tab_visibility)
        self.bg_cb.currentTextChanged.connect(self._show_background_info)
        self.bg_cb.currentTextChanged.connect(self._auto_save_character)

        name_label = QLabel("─░sim")
        race_label = QLabel("Irk")
        class_label = QLabel("S─▒n─▒f")
        bg_label = QLabel("Arka Plan")

        sel_layout.addWidget(name_label, 0, 0)
        sel_layout.addWidget(self.character_name_edit, 0, 1)
        sel_layout.addWidget(race_label, 1, 0)
        sel_layout.addWidget(self.race_cb, 1, 1)
        sel_layout.addWidget(class_label, 2, 0)
        sel_layout.addWidget(self.class_cb, 2, 1)
        sel_layout.addWidget(bg_label, 3, 0)
        sel_layout.addWidget(self.bg_cb, 3, 1)
        sel_layout.setColumnStretch(1, 1)
        sel_group.setLayout(sel_layout)

        # Point-buy: 6 spinbox
        pb_group = QGroupBox("Yetenek Puanlar─▒ (Point-Buy)")
        pb_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Maximum)
        pb_grid = QGridLayout()
        pb_grid.setHorizontalSpacing(12)
        pb_grid.setVerticalSpacing(10)
        self.abilities = self.data.get("abilities", [])
        self.ability_spins: dict[str, QSpinBox] = {}
        self.pb_info = QLabel("Kalan puan: 27")
        for idx, ability in enumerate(self.abilities):
            label = QLabel(ability)
            spin = QSpinBox()
            spin.setRange(8, 15)
            spin.setValue(8)
            spin.valueChanged.connect(self._update_point_buy_info)
            spin.valueChanged.connect(self._auto_save_character)
            spin.valueChanged.connect(self._update_character_stats)
            self.ability_spins[ability] = spin
            row = idx // 3
            col = (idx % 3) * 2
            pb_grid.addWidget(label, row, col)
            pb_grid.addWidget(spin, row, col + 1)
        pb_grid.addWidget(self.pb_info, (len(self.abilities) + 2) // 3, 0, 1, 6)
        pb_group.setLayout(pb_grid)


        # Diller ve Ki┼şilik
        misc_group = QGroupBox("Diller ve Ki┼şilik")
        misc_layout = QVBoxLayout()
        self.extra_lang_edit = QLineEdit(); self.extra_lang_edit.setPlaceholderText("Ek diller (virg├╝lle ay─▒r─▒n)")
        self.trait_edit = QLineEdit(); self.trait_edit.setPlaceholderText("Personality Trait")
        self.ideal_edit = QLineEdit(); self.ideal_edit.setPlaceholderText("Ideal")
        self.bond_edit = QLineEdit(); self.bond_edit.setPlaceholderText("Bond")
        self.flaw_edit = QLineEdit(); self.flaw_edit.setPlaceholderText("Flaw")
        misc_layout.addWidget(QLabel("Ek Diller")); misc_layout.addWidget(self.extra_lang_edit)
        misc_layout.addWidget(self.trait_edit); misc_layout.addWidget(self.ideal_edit)
        misc_layout.addWidget(self.bond_edit); misc_layout.addWidget(self.flaw_edit)
        misc_group.setLayout(misc_layout)

        # Ki┼şisel ├ûzellikler
        personal_group = QGroupBox("Ki┼şisel ├ûzellikler")
        personal_layout = QVBoxLayout()
        
        # Fiziksel ├Âzellikler
        physical_layout = QGridLayout()
        physical_layout.setHorizontalSpacing(10)
        physical_layout.setVerticalSpacing(6)
        self.height_edit = QLineEdit(); self.height_edit.setPlaceholderText("Boy (├Ârn: 5'8\")")
        self.weight_edit = QLineEdit(); self.weight_edit.setPlaceholderText("Kilo (├Ârn: 150 lbs)")
        self.age_edit = QLineEdit(); self.age_edit.setPlaceholderText("Ya┼ş (├Ârn: 25)")
        physical_layout.addWidget(QLabel("Boy:"), 0, 0)
        physical_layout.addWidget(self.height_edit, 0, 1)
        physical_layout.addWidget(QLabel("Kilo:"), 1, 0)
        physical_layout.addWidget(self.weight_edit, 1, 1)
        physical_layout.addWidget(QLabel("Ya┼ş:"), 2, 0)
        physical_layout.addWidget(self.age_edit, 2, 1)
        physical_layout.setColumnStretch(1, 1)
        
        # G├Âr├╝n├╝m ├Âzellikleri
        appearance_layout = QGridLayout()
        appearance_layout.setHorizontalSpacing(10)
        appearance_layout.setVerticalSpacing(6)
        self.hair_color_edit = QLineEdit(); self.hair_color_edit.setPlaceholderText("Sa├ğ Rengi")
        self.eye_color_edit = QLineEdit(); self.eye_color_edit.setPlaceholderText("G├Âz Rengi")
        self.skin_color_edit = QLineEdit(); self.skin_color_edit.setPlaceholderText("Ten Rengi")
        appearance_layout.addWidget(QLabel("Sa├ğ:"), 0, 0)
        appearance_layout.addWidget(self.hair_color_edit, 0, 1)
        appearance_layout.addWidget(QLabel("G├Âz:"), 1, 0)
        appearance_layout.addWidget(self.eye_color_edit, 1, 1)
        appearance_layout.addWidget(QLabel("Ten:"), 2, 0)
        appearance_layout.addWidget(self.skin_color_edit, 2, 1)
        appearance_layout.setColumnStretch(1, 1)
        
        # Karakter resmi
        image_group = QGroupBox("­şû╝´©Å Karakter Resmi")
        image_layout = QVBoxLayout()
        
        # Resim g├Âr├╝nt├╝leme alan─▒
        self.character_image_label = QLabel()
        self.character_image_label.setMinimumSize(200, 200)
        self.character_image_label.setMaximumSize(300, 300)
        self.character_image_label.setAlignment(Qt.AlignCenter)
        self.character_image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #95a5a6;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
        """)
        self.character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")
        self.character_image_label.setWordWrap(True)
        image_layout.addWidget(self.character_image_label)
        
        # Resim butonlar─▒
        image_buttons_layout = QHBoxLayout()
        
        load_image_btn = QPushButton("­şôÀ Resim Y├╝kle")
        load_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_image_btn.clicked.connect(self._load_character_image)
        image_buttons_layout.addWidget(load_image_btn)
        
        remove_image_btn = QPushButton("­şùæ´©Å Resmi Kald─▒r")
        remove_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_image_btn.clicked.connect(self._remove_character_image)
        image_buttons_layout.addWidget(remove_image_btn)
        
        image_layout.addLayout(image_buttons_layout)
        image_group.setLayout(image_layout)
        
        # Karakter ├Âzellikleri
        character_layout = QVBoxLayout()
        self.appearance_desc_edit = QTextEdit(); self.appearance_desc_edit.setPlaceholderText("G├Âr├╝n├╝m A├ğ─▒klamas─▒ (iste─şe ba─şl─▒)")
        self.appearance_desc_edit.setMaximumHeight(80)
        character_layout.addWidget(QLabel("G├Âr├╝n├╝m A├ğ─▒klamas─▒:"))
        character_layout.addWidget(self.appearance_desc_edit)
        
        # Alignment se├ğimi
        alignment_layout = QHBoxLayout()
        self.alignment_cb = QComboBox(); self.alignment_cb.addItems([
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ])
        alignment_layout.addWidget(QLabel("Alignment:")); alignment_layout.addWidget(self.alignment_cb)
        
        personal_layout.addLayout(physical_layout)
        personal_layout.addLayout(appearance_layout)
        personal_layout.addLayout(alignment_layout)
        personal_layout.addWidget(image_group)
        personal_layout.addLayout(character_layout)
        personal_group.setLayout(personal_layout)

    def _load_character_image(self):
        """Karakter resmi y├╝kle"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Karakter Resmi Se├ğ",
            "",
            "Resim Dosyalar─▒ (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;T├╝m Dosyalar (*)"
        )
        
        if file_path:
            try:
                image_path = Path(file_path)
                base64_str = _load_image_to_base64(image_path)
                
                if base64_str:
                    self.current_character_image_data = base64_str
                    
                    # Resmi g├Âster
                    pixmap = QPixmap(str(image_path))
                    if not pixmap.isNull():
                        # Resmi 300x300'e ├Âl├ğekle (orant─▒l─▒)
                        scaled_pixmap = pixmap.scaled(
                            300, 300,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.character_image_label.setPixmap(scaled_pixmap)
                        self.character_image_label.setText("")
                    
                    # Karakter verisini g├╝ncelle
                    if hasattr(self, 'current_character') and self.current_character:
                        self.current_character["image"] = base64_str
                        self._auto_save_character()
                    
                    QMessageBox.information(self, "Ba┼şar─▒l─▒", "Resim ba┼şar─▒yla y├╝klendi!")
                else:
                    QMessageBox.warning(self, "Hata", "Resim y├╝klenemedi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Resim y├╝klenirken bir hata olu┼ştu:\n{str(e)}")

    def _remove_character_image(self):
        """Karakter resmini kald─▒r"""
        reply = QMessageBox.question(
            self,
            "Resmi Kald─▒r",
            "Karakter resmini kald─▒rmak istedi─şinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_character_image_data = None
            self.character_image_label.clear()
            self.character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")
            
            # Karakter verisinden kald─▒r
            if hasattr(self, 'current_character') and self.current_character:
                if "image" in self.current_character:
                    del self.current_character["image"]
                self._auto_save_character()
            
            QMessageBox.information(self, "Ba┼şar─▒l─▒", "Resim kald─▒r─▒ld─▒.")

    def _load_character_image_to_gui(self, character: dict):
        """Karakter verisinden resmi GUI'ye y├╝kle"""
        image_data = character.get("image")
        if image_data:
            self.current_character_image_data = image_data
            pixmap = _get_image_from_character(character)
            if pixmap and not pixmap.isNull():
                # Resmi 300x300'e ├Âl├ğekle (orant─▒l─▒)
                scaled_pixmap = pixmap.scaled(
                    300, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.character_image_label.setPixmap(scaled_pixmap)
                self.character_image_label.setText("")
            else:
                self.character_image_label.setText("Resim y├╝klenemedi\n(Resim eklemek i├ğin butona t─▒klay─▒n)")
        else:
            self.current_character_image_data = None
            self.character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")

    def _build_character_form_widgets(self):
        """Karakter formu widget'lar─▒n─▒ olu┼ştur ve layout'a ekle"""
        if not hasattr(self, "character_form_container"):
            return
        
        layout = self.character_form_container.layout()
        if not layout:
            layout = QVBoxLayout(self.character_form_container)
        
        # Se├ğimler: Irk, S─▒n─▒f, Arka plan
        sel_group = QGroupBox("Se├ğimler")
        sel_layout = QHBoxLayout()
        self.character_name_edit = QLineEdit()
        self.character_name_edit.setPlaceholderText("Karakter ismini girin...")
        self.race_cb = QComboBox(); self.race_cb.addItems(sorted(self.data.get("races", {}).keys()))
        self.class_cb = QComboBox(); self.class_cb.addItems(sorted(self.data.get("classes", {}).keys()))
        self.bg_cb = QComboBox(); self.bg_cb.addItems(sorted(self.data.get("backgrounds", {}).keys()))
        
        # Event handler'lar─▒ ekle
        self.race_cb.currentTextChanged.connect(self._show_race_info)
        self.race_cb.currentTextChanged.connect(self._update_ability_scores)
        self.race_cb.currentTextChanged.connect(self._auto_save_character)
        self.class_cb.currentTextChanged.connect(self._show_class_info)
        self.class_cb.currentTextChanged.connect(self._refresh_class_features)
        self.class_cb.currentTextChanged.connect(self._auto_save_character)
        self.class_cb.currentTextChanged.connect(self._update_character_stats)
        self.bg_cb.currentTextChanged.connect(self._show_background_info)
        self.bg_cb.currentTextChanged.connect(self._auto_save_character)
        sel_layout.addWidget(QLabel("─░sim")); sel_layout.addWidget(self.character_name_edit)
        sel_layout.addWidget(QLabel("Irk")); sel_layout.addWidget(self.race_cb)
        sel_layout.addWidget(QLabel("S─▒n─▒f")); sel_layout.addWidget(self.class_cb)
        sel_layout.addWidget(QLabel("Arka Plan")); sel_layout.addWidget(self.bg_cb)
        sel_group.setLayout(sel_layout)

        # Point-buy: 6 spinbox
        pb_group = QGroupBox("Yetenek Puanlar─▒ (Point-Buy)")
        pb_layout = QHBoxLayout()
        self.abilities = self.data.get("abilities", [])
        self.ability_spins: dict[str, QSpinBox] = {}
        self.pb_info = QLabel("Kalan puan: 27")
        for ability in self.abilities:
            box = QVBoxLayout()
            box.addWidget(QLabel(ability))
            spin = QSpinBox(); spin.setRange(8, 15); spin.setValue(8)
            spin.valueChanged.connect(self._update_point_buy_info)
            spin.valueChanged.connect(self._auto_save_character)
            spin.valueChanged.connect(self._update_character_stats)
            self.ability_spins[ability] = spin
            box.addWidget(spin)
            col = QWidget(); col.setLayout(box)
            pb_layout.addWidget(col)
        column = QVBoxLayout()
        column.addLayout(pb_layout)
        column.addWidget(self.pb_info)
        wrap = QWidget(); wrap.setLayout(column)
        v = QVBoxLayout(); v.addWidget(wrap)
        pb_group.setLayout(v)

        # Diller ve Ki┼şilik
        misc_group = QGroupBox("Diller ve Ki┼şilik")
        misc_layout = QVBoxLayout()
        self.extra_lang_edit = QLineEdit(); self.extra_lang_edit.setPlaceholderText("Ek diller (virg├╝lle ay─▒r─▒n)")
        self.trait_edit = QLineEdit(); self.trait_edit.setPlaceholderText("Personality Trait")
        self.ideal_edit = QLineEdit(); self.ideal_edit.setPlaceholderText("Ideal")
        self.bond_edit = QLineEdit(); self.bond_edit.setPlaceholderText("Bond")
        self.flaw_edit = QLineEdit(); self.flaw_edit.setPlaceholderText("Flaw")
        misc_layout.addWidget(QLabel("Ek Diller")); misc_layout.addWidget(self.extra_lang_edit)
        misc_layout.addWidget(self.trait_edit); misc_layout.addWidget(self.ideal_edit)
        misc_layout.addWidget(self.bond_edit); misc_layout.addWidget(self.flaw_edit)
        misc_group.setLayout(misc_layout)

        # Ki┼şisel ├ûzellikler
        personal_group = QGroupBox("Ki┼şisel ├ûzellikler")
        personal_layout = QVBoxLayout()
        
        # Fiziksel ├Âzellikler
        physical_layout = QHBoxLayout()
        self.height_edit = QLineEdit(); self.height_edit.setPlaceholderText("Boy (├Ârn: 5'8\")")
        self.weight_edit = QLineEdit(); self.weight_edit.setPlaceholderText("Kilo (├Ârn: 150 lbs)")
        self.age_edit = QLineEdit(); self.age_edit.setPlaceholderText("Ya┼ş (├Ârn: 25)")
        physical_layout.addWidget(QLabel("Boy:")); physical_layout.addWidget(self.height_edit)
        physical_layout.addWidget(QLabel("Kilo:")); physical_layout.addWidget(self.weight_edit)
        physical_layout.addWidget(QLabel("Ya┼ş:")); physical_layout.addWidget(self.age_edit)
        
        # G├Âr├╝n├╝m ├Âzellikleri
        appearance_layout = QHBoxLayout()
        self.hair_color_edit = QLineEdit(); self.hair_color_edit.setPlaceholderText("Sa├ğ Rengi")
        self.eye_color_edit = QLineEdit(); self.eye_color_edit.setPlaceholderText("G├Âz Rengi")
        self.skin_color_edit = QLineEdit(); self.skin_color_edit.setPlaceholderText("Ten Rengi")
        appearance_layout.addWidget(QLabel("Sa├ğ:")); appearance_layout.addWidget(self.hair_color_edit)
        appearance_layout.addWidget(QLabel("G├Âz:")); appearance_layout.addWidget(self.eye_color_edit)
        appearance_layout.addWidget(QLabel("Ten:")); appearance_layout.addWidget(self.skin_color_edit)
        
        # Karakter resmi
        image_group = QGroupBox("­şû╝´©Å Karakter Resmi")
        image_layout = QVBoxLayout()
        
        # Resim g├Âr├╝nt├╝leme alan─▒
        self.character_image_label = QLabel()
        self.character_image_label.setMinimumSize(200, 200)
        self.character_image_label.setMaximumSize(300, 300)
        self.character_image_label.setAlignment(Qt.AlignCenter)
        self.character_image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #95a5a6;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
        """)
        self.character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")
        self.character_image_label.setWordWrap(True)
        image_layout.addWidget(self.character_image_label)
        
        # Resim butonlar─▒
        image_buttons_layout = QHBoxLayout()
        
        load_image_btn = QPushButton("­şôÀ Resim Y├╝kle")
        load_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_image_btn.clicked.connect(self._load_character_image)
        image_buttons_layout.addWidget(load_image_btn)
        
        remove_image_btn = QPushButton("­şùæ´©Å Resmi Kald─▒r")
        remove_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_image_btn.clicked.connect(self._remove_character_image)
        image_buttons_layout.addWidget(remove_image_btn)
        
        image_layout.addLayout(image_buttons_layout)
        image_group.setLayout(image_layout)
        
        # Karakter ├Âzellikleri
        character_layout = QVBoxLayout()
        self.appearance_desc_edit = QTextEdit(); self.appearance_desc_edit.setPlaceholderText("G├Âr├╝n├╝m A├ğ─▒klamas─▒ (iste─şe ba─şl─▒)")
        self.appearance_desc_edit.setMaximumHeight(80)
        character_layout.addWidget(QLabel("G├Âr├╝n├╝m A├ğ─▒klamas─▒:"))
        character_layout.addWidget(self.appearance_desc_edit)
        
        # Alignment se├ğimi
        alignment_layout = QHBoxLayout()
        self.alignment_cb = QComboBox(); self.alignment_cb.addItems([
            "Lawful Good", "Neutral Good", "Chaotic Good",
            "Lawful Neutral", "True Neutral", "Chaotic Neutral",
            "Lawful Evil", "Neutral Evil", "Chaotic Evil"
        ])
        alignment_layout.addWidget(QLabel("Alignment:")); alignment_layout.addWidget(self.alignment_cb)
        
        personal_layout.addLayout(physical_layout)
        personal_layout.addLayout(appearance_layout)
        personal_layout.addLayout(alignment_layout)
        personal_layout.addWidget(image_group)
        personal_layout.addLayout(character_layout)
        personal_group.setLayout(personal_layout)

        # S─▒n─▒f ├Âzel se├ğimleri
        self.wiz_group = QGroupBox("S─▒n─▒f Se├ğimleri")
        wiz_layout = QVBoxLayout()
        self.wiz_skills_label = QLabel("S─▒n─▒f Becerileri (se├ğim say─▒s─▒ de─şi┼şkendir)")
        self.wiz_skills = QListWidget(); self.wiz_skills.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.wiz_cantrips_label = QLabel("Cantrip Se├ğimi")
        self.wiz_cantrips = QListWidget(); self.wiz_cantrips.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.wiz_level1_label = QLabel("1. Seviye B├╝y├╝ler")
        self.wiz_level1 = QListWidget(); self.wiz_level1.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        
        # Rogue expertise
        self.wiz_expertise_label = QLabel("Uzmanl─▒k (Expertise) Se├ğimi")
        self.wiz_expertise = QListWidget(); self.wiz_expertise.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        
        wiz_layout.addWidget(self.wiz_skills_label)
        wiz_layout.addWidget(self.wiz_skills)
        wiz_layout.addWidget(self.wiz_cantrips_label)
        wiz_layout.addWidget(self.wiz_cantrips)
        wiz_layout.addWidget(self.wiz_level1_label)
        wiz_layout.addWidget(self.wiz_level1)
        wiz_layout.addWidget(self.wiz_expertise_label)
        wiz_layout.addWidget(self.wiz_expertise)
        self.wiz_group.setLayout(wiz_layout)
        self.wiz_group.setVisible(False)

        # S─▒n─▒f ├Âzellikleri se├ğimi
        self.features_group = QGroupBox("S─▒n─▒f ├ûzellikleri")
        features_layout = QVBoxLayout()
        self.features_list = QListWidget()
        self.features_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.features_label = QLabel("Seviye ile Gelen ├ûzellikler:")
        features_layout.addWidget(self.features_label)
        features_layout.addWidget(self.features_list)
        self.features_group.setLayout(features_layout)
        self.features_group.setVisible(False)

        # Feat se├ğimi
        self.feats_group = QGroupBox("Feat Se├ğimi")
        feats_layout = QVBoxLayout()
        self.feats_list = QListWidget()
        self.feats_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.feats_label = QLabel("Se├ğilebilir Feat'ler:")
        feats_layout.addWidget(self.feats_label)
        feats_layout.addWidget(self.feats_list)
        self.feats_group.setLayout(feats_layout)
        self.feats_group.setVisible(True)

        self.class_cb.currentIndexChanged.connect(self._refresh_class_options)
        self.race_cb.currentIndexChanged.connect(self._refresh_feats)
        
        # Cache temizleme ba─şlant─▒lar─▒
        self.race_cb.currentIndexChanged.connect(self._clear_cache)
        self.class_cb.currentIndexChanged.connect(self._clear_cache)
        self.bg_cb.currentIndexChanged.connect(self._clear_cache)
        self.character_name_edit.textChanged.connect(self._clear_cache)
        
        # S─▒n─▒f se├ğimleri de─şi┼şti─şinde istatistikleri g├╝ncelle
        self.wiz_skills.itemSelectionChanged.connect(self._update_character_stats)
        self._refresh_class_options()
        self._refresh_class_features()
        self._refresh_feats()

        # Olu┼ştur ve ├ûzet
        bottom = QVBoxLayout()
        bottom.setSpacing(15)
        create_btn = QPushButton("­şÄ» Karakteri Tamamla")
        create_btn.setToolTip("Karakteri tamamlay─▒n ve PDF karakter ka─ş─▒d─▒ olu┼şturun")
        create_btn.clicked.connect(self._complete_character)
        create_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        # Karakter ─░statistikleri Paneli
        stats_group = QGroupBox("­şôè Karakter ─░statistikleri")
        stats_layout = QVBoxLayout()
        
        # ─░statistik grid'i
        stats_grid = QWidget()
        stats_grid_layout = QHBoxLayout()
        
        # Sol kolon - Temel ─░statistikler
        left_stats = QVBoxLayout()
        
        # AC
        ac_layout = QHBoxLayout()
        ac_layout.addWidget(QLabel("AC:"))
        self.ac_label = QLabel("10")
        self.ac_label.setStyleSheet("font-weight: bold; color: #e74c3c; font-size: 14px;")
        ac_layout.addWidget(self.ac_label)
        ac_layout.addStretch()
        left_stats.addLayout(ac_layout)
        
        # HP
        hp_layout = QHBoxLayout()
        hp_layout.addWidget(QLabel("HP:"))
        self.hp_label = QLabel("8")
        self.hp_label.setStyleSheet("font-weight: bold; color: #27ae60; font-size: 14px;")
        hp_layout.addWidget(self.hp_label)
        hp_layout.addStretch()
        left_stats.addLayout(hp_layout)
        
        # Proficiency Bonus
        prof_layout = QHBoxLayout()
        prof_layout.addWidget(QLabel("Prof. Bonus:"))
        self.prof_bonus_label = QLabel("+2")
        self.prof_bonus_label.setStyleSheet("font-weight: bold; color: #3498db; font-size: 14px;")
        prof_layout.addWidget(self.prof_bonus_label)
        prof_layout.addStretch()
        left_stats.addLayout(prof_layout)
        
        # Sa─ş kolon - Yetenek Modifierlar─▒
        right_stats = QVBoxLayout()
        
        # Yetenek puanlar─▒ ve modifierlar─▒
        self.ability_mod_labels = {}
        for ability in ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]:
            mod_layout = QHBoxLayout()
            ability_tr = {
                "strength": "STR", "dexterity": "DEX", "constitution": "CON",
                "intelligence": "INT", "wisdom": "WIS", "charisma": "CHA"
            }
            mod_layout.addWidget(QLabel(f"{ability_tr[ability]}:"))
            mod_label = QLabel("+0")
            mod_label.setStyleSheet("font-weight: bold; color: #2c3e50; font-size: 12px;")
            self.ability_mod_labels[ability] = mod_label
            mod_layout.addWidget(mod_label)
            mod_layout.addStretch()
            right_stats.addLayout(mod_layout)
        
        stats_grid_layout.addLayout(left_stats)
        stats_grid_layout.addLayout(right_stats)
        stats_grid.setLayout(stats_grid_layout)
        stats_layout.addWidget(stats_grid)
        
        # Skill Modifierlar─▒
        skills_group = QGroupBox("Beceri Modifierlar─▒")
        skills_layout = QVBoxLayout()
        
        # Skill grid (2 kolon)
        skills_grid = QWidget()
        skills_grid_layout = QHBoxLayout()
        
        # Sol kolon - Beceriler
        left_skills = QVBoxLayout()
        self.skill_mod_labels = {}
        skills_left = ["acrobatics", "animal_handling", "arcana", "athletics", "deception", "history", 
                      "insight", "intimidation", "investigation", "medicine"]
        
        for skill in skills_left:
            skill_layout = QHBoxLayout()
            skill_tr = {
                "acrobatics": "Akrobasi", "animal_handling": "Hayvan Bak─▒m─▒", "arcana": "B├╝y├╝",
                "athletics": "Atletizm", "deception": "Aldatma", "history": "Tarih",
                "insight": "─░├ğg├Âr├╝", "intimidation": "G├Âzda─ş─▒", "investigation": "Ara┼şt─▒rma", "medicine": "T─▒p"
            }
            skill_layout.addWidget(QLabel(f"{skill_tr.get(skill, skill)}:"))
            skill_mod_label = QLabel("+0")
            skill_mod_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            self.skill_mod_labels[skill] = skill_mod_label
            skill_layout.addWidget(skill_mod_label)
            skill_layout.addStretch()
            left_skills.addLayout(skill_layout)
        
        # Sa─ş kolon - Beceriler
        right_skills = QVBoxLayout()
        skills_right = ["nature", "perception", "performance", "persuasion", "religion", "sleight_of_hand",
                       "stealth", "survival"]
        
        for skill in skills_right:
            skill_layout = QHBoxLayout()
            skill_tr = {
                "nature": "Do─şa", "perception": "Alg─▒", "performance": "Performans",
                "persuasion": "─░kna", "religion": "Din", "sleight_of_hand": "El ├çabuklu─şu",
                "stealth": "Gizlilik", "survival": "Hayatta Kalma"
            }
            skill_layout.addWidget(QLabel(f"{skill_tr.get(skill, skill)}:"))
            skill_mod_label = QLabel("+0")
            skill_mod_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            self.skill_mod_labels[skill] = skill_mod_label
            skill_layout.addWidget(skill_mod_label)
            skill_layout.addStretch()
            right_skills.addLayout(skill_layout)
        
        skills_grid_layout.addLayout(left_skills)
        skills_grid_layout.addLayout(right_skills)
        skills_grid.setLayout(skills_grid_layout)
        skills_layout.addWidget(skills_grid)
        
        skills_group.setLayout(skills_layout)
        stats_layout.addWidget(skills_group)
        
        stats_group.setLayout(stats_layout)
        
        # Eski ├Âzet
        self.summary = QTextEdit()
        self.summary.setReadOnly(True)
        self.summary.setMaximumHeight(150)
        
        bottom.addWidget(create_btn)
        bottom.addWidget(stats_group)
        bottom.addWidget(self.summary)
        bottom.addStretch()

        # Layout'a ekle
        layout.addWidget(sel_group)
        layout.addWidget(pb_group)
        layout.addWidget(misc_group)
        layout.addWidget(personal_group)
        layout.addWidget(self.wiz_group)
        layout.addWidget(self.features_group)
        layout.addWidget(self.feats_group)
        layout.addLayout(bottom)

    def _class_has_spellcasting(self, class_name: str) -> bool:
        if not class_name:
            return False
        classes = self.data.get("classes", {})
        cls = classes.get(class_name, {})
        if not isinstance(cls, dict):
            return False
        if cls.get("spells"):
            return True
        if isinstance(cls.get("spellcasting"), dict):
            return True
        return bool(cls.get("spellcasting"))

    def _update_spell_tab_visibility(self):
        class_name = self.class_cb.currentText() if hasattr(self, "class_cb") else ""
        has_spells = self._class_has_spellcasting(class_name)
        self._spellcasting_enabled = has_spells
        if hasattr(self, "tab_widget") and hasattr(self, "spells_tab_index"):
            self.tab_widget.setTabEnabled(self.spells_tab_index, has_spells)
            if not has_spells and self.tab_widget.currentIndex() == self.spells_tab_index:
                self.tab_widget.setCurrentIndex(0)
        if hasattr(self, "spell_selection_group"):
            self.spell_selection_group.setVisible(has_spells)
            self.spell_selection_group.setEnabled(has_spells)
        if hasattr(self, "spells_list"):
            self.spells_list.setEnabled(has_spells)
        if hasattr(self, "available_spells_for_selection"):
            self.available_spells_for_selection.setEnabled(has_spells)
        if hasattr(self, "spellcasting_check_label"):
            if has_spells:
                self.spellcasting_check_label.setText("Bu s─▒n─▒f b├╝y├╝ kullanabilir.")
                self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            else:
                self.spellcasting_check_label.setText("Bu s─▒n─▒f b├╝y├╝ kullanmaz.")
                self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #e74c3c;")

    def _clear_cache(self):
        """UI de─şi┼şti─şinde cache'i temizle"""
        if hasattr(self, '_feat_cache'):
            self._feat_cache.clear()
        if hasattr(self, '_summary_cache'):
            self._summary_cache.clear()

    def _update_point_buy_info(self):
        """Point-buy sistemini g├╝ncelle"""
        total_cost = 0
        for ability, spin in self.ability_spins.items():
            score = spin.value()
            if score == 8:
                cost = 0
            elif score == 9:
                cost = 1
            elif score == 10:
                cost = 2
            elif score == 11:
                cost = 3
            elif score == 12:
                cost = 4
            elif score == 13:
                cost = 5
            elif score == 14:
                cost = 7
            elif score == 15:
                cost = 9
            else:
                cost = 0
            total_cost += cost
        
        remaining = 27 - total_cost
        self.pb_info.setText(f"Kalan puan: {remaining}")
        
        # Renk kodlamas─▒
        if remaining < 0:
            self.pb_info.setStyleSheet("color: red; font-weight: bold;")
        elif remaining == 0:
            self.pb_info.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.pb_info.setStyleSheet("color: black;")

    @staticmethod
    def _clear_layout(layout: QLayout):
        """Bir layout i├ğindeki t├╝m widget ve alt layout'lar─▒ temizle"""
        if not layout:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                DndPage._clear_layout(item.layout())

    def _refresh_class_options(self):
        """S─▒n─▒f se├ğeneklerini g├╝ncelle"""
        class_name = self.class_cb.currentText()
        classes = self.data.get("classes", {})
        
        # ├ûnce t├╝m se├ğimleri temizle
        self.wiz_skills.clear()
        self.wiz_cantrips.clear()
        self.wiz_level1.clear()
        self.wiz_expertise.clear()
        
        if class_name in classes:
            cls = classes[class_name]
            
            # S─▒n─▒f becerileri (destekler: {"skills": {"choices": X, "from": [...]}} veya {"class_skills": [...], "skill_choices": X})
            choices = 0
            available_skills = []
            if "skills" in cls:
                skills = cls.get("skills", {})
                choices = skills.get("choices", 0)
                available_skills = skills.get("from", [])
            elif "class_skills" in cls:
                available_skills = cls.get("class_skills", [])
                choices = cls.get("skill_choices", 0)
            
            if available_skills:
                self.wiz_skills.clear()
                for skill in available_skills:
                    self.wiz_skills.addItem(skill)
                
                self.wiz_skills_label.setText(f"S─▒n─▒f Becerileri ({choices} se├ğim):")
            
            # B├╝y├╝ s─▒n─▒flar─▒ i├ğin b├╝y├╝ se├ğimi (cantrip ve 1. seviye)
            if "spells" in cls:
                spells = cls.get("spells", {})
                cantrips = spells.get("cantrips", [])
                level1 = spells.get("1st_level", []) or spells.get("level1", [])
                
                # Cantrip se├ğim say─▒s─▒ (s─▒n─▒fa ├Âzel veya varsay─▒lan)
                cantrip_choices = spells.get("cantrip_known_at_1")
                if cantrip_choices is None:
                    if class_name in ("Wizard", "Cleric"):
                        cantrip_choices = 3
                    elif class_name == "Druid":
                        cantrip_choices = 2
                    else:
                        cantrip_choices = 2
                
                # 1. seviye b├╝y├╝ se├ğim say─▒s─▒ (s─▒n─▒fa ├Âzel veya varsay─▒lan)
                level1_choices = spells.get("level1_known_at_1")
                if level1_choices is None:
                    if class_name == "Wizard":
                        level1_choices = 6
                    elif class_name in ("Cleric", "Druid"):
                        level1_choices = 2
                    else:
                        level1_choices = 2
                
                if cantrips:
                    self.wiz_cantrips.clear()
                    for spell in cantrips:
                        self.wiz_cantrips.addItem(spell)
                    self.wiz_cantrips_label.setText(f"Cantrip Se├ğimi ({cantrip_choices} se├ğim):")
                    self.wiz_cantrips.setVisible(True)
                
                if level1:
                    self.wiz_level1.clear()
                    for spell in level1:
                        self.wiz_level1.addItem(spell)
                    self.wiz_level1_label.setText(f"1. Seviye B├╝y├╝ler ({level1_choices} se├ğim):")
                    self.wiz_level1.setVisible(True)
            
            # Rogue i├ğin expertise
            if class_name == "Rogue":
                all_skills = list(self.data.get("skills", {}).keys())
                for skill in all_skills:
                    self.wiz_expertise.addItem(skill)
                self.wiz_expertise_label.setText("Uzmanl─▒k (Expertise) Se├ğimi (2 se├ğim):")
                self.wiz_expertise.setVisible(True)

    def _refresh_class_features(self):
        """S─▒n─▒f ├Âzelliklerini g├╝ncelle"""
        if not hasattr(self, 'class_cb') or not self.class_cb:
            return
        class_name = self.class_cb.currentText()
        level = 1  # Karakter olu┼şturma seviyesi 1
        
        classes = self.data.get("classes", {})
        if class_name in classes:
            cls = classes[class_name]
            class_features = cls.get("class_features", {})
            
            # Seviyeye g├Âre ├Âzellikleri topla
            features = []
            for lvl in range(1, level + 1):
                level_features = class_features.get(str(lvl), {})
                level_features_list = level_features.get("features", [])
                features.extend(level_features_list)
            
            if not hasattr(self, 'features_list') or not self.features_list:
                return
            self.features_list.clear()
            if features:
                for feature in features:
                    self.features_list.addItem(feature)
                if hasattr(self, 'features_group'):
                    self.features_group.setVisible(True)
                if hasattr(self, 'features_label'):
                    self.features_label.setText(f"Seviye ile Gelen ├ûzellikler (1-{level}):")
            else:
                if hasattr(self, 'features_group'):
                    self.features_group.setVisible(False)

    def _refresh_feats(self):
        """Feat listesini g├╝ncelle - optimize edilmi┼ş"""
        if not hasattr(self, 'feats_list') or not self.feats_list:
            return
        self.feats_list.clear()
        
        level = 1  # Karakter olu┼şturma seviyesi 1
        race = self.race_cb.currentText()
        
        # Cache key olu┼ştur
        cache_key = f"{race}_{level}"
        
        # E─şer ayn─▒ seviye ve ─▒rk i├ğin cache varsa kullan
        if hasattr(self, '_feat_cache') and cache_key in self._feat_cache:
            cached_data = self._feat_cache[cache_key]
            self.feats_list.addItems(cached_data['items'])
            self.feats_label.setText(cached_data['label'])
            return
        
        # Cache yoksa hesapla
        if not hasattr(self, '_feat_cache'):
            self._feat_cache = {}
        
        feats = self.data.get("equipment", {}).get("feats", {})
        
        # D&D kurallar─▒: 4, 6, 8, 12, 14, 16, 19. seviyelerde feat al─▒nabilir
        # Variant Human 1. seviyede feat alabilir
        feat_allowed_levels = [4, 6, 8, 12, 14, 16, 19]
        variant_human_feat = (race == "Human" and level == 1)
        
        if level not in feat_allowed_levels and not variant_human_feat:
            self.feats_list.addItem("Bu seviyede feat al─▒namaz (4, 6, 8, 12, 14, 16, 19. seviyeler)")
            self.feats_label.setText("Feat Se├ğimi: Bu seviyede feat al─▒namaz")
            self._feat_cache[cache_key] = {
                'items': ["Bu seviyede feat al─▒namaz (4, 6, 8, 12, 14, 16, 19. seviyeler)"],
                'label': "Feat Se├ğimi: Bu seviyede feat al─▒namaz"
            }
            return
        
        items = []
        for feat_name, feat_data in sorted(feats.items()):
            prerequisites = feat_data.get("prerequisites", {})
            description = feat_data.get("description", "")
            
            # Prerequisites kontrol├╝
            meets_prereqs = self._check_feat_prerequisites(feat_name, prerequisites)
            
            # Prerequisites varsa g├Âster
            prereq_text = ""
            if prerequisites:
                prereq_list = []
                for req_type, req_value in prerequisites.items():
                    if req_type == "ability_score_minimum":
                        prereq_list.append(f"Yetenek: {req_value}")
                    elif req_type == "level":
                        prereq_list.append(f"Seviye: {req_value}")
                    else:
                        prereq_list.append(f"{req_type}: {req_value}")
                
                prereq_text = f" ({', '.join(prereq_list)})"
                if not meets_prereqs:
                    prereq_text += " [GEREKS─░N─░MLER KAR┼ŞILANMIYOR]"
            
            # Feat'i listeye ekle
            item_text = f"{feat_name}{prereq_text}"
            items.append(item_text)
            
            item = QListWidgetItem(item_text)
            self.feats_list.addItem(item)
            
            # Prerequisites kar┼ş─▒lanm─▒yorsa gri yap
            if not meets_prereqs:
                item.setForeground(QColor("gray"))
            
            # Tooltip olarak a├ğ─▒klama ekle
            if item:
                item.setToolTip(f"{feat_name}: {description}")
        
        # Seviye bazl─▒ feat say─▒s─▒n─▒ hesapla
        feat_count = self._calculate_available_feat_count(level, race)
        label_text = f"Feat Se├ğimi (Se├ğilebilir: {feat_count} adet):"
        self.feats_label.setText(label_text)
        
        # Cache'e kaydet
        self._feat_cache[cache_key] = {
            'items': items,
            'label': label_text
        }

    def _check_feat_prerequisites(self, feat_name: str, prerequisites: dict) -> bool:
        """Feat prerequisites'lerini kontrol et"""
        if not prerequisites:
            return True
        
        # Mevcut ability score'lar─▒ al
        current_scores = {}
        for ability in self.abilities:
            current_scores[ability] = self.ability_spins[ability].value()
        
        # Class ve level bilgilerini al
        class_name = self.class_cb.currentText()
        level = 1  # Karakter olu┼şturma seviyesi 1
        
        for req_type, req_value in prerequisites.items():
            if req_type == "ability_score_minimum":
                for ability, minimum in req_value.items():
                    if current_scores.get(ability, 0) < minimum:
                        return False
            elif req_type == "level":
                if level < req_value:
                    return False
            elif req_type == "proficiency":
                # Bu basit versiyonda proficiency kontrol├╝ yapm─▒yoruz
                pass
        
        return True

    def _calculate_available_feat_count(self, level: int, race: str) -> int:
        """Seviye ve ─▒rka g├Âre al─▒nabilir feat say─▒s─▒n─▒ hesapla"""
        feat_count = 0
        
        # Normal feat seviyeleri (4, 6, 8, 12, 14, 16, 19)
        for feat_level in [4, 6, 8, 12, 14, 16, 19]:
            if level >= feat_level:
                feat_count += 1
        
        # Variant Human bonus feat (1. seviye)
        if race == "Human":
            feat_count += 1
        
        return feat_count

    def _show_all_tabs(self):
        """T├╝m sekmeleri g├Âr├╝n├╝r yap"""
        if hasattr(self, 'tab_widget'):
            if hasattr(self, 'spells_tab_index'):
                self.tab_widget.setTabVisible(self.spells_tab_index, True)
            if hasattr(self, 'levelup_tab_index'):
                self.tab_widget.setTabVisible(self.levelup_tab_index, True)
            if hasattr(self, 'inventory_tab_index'):
                self.tab_widget.setTabVisible(self.inventory_tab_index, True)
            if hasattr(self, 'dice_tab_index'):
                self.tab_widget.setTabVisible(self.dice_tab_index, True)
            if hasattr(self, 'advanced_tab_index'):
                self.tab_widget.setTabVisible(self.advanced_tab_index, True)
    
    def _complete_character(self):
        """Karakteri tamamla ve PDF'e ├ğevir"""
        # Karakter kontrol├╝
        if not hasattr(self, 'current_character') or not self.current_character:
            QMessageBox.warning(self, "Uyar─▒", "├ûnce bir karakter olu┼şturun!")
            return
        
        # Son g├╝ncellemeleri kaydet
        self._auto_save_character()
        
        # T├╝m sekmeleri g├Âr├╝n├╝r yap
        self._show_all_tabs()
        
        # PDF'e ├ğevir
        self._export_to_pdf(self.current_character)

    def _create_character(self):
        """Karakter olu┼ştur (sadece veri, isim yok)"""
        # Cache kontrol├╝
        cache_key = f"summary_{self.character_name_edit.text()}_{self.race_cb.currentText()}_{self.class_cb.currentText()}_1"
        
        if hasattr(self, '_summary_cache') and cache_key in self._summary_cache:
            self.summary.setPlainText(self._summary_cache[cache_key])
            return
        
        # Cache yoksa hesapla
        if not hasattr(self, '_summary_cache'):
            self._summary_cache = {}
        
        character = {
            "name": self.character_name_edit.text().strip() or "─░simsiz Karakter",
            "race": self.race_cb.currentText(),
            "class": self.class_cb.currentText(),
            "background": self.bg_cb.currentText(),
            "level": 1,
            "abilities": {},
            "skills": {},
            "equipment": [],
            "spells": {},
            "feats": [],
            "languages": [],
            "personality": {},
            "physical": {},
            "appearance": {}
        }
        
        # Yetenek puanlar─▒ - ├Ânce t├╝m yetenekleri initialize et
        for ability in self.abilities:
            character["abilities"][ability] = self.ability_spins[ability].value()
        
        # Race bonuslar─▒
        race_name = character["race"]
        race_data = self.data.get("races", {}).get(race_name, {})
        ability_increases = race_data.get("ability_score_increase", {})
        
        for ability, bonus in ability_increases.items():
            if ability == "all":
                for abil in self.abilities:
                    character["abilities"][abil] += bonus
            else:
                character["abilities"][ability] += bonus
        
        # Se├ğilen beceriler
        selected_skills = [item.text() for item in self.wiz_skills.selectedItems()]
        character["skills"]["class_skills"] = selected_skills
        
        # Se├ğilen b├╝y├╝ler
        selected_cantrips = [item.text() for item in self.wiz_cantrips.selectedItems()]
        selected_level1 = [item.text() for item in self.wiz_level1.selectedItems()]
        
        if selected_cantrips:
            character["spells"]["cantrips"] = selected_cantrips
        if selected_level1:
            character["spells"]["1st_level"] = selected_level1
        
        # Se├ğilen feat'ler
        selected_feats = [item.text().split(" (")[0] for item in self.feats_list.selectedItems()]
        character["feats"] = selected_feats
        
        # Ki┼şisel ├Âzellikler
        character["personality"] = {
            "trait": self.trait_edit.text(),
            "ideal": self.ideal_edit.text(),
            "bond": self.bond_edit.text(),
            "flaw": self.flaw_edit.text(),
            "alignment": self.alignment_cb.currentText()
        }
        
        character["physical"] = {
            "height": self.height_edit.text(),
            "weight": self.weight_edit.text(),
            "age": self.age_edit.text()
        }
        
        character["appearance"] = {
            "hair_color": self.hair_color_edit.text(),
            "eye_color": self.eye_color_edit.text(),
            "skin_color": self.skin_color_edit.text(),
            "description": self.appearance_desc_edit.toPlainText()
        }
        
        # Resmi ekle (varsa)
        if hasattr(self, 'current_character_image_data') and self.current_character_image_data:
            character["image"] = self.current_character_image_data
        
        # ├ûzet olu┼ştur
        lines = []
        lines.append(f"─░sim: {character['name']}")
        lines.append(f"Irk: {character['race']}")
        lines.append(f"S─▒n─▒f: {character['class']}")
        lines.append(f"Arka Plan: {character['background']}")
        lines.append(f"Seviye: {character['level']}")
        lines.append("")
        lines.append("Yetenek Puanlar─▒:")
        for ability, score in character["abilities"].items():
            modifier = (score - 10) // 2
            lines.append(f"  {ability}: {score} ({modifier:+d})")
        lines.append("")
        
        # AC hesaplama
        dex_modifier = (character["abilities"].get("dexterity", 10) - 10) // 2
        base_ac = 10 + dex_modifier
        lines.append(f"Armor Class (AC): {base_ac}")
        lines.append(f"  (Base 10 + Dex Modifier {dex_modifier:+d})")
        
        # HP hesaplama
        con_modifier = (character["abilities"].get("constitution", 10) - 10) // 2
        class_hp = {"Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
                   "Artificer": 8, "Bard": 8, "Cleric": 8, "Druid": 8, 
                   "Monk": 8, "Rogue": 8, "Warlock": 8, "Sorcerer": 6, "Wizard": 6}
        char_class = character.get("class", "")
        hp_dice = class_hp.get(char_class, 6)
        max_hp = hp_dice + con_modifier + (hp_dice + con_modifier) * (character["level"] - 1)
        lines.append(f"Hit Points (HP): {max_hp}")
        lines.append(f"  ({character['level']}d{hp_dice} + {con_modifier:+d} Con modifier)")
        
        lines.append("")
        lines.append(f"Beceriler: {', '.join(character['skills'].get('class_skills', []))}")
        lines.append(f"B├╝y├╝ler: {', '.join(character['spells'].get('cantrips', []))}")
        lines.append(f"Feat'ler: {', '.join(character['feats'])}")
        lines.append("")
        lines.append(f"Alignment: {character['personality']['alignment']}")
        lines.append(f"Boy: {character['physical']['height']}")
        lines.append(f"Kilo: {character['physical']['weight']}")
        lines.append(f"Ya┼ş: {character['physical']['age']}")
        
        summary_text = "\n".join(lines)
        self.summary.setPlainText(summary_text)
        
        # Cache'e kaydet
        self._summary_cache[cache_key] = summary_text
        
        # Karakteri kaydet
        self.current_character = character
        
        # B├╝y├╝ listesini g├╝ncelle
        self._update_spells_list()
        
        # Envanteri yenile
        if hasattr(self, '_load_current_character_inventory'):
            self._load_current_character_inventory()
        
        # Level up UI's─▒n─▒ g├╝ncelle
        if hasattr(self, '_refresh_current_character_info'):
            self._refresh_current_character_info()
        
        # B├╝y├╝ Y├Ânetimi sekmesine ge├ğ
        self.tab_widget.setCurrentIndex(1)
        
        return character

    def _init_spells_ui(self):
        """B├╝y├╝ y├Ânetimi UI's─▒n─▒ olu┼ştur"""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        scroll_area.setWidget(content_widget)
        self.spells_layout.addWidget(scroll_area)
        
        # Ba┼şl─▒k
        title_label = QLabel("B├╝y├╝ Y├Ânetimi")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Karakter se├ğimi
        char_group = QGroupBox("Karakter Se├ğimi")
        char_layout = QVBoxLayout()
        
        # Mevcut karakter
        current_char_layout = QHBoxLayout()
        current_char_layout.addWidget(QLabel("Mevcut Karakter:"))
        self.spells_character_combo = QComboBox()
        self.spells_character_combo.addItem("Hen├╝z karakter olu┼şturulmad─▒")
        current_char_layout.addWidget(self.spells_character_combo)
        char_layout.addLayout(current_char_layout)
        
        # B├╝y├╝ kontrol├╝
        self.spellcasting_check_label = QLabel("")
        self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        char_layout.addWidget(self.spellcasting_check_label)
        
        char_group.setLayout(char_layout)
        layout.addWidget(char_group)
        
        # B├╝y├╝ listesi
        spells_group = QGroupBox("Mevcut B├╝y├╝ler")
        spells_layout = QVBoxLayout()
        
        self.spells_list = QListWidget()
        self.spells_list.setMaximumHeight(200)
        spells_layout.addWidget(self.spells_list)
        
        # B├╝y├╝ bilgisi
        self.spell_info = QTextEdit()
        self.spell_info.setReadOnly(True)
        self.spell_info.setMaximumHeight(150)
        self.spell_info.setPlaceholderText("Bir b├╝y├╝ se├ğin, detaylar─▒ burada g├Âr├╝necek...")
        spells_layout.addWidget(self.spell_info)
        
        spells_group.setLayout(spells_layout)
        layout.addWidget(spells_group)
        
        # B├╝y├╝ se├ğimi
        self.spell_selection_group = QGroupBox("Yeni B├╝y├╝ Se├ğimi")
        spell_selection_layout = QVBoxLayout()
        
        # B├╝y├╝ seviye se├ğimi
        spell_level_layout = QHBoxLayout()
        spell_level_layout.addWidget(QLabel("B├╝y├╝ Seviyesi:"))
        
        self.spell_level_combo = QComboBox()
        self.spell_level_combo.addItems(["Cantrip", "1. Seviye", "2. Seviye", "3. Seviye", "4. Seviye", "5. Seviye"])
        self.spell_level_combo.currentTextChanged.connect(self._on_spell_level_changed)
        spell_level_layout.addWidget(self.spell_level_combo)
        
        spell_selection_layout.addLayout(spell_level_layout)
        
        # Se├ğilebilir b├╝y├╝ler listesi
        self.available_spells_for_selection = QListWidget()
        self.available_spells_for_selection.setMaximumHeight(200)
        spell_selection_layout.addWidget(QLabel("Se├ğilebilir B├╝y├╝ler:"))
        spell_selection_layout.addWidget(self.available_spells_for_selection)
        
        # B├╝y├╝ ekleme butonu
        add_spell_btn = QPushButton("B├╝y├╝y├╝ Ekle")
        add_spell_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_spell_btn.clicked.connect(self._add_spell_to_character)
        spell_selection_layout.addWidget(add_spell_btn)
        
        self.spell_selection_group.setLayout(spell_selection_layout)
        layout.addWidget(self.spell_selection_group)
        
        # B├╝y├╝ ekleme/├ğ─▒karma
        manage_group = QGroupBox("B├╝y├╝ Y├Ânetimi")
        manage_layout = QHBoxLayout()
        
        add_spell_btn = QPushButton("B├╝y├╝ Ekle")
        add_spell_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        
        remove_spell_btn = QPushButton("B├╝y├╝ ├ç─▒kar")
        remove_spell_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        
        manage_layout.addWidget(add_spell_btn)
        manage_layout.addWidget(remove_spell_btn)
        manage_layout.addStretch()
        
        manage_group.setLayout(manage_layout)
        layout.addWidget(manage_group)
        
        # Event handler'lar
        self.spells_list.itemClicked.connect(self._show_spell_details)
        add_spell_btn.clicked.connect(self._add_spell_dialog)
        remove_spell_btn.clicked.connect(self._remove_spell)
        
        # Karakter olu┼şturuldu─şunda listeyi g├╝ncelle
        if hasattr(self, 'current_character'):
            self._update_spells_list()

        layout.addStretch()

    def _init_levelup_ui(self):
        """Seviye atlama UI's─▒n─▒ olu┼ştur"""
        outer_layout = self.levelup_layout
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(12)
        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)
        
        # Karakter se├ğimi
        char_select_group = QGroupBox("Karakter Se├ğimi")
        char_select_layout = QVBoxLayout()
        
        # Karakter combo box
        char_combo_layout = QHBoxLayout()
        char_combo_layout.addWidget(QLabel("Karakter:"))
        self.levelup_character_combo = QComboBox()
        self.levelup_character_combo.setMinimumWidth(300)
        self.levelup_character_combo.currentIndexChanged.connect(self._load_character_for_levelup)
        char_combo_layout.addWidget(self.levelup_character_combo)
        
        # Yenile butonu
        refresh_list_btn = QPushButton("Yenile")
        refresh_list_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_list_btn.clicked.connect(self._refresh_levelup_character_list)
        char_combo_layout.addWidget(refresh_list_btn)
        char_combo_layout.addStretch()
        
        char_select_layout.addLayout(char_combo_layout)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Ara:"))
        self.levelup_search_edit = QLineEdit()
        self.levelup_search_edit.setPlaceholderText("Karakter ad─▒ ile ara...")
        self.levelup_search_edit.textChanged.connect(self._filter_levelup_characters)
        search_layout.addWidget(self.levelup_search_edit)
        char_select_layout.addLayout(search_layout)
        
        char_select_group.setLayout(char_select_layout)
        layout.addWidget(char_select_group)
        
        # Mevcut karakter bilgisi
        char_info_group = QGroupBox("Mevcut Karakter")
        char_info_layout = QHBoxLayout()
        
        self.current_character_label = QLabel("Hen├╝z karakter olu┼şturulmad─▒")
        self.current_character_label.setStyleSheet("font-weight: bold; color: #3498db; font-size: 16px;")
        char_info_layout.addWidget(self.current_character_label)
        
        char_info_layout.addStretch()
        
        # Karakteri yenile butonu
        refresh_char_btn = QPushButton("Karakteri Yenile")
        refresh_char_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        refresh_char_btn.clicked.connect(self._refresh_current_character_info)
        char_info_layout.addWidget(refresh_char_btn)
        
        char_info_group.setLayout(char_info_layout)
        layout.addWidget(char_info_group)
        
        # Seviye bilgileri
        level_group = QGroupBox("Seviye Bilgileri")
        level_layout = QVBoxLayout()
        
        level_info_layout = QHBoxLayout()
        level_info_layout.addWidget(QLabel("Mevcut Seviye:"))
        self.current_level_label = QLabel("1")
        self.current_level_label.setStyleSheet("font-weight: bold; color: #27ae60;")
        level_info_layout.addWidget(self.current_level_label)
        
        level_info_layout.addWidget(QLabel("Yeni Seviye:"))
        self.new_level_spin = QSpinBox()
        self.new_level_spin.setRange(2, 20)
        self.new_level_spin.setValue(2)
        self.new_level_spin.valueChanged.connect(self._on_level_change)
        level_info_layout.addWidget(self.new_level_spin)
        
        level_layout.addLayout(level_info_layout)
        
        # HP art─▒┼ş─▒
        hp_layout = QHBoxLayout()
        hp_layout.addWidget(QLabel("HP Art─▒┼ş─▒:"))
        self.hp_gain_label = QLabel("0")
        self.hp_gain_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        hp_layout.addWidget(self.hp_gain_label)
        level_layout.addLayout(hp_layout)
        
        level_group.setLayout(level_layout)
        layout.addWidget(level_group)
        
        # Ana splitter olu┼ştur
        main_splitter = QtWidgets.QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Sol panel - Seviye atlama se├ğenekleri (Scroll Area ile)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)
        
        # S─▒n─▒f ├Âzellikleri
        features_group = QGroupBox("Yeni S─▒n─▒f ├ûzellikleri")
        features_layout = QVBoxLayout()
        
        self.new_features_list = QListWidget()
        self.new_features_list.setMaximumHeight(150)
        features_layout.addWidget(self.new_features_list)
        
        features_group.setLayout(features_layout)
        left_layout.addWidget(features_group)
        
        # ASI/Feat Se├ğimi
        asi_group = QGroupBox("ASI veya Feat Se├ğimi")
        asi_layout = QVBoxLayout()
        
        # ASI/Feat se├ğim tipi
        choice_layout = QHBoxLayout()
        choice_layout.addWidget(QLabel("Se├ğim Tipi:"))
        
        self.asi_feat_choice = QComboBox()
        self.asi_feat_choice.addItems(["ASI (Ability Score Increase)", "Feat"])
        self.asi_feat_choice.currentTextChanged.connect(self._on_asi_feat_choice_changed)
        choice_layout.addWidget(self.asi_feat_choice)
        
        asi_layout.addLayout(choice_layout)
        
        # ASI se├ğenekleri - daha kompakt
        self.asi_group = QWidget()
        asi_options_layout = QHBoxLayout()
        
        # Sol kolon - 1. Yetenek
        left_asi = QVBoxLayout()
        left_asi.addWidget(QLabel("1. Yetenek (+1):"))
        self.asi_ability1 = QComboBox()
        self.asi_ability1.addItems(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
        left_asi.addWidget(self.asi_ability1)
        
        # Sa─ş kolon - 2. Yetenek
        right_asi = QVBoxLayout()
        right_asi.addWidget(QLabel("2. Yetenek (+1):"))
        self.asi_ability2 = QComboBox()
        self.asi_ability2.addItems(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
        right_asi.addWidget(self.asi_ability2)
        
        asi_options_layout.addLayout(left_asi)
        asi_options_layout.addLayout(right_asi)
        self.asi_group.setLayout(asi_options_layout)
        asi_layout.addWidget(self.asi_group)
        
        # Feat se├ğenekleri
        self.feat_group = QWidget()
        feat_options_layout = QVBoxLayout()
        
        feat_options_layout.addWidget(QLabel("Se├ğilebilir Feat'ler:"))
        self.available_feats_list = QListWidget()
        self.available_feats_list.setMaximumHeight(150)
        feat_options_layout.addWidget(self.available_feats_list)
        
        self.feat_group.setLayout(feat_options_layout)
        self.feat_group.setVisible(False)
        asi_layout.addWidget(self.feat_group)
        
        asi_group.setLayout(asi_layout)
        left_layout.addWidget(asi_group)
        
        # Bekleyen Se├ğimler
        pending_group = QGroupBox("ÔÅ│ Bekleyen Se├ğimler")
        pending_group.setMinimumHeight(150)
        pending_layout = QVBoxLayout()
        
        self.pending_choices_list = QListWidget()
        self.pending_choices_list.setMaximumHeight(100)
        pending_layout.addWidget(QLabel("Yap─▒lmas─▒ gereken se├ğimler:"))
        pending_layout.addWidget(self.pending_choices_list)
        
        # Bekleyen se├ğimi tamamla butonu
        complete_choice_btn = QPushButton("Se├ğili Se├ğimi Tamamla")
        complete_choice_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        complete_choice_btn.clicked.connect(self._complete_pending_choice)
        pending_layout.addWidget(complete_choice_btn)
        
        pending_group.setLayout(pending_layout)
        left_layout.addWidget(pending_group)
        
        # Scroll area'ya widget'─▒ ekle
        left_scroll.setWidget(left_panel)
        main_splitter.addWidget(left_scroll)
        
        # Sa─ş panel - Karakter ├Ânizleme
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Karakter ├Ânizleme
        preview_group = QGroupBox("Karakter ├ûnizleme")
        preview_layout = QVBoxLayout()
        
        self.character_preview = QTextEdit()
        self.character_preview.setReadOnly(True)
        self.character_preview.setMaximumHeight(400)
        preview_layout.addWidget(self.character_preview)
        
        preview_group.setLayout(preview_layout)
        right_layout.addWidget(preview_group)
        
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([600, 400])
        
        # Seviye atlama butonu
        levelup_btn = QPushButton("Seviye Atlat")
        levelup_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 15px 30px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        levelup_btn.clicked.connect(self._level_up_character)
        layout.addWidget(levelup_btn)
        layout.addStretch()
        
        # Karakter listesini yenile
        self._refresh_levelup_character_list()

    def _on_asi_feat_choice_changed(self, choice):
        """ASI/Feat se├ğimi de─şi┼şti─şinde UI'yi g├╝ncelle"""
        if choice == "ASI (Ability Score Increase)":
            self.asi_group.setVisible(True)
            self.feat_group.setVisible(False)
        else:  # Feat
            self.asi_group.setVisible(False)
            self.feat_group.setVisible(True)
            self._refresh_available_feats()

    def _refresh_available_feats(self):
        """Se├ğilebilir feat'leri g├╝ncelle"""
        try:
            # Mevcut karakter kontrol├╝
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                self.available_feats_list.clear()
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Karakterin mevcut feat'lerini al
            current_feats = character_data.get("feats", [])
            
            # T├╝m feat'leri al
            all_feats = self.data.get("feats", {})
            
            self.available_feats_list.clear()
            
            for feat_name, feat_data in all_feats.items():
                # Prerequisite kontrol├╝
                prerequisites = feat_data.get("prerequisite", [])
                can_take = True
                
                for prereq in prerequisites:
                    if prereq not in current_feats:
                        can_take = False
                        break
                
                if can_take and feat_name not in current_feats:
                    feat_text = f"{feat_name}"
                    if feat_data.get("description"):
                        feat_text += f" - {feat_data['description'][:50]}..."
                    self.available_feats_list.addItem(feat_text)
                    
        except Exception as e:
            print(f"Feat listesi g├╝ncellenirken hata: {e}")

    def _filter_levelup_characters(self, search_text):
        """Seviye atlama karakter listesini filtrele"""
        try:
            if not search_text.strip():
                self._refresh_levelup_character_list()
                return
                
            search_text = search_text.lower().strip()
            filtered_count = 0
            
            for i in range(self.levelup_character_combo.count()):
                item_text = self.levelup_character_combo.itemText(i).lower()
                if search_text in item_text:
                    self.levelup_character_combo.setItemHidden(i, False)
                    filtered_count += 1
                else:
                    self.levelup_character_combo.setItemHidden(i, True)
            
            # E─şer hi├ğ sonu├ğ yoksa bilgi ver
            if filtered_count == 0:
                QMessageBox.information(self, "Arama Sonucu", "Arama kriterlerine uygun karakter bulunamad─▒.")
                
        except Exception as e:
            print(f"Karakter filtreleme hatas─▒: {e}")

    def _refresh_levelup_character_list(self):
        """Seviye atlama karakter listesini yenile (GUI ve CLI kay─▒tlar─▒ dahil)"""
        try:
            import json
            
            self.levelup_character_combo.clear()
            characters = []
            
            characters_dir = _ensure_characters_dir()
            if characters_dir.exists():
                for filepath in characters_dir.glob("*.json"):
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            char_data = json.load(f)
                        # Sadece D&D 5e karakterleri
                        system = char_data.get("system")
                        if system not in ("DND5E", "Dnd5e", "dnd5e", None):
                            continue
                        char_name = char_data.get("name", "─░simsiz")
                        char_level = char_data.get("level", 1)
                        char_class = char_data.get("class", "")
                        display_name = f"{char_name} (Seviye {char_level} {char_class})"
                        self.levelup_character_combo.addItem(display_name, str(filepath))
                        characters.append((char_name, char_level, str(filepath)))
                    except Exception as e:
                        print(f"Karakter dosyas─▒ okunamad─▒ {filepath}: {e}")
            
            if not characters:
                self.levelup_character_combo.addItem("Hen├╝z karakter olu┼şturulmad─▒")
            
            # ─░lk karakteri se├ğ ve y├╝kle
            if characters:
                self.levelup_character_combo.setCurrentIndex(0)
                self._load_character_for_levelup()
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter listesi yenilenemedi:\n{str(e)}")

    def _load_character_for_levelup(self):
        """Se├ğilen karakteri seviye atlama i├ğin y├╝kle"""
        try:
            # Combo box'tan se├ğilen karakteri al
            current_index = self.levelup_character_combo.currentIndex()
            if current_index < 0:
                return
                
            filepath = self.levelup_character_combo.itemData(current_index)
            if not filepath:
                return
                
            # current_character_file'─▒ g├╝ncelle (di─şer fonksiyonlar i├ğin)
            self.current_character_file = filepath
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            # Karakter bilgisini g├Âster
            char_name = character_data.get("name", "─░simsiz")
            char_level = character_data.get("level", 1)
            char_class = character_data.get("class", "")
            self.current_character_label.setText(f"{char_name} - Seviye {char_level} {char_class}")
                
            current_level = character_data.get("level", 1)
            self.current_level_label.setText(str(current_level))
            self.new_level_spin.setRange(current_level + 1, 20)
            self.new_level_spin.setValue(current_level + 1)
            
            # HP art─▒┼ş─▒n─▒ hesapla
            self._on_level_change()
            
            # Yeni se├ğenekleri g├╝ncelle
            self._refresh_available_feats()
            self._update_character_preview()
            self._refresh_pending_choices()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter y├╝klenemedi:\n{str(e)}")

    def _update_character_preview(self):
        """Karakter ├Ânizlemesini g├╝ncelle"""
        try:
            # Mevcut karakter kontrol├╝
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                self.character_preview.clear()
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # ├ûnizleme metni olu┼ştur
            preview_lines = []
            
            # Temel bilgiler
            preview_lines.append(f"­şÄ¡ {character_data.get('name', '─░simsiz')}")
            preview_lines.append(f"Seviye {character_data.get('level', 1)} {character_data.get('class', 'S─▒n─▒fs─▒z')}")
            preview_lines.append(f"Irk: {character_data.get('race', 'Irks─▒z')}")
            preview_lines.append("")
            
            # Yetenek puanlar─▒
            preview_lines.append("­şôè Yetenek Puanlar─▒:")
            raw_abilities = character_data.get("abilities", {})
            # CLI karakterlerinde abilities {'scores': {...}, 'modifiers': {...}} olabilir
            if isinstance(raw_abilities, dict) and "scores" in raw_abilities:
                abilities = raw_abilities.get("scores", {})
            else:
                abilities = raw_abilities
            for ability, score in abilities.items():
                try:
                    val = int(score)
                except (ValueError, TypeError):
                    continue
                modifier = (val - 10) // 2
                preview_lines.append(f"  {ability.title()}: {val} ({modifier:+d})")
            
            preview_lines.append("")
            
            # HP ve AC
            con_score =  abilities.get("constitution", 10)
            try:
                con_score = int(con_score)
            except (ValueError, TypeError):
                con_score = 10
            con_modifier = (con_score - 10) // 2
            class_hp = {
                "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
                "Artificer": 8, "Bard": 8, "Cleric": 8, "Druid": 8, 
                "Monk": 8, "Rogue": 8, "Warlock": 8, "Sorcerer": 6, "Wizard": 6
            }
            char_class = character_data.get("class", "")
            hp_dice = class_hp.get(char_class, 6)
            max_hp = hp_dice + con_modifier + (hp_dice + con_modifier) * (character_data.get("level", 1) - 1)
            
            dex_modifier = (abilities.get("dexterity", 10) - 10) // 2
            base_ac = 10 + dex_modifier
            
            preview_lines.append(f"ÔØñ´©Å HP: {max_hp}")
            preview_lines.append(f"­şøí´©Å AC: {base_ac}")
            preview_lines.append("")
            
            # Feat'ler
            feats = character_data.get("feats", [])
            if feats:
                preview_lines.append("­şÄ» Feat'ler:")
                for feat in feats:
                    preview_lines.append(f"  ÔÇó {feat}")
                preview_lines.append("")
            
            # B├╝y├╝ler
            spells = character_data.get("spells", {})
            if spells:
                preview_lines.append("­şö« B├╝y├╝ler:")
                for spell_type, spell_list in spells.items():
                    if spell_list:
                        preview_lines.append(f"  {spell_type.title()}: {', '.join(spell_list)}")
                preview_lines.append("")
            
            preview_text = "\n".join(preview_lines)
            self.character_preview.setPlainText(preview_text)
            
        except Exception as e:
            print(f"Karakter ├Ânizleme g├╝ncellenirken hata: {e}")

    def _on_level_change(self):
        """Seviye de─şi┼şti─şinde HP art─▒┼ş─▒n─▒ hesapla"""
        try:
            # Mevcut karakter kontrol├╝
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                self.hp_gain_label.setText("0")
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            current_level = character_data.get("level", 1)
            new_level = self.new_level_spin.value()
            
            if new_level <= current_level:
                self.hp_gain_label.setText("0")
                return
                
            # HP art─▒┼ş─▒n─▒ hesapla
            char_class = character_data.get("class", "")
            constitution = character_data.get("abilities", {}).get("constitution", 10)
            con_modifier = (constitution - 10) // 2
            
            # S─▒n─▒f HP dice'lar─▒
            hp_dice = {
                "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
                "Artificer": 8, "Bard": 8, "Cleric": 8, "Druid": 8, 
                "Monk": 8, "Rogue": 8, "Warlock": 8,
                "Sorcerer": 6, "Wizard": 6
            }
            
            class_hp = hp_dice.get(char_class, 6)
            hp_gain = (new_level - current_level) * (class_hp + con_modifier)
            
            self.hp_gain_label.setText(str(hp_gain))
            
            # Yeni s─▒n─▒f ├Âzelliklerini g├Âster
            self._update_class_features(new_level)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"HP hesaplanamad─▒:\n{str(e)}")

    def _update_class_features(self, new_level):
        """Yeni seviyede kazan─▒lan s─▒n─▒f ├Âzelliklerini g├╝ncelle"""
        try:
            self.new_features_list.clear()
            
            # Mevcut karakter kontrol├╝
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            char_class = character_data.get("class", "")
            current_level = character_data.get("level", 1)
            new_level = self.new_level_spin.value()
            
            if new_level <= current_level:
                return
                
            # S─▒n─▒f ├Âzelliklerini kontrol et
            classes = self.data.get("classes", {})
            if char_class in classes:
                class_data = classes[char_class]
                class_features = class_data.get("class_features", {})
                
                for level, features in class_features.items():
                    level_num = int(level)
                    if current_level < level_num <= new_level:
                        if isinstance(features, list):
                            for feature in features:
                                self.new_features_list.addItem(f"Seviye {level_num}: {feature}")
                        elif isinstance(features, dict):
                            for feature_name, feature_desc in features.items():
                                self.new_features_list.addItem(f"Seviye {level_num}: {feature_name}")
                                
        except Exception as e:
            print(f"S─▒n─▒f ├Âzellikleri g├╝ncellenemedi: {e}")

    def _level_up_character(self):
        """Karakteri seviye atlat"""
        try:
            # Mevcut karakter kontrol├╝
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen ├Ânce bir karakter olu┼şturun veya y├╝kleyin!")
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            current_level = character_data.get("level", 1)
            new_level = self.new_level_spin.value()
            
            if new_level <= current_level:
                QMessageBox.warning(self, "Uyar─▒", "Yeni seviye mevcut seviyeden b├╝y├╝k olmal─▒!")
                return
                
            # HP art─▒┼ş─▒n─▒ hesapla ve uygula
            char_class = character_data.get("class", "")
            constitution = character_data.get("abilities", {}).get("constitution", 10)
            con_modifier = (constitution - 10) // 2
            
            hp_dice = {
                "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
                "Artificer": 8, "Bard": 8, "Cleric": 8, "Druid": 8, 
                "Monk": 8, "Rogue": 8, "Warlock": 8,
                "Sorcerer": 6, "Wizard": 6
            }
            
            class_hp = hp_dice.get(char_class, 6)
            hp_gain = (new_level - current_level) * (class_hp + con_modifier)
            
            # ASI/Feat se├ğimi
            if new_level in [4, 6, 8, 12, 16, 19]:  # ASI seviyeleri
                choice = self.asi_feat_choice.currentText()
                if choice == "ASI (Ability Score Increase)":
                    # ASI uygula
                    ability1 = self.asi_ability1.currentText().lower()
                    ability2 = self.asi_ability2.currentText().lower()
                    
                    if ability1 not in character_data["abilities"]:
                        character_data["abilities"][ability1] = 8
                    if ability2 not in character_data["abilities"]:
                        character_data["abilities"][ability2] = 8
                        
                    character_data["abilities"][ability1] += 1
                    character_data["abilities"][ability2] += 1
                    
                else:  # Feat
                    selected_feat = self.available_feats_list.currentItem()
                    if selected_feat:
                        feat_name = selected_feat.text().split(" - ")[0]
                        if "feats" not in character_data:
                            character_data["feats"] = []
                        character_data["feats"].append(feat_name)
                    else:
                        # Feat se├ğilmediyse bekleyen se├ğimlere ekle
                        if "pending_choices" not in character_data:
                            character_data["pending_choices"] = []
                        character_data["pending_choices"].append({
                            "type": "feat",
                            "level": new_level,
                            "description": f"Seviye {new_level} Feat Se├ğimi"
                        })
            
            # Karakteri g├╝ncelle
            character_data["level"] = new_level
            if "hp" not in character_data:
                character_data["hp"] = class_hp + con_modifier  # Seviye 1 HP
            character_data["hp"] += hp_gain
            
            # Dosyaya kaydet
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
                
            QMessageBox.information(self, "Ba┼şar─▒l─▒", 
                f"Karakter seviye {new_level}'e y├╝kseltildi!\nHP art─▒┼ş─▒: +{hp_gain}")
            
            # Mevcut karakter bilgisini yenile
            self._refresh_current_character_info()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Seviye atlama ba┼şar─▒s─▒z:\n{str(e)}")

    def _refresh_pending_choices(self):
        """Bekleyen se├ğimleri g├╝ncelle"""
        try:
            # Mevcut karakter kontrol├╝
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                self.pending_choices_list.clear()
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Bekleyen se├ğimleri temizle
            self.pending_choices_list.clear()
            
            # Bekleyen se├ğimleri listele
            pending_choices = character_data.get("pending_choices", [])
            for choice in pending_choices:
                choice_text = f"Seviye {choice['level']}: {choice['description']}"
                item = QListWidgetItem(choice_text)
                item.setData(Qt.UserRole, choice)  # Se├ğim verisini sakla
                self.pending_choices_list.addItem(item)
                
        except Exception as e:
            print(f"Bekleyen se├ğimler g├╝ncellenirken hata: {e}")

    def _complete_pending_choice(self):
        """Se├ğili bekleyen se├ğimi tamamla"""
        try:
            selected_item = self.pending_choices_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen tamamlamak istedi─şiniz se├ğimi se├ğin!")
                return
            
            choice_data = selected_item.data(Qt.UserRole)
            choice_type = choice_data.get("type")
            
            if choice_type == "feat":
                self._complete_pending_feat_choice(choice_data)
            else:
                QMessageBox.information(self, "Bilgi", f"Bu se├ğim t├╝r├╝ hen├╝z desteklenmiyor: {choice_type}")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bekleyen se├ğim tamamlan─▒rken hata olu┼ştu:\n{str(e)}")

    def _complete_pending_feat_choice(self, choice_data):
        """Bekleyen feat se├ğimini tamamla"""
        try:
            # Feat se├ğim dialog'u a├ğ
            feat_dialog = QDialog(self)
            feat_dialog.setWindowTitle(f"Feat Se├ğimi - {choice_data['description']}")
            feat_dialog.setModal(True)
            feat_dialog.resize(500, 400)
            
            layout = QVBoxLayout(feat_dialog)
            
            # Ba┼şl─▒k
            title_label = QLabel(f"Seviye {choice_data['level']} i├ğin feat se├ğin:")
            title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(title_label)
            
            # Mevcut karakter bilgilerini al
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                QMessageBox.warning(self, "Uyar─▒", "Mevcut karakter bulunamad─▒!")
                return
                
            filepath = self.current_character_file
            
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Se├ğilebilir feat'leri al
            current_feats = character_data.get("feats", [])
            all_feats = self.data.get("feats", {})
            
            feat_list = QListWidget()
            for feat_name, feat_data in all_feats.items():
                # Prerequisite kontrol├╝
                prerequisites = feat_data.get("prerequisite", [])
                can_take = True
                
                for prereq in prerequisites:
                    if prereq not in current_feats:
                        can_take = False
                        break
                
                if can_take and feat_name not in current_feats:
                    feat_text = f"{feat_name}"
                    if feat_data.get("description"):
                        feat_text += f" - {feat_data['description'][:100]}..."
                    feat_list.addItem(feat_text)
            
            layout.addWidget(feat_list)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            cancel_btn = QPushButton("─░ptal")
            cancel_btn.clicked.connect(feat_dialog.reject)
            button_layout.addWidget(cancel_btn)
            
            select_btn = QPushButton("Se├ğ")
            select_btn.setStyleSheet("""
                QPushButton {
                    background-color: #27ae60;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #229954;
                }
            """)
            
            def on_feat_selected():
                selected_feat = feat_list.currentItem()
                if not selected_feat:
                    QMessageBox.warning(feat_dialog, "Uyar─▒", "L├╝tfen bir feat se├ğin!")
                    return
                
                feat_name = selected_feat.text().split(" - ")[0]
                
                # Feat'i karaktere ekle
                if "feats" not in character_data:
                    character_data["feats"] = []
                character_data["feats"].append(feat_name)
                
                # Bekleyen se├ğimi kald─▒r
                pending_choices = character_data.get("pending_choices", [])
                pending_choices = [c for c in pending_choices if c != choice_data]
                character_data["pending_choices"] = pending_choices
                
                # Dosyaya kaydet
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(character_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(feat_dialog, "Ba┼şar─▒l─▒", f"{feat_name} feat'i eklendi!")
                feat_dialog.accept()
                
                # Listeleri yenile
                self._refresh_current_character_info()
                self._refresh_pending_choices()
                self._update_character_preview()
            
            select_btn.clicked.connect(on_feat_selected)
            button_layout.addWidget(select_btn)
            
            layout.addLayout(button_layout)
            feat_dialog.exec()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Feat se├ğimi tamamlan─▒rken hata olu┼ştu:\n{str(e)}")

    def _refresh_current_character_info(self):
        """Mevcut karakter bilgisini yenile"""
        try:
            if hasattr(self, 'current_character') and self.current_character:
                char_name = self.current_character.get('name', '─░simsiz')
                char_level = self.current_character.get('level', 1)
                char_class = self.current_character.get('class', 'S─▒n─▒fs─▒z')
                
                info_text = f"{char_name} - Seviye {char_level} {char_class}"
                self.current_character_label.setText(info_text)
                
                # Seviye bilgilerini g├╝ncelle
                self.current_level_label.setText(str(char_level))
                self.new_level_spin.setValue(char_level + 1)
                
                # HP art─▒┼ş─▒n─▒ hesapla
                self._on_level_change()
                
                # Yeni se├ğenekleri g├╝ncelle
                self._refresh_available_feats()
                self._update_character_preview()
                self._refresh_pending_choices()
            else:
                self.current_character_label.setText("Hen├╝z karakter olu┼şturulmad─▒")
                self.current_level_label.setText("1")
                self.new_level_spin.setValue(2)
                
        except Exception as e:
            print(f"Karakter bilgisi yenilenirken hata: {e}")

    def _init_inventory_ui(self):
        """Envanter UI's─▒n─▒ olu┼ştur"""
        layout = self.inventory_layout
        
        # Ana splitter (sol: envanter, sa─ş: e┼şya detaylar─▒)
        main_splitter = QtWidgets.QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Sol panel - Envanter (Scroll Area ile)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)
        
        
        # Envanter listesi (kompakt)
        inventory_group = QGroupBox()
        inventory_group.setTitle("")  # Ba┼şl─▒─ş─▒ kald─▒r
        inventory_group.setContentsMargins(3, 3, 3, 3)
        inventory_layout = QVBoxLayout()
        inventory_layout.setContentsMargins(3, 3, 3, 3)
        inventory_layout.setSpacing(2)
        
        self.inventory_list = QListWidget()
        self.inventory_list.setMinimumHeight(100)
        self.inventory_list.itemClicked.connect(self._show_item_details)
        inventory_layout.addWidget(self.inventory_list)
        
        # Envanter butonlar─▒ (kompakt)
        item_buttons_layout = QHBoxLayout()
        
        add_item_btn = QPushButton("E┼şya Ekle")
        add_item_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 4px 8px;
                font-weight: bold;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_item_btn.clicked.connect(self._show_item_categories)
        item_buttons_layout.addWidget(add_item_btn)
        
        remove_item_btn = QPushButton("E┼şya ├ç─▒kar")
        remove_item_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 4px 8px;
                font-weight: bold;
                border-radius: 3px;
                font-size: 11px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_item_btn.clicked.connect(self._remove_item)
        item_buttons_layout.addWidget(remove_item_btn)
        
        inventory_layout.addLayout(item_buttons_layout)
        inventory_group.setLayout(inventory_layout)
        left_layout.addWidget(inventory_group)
        
        # Envanter ├Âzeti (kompakt)
        summary_group = QGroupBox()
        summary_group.setTitle("")  # Ba┼şl─▒─ş─▒ kald─▒r
        summary_group.setContentsMargins(3, 3, 3, 3)
        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(3, 3, 3, 3)
        
        self.weight_label = QLabel("A─ş─▒rl─▒k: 0 lb")
        self.weight_label.setStyleSheet("font-weight: bold; color: #f39c12; font-size: 11px;")
        summary_layout.addWidget(self.weight_label)
        
        self.gold_label = QLabel("Alt─▒n: 0 gp")
        self.gold_label.setStyleSheet("font-weight: bold; color: #f1c40f; font-size: 11px;")
        summary_layout.addWidget(self.gold_label)
        
        summary_group.setLayout(summary_layout)
        left_layout.addWidget(summary_group)
        
        # E┼şya kategorileri (ana b├Âl├╝m)
        categories_group = QGroupBox("­şôï D&D 5e E┼şya Kategorileri")
        categories_group.setContentsMargins(5, 5, 5, 5)
        categories_group.setMinimumHeight(300)
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(5, 5, 5, 5)
        categories_layout.setSpacing(3)
        
        # Kategoriler i├ğin tab widget
        self.categories_tabs = QTabWidget()
        
        # Silahlar sekmesi
        self.weapons_tab = QtWidgets.QWidget()
        self.weapons_list = QListWidget()
        weapons_layout = QVBoxLayout()
        weapons_layout.addWidget(self.weapons_list)
        self.weapons_tab.setLayout(weapons_layout)
        self.categories_tabs.addTab(self.weapons_tab, "ÔÜö´©Å Silahlar")
        
        # Z─▒rhlar sekmesi
        self.armor_tab = QtWidgets.QWidget()
        self.armor_list = QListWidget()
        armor_layout = QVBoxLayout()
        armor_layout.addWidget(self.armor_list)
        self.armor_tab.setLayout(armor_layout)
        self.categories_tabs.addTab(self.armor_tab, "­şøí´©Å Z─▒rhlar")
        
        # Macera e┼şyalar─▒ sekmesi (tab widget i├ğinde)
        self.adventure_gear_tab = QtWidgets.QWidget()
        adventure_gear_layout = QVBoxLayout()
        
        # Macera e┼şyalar─▒ i├ğin alt tab widget
        self.adventure_gear_subtabs = QTabWidget()
        
        # Alt kategoriler
        self.storage_tab = QtWidgets.QWidget()
        self.storage_list = QListWidget()
        storage_layout = QVBoxLayout()
        storage_layout.addWidget(self.storage_list)
        self.storage_tab.setLayout(storage_layout)
        self.adventure_gear_subtabs.addTab(self.storage_tab, "­şôĞ Depolama")
        
        self.tools_tab = QtWidgets.QWidget()
        self.tools_list = QListWidget()
        tools_layout = QVBoxLayout()
        tools_layout.addWidget(self.tools_list)
        self.tools_tab.setLayout(tools_layout)
        self.adventure_gear_subtabs.addTab(self.tools_tab, "­şöğ Ara├ğlar")
        
        self.focus_tab = QtWidgets.QWidget()
        self.focus_list = QListWidget()
        focus_layout = QVBoxLayout()
        focus_layout.addWidget(self.focus_list)
        self.focus_tab.setLayout(focus_layout)
        self.adventure_gear_subtabs.addTab(self.focus_tab, "­şö« B├╝y├╝ Odaklar─▒")
        
        self.clothing_tab = QtWidgets.QWidget()
        self.clothing_list = QListWidget()
        clothing_layout = QVBoxLayout()
        clothing_layout.addWidget(self.clothing_list)
        self.clothing_tab.setLayout(clothing_layout)
        self.adventure_gear_subtabs.addTab(self.clothing_tab, "­şæò Giysiler")
        
        self.other_tab = QtWidgets.QWidget()
        self.other_list = QListWidget()
        other_layout = QVBoxLayout()
        other_layout.addWidget(self.other_list)
        self.other_tab.setLayout(other_layout)
        self.adventure_gear_subtabs.addTab(self.other_tab, "­şÄ» Di─şer")
        
        adventure_gear_layout.addWidget(self.adventure_gear_subtabs)
        self.adventure_gear_tab.setLayout(adventure_gear_layout)
        self.categories_tabs.addTab(self.adventure_gear_tab, "­şÄÆ Macera E┼şyalar─▒")
        
        categories_layout.addWidget(self.categories_tabs)
        
        # Kategorilerden e┼şya ekleme butonu
        add_from_category_btn = QPushButton("Se├ğili E┼şyay─▒ Envantere Ekle")
        add_from_category_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 6px 12px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_from_category_btn.clicked.connect(self._add_selected_item_from_category)
        categories_layout.addWidget(add_from_category_btn)
        
        categories_group.setLayout(categories_layout)
        
        # Scroll area'ya widget'─▒ ekle
        left_scroll.setWidget(left_panel)
        
        # E┼şya kategorileri b├Âl├╝m├╝n├╝ scroll area d─▒┼ş─▒na ekle
        left_layout.addWidget(categories_group)
        
        # Kategori listelerini doldur
        self._populate_item_categories()
        
        main_splitter.addWidget(left_scroll)
        
        # Sa─ş panel - E┼şya detaylar─▒
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        details_group = QGroupBox("E┼şya Detaylar─▒")
        details_layout = QVBoxLayout()
        
        self.item_details_text = QTextEdit()
        self.item_details_text.setReadOnly(True)
        self.item_details_text.setMinimumHeight(300)
        details_layout.addWidget(self.item_details_text)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 600])
        
        # Mevcut karakterin envanterini y├╝kle
        self._load_current_character_inventory()

    def _load_current_character_inventory(self):
        """Mevcut karakterin envanterini y├╝kle"""
        try:
            if hasattr(self, 'current_character_file') and self.current_character_file:
                import json
                with open(self.current_character_file, 'r', encoding='utf-8') as f:
                    character_data = json.load(f)
                
                # Envanteri temizle
                self.inventory_list.clear()
                
                # Envanter e┼şyalar─▒n─▒ y├╝kle
                equipment = character_data.get("equipment", [])
                for item in equipment:
                    item_name = item.get('name', '─░simsiz E┼şya')
                    quantity = item.get('quantity', 1)
                    category = item.get('category', '')
                    
                    # E┼şya tipine g├Âre ikon ekle
                    if item.get('type') == 'weapon':
                        icon = "ÔÜö´©Å"
                    elif item.get('type') == 'armor':
                        icon = "­şøí´©Å"
                    elif item.get('type') == 'gear':
                        icon = "­şÄÆ"
                    else:
                        icon = "­şôĞ"
                    
                    item_text = f"{icon} {item_name}"
                    if quantity > 1:
                        item_text += f" x{quantity}"
                    if category:
                        item_text += f" ({category})"
                    
                    self.inventory_list.addItem(item_text)
                
                # Envanter ├Âzetini g├╝ncelle
                self._update_inventory_summary(character_data)
            else:
                # Karakter yoksa envanteri temizle
                self.inventory_list.clear()
                self.weight_label.setText("A─ş─▒rl─▒k: 0 lb")
                self.gold_label.setText("Alt─▒n: 0 gp")
                
        except Exception as e:
            print(f"Envanter y├╝klenemedi: {e}")

    def _populate_item_categories(self):
        """E┼şya kategorilerini doldur"""
        try:
            # Silahlar
            weapons = self.data.get("equipment", {}).get("weapons", {})
            self.weapons_list.clear()
            for weapon_name, weapon_data in weapons.items():
                cost = weapon_data.get("cost", "0 gp")
                weight = weapon_data.get("weight", 0)
                damage = weapon_data.get("damage", "")
                item_text = f"{weapon_name} - {cost} ({weight} lb)"
                if damage:
                    item_text += f" - {damage}"
                self.weapons_list.addItem(item_text)
            
            # Z─▒rhlar
            armor = self.data.get("equipment", {}).get("armor", {})
            self.armor_list.clear()
            for armor_name, armor_data in armor.items():
                cost = armor_data.get("cost", "0 gp")
                weight = armor_data.get("weight", 0)
                ac = armor_data.get("ac", "")
                item_text = f"{armor_name} - {cost} ({weight} lb)"
                if ac:
                    item_text += f" - AC {ac}"
                self.armor_list.addItem(item_text)
            
            # Macera e┼şyalar─▒ kategorilere ay─▒r
            adventure_gear = self.data.get("equipment", {}).get("adventuring_gear", {})
        
            # Kategorileri temizle
            self.storage_list.clear()
            self.tools_list.clear()
            self.focus_list.clear()
            self.clothing_list.clear()
            self.other_list.clear()
            
            # Kategorilere g├Âre e┼şyalar─▒ ay─▒r
            for gear_name, gear_data in adventure_gear.items():
                cost = gear_data.get("cost", "0 gp")
                weight = gear_data.get("weight", 0)
                description = gear_data.get("description", "")
                item_text = f"{gear_name} - {cost} ({weight} lb)"
                
                # Kategori belirleme
                category = self._categorize_adventure_gear(gear_name, description)
                
                if category == "storage":
                    self.storage_list.addItem(item_text)
                elif category == "tools":
                    self.tools_list.addItem(item_text)
                elif category == "focus":
                    self.focus_list.addItem(item_text)
                elif category == "clothing":
                    self.clothing_list.addItem(item_text)
                else:
                    self.other_list.addItem(item_text)
                
        except Exception as e:
            print(f"E┼şya kategorileri y├╝klenirken hata: {e}")

    def _categorize_adventure_gear(self, gear_name, description):
        """Macera e┼şyalar─▒n─▒ kategorilere ay─▒r"""
        gear_name_lower = gear_name.lower()
        description_lower = description.lower()
        
        # Depolama e┼şyalar─▒
        storage_keywords = [
            "backpack", "bag", "barrel", "basket", "bottle", "bucket", 
            "chest", "case", "pouch", "sack", "vial", "flask", "tankard",
            "waterskin", "container", "storage"
        ]
        
        # Ara├ğlar
        tools_keywords = [
            "hammer", "crowbar", "grappling", "block and tackle", "climber's kit",
            "fishing tackle", "healer's kit", "hunting trap", "ball bearings",
            "caltrops", "chain", "chalk", "rope", "lantern", "torch", "oil",
            "spike", "tinderbox", "tool", "kit", "lock", "pick", "shovel",
            "tent", "bedroll", "blanket", "bell", "candle", "lamp"
        ]
        
        # B├╝y├╝ odaklar─▒
        focus_keywords = [
            "arcane focus", "druidic focus", "holy symbol", "component pouch",
            "crystal", "orb", "rod", "staff", "wand", "amulet", "emblem",
            "reliquary", "totem", "mistletoe", "yew"
        ]
        
        # Giysiler
        clothing_keywords = [
            "clothes", "costume", "fine", "common", "traveler", "clothing",
            "robe", "vest", "hat", "cap", "boots", "gloves"
        ]
        
        # Kontrol et
        for keyword in storage_keywords:
            if keyword in gear_name_lower or keyword in description_lower:
                return "storage"
        
        for keyword in tools_keywords:
            if keyword in gear_name_lower or keyword in description_lower:
                return "tools"
        
        for keyword in focus_keywords:
            if keyword in gear_name_lower or keyword in description_lower:
                return "focus"
        
        for keyword in clothing_keywords:
            if keyword in gear_name_lower or keyword in description_lower:
                return "clothing"
        
        # Di─şer (varsay─▒lan)
        return "other"

    def _show_item_categories(self):
        """E┼şya kategorilerini g├Âster"""
        if not hasattr(self, 'categories_tabs'):
            return
        
        # Kategoriler grubunu vurgula
        self.categories_tabs.setCurrentIndex(0)  # Silahlar sekmesine git
        
        # Bilgi mesaj─▒ g├Âster
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("E┼şya Ekleme")
        msg.setText("A┼şa─ş─▒daki kategorilerden bir e┼şya se├ğin ve 'Se├ğili E┼şyay─▒ Envantere Ekle' butonuna t─▒klay─▒n.")
        msg.setInformativeText("ÔÇó ÔÜö´©Å Silahlar sekmesinde silahlar\nÔÇó ­şøí´©Å Z─▒rhlar sekmesinde z─▒rhlar\nÔÇó ­şÄÆ Macera E┼şyalar─▒ sekmesinde:\n  - ­şôĞ Depolama e┼şyalar─▒\n  - ­şöğ Ara├ğlar\n  - ­şö« B├╝y├╝ Odaklar─▒\n  - ­şæò Giysiler\n  - ­şÄ» Di─şer")
        msg.exec()

    def _add_selected_item_from_category(self):
        """Se├ğili e┼şyay─▒ envantere ekle"""
        try:
            # Hangi sekme aktif?
            current_tab = self.categories_tabs.currentIndex()
            
            if current_tab == 0:  # Silahlar
                selected_item = self.weapons_list.currentItem()
                item_data = self.data.get("equipment", {}).get("weapons", {})
            elif current_tab == 1:  # Z─▒rhlar
                selected_item = self.armor_list.currentItem()
                item_data = self.data.get("equipment", {}).get("armor", {})
            elif current_tab == 2:  # Macera e┼şyalar─▒
                # Alt sekme kontrol├╝
                sub_tab = self.adventure_gear_subtabs.currentIndex()
                if sub_tab == 0:  # Depolama
                    selected_item = self.storage_list.currentItem()
                elif sub_tab == 1:  # Ara├ğlar
                    selected_item = self.tools_list.currentItem()
                elif sub_tab == 2:  # B├╝y├╝ Odaklar─▒
                    selected_item = self.focus_list.currentItem()
                elif sub_tab == 3:  # Giysiler
                    selected_item = self.clothing_list.currentItem()
                elif sub_tab == 4:  # Di─şer
                    selected_item = self.other_list.currentItem()
                else:
                    return
                
                item_data = self.data.get("equipment", {}).get("adventuring_gear", {})
            
            if not selected_item:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Uyar─▒", "L├╝tfen eklemek istedi─şiniz e┼şyay─▒ se├ğin!")
                return
            
            # E┼şya ad─▒n─▒ parse et (format: "E┼şya Ad─▒ - 10 gp (5 lb)")
            item_text = selected_item.text()
            item_name = item_text.split(" - ")[0]
            
            # E┼şya verilerini al
            if item_name not in item_data:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Hata", "E┼şya verileri bulunamad─▒!")
                return
            
            item_info = item_data[item_name]
            
            # Miktar sor
            from PySide6.QtWidgets import QInputDialog
            quantity, ok = QInputDialog.getInt(None, "Miktar", f"{item_name} ka├ğ adet eklemek istiyorsunuz?", 1, 1, 1000)
            
            if not ok:
                return
            
            # Mevcut karakter kontrol├╝
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Uyar─▒", "L├╝tfen ├Ânce bir karakter olu┼şturun!")
                return
            
            character_file = self.current_character_file
            
            try:
                import json
                with open(character_file, 'r', encoding='utf-8') as f:
                    character_data = json.load(f)
            except:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Hata", "Karakter dosyas─▒ y├╝klenemedi!")
                return
            
            # Yeni e┼şya olu┼ştur
            new_item = {
                "name": item_name,
                "category": "Silah" if current_tab == 0 else "Z─▒rh" if current_tab == 1 else "Macera E┼şyas─▒",
                "weight": item_info.get("weight", 0),
                "cost": item_info.get("cost", "0 gp"),
                "quantity": quantity
            }
            
            # Silah ├Âzellikleri
            if current_tab == 0:  # Silahlar
                new_item["damage"] = item_info.get("damage", "")
                new_item["properties"] = item_info.get("properties", "")
            
            # Z─▒rh ├Âzellikleri
            elif current_tab == 1:  # Z─▒rhlar
                new_item["ac"] = item_info.get("ac", "")
                new_item["armor_type"] = item_info.get("armor_type", "")
            
            # Macera e┼şyas─▒ ├Âzellikleri
            else:
                new_item["description"] = item_info.get("description", "")
            
            # E┼şyay─▒ karaktere ekle
            if "equipment" not in character_data:
                character_data["equipment"] = []
            
            character_data["equipment"].append(new_item)
            
            # Karakteri kaydet
            with open(character_file, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
            
            # Envanteri yenile
            self._load_current_character_inventory()
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(None, "Ba┼şar─▒l─▒", f"{item_name} x{quantity} envantere eklendi!")
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Hata", f"E┼şya eklenirken hata olu┼ştu: {e}")

    def _refresh_inventory_character_list(self):
        """Envanter karakter listesini yenile"""
        try:
            import os
            import json
            
            self.inventory_character_combo.clear()
            characters = []
            
            if os.path.exists("characters"):
                for filename in os.listdir("characters"):
                    if filename.endswith("_karakter.json"):
                        filepath = os.path.join("characters", filename)
                        try:
                            with open(filepath, 'r', encoding='utf-8') as f:
                                char_data = json.load(f)
                                char_name = char_data.get("name", "─░simsiz")
                                char_level = char_data.get("level", 1)
                                char_class = char_data.get("class", "")
                                display_name = f"{char_name} (Seviye {char_level} {char_class})"
                                self.inventory_character_combo.addItem(display_name, filepath)
                                characters.append((char_name, char_level, filepath))
                        except Exception as e:
                            print(f"Karakter dosyas─▒ okunamad─▒ {filename}: {e}")
            
            if not characters:
                self.inventory_character_combo.addItem("Hen├╝z karakter olu┼şturulmad─▒")
            
            # ─░lk karakteri se├ğ ve envanteri y├╝kle
            if characters:
                self.inventory_character_combo.setCurrentIndex(0)
                self._load_character_inventory()
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter listesi yenilenemedi:\n{str(e)}")

    def _load_character_inventory(self):
        """Se├ğilen karakterin envanterini y├╝kle"""
        try:
            current_index = self.inventory_character_combo.currentIndex()
            if current_index < 0:
                return
                
            filepath = self.inventory_character_combo.itemData(current_index)
            if not filepath:
                return
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            # Envanteri temizle
            self.inventory_list.clear()
            
            # Envanter e┼şyalar─▒n─▒ y├╝kle
            equipment = character_data.get("equipment", [])
            for item in equipment:
                item_name = item.get('name', '─░simsiz E┼şya')
                quantity = item.get('quantity', 1)
                category = item.get('category', '')
                
                # E┼şya tipine g├Âre ikon ekle
                if item.get('type') == 'weapon':
                    icon = "ÔÜö´©Å"
                elif item.get('type') == 'armor':
                    icon = "­şøí´©Å"
                elif item.get('type') == 'gear':
                    icon = "­şÄÆ"
                else:
                    icon = "­şôĞ"
                
                item_text = f"{icon} {item_name}"
                if quantity > 1:
                    item_text += f" x{quantity}"
                if category:
                    item_text += f" ({category})"
                
                self.inventory_list.addItem(item_text)
            
            # Envanter ├Âzetini g├╝ncelle
            self._update_inventory_summary(character_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Envanter y├╝klenemedi:\n{str(e)}")

    def _update_inventory_summary(self, character_data):
        """Envanter ├Âzetini g├╝ncelle"""
        try:
            equipment = character_data.get("equipment", [])
            total_weight = 0
            total_gold = 0
            
            for item in equipment:
                # A─ş─▒rl─▒k hesaplama
                weight = item.get('weight', 0)
                quantity = item.get('quantity', 1)
                total_weight += weight * quantity
                
                # Alt─▒n hesaplama - cost field'─▒ndan parse et
                cost_str = item.get('cost', '0 gp')
                try:
                    # "10 gp", "5 sp" gibi formatlar─▒ parse et
                    if 'gp' in cost_str:
                        gold_value = float(cost_str.replace('gp', '').strip())
                        total_gold += gold_value * quantity
                    elif 'sp' in cost_str:
                        silver_value = float(cost_str.replace('sp', '').strip())
                        total_gold += (silver_value / 10) * quantity  # 10 sp = 1 gp
                    elif 'cp' in cost_str:
                        copper_value = float(cost_str.replace('cp', '').strip())
                        total_gold += (copper_value / 100) * quantity  # 100 cp = 1 gp
                except:
                    pass  # Parse edilemeyen de─şerleri g├Ârmezden gel
            
            self.weight_label.setText(f"Toplam A─ş─▒rl─▒k: {total_weight} lb")
            
            # Karakterin alt─▒n miktar─▒n─▒ da kontrol et
            character_gold = character_data.get("gold", 0)
            self.gold_label.setText(f"Alt─▒n: {total_gold + character_gold} gp")
            
        except Exception as e:
            print(f"Envanter ├Âzeti g├╝ncellenemedi: {e}")

    def _show_item_details(self, item):
        """Se├ğili e┼şyan─▒n detaylar─▒n─▒ g├Âster"""
        try:
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            equipment = character_data.get("equipment", [])
            item_index = self.inventory_list.row(item)
            
            if 0 <= item_index < len(equipment):
                item_data = equipment[item_index]
                
                # E┼şya ad─▒ ve ikon
                item_name = item_data.get('name', '─░simsiz E┼şya')
                item_type = item_data.get('type', 'gear')
                
                # ─░kon belirleme
                if item_type == 'weapon':
                    icon = "ÔÜö´©Å"
                elif item_type == 'armor':
                    icon = "­şøí´©Å"
                else:
                    icon = "­şÄÆ"
                
                details = f"<h3>{icon} {item_name}</h3><br>"
                
                # Temel bilgiler
                details += "<b>­şôï Temel Bilgiler:</b><br>"
                
                if 'category' in item_data:
                    details += f"ÔÇó <b>Kategori:</b> {item_data['category']}<br>"
                
                if 'cost' in item_data:
                    details += f"ÔÇó <b>De─şer:</b> {item_data['cost']}<br>"
                
                if 'weight' in item_data:
                    weight = item_data['weight']
                    total_weight = weight * item_data.get('quantity', 1)
                    details += f"ÔÇó <b>A─ş─▒rl─▒k:</b> {weight} lb (Toplam: {total_weight} lb)<br>"
                
                if 'quantity' in item_data:
                    details += f"ÔÇó <b>Miktar:</b> {item_data['quantity']}<br>"
                
                details += "<br>"
                
                # E┼şya tipine g├Âre ├Âzel bilgiler
                if item_type == 'weapon':
                    details += "<b>ÔÜö´©Å Silah Bilgileri:</b><br>"
                    
                    if 'damage' in item_data:
                        details += f"ÔÇó <b>Hasar:</b> {item_data['damage']}<br>"
                    
                    if 'versatile_damage' in item_data and item_data['versatile_damage']:
                        details += f"ÔÇó <b>├çok Ama├ğl─▒ Hasar:</b> {item_data['versatile_damage']}<br>"
                    
                    if 'weapon_type' in item_data:
                        weapon_type_tr = {"melee": "Yak─▒n D├Âv├╝┼ş", "ranged": "Uzak D├Âv├╝┼ş"}
                        details += f"ÔÇó <b>T├╝r:</b> {weapon_type_tr.get(item_data['weapon_type'], item_data['weapon_type'])}<br>"
                    
                    if 'range' in item_data and item_data['range']:
                        details += f"ÔÇó <b>Menzil:</b> {item_data['range']}<br>"
                    
                    if 'thrown' in item_data:
                        thrown_tr = "Evet" if item_data['thrown'] else "Hay─▒r"
                        details += f"ÔÇó <b>F─▒rlat─▒labilir:</b> {thrown_tr}<br>"
                    
                    if 'properties' in item_data and item_data['properties']:
                        properties = item_data['properties']
                        if isinstance(properties, list):
                            properties_tr = {
                                "Light": "Hafif", "Heavy": "A─ş─▒r", "Finesse": "├çeviklik", 
                                "Two-handed": "─░ki Elle", "Versatile": "├çok Ama├ğl─▒",
                                "Ammunition": "Cephane", "Loading": "Y├╝kleme",
                                "Reach": "Uzun Menzil", "Thrown": "F─▒rlat─▒labilir"
                            }
                            properties_display = [properties_tr.get(p, p) for p in properties]
                            details += f"ÔÇó <b>├ûzellikler:</b> {', '.join(properties_display)}<br>"
                
                elif item_type == 'armor':
                    details += "<b>­şøí´©Å Z─▒rh Bilgileri:</b><br>"
                    
                    if 'ac' in item_data:
                        details += f"ÔÇó <b>Z─▒rh S─▒n─▒f─▒:</b> {item_data['ac']}<br>"
                    
                    if 'armor_type' in item_data:
                        armor_type_tr = {
                            "light": "Hafif Z─▒rh", "medium": "Orta Z─▒rh", 
                            "heavy": "A─ş─▒r Z─▒rh", "shield": "Kalkan"
                        }
                        details += f"ÔÇó <b>Z─▒rh T├╝r├╝:</b> {armor_type_tr.get(item_data['armor_type'], item_data['armor_type'])}<br>"
                    
                    if 'max_dex' in item_data and item_data['max_dex'] is not None:
                        details += f"ÔÇó <b>Maksimum ├çeviklik Bonusu:</b> +{item_data['max_dex']}<br>"
                    
                    if 'stealth_disadvantage' in item_data:
                        stealth_tr = "Evet" if item_data['stealth_disadvantage'] else "Hay─▒r"
                        details += f"ÔÇó <b>Gizlilik Dezavantaj─▒:</b> {stealth_tr}<br>"
                
                else:  # gear/macera e┼şyas─▒
                    details += "<b>­şÄÆ Macera E┼şyas─▒ Bilgileri:</b><br>"
                    
                    if 'description' in item_data:
                        details += f"ÔÇó <b>A├ğ─▒klama:</b> {item_data['description']}<br>"
                    
                    if 'type' in item_data and item_data['type'] != 'gear':
                        details += f"ÔÇó <b>T├╝r:</b> {item_data['type']}<br>"
                
                # Ek bilgiler
                details += "<br><b>­şôØ Notlar:</b><br>"
                details += "ÔÇó E┼şya karakterinizin envanterinde bulunmaktad─▒r<br>"
                details += "ÔÇó E┼şyay─▒ ├ğ─▒karmak i├ğin 'E┼şya ├ç─▒kar' butonunu kullan─▒n<br>"
                details += "ÔÇó Miktar─▒n─▒ de─şi┼ştirmek i├ğin e┼şyay─▒ yeniden ekleyin"
                
                self.item_details_text.setHtml(details)
            
        except Exception as e:
            print(f"E┼şya detaylar─▒ g├Âsterilemedi: {e}")

    def _remove_item(self):
        """Se├ğili e┼şyay─▒ ├ğ─▒kar"""
        try:
            current_item = self.inventory_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uyar─▒", "├ç─▒karmak i├ğin bir e┼şya se├ğin!")
                return
            
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen ├Ânce bir karakter olu┼şturun!")
                return
                
            filepath = self.current_character_file
            
            # Onay dialog'u
            reply = QMessageBox.question(self, "E┼şya ├ç─▒kar", 
                "Bu e┼şyay─▒ envanterden ├ğ─▒karmak istedi─şinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply != QMessageBox.Yes:
                return
            
            # Karakter dosyas─▒n─▒ g├╝ncelle
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            equipment = character_data.get("equipment", [])
            item_index = self.inventory_list.row(current_item)
            
            if 0 <= item_index < len(equipment):
                removed_item = equipment.pop(item_index)
                
                # Dosyaya kaydet
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(character_data, f, ensure_ascii=False, indent=2)
                
            # Envanteri yenile
            self._load_current_character_inventory()
                
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{removed_item.get('name', 'E┼şya')} ├ğ─▒kar─▒ld─▒!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"E┼şya ├ğ─▒kar─▒lamad─▒:\n{str(e)}")

    def _init_advanced_ui(self):
        """Geli┼şmi┼ş ├Âzellikler UI's─▒n─▒ olu┼ştur (opsiyonel)"""
        outer_layout = self.advanced_layout
        
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        content_widget = QWidget()
        layout = QVBoxLayout(content_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        scroll_area.setWidget(content_widget)
        outer_layout.addWidget(scroll_area)
        
        # Ba┼şl─▒k ve a├ğ─▒klama
        title_label = QLabel("ÔÜÖ´©Å Geli┼şmi┼ş ├ûzellikler")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel(
            "Bu sekme tamamen opsiyonel ├Âzellikler i├ğerir.\n"
            "Normal karakter olu┼şturma i├ğin bu ├Âzelliklere ihtiyac─▒n─▒z yoktur."
        )
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Kural Kitab─▒ Y├╝kleme Grubu
        rules_group = QGroupBox("­şôÜ Kural Kitab─▒ Y├╝kleme (Opsiyonel)")
        rules_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        rules_layout = QVBoxLayout(rules_group)
        
        rules_info = QLabel(
            "Kural kitab─▒n─▒z─▒ (PDF veya TXT format─▒nda) y├╝kleyerek, "
            "hesaplamalar─▒n otomatik olarak bu kurallara g├Âre yap─▒lmas─▒n─▒ sa─şlayabilirsiniz.\n\n"
            "Bu ├Âzellik opsiyoneldir. Kural y├╝klemezseniz, varsay─▒lan hesaplamalar kullan─▒l─▒r."
        )
        rules_info.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 10px;")
        rules_info.setWordWrap(True)
        rules_layout.addWidget(rules_info)
        
        # Kural y├╝kleme butonu
        load_rules_btn = QPushButton("­şôä Kural Kitab─▒ Y├╝kle (PDF/TXT)")
        load_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_rules_btn.clicked.connect(self._load_rules_from_file)
        load_rules_btn.setToolTip("Kural kitab─▒ndan kurallar─▒ y├╝kle (PDF/TXT)")
        rules_layout.addWidget(load_rules_btn)
        
        # Kural d├╝zenleme butonu
        edit_rules_btn = QPushButton("Ô£Å´©Å Kural D├╝zenle")
        edit_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        edit_rules_btn.clicked.connect(self._edit_rules)
        edit_rules_btn.setToolTip("Y├╝klenen kurallar─▒ d├╝zenle (JSON format─▒nda)")
        rules_layout.addWidget(edit_rules_btn)
        
        # Kural ├Ânizleme butonu
        preview_rules_btn = QPushButton("­şæü´©Å Kurallar─▒ G├Âr├╝nt├╝le")
        preview_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        preview_rules_btn.clicked.connect(self._preview_rules)
        preview_rules_btn.setToolTip("Y├╝klenen kurallar─▒ okunabilir formatta g├Âr├╝nt├╝le")
        rules_layout.addWidget(preview_rules_btn)
        
        # Versiyon y├Ânetimi butonu
        version_btn = QPushButton("­şôĞ Versiyon Y├Ânetimi")
        version_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        version_btn.clicked.connect(self._manage_versions)
        version_btn.setToolTip("Kural versiyonlar─▒n─▒ g├Âr├╝nt├╝le, geri y├╝kle veya sil")
        rules_layout.addWidget(version_btn)
        
        # NLP durumu
        nlp_status = get_nlp_status()
        if nlp_status["available"]:
            nlp_info = QLabel("­şñû NLP: Aktif (spaCy model y├╝kl├╝)")
            nlp_info.setStyleSheet("font-size: 10px; color: #27ae60; padding: 3px;")
        else:
            nlp_info = QLabel("­şñû NLP: Devre d─▒┼ş─▒ (spaCy modeli y├╝klenmemi┼ş)")
            nlp_info.setStyleSheet("font-size: 10px; color: #95a5a6; padding: 3px;")
        nlp_info.setToolTip(
            "NLP (Do─şal Dil ─░┼şleme) ile daha geli┼şmi┼ş kural ├ğ─▒karma yap─▒labilir.\n"
            "Kurulum: pip install spacy && python -m spacy download en_core_web_sm"
        )
        rules_layout.addWidget(nlp_info)
        
        # Mevcut kural durumu
        self.rules_status_label = QLabel("Durum: Kural y├╝klenmedi")
        self.rules_status_label.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
        rules_layout.addWidget(self.rules_status_label)
        
        # Kural durumunu kontrol et
        self._update_rules_status()
        
        layout.addWidget(rules_group)
        layout.addStretch()

    def _update_rules_status(self):
        """Kural durumunu g├╝ncelle"""
        if not hasattr(self, 'rules_status_label'):
            return
        
        rules = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
        if rules and rules.get('rules'):
            self.rules_status_label.setText("Ô£à Durum: Kural y├╝kl├╝ - Hesaplamalar ├Âzel kurallara g├Âre yap─▒l─▒yor")
            self.rules_status_label.setStyleSheet("font-size: 11px; color: #27ae60; padding: 5px;")
        else:
            self.rules_status_label.setText("Ôä╣´©Å Durum: Kural y├╝klenmedi - Varsay─▒lan hesaplamalar kullan─▒l─▒yor")
            self.rules_status_label.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
    
    def _load_rules_from_file(self):
        """Kural kitab─▒ndan kurallar─▒ y├╝kle (D&D 5e)"""
        file_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Kural Kitab─▒ Y├╝kle (PDF/TXT)",
            str(APP_BASE_DIR),
            "Dosyalar (*.pdf *.txt);;PDF Dosyalar─▒ (*.pdf);;Metin Dosyalar─▒ (*.txt)"
        )
        if not file_path_str:
            return

        file_path = Path(file_path_str)

        use_nlp = False
        if is_nlp_available():
            reply = QMessageBox.question(
                self,
                "NLP Kullan─▒m─▒",
                "Geli┼şmi┼ş NLP (Do─şal Dil ─░┼şleme) ile kural ├ğ─▒karma kullan─▒ls─▒n m─▒?\n\n"
                "NLP daha karma┼ş─▒k kurallar─▒ ├ğ─▒karabilir ama daha yava┼ş olabilir.\n\n"
                "Evet: NLP kullan (├Ânerilir)\n"
                "Hay─▒r: Standart pattern matching kullan",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            use_nlp = (reply == QMessageBox.Yes)
        elif NLP_MODULE_AVAILABLE:
            QMessageBox.information(
                self,
                "NLP Bilgisi",
                "NLP mod├╝l├╝ mevcut ancak spaCy modeli y├╝klenmemi┼ş.\n\n"
                "NLP kullanmak i├ğin:\n"
                "1. pip install spacy\n"
                "2. python -m spacy download en_core_web_sm\n\n"
                "Standart pattern matching kullan─▒lacak."
            )

        try:
            rules = extract_rules_from_file(file_path, self.SYSTEM_NAME, use_nlp=use_nlp)
            if not rules or not rules.get("rules"):
                QMessageBox.warning(
                    self,
                    "Uyar─▒",
                    "Dosyadan kural ├ğ─▒kar─▒lamad─▒.\n"
                    "L├╝tfen dosyan─▒n do─şru formatta oldu─şundan emin olun."
                )
                return

            is_valid, issues = validate_rules(rules)
            if issues:
                report = format_validation_report(issues)
                reply = QMessageBox.question(
                    self,
                    "Kural Do─şrulama",
                    f"Kurallarda sorunlar bulundu:\n\n{report[:200]}...\n\n"
                    "Yine de kaydetmek istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

                if not is_valid:
                    detail_msg = QMessageBox(self)
                    detail_msg.setWindowTitle("Kural Do─şrulama Detaylar─▒")
                    detail_msg.setText("Kurallarda kritik hatalar bulundu. Detaylar:")
                    detail_msg.setDetailedText(report)
                    detail_msg.setIcon(QMessageBox.Warning)
                    detail_msg.exec()

            saved_path = save_rules(rules, APP_BASE_DIR, self.SYSTEM_NAME)

            rules_text = json.dumps(rules, ensure_ascii=False, indent=2)
            msg = QMessageBox(self)
            msg.setWindowTitle("Kurallar Y├╝klendi")
            msg.setText(f"Kurallar ba┼şar─▒yla ├ğ─▒kar─▒ld─▒ ve kaydedildi:\n{saved_path}")
            msg.setDetailedText(rules_text)
            msg.setIcon(QMessageBox.Information)
            msg.exec()

            QMessageBox.information(
                self,
                "Ba┼şar─▒l─▒",
                f"Kurallar y├╝klendi!\n{saved_path}\n\n"
                "Art─▒k hesaplamalar bu kurallara g├Âre yap─▒lacak."
            )

            self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            self._update_rules_status()
            self._update_character_stats()
            if hasattr(self, "_refresh_available_spells_for_selection"):
                self._refresh_available_spells_for_selection()

        except ImportError as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"PDF okuma i├ğin gerekli k├╝t├╝phane eksik:\n{str(e)}\n\n"
                "L├╝tfen 'pip install PyPDF2' ile y├╝kleyin."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Kural y├╝kleme hatas─▒:\n{str(e)}"
            )
    
    def _edit_rules(self):
        """Kural d├╝zenleme diyalo─şunu a├ğ"""
        dialog = RuleEditorDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle
            self._rules_cache = None
            # Durumu g├╝ncelle
            self._update_rules_status()
    
    def _preview_rules(self):
        """Kural ├Ânizleme diyalo─şunu a├ğ"""
        dialog = RulePreviewDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        dialog.exec()
    
    def _manage_versions(self):
        """Kural versiyon y├Ânetimi diyalo─şunu a├ğ"""
        dialog = RuleVersionDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle (versiyon geri y├╝klendiyse)
            self._rules_cache = None
            # Durumu g├╝ncelle
            self._update_rules_status()

    def _init_dice_ui(self):
        """Dice Roller UI's─▒n─▒ olu┼ştur"""
        layout = self.dice_layout
        
        # Ba┼şl─▒k
        title_label = QLabel("­şÄ▓ Dice Roller")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Ana splitter
        main_splitter = QtWidgets.QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Sol panel - Dice roller
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # H─▒zl─▒ roll'lar
        quick_group = QGroupBox("H─▒zl─▒ Roll'lar")
        quick_layout = QVBoxLayout()
        
        # D20 roll'lar─▒
        d20_layout = QHBoxLayout()
        d20_btn = QPushButton("d20")
        d20_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        d20_btn.clicked.connect(lambda: self._roll_dice(20))
        d20_layout.addWidget(d20_btn)
        
        d12_btn = QPushButton("d12")
        d12_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #e67e22;
            }
        """)
        d12_btn.clicked.connect(lambda: self._roll_dice(12))
        d20_layout.addWidget(d12_btn)
        
        d10_btn = QPushButton("d10")
        d10_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        d10_btn.clicked.connect(lambda: self._roll_dice(10))
        d20_layout.addWidget(d10_btn)
        
        d8_btn = QPushButton("d8")
        d8_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        d8_btn.clicked.connect(lambda: self._roll_dice(8))
        d20_layout.addWidget(d8_btn)
        
        d6_btn = QPushButton("d6")
        d6_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        d6_btn.clicked.connect(lambda: self._roll_dice(6))
        d20_layout.addWidget(d6_btn)
        
        d4_btn = QPushButton("d4")
        d4_btn.setStyleSheet("""
            QPushButton {
                background-color: #34495e;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #2c3e50;
            }
        """)
        d4_btn.clicked.connect(lambda: self._roll_dice(4))
        d20_layout.addWidget(d4_btn)
        
        quick_layout.addLayout(d20_layout)
        quick_group.setLayout(quick_layout)
        left_layout.addWidget(quick_group)
        
        # d100 roll
        d100_layout = QHBoxLayout()
        d100_btn = QPushButton("d100")
        d100_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        d100_btn.clicked.connect(lambda: self._roll_dice(100))
        d100_layout.addWidget(d100_btn)
        
        # Advantage/Disadvantage
        adv_btn = QPushButton("Advantage")
        adv_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        adv_btn.clicked.connect(self._roll_advantage)
        d100_layout.addWidget(adv_btn)
        
        dis_btn = QPushButton("Disadvantage")
        dis_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 15px 25px;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
                margin: 5px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        dis_btn.clicked.connect(self._roll_disadvantage)
        d100_layout.addWidget(dis_btn)
        
        quick_layout.addLayout(d100_layout)
        
        # ├ûzel roll
        custom_group = QGroupBox("├ûzel Roll")
        custom_layout = QVBoxLayout()
        
        custom_input_layout = QHBoxLayout()
        custom_input_layout.addWidget(QLabel("Roll:"))
        
        self.custom_dice_input = QLineEdit()
        self.custom_dice_input.setPlaceholderText("├ûrnek: 3d6+2, 2d20, 1d100")
        custom_input_layout.addWidget(self.custom_dice_input)
        
        custom_roll_btn = QPushButton("Roll Et")
        custom_roll_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                padding: 10px 20px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        custom_roll_btn.clicked.connect(self._roll_custom_dice)
        custom_input_layout.addWidget(custom_roll_btn)
        
        custom_layout.addLayout(custom_input_layout)
        custom_group.setLayout(custom_layout)
        left_layout.addWidget(custom_group)
        
        # Kay─▒tl─▒ profiller
        profiles_group = QGroupBox("Kay─▒tl─▒ Profiller")
        profiles_layout = QVBoxLayout()
        
        # Profil ekleme
        profile_input_layout = QHBoxLayout()
        profile_input_layout.addWidget(QLabel("Profil Ad─▒:"))
        
        self.profile_name_input = QLineEdit()
        self.profile_name_input.setPlaceholderText("├ûrnek: Sald─▒r─▒")
        profile_input_layout.addWidget(self.profile_name_input)
        
        profile_input_layout.addWidget(QLabel("Roll:"))
        self.profile_roll_input = QLineEdit()
        self.profile_roll_input.setPlaceholderText("1d20+5")
        profile_input_layout.addWidget(self.profile_roll_input)
        
        add_profile_btn = QPushButton("Ekle")
        add_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        add_profile_btn.clicked.connect(self._add_dice_profile)
        profile_input_layout.addWidget(add_profile_btn)
        
        profiles_layout.addLayout(profile_input_layout)
        
        # Profil listesi
        self.profiles_list = QListWidget()
        self.profiles_list.setMaximumHeight(150)
        profiles_layout.addWidget(self.profiles_list)
        
        # Profil butonlar─▒
        profile_buttons_layout = QHBoxLayout()
        
        roll_profile_btn = QPushButton("Se├ğili Profili Roll Et")
        roll_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        roll_profile_btn.clicked.connect(self._roll_selected_profile)
        profile_buttons_layout.addWidget(roll_profile_btn)
        
        remove_profile_btn = QPushButton("Profili Sil")
        remove_profile_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_profile_btn.clicked.connect(self._remove_dice_profile)
        profile_buttons_layout.addWidget(remove_profile_btn)
        
        profiles_layout.addLayout(profile_buttons_layout)
        profiles_group.setLayout(profiles_layout)
        left_layout.addWidget(profiles_group)
        
        main_splitter.addWidget(left_panel)
        
        # Sa─ş panel - Sonu├ğlar
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        results_group = QGroupBox("Roll Sonu├ğlar─▒")
        results_layout = QVBoxLayout()
        
        self.dice_results_text = QTextEdit()
        self.dice_results_text.setReadOnly(True)
        self.dice_results_text.setMaximumHeight(300)
        results_layout.addWidget(self.dice_results_text)
        
        clear_btn = QPushButton("Sonu├ğlar─▒ Temizle")
        clear_btn.clicked.connect(self._clear_dice_results)
        results_layout.addWidget(clear_btn)
        
        results_group.setLayout(results_layout)
        right_layout.addWidget(results_group)
        
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([300, 400])

    def _roll_dice(self, sides):
        """Basit dice roll"""
        import random
        from datetime import datetime
        
        result = random.randint(1, sides)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.dice_results_text.append(f"[{timestamp}] ­şÄ▓ d{sides}: {result}")
        
        # E─şer 20 ise ├Âzel mesaj
        if sides == 20:
            if result == 20:
                self.dice_results_text.append("  ­şÄë NATURAL 20! CRITICAL SUCCESS!")
            elif result == 1:
                self.dice_results_text.append("  ­şÆÇ NATURAL 1! CRITICAL FAILURE!")
        
        # d100 i├ğin ├Âzel mesaj
        elif sides == 100:
            if result <= 5:
                self.dice_results_text.append("  ­şÄ» Kritik Ba┼şar─▒!")
            elif result >= 95:
                self.dice_results_text.append("  ­şÆÑ Kritik Ba┼şar─▒s─▒zl─▒k!")
        
        self.dice_results_text.append("")

    def _roll_custom_dice(self):
        """├ûzel dice roll (├Ârn: 3d6+2)"""
        try:
            import random
            import re
            
            roll_text = self.custom_dice_input.text().strip()
            if not roll_text:
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen roll format─▒ girin! (├ûrnek: 3d6+2)")
                return
            
            # Roll format─▒n─▒ parse et (basit regex)
            # ├ûrnek: 3d6+2, 2d20, 1d100-1
            pattern = r'(\d+)d(\d+)([+-]\d+)?'
            match = re.match(pattern, roll_text.lower())
            
            if not match:
                QMessageBox.warning(self, "Hata", "Ge├ğersiz roll format─▒! ├ûrnek: 3d6+2")
                return
            
            num_dice = int(match.group(1))
            sides = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            
            if num_dice > 20:
                QMessageBox.warning(self, "Uyar─▒", "Maksimum 20 zar atabilirsiniz!")
                return
                
            if sides > 100:
                QMessageBox.warning(self, "Uyar─▒", "Maksimum 100 y├╝zl├╝ zar kullanabilirsiniz!")
                return
            
            # Zar at
            results = []
            for _ in range(num_dice):
                results.append(random.randint(1, sides))
            
            total = sum(results) + modifier
            
            # Sonucu g├Âster
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            result_text = f"[{timestamp}] ­şÄ▓ {roll_text}: "
            
            if num_dice > 1:
                result_text += f"{results} "
                if modifier != 0:
                    result_text += f"+ {modifier} "
                result_text += f"= {total}"
            else:
                result_text += f"{results[0]}"
                if modifier != 0:
                    result_text += f" + {modifier} = {total}"
                else:
                    result_text += f" = {total}"
            
            self.dice_results_text.append(result_text)
            self.dice_results_text.append("")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Dice roll hatas─▒:\n{str(e)}")

    def _clear_dice_results(self):
        """Dice roll sonu├ğlar─▒n─▒ temizle"""
        self.dice_results_text.clear()

    def _roll_advantage(self):
        """Advantage roll (2d20, en y├╝kse─şini al)"""
        import random
        from datetime import datetime
        
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        result = max(roll1, roll2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.dice_results_text.append(f"[{timestamp}] ­şÄ» Advantage: {roll1}, {roll2} ÔåÆ {result}")
        
        if result == 20:
            self.dice_results_text.append("  ­şÄë NATURAL 20! CRITICAL SUCCESS!")
        elif result == 1:
            self.dice_results_text.append("  ­şÆÇ NATURAL 1! CRITICAL FAILURE!")
        
        self.dice_results_text.append("")

    def _roll_disadvantage(self):
        """Disadvantage roll (2d20, en d├╝┼ş├╝─ş├╝n├╝ al)"""
        import random
        from datetime import datetime
        
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        result = min(roll1, roll2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.dice_results_text.append(f"[{timestamp}] ÔÜá´©Å Disadvantage: {roll1}, {roll2} ÔåÆ {result}")
        
        if result == 20:
            self.dice_results_text.append("  ­şÄë NATURAL 20! CRITICAL SUCCESS!")
        elif result == 1:
            self.dice_results_text.append("  ­şÆÇ NATURAL 1! CRITICAL FAILURE!")
        
        self.dice_results_text.append("")

    def _add_dice_profile(self):
        """Dice profili ekle"""
        try:
            profile_name = self.profile_name_input.text().strip()
            profile_roll = self.profile_roll_input.text().strip()
            
            if not profile_name or not profile_roll:
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen profil ad─▒ ve roll format─▒n─▒ girin!")
                return
            
            # Roll format─▒n─▒ kontrol et
            import re
            pattern = r'(\d+)d(\d+)([+-]\d+)?'
            match = re.match(pattern, profile_roll.lower())
            
            if not match:
                QMessageBox.warning(self, "Hata", "Ge├ğersiz roll format─▒! ├ûrnek: 1d20+5")
                return
            
            # Profili ekle
            profile_text = f"{profile_name}: {profile_roll}"
            self.profiles_list.addItem(profile_text)
            
            # Input'lar─▒ temizle
            self.profile_name_input.clear()
            self.profile_roll_input.clear()
            
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"Profil '{profile_name}' eklendi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Profil eklenirken hata olu┼ştu:\n{str(e)}")

    def _roll_selected_profile(self):
        """Se├ğili profili roll et"""
        try:
            selected_item = self.profiles_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen roll etmek i├ğin bir profil se├ğin!")
                return
            
            profile_text = selected_item.text()
            profile_name, profile_roll = profile_text.split(": ", 1)
            
            # Roll'u ├ğal─▒┼şt─▒r
            self.custom_dice_input.setText(profile_roll)
            self._roll_custom_dice()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Profil roll edilirken hata olu┼ştu:\n{str(e)}")

    def _remove_dice_profile(self):
        """Se├ğili profili sil"""
        try:
            selected_item = self.profiles_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen silmek i├ğin bir profil se├ğin!")
                return
            
            profile_text = selected_item.text()
            profile_name = profile_text.split(": ", 1)[0]
            
            # Onay dialog'u
            reply = QMessageBox.question(self, "Profil Sil", 
                f"'{profile_name}' profilini silmek istedi─şinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.profiles_list.takeItem(self.profiles_list.row(selected_item))
                QMessageBox.information(self, "Ba┼şar─▒l─▒", f"Profil '{profile_name}' silindi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Profil silinirken hata olu┼ştu:\n{str(e)}")

    def _show_race_info(self, race_name):
        """Irk bilgilerini g├Âster"""
        if not race_name:
            return
            
        race_data = self.data.get("races", {}).get(race_name, {})
        if not race_data:
            return
            
        info_text = f"<h2>{race_name}</h2>"
        
        # Yetenek puan─▒ art─▒┼şlar─▒
        ability_increases = race_data.get("ability_score_increase", {})
        if ability_increases:
            info_text += "<h3>Yetenek Puan─▒ Art─▒┼şlar─▒:</h3><ul>"
            for ability, bonus in ability_increases.items():
                if ability == "all":
                    info_text += f"<li>T├╝m yetenekler: +{bonus}</li>"
                else:
                    ability_names = {
                        "strength": "G├╝├ğ", "dexterity": "├çeviklik", "constitution": "Dayan─▒kl─▒l─▒k",
                        "intelligence": "Zeka", "wisdom": "Bilgelik", "charisma": "Karizma"
                    }
                    info_text += f"<li>{ability_names.get(ability, ability.title())}: +{bonus}</li>"
            info_text += "</ul>"
        
        # H─▒z
        speed = race_data.get("speed", {})
        if speed:
            info_text += f"<h3>H─▒z:</h3><p>{speed} fit</p>"
        
        # Irk ├Âzellikleri
        traits = race_data.get("traits", [])
        if traits:
            info_text += "<h3>Irk ├ûzellikleri:</h3><ul>"
            for trait in traits:
                info_text += f"<li>{trait}</li>"
            info_text += "</ul>"
        
        self.info_text.setHtml(info_text)

    def _show_class_info(self, class_name):
        """S─▒n─▒f bilgilerini g├Âster"""
        if not class_name:
            return
            
        class_data = self.data.get("classes", {}).get(class_name, {})
        if not class_data:
            return
            
        info_text = f"<h2>{class_name}</h2>"
        
        # Hit Dice
        hit_dice = class_data.get("hit_dice", "")
        if hit_dice:
            info_text += f"<h3>Hit Dice:</h3><p>{hit_dice}</p>"
        
        # Ana Yetenek
        primary_ability = class_data.get("primary_ability", [])
        if primary_ability:
            ability_names = {
                "strength": "G├╝├ğ", "dexterity": "├çeviklik", "constitution": "Dayan─▒kl─▒l─▒k",
                "intelligence": "Zeka", "wisdom": "Bilgelik", "charisma": "Karizma"
            }
            abilities = [ability_names.get(ab, ab.title()) for ab in primary_ability]
            info_text += f"<h3>Ana Yetenek:</h3><p>{', '.join(abilities)}</p>"
        
        # Skills
        skills = class_data.get("skills", [])
        if skills:
            info_text += f"<h3>S─▒n─▒f Becerileri:</h3><p>{', '.join(skills)}</p>"
        
        self.info_text.setHtml(info_text)

    def _show_background_info(self, background_name):
        """Arka plan bilgilerini g├Âster"""
        if not background_name:
            return
            
        background_data = self.data.get("backgrounds", {}).get(background_name, {})
        if not background_data:
            return
            
        info_text = f"<h2>{background_name}</h2>"
        
        # Skills
        skills = background_data.get("skills", [])
        if skills:
            info_text += f"<h3>Beceri Yeterlili─şi:</h3><p>{', '.join(skills)}</p>"
        
        # Feature
        feature = background_data.get("feature", "")
        if feature:
            info_text += f"<h3>├ûzellik:</h3><p>{feature}</p>"
        
        self.info_text.setHtml(info_text)

    def _update_ability_scores(self, race_name):
        """Irk se├ğimi de─şi┼şti─şinde yetenek puanlar─▒n─▒ g├╝ncelle"""
        if not race_name or not hasattr(self, 'ability_spins'):
            return
            
        race_data = self.data.get("races", {}).get(race_name, {})
        if not race_data:
            return
            
        ability_increases = race_data.get("ability_score_increase", {}) or {}
        
        # ├ûnce bir ├Ânceki ─▒rk bonuslar─▒n─▒ geri al
        prev_bonus = getattr(self, "_current_race_bonus", {}) or {}
        for ability, bonus in prev_bonus.items():
            if ability == "all":
                for _, spin in self.ability_spins.items():
                    spin.setValue(max(spin.minimum(), spin.value() - bonus))
            else:
                if ability in self.ability_spins:
                    spin = self.ability_spins[ability]
                    spin.setValue(max(spin.minimum(), spin.value() - bonus))
        
        # Yeni ─▒rk bonuslar─▒n─▒ uygula
        for ability, bonus in ability_increases.items():
            if ability == "all":
                for _, spin in self.ability_spins.items():
                    spin.setValue(min(spin.maximum(), spin.value() + bonus))
            else:
                if ability in self.ability_spins:
                    spin = self.ability_spins[ability]
                    spin.setValue(min(spin.maximum(), spin.value() + bonus))
        
        # Aktif bonusu sakla
        self._current_race_bonus = ability_increases
        
        # ─░statistikleri g├╝ncelle
        self._update_character_stats()

    def _update_character_stats(self):
        """Karakter istatistiklerini g├╝ncelle"""
        try:
            # Yetenek puanlar─▒n─▒ al
            abilities = {}
            for ability, spin in self.ability_spins.items():
                abilities[ability] = spin.value()
            
            # Yetenek modifierlar─▒n─▒ hesapla ve g├╝ncelle
            for ability, score in abilities.items():
                modifier = (score - 10) // 2
                modifier_text = f"{modifier:+d}" if modifier >= 0 else f"{modifier:d}"
                
                # Ability key'ini k├╝├ğ├╝k harfe ├ğevir
                ability_key = ability.lower()
                if ability_key in self.ability_mod_labels:
                    self.ability_mod_labels[ability_key].setText(modifier_text)
                
                # Renk kodlamas─▒
                if modifier >= 2:
                    color = "#27ae60"  # Ye┼şil
                elif modifier >= 0:
                    color = "#3498db"  # Mavi
                elif modifier >= -2:
                    color = "#f39c12"  # Turuncu
                else:
                    color = "#e74c3c"  # K─▒rm─▒z─▒
                
                if ability_key in self.ability_mod_labels:
                    self.ability_mod_labels[ability_key].setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")
            
            # AC hesaplama (z─▒rh bazl─▒) - Dinamik kural deste─şi
            if hasattr(self, 'current_character') and self.current_character:
                # ├ûnce y├╝klenen kurallar─▒ kontrol et
                if self._rules_cache is None:
                    self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
                ac = calculate_dynamic_armor_class(self.current_character, self._rules_cache, self.data)
            else:
                # Karakter hen├╝z olu┼şturulmam─▒┼şsa basit hesaplama
                dex_modifier = (abilities.get("Dexterity", 10) - 10) // 2
                ac = 10 + dex_modifier
            self.ac_label.setText(str(ac))
            self.ac_label.setToolTip(f"Armor Class: {ac}")
            
            # HP hesaplama (seviyeye g├Âre) - Dinamik kural deste─şi
            if hasattr(self, 'current_character') and self.current_character:
                # ├ûnce y├╝klenen kurallar─▒ kontrol et
                if self._rules_cache is None:
                    self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
                hp = calculate_dynamic_hit_points(self.current_character, self._rules_cache, self.data)
            else:
                # Karakter hen├╝z olu┼şturulmam─▒┼şsa basit hesaplama
                con_modifier = (abilities.get("Constitution", 10) - 10) // 2
                class_hp = {
                    "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
                    "Artificer": 8, "Bard": 8, "Cleric": 8, "Druid": 8, 
                    "Monk": 8, "Rogue": 8, "Warlock": 8, "Sorcerer": 6, "Wizard": 6
                }
                char_class = self.class_cb.currentText()
                hp_dice = class_hp.get(char_class, 6)
                hp = hp_dice + con_modifier
            self.hp_label.setText(str(hp))
            
            # Proficiency Bonus hesaplama (seviyeye g├Âre) - Dinamik kural deste─şi
            level = self.current_character.get("level", 1) if hasattr(self, 'current_character') and self.current_character else 1
            # ├ûnce y├╝klenen kurallar─▒ kontrol et
            if self._rules_cache is None:
                self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            prof_bonus = calculate_dynamic_proficiency_bonus(level, self._rules_cache)
            self.prof_bonus_label.setText(f"+{prof_bonus}")
            
            # Skill modifierlar─▒ hesaplama
            skill_abilities = {
                "acrobatics": "dexterity", "animal_handling": "wisdom", "arcana": "intelligence",
                "athletics": "strength", "deception": "charisma", "history": "intelligence",
                "insight": "wisdom", "intimidation": "charisma", "investigation": "intelligence",
                "medicine": "wisdom", "nature": "intelligence", "perception": "wisdom",
                "performance": "charisma", "persuasion": "charisma", "religion": "intelligence",
                "sleight_of_hand": "dexterity", "stealth": "dexterity", "survival": "wisdom"
            }
            
            # Se├ğilen s─▒n─▒f becerilerini al (e─şer karakter olu┼şturma a┼şamas─▒ndaysa)
            if hasattr(self, 'current_character') and self.current_character:
                class_skills = self.current_character.get("skills", {}).get("class_skills", [])
            else:
                # E─şer hen├╝z karakter olu┼şturulmam─▒┼şsa, se├ğilen becerileri al
                selected_skills = [item.text() for item in self.wiz_skills.selectedItems()]
                class_skills = selected_skills
            
            for skill, ability in skill_abilities.items():
                # Ability key'ini b├╝y├╝k harfle ba┼şlayacak ┼şekilde d├╝zelt
                ability_key = ability.title()
                ability_modifier = (abilities.get(ability_key, 10) - 10) // 2
                
                # Proficiency bonus ekle (e─şer s─▒n─▒f becerisi ise)
                if skill in class_skills:
                    skill_modifier = ability_modifier + prof_bonus
                    modifier_text = f"{skill_modifier:+d}"
                    color = "#27ae60"  # Ye┼şil - proficient
                else:
                    skill_modifier = ability_modifier
                    modifier_text = f"{skill_modifier:+d}"
                    color = "#7f8c8d"  # Gri - not proficient
                
                self.skill_mod_labels[skill].setText(modifier_text)
                self.skill_mod_labels[skill].setStyleSheet(f"font-size: 11px; color: {color};")
                
        except Exception as e:
            print(f"─░statistik g├╝ncelleme hatas─▒: {e}")

    def _update_spells_list(self):
        """B├╝y├╝ listesini g├╝ncelle"""
        if hasattr(self, 'current_character') and self.current_character:
            self.spells_character_combo.clear()
            char_name = f"{self.current_character['name']} (Seviye {self.current_character['level']})"
            self.spells_character_combo.addItem(char_name)
            
            # B├╝y├╝ kullan─▒m kontrol├╝
            char_class = self.current_character.get("class", "")
            spellcasting_classes = ["Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard", "Paladin", "Ranger", "Artificer"]
            
            if char_class in spellcasting_classes:
                self.spellcasting_check_label.setText(f"Ô£à {char_class} b├╝y├╝ kullanabilir")
                self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #27ae60;")
                self.spell_selection_group.setVisible(True)
                self._refresh_available_spells_for_selection()
            else:
                self.spellcasting_check_label.setText(f"ÔØî {char_class} b├╝y├╝ kullanamaz")
                self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
                self.spell_selection_group.setVisible(False)
            
            # Mevcut b├╝y├╝leri listele
            self.spells_list.clear()
            spells = self.current_character.get("spells", {})
            
            # T├╝m b├╝y├╝ seviyelerini kontrol et
            for spell_type, spell_list in spells.items():
                if spell_list:
                    if spell_type == "cantrips":
                        self.spells_list.addItem("=== CANTRIPS ===")
                    else:
                        level_num = spell_type.replace("level_", "")
                        self.spells_list.addItem(f"=== {level_num}. SEV─░YE B├£Y├£LER ===")
                    
                    for spell in spell_list:
                        self.spells_list.addItem(f"ÔÇó {spell}")

    def _on_spell_level_changed(self, spell_level):
        """B├╝y├╝ seviye se├ğimi de─şi┼şti─şinde b├╝y├╝ listesini g├╝ncelle"""
        self._refresh_available_spells_for_selection()

    def _refresh_available_spells_for_selection(self):
        """Se├ğilebilir b├╝y├╝leri g├╝ncelle"""
        try:
            if not hasattr(self, 'current_character') or not self.current_character:
                return
            
            char_class = self.current_character.get("class", "")
            class_data = self.data.get("classes", {}).get(char_class, {})
            current_spells = self.current_character.get("spells", {})
            
            self.available_spells_for_selection.clear()
            
            # Spell seviyesini belirle
            spell_level = self.spell_level_combo.currentText()
            if spell_level == "Cantrip":
                spell_key = "cantrips"
            else:
                level_num = int(spell_level.split()[0])
                spell_key = f"level_{level_num}"
            
            # S─▒n─▒f b├╝y├╝lerini al
            class_spells = class_data.get("spells", {}).get(spell_key, [])
            
            for spell_name in class_spells:
                # E─şer b├╝y├╝ zaten biliniyorsa atla
                if spell_name not in current_spells.get(spell_key, []):
                    spell_data = self.data.get("spells", {}).get(spell_name, {})
                    spell_text = f"{spell_name}"
                    if spell_data.get("description"):
                        spell_text += f" - {spell_data['description'][:50]}..."
                    self.available_spells_for_selection.addItem(spell_text)
                    
        except Exception as e:
            print(f"B├╝y├╝ listesi g├╝ncellenirken hata: {e}")

    def _add_spell_to_character(self):
        """Se├ğili b├╝y├╝y├╝ karaktere ekle"""
        try:
            if not hasattr(self, 'current_character') or not self.current_character:
                QMessageBox.warning(self, "Uyar─▒", "├ûnce bir karakter olu┼şturun!")
                return
            
            selected_spell = self.available_spells_for_selection.currentItem()
            if not selected_spell:
                QMessageBox.warning(self, "Uyar─▒", "L├╝tfen eklemek istedi─şiniz b├╝y├╝y├╝ se├ğin!")
                return
            
            spell_name = selected_spell.text().split(" - ")[0]
            spell_level = self.spell_level_combo.currentText()
            
            if spell_level == "Cantrip":
                spell_key = "cantrips"
            else:
                level_num = int(spell_level.split()[0])
                spell_key = f"level_{level_num}"
            
            # B├╝y├╝y├╝ karaktere ekle
            if "spells" not in self.current_character:
                self.current_character["spells"] = {}
            if spell_key not in self.current_character["spells"]:
                self.current_character["spells"][spell_key] = []
            
            self.current_character["spells"][spell_key].append(spell_name)
            
            # Karakteri kaydet
            if hasattr(self, 'current_character_file') and self.current_character_file:
                import json
                with open(self.current_character_file, 'w', encoding='utf-8') as f:
                    json.dump(self.current_character, f, ensure_ascii=False, indent=2)
            
            # Listeleri g├╝ncelle
            self._update_spells_list()
            
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{spell_name} b├╝y├╝s├╝ eklendi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"B├╝y├╝ eklenirken hata olu┼ştu:\n{str(e)}")

    def _show_spell_details(self, item):
        """B├╝y├╝ detaylar─▒n─▒ g├Âster"""
        spell_name = item.text()
        if spell_name.startswith("===") or spell_name.startswith("ÔÇó "):
            return
            
        # B├╝y├╝ bilgilerini bul
        spell_data = self.data.get("spells", {}).get(spell_name, {})
        if spell_data:
            info_text = f"<h3>{spell_name}</h3>"
            info_text += f"<p><b>Seviye:</b> {spell_data.get('level', 'Bilinmiyor')}</p>"
            info_text += f"<p><b>S├╝re:</b> {spell_data.get('duration', 'Bilinmiyor')}</p>"
            info_text += f"<p><b>Menzil:</b> {spell_data.get('range', 'Bilinmiyor')}</p>"
            info_text += f"<p><b>A├ğ─▒klama:</b> {spell_data.get('description', 'A├ğ─▒klama bulunamad─▒')}</p>"
            self.spell_info.setHtml(info_text)
        else:
            self.spell_info.setPlainText(f"{spell_name} i├ğin detay bulunamad─▒.")

    def _add_spell_dialog(self):
        """B├╝y├╝ ekleme dialog'u"""
        if not hasattr(self, 'current_character') or not self.current_character:
            QMessageBox.warning(self, "Uyar─▒", "├ûnce bir karakter olu┼şturun!")
            return
            
        # Mevcut b├╝y├╝leri al (equipment alt─▒nda)
        equipment = self.data.get("equipment", {})
        all_spells = list(equipment.get("spells", {}).keys())
        if not all_spells:
            QMessageBox.information(self, "Bilgi", "B├╝y├╝ listesi bulunamad─▒.")
            return
            
        # Dialog ile b├╝y├╝ se├ğ
        spell_name, ok = QInputDialog.getItem(self, "B├╝y├╝ Ekle", "Eklemek istedi─şiniz b├╝y├╝y├╝ se├ğin:", all_spells, 0, False)
        if ok and spell_name:
            # B├╝y├╝y├╝ karaktere ekle
            if not hasattr(self.current_character, 'spells'):
                self.current_character['spells'] = {}
            
            spell_data = equipment.get("spells", {}).get(spell_name, {})
            spell_level = spell_data.get('level', '1st')
            
            if spell_level == 'Cantrip':
                if 'cantrips' not in self.current_character['spells']:
                    self.current_character['spells']['cantrips'] = []
                self.current_character['spells']['cantrips'].append(spell_name)
            else:
                if spell_level not in self.current_character['spells']:
                    self.current_character['spells'][spell_level] = []
                self.current_character['spells'][spell_level].append(spell_name)
            
            # Listeyi g├╝ncelle
            self._update_spells_list()
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{spell_name} b├╝y├╝s├╝ eklendi!")

    def _remove_spell(self):
        """Se├ğili b├╝y├╝y├╝ kald─▒r"""
        current_item = self.spells_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyar─▒", "Kald─▒rmak i├ğin bir b├╝y├╝ se├ğin!")
            return
            
        spell_text = current_item.text()
        if spell_text.startswith("===") or not spell_text.startswith("ÔÇó "):
            QMessageBox.warning(self, "Uyar─▒", "Ge├ğerli bir b├╝y├╝ se├ğin!")
            return
            
        spell_name = spell_text[2:]  # "ÔÇó " k─▒sm─▒n─▒ kald─▒r
        
        # B├╝y├╝y├╝ karakterden ├ğ─▒kar
        spells = self.current_character.get("spells", {})
        for level, spell_list in spells.items():
            if spell_name in spell_list:
                spell_list.remove(spell_name)
                break
        
        # Listeyi g├╝ncelle
        self._update_spells_list()
        QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{spell_name} b├╝y├╝s├╝ kald─▒r─▒ld─▒!")

    def _export_to_pdf(self, character):
        """Karakteri PDF'e ├ğevir"""
        self._auto_save_character()
        self._export_character(character, "PDF")
    
    def _export_character(self, character: dict, format_type: str = None):
        """Karakteri farkl─▒ formatlarda export et"""
        if not format_type:
            # Format se├ğimi diyalo─şu
            dialog = ExportFormatDialog(self, character)
            if dialog.exec() == QDialog.Accepted:
                format_type, file_path = dialog.get_selected_format()
                if format_type and file_path:
                    self._perform_export(character, format_type, Path(file_path))
        else:
            # Direkt export (geriye uyumluluk)
            safe_name = "".join(c for c in character.get("name", "karakter") if c.isalnum() or c in (' ', '-', '_')).rstrip() or "dnd_karakter"
            default_path = _ensure_characters_dir() / f"{safe_name}.{format_type.lower()}"
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                f"D&D Karakterini {format_type} olarak kaydet",
                str(default_path),
                f"{format_type} Dosyalar─▒ (*.{format_type.lower()})"
            )
            if file_path:
                self._perform_export(character, format_type, Path(file_path))
    
    def _perform_export(self, character: dict, format_type: str, file_path: Path):
        """Export i┼şlemini ger├ğekle┼ştir"""
        try:
            system = character.get("system", "DND5E")
            
            if format_type == "PDF":
                if system == "DND5E":
                    export_dnd_character_pdf(character, file_path)
                elif system == "MUTANTS_AND_MASTERMINDS":
                    export_mm_character_pdf(character, file_path)
                elif system == "VTM5E":
                    export_vtm_character_pdf(character, file_path)
            elif format_type == "HTML":
                export_character_html(character, file_path)
            elif format_type == "JSON":
                export_character_json(character, file_path)
            elif format_type == "CSV":
                export_character_csv(character, file_path)
            else:
                QMessageBox.warning(self, "Uyar─▒", f"Desteklenmeyen format: {format_type}")
                return
            
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"Karakter {format_type} format─▒nda kaydedildi:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Export s─▒ras─▒nda hata olu┼ştu:\n{str(e)}")


class MmPage(QWidget):
    SYSTEM_NAME = "MUTANTS_AND_MASTERMINDS"

    def __init__(self):
        super().__init__()
        self.data = load_mm_data(APP_BASE_DIR)
        self.current_character: dict | None = None
        self.current_character_image_data = None  # Resim verisi (base64)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header k─▒sm─▒ - Logo ve ba┼şl─▒k
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #34495e; border-radius: 10px; margin: 5px;")
        header_widget.setMaximumHeight(140)  # Header maksimum y├╝kseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Sol taraf i├ğin bo┼ş alan
        header_layout.addStretch()
        
        # Ba┼şl─▒k (logo kald─▒r─▒ld─▒)
        title = QLabel("Diyargezer - Mutants & Masterminds")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)  # Uzun metinler i├ğin kelime kayd─▒rma
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addWidget(header_widget)

        layout.addWidget(self._build_toolbar())

        # Tab widget olu┼ştur
        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                margin-top: -2px;
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34495e, stop: 1 #2c3e50);
                color: #ecf0f1;
                padding: 12px 24px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
                border: 1px solid #34495e;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-bottom: 2px solid #3498db;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5dade2, stop: 1 #3498db);
            }
            QTabBar::tab:!selected {
                margin-top: 3px;
            }
        """)
        
        # Ana karakter sekmesi
        main_tab = QWidget()
        main_layout = QVBoxLayout(main_tab)
        main_layout.setContentsMargins(0, 0, 0, 0)
        
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        scroll.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        container = QWidget()
        form_layout = QVBoxLayout(container)
        form_layout.setContentsMargins(10, 10, 10, 10)
        form_layout.setSpacing(15)

        form_layout.addWidget(self._build_basic_info_group())
        form_layout.addWidget(self._build_ability_group())
        form_layout.addWidget(self._build_power_group())
        form_layout.addWidget(self._build_defense_group())
        form_layout.addWidget(self._build_notes_group())
        form_layout.addWidget(self._build_summary_group())
        form_layout.addStretch()

        scroll.setWidget(container)
        main_layout.addWidget(scroll)
        self.tab_widget.addTab(main_tab, "­şÄ¡ Karakter")
        
        # Geli┼şmi┼ş sekmesi
        self.advanced_tab_mm = QWidget()
        self.advanced_layout_mm = QVBoxLayout(self.advanced_tab_mm)
        self._init_advanced_ui_mm()
        self.tab_widget.addTab(self.advanced_tab_mm, "ÔÜÖ´©Å Geli┼şmi┼ş")
        
        layout.addWidget(self.tab_widget)

        self._start_new_character()

    def _build_toolbar(self) -> QWidget:
        widget = QWidget()
        bar = QHBoxLayout(widget)
        bar.setContentsMargins(0, 0, 0, 0)

        new_btn = QPushButton("Yeni Karakter")
        new_btn.setIcon(QIcon.fromTheme("document-new"))
        new_btn.clicked.connect(self._start_new_character)

        load_btn = QPushButton("Karakter Y├╝kle")
        load_btn.setIcon(QIcon.fromTheme("document-open"))
        load_btn.clicked.connect(self._load_character)
        
        browse_btn = QPushButton("­şôï Karakterleri Listele")
        browse_btn.setToolTip("T├╝m karakterleri g├Âr├╝nt├╝le, ara ve filtrele")
        browse_btn.clicked.connect(self._browse_characters)
        
        template_btn = QPushButton("­şôØ ┼Şablonlar")
        template_btn.setToolTip("Karakter ┼şablonlar─▒n─▒ y├Ânet")
        template_btn.clicked.connect(self._manage_templates)
        
        version_btn = QPushButton("­şô£ Versiyonlar")
        version_btn.setToolTip("Karakter versiyon ge├ğmi┼şini g├Âr├╝nt├╝le ve y├Ânet")
        version_btn.clicked.connect(self._manage_versions)
        
        compare_btn = QPushButton("ÔÜû´©Å Kar┼ş─▒la┼şt─▒r")
        compare_btn.setToolTip("─░ki karakteri kar┼ş─▒la┼şt─▒r")
        compare_btn.clicked.connect(self._compare_characters)

        save_btn = QPushButton("Kaydet")
        save_btn.setIcon(QIcon.fromTheme("document-save"))
        save_btn.clicked.connect(self._save_character)

        # SQLite butonlar─▒ gizli (opsiyonel ├Âzellik)
        # sqlite_save_btn = QPushButton("SQLite Kaydet")
        # sqlite_save_btn.clicked.connect(self._save_to_sqlite)
        # sqlite_load_btn = QPushButton("SQLite Y├╝kle")
        # sqlite_load_btn.clicked.connect(self._load_from_sqlite)

        pdf_btn = QPushButton("PDF Export")
        pdf_btn.clicked.connect(self._export_pdf)
        pdf_btn.setToolTip("Karakteri PDF olarak d─▒┼şa aktar")

        batch_btn = QPushButton("­şôĞ Toplu ─░┼şlemler")
        batch_btn.setToolTip("Birden fazla karakter ├╝zerinde toplu i┼şlem yap")
        batch_btn.clicked.connect(self._show_batch_operations)

        bar.addWidget(new_btn)
        bar.addWidget(load_btn)
        bar.addWidget(browse_btn)
        bar.addWidget(template_btn)
        bar.addWidget(version_btn)
        bar.addWidget(batch_btn)
        bar.addWidget(compare_btn)
        bar.addWidget(save_btn)
        # bar.addWidget(sqlite_save_btn)
        # bar.addWidget(sqlite_load_btn)
        bar.addWidget(pdf_btn)
        bar.addStretch()

        return widget

    def _build_basic_info_group(self) -> QWidget:
        group = QGroupBox("Temel Bilgiler")
        form = QFormLayout(group)

        self.name_edit = QLineEdit()
        self.codename_edit = QLineEdit()

        self.pl_combo = QComboBox()
        self.pl_combo.addItems(self.data.get("power_levels", {}).keys())
        self.pl_combo.currentTextChanged.connect(self._update_pl_limits)

        self.archetype_combo = QComboBox()
        self.archetype_combo.addItems(self.data.get("archetypes", {}).keys())
        self.archetype_combo.currentTextChanged.connect(self._update_archetype_info)

        self.archetype_info = QTextEdit()
        self.archetype_info.setReadOnly(True)
        self.archetype_info.setFixedHeight(80)

        form.addRow("Karakter Ad─▒:", self.name_edit)
        form.addRow("Kod Ad─▒:", self.codename_edit)
        form.addRow("Power Level:", self.pl_combo)
        form.addRow("Arketip:", self.archetype_combo)
        form.addRow("Arketip ├ûzeti:", self.archetype_info)

        # Karakter resmi
        image_group = QGroupBox("­şû╝´©Å Karakter Resmi")
        image_layout = QVBoxLayout()
        
        self.mm_character_image_label = QLabel()
        self.mm_character_image_label.setMinimumSize(200, 200)
        self.mm_character_image_label.setMaximumSize(300, 300)
        self.mm_character_image_label.setAlignment(Qt.AlignCenter)
        self.mm_character_image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #95a5a6;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
        """)
        self.mm_character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")
        self.mm_character_image_label.setWordWrap(True)
        image_layout.addWidget(self.mm_character_image_label)
        
        image_buttons_layout = QHBoxLayout()
        
        load_image_btn = QPushButton("­şôÀ Resim Y├╝kle")
        load_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_image_btn.clicked.connect(self._load_character_image)
        image_buttons_layout.addWidget(load_image_btn)
        
        remove_image_btn = QPushButton("­şùæ´©Å Resmi Kald─▒r")
        remove_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_image_btn.clicked.connect(self._remove_character_image)
        image_buttons_layout.addWidget(remove_image_btn)
        
        image_layout.addLayout(image_buttons_layout)
        image_group.setLayout(image_layout)

        self.name_edit.textChanged.connect(self._refresh_summary)
        self.codename_edit.textChanged.connect(self._refresh_summary)
        self.pl_combo.currentTextChanged.connect(self._refresh_summary)

        # Ana layout'a resim grubunu ekle
        main_layout = QVBoxLayout()
        main_layout.addLayout(form)
        main_layout.addWidget(image_group)
        
        group.setLayout(main_layout)
        return group

    def _build_ability_group(self) -> QWidget:
        group = QGroupBox("Ability Scores")
        layout = QVBoxLayout(group)

        grid = QGridLayout()
        self.ability_spins: dict[str, QSpinBox] = {}
        abilities = self.data.get("abilities", [])
        for idx, ability in enumerate(abilities):
            label = QLabel(ability)
            spin = QSpinBox()
            spin.setRange(0, 20)
            spin.setValue(0)
            spin.valueChanged.connect(self._refresh_summary)
            self.ability_spins[ability] = spin

            grid.addWidget(label, idx // 4, (idx % 4) * 2)
            grid.addWidget(spin, idx // 4, (idx % 4) * 2 + 1)

        layout.addLayout(grid)
        self.pl_limit_label = QLabel("")
        layout.addWidget(self.pl_limit_label)
        self.pl_warning_label = QLabel("")
        layout.addWidget(self.pl_warning_label)

        return group

    def _build_power_group(self) -> QWidget:
        group = QGroupBox("Powers & Advantages")
        layout = QHBoxLayout(group)

        self.powers_edit = QTextEdit()
        self.powers_edit.setPlaceholderText("Her sat─▒ra bir power yaz─▒n...")
        self.powers_edit.textChanged.connect(self._refresh_summary)

        self.advantages_edit = QTextEdit()
        self.advantages_edit.setPlaceholderText("Her sat─▒ra bir advantage yaz─▒n...")
        self.advantages_edit.textChanged.connect(self._refresh_summary)

        layout.addWidget(self._wrap_with_label(self.powers_edit, "Powers"))
        layout.addWidget(self._wrap_with_label(self.advantages_edit, "Advantages"))

        return group

    def _build_defense_group(self) -> QWidget:
        group = QGroupBox("Savunmalar & PP")
        form = QFormLayout(group)

        self.defense_spins: dict[str, QSpinBox] = {}
        for key, label_text in [
            ("attack_bonus", "Attack Bonus"),
            ("effect_rank", "Effect Rank"),
            ("defense", "Defense"),
            ("toughness", "Toughness"),
        ]:
            spin = QSpinBox()
            spin.setRange(0, 20)
            spin.valueChanged.connect(self._refresh_summary)
            spin.valueChanged.connect(self._check_pl_limits)
            self.defense_spins[key] = spin
            form.addRow(label_text + ":", spin)

        self.pp_spin = QSpinBox()
        self.pp_spin.setRange(0, 300)
        self.pp_spin.valueChanged.connect(self._refresh_summary)
        form.addRow("Power Points:", self.pp_spin)

        return group

    def _build_notes_group(self) -> QWidget:
        group = QGroupBox("Notlar / Arka Plan")
        layout = QVBoxLayout(group)
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("Karakter ge├ğmi┼şi, motivasyonlar─▒ vb.")
        self.notes_edit.textChanged.connect(self._refresh_summary)
        layout.addWidget(self.notes_edit)
        return group

    def _build_summary_group(self) -> QWidget:
        group = QGroupBox("├ûzet")
        layout = QVBoxLayout(group)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        self.summary_text.setMinimumHeight(200)
        layout.addWidget(self.summary_text)
        return group

    @staticmethod
    def _wrap_with_label(widget: QWidget, label_text: str) -> QWidget:
        container = QWidget()
        vbox = QVBoxLayout(container)
        vbox.addWidget(QLabel(label_text))
        vbox.addWidget(widget)
        return container

    def _start_new_character(self):
        self.current_character = None
        self.name_edit.clear()
        self.codename_edit.clear()
        if self.pl_combo.count() > 0:
            self.pl_combo.setCurrentIndex(0)
        if self.archetype_combo.count() > 0:
            self.archetype_combo.setCurrentIndex(0)
        for spin in self.ability_spins.values():
            spin.setValue(0)
        for spin in self.defense_spins.values():
            spin.setValue(0)
        self.pp_spin.setValue(0)
        self.powers_edit.clear()
        self.advantages_edit.clear()
        self.notes_edit.clear()
        self.summary_text.clear()
        self._update_archetype_info()
        self._update_pl_limits()
        self._refresh_summary()

    def _save_character(self):
        character = self._collect_character_data()
        if not character:
            return
        default_name = character.get("codename") or character.get("name") or "mm_karakter"
        
        # E─şer mevcut dosya varsa versiyon olu┼ştur
        if hasattr(self, 'current_character_file') and self.current_character_file:
            save_character_version(
                character,
                APP_BASE_DIR,
                self.current_character_file,
                "Manuel kay─▒t"
            )
        
        _save_character_via_dialog(self, character, "M&M Karakterini Kaydet", default_name)

    def _save_to_sqlite(self):
        character = self._collect_character_data()
        if not character:
            return
        db_path_str, _ = QFileDialog.getSaveFileName(
            self,
            "SQLite'e Kaydet",
            str(APP_BASE_DIR / "characters" / "mm_characters.db"),
            "SQLite Veritaban─▒ (*.db)"
        )
        if not db_path_str:
            return
        db_path = Path(db_path_str)
        init_db(db_path)
        record = CharacterRecord(
            id=None,
            system=self.SYSTEM_NAME,
            name=character.get("name") or "─░simsiz",
            data=character,
        )
        save_character(db_path, record)
        QMessageBox.information(self, "Ba┼şar─▒l─▒", "Karakter SQLite veritaban─▒na kaydedildi.")

    def _load_character(self):
        data, path = _load_character_via_dialog(self, "M&M Karakteri Y├╝kle", self.SYSTEM_NAME)
        if not data:
            return
        self._apply_character(data)
        self.current_character = data
        self.current_character_file = path
        QMessageBox.information(self, "Ba┼şar─▒l─▒", "Karakter formu y├╝klendi.")
    
    def _browse_characters(self):
        """Karakter listesi diyalo─şunu a├ğ (t├╝m sistemler)"""
        dialog = CharacterListDialog(self, None)  # T├╝m sistemler
        dialog.setWindowTitle("Karakter Listesi - T├╝m Sistemler")
        
        if dialog.exec() == QDialog.Accepted:
            data, path = dialog.get_selected_character()
            if not data:
                return
            
            # Sistem kontrol├╝ ve ilgili sayfaya y├Ânlendirme
            system = data.get("system")
            if system == "MUTANTS_AND_MASTERMINDS":
                self._apply_character(data)
                self.current_character = data
                self.current_character_file = path
                QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{data.get('name', 'Karakter')} y├╝klendi!")
            else:
                QMessageBox.information(
                    self,
                    "Bilgi",
                    f"Bu karakter {system} sistemine ait.\n"
                    f"L├╝tfen ilgili sistem sekmesinden y├╝kleyin."
                )
    
    def _manage_templates(self):
        """┼Şablonlardan yeni M&M karakteri olu┼ştur"""
        character, character_name = _select_template_character(self, self.SYSTEM_NAME)
        if not character:
            return
        
        self._apply_character(character)
        self.current_character = character
        self.current_character_file = None
        QMessageBox.information(
            self,
            "┼Şablon Kullan─▒ld─▒",
            f"{character_name} ┼şablonu y├╝klendi. Kaydetmek i├ğin 'Kaydet' butonunu kullanabilirsiniz."
        )
    
    def _compare_characters(self):
        """Karakter kar┼ş─▒la┼şt─▒rma diyalo─şunu a├ğ"""
        dialog = CharacterComparisonDialog(self, self.SYSTEM_NAME)
        dialog.exec()
    
    def _show_batch_operations(self):
        """Toplu i┼şlemler i├ğin bilgilendirme"""
        QMessageBox.information(
            self,
            "Toplu ─░┼şlemler",
            "M&M i├ğin toplu i┼şlemler deste─şi hen├╝z bu s├╝r├╝mde aktif de─şil."
        )

    def _load_from_sqlite(self):
        db_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "SQLite'dan Y├╝kle",
            str(APP_BASE_DIR / "characters"),
            "SQLite Veritaban─▒ (*.db)"
        )
        if not db_path_str:
            return
        db_path = Path(db_path_str)
        
        dialog = SqliteCharacterDialog(self, db_path, self.SYSTEM_NAME)
        if dialog.exec() != QDialog.Accepted:
            return
        
        rec = dialog.get_selected_record()
        if not rec:
            return
        
        if rec.system != self.SYSTEM_NAME:
            QMessageBox.warning(
                self,
                "Uyar─▒",
                f"Bu karakter {rec.system} sistemine ait. "
                f"L├╝tfen {self.SYSTEM_NAME} karakterlerini y├╝kleyin."
            )
            return
        
        self._apply_character(rec.data)
        self.current_character = rec.data
        self.current_character_file = None
        QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{rec.name} y├╝klendi.")

    def _export_pdf(self):
        character = self._collect_character_data()
        if not character:
            return
        self._export_character(character)
    
    def _export_character(self, character: dict):
        """Karakteri farkl─▒ formatlarda export et"""
        dialog = ExportFormatDialog(self, character)
        if dialog.exec() == QDialog.Accepted:
            format_type, file_path = dialog.get_selected_format()
            if format_type and file_path:
                self._perform_export(character, format_type, Path(file_path))
    
    def _perform_export(self, character: dict, format_type: str, file_path: Path):
        """Export i┼şlemini ger├ğekle┼ştir"""
        try:
            system = character.get("system", "MUTANTS_AND_MASTERMINDS")
            
            if format_type == "PDF":
                # Arkaplan se├ğimi (opsiyonel - sadece PDF i├ğin)
                background_path = None
                use_bg = QMessageBox.question(
                    self,
                    "Arkaplan",
                    "PDF'e arkaplan g├Ârseli eklemek ister misiniz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if use_bg == QMessageBox.Yes:
                    bg_path_str, _ = QFileDialog.getOpenFileName(
                        self,
                        "Arkaplan G├Ârseli Se├ğ",
                        str(APP_BASE_DIR / "assets"),
                        "G├Ârsel Dosyalar─▒ (*.png *.jpg *.jpeg)"
                    )
                    if bg_path_str:
                        background_path = Path(bg_path_str)
                
                if system == "DND5E":
                    export_dnd_character_pdf(character, file_path, background_path)
                elif system == "MUTANTS_AND_MASTERMINDS":
                    export_mm_character_pdf(character, file_path, background_path)
                elif system == "VTM5E":
                    export_vtm_character_pdf(character, file_path, background_path)
            elif format_type == "HTML":
                export_character_html(character, file_path)
            elif format_type == "JSON":
                export_character_json(character, file_path)
            elif format_type == "CSV":
                export_character_csv(character, file_path)
            else:
                QMessageBox.warning(self, "Uyar─▒", f"Desteklenmeyen format: {format_type}")
                return
            
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"Karakter {format_type} format─▒nda kaydedildi:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Export s─▒ras─▒nda hata olu┼ştu:\n{str(e)}")

    def _load_rules_from_file(self):
        """Kural kitab─▒ndan kurallar─▒ y├╝kle"""
        file_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Kural Kitab─▒ Y├╝kle (PDF/TXT)",
            str(APP_BASE_DIR),
            "Dosyalar (*.pdf *.txt);;PDF Dosyalar─▒ (*.pdf);;Metin Dosyalar─▒ (*.txt)"
        )
        if not file_path_str:
            return
        
        file_path = Path(file_path_str)
        
        # NLP kullan─▒m─▒n─▒ sor (e─şer mevcut ise)
        use_nlp = False
        if is_nlp_available():
            reply = QMessageBox.question(
                self,
                "NLP Kullan─▒m─▒",
                "Geli┼şmi┼ş NLP (Do─şal Dil ─░┼şleme) ile kural ├ğ─▒karma kullan─▒ls─▒n m─▒?\n\n"
                "NLP daha karma┼ş─▒k kurallar─▒ ├ğ─▒karabilir ama daha yava┼ş olabilir.\n\n"
                "Evet: NLP kullan (├Ânerilir)\n"
                "Hay─▒r: Standart pattern matching kullan",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            use_nlp = (reply == QMessageBox.Yes)
        elif NLP_MODULE_AVAILABLE:
            # NLP mod├╝l├╝ var ama model y├╝klenmemi┼ş
            QMessageBox.information(
                self,
                "NLP Bilgisi",
                "NLP mod├╝l├╝ mevcut ancak spaCy modeli y├╝klenmemi┼ş.\n\n"
                "NLP kullanmak i├ğin:\n"
                "1. pip install spacy\n"
                "2. python -m spacy download en_core_web_sm\n\n"
                "Standart pattern matching kullan─▒lacak."
            )
        
        try:
            # Kurallar─▒ ├ğ─▒kar
            rules = extract_rules_from_file(file_path, self.SYSTEM_NAME, use_nlp=use_nlp)
            
            if not rules or not rules.get('rules'):
                QMessageBox.warning(
                    self,
                    "Uyar─▒",
                    "Dosyadan kural ├ğ─▒kar─▒lamad─▒.\n"
                    "L├╝tfen dosyan─▒n do─şru formatta oldu─şundan emin olun."
                )
                return
            
            # Kurallar─▒ do─şrula
            is_valid, issues = validate_rules(rules)
            if issues:
                report = format_validation_report(issues)
                reply = QMessageBox.question(
                    self,
                    "Kural Do─şrulama",
                    f"Kurallarda sorunlar bulundu:\n\n{report[:200]}...\n\n"
                    "Yine de kaydetmek istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
                
                # Detayl─▒ rapor g├Âster
                if not is_valid:
                    detail_msg = QMessageBox(self)
                    detail_msg.setWindowTitle("Kural Do─şrulama Detaylar─▒")
                    detail_msg.setText("Kurallarda kritik hatalar bulundu. Detaylar:")
                    detail_msg.setDetailedText(report)
                    detail_msg.setIcon(QMessageBox.Warning)
                    detail_msg.exec()
            
            # Kurallar─▒ kaydet
            saved_path = save_rules(rules, APP_BASE_DIR, self.SYSTEM_NAME)
            
            # ├ç─▒kar─▒lan kurallar─▒ g├Âster
            rules_text = json.dumps(rules, ensure_ascii=False, indent=2)
            msg = QMessageBox(self)
            msg.setWindowTitle("Kurallar Y├╝klendi")
            msg.setText(f"Kurallar ba┼şar─▒yla ├ğ─▒kar─▒ld─▒ ve kaydedildi:\n{saved_path}")
            msg.setDetailedText(rules_text)
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            
            QMessageBox.information(
                self,
                "Ba┼şar─▒l─▒",
                f"Kurallar y├╝klendi!\n{saved_path}\n\n"
                "Art─▒k hesaplamalar bu kurallara g├Âre yap─▒lacak."
            )
            
            # Cache'i yenile
            self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            # ─░statistikleri g├╝ncelle
            if hasattr(self, '_update_pl_limits'):
                self._update_pl_limits()
            
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"PDF okuma i├ğin gerekli k├╝t├╝phane eksik:\n{str(e)}\n\n"
                "L├╝tfen 'pip install PyPDF2' ile y├╝kleyin."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Kural y├╝kleme hatas─▒:\n{str(e)}"
            )

    def _collect_character_data(self) -> dict | None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Uyar─▒", "Karakter ad─▒ zorunludur.")
            return None

        archetype = self.archetype_combo.currentText()
        powers = [line.strip() for line in self.powers_edit.toPlainText().splitlines() if line.strip()]
        advantages = [line.strip() for line in self.advantages_edit.toPlainText().splitlines() if line.strip()]

        character_data = {
            "system": self.SYSTEM_NAME,
            "name": name,
            "codename": self.codename_edit.text().strip(),
            "power_level": self.pl_combo.currentText(),
            "archetype": archetype,
            "abilities": {key: spin.value() for key, spin in self.ability_spins.items()},
            "defenses": {key: spin.value() for key, spin in self.defense_spins.items()},
            "power_points": self.pp_spin.value(),
            "powers": powers,
            "advantages": advantages,
            "notes": self.notes_edit.toPlainText().strip(),
        }
        
        # Resmi ekle (varsa)
        if hasattr(self, 'current_character_image_data') and self.current_character_image_data:
            character_data["image"] = self.current_character_image_data
        
        return character_data

    def _apply_character(self, character: dict):
        self.current_character = character
        self.name_edit.setText(character.get("name", ""))
        self.codename_edit.setText(character.get("codename", ""))

        pl = character.get("power_level", "")
        idx = self.pl_combo.findText(pl)
        if idx >= 0:
            self.pl_combo.setCurrentIndex(idx)

        archetype = character.get("archetype", "")
        idx = self.archetype_combo.findText(archetype)
        if idx >= 0:
            self.archetype_combo.setCurrentIndex(idx)

        for key, spin in self.ability_spins.items():
            spin.setValue(int(character.get("abilities", {}).get(key, 0)))

        for key, spin in self.defense_spins.items():
            spin.setValue(int(character.get("defenses", {}).get(key, 0)))

        self.pp_spin.setValue(int(character.get("power_points", 0)))
        self.powers_edit.setPlainText("\n".join(character.get("powers", [])))
        self.advantages_edit.setPlainText("\n".join(character.get("advantages", [])))
        self.notes_edit.setPlainText(character.get("notes", ""))
        
        # Resmi y├╝kle
        self._load_character_image_to_gui(character)
        
        self._update_pl_limits()
        self._refresh_summary()

    def _update_archetype_info(self):
        archetype = self.archetype_combo.currentText()
        info = self.data.get("archetypes", {}).get(archetype, {})
        summary = info.get("summary", "")
        suggested_powers = ", ".join(info.get("suggested_powers", []))
        suggested_adv = ", ".join(info.get("suggested_advantages", []))

        text = summary
        if suggested_powers:
            text += f"\n├ûnerilen Powers: {suggested_powers}"
        if suggested_adv:
            text += f"\n├ûnerilen Advantages: {suggested_adv}"
        self.archetype_info.setPlainText(text.strip())
        self._refresh_summary()
        self._update_pl_limits()

    def _update_pl_limits(self):
        pl_name = self.pl_combo.currentText()
        caps = self.data.get("power_levels", {}).get(pl_name, {})
        self.current_pl_caps = caps
        
        # Power Points otomatik hesaplama - Dinamik kural deste─şi
        try:
            pl_value = int(pl_name) if pl_name.isdigit() else 1
            # ├ûnce y├╝klenen kurallar─▒ kontrol et
            if self._rules_cache is None:
                self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            calculated_pp = calculate_dynamic_power_points(pl_value, self._rules_cache)
            self.pp_spin.setValue(calculated_pp)
        except (ValueError, AttributeError):
            pass
        
        if caps:
            text = (
                f"PL {pl_name} Limitleri ÔÇö "
                f"Attack/Effekt Ôëñ {caps.get('attack_bonus_cap', '-')} / {caps.get('effect_rank_cap', '-')}, "
                f"Defense/Toughness Ôëñ {caps.get('defense_cap', '-')} / {caps.get('toughness_cap', '-')}"
            )
        else:
            text = "PL limit bilgisi bulunamad─▒."
        self.pl_limit_label.setText(text)
        self.pl_limit_label.setStyleSheet("font-weight: bold;")
        self._check_pl_limits()

    def _check_pl_limits(self):
        caps = getattr(self, "current_pl_caps", {})
        warnings = []
        for key, cap_key, label in [
            ("attack_bonus", "attack_bonus_cap", "Attack Bonus"),
            ("effect_rank", "effect_rank_cap", "Effect Rank"),
            ("defense", "defense_cap", "Defense"),
            ("toughness", "toughness_cap", "Toughness"),
        ]:
            spin = self.defense_spins[key]
            cap = caps.get(cap_key)
            if cap is None:
                spin.setStyleSheet("")
                continue
            if spin.value() > cap:
                warnings.append(f"{label}>{cap}")
                spin.setStyleSheet("color: #e74c3c; font-weight: bold;")
            else:
                spin.setStyleSheet("")
        if warnings:
            self.pl_warning_label.setText("Limit a┼ş─▒ld─▒: " + ", ".join(warnings))
            self.pl_warning_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            self.pl_warning_label.setText("Limitler dahilinde.")
            self.pl_warning_label.setStyleSheet("color: #27ae60; font-weight: bold;")

    def _load_character_image(self):
        """Karakter resmi y├╝kle (MmPage)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Karakter Resmi Se├ğ",
            "",
            "Resim Dosyalar─▒ (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;T├╝m Dosyalar (*)"
        )
        
        if file_path:
            try:
                image_path = Path(file_path)
                base64_str = _load_image_to_base64(image_path)
                
                if base64_str:
                    self.current_character_image_data = base64_str
                    
                    # Resmi g├Âster
                    pixmap = QPixmap(str(image_path))
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            300, 300,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.mm_character_image_label.setPixmap(scaled_pixmap)
                        self.mm_character_image_label.setText("")
                    
                    # Karakter verisini g├╝ncelle
                    if hasattr(self, 'current_character') and self.current_character:
                        self.current_character["image"] = base64_str
                    
                    QMessageBox.information(self, "Ba┼şar─▒l─▒", "Resim ba┼şar─▒yla y├╝klendi!")
                else:
                    QMessageBox.warning(self, "Hata", "Resim y├╝klenemedi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Resim y├╝klenirken bir hata olu┼ştu:\n{str(e)}")

    def _remove_character_image(self):
        """Karakter resmini kald─▒r (MmPage)"""
        reply = QMessageBox.question(
            self,
            "Resmi Kald─▒r",
            "Karakter resmini kald─▒rmak istedi─şinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_character_image_data = None
            self.mm_character_image_label.clear()
            self.mm_character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")
            
            # Karakter verisinden kald─▒r
            if hasattr(self, 'current_character') and self.current_character:
                if "image" in self.current_character:
                    del self.current_character["image"]
            
            QMessageBox.information(self, "Ba┼şar─▒l─▒", "Resim kald─▒r─▒ld─▒.")

    def _load_character_image_to_gui(self, character: dict):
        """Karakter verisinden resmi GUI'ye y├╝kle (MmPage)"""
        image_data = character.get("image")
        if image_data:
            self.current_character_image_data = image_data
            pixmap = _get_image_from_character(character)
            if pixmap and not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    300, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.mm_character_image_label.setPixmap(scaled_pixmap)
                self.mm_character_image_label.setText("")
            else:
                self.mm_character_image_label.setText("Resim y├╝klenemedi\n(Resim eklemek i├ğin butona t─▒klay─▒n)")
        else:
            self.current_character_image_data = None
            self.mm_character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")

    def _refresh_summary(self):
        if not hasattr(self, "summary_text"):
            return

        name = self.name_edit.text().strip() or "─░simsiz"
        codename = self.codename_edit.text().strip()
        pl = self.pl_combo.currentText()
        archetype = self.archetype_combo.currentText()

        lines = [
            f"─░sim: {name}",
            f"Kod Ad─▒: {codename or '-'}",
            f"Power Level: {pl}",
            f"Arketip: {archetype}",
            "",
            "Ability Scores:"
        ]

        for ability, spin in self.ability_spins.items():
            lines.append(f"  {ability}: {spin.value()}")

        lines.append("")
        lines.append("Savunmalar:")
        for key, label in [
            ("attack_bonus", "Attack Bonus"),
            ("effect_rank", "Effect Rank"),
            ("defense", "Defense"),
            ("toughness", "Toughness"),
        ]:
            value = self.defense_spins[key].value()
            lines.append(f"  {label}: {value}")

        lines.append("")
        lines.append(f"Power Points: {self.pp_spin.value()}")

        powers = [line.strip() for line in self.powers_edit.toPlainText().splitlines() if line.strip()]
        if powers:
            lines.append("Powers: " + ", ".join(powers))

        advantages = [line.strip() for line in self.advantages_edit.toPlainText().splitlines() if line.strip()]
        if advantages:
            lines.append("Advantages: " + ", ".join(advantages))

        notes = self.notes_edit.toPlainText().strip()
        if notes:
            lines.append("")
            lines.append("Notlar:")
            lines.append(notes)

        self.summary_text.setPlainText("\n".join(lines))
        self._check_pl_limits()

    def _init_advanced_ui_mm(self):
        """Geli┼şmi┼ş ├Âzellikler UI's─▒n─▒ olu┼ştur (opsiyonel) - M&M"""
        layout = self.advanced_layout_mm
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Ba┼şl─▒k ve a├ğ─▒klama
        title_label = QLabel("ÔÜÖ´©Å Geli┼şmi┼ş ├ûzellikler")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel(
            "Bu sekme tamamen opsiyonel ├Âzellikler i├ğerir.\n"
            "Normal karakter olu┼şturma i├ğin bu ├Âzelliklere ihtiyac─▒n─▒z yoktur."
        )
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Kural Kitab─▒ Y├╝kleme Grubu
        rules_group = QGroupBox("­şôÜ Kural Kitab─▒ Y├╝kleme (Opsiyonel)")
        rules_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        rules_layout = QVBoxLayout(rules_group)
        
        rules_info = QLabel(
            "Kural kitab─▒n─▒z─▒ (PDF veya TXT format─▒nda) y├╝kleyerek, "
            "hesaplamalar─▒n otomatik olarak bu kurallara g├Âre yap─▒lmas─▒n─▒ sa─şlayabilirsiniz.\n\n"
            "Bu ├Âzellik opsiyoneldir. Kural y├╝klemezseniz, varsay─▒lan hesaplamalar kullan─▒l─▒r."
        )
        rules_info.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 10px;")
        rules_info.setWordWrap(True)
        rules_layout.addWidget(rules_info)
        
        # Kural y├╝kleme butonu
        load_rules_btn = QPushButton("­şôä Kural Kitab─▒ Y├╝kle (PDF/TXT)")
        load_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_rules_btn.clicked.connect(self._load_rules_from_file)
        load_rules_btn.setToolTip("Kural kitab─▒ndan kurallar─▒ y├╝kle (PDF/TXT)")
        rules_layout.addWidget(load_rules_btn)
        
        # Kural d├╝zenleme butonu
        edit_rules_btn = QPushButton("Ô£Å´©Å Kural D├╝zenle")
        edit_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        edit_rules_btn.clicked.connect(self._edit_rules)
        edit_rules_btn.setToolTip("Y├╝klenen kurallar─▒ d├╝zenle (JSON format─▒nda)")
        rules_layout.addWidget(edit_rules_btn)
        
        # Kural ├Ânizleme butonu
        preview_rules_btn = QPushButton("­şæü´©Å Kurallar─▒ G├Âr├╝nt├╝le")
        preview_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        preview_rules_btn.clicked.connect(self._preview_rules)
        preview_rules_btn.setToolTip("Y├╝klenen kurallar─▒ okunabilir formatta g├Âr├╝nt├╝le")
        rules_layout.addWidget(preview_rules_btn)
        
        # Mevcut kural durumu
        self.rules_status_label_mm = QLabel("Durum: Kural y├╝klenmedi")
        self.rules_status_label_mm.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
        rules_layout.addWidget(self.rules_status_label_mm)
        
        # Kural durumunu kontrol et
        self._update_rules_status_mm()
        
        layout.addWidget(rules_group)
        layout.addStretch()

    def _update_rules_status_mm(self):
        """Kural durumunu g├╝ncelle - M&M"""
        if not hasattr(self, 'rules_status_label_mm'):
            return
        
        rules = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
        if rules and rules.get('rules'):
            self.rules_status_label_mm.setText("Ô£à Durum: Kural y├╝kl├╝ - Hesaplamalar ├Âzel kurallara g├Âre yap─▒l─▒yor")
            self.rules_status_label_mm.setStyleSheet("font-size: 11px; color: #27ae60; padding: 5px;")
        else:
            self.rules_status_label_mm.setText("Ôä╣´©Å Durum: Kural y├╝klenmedi - Varsay─▒lan hesaplamalar kullan─▒l─▒yor")
            self.rules_status_label_mm.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
    
    def _edit_rules(self):
        """Kural d├╝zenleme diyalo─şunu a├ğ"""
        dialog = RuleEditorDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle
            self._rules_cache = None
            # Durumu g├╝ncelle
            self._update_rules_status_mm()
    
    def _preview_rules(self):
        """Kural ├Ânizleme diyalo─şunu a├ğ"""
        dialog = RulePreviewDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        dialog.exec()
    
    def _manage_versions(self):
        """Kural versiyon y├Ânetimi diyalo─şunu a├ğ"""
        dialog = RuleVersionDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle (versiyon geri y├╝klendiyse)
            self._rules_cache = None
            # Durumu g├╝ncelle
            self._update_rules_status()


class VtmPage(QWidget):
    SYSTEM_NAME = "VTM5E"

    def __init__(self):
        super().__init__()
        self.data = load_vtm_data(APP_BASE_DIR)
        self.current_character: dict | None = None
        self._rules_cache = None  # Kural cache
        self.current_character_image_data = None  # Resim verisi (base64)
        self._init_ui()

    def _init_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # Header k─▒sm─▒ - Logo ve ba┼şl─▒k
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #34495e; border-radius: 10px; margin: 5px;")
        header_widget.setMaximumHeight(140)  # Header maksimum y├╝kseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Sol taraf i├ğin bo┼ş alan
        header_layout.addStretch()
        
        # Ba┼şl─▒k (logo kald─▒r─▒ld─▒)
        title = QLabel("Diyargezer - Vampire: The Masquerade")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)  # Uzun metinler i├ğin kelime kayd─▒rma
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addWidget(header_widget)

        layout.addWidget(self._build_toolbar())

        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_widget.addTab(self._build_basic_tab(), "Temel Bilgiler")
        self.tab_widget.addTab(self._build_attributes_tab(), "Attributes")
        self.tab_widget.addTab(self._build_skills_tab(), "Skills & Disciplines")
        self.tab_widget.addTab(self._build_summary_tab(), "├ûzet")
        
        # Geli┼şmi┼ş sekmesi
        self.advanced_tab_vtm = QWidget()
        self.advanced_layout_vtm = QVBoxLayout(self.advanced_tab_vtm)
        self._init_advanced_ui_vtm()
        self.tab_widget.addTab(self.advanced_tab_vtm, "ÔÜÖ´©Å Geli┼şmi┼ş")
        
        layout.addWidget(self.tab_widget)

        self._start_new_character()

    def _build_toolbar(self) -> QWidget:
        widget = QWidget()
        bar = QHBoxLayout(widget)
        bar.setContentsMargins(0, 0, 0, 0)

        new_btn = QPushButton("Yeni Karakter")
        new_btn.clicked.connect(self._start_new_character)

        load_btn = QPushButton("Karakter Y├╝kle")
        load_btn.clicked.connect(self._load_character)
        
        browse_btn = QPushButton("­şôï Karakterleri Listele")
        browse_btn.setToolTip("T├╝m karakterleri g├Âr├╝nt├╝le, ara ve filtrele")
        browse_btn.clicked.connect(self._browse_characters)
        
        template_btn = QPushButton("­şôØ ┼Şablonlar")
        template_btn.setToolTip("Karakter ┼şablonlar─▒n─▒ y├Ânet")
        template_btn.clicked.connect(self._manage_templates)
        
        version_btn = QPushButton("­şô£ Versiyonlar")
        version_btn.setToolTip("Karakter versiyon ge├ğmi┼şini g├Âr├╝nt├╝le ve y├Ânet")
        version_btn.clicked.connect(self._manage_versions)
        
        compare_btn = QPushButton("ÔÜû´©Å Kar┼ş─▒la┼şt─▒r")
        compare_btn.setToolTip("─░ki karakteri kar┼ş─▒la┼şt─▒r")
        compare_btn.clicked.connect(self._compare_characters)

        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self._save_character)

        # SQLite butonlar─▒ gizli (opsiyonel ├Âzellik)
        # sqlite_save_btn = QPushButton("SQLite Kaydet")
        # sqlite_save_btn.clicked.connect(self._save_to_sqlite)
        # sqlite_load_btn = QPushButton("SQLite Y├╝kle")
        # sqlite_load_btn.clicked.connect(self._load_from_sqlite)

        pdf_btn = QPushButton("PDF Export")
        pdf_btn.clicked.connect(self._export_pdf)

        stats_btn = QPushButton("­şôè ─░statistikler")
        stats_btn.setToolTip("Karakter istatistikleri ve analiz")
        stats_btn.clicked.connect(self._show_statistics)
        
        batch_btn = QPushButton("­şôĞ Toplu ─░┼şlemler")
        batch_btn.setToolTip("Birden fazla karakter ├╝zerinde toplu i┼şlem yap")
        batch_btn.clicked.connect(self._show_batch_operations)

        bar.addWidget(new_btn)
        bar.addWidget(load_btn)
        bar.addWidget(browse_btn)
        bar.addWidget(template_btn)
        bar.addWidget(version_btn)
        bar.addWidget(stats_btn)
        bar.addWidget(batch_btn)
        bar.addWidget(compare_btn)
        bar.addWidget(save_btn)
        # bar.addWidget(sqlite_save_btn)
        # bar.addWidget(sqlite_load_btn)
        bar.addWidget(pdf_btn)
        bar.addStretch()
        return widget
    
    def _compare_characters(self):
        """Karakter kar┼ş─▒la┼şt─▒rma diyalo─şunu a├ğ"""
        dialog = CharacterComparisonDialog(self, self.SYSTEM_NAME)
        dialog.exec()
    
    def _show_statistics(self):
        """─░statistik ├Âzeti i├ğin bilgilendirme"""
        QMessageBox.information(
            self,
            "─░statistikler",
            "VtM istatistik ├Âzeti hen├╝z bu s├╝r├╝mde i├ğinde de─şil."
        )
    
    def _manage_templates(self):
        """┼Şablonlardan yeni VtM karakteri olu┼ştur"""
        character, character_name = _select_template_character(self, self.SYSTEM_NAME)
        if not character:
            return
        
        self._apply_character(character)
        self.current_character = character
        self.current_character_file = None
        QMessageBox.information(
            self,
            "┼Şablon Kullan─▒ld─▒",
            f"{character_name} ┼şablonu y├╝klendi. Kaydetmek i├ğin 'Kaydet' butonunu kullanabilirsiniz."
        )
    
    def _show_batch_operations(self):
        """Toplu i┼şlemler i├ğin bilgilendirme"""
        QMessageBox.information(
            self,
            "Toplu ─░┼şlemler",
            "VtM i├ğin toplu i┼şlemler deste─şi hen├╝z bu s├╝r├╝mde aktif de─şil."
        )
    
    def _manage_versions(self):
        """Kural versiyon y├Ânetimi diyalo─şunu a├ğ"""
        dialog = RuleVersionDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            self._rules_cache = None
            self._update_rules_status_vtm()

    def _build_basic_tab(self) -> QWidget:
        widget = QWidget()
        form = QFormLayout(widget)

        self.vtm_name_edit = QLineEdit()
        self.player_edit = QLineEdit()
        self.chronicle_edit = QLineEdit()
        self.concept_edit = QLineEdit()
        self.ambition_edit = QLineEdit()
        self.desire_edit = QLineEdit()
        self.sire_edit = QLineEdit()
        self.predator_edit = QLineEdit()

        self.clan_combo = QComboBox()
        self.clan_combo.addItems(self.data.get("clans", {}).keys())
        self.clan_combo.currentTextChanged.connect(self._update_clan_info)

        self.clan_bane_label = QLabel("")
        self.clan_bane_label.setWordWrap(True)
        self.clan_disciplines_label = QLabel("")
        self.clan_disciplines_label.setWordWrap(True)

        form.addRow("Karakter Ad─▒:", self.vtm_name_edit)
        form.addRow("Oyuncu:", self.player_edit)
        form.addRow("Chronicle:", self.chronicle_edit)
        form.addRow("Concept:", self.concept_edit)
        form.addRow("Ambition:", self.ambition_edit)
        form.addRow("Desire:", self.desire_edit)
        form.addRow("Predator Type:", self.predator_edit)
        form.addRow("Sire:", self.sire_edit)
        form.addRow("Clan:", self.clan_combo)
        form.addRow("Bane:", self.clan_bane_label)
        form.addRow("Clan Disciplines:", self.clan_disciplines_label)

        # Karakter resmi
        image_group = QGroupBox("­şû╝´©Å Karakter Resmi")
        image_layout = QVBoxLayout()
        
        self.vtm_character_image_label = QLabel()
        self.vtm_character_image_label.setMinimumSize(200, 200)
        self.vtm_character_image_label.setMaximumSize(300, 300)
        self.vtm_character_image_label.setAlignment(Qt.AlignCenter)
        self.vtm_character_image_label.setStyleSheet("""
            QLabel {
                border: 2px dashed #95a5a6;
                border-radius: 8px;
                background-color: #ecf0f1;
            }
        """)
        self.vtm_character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")
        self.vtm_character_image_label.setWordWrap(True)
        image_layout.addWidget(self.vtm_character_image_label)
        
        image_buttons_layout = QHBoxLayout()
        
        load_image_btn = QPushButton("­şôÀ Resim Y├╝kle")
        load_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_image_btn.clicked.connect(self._load_character_image)
        image_buttons_layout.addWidget(load_image_btn)
        
        remove_image_btn = QPushButton("­şùæ´©Å Resmi Kald─▒r")
        remove_image_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        remove_image_btn.clicked.connect(self._remove_character_image)
        image_buttons_layout.addWidget(remove_image_btn)
        
        image_layout.addLayout(image_buttons_layout)
        image_group.setLayout(image_layout)

        for widget_field in [
            self.vtm_name_edit,
            self.player_edit,
            self.chronicle_edit,
            self.concept_edit,
            self.ambition_edit,
            self.desire_edit,
            self.predator_edit,
            self.sire_edit,
        ]:
            widget_field.textChanged.connect(self._refresh_summary)

        # Ana layout'a resim grubunu ekle
        main_layout = QVBoxLayout()
        main_layout.addLayout(form)
        main_layout.addWidget(image_group)
        
        widget.setLayout(main_layout)
        return widget

    def _load_character_image(self):
        """VtM karakter resmi y├╝kle"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Karakter Resmi Se├ğ",
            "",
            "Resim Dosyalar─▒ (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;T├╝m Dosyalar (*)"
        )
        if not file_path:
            return

        try:
            image_path = Path(file_path)
            base64_str = _load_image_to_base64(image_path)
            if not base64_str:
                QMessageBox.warning(self, "Hata", "Resim y├╝klenemedi.")
                return

            self.current_character_image_data = base64_str

            pixmap = QPixmap(str(image_path))
            if not pixmap.isNull():
                scaled_pixmap = pixmap.scaled(
                    300,
                    300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.vtm_character_image_label.setPixmap(scaled_pixmap)
                self.vtm_character_image_label.setText("")

            if self.current_character:
                self.current_character["image"] = base64_str
                self._auto_save_character()

            QMessageBox.information(self, "Ba┼şar─▒l─▒", "Resim ba┼şar─▒yla y├╝klendi!")
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"Resim y├╝klenirken bir hata olu┼ştu:\n{exc}")

    def _remove_character_image(self):
        """VtM karakter resmini kald─▒r"""
        reply = QMessageBox.question(
            self,
            "Resmi Kald─▒r",
            "Karakter resmini kald─▒rmak istedi─şinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.current_character_image_data = None
        self.vtm_character_image_label.clear()
        self.vtm_character_image_label.setText("Resim yok\n(Resim eklemek i├ğin butona t─▒klay─▒n)")

        if self.current_character and "image" in self.current_character:
            del self.current_character["image"]
            self._auto_save_character()

        QMessageBox.information(self, "Ba┼şar─▒l─▒", "Resim kald─▒r─▒ld─▒.")

    def _build_attributes_tab(self) -> QWidget:
        widget = QWidget()
        grid = QGridLayout(widget)

        self.attribute_spins: dict[str, dict[str, QSpinBox]] = {}
        attributes = self.data.get("attributes", {})

        for col, (category, attrs) in enumerate(attributes.items()):
            group = QGroupBox(category)
            form = QFormLayout(group)
            self.attribute_spins[category] = {}
            for attr in attrs:
                spin = QSpinBox()
                spin.setRange(0, 5)
                spin.valueChanged.connect(self._refresh_summary)
                spin.valueChanged.connect(self._update_attribute_summary)
                form.addRow(attr + ":", spin)
                self.attribute_spins[category][attr] = spin
            grid.addWidget(group, 0, col)

        self.humanity_spin = QSpinBox()
        self.humanity_spin.setRange(0, 10)
        self.humanity_spin.valueChanged.connect(self._refresh_summary)
        humanity_group = QGroupBox("Humanity")
        h_layout = QVBoxLayout(humanity_group)
        h_layout.addWidget(self.humanity_spin)
        grid.addWidget(humanity_group, 1, 0)

        self.attribute_summary_label = QLabel("")
        self.attribute_summary_label.setWordWrap(True)
        grid.addWidget(self.attribute_summary_label, 2, 0, 1, len(attributes))

        return widget

    def _build_skills_tab(self) -> QWidget:
        widget = QWidget()
        layout = QHBoxLayout(widget)

        self.skill_spins: dict[str, dict[str, QSpinBox]] = {}
        skills = self.data.get("skills", {})

        skills_container = QWidget()
        skills_layout = QHBoxLayout(skills_container)
        for category, skill_list in skills.items():
            group = QGroupBox(category)
            form = QFormLayout(group)
            self.skill_spins[category] = {}
            for skill in skill_list:
                spin = QSpinBox()
                spin.setRange(0, 5)
                spin.valueChanged.connect(self._refresh_summary)
                spin.valueChanged.connect(self._update_skill_summary)
                form.addRow(skill + ":", spin)
                self.skill_spins[category][skill] = spin
            skills_layout.addWidget(group)
        layout.addWidget(skills_container, 3)

        self.skill_summary_label = QLabel("")
        self.skill_summary_label.setWordWrap(True)
        layout.addWidget(self.skill_summary_label, alignment=Qt.AlignTop)

        disciplines_group = QGroupBox("Disciplines")
        d_layout = QVBoxLayout(disciplines_group)
        self.discipline_list = QListWidget()
        self.discipline_items: dict[str, QListWidgetItem] = {}

        all_disciplines = set()
        for clan in self.data.get("clans", {}).values():
            for disc in clan.get("disciplines", []):
                all_disciplines.add(disc)

        for disc in sorted(all_disciplines):
            item = QListWidgetItem(disc)
            item.setFlags(item.flags() | Qt.ItemIsUserCheckable)
            item.setCheckState(Qt.Unchecked)
            self.discipline_list.addItem(item)
            self.discipline_items[disc] = item

        self.extra_discipline_edit = QLineEdit()
        self.extra_discipline_edit.setPlaceholderText("Virg├╝lle ayr─▒lm─▒┼ş ek disiplinler")
        self.extra_discipline_edit.textChanged.connect(self._refresh_summary)

        d_layout.addWidget(QLabel("Klan disiplinlerini i┼şaretleyin:"))
        d_layout.addWidget(self.discipline_list)
        d_layout.addWidget(QLabel("Ek Disiplinler:"))
        d_layout.addWidget(self.extra_discipline_edit)

        layout.addWidget(disciplines_group, 2)

        return widget

    def _build_summary_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.notes_edit_vtm = QTextEdit()
        self.notes_edit_vtm.setPlaceholderText("K─▒sa arka plan / Touchstones vb.")
        self.notes_edit_vtm.textChanged.connect(self._refresh_summary)

        self.summary_text_vtm = QTextEdit()
        self.summary_text_vtm.setReadOnly(True)

        layout.addWidget(QLabel("Notlar"))
        layout.addWidget(self.notes_edit_vtm)
        layout.addWidget(QLabel("├ûzet"))
        layout.addWidget(self.summary_text_vtm)

        return widget

    def _start_new_character(self):
        self.current_character = None
        for edit in [
            self.vtm_name_edit,
            self.player_edit,
            self.chronicle_edit,
            self.concept_edit,
            self.ambition_edit,
            self.desire_edit,
            self.predator_edit,
            self.sire_edit,
        ]:
            edit.clear()
        if self.clan_combo.count() > 0:
            self.clan_combo.setCurrentIndex(0)

        for category in self.attribute_spins.values():
            for spin in category.values():
                spin.setValue(0)

        for category in self.skill_spins.values():
            for spin in category.values():
                spin.setValue(0)

        for item in self.discipline_items.values():
            item.setCheckState(Qt.Unchecked)
        self.extra_discipline_edit.clear()
        self.humanity_spin.setValue(7)
        self.notes_edit_vtm.clear()
        self.summary_text_vtm.clear()
        self._update_clan_info()
        self._update_attribute_summary()
        self._update_skill_summary()
        self._refresh_summary()

    def _save_character(self):
        character = self._collect_character_data()
        if not character:
            return
        default_name = character.get("name") or "vtm_karakter"
        
        # E─şer mevcut dosya varsa versiyon olu┼ştur
        if hasattr(self, 'current_character_file') and self.current_character_file:
            save_character_version(
                character,
                APP_BASE_DIR,
                self.current_character_file,
                "Manuel kay─▒t"
            )
        
        _save_character_via_dialog(self, character, "VtM Karakterini Kaydet", default_name)

    def _save_to_sqlite(self):
        character = self._collect_character_data()
        if not character:
            return
        db_path_str, _ = QFileDialog.getSaveFileName(
            self,
            "SQLite'e Kaydet",
            str(APP_BASE_DIR / "characters" / "vtm_characters.db"),
            "SQLite Veritaban─▒ (*.db)"
        )
        if not db_path_str:
            return
        db_path = Path(db_path_str)
        init_db(db_path)
        record = CharacterRecord(
            id=None,
            system=self.SYSTEM_NAME,
            name=character.get("name") or "─░simsiz",
            data=character,
        )
        save_character(db_path, record)
        QMessageBox.information(self, "Ba┼şar─▒l─▒", "Karakter SQLite veritaban─▒na kaydedildi.")

    def _load_character(self):
        data, path = _load_character_via_dialog(self, "VtM Karakteri Y├╝kle", self.SYSTEM_NAME)
        if not data:
            return
        self._apply_character(data)
        self.current_character = data
        self.current_character_file = path
        
        # Son a├ğ─▒lanlara ekle
        if path:
            add_recent_character(APP_BASE_DIR, path, data.get("name", ""))
        
        QMessageBox.information(self, "Ba┼şar─▒l─▒", "VtM karakteri y├╝klendi.")

    def _browse_characters(self):
        """Karakter listesi diyalo─şunu a├ğ ve VtM karakteri se├ğ"""
        dialog = CharacterListDialog(self, None)
        dialog.setWindowTitle("Karakter Listesi - T├╝m Sistemler")
        if dialog.exec() != QDialog.Accepted:
            return

        data, path = dialog.get_selected_character()
        if not data:
            return

        system = data.get("system")
        if system == self.SYSTEM_NAME:
            self._apply_character(data)
            self.current_character = data
            self.current_character_file = path
            if path:
                add_recent_character(APP_BASE_DIR, path, data.get("name", ""))
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{data.get('name', 'Karakter')} y├╝klendi!")
        else:
            QMessageBox.information(
                self,
                "Bilgi",
                f"Bu karakter {system} sistemine ait.\nL├╝tfen ilgili sekmeden y├╝kleyin."
            )

    def _load_from_sqlite(self):
        db_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "SQLite'dan Y├╝kle",
            str(APP_BASE_DIR / "characters"),
            "SQLite Veritaban─▒ (*.db)"
        )
        if not db_path_str:
            return
        db_path = Path(db_path_str)
        
        dialog = SqliteCharacterDialog(self, db_path, self.SYSTEM_NAME)
        if dialog.exec() != QDialog.Accepted:
            return
        
        rec = dialog.get_selected_record()
        if not rec:
            return
        
        if rec.system != self.SYSTEM_NAME:
            QMessageBox.warning(
                self,
                "Uyar─▒",
                f"Bu karakter {rec.system} sistemine ait. "
                f"L├╝tfen {self.SYSTEM_NAME} karakterlerini y├╝kleyin."
            )
            return
        
        self._apply_character(rec.data)
        self.current_character = rec.data
        self.current_character_file = None
        QMessageBox.information(self, "Ba┼şar─▒l─▒", f"{rec.name} y├╝klendi.")

    def _load_rules_from_file(self):
        """Kural kitab─▒ndan kurallar─▒ y├╝kle"""
        file_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Kural Kitab─▒ Y├╝kle (PDF/TXT)",
            str(APP_BASE_DIR),
            "Dosyalar (*.pdf *.txt);;PDF Dosyalar─▒ (*.pdf);;Metin Dosyalar─▒ (*.txt)"
        )
        if not file_path_str:
            return
        
        file_path = Path(file_path_str)
        
        # NLP kullan─▒m─▒n─▒ sor (e─şer mevcut ise)
        use_nlp = False
        if is_nlp_available():
            reply = QMessageBox.question(
                self,
                "NLP Kullan─▒m─▒",
                "Geli┼şmi┼ş NLP (Do─şal Dil ─░┼şleme) ile kural ├ğ─▒karma kullan─▒ls─▒n m─▒?\n\n"
                "NLP daha karma┼ş─▒k kurallar─▒ ├ğ─▒karabilir ama daha yava┼ş olabilir.\n\n"
                "Evet: NLP kullan (├Ânerilir)\n"
                "Hay─▒r: Standart pattern matching kullan",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            use_nlp = (reply == QMessageBox.Yes)
        elif NLP_MODULE_AVAILABLE:
            # NLP mod├╝l├╝ var ama model y├╝klenmemi┼ş
            QMessageBox.information(
                self,
                "NLP Bilgisi",
                "NLP mod├╝l├╝ mevcut ancak spaCy modeli y├╝klenmemi┼ş.\n\n"
                "NLP kullanmak i├ğin:\n"
                "1. pip install spacy\n"
                "2. python -m spacy download en_core_web_sm\n\n"
                "Standart pattern matching kullan─▒lacak."
            )
        
        try:
            # Kurallar─▒ ├ğ─▒kar
            rules = extract_rules_from_file(file_path, self.SYSTEM_NAME, use_nlp=use_nlp)
            
            if not rules or not rules.get('rules'):
                QMessageBox.warning(
                    self,
                    "Uyar─▒",
                    "Dosyadan kural ├ğ─▒kar─▒lamad─▒.\n"
                    "L├╝tfen dosyan─▒n do─şru formatta oldu─şundan emin olun."
                )
                return
            
            # Kurallar─▒ do─şrula
            is_valid, issues = validate_rules(rules)
            if issues:
                report = format_validation_report(issues)
                reply = QMessageBox.question(
                    self,
                    "Kural Do─şrulama",
                    f"Kurallarda sorunlar bulundu:\n\n{report[:200]}...\n\n"
                    "Yine de kaydetmek istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
                
                # Detayl─▒ rapor g├Âster
                if not is_valid:
                    detail_msg = QMessageBox(self)
                    detail_msg.setWindowTitle("Kural Do─şrulama Detaylar─▒")
                    detail_msg.setText("Kurallarda kritik hatalar bulundu. Detaylar:")
                    detail_msg.setDetailedText(report)
                    detail_msg.setIcon(QMessageBox.Warning)
                    detail_msg.exec()
            
            # Kurallar─▒ kaydet
            saved_path = save_rules(rules, APP_BASE_DIR, self.SYSTEM_NAME)
            
            # ├ç─▒kar─▒lan kurallar─▒ g├Âster
            rules_text = json.dumps(rules, ensure_ascii=False, indent=2)
            msg = QMessageBox(self)
            msg.setWindowTitle("Kurallar Y├╝klendi")
            msg.setText(f"Kurallar ba┼şar─▒yla ├ğ─▒kar─▒ld─▒ ve kaydedildi:\n{saved_path}")
            msg.setDetailedText(rules_text)
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            
            QMessageBox.information(
                self,
                "Ba┼şar─▒l─▒",
                f"Kurallar y├╝klendi!\n{saved_path}\n\n"
                "Art─▒k hesaplamalar bu kurallara g├Âre yap─▒lacak."
            )
            
            # Cache'i yenile
            self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            # ─░statistikleri g├╝ncelle
            if hasattr(self, '_refresh_summary'):
                self._refresh_summary()
            # Kural durumunu g├╝ncelle
            if hasattr(self, '_update_rules_status_vtm'):
                self._update_rules_status_vtm()
            
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"PDF okuma i├ğin gerekli k├╝t├╝phane eksik:\n{str(e)}\n\n"
                "L├╝tfen 'pip install PyPDF2' ile y├╝kleyin."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Kural y├╝kleme hatas─▒:\n{str(e)}"
            )

    def _export_pdf(self):
        character = self._collect_character_data()
        if not character:
            return
        self._export_character(character)
    
    def _export_character(self, character: dict):
        """Karakteri farkl─▒ formatlarda export et"""
        dialog = ExportFormatDialog(self, character)
        if dialog.exec() == QDialog.Accepted:
            format_type, file_path = dialog.get_selected_format()
            if format_type and file_path:
                self._perform_export(character, format_type, Path(file_path))
    
    def _perform_export(self, character: dict, format_type: str, file_path: Path):
        """Export i┼şlemini ger├ğekle┼ştir"""
        try:
            system = character.get("system", "VTM5E")
            
            if format_type == "PDF":
                # Arkaplan se├ğimi (opsiyonel - sadece PDF i├ğin)
                background_path = None
                use_bg = QMessageBox.question(
                    self,
                    "Arkaplan",
                    "PDF'e arkaplan g├Ârseli eklemek ister misiniz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if use_bg == QMessageBox.Yes:
                    bg_path_str, _ = QFileDialog.getOpenFileName(
                        self,
                        "Arkaplan G├Ârseli Se├ğ",
                        str(APP_BASE_DIR / "assets"),
                        "G├Ârsel Dosyalar─▒ (*.png *.jpg *.jpeg)"
                    )
                    if bg_path_str:
                        background_path = Path(bg_path_str)
                
                if system == "DND5E":
                    export_dnd_character_pdf(character, file_path, background_path)
                elif system == "MUTANTS_AND_MASTERMINDS":
                    export_mm_character_pdf(character, file_path, background_path)
                elif system == "VTM5E":
                    export_vtm_character_pdf(character, file_path, background_path)
            elif format_type == "HTML":
                export_character_html(character, file_path)
            elif format_type == "JSON":
                export_character_json(character, file_path)
            elif format_type == "CSV":
                export_character_csv(character, file_path)
            else:
                QMessageBox.warning(self, "Uyar─▒", f"Desteklenmeyen format: {format_type}")
                return
            
            QMessageBox.information(self, "Ba┼şar─▒l─▒", f"Karakter {format_type} format─▒nda kaydedildi:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Export s─▒ras─▒nda hata olu┼ştu:\n{str(e)}")

    def _collect_character_data(self, validate: bool = True) -> dict | None:
        name = self.vtm_name_edit.text().strip()
        if not name:
            if validate:
                QMessageBox.warning(self, "Uyar─▒", "Karakter ad─▒ zorunludur.")
                return None
            name = "─░simsiz"

        attributes = {
            category: {attr: spin.value() for attr, spin in spins.items()}
            for category, spins in self.attribute_spins.items()
        }
        skills = {
            category: {skill: spin.value() for skill, spin in spins.items()}
            for category, spins in self.skill_spins.items()
        }

        disciplines = self._gather_selected_disciplines()

        # Health ve Willpower otomatik hesaplama - Dinamik kural deste─şi
        character_temp = {
            "attributes": attributes,
            "humanity": self.humanity_spin.value()
        }
        # ├ûnce y├╝klenen kurallar─▒ kontrol et
        if self._rules_cache is None:
            self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
        health = calculate_dynamic_health(character_temp, self._rules_cache)
        willpower = calculate_dynamic_willpower(character_temp, self._rules_cache)

        character_data = {
            "system": self.SYSTEM_NAME,
            "name": name,
            "player": self.player_edit.text().strip(),
            "chronicle": self.chronicle_edit.text().strip(),
            "concept": self.concept_edit.text().strip(),
            "ambition": self.ambition_edit.text().strip(),
            "desire": self.desire_edit.text().strip(),
            "predator_type": self.predator_edit.text().strip(),
            "sire": self.sire_edit.text().strip(),
            "clan": self.clan_combo.currentText(),
            "attributes": attributes,
            "skills": skills,
            "disciplines": disciplines,
            "humanity": self.humanity_spin.value(),
            "health": health,
            "willpower": willpower,
            "notes": self.notes_edit_vtm.toPlainText().strip(),
        }
        
        # Resmi ekle (varsa)
        if hasattr(self, 'current_character_image_data') and self.current_character_image_data:
            character_data["image"] = self.current_character_image_data
        
        return character_data

    def _apply_character(self, character: dict):
        self.current_character = character

        self.vtm_name_edit.setText(character.get("name", ""))
        self.player_edit.setText(character.get("player", ""))
        self.chronicle_edit.setText(character.get("chronicle", ""))
        self.concept_edit.setText(character.get("concept", ""))
        self.ambition_edit.setText(character.get("ambition", ""))
        self.desire_edit.setText(character.get("desire", ""))
        self.predator_edit.setText(character.get("predator_type", ""))
        self.sire_edit.setText(character.get("sire", ""))

        clan = character.get("clan", "")
        idx = self.clan_combo.findText(clan)
        if idx >= 0:
            self.clan_combo.setCurrentIndex(idx)

        for category, spins in self.attribute_spins.items():
            for attr, spin in spins.items():
                spin.setValue(int(character.get("attributes", {}).get(category, {}).get(attr, 0)))

        for category, spins in self.skill_spins.items():
            for skill, spin in spins.items():
                spin.setValue(int(character.get("skills", {}).get(category, {}).get(skill, 0)))

        for item in self.discipline_items.values():
            item.setCheckState(Qt.Unchecked)
        self.extra_discipline_edit.clear()
        for disc in character.get("disciplines", []):
            if disc in self.discipline_items:
                self.discipline_items[disc].setCheckState(Qt.Checked)
            else:
                # Append to extra discipline text if custom
                extra = self.extra_discipline_edit.text().strip()
                extras = [e.strip() for e in extra.split(",") if e.strip()]
                if disc not in extras:
                    extras.append(disc)
                    self.extra_discipline_edit.setText(", ".join(extras))

        self.humanity_spin.setValue(int(character.get("humanity", 7)))
        self.notes_edit_vtm.setPlainText(character.get("notes", ""))
        self._refresh_summary()

    def _gather_selected_disciplines(self) -> list[str]:
        selected = [name for name, item in self.discipline_items.items() if item.checkState() == Qt.Checked]
        extra = [part.strip() for part in self.extra_discipline_edit.text().split(",") if part.strip()]
        return selected + extra

    def _update_clan_info(self):
        clan_name = self.clan_combo.currentText()
        clan = self.data.get("clans", {}).get(clan_name, {})
        self.clan_bane_label.setText(clan.get("bane", ""))
        self.clan_disciplines_label.setText(", ".join(clan.get("disciplines", [])))
        self._refresh_summary()
        self._update_attribute_summary()
        self._update_skill_summary()

    def _update_attribute_summary(self):
        if not hasattr(self, "attribute_spins"):
            return
        lines = []
        total = 0
        for category, spins in self.attribute_spins.items():
            cat_total = sum(spin.value() for spin in spins.values())
            total += cat_total
            lines.append(f"{category}: {cat_total} nokta")
        lines.append(f"Toplam: {total} nokta")
        if hasattr(self, "attribute_summary_label"):
            self.attribute_summary_label.setText(" | ".join(lines))

    def _update_skill_summary(self):
        if not hasattr(self, "skill_spins"):
            return
        lines = []
        total = 0
        for category, spins in self.skill_spins.items():
            cat_total = sum(spin.value() for spin in spins.values())
            total += cat_total
            lines.append(f"{category}: {cat_total}")
        lines.append(f"Toplam: {total}")
        if hasattr(self, "skill_summary_label"):
            self.skill_summary_label.setText(" | ".join(lines))

    def _init_advanced_ui_vtm(self):
        """Geli┼şmi┼ş ├Âzellikler UI's─▒n─▒ olu┼ştur (opsiyonel) - VtM"""
        layout = self.advanced_layout_vtm
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Ba┼şl─▒k ve a├ğ─▒klama
        title_label = QLabel("ÔÜÖ´©Å Geli┼şmi┼ş ├ûzellikler")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel(
            "Bu sekme tamamen opsiyonel ├Âzellikler i├ğerir.\n"
            "Normal karakter olu┼şturma i├ğin bu ├Âzelliklere ihtiyac─▒n─▒z yoktur."
        )
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Kural Kitab─▒ Y├╝kleme Grubu
        rules_group = QGroupBox("­şôÜ Kural Kitab─▒ Y├╝kleme (Opsiyonel)")
        rules_group.setStyleSheet("""
            QGroupBox {
                font-size: 16px;
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
            }
        """)
        rules_layout = QVBoxLayout(rules_group)
        
        rules_info = QLabel(
            "Kural kitab─▒n─▒z─▒ (PDF veya TXT format─▒nda) y├╝kleyerek, "
            "hesaplamalar─▒n otomatik olarak bu kurallara g├Âre yap─▒lmas─▒n─▒ sa─şlayabilirsiniz.\n\n"
            "Bu ├Âzellik opsiyoneldir. Kural y├╝klemezseniz, varsay─▒lan hesaplamalar kullan─▒l─▒r."
        )
        rules_info.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 10px;")
        rules_info.setWordWrap(True)
        rules_layout.addWidget(rules_info)
        
        # Kural y├╝kleme butonu
        load_rules_btn = QPushButton("­şôä Kural Kitab─▒ Y├╝kle (PDF/TXT)")
        load_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        load_rules_btn.clicked.connect(self._load_rules_from_file)
        load_rules_btn.setToolTip("Kural kitab─▒ndan kurallar─▒ y├╝kle (PDF/TXT)")
        rules_layout.addWidget(load_rules_btn)
        
        # Kural d├╝zenleme butonu
        edit_rules_btn = QPushButton("Ô£Å´©Å Kural D├╝zenle")
        edit_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #9b59b6;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #8e44ad;
            }
        """)
        edit_rules_btn.clicked.connect(self._edit_rules)
        edit_rules_btn.setToolTip("Y├╝klenen kurallar─▒ d├╝zenle (JSON format─▒nda)")
        rules_layout.addWidget(edit_rules_btn)
        
        # Kural ├Ânizleme butonu
        preview_rules_btn = QPushButton("­şæü´©Å Kurallar─▒ G├Âr├╝nt├╝le")
        preview_rules_btn.setStyleSheet("""
            QPushButton {
                background-color: #16a085;
                color: white;
                border: none;
                padding: 12px 24px;
                font-size: 14px;
                font-weight: bold;
                border-radius: 6px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #138d75;
            }
        """)
        preview_rules_btn.clicked.connect(self._preview_rules)
        preview_rules_btn.setToolTip("Y├╝klenen kurallar─▒ okunabilir formatta g├Âr├╝nt├╝le")
        rules_layout.addWidget(preview_rules_btn)
        
        # Mevcut kural durumu
        self.rules_status_label_vtm = QLabel("Durum: Kural y├╝klenmedi")
        self.rules_status_label_vtm.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
        rules_layout.addWidget(self.rules_status_label_vtm)
        
        # Kural durumunu kontrol et
        self._update_rules_status_vtm()
        
        layout.addWidget(rules_group)
        layout.addStretch()

    def _update_rules_status_vtm(self):
        """Kural durumunu g├╝ncelle - VtM"""
        if not hasattr(self, 'rules_status_label_vtm'):
            return
        
        rules = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
        if rules and rules.get('rules'):
            self.rules_status_label_vtm.setText("Ô£à Durum: Kural y├╝kl├╝ - Hesaplamalar ├Âzel kurallara g├Âre yap─▒l─▒yor")
            self.rules_status_label_vtm.setStyleSheet("font-size: 11px; color: #27ae60; padding: 5px;")
        else:
            self.rules_status_label_vtm.setText("Ôä╣´©Å Durum: Kural y├╝klenmedi - Varsay─▒lan hesaplamalar kullan─▒l─▒yor")
            self.rules_status_label_vtm.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
    
    def _edit_rules(self):
        """Kural d├╝zenleme diyalo─şunu a├ğ"""
        dialog = RuleEditorDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle
            self._rules_cache = None
            # Durumu g├╝ncelle
            self._update_rules_status_vtm()

    def _preview_rules(self):
        """VtM kurallar─▒n─▒ ├Ânizle"""
        dialog = RulePreviewDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        dialog.exec()

    def _refresh_summary(self):
        if not hasattr(self, "summary_text_vtm"):
            return

        character = self._collect_character_data(validate=False)
        if not character:
            self.summary_text_vtm.clear()
            return

        lines = [
            f"─░sim: {character['name']}",
            f"Clan: {character.get('clan', '-')}",
            f"Chronicle: {character.get('chronicle', '-')}",
            f"Concept: {character.get('concept', '-')}",
            "",
            "Attributes:"
        ]
        for category, attrs in character.get("attributes", {}).items():
            lines.append(f"  {category}: " + ", ".join(f"{attr} {value}" for attr, value in attrs.items()))

        lines.append("")
        lines.append("Skills:")
        for category, skills in character.get("skills", {}).items():
            nonzero = [f"{skill} {value}" for skill, value in skills.items() if value]
            if nonzero:
                lines.append(f"  {category}: " + ", ".join(nonzero))

        disciplines = character.get("disciplines", [])
        if disciplines:
            lines.append("")
            lines.append("Disciplines: " + ", ".join(disciplines))

        lines.append("")
        lines.append(f"Humanity: {character.get('humanity', 0)}")
        lines.append(f"Health: {character.get('health', 0)}")
        lines.append(f"Willpower: {character.get('willpower', 0)}")

        notes = character.get("notes")
        if notes:
            lines.append("")
            lines.append("Notlar:")
            lines.append(notes)

        self.summary_text_vtm.setPlainText("\n".join(lines))
        self._update_attribute_summary()
        self._update_skill_summary()


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diyargezer - FRP Karakter Olu┼şturucu")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Dark theme uygula
        self._apply_dark_theme()
        
        # Keyboard shortcuts ekle
        self._setup_shortcuts()
        
        # Pencere ikonu ayarla
        self._set_window_icon()

        # Ana widget olu┼ştur (logo header + tab widget)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Logo header ekle
        header_widget = self._create_header()
        header_widget.setMaximumHeight(140)  # Header maksimum y├╝kseklik
        main_layout.addWidget(header_widget)
        
        # Tab widget
        central = QtWidgets.QTabWidget()
        central.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        central.addTab(DndPage(), "­şÄ▓ D&D 5e")
        central.addTab(MmPage(), "­şĞ© M&M")
        central.addTab(VtmPage(), "­şğø VtM")
        main_layout.addWidget(central)
        
        self.setCentralWidget(main_widget)

    def _apply_dark_theme(self):
        """Dark theme uygula"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #2c3e50;
                color: #ecf0f1;
            }
            QTabWidget::pane {
                border: 2px solid #34495e;
                border-radius: 8px;
                background-color: #2c3e50;
                margin-top: -2px;
            }
            QTabBar::tab {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #34495e, stop: 1 #2c3e50);
                color: #ecf0f1;
                padding: 12px 24px;
                margin-right: 3px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
                border: 1px solid #34495e;
            }
            QTabBar::tab:selected {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #3498db, stop: 1 #2980b9);
                border-bottom: 2px solid #3498db;
            }
            QTabBar::tab:hover {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #5dade2, stop: 1 #3498db);
            }
            QTabBar::tab:!selected {
                margin-top: 3px;
            }
            QGroupBox {
                font-weight: bold;
                border: 2px solid #34495e;
                border-radius: 8px;
                margin-top: 10px;
                padding-top: 10px;
                background-color: #34495e;
                color: #ecf0f1;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 10px 0 10px;
                background-color: #2c3e50;
            }
        """)

    def _setup_shortcuts(self):
        """Keyboard shortcuts ayarla"""
        # Ctrl+N: Yeni karakter
        new_char_shortcut = QShortcut(QKeySequence("Ctrl+N"), self)
        new_char_shortcut.activated.connect(self._new_character_shortcut)
        
        # Ctrl+O: Karakter y├╝kle
        load_char_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        load_char_shortcut.activated.connect(self._load_character_shortcut)
        
        # Ctrl+S: Karakter kaydet
        save_char_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_char_shortcut.activated.connect(self._save_character_shortcut)
        
        # Ctrl+E: PDF export
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self._export_shortcut)
        
        # F1: Yard─▒m
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self._show_help)

    def _new_character_shortcut(self):
        """Yeni karakter olu┼ştur (Ctrl+N)"""
        # D&D sayfas─▒na ge├ğ ve yeni karakter ba┼şlat
        if hasattr(self, 'centralWidget'):
            tab_widget = self.centralWidget()
            if isinstance(tab_widget, QTabWidget):
                tab_widget.setCurrentIndex(0)  # D&D sekmesi

    def _load_character_shortcut(self):
        """Karakter y├╝kle (Ctrl+O)"""
        # D&D sayfas─▒na ge├ğ ve karakter y├╝kleme dialog'unu a├ğ
        if hasattr(self, 'centralWidget'):
            tab_widget = self.centralWidget()
            if isinstance(tab_widget, QTabWidget):
                tab_widget.setCurrentIndex(0)  # D&D sekmesi

    def _save_character_shortcut(self):
        """Karakter kaydet (Ctrl+S)"""
        # Otomatik kaydetme zaten aktif, bilgi mesaj─▒ g├Âster
        QMessageBox.information(self, "Bilgi", "Karakter otomatik olarak kaydediliyor!")

    def _export_shortcut(self):
        """PDF export (Ctrl+E)"""
        # D&D sayfas─▒na ge├ğ ve export yap
        if hasattr(self, 'centralWidget'):
            tab_widget = self.centralWidget()
            if isinstance(tab_widget, QTabWidget):
                tab_widget.setCurrentIndex(0)  # D&D sekmesi

    def _show_help(self):
        """Yard─▒m g├Âster (F1)"""
        help_text = """
­şÄ« Diyargezer - FRP Karakter Olu┼şturucu

Ôî¿´©Å Klavye K─▒sayollar─▒:
ÔÇó Ctrl+N: Yeni Karakter Olu┼ştur
ÔÇó Ctrl+O: Karakter Y├╝kle
ÔÇó Ctrl+S: Karakter Kaydet
ÔÇó Ctrl+E: PDF Export
ÔÇó F1: Bu Yard─▒m

­şÄ» ├ûzellikler:
ÔÇó D&D 5e karakter olu┼şturma
ÔÇó Otomatik istatistik hesaplama
ÔÇó Envanter y├Ânetimi
ÔÇó B├╝y├╝ sistemi
ÔÇó Dice roller
ÔÇó PDF export

­şôğ Destek: [Destek bilgileri]
        """
        QMessageBox.information(self, "Yard─▒m - Klavye K─▒sayollar─▒", help_text)

    def _create_header(self) -> QWidget:
        """Ana pencere i├ğin logo header olu┼ştur"""
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #34495e; border-bottom: 2px solid #2c3e50;")
        header_widget.setMaximumHeight(140)  # Header maksimum y├╝kseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Logo
        logo_path = Path(__file__).resolve().parents[1] / "Gemini_Generated_Image_c510m9c510m9c510.png"
        if logo_path.exists():
            logo_label = QLabel()
            logo_pixmap = QPixmap(str(logo_path))
            if not logo_pixmap.isNull():
                # Logoyu k├╝├ğ├╝lt (maksimum 100x100, aspect ratio korunarak)
                scaled_pixmap = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setScaledContents(True)  # K├╝├ğ├╝lt├╝lm├╝┼ş boyutta g├Âster
            logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            logo_label.setFixedSize(100, 100)  # Sabit boyut
            header_layout.addWidget(logo_label)
        
        # Ba┼şl─▒k
        title_label = QLabel("Diyargezer - FRP Karakter Olu┼şturucu")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-left: 20px;")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setWordWrap(True)  # Uzun metinler i├ğin kelime kayd─▒rma
        header_layout.addWidget(title_label)
        
        header_layout.addStretch()
        
        return header_widget
    
    def _set_window_icon(self):
        """Pencere ikonunu ayarla"""
        logo_path = Path(__file__).resolve().parents[1] / "Gemini_Generated_Image_c510m9c510m9c510.png"
        if logo_path.exists():
            icon = QIcon(str(logo_path))
            self.setWindowIcon(icon)


def run():
    import qdarkstyle
    app = QApplication([])
    try:
        app.setStyleSheet(qdarkstyle.load_stylesheet(qt_api='pyside6'))
    except Exception:
        pass
    w = MainWindow()
    w.show()
    app.exec()


if __name__ == "__main__":
    run()

