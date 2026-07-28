"""
High-Fantasy QSS Theme for Diyargezen Desktop App
==================================================
Web platformu ile birebir uyumlu High-Fantasy (Gold, Obsidian, Midnight & Parchment) QSS Teması.

Palet:
  Midnight        #0f0f1a   Ana zemin
  Slate           #1a1a2e   İkincil zemin / kartlar
  Ink             #22223b   Girdi / Eleman zemin
  Gold            #e6c567   Ana altın vurgu
  Gold Bright     #fced88   Parlak altın başlık ve değerler
  Gold Dim        #a38968   İkincil kenarlık ve pasif vurgular
  Text Primary    #fcf7ec   Net birincil yazı
  Text Secondary  #e8dbbf   İkincil yazı
  Text Muted      #a8b3cf   Devre dışı / ipucu metni
  Crimson / Ruby  #ff5270   Uyarı / silme
  Emerald         #47d159   Başarı / bonus
  Violet          #8e82ff   Büyü / Gizemli aksan
"""

from pathlib import Path
import logging
from PySide6.QtGui import QFontDatabase

logger = logging.getLogger(__name__)

def load_custom_fonts() -> None:
    """assets/fonts dizinindeki custom TTF fontlarını PySide6 QFontDatabase'e yükler."""
    fonts_dir = Path(__file__).resolve().parent.parent.parent / "assets" / "fonts"
    if not fonts_dir.exists():
        logger.warning("Font dizini bulunamadı: %s", fonts_dir)
        return

    for font_file in fonts_dir.glob("*.ttf"):
        font_id = QFontDatabase.addApplicationFont(str(font_file))
        if font_id != -1:
            families = QFontDatabase.applicationFontFamilies(font_id)
            logger.info("Font yüklendi: %s (%s)", font_file.name, families)
        else:
            logger.warning("Font yüklenemedi: %s", font_file.name)

DARK_FANTASY_QSS = """
/* ======================================================
   GLOBAL STYLES
   ====================================================== */
QWidget {
    background-color: #0f0f1a;
    color: #fcf7ec;
    font-family: "Cinzel", "EB Garamond", "Segoe UI", sans-serif;
    font-size: 14px;
}

/* ======================================================
   MAIN WINDOW & DIALOGS
   ====================================================== */
QMainWindow, QDialog {
    background-color: #0f0f1a;
}

/* ======================================================
   SIDEBAR & TOOLBAR
   ====================================================== */
QFrame#Sidebar {
    background-color: #1a1a2e;
    border-right: 1px solid rgba(230, 197, 103, 0.25);
}

/* ======================================================
   LABELS & HEADERS
   ====================================================== */
QLabel {
    background: transparent;
    color: #fcf7ec;
}

QLabel#SidebarTitle {
    font-size: 22px;
    font-weight: bold;
    font-family: "Cinzel", serif;
    color: #fced88;
    letter-spacing: 1px;
}

QLabel#SidebarSubtitle {
    font-size: 11px;
    color: #e8dbbf;
    letter-spacing: 0.5px;
}

QLabel#PageTitle {
    font-size: 24px;
    font-weight: bold;
    font-family: "Cinzel", serif;
    color: #fced88;
    padding: 10px 0;
}

QLabel#SectionHeader {
    font-size: 15px;
    font-weight: bold;
    font-family: "Cinzel", serif;
    color: #e6c567;
    border-bottom: 1px solid rgba(230, 197, 103, 0.3);
    padding-bottom: 4px;
    margin-top: 8px;
    text-transform: uppercase;
}

QLabel#StatValue {
    font-size: 20px;
    font-weight: bold;
    font-family: "DM Mono", "Consolas", monospace;
    color: #fced88;
}

QLabel#StatusBar {
    font-size: 11px;
    color: #a8b3cf;
    padding: 4px 12px;
    background-color: #1a1a2e;
    border-top: 1px solid rgba(230, 197, 103, 0.2);
}

/* ======================================================
   PUSH BUTTONS (GOLD & CRIMSON HIGH-FANTASY)
   ====================================================== */
QPushButton {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #c9a84c, stop:1 #9d7e2e);
    color: #0b0b14;
    border: 1px solid #d4af37;
    border-radius: 8px;
    padding: 8px 18px;
    font-weight: 800;
    font-family: "Cinzel", serif;
    font-size: 13px;
    letter-spacing: 0.5px;
    text-transform: uppercase;
    min-height: 24px;
}

QPushButton:hover {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #e6c567, stop:1 #b89535);
    border-color: #fced88;
    color: #04030a;
}

QPushButton:pressed {
    background: #9d7e2e;
    color: #04030a;
}

QPushButton:disabled {
    background: #1a1a2e;
    color: #a8b3cf;
    border-color: rgba(230, 197, 103, 0.2);
}

QPushButton#NavButton {
    background: transparent;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 16px;
    font-size: 14px;
    color: #e8dbbf;
    font-family: "Cinzel", serif;
}

QPushButton#NavButton:hover {
    background: rgba(230, 197, 103, 0.12);
    color: #fced88;
}

QPushButton#NavButton:checked {
    background: rgba(230, 197, 103, 0.2);
    color: #fced88;
    border-left: 4px solid #e6c567;
}

QPushButton#DangerButton {
    border-color: #ff5270;
    color: #ff5270;
    background: rgba(255, 82, 112, 0.15);
}

QPushButton#DangerButton:hover {
    background: #ff5270;
    color: #0f0f1a;
}

QPushButton#SuccessButton {
    border-color: #47d159;
    color: #47d159;
    background: rgba(71, 209, 89, 0.15);
}

QPushButton#SuccessButton:hover {
    background: #47d159;
    color: #0f0f1a;
}

/* ======================================================
   INPUT FIELDS (RUNIC SLATE INPUTS)
   ====================================================== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #1e1e36;
    color: #fcf7ec;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 8px 12px;
    font-family: "EB Garamond", serif;
    font-size: 14px;
    selection-background-color: #e6c567;
    selection-color: #0f0f1a;
}

QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {
    border: 2px solid #e6c567;
    background-color: #252542;
}

QLineEdit:disabled {
    background-color: #1a1a2e;
    color: #a8b3cf;
}

/* ======================================================
   COMBO BOX (RUNIC SELECT)
   ====================================================== */
QComboBox {
    background-color: #1e1e36;
    color: #fcf7ec;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 8px 12px;
    min-height: 24px;
    font-family: "EB Garamond", serif;
    font-size: 14px;
}

QComboBox:hover { border-color: #e6c567; }

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1a1a2e;
    color: #fcf7ec;
    border: 1px solid #e6c567;
    selection-background-color: #e6c567;
    selection-color: #0f0f1a;
}

/* ======================================================
   SPIN BOX
   ====================================================== */
QSpinBox {
    background-color: #1e1e36;
    color: #fced88;
    border: 1px solid rgba(255, 255, 255, 0.12);
    border-radius: 8px;
    padding: 6px 10px;
    font-family: "DM Mono", monospace;
    font-size: 15px;
    font-weight: bold;
}

QSpinBox:focus { border-color: #e6c567; }

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #22223b;
    border: none;
    width: 20px;
    border-radius: 4px;
}

/* ======================================================
   TAB WIDGET (EPIC TABS)
   ====================================================== */
QTabWidget::pane {
    background-color: #111120;
    border: 1px solid rgba(201, 168, 76, 0.25);
    border-radius: 12px;
}

QTabBar::tab {
    background-color: #1a1a2e;
    color: #e8dbbf;
    border: 1px solid rgba(255, 255, 255, 0.1);
    border-bottom: none;
    padding: 10px 22px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    font-family: "Cinzel", serif;
    font-size: 12px;
    font-weight: bold;
}

QTabBar::tab:selected {
    background-color: #111120;
    color: #fced88;
    border-color: rgba(201, 168, 76, 0.45);
    border-bottom: 3px solid #e6c567;
}

QTabBar::tab:hover:!selected {
    background-color: #22223b;
    color: #fcf7ec;
}

/* ======================================================
   SCROLL AREA / SCROLL BAR
   ====================================================== */
QScrollArea {
    background: transparent;
    border: none;
}

QScrollBar:vertical {
    background-color: #0f0f1a;
    width: 8px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #22223b;
    border: 1px solid rgba(201, 168, 76, 0.15);
    border-radius: 4px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover { background-color: #e6c567; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background-color: #0f0f1a;
    height: 8px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #22223b;
    border: 1px solid rgba(201, 168, 76, 0.15);
    border-radius: 4px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover { background-color: #e6c567; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ======================================================
   FRAMES / CARDS (GLASS CARDS)
   ====================================================== */
QFrame#Card {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:1, stop:0 #1c1c32, stop:1 #111120);
    border: 1px solid rgba(201, 168, 76, 0.25);
    border-radius: 12px;
    padding: 16px;
}

QFrame#Card:hover {
    border-color: rgba(201, 168, 76, 0.55);
}

QFrame#StepPanel {
    background-color: #1a1a2e;
    border: 1px solid rgba(201, 168, 76, 0.25);
    border-radius: 12px;
    padding: 18px;
}

/* ======================================================
   GROUP BOX
   ====================================================== */
QGroupBox {
    background-color: #111120;
    border: 1px solid rgba(201, 168, 76, 0.25);
    border-radius: 12px;
    margin-top: 16px;
    padding-top: 24px;
    font-weight: bold;
    font-family: "Cinzel", serif;
    color: #fced88;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 12px;
    color: #fced88;
    font-family: "Cinzel", serif;
}

/* ======================================================
   TABLE WIDGET
   ====================================================== */
QTableWidget {
    background-color: #111120;
    color: #fcf7ec;
    gridline-color: #2a2a48;
    border: 1px solid rgba(201, 168, 76, 0.25);
    border-radius: 8px;
    selection-background-color: #e6c567;
    selection-color: #0f0f1a;
}

QHeaderView::section {
    background-color: #1a1a2e;
    color: #fced88;
    border: 1px solid rgba(230, 197, 103, 0.2);
    padding: 8px;
    font-weight: bold;
    font-family: "Cinzel", serif;
}

/* ======================================================
   PROGRESS BAR
   ====================================================== */
QProgressBar {
    background-color: #1e1e36;
    border: 1px solid rgba(230, 197, 103, 0.3);
    border-radius: 6px;
    text-align: center;
    color: #fced88;
    height: 20px;
    font-family: "DM Mono", monospace;
}

QProgressBar::chunk {
    background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #c9a84c, stop:1 #e6c567);
    border-radius: 5px;
}

/* ======================================================
   TOOLTIP
   ====================================================== */
QToolTip {
    background-color: #1a1a2e;
    color: #fcf7ec;
    border: 1px solid #e6c567;
    padding: 8px;
    border-radius: 6px;
    font-family: "EB Garamond", serif;
}
"""
