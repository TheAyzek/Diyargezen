#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Merge logic'i test et"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from utils.pathfinder_scraper import PathfinderScraper, _merge_category_data


def test_merge_logic():
    """Merge logic'ini test et"""
    print("=" * 60)
    print("MERGE LOGIC TEST")
    print("=" * 60)
    
    # Test verisi oluştur
    primary = {
        "Human": {
            "ability_score_increase": {"any": 2},
            "size": "Medium",
            "speed": 30,
            "vision": "normal",
            "languages": ["Common"],
            "traits": ["Medium", "Normal Speed"],
            "description": "Primary description"
        },
        "Elf": {
            "ability_score_increase": {"dexterity": 2, "intelligence": 2},
            "size": "Medium",
            "speed": 30,
            "vision": "low-light",
            "languages": ["Common", "Elven"],
            "traits": ["Medium", "Low-Light Vision"]
        }
    }
    
    secondary = {
        "Human": {
            "ability_score_increase": {"any": 2},
            "size": "Medium",
            "speed": 30,
            "vision": "normal",
            "languages": ["Common", "Giant", "Goblin"],  # Daha fazla dil
            "traits": ["Medium", "Normal Speed", "Bonus Feat"],  # Ekstra trait
            "description": "Secondary description - more detailed",  # Daha detaylı
            "favored_classes": ["Any"]  # Yeni alan
        },
        "Dwarf": {  # Yeni ırk
            "ability_score_increase": {"constitution": 2, "wisdom": 2},
            "size": "Medium",
            "speed": 20,
            "vision": "darkvision",
            "languages": ["Common", "Dwarven"]
        }
    }
    
    print("\n📊 Primary veri:")
    print(f"  - Human: {len(primary['Human'])} alan")
    print(f"  - Elf: {len(primary['Elf'])} alan")
    
    print("\n📊 Secondary veri:")
    print(f"  - Human: {len(secondary['Human'])} alan")
    print(f"  - Dwarf: {len(secondary['Dwarf'])} alan")
    
    # Merge et
    merged = _merge_category_data(primary, secondary)
    
    print("\n📊 Birleştirilmiş veri:")
    print(f"  - Toplam ırk: {len(merged)}")
    
    # Human'ı kontrol et
    human_merged = merged.get("Human", {})
    print(f"\n✅ Human merge kontrolü:")
    print(f"  - Languages: {human_merged.get('languages', [])}")
    print(f"    (Primary: {primary['Human']['languages']}, Secondary: {secondary['Human']['languages']})")
    print(f"  - Traits: {human_merged.get('traits', [])}")
    print(f"    (Primary: {primary['Human']['traits']}, Secondary: {secondary['Human']['traits']})")
    print(f"  - Favored Classes: {human_merged.get('favored_classes', 'Yok')}")
    print(f"  - Description: {human_merged.get('description', 'Yok')[:50]}...")
    
    # Dwarf'ı kontrol et (yeni eklenen)
    dwarf_merged = merged.get("Dwarf", {})
    print(f"\n✅ Dwarf merge kontrolü (yeni eklenen):")
    print(f"  - Ability Score: {dwarf_merged.get('ability_score_increase', {})}")
    print(f"  - Vision: {dwarf_merged.get('vision', 'Yok')}")
    
    # Elf'i kontrol et (sadece primary'de var)
    elf_merged = merged.get("Elf", {})
    print(f"\n✅ Elf merge kontrolü (sadece primary'de):")
    print(f"  - Ability Score: {elf_merged.get('ability_score_increase', {})}")
    print(f"  - Vision: {elf_merged.get('vision', 'Yok')}")
    
    # Test sonuçları
    print("\n" + "=" * 60)
    print("TEST SONUÇLARI")
    print("=" * 60)
    
    tests_passed = 0
    tests_total = 0
    
    # Test 1: Human'ın languages'ı birleştirildi mi?
    tests_total += 1
    if len(human_merged.get('languages', [])) >= len(primary['Human']['languages']):
        print("✅ Test 1: Languages birleştirildi")
        tests_passed += 1
    else:
        print("❌ Test 1: Languages birleştirilemedi")
    
    # Test 2: Human'ın traits'i birleştirildi mi?
    tests_total += 1
    if len(human_merged.get('traits', [])) >= len(primary['Human']['traits']):
        print("✅ Test 2: Traits birleştirildi")
        tests_passed += 1
    else:
        print("❌ Test 2: Traits birleştirilemedi")
    
    # Test 3: Human'ın favored_classes eklendi mi?
    tests_total += 1
    if 'favored_classes' in human_merged:
        print("✅ Test 3: Favored classes eklendi")
        tests_passed += 1
    else:
        print("❌ Test 3: Favored classes eklenemedi")
    
    # Test 4: Dwarf eklendi mi?
    tests_total += 1
    if 'Dwarf' in merged:
        print("✅ Test 4: Yeni ırk (Dwarf) eklendi")
        tests_passed += 1
    else:
        print("❌ Test 4: Yeni ırk eklenemedi")
    
    # Test 5: Elf korundu mu?
    tests_total += 1
    if 'Elf' in merged and merged['Elf'] == primary['Elf']:
        print("✅ Test 5: Sadece primary'de olan ırk (Elf) korundu")
        tests_passed += 1
    else:
        print("❌ Test 5: Elf korunamadı")
    
    print(f"\n📊 Sonuç: {tests_passed}/{tests_total} test başarılı")
    
    if tests_passed == tests_total:
        print("✅ Merge logic çalışıyor!")
        return True
    else:
        print("❌ Merge logic'te sorun var!")
        return False


if __name__ == "__main__":
    success = test_merge_logic()
    sys.exit(0 if success else 1)


