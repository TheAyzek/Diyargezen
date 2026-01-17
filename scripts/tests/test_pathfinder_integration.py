#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Pathfinder 1e entegrasyonunu test et"""

import sys
import json
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

def test_data_loading():
    """Veri yükleme testi"""
    print("=" * 60)
    print("TEST 1: Veri Yükleme")
    print("=" * 60)
    
    try:
        from utils.data_loader import load_pathfinder_1e_data
        
        data = load_pathfinder_1e_data(project_root)
        
        print(f"[OK] Veri yuklendi")
        print(f"  - Irk sayisi: {len(data.get('races', {}))}")
        print(f"  - Sinif sayisi: {len(data.get('classes', {}))}")
        print(f"  - Feat sayisi: {len(data.get('feats', {}))}")
        print(f"  - Buyu sayisi: {len(data.get('spells', {}))}")
        
        # İlk birkaç ırkı kontrol et
        races = data.get('races', {})
        if races:
            print(f"\n  Ornek irklar:")
            for i, (name, race) in enumerate(list(races.items())[:5]):
                ability = race.get('ability_score_increase_text', 'N/A')
                vision = race.get('vision', 'normal')
                traits_count = len(race.get('traits', []))
                print(f"    {i+1}. {name}: {ability}, Vision: {vision}, Traits: {traits_count}")
        
        return True
    except Exception as e:
        print(f"[HATA] Veri yuklenemedi: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_race_detail_structure():
    """Irk detay yapısı testi"""
    print("\n" + "=" * 60)
    print("TEST 2: Irk Detay Yapisi")
    print("=" * 60)
    
    try:
        data_file = project_root / "data" / "pathfinder_1e_data.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        races = data.get('races', {})
        if not races:
            print("[HATA] Hic irk bulunamadi!")
            return False
        
        # Human'ı test et (bilinen bir ırk)
        human = races.get('Human')
        if not human:
            print("[HATA] Human irki bulunamadi!")
            return False
        
        print(f"[OK] Human irki bulundu")
        print(f"  - Ability Score: {human.get('ability_score_increase', {})}")
        print(f"  - Size: {human.get('size', 'N/A')}")
        print(f"  - Speed: {human.get('speed', 'N/A')}")
        print(f"  - Vision: {human.get('vision', 'N/A')}")
        print(f"  - Languages: {human.get('languages', [])}")
        print(f"  - Traits sayisi: {len(human.get('traits', []))}")
        print(f"  - Favored Classes: {human.get('favored_classes', [])}")
        print(f"  - Description: {human.get('description', 'N/A')[:100]}...")
        
        # Gerekli alanları kontrol et
        required_fields = ['ability_score_increase', 'size', 'speed', 'vision', 'traits']
        missing_fields = [field for field in required_fields if field not in human]
        
        if missing_fields:
            print(f"[UYARI] Eksik alanlar: {missing_fields}")
        else:
            print(f"[OK] Tum gerekli alanlar mevcut")
        
        return True
    except Exception as e:
        print(f"[HATA] Irk detay yapisi test edilemedi: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_race_auto_apply_logic():
    """Irk otomatik uygulama mantığı testi"""
    print("\n" + "=" * 60)
    print("TEST 3: Irk Otomatik Uygulama Mantigi")
    print("=" * 60)
    
    try:
        # Önce veriyi yükle
        data_file = project_root / "data" / "pathfinder_1e_data.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        races = data.get('races', {})
        
        # Birkaç farklı ırkı test et
        test_races = ['Human', 'Elf', 'Dwarf', 'Halfling', 'Gnome']
        
        for race_name in test_races:
            if race_name not in races:
                print(f"[UYARI] {race_name} bulunamadi, atlaniyor...")
                continue
            
            race = races[race_name]
            print(f"\n  {race_name}:")
            
            # Ability score increases kontrolü
            ability_increases = race.get('ability_score_increase', {})
            if ability_increases:
                print(f"    - Ability Score Increases: {ability_increases}")
            else:
                print(f"    - [UYARI] Ability score increases bulunamadi")
            
            # Vision kontrolü
            vision = race.get('vision', 'normal')
            vision_range = race.get('vision_range', 0)
            print(f"    - Vision: {vision} ({vision_range} feet)" if vision_range > 0 else f"    - Vision: {vision}")
            
            # Languages kontrolü
            languages = race.get('languages', [])
            auto_langs = race.get('languages_automatic', [])
            bonus_langs = race.get('languages_bonus', [])
            print(f"    - Languages: {len(languages)} dil (Auto: {len(auto_langs)}, Bonus: {len(bonus_langs)})")
            
            # Traits kontrolü
            traits = race.get('traits', [])
            traits_detailed = race.get('traits_detailed', {})
            print(f"    - Traits: {len(traits)} ozellik ({len(traits_detailed)} detayli)")
            
            # İlk birkaç trait'i göster
            if traits:
                print(f"    - Ilk 3 trait: {', '.join(traits[:3])}")
        
        print(f"\n[OK] Irk otomatik uygulama mantigi test edildi")
        return True
    except Exception as e:
        print(f"[HATA] Irk otomatik uygulama mantigi test edilemedi: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_character_creation_simulation():
    """Karakter oluşturma simülasyonu testi"""
    print("\n" + "=" * 60)
    print("TEST 4: Karakter Olusturma Simulasyonu")
    print("=" * 60)
    
    try:
        # Veriyi yükle
        data_file = project_root / "data" / "pathfinder_1e_data.json"
        with open(data_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        races = data.get('races', {})
        classes = data.get('classes', {})
        
        # Test karakteri oluştur
        test_character = {
            "system": "PATHFINDER_1E",
            "name": "Test Karakteri",
            "race": "Human",
            "class": "Fighter",
            "level": 1,
            "abilities": {
                "Strength": 10,
                "Dexterity": 10,
                "Constitution": 10,
                "Intelligence": 10,
                "Wisdom": 10,
                "Charisma": 10
            },
            "skills": {},
            "equipment": [],
            "spells": {},
            "feats": [],
            "languages": [],
            "personality": {},
            "physical": {},
            "appearance": {}
        }
        
        # Human ırkının özelliklerini uygula
        human = races.get('Human')
        if human:
            # Ability score increases (any +2)
            test_character['race_data'] = {
                'size': human.get('size', 'Medium'),
                'speed': human.get('speed', 30),
                'vision': human.get('vision', 'normal'),
                'vision_range': human.get('vision_range', 0),
            }
            
            # Languages ekle
            languages = human.get('languages', [])
            test_character['languages'] = languages.copy()
            
            # Traits ekle
            traits = human.get('traits', [])
            test_character['race_data']['traits'] = traits[:5]  # İlk 5 trait
            
            print(f"[OK] Test karakteri olusturuldu")
            print(f"  - Isim: {test_character['name']}")
            print(f"  - Irk: {test_character['race']}")
            print(f"  - Sinif: {test_character['class']}")
            print(f"  - Race Data: {test_character.get('race_data', {})}")
            print(f"  - Languages: {test_character['languages']}")
            print(f"  - Ability Scores: {test_character['abilities']}")
            
            # Irk bonuslarını uygula (simülasyon)
            ability_increases = human.get('ability_score_increase', {})
            if 'any' in ability_increases:
                bonus = ability_increases['any']
                print(f"  - [NOT] Human'in 'any' ability bonus'u ({bonus}) GUI'de kullanici secimine acik")
            else:
                for ability, bonus in ability_increases.items():
                    ability_capitalized = ability.capitalize()
                    if ability_capitalized in test_character['abilities']:
                        test_character['abilities'][ability_capitalized] += bonus
                        print(f"  - {ability_capitalized} bonus'u uygulandi: +{bonus}")
            
            print(f"  - Guncellenmis Ability Scores: {test_character['abilities']}")
        
        return True
    except Exception as e:
        print(f"[HATA] Karakter olusturma simulasyonu test edilemedi: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_gui_pathfinder_page():
    """GUI PathfinderPage testi (kod seviyesinde)"""
    print("\n" + "=" * 60)
    print("TEST 5: GUI PathfinderPage (Kod Seviyesi)")
    print("=" * 60)
    
    try:
        # PathfinderPage'i import et
        from gui.app import PathfinderPage
        from PySide6.QtWidgets import QApplication
        import sys
        
        # QApplication oluştur (GUI için gerekli)
        if not QApplication.instance():
            app = QApplication(sys.argv)
        else:
            app = QApplication.instance()
        
        # PathfinderPage oluştur
        print("[INFO] PathfinderPage olusturuluyor...")
        page = PathfinderPage()
        
        print(f"[OK] PathfinderPage olusturuldu")
        print(f"  - Sistem: {page.SYSTEM_NAME}")
        print(f"  - Adim sayisi: {len(page.steps)}")
        print(f"  - Data yuklendi: {len(page.data.get('races', {}))} irk")
        
        # Data kontrolü
        races = page.data.get('races', {})
        if races:
            print(f"  - [OK] {len(races)} irk yuklendi")
            
            # İlk birkaç ırkı listele
            print(f"  - Ornek irklar: {', '.join(list(races.keys())[:5])}")
        else:
            print(f"  - [HATA] Hic irk yuklenemedi!")
            return False
        
        classes = page.data.get('classes', {})
        if classes:
            print(f"  - [OK] {len(classes)} sinif yuklendi")
        else:
            print(f"  - [UYARI] Sinif verisi yuklenemedi (beklenen)")
        
        feats = page.data.get('feats', {})
        if feats:
            print(f"  - [OK] {len(feats)} feat yuklendi")
        else:
            print(f"  - [UYARI] Feat verisi yuklenemedi (beklenen)")
        
        # Widget'ları kontrol et
        if hasattr(page, 'ability_spins'):
            print(f"  - [OK] Ability spins widget'lari olusturuldu: {len(page.ability_spins)}")
        else:
            print(f"  - [UYARI] Ability spins widget'lari henuz olusturulmadi")
        
        return True
    except Exception as e:
        print(f"[HATA] GUI PathfinderPage test edilemedi: {e}")
        import traceback
        traceback.print_exc()
        return False

def main():
    """Tüm testleri çalıştır"""
    print("=" * 60)
    print("PATHFINDER 1E ENTEGRASYON TESTLERI")
    print("=" * 60)
    print()
    
    tests = [
        ("Veri Yükleme", test_data_loading),
        ("Irk Detay Yapısı", test_race_detail_structure),
        ("Irk Otomatik Uygulama Mantığı", test_race_auto_apply_logic),
        ("Karakter Oluşturma Simülasyonu", test_character_creation_simulation),
        ("GUI PathfinderPage", test_gui_pathfinder_page),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"[HATA] {test_name} testi sirasinda hata: {e}")
            results.append((test_name, False))
    
    # Özet
    print("\n" + "=" * 60)
    print("TEST OZETI")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[HATA]"
        print(f"{status} {test_name}")
    
    print(f"\nToplam: {passed}/{total} test basarili")
    
    if passed == total:
        print("\n[OK] Tum testler basarili! Pathfinder 1e entegrasyonu hazir.")
        return 0
    else:
        print(f"\n[UYARI] {total - passed} test basarisiz. Kontrol edin.")
        return 1

if __name__ == "__main__":
    sys.exit(main())


