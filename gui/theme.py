"""
Dark Fantasy QSS Theme
======================
"Diyargezer" masaüstü uygulaması için tam QSS (Qt Style Sheet) teması.

Palet:
  Midnight   #0f0f1a   En koyu arka plan
  Dark Slate #1a1a2e   Panel / kart arka planı
  Deep Blue  #16213e   Sidebar / vurgulu panel
  Ink        #22223b   Giriş alanları
  Border     #30363d   Genel kenarlık
  Gold       #c9a84c   Buton / vurgu / başlık
  Bronze     #8b7355   İkincil buton
  Parchment  #f0e6d2   Birincil metin
  Aged       #d4c5a9   İkincil metin
  Muted      #8b949e   Devre dışı / ipucu
  Ruby       #e94560   Uyarı / silme
  Emerald    #3fb950   Başarı
"""

DARK_FANTASY_QSS = """
/* ======================================================
   GLOBAL
   ====================================================== */
QWidget {
    background-color: #0f0f1a;
    color: #f0e6d2;
    font-family: "Segoe UI", "Noto Sans", sans-serif;
    font-size: 13px;
}

/* ======================================================
   MAIN WINDOW
   ====================================================== */
QMainWindow {
    background-color: #0f0f1a;
}

/* ======================================================
   SIDEBAR
   ====================================================== */
QFrame#Sidebar {
    background-color: #0d0d18;
    border-right: 2px solid #c9a84c;
}

/* ======================================================
   LABELS
   ====================================================== */
QLabel {
    background: transparent;
    color: #f0e6d2;
}

QLabel#SidebarTitle {
    font-size: 20px;
    font-weight: bold;
    color: #c9a84c;
}

QLabel#SidebarSubtitle {
    font-size: 11px;
    color: #8b949e;
}

QLabel#PageTitle {
    font-size: 22px;
    font-weight: bold;
    color: #c9a84c;
    padding: 8px 0;
}

QLabel#SectionHeader {
    font-size: 15px;
    font-weight: bold;
    color: #d4c5a9;
    border-bottom: 1px solid #30363d;
    padding-bottom: 4px;
    margin-top: 6px;
}

QLabel#StatValue {
    font-size: 20px;
    font-weight: bold;
    color: #c9a84c;
}

QLabel#StatusBar {
    font-size: 11px;
    color: #8b949e;
    padding: 4px 12px;
    background-color: #0d0d18;
    border-top: 1px solid #30363d;
}

/* ======================================================
   PUSH BUTTONS
   ====================================================== */
QPushButton {
    background-color: #1a1a2e;
    color: #f0e6d2;
    border: 1px solid #c9a84c;
    border-radius: 6px;
    padding: 8px 18px;
    font-weight: bold;
    min-height: 20px;
}

QPushButton:hover {
    background-color: #c9a84c;
    color: #0f0f1a;
}

QPushButton:pressed {
    background-color: #8b7355;
    color: #0f0f1a;
}

QPushButton:disabled {
    background-color: #16213e;
    color: #8b949e;
    border-color: #30363d;
}

QPushButton#NavButton {
    background-color: transparent;
    border: none;
    border-radius: 8px;
    text-align: left;
    padding: 10px 16px;
    font-size: 14px;
    color: #d4c5a9;
}

QPushButton#NavButton:hover {
    background-color: #1a1a2e;
    color: #c9a84c;
}

QPushButton#NavButton:checked {
    background-color: #16213e;
    color: #c9a84c;
    border-left: 3px solid #c9a84c;
}

QPushButton#DangerButton {
    border-color: #e94560;
    color: #e94560;
}

QPushButton#DangerButton:hover {
    background-color: #e94560;
    color: #0f0f1a;
}

QPushButton#SuccessButton {
    border-color: #3fb950;
    color: #3fb950;
}

QPushButton#SuccessButton:hover {
    background-color: #3fb950;
    color: #0f0f1a;
}

/* ======================================================
   INPUT FIELDS
   ====================================================== */
QLineEdit, QTextEdit, QPlainTextEdit {
    background-color: #22223b;
    color: #f0e6d2;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    selection-background-color: #c9a84c;
    selection-color: #0f0f1a;
}

QLineEdit:focus, QTextEdit:focus {
    border-color: #c9a84c;
}

QLineEdit:disabled {
    background-color: #16213e;
    color: #8b949e;
}

/* ======================================================
   COMBO BOX
   ====================================================== */
QComboBox {
    background-color: #22223b;
    color: #f0e6d2;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 6px 10px;
    min-height: 22px;
}

QComboBox:hover { border-color: #c9a84c; }

QComboBox::drop-down {
    border: none;
    width: 24px;
}

QComboBox QAbstractItemView {
    background-color: #1a1a2e;
    color: #f0e6d2;
    border: 1px solid #c9a84c;
    selection-background-color: #c9a84c;
    selection-color: #0f0f1a;
}

/* ======================================================
   SPIN BOX
   ====================================================== */
QSpinBox {
    background-color: #22223b;
    color: #f0e6d2;
    border: 1px solid #30363d;
    border-radius: 6px;
    padding: 4px 8px;
}

QSpinBox:focus { border-color: #c9a84c; }

QSpinBox::up-button, QSpinBox::down-button {
    background-color: #1a1a2e;
    border: none;
    width: 18px;
}

/* ======================================================
   TAB WIDGET
   ====================================================== */
QTabWidget::pane {
    background-color: #1a1a2e;
    border: 1px solid #30363d;
    border-radius: 4px;
}

QTabBar::tab {
    background-color: #16213e;
    color: #d4c5a9;
    border: 1px solid #30363d;
    border-bottom: none;
    padding: 8px 20px;
    margin-right: 2px;
    border-top-left-radius: 6px;
    border-top-right-radius: 6px;
}

QTabBar::tab:selected {
    background-color: #1a1a2e;
    color: #c9a84c;
    border-color: #c9a84c;
    font-weight: bold;
}

QTabBar::tab:hover:!selected {
    background-color: #1a1a2e;
    color: #f0e6d2;
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
    width: 10px;
    border: none;
}

QScrollBar::handle:vertical {
    background-color: #30363d;
    border-radius: 5px;
    min-height: 30px;
}

QScrollBar::handle:vertical:hover { background-color: #c9a84c; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

QScrollBar:horizontal {
    background-color: #0f0f1a;
    height: 10px;
    border: none;
}

QScrollBar::handle:horizontal {
    background-color: #30363d;
    border-radius: 5px;
    min-width: 30px;
}

QScrollBar::handle:horizontal:hover { background-color: #c9a84c; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0; }

/* ======================================================
   FRAMES / CARDS
   ====================================================== */
QFrame#Card {
    background-color: #1a1a2e;
    border: 1px solid #30363d;
    border-radius: 10px;
    padding: 12px;
}

QFrame#Card:hover {
    border-color: #c9a84c;
}

QFrame#StepPanel {
    background-color: #16213e;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 16px;
}

/* ======================================================
   GROUP BOX
   ====================================================== */
QGroupBox {
    background-color: #1a1a2e;
    border: 1px solid #30363d;
    border-radius: 8px;
    margin-top: 12px;
    padding-top: 20px;
    font-weight: bold;
    color: #d4c5a9;
}

QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top left;
    padding: 2px 10px;
    color: #c9a84c;
}

/* ======================================================
   TABLE WIDGET
   ====================================================== */
QTableWidget {
    background-color: #1a1a2e;
    color: #f0e6d2;
    gridline-color: #30363d;
    border: 1px solid #30363d;
    border-radius: 4px;
    selection-background-color: #c9a84c;
    selection-color: #0f0f1a;
}

QHeaderView::section {
    background-color: #16213e;
    color: #c9a84c;
    border: 1px solid #30363d;
    padding: 6px;
    font-weight: bold;
}

/* ======================================================
   PROGRESS BAR
   ====================================================== */
QProgressBar {
    background-color: #22223b;
    border: 1px solid #30363d;
    border-radius: 6px;
    text-align: center;
    color: #f0e6d2;
    height: 18px;
}

QProgressBar::chunk {
    background-color: #c9a84c;
    border-radius: 5px;
}

/* ======================================================
   TOOLTIP
   ====================================================== */
QToolTip {
    background-color: #1a1a2e;
    color: #f0e6d2;
    border: 1px solid #c9a84c;
    padding: 6px;
    border-radius: 4px;
}
"""
