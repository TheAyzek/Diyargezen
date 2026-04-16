#!/usr/bin/env python3
"""
Diyargezer — TTRPG Karakter Yöneticisi
=======================================
Ana giriş noktası.

Çalıştırma:
    python main.py              # PySide6 Dark Fantasy GUI
    python main.py --ctk        # CustomTkinter alternatif GUI
    python main.py --cli        # CLI modu (gelecek)
"""

import sys
import logging
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def main() -> None:
    use_ctk = "--ctk" in sys.argv

    print("═" * 50)
    print("  Diyargezer — TTRPG Karakter Yöneticisi")
    print("  D&D 5e  •  Pathfinder 1e  •  VtM 5e  •  M&M 3e")
    print("═" * 50)

    if use_ctk:
        try:
            from gui.app_desktop import main as ctk_main
            ctk_main()
            return
        except ImportError as exc:
            print(f"CustomTkinter yüklenemedi: {exc}")
            print("pip install customtkinter")
            sys.exit(1)

    try:
        from gui.main_window import run_app
        run_app()
    except ImportError as exc:
        print(f"PySide6 GUI yüklenemedi: {exc}")
        print("Alternatif: python main.py --ctk")
        sys.exit(1)


if __name__ == "__main__":
    main()
