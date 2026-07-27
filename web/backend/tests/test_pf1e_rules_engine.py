import pytest
from rules.calculators import PF1e_Calculator

def test_pf1e_custom_modifiers():
    calc = PF1e_Calculator()
    char = {
        "system": "pf1e",
        "level": 1,
        "class": "Fighter",
        "class_data": {"hit_die": "d10", "bab_progression": "full"},
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "custom_modifiers": [
            {"stat": "ac", "value": 2, "is_active": True, "name": "GM Armor Shield Buff"},
            {"stat": "hp", "value": 5, "is_active": True, "name": "Toughness GM Bonus"},
            {"stat": "bab", "value": 1, "is_active": True, "name": "Blessing"}
        ]
    }
    derived = calc.update_all_stats(char)
    # Base AC = 10 + 2 (Dex) + 2 (Custom AC) = 14
    assert derived["armor_class"] == 14
    # Base HP = 10 + 2 (Con) + 5 (Custom HP) = 17
    assert derived["hit_points"] == 17
    # Base BAB = 1 + 1 (Custom BAB) = 2
    assert derived["bab"] == 2

def test_pf1e_prerequisite_soft_block():
    calc = PF1e_Calculator()
    char = {
        "system": "pf1e",
        "level": 1,
        "abilities": {"strength": 10, "dexterity": 10},
        "bab": 0
    }
    feat_data = {
        "name": "Power Attack",
        "prerequisites": ["Str 13", "Base attack bonus +1"]
    }
    
    # Without override -> fails validation
    res = calc.check_prerequisites(char, feat_data, is_overridden=False)
    assert res["valid"] is False
    assert len(res["warnings"]) == 2
    assert res["can_override"] is True
    
    # With GM override -> passes validation with overridden flag
    res_override = calc.check_prerequisites(char, feat_data, is_overridden=True)
    assert res_override["valid"] is True
    assert res_override["overridden"] is True
    assert len(res_override["warnings"]) == 2

def test_pf1e_racial_ability_bonuses():
    calc = PF1e_Calculator()
    
    # 1. Dwarf: +2 Con, +2 Wis, -2 Cha
    char_dwarf = {
        "system": "pf1e",
        "race": "Dwarf",
        "abilities": {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}
    }
    scores_dwarf = calc.get_adjusted_abilities(char_dwarf)
    assert scores_dwarf["constitution"] == 12
    assert scores_dwarf["wisdom"] == 12
    assert scores_dwarf["charisma"] == 8
    assert scores_dwarf["strength"] == 10

    # 2. Elf: +2 Dex, +2 Int, -2 Con
    char_elf = {
        "system": "pf1e",
        "race": "Elf",
        "abilities": {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}
    }
    scores_elf = calc.get_adjusted_abilities(char_elf)
    assert scores_elf["dexterity"] == 12
    assert scores_elf["intelligence"] == 12
    assert scores_elf["constitution"] == 8

    # 3. Human: +2 to chosen stat (or default Strength)
    char_human = {
        "system": "pf1e",
        "race": "Human",
        "abilities": {"strength": 10, "dexterity": 10, "constitution": 10, "intelligence": 10, "wisdom": 10, "charisma": 10}
    }
    scores_human = calc.get_adjusted_abilities(char_human)
    assert scores_human["strength"] == 12

