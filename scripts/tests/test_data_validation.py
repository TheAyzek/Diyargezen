"""
Veri doğrulama testleri - D&D 5e verilerinin kalitesini kontrol eder
"""
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent  # scripts/tests -> scripts -> project_root
sys.path.insert(0, str(project_root))

from utils.data_loader import load_dnd_data

def test_data_integrity():
    """Veri bütünlüğü testi"""
    print("=" * 70)
    print("TEST 1: Veri Butunlugu")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        
        # Zorunlu alanlar
        required_keys = ['races', 'classes', 'feats', 'backgrounds', 'spells']
        missing_keys = [key for key in required_keys if key not in dnd_data]
        
        if missing_keys:
            print(f"[HATA] Eksik anahtarlar: {missing_keys}")
            return False
        
        print("[OK] Tum zorunlu anahtarlar mevcut")
        
        # Veri sayıları
        races_count = len(dnd_data.get('races', {}))
        classes_count = len(dnd_data.get('classes', {}))
        feats_count = len(dnd_data.get('feats', {}))
        backgrounds_count = len(dnd_data.get('backgrounds', {}))
        spells_count = len(dnd_data.get('spells', {}))
        
        print(f"[OK] Races: {races_count}")
        print(f"[OK] Classes: {classes_count}")
        print(f"[OK] Feats: {feats_count}")
        print(f"[OK] Backgrounds: {backgrounds_count}")
        print(f"[OK] Spells: {spells_count}")
        
        # Minimum değerler kontrolü
        if races_count < 9:  # En az 9 core race olmalı
            print(f"[UYARI] Races sayisi dusuk: {races_count}")
        
        if classes_count < 12:  # En az 12 core class olmalı
            print(f"[UYARI] Classes sayisi dusuk: {classes_count}")
        
        if feats_count < 100:
            print(f"[UYARI] Feats sayisi dusuk: {feats_count}")
        
        if backgrounds_count < 10:
            print(f"[UYARI] Backgrounds sayisi dusuk: {backgrounds_count}")
        
        if spells_count < 300:
            print(f"[UYARI] Spells sayisi dusuk: {spells_count}")
        
        return True
        
    except Exception as e:
        print(f"[HATA] Veri yuklenemedi: {e}")
        return False

def test_class_data_quality():
    """Class verilerinin kalitesini kontrol et"""
    print("\n" + "=" * 70)
    print("TEST 2: Class Veri Kalitesi")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        classes = dnd_data.get('classes', {})
        
        if not classes:
            print("[HATA] Classes verisi yok")
            return False
        
        required_fields = ['name', 'hit_dice', 'proficiencies']
        issues = []
        
        for class_name, class_data in classes.items():
            if not isinstance(class_data, dict):
                issues.append(f"{class_name}: Dict degil")
                continue
            
            # Zorunlu alanlar kontrolü
            for field in required_fields:
                if field not in class_data:
                    issues.append(f"{class_name}: {field} eksik")
            
            # Hit dice format kontrolü
            hit_dice = class_data.get('hit_dice', '')
            if hit_dice and not (isinstance(hit_dice, (int, str))):
                issues.append(f"{class_name}: hit_dice format hatasi")
            
            # Proficiencies kontrolü
            proficiencies = class_data.get('proficiencies', {})
            if not isinstance(proficiencies, dict):
                issues.append(f"{class_name}: proficiencies dict degil")
        
        if issues:
            print(f"[UYARI] {len(issues)} sorun bulundu:")
            for issue in issues[:10]:  # İlk 10 sorunu göster
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... ve {len(issues) - 10} sorun daha")
            return len(issues) < 50  # 50'den az sorun kabul edilebilir
        
        print(f"[OK] Tum {len(classes)} class verisi gecerli")
        return True
        
    except Exception as e:
        print(f"[HATA] Class veri kontrolu basarisiz: {e}")
        return False

def test_race_data_quality():
    """Race verilerinin kalitesini kontrol et"""
    print("\n" + "=" * 70)
    print("TEST 3: Race Veri Kalitesi")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        races = dnd_data.get('races', {})
        
        if not races:
            print("[HATA] Races verisi yok")
            return False
        
        required_fields = ['name']
        issues = []
        
        core_races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Dragonborn', 
                     'Gnome', 'Half-Elf', 'Half-Orc', 'Tiefling']
        
        missing_core_races = [race for race in core_races if race not in races]
        
        if missing_core_races:
            print(f"[UYARI] Eksik core races: {missing_core_races}")
        
        for race_name, race_data in races.items():
            if not isinstance(race_data, dict):
                issues.append(f"{race_name}: Dict degil")
                continue
            
            # Name kontrolü
            if 'name' not in race_data:
                issues.append(f"{race_name}: name eksik")
            
            # Ability score increase kontrolü
            asi = race_data.get('ability_score_increase', {})
            if asi and not isinstance(asi, dict):
                issues.append(f"{race_name}: ability_score_increase dict degil")
        
        if issues:
            print(f"[UYARI] {len(issues)} sorun bulundu:")
            for issue in issues[:10]:
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... ve {len(issues) - 10} sorun daha")
            return len(issues) < 20
        
        print(f"[OK] Tum {len(races)} race verisi gecerli")
        return True
        
    except Exception as e:
        print(f"[HATA] Race veri kontrolu basarisiz: {e}")
        return False

def test_spell_data_quality():
    """Spell verilerinin kalitesini kontrol et"""
    print("\n" + "=" * 70)
    print("TEST 4: Spell Veri Kalitesi")
    print("=" * 70)
    
    try:
        dnd_data = load_dnd_data(project_root)
        spells = dnd_data.get('spells', {})
        
        if not spells:
            print("[UYARI] Spells verisi yok")
            return False
        
        required_fields = ['name', 'level']
        issues = []
        valid_spells = 0
        
        for spell_name, spell_data in spells.items():
            if not isinstance(spell_data, dict):
                issues.append(f"{spell_name}: Dict degil")
                continue
            
            # Zorunlu alanlar
            for field in required_fields:
                if field not in spell_data:
                    issues.append(f"{spell_name}: {field} eksik")
                    break
            else:
                valid_spells += 1
            
            # Level kontrolü
            level = spell_data.get('level', -1)
            if not isinstance(level, int) or level < 0 or level > 9:
                if level != -1:  # -1 eksik veri demek
                    issues.append(f"{spell_name}: Gecersiz level: {level}")
        
        print(f"[OK] {valid_spells}/{len(spells)} spell gecerli")
        
        if issues:
            print(f"[UYARI] {len(issues)} sorun bulundu:")
            for issue in issues[:10]:
                print(f"  - {issue}")
            if len(issues) > 10:
                print(f"  ... ve {len(issues) - 10} sorun daha")
            return len(issues) < valid_spells * 0.1  # %10'dan az hata kabul edilebilir
        
        return True
        
    except Exception as e:
        print(f"[HATA] Spell veri kontrolu basarisiz: {e}")
        return False

def main():
    """Tum veri doğrulama testlerini calistir"""
    print("=" * 70)
    print("VERI DOGRULAMA TESTLERI")
    print("=" * 70)
    print()
    
    tests = [
        ("Veri Butunlugu", test_data_integrity),
        ("Class Veri Kalitesi", test_class_data_quality),
        ("Race Veri Kalitesi", test_race_data_quality),
        ("Spell Veri Kalitesi", test_spell_data_quality),
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






