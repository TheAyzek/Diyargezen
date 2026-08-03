#!/usr/bin/env python3
"""
Diyargezer — TTRPG Karakter Yöneticisi
=======================================
Ana giriş noktası.

Çalıştırma:
    python main_desktop.py      # PySide6 Dark Fantasy GUI
"""

import sys
import os
import logging
from pathlib import Path

from PySide6.QtCore import Qt, QCoreApplication

# Enable OpenGL context sharing for QWebEngineView on Windows
QCoreApplication.setAttribute(Qt.AA_ShareOpenGLContexts)

if getattr(sys, 'frozen', False):
    BASE_DIR = Path(getattr(sys, '_MEIPASS', ''))
    EXEC_DIR = Path(sys.executable).parent
else:
    BASE_DIR = Path(__file__).resolve().parent.parent
    EXEC_DIR = BASE_DIR

if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
desktop_dir = BASE_DIR / "desktop"
if str(desktop_dir) not in sys.path:
    sys.path.insert(0, str(desktop_dir))
backend_dir = BASE_DIR / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))


class FlushFileHandler(logging.FileHandler):
    def emit(self, record):
        super().emit(record)
        self.flush()

try:
    log_file = EXEC_DIR / "Diyargezen_desktop.log"
    handler = FlushFileHandler(str(log_file), mode="w", encoding="utf-8")
except Exception:
    log_file = Path.home() / "Diyargezen_desktop.log"
    handler = FlushFileHandler(str(log_file), mode="w", encoding="utf-8")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
    handlers=[
        handler,
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger("main_desktop")





def main() -> None:
    print("-" * 50)
    print("  Diyargezer - TTRPG Karakter Yoneticisi (Masaüstü)")
    print("  Pathfinder 1e — Offline-First istemci")
    print("-" * 50)

    try:
        from gui.main_window import run_app
        run_app()
    except ImportError as exc:
        print(f"PySide6 GUI yüklenemedi: {exc}")
        print("Çözüm: pip install PySide6")
        sys.exit(1)


if __name__ == "__main__":
    main()
