import pytest
from pathlib import Path
from rules.character_manager import CharacterManager

def test_spells_auto_preserved_across_level_up(tmp_path: Path):
    """Test that spells chosen in previous level are automatically carried over when leveling up."""
    db_path = tmp_path / "dummy.db"
    cm = CharacterManager(db_path)

    # Level 1 Wizard with 2 initial spells
    wizard_char = {
        "id": 101,
        "name": "Ezren",
        "system": "pathfinder1e",
        "class": "Wizard",
        "level": 1,
        "abilities": {"strength": 10, "dexterity": 14, "constitution": 12, "intelligence": 18, "wisdom": 12, "charisma": 10},
        "spells": [
            {"name": "Magic Missile", "sistem_verisi": {"level": 1, "school": "Evocation"}},
            {"name": "Shield", "sistem_verisi": {"level": 1, "school": "Abjuration"}}
        ]
    }

    cm.active_character = wizard_char
    cm.recalculate_character()

    # Verify Level 1 spells present
    assert len(wizard_char["spells"]) == 2
    spell_names = [s["name"] for s in wizard_char["spells"]]
    assert "Magic Missile" in spell_names
    assert "Shield" in spell_names

    # Level Up to Level 2 and add new Level 1 spell (Mage Armor)
    choices_lvl2 = {
        "hp_gain": 4,
        "skill_ranks": {"Spellcraft": 1},
        "spells_learned": [
            {"name": "Magic Missile", "sistem_verisi": {"level": 1, "school": "Evocation"}}, # Previous
            {"name": "Shield", "sistem_verisi": {"level": 1, "school": "Abjuration"}},       # Previous
            {"name": "Mage Armor", "sistem_verisi": {"level": 1, "school": "Conjuration"}}   # New
        ]
    }

    updated_char = cm.apply_level_up(choices_lvl2)

    # Verify Level 2 character retains all 3 spells
    assert updated_char["level"] == 2
    updated_spell_names = [s.get("name") or s.get("isim") for s in updated_char["spells"]]
    assert len(updated_spell_names) == 3
    assert "Magic Missile" in updated_spell_names
    assert "Shield" in updated_spell_names
    assert "Mage Armor" in updated_spell_names

    # Level Up to Level 3 and add Level 2 spell (Scorching Ray)
    choices_lvl3 = {
        "hp_gain": 5,
        "skill_ranks": {"Spellcraft": 1},
        "spells_learned": [
            {"name": "Scorching Ray", "sistem_verisi": {"level": 2, "school": "Evocation"}}
        ]
    }

    updated_char_lvl3 = cm.apply_level_up(choices_lvl3)

    # Verify Level 3 character retains all 4 spells from level 1, 2, and 3
    assert updated_char_lvl3["level"] == 3
    lvl3_spell_names = [s.get("name") or s.get("isim") for s in updated_char_lvl3["spells"]]
    assert len(lvl3_spell_names) == 4
    assert "Magic Missile" in lvl3_spell_names
    assert "Shield" in lvl3_spell_names
    assert "Mage Armor" in lvl3_spell_names
    assert "Scorching Ray" in lvl3_spell_names
