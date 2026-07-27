import pytest
from rules.spell_engine import (
    calculate_bonus_spell_slots,
    calculate_spell_save_dc,
    get_base_spell_slots,
    calculate_total_spell_slots,
    validate_spell_prerequisites,
    get_casting_ability_for_class,
)

def test_casting_ability_mapping():
    assert get_casting_ability_for_class("Wizard") == "intelligence"
    assert get_casting_ability_for_class("Cleric") == "wisdom"
    assert get_casting_ability_for_class("Sorcerer") == "charisma"
    assert get_casting_ability_for_class("Bard") == "charisma"


def test_bonus_spell_slots_pf1e():
    # Ability score 10 (+0): 0 bonus slots
    assert calculate_bonus_spell_slots(10) == {}

    # Ability score 14 (+2): 1st -> 1, 2nd -> 1
    slots14 = calculate_bonus_spell_slots(14)
    assert slots14.get(1) == 1
    assert slots14.get(2) == 1
    assert slots14.get(3) is None

    # Ability score 20 (+5): 1st -> 2, 2nd -> 1, 3rd -> 1, 4th -> 1, 5th -> 1
    slots20 = calculate_bonus_spell_slots(20)
    assert slots20.get(1) == 2
    assert slots20.get(2) == 1
    assert slots20.get(5) == 1


def test_spell_save_dc():
    # Level 3 spell, INT mod +4 -> DC = 10 + 3 + 4 = 17
    assert calculate_spell_save_dc(3, 4) == 17
    # Level 1 spell, WIS mod +3, misc +2 -> DC = 10 + 1 + 3 + 2 = 16
    assert calculate_spell_save_dc(1, 3, misc_bonus=2) == 16


def test_total_spell_slots_combination():
    # Wizard level 5 (Base: L0: 4, L1: 3, L2: 2, L3: 1) with INT 18 (+4)
    slots = calculate_total_spell_slots("Wizard", 5, 18)
    assert slots[0] == 4
    assert slots[1] == 4  # 3 base + 1 bonus
    assert slots[2] == 3  # 2 base + 1 bonus
    assert slots[3] == 2  # 1 base + 1 bonus


def test_validate_spell_prerequisites():
    spell_fireball = {
        "name": "Fireball",
        "level": 3,
        "levels_by_class": {"Wizard": 3, "Sorcerer": 3}
    }
    char_low_level = {
        "class": "Wizard",
        "level": 1,
        "abilities": {"intelligence": 16}
    }
    # Level 1 wizard cannot cast level 3 spell
    res = validate_spell_prerequisites(spell_fireball, char_low_level)
    assert not res["valid"]
    assert len(res["reasons"]) > 0

    # Overridden by GM
    res_override = validate_spell_prerequisites(spell_fireball, char_low_level, is_overridden=True)
    assert res_override["valid"]
    assert res_override["is_overridden"]

    # Level 5 Wizard with INT 16 can cast Fireball
    char_capable = {
        "class": "Wizard",
        "level": 5,
        "abilities": {"intelligence": 16}
    }
    res_capable = validate_spell_prerequisites(spell_fireball, char_capable)
    assert res_capable["valid"]
