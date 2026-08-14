"""
Unit Tests for PF1e Archetype Compatibility & Multiclass Stacking Engine
========================================================================
Verifies archetype feature replacement conflict detection, archetype combination,
and multiclass BAB / Fort / Ref / Will save stacking.
"""

import pytest
from rules.archetype_engine import PF1eArchetypeEngine, PF1eMulticlassEngine
from rules.calculators import PF1e_Calculator


def test_archetype_compatibility_validation():
    """Weapon Master + Armor Master (compatible) vs Two-Handed + Weapon Master (conflict)."""
    # 1. Weapon Master + Armor Master -> Compatible (No overlapping replaced features)
    is_compat, conflicts = PF1eArchetypeEngine.validate_archetype_compatibility(
        "Fighter", ["weapon master", "armor master"]
    )
    assert is_compat is True
    assert len(conflicts) == 0

    # 2. Weapon Master + Two-Handed Fighter -> Conflict (Both replace Armor Training 1..4)
    is_compat_bad, conflicts_bad = PF1eArchetypeEngine.validate_archetype_compatibility(
        "Fighter", ["weapon master", "two-handed fighter"]
    )
    assert is_compat_bad is False
    assert len(conflicts_bad) > 0
    assert "Armor Training 1" in conflicts_bad[0]


def test_rogue_archetypes_knife_master_and_scout_stacking():
    """Rogue Knife Master (replaces Trapfinding) + Scout (replaces Uncanny Dodge) are 100% compatible."""
    is_compat, conflicts = PF1eArchetypeEngine.validate_archetype_compatibility(
        "Rogue", ["Knife Master", "Scout"]
    )
    assert is_compat is True
    assert len(conflicts) == 0

    feats = PF1eArchetypeEngine.get_archetype_features("Rogue", ["Knife Master", "Scout"])
    assert "Trapfinding" in feats["replaced_features"]
    assert "Uncanny Dodge" in feats["replaced_features"]
    assert "Hidden Blade" in feats["granted_features"]
    assert "Scout's Charge" in feats["granted_features"]


def test_rogue_knife_master_and_rake_conflict():
    """Knife Master (replaces Trapfinding) + Rake (replaces Trapfinding) -> Conflict on Trapfinding."""
    is_compat, conflicts = PF1eArchetypeEngine.validate_archetype_compatibility(
        "Rogue", ["Knife Master", "Rake"]
    )
    assert is_compat is False
    assert len(conflicts) == 1
    assert "Trapfinding" in conflicts[0]


def test_wizard_spellslinger_and_scrollmaster_conflict():
    """Spellslinger (replaces Arcane Bond) + Scrollmaster (replaces Arcane Bond) -> Conflict on Arcane Bond."""
    is_compat, conflicts = PF1eArchetypeEngine.validate_archetype_compatibility(
        "Wizard", ["Spellslinger", "Scrollmaster"]
    )
    assert is_compat is False
    assert any("Arcane Bond" in c for c in conflicts)


def test_alchemist_vivisectionist_and_grenadier_compatibility():
    """Vivisectionist (replaces Bomb) + Grenadier (replaces Brew Potion, Poison Resistance) -> Compatible."""
    is_compat, conflicts = PF1eArchetypeEngine.validate_archetype_compatibility(
        "Alchemist", ["Vivisectionist", "Grenadier"]
    )
    assert is_compat is True
    assert len(conflicts) == 0


def test_get_available_archetypes():
    """Check that registered classes have available archetypes."""
    fighter_archs = PF1eArchetypeEngine.get_available_archetypes("Fighter")
    assert "Weapon Master" in fighter_archs
    assert "Armor Master" in fighter_archs
    assert "Mutation Warrior" in fighter_archs

    barbarian_archs = PF1eArchetypeEngine.get_available_archetypes("Barbarian")
    assert "Titan Mauler" in barbarian_archs
    assert "Invulnerable Rager" in barbarian_archs


def test_archetype_feature_replacements():
    """Weapon Master replaces Armor Training and grants Weapon Guard."""
    feats = PF1eArchetypeEngine.get_archetype_features("Fighter", ["weapon master"])
    assert "Armor Training 1" in feats["replaced_features"]
    assert "Weapon Guard" in feats["granted_features"]


def test_multiclass_bab_and_save_stacking():
    """Fighter 3 (Full BAB 3, Good Fort 3, Poor Ref 1, Poor Will 1) + Rogue 2 (Med BAB 1, Poor Fort 0, Good Ref 3, Poor Will 0)."""
    res = PF1eMulticlassEngine.calculate_multiclass_progression({"Fighter": 3, "Rogue": 2})

    assert res["total_level"] == 5
    assert res["total_bab"] == 4  # 3 (Fighter 3) + 1 (Rogue 2: floor(2*3/4)) = 4
    assert res["base_fort"] == 3  # 3 (Fighter 3) + 0 (Rogue 2: floor(2/3)) = 3
    assert res["base_ref"] == 4   # 1 (Fighter 3: floor(3/3)) + 3 (Rogue 2: 2 + 2/2) = 4
    assert res["base_will"] == 1  # 1 (Fighter 3) + 0 (Rogue 2) = 1


def test_multiclass_triple_class_stacking():
    """Fighter 4 (BAB 4, Fort 4, Ref 1, Will 1) + Rogue 4 (BAB 3, Fort 1, Ref 4, Will 1) + Wizard 2 (BAB 1, Fort 0, Ref 0, Will 3)."""
    res = PF1eMulticlassEngine.calculate_multiclass_progression({
        "Fighter": 4,
        "Rogue": 4,
        "Wizard": 2
    })

    assert res["total_level"] == 10
    # BAB: 4 (Ftr) + 3 (Rog) + 1 (Wiz) = 8
    assert res["total_bab"] == 8
    # Fort: 4 (Ftr) + 1 (Rog) + 0 (Wiz) = 5
    assert res["base_fort"] == 5
    # Ref: 1 (Ftr) + 4 (Rog) + 0 (Wiz) = 5
    assert res["base_ref"] == 5
    # Will: 1 (Ftr) + 1 (Rog) + 3 (Wiz) = 5
    assert res["base_will"] == 5


def test_multiclass_stat_pipeline_integration():
    """PF1e_Calculator applies multiclass BAB, save stacking, and archetype details."""
    calc = PF1e_Calculator()
    char_mc = {
        "name": "Valeros Rogue",
        "system": "pathfinder1e",
        "level": 5,
        "class": "Fighter",
        "archetype": "Weapon Master",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "wisdom": 10},
        "multiclass": {"Fighter": 3, "Rogue": 2}
    }

    derived = calc.update_all_stats(char_mc)

    assert derived["bab"] == 4
    assert derived["saving_throws"]["Fortitude"] == 5  # Base Fort 3 + Con 2
    assert derived["saving_throws"]["Reflex"] == 6     # Base Ref 4 + Dex 2
    assert derived["saving_throws"]["Will"] == 1       # Base Will 1 + Wis 0

    assert derived["archetype_details"]["is_compatible"] is True
    assert "Weapon Guard" in derived["archetype_details"]["granted_features"]
    assert "Armor Training 1" in derived["archetype_details"]["replaced_features"]

