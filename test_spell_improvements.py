#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spell sistemi iyileştirmelerini test et"""

from utils.calculations import (
    calculate_spell_upcasting,
    check_ritual_casting,
    track_spell_concentration,
    calculate_material_components_needed
)

print("=" * 70)
print("D&D 5E SPELL SYSTEM IMPROVEMENTS TEST")
print("=" * 70)

# Test 1: Upcasting
print("\n1. UPCASTING TEST")
print("-" * 70)
spell = {
    'name': 'Magic Missile',
    'level': 1,
    'ritual': False,
    'scaling': 'Add 1 missile for each slot level above 1st'
}
result = calculate_spell_upcasting(spell, 3)
print(f"Original: {spell['name']} (Level {spell['level']})")
print(f"Cast with slot level: 3")
print(f"Result:")
print(f"  - Upcasted levels: {result.get('upcasted_levels')}")
print(f"  - Scaling effect: {result.get('scaling_effect')}")

# Test 2: Ritual Casting
print("\n2. RITUAL CASTING TEST")
print("-" * 70)
wizard = {
    'class': 'Wizard',
    'name': 'Gandalf',
    'spellbook': ['Magic Missile', 'Detect Magic', 'Identify', 'Light']
}
ritual_spell = {
    'name': 'Identify',
    'level': 1,
    'ritual': True
}
non_ritual_spell = {
    'name': 'Magic Missile',
    'level': 1,
    'ritual': False
}
print(f"Wizard: {wizard['name']}")
print(f"Spellbook: {wizard['spellbook']}")
print(f"Identify (ritual spell): {check_ritual_casting(wizard, ritual_spell)}")
print(f"Magic Missile (non-ritual): {check_ritual_casting(wizard, non_ritual_spell)}")

# Test 3: Concentration Tracking
print("\n3. CONCENTRATION TRACKING TEST")
print("-" * 70)
character = {
    'active_spells': {
        'requires_concentration': True,
        'concentration_spell': 'Concentration Spell'
    }
}
result = track_spell_concentration(character, 'Magic Missile')
print(f"Current concentration spell: Concentration Spell")
print(f"New spell to cast: Magic Missile")
print(f"Result:")
print(f"  - Can cast: {result['can_cast']}")
print(f"  - Breaks concentration: {result['breaks_current_concentration']}")
print(f"  - Warning: {result['warning']}")

# Test 4: Material Components
print("\n4. MATERIAL COMPONENTS TEST")
print("-" * 70)
spells = [
    {
        'name': 'Fireball',
        'level': 3,
        'material_components': ['Sulfur', 'Rubystone'],
        'material_consumed': True
    },
    {
        'name': 'Magic Circle',
        'level': 3,
        'material_components': ['Rubystone', 'Holy water'],
        'material_consumed': False
    }
]
result = calculate_material_components_needed(spells)
print(f"Spells being cast: {[s['name'] for s in spells]}")
print(f"Materials needed:")
for material, info in result['all_materials'].items():
    consumed = " (CONSUMED)" if info['consumed'] else ""
    print(f"  - {material}: {info['count']} uses{consumed}")

print("\n" + "=" * 70)
print("✅ ALL TESTS COMPLETED")
print("=" * 70)
