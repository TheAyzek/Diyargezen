#!/usr/bin/env python3
"""
Clean GUI for Diyargezen - Simple test version
"""

import sys
from pathlib import Path
from typing import List

try:
    from PyQt5.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, 
        QPushButton, QLabel, QMessageBox, QHBoxLayout
    )
except Exception:
    from PySide6.QtWidgets import (
        QApplication, QMainWindow, QWidget, QVBoxLayout, 
        QPushButton, QLabel, QMessageBox, QHBoxLayout
    )

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Diyargezen - FRP Karakter Oluşturucu")
        self.setGeometry(100, 100, 800, 600)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Layout
        layout = QVBoxLayout()
        central_widget.setLayout(layout)
        
        # Title
        title = QLabel("🎲 Diyargezen - FRP Karakter Oluşturucu")
        title.setStyleSheet("font-size: 24px; font-weight: bold; margin: 20px;")
        layout.addWidget(title)
        
        # System buttons
        systems = [
            ("D&D 5e", "dnd5e"),
            ("Pathfinder 1e", "pathfinder1e"), 
            ("Vampire: The Masquerade", "vtm5e"),
            ("Mutants & Masterminds", "mm3e")
        ]
        
        for name, system in systems:
            btn = QPushButton(f"📋 {name} Karakter Oluştur")
            btn.clicked.connect(lambda checked, s=system: self.create_character(s))
            btn.setStyleSheet("padding: 15px; font-size: 16px; margin: 5px;")
            layout.addWidget(btn)
        
        # Status label
        self.status_label = QLabel("Hazır - Sistem seçin")
        layout.addWidget(self.status_label)
    
    def create_character(self, system):
        """Test character creation"""
        try:
            # Add project root to path
            project_root = Path(__file__).parent.parent
            if str(project_root) not in sys.path:
                sys.path.insert(0, str(project_root))
            
            from creators import CharacterFactory
            
            # Create character
            creator = CharacterFactory.create_creator(system)
            character = creator.create_character()
            
            # Save character
            filename = f"test_{system}_character"
            if creator.save_character(character, filename):
                self.status_label.setText(f"✅ {system} karakteri oluşturuldu: {filename}.json")
                QMessageBox.information(self, "Başarılı", f"{system} karakteri başarıyla oluşturuldu!\n\nİsim: {character.get('name', 'N/A')}\nSistem: {character.get('system', 'N/A')}")
            else:
                self.status_label.setText(f"❌ {system} karakteri kaydedilemedi")
                
        except Exception as e:
            error_msg = f"{system} karakter oluşturma hatası: {e}"
            self.status_label.setText(f"❌ {error_msg}")
            QMessageBox.critical(self, "Hata", error_msg)

def main(argv: List[str] | None = None) -> int:
    app = QApplication(argv or sys.argv)
    win = MainWindow()
    win.show()
    return app.exec()

if __name__ == "__main__":
    raise SystemExit(main())
