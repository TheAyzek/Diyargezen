#!/usr/bin/env python3
"""
Diyargezen EXE Builder
PyInstaller kullanarak executable oluşturur
"""

import subprocess
import sys
from pathlib import Path

def build_exe():
    """EXE dosyasını oluştur"""
    print("=" * 60)
    print("Diyargezen EXE Builder")
    print("=" * 60)
    print()
    
    # PyInstaller'ın kurulu olup olmadığını kontrol et
    try:
        import PyInstaller
        print("✓ PyInstaller kurulu")
    except ImportError:
        print("✗ PyInstaller bulunamadı!")
        print("Kurulum için: pip install pyinstaller")
        return 1
    
    # Ana dizin
    base_dir = Path(__file__).resolve().parent
    
    # PyInstaller komutu
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Diyargezen",
        "--onefile",  # Tek dosya olarak
        "--windowed",  # Konsol penceresi gösterme (GUI için)
        "--icon=assets/diyargezer_logo.png",  # Icon (varsa)
        "--add-data=data;data",  # Data klasörünü ekle
        "--add-data=assets;assets",  # Assets klasörünü ekle
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
        "gui/app.py"  # Ana dosya
    ]
    
    print("PyInstaller çalıştırılıyor...")
    print(f"Komut: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, cwd=str(base_dir))
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
        print("✗ Beklenmeyen hata!")
        print("=" * 60)
        print(f"Hata: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(build_exe())



Diyargezen EXE Builder
PyInstaller kullanarak executable oluşturur
"""

import subprocess
import sys
from pathlib import Path

def build_exe():
    """EXE dosyasını oluştur"""
    print("=" * 60)
    print("Diyargezen EXE Builder")
    print("=" * 60)
    print()
    
    # PyInstaller'ın kurulu olup olmadığını kontrol et
    try:
        import PyInstaller
        print("✓ PyInstaller kurulu")
    except ImportError:
        print("✗ PyInstaller bulunamadı!")
        print("Kurulum için: pip install pyinstaller")
        return 1
    
    # Ana dizin
    base_dir = Path(__file__).resolve().parent
    
    # PyInstaller komutu
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Diyargezen",
        "--onefile",  # Tek dosya olarak
        "--windowed",  # Konsol penceresi gösterme (GUI için)
        "--icon=assets/diyargezer_logo.png",  # Icon (varsa)
        "--add-data=data;data",  # Data klasörünü ekle
        "--add-data=assets;assets",  # Assets klasörünü ekle
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
        "gui/app.py"  # Ana dosya
    ]
    
    print("PyInstaller çalıştırılıyor...")
    print(f"Komut: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, cwd=str(base_dir))
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
        print("✗ Beklenmeyen hata!")
        print("=" * 60)
        print(f"Hata: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(build_exe())



Diyargezen EXE Builder
PyInstaller kullanarak executable oluşturur
"""

import subprocess
import sys
from pathlib import Path

def build_exe():
    """EXE dosyasını oluştur"""
    print("=" * 60)
    print("Diyargezen EXE Builder")
    print("=" * 60)
    print()
    
    # PyInstaller'ın kurulu olup olmadığını kontrol et
    try:
        import PyInstaller
        print("✓ PyInstaller kurulu")
    except ImportError:
        print("✗ PyInstaller bulunamadı!")
        print("Kurulum için: pip install pyinstaller")
        return 1
    
    # Ana dizin
    base_dir = Path(__file__).resolve().parent
    
    # PyInstaller komutu
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Diyargezen",
        "--onefile",  # Tek dosya olarak
        "--windowed",  # Konsol penceresi gösterme (GUI için)
        "--icon=assets/diyargezer_logo.png",  # Icon (varsa)
        "--add-data=data;data",  # Data klasörünü ekle
        "--add-data=assets;assets",  # Assets klasörünü ekle
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
        "gui/app.py"  # Ana dosya
    ]
    
    print("PyInstaller çalıştırılıyor...")
    print(f"Komut: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, cwd=str(base_dir))
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
        print("✗ Beklenmeyen hata!")
        print("=" * 60)
        print(f"Hata: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(build_exe())



Diyargezen EXE Builder
PyInstaller kullanarak executable oluşturur
"""

import subprocess
import sys
from pathlib import Path

def build_exe():
    """EXE dosyasını oluştur"""
    print("=" * 60)
    print("Diyargezen EXE Builder")
    print("=" * 60)
    print()
    
    # PyInstaller'ın kurulu olup olmadığını kontrol et
    try:
        import PyInstaller
        print("✓ PyInstaller kurulu")
    except ImportError:
        print("✗ PyInstaller bulunamadı!")
        print("Kurulum için: pip install pyinstaller")
        return 1
    
    # Ana dizin
    base_dir = Path(__file__).resolve().parent
    
    # PyInstaller komutu
    cmd = [
        sys.executable,
        "-m",
        "PyInstaller",
        "--name=Diyargezen",
        "--onefile",  # Tek dosya olarak
        "--windowed",  # Konsol penceresi gösterme (GUI için)
        "--icon=assets/diyargezer_logo.png",  # Icon (varsa)
        "--add-data=data;data",  # Data klasörünü ekle
        "--add-data=assets;assets",  # Assets klasörünü ekle
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
        "gui/app.py"  # Ana dosya
    ]
    
    print("PyInstaller çalıştırılıyor...")
    print(f"Komut: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(cmd, check=True, cwd=str(base_dir))
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
        print("✗ Beklenmeyen hata!")
        print("=" * 60)
        print(f"Hata: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(build_exe())


