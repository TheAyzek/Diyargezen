#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M&M veri detaylarını kontrol et"""

import json
from pathlib import Path

data_file = Path("data/mm_data.json")
if data_file.exists():
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    print("=" * 70)
    print("M&M VERİ DETAYLARI")
    print("=" * 70)
    
    # Abilities
    print("\n1. ABILITIES AÇIKLAMALARI:")
    abilities = data.get('abilities', {})
    for name, ab in abilities.items():
        desc_len = len(ab.get('description', ''))
        desc_preview = ab.get('description', '')[:80]
        status = "✅" if desc_len > 100 else "⚠️"
        print(f"  {status} {name}: {desc_len} karakter - {desc_preview}...")
    
    # Archetype örneği
    print("\n2. ARCHETYPE ÖRNEĞİ (Battlesuit):")
    battlesuit = data.get('archetypes', {}).get('Battlesuit', {})
    print(f"  Suggested Powers: {len(battlesuit.get('suggested_powers', []))}")
    print(f"  Suggested Advantages: {len(battlesuit.get('suggested_advantages', []))}")
    print(f"  Suggested Skills: {len(battlesuit.get('suggested_skills', []))}")
    
    if battlesuit.get('suggested_advantages'):
        print(f"\n  Örnek Advantages:")
        for i, adv in enumerate(battlesuit['suggested_advantages'][:5]):
            print(f"    {i+1}. {adv}")
    
    if battlesuit.get('suggested_skills'):
        print(f"\n  Örnek Skills:")
        for i, skill in enumerate(battlesuit['suggested_skills'][:5]):
            print(f"    {i+1}. {skill}")
    
    # Power Effects
    print("\n3. POWER EFFECTS:")
    power_effects = data.get('power_effects', {})
    print(f"  Toplam: {len(power_effects)}")
    if power_effects:
        for name, effect in list(power_effects.items())[:5]:
            print(f"    - {name}: Category={effect.get('category', 'N/A')}")


