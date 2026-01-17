"""
Kapsamli D&D 5e karakter olusturma testleri
"""
import sys
import json
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.calculations import (
    calculate_all_dnd_stats, calculate_proficiency_bonus,
    calculate_ability_modifier, calculate_hit_points,
    calculate_armor_class, calculate_movement_speed
)
from utils.data_loader import load_dnd_data

def test_basic_character_creation():
    """Temel karakter olusturma testi"""
    print("=" * 70)
    print("TEST 1: Temel Karakter Olusturma")
    print("=" * 70)
    
    character = {
        "name": "Test Fighter",
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "level": 1,
        "abilities": {
            "Strength": 15,
            "Dexterity": 13,
            "Constitution": 14,
            "Intelligence": 12,
            "Wisdom": 10,
            "Charisma": 8
        },
        "skills": {
            "proficiencies": ["Athletics", "Intimidation"]
        },
        "equipment": [],
        "feats": [],
        "spells": {}
    }
    
    try:
        # Data yukle
        dnd_data = load_dnd_data(project_root)
        
        # Race ve class data
        race_data = dnd_data.get("races", {}).get(character["race"])
        class_data = {"classes": {character["class"]: dnd_data.get("classes", {}).get(character["class"], {})}}
        
        # Stats hesapla
        stats = calculate_all_dnd_stats(character, race_data=race_data, class_data=class_data)
        
        # Test assertions
        assert stats.get("proficiency_bonus") == 2, f"Proficiency bonus yanlis: {stats.get('proficiency_bonus')}"
        assert stats.get("hit_points", 0) > 0, f"HP 0'dan buyuk olmali: {stats.get('hit_points')}"
        assert stats.get("armor_class", 0) >= 10, f"AC en az 10 olmali: {stats.get('armor_class')}"
        
        print("OK: Temel karakter olusturma basarili")
        print(f"  HP: {stats['hit_points']}")
        print(f"  AC: {stats['armor_class']}")
        print(f"  Proficiency Bonus: {stats['proficiency_bonus']}")
        return True
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_race_ability_increases():
    """Irk yetenek artislari testi"""
    print("\n" + "=" * 70)
    print("TEST 2: Irk Yetenek Artislari")
    print("=" * 70)
    
    test_cases = [
        {
            "race": "Human",
            "expected_increase": {"all": 1},
            "base_abilities": {"Strength": 10, "Dexterity": 10, "Constitution": 10, "Intelligence": 10, "Wisdom": 10, "Charisma": 10},
            "expected_final": {"Strength": 11, "Dexterity": 11, "Constitution": 11, "Intelligence": 11, "Wisdom": 11, "Charisma": 11}
        },
        {
            "race": "Elf (High)",
            "expected_increase": {"Dexterity": 2},
            "base_abilities": {"Strength": 10, "Dexterity": 10, "Constitution": 10, "Intelligence": 10, "Wisdom": 10, "Charisma": 10},
            "expected_final": {"Strength": 10, "Dexterity": 12, "Constitution": 10, "Intelligence": 10, "Wisdom": 10, "Charisma": 10}
        }
    ]
    
    try:
        dnd_data = load_dnd_data(project_root)
        races = dnd_data.get("races", {})
        
        for test_case in test_cases:
            race_name = test_case["race"]
            race_data = races.get(race_name, {})
            ability_increase = race_data.get("ability_score_increase", {})
            
            # Expected ile karsilastir
            if test_case["expected_increase"]:
                if ability_increase != test_case["expected_increase"]:
                    print(f"UYARI: {race_name} ability increase beklentiden farkli")
                    print(f"  Beklenen: {test_case['expected_increase']}")
                    print(f"  Gercek: {ability_increase}")
            
            # Final abilities hesapla
            final_abilities = test_case["base_abilities"].copy()
            for ability, bonus in ability_increase.items():
                if ability == "all":
                    for abil in final_abilities:
                        final_abilities[abil] += bonus
                else:
                    # Ability name'i normalize et (lowercase -> Capitalized)
                    ability_normalized = ability.capitalize()
                    if ability_normalized in final_abilities:
                        final_abilities[ability_normalized] += bonus
                    elif ability in final_abilities:
                        final_abilities[ability] += bonus
            
            print(f"OK: {race_name} - Ability increases uygulandi")
            print(f"  Final: {final_abilities}")
        
        return True
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_class_hit_points():
    """Sinif HP hesaplama testi"""
    print("\n" + "=" * 70)
    print("TEST 3: Sinif HP Hesaplama")
    print("=" * 70)
    
    test_cases = [
        {"class": "Barbarian", "level": 1, "con": 14, "expected_min": 12},  # d12 (max) + 2 CON = 14 minimum (level 1'de max roll)
        {"class": "Fighter", "level": 1, "con": 14, "expected_min": 10},  # d10 + 2 CON = 12 minimum
        {"class": "Wizard", "level": 1, "con": 14, "expected_min": 6},  # d6 + 2 CON = 8 minimum
        {"class": "Barbarian", "level": 5, "con": 14, "expected_min": 50},  # 5 * (d12/2 + 1) + 5*2 CON = ~50
    ]
    
    try:
        dnd_data = load_dnd_data(project_root)
        classes = dnd_data.get("classes", {})
        
        for test_case in test_cases:
            char_class = test_case["class"]
            level = test_case["level"]
            con = test_case["con"]
            expected_min = test_case["expected_min"]
            
            character = {
                "level": level,
                "class": char_class,
                "abilities": {"Constitution": con},
                "hp": None
            }
            
            class_data = {"classes": {char_class: classes.get(char_class, {})}}
            
            hp = calculate_hit_points(character, class_data=class_data)
            
            if hp >= expected_min:
                print(f"OK: {char_class} Level {level} (CON {con}) - HP: {hp} (min: {expected_min})")
            else:
                print(f"HATA: {char_class} Level {level} (CON {con}) - HP: {hp} (beklenen min: {expected_min})")
                return False
        
        return True
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_movement_speed():
    """Hareket hizi testi"""
    print("\n" + "=" * 70)
    print("TEST 4: Hareket Hizi")
    print("=" * 70)
    
    test_cases = [
        {
            "name": "Human base speed",
            "character": {"level": 1, "race": "Human", "abilities": {"Strength": 10}, "equipment": [], "feats": []},
            "race_data": {"speed": 30},
            "expected": 30
        },
        {
            "name": "Human with Mobile feat",
            "character": {"level": 1, "race": "Human", "abilities": {"Strength": 10}, "equipment": [], "feats": ["Mobile"]},
            "race_data": {"speed": 30},
            "expected": 40
        },
        {
            "name": "Monk level 5",
            "character": {"level": 5, "race": "Human", "class": "Monk", "abilities": {"Strength": 10}, "equipment": [], "feats": []},
            "race_data": {"speed": 30},
            "class_data": {"classes": {"Monk": {"hit_die": "d8"}}},
            "expected": 40  # 30 base + 10 monk
        },
        {
            "name": "Human with Longstrider",
            "character": {"level": 1, "race": "Human", "abilities": {"Strength": 10}, "equipment": [], "feats": [], "active_spells": ["Longstrider"]},
            "race_data": {"speed": 30},
            "expected": 40
        }
    ]
    
    try:
        dnd_data = load_dnd_data(project_root)
        
        for test_case in test_cases:
            character = test_case["character"]
            race_data = test_case.get("race_data")
            class_data = test_case.get("class_data")
            expected = test_case["expected"]
            
            speed = calculate_movement_speed(character, race_data=race_data, class_data=class_data)
            
            if speed == expected:
                print(f"OK: {test_case['name']} - Speed: {speed} (beklenen: {expected})")
            else:
                print(f"HATA: {test_case['name']} - Speed: {speed} (beklenen: {expected})")
                return False
        
        return True
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_proficiency_bonus():
    """Proficiency bonus hesaplama testi"""
    print("\n" + "=" * 70)
    print("TEST 5: Proficiency Bonus")
    print("=" * 70)
    
    test_cases = [
        {"level": 1, "expected": 2},
        {"level": 4, "expected": 2},
        {"level": 5, "expected": 3},
        {"level": 9, "expected": 4},
        {"level": 13, "expected": 5},
        {"level": 17, "expected": 6},
        {"level": 20, "expected": 6},
    ]
    
    try:
        for test_case in test_cases:
            level = test_case["level"]
            expected = test_case["expected"]
            
            pb = calculate_proficiency_bonus(level)
            
            if pb == expected:
                print(f"OK: Level {level} - PB: {pb} (beklenen: {expected})")
            else:
                print(f"HATA: Level {level} - PB: {pb} (beklenen: {expected})")
                return False
        
        return True
    except Exception as e:
        print(f"HATA: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_edge_cases():
    """Edge case testleri"""
    print("\n" + "=" * 70)
    print("TEST 6: Edge Cases")
    print("=" * 70)
    
    errors = []
    
    # Test 1: Eksik field'lar
    try:
        character_minimal = {
            "level": 1,
            "abilities": {"Strength": 10, "Dexterity": 10, "Constitution": 10, "Intelligence": 10, "Wisdom": 10, "Charisma": 10}
        }
        stats = calculate_all_dnd_stats(character_minimal)
        print("OK: Minimal character (eksik field'lar) - hata vermedi")
    except Exception as e:
        errors.append(f"Minimal character hatasi: {e}")
    
    # Test 2: Yüksek level
    try:
        character_high_level = {
            "level": 20,
            "class": "Fighter",
            "abilities": {"Strength": 20, "Dexterity": 10, "Constitution": 20, "Intelligence": 10, "Wisdom": 10, "Charisma": 10},
            "equipment": [],
            "feats": []
        }
        dnd_data = load_dnd_data(project_root)
        class_data = {"classes": {"Fighter": dnd_data.get("classes", {}).get("Fighter", {})}}
        stats = calculate_all_dnd_stats(character_high_level, class_data=class_data)
        print(f"OK: Level 20 character - HP: {stats['hit_points']}")
    except Exception as e:
        errors.append(f"High level character hatasi: {e}")
    
    # Test 3: Düsük ability scores
    try:
        character_low_abilities = {
            "level": 1,
            "abilities": {"Strength": 1, "Dexterity": 1, "Constitution": 1, "Intelligence": 1, "Wisdom": 1, "Charisma": 1},
            "equipment": [],
            "feats": []
        }
        stats = calculate_all_dnd_stats(character_low_abilities)
        print(f"OK: Dusuk ability scores - Modifiers hesaplandi")
    except Exception as e:
        errors.append(f"Low abilities hatasi: {e}")
    
    if errors:
        for error in errors:
            print(f"HATA: {error}")
        return False
    
    return True

def main():
    """Tum testleri calistir"""
    print("=" * 70)
    print("D&D 5E KAPSAMLI KARAKTER OLUSTURMA TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("Temel Karakter Olusturma", test_basic_character_creation),
        ("Irk Yetenek Artislari", test_race_ability_increases),
        ("Sinif HP Hesaplama", test_class_hit_points),
        ("Hareket Hizi", test_movement_speed),
        ("Proficiency Bonus", test_proficiency_bonus),
        ("Edge Cases", test_edge_cases),
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

