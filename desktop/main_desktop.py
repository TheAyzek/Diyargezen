#!/usr/bin/env python3
"""
Diyargezer — TTRPG Karakter Yöneticisi
=======================================
Ana giriş noktası.

Çalıştırma:
    python main.py      # PySide6 Dark Fantasy GUI
"""

import sys
import logging
from pathlib import Path

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
    print("  D&D 5e  |  Pathfinder 1e  |  M&M 3e")
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
