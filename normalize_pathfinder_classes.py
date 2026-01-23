#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pathfinder 1e Classlarındaki Duplicateleri Temizle"""

import json
from pathlib import Path

print("Pathfinder 1e Classes Normalization")
print("=" * 60)

# Veri yükle
with open('data/pathfinder_1e_data.json', encoding='utf-8') as f:
    data = json.load(f)

classes = data.get('classes', {})
print(f"Başlangıç: {len(classes)} class")

# Duplicateleri tespit et
duplicates_found = {}
for name in classes.keys():
    lower = name.lower()
    if lower not in duplicates_found:
        duplicates_found[lower] = []
    duplicates_found[lower].append(name)

# Normalize et - Title Case ile birleştir
new_classes = {}
removed_count = 0

for lower_name, variations in sorted(duplicates_found.items()):
    if len(variations) > 1:
        # Birden fazla varyasyon varsa, Title Case kullan
        canonical = variations[0].title()
        
        # Tüm varyasyonları kopyala
        merged_data = {}
        for var in variations:
            if var in classes:
                merged_data.update(classes[var])
        
        new_classes[canonical] = merged_data
        removed_count += len(variations) - 1
        print(f"  ✓ Merged {variations} → {canonical}")
    else:
        # Tek varyasyon varsa olduğu gibi al
        new_classes[variations[0]] = classes[variations[0]]

# Güncelle
data['classes'] = new_classes

# Kaydet
with open('data/pathfinder_1e_data.json', 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("\n" + "=" * 60)
print(f"Sonuç: {len(new_classes)} unique class (Removed: {removed_count} duplicate)")
print("✅ Saved to data/pathfinder_1e_data.json")
