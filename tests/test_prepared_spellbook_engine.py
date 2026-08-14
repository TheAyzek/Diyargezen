import pytest
from rules.calculators import PF1e_Calculator

def test_prepared_spellcaster_dcs_and_bonus_slots():
    """Verify Level 5 Wizard spell DCs (10 + level + INT mod) and bonus spell slots."""
    wizard_char = {
        "system": "pathfinder1e",
        "name": "Ezren",
        "class": "Wizard",
        "level": 5,
        "abilities": {
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 18,  # +4 INT Mod
            "wisdom": 10,
            "charisma": 10
        },
        "feats": ["Spell Focus (Evocation)", "Combat Casting"]
    }

    calc = PF1e_Calculator()
    res = calc.update_all_stats(wizard_char)

    assert "spellcasting" in res
    sc = res["spellcasting"]

    # Ability & Caster Level
    assert sc["primary_ability"] == "intelligence"
    assert sc["ability_modifier"] == 4
    assert sc["caster_level"] == 5

    # Concentration: CL 5 + IntMod 4 + Combat Casting 4 = 13
    assert sc["has_combat_casting"] is True
    assert sc["concentration_bonus"] == 13

    # Spell DCs: 10 + lvl + IntMod(4) + SpellFocus(1)
    # Lvl 0 -> 10 + 0 + 4 + 1 = 15
    # Lvl 1 -> 10 + 1 + 4 + 1 = 16
    # Lvl 2 -> 10 + 2 + 4 + 1 = 17
    # Lvl 3 -> 10 + 3 + 4 + 1 = 18
    assert sc["spell_dcs"]["0"] == 15
    assert sc["spell_dcs"]["1"] == 16
    assert sc["spell_dcs"]["2"] == 17
    assert sc["spell_dcs"]["3"] == 18

    # Bonus slots for 18 Int (+4 Mod):
    # Lvl 1: +1 slot, Lvl 2: +1 slot, Lvl 3: +1 slot, Lvl 4: +1 slot
    assert sc["bonus_slots"][1] == 1
    assert sc["bonus_slots"][2] == 1
    assert sc["bonus_slots"][3] == 1

def test_spontaneous_spellcaster_and_slot_tracking():
    """Verify Sorcerer spellcasting setup and slot calculation."""
    sorcerer_char = {
        "system": "pathfinder1e",
        "name": "Seoni",
        "class": "Sorcerer",
        "level": 5,
        "abilities": {
            "strength": 10,
            "dexterity": 14,
            "constitution": 12,
            "intelligence": 10,
            "wisdom": 10,
            "charisma": 18  # +4 CHA Mod
        }
    }

    calc = PF1e_Calculator()
    res = calc.update_all_stats(sorcerer_char)

    sc = res["spellcasting"]
    assert sc["primary_ability"] == "charisma"
    assert sc["ability_modifier"] == 4

    # Spell DCs for 18 Cha (+4 Mod):
    # Lvl 1 -> 10 + 1 + 4 = 15
    # Lvl 2 -> 10 + 2 + 4 = 16
    assert sc["spell_dcs"]["1"] == 15
    assert sc["spell_dcs"]["2"] == 16
    assert sc["is_spontaneous"] is True
    assert sc["is_prepared"] is False


def test_caster_classification_and_prepared_slot_validation():
    """Verify prepared vs spontaneous caster identification and metamagic slot validation."""
    from rules.spell_engine import (
        is_prepared_caster,
        is_spontaneous_caster,
        validate_prepared_spell_slot
    )

    # Classification
    assert is_prepared_caster("Wizard") is True
    assert is_prepared_caster("Cleric") is True
    assert is_prepared_caster("Druid") is True
    assert is_prepared_caster("Magus") is True
    assert is_prepared_caster("Sorcerer") is False
    assert is_prepared_caster("Bard") is False

    assert is_spontaneous_caster("Sorcerer") is True
    assert is_spontaneous_caster("Oracle") is True
    assert is_spontaneous_caster("Bard") is True
    assert is_spontaneous_caster("Wizard") is False

    # Legal: Level 1 spell in Level 1 slot
    res1 = validate_prepared_spell_slot(slot_level=1, base_spell_level=1)
    assert res1["valid"] is True
    assert res1["effective_spell_level"] == 1

    # Legal: Level 1 spell in Level 2 slot (under-preparation allowed in PF1e)
    res2 = validate_prepared_spell_slot(slot_level=2, base_spell_level=1)
    assert res2["valid"] is True

    # Illegal: Level 2 spell in Level 1 slot
    res3 = validate_prepared_spell_slot(slot_level=1, base_spell_level=2)
    assert res3["valid"] is False
    assert len(res3["reasons"]) > 0

    # Metamagic: Level 1 spell + Empower (+2) = Effective 3 -> In Level 3 slot: VALID
    res4 = validate_prepared_spell_slot(
        slot_level=3,
        base_spell_level=1,
        applied_metamagic=["Empower Spell"]
    )
    assert res4["valid"] is True
    assert res4["effective_spell_level"] == 3

    # Metamagic: Level 1 spell + Empower (+2) = Effective 3 -> In Level 2 slot: INVALID
    res5 = validate_prepared_spell_slot(
        slot_level=2,
        base_spell_level=1,
        applied_metamagic=["Empower Spell"]
    )
    assert res5["valid"] is False

    # GM Override: Overriding illegal preparation
    res6 = validate_prepared_spell_slot(
        slot_level=2,
        base_spell_level=1,
        applied_metamagic=["Empower Spell"],
        is_overridden=True
    )
    assert res6["valid"] is True
    assert res6["is_overridden"] is True

