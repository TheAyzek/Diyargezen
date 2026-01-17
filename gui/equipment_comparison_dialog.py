"""
Equipment Comparison Dialog - İYİLEŞTİRİLDİ (Equipment Comparison)
İki equipment item'ını karşılaştırma dialog'u
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QListWidget, QMessageBox
)
from PySide6.QtCore import Qt
from utils.equipment_comparison import compare_equipment_items


class EquipmentComparisonDialog(QDialog):
    """Equipment karşılaştırma dialog'u"""
    
    def __init__(self, parent, character_data, data):
        super().__init__(parent)
        self.character_data = character_data
        self.data = data
        self.setWindowTitle("⚖️ Eşya Karşılaştırma")
        self.setMinimumSize(800, 600)
        self._init_ui()
    
    def _init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("Eşya Karşılaştırma")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Item seçim bölümü
        selection_layout = QHBoxLayout()
        
        # Item 1 seçimi
        item1_group = QLabel("Item 1:")
        item1_group.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(item1_group)
        
        self.item1_combo = QComboBox()
        self.item1_combo.setMinimumWidth(250)
        self._populate_item_combo(self.item1_combo)
        selection_layout.addWidget(self.item1_combo)
        
        selection_layout.addStretch()
        
        # Item 2 seçimi
        item2_group = QLabel("Item 2:")
        item2_group.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(item2_group)
        
        self.item2_combo = QComboBox()
        self.item2_combo.setMinimumWidth(250)
        self._populate_item_combo(self.item2_combo)
        selection_layout.addWidget(self.item2_combo)
        
        layout.addLayout(selection_layout)
        
        # Karşılaştır butonu
        compare_btn = QPushButton("⚖️ Karşılaştır")
        compare_btn.setStyleSheet("""
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
        compare_btn.clicked.connect(self._compare_items)
        layout.addWidget(compare_btn)
        
        # Karşılaştırma sonuçları
        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        self.comparison_text.setMinimumHeight(400)
        self.comparison_text.setPlaceholderText("İki item seçin ve 'Karşılaştır' butonuna tıklayın...")
        layout.addWidget(self.comparison_text)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _populate_item_combo(self, combo):
        """Item combo box'unu doldur"""
        equipment = self.character_data.get("equipment", [])
        combo.clear()
        combo.addItem("-- Item Seçin --", None)
        
        for item in equipment:
            item_name = item.get("name", "İsimsiz Eşya")
            item_type = item.get("type", "gear")
            icon = "⚔️" if item_type == "weapon" else "🛡️" if item_type == "armor" else "🎒"
            combo.addItem(f"{icon} {item_name}", item)
    
    def _compare_items(self):
        """Seçili item'ları karşılaştır"""
        item1_data = self.item1_combo.currentData()
        item2_data = self.item2_combo.currentData()
        
        if not item1_data or not item2_data:
            QMessageBox.warning(self, "Uyarı", "Lütfen iki item seçin!")
            return
        
        if item1_data == item2_data:
            QMessageBox.warning(self, "Uyarı", "Aynı item'ı karşılaştıramazsınız!")
            return
        
        try:
            comparison = compare_equipment_items(item1_data, item2_data)
            
            if "error" in comparison:
                self.comparison_text.setHtml(f"<p style='color: #e74c3c;'><b>Hata:</b> {comparison['error']}</p>")
                return
            
            # Karşılaştırma sonuçlarını formatla
            html = f"<h2>⚖️ {comparison['item1_name']} vs {comparison['item2_name']}</h2><br>"
            
            # Advantages
            if comparison.get("advantages_item1"):
                html += "<h3 style='color: #27ae60;'>✅ " + comparison['item1_name'] + " Avantajları:</h3><ul>"
                for advantage in comparison["advantages_item1"]:
                    html += f"<li>{advantage}</li>"
                html += "</ul>"
            
            if comparison.get("advantages_item2"):
                html += "<h3 style='color: #3498db;'>✅ " + comparison['item2_name'] + " Avantajları:</h3><ul>"
                for advantage in comparison["advantages_item2"]:
                    html += f"<li>{advantage}</li>"
                html += "</ul>"
            
            # Differences
            if comparison.get("differences"):
                html += "<h3>📊 Farklar:</h3><table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
                html += "<tr><th>Özellik</th><th>" + comparison['item1_name'] + "</th><th>" + comparison['item2_name'] + "</th></tr>"
                
                for diff in comparison["differences"]:
                    field = diff.get("field", "N/A")
                    val1 = diff.get("item1_value", "N/A")
                    val2 = diff.get("item2_value", "N/A")
                    
                    item1_style = "color: #27ae60; font-weight: bold;" if diff.get("item1_better") else ""
                    item2_style = "color: #3498db; font-weight: bold;" if diff.get("item2_better") else ""
                    
                    html += f"<tr>"
                    html += f"<td><b>{field.title()}</b></td>"
                    html += f"<td style='{item1_style}'>{val1}</td>"
                    html += f"<td style='{item2_style}'>{val2}</td>"
                    html += f"</tr>"
                
                html += "</table><br>"
            
            # Recommendation
            if comparison.get("recommendation"):
                html += f"<h3 style='color: #f39c12;'>💡 Öneri:</h3>"
                html += f"<p style='font-size: 14px;'>{comparison['recommendation']}</p>"
            
            self.comparison_text.setHtml(html)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karşılaştırma yapılırken hata oluştu:\n{str(e)}")
            import traceback
            print(traceback.format_exc())


İki equipment item'ını karşılaştırma dialog'u
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QListWidget, QMessageBox
)
from PySide6.QtCore import Qt
from utils.equipment_comparison import compare_equipment_items


class EquipmentComparisonDialog(QDialog):
    """Equipment karşılaştırma dialog'u"""
    
    def __init__(self, parent, character_data, data):
        super().__init__(parent)
        self.character_data = character_data
        self.data = data
        self.setWindowTitle("⚖️ Eşya Karşılaştırma")
        self.setMinimumSize(800, 600)
        self._init_ui()
    
    def _init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("Eşya Karşılaştırma")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Item seçim bölümü
        selection_layout = QHBoxLayout()
        
        # Item 1 seçimi
        item1_group = QLabel("Item 1:")
        item1_group.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(item1_group)
        
        self.item1_combo = QComboBox()
        self.item1_combo.setMinimumWidth(250)
        self._populate_item_combo(self.item1_combo)
        selection_layout.addWidget(self.item1_combo)
        
        selection_layout.addStretch()
        
        # Item 2 seçimi
        item2_group = QLabel("Item 2:")
        item2_group.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(item2_group)
        
        self.item2_combo = QComboBox()
        self.item2_combo.setMinimumWidth(250)
        self._populate_item_combo(self.item2_combo)
        selection_layout.addWidget(self.item2_combo)
        
        layout.addLayout(selection_layout)
        
        # Karşılaştır butonu
        compare_btn = QPushButton("⚖️ Karşılaştır")
        compare_btn.setStyleSheet("""
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
        compare_btn.clicked.connect(self._compare_items)
        layout.addWidget(compare_btn)
        
        # Karşılaştırma sonuçları
        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        self.comparison_text.setMinimumHeight(400)
        self.comparison_text.setPlaceholderText("İki item seçin ve 'Karşılaştır' butonuna tıklayın...")
        layout.addWidget(self.comparison_text)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _populate_item_combo(self, combo):
        """Item combo box'unu doldur"""
        equipment = self.character_data.get("equipment", [])
        combo.clear()
        combo.addItem("-- Item Seçin --", None)
        
        for item in equipment:
            item_name = item.get("name", "İsimsiz Eşya")
            item_type = item.get("type", "gear")
            icon = "⚔️" if item_type == "weapon" else "🛡️" if item_type == "armor" else "🎒"
            combo.addItem(f"{icon} {item_name}", item)
    
    def _compare_items(self):
        """Seçili item'ları karşılaştır"""
        item1_data = self.item1_combo.currentData()
        item2_data = self.item2_combo.currentData()
        
        if not item1_data or not item2_data:
            QMessageBox.warning(self, "Uyarı", "Lütfen iki item seçin!")
            return
        
        if item1_data == item2_data:
            QMessageBox.warning(self, "Uyarı", "Aynı item'ı karşılaştıramazsınız!")
            return
        
        try:
            comparison = compare_equipment_items(item1_data, item2_data)
            
            if "error" in comparison:
                self.comparison_text.setHtml(f"<p style='color: #e74c3c;'><b>Hata:</b> {comparison['error']}</p>")
                return
            
            # Karşılaştırma sonuçlarını formatla
            html = f"<h2>⚖️ {comparison['item1_name']} vs {comparison['item2_name']}</h2><br>"
            
            # Advantages
            if comparison.get("advantages_item1"):
                html += "<h3 style='color: #27ae60;'>✅ " + comparison['item1_name'] + " Avantajları:</h3><ul>"
                for advantage in comparison["advantages_item1"]:
                    html += f"<li>{advantage}</li>"
                html += "</ul>"
            
            if comparison.get("advantages_item2"):
                html += "<h3 style='color: #3498db;'>✅ " + comparison['item2_name'] + " Avantajları:</h3><ul>"
                for advantage in comparison["advantages_item2"]:
                    html += f"<li>{advantage}</li>"
                html += "</ul>"
            
            # Differences
            if comparison.get("differences"):
                html += "<h3>📊 Farklar:</h3><table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
                html += "<tr><th>Özellik</th><th>" + comparison['item1_name'] + "</th><th>" + comparison['item2_name'] + "</th></tr>"
                
                for diff in comparison["differences"]:
                    field = diff.get("field", "N/A")
                    val1 = diff.get("item1_value", "N/A")
                    val2 = diff.get("item2_value", "N/A")
                    
                    item1_style = "color: #27ae60; font-weight: bold;" if diff.get("item1_better") else ""
                    item2_style = "color: #3498db; font-weight: bold;" if diff.get("item2_better") else ""
                    
                    html += f"<tr>"
                    html += f"<td><b>{field.title()}</b></td>"
                    html += f"<td style='{item1_style}'>{val1}</td>"
                    html += f"<td style='{item2_style}'>{val2}</td>"
                    html += f"</tr>"
                
                html += "</table><br>"
            
            # Recommendation
            if comparison.get("recommendation"):
                html += f"<h3 style='color: #f39c12;'>💡 Öneri:</h3>"
                html += f"<p style='font-size: 14px;'>{comparison['recommendation']}</p>"
            
            self.comparison_text.setHtml(html)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karşılaştırma yapılırken hata oluştu:\n{str(e)}")
            import traceback
            print(traceback.format_exc())


İki equipment item'ını karşılaştırma dialog'u
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QListWidget, QMessageBox
)
from PySide6.QtCore import Qt
from utils.equipment_comparison import compare_equipment_items


class EquipmentComparisonDialog(QDialog):
    """Equipment karşılaştırma dialog'u"""
    
    def __init__(self, parent, character_data, data):
        super().__init__(parent)
        self.character_data = character_data
        self.data = data
        self.setWindowTitle("⚖️ Eşya Karşılaştırma")
        self.setMinimumSize(800, 600)
        self._init_ui()
    
    def _init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("Eşya Karşılaştırma")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Item seçim bölümü
        selection_layout = QHBoxLayout()
        
        # Item 1 seçimi
        item1_group = QLabel("Item 1:")
        item1_group.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(item1_group)
        
        self.item1_combo = QComboBox()
        self.item1_combo.setMinimumWidth(250)
        self._populate_item_combo(self.item1_combo)
        selection_layout.addWidget(self.item1_combo)
        
        selection_layout.addStretch()
        
        # Item 2 seçimi
        item2_group = QLabel("Item 2:")
        item2_group.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(item2_group)
        
        self.item2_combo = QComboBox()
        self.item2_combo.setMinimumWidth(250)
        self._populate_item_combo(self.item2_combo)
        selection_layout.addWidget(self.item2_combo)
        
        layout.addLayout(selection_layout)
        
        # Karşılaştır butonu
        compare_btn = QPushButton("⚖️ Karşılaştır")
        compare_btn.setStyleSheet("""
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
        compare_btn.clicked.connect(self._compare_items)
        layout.addWidget(compare_btn)
        
        # Karşılaştırma sonuçları
        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        self.comparison_text.setMinimumHeight(400)
        self.comparison_text.setPlaceholderText("İki item seçin ve 'Karşılaştır' butonuna tıklayın...")
        layout.addWidget(self.comparison_text)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _populate_item_combo(self, combo):
        """Item combo box'unu doldur"""
        equipment = self.character_data.get("equipment", [])
        combo.clear()
        combo.addItem("-- Item Seçin --", None)
        
        for item in equipment:
            item_name = item.get("name", "İsimsiz Eşya")
            item_type = item.get("type", "gear")
            icon = "⚔️" if item_type == "weapon" else "🛡️" if item_type == "armor" else "🎒"
            combo.addItem(f"{icon} {item_name}", item)
    
    def _compare_items(self):
        """Seçili item'ları karşılaştır"""
        item1_data = self.item1_combo.currentData()
        item2_data = self.item2_combo.currentData()
        
        if not item1_data or not item2_data:
            QMessageBox.warning(self, "Uyarı", "Lütfen iki item seçin!")
            return
        
        if item1_data == item2_data:
            QMessageBox.warning(self, "Uyarı", "Aynı item'ı karşılaştıramazsınız!")
            return
        
        try:
            comparison = compare_equipment_items(item1_data, item2_data)
            
            if "error" in comparison:
                self.comparison_text.setHtml(f"<p style='color: #e74c3c;'><b>Hata:</b> {comparison['error']}</p>")
                return
            
            # Karşılaştırma sonuçlarını formatla
            html = f"<h2>⚖️ {comparison['item1_name']} vs {comparison['item2_name']}</h2><br>"
            
            # Advantages
            if comparison.get("advantages_item1"):
                html += "<h3 style='color: #27ae60;'>✅ " + comparison['item1_name'] + " Avantajları:</h3><ul>"
                for advantage in comparison["advantages_item1"]:
                    html += f"<li>{advantage}</li>"
                html += "</ul>"
            
            if comparison.get("advantages_item2"):
                html += "<h3 style='color: #3498db;'>✅ " + comparison['item2_name'] + " Avantajları:</h3><ul>"
                for advantage in comparison["advantages_item2"]:
                    html += f"<li>{advantage}</li>"
                html += "</ul>"
            
            # Differences
            if comparison.get("differences"):
                html += "<h3>📊 Farklar:</h3><table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
                html += "<tr><th>Özellik</th><th>" + comparison['item1_name'] + "</th><th>" + comparison['item2_name'] + "</th></tr>"
                
                for diff in comparison["differences"]:
                    field = diff.get("field", "N/A")
                    val1 = diff.get("item1_value", "N/A")
                    val2 = diff.get("item2_value", "N/A")
                    
                    item1_style = "color: #27ae60; font-weight: bold;" if diff.get("item1_better") else ""
                    item2_style = "color: #3498db; font-weight: bold;" if diff.get("item2_better") else ""
                    
                    html += f"<tr>"
                    html += f"<td><b>{field.title()}</b></td>"
                    html += f"<td style='{item1_style}'>{val1}</td>"
                    html += f"<td style='{item2_style}'>{val2}</td>"
                    html += f"</tr>"
                
                html += "</table><br>"
            
            # Recommendation
            if comparison.get("recommendation"):
                html += f"<h3 style='color: #f39c12;'>💡 Öneri:</h3>"
                html += f"<p style='font-size: 14px;'>{comparison['recommendation']}</p>"
            
            self.comparison_text.setHtml(html)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karşılaştırma yapılırken hata oluştu:\n{str(e)}")
            import traceback
            print(traceback.format_exc())


İki equipment item'ını karşılaştırma dialog'u
"""

from PySide6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QTextEdit,
    QPushButton, QComboBox, QListWidget, QMessageBox
)
from PySide6.QtCore import Qt
from utils.equipment_comparison import compare_equipment_items


class EquipmentComparisonDialog(QDialog):
    """Equipment karşılaştırma dialog'u"""
    
    def __init__(self, parent, character_data, data):
        super().__init__(parent)
        self.character_data = character_data
        self.data = data
        self.setWindowTitle("⚖️ Eşya Karşılaştırma")
        self.setMinimumSize(800, 600)
        self._init_ui()
    
    def _init_ui(self):
        """UI oluştur"""
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # Başlık
        title = QLabel("Eşya Karşılaştırma")
        title.setStyleSheet("font-size: 20px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        title.setAlignment(Qt.AlignCenter)
        layout.addWidget(title)
        
        # Item seçim bölümü
        selection_layout = QHBoxLayout()
        
        # Item 1 seçimi
        item1_group = QLabel("Item 1:")
        item1_group.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(item1_group)
        
        self.item1_combo = QComboBox()
        self.item1_combo.setMinimumWidth(250)
        self._populate_item_combo(self.item1_combo)
        selection_layout.addWidget(self.item1_combo)
        
        selection_layout.addStretch()
        
        # Item 2 seçimi
        item2_group = QLabel("Item 2:")
        item2_group.setStyleSheet("font-weight: bold;")
        selection_layout.addWidget(item2_group)
        
        self.item2_combo = QComboBox()
        self.item2_combo.setMinimumWidth(250)
        self._populate_item_combo(self.item2_combo)
        selection_layout.addWidget(self.item2_combo)
        
        layout.addLayout(selection_layout)
        
        # Karşılaştır butonu
        compare_btn = QPushButton("⚖️ Karşılaştır")
        compare_btn.setStyleSheet("""
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
        compare_btn.clicked.connect(self._compare_items)
        layout.addWidget(compare_btn)
        
        # Karşılaştırma sonuçları
        self.comparison_text = QTextEdit()
        self.comparison_text.setReadOnly(True)
        self.comparison_text.setMinimumHeight(400)
        self.comparison_text.setPlaceholderText("İki item seçin ve 'Karşılaştır' butonuna tıklayın...")
        layout.addWidget(self.comparison_text)
        
        # Kapat butonu
        close_btn = QPushButton("Kapat")
        close_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def _populate_item_combo(self, combo):
        """Item combo box'unu doldur"""
        equipment = self.character_data.get("equipment", [])
        combo.clear()
        combo.addItem("-- Item Seçin --", None)
        
        for item in equipment:
            item_name = item.get("name", "İsimsiz Eşya")
            item_type = item.get("type", "gear")
            icon = "⚔️" if item_type == "weapon" else "🛡️" if item_type == "armor" else "🎒"
            combo.addItem(f"{icon} {item_name}", item)
    
    def _compare_items(self):
        """Seçili item'ları karşılaştır"""
        item1_data = self.item1_combo.currentData()
        item2_data = self.item2_combo.currentData()
        
        if not item1_data or not item2_data:
            QMessageBox.warning(self, "Uyarı", "Lütfen iki item seçin!")
            return
        
        if item1_data == item2_data:
            QMessageBox.warning(self, "Uyarı", "Aynı item'ı karşılaştıramazsınız!")
            return
        
        try:
            comparison = compare_equipment_items(item1_data, item2_data)
            
            if "error" in comparison:
                self.comparison_text.setHtml(f"<p style='color: #e74c3c;'><b>Hata:</b> {comparison['error']}</p>")
                return
            
            # Karşılaştırma sonuçlarını formatla
            html = f"<h2>⚖️ {comparison['item1_name']} vs {comparison['item2_name']}</h2><br>"
            
            # Advantages
            if comparison.get("advantages_item1"):
                html += "<h3 style='color: #27ae60;'>✅ " + comparison['item1_name'] + " Avantajları:</h3><ul>"
                for advantage in comparison["advantages_item1"]:
                    html += f"<li>{advantage}</li>"
                html += "</ul>"
            
            if comparison.get("advantages_item2"):
                html += "<h3 style='color: #3498db;'>✅ " + comparison['item2_name'] + " Avantajları:</h3><ul>"
                for advantage in comparison["advantages_item2"]:
                    html += f"<li>{advantage}</li>"
                html += "</ul>"
            
            # Differences
            if comparison.get("differences"):
                html += "<h3>📊 Farklar:</h3><table border='1' cellpadding='5' cellspacing='0' style='border-collapse: collapse; width: 100%;'>"
                html += "<tr><th>Özellik</th><th>" + comparison['item1_name'] + "</th><th>" + comparison['item2_name'] + "</th></tr>"
                
                for diff in comparison["differences"]:
                    field = diff.get("field", "N/A")
                    val1 = diff.get("item1_value", "N/A")
                    val2 = diff.get("item2_value", "N/A")
                    
                    item1_style = "color: #27ae60; font-weight: bold;" if diff.get("item1_better") else ""
                    item2_style = "color: #3498db; font-weight: bold;" if diff.get("item2_better") else ""
                    
                    html += f"<tr>"
                    html += f"<td><b>{field.title()}</b></td>"
                    html += f"<td style='{item1_style}'>{val1}</td>"
                    html += f"<td style='{item2_style}'>{val2}</td>"
                    html += f"</tr>"
                
                html += "</table><br>"
            
            # Recommendation
            if comparison.get("recommendation"):
                html += f"<h3 style='color: #f39c12;'>💡 Öneri:</h3>"
                html += f"<p style='font-size: 14px;'>{comparison['recommendation']}</p>"
            
            self.comparison_text.setHtml(html)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Karşılaştırma yapılırken hata oluştu:\n{str(e)}")
            import traceback
            print(traceback.format_exc())

