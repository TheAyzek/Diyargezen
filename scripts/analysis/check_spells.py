#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
from pathlib import Path

data_file = Path("data/pathfinder_1e_data.json")
if data_file.exists():
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    spells = data.get('spells', {})
    print(f"Toplam büyü: {len(spells)}")
    if spells:
        print("\nİlk 3 büyü:")
        for i, (name, spell) in enumerate(list(spells.items())[:3]):
            print(f"\n{i+1}. {name}:")
            print(f"   Level: {spell.get('level', '?')}")
            print(f"   School: {spell.get('school', '?')}")
            print(f"   Casting Time: {spell.get('casting_time', '?')}")
            print(f"   Components: {spell.get('components', '?')}")
            print(f"   Range: {spell.get('range', '?')}")
            print(f"   Description: {spell.get('description', '?')[:100]}...")


