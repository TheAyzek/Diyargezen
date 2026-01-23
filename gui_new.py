#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Diyargezen GUI - Ana Uygulama Penceresi
Tüm RPG sistemleri (D&D 5e, Pathfinder, M&M, VtM) için birleşik arayüz
"""

import sys
import json
from pathlib import Path
from typing import Dict, Any, Optional

from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QTabWidget, QLabel, QLineEdit, QComboBox, QPushButton, QMessageBox,
    QTableWidget, QTableWidgetItem, QFileDialog, QDialog, QSpinBox,
    QCheckBox, QTextEdit, QGroupBox, QGridLayout, QListWidget, QListWidgetItem
)
from PySide6.QtCore import Qt
from PySide6.QtGui import QFont, QIcon


class SystemTab(QWidget):
    """Her sistem için ayrı tab"""
    
    def __init__(self, system_name: str, data: Dict[str, Any], parent=None):
        super().__init__(parent)
        self.system_name = system_name
        self.data = data
        self.character = {}
        self.init_ui()
    
    def init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        
        # Karaktere Bilgileri Grubu
        char_group = QGroupBox("Karakter Bilgileri")
        char_layout = QGridLayout()
        
        char_layout.addWidget(QLabel("Karakter Adı:"), 0, 0)
        self.name_edit = QLineEdit()
        char_layout.addWidget(self.name_edit, 0, 1)
        
        char_layout.addWidget(QLabel("Sistem:"), 0, 2)
        system_label = QLabel(self.system_name)
        char_layout.addWidget(system_label, 0, 3)
        
        # Race/Irk
        char_layout.addWidget(QLabel("Irk:"), 1, 0)
        self.race_combo = QComboBox()
        self.race_combo.addItems(sorted(self.data.get("races", {}).keys()))
        char_layout.addWidget(self.race_combo, 1, 1)
        
        # Class/Sınıf
        char_layout.addWidget(QLabel("Sınıf:"), 1, 2)
        self.class_combo = QComboBox()
        self.class_combo.addItems(sorted(self.data.get("classes", {}).keys()))
        char_layout.addWidget(self.class_combo, 1, 3)
        
        # Level
        char_layout.addWidget(QLabel("Seviye:"), 2, 0)
        self.level_spin = QSpinBox()
        self.level_spin.setMinimum(1)
        self.level_spin.setMaximum(20)
        self.level_spin.setValue(1)
        char_layout.addWidget(self.level_spin, 2, 1)
        
        char_group.setLayout(char_layout)
        layout.addWidget(char_group)
        
        # Ability Scores
        ability_group = QGroupBox("Yetenekler (Abilities)")
        ability_layout = QGridLayout()
        
        self.ability_edits = {}
        abilities = ["Strength", "Dexterity", "Constitution", "Intelligence", "Wisdom", "Charisma"]
        
        for idx, ability in enumerate(abilities):
            label = QLabel(f"{ability} (STR/DEX/CON/INT/WIS/CHA)"[0])
            ability_layout.addWidget(label, 0, idx)
            
            spin = QSpinBox()
            spin.setMinimum(3)
            spin.setMaximum(20)
            spin.setValue(10)
            self.ability_edits[ability] = spin
            ability_layout.addWidget(spin, 1, idx)
        
        ability_group.setLayout(ability_layout)
        layout.addWidget(ability_group)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        create_btn = QPushButton("Karakter Oluştur")
        create_btn.clicked.connect(self.create_character)
        button_layout.addWidget(create_btn)
        
        save_btn = QPushButton("Kaydet")
        save_btn.clicked.connect(self.save_character)
        button_layout.addWidget(save_btn)
        
        load_btn = QPushButton("Yükle")
        load_btn.clicked.connect(self.load_character)
        button_layout.addWidget(load_btn)
        
        export_btn = QPushButton("PDF Export")
        export_btn.clicked.connect(self.export_pdf)
        button_layout.addWidget(export_btn)
        
        layout.addLayout(button_layout)
        
        # Character Display
        display_group = QGroupBox("Karakter Özeti")
        display_layout = QVBoxLayout()
        self.display_text = QTextEdit()
        self.display_text.setReadOnly(True)
        display_layout.addWidget(self.display_text)
        display_group.setLayout(display_layout)
        layout.addWidget(display_group)
        
        layout.addStretch()
    
    def create_character(self):
        """Karakter oluştur"""
        self.character = {
            "name": self.name_edit.text() or "Unnamed",
            "system": self.system_name,
            "race": self.race_combo.currentText(),
            "class": self.class_combo.currentText(),
            "level": self.level_spin.value(),
            "abilities": {
                ability: self.ability_edits[ability].value()
                for ability in self.ability_edits
            }
        }
        
        self.display_text.setText(
            f"Karakter: {self.character['name']}\n"
            f"Sistem: {self.character['system']}\n"
            f"Irk: {self.character['race']}\n"
            f"Sınıf: {self.character['class']}\n"
            f"Seviye: {self.character['level']}\n\n"
            f"Yetenekler:\n" +
            "\n".join(f"  {k}: {v}" for k, v in self.character['abilities'].items())
        )
        
        QMessageBox.information(self, "Başarılı", f"{self.character['name']} oluşturuldu!")
    
    def save_character(self):
        """Karakteri kaydet"""
        if not self.character:
            QMessageBox.warning(self, "Uyarı", "Önce karakter oluşturun!")
            return
        
        filename, _ = QFileDialog.getSaveFileName(
            self, "Karakteri Kaydet", "", "JSON Files (*.json)"
        )
        
        if filename:
            with open(filename, 'w', encoding='utf-8') as f:
                json.dump(self.character, f, ensure_ascii=False, indent=2)
            QMessageBox.information(self, "Başarılı", f"Karakter kaydedildi: {filename}")
    
    def load_character(self):
        """Karakteri yükle"""
        filename, _ = QFileDialog.getOpenFileName(
            self, "Karakteri Yükle", "", "JSON Files (*.json)"
        )
        
        if filename:
            with open(filename, 'r', encoding='utf-8') as f:
                self.character = json.load(f)
            
            self.name_edit.setText(self.character.get("name", ""))
            self.race_combo.setCurrentText(self.character.get("race", ""))
            self.class_combo.setCurrentText(self.character.get("class", ""))
            self.level_spin.setValue(self.character.get("level", 1))
            
            for ability, value in self.character.get("abilities", {}).items():
                if ability in self.ability_edits:
                    self.ability_edits[ability].setValue(value)
            
            self.display_text.setText(
                f"Karakter: {self.character['name']}\n"
                f"Sistem: {self.character['system']}\n"
                f"Irk: {self.character['race']}\n"
                f"Sınıf: {self.character['class']}\n"
                f"Seviye: {self.character['level']}\n\n"
                f"Yetenekler:\n" +
                "\n".join(f"  {k}: {v}" for k, v in self.character['abilities'].items())
            )
            
            QMessageBox.information(self, "Başarılı", "Karakter yüklendi!")
    
    def export_pdf(self):
        """PDF olarak dışa aktar"""
        if not self.character:
            QMessageBox.warning(self, "Uyarı", "Önce karakter oluşturun!")
            return
        
        QMessageBox.information(self, "Bilgi", "PDF export şu anda geliştirilmektedir.")


class MainWindow(QMainWindow):
    """Ana Pencere - Tüm sistemleri içeren tab arayüzü"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diyargezen - RPG Karakter Oluşturucu")
        self.setGeometry(100, 100, 1000, 800)
        
        self.data = self.load_data()
        self.init_ui()
    
    def load_data(self) -> Dict[str, Dict[str, Any]]:
        """Tüm sistem verilerini yükle"""
        base_dir = Path(__file__).parent.parent
        data = {}
        
        # D&D 5e
        try:
            with open(base_dir / "data" / "dnd_data.json", encoding='utf-8') as f:
                data["D&D 5e"] = json.load(f)
        except:
            data["D&D 5e"] = {"races": {}, "classes": {}}
        
        # Pathfinder 1e
        try:
            with open(base_dir / "data" / "pathfinder_1e_data.json", encoding='utf-8') as f:
                data["Pathfinder 1e"] = json.load(f)
        except:
            data["Pathfinder 1e"] = {"races": {}, "classes": {}}
        
        # M&M
        try:
            with open(base_dir / "data" / "mm_data.json", encoding='utf-8') as f:
                data["M&M"] = json.load(f)
        except:
            data["M&M"] = {"races": {"Human": {}}, "classes": {"Superhero": {}}}
        
        # VtM
        try:
            with open(base_dir / "data" / "vtm_data.json", encoding='utf-8') as f:
                data["VtM"] = json.load(f)
        except:
            data["VtM"] = {"races": {"Vampire": {}}, "classes": {"Clan": {}}}
        
        return data
    
    def init_ui(self):
        """Ana arayüzü oluştur"""
        # Central widget
        central = QWidget()
        self.setCentralWidget(central)
        main_layout = QVBoxLayout(central)
        
        # Başlık
        title = QLabel("Diyargezen - Evrensel FRP Karakter Oluşturucu")
        title.setFont(QFont("Arial", 14, QFont.Bold))
        main_layout.addWidget(title)
        
        # Tab widget
        self.tabs = QTabWidget()
        
        # Her sistem için tab oluştur
        systems = ["D&D 5e", "Pathfinder 1e", "M&M", "VtM"]
        for system in systems:
            tab = SystemTab(system, self.data.get(system, {}))
            self.tabs.addTab(tab, system)
        
        main_layout.addWidget(self.tabs)
        
        # Alt butonlar
        bottom_layout = QHBoxLayout()
        
        about_btn = QPushButton("Hakkında")
        about_btn.clicked.connect(self.show_about)
        bottom_layout.addWidget(about_btn)
        
        exit_btn = QPushButton("Çıkış")
        exit_btn.clicked.connect(self.close)
        bottom_layout.addWidget(exit_btn)
        
        bottom_layout.addStretch()
        main_layout.addLayout(bottom_layout)
    
    def show_about(self):
        """Hakkında dialogu göster"""
        QMessageBox.information(
            self,
            "Hakkında",
            "Diyargezen - Evrensel FRP Karakter Oluşturucu\n\n"
            "Desteklenen Sistemler:\n"
            "• Dungeons & Dragons 5e\n"
            "• Pathfinder 1e\n"
            "• Mutants & Masterminds\n"
            "• Vampire: The Masquerade\n\n"
            "Sürüm: 1.0"
        )


def main():
    """Ana fonksiyon"""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
