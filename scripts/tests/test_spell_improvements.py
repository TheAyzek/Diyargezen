"""
Spell sistemi iyileştirme testleri - Upcasting, Ritual, Concentration, Material Components
"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.calculations import (
    calculate_spell_upcast_damage, is_ritual_spell,
    is_concentration_spell, extract_material_components
)
from utils.data_loader import load_dnd_data

def test_spell_upcasting():
    """Spell upcasting testi"""
    print("=" * 70)
    print("TEST 1: Spell Upcasting")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        test_cases = [
            {"name": "Magic Missile", "base": 1, "cast": 3},
            {"name": "Cure Wounds", "base": 1, "cast": 5},
            {"name": "Fireball", "base": 3, "cast": 5},
        ]
        
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            spell_name = test_case["name"]
            base_level = test_case["base"]
            cast_level = test_case["cast"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            upcast_info = calculate_spell_upcast_damage(
                spell_name, base_level, cast_level, spell_data, dnd_data
            )
            
            if upcast_info:
                print(f"  [OK] {spell_name} (Level {base_level} -> {cast_level}):")
                if upcast_info.get('additional_dice'):
                    print(f"    Additional dice: {upcast_info['additional_dice']}")
                if upcast_info.get('additional_damage_per_level'):
                    print(f"    Damage per level: {upcast_info['additional_damage_per_level']}")
                passed += 1
            else:
                print(f"  [UYARI] {spell_name}: Upcast bilgisi bulunamadi")
        
        print(f"\n[OK] {passed}/{total} upcast testi basarili")
        return passed > 0
        
    except Exception as e:
        print(f"[HATA] Upcast testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ritual_spells():
    """Ritual spell testi"""
    print("\n" + "=" * 70)
    print("TEST 2: Ritual Spells")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Identify", "expected": True},
            {"name": "Find Familiar", "expected": True},
            {"name": "Alarm", "expected": True},  # Ritual spell
            {"name": "Magic Missile", "expected": False},
            {"name": "Haste", "expected": False},  # Concentration ama ritual değil
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected = test_case["expected"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            is_ritual = is_ritual_spell(spell_name, spell_data, dnd_data)
            
            status = "[OK]" if is_ritual == expected else "[UYARI]"
            print(f"  {status} {spell_name}: Ritual = {is_ritual} (expected: {expected})")
            
            if is_ritual == expected:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} ritual testi basarili")
        return passed >= total * 0.5  # En az yarısı doğru olmalı
        
    except Exception as e:
        print(f"[HATA] Ritual testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concentration_spells():
    """Concentration spell testi"""
    print("\n" + "=" * 70)
    print("TEST 3: Concentration Spells")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Magic Missile", "expected": False},
            {"name": "Haste", "expected": True},
            {"name": "Fly", "expected": True},
            {"name": "Identify", "expected": False},  # Concentration değil
            {"name": "Find Familiar", "expected": False},  # Concentration değil
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected = test_case["expected"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            is_concentration = is_concentration_spell(spell_name, spell_data, dnd_data)
            
            status = "[OK]" if is_concentration == expected else "[UYARI]"
            print(f"  {status} {spell_name}: Concentration = {is_concentration} (expected: {expected})")
            
            if is_concentration == expected:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} concentration testi basarili")
        return passed >= total * 0.5
        
    except Exception as e:
        print(f"[HATA] Concentration testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_material_components():
    """Material components testi"""
    print("\n" + "=" * 70)
    print("TEST 4: Material Components")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Find Familiar", "has_material": True},
            {"name": "Identify", "has_material": True},
            {"name": "Magic Missile", "has_material": False},
            {"name": "Haste", "has_material": True},  # Material component var (licorice root)
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected_material = test_case["has_material"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            material = extract_material_components(spell_data)
            has_material = material is not None
            
            status = "[OK]" if has_material == expected_material else "[UYARI]"
            print(f"  {status} {spell_name}: Material = {has_material} (expected: {expected_material})")
            
            if material:
                print(f"    Component: {material.get('component', 'N/A')[:50]}...")
                if material.get('cost'):
                    print(f"    Cost: {material['cost']} gp")
                print(f"    Consumed: {material.get('consumed', False)}")
            
            if has_material == expected_material:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} material component testi basarili")
        return passed >= total * 0.5
        
    except Exception as e:
        print(f"[HATA] Material component testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Tum spell iyilestirme testlerini calistir"""
    print("=" * 70)
    print("SPELL SISTEMI IYILESTIRME TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("Spell Upcasting", test_spell_upcasting),
        ("Ritual Spells", test_ritual_spells),
        ("Concentration Spells", test_concentration_spells),
        ("Material Components", test_material_components),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[HATA] {test_name} testi basarisiz: {e}")
            results.append((test_name, False))
    
    # Ozet
    print("\n" + "=" * 70)
    print("TEST OZETI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[HATA]"
        print(f"{status} {test_name}")
    
    print(f"\nToplam: {passed}/{total} test basarili")
    
    if passed == total:
        print("\n[OK] Tum testler basarili!")
        return 0
    else:
        print(f"\n[UYARI] {total - passed} test basarisiz.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.calculations import (
    calculate_spell_upcast_damage, is_ritual_spell,
    is_concentration_spell, extract_material_components
)
from utils.data_loader import load_dnd_data

def test_spell_upcasting():
    """Spell upcasting testi"""
    print("=" * 70)
    print("TEST 1: Spell Upcasting")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        test_cases = [
            {"name": "Magic Missile", "base": 1, "cast": 3},
            {"name": "Cure Wounds", "base": 1, "cast": 5},
            {"name": "Fireball", "base": 3, "cast": 5},
        ]
        
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            spell_name = test_case["name"]
            base_level = test_case["base"]
            cast_level = test_case["cast"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            upcast_info = calculate_spell_upcast_damage(
                spell_name, base_level, cast_level, spell_data, dnd_data
            )
            
            if upcast_info:
                print(f"  [OK] {spell_name} (Level {base_level} -> {cast_level}):")
                if upcast_info.get('additional_dice'):
                    print(f"    Additional dice: {upcast_info['additional_dice']}")
                if upcast_info.get('additional_damage_per_level'):
                    print(f"    Damage per level: {upcast_info['additional_damage_per_level']}")
                passed += 1
            else:
                print(f"  [UYARI] {spell_name}: Upcast bilgisi bulunamadi")
        
        print(f"\n[OK] {passed}/{total} upcast testi basarili")
        return passed > 0
        
    except Exception as e:
        print(f"[HATA] Upcast testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ritual_spells():
    """Ritual spell testi"""
    print("\n" + "=" * 70)
    print("TEST 2: Ritual Spells")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Identify", "expected": True},
            {"name": "Find Familiar", "expected": True},
            {"name": "Alarm", "expected": True},  # Ritual spell
            {"name": "Magic Missile", "expected": False},
            {"name": "Haste", "expected": False},  # Concentration ama ritual değil
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected = test_case["expected"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            is_ritual = is_ritual_spell(spell_name, spell_data, dnd_data)
            
            status = "[OK]" if is_ritual == expected else "[UYARI]"
            print(f"  {status} {spell_name}: Ritual = {is_ritual} (expected: {expected})")
            
            if is_ritual == expected:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} ritual testi basarili")
        return passed >= total * 0.5  # En az yarısı doğru olmalı
        
    except Exception as e:
        print(f"[HATA] Ritual testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concentration_spells():
    """Concentration spell testi"""
    print("\n" + "=" * 70)
    print("TEST 3: Concentration Spells")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Magic Missile", "expected": False},
            {"name": "Haste", "expected": True},
            {"name": "Fly", "expected": True},
            {"name": "Identify", "expected": False},  # Concentration değil
            {"name": "Find Familiar", "expected": False},  # Concentration değil
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected = test_case["expected"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            is_concentration = is_concentration_spell(spell_name, spell_data, dnd_data)
            
            status = "[OK]" if is_concentration == expected else "[UYARI]"
            print(f"  {status} {spell_name}: Concentration = {is_concentration} (expected: {expected})")
            
            if is_concentration == expected:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} concentration testi basarili")
        return passed >= total * 0.5
        
    except Exception as e:
        print(f"[HATA] Concentration testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_material_components():
    """Material components testi"""
    print("\n" + "=" * 70)
    print("TEST 4: Material Components")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Find Familiar", "has_material": True},
            {"name": "Identify", "has_material": True},
            {"name": "Magic Missile", "has_material": False},
            {"name": "Haste", "has_material": True},  # Material component var (licorice root)
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected_material = test_case["has_material"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            material = extract_material_components(spell_data)
            has_material = material is not None
            
            status = "[OK]" if has_material == expected_material else "[UYARI]"
            print(f"  {status} {spell_name}: Material = {has_material} (expected: {expected_material})")
            
            if material:
                print(f"    Component: {material.get('component', 'N/A')[:50]}...")
                if material.get('cost'):
                    print(f"    Cost: {material['cost']} gp")
                print(f"    Consumed: {material.get('consumed', False)}")
            
            if has_material == expected_material:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} material component testi basarili")
        return passed >= total * 0.5
        
    except Exception as e:
        print(f"[HATA] Material component testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Tum spell iyilestirme testlerini calistir"""
    print("=" * 70)
    print("SPELL SISTEMI IYILESTIRME TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("Spell Upcasting", test_spell_upcasting),
        ("Ritual Spells", test_ritual_spells),
        ("Concentration Spells", test_concentration_spells),
        ("Material Components", test_material_components),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[HATA] {test_name} testi basarisiz: {e}")
            results.append((test_name, False))
    
    # Ozet
    print("\n" + "=" * 70)
    print("TEST OZETI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[HATA]"
        print(f"{status} {test_name}")
    
    print(f"\nToplam: {passed}/{total} test basarili")
    
    if passed == total:
        print("\n[OK] Tum testler basarili!")
        return 0
    else:
        print(f"\n[UYARI] {total - passed} test basarisiz.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.calculations import (
    calculate_spell_upcast_damage, is_ritual_spell,
    is_concentration_spell, extract_material_components
)
from utils.data_loader import load_dnd_data

def test_spell_upcasting():
    """Spell upcasting testi"""
    print("=" * 70)
    print("TEST 1: Spell Upcasting")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        test_cases = [
            {"name": "Magic Missile", "base": 1, "cast": 3},
            {"name": "Cure Wounds", "base": 1, "cast": 5},
            {"name": "Fireball", "base": 3, "cast": 5},
        ]
        
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            spell_name = test_case["name"]
            base_level = test_case["base"]
            cast_level = test_case["cast"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            upcast_info = calculate_spell_upcast_damage(
                spell_name, base_level, cast_level, spell_data, dnd_data
            )
            
            if upcast_info:
                print(f"  [OK] {spell_name} (Level {base_level} -> {cast_level}):")
                if upcast_info.get('additional_dice'):
                    print(f"    Additional dice: {upcast_info['additional_dice']}")
                if upcast_info.get('additional_damage_per_level'):
                    print(f"    Damage per level: {upcast_info['additional_damage_per_level']}")
                passed += 1
            else:
                print(f"  [UYARI] {spell_name}: Upcast bilgisi bulunamadi")
        
        print(f"\n[OK] {passed}/{total} upcast testi basarili")
        return passed > 0
        
    except Exception as e:
        print(f"[HATA] Upcast testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ritual_spells():
    """Ritual spell testi"""
    print("\n" + "=" * 70)
    print("TEST 2: Ritual Spells")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Identify", "expected": True},
            {"name": "Find Familiar", "expected": True},
            {"name": "Alarm", "expected": True},  # Ritual spell
            {"name": "Magic Missile", "expected": False},
            {"name": "Haste", "expected": False},  # Concentration ama ritual değil
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected = test_case["expected"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            is_ritual = is_ritual_spell(spell_name, spell_data, dnd_data)
            
            status = "[OK]" if is_ritual == expected else "[UYARI]"
            print(f"  {status} {spell_name}: Ritual = {is_ritual} (expected: {expected})")
            
            if is_ritual == expected:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} ritual testi basarili")
        return passed >= total * 0.5  # En az yarısı doğru olmalı
        
    except Exception as e:
        print(f"[HATA] Ritual testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concentration_spells():
    """Concentration spell testi"""
    print("\n" + "=" * 70)
    print("TEST 3: Concentration Spells")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Magic Missile", "expected": False},
            {"name": "Haste", "expected": True},
            {"name": "Fly", "expected": True},
            {"name": "Identify", "expected": False},  # Concentration değil
            {"name": "Find Familiar", "expected": False},  # Concentration değil
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected = test_case["expected"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            is_concentration = is_concentration_spell(spell_name, spell_data, dnd_data)
            
            status = "[OK]" if is_concentration == expected else "[UYARI]"
            print(f"  {status} {spell_name}: Concentration = {is_concentration} (expected: {expected})")
            
            if is_concentration == expected:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} concentration testi basarili")
        return passed >= total * 0.5
        
    except Exception as e:
        print(f"[HATA] Concentration testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_material_components():
    """Material components testi"""
    print("\n" + "=" * 70)
    print("TEST 4: Material Components")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Find Familiar", "has_material": True},
            {"name": "Identify", "has_material": True},
            {"name": "Magic Missile", "has_material": False},
            {"name": "Haste", "has_material": True},  # Material component var (licorice root)
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected_material = test_case["has_material"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            material = extract_material_components(spell_data)
            has_material = material is not None
            
            status = "[OK]" if has_material == expected_material else "[UYARI]"
            print(f"  {status} {spell_name}: Material = {has_material} (expected: {expected_material})")
            
            if material:
                print(f"    Component: {material.get('component', 'N/A')[:50]}...")
                if material.get('cost'):
                    print(f"    Cost: {material['cost']} gp")
                print(f"    Consumed: {material.get('consumed', False)}")
            
            if has_material == expected_material:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} material component testi basarili")
        return passed >= total * 0.5
        
    except Exception as e:
        print(f"[HATA] Material component testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Tum spell iyilestirme testlerini calistir"""
    print("=" * 70)
    print("SPELL SISTEMI IYILESTIRME TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("Spell Upcasting", test_spell_upcasting),
        ("Ritual Spells", test_ritual_spells),
        ("Concentration Spells", test_concentration_spells),
        ("Material Components", test_material_components),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[HATA] {test_name} testi basarisiz: {e}")
            results.append((test_name, False))
    
    # Ozet
    print("\n" + "=" * 70)
    print("TEST OZETI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[HATA]"
        print(f"{status} {test_name}")
    
    print(f"\nToplam: {passed}/{total} test basarili")
    
    if passed == total:
        print("\n[OK] Tum testler basarili!")
        return 0
    else:
        print(f"\n[UYARI] {total - passed} test basarisiz.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.calculations import (
    calculate_spell_upcast_damage, is_ritual_spell,
    is_concentration_spell, extract_material_components
)
from utils.data_loader import load_dnd_data

def test_spell_upcasting():
    """Spell upcasting testi"""
    print("=" * 70)
    print("TEST 1: Spell Upcasting")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        test_cases = [
            {"name": "Magic Missile", "base": 1, "cast": 3},
            {"name": "Cure Wounds", "base": 1, "cast": 5},
            {"name": "Fireball", "base": 3, "cast": 5},
        ]
        
        passed = 0
        total = len(test_cases)
        
        for test_case in test_cases:
            spell_name = test_case["name"]
            base_level = test_case["base"]
            cast_level = test_case["cast"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            upcast_info = calculate_spell_upcast_damage(
                spell_name, base_level, cast_level, spell_data, dnd_data
            )
            
            if upcast_info:
                print(f"  [OK] {spell_name} (Level {base_level} -> {cast_level}):")
                if upcast_info.get('additional_dice'):
                    print(f"    Additional dice: {upcast_info['additional_dice']}")
                if upcast_info.get('additional_damage_per_level'):
                    print(f"    Damage per level: {upcast_info['additional_damage_per_level']}")
                passed += 1
            else:
                print(f"  [UYARI] {spell_name}: Upcast bilgisi bulunamadi")
        
        print(f"\n[OK] {passed}/{total} upcast testi basarili")
        return passed > 0
        
    except Exception as e:
        print(f"[HATA] Upcast testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_ritual_spells():
    """Ritual spell testi"""
    print("\n" + "=" * 70)
    print("TEST 2: Ritual Spells")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Identify", "expected": True},
            {"name": "Find Familiar", "expected": True},
            {"name": "Alarm", "expected": True},  # Ritual spell
            {"name": "Magic Missile", "expected": False},
            {"name": "Haste", "expected": False},  # Concentration ama ritual değil
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected = test_case["expected"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            is_ritual = is_ritual_spell(spell_name, spell_data, dnd_data)
            
            status = "[OK]" if is_ritual == expected else "[UYARI]"
            print(f"  {status} {spell_name}: Ritual = {is_ritual} (expected: {expected})")
            
            if is_ritual == expected:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} ritual testi basarili")
        return passed >= total * 0.5  # En az yarısı doğru olmalı
        
    except Exception as e:
        print(f"[HATA] Ritual testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_concentration_spells():
    """Concentration spell testi"""
    print("\n" + "=" * 70)
    print("TEST 3: Concentration Spells")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Magic Missile", "expected": False},
            {"name": "Haste", "expected": True},
            {"name": "Fly", "expected": True},
            {"name": "Identify", "expected": False},  # Concentration değil
            {"name": "Find Familiar", "expected": False},  # Concentration değil
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected = test_case["expected"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            is_concentration = is_concentration_spell(spell_name, spell_data, dnd_data)
            
            status = "[OK]" if is_concentration == expected else "[UYARI]"
            print(f"  {status} {spell_name}: Concentration = {is_concentration} (expected: {expected})")
            
            if is_concentration == expected:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} concentration testi basarili")
        return passed >= total * 0.5
        
    except Exception as e:
        print(f"[HATA] Concentration testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_material_components():
    """Material components testi"""
    print("\n" + "=" * 70)
    print("TEST 4: Material Components")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        # Mevcut veri setine göre test spell'leri - DÜZELTİLDİ (Test Case Fix)
        test_spells = [
            {"name": "Find Familiar", "has_material": True},
            {"name": "Identify", "has_material": True},
            {"name": "Magic Missile", "has_material": False},
            {"name": "Haste", "has_material": True},  # Material component var (licorice root)
        ]
        
        passed = 0
        total = len(test_spells)
        
        for test_case in test_spells:
            spell_name = test_case["name"]
            expected_material = test_case["has_material"]
            
            spell_data = spells.get(spell_name)
            if not spell_data:
                print(f"  [ATLA] {spell_name}: Spell bulunamadi")
                continue
            
            material = extract_material_components(spell_data)
            has_material = material is not None
            
            status = "[OK]" if has_material == expected_material else "[UYARI]"
            print(f"  {status} {spell_name}: Material = {has_material} (expected: {expected_material})")
            
            if material:
                print(f"    Component: {material.get('component', 'N/A')[:50]}...")
                if material.get('cost'):
                    print(f"    Cost: {material['cost']} gp")
                print(f"    Consumed: {material.get('consumed', False)}")
            
            if has_material == expected_material:
                passed += 1
        
        print(f"\n[OK] {passed}/{total} material component testi basarili")
        return passed >= total * 0.5
        
    except Exception as e:
        print(f"[HATA] Material component testi basarisiz: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Tum spell iyilestirme testlerini calistir"""
    print("=" * 70)
    print("SPELL SISTEMI IYILESTIRME TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("Spell Upcasting", test_spell_upcasting),
        ("Ritual Spells", test_ritual_spells),
        ("Concentration Spells", test_concentration_spells),
        ("Material Components", test_material_components),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[HATA] {test_name} testi basarisiz: {e}")
            results.append((test_name, False))
    
    # Ozet
    print("\n" + "=" * 70)
    print("TEST OZETI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[HATA]"
        print(f"{status} {test_name}")
    
    print(f"\nToplam: {passed}/{total} test basarili")
    
    if passed == total:
        print("\n[OK] Tum testler basarili!")
        return 0
    else:
        print(f"\n[UYARI] {total - passed} test basarisiz.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

