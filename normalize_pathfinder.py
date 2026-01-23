#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pathfinder 1e veri dosyasındaki duplicate entries'i temizle ve normalize et"""

import json
from pathlib import Path

def normalize_races(races_dict):
    """Race names'i normalize et ve duplicates'i birleştir"""
    normalized = {}
    
    duplicates_map = {
        'half-orc': 'Half-Orc',
        'dwarves': 'Dwarf',
        'elven': 'Elf',
        'gnomes': 'Gnome',
        'human': 'Human',
        'halfling': 'Halfling',
        'Half Elf': 'Half-Elf',
    }
    
    for name, data in races_dict.items():
        # Eğer mapping varsa
        if name.lower() in [k.lower() for k in duplicates_map.keys()]:
            canonical_name = next((v for k, v in duplicates_map.items() if k.lower() == name.lower()), name)
        else:
            canonical_name = name
        
        # Eğer bu canonical name zaten yoksa veya mevcut versiyonu daha fazla bilgi içeriyorsa
        if canonical_name not in normalized or len(data) > len(normalized.get(canonical_name, {})):
            normalized[canonical_name] = data
    
    return normalized

def main():
    data_file = Path("data/pathfinder_1e_data.json")
    
    print("=" * 70)
    print("PATHFINDER 1E VERİ NORMALIZASYONU")
    print("=" * 70)
    
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print(f"\nÖncesi:")
    print(f"  Races: {len(data.get('races', {}))}")
    print(f"  Classes: {len(data.get('classes', {}))}")
    print(f"  Spells: {len(data.get('spells', {}))}")
    print(f"  Feats: {len(data.get('feats', {}))}")
    
    # Races'i normalize et
    if 'races' in data:
        old_count = len(data['races'])
        data['races'] = normalize_races(data['races'])
        new_count = len(data['races'])
        
        print(f"\n✅ Races normalized: {old_count} → {new_count}")
        
        # Removed entries
        if old_count > new_count:
            print(f"   {old_count - new_count} duplicate entry çıkartıldı")
    
    # Classes'ları da normalize et (küçük/büyük harf sorunları)
    if 'classes' in data:
        classes_normalized = {}
        for name, data_item in data['classes'].items():
            # Unchained, etc variations için birleştir
            canonical = name.replace('(Unchained)', '').strip()
            if canonical not in classes_normalized or len(data_item) > len(classes_normalized.get(canonical, {})):
                classes_normalized[canonical] = data_item
        
        # Orijinal veriyi koru, sadece listing için
        print(f"\n✅ Classes kontrol edildi: {len(data['classes'])} entries")
    
    # Kaydet
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    
    print(f"\n✅ Normalized data kaydedildi!")
    print(f"\nSonrası:")
    print(f"  Races: {len(data.get('races', {}))}")
    print(f"  Classes: {len(data.get('classes', {}))}")
    print(f"  Spells: {len(data.get('spells', {}))}")
    print(f"  Feats: {len(data.get('feats', {}))}")

if __name__ == "__main__":
    main()
