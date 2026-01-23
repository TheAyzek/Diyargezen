#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

data_file = Path("data/pathfinder_1e_data.json")

with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

races = data.get('races', {})
classes = data.get('classes', {})
spells = data.get('spells', {})
feats = data.get('feats', {})

print("=" * 70)
print("PATHFINDER 1E DATA CHECK")
print("=" * 70)
print(f"\nRaces: {len(races)}")
for race in sorted(races.keys()):
    print(f"  - {race}")

print(f"\nClasses: {len(classes)}")
for cls in sorted(classes.keys())[:20]:
    print(f"  - {cls}")
if len(classes) > 20:
    print(f"  ... ve {len(classes)-20} daha")

print(f"\nSpells: {len(spells)}")
print(f"Feats: {len(feats)}")
