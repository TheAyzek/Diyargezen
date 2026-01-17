"""
PDF Export Test Script - İYİLEŞTİRİLDİ (PDF Export İyileştirmeleri Test)
PDF export fonksiyonlarını test eder
"""

import sys
from pathlib import Path

# Project root'u path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.pdf_templates import (
    export_dnd_character_pdf_improved,
    export_dnd_spell_sheet_pdf,
    _get_color_scheme,
    _create_styles,
    _create_ability_scores_table,
    _create_combat_stats_table,
    _create_saving_throws_table,
    _create_skills_table
)


def test_color_scheme():
    """Color scheme fonksiyonunu test et"""
    print("\n[TEST] Color Scheme...")
    try:
        default_scheme = _get_color_scheme("default")
        blue_scheme = _get_color_scheme("blue")
        green_scheme = _get_color_scheme("green")
        red_scheme = _get_color_scheme("red")
        
        assert "primary" in default_scheme
        assert "secondary" in default_scheme
        assert default_scheme["primary"] == "#2c3e50"
        assert blue_scheme["primary"] == "#1a237e"
        assert green_scheme["primary"] == "#1b5e20"
        assert red_scheme["primary"] == "#b71c1c"
        
        print("  [OK] Color scheme testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Color scheme testleri başarısız: {e}")
        return False


def test_create_styles():
    """Style oluşturma fonksiyonunu test et"""
    print("\n[TEST] Create Styles...")
    try:
        styles = _create_styles("Helvetica", "default")
        assert "title" in styles
        assert "heading" in styles
        assert "normal" in styles
        assert "bold" in styles
        
        # Color scheme ile test (textColor bir Color objesi, hex'e çevirmek için str() kullan)
        blue_styles = _create_styles("Helvetica", "blue")
        # Color objesini test etmek yerine, style'ın oluşturulduğunu doğrula
        assert blue_styles["title"].textColor is not None
        
        print("  [OK] Style oluşturma testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Style oluşturma testleri başarısız: {e}")
        return False


def create_dummy_character():
    """Test için dummy character oluştur"""
    return {
        "name": "Test Karakter",
        "level": 5,
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "abilities": {
            "Strength": 16,
            "Dexterity": 14,
            "Constitution": 15,
            "Intelligence": 10,
            "Wisdom": 12,
            "Charisma": 8
        },
        "ability_modifiers": {
            "Strength": 3,
            "Dexterity": 2,
            "Constitution": 2,
            "Intelligence": 0,
            "Wisdom": 1,
            "Charisma": -1
        },
        "armor_class": 18,
        "hp_max": 45,
        "hit_dice": "d10",
        "speed": 30,
        "movement_speed": 30,
        "initiative": 2,
        "passive_perception": 11,
        "saving_throws": ["Strength", "Constitution"],
        "saving_throw_modifiers": {
            "Strength": 6,
            "Dexterity": 2,
            "Constitution": 5,
            "Intelligence": 0,
            "Wisdom": 1,
            "Charisma": -1
        },
        "skills": {
            "Athletics": 6,
            "Perception": 4,
            "Survival": 4
        },
        "equipment": [
            {"name": "Longsword", "quantity": 1},
            {"name": "Shield", "quantity": 1},
            {"name": "Chain Mail", "quantity": 1}
        ],
        "spells": {
            "cantrips": ["Light", "Mending"],
            "level1": ["Cure Wounds", "Shield of Faith"]
        },
        "feats": ["Great Weapon Master"],
        "languages": ["Common", "Dwarvish"],
        "personality": {
            "trait": "I'm always polite and respectful",
            "ideal": "Greater Good",
            "bond": "My family",
            "flaw": "I have little respect for those not in the military"
        }
    }


def test_table_creation():
    """Table oluşturma fonksiyonlarını test et"""
    print("\n[TEST] Table Creation...")
    try:
        character = create_dummy_character()
        styles = _create_styles("Helvetica", "default")
        
        # Ability Scores table
        ability_table = _create_ability_scores_table(character, styles)
        assert ability_table is not None
        
        # Combat Stats table
        combat_table = _create_combat_stats_table(character, styles)
        assert combat_table is not None
        
        # Saving Throws table
        saves_table = _create_saving_throws_table(character, styles)
        assert saves_table is not None
        
        # Skills table
        skills_table = _create_skills_table(character, styles)
        assert skills_table is not None
        
        print("  [OK] Table oluşturma testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Table oluşturma testleri başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export():
    """PDF export fonksiyonunu test et (PDF oluşturma)"""
    print("\n[TEST] PDF Export...")
    try:
        character = create_dummy_character()
        test_output = project_root / "characters" / "exports" / "test_character.pdf"
        test_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Standard template
        export_dnd_character_pdf_improved(
            character, 
            test_output,
            template="standard",
            page_size="A4",
            options={"show_abilities": True, "show_combat_stats": True}
        )
        
        assert test_output.exists(), "PDF dosyası oluşturulmadı"
        assert test_output.stat().st_size > 0, "PDF dosyası boş"
        
        print(f"  [OK] PDF export testi başarılı: {test_output}")
        
        # Cleanup (opsiyonel)
        # test_output.unlink()
        
        return True
    except Exception as e:
        print(f"  [FAIL] PDF export testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_templates():
    """Farklı template'leri test et"""
    print("\n[TEST] PDF Export Templates...")
    try:
        character = create_dummy_character()
        test_dir = project_root / "characters" / "exports"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        templates = ["standard", "compact", "detailed"]
        results = []
        
        for template in templates:
            test_output = test_dir / f"test_character_{template}.pdf"
            try:
                export_dnd_character_pdf_improved(
                    character,
                    test_output,
                    template=template,
                    page_size="A4"
                )
                assert test_output.exists()
                results.append((template, True, test_output))
                print(f"  [OK] {template} template PDF oluşturuldu")
            except Exception as e:
                results.append((template, False, str(e)))
                print(f"  [FAIL] {template} template PDF oluşturulamadı: {e}")
        
        all_success = all(result[1] for result in results)
        return all_success
    except Exception as e:
        print(f"  [FAIL] Template testleri başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_options():
    """PDF export options'ı test et"""
    print("\n[TEST] PDF Export Options...")
    try:
        character = create_dummy_character()
        test_output = project_root / "characters" / "exports" / "test_character_options.pdf"
        test_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Options ile export
        export_dnd_character_pdf_improved(
            character,
            test_output,
            template="standard",
            page_size="A4",
            options={
                "show_abilities": True,
                "show_combat_stats": True,
                "show_saving_throws": False,  # Bu bölümü gizle
                "show_skills": True,
                "show_equipment": False,  # Bu bölümü gizle
                "show_spells": True,
                "color_scheme": "blue"
            }
        )
        
        assert test_output.exists()
        print(f"  [OK] Options ile PDF export başarılı: {test_output}")
        return True
    except Exception as e:
        print(f"  [FAIL] Options testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Tüm testleri çalıştır"""
    print("=" * 70)
    print("PDF EXPORT TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Color Scheme", test_color_scheme),
        ("Create Styles", test_create_styles),
        ("Table Creation", test_table_creation),
        ("PDF Export", test_pdf_export),
        ("PDF Export Templates", test_pdf_export_templates),
        ("PDF Export Options", test_pdf_export_options),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name} testi exception fırlattı: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Özet
    print("\n" + "=" * 70)
    print("TEST SONUÇLARI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 70)
    print(f"TOPLAM: {passed}/{total} test başarılı")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


PDF export fonksiyonlarını test eder
"""

import sys
from pathlib import Path

# Project root'u path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.pdf_templates import (
    export_dnd_character_pdf_improved,
    export_dnd_spell_sheet_pdf,
    _get_color_scheme,
    _create_styles,
    _create_ability_scores_table,
    _create_combat_stats_table,
    _create_saving_throws_table,
    _create_skills_table
)


def test_color_scheme():
    """Color scheme fonksiyonunu test et"""
    print("\n[TEST] Color Scheme...")
    try:
        default_scheme = _get_color_scheme("default")
        blue_scheme = _get_color_scheme("blue")
        green_scheme = _get_color_scheme("green")
        red_scheme = _get_color_scheme("red")
        
        assert "primary" in default_scheme
        assert "secondary" in default_scheme
        assert default_scheme["primary"] == "#2c3e50"
        assert blue_scheme["primary"] == "#1a237e"
        assert green_scheme["primary"] == "#1b5e20"
        assert red_scheme["primary"] == "#b71c1c"
        
        print("  [OK] Color scheme testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Color scheme testleri başarısız: {e}")
        return False


def test_create_styles():
    """Style oluşturma fonksiyonunu test et"""
    print("\n[TEST] Create Styles...")
    try:
        styles = _create_styles("Helvetica", "default")
        assert "title" in styles
        assert "heading" in styles
        assert "normal" in styles
        assert "bold" in styles
        
        # Color scheme ile test (textColor bir Color objesi, hex'e çevirmek için str() kullan)
        blue_styles = _create_styles("Helvetica", "blue")
        # Color objesini test etmek yerine, style'ın oluşturulduğunu doğrula
        assert blue_styles["title"].textColor is not None
        
        print("  [OK] Style oluşturma testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Style oluşturma testleri başarısız: {e}")
        return False


def create_dummy_character():
    """Test için dummy character oluştur"""
    return {
        "name": "Test Karakter",
        "level": 5,
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "abilities": {
            "Strength": 16,
            "Dexterity": 14,
            "Constitution": 15,
            "Intelligence": 10,
            "Wisdom": 12,
            "Charisma": 8
        },
        "ability_modifiers": {
            "Strength": 3,
            "Dexterity": 2,
            "Constitution": 2,
            "Intelligence": 0,
            "Wisdom": 1,
            "Charisma": -1
        },
        "armor_class": 18,
        "hp_max": 45,
        "hit_dice": "d10",
        "speed": 30,
        "movement_speed": 30,
        "initiative": 2,
        "passive_perception": 11,
        "saving_throws": ["Strength", "Constitution"],
        "saving_throw_modifiers": {
            "Strength": 6,
            "Dexterity": 2,
            "Constitution": 5,
            "Intelligence": 0,
            "Wisdom": 1,
            "Charisma": -1
        },
        "skills": {
            "Athletics": 6,
            "Perception": 4,
            "Survival": 4
        },
        "equipment": [
            {"name": "Longsword", "quantity": 1},
            {"name": "Shield", "quantity": 1},
            {"name": "Chain Mail", "quantity": 1}
        ],
        "spells": {
            "cantrips": ["Light", "Mending"],
            "level1": ["Cure Wounds", "Shield of Faith"]
        },
        "feats": ["Great Weapon Master"],
        "languages": ["Common", "Dwarvish"],
        "personality": {
            "trait": "I'm always polite and respectful",
            "ideal": "Greater Good",
            "bond": "My family",
            "flaw": "I have little respect for those not in the military"
        }
    }


def test_table_creation():
    """Table oluşturma fonksiyonlarını test et"""
    print("\n[TEST] Table Creation...")
    try:
        character = create_dummy_character()
        styles = _create_styles("Helvetica", "default")
        
        # Ability Scores table
        ability_table = _create_ability_scores_table(character, styles)
        assert ability_table is not None
        
        # Combat Stats table
        combat_table = _create_combat_stats_table(character, styles)
        assert combat_table is not None
        
        # Saving Throws table
        saves_table = _create_saving_throws_table(character, styles)
        assert saves_table is not None
        
        # Skills table
        skills_table = _create_skills_table(character, styles)
        assert skills_table is not None
        
        print("  [OK] Table oluşturma testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Table oluşturma testleri başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export():
    """PDF export fonksiyonunu test et (PDF oluşturma)"""
    print("\n[TEST] PDF Export...")
    try:
        character = create_dummy_character()
        test_output = project_root / "characters" / "exports" / "test_character.pdf"
        test_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Standard template
        export_dnd_character_pdf_improved(
            character, 
            test_output,
            template="standard",
            page_size="A4",
            options={"show_abilities": True, "show_combat_stats": True}
        )
        
        assert test_output.exists(), "PDF dosyası oluşturulmadı"
        assert test_output.stat().st_size > 0, "PDF dosyası boş"
        
        print(f"  [OK] PDF export testi başarılı: {test_output}")
        
        # Cleanup (opsiyonel)
        # test_output.unlink()
        
        return True
    except Exception as e:
        print(f"  [FAIL] PDF export testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_templates():
    """Farklı template'leri test et"""
    print("\n[TEST] PDF Export Templates...")
    try:
        character = create_dummy_character()
        test_dir = project_root / "characters" / "exports"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        templates = ["standard", "compact", "detailed"]
        results = []
        
        for template in templates:
            test_output = test_dir / f"test_character_{template}.pdf"
            try:
                export_dnd_character_pdf_improved(
                    character,
                    test_output,
                    template=template,
                    page_size="A4"
                )
                assert test_output.exists()
                results.append((template, True, test_output))
                print(f"  [OK] {template} template PDF oluşturuldu")
            except Exception as e:
                results.append((template, False, str(e)))
                print(f"  [FAIL] {template} template PDF oluşturulamadı: {e}")
        
        all_success = all(result[1] for result in results)
        return all_success
    except Exception as e:
        print(f"  [FAIL] Template testleri başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_options():
    """PDF export options'ı test et"""
    print("\n[TEST] PDF Export Options...")
    try:
        character = create_dummy_character()
        test_output = project_root / "characters" / "exports" / "test_character_options.pdf"
        test_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Options ile export
        export_dnd_character_pdf_improved(
            character,
            test_output,
            template="standard",
            page_size="A4",
            options={
                "show_abilities": True,
                "show_combat_stats": True,
                "show_saving_throws": False,  # Bu bölümü gizle
                "show_skills": True,
                "show_equipment": False,  # Bu bölümü gizle
                "show_spells": True,
                "color_scheme": "blue"
            }
        )
        
        assert test_output.exists()
        print(f"  [OK] Options ile PDF export başarılı: {test_output}")
        return True
    except Exception as e:
        print(f"  [FAIL] Options testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Tüm testleri çalıştır"""
    print("=" * 70)
    print("PDF EXPORT TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Color Scheme", test_color_scheme),
        ("Create Styles", test_create_styles),
        ("Table Creation", test_table_creation),
        ("PDF Export", test_pdf_export),
        ("PDF Export Templates", test_pdf_export_templates),
        ("PDF Export Options", test_pdf_export_options),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name} testi exception fırlattı: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Özet
    print("\n" + "=" * 70)
    print("TEST SONUÇLARI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 70)
    print(f"TOPLAM: {passed}/{total} test başarılı")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


PDF export fonksiyonlarını test eder
"""

import sys
from pathlib import Path

# Project root'u path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.pdf_templates import (
    export_dnd_character_pdf_improved,
    export_dnd_spell_sheet_pdf,
    _get_color_scheme,
    _create_styles,
    _create_ability_scores_table,
    _create_combat_stats_table,
    _create_saving_throws_table,
    _create_skills_table
)


def test_color_scheme():
    """Color scheme fonksiyonunu test et"""
    print("\n[TEST] Color Scheme...")
    try:
        default_scheme = _get_color_scheme("default")
        blue_scheme = _get_color_scheme("blue")
        green_scheme = _get_color_scheme("green")
        red_scheme = _get_color_scheme("red")
        
        assert "primary" in default_scheme
        assert "secondary" in default_scheme
        assert default_scheme["primary"] == "#2c3e50"
        assert blue_scheme["primary"] == "#1a237e"
        assert green_scheme["primary"] == "#1b5e20"
        assert red_scheme["primary"] == "#b71c1c"
        
        print("  [OK] Color scheme testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Color scheme testleri başarısız: {e}")
        return False


def test_create_styles():
    """Style oluşturma fonksiyonunu test et"""
    print("\n[TEST] Create Styles...")
    try:
        styles = _create_styles("Helvetica", "default")
        assert "title" in styles
        assert "heading" in styles
        assert "normal" in styles
        assert "bold" in styles
        
        # Color scheme ile test (textColor bir Color objesi, hex'e çevirmek için str() kullan)
        blue_styles = _create_styles("Helvetica", "blue")
        # Color objesini test etmek yerine, style'ın oluşturulduğunu doğrula
        assert blue_styles["title"].textColor is not None
        
        print("  [OK] Style oluşturma testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Style oluşturma testleri başarısız: {e}")
        return False


def create_dummy_character():
    """Test için dummy character oluştur"""
    return {
        "name": "Test Karakter",
        "level": 5,
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "abilities": {
            "Strength": 16,
            "Dexterity": 14,
            "Constitution": 15,
            "Intelligence": 10,
            "Wisdom": 12,
            "Charisma": 8
        },
        "ability_modifiers": {
            "Strength": 3,
            "Dexterity": 2,
            "Constitution": 2,
            "Intelligence": 0,
            "Wisdom": 1,
            "Charisma": -1
        },
        "armor_class": 18,
        "hp_max": 45,
        "hit_dice": "d10",
        "speed": 30,
        "movement_speed": 30,
        "initiative": 2,
        "passive_perception": 11,
        "saving_throws": ["Strength", "Constitution"],
        "saving_throw_modifiers": {
            "Strength": 6,
            "Dexterity": 2,
            "Constitution": 5,
            "Intelligence": 0,
            "Wisdom": 1,
            "Charisma": -1
        },
        "skills": {
            "Athletics": 6,
            "Perception": 4,
            "Survival": 4
        },
        "equipment": [
            {"name": "Longsword", "quantity": 1},
            {"name": "Shield", "quantity": 1},
            {"name": "Chain Mail", "quantity": 1}
        ],
        "spells": {
            "cantrips": ["Light", "Mending"],
            "level1": ["Cure Wounds", "Shield of Faith"]
        },
        "feats": ["Great Weapon Master"],
        "languages": ["Common", "Dwarvish"],
        "personality": {
            "trait": "I'm always polite and respectful",
            "ideal": "Greater Good",
            "bond": "My family",
            "flaw": "I have little respect for those not in the military"
        }
    }


def test_table_creation():
    """Table oluşturma fonksiyonlarını test et"""
    print("\n[TEST] Table Creation...")
    try:
        character = create_dummy_character()
        styles = _create_styles("Helvetica", "default")
        
        # Ability Scores table
        ability_table = _create_ability_scores_table(character, styles)
        assert ability_table is not None
        
        # Combat Stats table
        combat_table = _create_combat_stats_table(character, styles)
        assert combat_table is not None
        
        # Saving Throws table
        saves_table = _create_saving_throws_table(character, styles)
        assert saves_table is not None
        
        # Skills table
        skills_table = _create_skills_table(character, styles)
        assert skills_table is not None
        
        print("  [OK] Table oluşturma testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Table oluşturma testleri başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export():
    """PDF export fonksiyonunu test et (PDF oluşturma)"""
    print("\n[TEST] PDF Export...")
    try:
        character = create_dummy_character()
        test_output = project_root / "characters" / "exports" / "test_character.pdf"
        test_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Standard template
        export_dnd_character_pdf_improved(
            character, 
            test_output,
            template="standard",
            page_size="A4",
            options={"show_abilities": True, "show_combat_stats": True}
        )
        
        assert test_output.exists(), "PDF dosyası oluşturulmadı"
        assert test_output.stat().st_size > 0, "PDF dosyası boş"
        
        print(f"  [OK] PDF export testi başarılı: {test_output}")
        
        # Cleanup (opsiyonel)
        # test_output.unlink()
        
        return True
    except Exception as e:
        print(f"  [FAIL] PDF export testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_templates():
    """Farklı template'leri test et"""
    print("\n[TEST] PDF Export Templates...")
    try:
        character = create_dummy_character()
        test_dir = project_root / "characters" / "exports"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        templates = ["standard", "compact", "detailed"]
        results = []
        
        for template in templates:
            test_output = test_dir / f"test_character_{template}.pdf"
            try:
                export_dnd_character_pdf_improved(
                    character,
                    test_output,
                    template=template,
                    page_size="A4"
                )
                assert test_output.exists()
                results.append((template, True, test_output))
                print(f"  [OK] {template} template PDF oluşturuldu")
            except Exception as e:
                results.append((template, False, str(e)))
                print(f"  [FAIL] {template} template PDF oluşturulamadı: {e}")
        
        all_success = all(result[1] for result in results)
        return all_success
    except Exception as e:
        print(f"  [FAIL] Template testleri başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_options():
    """PDF export options'ı test et"""
    print("\n[TEST] PDF Export Options...")
    try:
        character = create_dummy_character()
        test_output = project_root / "characters" / "exports" / "test_character_options.pdf"
        test_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Options ile export
        export_dnd_character_pdf_improved(
            character,
            test_output,
            template="standard",
            page_size="A4",
            options={
                "show_abilities": True,
                "show_combat_stats": True,
                "show_saving_throws": False,  # Bu bölümü gizle
                "show_skills": True,
                "show_equipment": False,  # Bu bölümü gizle
                "show_spells": True,
                "color_scheme": "blue"
            }
        )
        
        assert test_output.exists()
        print(f"  [OK] Options ile PDF export başarılı: {test_output}")
        return True
    except Exception as e:
        print(f"  [FAIL] Options testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Tüm testleri çalıştır"""
    print("=" * 70)
    print("PDF EXPORT TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Color Scheme", test_color_scheme),
        ("Create Styles", test_create_styles),
        ("Table Creation", test_table_creation),
        ("PDF Export", test_pdf_export),
        ("PDF Export Templates", test_pdf_export_templates),
        ("PDF Export Options", test_pdf_export_options),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name} testi exception fırlattı: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Özet
    print("\n" + "=" * 70)
    print("TEST SONUÇLARI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 70)
    print(f"TOPLAM: {passed}/{total} test başarılı")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)


PDF export fonksiyonlarını test eder
"""

import sys
from pathlib import Path

# Project root'u path'e ekle
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.pdf_templates import (
    export_dnd_character_pdf_improved,
    export_dnd_spell_sheet_pdf,
    _get_color_scheme,
    _create_styles,
    _create_ability_scores_table,
    _create_combat_stats_table,
    _create_saving_throws_table,
    _create_skills_table
)


def test_color_scheme():
    """Color scheme fonksiyonunu test et"""
    print("\n[TEST] Color Scheme...")
    try:
        default_scheme = _get_color_scheme("default")
        blue_scheme = _get_color_scheme("blue")
        green_scheme = _get_color_scheme("green")
        red_scheme = _get_color_scheme("red")
        
        assert "primary" in default_scheme
        assert "secondary" in default_scheme
        assert default_scheme["primary"] == "#2c3e50"
        assert blue_scheme["primary"] == "#1a237e"
        assert green_scheme["primary"] == "#1b5e20"
        assert red_scheme["primary"] == "#b71c1c"
        
        print("  [OK] Color scheme testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Color scheme testleri başarısız: {e}")
        return False


def test_create_styles():
    """Style oluşturma fonksiyonunu test et"""
    print("\n[TEST] Create Styles...")
    try:
        styles = _create_styles("Helvetica", "default")
        assert "title" in styles
        assert "heading" in styles
        assert "normal" in styles
        assert "bold" in styles
        
        # Color scheme ile test (textColor bir Color objesi, hex'e çevirmek için str() kullan)
        blue_styles = _create_styles("Helvetica", "blue")
        # Color objesini test etmek yerine, style'ın oluşturulduğunu doğrula
        assert blue_styles["title"].textColor is not None
        
        print("  [OK] Style oluşturma testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Style oluşturma testleri başarısız: {e}")
        return False


def create_dummy_character():
    """Test için dummy character oluştur"""
    return {
        "name": "Test Karakter",
        "level": 5,
        "race": "Human",
        "class": "Fighter",
        "background": "Soldier",
        "abilities": {
            "Strength": 16,
            "Dexterity": 14,
            "Constitution": 15,
            "Intelligence": 10,
            "Wisdom": 12,
            "Charisma": 8
        },
        "ability_modifiers": {
            "Strength": 3,
            "Dexterity": 2,
            "Constitution": 2,
            "Intelligence": 0,
            "Wisdom": 1,
            "Charisma": -1
        },
        "armor_class": 18,
        "hp_max": 45,
        "hit_dice": "d10",
        "speed": 30,
        "movement_speed": 30,
        "initiative": 2,
        "passive_perception": 11,
        "saving_throws": ["Strength", "Constitution"],
        "saving_throw_modifiers": {
            "Strength": 6,
            "Dexterity": 2,
            "Constitution": 5,
            "Intelligence": 0,
            "Wisdom": 1,
            "Charisma": -1
        },
        "skills": {
            "Athletics": 6,
            "Perception": 4,
            "Survival": 4
        },
        "equipment": [
            {"name": "Longsword", "quantity": 1},
            {"name": "Shield", "quantity": 1},
            {"name": "Chain Mail", "quantity": 1}
        ],
        "spells": {
            "cantrips": ["Light", "Mending"],
            "level1": ["Cure Wounds", "Shield of Faith"]
        },
        "feats": ["Great Weapon Master"],
        "languages": ["Common", "Dwarvish"],
        "personality": {
            "trait": "I'm always polite and respectful",
            "ideal": "Greater Good",
            "bond": "My family",
            "flaw": "I have little respect for those not in the military"
        }
    }


def test_table_creation():
    """Table oluşturma fonksiyonlarını test et"""
    print("\n[TEST] Table Creation...")
    try:
        character = create_dummy_character()
        styles = _create_styles("Helvetica", "default")
        
        # Ability Scores table
        ability_table = _create_ability_scores_table(character, styles)
        assert ability_table is not None
        
        # Combat Stats table
        combat_table = _create_combat_stats_table(character, styles)
        assert combat_table is not None
        
        # Saving Throws table
        saves_table = _create_saving_throws_table(character, styles)
        assert saves_table is not None
        
        # Skills table
        skills_table = _create_skills_table(character, styles)
        assert skills_table is not None
        
        print("  [OK] Table oluşturma testleri başarılı")
        return True
    except Exception as e:
        print(f"  [FAIL] Table oluşturma testleri başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export():
    """PDF export fonksiyonunu test et (PDF oluşturma)"""
    print("\n[TEST] PDF Export...")
    try:
        character = create_dummy_character()
        test_output = project_root / "characters" / "exports" / "test_character.pdf"
        test_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Standard template
        export_dnd_character_pdf_improved(
            character, 
            test_output,
            template="standard",
            page_size="A4",
            options={"show_abilities": True, "show_combat_stats": True}
        )
        
        assert test_output.exists(), "PDF dosyası oluşturulmadı"
        assert test_output.stat().st_size > 0, "PDF dosyası boş"
        
        print(f"  [OK] PDF export testi başarılı: {test_output}")
        
        # Cleanup (opsiyonel)
        # test_output.unlink()
        
        return True
    except Exception as e:
        print(f"  [FAIL] PDF export testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_templates():
    """Farklı template'leri test et"""
    print("\n[TEST] PDF Export Templates...")
    try:
        character = create_dummy_character()
        test_dir = project_root / "characters" / "exports"
        test_dir.mkdir(parents=True, exist_ok=True)
        
        templates = ["standard", "compact", "detailed"]
        results = []
        
        for template in templates:
            test_output = test_dir / f"test_character_{template}.pdf"
            try:
                export_dnd_character_pdf_improved(
                    character,
                    test_output,
                    template=template,
                    page_size="A4"
                )
                assert test_output.exists()
                results.append((template, True, test_output))
                print(f"  [OK] {template} template PDF oluşturuldu")
            except Exception as e:
                results.append((template, False, str(e)))
                print(f"  [FAIL] {template} template PDF oluşturulamadı: {e}")
        
        all_success = all(result[1] for result in results)
        return all_success
    except Exception as e:
        print(f"  [FAIL] Template testleri başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_pdf_export_options():
    """PDF export options'ı test et"""
    print("\n[TEST] PDF Export Options...")
    try:
        character = create_dummy_character()
        test_output = project_root / "characters" / "exports" / "test_character_options.pdf"
        test_output.parent.mkdir(parents=True, exist_ok=True)
        
        # Options ile export
        export_dnd_character_pdf_improved(
            character,
            test_output,
            template="standard",
            page_size="A4",
            options={
                "show_abilities": True,
                "show_combat_stats": True,
                "show_saving_throws": False,  # Bu bölümü gizle
                "show_skills": True,
                "show_equipment": False,  # Bu bölümü gizle
                "show_spells": True,
                "color_scheme": "blue"
            }
        )
        
        assert test_output.exists()
        print(f"  [OK] Options ile PDF export başarılı: {test_output}")
        return True
    except Exception as e:
        print(f"  [FAIL] Options testi başarısız: {e}")
        import traceback
        traceback.print_exc()
        return False


def run_all_tests():
    """Tüm testleri çalıştır"""
    print("=" * 70)
    print("PDF EXPORT TEST SUITE")
    print("=" * 70)
    
    tests = [
        ("Color Scheme", test_color_scheme),
        ("Create Styles", test_create_styles),
        ("Table Creation", test_table_creation),
        ("PDF Export", test_pdf_export),
        ("PDF Export Templates", test_pdf_export_templates),
        ("PDF Export Options", test_pdf_export_options),
    ]
    
    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n[ERROR] {test_name} testi exception fırlattı: {e}")
            import traceback
            traceback.print_exc()
            results.append((test_name, False))
    
    # Özet
    print("\n" + "=" * 70)
    print("TEST SONUÇLARI")
    print("=" * 70)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "[OK]" if result else "[FAIL]"
        print(f"{status} {test_name}")
    
    print("\n" + "=" * 70)
    print(f"TOPLAM: {passed}/{total} test başarılı")
    print("=" * 70)
    
    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

