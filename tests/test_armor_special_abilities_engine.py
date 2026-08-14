"""
Unit Tests for PF1e Armor & Shield Special Abilities Engine
===========================================================
Verifies:
- Fortification critical hit & sneak attack negation percentages (25%/50%/75%)
- Skill bonus buffs (Shadow +5 Stealth, Slick +5 Escape Artist)
- Animated shield floating defense (Hands free)
- Spell Resistance and Energy Resistance
- Effective bonus caps (+10 max) and GP pricing
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.armor_special_abilities import (
    calculate_armor_magical_properties,
    get_armor_abilities_catalog
)
from fastapi.testclient import TestClient
from app.main import app


def test_breastplate_light_fortification():
    """Verify +1 Light Fortification Breastplate AC and 25% crit negation."""
    armor = {"name": "Breastplate", "ac_bonus": 6, "cost_gp": 200, "is_shield": False}
    res = calculate_armor_magical_properties(armor, base_enhancement=1, applied_abilities=["fortification_light"])

    assert res["total_ac_bonus"] == 7 # 6 + 1
    assert res["total_effective_bonus"] == 2 # 1 enh + 1 light fort
    assert res["crit_negation_pct"] == 25
    assert res["market_price_gp"] == (4 * 1000) + 150 + 200 # 4350 gp
    assert res["is_valid"] is True


def test_shadow_chain_shirt():
    """Verify +2 Shadow Chain Shirt grants +5 Stealth."""
    armor = {"name": "Chain Shirt", "ac_bonus": 4, "cost_gp": 100, "is_shield": False}
    res = calculate_armor_magical_properties(armor, base_enhancement=2, applied_abilities=["shadow"])

    assert res["total_ac_bonus"] == 6 # 4 + 2
    assert res["skill_bonuses"]["Stealth"] == 5
    # (2^2 * 1000) + 150 + 100 + 3750 = 8000 gp
    assert res["market_price_gp"] == 8000


def test_animated_heavy_shield():
    """Verify +1 Animated Heavy Shield floats and provides +3 Shield AC."""
    shield = {"name": "Heavy Steel Shield", "ac_bonus": 2, "cost_gp": 20, "is_shield": True}
    res = calculate_armor_magical_properties(shield, base_enhancement=1, applied_abilities=["animated"])

    assert res["total_ac_bonus"] == 3 # 2 + 1
    assert res["total_effective_bonus"] == 3 # 1 + 2
    assert res["is_animated"] is True
    # (3^2 * 1000) + 150 + 20 = 9170 gp
    assert res["market_price_gp"] == 9170


def test_spell_resistance_and_energy_resistance():
    """Verify SR 15 and Energy Resistance properties."""
    armor = {"name": "Full Plate", "ac_bonus": 9, "cost_gp": 1500, "is_shield": False}
    res = calculate_armor_magical_properties(
        armor,
        base_enhancement=1,
        applied_abilities=["spell_resistance_15", "energy_resistance"]
    )

    assert res["spell_resistance"] == 15
    assert res["energy_resistance"] == 10
    assert res["total_effective_bonus"] == 4 # 1 + 3


def test_armor_rules_caps_and_validation():
    """Verify +0 armor warning and +10 bonus cap warning."""
    armor = {"name": "Leather Armor", "ac_bonus": 2, "cost_gp": 10}

    # Ability without +1 base enhancement
    res_no_enh = calculate_armor_magical_properties(armor, base_enhancement=0, applied_abilities=["glamered"])
    assert res_no_enh["is_valid"] is False
    assert any("en az +1" in w for w in res_no_enh["warnings"])

    # Over +10 effective bonus
    res_over = calculate_armor_magical_properties(
        armor,
        base_enhancement=5,
        applied_abilities=["fortification_heavy", "spell_resistance_19"] # 5 + 5 + 5 = 15 > 10
    )
    assert res_over["is_valid"] is False
    assert any("+10 tavanını aşıyor" in w for w in res_over["warnings"])


def test_armor_abilities_backend_api():
    """Verify /api/rules/armor-abilities-catalog and /api/rules/evaluate-armor-abilities."""
    client = TestClient(app)

    # 1. Catalog
    res_cat = client.get("/api/rules/armor-abilities-catalog")
    assert res_cat.status_code == 200
    catalog = res_cat.json()["abilities"]
    assert "fortification_light" in catalog
    assert "animated" in catalog

    # 2. Evaluate POST
    res_eval = client.post("/api/rules/evaluate-armor-abilities", json={
        "armor": {"name": "Banded Mail", "ac_bonus": 7, "cost_gp": 250},
        "base_enhancement": 1,
        "applied_abilities": ["slick"]
    })
    assert res_eval.status_code == 200
    data = res_eval.json()
    assert data["total_ac_bonus"] == 8
    assert data["skill_bonuses"]["Escape Artist"] == 5
