"""
Unit Tests for PF1e Weapon Special Abilities & Elemental Damage Engine
======================================================================
Verifies:
- Elemental damage dice (+1d6 Fire/Cold/Shock/Acid)
- Critical threat range doubling (Keen: 18-20 -> 15-20, 19-20 -> 17-20)
- Alignment and Bane mechanics (Holy +2d6, Bane +2/+2d6)
- Speed weapon extra full-round attack
- Effective bonus caps and GP market pricing
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.weapon_special_abilities import (
    calculate_weapon_magical_properties,
    expand_critical_threat_range,
    get_weapon_abilities_catalog
)
from fastapi.testclient import TestClient
from app.main import app


def test_flaming_longsword():
    """Verify +1 Flaming Longsword extra fire damage and market price."""
    weapon = {"name": "Longsword", "damage": "1d8", "crit": "19-20/x2", "cost_gp": 15}
    res = calculate_weapon_magical_properties(weapon, base_enhancement=1, applied_abilities=["flaming"])

    assert res["total_effective_bonus"] == 2
    assert res["effective_attack_bonus"] == 1
    assert res["effective_damage_bonus"] == 1
    assert "1d6 Ateş (Fire)" in res["combined_damage_string"]
    assert res["market_price_gp"] == (4 * 2000) + 300 + 15 # 8315 gp
    assert res["is_valid"] is True


def test_keen_threat_range_expansion():
    """Verify Keen doubles threat range."""
    assert expand_critical_threat_range("18-20/x2") == "15-20/x2"
    assert expand_critical_threat_range("19-20/x2") == "17-20/x2"
    assert expand_critical_threat_range("20/x2") == "19-20/x2"
    assert expand_critical_threat_range("20/x4") == "19-20/x4"

    weapon = {"name": "Scimitar", "damage": "1d6", "crit": "18-20/x2", "cost_gp": 15}
    res = calculate_weapon_magical_properties(weapon, base_enhancement=1, applied_abilities=["keen"])
    assert res["critical"] == "15-20/x2"
    assert res["has_keen"] is True


def test_holy_bane_greatsword_against_evil():
    """Verify +2 Holy Bane Greatsword vs active bane foe."""
    weapon = {"name": "Greatsword", "damage": "2d6", "crit": "19-20/x2", "cost_gp": 50}
    res = calculate_weapon_magical_properties(
        weapon,
        base_enhancement=2,
        applied_abilities=["holy", "bane"],
        is_bane_active=True
    )

    # Base +2, Holy +2, Bane +1 = +5 total effective bonus
    assert res["total_effective_bonus"] == 5
    # Active bane adds +2 atk and +2 dmg
    assert res["effective_attack_bonus"] == 4
    assert res["effective_damage_bonus"] == 4
    assert "2d6 Kutsal (Holy)" in res["combined_damage_string"]
    assert "2d6 Bane Hasarı" in res["combined_damage_string"]
    # 25 * 2000 + 300 + 50 = 50,350 gp
    assert res["market_price_gp"] == 50350


def test_speed_weapon_extra_attack():
    """Verify Speed weapon grants 1 extra full attack."""
    weapon = {"name": "Composite Longbow", "damage": "1d8", "crit": "20/x3", "cost_gp": 100}
    res = calculate_weapon_magical_properties(weapon, base_enhancement=1, applied_abilities=["speed"])

    assert res["has_speed"] is True
    assert res["extra_full_attacks"] == 1
    assert res["total_effective_bonus"] == 4 # 1 + 3


def test_weapon_rules_validation_and_caps():
    """Verify +0 weapon cannot have abilities, and max +10 bonus cap."""
    weapon = {"name": "Dagger", "damage": "1d4", "cost_gp": 2}

    # Cannot add special ability without +1 base enhancement
    res_no_enh = calculate_weapon_magical_properties(weapon, base_enhancement=0, applied_abilities=["flaming"])
    assert res_no_enh["is_valid"] is False
    assert any("en az +1" in w for w in res_no_enh["warnings"])

    # Cannot exceed +10 effective bonus
    res_overflow = calculate_weapon_magical_properties(
        weapon,
        base_enhancement=5,
        applied_abilities=["holy", "unholy", "anarchic", "axiomatic"] # 5 + 8 = 13 > 10
    )
    assert res_overflow["is_valid"] is False
    assert any("+10 tavanını aşıyor" in w for w in res_overflow["warnings"])


def test_weapon_abilities_backend_api():
    """Verify /api/rules/weapon-abilities-catalog and /api/rules/evaluate-weapon-abilities."""
    client = TestClient(app)

    # 1. Catalog
    res_cat = client.get("/api/rules/weapon-abilities-catalog")
    assert res_cat.status_code == 200
    catalog = res_cat.json()["abilities"]
    assert "flaming" in catalog
    assert "keen" in catalog
    assert "vorpal" in catalog

    # 2. Evaluate POST
    res_eval = client.post("/api/rules/evaluate-weapon-abilities", json={
        "weapon": {"name": "Rapier", "damage": "1d6", "crit": "18-20/x2", "cost_gp": 20},
        "base_enhancement": 1,
        "applied_abilities": ["frost", "keen"],
        "is_bane_active": False
    })
    assert res_eval.status_code == 200
    data = res_eval.json()
    assert data["total_effective_bonus"] == 3
    assert data["critical"] == "15-20/x2"
    assert "1d6 Soğuk (Cold)" in data["combined_damage_string"]
