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

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(getattr(sys, '_MEIPASS', ''))
    EXEC_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent
    EXEC_DIR = BASE_DIR

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
desktop_dir = BASE_DIR / "desktop"
if str(desktop_dir) not in sys.path:
    sys.path.insert(0, str(desktop_dir))
backend_dir = BASE_DIR / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

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

try:
    from web.backend.app.core.config import DB_PATH  # type: ignore[import-not-found] # pyright: ignore[reportMissingImports]
except ImportError:
    from app.core.config import DB_PATH  # type: ignore[import-not-found] # pyright: ignore[reportMissingImports]

DB_PATH.parent.mkdir(parents=True, exist_ok=True)
LOGO_PATH = BASE_DIR / "assets" / "diyargezer_logo.png"


_owned_server = None


def ensure_local_server_running():
    """Only return a listener owned by this application, never a discovered URL."""
    global _owned_server
    from desktop.local_server import OwnedLocalServer
    if _owned_server is not None:
        if not _owned_server.is_running():
            raise RuntimeError("Yerel sunucu durdu; uygulamayı yeniden başlatın.")
        return _owned_server

    def load_app():
        from app.main import app
        return app

    _owned_server = OwnedLocalServer(load_app)
    return _owned_server


class MainWindow(QMainWindow):
    """Uygulamanın ana penceresi: QWebEngineView ile Web frontend render eder."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("Diyargezen — Pathfinder 1e Karakter Yöneticisi")
        self.resize(1280, 800)
        self.setMinimumSize(960, 640)
        self.setWindowState(Qt.WindowMaximized)

        if LOGO_PATH.exists():
            self.setWindowIcon(QIcon(str(LOGO_PATH)))

        self._local_server = None
        try:
            self._local_server = ensure_local_server_running()
        except Exception:
            logger.exception("Güvenilir yerel sunucu başlatılamadı")

        from desktop import local_db
        from desktop.api_client import api_client
        local_db.init_local_db(DB_PATH)

        auth_info = local_db.get_local_auth(DB_PATH)
        if auth_info:
            api_client.set_token(auth_info[1], auth_info[0])

        # The owned API lifespan is the sole ETL owner. A second writer could
        # race catalog backup/import while the UI is already querying it.

        self._build_ui()

    # ------------------------------------------------------------------
    # UI
    # ------------------------------------------------------------------

    def _build_ui(self) -> None:
        central = QWidget()
        self.setCentralWidget(central)
        root = QVBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ---- Main Content: QWebEngineView ----
        self._web_view = DiyargezerWebView(self, local_server=self._local_server, storage_path=DB_PATH)
        root.addWidget(self._web_view, stretch=1)

        # ---- Status bar ----
        status = QLabel("PF1e • Masaüstü deposu: SQLite • Senkronizasyon: web v2 kuyruğu")
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
        if self._local_server:
            self._local_server.stop()
        event.accept()


# ======================================================================
# Application Entry Point
# ======================================================================

def run_app() -> None:
    """PySide6 uygulamasını başlat."""
    import os
    os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu-compositing --disable-gpu-rasterization --enable-begin-frame-scheduling"
    from PySide6.QtCore import Qt, QCoreApplication
    QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

    app = QApplication.instance() or QApplication(sys.argv)
    load_custom_fonts()
    app.setStyleSheet(DARK_FANTASY_QSS)



    window = MainWindow()
    window.showMaximized()

    sys.exit(app.exec())
