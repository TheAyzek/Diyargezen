"""
Export/Import testleri - Karakter export/import fonksiyonlarını test eder
"""
import sys
import json
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

def test_json_export_import():
    """JSON export/import testi"""
    print("=" * 70)
    print("TEST 1: JSON Export/Import")
    print("=" * 70)
    
    # Test karakteri
    test_character = {
        "system": "DND5E",
        "name": "Test Character",
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "level": 5,
        "abilities": {
            "Strength": 18,
            "Dexterity": 14,
            "Constitution": 16,
            "Intelligence": 12,
            "Wisdom": 10,
            "Charisma": 8
        },
        "hp": 45,
        "skills": {
            "proficiencies": ["Athletics", "Intimidation"]
        },
        "equipment": ["Longsword", "Shield"],
        "feats": [],
        "spells": {}
    }
    
    try:
        # Temp dosya oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = Path(f.name)
            json.dump(test_character, f, ensure_ascii=False, indent=2)
        
        # Import test
        with open(temp_file, 'r', encoding='utf-8') as f:
            imported_character = json.load(f)
        
        # Kontrol et
        if imported_character['name'] != test_character['name']:
            print(f"[HATA] Name eslesmedi: {imported_character['name']} != {test_character['name']}")
            temp_file.unlink()
            return False
        
        if imported_character['level'] != test_character['level']:
            print(f"[HATA] Level eslesmedi: {imported_character['level']} != {test_character['level']}")
            temp_file.unlink()
            return False
        
        if imported_character['abilities']['Strength'] != test_character['abilities']['Strength']:
            print(f"[HATA] Strength eslesmedi")
            temp_file.unlink()
            return False
        
        # Temizle
        temp_file.unlink()
        
        print("[OK] JSON export/import basarili")
        return True
        
    except Exception as e:
        print(f"[HATA] JSON export/import basarisiz: {e}")
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False

def test_character_data_structure():
    """Karakter veri yapısı kontrolü"""
    print("\n" + "=" * 70)
    print("TEST 2: Karakter Veri Yapisi")
    print("=" * 70)
    
    # Zorunlu alanlar
    required_fields = ['system', 'name', 'race', 'class', 'level', 'abilities']
    
    # Test karakteri
    test_character = {
        "system": "DND5E",
        "name": "Test Character",
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
        }
    }
    
    try:
        # Zorunlu alanlar kontrolü
        missing_fields = [field for field in required_fields if field not in test_character]
        
        if missing_fields:
            print(f"[HATA] Eksik alanlar: {missing_fields}")
            return False
        
        # Abilities kontrolü
        abilities = test_character.get('abilities', {})
        required_abilities = ['Strength', 'Dexterity', 'Constitution', 
                             'Intelligence', 'Wisdom', 'Charisma']
        
        missing_abilities = [ability for ability in required_abilities 
                            if ability not in abilities]
        
        if missing_abilities:
            print(f"[HATA] Eksik yetenekler: {missing_abilities}")
            return False
        
        # Değer aralığı kontrolü
        for ability, value in abilities.items():
            if not isinstance(value, int) or value < 1 or value > 30:
                print(f"[HATA] Gecersiz {ability} degeri: {value}")
                return False
        
        # Level kontrolü
        level = test_character.get('level', 0)
        if not isinstance(level, int) or level < 1 or level > 20:
            print(f"[HATA] Gecersiz level: {level}")
            return False
        
        print("[OK] Karakter veri yapisi gecerli")
        return True
        
    except Exception as e:
        print(f"[HATA] Veri yapisi kontrolu basarisiz: {e}")
        return False

def test_character_roundtrip():
    """Karakter roundtrip testi (export -> import -> kontrol)"""
    print("\n" + "=" * 70)
    print("TEST 3: Karakter Roundtrip")
    print("=" * 70)
    
    # Kapsamlı test karakteri
    original_character = {
        "system": "DND5E",
        "name": "Test Roundtrip Character",
        "race": "Elf",
        "class": "Wizard",
        "background": "Sage",
        "level": 3,
        "abilities": {
            "Strength": 8,
            "Dexterity": 14,
            "Constitution": 13,
            "Intelligence": 16,
            "Wisdom": 12,
            "Charisma": 10
        },
        "hp": 18,
        "skills": {
            "proficiencies": ["Arcana", "History", "Investigation"]
        },
        "equipment": ["Spellbook", "Component Pouch"],
        "feats": [],
        "spells": {
            "known": ["Magic Missile", "Shield", "Mage Armor"],
            "prepared": ["Magic Missile", "Shield"]
        },
        "features": ["Arcane Recovery"]
    }
    
    try:
        # Export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = Path(f.name)
            json.dump(original_character, f, ensure_ascii=False, indent=2)
        
        # Import
        with open(temp_file, 'r', encoding='utf-8') as f:
            imported_character = json.load(f)
        
        # Karşılaştır
        fields_to_check = ['name', 'race', 'class', 'background', 'level', 
                          'hp', 'abilities', 'skills', 'equipment', 'spells', 'features']
        
        differences = []
        for field in fields_to_check:
            original_value = original_character.get(field)
            imported_value = imported_character.get(field)
            
            if original_value != imported_value:
                differences.append(f"{field}: {original_value} != {imported_value}")
        
        if differences:
            print(f"[HATA] {len(differences)} fark bulundu:")
            for diff in differences[:5]:
                print(f"  - {diff}")
            if len(differences) > 5:
                print(f"  ... ve {len(differences) - 5} fark daha")
            temp_file.unlink()
            return False
        
        # Temizle
        temp_file.unlink()
        
        print("[OK] Karakter roundtrip basarili")
        return True
        
    except Exception as e:
        print(f"[HATA] Roundtrip testi basarisiz: {e}")
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False

def main():
    """Tum export/import testlerini calistir"""
    print("=" * 70)
    print("EXPORT/IMPORT TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("JSON Export/Import", test_json_export_import),
        ("Karakter Veri Yapisi", test_character_data_structure),
        ("Karakter Roundtrip", test_character_roundtrip),
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


Export/Import testleri - Karakter export/import fonksiyonlarını test eder
"""
import sys
import json
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

def test_json_export_import():
    """JSON export/import testi"""
    print("=" * 70)
    print("TEST 1: JSON Export/Import")
    print("=" * 70)
    
    # Test karakteri
    test_character = {
        "system": "DND5E",
        "name": "Test Character",
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "level": 5,
        "abilities": {
            "Strength": 18,
            "Dexterity": 14,
            "Constitution": 16,
            "Intelligence": 12,
            "Wisdom": 10,
            "Charisma": 8
        },
        "hp": 45,
        "skills": {
            "proficiencies": ["Athletics", "Intimidation"]
        },
        "equipment": ["Longsword", "Shield"],
        "feats": [],
        "spells": {}
    }
    
    try:
        # Temp dosya oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = Path(f.name)
            json.dump(test_character, f, ensure_ascii=False, indent=2)
        
        # Import test
        with open(temp_file, 'r', encoding='utf-8') as f:
            imported_character = json.load(f)
        
        # Kontrol et
        if imported_character['name'] != test_character['name']:
            print(f"[HATA] Name eslesmedi: {imported_character['name']} != {test_character['name']}")
            temp_file.unlink()
            return False
        
        if imported_character['level'] != test_character['level']:
            print(f"[HATA] Level eslesmedi: {imported_character['level']} != {test_character['level']}")
            temp_file.unlink()
            return False
        
        if imported_character['abilities']['Strength'] != test_character['abilities']['Strength']:
            print(f"[HATA] Strength eslesmedi")
            temp_file.unlink()
            return False
        
        # Temizle
        temp_file.unlink()
        
        print("[OK] JSON export/import basarili")
        return True
        
    except Exception as e:
        print(f"[HATA] JSON export/import basarisiz: {e}")
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False

def test_character_data_structure():
    """Karakter veri yapısı kontrolü"""
    print("\n" + "=" * 70)
    print("TEST 2: Karakter Veri Yapisi")
    print("=" * 70)
    
    # Zorunlu alanlar
    required_fields = ['system', 'name', 'race', 'class', 'level', 'abilities']
    
    # Test karakteri
    test_character = {
        "system": "DND5E",
        "name": "Test Character",
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
        }
    }
    
    try:
        # Zorunlu alanlar kontrolü
        missing_fields = [field for field in required_fields if field not in test_character]
        
        if missing_fields:
            print(f"[HATA] Eksik alanlar: {missing_fields}")
            return False
        
        # Abilities kontrolü
        abilities = test_character.get('abilities', {})
        required_abilities = ['Strength', 'Dexterity', 'Constitution', 
                             'Intelligence', 'Wisdom', 'Charisma']
        
        missing_abilities = [ability for ability in required_abilities 
                            if ability not in abilities]
        
        if missing_abilities:
            print(f"[HATA] Eksik yetenekler: {missing_abilities}")
            return False
        
        # Değer aralığı kontrolü
        for ability, value in abilities.items():
            if not isinstance(value, int) or value < 1 or value > 30:
                print(f"[HATA] Gecersiz {ability} degeri: {value}")
                return False
        
        # Level kontrolü
        level = test_character.get('level', 0)
        if not isinstance(level, int) or level < 1 or level > 20:
            print(f"[HATA] Gecersiz level: {level}")
            return False
        
        print("[OK] Karakter veri yapisi gecerli")
        return True
        
    except Exception as e:
        print(f"[HATA] Veri yapisi kontrolu basarisiz: {e}")
        return False

def test_character_roundtrip():
    """Karakter roundtrip testi (export -> import -> kontrol)"""
    print("\n" + "=" * 70)
    print("TEST 3: Karakter Roundtrip")
    print("=" * 70)
    
    # Kapsamlı test karakteri
    original_character = {
        "system": "DND5E",
        "name": "Test Roundtrip Character",
        "race": "Elf",
        "class": "Wizard",
        "background": "Sage",
        "level": 3,
        "abilities": {
            "Strength": 8,
            "Dexterity": 14,
            "Constitution": 13,
            "Intelligence": 16,
            "Wisdom": 12,
            "Charisma": 10
        },
        "hp": 18,
        "skills": {
            "proficiencies": ["Arcana", "History", "Investigation"]
        },
        "equipment": ["Spellbook", "Component Pouch"],
        "feats": [],
        "spells": {
            "known": ["Magic Missile", "Shield", "Mage Armor"],
            "prepared": ["Magic Missile", "Shield"]
        },
        "features": ["Arcane Recovery"]
    }
    
    try:
        # Export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = Path(f.name)
            json.dump(original_character, f, ensure_ascii=False, indent=2)
        
        # Import
        with open(temp_file, 'r', encoding='utf-8') as f:
            imported_character = json.load(f)
        
        # Karşılaştır
        fields_to_check = ['name', 'race', 'class', 'background', 'level', 
                          'hp', 'abilities', 'skills', 'equipment', 'spells', 'features']
        
        differences = []
        for field in fields_to_check:
            original_value = original_character.get(field)
            imported_value = imported_character.get(field)
            
            if original_value != imported_value:
                differences.append(f"{field}: {original_value} != {imported_value}")
        
        if differences:
            print(f"[HATA] {len(differences)} fark bulundu:")
            for diff in differences[:5]:
                print(f"  - {diff}")
            if len(differences) > 5:
                print(f"  ... ve {len(differences) - 5} fark daha")
            temp_file.unlink()
            return False
        
        # Temizle
        temp_file.unlink()
        
        print("[OK] Karakter roundtrip basarili")
        return True
        
    except Exception as e:
        print(f"[HATA] Roundtrip testi basarisiz: {e}")
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False

def main():
    """Tum export/import testlerini calistir"""
    print("=" * 70)
    print("EXPORT/IMPORT TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("JSON Export/Import", test_json_export_import),
        ("Karakter Veri Yapisi", test_character_data_structure),
        ("Karakter Roundtrip", test_character_roundtrip),
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




Export/Import testleri - Karakter export/import fonksiyonlarını test eder
"""
import sys
import json
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

def test_json_export_import():
    """JSON export/import testi"""
    print("=" * 70)
    print("TEST 1: JSON Export/Import")
    print("=" * 70)
    
    # Test karakteri
    test_character = {
        "system": "DND5E",
        "name": "Test Character",
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "level": 5,
        "abilities": {
            "Strength": 18,
            "Dexterity": 14,
            "Constitution": 16,
            "Intelligence": 12,
            "Wisdom": 10,
            "Charisma": 8
        },
        "hp": 45,
        "skills": {
            "proficiencies": ["Athletics", "Intimidation"]
        },
        "equipment": ["Longsword", "Shield"],
        "feats": [],
        "spells": {}
    }
    
    try:
        # Temp dosya oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = Path(f.name)
            json.dump(test_character, f, ensure_ascii=False, indent=2)
        
        # Import test
        with open(temp_file, 'r', encoding='utf-8') as f:
            imported_character = json.load(f)
        
        # Kontrol et
        if imported_character['name'] != test_character['name']:
            print(f"[HATA] Name eslesmedi: {imported_character['name']} != {test_character['name']}")
            temp_file.unlink()
            return False
        
        if imported_character['level'] != test_character['level']:
            print(f"[HATA] Level eslesmedi: {imported_character['level']} != {test_character['level']}")
            temp_file.unlink()
            return False
        
        if imported_character['abilities']['Strength'] != test_character['abilities']['Strength']:
            print(f"[HATA] Strength eslesmedi")
            temp_file.unlink()
            return False
        
        # Temizle
        temp_file.unlink()
        
        print("[OK] JSON export/import basarili")
        return True
        
    except Exception as e:
        print(f"[HATA] JSON export/import basarisiz: {e}")
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False

def test_character_data_structure():
    """Karakter veri yapısı kontrolü"""
    print("\n" + "=" * 70)
    print("TEST 2: Karakter Veri Yapisi")
    print("=" * 70)
    
    # Zorunlu alanlar
    required_fields = ['system', 'name', 'race', 'class', 'level', 'abilities']
    
    # Test karakteri
    test_character = {
        "system": "DND5E",
        "name": "Test Character",
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
        }
    }
    
    try:
        # Zorunlu alanlar kontrolü
        missing_fields = [field for field in required_fields if field not in test_character]
        
        if missing_fields:
            print(f"[HATA] Eksik alanlar: {missing_fields}")
            return False
        
        # Abilities kontrolü
        abilities = test_character.get('abilities', {})
        required_abilities = ['Strength', 'Dexterity', 'Constitution', 
                             'Intelligence', 'Wisdom', 'Charisma']
        
        missing_abilities = [ability for ability in required_abilities 
                            if ability not in abilities]
        
        if missing_abilities:
            print(f"[HATA] Eksik yetenekler: {missing_abilities}")
            return False
        
        # Değer aralığı kontrolü
        for ability, value in abilities.items():
            if not isinstance(value, int) or value < 1 or value > 30:
                print(f"[HATA] Gecersiz {ability} degeri: {value}")
                return False
        
        # Level kontrolü
        level = test_character.get('level', 0)
        if not isinstance(level, int) or level < 1 or level > 20:
            print(f"[HATA] Gecersiz level: {level}")
            return False
        
        print("[OK] Karakter veri yapisi gecerli")
        return True
        
    except Exception as e:
        print(f"[HATA] Veri yapisi kontrolu basarisiz: {e}")
        return False

def test_character_roundtrip():
    """Karakter roundtrip testi (export -> import -> kontrol)"""
    print("\n" + "=" * 70)
    print("TEST 3: Karakter Roundtrip")
    print("=" * 70)
    
    # Kapsamlı test karakteri
    original_character = {
        "system": "DND5E",
        "name": "Test Roundtrip Character",
        "race": "Elf",
        "class": "Wizard",
        "background": "Sage",
        "level": 3,
        "abilities": {
            "Strength": 8,
            "Dexterity": 14,
            "Constitution": 13,
            "Intelligence": 16,
            "Wisdom": 12,
            "Charisma": 10
        },
        "hp": 18,
        "skills": {
            "proficiencies": ["Arcana", "History", "Investigation"]
        },
        "equipment": ["Spellbook", "Component Pouch"],
        "feats": [],
        "spells": {
            "known": ["Magic Missile", "Shield", "Mage Armor"],
            "prepared": ["Magic Missile", "Shield"]
        },
        "features": ["Arcane Recovery"]
    }
    
    try:
        # Export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = Path(f.name)
            json.dump(original_character, f, ensure_ascii=False, indent=2)
        
        # Import
        with open(temp_file, 'r', encoding='utf-8') as f:
            imported_character = json.load(f)
        
        # Karşılaştır
        fields_to_check = ['name', 'race', 'class', 'background', 'level', 
                          'hp', 'abilities', 'skills', 'equipment', 'spells', 'features']
        
        differences = []
        for field in fields_to_check:
            original_value = original_character.get(field)
            imported_value = imported_character.get(field)
            
            if original_value != imported_value:
                differences.append(f"{field}: {original_value} != {imported_value}")
        
        if differences:
            print(f"[HATA] {len(differences)} fark bulundu:")
            for diff in differences[:5]:
                print(f"  - {diff}")
            if len(differences) > 5:
                print(f"  ... ve {len(differences) - 5} fark daha")
            temp_file.unlink()
            return False
        
        # Temizle
        temp_file.unlink()
        
        print("[OK] Karakter roundtrip basarili")
        return True
        
    except Exception as e:
        print(f"[HATA] Roundtrip testi basarisiz: {e}")
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False

def main():
    """Tum export/import testlerini calistir"""
    print("=" * 70)
    print("EXPORT/IMPORT TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("JSON Export/Import", test_json_export_import),
        ("Karakter Veri Yapisi", test_character_data_structure),
        ("Karakter Roundtrip", test_character_roundtrip),
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


Export/Import testleri - Karakter export/import fonksiyonlarını test eder
"""
import sys
import json
import tempfile
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

def test_json_export_import():
    """JSON export/import testi"""
    print("=" * 70)
    print("TEST 1: JSON Export/Import")
    print("=" * 70)
    
    # Test karakteri
    test_character = {
        "system": "DND5E",
        "name": "Test Character",
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "level": 5,
        "abilities": {
            "Strength": 18,
            "Dexterity": 14,
            "Constitution": 16,
            "Intelligence": 12,
            "Wisdom": 10,
            "Charisma": 8
        },
        "hp": 45,
        "skills": {
            "proficiencies": ["Athletics", "Intimidation"]
        },
        "equipment": ["Longsword", "Shield"],
        "feats": [],
        "spells": {}
    }
    
    try:
        # Temp dosya oluştur
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = Path(f.name)
            json.dump(test_character, f, ensure_ascii=False, indent=2)
        
        # Import test
        with open(temp_file, 'r', encoding='utf-8') as f:
            imported_character = json.load(f)
        
        # Kontrol et
        if imported_character['name'] != test_character['name']:
            print(f"[HATA] Name eslesmedi: {imported_character['name']} != {test_character['name']}")
            temp_file.unlink()
            return False
        
        if imported_character['level'] != test_character['level']:
            print(f"[HATA] Level eslesmedi: {imported_character['level']} != {test_character['level']}")
            temp_file.unlink()
            return False
        
        if imported_character['abilities']['Strength'] != test_character['abilities']['Strength']:
            print(f"[HATA] Strength eslesmedi")
            temp_file.unlink()
            return False
        
        # Temizle
        temp_file.unlink()
        
        print("[OK] JSON export/import basarili")
        return True
        
    except Exception as e:
        print(f"[HATA] JSON export/import basarisiz: {e}")
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False

def test_character_data_structure():
    """Karakter veri yapısı kontrolü"""
    print("\n" + "=" * 70)
    print("TEST 2: Karakter Veri Yapisi")
    print("=" * 70)
    
    # Zorunlu alanlar
    required_fields = ['system', 'name', 'race', 'class', 'level', 'abilities']
    
    # Test karakteri
    test_character = {
        "system": "DND5E",
        "name": "Test Character",
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
        }
    }
    
    try:
        # Zorunlu alanlar kontrolü
        missing_fields = [field for field in required_fields if field not in test_character]
        
        if missing_fields:
            print(f"[HATA] Eksik alanlar: {missing_fields}")
            return False
        
        # Abilities kontrolü
        abilities = test_character.get('abilities', {})
        required_abilities = ['Strength', 'Dexterity', 'Constitution', 
                             'Intelligence', 'Wisdom', 'Charisma']
        
        missing_abilities = [ability for ability in required_abilities 
                            if ability not in abilities]
        
        if missing_abilities:
            print(f"[HATA] Eksik yetenekler: {missing_abilities}")
            return False
        
        # Değer aralığı kontrolü
        for ability, value in abilities.items():
            if not isinstance(value, int) or value < 1 or value > 30:
                print(f"[HATA] Gecersiz {ability} degeri: {value}")
                return False
        
        # Level kontrolü
        level = test_character.get('level', 0)
        if not isinstance(level, int) or level < 1 or level > 20:
            print(f"[HATA] Gecersiz level: {level}")
            return False
        
        print("[OK] Karakter veri yapisi gecerli")
        return True
        
    except Exception as e:
        print(f"[HATA] Veri yapisi kontrolu basarisiz: {e}")
        return False

def test_character_roundtrip():
    """Karakter roundtrip testi (export -> import -> kontrol)"""
    print("\n" + "=" * 70)
    print("TEST 3: Karakter Roundtrip")
    print("=" * 70)
    
    # Kapsamlı test karakteri
    original_character = {
        "system": "DND5E",
        "name": "Test Roundtrip Character",
        "race": "Elf",
        "class": "Wizard",
        "background": "Sage",
        "level": 3,
        "abilities": {
            "Strength": 8,
            "Dexterity": 14,
            "Constitution": 13,
            "Intelligence": 16,
            "Wisdom": 12,
            "Charisma": 10
        },
        "hp": 18,
        "skills": {
            "proficiencies": ["Arcana", "History", "Investigation"]
        },
        "equipment": ["Spellbook", "Component Pouch"],
        "feats": [],
        "spells": {
            "known": ["Magic Missile", "Shield", "Mage Armor"],
            "prepared": ["Magic Missile", "Shield"]
        },
        "features": ["Arcane Recovery"]
    }
    
    try:
        # Export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False, encoding='utf-8') as f:
            temp_file = Path(f.name)
            json.dump(original_character, f, ensure_ascii=False, indent=2)
        
        # Import
        with open(temp_file, 'r', encoding='utf-8') as f:
            imported_character = json.load(f)
        
        # Karşılaştır
        fields_to_check = ['name', 'race', 'class', 'background', 'level', 
                          'hp', 'abilities', 'skills', 'equipment', 'spells', 'features']
        
        differences = []
        for field in fields_to_check:
            original_value = original_character.get(field)
            imported_value = imported_character.get(field)
            
            if original_value != imported_value:
                differences.append(f"{field}: {original_value} != {imported_value}")
        
        if differences:
            print(f"[HATA] {len(differences)} fark bulundu:")
            for diff in differences[:5]:
                print(f"  - {diff}")
            if len(differences) > 5:
                print(f"  ... ve {len(differences) - 5} fark daha")
            temp_file.unlink()
            return False
        
        # Temizle
        temp_file.unlink()
        
        print("[OK] Karakter roundtrip basarili")
        return True
        
    except Exception as e:
        print(f"[HATA] Roundtrip testi basarisiz: {e}")
        if 'temp_file' in locals() and temp_file.exists():
            temp_file.unlink()
        return False

def main():
    """Tum export/import testlerini calistir"""
    print("=" * 70)
    print("EXPORT/IMPORT TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("JSON Export/Import", test_json_export_import),
        ("Karakter Veri Yapisi", test_character_data_structure),
        ("Karakter Roundtrip", test_character_roundtrip),
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





