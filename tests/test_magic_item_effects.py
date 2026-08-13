import pytest
from rules.calculators import PF1e_Calculator, extract_magic_item_modifiers, is_item_equipped

def test_belt_of_strength_increases_str_and_attack():
    """Test that equipping Belt of Giant Strength +2 increases Strength, modifier, and melee attack."""
    calc = PF1e_Calculator()
    char = {
        "system": "pathfinder1e",
        "name": "Krag",
        "class": "Fighter",
        "class_data": {"bab_progression": "full"},
        "level": 1,
        "race": "Human",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 12, "intelligence": 10, "wisdom": 10, "charisma": 8},
        "equipment": []
    }

    # Unequipped baseline (Human gets +2 racial Strength -> 18, Mod +4, BAB 1 -> Melee Atk +5)
    res_base = calc.update_all_stats(char)
    assert res_base["ability_scores"]["Strength"] == 18
    assert res_base["ability_modifiers"]["Strength"] == 4
    assert res_base["melee_attack_bonus"] == 5  # BAB 1 + STR mod 4

    # Equip Belt of Giant Strength +2 -> Strength becomes 20 (Mod +5, BAB 1 -> Melee Atk +6)
    belt = {"name": "Belt of Giant Strength +2", "is_equipped": True, "kategori": "gear"}
    char["equipment"] = [belt]

    res_belt = calc.update_all_stats(char)
    assert res_belt["ability_scores"]["Strength"] == 20
    assert res_belt["ability_modifiers"]["Strength"] == 5
    assert res_belt["melee_attack_bonus"] == 6  # BAB 1 + STR mod 5

    # Unequip Belt -> Returns to 18 Strength
    belt["is_equipped"] = False
    res_unequipped = calc.update_all_stats(char)
    assert res_unequipped["ability_scores"]["Strength"] == 18
    assert res_unequipped["melee_attack_bonus"] == 5


def test_ring_of_protection_and_cloak_of_resistance():
    """Test Ring of Protection +2 (Deflection AC) and Cloak of Resistance +3 (Saves)."""
    calc = PF1e_Calculator()
    char = {
        "system": "pathfinder1e",
        "name": "Valeros",
        "class": "Fighter",
        "level": 1,
        "race": "Human",
        "abilities": {"strength": 14, "dexterity": 14, "constitution": 14, "intelligence": 10, "wisdom": 10, "charisma": 10},
        "equipment": []
    }

    res_base = calc.update_all_stats(char)
    base_ac = res_base["armor_class"]
    base_fort = res_base["saving_throws"]["Fortitude"]
    base_ref = res_base["saving_throws"]["Reflex"]
    base_will = res_base["saving_throws"]["Will"]

    # Equip Ring of Protection +2 and Cloak of Resistance +3
    ring = {"name": "Ring of Protection +2", "is_equipped": True}
    cloak = {"name": "Cloak of Resistance +3", "is_equipped": True}
    char["equipment"] = [ring, cloak]

    res_magic = calc.update_all_stats(char)
    assert res_magic["armor_class"] == base_ac + 2
    assert res_magic["touch_ac"] == 10 + 2 + 2  # 10 + DEX 2 + Deflection 2
    assert res_magic["saving_throws"]["Fortitude"] == base_fort + 3
    assert res_magic["saving_throws"]["Reflex"] == base_ref + 3
    assert res_magic["saving_throws"]["Will"] == base_will + 3


def test_magic_item_bonus_stacking_rules():
    """Test PF1e CRB Chapter 15 bonus stacking rules (only highest bonus of each type applies)."""
    ring1 = {"name": "Ring of Protection +1", "is_equipped": True}
    ring2 = {"name": "Ring of Protection +3", "is_equipped": True}
    ring3 = {"name": "Ring of Protection +2", "is_equipped": True}
    eq = [ring1, ring2, ring3]

    mods = extract_magic_item_modifiers(eq)
    # Only highest deflection bonus (+3) should apply!
    assert mods["deflection_ac"] == 3


def test_boots_of_elvenkind_skill_bonus():
    """Test Boots of Elvenkind (+5 Acrobatics skill bonus)."""
    calc = PF1e_Calculator()
    char = {
        "system": "pathfinder1e",
        "name": "Merisiel",
        "class": "Rogue",
        "level": 1,
        "race": "Elf",
        "abilities": {"strength": 10, "dexterity": 16, "constitution": 12, "intelligence": 12, "wisdom": 10, "charisma": 10},
        "equipment": [{"name": "Boots of Elvenkind", "is_equipped": True}]
    }

    res = calc.update_all_stats(char)
    # Acrobatics = DEX 3 + Boots 5 = 8 (plus ranks if any)
    assert res["skills"]["acrobatics"] >= 8
