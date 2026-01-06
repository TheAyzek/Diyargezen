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

# PyInstaller için çalıştırma dizini: frozen ise _MEIPASS, değilse repo kökü
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
    """Karakter resimleri klasörünü oluştur ve döndür"""
    images_dir = APP_BASE_DIR / "characters" / "images"
    images_dir.mkdir(parents=True, exist_ok=True)
    return images_dir


def _load_image_to_base64(image_path: Path) -> Optional[str]:
    """
    Resim dosyasını base64 string'e çevir
    
    Args:
        image_path: Resim dosyası yolu
    
    Returns:
        Base64 encoded string veya None
    """
    try:
        if not image_path.exists():
            return None
        
        with open(image_path, 'rb') as f:
            image_data = f.read()
            base64_str = base64.b64encode(image_data).decode('utf-8')
            # MIME type'ı belirle
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
    Karakter verisinden resmi yükle ve QPixmap olarak döndür
    
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
        "JSON Dosyaları (*.json)"
    )
    if not file_path:
        return
    try:
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(character, f, ensure_ascii=False, indent=2)
        QMessageBox.information(parent, "Başarılı", f"Karakter kaydedildi:\n{file_path}")
    except Exception as exc:
        QMessageBox.critical(parent, "Hata", f"Karakter kaydedilemedi:\n{exc}")


class SqliteCharacterDialog(QDialog):
    """SQLite veritabanından karakter seçmek için gelişmiş dialog"""
    
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
        self.system_combo.addItem("Tüm Sistemler", None)
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
        self.search_edit.setPlaceholderText("Karakter adı ile ara...")
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
        
        # Önizleme alanı
        preview_label = QLabel("Önizleme:")
        layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        layout.addWidget(self.preview_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("Yükle")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("İptal")
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
            QMessageBox.critical(self, "Hata", f"Karakterler yüklenemedi:\n{e}")
            return
        
        for rec in self.all_records:
            item_text = f"#{rec.id or '-'} - {rec.name} ({rec.system})"
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, rec)
            self.character_list.addItem(item)
        
        if not self.all_records:
            self.character_list.addItem("Karakter bulunamadı")
    
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
        
        # Önizleme oluştur
        preview_lines = [
            f"ID: {rec.id}",
            f"İsim: {rec.name}",
            f"Sistem: {rec.system}",
            "",
            "Karakter Bilgileri:"
        ]
        
        data = rec.data
        if isinstance(data, dict):
            if data.get("race"):
                preview_lines.append(f"Irk/Klan: {data.get('race', data.get('clan', '-'))}")
            if data.get("class"):
                preview_lines.append(f"Sınıf/Arketip: {data.get('class', data.get('archetype', '-'))}")
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
    """JSON karakter dosyalarını listeleyen ve filtreleyen diyalog"""
    
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
        self.system_combo.addItem("Tümü", None)
        self.system_combo.addItem("D&D 5e", "DND5E")
        self.system_combo.addItem("M&M", "MUTANTS_AND_MASTERMINDS")
        self.system_combo.addItem("VtM", "VTM5E")
        if self.expected_system:
            index = self.system_combo.findData(self.expected_system)
            if index >= 0:
                self.system_combo.setCurrentIndex(index)
        self.system_combo.currentIndexChanged.connect(self._filter_characters)
        filter_layout.addWidget(self.system_combo)
        
        # Irk filtresi (D&D için)
        filter_layout.addWidget(QLabel("Irk:"))
        self.race_combo = QComboBox()
        self.race_combo.addItem("Tümü", None)
        self.race_combo.currentIndexChanged.connect(self._filter_characters)
        filter_layout.addWidget(self.race_combo)
        
        # Sınıf filtresi (D&D için)
        filter_layout.addWidget(QLabel("Sınıf:"))
        self.class_combo = QComboBox()
        self.class_combo.addItem("Tümü", None)
        self.class_combo.currentIndexChanged.connect(self._filter_characters)
        filter_layout.addWidget(self.class_combo)
        
        filter_layout.addStretch()
        layout.addLayout(filter_layout)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Ara:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Karakter adına göre ara...")
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
        
        # Önizleme alanı
        preview_label = QLabel("Önizleme:")
        layout.addWidget(preview_label)
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.preview_text.setMaximumHeight(150)
        layout.addWidget(self.preview_text)
        
        # Butonlar
        button_layout = QHBoxLayout()
        self.load_btn = QPushButton("Yükle")
        self.load_btn.setEnabled(False)
        self.load_btn.clicked.connect(self.accept)
        self.cancel_btn = QPushButton("İptal")
        self.cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(self.load_btn)
        button_layout.addWidget(self.cancel_btn)
        layout.addLayout(button_layout)
    
    def _load_characters(self):
        """Tüm karakter dosyalarını yükle (optimize edilmiş)"""
        self.character_list.clear()
        self.all_characters = []
        
        characters_dir = _ensure_characters_dir()
        if not characters_dir.exists():
            self.character_list.addItem("Karakter klasörü bulunamadı")
            return
        
        # Performans izleme
        start_time = time.time()
        
        # Tüm JSON dosyalarını yükle (batch processing ile)
        json_files = [f for f in characters_dir.glob("*.json") if "images" not in str(f)]
        
        # Büyük listeler için batch processing
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
            
            # GUI'yi güncelle (her batch'te)
            if i + batch_size < len(json_files):
                QApplication.processEvents()
        
        # Irk ve sınıf listelerini güncelle
        self._update_filter_lists()
        
        # Karakterleri filtrele ve göster
        self._filter_characters()
        
        # Performans log (debug için)
        load_time = time.time() - start_time
        if load_time > 0.5:  # 0.5 saniyeden uzun sürerse log
            print(f"CharacterListDialog: {len(self.all_characters)} karakter {load_time:.2f}s'de yüklendi")
    
    def _update_filter_lists(self):
        """Irk ve sınıf filtre listelerini güncelle"""
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
        
        # Irk combo box'ını güncelle
        self.race_combo.clear()
        self.race_combo.addItem("Tümü", None)
        for race in sorted(races):
            self.race_combo.addItem(race, race)
        
        # Sınıf combo box'ını güncelle
        self.class_combo.clear()
        self.class_combo.addItem("Tümü", None)
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
            
            # Beklenen sistem kontrolü
            if self.expected_system and char.get("system") != self.expected_system:
                continue
            
            # Arama filtresi
            if search_text:
                name = char.get("name", "").lower()
                if search_text not in name:
                    continue
            
            # Irk filtresi (sadece D&D için)
            if race_filter and char.get("system") == "DND5E":
                if char.get("race") != race_filter:
                    continue
            
            # Sınıf filtresi (sadece D&D için)
            if class_filter and char.get("system") == "DND5E":
                if char.get("class") != class_filter:
                    continue
            
            filtered.append(char)
        
        # Karakterleri listele (batch processing ile)
        batch_size = 100
        for i in range(0, len(filtered), batch_size):
            batch = filtered[i:i + batch_size]
            for char in batch:
                name = char.get("name", "İsimsiz")
                system = char.get("system", "Bilinmeyen")
                system_display = {
                    "DND5E": "D&D 5e",
                    "MUTANTS_AND_MASTERMINDS": "M&M",
                    "VTM5E": "VtM"
                }.get(system, system)
                
                # D&D için ek bilgiler
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
            
            # GUI'yi güncelle (her batch'te)
            if i + batch_size < len(filtered):
                QApplication.processEvents()
        
        if not filtered:
            self.character_list.addItem("Karakter bulunamadı")
    
    def _on_selection_changed(self):
        """Seçim değiştiğinde önizlemeyi güncelle"""
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
        
        # Önizleme oluştur
        preview_lines = []
        preview_lines.append(f"İsim: {char.get('name', 'İsimsiz')}")
        preview_lines.append(f"Sistem: {char.get('system', 'Bilinmeyen')}")
        
        if char.get("system") == "DND5E":
            preview_lines.append(f"Irk: {char.get('race', '')}")
            preview_lines.append(f"Sınıf: {char.get('class', '')}")
            preview_lines.append(f"Seviye: {char.get('level', 1)}")
        elif char.get("system") == "MUTANTS_AND_MASTERMINDS":
            preview_lines.append(f"Power Level: {char.get('power_level', '')}")
            preview_lines.append(f"Arketip: {char.get('archetype', '')}")
        elif char.get("system") == "VTM5E":
            preview_lines.append(f"Clan: {char.get('clan', '')}")
            preview_lines.append(f"Concept: {char.get('concept', '')}")
        
        self.preview_text.setPlainText("\n".join(preview_lines))
    
    def _on_double_click(self):
        """Çift tıklama ile hızlı yükleme"""
        if self.load_btn.isEnabled():
            self.accept()
    
    def get_selected_character(self) -> tuple[dict | None, str | None]:
        """Seçili karakteri döndür"""
        if self.selected_character_data and self.selected_file_path:
            return self.selected_character_data, self.selected_file_path
        return None, None


class TemplateManagerDialog(QDialog):
    """Şablon yönetimi diyaloğu"""
    
    def __init__(self, parent: QWidget, system_filter: str | None = None):
        from datetime import datetime  # Lazy import
        super().__init__(parent)
        self.system_filter = system_filter
        self.selected_template = None
        self._init_ui()
        self._load_templates()
    
    def _init_ui(self):
        self.setWindowTitle("Karakter Şablonları")
        self.setMinimumSize(700, 600)
        layout = QVBoxLayout(self)
        
        # Butonlar (üstte)
        button_layout = QHBoxLayout()
        
        save_template_btn = QPushButton("💾 Mevcut Karakteri Şablon Olarak Kaydet")
        save_template_btn.setToolTip("Açık olan karakteri şablon olarak kaydet")
        save_template_btn.clicked.connect(self._save_current_as_template)
        button_layout.addWidget(save_template_btn)
        
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.clicked.connect(self._load_templates)
        button_layout.addWidget(refresh_btn)
        
        button_layout.addStretch()
        layout.addLayout(button_layout)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("🔍 Ara:"))
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("Şablon adına göre ara...")
        self.search_edit.textChanged.connect(self._filter_templates)
        search_layout.addWidget(self.search_edit)
        layout.addLayout(search_layout)
        
        # Şablon listesi
        list_label = QLabel("Şablonlar:")
        layout.addWidget(list_label)
        
        self.template_list = QListWidget()
        self.template_list.itemDoubleClicked.connect(self._on_double_click)
        self.template_list.itemSelectionChanged.connect(self._on_selection_changed)
        layout.addWidget(self.template_list)
        
        # Önizleme alanı
        preview_label = QLabel("Önizleme:")
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
        
        delete_btn = QPushButton("🗑️ Sil")
        delete_btn.setEnabled(False)
        delete_btn.clicked.connect(self._delete_template)
        self.delete_btn = delete_btn
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout2.addWidget(delete_btn)
        button_layout2.addStretch()
        button_layout2.addWidget(self.use_btn)
        button_layout2.addWidget(cancel_btn)
        layout.addLayout(button_layout2)
    
    def _load_templates(self):
        """Tüm şablonları yükle"""
        self.template_list.clear()
        self.all_templates = list_templates(APP_BASE_DIR, self.system_filter)
        self._filter_templates()
    
    def _filter_templates(self):
        """Şablonları filtrele ve listele"""
        from datetime import datetime
        
        self.template_list.clear()
        
        search_text = self.search_edit.text().lower()
        
        for template in self.all_templates:
            template_name = template.get("template_name", "").lower()
            if search_text and search_text not in template_name:
                continue
            
            # Şablon bilgilerini göster
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
            
            item_text = f"{template.get('template_name', 'İsimsiz')} - {system_display}"
            if description:
                item_text += f" | {description}"
            
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, template)
            self.template_list.addItem(item)
        
        if not self.template_list.count():
            self.template_list.addItem("Şablon bulunamadı")
    
    def _on_selection_changed(self):
        """Seçim değiştiğinde önizlemeyi güncelle"""
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
        
        # Önizleme oluştur
        preview_lines = []
        preview_lines.append(f"Şablon Adı: {template.get('template_name', 'İsimsiz')}")
        preview_lines.append(f"Sistem: {template.get('system', 'Bilinmeyen')}")
        
        description = template.get("description", "")
        if description:
            preview_lines.append(f"Açıklama: {description}")
        
        created_at = template.get("created_at", "")
        if created_at:
            try:
                from datetime import datetime
                dt = datetime.fromisoformat(created_at)
                date_str = dt.strftime("%Y-%m-%d %H:%M")
                preview_lines.append(f"Oluşturulma: {date_str}")
            except:
                pass
        
        template_data = template.get("template_data", {})
        if template_data:
            preview_lines.append("")
            preview_lines.append("Şablon İçeriği:")
            
            if template.get("system") == "DND5E":
                if template_data.get("race"):
                    preview_lines.append(f"  Irk: {template_data.get('race')}")
                if template_data.get("class"):
                    preview_lines.append(f"  Sınıf: {template_data.get('class')}")
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
        """Çift tıklama ile hızlı kullanma"""
        if self.use_btn.isEnabled():
            self.accept()
    
    def _save_current_as_template(self):
        """Mevcut karakteri şablon olarak kaydet"""
        # Parent'tan mevcut karakteri al
        parent = self.parent()
        if not hasattr(parent, 'current_character') or not parent.current_character:
            QMessageBox.warning(self, "Uyarı", "Önce bir karakter oluşturmanız gerekiyor.")
            return
        
        # Şablon adı ve açıklaması al
        template_name, ok = QInputDialog.getText(
            self,
            "Şablon Olarak Kaydet",
            "Şablon adı:"
        )
        if not ok or not template_name.strip():
            return
        
        description, ok = QInputDialog.getText(
            self,
            "Şablon Açıklaması",
            "Şablon açıklaması (opsiyonel):"
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
            QMessageBox.information(self, "Başarılı", f"Şablon kaydedildi:\n{template_path}")
            self._load_templates()  # Listeyi yenile
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Şablon kaydedilemedi:\n{str(e)}")
    
    def _delete_template(self):
        """Seçili şablonu sil"""
        if not self.selected_template:
            return
        
        template_name = self.selected_template.get("template_name", "Bu şablon")
        reply = QMessageBox.question(
            self,
            "Şablonu Sil",
            f"'{template_name}' şablonunu silmek istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            file_path = self.selected_template.get("_file_path")
            if file_path:
                if delete_template(Path(file_path)):
                    QMessageBox.information(self, "Başarılı", "Şablon silindi.")
                    self._load_templates()  # Listeyi yenile
                else:
                    QMessageBox.warning(self, "Hata", "Şablon silinemedi.")
    
    def get_selected_template(self) -> dict | None:
        """Seçili şablonu döndür"""
        return self.selected_template


class ExportFormatDialog(QDialog):
    """Export format seçimi diyaloğu"""
    
    def __init__(self, parent: QWidget, character: dict):
        super().__init__(parent)
        self.character = character
        self.selected_format = None
        self.selected_path = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("Export Formatı Seç")
        self.setMinimumSize(500, 400)
        layout = QVBoxLayout(self)
        
        # Başlık
        title = QLabel("Karakter Export Formatı Seçin")
        title.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px;")
        layout.addWidget(title)
        
        # Format seçimi
        format_group = QGroupBox("Format")
        format_layout = QVBoxLayout()
        
        self.format_buttons = {}
        formats = [
            ("PDF", "📄 PDF - Yazdırılabilir format"),
            ("HTML", "🌐 HTML - Web görüntüleme"),
            ("JSON", "📋 JSON - Veri aktarımı"),
            ("CSV", "📊 CSV - Tablo formatı"),
        ]
        
        for format_type, label in formats:
            btn = QRadioButton(label)
            btn.setStyleSheet("font-size: 12px; padding: 5px;")
            format_layout.addWidget(btn)
            self.format_buttons[format_type] = btn
        
        # İlk seçeneği varsayılan yap
        if "PDF" in self.format_buttons:
            self.format_buttons["PDF"].setChecked(True)
        
        format_group.setLayout(format_layout)
        layout.addWidget(format_group)
        
        # Dosya yolu
        path_group = QGroupBox("Kayıt Konumu")
        path_layout = QVBoxLayout()
        
        path_layout_widget = QHBoxLayout()
        self.path_edit = QLineEdit()
        self.path_edit.setReadOnly(True)
        browse_btn = QPushButton("📁 Gözat")
        browse_btn.clicked.connect(self._browse_file)
        path_layout_widget.addWidget(self.path_edit)
        path_layout_widget.addWidget(browse_btn)
        path_layout.addLayout(path_layout_widget)
        
        # Format değiştiğinde dosya yolunu güncelle
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
        
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        
        button_layout.addStretch()
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(export_btn)
        layout.addLayout(button_layout)
        
        # İlk path güncellemesi
        self._update_path()
    
    def _update_path(self):
        """Seçili formata göre dosya yolunu güncelle"""
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
        """Dosya kayıt konumu seç"""
        selected_format = None
        for format_type, btn in self.format_buttons.items():
            if btn.isChecked():
                selected_format = format_type
                break
        
        if not selected_format:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir format seçin.")
            return
        
        safe_name = "".join(c for c in self.character.get("name", "karakter") if c.isalnum() or c in (' ', '-', '_')).rstrip() or "karakter"
        default_path = _ensure_characters_dir() / f"{safe_name}.{selected_format.lower()}"
        
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            f"Karakteri {selected_format} olarak kaydet",
            str(default_path),
            f"{selected_format} Dosyaları (*.{selected_format.lower()})"
        )
        
        if file_path:
            self.path_edit.setText(file_path)
    
    def get_selected_format(self) -> tuple[str | None, str | None]:
        """Seçili format ve dosya yolunu döndür"""
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
    """Karakter karşılaştırma diyaloğu"""
    
    def __init__(self, parent: QWidget, system_filter: str | None = None):
        super().__init__(parent)
        self.system_filter = system_filter
        self.char1_data = None
        self.char2_data = None
        self._init_ui()
    
    def _init_ui(self):
        self.setWindowTitle("Karakter Karşılaştırma")
        self.setMinimumSize(1000, 700)
        layout = QVBoxLayout(self)
        
        # Karakter seçimi
        selection_layout = QHBoxLayout()
        
        # Karakter 1
        char1_group = QGroupBox("Karakter 1")
        char1_layout = QVBoxLayout()
        self.char1_label = QLabel("Karakter seçilmedi")
        self.char1_label.setStyleSheet("font-weight: bold; padding: 5px;")
        char1_btn = QPushButton("📋 Karakter Seç")
        char1_btn.clicked.connect(lambda: self._select_character(1))
        char1_layout.addWidget(self.char1_label)
        char1_layout.addWidget(char1_btn)
        char1_group.setLayout(char1_layout)
        
        # Karakter 2
        char2_group = QGroupBox("Karakter 2")
        char2_layout = QVBoxLayout()
        self.char2_label = QLabel("Karakter seçilmedi")
        self.char2_label.setStyleSheet("font-weight: bold; padding: 5px;")
        char2_btn = QPushButton("📋 Karakter Seç")
        char2_btn.clicked.connect(lambda: self._select_character(2))
        char2_layout.addWidget(self.char2_label)
        char2_layout.addWidget(char2_btn)
        char2_group.setLayout(char2_layout)
        
        selection_layout.addWidget(char1_group)
        selection_layout.addWidget(char2_group)
        layout.addLayout(selection_layout)
        
        # Karşılaştır butonu
        compare_btn = QPushButton("🔍 Karşılaştır")
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
        
        # Sonuçlar (tab widget)
        self.results_tabs = QTabWidget()
        layout.addWidget(self.results_tabs)
        
        # Özet sekmesi
        self.summary_tab = QWidget()
        summary_layout = QVBoxLayout(self.summary_tab)
        self.summary_text = QTextEdit()
        self.summary_text.setReadOnly(True)
        summary_layout.addWidget(self.summary_text)
        self.results_tabs.addTab(self.summary_tab, "📊 Özet")
        
        # Farklar sekmesi
        self.differences_tab = QWidget()
        differences_layout = QVBoxLayout(self.differences_tab)
        self.differences_text = QTextEdit()
        self.differences_text.setReadOnly(True)
        differences_layout.addWidget(self.differences_text)
        self.results_tabs.addTab(self.differences_tab, "⚠️ Farklar")
        
        # Benzerlikler sekmesi
        self.similarities_tab = QWidget()
        similarities_layout = QVBoxLayout(self.similarities_tab)
        self.similarities_text = QTextEdit()
        self.similarities_text.setReadOnly(True)
        similarities_layout.addWidget(self.similarities_text)
        self.results_tabs.addTab(self.similarities_tab, "✅ Benzerlikler")
        
        # Butonlar
        button_layout = QHBoxLayout()
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        button_layout.addStretch()
        button_layout.addWidget(close_btn)
        layout.addLayout(button_layout)
        
        # Başlangıçta sonuçları gizle
        self.results_tabs.setVisible(False)
        self.compare_btn.setEnabled(False)
    
    def _select_character(self, char_num: int):
        """Karakter seç"""
        dialog = CharacterListDialog(self, self.system_filter)
        dialog.setWindowTitle(f"Karakter {char_num} Seç")
        
        if dialog.exec() == QDialog.Accepted:
            data, path = dialog.get_selected_character()
            if data:
                if char_num == 1:
                    self.char1_data = data
                    self.char1_label.setText(f"✅ {data.get('name', 'İsimsiz')} ({data.get('system', 'Unknown')})")
                else:
                    self.char2_data = data
                    self.char2_label.setText(f"✅ {data.get('name', 'İsimsiz')} ({data.get('system', 'Unknown')})")
                
                # Her iki karakter seçildiyse karşılaştır butonunu etkinleştir
                if self.char1_data and self.char2_data:
                    self.compare_btn.setEnabled(True)
    
    def _compare_characters(self):
        """Karakterleri karşılaştır"""
        if not self.char1_data or not self.char2_data:
            QMessageBox.warning(self, "Uyarı", "Lütfen her iki karakteri de seçin.")
            return
        
        try:
            result = compare_characters(self.char1_data, self.char2_data)
            
            if "error" in result:
                QMessageBox.warning(self, "Hata", result["error"])
                return
            
            # Sonuçları göster
            self._display_results(result)
            self.results_tabs.setVisible(True)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karşılaştırma sırasında hata oluştu:\n{str(e)}")
    
    def _display_results(self, result: dict):
        """Karşılaştırma sonuçlarını göster"""
        system = result.get("system", "Unknown")
        char1_name = result.get("char1_name", "Unknown")
        char2_name = result.get("char2_name", "Unknown")
        differences = result.get("differences", [])
        similarities = result.get("similarities", [])
        summary = result.get("summary", {})
        
        # Özet
        summary_lines = []
        summary_lines.append(f"📊 Karakter Karşılaştırma Özeti")
        summary_lines.append(f"{'=' * 50}")
        summary_lines.append(f"")
        summary_lines.append(f"Karakter 1: {char1_name}")
        summary_lines.append(f"Karakter 2: {char2_name}")
        summary_lines.append(f"Sistem: {system}")
        summary_lines.append(f"")
        summary_lines.append(f"📈 İstatistikler:")
        summary_lines.append(f"  • Toplam Fark: {summary.get('total_differences', 0)}")
        summary_lines.append(f"  • Toplam Benzerlik: {summary.get('total_similarities', 0)}")
        
        if "level_difference" in summary:
            level_diff = summary["level_difference"]
            if level_diff > 0:
                summary_lines.append(f"  • Seviye Farkı: {char1_name} {level_diff} seviye daha yüksek")
            elif level_diff < 0:
                summary_lines.append(f"  • Seviye Farkı: {char2_name} {abs(level_diff)} seviye daha yüksek")
            else:
                summary_lines.append(f"  • Seviye: Aynı")
        
        self.summary_text.setPlainText("\n".join(summary_lines))
        
        # Farklar
        if differences:
            diff_lines = []
            diff_lines.append(f"⚠️ Karakterler Arasındaki Farklar")
            diff_lines.append(f"{'=' * 50}")
            diff_lines.append("")
            
            for diff in differences:
                field = diff.get("field", "Unknown")
                diff_type = diff.get("type", "unknown")
                
                if diff_type == "basic":
                    diff_lines.append(f"📝 {field.replace('_', ' ').title()}:")
                    diff_lines.append(f"   {char1_name}: {diff.get('char1', 'N/A')}")
                    diff_lines.append(f"   {char2_name}: {diff.get('char2', 'N/A')}")
                    diff_lines.append("")
                
                elif diff_type in ["ability", "attribute", "defense", "skill", "power_points", "humanity", "health", "willpower"]:
                    diff_val = diff.get("difference", 0)
                    if diff_val > 0:
                        diff_lines.append(f"📈 {field.replace('_', ' ').title()}: {char1_name} +{diff_val} daha yüksek")
                    else:
                        diff_lines.append(f"📉 {field.replace('_', ' ').title()}: {char2_name} +{abs(diff_val)} daha yüksek")
                    diff_lines.append(f"   {char1_name}: {diff.get('char1', 0)}")
                    diff_lines.append(f"   {char2_name}: {diff.get('char2', 0)}")
                    diff_lines.append("")
                
                elif diff_type in ["skills", "spells", "feats", "powers", "disciplines"]:
                    diff_lines.append(f"📋 {field.replace('_', ' ').title()}:")
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
            self.differences_text.setPlainText("🎉 Hiç fark yok! Karakterler tamamen aynı.")
        
        # Benzerlikler
        if similarities:
            sim_lines = []
            sim_lines.append(f"✅ Ortak Özellikler")
            sim_lines.append(f"{'=' * 50}")
            sim_lines.append("")
            
            for sim in similarities:
                field = sim.get("field", "Unknown")
                value = sim.get("value", "N/A")
                sim_type = sim.get("type", "unknown")
                
                if sim_type == "basic":
                    sim_lines.append(f"📝 {field.replace('_', ' ').title()}: {value}")
                elif sim_type in ["ability", "attribute"]:
                    sim_lines.append(f"📊 {field.replace('_', ' ').title()}: {value}")
            
            self.similarities_text.setPlainText("\n".join(sim_lines))
        else:
            self.similarities_text.setPlainText("ℹ️ Ortak özellik bulunamadı.")


def _load_character_via_dialog(parent: QWidget, dialog_title: str, expected_system: str) -> tuple[dict | None, str | None]:
    """Karakter yükleme diyaloğu - eski yöntem (dosya seçimi)"""
    # Yeni karakter listesi diyaloğunu kullan
    dialog = CharacterListDialog(parent, expected_system)
    dialog.setWindowTitle(dialog_title)
    
    if dialog.exec() == QDialog.Accepted:
        return dialog.get_selected_character()
    
    return None, None

def _select_template_character(parent: QWidget, system_name: str) -> tuple[dict | None, str | None]:
    """Şablon seçimi sonrası karakter verisini döndür"""
    dialog = TemplateManagerDialog(parent, system_name)
    if dialog.exec() != QDialog.Accepted:
        return None, None

    template = dialog.get_selected_template()
    if not template:
        QMessageBox.warning(parent, "Uyarı", "Bir şablon seçmediniz.")
        return None, None

    default_name = template.get("template_name", "Yeni Karakter")
    character_name, ok = QInputDialog.getText(
        parent,
        "Şablonu Kullan",
        "Yeni karakter adı:",
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
    """Kural düzenleme diyaloğu"""
    
    def __init__(self, parent: QWidget, system_name: str, base_dir: Path):
        super().__init__(parent)
        self.system_name = system_name
        self.base_dir = base_dir
        self.rules = None
        self._init_ui()
        self._load_rules()
    
    def _init_ui(self):
        self.setWindowTitle(f"Kural Düzenle - {self.system_name}")
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        
        # Bilgi etiketi
        info_label = QLabel(
            "Kuralları JSON formatında düzenleyebilirsiniz. "
            "Değişiklikleri kaydetmek için 'Kaydet' butonuna tıklayın."
        )
        info_label.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 10px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # JSON editörü
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
        
        # Yeniden yükle butonu
        reload_btn = QPushButton("🔄 Yeniden Yükle")
        reload_btn.setToolTip("Orijinal kuralları yükle (değişiklikler kaybolur)")
        reload_btn.clicked.connect(self._load_rules)
        button_layout.addWidget(reload_btn)
        
        # JSON doğrula butonu
        validate_json_btn = QPushButton("✓ JSON Doğrula")
        validate_json_btn.setToolTip("JSON formatını kontrol et")
        validate_json_btn.clicked.connect(self._validate_json)
        button_layout.addWidget(validate_json_btn)
        
        # Kural doğrulama butonu
        validate_rules_btn = QPushButton("🔍 Kuralları Doğrula")
        validate_rules_btn.setToolTip("Kural yapısını, eksiklikleri ve çelişkileri kontrol et")
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
        
        # İptal butonu
        cancel_btn = QPushButton("İptal")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        # Kaydet butonu
        save_btn = QPushButton("💾 Kaydet")
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
        """Mevcut kuralları yükle"""
        rules = load_rules(self.base_dir, self.system_name)
        if rules:
            self.rules = rules
            rules_text = json.dumps(rules, ensure_ascii=False, indent=2)
            self.json_editor.setPlainText(rules_text)
        else:
            # Varsayılan boş kural yapısı
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
                "Henüz kural yüklenmemiş. Yeni kural oluşturabilirsiniz."
            )
    
    def _validate_json(self):
        """JSON formatını doğrula"""
        text = self.json_editor.toPlainText()
        try:
            json.loads(text)
            QMessageBox.information(
                self,
                "Başarılı",
                "JSON formatı geçerli!"
            )
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "JSON Hatası",
                f"JSON formatı geçersiz:\n\n{str(e)}\n\n"
                "Lütfen JSON sözdizimini düzeltin."
            )
    
    def _validate_rules(self):
        """Kuralları doğrula"""
        text = self.json_editor.toPlainText()
        
        # Önce JSON formatını kontrol et
        try:
            rules = json.loads(text)
        except json.JSONDecodeError as e:
            QMessageBox.warning(
                self,
                "JSON Hatası",
                f"JSON formatı geçersiz:\n\n{str(e)}\n\n"
                "Lütfen önce JSON formatını düzeltin."
            )
            return
        
        # Kural doğrulama
        is_valid, issues = validate_rules(rules)
        report = format_validation_report(issues)
        
        # Sonuçları göster
        dialog = QDialog(self)
        dialog.setWindowTitle("Kural Doğrulama Raporu")
        dialog.setMinimumSize(600, 400)
        layout = QVBoxLayout(dialog)
        
        # Başlık
        if is_valid:
            title_label = QLabel("✅ Kurallar Geçerli")
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #27ae60; padding: 10px;")
        else:
            title_label = QLabel("❌ Kurallarda Hatalar Bulundu")
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
        """Düzenlenen kuralları kaydet"""
        text = self.json_editor.toPlainText()
        
        # JSON doğrulama
        try:
            rules = json.loads(text)
        except json.JSONDecodeError as e:
            QMessageBox.critical(
                self,
                "JSON Hatası",
                f"JSON formatı geçersiz:\n\n{str(e)}\n\n"
                "Lütfen JSON sözdizimini düzeltin ve tekrar deneyin."
            )
            return
        
        # Sistem kontrolü
        if rules.get("system") != self.system_name:
            reply = QMessageBox.question(
                self,
                "Sistem Uyarısı",
                f"Kural sistem adı '{rules.get('system')}' mevcut sistem '{self.system_name}' ile eşleşmiyor.\n\n"
                "Yine de kaydetmek istiyor musunuz?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Kuralları doğrula
        is_valid, issues = validate_rules(rules)
        if issues:
            report = format_validation_report(issues)
            if not is_valid:
                # Kritik hatalar varsa kullanıcıya sor
                reply = QMessageBox.question(
                    self,
                    "Kural Doğrulama Hatası",
                    f"Kurallarda kritik hatalar bulundu:\n\n{report[:300]}...\n\n"
                    "Yine de kaydetmek istiyor musunuz? (Önerilmez)",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
            else:
                # Sadece uyarılar varsa bilgi ver
                QMessageBox.information(
                    self,
                    "Kural Doğrulama Uyarıları",
                    f"Kurallarda bazı uyarılar bulundu:\n\n{report[:300]}...\n\n"
                    "Kurallar kaydedilecek."
                )
        
        # Kuralları kaydet
        try:
            saved_path = save_rules(rules, self.base_dir, self.system_name)
            QMessageBox.information(
                self,
                "Başarılı",
                f"Kurallar kaydedildi:\n{saved_path}\n\n"
                "Değişikliklerin etkili olması için uygulamayı yeniden başlatmanız gerekebilir."
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
    """Kural önizleme diyaloğu"""
    
    def __init__(self, parent: QWidget, system_name: str, base_dir: Path):
        super().__init__(parent)
        self.system_name = system_name
        self.base_dir = base_dir
        self._init_ui()
        self._load_preview()
    
    def _init_ui(self):
        self.setWindowTitle(f"Kural Önizleme - {self.system_name}")
        self.setMinimumSize(700, 500)
        layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel("📚 Kural Önizleme")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # Önizleme metni
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
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.setToolTip("Kuralları yeniden yükle")
        refresh_btn.clicked.connect(self._load_preview)
        button_layout.addWidget(refresh_btn)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.clicked.connect(self.accept)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
    
    def _load_preview(self):
        """Kuralları yükle ve önizle"""
        from utils.rule_storage import load_rules
        
        rules = load_rules(self.base_dir, self.system_name)
        preview_text = format_rule_preview(rules) if rules else "❌ Kural yüklenmemiş."
        self.preview_text.setPlainText(preview_text)


class RuleVersionDialog(QDialog):
    """Kural versiyon yönetimi diyaloğu"""
    
    def __init__(self, parent: QWidget, system_name: str, base_dir: Path):
        super().__init__(parent)
        self.system_name = system_name
        self.base_dir = base_dir
        self._init_ui()
        self._load_versions()
    
    def _init_ui(self):
        self.setWindowTitle(f"Kural Versiyon Yönetimi - {self.system_name}")
        self.setMinimumSize(800, 600)
        layout = QVBoxLayout(self)
        
        # Başlık
        title_label = QLabel("📦 Kural Versiyon Yönetimi")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; color: #2c3e50; padding: 10px;")
        layout.addWidget(title_label)
        
        # Bilgi etiketi
        info_label = QLabel(
            "Kurallarınızın versiyon geçmişi. Bir versiyonu geri yükleyebilir veya silebilirsiniz."
        )
        info_label.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 5px;")
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        # Versiyon listesi
        list_label = QLabel("Versiyonlar (en yeni önce):")
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
        refresh_btn = QPushButton("🔄 Yenile")
        refresh_btn.clicked.connect(self._load_versions)
        button_layout.addWidget(refresh_btn)
        
        # Detaylar butonu
        details_btn = QPushButton("📋 Detaylar")
        details_btn.clicked.connect(self._show_selected_version_details)
        button_layout.addWidget(details_btn)
        
        button_layout.addStretch()
        
        # Geri yükle butonu
        restore_btn = QPushButton("↩️ Geri Yükle")
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
        delete_btn = QPushButton("🗑️ Sil")
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
        """Versiyon listesini yükle"""
        self.version_list.clear()
        versions = load_versions_list(self.base_dir, self.system_name)
        
        if not versions:
            item = QListWidgetItem("Versiyon bulunamadı")
            item.setFlags(Qt.NoItemFlags)
            self.version_list.addItem(item)
            return
        
        for version_meta in versions:
            version_info = format_version_info(version_meta)
            item = QListWidgetItem(version_info)
            item.setData(Qt.UserRole, version_meta["version_id"])
            self.version_list.addItem(item)
    
    def _get_selected_version_id(self) -> Optional[str]:
        """Seçili versiyon ID'sini döndür"""
        current_item = self.version_list.currentItem()
        if current_item:
            return current_item.data(Qt.UserRole)
        return None
    
    def _show_version_details(self, item: QListWidgetItem):
        """Versiyon detaylarını göster"""
        version_id = item.data(Qt.UserRole)
        if not version_id:
            return
        self._show_version_details_by_id(version_id)
    
    def _show_selected_version_details(self):
        """Seçili versiyonun detaylarını göster"""
        version_id = self._get_selected_version_id()
        if not version_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir versiyon seçin.")
            return
        self._show_version_details_by_id(version_id)
    
    def _show_version_details_by_id(self, version_id: str):
        """Belirli bir versiyonun detaylarını göster"""
        version = load_version(self.base_dir, self.system_name, version_id)
        if not version:
            QMessageBox.warning(self, "Hata", "Versiyon yüklenemedi.")
            return
        
        # Detay diyaloğu
        dialog = QDialog(self)
        dialog.setWindowTitle(f"Versiyon Detayları - {version_id}")
        dialog.setMinimumSize(600, 500)
        layout = QVBoxLayout(dialog)
        
        # Versiyon bilgisi
        info_text = f"Versiyon ID: {version.version_id}\n"
        info_text += f"Tarih: {version.timestamp}\n"
        info_text += f"Açıklama: {version.description or '(Açıklama yok)'}\n"
        info_label = QLabel(info_text)
        info_label.setStyleSheet("font-weight: bold; padding: 10px;")
        layout.addWidget(info_label)
        
        # Kural önizleme
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
        """Seçili versiyonu geri yükle"""
        version_id = self._get_selected_version_id()
        if not version_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir versiyon seçin.")
            return
        
        reply = QMessageBox.question(
            self,
            "Versiyon Geri Yükle",
            "Bu versiyonu geri yüklemek istediğinizden emin misiniz?\n\n"
            "Mevcut kurallar otomatik olarak yedeklenecektir.",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if restore_version(self.base_dir, self.system_name, version_id):
                    QMessageBox.information(
                        self,
                        "Başarılı",
                        "Versiyon geri yüklendi!\n\n"
                        "Değişikliklerin etkili olması için uygulamayı yeniden başlatmanız gerekebilir."
                    )
                    self._load_versions()
                else:
                    QMessageBox.warning(self, "Hata", "Versiyon geri yüklenemedi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Versiyon geri yükleme hatası:\n{str(e)}")
    
    def _delete_selected_version(self):
        """Seçili versiyonu sil"""
        version_id = self._get_selected_version_id()
        if not version_id:
            QMessageBox.warning(self, "Uyarı", "Lütfen bir versiyon seçin.")
            return
        
        reply = QMessageBox.question(
            self,
            "Versiyon Sil",
            "Bu versiyonu silmek istediğinizden emin misiniz?\n\n"
            "Bu işlem geri alınamaz!",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                if delete_version(self.base_dir, self.system_name, version_id):
                    QMessageBox.information(self, "Başarılı", "Versiyon silindi.")
                    self._load_versions()
                else:
                    QMessageBox.warning(self, "Hata", "Versiyon silinemedi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Versiyon silme hatası:\n{str(e)}")


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

        form.addRow("İsim:", self.name_edit)
        form.addRow("Sınıf:", self.class_combo)
        layout.addLayout(form)

        buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        buttons.accepted.connect(self._on_accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)

    def _on_accept(self):
        if not self.name_edit.text().strip():
            QMessageBox.warning(self, "Uyarı", "Lütfen karakter ismi girin.")
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
        self.current_step = 0  # Mevcut adım indeksi
        self._current_race_bonus: dict[str, int] = {}  # Son uygulanan ırk bonusları
        self.steps = [
            {"name": "İsim ve Sınıf", "description": "Karakterinizin ismini ve sınıfını seçin"},
            {"name": "Irk", "description": "Karakterinizin ırkını seçin"},
            {"name": "Arka Plan", "description": "Karakterinizin arka planını seçin"},
            {"name": "Yetenek Puanları", "description": "Point-buy sistemi ile yetenek puanlarınızı dağıtın"},
            {"name": "Sınıf Becerileri", "description": "Sınıfınıza özel becerileri seçin"},
            {"name": "Büyüler", "description": "Büyücü sınıflar için büyü seçimi"},
            {"name": "Feat'ler", "description": "İsteğe bağlı feat'leri seçin"},
            {"name": "Ekipman", "description": "Başlangıç ekipmanınızı seçin"},
            {"name": "Kişilik", "description": "Karakterinizin kişilik ve fiziksel özelliklerini belirleyin"},
            {"name": "Özet", "description": "Karakterinizin özetini görüntüleyin ve tamamlayın"}
        ]
        self._init_ui()

    def _load_dnd_data(self) -> dict:
        """D&D verisini yükle - cache ile optimize edilmiş"""
        if not hasattr(self.__class__, '_data_cache'):
            base_dir = Path(__file__).resolve().parents[1]
            data_file = base_dir / "data" / "dnd_data.json"
            with open(data_file, 'r', encoding='utf-8') as f:
                self.__class__._data_cache = json.load(f)
        return self.__class__._data_cache

    def _load_logo(self) -> QPixmap:
        """Logoyu yükle - küçültülmüş boyutta"""
        logo_path = Path(__file__).resolve().parents[1] / "Gemini_Generated_Image_c510m9c510m9c510.png"
        if logo_path.exists():
            pixmap = QPixmap(str(logo_path))
            # Logoyu küçült (maksimum 150x150, aspect ratio korunarak)
            if not pixmap.isNull():
                scaled = pixmap.scaled(150, 150, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                return scaled
        return QPixmap()  # Boş pixmap döndür

    def _init_ui(self):
        # Ana layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(2)  # Spacing'i azalt
        
        # Header kısmı - Logo ve başlık
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #34495e; border-radius: 10px; margin: 5px;")
        header_widget.setMaximumHeight(140)  # Header maksimum yükseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Sol taraf için boş alan
        header_layout.addStretch()
        
        # Başlık (logo kaldırıldı)
        title_label = QLabel("Diyargezer - D&D 5e Karakter Oluşturucu")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin: 5px;")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setWordWrap(True)  # Uzun metinler için kelime kaydırma
        header_layout.addWidget(title_label)
        
        # Sağ taraf için boş alan
        header_layout.addStretch()
        
        layout.addWidget(header_widget)
        
        # Toolbar ekle
        toolbar_widget = self._build_toolbar()
        toolbar_widget.setMaximumHeight(40)  # Toolbar yüksekliğini sınırla
        layout.addWidget(toolbar_widget)
        
        # Tab widget oluştur
        self.tab_widget = QtWidgets.QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        layout.addWidget(self.tab_widget, 1)  # Stretch factor = 1 (kalan alanı kapla)
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
        layout.addWidget(self.tab_widget, 1)  # Stretch factor = 1 (kalan alanı kapla)
        
        # Karakter Oluşturma sekmesi
        self.character_tab = QWidget()
        self.character_layout = QVBoxLayout(self.character_tab)
        self.character_layout.setContentsMargins(0, 0, 0, 0)  # Margin'leri kaldır
        self.character_layout.setSpacing(0)  # Spacing'i kaldır
        self.tab_widget.addTab(self.character_tab, "🎭 Karakter")
        
        # Büyü yönetimi sekmesi
        self.spells_tab = QWidget()
        self.spells_layout = QVBoxLayout(self.spells_tab)
        self.spells_tab_index = self.tab_widget.addTab(self.spells_tab, "🔮 Büyüler")
        
        # Seviye atlama sekmesi
        self.levelup_tab = QWidget()
        self.levelup_layout = QVBoxLayout(self.levelup_tab)
        self.levelup_tab_index = self.tab_widget.addTab(self.levelup_tab, "📈 Level Up")
        
        # Envanter sekmesi
        self.inventory_tab = QWidget()
        self.inventory_layout = QVBoxLayout(self.inventory_tab)
        self.inventory_tab_index = self.tab_widget.addTab(self.inventory_tab, "🎒 Envanter")
        
        # Dice Roller sekmesi
        self.dice_tab = QWidget()
        self.dice_layout = QVBoxLayout(self.dice_tab)
        self._init_dice_ui()
        self.dice_tab_index = self.tab_widget.addTab(self.dice_tab, "🎲 Dice")
        
        # Gelişmiş sekmesi (opsiyonel özellikler)
        self.advanced_tab = QWidget()
        self.advanced_layout = QVBoxLayout(self.advanced_tab)
        self._init_advanced_ui()
        self.advanced_tab_index = self.tab_widget.addTab(self.advanced_tab, "⚙️ Gelişmiş")
        
        # Başlangıçta sadece Karakter sekmesi görünür olsun
        self.tab_widget.setTabVisible(self.spells_tab_index, False)
        self.tab_widget.setTabVisible(self.levelup_tab_index, False)
        self.tab_widget.setTabVisible(self.inventory_tab_index, False)
        self.tab_widget.setTabVisible(self.dice_tab_index, False)
        self.tab_widget.setTabVisible(self.advanced_tab_index, False)
        
        # Karakter oluşturma UI'sını oluştur
        self._init_character_ui()
        
        # Büyü yönetimi UI'sını oluştur
        self._init_spells_ui()
        
        # Seviye atlama UI'sını oluştur
        self._init_levelup_ui()
        
        # Envanter UI'sını oluştur
        self._init_inventory_ui()

        # Başlangıçta büyü sekmesi durumunu güncelle
        self._update_spell_tab_visibility()

    def _build_toolbar(self) -> QWidget:
        """Toolbar oluştur"""
        widget = QWidget()
        bar = QHBoxLayout(widget)
        bar.setContentsMargins(0, 0, 0, 0)

        new_btn = QPushButton("Yeni Karakter")
        new_btn.setIcon(QIcon.fromTheme("document-new"))
        new_btn.clicked.connect(self._start_new_character)

        load_btn = QPushButton("Karakter Yükle")
        load_btn.setIcon(QIcon.fromTheme("document-open"))
        load_btn.clicked.connect(self._load_existing_character)
        
        browse_btn = QPushButton("📋 Karakterleri Listele")
        browse_btn.setToolTip("Tüm karakterleri görüntüle, ara ve filtrele")
        browse_btn.clicked.connect(self._browse_characters)
        
        template_btn = QPushButton("📝 Şablonlar")
        template_btn.setToolTip("Karakter şablonlarını yönet")
        template_btn.clicked.connect(self._manage_templates)
        
        version_btn = QPushButton("📜 Versiyonlar")
        version_btn.setToolTip("Karakter versiyon geçmişini görüntüle ve yönet")
        version_btn.clicked.connect(self._manage_versions)

        save_btn = QPushButton("Kaydet")
        save_btn.setIcon(QIcon.fromTheme("document-save"))
        save_btn.clicked.connect(self._manual_save_character)

        pdf_btn = QPushButton("PDF Export")
        pdf_btn.clicked.connect(self._export_to_pdf_from_toolbar)
        pdf_btn.setToolTip("Karakteri PDF olarak dışa aktar")

        compare_btn = QPushButton("⚖️ Karşılaştır")
        compare_btn.setToolTip("İki karakteri karşılaştır")
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
        """Karakter karşılaştırma diyaloğunu aç"""
        dialog = CharacterComparisonDialog(self, self.SYSTEM_NAME)
        dialog.exec()

    def _start_new_character(self):
        """Yeni karakter yaratmaya başla - ilk önce isim sor"""
        classes = sorted(self.data.get("classes", {}).keys())
        if not classes:
            QMessageBox.warning(self, "Uyarı", "Herhangi bir sınıf verisi bulunamadı.")
            return
        
        dialog = CharacterIntroDialog(self, classes)
        if dialog.exec() != QDialog.Accepted:
            return
        
        character_name, class_name = dialog.get_values()
        if not character_name:
            return
        
        # Karakter verisi oluştur
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
        
        # Karakter formunu güncelle
        self._load_character_to_gui(self.current_character)
        
        # Adım widget'larını güncelle (karakter bilgilerini yükle)
        if hasattr(self, '_populate_step_widgets'):
            self._populate_step_widgets()
        
        # Karakter sayfalarına geç
        self.tab_widget.setCurrentIndex(0)
        
        self.current_character_file = str(_ensure_characters_dir() / f"{character_name}_karakter.json")
        self._save_character_to_file()

        # Büyü sekmesi görünürlüğünü güncelle
        self._update_spell_tab_visibility()
        
        # Tüm sekmeleri görünür yap (karakter oluşturulduğu için)
        self._show_all_tabs()

        # Level up sekmesinde bu karakteri otomatik seç
        self._focus_current_character_in_levelup()
        
        # İlk adıma git (İsim ve Sınıf adımı zaten tamamlandı, Irk adımına geç)
        if hasattr(self, 'step_stack'):
            self._go_to_step(1)  # Irk adımına geç
        
        QMessageBox.information(self, "Başarılı", f"'{character_name}' karakteri oluşturuldu!\nArtık karakterinizi özelleştirebilirsiniz.")

    def _focus_current_character_in_levelup(self):
        """Level Up sekmesinde mevcut karakteri otomatik seç"""
        try:
            if not hasattr(self, 'levelup_character_combo'):
                return
            if not getattr(self, "current_character_file", None):
                return

            # Listeyi yenile (diskteki son durumu al)
            self._refresh_levelup_character_list()

            # Combo içinde current_character_file'a karşılık gelen girdiyi bul
            target_path = str(self.current_character_file)
            for i in range(self.levelup_character_combo.count()):
                data = self.levelup_character_combo.itemData(i)
                if data and str(data) == target_path:
                    self.levelup_character_combo.setCurrentIndex(i)
                    break
        except Exception as e:
            print(f"Level up karakter odağı ayarlanırken hata: {e}")

    def _save_character_to_file(self, change_note: str = ""):
        """Mevcut karakteri dosyaya kaydet ve versiyon oluştur"""
        if not hasattr(self, 'current_character') or not self.current_character:
            return
        
        if not getattr(self, "current_character_file", None):
            return

        try:
            path = Path(self.current_character_file)
            path.parent.mkdir(parents=True, exist_ok=True)
            
            # Mevcut dosyayı kaydet (varsa)
            old_character = None
            if path.exists():
                try:
                    with path.open("r", encoding="utf-8") as f:
                        old_character = json.load(f)
                except Exception:
                    pass
            
            # Yeni versiyonu kaydet (değişiklik varsa)
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
        """Her değişiklikte otomatik kaydet"""
        if hasattr(self, 'current_character') and self.current_character:
            self.current_character["system"] = self.SYSTEM_NAME
            # Mevcut seçimleri karakter verisine güncelle
            self.current_character["race"] = self.race_cb.currentText()
            self.current_character["class"] = self.class_cb.currentText()
            self.current_character["background"] = self.bg_cb.currentText()
            
            # Yetenek puanlarını güncelle
            for ability, spin in self.ability_spins.items():
                self.current_character["abilities"][ability] = spin.value()
            
            # Resmi güncelle (varsa)
            if hasattr(self, 'current_character_image_data'):
                if self.current_character_image_data:
                    self.current_character["image"] = self.current_character_image_data
                elif "image" in self.current_character:
                    del self.current_character["image"]
            
            # Dosyaya kaydet
            self._save_character_to_file()
            
            # Adım listesini güncelle
            if hasattr(self, '_update_step_list'):
                self._update_step_list()

    def _manual_save_character(self):
        """Karakteri seçilen bir dosyaya kaydet"""
        if not hasattr(self, "current_character") or not self.current_character:
            QMessageBox.warning(self, "Uyarı", "Önce bir karakter oluşturmanız gerekiyor.")
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
        """Hazır karakter dosyasını yükle"""
        data, path = _load_character_via_dialog(self, "D&D Karakteri Yükle", self.SYSTEM_NAME)
        if not data:
            return
        self._load_character_to_gui(data)
        self.current_character = data
        self.current_character_file = path
        
        # Son açılanlara ekle
        if path:
            add_recent_character(APP_BASE_DIR, path, data.get("name", ""))
        
        # Tüm sekmeleri görünür yap
        self._show_all_tabs()

        # Level up sekmesinde bu karakteri otomatik seç
        self._focus_current_character_in_levelup()
        
        QMessageBox.information(self, "Başarılı", f"{data.get('name', 'Karakter')} yüklendi!")

    def _browse_characters(self):
        """Karakter listesi diyaloğunu aç ve D&D karakteri seç"""
        dialog = CharacterListDialog(self, None)
        dialog.setWindowTitle("Karakter Listesi - Tüm Sistemler")
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
            # Tüm sekmeleri görünür yap
            self._show_all_tabs()

            # Level up sekmesinde bu karakteri otomatik seç
            self._focus_current_character_in_levelup()

            QMessageBox.information(self, "Başarılı", f"{data.get('name', 'Karakter')} yüklendi!")
        else:
            QMessageBox.information(
                self,
                "Bilgi",
                f"Bu karakter {system} sistemine ait.\nLütfen ilgili sekmeden yükleyin."
            )

    def _manage_templates(self):
        """Şablon yönetim diyaloğunu aç"""
        character, character_name = _select_template_character(self, self.SYSTEM_NAME)
        if not character:
            return

        self._load_character_to_gui(character)
        safe_name = "".join(c for c in character_name if c.isalnum() or c in (" ", "-", "_")).strip()
        if not safe_name:
            safe_name = "dnd_karakter"
        safe_name = safe_name.replace(" ", "_")
        self.current_character_file = str(_ensure_characters_dir() / f"{safe_name}_karakter.json")
        self._save_character_to_file("Şablondan oluşturuldu")

        # Sekmeleri göster ve level up sekmesinde bu karakteri seç
        self._show_all_tabs()
        self._focus_current_character_in_levelup()

        QMessageBox.information(self, "Başarılı", f"{character_name} şablondan oluşturuldu.")

    def _export_to_pdf_from_toolbar(self):
        """Toolbar'dan PDF export"""
        if not hasattr(self, "current_character") or not self.current_character:
            QMessageBox.warning(self, "Uyarı", "Önce bir karakter oluşturmanız gerekiyor.")
            return
        self._export_to_pdf(self.current_character)

    def _load_character_to_gui(self, character):
        """Karakteri GUI'ye yükle"""
        try:
            # Mevcut karakteri güncelle
            self.current_character = character
            
            # İsim alanını güncelle
            if hasattr(self, 'character_name_edit') and self.character_name_edit:
                self.character_name_edit.setText(character.get("name", ""))
                self.character_name_edit.setReadOnly(True)
            
            # Race seçimi
            race = character.get("race", "")
            if race and hasattr(self, 'race_cb') and self.race_cb:
                index = self.race_cb.findText(race)
                if index >= 0:
                    self.race_cb.setCurrentIndex(index)
            
            # Class seçimi
            char_class = character.get("class", "")
            if char_class and hasattr(self, 'class_cb') and self.class_cb:
                index = self.class_cb.findText(char_class)
                if index >= 0:
                    self.class_cb.setCurrentIndex(index)
            
            # Background seçimi
            background = character.get("background", "")
            if background and hasattr(self, 'bg_cb') and self.bg_cb:
                index = self.bg_cb.findText(background)
                if index >= 0:
                    self.bg_cb.setCurrentIndex(index)
            
            # Yetenek puanları
            abilities = character.get("abilities", {})
            if hasattr(self, 'ability_spins'):
                for ability, score in abilities.items():
                    if ability in self.ability_spins:
                        self.ability_spins[ability].setValue(score)
            
            # Sınıf seçimlerini güncelle (widget'lar varsa)
            if hasattr(self, '_refresh_class_options'):
                self._refresh_class_options()
            if hasattr(self, '_refresh_class_features'):
                self._refresh_class_features()
            if hasattr(self, '_refresh_feats'):
                self._refresh_feats()
            
            # Karakter oluşturma sekmesine geç
            self.tab_widget.setCurrentIndex(0)
            
            # Büyü listesini güncelle
            self._update_spells_list()
            
            # Envanteri yenile
            if hasattr(self, '_load_current_character_inventory'):
                self._load_current_character_inventory()
            
            # Resmi yükle
            self._load_character_image_to_gui(character)

            self._update_spell_tab_visibility()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter GUI'ye yüklenemedi:\n{str(e)}")

    def _init_character_ui(self):
        """Karakter oluşturma UI'sını oluştur - Adım bazlı yapı"""
        # Ana splitter oluştur (sol: adım listesi, orta: içerik, sağ: açıklama)
        main_splitter = QtWidgets.QSplitter(Qt.Horizontal)
        main_splitter.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)  # Tüm alanı kapla
        
        # Sol panel: Adım listesi
        self.step_list_widget = QWidget()
        step_list_layout = QVBoxLayout(self.step_list_widget)
        step_list_layout.setContentsMargins(10, 10, 10, 10)
        
        step_list_title = QLabel("Adımlar")
        step_list_title.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        step_list_layout.addWidget(step_list_title)
        
        # Adım listesi
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
        self.step_items = []  # Adım item'larını sakla
        for i, step in enumerate(self.steps):
            item_text = f"{i+1}. {step['name']}"
            item = QListWidgetItem(item_text)
            self.step_list.addItem(item)
            self.step_items.append(item)
        self.step_list.setCurrentRow(0)
        self.step_list.currentRowChanged.connect(self._on_step_changed)
        step_list_layout.addWidget(self.step_list)
        
        # Orta panel: Adım içeriği (StackedWidget)
        self.step_stack = QStackedWidget()
        self.step_widgets = []  # Her adım için widget'ları sakla
        
        # Her adım için widget oluştur
        for i, step in enumerate(self.steps):
            step_widget = QWidget()
            step_layout = QVBoxLayout(step_widget)
            step_layout.setContentsMargins(10, 10, 10, 10)
            
            # Scroll area içinde
            scroll = QScrollArea()
            scroll.setWidgetResizable(True)
            scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
            
            content_widget = QWidget()
            content_layout = QVBoxLayout(content_widget)
            content_layout.setSpacing(15)
            
            # Adım başlığı
            step_title = QLabel(step['name'])
            step_title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
            content_layout.addWidget(step_title)
            
            # Adım açıklaması
            step_desc = QLabel(step['description'])
            step_desc.setStyleSheet("font-size: 14px; color: #7f8c8d; margin-bottom: 15px;")
            step_desc.setWordWrap(True)
            content_layout.addWidget(step_desc)
            
            # Placeholder - gerçek içerik _build_step_widgets'te oluşturulacak
            placeholder = QLabel(f"{step['name']} içeriği buraya gelecek")
            placeholder.setStyleSheet("color: #95a5a6; font-style: italic;")
            content_layout.addWidget(placeholder)
            content_layout.addStretch()
            
            scroll.setWidget(content_widget)
            step_layout.addWidget(scroll)
            
            # İleri/Geri butonları
            nav_layout = QHBoxLayout()
            back_btn = QPushButton("← Geri")
            back_btn.setEnabled(i > 0)
            back_btn.clicked.connect(lambda checked, idx=i: self._go_to_step(idx - 1))
            next_btn = QPushButton("İleri →")
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
        
        # Sağ panel: Açıklama paneli
        self.info_panel = QWidget()
        info_layout = QVBoxLayout(self.info_panel)
        
        # Açıklama paneli başlığı
        info_title = QLabel("Seçim Açıklaması")
        info_title.setStyleSheet("font-size: 18px; font-weight: bold; color: #ecf0f1; margin: 10px;")
        info_title.setAlignment(Qt.AlignCenter)
        info_layout.addWidget(info_title)
        
        # Açıklama metni
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
        self.info_text.setPlaceholderText("Bir seçim yapın, açıklaması burada görünecek...")
        info_layout.addWidget(self.info_text)
        
        # Splitter'a panelleri ekle
        main_splitter.addWidget(self.step_list_widget)
        main_splitter.addWidget(self.step_stack)
        main_splitter.addWidget(self.info_panel)
        
        # Splitter oranları (sol: 200px, orta: esnek, sağ: 300px)
        main_splitter.setSizes([200, 600, 300])
        main_splitter.setChildrenCollapsible(False)
        
        # Görünmez bir container oluştur (widget'ları oluşturmak için)
        self.character_form_container = QWidget()
        self.character_form_container.setVisible(False)
        self.character_form_container.setMaximumSize(0, 0)
        
        # Character form widget'larını oluştur (eski yapıyı koruyoruz ama adım bazlı gösteriyoruz)
        self._build_character_form_widgets()
        
        # Adım widget'larını doldur
        self._populate_step_widgets()
        
        # Character tab'a splitter'ı ekle
        toolbar = self._build_character_toolbar()
        toolbar.setMaximumHeight(40)  # Toolbar yüksekliğini sınırla
        self.character_layout.addWidget(toolbar)
        self.character_layout.addWidget(main_splitter, 1)  # Stretch factor = 1 (tüm kalan alanı kapla)
        
        # İlk adımı göster
        self._go_to_step(0)

    def _build_character_toolbar(self) -> QWidget:
        widget = QWidget()
        widget.setMaximumHeight(35)  # Toolbar yüksekliğini sınırla
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)  # Margin'leri azalt
        layout.setSpacing(5)
        save_btn = QPushButton("💾 Farklı Kaydet")
        save_btn.setToolTip("Karakteri farklı bir JSON dosyasına kaydet")
        save_btn.setMaximumHeight(30)  # Buton yüksekliğini sınırla
        save_btn.clicked.connect(self._manual_save_character)
        layout.addWidget(save_btn)
        layout.addStretch()
        return widget
    
    def _on_step_changed(self, new_index: int):
        """Adım listesinden adım değiştiğinde çağrılır"""
        if 0 <= new_index < len(self.steps):
            self._go_to_step(new_index)
    
    def _go_to_step(self, step_index: int):
        """Belirtilen adıma git"""
        if step_index < 0 or step_index >= len(self.steps):
            return
        
        # Widget'ların varlığını kontrol et
        if not hasattr(self, 'step_stack') or not hasattr(self, 'step_list') or not hasattr(self, 'info_text'):
            return
        
        # Validasyon yap (eğer ileri gidiyorsak)
        if step_index > self.current_step:
            if not self._validate_current_step():
                return
        
        self.current_step = step_index
        
        # Güvenli widget erişimi
        try:
            if self.step_stack.count() > step_index:
                self.step_stack.setCurrentIndex(step_index)
            if self.step_list.count() > step_index:
                self.step_list.setCurrentRow(step_index)
            
            # Adım açıklamasını güncelle
            step = self.steps[step_index]
            self.info_text.setText(f"<b>{step['name']}</b><br><br>{step['description']}")
        except (AttributeError, RuntimeError) as e:
            # Widget henüz hazır değil veya silinmiş
            return
        
        # Özet ve Büyüler adımlarına gelindiğinde ilgili güncellemeleri yap
        try:
            if step['name'] == "Özet":
                self._update_summary_step()
            
            # Büyüler adımının görünürlüğünü kontrol et
            if step['name'] == "Büyüler":
                self._update_spells_step_visibility()
        except (AttributeError, RuntimeError):
            pass
        
        # Sınıf Becerileri adımına gelindiğinde becerileri yenile
        if step['name'] == "Sınıf Becerileri":
            try:
                # Sınıf bilgisini current_character'dan al ve class_cb'yi ayarla
                if hasattr(self, 'current_character') and self.current_character:
                    class_name = self.current_character.get('class', '')
                    if class_name and hasattr(self, 'class_cb'):
                        idx = self.class_cb.findText(class_name)
                        if idx >= 0:
                            self.class_cb.setCurrentIndex(idx)
                        else:
                            # class_cb listesinde yoksa, yine de becerileri yenilemek için adı aktar
                            self.class_cb.addItem(class_name)
                            self.class_cb.setCurrentText(class_name)
                # Becerileri yenile
                if hasattr(self, 'class_cb') and self.class_cb.currentText():
                    self._refresh_class_options()
            except (AttributeError, RuntimeError):
                pass
        
        # İleri/Geri butonlarını güncelle
        try:
            self._update_navigation_buttons()
        except (AttributeError, RuntimeError):
            pass
        
        # Adım listesini güncelle (tamamlanan adımları işaretle)
        try:
            self._update_step_list()
        except (AttributeError, RuntimeError):
            pass
    
    def _update_summary_step(self):
        """Özet adımındaki içeriği güncelle"""
        if not hasattr(self, 'step_widgets') or len(self.step_widgets) < 10:
            return
        
        summary_layout = self.step_widgets[9].layout()
        if not summary_layout:
            return
        
        # Özet widget'ını bul
        summary_text = None
        for i in range(summary_layout.count()):
            item = summary_layout.itemAt(i)
            if item and item.widget():
                widget = item.widget()
                if isinstance(widget, QGroupBox) and widget.title() == "Karakter Özeti":
                    inner_layout = widget.layout()
                    if inner_layout and inner_layout.count() > 0:
                        text_item = inner_layout.itemAt(0)
                        if text_item and text_item.widget() and isinstance(text_item.widget(), QTextEdit):
                            summary_text = text_item.widget()
                            break
        
        if summary_text and hasattr(self, 'current_character') and self.current_character:
            char = self.current_character
            summary_html = f"""
            <h2 style='color: #2c3e50;'>{char.get('name', 'İsimsiz')}</h2>
            <hr>
            <p><b>Sınıf:</b> {char.get('class', 'Seçilmedi')}</p>
            <p><b>Irk:</b> {char.get('race', 'Seçilmedi')}</p>
            <p><b>Arka Plan:</b> {char.get('background', 'Seçilmedi')}</p>
            <p><b>Seviye:</b> {char.get('level', 1)}</p>
            """
            
            # Yetenek puanları
            if hasattr(self, 'ability_spins'):
                summary_html += "<h3 style='color: #3498db; margin-top: 15px;'>Yetenek Puanları:</h3><ul>"
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
                    prof_text = "✓ Uzman" if prof else "Normal"
                    summary_html += f"<li>{skill}: {prof_text}</li>"
                summary_html += "</ul>"
            
            # Büyüler
            if char.get('spells'):
                summary_html += "<h3 style='color: #3498db; margin-top: 15px;'>Büyüler:</h3><ul>"
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
        """Büyüler adımının görünürlüğünü kontrol et"""
        if not hasattr(self, 'current_character') or not self.current_character:
            return
        
        class_name = self.current_character.get('class', '')
        if not class_name:
            return
        
        # Sınıfın büyü kullanıp kullanmadığını kontrol et
        class_data = self.data.get('classes', {}).get(class_name, {})
        is_spellcaster = class_data.get('spellcasting', False) or class_name.lower() in ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard', 'ranger', 'paladin']
        
        # Büyüler adımının widget'ını bul ve güncelle
        spells_step_index = None
        for i, step in enumerate(self.steps):
            if step['name'] == "Büyüler":
                spells_step_index = i
                break
        
        if spells_step_index is not None and spells_step_index < len(self.step_widgets):
            spells_layout = self.step_widgets[spells_step_index].layout()
            if spells_layout:
                # Placeholder'ı kontrol et
                for i in range(spells_layout.count()):
                    item = spells_layout.itemAt(i)
                    if item and item.widget():
                        widget = item.widget()
                        if isinstance(widget, QLabel) and "Bu sınıf büyü kullanmaz" in widget.text():
                            # Büyü kullanıyorsa placeholder'ı gizle
                            widget.setVisible(not is_spellcaster)
                        elif isinstance(widget, QGroupBox) and widget.title() == "Büyü Seçimi":
                            # Büyü kullanmıyorsa widget'ı gizle
                            widget.setVisible(is_spellcaster)
    
    def _validate_current_step(self) -> bool:
        """Mevcut adımın geçerli olup olmadığını kontrol et"""
        step = self.steps[self.current_step]
        
        if step['name'] == "İsim ve Sınıf":
            # Karakter oluşturulmuş mu kontrol et
            if not hasattr(self, 'current_character') or not self.current_character:
                # Eğer karakter yoksa, karakter oluşturma diyaloğunu aç
                self._start_new_character()
                return False
            # İsim ve sınıf kontrolü
            if not self.current_character.get('name') or not self.current_character.get('class'):
                # Eğer isim veya sınıf yoksa, karakter oluşturma diyaloğunu aç
                self._start_new_character()
                return False
            # Karakter oluşturulmuş ve isim/sınıf var, geçerli
            return True
        elif step['name'] == "Irk":
            if not self.current_character or not self.current_character.get('race'):
                QMessageBox.warning(self, "Uyarı", "Lütfen bir ırk seçin.")
                return False
        elif step['name'] == "Arka Plan":
            if not self.current_character or not self.current_character.get('background'):
                QMessageBox.warning(self, "Uyarı", "Lütfen bir arka plan seçin.")
                return False
        elif step['name'] == "Yetenek Puanları":
            # Point-buy kontrolü
            if hasattr(self, 'ability_spins'):
                total_points = sum(self.ability_spins[ability].value() - 8 for ability in self.abilities)
                if total_points > 27:
                    QMessageBox.warning(self, "Uyarı", "Toplam point-buy puanı 27'yi geçemez!")
                    return False
        elif step['name'] == "Sınıf Becerileri":
            # Sınıf becerileri seçim kontrolü (opsiyonel - sınıfa göre değişir)
            if hasattr(self, 'wiz_skills') and hasattr(self, 'current_character'):
                class_name = self.current_character.get('class', '')
                if class_name:
                    class_data = self.data.get('classes', {}).get(class_name, {})
                    skill_choices = class_data.get('skill_choices', 0)
                    selected_count = len(self.wiz_skills.selectedItems())
                    if skill_choices > 0 and selected_count < skill_choices:
                        QMessageBox.warning(self, "Uyarı", f"Lütfen {skill_choices} beceri seçin.")
                        return False
        elif step['name'] == "Büyüler":
            # Büyüler opsiyonel - sadece büyücü sınıflar için kontrol
            if hasattr(self, 'current_character') and self.current_character:
                class_name = self.current_character.get('class', '')
                class_data = self.data.get('classes', {}).get(class_name, {})
                is_spellcaster = class_data.get('spellcasting', False)
                if is_spellcaster and hasattr(self, 'wiz_cantrips'):
                    # Cantrip seçimi kontrolü
                    cantrip_choices = class_data.get('cantrip_choices', 0)
                    selected_cantrips = len(self.wiz_cantrips.selectedItems())
                    if cantrip_choices > 0 and selected_cantrips < cantrip_choices:
                        QMessageBox.warning(self, "Uyarı", f"Lütfen {cantrip_choices} cantrip seçin.")
                        return False
        
        return True
    
    def _update_step_list(self):
        """Adım listesini güncelle - tamamlanan adımları işaretle"""
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
                
                # Adım metnini oluştur
                if is_completed:
                    item_text = f"✓ {i+1}. {step['name']}"
                    item.setForeground(QColor("#27ae60"))  # Yeşil renk
                else:
                    item_text = f"{i+1}. {step['name']}"
                    item.setForeground(QColor("#2c3e50"))  # Normal renk
                
                if is_current:
                    item.setForeground(QColor("#ffffff"))  # Seçili adım beyaz
                
                item.setText(item_text)
        except (AttributeError, RuntimeError, IndexError):
            # Widget henüz hazır değil veya silinmiş
            return
    
    def _is_step_completed(self, step_index: int) -> bool:
        """Bir adımın tamamlanıp tamamlanmadığını kontrol et"""
        if not hasattr(self, 'current_character') or not self.current_character:
            return False
        
        step = self.steps[step_index]
        char = self.current_character
        
        if step['name'] == "İsim ve Sınıf":
            return bool(char.get('name') and char.get('class'))
        elif step['name'] == "Irk":
            return bool(char.get('race'))
        elif step['name'] == "Arka Plan":
            return bool(char.get('background'))
        elif step['name'] == "Yetenek Puanları":
            if hasattr(self, 'ability_spins'):
                # En az bir yetenek puanı ayarlanmışsa tamamlanmış sayılır
                return any(spin.value() > 8 for spin in self.ability_spins.values())
            return False
        elif step['name'] == "Sınıf Becerileri":
            # Beceriler seçilmişse tamamlanmış sayılır (opsiyonel)
            return bool(char.get('skills'))
        elif step['name'] == "Büyüler":
            # Büyücü değilse veya büyüler seçilmişse tamamlanmış sayılır
            class_name = char.get('class', '')
            class_data = self.data.get('classes', {}).get(class_name, {})
            is_spellcaster = class_data.get('spellcasting', False)
            if not is_spellcaster:
                return True  # Büyücü değilse atlanabilir
            return bool(char.get('spells'))
        elif step['name'] == "Feat'ler":
            # Feat'ler opsiyonel, seçilmişse tamamlanmış sayılır
            return True  # Her zaman tamamlanmış sayılır (opsiyonel)
        elif step['name'] == "Ekipman":
            # Ekipman opsiyonel
            return True  # Her zaman tamamlanmış sayılır (opsiyonel)
        elif step['name'] == "Kişilik":
            # Kişilik özellikleri opsiyonel
            return True  # Her zaman tamamlanmış sayılır (opsiyonel)
        elif step['name'] == "Özet":
            # Özet her zaman erişilebilir
            return True
        
        return False
    
    def _update_navigation_buttons(self):
        """İleri/Geri butonlarını güncelle"""
        # Widget'ların varlığını kontrol et
        if not hasattr(self, 'step_stack') or not self.step_stack:
            return
        
        # Tüm adım widget'larındaki butonları bul ve güncelle
        try:
            for i in range(self.step_stack.count()):
                step_widget = self.step_stack.widget(i)
                if not step_widget or not step_widget.layout():
                    continue
                nav_layout_item = step_widget.layout().itemAt(step_widget.layout().count() - 1)
                if not nav_layout_item or not nav_layout_item.layout():
                    continue
                nav_layout = nav_layout_item.layout()
                
                # Butonları bul
                back_btn = None
                next_btn = None
                for j in range(nav_layout.count()):
                    item = nav_layout.itemAt(j)
                    if item and item.widget():
                        widget = item.widget()
                        if isinstance(widget, QPushButton):
                            if "Geri" in widget.text():
                                back_btn = widget
                            elif "İleri" in widget.text() or "Tamamla" in widget.text():
                                next_btn = widget
                
                if back_btn:
                    back_btn.setEnabled(i > 0)
                if next_btn:
                    if i == len(self.steps) - 1:
                        next_btn.setText("Tamamla")
                        # Son adımdaki butonun bağlantısını kontrol et
                        try:
                            next_btn.clicked.disconnect()
                        except TypeError:
                            pass  # Bağlantı yoksa devam et
                        next_btn.clicked.connect(self._complete_character)
                    else:
                        next_btn.setText("İleri →")
                        # Diğer adımlardaki butonların bağlantısını kontrol et
                        try:
                            next_btn.clicked.disconnect()
                        except TypeError:
                            pass  # Bağlantı yoksa devam et
                        next_btn.clicked.connect(lambda checked, idx=i: self._go_to_step(idx + 1))
        except (AttributeError, RuntimeError):
            # Widget henüz hazır değil veya silinmiş
            return
    
    def _populate_step_widgets(self):
        """Her adım için widget içeriğini doldur"""
        # Önce mevcut widget'ları oluştur (eğer yoksa)
        if not hasattr(self, 'character_name_edit'):
            # character_form_container'ı oluştur (görünmez olarak)
            self.character_form_container = QWidget()
            self._build_character_form_widgets()
        
        # Her adım için içeriği doldur
        for i, step in enumerate(self.steps):
            if i >= len(self.step_widgets):
                continue
            
            layout = self.step_widgets[i].layout()

            # Mevcut içeriği temizle (tekrarlı görünümü engellemek için)
            self._clear_layout(layout)
            
            # Placeholder'ı kaldır
            widgets_to_remove = []
            for j in reversed(range(layout.count())):
                item = layout.itemAt(j)
                if item:
                    widget = item.widget()
                    if widget and isinstance(widget, QLabel):
                        try:
                            if "içeriği buraya gelecek" in widget.text() or "yakında eklenecek" in widget.text():
                                widgets_to_remove.append((j, widget))
                        except RuntimeError:
                            # Widget zaten silinmiş, devam et
                            continue
            
            # Widget'ları güvenli şekilde kaldır
            for j, widget in widgets_to_remove:
                layout.removeWidget(widget)
                widget.deleteLater()
            
            # Adım 0: İsim ve Sınıf
            if step['name'] == "İsim ve Sınıf":
                name_class_group = QGroupBox("Karakter Bilgileri")
                name_class_layout = QVBoxLayout()
                name_class_layout.setContentsMargins(5, 5, 5, 5)
                name_class_layout.setSpacing(6)
                name_label = QLabel("İsim:")
                name_edit = QLineEdit()
                name_edit.setMaximumHeight(32)  # Daha kompakt görünüm
                # Bu adım sadece bilgiyi göstermek için; tekrar giriş istememek adına placeholder kaldırıldı
                name_edit.setPlaceholderText("")
                # Karakter bilgilerini yükle
                if hasattr(self, 'current_character') and self.current_character:
                    name_edit.setText(self.current_character.get('name', ''))
                elif hasattr(self, 'character_name_edit'):
                    name_edit.setText(self.character_name_edit.text())
                # Signal bağlantısı
                if hasattr(self, 'character_name_edit'):
                    def update_name(text):
                        if hasattr(self, 'character_name_edit'):
                            self.character_name_edit.setText(text)
                        if hasattr(self, 'current_character') and self.current_character:
                            self.current_character['name'] = text
                            self.current_character['system'] = self.SYSTEM_NAME
                            self._auto_save_character()
                    # Bu adımda kullanıcıdan ikinci kez giriş istenmesin diye alanı sadece-okunur yapıyoruz
                    name_edit.setReadOnly(True)
                    # Yine de programatik güncelleme için sinyal bağlı kalabilir
                    name_edit.textChanged.connect(update_name)
                name_class_layout.addWidget(name_label)
                name_class_layout.addWidget(name_edit)
                
                class_label = QLabel("Sınıf:")
                class_combo = QComboBox()
                class_combo.addItems(sorted(self.data.get("classes", {}).keys()))
                # Karakter bilgilerini yükle
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
                # Signal bağlantısı
                if hasattr(self, 'class_cb'):
                    def update_class(text):
                        if hasattr(self, 'class_cb'):
                            self.class_cb.setCurrentText(text)
                        if hasattr(self, 'current_character') and self.current_character:
                            self.current_character['class'] = text
                            self.current_character['system'] = self.SYSTEM_NAME
                            self._auto_save_character()
                    # Kullanıcıdan tekrar seçim istememek için combobox'ı pasif hale getiriyoruz
                    class_combo.setEnabled(False)
                    class_combo.currentTextChanged.connect(update_class)
                class_combo.setMaximumHeight(32)  # Daha kompakt görünüm
                name_class_layout.addWidget(class_label)
                name_class_layout.addWidget(class_combo)
                name_class_group.setLayout(name_class_layout)
                name_class_group.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
                name_class_group.setMaximumHeight(180)
                layout.insertWidget(2, name_class_group)
            
            # Adım 1: Irk
            elif step['name'] == "Irk":
                race_group = QGroupBox("Irk Seçimi")
                race_layout = QVBoxLayout()
                race_layout.setContentsMargins(5, 5, 5, 5)
                race_layout.setSpacing(6)
                race_label = QLabel("Irk:")
                race_combo = QComboBox()
                race_combo.setMaximumHeight(32)  # Daha kompakt görünüm
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
            
            # Adım 2: Arka Plan
            elif step['name'] == "Arka Plan":
                bg_group = QGroupBox("Arka Plan Seçimi")
                bg_layout = QVBoxLayout()
                bg_layout.setContentsMargins(5, 5, 5, 5)
                bg_layout.setSpacing(6)
                bg_label = QLabel("Arka Plan:")
                bg_combo = QComboBox()
                bg_combo.setMaximumHeight(32)  # Daha kompakt görünüm
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
            
            # Adım 3: Yetenek Puanları
            elif step['name'] == "Yetenek Puanları":
                if hasattr(self, 'ability_spins'):
                    pb_group = QGroupBox("Yetenek Puanları (Point-Buy)")
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
            
            # Adım 4: Sınıf Becerileri
            elif step['name'] == "Sınıf Becerileri":
                if hasattr(self, 'wiz_skills'):
                    skills_group = QGroupBox("Sınıf Becerileri")
                    skills_layout = QVBoxLayout()
                    if hasattr(self, 'wiz_skills_label'):
                        skills_layout.addWidget(self.wiz_skills_label)
                    if hasattr(self, 'wiz_skills'):
                        skills_layout.addWidget(self.wiz_skills)
                    # Expertise için (Rogue vb.)
                    if hasattr(self, 'wiz_expertise_label') and hasattr(self, 'wiz_expertise'):
                        skills_layout.addWidget(self.wiz_expertise_label)
                        skills_layout.addWidget(self.wiz_expertise)
                    skills_group.setLayout(skills_layout)
                    layout.insertWidget(2, skills_group)
                    
                    # Sınıf seçilmişse becerileri yenile
                    class_name = None
                    if hasattr(self, 'current_character') and self.current_character:
                        class_name = self.current_character.get('class', '')
                    elif hasattr(self, 'class_cb') and self.class_cb.currentText():
                        class_name = self.class_cb.currentText()
                    
                    if class_name:
                        # Geçici olarak class_cb'yi ayarla (eğer yoksa)
                        if not hasattr(self, 'class_cb') or not self.class_cb.currentText():
                            if hasattr(self, 'class_cb'):
                                idx = self.class_cb.findText(class_name)
                                if idx >= 0:
                                    self.class_cb.setCurrentIndex(idx)
                        self._refresh_class_options()
                    else:
                        # Sınıf seçilmemişse uyarı göster
                        warning_label = QLabel("⚠️ Lütfen önce bir sınıf seçin (İsim ve Sınıf adımına dönün).")
                        warning_label.setStyleSheet("color: #e74c3c; font-weight: bold; padding: 10px;")
                        skills_layout.insertWidget(0, warning_label)
                else:
                    placeholder = QLabel("Lütfen önce bir sınıf seçin.")
                    placeholder.setStyleSheet("color: #95a5a6; font-style: italic; padding: 20px;")
                    layout.insertWidget(2, placeholder)
            
            # Adım 5: Büyüler
            elif step['name'] == "Büyüler":
                if hasattr(self, 'wiz_cantrips') and hasattr(self, 'wiz_level1'):
                    spells_group = QGroupBox("Büyü Seçimi")
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
                    placeholder = QLabel("Bu sınıf büyü kullanmaz. Bu adımı atlayabilirsiniz.")
                    placeholder.setStyleSheet("color: #95a5a6; font-style: italic; padding: 20px;")
                    layout.insertWidget(2, placeholder)
            
            # Adım 6: Feat'ler
            elif step['name'] == "Feat'ler":
                if hasattr(self, 'feats_group'):
                    feats_group = QGroupBox("Feat Seçimi")
                    feats_layout = QVBoxLayout()
                    if hasattr(self, 'feats_label'):
                        feats_layout.addWidget(self.feats_label)
                    if hasattr(self, 'feats_list'):
                        feats_layout.addWidget(self.feats_list)
                    feats_group.setLayout(feats_layout)
                    layout.insertWidget(2, feats_group)
            
            # Adım 7: Ekipman
            elif step['name'] == "Ekipman":
                equipment_group = QGroupBox("Başlangıç Ekipmanı")
                equipment_layout = QVBoxLayout()
                equipment_info = QLabel("Ekipman seçimi için 'Envanter' sekmesini kullanabilirsiniz.\nVeya sınıfınızın başlangıç ekipmanını seçebilirsiniz.")
                equipment_info.setWordWrap(True)
                equipment_info.setStyleSheet("color: #7f8c8d; padding: 10px;")
                equipment_layout.addWidget(equipment_info)
                
                # Sınıf ekipman seçeneklerini göster (eğer varsa)
                if hasattr(self, 'current_character') and self.current_character:
                    class_name = self.current_character.get('class', '')
                    if class_name and class_name in self.data.get('classes', {}):
                        class_data = self.data['classes'][class_name]
                        equipment_options = class_data.get('starting_equipment', {})
                        if equipment_options:
                            options_label = QLabel("Sınıf Ekipman Seçenekleri:")
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
            
            # Adım 8: Kişilik
            elif step['name'] == "Kişilik":
                personality_container = QWidget()
                personality_layout = QVBoxLayout(personality_container)
                
                # Diller ve Kişilik
                if hasattr(self, 'extra_lang_edit'):
                    misc_group = QGroupBox("Diller ve Kişilik")
                    misc_layout = QVBoxLayout()
                    misc_layout.addWidget(QLabel("Ek Diller"))
                    misc_layout.addWidget(self.extra_lang_edit)
                    misc_layout.addWidget(self.trait_edit)
                    misc_layout.addWidget(self.ideal_edit)
                    misc_layout.addWidget(self.bond_edit)
                    misc_layout.addWidget(self.flaw_edit)
                    misc_group.setLayout(misc_layout)
                    personality_layout.addWidget(misc_group)
                
                # Kişisel Özellikler
                if hasattr(self, 'height_edit'):
                    personal_group = QGroupBox("Fiziksel ve Görünüm Özellikleri")
                    personal_layout = QVBoxLayout()
                    
                    # Fiziksel özellikler
                    physical_group = QGroupBox("Fiziksel Özellikler")
                    physical_layout = QGridLayout()
                    physical_layout.addWidget(QLabel("Boy:"), 0, 0)
                    physical_layout.addWidget(self.height_edit, 0, 1)
                    physical_layout.addWidget(QLabel("Kilo:"), 1, 0)
                    physical_layout.addWidget(self.weight_edit, 1, 1)
                    physical_layout.addWidget(QLabel("Yaş:"), 2, 0)
                    physical_layout.addWidget(self.age_edit, 2, 1)
                    physical_layout.setColumnStretch(1, 1)
                    physical_group.setLayout(physical_layout)
                    personal_layout.addWidget(physical_group)
                    
                    # Görünüm özellikleri
                    appearance_group = QGroupBox("Görünüm Özellikleri")
                    appearance_layout = QGridLayout()
                    appearance_layout.addWidget(QLabel("Saç:"), 0, 0)
                    appearance_layout.addWidget(self.hair_color_edit, 0, 1)
                    appearance_layout.addWidget(QLabel("Göz:"), 1, 0)
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
                    
                    # Görünüm açıklaması
                    if hasattr(self, 'appearance_desc_edit'):
                        desc_group = QGroupBox("Görünüm Açıklaması")
                        desc_layout = QVBoxLayout()
                        desc_layout.addWidget(self.appearance_desc_edit)
                        desc_group.setLayout(desc_layout)
                        personal_layout.addWidget(desc_group)
                    
                    # Karakter resmi
                    if hasattr(self, 'character_image_label'):
                        image_group = QGroupBox("🖼️ Karakter Resmi")
                        image_layout = QVBoxLayout()
                        image_layout.addWidget(self.character_image_label)
                        
                        image_buttons = QHBoxLayout()
                        load_btn = QPushButton("📷 Resim Yükle")
                        load_btn.clicked.connect(self._load_character_image)
                        remove_btn = QPushButton("🗑️ Resmi Kaldır")
                        remove_btn.clicked.connect(self._remove_character_image)
                        image_buttons.addWidget(load_btn)
                        image_buttons.addWidget(remove_btn)
                        image_layout.addLayout(image_buttons)
                        image_group.setLayout(image_layout)
                        personal_layout.addWidget(image_group)
                    
                    personal_group.setLayout(personal_layout)
                    personality_layout.addWidget(personal_group)
                
                layout.insertWidget(2, personality_container)
            
            # Adım 9: Özet
            elif step['name'] == "Özet":
                summary_group = QGroupBox("Karakter Özeti")
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
                
                # Özet metnini oluştur
                if hasattr(self, 'current_character') and self.current_character:
                    char = self.current_character
                    summary_html = f"""
                    <h2>{char.get('name', 'İsimsiz')}</h2>
                    <p><b>Sınıf:</b> {char.get('class', 'Seçilmedi')}</p>
                    <p><b>Irk:</b> {char.get('race', 'Seçilmedi')}</p>
                    <p><b>Arka Plan:</b> {char.get('background', 'Seçilmedi')}</p>
                    <p><b>Seviye:</b> {char.get('level', 1)}</p>
                    """
                    
                    # Yetenek puanları
                    if hasattr(self, 'ability_spins'):
                        summary_html += "<h3>Yetenek Puanları:</h3><ul>"
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
                    
                    # Büyüler
                    if char.get('spells'):
                        summary_html += "<h3>Büyüler:</h3><ul>"
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
                    summary_text.setText("Henüz bir karakter oluşturulmadı.")
                
                summary_layout.addWidget(summary_text)
                summary_group.setLayout(summary_layout)
                layout.insertWidget(2, summary_group)
            
            # Bilinmeyen adımlar için placeholder
            else:
                placeholder = QLabel(f"{step['name']} içeriği yakında eklenecek")
                placeholder.setStyleSheet("color: #95a5a6; font-style: italic; padding: 20px;")
                layout.insertWidget(2, placeholder)

    def _build_character_form(self):
        """Karakter formu widget'larını oluştur"""
        # Seçimler: Irk, Sınıf, Arka plan
        sel_group = QGroupBox("Seçimler")
        sel_layout = QGridLayout()
        sel_layout.setHorizontalSpacing(12)
        sel_layout.setVerticalSpacing(8)
        self.character_name_edit = QLineEdit()
        self.character_name_edit.setPlaceholderText("Karakter ismini girin...")
        self.race_cb = QComboBox(); self.race_cb.addItems(sorted(self.data.get("races", {}).keys()))
        self.class_cb = QComboBox(); self.class_cb.addItems(sorted(self.data.get("classes", {}).keys()))
        self.bg_cb = QComboBox(); self.bg_cb.addItems(sorted(self.data.get("backgrounds", {}).keys()))
        
        # Event handler'ları ekle
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

        name_label = QLabel("İsim")
        race_label = QLabel("Irk")
        class_label = QLabel("Sınıf")
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
        pb_group = QGroupBox("Yetenek Puanları (Point-Buy)")
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


        # Diller ve Kişilik
        misc_group = QGroupBox("Diller ve Kişilik")
        misc_layout = QVBoxLayout()
        self.extra_lang_edit = QLineEdit(); self.extra_lang_edit.setPlaceholderText("Ek diller (virgülle ayırın)")
        self.trait_edit = QLineEdit(); self.trait_edit.setPlaceholderText("Personality Trait")
        self.ideal_edit = QLineEdit(); self.ideal_edit.setPlaceholderText("Ideal")
        self.bond_edit = QLineEdit(); self.bond_edit.setPlaceholderText("Bond")
        self.flaw_edit = QLineEdit(); self.flaw_edit.setPlaceholderText("Flaw")
        misc_layout.addWidget(QLabel("Ek Diller")); misc_layout.addWidget(self.extra_lang_edit)
        misc_layout.addWidget(self.trait_edit); misc_layout.addWidget(self.ideal_edit)
        misc_layout.addWidget(self.bond_edit); misc_layout.addWidget(self.flaw_edit)
        misc_group.setLayout(misc_layout)

        # Kişisel Özellikler
        personal_group = QGroupBox("Kişisel Özellikler")
        personal_layout = QVBoxLayout()
        
        # Fiziksel özellikler
        physical_layout = QGridLayout()
        physical_layout.setHorizontalSpacing(10)
        physical_layout.setVerticalSpacing(6)
        self.height_edit = QLineEdit(); self.height_edit.setPlaceholderText("Boy (örn: 5'8\")")
        self.weight_edit = QLineEdit(); self.weight_edit.setPlaceholderText("Kilo (örn: 150 lbs)")
        self.age_edit = QLineEdit(); self.age_edit.setPlaceholderText("Yaş (örn: 25)")
        physical_layout.addWidget(QLabel("Boy:"), 0, 0)
        physical_layout.addWidget(self.height_edit, 0, 1)
        physical_layout.addWidget(QLabel("Kilo:"), 1, 0)
        physical_layout.addWidget(self.weight_edit, 1, 1)
        physical_layout.addWidget(QLabel("Yaş:"), 2, 0)
        physical_layout.addWidget(self.age_edit, 2, 1)
        physical_layout.setColumnStretch(1, 1)
        
        # Görünüm özellikleri
        appearance_layout = QGridLayout()
        appearance_layout.setHorizontalSpacing(10)
        appearance_layout.setVerticalSpacing(6)
        self.hair_color_edit = QLineEdit(); self.hair_color_edit.setPlaceholderText("Saç Rengi")
        self.eye_color_edit = QLineEdit(); self.eye_color_edit.setPlaceholderText("Göz Rengi")
        self.skin_color_edit = QLineEdit(); self.skin_color_edit.setPlaceholderText("Ten Rengi")
        appearance_layout.addWidget(QLabel("Saç:"), 0, 0)
        appearance_layout.addWidget(self.hair_color_edit, 0, 1)
        appearance_layout.addWidget(QLabel("Göz:"), 1, 0)
        appearance_layout.addWidget(self.eye_color_edit, 1, 1)
        appearance_layout.addWidget(QLabel("Ten:"), 2, 0)
        appearance_layout.addWidget(self.skin_color_edit, 2, 1)
        appearance_layout.setColumnStretch(1, 1)
        
        # Karakter resmi
        image_group = QGroupBox("🖼️ Karakter Resmi")
        image_layout = QVBoxLayout()
        
        # Resim görüntüleme alanı
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
        self.character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")
        self.character_image_label.setWordWrap(True)
        image_layout.addWidget(self.character_image_label)
        
        # Resim butonları
        image_buttons_layout = QHBoxLayout()
        
        load_image_btn = QPushButton("📷 Resim Yükle")
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
        
        remove_image_btn = QPushButton("🗑️ Resmi Kaldır")
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
        
        # Karakter özellikleri
        character_layout = QVBoxLayout()
        self.appearance_desc_edit = QTextEdit(); self.appearance_desc_edit.setPlaceholderText("Görünüm Açıklaması (isteğe bağlı)")
        self.appearance_desc_edit.setMaximumHeight(80)
        character_layout.addWidget(QLabel("Görünüm Açıklaması:"))
        character_layout.addWidget(self.appearance_desc_edit)
        
        # Alignment seçimi
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
        """Karakter resmi yükle"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Karakter Resmi Seç",
            "",
            "Resim Dosyaları (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            try:
                image_path = Path(file_path)
                base64_str = _load_image_to_base64(image_path)
                
                if base64_str:
                    self.current_character_image_data = base64_str
                    
                    # Resmi göster
                    pixmap = QPixmap(str(image_path))
                    if not pixmap.isNull():
                        # Resmi 300x300'e ölçekle (orantılı)
                        scaled_pixmap = pixmap.scaled(
                            300, 300,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.character_image_label.setPixmap(scaled_pixmap)
                        self.character_image_label.setText("")
                    
                    # Karakter verisini güncelle
                    if hasattr(self, 'current_character') and self.current_character:
                        self.current_character["image"] = base64_str
                        self._auto_save_character()
                    
                    QMessageBox.information(self, "Başarılı", "Resim başarıyla yüklendi!")
                else:
                    QMessageBox.warning(self, "Hata", "Resim yüklenemedi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Resim yüklenirken bir hata oluştu:\n{str(e)}")

    def _remove_character_image(self):
        """Karakter resmini kaldır"""
        reply = QMessageBox.question(
            self,
            "Resmi Kaldır",
            "Karakter resmini kaldırmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_character_image_data = None
            self.character_image_label.clear()
            self.character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")
            
            # Karakter verisinden kaldır
            if hasattr(self, 'current_character') and self.current_character:
                if "image" in self.current_character:
                    del self.current_character["image"]
                self._auto_save_character()
            
            QMessageBox.information(self, "Başarılı", "Resim kaldırıldı.")

    def _load_character_image_to_gui(self, character: dict):
        """Karakter verisinden resmi GUI'ye yükle"""
        image_data = character.get("image")
        if image_data:
            self.current_character_image_data = image_data
            pixmap = _get_image_from_character(character)
            if pixmap and not pixmap.isNull():
                # Resmi 300x300'e ölçekle (orantılı)
                scaled_pixmap = pixmap.scaled(
                    300, 300,
                    Qt.KeepAspectRatio,
                    Qt.SmoothTransformation
                )
                self.character_image_label.setPixmap(scaled_pixmap)
                self.character_image_label.setText("")
            else:
                self.character_image_label.setText("Resim yüklenemedi\n(Resim eklemek için butona tıklayın)")
        else:
            self.current_character_image_data = None
            self.character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")

    def _build_character_form_widgets(self):
        """Karakter formu widget'larını oluştur ve layout'a ekle"""
        if not hasattr(self, "character_form_container"):
            return
        
        layout = self.character_form_container.layout()
        if not layout:
            layout = QVBoxLayout(self.character_form_container)
        
        # Seçimler: Irk, Sınıf, Arka plan
        sel_group = QGroupBox("Seçimler")
        sel_layout = QHBoxLayout()
        self.character_name_edit = QLineEdit()
        self.character_name_edit.setPlaceholderText("Karakter ismini girin...")
        self.race_cb = QComboBox(); self.race_cb.addItems(sorted(self.data.get("races", {}).keys()))
        self.class_cb = QComboBox(); self.class_cb.addItems(sorted(self.data.get("classes", {}).keys()))
        self.bg_cb = QComboBox(); self.bg_cb.addItems(sorted(self.data.get("backgrounds", {}).keys()))
        
        # Event handler'ları ekle
        self.race_cb.currentTextChanged.connect(self._show_race_info)
        self.race_cb.currentTextChanged.connect(self._update_ability_scores)
        self.race_cb.currentTextChanged.connect(self._auto_save_character)
        self.class_cb.currentTextChanged.connect(self._show_class_info)
        self.class_cb.currentTextChanged.connect(self._refresh_class_features)
        self.class_cb.currentTextChanged.connect(self._auto_save_character)
        self.class_cb.currentTextChanged.connect(self._update_character_stats)
        self.bg_cb.currentTextChanged.connect(self._show_background_info)
        self.bg_cb.currentTextChanged.connect(self._auto_save_character)
        sel_layout.addWidget(QLabel("İsim")); sel_layout.addWidget(self.character_name_edit)
        sel_layout.addWidget(QLabel("Irk")); sel_layout.addWidget(self.race_cb)
        sel_layout.addWidget(QLabel("Sınıf")); sel_layout.addWidget(self.class_cb)
        sel_layout.addWidget(QLabel("Arka Plan")); sel_layout.addWidget(self.bg_cb)
        sel_group.setLayout(sel_layout)

        # Point-buy: 6 spinbox
        pb_group = QGroupBox("Yetenek Puanları (Point-Buy)")
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

        # Diller ve Kişilik
        misc_group = QGroupBox("Diller ve Kişilik")
        misc_layout = QVBoxLayout()
        self.extra_lang_edit = QLineEdit(); self.extra_lang_edit.setPlaceholderText("Ek diller (virgülle ayırın)")
        self.trait_edit = QLineEdit(); self.trait_edit.setPlaceholderText("Personality Trait")
        self.ideal_edit = QLineEdit(); self.ideal_edit.setPlaceholderText("Ideal")
        self.bond_edit = QLineEdit(); self.bond_edit.setPlaceholderText("Bond")
        self.flaw_edit = QLineEdit(); self.flaw_edit.setPlaceholderText("Flaw")
        misc_layout.addWidget(QLabel("Ek Diller")); misc_layout.addWidget(self.extra_lang_edit)
        misc_layout.addWidget(self.trait_edit); misc_layout.addWidget(self.ideal_edit)
        misc_layout.addWidget(self.bond_edit); misc_layout.addWidget(self.flaw_edit)
        misc_group.setLayout(misc_layout)

        # Kişisel Özellikler
        personal_group = QGroupBox("Kişisel Özellikler")
        personal_layout = QVBoxLayout()
        
        # Fiziksel özellikler
        physical_layout = QHBoxLayout()
        self.height_edit = QLineEdit(); self.height_edit.setPlaceholderText("Boy (örn: 5'8\")")
        self.weight_edit = QLineEdit(); self.weight_edit.setPlaceholderText("Kilo (örn: 150 lbs)")
        self.age_edit = QLineEdit(); self.age_edit.setPlaceholderText("Yaş (örn: 25)")
        physical_layout.addWidget(QLabel("Boy:")); physical_layout.addWidget(self.height_edit)
        physical_layout.addWidget(QLabel("Kilo:")); physical_layout.addWidget(self.weight_edit)
        physical_layout.addWidget(QLabel("Yaş:")); physical_layout.addWidget(self.age_edit)
        
        # Görünüm özellikleri
        appearance_layout = QHBoxLayout()
        self.hair_color_edit = QLineEdit(); self.hair_color_edit.setPlaceholderText("Saç Rengi")
        self.eye_color_edit = QLineEdit(); self.eye_color_edit.setPlaceholderText("Göz Rengi")
        self.skin_color_edit = QLineEdit(); self.skin_color_edit.setPlaceholderText("Ten Rengi")
        appearance_layout.addWidget(QLabel("Saç:")); appearance_layout.addWidget(self.hair_color_edit)
        appearance_layout.addWidget(QLabel("Göz:")); appearance_layout.addWidget(self.eye_color_edit)
        appearance_layout.addWidget(QLabel("Ten:")); appearance_layout.addWidget(self.skin_color_edit)
        
        # Karakter resmi
        image_group = QGroupBox("🖼️ Karakter Resmi")
        image_layout = QVBoxLayout()
        
        # Resim görüntüleme alanı
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
        self.character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")
        self.character_image_label.setWordWrap(True)
        image_layout.addWidget(self.character_image_label)
        
        # Resim butonları
        image_buttons_layout = QHBoxLayout()
        
        load_image_btn = QPushButton("📷 Resim Yükle")
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
        
        remove_image_btn = QPushButton("🗑️ Resmi Kaldır")
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
        
        # Karakter özellikleri
        character_layout = QVBoxLayout()
        self.appearance_desc_edit = QTextEdit(); self.appearance_desc_edit.setPlaceholderText("Görünüm Açıklaması (isteğe bağlı)")
        self.appearance_desc_edit.setMaximumHeight(80)
        character_layout.addWidget(QLabel("Görünüm Açıklaması:"))
        character_layout.addWidget(self.appearance_desc_edit)
        
        # Alignment seçimi
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

        # Sınıf özel seçimleri
        self.wiz_group = QGroupBox("Sınıf Seçimleri")
        wiz_layout = QVBoxLayout()
        self.wiz_skills_label = QLabel("Sınıf Becerileri (seçim sayısı değişkendir)")
        self.wiz_skills = QListWidget(); self.wiz_skills.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.wiz_cantrips_label = QLabel("Cantrip Seçimi")
        self.wiz_cantrips = QListWidget(); self.wiz_cantrips.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.wiz_level1_label = QLabel("1. Seviye Büyüler")
        self.wiz_level1 = QListWidget(); self.wiz_level1.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        
        # Rogue expertise
        self.wiz_expertise_label = QLabel("Uzmanlık (Expertise) Seçimi")
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

        # Sınıf özellikleri seçimi
        self.features_group = QGroupBox("Sınıf Özellikleri")
        features_layout = QVBoxLayout()
        self.features_list = QListWidget()
        self.features_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.features_label = QLabel("Seviye ile Gelen Özellikler:")
        features_layout.addWidget(self.features_label)
        features_layout.addWidget(self.features_list)
        self.features_group.setLayout(features_layout)
        self.features_group.setVisible(False)

        # Feat seçimi
        self.feats_group = QGroupBox("Feat Seçimi")
        feats_layout = QVBoxLayout()
        self.feats_list = QListWidget()
        self.feats_list.setSelectionMode(QtWidgets.QAbstractItemView.MultiSelection)
        self.feats_label = QLabel("Seçilebilir Feat'ler:")
        feats_layout.addWidget(self.feats_label)
        feats_layout.addWidget(self.feats_list)
        self.feats_group.setLayout(feats_layout)
        self.feats_group.setVisible(True)

        self.class_cb.currentIndexChanged.connect(self._refresh_class_options)
        self.race_cb.currentIndexChanged.connect(self._refresh_feats)
        
        # Cache temizleme bağlantıları
        self.race_cb.currentIndexChanged.connect(self._clear_cache)
        self.class_cb.currentIndexChanged.connect(self._clear_cache)
        self.bg_cb.currentIndexChanged.connect(self._clear_cache)
        self.character_name_edit.textChanged.connect(self._clear_cache)
        
        # Sınıf seçimleri değiştiğinde istatistikleri güncelle
        self.wiz_skills.itemSelectionChanged.connect(self._update_character_stats)
        self._refresh_class_options()
        self._refresh_class_features()
        self._refresh_feats()

        # Oluştur ve Özet
        bottom = QVBoxLayout()
        bottom.setSpacing(15)
        create_btn = QPushButton("🎯 Karakteri Tamamla")
        create_btn.setToolTip("Karakteri tamamlayın ve PDF karakter kağıdı oluşturun")
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
        
        # Karakter İstatistikleri Paneli
        stats_group = QGroupBox("📊 Karakter İstatistikleri")
        stats_layout = QVBoxLayout()
        
        # İstatistik grid'i
        stats_grid = QWidget()
        stats_grid_layout = QHBoxLayout()
        
        # Sol kolon - Temel İstatistikler
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
        
        # Sağ kolon - Yetenek Modifierları
        right_stats = QVBoxLayout()
        
        # Yetenek puanları ve modifierları
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
        
        # Skill Modifierları
        skills_group = QGroupBox("Beceri Modifierları")
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
                "acrobatics": "Akrobasi", "animal_handling": "Hayvan Bakımı", "arcana": "Büyü",
                "athletics": "Atletizm", "deception": "Aldatma", "history": "Tarih",
                "insight": "İçgörü", "intimidation": "Gözdağı", "investigation": "Araştırma", "medicine": "Tıp"
            }
            skill_layout.addWidget(QLabel(f"{skill_tr.get(skill, skill)}:"))
            skill_mod_label = QLabel("+0")
            skill_mod_label.setStyleSheet("font-size: 11px; color: #7f8c8d;")
            self.skill_mod_labels[skill] = skill_mod_label
            skill_layout.addWidget(skill_mod_label)
            skill_layout.addStretch()
            left_skills.addLayout(skill_layout)
        
        # Sağ kolon - Beceriler
        right_skills = QVBoxLayout()
        skills_right = ["nature", "perception", "performance", "persuasion", "religion", "sleight_of_hand",
                       "stealth", "survival"]
        
        for skill in skills_right:
            skill_layout = QHBoxLayout()
            skill_tr = {
                "nature": "Doğa", "perception": "Algı", "performance": "Performans",
                "persuasion": "İkna", "religion": "Din", "sleight_of_hand": "El Çabukluğu",
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
        
        # Eski özet
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
                self.spellcasting_check_label.setText("Bu sınıf büyü kullanabilir.")
                self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #27ae60;")
            else:
                self.spellcasting_check_label.setText("Bu sınıf büyü kullanmaz.")
                self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #e74c3c;")

    def _clear_cache(self):
        """UI değiştiğinde cache'i temizle"""
        if hasattr(self, '_feat_cache'):
            self._feat_cache.clear()
        if hasattr(self, '_summary_cache'):
            self._summary_cache.clear()

    def _update_point_buy_info(self):
        """Point-buy sistemini güncelle"""
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
        
        # Renk kodlaması
        if remaining < 0:
            self.pb_info.setStyleSheet("color: red; font-weight: bold;")
        elif remaining == 0:
            self.pb_info.setStyleSheet("color: green; font-weight: bold;")
        else:
            self.pb_info.setStyleSheet("color: black;")

    @staticmethod
    def _clear_layout(layout: QLayout):
        """Bir layout içindeki tüm widget ve alt layout'ları temizle"""
        if not layout:
            return
        while layout.count():
            item = layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
            elif item.layout():
                DndPage._clear_layout(item.layout())

    def _refresh_class_options(self):
        """Sınıf seçeneklerini güncelle"""
        class_name = self.class_cb.currentText()
        classes = self.data.get("classes", {})
        
        # Önce tüm seçimleri temizle
        self.wiz_skills.clear()
        self.wiz_cantrips.clear()
        self.wiz_level1.clear()
        self.wiz_expertise.clear()
        
        if class_name in classes:
            cls = classes[class_name]
            
            # Sınıf becerileri (destekler: {"skills": {"choices": X, "from": [...]}} veya {"class_skills": [...], "skill_choices": X})
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
                
                self.wiz_skills_label.setText(f"Sınıf Becerileri ({choices} seçim):")
            
            # Büyü sınıfları için büyü seçimi (cantrip ve 1. seviye)
            if "spells" in cls:
                spells = cls.get("spells", {})
                cantrips = spells.get("cantrips", [])
                level1 = spells.get("1st_level", []) or spells.get("level1", [])
                
                # Cantrip seçim sayısı (sınıfa özel veya varsayılan)
                cantrip_choices = spells.get("cantrip_known_at_1")
                if cantrip_choices is None:
                    if class_name in ("Wizard", "Cleric"):
                        cantrip_choices = 3
                    elif class_name == "Druid":
                        cantrip_choices = 2
                    else:
                        cantrip_choices = 2
                
                # 1. seviye büyü seçim sayısı (sınıfa özel veya varsayılan)
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
                    self.wiz_cantrips_label.setText(f"Cantrip Seçimi ({cantrip_choices} seçim):")
                    self.wiz_cantrips.setVisible(True)
                
                if level1:
                    self.wiz_level1.clear()
                    for spell in level1:
                        self.wiz_level1.addItem(spell)
                    self.wiz_level1_label.setText(f"1. Seviye Büyüler ({level1_choices} seçim):")
                    self.wiz_level1.setVisible(True)
            
            # Rogue için expertise
            if class_name == "Rogue":
                all_skills = list(self.data.get("skills", {}).keys())
                for skill in all_skills:
                    self.wiz_expertise.addItem(skill)
                self.wiz_expertise_label.setText("Uzmanlık (Expertise) Seçimi (2 seçim):")
                self.wiz_expertise.setVisible(True)

    def _refresh_class_features(self):
        """Sınıf özelliklerini güncelle"""
        if not hasattr(self, 'class_cb') or not self.class_cb:
            return
        class_name = self.class_cb.currentText()
        level = 1  # Karakter oluşturma seviyesi 1
        
        classes = self.data.get("classes", {})
        if class_name in classes:
            cls = classes[class_name]
            class_features = cls.get("class_features", {})
            
            # Seviyeye göre özellikleri topla
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
                    self.features_label.setText(f"Seviye ile Gelen Özellikler (1-{level}):")
            else:
                if hasattr(self, 'features_group'):
                    self.features_group.setVisible(False)

    def _refresh_feats(self):
        """Feat listesini güncelle - optimize edilmiş"""
        if not hasattr(self, 'feats_list') or not self.feats_list:
            return
        self.feats_list.clear()
        
        level = 1  # Karakter oluşturma seviyesi 1
        race = self.race_cb.currentText()
        
        # Cache key oluştur
        cache_key = f"{race}_{level}"
        
        # Eğer aynı seviye ve ırk için cache varsa kullan
        if hasattr(self, '_feat_cache') and cache_key in self._feat_cache:
            cached_data = self._feat_cache[cache_key]
            self.feats_list.addItems(cached_data['items'])
            self.feats_label.setText(cached_data['label'])
            return
        
        # Cache yoksa hesapla
        if not hasattr(self, '_feat_cache'):
            self._feat_cache = {}
        
        feats = self.data.get("equipment", {}).get("feats", {})
        
        # D&D kuralları: 4, 6, 8, 12, 14, 16, 19. seviyelerde feat alınabilir
        # Variant Human 1. seviyede feat alabilir
        feat_allowed_levels = [4, 6, 8, 12, 14, 16, 19]
        variant_human_feat = (race == "Human" and level == 1)
        
        if level not in feat_allowed_levels and not variant_human_feat:
            self.feats_list.addItem("Bu seviyede feat alınamaz (4, 6, 8, 12, 14, 16, 19. seviyeler)")
            self.feats_label.setText("Feat Seçimi: Bu seviyede feat alınamaz")
            self._feat_cache[cache_key] = {
                'items': ["Bu seviyede feat alınamaz (4, 6, 8, 12, 14, 16, 19. seviyeler)"],
                'label': "Feat Seçimi: Bu seviyede feat alınamaz"
            }
            return
        
        items = []
        for feat_name, feat_data in sorted(feats.items()):
            prerequisites = feat_data.get("prerequisites", {})
            description = feat_data.get("description", "")
            
            # Prerequisites kontrolü
            meets_prereqs = self._check_feat_prerequisites(feat_name, prerequisites)
            
            # Prerequisites varsa göster
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
                    prereq_text += " [GEREKSİNİMLER KARŞILANMIYOR]"
            
            # Feat'i listeye ekle
            item_text = f"{feat_name}{prereq_text}"
            items.append(item_text)
            
            item = QListWidgetItem(item_text)
            self.feats_list.addItem(item)
            
            # Prerequisites karşılanmıyorsa gri yap
            if not meets_prereqs:
                item.setForeground(QColor("gray"))
            
            # Tooltip olarak açıklama ekle
            if item:
                item.setToolTip(f"{feat_name}: {description}")
        
        # Seviye bazlı feat sayısını hesapla
        feat_count = self._calculate_available_feat_count(level, race)
        label_text = f"Feat Seçimi (Seçilebilir: {feat_count} adet):"
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
        
        # Mevcut ability score'ları al
        current_scores = {}
        for ability in self.abilities:
            current_scores[ability] = self.ability_spins[ability].value()
        
        # Class ve level bilgilerini al
        class_name = self.class_cb.currentText()
        level = 1  # Karakter oluşturma seviyesi 1
        
        for req_type, req_value in prerequisites.items():
            if req_type == "ability_score_minimum":
                for ability, minimum in req_value.items():
                    if current_scores.get(ability, 0) < minimum:
                        return False
            elif req_type == "level":
                if level < req_value:
                    return False
            elif req_type == "proficiency":
                # Bu basit versiyonda proficiency kontrolü yapmıyoruz
                pass
        
        return True

    def _calculate_available_feat_count(self, level: int, race: str) -> int:
        """Seviye ve ırka göre alınabilir feat sayısını hesapla"""
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
        """Tüm sekmeleri görünür yap"""
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
        """Karakteri tamamla ve PDF'e çevir"""
        # Karakter kontrolü
        if not hasattr(self, 'current_character') or not self.current_character:
            QMessageBox.warning(self, "Uyarı", "Önce bir karakter oluşturun!")
            return
        
        # Son güncellemeleri kaydet
        self._auto_save_character()
        
        # Tüm sekmeleri görünür yap
        self._show_all_tabs()
        
        # PDF'e çevir
        self._export_to_pdf(self.current_character)

    def _create_character(self):
        """Karakter oluştur (sadece veri, isim yok)"""
        # Cache kontrolü
        cache_key = f"summary_{self.character_name_edit.text()}_{self.race_cb.currentText()}_{self.class_cb.currentText()}_1"
        
        if hasattr(self, '_summary_cache') and cache_key in self._summary_cache:
            self.summary.setPlainText(self._summary_cache[cache_key])
            return
        
        # Cache yoksa hesapla
        if not hasattr(self, '_summary_cache'):
            self._summary_cache = {}
        
        character = {
            "name": self.character_name_edit.text().strip() or "İsimsiz Karakter",
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
        
        # Yetenek puanları - önce tüm yetenekleri initialize et
        for ability in self.abilities:
            character["abilities"][ability] = self.ability_spins[ability].value()
        
        # Race bonusları
        race_name = character["race"]
        race_data = self.data.get("races", {}).get(race_name, {})
        ability_increases = race_data.get("ability_score_increase", {})
        
        for ability, bonus in ability_increases.items():
            if ability == "all":
                for abil in self.abilities:
                    character["abilities"][abil] += bonus
            else:
                character["abilities"][ability] += bonus
        
        # Seçilen beceriler
        selected_skills = [item.text() for item in self.wiz_skills.selectedItems()]
        character["skills"]["class_skills"] = selected_skills
        
        # Seçilen büyüler
        selected_cantrips = [item.text() for item in self.wiz_cantrips.selectedItems()]
        selected_level1 = [item.text() for item in self.wiz_level1.selectedItems()]
        
        if selected_cantrips:
            character["spells"]["cantrips"] = selected_cantrips
        if selected_level1:
            character["spells"]["1st_level"] = selected_level1
        
        # Seçilen feat'ler
        selected_feats = [item.text().split(" (")[0] for item in self.feats_list.selectedItems()]
        character["feats"] = selected_feats
        
        # Kişisel özellikler
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
        
        # Özet oluştur
        lines = []
        lines.append(f"İsim: {character['name']}")
        lines.append(f"Irk: {character['race']}")
        lines.append(f"Sınıf: {character['class']}")
        lines.append(f"Arka Plan: {character['background']}")
        lines.append(f"Seviye: {character['level']}")
        lines.append("")
        lines.append("Yetenek Puanları:")
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
        lines.append(f"Büyüler: {', '.join(character['spells'].get('cantrips', []))}")
        lines.append(f"Feat'ler: {', '.join(character['feats'])}")
        lines.append("")
        lines.append(f"Alignment: {character['personality']['alignment']}")
        lines.append(f"Boy: {character['physical']['height']}")
        lines.append(f"Kilo: {character['physical']['weight']}")
        lines.append(f"Yaş: {character['physical']['age']}")
        
        summary_text = "\n".join(lines)
        self.summary.setPlainText(summary_text)
        
        # Cache'e kaydet
        self._summary_cache[cache_key] = summary_text
        
        # Karakteri kaydet
        self.current_character = character
        
        # Büyü listesini güncelle
        self._update_spells_list()
        
        # Envanteri yenile
        if hasattr(self, '_load_current_character_inventory'):
            self._load_current_character_inventory()
        
        # Level up UI'sını güncelle
        if hasattr(self, '_refresh_current_character_info'):
            self._refresh_current_character_info()
        
        # Büyü Yönetimi sekmesine geç
        self.tab_widget.setCurrentIndex(1)
        
        return character

    def _init_spells_ui(self):
        """Büyü yönetimi UI'sını oluştur"""
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
        
        # Başlık
        title_label = QLabel("Büyü Yönetimi")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Karakter seçimi
        char_group = QGroupBox("Karakter Seçimi")
        char_layout = QVBoxLayout()
        
        # Mevcut karakter
        current_char_layout = QHBoxLayout()
        current_char_layout.addWidget(QLabel("Mevcut Karakter:"))
        self.spells_character_combo = QComboBox()
        self.spells_character_combo.addItem("Henüz karakter oluşturulmadı")
        current_char_layout.addWidget(self.spells_character_combo)
        char_layout.addLayout(current_char_layout)
        
        # Büyü kontrolü
        self.spellcasting_check_label = QLabel("")
        self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        char_layout.addWidget(self.spellcasting_check_label)
        
        char_group.setLayout(char_layout)
        layout.addWidget(char_group)
        
        # Büyü listesi
        spells_group = QGroupBox("Mevcut Büyüler")
        spells_layout = QVBoxLayout()
        
        self.spells_list = QListWidget()
        self.spells_list.setMaximumHeight(200)
        spells_layout.addWidget(self.spells_list)
        
        # Büyü bilgisi
        self.spell_info = QTextEdit()
        self.spell_info.setReadOnly(True)
        self.spell_info.setMaximumHeight(150)
        self.spell_info.setPlaceholderText("Bir büyü seçin, detayları burada görünecek...")
        spells_layout.addWidget(self.spell_info)
        
        spells_group.setLayout(spells_layout)
        layout.addWidget(spells_group)
        
        # Büyü seçimi
        self.spell_selection_group = QGroupBox("Yeni Büyü Seçimi")
        spell_selection_layout = QVBoxLayout()
        
        # Büyü seviye seçimi
        spell_level_layout = QHBoxLayout()
        spell_level_layout.addWidget(QLabel("Büyü Seviyesi:"))
        
        self.spell_level_combo = QComboBox()
        self.spell_level_combo.addItems(["Cantrip", "1. Seviye", "2. Seviye", "3. Seviye", "4. Seviye", "5. Seviye"])
        self.spell_level_combo.currentTextChanged.connect(self._on_spell_level_changed)
        spell_level_layout.addWidget(self.spell_level_combo)
        
        spell_selection_layout.addLayout(spell_level_layout)
        
        # Seçilebilir büyüler listesi
        self.available_spells_for_selection = QListWidget()
        self.available_spells_for_selection.setMaximumHeight(200)
        spell_selection_layout.addWidget(QLabel("Seçilebilir Büyüler:"))
        spell_selection_layout.addWidget(self.available_spells_for_selection)
        
        # Büyü ekleme butonu
        add_spell_btn = QPushButton("Büyüyü Ekle")
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
        
        # Büyü ekleme/çıkarma
        manage_group = QGroupBox("Büyü Yönetimi")
        manage_layout = QHBoxLayout()
        
        add_spell_btn = QPushButton("Büyü Ekle")
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
        
        remove_spell_btn = QPushButton("Büyü Çıkar")
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
        
        # Karakter oluşturulduğunda listeyi güncelle
        if hasattr(self, 'current_character'):
            self._update_spells_list()

        layout.addStretch()

    def _init_levelup_ui(self):
        """Seviye atlama UI'sını oluştur"""
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
        
        # Karakter seçimi
        char_select_group = QGroupBox("Karakter Seçimi")
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
        self.levelup_search_edit.setPlaceholderText("Karakter adı ile ara...")
        self.levelup_search_edit.textChanged.connect(self._filter_levelup_characters)
        search_layout.addWidget(self.levelup_search_edit)
        char_select_layout.addLayout(search_layout)
        
        char_select_group.setLayout(char_select_layout)
        layout.addWidget(char_select_group)
        
        # Mevcut karakter bilgisi
        char_info_group = QGroupBox("Mevcut Karakter")
        char_info_layout = QHBoxLayout()
        
        self.current_character_label = QLabel("Henüz karakter oluşturulmadı")
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
        
        # HP artışı
        hp_layout = QHBoxLayout()
        hp_layout.addWidget(QLabel("HP Artışı:"))
        self.hp_gain_label = QLabel("0")
        self.hp_gain_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
        hp_layout.addWidget(self.hp_gain_label)
        level_layout.addLayout(hp_layout)
        
        level_group.setLayout(level_layout)
        layout.addWidget(level_group)
        
        # Ana splitter oluştur
        main_splitter = QtWidgets.QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Sol panel - Seviye atlama seçenekleri (Scroll Area ile)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        left_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        left_layout.setContentsMargins(5, 5, 5, 5)
        left_layout.setSpacing(5)
        
        # Sınıf özellikleri
        features_group = QGroupBox("Yeni Sınıf Özellikleri")
        features_layout = QVBoxLayout()
        
        self.new_features_list = QListWidget()
        self.new_features_list.setMaximumHeight(150)
        features_layout.addWidget(self.new_features_list)
        
        features_group.setLayout(features_layout)
        left_layout.addWidget(features_group)
        
        # ASI/Feat Seçimi
        asi_group = QGroupBox("ASI veya Feat Seçimi")
        asi_layout = QVBoxLayout()
        
        # ASI/Feat seçim tipi
        choice_layout = QHBoxLayout()
        choice_layout.addWidget(QLabel("Seçim Tipi:"))
        
        self.asi_feat_choice = QComboBox()
        self.asi_feat_choice.addItems(["ASI (Ability Score Increase)", "Feat"])
        self.asi_feat_choice.currentTextChanged.connect(self._on_asi_feat_choice_changed)
        choice_layout.addWidget(self.asi_feat_choice)
        
        asi_layout.addLayout(choice_layout)
        
        # ASI seçenekleri - daha kompakt
        self.asi_group = QWidget()
        asi_options_layout = QHBoxLayout()
        
        # Sol kolon - 1. Yetenek
        left_asi = QVBoxLayout()
        left_asi.addWidget(QLabel("1. Yetenek (+1):"))
        self.asi_ability1 = QComboBox()
        self.asi_ability1.addItems(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
        left_asi.addWidget(self.asi_ability1)
        
        # Sağ kolon - 2. Yetenek
        right_asi = QVBoxLayout()
        right_asi.addWidget(QLabel("2. Yetenek (+1):"))
        self.asi_ability2 = QComboBox()
        self.asi_ability2.addItems(["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"])
        right_asi.addWidget(self.asi_ability2)
        
        asi_options_layout.addLayout(left_asi)
        asi_options_layout.addLayout(right_asi)
        self.asi_group.setLayout(asi_options_layout)
        asi_layout.addWidget(self.asi_group)
        
        # Feat seçenekleri
        self.feat_group = QWidget()
        feat_options_layout = QVBoxLayout()
        
        feat_options_layout.addWidget(QLabel("Seçilebilir Feat'ler:"))
        self.available_feats_list = QListWidget()
        self.available_feats_list.setMaximumHeight(150)
        feat_options_layout.addWidget(self.available_feats_list)
        
        self.feat_group.setLayout(feat_options_layout)
        self.feat_group.setVisible(False)
        asi_layout.addWidget(self.feat_group)
        
        asi_group.setLayout(asi_layout)
        left_layout.addWidget(asi_group)
        
        # Bekleyen Seçimler
        pending_group = QGroupBox("⏳ Bekleyen Seçimler")
        pending_group.setMinimumHeight(150)
        pending_layout = QVBoxLayout()
        
        self.pending_choices_list = QListWidget()
        self.pending_choices_list.setMaximumHeight(100)
        pending_layout.addWidget(QLabel("Yapılması gereken seçimler:"))
        pending_layout.addWidget(self.pending_choices_list)
        
        # Bekleyen seçimi tamamla butonu
        complete_choice_btn = QPushButton("Seçili Seçimi Tamamla")
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
        
        # Scroll area'ya widget'ı ekle
        left_scroll.setWidget(left_panel)
        main_splitter.addWidget(left_scroll)
        
        # Sağ panel - Karakter önizleme
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        # Karakter önizleme
        preview_group = QGroupBox("Karakter Önizleme")
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
        """ASI/Feat seçimi değiştiğinde UI'yi güncelle"""
        if choice == "ASI (Ability Score Increase)":
            self.asi_group.setVisible(True)
            self.feat_group.setVisible(False)
        else:  # Feat
            self.asi_group.setVisible(False)
            self.feat_group.setVisible(True)
            self._refresh_available_feats()

    def _refresh_available_feats(self):
        """Seçilebilir feat'leri güncelle"""
        try:
            # Mevcut karakter kontrolü
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                self.available_feats_list.clear()
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Karakterin mevcut feat'lerini al
            current_feats = character_data.get("feats", [])
            
            # Tüm feat'leri al
            all_feats = self.data.get("feats", {})
            
            self.available_feats_list.clear()
            
            for feat_name, feat_data in all_feats.items():
                # Prerequisite kontrolü
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
            print(f"Feat listesi güncellenirken hata: {e}")

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
            
            # Eğer hiç sonuç yoksa bilgi ver
            if filtered_count == 0:
                QMessageBox.information(self, "Arama Sonucu", "Arama kriterlerine uygun karakter bulunamadı.")
                
        except Exception as e:
            print(f"Karakter filtreleme hatası: {e}")

    def _refresh_levelup_character_list(self):
        """Seviye atlama karakter listesini yenile (GUI ve CLI kayıtları dahil)"""
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
                        char_name = char_data.get("name", "İsimsiz")
                        char_level = char_data.get("level", 1)
                        char_class = char_data.get("class", "")
                        display_name = f"{char_name} (Seviye {char_level} {char_class})"
                        self.levelup_character_combo.addItem(display_name, str(filepath))
                        characters.append((char_name, char_level, str(filepath)))
                    except Exception as e:
                        print(f"Karakter dosyası okunamadı {filepath}: {e}")
            
            if not characters:
                self.levelup_character_combo.addItem("Henüz karakter oluşturulmadı")
            
            # İlk karakteri seç ve yükle
            if characters:
                self.levelup_character_combo.setCurrentIndex(0)
                self._load_character_for_levelup()
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter listesi yenilenemedi:\n{str(e)}")

    def _load_character_for_levelup(self):
        """Seçilen karakteri seviye atlama için yükle"""
        try:
            # Combo box'tan seçilen karakteri al
            current_index = self.levelup_character_combo.currentIndex()
            if current_index < 0:
                return
                
            filepath = self.levelup_character_combo.itemData(current_index)
            if not filepath:
                return
                
            # current_character_file'ı güncelle (diğer fonksiyonlar için)
            self.current_character_file = filepath
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            # Karakter bilgisini göster
            char_name = character_data.get("name", "İsimsiz")
            char_level = character_data.get("level", 1)
            char_class = character_data.get("class", "")
            self.current_character_label.setText(f"{char_name} - Seviye {char_level} {char_class}")
                
            current_level = character_data.get("level", 1)
            self.current_level_label.setText(str(current_level))
            self.new_level_spin.setRange(current_level + 1, 20)
            self.new_level_spin.setValue(current_level + 1)
            
            # HP artışını hesapla
            self._on_level_change()
            
            # Yeni seçenekleri güncelle
            self._refresh_available_feats()
            self._update_character_preview()
            self._refresh_pending_choices()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter yüklenemedi:\n{str(e)}")

    def _update_character_preview(self):
        """Karakter önizlemesini güncelle"""
        try:
            # Mevcut karakter kontrolü
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                self.character_preview.clear()
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Önizleme metni oluştur
            preview_lines = []
            
            # Temel bilgiler
            preview_lines.append(f"🎭 {character_data.get('name', 'İsimsiz')}")
            preview_lines.append(f"Seviye {character_data.get('level', 1)} {character_data.get('class', 'Sınıfsız')}")
            preview_lines.append(f"Irk: {character_data.get('race', 'Irksız')}")
            preview_lines.append("")
            
            # Yetenek puanları
            preview_lines.append("📊 Yetenek Puanları:")
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
            
            preview_lines.append(f"❤️ HP: {max_hp}")
            preview_lines.append(f"🛡️ AC: {base_ac}")
            preview_lines.append("")
            
            # Feat'ler
            feats = character_data.get("feats", [])
            if feats:
                preview_lines.append("🎯 Feat'ler:")
                for feat in feats:
                    preview_lines.append(f"  • {feat}")
                preview_lines.append("")
            
            # Büyüler
            spells = character_data.get("spells", {})
            if spells:
                preview_lines.append("🔮 Büyüler:")
                for spell_type, spell_list in spells.items():
                    if spell_list:
                        preview_lines.append(f"  {spell_type.title()}: {', '.join(spell_list)}")
                preview_lines.append("")
            
            preview_text = "\n".join(preview_lines)
            self.character_preview.setPlainText(preview_text)
            
        except Exception as e:
            print(f"Karakter önizleme güncellenirken hata: {e}")

    def _on_level_change(self):
        """Seviye değiştiğinde HP artışını hesapla"""
        try:
            # Mevcut karakter kontrolü
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
                
            # HP artışını hesapla
            char_class = character_data.get("class", "")
            constitution = character_data.get("abilities", {}).get("constitution", 10)
            con_modifier = (constitution - 10) // 2
            
            # Sınıf HP dice'ları
            hp_dice = {
                "Barbarian": 12, "Fighter": 10, "Paladin": 10, "Ranger": 10,
                "Artificer": 8, "Bard": 8, "Cleric": 8, "Druid": 8, 
                "Monk": 8, "Rogue": 8, "Warlock": 8,
                "Sorcerer": 6, "Wizard": 6
            }
            
            class_hp = hp_dice.get(char_class, 6)
            hp_gain = (new_level - current_level) * (class_hp + con_modifier)
            
            self.hp_gain_label.setText(str(hp_gain))
            
            # Yeni sınıf özelliklerini göster
            self._update_class_features(new_level)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"HP hesaplanamadı:\n{str(e)}")

    def _update_class_features(self, new_level):
        """Yeni seviyede kazanılan sınıf özelliklerini güncelle"""
        try:
            self.new_features_list.clear()
            
            # Mevcut karakter kontrolü
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
                
            # Sınıf özelliklerini kontrol et
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
            print(f"Sınıf özellikleri güncellenemedi: {e}")

    def _level_up_character(self):
        """Karakteri seviye atlat"""
        try:
            # Mevcut karakter kontrolü
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                QMessageBox.warning(self, "Uyarı", "Lütfen önce bir karakter oluşturun veya yükleyin!")
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
                
            current_level = character_data.get("level", 1)
            new_level = self.new_level_spin.value()
            
            if new_level <= current_level:
                QMessageBox.warning(self, "Uyarı", "Yeni seviye mevcut seviyeden büyük olmalı!")
                return
                
            # HP artışını hesapla ve uygula
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
            
            # ASI/Feat seçimi
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
                        # Feat seçilmediyse bekleyen seçimlere ekle
                        if "pending_choices" not in character_data:
                            character_data["pending_choices"] = []
                        character_data["pending_choices"].append({
                            "type": "feat",
                            "level": new_level,
                            "description": f"Seviye {new_level} Feat Seçimi"
                        })
            
            # Karakteri güncelle
            character_data["level"] = new_level
            if "hp" not in character_data:
                character_data["hp"] = class_hp + con_modifier  # Seviye 1 HP
            character_data["hp"] += hp_gain
            
            # Dosyaya kaydet
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
                
            QMessageBox.information(self, "Başarılı", 
                f"Karakter seviye {new_level}'e yükseltildi!\nHP artışı: +{hp_gain}")
            
            # Mevcut karakter bilgisini yenile
            self._refresh_current_character_info()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Seviye atlama başarısız:\n{str(e)}")

    def _refresh_pending_choices(self):
        """Bekleyen seçimleri güncelle"""
        try:
            # Mevcut karakter kontrolü
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                self.pending_choices_list.clear()
                return
                
            filepath = self.current_character_file
                
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Bekleyen seçimleri temizle
            self.pending_choices_list.clear()
            
            # Bekleyen seçimleri listele
            pending_choices = character_data.get("pending_choices", [])
            for choice in pending_choices:
                choice_text = f"Seviye {choice['level']}: {choice['description']}"
                item = QListWidgetItem(choice_text)
                item.setData(Qt.UserRole, choice)  # Seçim verisini sakla
                self.pending_choices_list.addItem(item)
                
        except Exception as e:
            print(f"Bekleyen seçimler güncellenirken hata: {e}")

    def _complete_pending_choice(self):
        """Seçili bekleyen seçimi tamamla"""
        try:
            selected_item = self.pending_choices_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Uyarı", "Lütfen tamamlamak istediğiniz seçimi seçin!")
                return
            
            choice_data = selected_item.data(Qt.UserRole)
            choice_type = choice_data.get("type")
            
            if choice_type == "feat":
                self._complete_pending_feat_choice(choice_data)
            else:
                QMessageBox.information(self, "Bilgi", f"Bu seçim türü henüz desteklenmiyor: {choice_type}")
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Bekleyen seçim tamamlanırken hata oluştu:\n{str(e)}")

    def _complete_pending_feat_choice(self, choice_data):
        """Bekleyen feat seçimini tamamla"""
        try:
            # Feat seçim dialog'u aç
            feat_dialog = QDialog(self)
            feat_dialog.setWindowTitle(f"Feat Seçimi - {choice_data['description']}")
            feat_dialog.setModal(True)
            feat_dialog.resize(500, 400)
            
            layout = QVBoxLayout(feat_dialog)
            
            # Başlık
            title_label = QLabel(f"Seviye {choice_data['level']} için feat seçin:")
            title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(title_label)
            
            # Mevcut karakter bilgilerini al
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                QMessageBox.warning(self, "Uyarı", "Mevcut karakter bulunamadı!")
                return
                
            filepath = self.current_character_file
            
            import json
            with open(filepath, 'r', encoding='utf-8') as f:
                character_data = json.load(f)
            
            # Seçilebilir feat'leri al
            current_feats = character_data.get("feats", [])
            all_feats = self.data.get("feats", {})
            
            feat_list = QListWidget()
            for feat_name, feat_data in all_feats.items():
                # Prerequisite kontrolü
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
            
            cancel_btn = QPushButton("İptal")
            cancel_btn.clicked.connect(feat_dialog.reject)
            button_layout.addWidget(cancel_btn)
            
            select_btn = QPushButton("Seç")
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
                    QMessageBox.warning(feat_dialog, "Uyarı", "Lütfen bir feat seçin!")
                    return
                
                feat_name = selected_feat.text().split(" - ")[0]
                
                # Feat'i karaktere ekle
                if "feats" not in character_data:
                    character_data["feats"] = []
                character_data["feats"].append(feat_name)
                
                # Bekleyen seçimi kaldır
                pending_choices = character_data.get("pending_choices", [])
                pending_choices = [c for c in pending_choices if c != choice_data]
                character_data["pending_choices"] = pending_choices
                
                # Dosyaya kaydet
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(character_data, f, ensure_ascii=False, indent=2)
                
                QMessageBox.information(feat_dialog, "Başarılı", f"{feat_name} feat'i eklendi!")
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
            QMessageBox.critical(self, "Hata", f"Feat seçimi tamamlanırken hata oluştu:\n{str(e)}")

    def _refresh_current_character_info(self):
        """Mevcut karakter bilgisini yenile"""
        try:
            if hasattr(self, 'current_character') and self.current_character:
                char_name = self.current_character.get('name', 'İsimsiz')
                char_level = self.current_character.get('level', 1)
                char_class = self.current_character.get('class', 'Sınıfsız')
                
                info_text = f"{char_name} - Seviye {char_level} {char_class}"
                self.current_character_label.setText(info_text)
                
                # Seviye bilgilerini güncelle
                self.current_level_label.setText(str(char_level))
                self.new_level_spin.setValue(char_level + 1)
                
                # HP artışını hesapla
                self._on_level_change()
                
                # Yeni seçenekleri güncelle
                self._refresh_available_feats()
                self._update_character_preview()
                self._refresh_pending_choices()
            else:
                self.current_character_label.setText("Henüz karakter oluşturulmadı")
                self.current_level_label.setText("1")
                self.new_level_spin.setValue(2)
                
        except Exception as e:
            print(f"Karakter bilgisi yenilenirken hata: {e}")

    def _init_inventory_ui(self):
        """Envanter UI'sını oluştur"""
        layout = self.inventory_layout
        
        # Ana splitter (sol: envanter, sağ: eşya detayları)
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
        inventory_group.setTitle("")  # Başlığı kaldır
        inventory_group.setContentsMargins(3, 3, 3, 3)
        inventory_layout = QVBoxLayout()
        inventory_layout.setContentsMargins(3, 3, 3, 3)
        inventory_layout.setSpacing(2)
        
        self.inventory_list = QListWidget()
        self.inventory_list.setMinimumHeight(100)
        self.inventory_list.itemClicked.connect(self._show_item_details)
        inventory_layout.addWidget(self.inventory_list)
        
        # Envanter butonları (kompakt)
        item_buttons_layout = QHBoxLayout()
        
        add_item_btn = QPushButton("Eşya Ekle")
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
        
        remove_item_btn = QPushButton("Eşya Çıkar")
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
        
        # Envanter özeti (kompakt)
        summary_group = QGroupBox()
        summary_group.setTitle("")  # Başlığı kaldır
        summary_group.setContentsMargins(3, 3, 3, 3)
        summary_layout = QHBoxLayout()
        summary_layout.setContentsMargins(3, 3, 3, 3)
        
        self.weight_label = QLabel("Ağırlık: 0 lb")
        self.weight_label.setStyleSheet("font-weight: bold; color: #f39c12; font-size: 11px;")
        summary_layout.addWidget(self.weight_label)
        
        self.gold_label = QLabel("Altın: 0 gp")
        self.gold_label.setStyleSheet("font-weight: bold; color: #f1c40f; font-size: 11px;")
        summary_layout.addWidget(self.gold_label)
        
        summary_group.setLayout(summary_layout)
        left_layout.addWidget(summary_group)
        
        # Eşya kategorileri (ana bölüm)
        categories_group = QGroupBox("📋 D&D 5e Eşya Kategorileri")
        categories_group.setContentsMargins(5, 5, 5, 5)
        categories_group.setMinimumHeight(300)
        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(5, 5, 5, 5)
        categories_layout.setSpacing(3)
        
        # Kategoriler için tab widget
        self.categories_tabs = QTabWidget()
        
        # Silahlar sekmesi
        self.weapons_tab = QtWidgets.QWidget()
        self.weapons_list = QListWidget()
        weapons_layout = QVBoxLayout()
        weapons_layout.addWidget(self.weapons_list)
        self.weapons_tab.setLayout(weapons_layout)
        self.categories_tabs.addTab(self.weapons_tab, "⚔️ Silahlar")
        
        # Zırhlar sekmesi
        self.armor_tab = QtWidgets.QWidget()
        self.armor_list = QListWidget()
        armor_layout = QVBoxLayout()
        armor_layout.addWidget(self.armor_list)
        self.armor_tab.setLayout(armor_layout)
        self.categories_tabs.addTab(self.armor_tab, "🛡️ Zırhlar")
        
        # Macera eşyaları sekmesi (tab widget içinde)
        self.adventure_gear_tab = QtWidgets.QWidget()
        adventure_gear_layout = QVBoxLayout()
        
        # Macera eşyaları için alt tab widget
        self.adventure_gear_subtabs = QTabWidget()
        
        # Alt kategoriler
        self.storage_tab = QtWidgets.QWidget()
        self.storage_list = QListWidget()
        storage_layout = QVBoxLayout()
        storage_layout.addWidget(self.storage_list)
        self.storage_tab.setLayout(storage_layout)
        self.adventure_gear_subtabs.addTab(self.storage_tab, "📦 Depolama")
        
        self.tools_tab = QtWidgets.QWidget()
        self.tools_list = QListWidget()
        tools_layout = QVBoxLayout()
        tools_layout.addWidget(self.tools_list)
        self.tools_tab.setLayout(tools_layout)
        self.adventure_gear_subtabs.addTab(self.tools_tab, "🔧 Araçlar")
        
        self.focus_tab = QtWidgets.QWidget()
        self.focus_list = QListWidget()
        focus_layout = QVBoxLayout()
        focus_layout.addWidget(self.focus_list)
        self.focus_tab.setLayout(focus_layout)
        self.adventure_gear_subtabs.addTab(self.focus_tab, "🔮 Büyü Odakları")
        
        self.clothing_tab = QtWidgets.QWidget()
        self.clothing_list = QListWidget()
        clothing_layout = QVBoxLayout()
        clothing_layout.addWidget(self.clothing_list)
        self.clothing_tab.setLayout(clothing_layout)
        self.adventure_gear_subtabs.addTab(self.clothing_tab, "👕 Giysiler")
        
        self.other_tab = QtWidgets.QWidget()
        self.other_list = QListWidget()
        other_layout = QVBoxLayout()
        other_layout.addWidget(self.other_list)
        self.other_tab.setLayout(other_layout)
        self.adventure_gear_subtabs.addTab(self.other_tab, "🎯 Diğer")
        
        adventure_gear_layout.addWidget(self.adventure_gear_subtabs)
        self.adventure_gear_tab.setLayout(adventure_gear_layout)
        self.categories_tabs.addTab(self.adventure_gear_tab, "🎒 Macera Eşyaları")
        
        categories_layout.addWidget(self.categories_tabs)
        
        # Kategorilerden eşya ekleme butonu
        add_from_category_btn = QPushButton("Seçili Eşyayı Envantere Ekle")
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
        
        # Scroll area'ya widget'ı ekle
        left_scroll.setWidget(left_panel)
        
        # Eşya kategorileri bölümünü scroll area dışına ekle
        left_layout.addWidget(categories_group)
        
        # Kategori listelerini doldur
        self._populate_item_categories()
        
        main_splitter.addWidget(left_scroll)
        
        # Sağ panel - Eşya detayları
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        details_group = QGroupBox("Eşya Detayları")
        details_layout = QVBoxLayout()
        
        self.item_details_text = QTextEdit()
        self.item_details_text.setReadOnly(True)
        self.item_details_text.setMinimumHeight(300)
        details_layout.addWidget(self.item_details_text)
        
        details_group.setLayout(details_layout)
        right_layout.addWidget(details_group)
        
        main_splitter.addWidget(right_panel)
        main_splitter.setSizes([400, 600])
        
        # Mevcut karakterin envanterini yükle
        self._load_current_character_inventory()

    def _load_current_character_inventory(self):
        """Mevcut karakterin envanterini yükle"""
        try:
            if hasattr(self, 'current_character_file') and self.current_character_file:
                import json
                with open(self.current_character_file, 'r', encoding='utf-8') as f:
                    character_data = json.load(f)
                
                # Envanteri temizle
                self.inventory_list.clear()
                
                # Envanter eşyalarını yükle
                equipment = character_data.get("equipment", [])
                for item in equipment:
                    item_name = item.get('name', 'İsimsiz Eşya')
                    quantity = item.get('quantity', 1)
                    category = item.get('category', '')
                    
                    # Eşya tipine göre ikon ekle
                    if item.get('type') == 'weapon':
                        icon = "⚔️"
                    elif item.get('type') == 'armor':
                        icon = "🛡️"
                    elif item.get('type') == 'gear':
                        icon = "🎒"
                    else:
                        icon = "📦"
                    
                    item_text = f"{icon} {item_name}"
                    if quantity > 1:
                        item_text += f" x{quantity}"
                    if category:
                        item_text += f" ({category})"
                    
                    self.inventory_list.addItem(item_text)
                
                # Envanter özetini güncelle
                self._update_inventory_summary(character_data)
            else:
                # Karakter yoksa envanteri temizle
                self.inventory_list.clear()
                self.weight_label.setText("Ağırlık: 0 lb")
                self.gold_label.setText("Altın: 0 gp")
                
        except Exception as e:
            print(f"Envanter yüklenemedi: {e}")

    def _populate_item_categories(self):
        """Eşya kategorilerini doldur"""
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
            
            # Zırhlar
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
            
            # Macera eşyaları kategorilere ayır
            adventure_gear = self.data.get("equipment", {}).get("adventuring_gear", {})
        
            # Kategorileri temizle
            self.storage_list.clear()
            self.tools_list.clear()
            self.focus_list.clear()
            self.clothing_list.clear()
            self.other_list.clear()
            
            # Kategorilere göre eşyaları ayır
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
            print(f"Eşya kategorileri yüklenirken hata: {e}")

    def _categorize_adventure_gear(self, gear_name, description):
        """Macera eşyalarını kategorilere ayır"""
        gear_name_lower = gear_name.lower()
        description_lower = description.lower()
        
        # Depolama eşyaları
        storage_keywords = [
            "backpack", "bag", "barrel", "basket", "bottle", "bucket", 
            "chest", "case", "pouch", "sack", "vial", "flask", "tankard",
            "waterskin", "container", "storage"
        ]
        
        # Araçlar
        tools_keywords = [
            "hammer", "crowbar", "grappling", "block and tackle", "climber's kit",
            "fishing tackle", "healer's kit", "hunting trap", "ball bearings",
            "caltrops", "chain", "chalk", "rope", "lantern", "torch", "oil",
            "spike", "tinderbox", "tool", "kit", "lock", "pick", "shovel",
            "tent", "bedroll", "blanket", "bell", "candle", "lamp"
        ]
        
        # Büyü odakları
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
        
        # Diğer (varsayılan)
        return "other"

    def _show_item_categories(self):
        """Eşya kategorilerini göster"""
        if not hasattr(self, 'categories_tabs'):
            return
        
        # Kategoriler grubunu vurgula
        self.categories_tabs.setCurrentIndex(0)  # Silahlar sekmesine git
        
        # Bilgi mesajı göster
        from PySide6.QtWidgets import QMessageBox
        msg = QMessageBox()
        msg.setWindowTitle("Eşya Ekleme")
        msg.setText("Aşağıdaki kategorilerden bir eşya seçin ve 'Seçili Eşyayı Envantere Ekle' butonuna tıklayın.")
        msg.setInformativeText("• ⚔️ Silahlar sekmesinde silahlar\n• 🛡️ Zırhlar sekmesinde zırhlar\n• 🎒 Macera Eşyaları sekmesinde:\n  - 📦 Depolama eşyaları\n  - 🔧 Araçlar\n  - 🔮 Büyü Odakları\n  - 👕 Giysiler\n  - 🎯 Diğer")
        msg.exec()

    def _add_selected_item_from_category(self):
        """Seçili eşyayı envantere ekle"""
        try:
            # Hangi sekme aktif?
            current_tab = self.categories_tabs.currentIndex()
            
            if current_tab == 0:  # Silahlar
                selected_item = self.weapons_list.currentItem()
                item_data = self.data.get("equipment", {}).get("weapons", {})
            elif current_tab == 1:  # Zırhlar
                selected_item = self.armor_list.currentItem()
                item_data = self.data.get("equipment", {}).get("armor", {})
            elif current_tab == 2:  # Macera eşyaları
                # Alt sekme kontrolü
                sub_tab = self.adventure_gear_subtabs.currentIndex()
                if sub_tab == 0:  # Depolama
                    selected_item = self.storage_list.currentItem()
                elif sub_tab == 1:  # Araçlar
                    selected_item = self.tools_list.currentItem()
                elif sub_tab == 2:  # Büyü Odakları
                    selected_item = self.focus_list.currentItem()
                elif sub_tab == 3:  # Giysiler
                    selected_item = self.clothing_list.currentItem()
                elif sub_tab == 4:  # Diğer
                    selected_item = self.other_list.currentItem()
                else:
                    return
                
                item_data = self.data.get("equipment", {}).get("adventuring_gear", {})
            
            if not selected_item:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Uyarı", "Lütfen eklemek istediğiniz eşyayı seçin!")
                return
            
            # Eşya adını parse et (format: "Eşya Adı - 10 gp (5 lb)")
            item_text = selected_item.text()
            item_name = item_text.split(" - ")[0]
            
            # Eşya verilerini al
            if item_name not in item_data:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Hata", "Eşya verileri bulunamadı!")
                return
            
            item_info = item_data[item_name]
            
            # Miktar sor
            from PySide6.QtWidgets import QInputDialog
            quantity, ok = QInputDialog.getInt(None, "Miktar", f"{item_name} kaç adet eklemek istiyorsunuz?", 1, 1, 1000)
            
            if not ok:
                return
            
            # Mevcut karakter kontrolü
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Uyarı", "Lütfen önce bir karakter oluşturun!")
                return
            
            character_file = self.current_character_file
            
            try:
                import json
                with open(character_file, 'r', encoding='utf-8') as f:
                    character_data = json.load(f)
            except:
                from PySide6.QtWidgets import QMessageBox
                QMessageBox.warning(None, "Hata", "Karakter dosyası yüklenemedi!")
                return
            
            # Yeni eşya oluştur
            new_item = {
                "name": item_name,
                "category": "Silah" if current_tab == 0 else "Zırh" if current_tab == 1 else "Macera Eşyası",
                "weight": item_info.get("weight", 0),
                "cost": item_info.get("cost", "0 gp"),
                "quantity": quantity
            }
            
            # Silah özellikleri
            if current_tab == 0:  # Silahlar
                new_item["damage"] = item_info.get("damage", "")
                new_item["properties"] = item_info.get("properties", "")
            
            # Zırh özellikleri
            elif current_tab == 1:  # Zırhlar
                new_item["ac"] = item_info.get("ac", "")
                new_item["armor_type"] = item_info.get("armor_type", "")
            
            # Macera eşyası özellikleri
            else:
                new_item["description"] = item_info.get("description", "")
            
            # Eşyayı karaktere ekle
            if "equipment" not in character_data:
                character_data["equipment"] = []
            
            character_data["equipment"].append(new_item)
            
            # Karakteri kaydet
            with open(character_file, 'w', encoding='utf-8') as f:
                json.dump(character_data, f, ensure_ascii=False, indent=2)
            
            # Envanteri yenile
            self._load_current_character_inventory()
            
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.information(None, "Başarılı", f"{item_name} x{quantity} envantere eklendi!")
            
        except Exception as e:
            from PySide6.QtWidgets import QMessageBox
            QMessageBox.critical(None, "Hata", f"Eşya eklenirken hata oluştu: {e}")

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
                                char_name = char_data.get("name", "İsimsiz")
                                char_level = char_data.get("level", 1)
                                char_class = char_data.get("class", "")
                                display_name = f"{char_name} (Seviye {char_level} {char_class})"
                                self.inventory_character_combo.addItem(display_name, filepath)
                                characters.append((char_name, char_level, filepath))
                        except Exception as e:
                            print(f"Karakter dosyası okunamadı {filename}: {e}")
            
            if not characters:
                self.inventory_character_combo.addItem("Henüz karakter oluşturulmadı")
            
            # İlk karakteri seç ve envanteri yükle
            if characters:
                self.inventory_character_combo.setCurrentIndex(0)
                self._load_character_inventory()
                
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karakter listesi yenilenemedi:\n{str(e)}")

    def _load_character_inventory(self):
        """Seçilen karakterin envanterini yükle"""
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
            
            # Envanter eşyalarını yükle
            equipment = character_data.get("equipment", [])
            for item in equipment:
                item_name = item.get('name', 'İsimsiz Eşya')
                quantity = item.get('quantity', 1)
                category = item.get('category', '')
                
                # Eşya tipine göre ikon ekle
                if item.get('type') == 'weapon':
                    icon = "⚔️"
                elif item.get('type') == 'armor':
                    icon = "🛡️"
                elif item.get('type') == 'gear':
                    icon = "🎒"
                else:
                    icon = "📦"
                
                item_text = f"{icon} {item_name}"
                if quantity > 1:
                    item_text += f" x{quantity}"
                if category:
                    item_text += f" ({category})"
                
                self.inventory_list.addItem(item_text)
            
            # Envanter özetini güncelle
            self._update_inventory_summary(character_data)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Envanter yüklenemedi:\n{str(e)}")

    def _update_inventory_summary(self, character_data):
        """Envanter özetini güncelle"""
        try:
            equipment = character_data.get("equipment", [])
            total_weight = 0
            total_gold = 0
            
            for item in equipment:
                # Ağırlık hesaplama
                weight = item.get('weight', 0)
                quantity = item.get('quantity', 1)
                total_weight += weight * quantity
                
                # Altın hesaplama - cost field'ından parse et
                cost_str = item.get('cost', '0 gp')
                try:
                    # "10 gp", "5 sp" gibi formatları parse et
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
                    pass  # Parse edilemeyen değerleri görmezden gel
            
            self.weight_label.setText(f"Toplam Ağırlık: {total_weight} lb")
            
            # Karakterin altın miktarını da kontrol et
            character_gold = character_data.get("gold", 0)
            self.gold_label.setText(f"Altın: {total_gold + character_gold} gp")
            
        except Exception as e:
            print(f"Envanter özeti güncellenemedi: {e}")

    def _show_item_details(self, item):
        """Seçili eşyanın detaylarını göster"""
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
                
                # Eşya adı ve ikon
                item_name = item_data.get('name', 'İsimsiz Eşya')
                item_type = item_data.get('type', 'gear')
                
                # İkon belirleme
                if item_type == 'weapon':
                    icon = "⚔️"
                elif item_type == 'armor':
                    icon = "🛡️"
                else:
                    icon = "🎒"
                
                details = f"<h3>{icon} {item_name}</h3><br>"
                
                # Temel bilgiler
                details += "<b>📋 Temel Bilgiler:</b><br>"
                
                if 'category' in item_data:
                    details += f"• <b>Kategori:</b> {item_data['category']}<br>"
                
                if 'cost' in item_data:
                    details += f"• <b>Değer:</b> {item_data['cost']}<br>"
                
                if 'weight' in item_data:
                    weight = item_data['weight']
                    total_weight = weight * item_data.get('quantity', 1)
                    details += f"• <b>Ağırlık:</b> {weight} lb (Toplam: {total_weight} lb)<br>"
                
                if 'quantity' in item_data:
                    details += f"• <b>Miktar:</b> {item_data['quantity']}<br>"
                
                details += "<br>"
                
                # Eşya tipine göre özel bilgiler
                if item_type == 'weapon':
                    details += "<b>⚔️ Silah Bilgileri:</b><br>"
                    
                    if 'damage' in item_data:
                        details += f"• <b>Hasar:</b> {item_data['damage']}<br>"
                    
                    if 'versatile_damage' in item_data and item_data['versatile_damage']:
                        details += f"• <b>Çok Amaçlı Hasar:</b> {item_data['versatile_damage']}<br>"
                    
                    if 'weapon_type' in item_data:
                        weapon_type_tr = {"melee": "Yakın Dövüş", "ranged": "Uzak Dövüş"}
                        details += f"• <b>Tür:</b> {weapon_type_tr.get(item_data['weapon_type'], item_data['weapon_type'])}<br>"
                    
                    if 'range' in item_data and item_data['range']:
                        details += f"• <b>Menzil:</b> {item_data['range']}<br>"
                    
                    if 'thrown' in item_data:
                        thrown_tr = "Evet" if item_data['thrown'] else "Hayır"
                        details += f"• <b>Fırlatılabilir:</b> {thrown_tr}<br>"
                    
                    if 'properties' in item_data and item_data['properties']:
                        properties = item_data['properties']
                        if isinstance(properties, list):
                            properties_tr = {
                                "Light": "Hafif", "Heavy": "Ağır", "Finesse": "Çeviklik", 
                                "Two-handed": "İki Elle", "Versatile": "Çok Amaçlı",
                                "Ammunition": "Cephane", "Loading": "Yükleme",
                                "Reach": "Uzun Menzil", "Thrown": "Fırlatılabilir"
                            }
                            properties_display = [properties_tr.get(p, p) for p in properties]
                            details += f"• <b>Özellikler:</b> {', '.join(properties_display)}<br>"
                
                elif item_type == 'armor':
                    details += "<b>🛡️ Zırh Bilgileri:</b><br>"
                    
                    if 'ac' in item_data:
                        details += f"• <b>Zırh Sınıfı:</b> {item_data['ac']}<br>"
                    
                    if 'armor_type' in item_data:
                        armor_type_tr = {
                            "light": "Hafif Zırh", "medium": "Orta Zırh", 
                            "heavy": "Ağır Zırh", "shield": "Kalkan"
                        }
                        details += f"• <b>Zırh Türü:</b> {armor_type_tr.get(item_data['armor_type'], item_data['armor_type'])}<br>"
                    
                    if 'max_dex' in item_data and item_data['max_dex'] is not None:
                        details += f"• <b>Maksimum Çeviklik Bonusu:</b> +{item_data['max_dex']}<br>"
                    
                    if 'stealth_disadvantage' in item_data:
                        stealth_tr = "Evet" if item_data['stealth_disadvantage'] else "Hayır"
                        details += f"• <b>Gizlilik Dezavantajı:</b> {stealth_tr}<br>"
                
                else:  # gear/macera eşyası
                    details += "<b>🎒 Macera Eşyası Bilgileri:</b><br>"
                    
                    if 'description' in item_data:
                        details += f"• <b>Açıklama:</b> {item_data['description']}<br>"
                    
                    if 'type' in item_data and item_data['type'] != 'gear':
                        details += f"• <b>Tür:</b> {item_data['type']}<br>"
                
                # Ek bilgiler
                details += "<br><b>📝 Notlar:</b><br>"
                details += "• Eşya karakterinizin envanterinde bulunmaktadır<br>"
                details += "• Eşyayı çıkarmak için 'Eşya Çıkar' butonunu kullanın<br>"
                details += "• Miktarını değiştirmek için eşyayı yeniden ekleyin"
                
                self.item_details_text.setHtml(details)
            
        except Exception as e:
            print(f"Eşya detayları gösterilemedi: {e}")

    def _remove_item(self):
        """Seçili eşyayı çıkar"""
        try:
            current_item = self.inventory_list.currentItem()
            if not current_item:
                QMessageBox.warning(self, "Uyarı", "Çıkarmak için bir eşya seçin!")
                return
            
            if not hasattr(self, 'current_character_file') or not self.current_character_file:
                QMessageBox.warning(self, "Uyarı", "Lütfen önce bir karakter oluşturun!")
                return
                
            filepath = self.current_character_file
            
            # Onay dialog'u
            reply = QMessageBox.question(self, "Eşya Çıkar", 
                "Bu eşyayı envanterden çıkarmak istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply != QMessageBox.Yes:
                return
            
            # Karakter dosyasını güncelle
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
                
            QMessageBox.information(self, "Başarılı", f"{removed_item.get('name', 'Eşya')} çıkarıldı!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Eşya çıkarılamadı:\n{str(e)}")

    def _init_advanced_ui(self):
        """Gelişmiş özellikler UI'sını oluştur (opsiyonel)"""
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
        
        # Başlık ve açıklama
        title_label = QLabel("⚙️ Gelişmiş Özellikler")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel(
            "Bu sekme tamamen opsiyonel özellikler içerir.\n"
            "Normal karakter oluşturma için bu özelliklere ihtiyacınız yoktur."
        )
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Kural Kitabı Yükleme Grubu
        rules_group = QGroupBox("📚 Kural Kitabı Yükleme (Opsiyonel)")
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
            "Kural kitabınızı (PDF veya TXT formatında) yükleyerek, "
            "hesaplamaların otomatik olarak bu kurallara göre yapılmasını sağlayabilirsiniz.\n\n"
            "Bu özellik opsiyoneldir. Kural yüklemezseniz, varsayılan hesaplamalar kullanılır."
        )
        rules_info.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 10px;")
        rules_info.setWordWrap(True)
        rules_layout.addWidget(rules_info)
        
        # Kural yükleme butonu
        load_rules_btn = QPushButton("📄 Kural Kitabı Yükle (PDF/TXT)")
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
        load_rules_btn.setToolTip("Kural kitabından kuralları yükle (PDF/TXT)")
        rules_layout.addWidget(load_rules_btn)
        
        # Kural düzenleme butonu
        edit_rules_btn = QPushButton("✏️ Kural Düzenle")
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
        edit_rules_btn.setToolTip("Yüklenen kuralları düzenle (JSON formatında)")
        rules_layout.addWidget(edit_rules_btn)
        
        # Kural önizleme butonu
        preview_rules_btn = QPushButton("👁️ Kuralları Görüntüle")
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
        preview_rules_btn.setToolTip("Yüklenen kuralları okunabilir formatta görüntüle")
        rules_layout.addWidget(preview_rules_btn)
        
        # Versiyon yönetimi butonu
        version_btn = QPushButton("📦 Versiyon Yönetimi")
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
        version_btn.setToolTip("Kural versiyonlarını görüntüle, geri yükle veya sil")
        rules_layout.addWidget(version_btn)
        
        # NLP durumu
        nlp_status = get_nlp_status()
        if nlp_status["available"]:
            nlp_info = QLabel("🤖 NLP: Aktif (spaCy model yüklü)")
            nlp_info.setStyleSheet("font-size: 10px; color: #27ae60; padding: 3px;")
        else:
            nlp_info = QLabel("🤖 NLP: Devre dışı (spaCy modeli yüklenmemiş)")
            nlp_info.setStyleSheet("font-size: 10px; color: #95a5a6; padding: 3px;")
        nlp_info.setToolTip(
            "NLP (Doğal Dil İşleme) ile daha gelişmiş kural çıkarma yapılabilir.\n"
            "Kurulum: pip install spacy && python -m spacy download en_core_web_sm"
        )
        rules_layout.addWidget(nlp_info)
        
        # Mevcut kural durumu
        self.rules_status_label = QLabel("Durum: Kural yüklenmedi")
        self.rules_status_label.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
        rules_layout.addWidget(self.rules_status_label)
        
        # Kural durumunu kontrol et
        self._update_rules_status()
        
        layout.addWidget(rules_group)
        layout.addStretch()

    def _update_rules_status(self):
        """Kural durumunu güncelle"""
        if not hasattr(self, 'rules_status_label'):
            return
        
        rules = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
        if rules and rules.get('rules'):
            self.rules_status_label.setText("✅ Durum: Kural yüklü - Hesaplamalar özel kurallara göre yapılıyor")
            self.rules_status_label.setStyleSheet("font-size: 11px; color: #27ae60; padding: 5px;")
        else:
            self.rules_status_label.setText("ℹ️ Durum: Kural yüklenmedi - Varsayılan hesaplamalar kullanılıyor")
            self.rules_status_label.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
    
    def _load_rules_from_file(self):
        """Kural kitabından kuralları yükle (D&D 5e)"""
        file_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Kural Kitabı Yükle (PDF/TXT)",
            str(APP_BASE_DIR),
            "Dosyalar (*.pdf *.txt);;PDF Dosyaları (*.pdf);;Metin Dosyaları (*.txt)"
        )
        if not file_path_str:
            return

        file_path = Path(file_path_str)

        use_nlp = False
        if is_nlp_available():
            reply = QMessageBox.question(
                self,
                "NLP Kullanımı",
                "Gelişmiş NLP (Doğal Dil İşleme) ile kural çıkarma kullanılsın mı?\n\n"
                "NLP daha karmaşık kuralları çıkarabilir ama daha yavaş olabilir.\n\n"
                "Evet: NLP kullan (önerilir)\n"
                "Hayır: Standart pattern matching kullan",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            use_nlp = (reply == QMessageBox.Yes)
        elif NLP_MODULE_AVAILABLE:
            QMessageBox.information(
                self,
                "NLP Bilgisi",
                "NLP modülü mevcut ancak spaCy modeli yüklenmemiş.\n\n"
                "NLP kullanmak için:\n"
                "1. pip install spacy\n"
                "2. python -m spacy download en_core_web_sm\n\n"
                "Standart pattern matching kullanılacak."
            )

        try:
            rules = extract_rules_from_file(file_path, self.SYSTEM_NAME, use_nlp=use_nlp)
            if not rules or not rules.get("rules"):
                QMessageBox.warning(
                    self,
                    "Uyarı",
                    "Dosyadan kural çıkarılamadı.\n"
                    "Lütfen dosyanın doğru formatta olduğundan emin olun."
                )
                return

            is_valid, issues = validate_rules(rules)
            if issues:
                report = format_validation_report(issues)
                reply = QMessageBox.question(
                    self,
                    "Kural Doğrulama",
                    f"Kurallarda sorunlar bulundu:\n\n{report[:200]}...\n\n"
                    "Yine de kaydetmek istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return

                if not is_valid:
                    detail_msg = QMessageBox(self)
                    detail_msg.setWindowTitle("Kural Doğrulama Detayları")
                    detail_msg.setText("Kurallarda kritik hatalar bulundu. Detaylar:")
                    detail_msg.setDetailedText(report)
                    detail_msg.setIcon(QMessageBox.Warning)
                    detail_msg.exec()

            saved_path = save_rules(rules, APP_BASE_DIR, self.SYSTEM_NAME)

            rules_text = json.dumps(rules, ensure_ascii=False, indent=2)
            msg = QMessageBox(self)
            msg.setWindowTitle("Kurallar Yüklendi")
            msg.setText(f"Kurallar başarıyla çıkarıldı ve kaydedildi:\n{saved_path}")
            msg.setDetailedText(rules_text)
            msg.setIcon(QMessageBox.Information)
            msg.exec()

            QMessageBox.information(
                self,
                "Başarılı",
                f"Kurallar yüklendi!\n{saved_path}\n\n"
                "Artık hesaplamalar bu kurallara göre yapılacak."
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
                f"PDF okuma için gerekli kütüphane eksik:\n{str(e)}\n\n"
                "Lütfen 'pip install PyPDF2' ile yükleyin."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Kural yükleme hatası:\n{str(e)}"
            )
    
    def _edit_rules(self):
        """Kural düzenleme diyaloğunu aç"""
        dialog = RuleEditorDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle
            self._rules_cache = None
            # Durumu güncelle
            self._update_rules_status()
    
    def _preview_rules(self):
        """Kural önizleme diyaloğunu aç"""
        dialog = RulePreviewDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        dialog.exec()
    
    def _manage_versions(self):
        """Kural versiyon yönetimi diyaloğunu aç"""
        dialog = RuleVersionDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle (versiyon geri yüklendiyse)
            self._rules_cache = None
            # Durumu güncelle
            self._update_rules_status()

    def _init_dice_ui(self):
        """Dice Roller UI'sını oluştur"""
        layout = self.dice_layout
        
        # Başlık
        title_label = QLabel("🎲 Dice Roller")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 20px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        # Ana splitter
        main_splitter = QtWidgets.QSplitter(Qt.Horizontal)
        layout.addWidget(main_splitter)
        
        # Sol panel - Dice roller
        left_panel = QWidget()
        left_layout = QVBoxLayout(left_panel)
        
        # Hızlı roll'lar
        quick_group = QGroupBox("Hızlı Roll'lar")
        quick_layout = QVBoxLayout()
        
        # D20 roll'ları
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
        
        # Özel roll
        custom_group = QGroupBox("Özel Roll")
        custom_layout = QVBoxLayout()
        
        custom_input_layout = QHBoxLayout()
        custom_input_layout.addWidget(QLabel("Roll:"))
        
        self.custom_dice_input = QLineEdit()
        self.custom_dice_input.setPlaceholderText("Örnek: 3d6+2, 2d20, 1d100")
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
        
        # Kayıtlı profiller
        profiles_group = QGroupBox("Kayıtlı Profiller")
        profiles_layout = QVBoxLayout()
        
        # Profil ekleme
        profile_input_layout = QHBoxLayout()
        profile_input_layout.addWidget(QLabel("Profil Adı:"))
        
        self.profile_name_input = QLineEdit()
        self.profile_name_input.setPlaceholderText("Örnek: Saldırı")
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
        
        # Profil butonları
        profile_buttons_layout = QHBoxLayout()
        
        roll_profile_btn = QPushButton("Seçili Profili Roll Et")
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
        
        # Sağ panel - Sonuçlar
        right_panel = QWidget()
        right_layout = QVBoxLayout(right_panel)
        
        results_group = QGroupBox("Roll Sonuçları")
        results_layout = QVBoxLayout()
        
        self.dice_results_text = QTextEdit()
        self.dice_results_text.setReadOnly(True)
        self.dice_results_text.setMaximumHeight(300)
        results_layout.addWidget(self.dice_results_text)
        
        clear_btn = QPushButton("Sonuçları Temizle")
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
        
        self.dice_results_text.append(f"[{timestamp}] 🎲 d{sides}: {result}")
        
        # Eğer 20 ise özel mesaj
        if sides == 20:
            if result == 20:
                self.dice_results_text.append("  🎉 NATURAL 20! CRITICAL SUCCESS!")
            elif result == 1:
                self.dice_results_text.append("  💀 NATURAL 1! CRITICAL FAILURE!")
        
        # d100 için özel mesaj
        elif sides == 100:
            if result <= 5:
                self.dice_results_text.append("  🎯 Kritik Başarı!")
            elif result >= 95:
                self.dice_results_text.append("  💥 Kritik Başarısızlık!")
        
        self.dice_results_text.append("")

    def _roll_custom_dice(self):
        """Özel dice roll (örn: 3d6+2)"""
        try:
            import random
            import re
            
            roll_text = self.custom_dice_input.text().strip()
            if not roll_text:
                QMessageBox.warning(self, "Uyarı", "Lütfen roll formatı girin! (Örnek: 3d6+2)")
                return
            
            # Roll formatını parse et (basit regex)
            # Örnek: 3d6+2, 2d20, 1d100-1
            pattern = r'(\d+)d(\d+)([+-]\d+)?'
            match = re.match(pattern, roll_text.lower())
            
            if not match:
                QMessageBox.warning(self, "Hata", "Geçersiz roll formatı! Örnek: 3d6+2")
                return
            
            num_dice = int(match.group(1))
            sides = int(match.group(2))
            modifier = int(match.group(3)) if match.group(3) else 0
            
            if num_dice > 20:
                QMessageBox.warning(self, "Uyarı", "Maksimum 20 zar atabilirsiniz!")
                return
                
            if sides > 100:
                QMessageBox.warning(self, "Uyarı", "Maksimum 100 yüzlü zar kullanabilirsiniz!")
                return
            
            # Zar at
            results = []
            for _ in range(num_dice):
                results.append(random.randint(1, sides))
            
            total = sum(results) + modifier
            
            # Sonucu göster
            from datetime import datetime
            timestamp = datetime.now().strftime("%H:%M:%S")
            result_text = f"[{timestamp}] 🎲 {roll_text}: "
            
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
            QMessageBox.critical(self, "Hata", f"Dice roll hatası:\n{str(e)}")

    def _clear_dice_results(self):
        """Dice roll sonuçlarını temizle"""
        self.dice_results_text.clear()

    def _roll_advantage(self):
        """Advantage roll (2d20, en yükseğini al)"""
        import random
        from datetime import datetime
        
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        result = max(roll1, roll2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.dice_results_text.append(f"[{timestamp}] 🎯 Advantage: {roll1}, {roll2} → {result}")
        
        if result == 20:
            self.dice_results_text.append("  🎉 NATURAL 20! CRITICAL SUCCESS!")
        elif result == 1:
            self.dice_results_text.append("  💀 NATURAL 1! CRITICAL FAILURE!")
        
        self.dice_results_text.append("")

    def _roll_disadvantage(self):
        """Disadvantage roll (2d20, en düşüğünü al)"""
        import random
        from datetime import datetime
        
        roll1 = random.randint(1, 20)
        roll2 = random.randint(1, 20)
        result = min(roll1, roll2)
        timestamp = datetime.now().strftime("%H:%M:%S")
        
        self.dice_results_text.append(f"[{timestamp}] ⚠️ Disadvantage: {roll1}, {roll2} → {result}")
        
        if result == 20:
            self.dice_results_text.append("  🎉 NATURAL 20! CRITICAL SUCCESS!")
        elif result == 1:
            self.dice_results_text.append("  💀 NATURAL 1! CRITICAL FAILURE!")
        
        self.dice_results_text.append("")

    def _add_dice_profile(self):
        """Dice profili ekle"""
        try:
            profile_name = self.profile_name_input.text().strip()
            profile_roll = self.profile_roll_input.text().strip()
            
            if not profile_name or not profile_roll:
                QMessageBox.warning(self, "Uyarı", "Lütfen profil adı ve roll formatını girin!")
                return
            
            # Roll formatını kontrol et
            import re
            pattern = r'(\d+)d(\d+)([+-]\d+)?'
            match = re.match(pattern, profile_roll.lower())
            
            if not match:
                QMessageBox.warning(self, "Hata", "Geçersiz roll formatı! Örnek: 1d20+5")
                return
            
            # Profili ekle
            profile_text = f"{profile_name}: {profile_roll}"
            self.profiles_list.addItem(profile_text)
            
            # Input'ları temizle
            self.profile_name_input.clear()
            self.profile_roll_input.clear()
            
            QMessageBox.information(self, "Başarılı", f"Profil '{profile_name}' eklendi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Profil eklenirken hata oluştu:\n{str(e)}")

    def _roll_selected_profile(self):
        """Seçili profili roll et"""
        try:
            selected_item = self.profiles_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Uyarı", "Lütfen roll etmek için bir profil seçin!")
                return
            
            profile_text = selected_item.text()
            profile_name, profile_roll = profile_text.split(": ", 1)
            
            # Roll'u çalıştır
            self.custom_dice_input.setText(profile_roll)
            self._roll_custom_dice()
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Profil roll edilirken hata oluştu:\n{str(e)}")

    def _remove_dice_profile(self):
        """Seçili profili sil"""
        try:
            selected_item = self.profiles_list.currentItem()
            if not selected_item:
                QMessageBox.warning(self, "Uyarı", "Lütfen silmek için bir profil seçin!")
                return
            
            profile_text = selected_item.text()
            profile_name = profile_text.split(": ", 1)[0]
            
            # Onay dialog'u
            reply = QMessageBox.question(self, "Profil Sil", 
                f"'{profile_name}' profilini silmek istediğinizden emin misiniz?",
                QMessageBox.Yes | QMessageBox.No)
            
            if reply == QMessageBox.Yes:
                self.profiles_list.takeItem(self.profiles_list.row(selected_item))
                QMessageBox.information(self, "Başarılı", f"Profil '{profile_name}' silindi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Profil silinirken hata oluştu:\n{str(e)}")

    def _show_race_info(self, race_name):
        """Irk bilgilerini göster"""
        if not race_name:
            return
            
        race_data = self.data.get("races", {}).get(race_name, {})
        if not race_data:
            return
            
        info_text = f"<h2>{race_name}</h2>"
        
        # Yetenek puanı artışları
        ability_increases = race_data.get("ability_score_increase", {})
        if ability_increases:
            info_text += "<h3>Yetenek Puanı Artışları:</h3><ul>"
            for ability, bonus in ability_increases.items():
                if ability == "all":
                    info_text += f"<li>Tüm yetenekler: +{bonus}</li>"
                else:
                    ability_names = {
                        "strength": "Güç", "dexterity": "Çeviklik", "constitution": "Dayanıklılık",
                        "intelligence": "Zeka", "wisdom": "Bilgelik", "charisma": "Karizma"
                    }
                    info_text += f"<li>{ability_names.get(ability, ability.title())}: +{bonus}</li>"
            info_text += "</ul>"
        
        # Hız
        speed = race_data.get("speed", {})
        if speed:
            info_text += f"<h3>Hız:</h3><p>{speed} fit</p>"
        
        # Irk özellikleri
        traits = race_data.get("traits", [])
        if traits:
            info_text += "<h3>Irk Özellikleri:</h3><ul>"
            for trait in traits:
                info_text += f"<li>{trait}</li>"
            info_text += "</ul>"
        
        self.info_text.setHtml(info_text)

    def _show_class_info(self, class_name):
        """Sınıf bilgilerini göster"""
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
                "strength": "Güç", "dexterity": "Çeviklik", "constitution": "Dayanıklılık",
                "intelligence": "Zeka", "wisdom": "Bilgelik", "charisma": "Karizma"
            }
            abilities = [ability_names.get(ab, ab.title()) for ab in primary_ability]
            info_text += f"<h3>Ana Yetenek:</h3><p>{', '.join(abilities)}</p>"
        
        # Skills
        skills = class_data.get("skills", [])
        if skills:
            info_text += f"<h3>Sınıf Becerileri:</h3><p>{', '.join(skills)}</p>"
        
        self.info_text.setHtml(info_text)

    def _show_background_info(self, background_name):
        """Arka plan bilgilerini göster"""
        if not background_name:
            return
            
        background_data = self.data.get("backgrounds", {}).get(background_name, {})
        if not background_data:
            return
            
        info_text = f"<h2>{background_name}</h2>"
        
        # Skills
        skills = background_data.get("skills", [])
        if skills:
            info_text += f"<h3>Beceri Yeterliliği:</h3><p>{', '.join(skills)}</p>"
        
        # Feature
        feature = background_data.get("feature", "")
        if feature:
            info_text += f"<h3>Özellik:</h3><p>{feature}</p>"
        
        self.info_text.setHtml(info_text)

    def _update_ability_scores(self, race_name):
        """Irk seçimi değiştiğinde yetenek puanlarını güncelle"""
        if not race_name or not hasattr(self, 'ability_spins'):
            return
            
        race_data = self.data.get("races", {}).get(race_name, {})
        if not race_data:
            return
            
        ability_increases = race_data.get("ability_score_increase", {}) or {}
        
        # Önce bir önceki ırk bonuslarını geri al
        prev_bonus = getattr(self, "_current_race_bonus", {}) or {}
        for ability, bonus in prev_bonus.items():
            if ability == "all":
                for _, spin in self.ability_spins.items():
                    spin.setValue(max(spin.minimum(), spin.value() - bonus))
            else:
                if ability in self.ability_spins:
                    spin = self.ability_spins[ability]
                    spin.setValue(max(spin.minimum(), spin.value() - bonus))
        
        # Yeni ırk bonuslarını uygula
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
        
        # İstatistikleri güncelle
        self._update_character_stats()

    def _update_character_stats(self):
        """Karakter istatistiklerini güncelle"""
        try:
            # Yetenek puanlarını al
            abilities = {}
            for ability, spin in self.ability_spins.items():
                abilities[ability] = spin.value()
            
            # Yetenek modifierlarını hesapla ve güncelle
            for ability, score in abilities.items():
                modifier = (score - 10) // 2
                modifier_text = f"{modifier:+d}" if modifier >= 0 else f"{modifier:d}"
                
                # Ability key'ini küçük harfe çevir
                ability_key = ability.lower()
                if ability_key in self.ability_mod_labels:
                    self.ability_mod_labels[ability_key].setText(modifier_text)
                
                # Renk kodlaması
                if modifier >= 2:
                    color = "#27ae60"  # Yeşil
                elif modifier >= 0:
                    color = "#3498db"  # Mavi
                elif modifier >= -2:
                    color = "#f39c12"  # Turuncu
                else:
                    color = "#e74c3c"  # Kırmızı
                
                if ability_key in self.ability_mod_labels:
                    self.ability_mod_labels[ability_key].setStyleSheet(f"font-weight: bold; color: {color}; font-size: 12px;")
            
            # AC hesaplama (zırh bazlı) - Dinamik kural desteği
            if hasattr(self, 'current_character') and self.current_character:
                # Önce yüklenen kuralları kontrol et
                if self._rules_cache is None:
                    self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
                ac = calculate_dynamic_armor_class(self.current_character, self._rules_cache, self.data)
            else:
                # Karakter henüz oluşturulmamışsa basit hesaplama
                dex_modifier = (abilities.get("Dexterity", 10) - 10) // 2
                ac = 10 + dex_modifier
            self.ac_label.setText(str(ac))
            self.ac_label.setToolTip(f"Armor Class: {ac}")
            
            # HP hesaplama (seviyeye göre) - Dinamik kural desteği
            if hasattr(self, 'current_character') and self.current_character:
                # Önce yüklenen kuralları kontrol et
                if self._rules_cache is None:
                    self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
                hp = calculate_dynamic_hit_points(self.current_character, self._rules_cache, self.data)
            else:
                # Karakter henüz oluşturulmamışsa basit hesaplama
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
            
            # Proficiency Bonus hesaplama (seviyeye göre) - Dinamik kural desteği
            level = self.current_character.get("level", 1) if hasattr(self, 'current_character') and self.current_character else 1
            # Önce yüklenen kuralları kontrol et
            if self._rules_cache is None:
                self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            prof_bonus = calculate_dynamic_proficiency_bonus(level, self._rules_cache)
            self.prof_bonus_label.setText(f"+{prof_bonus}")
            
            # Skill modifierları hesaplama
            skill_abilities = {
                "acrobatics": "dexterity", "animal_handling": "wisdom", "arcana": "intelligence",
                "athletics": "strength", "deception": "charisma", "history": "intelligence",
                "insight": "wisdom", "intimidation": "charisma", "investigation": "intelligence",
                "medicine": "wisdom", "nature": "intelligence", "perception": "wisdom",
                "performance": "charisma", "persuasion": "charisma", "religion": "intelligence",
                "sleight_of_hand": "dexterity", "stealth": "dexterity", "survival": "wisdom"
            }
            
            # Seçilen sınıf becerilerini al (eğer karakter oluşturma aşamasındaysa)
            if hasattr(self, 'current_character') and self.current_character:
                class_skills = self.current_character.get("skills", {}).get("class_skills", [])
            else:
                # Eğer henüz karakter oluşturulmamışsa, seçilen becerileri al
                selected_skills = [item.text() for item in self.wiz_skills.selectedItems()]
                class_skills = selected_skills
            
            for skill, ability in skill_abilities.items():
                # Ability key'ini büyük harfle başlayacak şekilde düzelt
                ability_key = ability.title()
                ability_modifier = (abilities.get(ability_key, 10) - 10) // 2
                
                # Proficiency bonus ekle (eğer sınıf becerisi ise)
                if skill in class_skills:
                    skill_modifier = ability_modifier + prof_bonus
                    modifier_text = f"{skill_modifier:+d}"
                    color = "#27ae60"  # Yeşil - proficient
                else:
                    skill_modifier = ability_modifier
                    modifier_text = f"{skill_modifier:+d}"
                    color = "#7f8c8d"  # Gri - not proficient
                
                self.skill_mod_labels[skill].setText(modifier_text)
                self.skill_mod_labels[skill].setStyleSheet(f"font-size: 11px; color: {color};")
                
        except Exception as e:
            print(f"İstatistik güncelleme hatası: {e}")

    def _update_spells_list(self):
        """Büyü listesini güncelle"""
        if hasattr(self, 'current_character') and self.current_character:
            self.spells_character_combo.clear()
            char_name = f"{self.current_character['name']} (Seviye {self.current_character['level']})"
            self.spells_character_combo.addItem(char_name)
            
            # Büyü kullanım kontrolü
            char_class = self.current_character.get("class", "")
            spellcasting_classes = ["Wizard", "Sorcerer", "Warlock", "Cleric", "Druid", "Bard", "Paladin", "Ranger", "Artificer"]
            
            if char_class in spellcasting_classes:
                self.spellcasting_check_label.setText(f"✅ {char_class} büyü kullanabilir")
                self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #27ae60;")
                self.spell_selection_group.setVisible(True)
                self._refresh_available_spells_for_selection()
            else:
                self.spellcasting_check_label.setText(f"❌ {char_class} büyü kullanamaz")
                self.spellcasting_check_label.setStyleSheet("font-weight: bold; color: #e74c3c;")
                self.spell_selection_group.setVisible(False)
            
            # Mevcut büyüleri listele
            self.spells_list.clear()
            spells = self.current_character.get("spells", {})
            
            # Tüm büyü seviyelerini kontrol et
            for spell_type, spell_list in spells.items():
                if spell_list:
                    if spell_type == "cantrips":
                        self.spells_list.addItem("=== CANTRIPS ===")
                    else:
                        level_num = spell_type.replace("level_", "")
                        self.spells_list.addItem(f"=== {level_num}. SEVİYE BÜYÜLER ===")
                    
                    for spell in spell_list:
                        self.spells_list.addItem(f"• {spell}")

    def _on_spell_level_changed(self, spell_level):
        """Büyü seviye seçimi değiştiğinde büyü listesini güncelle"""
        self._refresh_available_spells_for_selection()

    def _refresh_available_spells_for_selection(self):
        """Seçilebilir büyüleri güncelle"""
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
            
            # Sınıf büyülerini al
            class_spells = class_data.get("spells", {}).get(spell_key, [])
            
            for spell_name in class_spells:
                # Eğer büyü zaten biliniyorsa atla
                if spell_name not in current_spells.get(spell_key, []):
                    spell_data = self.data.get("spells", {}).get(spell_name, {})
                    spell_text = f"{spell_name}"
                    if spell_data.get("description"):
                        spell_text += f" - {spell_data['description'][:50]}..."
                    self.available_spells_for_selection.addItem(spell_text)
                    
        except Exception as e:
            print(f"Büyü listesi güncellenirken hata: {e}")

    def _add_spell_to_character(self):
        """Seçili büyüyü karaktere ekle"""
        try:
            if not hasattr(self, 'current_character') or not self.current_character:
                QMessageBox.warning(self, "Uyarı", "Önce bir karakter oluşturun!")
                return
            
            selected_spell = self.available_spells_for_selection.currentItem()
            if not selected_spell:
                QMessageBox.warning(self, "Uyarı", "Lütfen eklemek istediğiniz büyüyü seçin!")
                return
            
            spell_name = selected_spell.text().split(" - ")[0]
            spell_level = self.spell_level_combo.currentText()
            
            if spell_level == "Cantrip":
                spell_key = "cantrips"
            else:
                level_num = int(spell_level.split()[0])
                spell_key = f"level_{level_num}"
            
            # Büyüyü karaktere ekle
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
            
            # Listeleri güncelle
            self._update_spells_list()
            
            QMessageBox.information(self, "Başarılı", f"{spell_name} büyüsü eklendi!")
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Büyü eklenirken hata oluştu:\n{str(e)}")

    def _show_spell_details(self, item):
        """Büyü detaylarını göster"""
        spell_name = item.text()
        if spell_name.startswith("===") or spell_name.startswith("• "):
            return
            
        # Büyü bilgilerini bul
        spell_data = self.data.get("spells", {}).get(spell_name, {})
        if spell_data:
            info_text = f"<h3>{spell_name}</h3>"
            info_text += f"<p><b>Seviye:</b> {spell_data.get('level', 'Bilinmiyor')}</p>"
            info_text += f"<p><b>Süre:</b> {spell_data.get('duration', 'Bilinmiyor')}</p>"
            info_text += f"<p><b>Menzil:</b> {spell_data.get('range', 'Bilinmiyor')}</p>"
            info_text += f"<p><b>Açıklama:</b> {spell_data.get('description', 'Açıklama bulunamadı')}</p>"
            self.spell_info.setHtml(info_text)
        else:
            self.spell_info.setPlainText(f"{spell_name} için detay bulunamadı.")

    def _add_spell_dialog(self):
        """Büyü ekleme dialog'u"""
        if not hasattr(self, 'current_character') or not self.current_character:
            QMessageBox.warning(self, "Uyarı", "Önce bir karakter oluşturun!")
            return
            
        # Mevcut büyüleri al (equipment altında)
        equipment = self.data.get("equipment", {})
        all_spells = list(equipment.get("spells", {}).keys())
        if not all_spells:
            QMessageBox.information(self, "Bilgi", "Büyü listesi bulunamadı.")
            return
            
        # Dialog ile büyü seç
        spell_name, ok = QInputDialog.getItem(self, "Büyü Ekle", "Eklemek istediğiniz büyüyü seçin:", all_spells, 0, False)
        if ok and spell_name:
            # Büyüyü karaktere ekle
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
            
            # Listeyi güncelle
            self._update_spells_list()
            QMessageBox.information(self, "Başarılı", f"{spell_name} büyüsü eklendi!")

    def _remove_spell(self):
        """Seçili büyüyü kaldır"""
        current_item = self.spells_list.currentItem()
        if not current_item:
            QMessageBox.warning(self, "Uyarı", "Kaldırmak için bir büyü seçin!")
            return
            
        spell_text = current_item.text()
        if spell_text.startswith("===") or not spell_text.startswith("• "):
            QMessageBox.warning(self, "Uyarı", "Geçerli bir büyü seçin!")
            return
            
        spell_name = spell_text[2:]  # "• " kısmını kaldır
        
        # Büyüyü karakterden çıkar
        spells = self.current_character.get("spells", {})
        for level, spell_list in spells.items():
            if spell_name in spell_list:
                spell_list.remove(spell_name)
                break
        
        # Listeyi güncelle
        self._update_spells_list()
        QMessageBox.information(self, "Başarılı", f"{spell_name} büyüsü kaldırıldı!")

    def _export_to_pdf(self, character):
        """Karakteri PDF'e çevir"""
        self._auto_save_character()
        self._export_character(character, "PDF")
    
    def _export_character(self, character: dict, format_type: str = None):
        """Karakteri farklı formatlarda export et"""
        if not format_type:
            # Format seçimi diyaloğu
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
                f"{format_type} Dosyaları (*.{format_type.lower()})"
            )
            if file_path:
                self._perform_export(character, format_type, Path(file_path))
    
    def _perform_export(self, character: dict, format_type: str, file_path: Path):
        """Export işlemini gerçekleştir"""
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
                QMessageBox.warning(self, "Uyarı", f"Desteklenmeyen format: {format_type}")
                return
            
            QMessageBox.information(self, "Başarılı", f"Karakter {format_type} formatında kaydedildi:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Export sırasında hata oluştu:\n{str(e)}")


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

        # Header kısmı - Logo ve başlık
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #34495e; border-radius: 10px; margin: 5px;")
        header_widget.setMaximumHeight(140)  # Header maksimum yükseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Sol taraf için boş alan
        header_layout.addStretch()
        
        # Başlık (logo kaldırıldı)
        title = QLabel("Diyargezer - Mutants & Masterminds")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)  # Uzun metinler için kelime kaydırma
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addWidget(header_widget)

        layout.addWidget(self._build_toolbar())

        # Tab widget oluştur
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
        self.tab_widget.addTab(main_tab, "🎭 Karakter")
        
        # Gelişmiş sekmesi
        self.advanced_tab_mm = QWidget()
        self.advanced_layout_mm = QVBoxLayout(self.advanced_tab_mm)
        self._init_advanced_ui_mm()
        self.tab_widget.addTab(self.advanced_tab_mm, "⚙️ Gelişmiş")
        
        layout.addWidget(self.tab_widget)

        self._start_new_character()

    def _build_toolbar(self) -> QWidget:
        widget = QWidget()
        bar = QHBoxLayout(widget)
        bar.setContentsMargins(0, 0, 0, 0)

        new_btn = QPushButton("Yeni Karakter")
        new_btn.setIcon(QIcon.fromTheme("document-new"))
        new_btn.clicked.connect(self._start_new_character)

        load_btn = QPushButton("Karakter Yükle")
        load_btn.setIcon(QIcon.fromTheme("document-open"))
        load_btn.clicked.connect(self._load_character)
        
        browse_btn = QPushButton("📋 Karakterleri Listele")
        browse_btn.setToolTip("Tüm karakterleri görüntüle, ara ve filtrele")
        browse_btn.clicked.connect(self._browse_characters)
        
        template_btn = QPushButton("📝 Şablonlar")
        template_btn.setToolTip("Karakter şablonlarını yönet")
        template_btn.clicked.connect(self._manage_templates)
        
        version_btn = QPushButton("📜 Versiyonlar")
        version_btn.setToolTip("Karakter versiyon geçmişini görüntüle ve yönet")
        version_btn.clicked.connect(self._manage_versions)
        
        compare_btn = QPushButton("⚖️ Karşılaştır")
        compare_btn.setToolTip("İki karakteri karşılaştır")
        compare_btn.clicked.connect(self._compare_characters)

        save_btn = QPushButton("Kaydet")
        save_btn.setIcon(QIcon.fromTheme("document-save"))
        save_btn.clicked.connect(self._save_character)

        # SQLite butonları gizli (opsiyonel özellik)
        # sqlite_save_btn = QPushButton("SQLite Kaydet")
        # sqlite_save_btn.clicked.connect(self._save_to_sqlite)
        # sqlite_load_btn = QPushButton("SQLite Yükle")
        # sqlite_load_btn.clicked.connect(self._load_from_sqlite)

        pdf_btn = QPushButton("PDF Export")
        pdf_btn.clicked.connect(self._export_pdf)
        pdf_btn.setToolTip("Karakteri PDF olarak dışa aktar")

        batch_btn = QPushButton("📦 Toplu İşlemler")
        batch_btn.setToolTip("Birden fazla karakter üzerinde toplu işlem yap")
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

        form.addRow("Karakter Adı:", self.name_edit)
        form.addRow("Kod Adı:", self.codename_edit)
        form.addRow("Power Level:", self.pl_combo)
        form.addRow("Arketip:", self.archetype_combo)
        form.addRow("Arketip Özeti:", self.archetype_info)

        # Karakter resmi
        image_group = QGroupBox("🖼️ Karakter Resmi")
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
        self.mm_character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")
        self.mm_character_image_label.setWordWrap(True)
        image_layout.addWidget(self.mm_character_image_label)
        
        image_buttons_layout = QHBoxLayout()
        
        load_image_btn = QPushButton("📷 Resim Yükle")
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
        
        remove_image_btn = QPushButton("🗑️ Resmi Kaldır")
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
        self.powers_edit.setPlaceholderText("Her satıra bir power yazın...")
        self.powers_edit.textChanged.connect(self._refresh_summary)

        self.advantages_edit = QTextEdit()
        self.advantages_edit.setPlaceholderText("Her satıra bir advantage yazın...")
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
        self.notes_edit.setPlaceholderText("Karakter geçmişi, motivasyonları vb.")
        self.notes_edit.textChanged.connect(self._refresh_summary)
        layout.addWidget(self.notes_edit)
        return group

    def _build_summary_group(self) -> QWidget:
        group = QGroupBox("Özet")
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
        
        # Eğer mevcut dosya varsa versiyon oluştur
        if hasattr(self, 'current_character_file') and self.current_character_file:
            save_character_version(
                character,
                APP_BASE_DIR,
                self.current_character_file,
                "Manuel kayıt"
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
            "SQLite Veritabanı (*.db)"
        )
        if not db_path_str:
            return
        db_path = Path(db_path_str)
        init_db(db_path)
        record = CharacterRecord(
            id=None,
            system=self.SYSTEM_NAME,
            name=character.get("name") or "İsimsiz",
            data=character,
        )
        save_character(db_path, record)
        QMessageBox.information(self, "Başarılı", "Karakter SQLite veritabanına kaydedildi.")

    def _load_character(self):
        data, path = _load_character_via_dialog(self, "M&M Karakteri Yükle", self.SYSTEM_NAME)
        if not data:
            return
        self._apply_character(data)
        self.current_character = data
        self.current_character_file = path
        QMessageBox.information(self, "Başarılı", "Karakter formu yüklendi.")
    
    def _browse_characters(self):
        """Karakter listesi diyaloğunu aç (tüm sistemler)"""
        dialog = CharacterListDialog(self, None)  # Tüm sistemler
        dialog.setWindowTitle("Karakter Listesi - Tüm Sistemler")
        
        if dialog.exec() == QDialog.Accepted:
            data, path = dialog.get_selected_character()
            if not data:
                return
            
            # Sistem kontrolü ve ilgili sayfaya yönlendirme
            system = data.get("system")
            if system == "MUTANTS_AND_MASTERMINDS":
                self._apply_character(data)
                self.current_character = data
                self.current_character_file = path
                QMessageBox.information(self, "Başarılı", f"{data.get('name', 'Karakter')} yüklendi!")
            else:
                QMessageBox.information(
                    self,
                    "Bilgi",
                    f"Bu karakter {system} sistemine ait.\n"
                    f"Lütfen ilgili sistem sekmesinden yükleyin."
                )
    
    def _manage_templates(self):
        """Şablonlardan yeni M&M karakteri oluştur"""
        character, character_name = _select_template_character(self, self.SYSTEM_NAME)
        if not character:
            return
        
        self._apply_character(character)
        self.current_character = character
        self.current_character_file = None
        QMessageBox.information(
            self,
            "Şablon Kullanıldı",
            f"{character_name} şablonu yüklendi. Kaydetmek için 'Kaydet' butonunu kullanabilirsiniz."
        )
    
    def _compare_characters(self):
        """Karakter karşılaştırma diyaloğunu aç"""
        dialog = CharacterComparisonDialog(self, self.SYSTEM_NAME)
        dialog.exec()
    
    def _show_batch_operations(self):
        """Toplu işlemler için bilgilendirme"""
        QMessageBox.information(
            self,
            "Toplu İşlemler",
            "M&M için toplu işlemler desteği henüz bu sürümde aktif değil."
        )

    def _load_from_sqlite(self):
        db_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "SQLite'dan Yükle",
            str(APP_BASE_DIR / "characters"),
            "SQLite Veritabanı (*.db)"
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
                "Uyarı",
                f"Bu karakter {rec.system} sistemine ait. "
                f"Lütfen {self.SYSTEM_NAME} karakterlerini yükleyin."
            )
            return
        
        self._apply_character(rec.data)
        self.current_character = rec.data
        self.current_character_file = None
        QMessageBox.information(self, "Başarılı", f"{rec.name} yüklendi.")

    def _export_pdf(self):
        character = self._collect_character_data()
        if not character:
            return
        self._export_character(character)
    
    def _export_character(self, character: dict):
        """Karakteri farklı formatlarda export et"""
        dialog = ExportFormatDialog(self, character)
        if dialog.exec() == QDialog.Accepted:
            format_type, file_path = dialog.get_selected_format()
            if format_type and file_path:
                self._perform_export(character, format_type, Path(file_path))
    
    def _perform_export(self, character: dict, format_type: str, file_path: Path):
        """Export işlemini gerçekleştir"""
        try:
            system = character.get("system", "MUTANTS_AND_MASTERMINDS")
            
            if format_type == "PDF":
                # Arkaplan seçimi (opsiyonel - sadece PDF için)
                background_path = None
                use_bg = QMessageBox.question(
                    self,
                    "Arkaplan",
                    "PDF'e arkaplan görseli eklemek ister misiniz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if use_bg == QMessageBox.Yes:
                    bg_path_str, _ = QFileDialog.getOpenFileName(
                        self,
                        "Arkaplan Görseli Seç",
                        str(APP_BASE_DIR / "assets"),
                        "Görsel Dosyaları (*.png *.jpg *.jpeg)"
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
                QMessageBox.warning(self, "Uyarı", f"Desteklenmeyen format: {format_type}")
                return
            
            QMessageBox.information(self, "Başarılı", f"Karakter {format_type} formatında kaydedildi:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Export sırasında hata oluştu:\n{str(e)}")

    def _load_rules_from_file(self):
        """Kural kitabından kuralları yükle"""
        file_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Kural Kitabı Yükle (PDF/TXT)",
            str(APP_BASE_DIR),
            "Dosyalar (*.pdf *.txt);;PDF Dosyaları (*.pdf);;Metin Dosyaları (*.txt)"
        )
        if not file_path_str:
            return
        
        file_path = Path(file_path_str)
        
        # NLP kullanımını sor (eğer mevcut ise)
        use_nlp = False
        if is_nlp_available():
            reply = QMessageBox.question(
                self,
                "NLP Kullanımı",
                "Gelişmiş NLP (Doğal Dil İşleme) ile kural çıkarma kullanılsın mı?\n\n"
                "NLP daha karmaşık kuralları çıkarabilir ama daha yavaş olabilir.\n\n"
                "Evet: NLP kullan (önerilir)\n"
                "Hayır: Standart pattern matching kullan",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            use_nlp = (reply == QMessageBox.Yes)
        elif NLP_MODULE_AVAILABLE:
            # NLP modülü var ama model yüklenmemiş
            QMessageBox.information(
                self,
                "NLP Bilgisi",
                "NLP modülü mevcut ancak spaCy modeli yüklenmemiş.\n\n"
                "NLP kullanmak için:\n"
                "1. pip install spacy\n"
                "2. python -m spacy download en_core_web_sm\n\n"
                "Standart pattern matching kullanılacak."
            )
        
        try:
            # Kuralları çıkar
            rules = extract_rules_from_file(file_path, self.SYSTEM_NAME, use_nlp=use_nlp)
            
            if not rules or not rules.get('rules'):
                QMessageBox.warning(
                    self,
                    "Uyarı",
                    "Dosyadan kural çıkarılamadı.\n"
                    "Lütfen dosyanın doğru formatta olduğundan emin olun."
                )
                return
            
            # Kuralları doğrula
            is_valid, issues = validate_rules(rules)
            if issues:
                report = format_validation_report(issues)
                reply = QMessageBox.question(
                    self,
                    "Kural Doğrulama",
                    f"Kurallarda sorunlar bulundu:\n\n{report[:200]}...\n\n"
                    "Yine de kaydetmek istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
                
                # Detaylı rapor göster
                if not is_valid:
                    detail_msg = QMessageBox(self)
                    detail_msg.setWindowTitle("Kural Doğrulama Detayları")
                    detail_msg.setText("Kurallarda kritik hatalar bulundu. Detaylar:")
                    detail_msg.setDetailedText(report)
                    detail_msg.setIcon(QMessageBox.Warning)
                    detail_msg.exec()
            
            # Kuralları kaydet
            saved_path = save_rules(rules, APP_BASE_DIR, self.SYSTEM_NAME)
            
            # Çıkarılan kuralları göster
            rules_text = json.dumps(rules, ensure_ascii=False, indent=2)
            msg = QMessageBox(self)
            msg.setWindowTitle("Kurallar Yüklendi")
            msg.setText(f"Kurallar başarıyla çıkarıldı ve kaydedildi:\n{saved_path}")
            msg.setDetailedText(rules_text)
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"Kurallar yüklendi!\n{saved_path}\n\n"
                "Artık hesaplamalar bu kurallara göre yapılacak."
            )
            
            # Cache'i yenile
            self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            # İstatistikleri güncelle
            if hasattr(self, '_update_pl_limits'):
                self._update_pl_limits()
            
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"PDF okuma için gerekli kütüphane eksik:\n{str(e)}\n\n"
                "Lütfen 'pip install PyPDF2' ile yükleyin."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Kural yükleme hatası:\n{str(e)}"
            )

    def _collect_character_data(self) -> dict | None:
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "Uyarı", "Karakter adı zorunludur.")
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
        
        # Resmi yükle
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
            text += f"\nÖnerilen Powers: {suggested_powers}"
        if suggested_adv:
            text += f"\nÖnerilen Advantages: {suggested_adv}"
        self.archetype_info.setPlainText(text.strip())
        self._refresh_summary()
        self._update_pl_limits()

    def _update_pl_limits(self):
        pl_name = self.pl_combo.currentText()
        caps = self.data.get("power_levels", {}).get(pl_name, {})
        self.current_pl_caps = caps
        
        # Power Points otomatik hesaplama - Dinamik kural desteği
        try:
            pl_value = int(pl_name) if pl_name.isdigit() else 1
            # Önce yüklenen kuralları kontrol et
            if self._rules_cache is None:
                self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            calculated_pp = calculate_dynamic_power_points(pl_value, self._rules_cache)
            self.pp_spin.setValue(calculated_pp)
        except (ValueError, AttributeError):
            pass
        
        if caps:
            text = (
                f"PL {pl_name} Limitleri — "
                f"Attack/Effekt ≤ {caps.get('attack_bonus_cap', '-')} / {caps.get('effect_rank_cap', '-')}, "
                f"Defense/Toughness ≤ {caps.get('defense_cap', '-')} / {caps.get('toughness_cap', '-')}"
            )
        else:
            text = "PL limit bilgisi bulunamadı."
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
            self.pl_warning_label.setText("Limit aşıldı: " + ", ".join(warnings))
            self.pl_warning_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
        else:
            self.pl_warning_label.setText("Limitler dahilinde.")
            self.pl_warning_label.setStyleSheet("color: #27ae60; font-weight: bold;")

    def _load_character_image(self):
        """Karakter resmi yükle (MmPage)"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Karakter Resmi Seç",
            "",
            "Resim Dosyaları (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;Tüm Dosyalar (*)"
        )
        
        if file_path:
            try:
                image_path = Path(file_path)
                base64_str = _load_image_to_base64(image_path)
                
                if base64_str:
                    self.current_character_image_data = base64_str
                    
                    # Resmi göster
                    pixmap = QPixmap(str(image_path))
                    if not pixmap.isNull():
                        scaled_pixmap = pixmap.scaled(
                            300, 300,
                            Qt.KeepAspectRatio,
                            Qt.SmoothTransformation
                        )
                        self.mm_character_image_label.setPixmap(scaled_pixmap)
                        self.mm_character_image_label.setText("")
                    
                    # Karakter verisini güncelle
                    if hasattr(self, 'current_character') and self.current_character:
                        self.current_character["image"] = base64_str
                    
                    QMessageBox.information(self, "Başarılı", "Resim başarıyla yüklendi!")
                else:
                    QMessageBox.warning(self, "Hata", "Resim yüklenemedi.")
            except Exception as e:
                QMessageBox.critical(self, "Hata", f"Resim yüklenirken bir hata oluştu:\n{str(e)}")

    def _remove_character_image(self):
        """Karakter resmini kaldır (MmPage)"""
        reply = QMessageBox.question(
            self,
            "Resmi Kaldır",
            "Karakter resmini kaldırmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.current_character_image_data = None
            self.mm_character_image_label.clear()
            self.mm_character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")
            
            # Karakter verisinden kaldır
            if hasattr(self, 'current_character') and self.current_character:
                if "image" in self.current_character:
                    del self.current_character["image"]
            
            QMessageBox.information(self, "Başarılı", "Resim kaldırıldı.")

    def _load_character_image_to_gui(self, character: dict):
        """Karakter verisinden resmi GUI'ye yükle (MmPage)"""
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
                self.mm_character_image_label.setText("Resim yüklenemedi\n(Resim eklemek için butona tıklayın)")
        else:
            self.current_character_image_data = None
            self.mm_character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")

    def _refresh_summary(self):
        if not hasattr(self, "summary_text"):
            return

        name = self.name_edit.text().strip() or "İsimsiz"
        codename = self.codename_edit.text().strip()
        pl = self.pl_combo.currentText()
        archetype = self.archetype_combo.currentText()

        lines = [
            f"İsim: {name}",
            f"Kod Adı: {codename or '-'}",
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
        """Gelişmiş özellikler UI'sını oluştur (opsiyonel) - M&M"""
        layout = self.advanced_layout_mm
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık ve açıklama
        title_label = QLabel("⚙️ Gelişmiş Özellikler")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel(
            "Bu sekme tamamen opsiyonel özellikler içerir.\n"
            "Normal karakter oluşturma için bu özelliklere ihtiyacınız yoktur."
        )
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Kural Kitabı Yükleme Grubu
        rules_group = QGroupBox("📚 Kural Kitabı Yükleme (Opsiyonel)")
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
            "Kural kitabınızı (PDF veya TXT formatında) yükleyerek, "
            "hesaplamaların otomatik olarak bu kurallara göre yapılmasını sağlayabilirsiniz.\n\n"
            "Bu özellik opsiyoneldir. Kural yüklemezseniz, varsayılan hesaplamalar kullanılır."
        )
        rules_info.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 10px;")
        rules_info.setWordWrap(True)
        rules_layout.addWidget(rules_info)
        
        # Kural yükleme butonu
        load_rules_btn = QPushButton("📄 Kural Kitabı Yükle (PDF/TXT)")
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
        load_rules_btn.setToolTip("Kural kitabından kuralları yükle (PDF/TXT)")
        rules_layout.addWidget(load_rules_btn)
        
        # Kural düzenleme butonu
        edit_rules_btn = QPushButton("✏️ Kural Düzenle")
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
        edit_rules_btn.setToolTip("Yüklenen kuralları düzenle (JSON formatında)")
        rules_layout.addWidget(edit_rules_btn)
        
        # Kural önizleme butonu
        preview_rules_btn = QPushButton("👁️ Kuralları Görüntüle")
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
        preview_rules_btn.setToolTip("Yüklenen kuralları okunabilir formatta görüntüle")
        rules_layout.addWidget(preview_rules_btn)
        
        # Mevcut kural durumu
        self.rules_status_label_mm = QLabel("Durum: Kural yüklenmedi")
        self.rules_status_label_mm.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
        rules_layout.addWidget(self.rules_status_label_mm)
        
        # Kural durumunu kontrol et
        self._update_rules_status_mm()
        
        layout.addWidget(rules_group)
        layout.addStretch()

    def _update_rules_status_mm(self):
        """Kural durumunu güncelle - M&M"""
        if not hasattr(self, 'rules_status_label_mm'):
            return
        
        rules = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
        if rules and rules.get('rules'):
            self.rules_status_label_mm.setText("✅ Durum: Kural yüklü - Hesaplamalar özel kurallara göre yapılıyor")
            self.rules_status_label_mm.setStyleSheet("font-size: 11px; color: #27ae60; padding: 5px;")
        else:
            self.rules_status_label_mm.setText("ℹ️ Durum: Kural yüklenmedi - Varsayılan hesaplamalar kullanılıyor")
            self.rules_status_label_mm.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
    
    def _edit_rules(self):
        """Kural düzenleme diyaloğunu aç"""
        dialog = RuleEditorDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle
            self._rules_cache = None
            # Durumu güncelle
            self._update_rules_status_mm()
    
    def _preview_rules(self):
        """Kural önizleme diyaloğunu aç"""
        dialog = RulePreviewDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        dialog.exec()
    
    def _manage_versions(self):
        """Kural versiyon yönetimi diyaloğunu aç"""
        dialog = RuleVersionDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle (versiyon geri yüklendiyse)
            self._rules_cache = None
            # Durumu güncelle
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

        # Header kısmı - Logo ve başlık
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #34495e; border-radius: 10px; margin: 5px;")
        header_widget.setMaximumHeight(140)  # Header maksimum yükseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(10, 5, 10, 5)
        
        # Sol taraf için boş alan
        header_layout.addStretch()
        
        # Başlık (logo kaldırıldı)
        title = QLabel("Diyargezer - Vampire: The Masquerade")
        title.setStyleSheet("font-size: 24px; font-weight: bold; color: white; margin: 10px;")
        title.setAlignment(Qt.AlignCenter)
        title.setWordWrap(True)  # Uzun metinler için kelime kaydırma
        header_layout.addWidget(title)
        
        header_layout.addStretch()
        layout.addWidget(header_widget)

        layout.addWidget(self._build_toolbar())

        self.tab_widget = QTabWidget()
        self.tab_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.tab_widget.addTab(self._build_basic_tab(), "Temel Bilgiler")
        self.tab_widget.addTab(self._build_attributes_tab(), "Attributes")
        self.tab_widget.addTab(self._build_skills_tab(), "Skills & Disciplines")
        self.tab_widget.addTab(self._build_summary_tab(), "Özet")
        
        # Gelişmiş sekmesi
        self.advanced_tab_vtm = QWidget()
        self.advanced_layout_vtm = QVBoxLayout(self.advanced_tab_vtm)
        self._init_advanced_ui_vtm()
        self.tab_widget.addTab(self.advanced_tab_vtm, "⚙️ Gelişmiş")
        
        layout.addWidget(self.tab_widget)

        self._start_new_character()

    def _build_toolbar(self) -> QWidget:
        widget = QWidget()
        bar = QHBoxLayout(widget)
        bar.setContentsMargins(0, 0, 0, 0)

        new_btn = QPushButton("Yeni Karakter")
        new_btn.clicked.connect(self._start_new_character)

        load_btn = QPushButton("Karakter Yükle")
        load_btn.clicked.connect(self._load_character)
        
        browse_btn = QPushButton("📋 Karakterleri Listele")
        browse_btn.setToolTip("Tüm karakterleri görüntüle, ara ve filtrele")
        browse_btn.clicked.connect(self._browse_characters)
        
        template_btn = QPushButton("📝 Şablonlar")
        template_btn.setToolTip("Karakter şablonlarını yönet")
        template_btn.clicked.connect(self._manage_templates)
        
        version_btn = QPushButton("📜 Versiyonlar")
        version_btn.setToolTip("Karakter versiyon geçmişini görüntüle ve yönet")
        version_btn.clicked.connect(self._manage_versions)
        
        compare_btn = QPushButton("⚖️ Karşılaştır")
        compare_btn.setToolTip("İki karakteri karşılaştır")
        compare_btn.clicked.connect(self._compare_characters)

        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self._save_character)

        # SQLite butonları gizli (opsiyonel özellik)
        # sqlite_save_btn = QPushButton("SQLite Kaydet")
        # sqlite_save_btn.clicked.connect(self._save_to_sqlite)
        # sqlite_load_btn = QPushButton("SQLite Yükle")
        # sqlite_load_btn.clicked.connect(self._load_from_sqlite)

        pdf_btn = QPushButton("PDF Export")
        pdf_btn.clicked.connect(self._export_pdf)

        stats_btn = QPushButton("📊 İstatistikler")
        stats_btn.setToolTip("Karakter istatistikleri ve analiz")
        stats_btn.clicked.connect(self._show_statistics)
        
        batch_btn = QPushButton("📦 Toplu İşlemler")
        batch_btn.setToolTip("Birden fazla karakter üzerinde toplu işlem yap")
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
        """Karakter karşılaştırma diyaloğunu aç"""
        dialog = CharacterComparisonDialog(self, self.SYSTEM_NAME)
        dialog.exec()
    
    def _show_statistics(self):
        """İstatistik özeti için bilgilendirme"""
        QMessageBox.information(
            self,
            "İstatistikler",
            "VtM istatistik özeti henüz bu sürümde içinde değil."
        )
    
    def _manage_templates(self):
        """Şablonlardan yeni VtM karakteri oluştur"""
        character, character_name = _select_template_character(self, self.SYSTEM_NAME)
        if not character:
            return
        
        self._apply_character(character)
        self.current_character = character
        self.current_character_file = None
        QMessageBox.information(
            self,
            "Şablon Kullanıldı",
            f"{character_name} şablonu yüklendi. Kaydetmek için 'Kaydet' butonunu kullanabilirsiniz."
        )
    
    def _show_batch_operations(self):
        """Toplu işlemler için bilgilendirme"""
        QMessageBox.information(
            self,
            "Toplu İşlemler",
            "VtM için toplu işlemler desteği henüz bu sürümde aktif değil."
        )
    
    def _manage_versions(self):
        """Kural versiyon yönetimi diyaloğunu aç"""
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

        form.addRow("Karakter Adı:", self.vtm_name_edit)
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
        image_group = QGroupBox("🖼️ Karakter Resmi")
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
        self.vtm_character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")
        self.vtm_character_image_label.setWordWrap(True)
        image_layout.addWidget(self.vtm_character_image_label)
        
        image_buttons_layout = QHBoxLayout()
        
        load_image_btn = QPushButton("📷 Resim Yükle")
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
        
        remove_image_btn = QPushButton("🗑️ Resmi Kaldır")
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
        """VtM karakter resmi yükle"""
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Karakter Resmi Seç",
            "",
            "Resim Dosyaları (*.png *.jpg *.jpeg *.gif *.bmp *.webp);;Tüm Dosyalar (*)"
        )
        if not file_path:
            return

        try:
            image_path = Path(file_path)
            base64_str = _load_image_to_base64(image_path)
            if not base64_str:
                QMessageBox.warning(self, "Hata", "Resim yüklenemedi.")
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

            QMessageBox.information(self, "Başarılı", "Resim başarıyla yüklendi!")
        except Exception as exc:
            QMessageBox.critical(self, "Hata", f"Resim yüklenirken bir hata oluştu:\n{exc}")

    def _remove_character_image(self):
        """VtM karakter resmini kaldır"""
        reply = QMessageBox.question(
            self,
            "Resmi Kaldır",
            "Karakter resmini kaldırmak istediğinize emin misiniz?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        if reply != QMessageBox.Yes:
            return

        self.current_character_image_data = None
        self.vtm_character_image_label.clear()
        self.vtm_character_image_label.setText("Resim yok\n(Resim eklemek için butona tıklayın)")

        if self.current_character and "image" in self.current_character:
            del self.current_character["image"]
            self._auto_save_character()

        QMessageBox.information(self, "Başarılı", "Resim kaldırıldı.")

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
        self.extra_discipline_edit.setPlaceholderText("Virgülle ayrılmış ek disiplinler")
        self.extra_discipline_edit.textChanged.connect(self._refresh_summary)

        d_layout.addWidget(QLabel("Klan disiplinlerini işaretleyin:"))
        d_layout.addWidget(self.discipline_list)
        d_layout.addWidget(QLabel("Ek Disiplinler:"))
        d_layout.addWidget(self.extra_discipline_edit)

        layout.addWidget(disciplines_group, 2)

        return widget

    def _build_summary_tab(self) -> QWidget:
        widget = QWidget()
        layout = QVBoxLayout(widget)

        self.notes_edit_vtm = QTextEdit()
        self.notes_edit_vtm.setPlaceholderText("Kısa arka plan / Touchstones vb.")
        self.notes_edit_vtm.textChanged.connect(self._refresh_summary)

        self.summary_text_vtm = QTextEdit()
        self.summary_text_vtm.setReadOnly(True)

        layout.addWidget(QLabel("Notlar"))
        layout.addWidget(self.notes_edit_vtm)
        layout.addWidget(QLabel("Özet"))
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
        
        # Eğer mevcut dosya varsa versiyon oluştur
        if hasattr(self, 'current_character_file') and self.current_character_file:
            save_character_version(
                character,
                APP_BASE_DIR,
                self.current_character_file,
                "Manuel kayıt"
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
            "SQLite Veritabanı (*.db)"
        )
        if not db_path_str:
            return
        db_path = Path(db_path_str)
        init_db(db_path)
        record = CharacterRecord(
            id=None,
            system=self.SYSTEM_NAME,
            name=character.get("name") or "İsimsiz",
            data=character,
        )
        save_character(db_path, record)
        QMessageBox.information(self, "Başarılı", "Karakter SQLite veritabanına kaydedildi.")

    def _load_character(self):
        data, path = _load_character_via_dialog(self, "VtM Karakteri Yükle", self.SYSTEM_NAME)
        if not data:
            return
        self._apply_character(data)
        self.current_character = data
        self.current_character_file = path
        
        # Son açılanlara ekle
        if path:
            add_recent_character(APP_BASE_DIR, path, data.get("name", ""))
        
        QMessageBox.information(self, "Başarılı", "VtM karakteri yüklendi.")

    def _browse_characters(self):
        """Karakter listesi diyaloğunu aç ve VtM karakteri seç"""
        dialog = CharacterListDialog(self, None)
        dialog.setWindowTitle("Karakter Listesi - Tüm Sistemler")
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
            QMessageBox.information(self, "Başarılı", f"{data.get('name', 'Karakter')} yüklendi!")
        else:
            QMessageBox.information(
                self,
                "Bilgi",
                f"Bu karakter {system} sistemine ait.\nLütfen ilgili sekmeden yükleyin."
            )

    def _load_from_sqlite(self):
        db_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "SQLite'dan Yükle",
            str(APP_BASE_DIR / "characters"),
            "SQLite Veritabanı (*.db)"
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
                "Uyarı",
                f"Bu karakter {rec.system} sistemine ait. "
                f"Lütfen {self.SYSTEM_NAME} karakterlerini yükleyin."
            )
            return
        
        self._apply_character(rec.data)
        self.current_character = rec.data
        self.current_character_file = None
        QMessageBox.information(self, "Başarılı", f"{rec.name} yüklendi.")

    def _load_rules_from_file(self):
        """Kural kitabından kuralları yükle"""
        file_path_str, _ = QFileDialog.getOpenFileName(
            self,
            "Kural Kitabı Yükle (PDF/TXT)",
            str(APP_BASE_DIR),
            "Dosyalar (*.pdf *.txt);;PDF Dosyaları (*.pdf);;Metin Dosyaları (*.txt)"
        )
        if not file_path_str:
            return
        
        file_path = Path(file_path_str)
        
        # NLP kullanımını sor (eğer mevcut ise)
        use_nlp = False
        if is_nlp_available():
            reply = QMessageBox.question(
                self,
                "NLP Kullanımı",
                "Gelişmiş NLP (Doğal Dil İşleme) ile kural çıkarma kullanılsın mı?\n\n"
                "NLP daha karmaşık kuralları çıkarabilir ama daha yavaş olabilir.\n\n"
                "Evet: NLP kullan (önerilir)\n"
                "Hayır: Standart pattern matching kullan",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.Yes
            )
            use_nlp = (reply == QMessageBox.Yes)
        elif NLP_MODULE_AVAILABLE:
            # NLP modülü var ama model yüklenmemiş
            QMessageBox.information(
                self,
                "NLP Bilgisi",
                "NLP modülü mevcut ancak spaCy modeli yüklenmemiş.\n\n"
                "NLP kullanmak için:\n"
                "1. pip install spacy\n"
                "2. python -m spacy download en_core_web_sm\n\n"
                "Standart pattern matching kullanılacak."
            )
        
        try:
            # Kuralları çıkar
            rules = extract_rules_from_file(file_path, self.SYSTEM_NAME, use_nlp=use_nlp)
            
            if not rules or not rules.get('rules'):
                QMessageBox.warning(
                    self,
                    "Uyarı",
                    "Dosyadan kural çıkarılamadı.\n"
                    "Lütfen dosyanın doğru formatta olduğundan emin olun."
                )
                return
            
            # Kuralları doğrula
            is_valid, issues = validate_rules(rules)
            if issues:
                report = format_validation_report(issues)
                reply = QMessageBox.question(
                    self,
                    "Kural Doğrulama",
                    f"Kurallarda sorunlar bulundu:\n\n{report[:200]}...\n\n"
                    "Yine de kaydetmek istiyor musunuz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if reply == QMessageBox.No:
                    return
                
                # Detaylı rapor göster
                if not is_valid:
                    detail_msg = QMessageBox(self)
                    detail_msg.setWindowTitle("Kural Doğrulama Detayları")
                    detail_msg.setText("Kurallarda kritik hatalar bulundu. Detaylar:")
                    detail_msg.setDetailedText(report)
                    detail_msg.setIcon(QMessageBox.Warning)
                    detail_msg.exec()
            
            # Kuralları kaydet
            saved_path = save_rules(rules, APP_BASE_DIR, self.SYSTEM_NAME)
            
            # Çıkarılan kuralları göster
            rules_text = json.dumps(rules, ensure_ascii=False, indent=2)
            msg = QMessageBox(self)
            msg.setWindowTitle("Kurallar Yüklendi")
            msg.setText(f"Kurallar başarıyla çıkarıldı ve kaydedildi:\n{saved_path}")
            msg.setDetailedText(rules_text)
            msg.setIcon(QMessageBox.Information)
            msg.exec()
            
            QMessageBox.information(
                self,
                "Başarılı",
                f"Kurallar yüklendi!\n{saved_path}\n\n"
                "Artık hesaplamalar bu kurallara göre yapılacak."
            )
            
            # Cache'i yenile
            self._rules_cache = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
            # İstatistikleri güncelle
            if hasattr(self, '_refresh_summary'):
                self._refresh_summary()
            # Kural durumunu güncelle
            if hasattr(self, '_update_rules_status_vtm'):
                self._update_rules_status_vtm()
            
        except ImportError as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"PDF okuma için gerekli kütüphane eksik:\n{str(e)}\n\n"
                "Lütfen 'pip install PyPDF2' ile yükleyin."
            )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Kural yükleme hatası:\n{str(e)}"
            )

    def _export_pdf(self):
        character = self._collect_character_data()
        if not character:
            return
        self._export_character(character)
    
    def _export_character(self, character: dict):
        """Karakteri farklı formatlarda export et"""
        dialog = ExportFormatDialog(self, character)
        if dialog.exec() == QDialog.Accepted:
            format_type, file_path = dialog.get_selected_format()
            if format_type and file_path:
                self._perform_export(character, format_type, Path(file_path))
    
    def _perform_export(self, character: dict, format_type: str, file_path: Path):
        """Export işlemini gerçekleştir"""
        try:
            system = character.get("system", "VTM5E")
            
            if format_type == "PDF":
                # Arkaplan seçimi (opsiyonel - sadece PDF için)
                background_path = None
                use_bg = QMessageBox.question(
                    self,
                    "Arkaplan",
                    "PDF'e arkaplan görseli eklemek ister misiniz?",
                    QMessageBox.Yes | QMessageBox.No,
                    QMessageBox.No
                )
                if use_bg == QMessageBox.Yes:
                    bg_path_str, _ = QFileDialog.getOpenFileName(
                        self,
                        "Arkaplan Görseli Seç",
                        str(APP_BASE_DIR / "assets"),
                        "Görsel Dosyaları (*.png *.jpg *.jpeg)"
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
                QMessageBox.warning(self, "Uyarı", f"Desteklenmeyen format: {format_type}")
                return
            
            QMessageBox.information(self, "Başarılı", f"Karakter {format_type} formatında kaydedildi:\n{file_path}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Export sırasında hata oluştu:\n{str(e)}")

    def _collect_character_data(self, validate: bool = True) -> dict | None:
        name = self.vtm_name_edit.text().strip()
        if not name:
            if validate:
                QMessageBox.warning(self, "Uyarı", "Karakter adı zorunludur.")
                return None
            name = "İsimsiz"

        attributes = {
            category: {attr: spin.value() for attr, spin in spins.items()}
            for category, spins in self.attribute_spins.items()
        }
        skills = {
            category: {skill: spin.value() for skill, spin in spins.items()}
            for category, spins in self.skill_spins.items()
        }

        disciplines = self._gather_selected_disciplines()

        # Health ve Willpower otomatik hesaplama - Dinamik kural desteği
        character_temp = {
            "attributes": attributes,
            "humanity": self.humanity_spin.value()
        }
        # Önce yüklenen kuralları kontrol et
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
        """Gelişmiş özellikler UI'sını oluştur (opsiyonel) - VtM"""
        layout = self.advanced_layout_vtm
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Başlık ve açıklama
        title_label = QLabel("⚙️ Gelişmiş Özellikler")
        title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #2c3e50; margin: 10px;")
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        info_label = QLabel(
            "Bu sekme tamamen opsiyonel özellikler içerir.\n"
            "Normal karakter oluşturma için bu özelliklere ihtiyacınız yoktur."
        )
        info_label.setStyleSheet("font-size: 12px; color: #7f8c8d; padding: 10px; background-color: #ecf0f1; border-radius: 5px;")
        info_label.setAlignment(Qt.AlignCenter)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)
        
        layout.addSpacing(20)
        
        # Kural Kitabı Yükleme Grubu
        rules_group = QGroupBox("📚 Kural Kitabı Yükleme (Opsiyonel)")
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
            "Kural kitabınızı (PDF veya TXT formatında) yükleyerek, "
            "hesaplamaların otomatik olarak bu kurallara göre yapılmasını sağlayabilirsiniz.\n\n"
            "Bu özellik opsiyoneldir. Kural yüklemezseniz, varsayılan hesaplamalar kullanılır."
        )
        rules_info.setStyleSheet("font-size: 11px; color: #7f8c8d; padding: 10px;")
        rules_info.setWordWrap(True)
        rules_layout.addWidget(rules_info)
        
        # Kural yükleme butonu
        load_rules_btn = QPushButton("📄 Kural Kitabı Yükle (PDF/TXT)")
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
        load_rules_btn.setToolTip("Kural kitabından kuralları yükle (PDF/TXT)")
        rules_layout.addWidget(load_rules_btn)
        
        # Kural düzenleme butonu
        edit_rules_btn = QPushButton("✏️ Kural Düzenle")
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
        edit_rules_btn.setToolTip("Yüklenen kuralları düzenle (JSON formatında)")
        rules_layout.addWidget(edit_rules_btn)
        
        # Kural önizleme butonu
        preview_rules_btn = QPushButton("👁️ Kuralları Görüntüle")
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
        preview_rules_btn.setToolTip("Yüklenen kuralları okunabilir formatta görüntüle")
        rules_layout.addWidget(preview_rules_btn)
        
        # Mevcut kural durumu
        self.rules_status_label_vtm = QLabel("Durum: Kural yüklenmedi")
        self.rules_status_label_vtm.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
        rules_layout.addWidget(self.rules_status_label_vtm)
        
        # Kural durumunu kontrol et
        self._update_rules_status_vtm()
        
        layout.addWidget(rules_group)
        layout.addStretch()

    def _update_rules_status_vtm(self):
        """Kural durumunu güncelle - VtM"""
        if not hasattr(self, 'rules_status_label_vtm'):
            return
        
        rules = load_rules_for_system(APP_BASE_DIR, self.SYSTEM_NAME)
        if rules and rules.get('rules'):
            self.rules_status_label_vtm.setText("✅ Durum: Kural yüklü - Hesaplamalar özel kurallara göre yapılıyor")
            self.rules_status_label_vtm.setStyleSheet("font-size: 11px; color: #27ae60; padding: 5px;")
        else:
            self.rules_status_label_vtm.setText("ℹ️ Durum: Kural yüklenmedi - Varsayılan hesaplamalar kullanılıyor")
            self.rules_status_label_vtm.setStyleSheet("font-size: 11px; color: #95a5a6; padding: 5px;")
    
    def _edit_rules(self):
        """Kural düzenleme diyaloğunu aç"""
        dialog = RuleEditorDialog(self, self.SYSTEM_NAME, APP_BASE_DIR)
        if dialog.exec() == QDialog.Accepted:
            # Kural cache'i temizle
            self._rules_cache = None
            # Durumu güncelle
            self._update_rules_status_vtm()

    def _preview_rules(self):
        """VtM kurallarını önizle"""
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
            f"İsim: {character['name']}",
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
        self.setWindowTitle("Diyargezer - FRP Karakter Oluşturucu")
        self.setMinimumSize(1000, 700)
        self.resize(1200, 800)
        
        # Dark theme uygula
        self._apply_dark_theme()
        
        # Keyboard shortcuts ekle
        self._setup_shortcuts()
        
        # Pencere ikonu ayarla
        self._set_window_icon()

        # Ana widget oluştur (logo header + tab widget)
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(5, 5, 5, 5)
        main_layout.setSpacing(5)
        
        # Logo header ekle
        header_widget = self._create_header()
        header_widget.setMaximumHeight(140)  # Header maksimum yükseklik
        main_layout.addWidget(header_widget)
        
        # Tab widget
        central = QtWidgets.QTabWidget()
        central.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        central.addTab(DndPage(), "🎲 D&D 5e")
        central.addTab(MmPage(), "🦸 M&M")
        central.addTab(VtmPage(), "🧛 VtM")
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
        
        # Ctrl+O: Karakter yükle
        load_char_shortcut = QShortcut(QKeySequence("Ctrl+O"), self)
        load_char_shortcut.activated.connect(self._load_character_shortcut)
        
        # Ctrl+S: Karakter kaydet
        save_char_shortcut = QShortcut(QKeySequence("Ctrl+S"), self)
        save_char_shortcut.activated.connect(self._save_character_shortcut)
        
        # Ctrl+E: PDF export
        export_shortcut = QShortcut(QKeySequence("Ctrl+E"), self)
        export_shortcut.activated.connect(self._export_shortcut)
        
        # F1: Yardım
        help_shortcut = QShortcut(QKeySequence("F1"), self)
        help_shortcut.activated.connect(self._show_help)

    def _new_character_shortcut(self):
        """Yeni karakter oluştur (Ctrl+N)"""
        # D&D sayfasına geç ve yeni karakter başlat
        if hasattr(self, 'centralWidget'):
            tab_widget = self.centralWidget()
            if isinstance(tab_widget, QTabWidget):
                tab_widget.setCurrentIndex(0)  # D&D sekmesi

    def _load_character_shortcut(self):
        """Karakter yükle (Ctrl+O)"""
        # D&D sayfasına geç ve karakter yükleme dialog'unu aç
        if hasattr(self, 'centralWidget'):
            tab_widget = self.centralWidget()
            if isinstance(tab_widget, QTabWidget):
                tab_widget.setCurrentIndex(0)  # D&D sekmesi

    def _save_character_shortcut(self):
        """Karakter kaydet (Ctrl+S)"""
        # Otomatik kaydetme zaten aktif, bilgi mesajı göster
        QMessageBox.information(self, "Bilgi", "Karakter otomatik olarak kaydediliyor!")

    def _export_shortcut(self):
        """PDF export (Ctrl+E)"""
        # D&D sayfasına geç ve export yap
        if hasattr(self, 'centralWidget'):
            tab_widget = self.centralWidget()
            if isinstance(tab_widget, QTabWidget):
                tab_widget.setCurrentIndex(0)  # D&D sekmesi

    def _show_help(self):
        """Yardım göster (F1)"""
        help_text = """
🎮 Diyargezer - FRP Karakter Oluşturucu

⌨️ Klavye Kısayolları:
• Ctrl+N: Yeni Karakter Oluştur
• Ctrl+O: Karakter Yükle
• Ctrl+S: Karakter Kaydet
• Ctrl+E: PDF Export
• F1: Bu Yardım

🎯 Özellikler:
• D&D 5e karakter oluşturma
• Otomatik istatistik hesaplama
• Envanter yönetimi
• Büyü sistemi
• Dice roller
• PDF export

📧 Destek: [Destek bilgileri]
        """
        QMessageBox.information(self, "Yardım - Klavye Kısayolları", help_text)

    def _create_header(self) -> QWidget:
        """Ana pencere için logo header oluştur"""
        header_widget = QWidget()
        header_widget.setStyleSheet("background-color: #34495e; border-bottom: 2px solid #2c3e50;")
        header_widget.setMaximumHeight(140)  # Header maksimum yükseklik
        header_layout = QHBoxLayout(header_widget)
        header_layout.setContentsMargins(15, 10, 15, 10)
        
        # Logo
        logo_path = Path(__file__).resolve().parents[1] / "Gemini_Generated_Image_c510m9c510m9c510.png"
        if logo_path.exists():
            logo_label = QLabel()
            logo_pixmap = QPixmap(str(logo_path))
            if not logo_pixmap.isNull():
                # Logoyu küçült (maksimum 100x100, aspect ratio korunarak)
                scaled_pixmap = logo_pixmap.scaled(100, 100, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                logo_label.setPixmap(scaled_pixmap)
                logo_label.setScaledContents(True)  # Küçültülmüş boyutta göster
            logo_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
            logo_label.setFixedSize(100, 100)  # Sabit boyut
            header_layout.addWidget(logo_label)
        
        # Başlık
        title_label = QLabel("Diyargezer - FRP Karakter Oluşturucu")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: white; margin-left: 20px;")
        title_label.setAlignment(Qt.AlignLeft | Qt.AlignVCenter)
        title_label.setWordWrap(True)  # Uzun metinler için kelime kaydırma
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
