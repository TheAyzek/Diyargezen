import socket
import urllib.request
from contextlib import asynccontextmanager

import pytest
from fastapi import FastAPI

from desktop.local_server import OwnedLocalServer, allows_navigation


def test_owned_server_serves_its_app_and_keeps_origin_reserved_after_worker_stops():
    app = FastAPI()

    @app.get("/probe")
    def probe():
        return {"owned": True}

    server = OwnedLocalServer(lambda: app, port=0)
    try:
        with urllib.request.urlopen(server.origin + "/probe", timeout=2) as response:
            assert response.read() == b'{"owned":true}'
        server._server.should_exit = True
        server._thread.join(timeout=3)
        assert not server.is_running()
        # Even a crashed/stopped worker must not release the window's origin.
        with socket.socket() as other:
            with pytest.raises(OSError):
                other.bind(server._socket.getsockname())
    finally:
        server.stop()


def test_busy_port_is_rejected_before_loading_backend():
    loaded = []
    with socket.socket() as occupied:
        if hasattr(socket, "SO_EXCLUSIVEADDRUSE"):
            occupied.setsockopt(socket.SOL_SOCKET, socket.SO_EXCLUSIVEADDRUSE, 1)
        occupied.bind(("127.0.0.1", 0))
        occupied.listen(1)
        with pytest.raises(OSError):
            OwnedLocalServer(lambda: loaded.append(True), port=occupied.getsockname()[1])
        assert loaded == []


def test_failed_startup_never_returns_trusted_server():
    @asynccontextmanager
    async def broken_lifespan(app):
        raise RuntimeError("Intentional isolated startup failure")
        yield

    with pytest.raises(RuntimeError, match="hazır hale gelemedi"):
        OwnedLocalServer(lambda: FastAPI(lifespan=broken_lifespan), port=0, timeout=2)


@pytest.mark.parametrize("url", [
    "https://example.com/", "http://127.0.0.1:8001/", "http://localhost:8000/",
    "https://127.0.0.1:8000/", "http://127.0.0.1:8000.evil.test/",
    "http://127.0.0.1:8000@evil.test/", "http://user@127.0.0.1:8000/",
    "file:///C:/secret.txt", "javascript:alert(1)", "data:text/html,test",
    "blob:https://example.com/id", "http://[invalid",
])
def test_navigation_rejects_other_origins_and_schemes(url):
    for main_frame in [True, False]:
        assert not allows_navigation(url, "http://127.0.0.1:8000", main_frame=main_frame)


def test_same_origin_navigation_and_child_blob_pdf_are_allowed():
    origin = "http://127.0.0.1:8000"
    assert allows_navigation(origin + "/characters#edit", origin, main_frame=True)
    assert allows_navigation("blob:" + origin + "/pdf-id", origin, main_frame=False)
    assert not allows_navigation("blob:" + origin + "/pdf-id", origin, main_frame=True)
