#!/usr/bin/env python3
"""
Diyargezen Automated Windows Installer Builder
==============================================
Masaüstü uygulamasını tek tıkla kurulabilir Windows Kurulum Paketine (.exe) dönüştürür.
"""

import os
import sys
import shutil
import subprocess
import zipfile
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

WORKSPACE_ROOT = Path(__file__).resolve().parent.parent
DIST_DIR = WORKSPACE_ROOT / "dist"
APP_DIR = DIST_DIR / "Diyargezen"
ISS_FILE = WORKSPACE_ROOT / "desktop" / "Diyargezen_Setup.iss"
SETUP_EXE = DIST_DIR / "Diyargezen_Setup_v2.0.exe"
SETUP_ZIP = DIST_DIR / "Diyargezen_Portable_v2.0.zip"


def check_and_build_app(force_rebuild: bool = True) -> bool:
    """Dağıtım klasörünü PyInstaller ile günceller."""
    exe_file = APP_DIR / "Diyargezen.exe"
    if force_rebuild or not exe_file.exists():
        print("🔨 Standalone .exe paketi derlemesi başlatılıyor...")
        build_script = WORKSPACE_ROOT / "desktop" / "build_exe.py"
        res = subprocess.run([sys.executable, str(build_script)], cwd=WORKSPACE_ROOT)
        if res.returncode != 0 or not exe_file.exists():
            print("❌ Standalone .exe derlemesi başarısız oldu!")
            return False
    return True


def find_iscc() -> Path | None:
    """Inno Setup Derleyicisi (ISCC.exe) yolunu tespit eder."""
    iscc_path = shutil.which("ISCC.exe") or shutil.which("iscc")
    if iscc_path:
        return Path(iscc_path)

    standard_paths = [
        Path(r"C:\Program Files (x86)\Inno Setup 6\ISCC.exe"),
        Path(r"C:\Program Files\Inno Setup 6\ISCC.exe"),
        Path(os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)")) / "Inno Setup 6" / "ISCC.exe",
        Path(os.environ.get("ProgramFiles", r"C:\Program Files")) / "Inno Setup 6" / "ISCC.exe",
    ]

    for p in standard_paths:
        if p.exists():
            return p

    return None



def build_zip_package() -> bool:
    """Taşınabilir ZIP paketini oluşturur."""
    print("📦 Taşınabilir ZIP paketi (Portable Zip) hazırlanıyor...")
    if SETUP_ZIP.exists():
        SETUP_ZIP.unlink()

    with zipfile.ZipFile(SETUP_ZIP, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk(APP_DIR):
            for file in files:
                file_path = Path(root) / file
                arcname = Path("Diyargezen") / file_path.relative_to(APP_DIR)
                zipf.write(file_path, arcname)

    print(f"✅ Taşınabilir Paket Oluşturuldu: {SETUP_ZIP}")
    return True


def build_installer() -> bool:
    """Windows Installer (.exe) paketleme işlemini yürütür."""
    print("\n" + "=" * 65)
    print("🚀 DIYARGEZEN WINDOWS KURULUM PAKETİ (INSTALLER) DERLEMESİ")
    print("=" * 65)

    if not check_and_build_app():
        return False

    # Always generate portable zip package as fallback
    build_zip_package()

    iscc_bin = find_iscc()
    if iscc_bin:
        print(f"\n✨ Inno Setup Compiler Tespit Edildi: {iscc_bin}")
        print(f"⚙️ ISS Yapılandırma Dosyası: {ISS_FILE}")

        cmd = [str(iscc_bin), str(ISS_FILE)]
        print(f"🔨 Derleme Komutu: {' '.join(cmd)}")
        res = subprocess.run(cmd, cwd=WORKSPACE_ROOT)

        if res.returncode == 0 and SETUP_EXE.exists():
            print("\n" + "=" * 65)
            print("🎉 DIYARGEZEN WINDOWS KURULUM SİHİRBAZI (.EXE) BAŞARIYLA OLUŞTURULDU!")
            print("=" * 65)
            print(f"🎮 Kurulum Dosyası (Setup Executable): {SETUP_EXE}")
            print("💡 Bu kurulum dosyasını kullanıcılarınıza dağıtabilirsiniz.")
            return True
        else:
            print("⚠️ ISCC derlemesi tamamlanamadı. Taşınabilir ZIP paketi kullanıma hazır.")
            return True
    else:
        print("\n💡 Bilgi: Bilgisayarınızda Inno Setup Compiler (ISCC.exe) yüklü değil.")
        print("   Inno Setup yüklendiğinde `Diyargezen_Setup_v2.0.exe` tek tıkla üretilebilir.")
        print("   Şu an için dağıtıma hazır taşınabilir paket üretildi:")
        print(f"   📂 {SETUP_ZIP}")
        return True


if __name__ == "__main__":
    success = build_installer()
    sys.exit(0 if success else 1)
