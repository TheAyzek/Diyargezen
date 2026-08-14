"""
Unit Tests for Diyargezen Level-Up Wizard & Soft-Block GM Validator
=====================================================================
Seviye Atlatma Sihirbazı (State Machine), HP kazanımı, Stat Artışı (L4/8/12/16/20),
Soft-Block Feat/Trait ön koşul uyarıları ve GM Override testleri.
"""

import sys
from pathlib import Path

root_dir = Path(__file__).resolve().parent.parent
if str(root_dir) not in sys.path:
    sys.path.insert(0, str(root_dir))

from rules.character_manager import CharacterManager
from rules.pf1e_rules import PF1EValidator



def test_level_up_slot_calculations(tmp_path: Path):
    db_path = tmp_path / "dummy.db"
    cm = CharacterManager(db_path)

    # 1. Level 1 Fighter (Con=14 (+2), Int=10 (+0), HitDie=10)
    char = {
        "name": "Valeros",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Fighter",
        "race": "Human",
        "hit_die": 10,
        "class_skill_points": 2,
        "abilities": {"str": 16, "dex": 13, "con": 14, "int": 10, "wis": 12, "cha": 8}
    }

    # Level 1 -> Level 2 transition
    slots_l2 = cm.calculate_level_up_slots(char)
    assert slots_l2["current_level"] == 1
    assert slots_l2["new_level"] == 2
    assert slots_l2["has_stat_increase"] is False
    assert slots_l2["has_new_feat"] is False
    # HP Average = floor(10/2) + 1 + 2 (CON) = 5 + 1 + 2 = 8
    assert slots_l2["hp_average_gain"] == 8
    # Skills = 2 (Base) + 0 (Int) + 1 (Human) = 3
    assert slots_l2["skill_ranks_available"] == 3

    # Level 3 -> Level 4 transition (Stat increase expected)
    char["level"] = 3
    slots_l4 = cm.calculate_level_up_slots(char)
    assert slots_l4["new_level"] == 4
    assert slots_l4["has_stat_increase"] is True
    assert slots_l4["stat_increase_points"] == 1


def test_apply_level_up_state_machine(tmp_path: Path):
    db_path = tmp_path / "dummy.db"
    cm = CharacterManager(db_path)

    char = {
        "name": "Seelah",
        "system": "pathfinder1e",
        "level": 3,
        "max_hp": 28,
        "hit_die": 10,
        "abilities": {"str": 17, "dex": 12, "con": 14, "int": 10, "wis": 12, "cha": 14},
        "skill_ranks": {"Acrobatics": 1},
        "feats": ["Weapon Focus"]
    }
    cm.set_active_character(char)

    # Apply Level 3 -> Level 4 choices (+1 STR, +8 HP, +1 Acrobatics rank)
    choices = {
        "hp_gain": 8,
        "stat_increase": "str",
        "skill_ranks": {"Acrobatics": 1},
        "feats": []
    }

    updated = cm.apply_level_up(choices)
    assert updated["level"] == 4
    assert updated["max_hp"] == 36
    assert updated["abilities"]["str"] == 18
    assert updated["skill_ranks"]["Acrobatics"] == 2


def test_pf1e_validator_soft_block_and_gm_override():
    validator = PF1EValidator()

    # Character failing Power Attack prerequisite (STR = 10 < 13)
    weak_char = {
        "level": 1,
        "bab": 1,
        "abilities": {"str": 10, "dex": 14, "int": 10},
        "feats": [{"name": "Power Attack"}],
        "traits": []
    }

    warnings = validator.validate(weak_char)
    assert len(warnings) >= 1
    assert any("Power Attack" in w and "Güç" in w for w in warnings)

    # Apply GM Override flag
    weak_char["gm_override"] = True
    warnings_overridden = validator.validate(weak_char)
    assert len(warnings_overridden) == 0


def test_pf1e_validator_trait_category_conflict():
    validator = PF1EValidator()

    # Character selecting 2 Combat traits
    conflict_char = {
        "level": 1,
        "abilities": {"str": 14, "dex": 14},
        "feats": [],
        "traits": [
            {"name": "Armor Expert", "trait_category": "Combat"},
            {"name": "Reactionary", "trait_category": "Combat"}
        ]
    }

    warnings = validator.validate(conflict_char)
    assert len(warnings) >= 1
    assert any("aynı kategoriden (Combat)" in w for w in warnings)


def test_retroactive_con_hp_gain(tmp_path: Path):
    """PF1e CRB p. 16: Increasing CON score at Level 4/8/12/16/20 grants +1 HP per previous level retroactively."""
    db_path = tmp_path / "dummy.db"
    cm = CharacterManager(db_path)

    # Level 3 Fighter with CON 13 (+1 mod), Max HP = 27
    char = {
        "name": "Amiri",
        "system": "pathfinder1e",
        "level": 3,
        "max_hp": 27,
        "hit_die": 10,
        "abilities": {"str": 16, "dex": 13, "con": 13, "int": 10, "wis": 12, "cha": 8},
    }
    cm.set_active_character(char)

    # Level up to 4, choosing CON increase (13 -> 14, mod goes +1 -> +2)
    # Base HP gain = 6 (average) + 2 (new CON mod) = 8
    # Retroactive HP gain = 3 (previous levels) * 1 (new CON mod - old CON mod) = 3
    # Total HP gain = 8 (base) + 3 (retroactive) = 11. Max HP should become 27 + 11 = 38
    choices = {
        "stat_increase": "con",
        "hp_gain": 8,
    }

    updated = cm.apply_level_up(choices)
    assert updated["level"] == 4
    assert updated["abilities"]["con"] == 14
    assert updated["max_hp"] == 38


def test_favored_class_bonus_hp(tmp_path: Path):
    """Testing Favored Class Bonus +1 HP choice during level up."""
    db_path = tmp_path / "dummy.db"
    cm = CharacterManager(db_path)

    char = {
        "name": "Kyra",
        "system": "pathfinder1e",
        "level": 1,
        "max_hp": 10,
        "hit_die": 8,
        "abilities": {"str": 14, "dex": 10, "con": 12, "int": 10, "wis": 16, "cha": 12},
    }
    cm.set_active_character(char)

    # Level up 1 -> 2 with FCB choice = "hp" (+1 extra HP)
    choices = {
        "hp_gain": 6,
        "favored_class_bonus": "hp"
    }

    updated = cm.apply_level_up(choices)
    assert updated["level"] == 2
    assert updated["max_hp"] == 10 + 6 + 1  # 17


def test_class_feature_filtering_by_class_name():
    """Verify that get_class_features and get_feats filter class features strictly by character class."""
    cm = CharacterManager("data/characters.db")
    witch_features = cm.get_class_features("pf1e", class_name="Witch")
    fighter_features = cm.get_class_features("pf1e", class_name="Fighter")

    # Barbarian Rage Powers should NOT appear in Witch features
    witch_names = [f.isim for f in witch_features]
    assert not any("Rage" in n for n in witch_names if "Rage Power" in n)

    # Witch Hexes should NOT appear in Fighter features
    fighter_names = [f.isim for f in fighter_features]
    assert not any(n in ("Agony", "Abominate", "Witchcraft") for n in fighter_names)


def test_level_up_max_hp_choice(tmp_path: Path):
    """Verify level up using Maximum HP mode (full Hit Die)."""
    db_path = tmp_path / "dummy.db"
    cm = CharacterManager(db_path)

    char = {
        "name": "Valeros Max",
        "system": "pathfinder1e",
        "level": 1,
        "max_hp": 12,
        "hit_die": 10,
        "abilities": {"str": 16, "dex": 13, "con": 14, "int": 10, "wis": 12, "cha": 8},
    }
    cm.set_active_character(char)

    # Level up 1 -> 2 choosing Maximum HP (10 Hit Die + 2 CON mod = 12)
    choices = {
        "hp_gain": 12,
        "favored_class_bonus": "hp"
    }

    updated = cm.apply_level_up(choices)
    assert updated["level"] == 2
    # 12 + 12 (max roll + con) + 1 (FCB) = 25
    assert updated["max_hp"] == 25


def test_level_up_human_bonus_skill_points(tmp_path: Path):
    """Verify that Humans gain +1 bonus skill rank per level during Level-Up (PF1e CRB p. 27)."""
    db_path = tmp_path / "dummy.db"
    cm = CharacterManager(db_path)

    human_fighter = {
        "name": "Human Fighter",
        "system": "pathfinder1e",
        "race": "Human",
        "class": "Fighter",
        "class_skill_points": 2,
        "abilities": {"int": 10} # 0 mod
    }

    slots = cm.calculate_level_up_slots(human_fighter)
    # 2 (Base) + 0 (Int) + 1 (Human) = 3
    assert slots["skill_ranks_available"] == 3

    elf_fighter = {
        "name": "Elf Fighter",
        "system": "pathfinder1e",
        "race": "Elf",
        "class": "Fighter",
        "class_skill_points": 2,
        "abilities": {"int": 10}
    }
    slots_elf = cm.calculate_level_up_slots(elf_fighter)
    # 2 (Base) + 0 (Int) + 0 (Elf) = 2
    assert slots_elf["skill_ranks_available"] == 2


def test_level_up_preserves_spells_across_multiple_levels(tmp_path: Path):
    """Verify that learning new spells at level-up accumulates without wiping previous spells."""
    db_path = tmp_path / "dummy.db"
    cm = CharacterManager(db_path)

    char = {
        "name": "Ezren",
        "system": "pathfinder1e",
        "level": 1,
        "class": "Wizard",
        "spells": [{"name": "Magic Missile", "level": 1}, {"name": "Mage Armor", "level": 1}]
    }
    cm.set_active_character(char)

    # Level up to 2, adding Shield and Burning Hands
    choices_l2 = {
        "hp_gain": 6,
        "spells_learned": [{"name": "Shield", "level": 1}, {"name": "Burning Hands", "level": 1}]
    }
    updated_l2 = cm.apply_level_up(choices_l2)
    assert updated_l2["level"] == 2
    assert len(updated_l2["spells"]) == 4

    spell_names = [s.get("name") for s in updated_l2["spells"]]
    assert "Magic Missile" in spell_names
    assert "Mage Armor" in spell_names
    assert "Shield" in spell_names
    assert "Burning Hands" in spell_names


