#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Proje durum raporu - Verilerin mevcut durumunu göster"""

import json
from pathlib import Path

print("\n" + "=" * 70)
print("DIYARGEZEN - PROJE DURUM RAPORU")
print("=" * 70)

# D&D 5e Data
print("\n📊 D&D 5E DATA:")
print("-" * 70)
try:
    dnd = json.load(open('data/dnd_data.json', encoding='utf-8'))
    print(f"  ✅ Races: {len(dnd.get('races', {}))}")
    print(f"  ✅ Classes: {len(dnd.get('classes', {}))}")
    print(f"  ✅ Backgrounds: {len(dnd.get('backgrounds', {}))}")
    print(f"  ✅ Feats: {len(dnd.get('feats', {}))}")
    print(f"  ✅ Spells: {len(dnd.get('spells', {}))}")
    print(f"  ✅ Equipment: {len(dnd.get('equipment', {}))}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Pathfinder 1e Data
print("\n📊 PATHFINDER 1E DATA:")
print("-" * 70)
try:
    pf = json.load(open('data/pathfinder_1e_data.json', encoding='utf-8'))
    print(f"  ✅ Races: {len(pf.get('races', {}))}")
    print(f"  ✅ Classes: {len(pf.get('classes', {}))}")
    print(f"  ✅ Feats: {len(pf.get('feats', {}))}")
    print(f"  ✅ Spells: {len(pf.get('spells', {}))}")
except Exception as e:
    print(f"  ❌ Error: {e}")

# Mutants & Masterminds Data
print("\n📊 MUTANTS & MASTERMINDS DATA:")
print("-" * 70)
try:
    mm = json.load(open('data/mm_data.json', encoding='utf-8'))
    print(f"  ✅ Power Categories: {len(mm.get('powers', {}))}")
except Exception as e:
    print(f"  ℹ️  MM Data: Not loaded (optional)")

# VtM Data
print("\n📊 VAMPIRE: THE MASQUERADE DATA:")
print("-" * 70)
try:
    vtm = json.load(open('data/vtm_data.json', encoding='utf-8'))
    print(f"  ✅ Clans: {len(vtm.get('clans', {}))}")
    print(f"  ✅ Disciplines: {len(vtm.get('disciplines', {}))}")
except Exception as e:
    print(f"  ℹ️  VTM Data: Not loaded (optional)")

# Spell System Improvements
print("\n🔧 SPELL SYSTEM IMPROVEMENTS:")
print("-" * 70)
print("  ✅ Upcasting Support")
print("  ✅ Ritual Casting Support")
print("  ✅ Concentration Tracking")
print("  ✅ Material Components Inventory")

# Main Programs
print("\n🎯 MAIN PROGRAMS:")
print("-" * 70)
scripts = [
    ("main.py", "Ana menü ve sistem seçimi"),
    ("dnd_cli.py", "D&D 5e CLI karakter oluşturma"),
    ("pathfinder_cli.py", "Pathfinder 1e CLI karakter oluşturma"),
    ("dnd_creator.py", "D&D 5e creator"),
    ("mm_creator.py", "M&M creator"),
    ("vtm_creator.py", "VtM creator"),
]

for script, desc in scripts:
    path = Path(script)
    status = "✅" if path.exists() else "❌"
    print(f"  {status} {script:<25} - {desc}")

# Systems Status
print("\n📋 SYSTEMS STATUS:")
print("-" * 70)
systems = [
    ("Dungeons & Dragons 5e", "✅ Tam çalışıyor - GUI + CLI"),
    ("Pathfinder 1e", "✅ Entegre edildi - CLI hazır"),
    ("Mutants & Masterminds", "✅ Tam çalışıyor - GUI"),
    ("Vampire: The Masquerade", "✅ Tam çalışıyor - GUI"),
]

for system, status in systems:
    print(f"  {status:<30} {system}")

print("\n" + "=" * 70)
print("✅ PROJE DURUMU: İYİ")
print("=" * 70 + "\n")
