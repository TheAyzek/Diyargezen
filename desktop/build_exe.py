#!/usr/bin/env python3
"""
Diyargezen Standalone EXE Builder
==================================
PyInstaller kullanarak PySide6 Masaüstü Uygulamasını bağımsız Windows .exe
paketi olarak derler.

Kullanım:
    python desktop/build_exe.py
"""

import sys
import shutil
import subprocess
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent

SPEC_FILE = WORKSPACE_ROOT / "desktop" / "Diyargezen.spec"
DIST_DIR = WORKSPACE_ROOT / "dist"
BUILD_DIR = WORKSPACE_ROOT / "build"
EXE_PATH = DIST_DIR / "Diyargezen" / "Diyargezen.exe"


def clean_build_artifacts() -> None:
    """Derleme öncesi eski paketleme artıklarını temizler."""
    print("🧹 Eski derleme kalıntıları temizleniyor...")
    if BUILD_DIR.exists():
        shutil.rmtree(BUILD_DIR, ignore_errors=True)
    if (DIST_DIR / "Diyargezen").exists():
        shutil.rmtree(DIST_DIR / "Diyargezen", ignore_errors=True)
    print("✨ Temizlik tamamlandı.")


def check_pyinstaller() -> bool:
    """PyInstaller paketinin yüklü olup olmadığını doğrular."""
    try:
        import PyInstaller
        return True
    except ImportError:
        print("❌ PyInstaller paketi bulunamadı! Yükleniyor: pip install pyinstaller")
        subprocess.run([sys.executable, "-m", "pip", "install", "pyinstaller"], check=True)
        return True


def build_exe() -> bool:
    """PyInstaller ile Diyargezen.exe uygulamasını derler."""
    print("\n🔨 Diyargezen High-Fantasy Masaüstü Paketleme Başlatılıyor...")
    print(f"📌 Spec Dosyası: {SPEC_FILE}")

    clean_build_artifacts()
    check_pyinstaller()

    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--noconfirm",
        str(SPEC_FILE),
    ]

    print(f"🚀 Derleme Komutu: {' '.join(cmd)}\n")
    result = subprocess.run(cmd, cwd=WORKSPACE_ROOT)

    if result.returncode == 0 and EXE_PATH.exists():
        print("\n" + "=" * 60)
        print("🎉 Diyargezen Standalone Windows .exe Derlemesi Başarılı!")
        print("=" * 60)
        print(f"📂 Çıktı Dizin: {DIST_DIR / 'Diyargezen'}")
        print(f"🎮 Çalıştırılabilir Dosya: {EXE_PATH}")
        print("💡 Bu klasörü herhangi bir Windows bilgisayara kopyalayarak")
        print("   Python kurulumuna gerek kalmadan doğrudan çalıştırabilirsiniz.")
        return True
    else:
        print("\n❌ Paketleme hatası! PyInstaller derlemesi başarısız oldu.")
        return False


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
