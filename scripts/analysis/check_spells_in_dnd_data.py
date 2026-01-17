#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""dnd_data.json'daki spell'leri kontrol et"""

import json
from pathlib import Path

dnd_file = Path("data/dnd_data.json")
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("DND_DATA.JSON SPELL KONTROLÜ")
print("=" * 70)
print()

# Ana spells bölümü
spells = data.get('spells', {})
print(f"Ana 'spells' bölümü: {len(spells)} spell")
print()

if spells:
    print("İlk 10 spell:")
    for i, (name, spell) in enumerate(list(spells.items())[:10], 1):
        level = spell.get('level', '?')
        school = spell.get('school', '?')
        level_str = str(level) if level != '?' else '?'
        print(f"  {i:2d}. {name:30s} | Level {level_str:2s} | {school}")
    
    if len(spells) > 10:
        print(f"  ... ve {len(spells) - 10} tane daha")
    
    print()
    
    # Level dağılımı
    levels = {}
    for name, spell in spells.items():
        level = spell.get('level')
        if level is not None:
            levels[level] = levels.get(level, 0) + 1
    
    print("Level Dağılımı:")
    for level in sorted(levels.keys()):
        print(f"  Level {level}: {levels[level]} spell")
    
    print()
    
    # Eksik veriler
    missing_stats = {
        'casting_time': 0,
        'range': 0,
        'components': 0,
        'duration': 0,
        'description': 0
    }
    
    for name, spell in spells.items():
        if not spell.get('casting_time'):
            missing_stats['casting_time'] += 1
        if not spell.get('range'):
            missing_stats['range'] += 1
        if not spell.get('components'):
            missing_stats['components'] += 1
        if not spell.get('duration'):
            missing_stats['duration'] += 1
        if not spell.get('description'):
            missing_stats['description'] += 1
    
    print("Eksik Veriler:")
    for stat, count in missing_stats.items():
        status = "EKSIK" if count > 0 else "TAM"
        print(f"  {status} {stat}: {count} spell'de eksik")

print()
print("=" * 70)

