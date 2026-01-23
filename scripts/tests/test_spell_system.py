"""
Spell sistemi kapsamli testleri
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.calculations import (
    calculate_spell_slots, calculate_spell_save_dc,
    calculate_spell_attack_bonus
)
from utils.data_loader import load_dnd_data

def test_spell_slots_by_class():
    """Sinifa gore spell slots testi"""
    print("=" * 70)
    print("TEST 1: Sinifa Gore Spell Slots")
    print("=" * 70)
    
    test_cases = [
        {"class": "Wizard", "level": 1, "expected": {1: 2}},
        {"class": "Wizard", "level": 3, "expected": {1: 4, 2: 2}},
        {"class": "Wizard", "level": 5, "expected": {1: 4, 2: 3, 3: 2}},
        {"class": "Sorcerer", "level": 5, "expected": {1: 4, 2: 3, 3: 2}},
        {"class": "Bard", "level": 3, "expected": {1: 4, 2: 2}},
        {"class": "Cleric", "level": 5, "expected": {1: 4, 2: 3, 3: 2}},
        {"class": "Paladin", "level": 5, "expected": {1: 4, 2: 2}},  # Half caster
        {"class": "Warlock", "level": 3, "expected": {2: 2}},  # Pact magic
        {"class": "Warlock", "level": 5, "expected": {3: 2}},
    ]
    
    try:
        dnd_data = load_dnd_data(project_root)
        classes = dnd_data.get("classes", {})
        
        for test_case in test_cases:
            char_class = test_case["class"]
            level = test_case["level"]
            expected = test_case["expected"]
            
            character = {
                "level": level,
                "class": char_class,
                "abilities": {"Intelligence": 16, "Charisma": 16, "Wisdom": 16},
                "equipment": [],
                "feats": []
            }
            
            class_data = {"classes": {char_class: classes.get(char_class, {})}}
            spell_slots = calculate_spell_slots(character, class_data=class_data)
            
            # Expected ile karsilastir
            matches = True
            for slot_level, expected_count in expected.items():
                actual_count = spell_slots.get(slot_level, 0)
                if actual_count != expected_count:
                    matches = False
                    print(f"HATA: {char_class} Level {level} - {slot_level} slot: {actual_count} (beklenen: {expected_count})")
            
            if matches:
                print(f"OK: {char_class} Level {level} - Spell slots: {spell_slots}")
        
        return True
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_spell_save_dc():
    """Spell Save DC testi"""
    print("\n" + "=" * 70)
    print("TEST 2: Spell Save DC")
    print("=" * 70)
    
    test_cases = [
        {"class": "Wizard", "level": 1, "int": 16, "expected_dc": 13},  # 8 + 2 (PB) + 3 (INT mod)
        {"class": "Wizard", "level": 5, "int": 16, "expected_dc": 14},  # 8 + 3 (PB) + 3 (INT mod)
        {"class": "Cleric", "level": 1, "wis": 16, "expected_dc": 13},  # 8 + 2 (PB) + 3 (WIS mod)
        {"class": "Bard", "level": 1, "cha": 18, "expected_dc": 14},  # 8 + 2 (PB) + 4 (CHA mod)
    ]
    
    try:
        dnd_data = load_dnd_data(project_root)
        classes = dnd_data.get("classes", {})
        
        for test_case in test_cases:
            char_class = test_case["class"]
            level = test_case["level"]
            expected_dc = test_case["expected_dc"]
            
            # Spellcasting ability'ye gore ability score set et
            abilities = {}
            if char_class in ["Wizard", "Artificer"]:
                abilities["Intelligence"] = test_case.get("int", 16)
            elif char_class in ["Cleric", "Druid", "Ranger"]:
                abilities["Wisdom"] = test_case.get("wis", 16)
            elif char_class in ["Bard", "Paladin", "Sorcerer", "Warlock"]:
                abilities["Charisma"] = test_case.get("cha", 16)
            
            character = {
                "level": level,
                "class": char_class,
                "abilities": abilities,
                "equipment": [],
                "feats": []
            }
            
            class_data = {"classes": {char_class: classes.get(char_class, {})}}
            spell_dc = calculate_spell_save_dc(character, class_data=class_data)
            
            if spell_dc == expected_dc:
                print(f"OK: {char_class} Level {level} - Spell Save DC: {spell_dc} (beklenen: {expected_dc})")
            else:
                print(f"HATA: {char_class} Level {level} - Spell Save DC: {spell_dc} (beklenen: {expected_dc})")
                return False
        
        return True
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_spell_attack_bonus():
    """Spell Attack Bonus testi"""
    print("\n" + "=" * 70)
    print("TEST 3: Spell Attack Bonus")
    print("=" * 70)
    
    test_cases = [
        {"class": "Wizard", "level": 1, "int": 16, "expected_bonus": 5},  # 2 (PB) + 3 (INT mod)
        {"class": "Wizard", "level": 5, "int": 16, "expected_bonus": 6},  # 3 (PB) + 3 (INT mod)
        {"class": "Wizard", "level": 5, "int": 20, "expected_bonus": 8},  # 3 (PB) + 5 (INT mod)
    ]
    
    try:
        dnd_data = load_dnd_data(project_root)
        classes = dnd_data.get("classes", {})
        
        for test_case in test_cases:
            char_class = test_case["class"]
            level = test_case["level"]
            expected_bonus = test_case["expected_bonus"]
            
            abilities = {"Intelligence": test_case.get("int", 16)}
            character = {
                "level": level,
                "class": char_class,
                "abilities": abilities,
                "equipment": [],
                "feats": []
            }
            
            class_data = {"classes": {char_class: classes.get(char_class, {})}}
            attack_bonus = calculate_spell_attack_bonus(character, class_data=class_data)
            
            if attack_bonus == expected_bonus:
                print(f"OK: {char_class} Level {level} (INT {test_case.get('int')}) - Spell Attack Bonus: {attack_bonus} (beklenen: {expected_bonus})")
            else:
                print(f"HATA: {char_class} Level {level} (INT {test_case.get('int')}) - Spell Attack Bonus: {attack_bonus} (beklenen: {expected_bonus})")
                return False
        
        return True
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Tum testleri calistir"""
    print("=" * 70)
    print("D&D 5E SPELL SISTEMI TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("Sinifa Gore Spell Slots", test_spell_slots_by_class),
        ("Spell Save DC", test_spell_save_dc),
        ("Spell Attack Bonus", test_spell_attack_bonus),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\nHATA: {test_name} testi sirasinda exception: {e}")
            import traceback
            traceback.print_exc()
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
        print(f"\n[UYARI] {total - passed} test basarisiz. Kontrol edin.")
        return 1

if __name__ == "__main__":
    sys.exit(main())

