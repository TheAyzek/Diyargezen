#!/usr/bin/env python3
"""
Diyargezen EXE Builder
PyInstaller kullanarak executable oluşturur
"""

from __future__ import annotations
import sys
from pathlib import Path
import importlib.util
import subprocess
import os


def build_exe() -> int:
    """EXE dosyasını oluştur"""
    print("=" * 60)
    print("Diyargezen EXE Builder")
    print("=" * 60)
    print()

    # PyInstaller'ın kurulu olup olmadığını kontrol et
    if importlib.util.find_spec("PyInstaller") is None:
        print("✗ PyInstaller bulunamadı!")
        print("Kurulum için: pip install pyinstaller")
        return 1
    else:
        print("✓ PyInstaller kurulu")

    # Ana dizin
    base_dir = Path(__file__).resolve().parent

    # Platform-aware add-data separator
    add_data_sep = ";" if os.name == "nt" else ":"

    # PyInstaller komutu
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Diyargezen",
        "--onefile",  # Tek dosya olarak
        "--windowed",  # Konsol penceresi gösterme (GUI için)
        "--icon=assets/diyargezer_logo.png",  # Icon (varsa)
        f"--add-data=data{add_data_sep}data",  # Data klasörünü ekle
        f"--add-data=assets{add_data_sep}assets",  # Assets klasörünü ekle
        "--hidden-import=PySide6.QtCore",
        "--hidden-import=PySide6.QtGui",
        "--hidden-import=PySide6.QtWidgets",
        "--hidden-import=qdarkstyle",
        "--hidden-import=reportlab",
        "--hidden-import=PIL",
        "--hidden-import=PyPDF2",
        "--hidden-import=utils.data_loader",
        "--hidden-import=utils.storage",
        "--hidden-import=utils.export_pdf",
        "--hidden-import=utils.export_formats",
        "--hidden-import=utils.character_versioning",
        "--hidden-import=utils.character_statistics",
        "--hidden-import=utils.rule_extractor",
        "--hidden-import=utils.rule_storage",
        "--clean",  # Önceki build'i temizle
        "gui/app.py",  # Ana dosya
    ]

    print("PyInstaller çalıştırılıyor...")
    print(f"Komut: {' '.join(cmd)}")
    print()

    try:
        subprocess.run(cmd, check=True, cwd=str(base_dir))
        print()
        print("=" * 60)
        print("✓ EXE başarıyla oluşturuldu!")
        print("=" * 60)
        print(f"EXE dosyası: {base_dir / 'dist' / 'Diyargezen.exe'}")
        print()
        print("Not: İlk çalıştırmada biraz yavaş olabilir (dosya açılıyor).")
        return 0
    except subprocess.CalledProcessError as e:
        print()
        print("=" * 60)
        print("✗ EXE oluşturma başarısız!")
        print("=" * 60)
        print(f"Hata: {e}")
        return 1
    except Exception as e:
        print()
        print("=" * 60)
        print("✗ Beklenmedik hata!")
        print("=" * 60)
        print(f"Hata: {e}")
        return 1


if __name__ == "__main__":
    raise SystemExit(build_exe())


