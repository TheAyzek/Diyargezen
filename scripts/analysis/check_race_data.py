#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Çekilen ırk verilerini kontrol et"""

import json
from pathlib import Path

data_file = Path("data/pathfinder_1e_data.json")
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

races = data.get('races', {})
print(f"Toplam irk sayisi: {len(races)}")
print("\nOrnek irklar:")
print("-" * 60)

for i, (name, race) in enumerate(list(races.items())[:10]):
    traits_count = len(race.get('traits', []))
    vision = race.get('vision', 'normal')
    languages_count = len(race.get('languages', []))
    ability = race.get('ability_score_increase_text', 'N/A')
    print(f"{i+1}. {name}")
    print(f"   Ability: {ability}")
    print(f"   Vision: {vision}")
    print(f"   Traits: {traits_count} ozellik")
    print(f"   Languages: {languages_count} dil")
    print()

print(f"\n[OK] Veri dosyasi hazir: {data_file}")


