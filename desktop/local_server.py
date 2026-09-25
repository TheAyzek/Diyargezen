"""Own the loopback listener before loading the desktop backend.

Never discover/trust a server by its HTTP health response. Keep a duplicate
listener open until shutdown so a crashed worker cannot surrender the origin
to another process while the window is open.
"""
from __future__ import annotations

import socket
import logging
import threading
import time
from urllib.parse import urlsplit


def allows_navigation(url: str, origin: str, *, main_frame: bool) -> bool:
    """Exact loopback origin, plus same-origin blob PDFs in child frames."""
    if url == "about:blank":
        return True
    if url.startswith("blob:"):
        if main_frame:
            return False
        url = url[5:]
    try:
        target, trusted = urlsplit(url), urlsplit(origin)
        return (
            trusted.scheme == target.scheme == "http"
            and trusted.hostname == target.hostname == "127.0.0.1"
            and trusted.port == target.port
            and target.username is None and target.password is None
        )
    except ValueError:
        return False


class OwnedLocalServer:
    def __init__(self, app_factory, *, port: int = 8000, timeout: float = 30):
        import uvicorn

        self._socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server = None
        self._thread = None
        self._worker_socket = None
        try:
            if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
                self._socket.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
            # Fixed production port preserves the existing IndexedDB origin.
            # A busy port is an error, never a reason to adopt another server.
            self._socket.bind(("127.0.0.1", port))
            self._socket.listen(128)
            self.origin = f"http://127.0.0.1:{self._socket.getsockname()[1]}"
            app = app_factory()
            self._worker_socket = self._socket.dup()
            self._server = uvicorn.Server(uvicorn.Config(
                app, host="127.0.0.1", port=self._socket.getsockname()[1],
                log_level="warning", loop="asyncio", timeout_graceful_shutdown=2,
            ))
            self._thread = threading.Thread(target=self._run, daemon=True, name="diyargezen-local-api")
            self._thread.start()
            deadline = time.monotonic() + timeout
            while not self.is_running():
                if not self._thread.is_alive() or time.monotonic() >= deadline:
                    raise RuntimeError("Gömülü sunucu hazır hale gelemedi; uygulamayı yeniden başlatın.")
                time.sleep(0.025)
        except BaseException:
            self.stop()
            raise

    def _run(self):
        try:
            self._server.run(sockets=[self._worker_socket])
        except BaseException:
            logging.getLogger(__name__).exception("Gömülü sunucu durdu")
        finally:
            self._worker_socket.close()

    def is_running(self) -> bool:
        return bool(self._server and self._server.started and not self._server.should_exit
                    and self._thread and self._thread.is_alive())

    def stop(self):
        if self._server:
            self._server.should_exit = True
        if self._thread:
            self._thread.join(timeout=3)
        if self._worker_socket and not (self._thread and self._thread.is_alive()):
            self._worker_socket.close()
        self._socket.close()
