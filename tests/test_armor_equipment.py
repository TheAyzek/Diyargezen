import pytest
from rules.calculators import PF1e_Calculator

def test_english_armor_and_shield_ac_calculation():
    """Verify English armor (Chainmail) and shield (Heavy Shield) AC calculations."""
    calc = PF1e_Calculator()
    char = {
        "name": "Valeros Test",
        "system": "pathfinder1e",
        "class": "Fighter",
        "level": 1,
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "equipment": [
            {"name": "Chainmail", "kategori": "armor_medium", "sistem_verisi": {"armor_class": {"value": 6, "dex": 2}, "check_penalty": -5}},
            {"name": "Heavy Steel Shield", "kategori": "armor_shield", "sistem_verisi": {"shield_bonus": 2, "check_penalty": -2}}
        ]
    }

    derived = calc.update_all_stats(char)

    # Base 10 + Dex +2 (max 2 from Chainmail) + Armor +6 + Shield +2 = 20 AC
    assert derived["armor_class"] == 20
    assert derived["touch_ac"] == 12  # Base 10 + Dex +2
    assert derived["flat_footed_ac"] == 18 # Base 10 + Armor +6 + Shield +2
    assert derived["armor_check_penalty"] == -7 # -5 armor -2 shield

def test_turkish_armor_and_shield_ac_calculation():
    """Verify Turkish named armor (Tam Plaka Zırh) and shield (Ağır Çelik Kalkan) AC calculations."""
    calc = PF1e_Calculator()
    char = {
        "name": "Seoni Test",
        "system": "pathfinder1e",
        "class": "Fighter",
        "level": 1,
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "equipment": [
            {"name": "Tam Plaka Zırh", "kategori": "armor_heavy", "sistem_verisi": {}},
            {"name": "Ağır Çelik Kalkan", "kategori": "armor_shield", "sistem_verisi": {}}
        ]
    }

    derived = calc.update_all_stats(char)

    # Full Plate (+9 AC, max Dex +1) + Heavy Shield (+2 AC) + Base 10 + Dex +1 = 22 AC
    assert derived["armor_class"] == 22
    assert derived["touch_ac"] == 11
    assert derived["flat_footed_ac"] == 21
    assert derived["armor_check_penalty"] <= -6
    assert len(derived["armor_shields"]) == 2
    assert len(derived["gear"]) == 0

