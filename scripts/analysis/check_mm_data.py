#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M&M verilerini kontrol et"""

import json
from pathlib import Path

data_file = Path("data/mm_data.json")
if data_file.exists():
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 60)
    print("MUTANTS & MASTERMINDS VERİ DURUMU")
    print("=" * 60)
    print(f"\nArchetypes: {len(data.get('archetypes', {}))}")
    print(f"Abilities: {len(data.get('abilities', {}))}")
    print(f"Skills: {len(data.get('skills', {}))}")
    print(f"Advantages: {len(data.get('advantages', {}))}")
    print(f"Powers: {len(data.get('powers', {}))}")
    print(f"Power Effects: {len(data.get('power_effects', {}))}")
    
    # Örnek archetype kontrolü
    if data.get('archetypes'):
        print("\nÖrnek Archetype (Battlesuit):")
        battlesuit = data['archetypes'].get('Battlesuit', {})
        print(f"  Summary uzunluğu: {len(battlesuit.get('summary', ''))}")
        print(f"  Suggested Powers: {len(battlesuit.get('suggested_powers', []))}")
        print(f"  Suggested Advantages: {len(battlesuit.get('suggested_advantages', []))}")
        print(f"  Suggested Skills: {len(battlesuit.get('suggested_skills', []))}")
else:
    print("M&M veri dosyası bulunamadı!")


