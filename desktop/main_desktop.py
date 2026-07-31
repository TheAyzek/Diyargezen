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

# ── QWebEngineView GPU beyaz ekran düzeltmesi ──
# Windows'ta bazı GPU sürücüleri QWebEngineView'ın beyaz ekran göstermesine
# neden olur. Bu ayarlar Qt/Chromium'u yazılım tabanlı render'a zorlar.
# Bu satırlar QApplication oluşturulmadan ÖNCE çalışmalıdır.
os.environ["QTWEBENGINE_CHROMIUM_FLAGS"] = "--disable-gpu --disable-gpu-compositing"
os.environ["QT_OPENGL"] = "software"

BASE_DIR = Path(__file__).resolve().parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
desktop_dir = Path(__file__).resolve().parent
if str(desktop_dir) not in sys.path:
    sys.path.insert(0, str(desktop_dir))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


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
