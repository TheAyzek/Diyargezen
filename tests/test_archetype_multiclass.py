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


def test_multiclass_stat_pipeline_integration():
    """PF1e_Calculator applies multiclass BAB and save stacking."""
    calc = PF1e_Calculator()
    char_mc = {
        "name": "Valeros Rogue",
        "system": "pathfinder1e",
        "level": 5,
        "class": "Fighter",
        "abilities": {"strength": 16, "dexterity": 14, "constitution": 14, "wisdom": 10},
        "multiclass": {"Fighter": 3, "Rogue": 2}
    }

    derived = calc.update_all_stats(char_mc)

    assert derived["bab"] == 4
    assert derived["saving_throws"]["Fortitude"] == 5  # Base Fort 3 + Con 2
    assert derived["saving_throws"]["Reflex"] == 6     # Base Ref 4 + Dex 2
    assert derived["saving_throws"]["Will"] == 1       # Base Will 1 + Wis 0
