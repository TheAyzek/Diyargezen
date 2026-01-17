#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parsing kalitesini test et"""

import sys
from pathlib import Path
import json

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

dnd_file = Path("data/dnd_data.json")
with open(dnd_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

spells = data.get('spells', {})

print("=" * 70)
print("PARSING KALİTE TESTİ")
print("=" * 70)
print()

# İstatistikler
total = len(spells)
complete = 0
incomplete = []

required_fields = ['level', 'school', 'casting_time', 'range', 'components', 'duration', 'description']

for name, spell in spells.items():
    is_complete = all(spell.get(field) for field in required_fields)
    if is_complete:
        complete += 1
    else:
        missing = [f for f in required_fields if not spell.get(f)]
        incomplete.append((name, missing))

print(f"Toplam spell: {total}")
print(f"Tam veri: {complete} ({complete*100/total:.1f}%)")
print(f"Eksik veri: {total - complete} ({100-complete*100/total:.1f}%)")
print()

if incomplete:
    print("İlk 10 eksik spell:")
    for i, (name, missing) in enumerate(incomplete[:10], 1):
        print(f"  {i:2d}. {name:35s} | Eksik: {', '.join(missing)}")
    
    if len(incomplete) > 10:
        print(f"  ... ve {len(incomplete) - 10} tane daha")

print()
print("=" * 70)

# Örnek tam spell göster
complete_spells = [(n, s) for n, s in spells.items() if all(s.get(f) for f in required_fields)]
if complete_spells:
    print("\nÖrnek Tam Spell:")
    print("-" * 70)
    name, spell = complete_spells[0]
    print(f"Name: {name}")
    for field in required_fields:
        value = spell.get(field)
        if isinstance(value, str) and len(value) > 80:
            value = value[:80] + "..."
        print(f"  {field}: {value}")
print()
print("=" * 70)


