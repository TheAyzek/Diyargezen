# -*- mode: python ; coding: utf-8 -*-
"""
PyInstaller spec dosyası - Diyargezen
Bu dosyayı özelleştirerek build ayarlarını değiştirebilirsiniz.
"""

import sys
from pathlib import Path

block_cipher = None

# Ana dizin
import os
try:
    base_dir = Path(SPECPATH).parent
except NameError:
    # SPECPATH yoksa mevcut dizini kullan
    base_dir = Path(__file__).parent if '__file__' in globals() else Path.cwd()

# Data dosyaları
datas = [
    ('data', 'data'),  # Data klasörünü ekle
    ('assets', 'assets'),  # Assets klasörünü ekle
]

# Hidden imports (otomatik bulunamayan modüller)
hiddenimports = [
    'PySide6.QtCore',
    'PySide6.QtGui',
    'PySide6.QtWidgets',
    'qdarkstyle',
    'reportlab',
    'PIL',
    'PIL._tkinter_finder',
    'PyPDF2',
    'utils.data_loader',
    'utils.storage',
    'utils.export_pdf',
    'utils.export_formats',
    'utils.character_versioning',
    'utils.character_statistics',
    'utils.character_comparator',
    'utils.rule_extractor',
    'utils.rule_storage',
    'utils.rule_validator',
    'utils.rule_preview',
    'utils.rule_versioning',
    'utils.dynamic_calculator',
    'utils.template_manager',
    'utils.batch_operations',
    'utils.recent_files',
    'utils.performance',
    'utils.calculations',
    'creators.dnd_integrated',
]

a = Analysis(
    ['gui/app.py'],
    pathex=[str(base_dir)],
    binaries=[],
    datas=datas,
    hiddenimports=hiddenimports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
        'tkinter',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='Diyargezen',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # GUI uygulaması için konsol penceresi gösterme
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=str(base_dir / 'assets' / 'diyargezer_logo.png') if (base_dir / 'assets' / 'diyargezer_logo.png').exists() else None,
)

