#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Mevcut D&D verilerini kontrol et"""

import json
from pathlib import Path

data_file = Path("data/dnd_data.json")
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

print("=" * 70)
print("MEVCUT D&D VERİLERİ")
print("=" * 70)
print()

print(f"📊 Races: {len(data.get('races', {}))}")
for race in list(data.get('races', {}).keys())[:10]:
    print(f"  - {race}")
if len(data.get('races', {})) > 10:
    print(f"  ... ve {len(data.get('races', {})) - 10} tane daha")
print()

print(f"📊 Classes: {len(data.get('classes', {}))}")
for cls in list(data.get('classes', {}).keys()):
    print(f"  - {cls}")
print()

print(f"📊 Spells: {len(data.get('spells', {}))}")
spell_levels = {}
for spell_name, spell_data in data.get('spells', {}).items():
    level = spell_data.get('level', 'Unknown')
    spell_levels[level] = spell_levels.get(level, 0) + 1
print("  Büyü seviyeleri:")
for level in sorted(spell_levels.keys()):
    print(f"    Level {level}: {spell_levels[level]} büyü")
print()

print(f"📊 Backgrounds: {len(data.get('backgrounds', {}))}")
for bg in list(data.get('backgrounds', {}).keys())[:10]:
    print(f"  - {bg}")
if len(data.get('backgrounds', {})) > 10:
    print(f"  ... ve {len(data.get('backgrounds', {})) - 10} tane daha")
print()

print(f"📊 Feats: {len(data.get('feats', {}))}")
for feat in list(data.get('feats', {}).keys())[:10]:
    print(f"  - {feat}")
if len(data.get('feats', {})) > 10:
    print(f"  ... ve {len(data.get('feats', {})) - 10} tane daha")
print()

print(f"📊 Equipment: {len(data.get('equipment', {}))}")
print()


