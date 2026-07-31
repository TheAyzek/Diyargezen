"""
Diyargezer Web View Module
==========================
Masaüstü (PySide6) istemcisinde React tabanlı High-Fantasy web uygulamasını
birebir render eden QWebEngineView kapsayıcı sınıfıdır.

Akademik Mimari Notu:
---------------------
Bu sınıf, Web SPA (Single Page Application) frontend'i ile PySide6 native
masaüstü pencere yöneticisi arasında köprü görevi görür. Öncelik sırasına göre:
1. Vite Geliştirici Sunucusu (http://127.0.0.1:5173) - Anlık kod güncellemeleri için
2. FastAPI Sunucusu (http://127.0.0.1:8000) - Yayın (Production) modunda statik SPA dağıtımı için
3. Yerel Statik Dosya / Sunucu Fallback'i - İnternet/Sunucu yokken offline çalışma için
"""

from __future__ import annotations

import logging
import urllib.request
from pathlib import Path
from typing import Optional

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QMenu,
)
from PySide6.QtWebEngineWidgets import QWebEngineView

import sys
import time

logger = logging.getLogger(__name__)

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(getattr(sys, '_MEIPASS', ''))
else:
    BASE_DIR = Path(__file__).resolve().parent.parent.parent

FRONTEND_DIST = BASE_DIR / "web" / "frontend" / "dist"


class DiyargezerWebView(QWidget):
    """
    High-Fantasy Web Arayüzünü PySide6 içerisinde render eden QWebEngineView kapsayıcısı.
    """

    page_loaded = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None) -> None:
        super().__init__(parent)
        self._target_url = self._determine_target_url()
        self._build_ui()

    def _determine_target_url(self) -> str:
        """
        Web uygulamasının sunulduğu aktif adresi tespit eder.
        1. Backend Sunucusu: http://127.0.0.1:8000
        2. Dev Server: http://127.0.0.1:5173
        3. Local Dist Fallback: file://.../dist/index.html
        """
        # Sunucu açılışı için kısa deneme döngüsü (Retry Loop)
        for attempt in range(5):
            try:
                req = urllib.request.urlopen("http://127.0.0.1:8000/", timeout=0.5)
                if req.status == 200:
                    logger.info("WebView backend sunucusu tespit edildi: http://127.0.0.1:8000/")
                    return "http://127.0.0.1:8000/"
            except Exception:
                pass

            try:
                req = urllib.request.urlopen("http://127.0.0.1:5173/", timeout=0.5)
                if req.status == 200:
                    logger.info("WebView dev server tespit edildi: http://127.0.0.1:5173/")
                    return "http://127.0.0.1:5173/"
            except Exception:
                pass

            time.sleep(0.3)

        # 3. Static Dist Fallback
        if FRONTEND_DIST.exists() and (FRONTEND_DIST / "index.html").exists():
            dist_index = (FRONTEND_DIST / "index.html").as_uri()
            logger.info("WebView yerel static dist kullanıyor: %s", dist_index)
            return dist_index

        # Fallback to default local address
        return "http://127.0.0.1:8000/"


    def _build_ui(self) -> None:
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # İlerleme çubuğu (Loading Indicator)
        self._progress_bar = QProgressBar()
        self._progress_bar.setFixedHeight(3)
        self._progress_bar.setTextVisible(False)
        self._progress_bar.setStyleSheet(
            "QProgressBar { background-color: #0f0f1a; border: none; }"
            "QProgressBar::chunk { background: qlineargradient(x1:0, y1:0, x2:1, y2:0, stop:0 #dfbe5e, stop:1 #fced88); }"
        )
        layout.addWidget(self._progress_bar)

        # QWebEngineView Ana Görünümü
        self._web_view = QWebEngineView()
        self._web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._web_view.customContextMenuRequested.connect(self._show_context_menu)

        # Sinyal bağlantıları
        self._web_view.loadProgress.connect(self._on_load_progress)
        self._web_view.loadFinished.connect(self._on_load_finished)

        layout.addWidget(self._web_view, stretch=1)

        # Sayfayı yükle
        self.reload_page()

    def reload_page(self) -> None:
        """Hedef adresi yeniden tespit et ve yükle."""
        self._target_url = self._determine_target_url()
        logger.info("WebView yükleniyor: %s", self._target_url)
        self._progress_bar.setValue(10)
        self._progress_bar.show()
        self._web_view.setUrl(QUrl(self._target_url))

    def navigate_to(self, url_str: str) -> None:
        """Belirtilen URL'e git."""
        self._web_view.setUrl(QUrl(url_str))

    def _on_load_progress(self, progress: int) -> None:
        self._progress_bar.setValue(progress)
        if progress >= 100:
            self._progress_bar.hide()

    def _on_load_finished(self, success: bool) -> None:
        self._progress_bar.hide()
        if not success:
            logger.warning("WebView sayfa yükleme başarısız: %s", self._target_url)
        else:
            logger.info("WebView sayfa başarıyla yüklendi: %s", self._target_url)
        self.page_loaded.emit(success)

    def _show_context_menu(self, pos) -> None:
        """Geliştirici ve gezinme bağlam menüsü."""
        menu = QMenu(self)
        menu.setStyleSheet(
            "QMenu { background-color: #1a1a2e; color: #fcf7ec; border: 1px solid #dfbe5e; border-radius: 6px; padding: 4px; }"
            "QMenu::item:selected { background-color: rgba(223, 190, 94, 0.2); color: #fced88; }"
        )

        reload_act = QAction("🔄 Sayfayı Yenile", self)
        reload_act.triggered.connect(self.reload_page)
        menu.addAction(reload_act)

        back_act = QAction("⬅️ Geri", self)
        back_act.triggered.connect(self._web_view.back)
        menu.addAction(back_act)

        fwd_act = QAction("➡️ İleri", self)
        fwd_act.triggered.connect(self._web_view.forward)
        menu.addAction(fwd_act)

        menu.exec_(self._web_view.mapToGlobal(pos))
