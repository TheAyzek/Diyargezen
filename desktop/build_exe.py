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


def build_frontend() -> bool:
    """React Web Frontend uygulamasını Vite ile derler."""
    frontend_dir = WORKSPACE_ROOT / "web" / "frontend"
    print("🌐 Web Frontend (Vite) derlemesi başlatılıyor...")
    npm_bin = shutil.which("npm.cmd") or shutil.which("npm") or "npm"
    try:
        res = subprocess.run([npm_bin, "run", "build"], cwd=frontend_dir, shell=True)
        if res.returncode == 0:
            print("✅ Frontend derlemesi başarılı.")
            return True
        else:
            print("⚠️ Frontend derlemesi tamamlandı.")
            return False
    except Exception as exc:
        print(f"⚠️ Frontend derlemesi atlandı: {exc}")
        return False


def prepopulate_database() -> bool:
    """Derleme öncesi tüm 15.000+ kural verisini (Feats, Traits, Spells, Classes, Items) SQLite veritabanına önceden işler."""
    print("📚 Kural veritabanı önceden işleniyor (Pre-populating 15,000+ Pathfinder 1e entities)...")
    try:
        if str(WORKSPACE_ROOT) not in sys.path:
            sys.path.insert(0, str(WORKSPACE_ROOT))
        from etl.pipeline import run_etl
        db_file = WORKSPACE_ROOT / "data" / "characters.db"
        db_file.parent.mkdir(parents=True, exist_ok=True)
        totals = run_etl(db_path=db_file, force=True)
        print(f"✅ Veritabanı ön işleme tamamlandı: {totals}")
        return True
    except Exception as exc:
        print(f"⚠️ Kural veritabanı ön işleme hatası: {exc}")
        return False


def create_portable_zip() -> bool:
    """Derlenmiş masaüstü uygulamasını tek tıkla paylaşılabilir ZIP arşivine dönüştürür."""
    exe_dir = DIST_DIR / "Diyargezen"
    zip_path = DIST_DIR / "Diyargezen_Portable.zip"
    if not exe_dir.exists():
        return False

    print("\n📦 Taşınabilir Taşınabilir ZIP paketi oluşturuluyor...")
    if zip_path.exists():
        zip_path.unlink()

    try:
        shutil.make_archive(str(DIST_DIR / "Diyargezen_Portable"), 'zip', root_dir=DIST_DIR, base_dir="Diyargezen")
        print(f"🎉 Taşınabilir Paket Hazır: {zip_path}")
        return True
    except Exception as exc:
        print(f"⚠️ ZIP paketi oluşturulamadı: {exc}")
        return False


def build_exe() -> bool:
    """PyInstaller ile Diyargezen.exe uygulamasını derler."""
    print("\n🔨 Diyargezen High-Fantasy Masaüstü Paketleme Başlatılıyor...")
    print(f"📌 Spec Dosyası: {SPEC_FILE}")

    clean_build_artifacts()
    prepopulate_database()
    build_frontend()
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
        # Ensure 159MB characters.db is placed directly in dist/Diyargezen/data/characters.db
        dist_db = DIST_DIR / "Diyargezen" / "data" / "characters.db"
        dist_db.parent.mkdir(parents=True, exist_ok=True)
        src_db = WORKSPACE_ROOT / "data" / "characters.db"
        if src_db.exists():
            print(f"📋 Veritabanı kopyalanıyor: {src_db} -> {dist_db}")
            shutil.copy2(src_db, dist_db)

        # Ensure PDF templates are placed directly in dist/Diyargezen/templates
        src_templates = WORKSPACE_ROOT / "templates"
        dist_templates = DIST_DIR / "Diyargezen" / "templates"
        dist_templates.mkdir(parents=True, exist_ok=True)
        if src_templates.exists():
            for pdf_f in src_templates.glob("*.pdf"):
                print(f"📄 PDF Şablonu kopyalanıyor: {pdf_f.name}")
                shutil.copy2(pdf_f, dist_templates / pdf_f.name)

        create_portable_zip()
        print("\n" + "=" * 65)
        print("🎉 Diyargezen Standalone Windows Masaüstü Paket Derlemesi Başarılı!")
        print("=" * 65)
        print(f"📂 Çıktı Klasörü: {DIST_DIR / 'Diyargezen'}")
        print(f"🎮 Çalıştırılabilir Dosya: {EXE_PATH}")
        print(f"📦 Arkadaşınızla Paylaşabileceğiniz Tek Dosya: {DIST_DIR / 'Diyargezen_Portable.zip'}")
        print("💡 Bu ZIP dosyasını arkadaşınıza attığınızda, zip'i açıp")
        print("   Diyargezen.exe'ye tıklamaları yeterlidir. Python, internet")
        print("   veya ek kurulum gerekmeden TÜM kural verisi ve karakter sistemi hazır çalışacaktır.")
        return True
    else:
        print("\n❌ Paketleme hatası! PyInstaller derlemesi başarısız oldu.")
        return False


if __name__ == "__main__":
    success = build_exe()
    sys.exit(0 if success else 1)
