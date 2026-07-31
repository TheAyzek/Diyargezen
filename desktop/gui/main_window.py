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

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
desktop_dir = Path(__file__).resolve().parent.parent
if str(desktop_dir) not in sys.path:
    sys.path.insert(0, str(desktop_dir))

try:
    from gui.theme import DARK_FANTASY_QSS, load_custom_fonts
    from gui.web_view import DiyargezerWebView
    from gui.screens.tavern import TavernPage
    from gui.screens.forge import ForgePage
    from gui.screens.character_sheet import CharacterSheetPage
except ImportError:
    from desktop.gui.theme import DARK_FANTASY_QSS, load_custom_fonts
    from desktop.gui.web_view import DiyargezerWebView
    from desktop.gui.screens.tavern import TavernPage
    from desktop.gui.screens.forge import ForgePage
    from desktop.gui.screens.character_sheet import CharacterSheetPage

from etl.pipeline import run_etl_if_needed

logger = logging.getLogger(__name__)

DB_PATH = BASE_DIR / "desktop" / "data" / "offline_pf1e.db"
LOGO_PATH = BASE_DIR / "assets" / "diyargezer_logo.png"


class MainWindow(QMainWindow):
    """Uygulamanın ana penceresi: QWebEngineView ile Web frontend render eder."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Diyargezer — High-Fantasy TTRPG Karakter Yöneticisi")
        self.resize(1280, 800)
        self.setMinimumSize(960, 640)
        self.setWindowState(Qt.WindowMaximized)

        if LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))

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

        # Arka plan otomatik senkronizasyon servisi
        self._sync_thread = BackgroundSyncThread(DB_PATH, parent=self)
        self._sync_thread.start()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Top Control Strip ----
        top_bar = QFrame()
        top_bar.setStyleSheet(
            "QFrame { background-color: #0b0b14; border-bottom: 1px solid rgba(223, 190, 94, 0.3); min-height: 38px; max-height: 38px; }"
        )
        tb_lay = QHBoxLayout(top_bar)
        tb_lay.setContentsMargins(12, 0, 12, 0)
        tb_lay.setSpacing(12)

        if LOGO_PATH.exists():
            logo_lbl = QLabel()
            pm = QPixmap(str(LOGO_PATH)).scaled(
                22, 22, Qt.KeepAspectRatio, Qt.SmoothTransformation,
            )
            logo_lbl.setPixmap(pm)
            tb_lay.addWidget(logo_lbl)

        brand = QLabel("Diyargezer Desktop")
        brand.setStyleSheet("font-family: 'Cinzel', serif; font-size: 14px; font-weight: bold; color: #fced88;")
        tb_lay.addWidget(brand)

        badge = QLabel("✨ High-Fantasy Web Engine")
        badge.setStyleSheet("background-color: rgba(223, 190, 94, 0.15); color: #dfbe5e; border: 1px solid rgba(223, 190, 94, 0.4); border-radius: 4px; padding: 2px 8px; font-size: 11px; font-weight: bold;")
        tb_lay.addWidget(badge)

        tb_lay.addStretch()

        reload_btn = QPushButton("🔄 Yenile (F5)")
        reload_btn.setStyleSheet("background: transparent; color: #e8dbbf; border: 1px solid rgba(255,255,255,0.15); border-radius: 4px; padding: 3px 10px; font-size: 11px; text-transform: none;")
        reload_btn.setCursor(Qt.PointingHandCursor)
        reload_btn.clicked.connect(self._reload_web_view)
        tb_lay.addWidget(reload_btn)

        self._cloud_btn = QPushButton("☁️ Bulut Girişi (Sync)")
        self._cloud_btn.setCursor(Qt.PointingHandCursor)
        self._cloud_btn.setStyleSheet("background-color: rgba(230, 197, 103, 0.15); color: #e6c567; border: 1px solid #e6c567; border-radius: 4px; padding: 3px 10px; font-weight: bold; font-size: 11px; text-transform: none;")
        self._cloud_btn.clicked.connect(self._open_login_dialog)
        tb_lay.addWidget(self._cloud_btn)

        root.addWidget(top_bar)

        # ---- Main Content: QWebEngineView ----
        self._web_view = DiyargezerWebView(self)
        root.addWidget(self._web_view, stretch=1)

        # ---- Status bar ----
        status = QLabel("Hazır  •  PF1e Offline-First SQLite Sync Aktif")
        status.setObjectName("StatusBar")
        self.statusBar().addPermanentWidget(status, stretch=1)
        self.statusBar().setStyleSheet(
            "QStatusBar { background: #0b0b14; border-top: 1px solid rgba(230, 197, 103, 0.2); color: #a8b3cf; font-size: 11px; }"
        )

    def keyPressEvent(self, event) -> None:
        """F5 kısayolu ile sayfayı yenileme."""
        if event.key() == Qt.Key_F5:
            self._reload_web_view()
        else:
            super().keyPressEvent(event)

    def _reload_web_view(self) -> None:
        if hasattr(self, "_web_view"):
            self._web_view.reload_page()

    def _open_login_dialog(self) -> None:
        from desktop.gui.dialogs.login_dialog import LoginDialog
        from desktop.api_client import api_client
        from desktop import local_db
        dlg = LoginDialog(self)
        if dlg.exec() == LoginDialog.Accepted and api_client.is_authenticated():
            local_db.save_local_auth(DB_PATH, api_client.username, api_client.token)
            self._cloud_btn.setText(f"☁️ {api_client.username}")


    def closeEvent(self, event) -> None:
        """Qt kapanırken arka plan iş parçacıklarını güvenle durdur."""
        if hasattr(self, "_sync_thread"):
            self._sync_thread.stop()
        event.accept()


# ======================================================================
# Application Entry Point
# ======================================================================

def run_app() -> None:
    """PySide6 uygulamasını başlat."""
    app = QApplication.instance() or QApplication(sys.argv)
    load_custom_fonts()
    app.setStyleSheet(DARK_FANTASY_QSS)

    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())

