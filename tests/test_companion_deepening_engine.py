import pytest
from rules.companion_calculator import PF1eCompanionCalculator, ANIMAL_COMPANION_TABLE
from rules.calculators import PF1e_Calculator

def test_effective_druid_level_calculation():
    """Verify EDL calculation for Druids vs Rangers."""
    assert PF1eCompanionCalculator.calculate_effective_druid_level("Druid", 5) == 5
    assert PF1eCompanionCalculator.calculate_effective_druid_level("Hunter", 7) == 7
    # Ranger gets Druid Level - 3 (min 1)
    assert PF1eCompanionCalculator.calculate_effective_druid_level("Ranger", 5) == 2
    assert PF1eCompanionCalculator.calculate_effective_druid_level("Ranger", 1) == 1

def test_animal_companion_stat_scaling():
    """Verify Animal Companion stat scaling for Level 1 vs Level 10 Druid."""
    raw = {"name": "Gölge", "species": "Kurt", "str": 13, "dex": 15, "con": 15, "acBonus": 2}
    
    # Level 1 Druid
    comp_lvl1 = PF1eCompanionCalculator.calculate_animal_companion(raw, "Druid", 1)
    assert comp_lvl1["effective_druid_level"] == 1
    assert comp_lvl1["hd_count"] == 2
    assert comp_lvl1["str"] == 13
    assert "Link" in comp_lvl1["special_abilities"]

    # Level 10 Druid (Table 3-8: hd 9, bab 6, nat_armor 8, str_dex +4)
    comp_lvl10 = PF1eCompanionCalculator.calculate_animal_companion(raw, "Druid", 10)
    assert comp_lvl10["effective_druid_level"] == 10
    assert comp_lvl10["hd_count"] == 9
    assert comp_lvl10["bab"] == 6
    assert comp_lvl10["str"] == 17  # 13 + 4
    assert comp_lvl10["natural_armor_bonus"] == 8
    assert "Multiattack" in comp_lvl10["special_abilities"]

def test_familiar_master_bonuses_application():
    """Verify Familiar stat scaling and Master bonus application (Toad +3 HP, Scorpion +4 Init, Weasel +2 Reflex)."""
    # 1. Toad familiar -> +3 HP to Master
    char_toad = {
        "system": "pathfinder1e",
        "name": "Ezren",
        "class": "Wizard",
        "level": 5,
        "abilities": {"strength": 10, "dexterity": 14, "constitution": 12, "intelligence": 18, "wisdom": 10, "charisma": 10},
        "companion": {
            "type": "familiar",
            "presetKey": "toad",
            "name": "Boru"
        }
    }

    calc = PF1e_Calculator()
    res_toad = calc.update_all_stats(char_toad)
    assert "companion" in res_toad
    fam_data = res_toad["companion"]
    assert fam_data["master_level"] == 5
    assert fam_data["int"] == 8  # 6 + floor(5/2) = 8
    assert fam_data["master_bonus"]["target"] == "hp"

    # 2. Greensting Scorpion familiar -> +4 Initiative to Master
    char_scorp = {
        "system": "pathfinder1e",
        "name": "Ezren",
        "class": "Wizard",
        "level": 5,
        "abilities": {"strength": 10, "dexterity": 14, "constitution": 12, "intelligence": 18, "wisdom": 10, "charisma": 10},
        "companion": {
            "type": "familiar",
            "presetKey": "scorpion",
            "name": "İğne"
        }
    }

    res_scorp = calc.update_all_stats(char_scorp)
    # Base Dex 14 (+2) + Scorpion (+4) = 6 Initiative
    assert res_scorp["initiative"] == 6
