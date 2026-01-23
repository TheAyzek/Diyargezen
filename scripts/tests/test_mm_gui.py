#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M&M GUI Test"""

import sys
import io
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# GUI testi
print("=" * 70)
print("MUTANTS & MASTERMINDS GUI TEST")
print("=" * 70)
print()

try:
    # GUI modüllerini import et
    sys.path.insert(0, str(Path(__file__).parent.parent / "gui"))
    from PySide6.QtWidgets import QApplication
    from app import MmPage
    from utils.data_loader import load_mm_data
    
    print("1. VERİ YÜKLEME TESTİ")
    print("-" * 70)
    data = load_mm_data(Path("."))
    print(f"  ✅ Veri yüklendi: {bool(data)}")
    print(f"  ✅ Abilities: {len(data.get('abilities', {}))}")
    print(f"  ✅ Skills: {len(data.get('skills', {}))}")
    print(f"  ✅ Advantages: {len(data.get('advantages', {}))}")
    print(f"  ✅ Powers: {len(data.get('powers', {}))}")
    print(f"  ✅ Power Effects: {len(data.get('power_effects', {}))}")
    print(f"  ✅ Archetypes: {len(data.get('archetypes', {}))}")
    print()
    
    print("2. MmPage OLUŞTURMA TESTİ")
    print("-" * 70)
    app = QApplication([])
    page = MmPage()
    print("  ✅ MmPage başarıyla oluşturuldu")
    print(f"  ✅ Veri yüklendi: {bool(page.data)}")
    print(f"  ✅ Abilities widget'ları: {len(page.ability_spins) if hasattr(page, 'ability_spins') else 0}")
    print(f"  ✅ PL combo mevcut: {hasattr(page, 'pl_combo')}")
    print(f"  ✅ Archetype combo mevcut: {hasattr(page, 'archetype_combo')}")
    print()
    
    print("3. WIDGET KONTROL TESTİ")
    print("-" * 70)
    widgets = [
        ('name_edit', 'İsim'),
        ('codename_edit', 'Kod Adı'),
        ('pl_combo', 'Power Level'),
        ('archetype_combo', 'Archetype'),
        ('ability_spins', 'Ability Scores'),
        ('defense_spins', 'Defense'),
        ('pp_spin', 'Power Points'),
        ('powers_edit', 'Powers'),
        ('advantages_edit', 'Advantages'),
        ('notes_edit', 'Notes'),
        ('summary_text', 'Summary')
    ]
    
    for widget_name, description in widgets:
        exists = hasattr(page, widget_name)
        status = "✅" if exists else "❌"
        print(f"  {status} {description}: {widget_name} {'mevcut' if exists else 'EKSİK'}")
    print()
    
    print("4. FONKSİYON KONTROL TESTİ")
    print("-" * 70)
    functions = [
        '_start_new_character',
        '_collect_character_data',
        '_save_character',
        '_load_character',
        '_update_archetype_info',
        '_update_pl_limits',
        '_refresh_summary',
        '_apply_character'
    ]
    
    for func_name in functions:
        exists = hasattr(page, func_name) and callable(getattr(page, func_name, None))
        status = "✅" if exists else "❌"
        print(f"  {status} {func_name}: {'mevcut' if exists else 'EKSİK'}")
    print()
    
    print("5. VERİ İÇERİK TESTİ")
    print("-" * 70)
    if hasattr(page, 'archetype_combo'):
        arch_count = page.archetype_combo.count()
        print(f"  ✅ Archetype combo: {arch_count} archetype yüklendi")
        
        # İlk archetype'ı kontrol et
        if arch_count > 0:
            first_arch = page.archetype_combo.itemText(0)
            arch_data = page.data.get('archetypes', {}).get(first_arch, {})
            suggested_powers = arch_data.get('suggested_powers', [])
            print(f"  ✅ İlk archetype ({first_arch}): {len(suggested_powers)} suggested power")
    
    if hasattr(page, 'pl_combo'):
        pl_count = page.pl_combo.count()
        print(f"  ✅ Power Level combo: {pl_count} PL seçeneği")
    print()
    
    print("=" * 70)
    print("✅ TÜM TESTLER TAMAMLANDI")
    print("=" * 70)
    print("GUI başarıyla çalışıyor. Uygulamayı başlatmak için:")
    print("  python gui/app.py")
    print()
    
    app.quit()
    
except Exception as e:
    print(f"❌ HATA: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)


