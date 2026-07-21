"""
Diyargezer Main Window
======================
Persistent left sidebar + QStackedWidget ile yönetilen üç ana ekran:
  - The Tavern  (Dashboard)
  - The Forge   (Creation Wizard)
  - Character Sheet

İş mantığı hiçbir zaman burada yapılmaz; ekranlar ve backend modülleri
aracılığıyla delege edilir.
"""

from __future__ import annotations

import logging
import sys
from pathlib import Path

from PySide6.QtCore import Qt, QSize
from PySide6.QtGui import QIcon, QPixmap
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QStackedWidget, QFrame, QSizePolicy,
)

from gui.theme import DARK_FANTASY_QSS
from gui.screens.tavern import TavernPage
from gui.screens.forge import ForgePage
from gui.screens.character_sheet import CharacterSheetPage
from utils.storage import init_db
from etl.pipeline import run_etl_if_needed

logger = logging.getLogger(__name__)

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
desktop_dir = Path(__file__).resolve().parent.parent
if str(desktop_dir) not in sys.path:
    sys.path.insert(0, str(desktop_dir))

DB_PATH = BASE_DIR / "data" / "characters.db"
LOGO_PATH = BASE_DIR / "assets" / "diyargezer_logo.png"


class MainWindow(QMainWindow):
    """Uygulamanın ana penceresi."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Diyargezer — TTRPG Karakter Yöneticisi")
        self.resize(1100, 720)
        self.setMinimumSize(900, 600)
        # Sunum modu: ekranı kaplayan pencere (taskbar ve X butonu korunur)
        self.setWindowState(Qt.WindowMaximized)

        if LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))

        init_db(DB_PATH)
        from desktop import local_db
        from desktop.api_client import api_client
        from desktop.sync_engine import BackgroundSyncThread
        local_db.init_local_db(DB_PATH)

        auth_info = local_db.get_local_auth(DB_PATH)
        if auth_info:
            api_client.set_token(auth_info[1], auth_info[0])

        try:
            totals = run_etl_if_needed(DB_PATH)
            logger.info("Oyun verisi hazır: %s", totals)
        except Exception as exc:
            logger.warning("ETL başlatılamadı (JSON fallback aktif): %s", exc)

        self._build_ui()
        self._navigate(0)

        # Arka plan otomatik senkronizasyon servisi
        self._sync_thread = BackgroundSyncThread(DB_PATH, parent=self)
        self._sync_thread.start()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Sidebar ----
        sidebar = QFrame()
        sidebar.setObjectName("Sidebar")
        sidebar.setFixedWidth(220)
        sb_lay = QVBoxLayout(sidebar)
        sb_lay.setContentsMargins(12, 16, 12, 16)
        sb_lay.setSpacing(4)

        if LOGO_PATH.exists():
            logo_lbl = QLabel()
            pm = QPixmap(str(LOGO_PATH)).scaled(
                72, 72, Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            logo_lbl.setPixmap(pm)
            logo_lbl.setAlignment(Qt.AlignCenter)
            sb_lay.addWidget(logo_lbl)

        brand = QLabel("Diyargezer")
        brand.setObjectName("SidebarTitle")
        brand.setAlignment(Qt.AlignCenter)
        sb_lay.addWidget(brand)

        subtitle = QLabel("TTRPG Karakter Yönetimi")
        subtitle.setObjectName("SidebarSubtitle")
        subtitle.setAlignment(Qt.AlignCenter)
        sb_lay.addWidget(subtitle)

        sb_lay.addSpacing(24)

        self._nav_buttons: list[QPushButton] = []
        nav_items = [
            ("The Tavern", "Kayıtlı karakterler"),
            ("The Forge", "Yeni karakter oluştur"),
            ("Character Sheet", "Karakter detayları"),
        ]
        for i, (text, tooltip) in enumerate(nav_items):
            btn = QPushButton(f"  {text}")
            btn.setObjectName("NavButton")
            btn.setCheckable(True)
            btn.setToolTip(tooltip)
            btn.setCursor(Qt.PointingHandCursor)
            btn.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Fixed)
            btn.setMinimumHeight(40)
            btn.clicked.connect(lambda checked, idx=i: self._navigate(idx))
            sb_lay.addWidget(btn)
            self._nav_buttons.append(btn)

        sb_lay.addStretch()

        self._cloud_btn = QPushButton("☁️ Bulut Girişi (Sync)")
        self._cloud_btn.setCursor(Qt.PointingHandCursor)
        self._cloud_btn.setStyleSheet("background-color: rgba(201, 168, 76, 0.15); color: #c9a84c; border: 1px solid #c9a84c; border-radius: 4px; padding: 6px; font-weight: bold;")
        self._cloud_btn.clicked.connect(self._open_login_dialog)
        sb_lay.addWidget(self._cloud_btn)

        version_lbl = QLabel("v2.0  •  PySide6 + Cloud")
        version_lbl.setObjectName("SidebarSubtitle")
        version_lbl.setAlignment(Qt.AlignCenter)
        sb_lay.addWidget(version_lbl)

        root.addWidget(sidebar)

        # ---- Content area ----
        self._stack = QStackedWidget()
        root.addWidget(self._stack, stretch=1)

        self._tavern = TavernPage(DB_PATH)
        self._forge = ForgePage(DB_PATH)
        self._sheet = CharacterSheetPage(DB_PATH)

        self._stack.addWidget(self._tavern)
        self._stack.addWidget(self._forge)
        self._stack.addWidget(self._sheet)

        # ---- Signals ----
        self._tavern.character_selected.connect(self._on_character_selected)
        self._forge.character_created.connect(self._on_character_created)

        # ---- Status bar ----
        status = QLabel("Hazır")
        status.setObjectName("StatusBar")
        self.statusBar().addPermanentWidget(status, stretch=1)
        self.statusBar().setStyleSheet(
            "QStatusBar { background: #0d0d18; border-top: 1px solid #30363d; }"
        )

    # ------------------------------------------------------------------
    # Navigation
    # ------------------------------------------------------------------

    def _navigate(self, index: int) -> None:
        self._stack.setCurrentIndex(index)
        for i, btn in enumerate(self._nav_buttons):
            btn.setChecked(i == index)

    def _on_character_selected(self, record_id: int) -> None:
        self._sheet.load_character(record_id)
        self._navigate(2)

    def _on_character_created(self, record_id: int) -> None:
        self._sheet.load_character(record_id)
        self._navigate(2)

    def _open_login_dialog(self) -> None:
        from desktop.gui.dialogs.login_dialog import LoginDialog
        from desktop.api_client import api_client
        from desktop import local_db
        dlg = LoginDialog(self)
        if dlg.exec() == LoginDialog.Accepted and api_client.is_authenticated():
            local_db.save_local_auth(DB_PATH, api_client.username, api_client.token)
            self._cloud_btn.setText(f"☁️ {api_client.username}")
            self._tavern.refresh()


# ======================================================================
# Application Entry Point
# ======================================================================

def run_app() -> None:
    """PySide6 uygulamasını başlat."""
    app = QApplication.instance() or QApplication(sys.argv)
    app.setStyleSheet(DARK_FANTASY_QSS)

    window = MainWindow()
    window.showMaximized()  # Tam ekran kaplayan, güvenli başlangıç

    sys.exit(app.exec())
