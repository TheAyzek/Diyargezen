#!/usr/bin/env python3
"""
Diyargezer - Evrensel FRP Karakter Oluşturucu
Ana giriş noktası
"""

import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))


def main():
    """Ana fonksiyon - GUI başlat"""
    print("=" * 50)
    print("  Diyargezer - Evrensel FRP Karakter Oluşturucu")
    print("=" * 50)
    print()
    print("Desteklenen Sistemler:")
    print("  D&D 5e | Pathfinder 1e | VtM 5e | M&M 3e")
    print()

    # Modern GUI (CustomTkinter) - ana arayuz
    try:
        print("Modern GUI başlatılıyor...")
        from gui.modern_gui import DiyargezerGUI
        app = DiyargezerGUI()
        app.run()
    except ImportError as e:
        print(f"Modern GUI yüklenemedi: {e}")
        print("Alternatif GUI deneniyor...")
        # Fallback: PySide6/PyQt5 GUI (gui/app.py)
        try:
            from gui.app import main as app_main
            app_main()
        except ImportError as e2:
            print(f"Alternatif GUI de yüklenemedi: {e2}")
            print("\nKurulum: pip install -r requirements.txt")
            sys.exit(1)
    except Exception as e:
        print(f"Beklenmeyen hata: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
