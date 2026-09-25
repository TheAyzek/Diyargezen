"""
Diyargezer Web View Module
==========================
Masaüstü (PySide6) istemcisinde React tabanlı High-Fantasy web uygulamasını
birebir render eden QWebEngineView kapsayıcı sınıfıdır.

Yalnızca uygulamanın kendi başlattığı yerel sunucu yüklenir. Port keşfi,
başka sunucuya veya file:// adresine otomatik geri dönüş yapılmaz.
"""

from __future__ import annotations

import logging
import json
from typing import Optional

from PySide6.QtCore import Qt, QUrl, Signal
from PySide6.QtGui import QAction
from PySide6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QProgressBar, QFrame, QMenu,
)
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWebEngineCore import QWebEnginePage

from desktop.local_server import allows_navigation

logger = logging.getLogger(__name__)

class DebugWebPage(QWebEnginePage):
    """JavaScript konsol mesajlarını Python loglarına yönlendiren QWebEnginePage."""

    _JS_LEVELS = {
        QWebEnginePage.JavaScriptConsoleMessageLevel.InfoMessageLevel: "JS:INFO",
        QWebEnginePage.JavaScriptConsoleMessageLevel.WarningMessageLevel: "JS:WARN",
        QWebEnginePage.JavaScriptConsoleMessageLevel.ErrorMessageLevel: "JS:ERROR",
    }

    def __init__(self, parent, local_server):
        super().__init__(parent)
        self._local_server = local_server

    def acceptNavigationRequest(self, url, navigation_type, is_main_frame):
        server = self._local_server
        return bool(server and server.is_running() and allows_navigation(
            url.toString(), server.origin, main_frame=is_main_frame,
        ))

    def createWindow(self, window_type):
        # No unguarded popup page inheriting a future native bridge.
        return None

    def javaScriptConsoleMessage(self, level, message, line, source_id):
        tag = self._JS_LEVELS.get(level, "JS")
        logger.info("[%s] %s (line %s) — %s", tag, message, line, source_id)


class DiyargezerWebView(QWidget):
    """
    High-Fantasy Web Arayüzünü PySide6 içerisinde render eden QWebEngineView kapsayıcısı.
    """

    page_loaded = Signal(bool)

    def __init__(self, parent: Optional[QWidget] = None, *, local_server=None, storage_path=None) -> None:
        super().__init__(parent)
        self._local_server = local_server
        self._storage_path = storage_path
        self._target_url = local_server.origin + "/" if local_server else None
        self._build_ui()


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

        self._error_label = QLabel(
            "Güvenilir yerel sunucu açılamadı veya durdu.\n"
            "8000 portunu kullanan başka bir Diyargezen/sunucu varsa kapatıp uygulamayı yeniden başlatın.\n"
            "Yerel kayıtlarınız silinmedi; güvenlik için başka bir sunucuya bağlanılmadı."
        )
        self._error_label.setWordWrap(True)
        self._error_label.setAlignment(Qt.AlignCenter)
        self._error_label.hide()
        layout.addWidget(self._error_label)

        # QWebEngineView Ana Görünümü — DebugWebPage ile JS hataları yakalanıyor
        self._web_view = QWebEngineView()
        self._debug_page = DebugWebPage(self._web_view, self._local_server)
        self._web_view.setPage(self._debug_page)
        if self._local_server and self._storage_path:
            self._install_storage_bridge()
        from PySide6.QtWebEngineCore import QWebEngineSettings
        settings = self._web_view.settings()
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessRemoteUrls, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalContentCanAccessFileUrls, False)
        settings.setAttribute(QWebEngineSettings.WebAttribute.LocalStorageEnabled, True)

        self._web_view.setContextMenuPolicy(Qt.CustomContextMenu)
        self._web_view.customContextMenuRequested.connect(self._show_context_menu)

        # Sinyal bağlantıları
        self._web_view.loadProgress.connect(self._on_load_progress)
        self._web_view.loadFinished.connect(self._on_load_finished)

        layout.addWidget(self._web_view, stretch=1)

        # Sayfayı yükle
        self.reload_page()

    def _install_storage_bridge(self):
        from PySide6.QtCore import QFile, QIODevice
        from PySide6.QtWebChannel import QWebChannel
        from PySide6.QtWebEngineCore import QWebEngineScript
        from desktop.web_bridge import StorageBridge
        source = QFile(':/qtwebchannel/qwebchannel.js')
        if not source.open(QIODevice.ReadOnly):
            raise RuntimeError('Qt SQLite köprü kaynağı bulunamadı')
        try:
            channel_js = bytes(source.readAll()).decode('utf-8')
        finally:
            source.close()
        self._storage_bridge = StorageBridge(self._debug_page, self._local_server, self._storage_path)
        self._channel = QWebChannel(self._debug_page)
        self._channel.registerObject('storage', self._storage_bridge)
        self._debug_page.setWebChannel(self._channel)
        bootstrap = '''
        (() => {
          if (location.origin !== ORIGIN) return;
          const ready = new Promise((resolve, reject) => {
            const startup = setTimeout(() => reject(new Error('SQLite köprüsü açılamadı')), 10000);
            new QWebChannel(qt.webChannelTransport, channel => {
              clearTimeout(startup);
              resolve(request => new Promise((done, fail) => {
                const timer = setTimeout(() => fail(new Error('SQLite yanıt vermedi; tekrar yükleyin')), 15000);
                channel.objects.storage.dispatch(JSON.stringify({...request, secret: SECRET}), raw => {
                  clearTimeout(timer);
                  try { done(JSON.parse(raw)); } catch (error) { fail(error); }
                });
              }));
            });
          });
          Object.defineProperty(window, '__diyargezenNativeReady', { value: ready });
        })();
        '''.replace('ORIGIN', json.dumps(self._local_server.origin)).replace('SECRET', json.dumps(self._storage_bridge.secret))
        script = QWebEngineScript()
        script.setName('diyargezen-sqlite-storage')
        script.setInjectionPoint(QWebEngineScript.DocumentCreation)
        script.setWorldId(QWebEngineScript.MainWorld)
        script.setRunsOnSubFrames(False)
        script.setSourceCode(channel_js + '\n' + bootstrap)
        self._debug_page.scripts().insert(script)


    def reload_page(self) -> None:
        """Reload only the owned origin; never rediscover a server."""
        if not self._local_server or not self._local_server.is_running():
            self._web_view.stop()
            self._web_view.hide()
            self._progress_bar.hide()
            self._error_label.show()
            return
        self._error_label.hide()
        self._web_view.show()
        logger.info("WebView yükleniyor: %s", self._target_url)
        self._progress_bar.setValue(10)
        self._progress_bar.show()
        self._web_view.setUrl(QUrl(self._target_url))

    def navigate_to(self, url_str: str) -> None:
        """Belirtilen URL'e git."""
        if self._local_server and self._local_server.is_running() and allows_navigation(
            url_str, self._local_server.origin, main_frame=True,
        ):
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
            # DOM durumunu kontrol et — beyaz ekran teşhisi
            self._web_view.page().runJavaScript(
                """
                (function() {
                    var root = document.getElementById('root');
                    var info = {
                        rootExists: !!root,
                        childCount: root ? root.childElementCount : -1,
                        innerHTMLLen: root ? root.innerHTML.length : 0,
                        bodyBg: getComputedStyle(document.body).backgroundColor,
                        title: document.title,
                        url: window.location.href,
                        preview: root ? root.innerHTML.substring(0, 300) : 'NO ROOT'
                    };
                    console.log('[DOM-DEBUG] ' + JSON.stringify(info));
                    return JSON.stringify(info);
                })()
                """,
                self._on_dom_debug
            )
        self.page_loaded.emit(success)

    def _on_dom_debug(self, result: str) -> None:
        """DOM debug sonucunu logla."""
        logger.info("DOM Debug: %s", result)


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
