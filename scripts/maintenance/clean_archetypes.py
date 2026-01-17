#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archetype'lardaki yanlış string'leri temizle"""

import sys
import io
import json
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

data_file = Path("data/mm_data.json")
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

archetypes = data.get('archetypes', {})
cleaned_count = 0

print("Archetype'lar temizleniyor...")
print()

for arch_name, arch_data in archetypes.items():
    suggested_powers = arch_data.get('suggested_powers', [])
    if suggested_powers:
        before_count = len(suggested_powers)
        # "Effect Descriptions" ile başlayan veya çok uzun (200+ karakter) string'leri kaldır
        cleaned = [p for p in suggested_powers 
                   if not p.startswith('Effect Descriptions') 
                   and len(p) < 200  # Çok uzun olanları da filtrele
                   and not (len(p) > 100 and 'AFFLICTION' in p and 'ATTACK' in p)]
        
        if len(cleaned) != len(suggested_powers):
            arch_data['suggested_powers'] = cleaned
            cleaned_count += 1
            print(f"  ✅ {arch_name}: {before_count - len(cleaned)} yanlış entry kaldırıldı ({before_count} -> {len(cleaned)})")

print()
print(f"✅ {cleaned_count} archetype temizlendi")
print()

# Kaydet
print("Veriler kaydediliyor...")
with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Tamamlandı!")

# Kontrol
print("\nKontrol:")
battlesuit = data.get('archetypes', {}).get('Battlesuit', {})
suggested = battlesuit.get('suggested_powers', [])
print(f"Battlesuit suggested_powers: {len(suggested)}")
if suggested:
    print(f"  İlk 3: {suggested[:3]}")


