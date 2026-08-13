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
