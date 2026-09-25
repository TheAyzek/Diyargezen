"""Real Qt/QWebChannel smoke test, offscreen, isolated DB and loopback server."""
import os
from pathlib import Path
import subprocess
import sys


def test_real_qt_channel_persists_to_sqlite(tmp_path):
    env = {**os.environ, 'QT_QPA_PLATFORM': 'offscreen',
           'QTWEBENGINE_CHROMIUM_FLAGS': '--disable-gpu'}
    result = subprocess.run([sys.executable, __file__, str(tmp_path / 'qt.db')],
                            env=env, capture_output=True, text=True, timeout=35)
    assert result.returncode == 0, result.stdout + result.stderr
    assert 'QT_SQLITE_OK' in result.stdout


def _probe(path):
    sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
    from fastapi import FastAPI
    from fastapi.responses import HTMLResponse
    from PySide6.QtCore import QTimer
    from PySide6.QtWidgets import QApplication
    from desktop.local_server import OwnedLocalServer
    from desktop.gui.web_view import DiyargezerWebView
    from desktop.web_storage import WebStorage
    application = QApplication([])
    backend = FastAPI()

    @backend.get('/')
    def index():
        return HTMLResponse('<html><body><div id="root">Probe</div></body></html>')

    server = OwnedLocalServer(lambda: backend, port=0)
    view = DiyargezerWebView(local_server=server, storage_path=path)
    outcome = []

    def loaded(ok):
        if not ok:
            application.exit(2)
            return
        view._web_view.page().runJavaScript('''
          (async () => {
            try {
              const call = await window.__diyargezenNativeReady;
              const session = {authenticated:false, token:'', owner:'guest'};
              const saved = await call({session, method:'save', args:{character:{name:'Qt hero',system:'pf1e',data:{level:1}}}});
              const rows = await call({session, method:'all', args:{}});
              window.probeResult = saved.ok && rows.ok && rows.value.length === 1 ? 'ok' : JSON.stringify({saved,rows});
            } catch (error) { window.probeResult = String(error); }
          })();
        ''')

    def poll():
        def checked(value):
            if value:
                outcome.append(value)
                application.quit()
        view._web_view.page().runJavaScript('window.probeResult || null', checked)

    view.page_loaded.connect(loaded)
    timer = QTimer()
    timer.timeout.connect(poll)
    timer.start(100)
    QTimer.singleShot(20000, application.quit)
    try:
        application.exec()
        assert outcome == ['ok'], outcome
        records = WebStorage(path).execute('guest', 'all', {})
        assert records[0]['name'] == 'Qt hero' and records[0]['is_dirty']
        print('QT_SQLITE_OK')
    finally:
        view._web_view.stop()
        view.close()
        server.stop()


if __name__ == '__main__':
    _probe(Path(sys.argv[1]))
