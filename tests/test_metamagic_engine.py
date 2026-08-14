"""
Unit Tests for PF1e Metamagic & Spell Slot Engine
=================================================
Verifies:
- Metamagic slot adjustments (Empower +2, Maximize +3, Quicken +4, etc.)
- Prepared vs Spontaneous casting times (Standard vs Full-Round vs Swift)
- Heighten Spell DC and level escalation
- 9th level slot overflow validation
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.metamagic_engine import (
    calculate_metamagic_spell,
    get_metamagic_catalog
)
from fastapi.testclient import TestClient
from app.main import app


def test_empowered_fireball_prepared_caster():
    """Verify Level 3 Fireball + Empower requires Level 5 slot and Standard Action."""
    spell = {
        "isim": "Fireball",
        "seviye": 3,
        "casting_time": "1 standard action"
    }

    res = calculate_metamagic_spell(spell, applied_metamagic=["empower"], caster_type="prepared", casting_mod=4)
    assert res["base_level"] == 3
    assert res["required_slot_level"] == 5
    assert res["total_level_adjustment"] == 2
    assert "Standart" in res["casting_time"] or "Standard" in res["casting_time"]
    assert res["effective_dc"] == 10 + 3 + 4  # DC remains based on base spell level 3 (17)
    assert res["is_valid"] is True


def test_quickened_magic_missile_swift_action():
    """Verify Level 1 Magic Missile + Quicken requires Level 5 slot and Swift Action."""
    spell = {
        "isim": "Magic Missile",
        "seviye": 1,
        "casting_time": "1 standard action"
    }

    res = calculate_metamagic_spell(spell, applied_metamagic=["quicken"], caster_type="prepared", casting_mod=3)
    assert res["required_slot_level"] == 5
    assert "Swift Action" in res["casting_time"]
    assert res["is_valid"] is True


def test_spontaneous_caster_full_round_action():
    """Verify Sorcerer applying Empower becomes Full-Round Action."""
    spell = {
        "isim": "Shocking Grasp",
        "seviye": 1,
        "casting_time": "1 standard action"
    }

    res = calculate_metamagic_spell(spell, applied_metamagic=["empower"], caster_type="sorcerer", casting_mod=3)
    assert res["required_slot_level"] == 3
    assert "Full-Round Action" in res["casting_time"]
    assert res["caster_type"] == "Spontaneous"


def test_heighten_spell_dc_escalation():
    """Verify Heighten Spell increases actual spell level and DC."""
    spell = {
        "isim": "Charm Person",
        "seviye": 1,
        "casting_time": "1 standard action"
    }

    # Heighten to 4th level
    res = calculate_metamagic_spell(
        spell,
        applied_metamagic=[{"key": "heighten", "target_level": 4}],
        caster_type="wizard",
        casting_mod=4
    )
    assert res["required_slot_level"] == 4
    assert res["effective_spell_level"] == 4
    # Heightened DC: 10 + 4 (effective lvl) + 4 (mod) = 18
    assert res["effective_dc"] == 18


def test_spell_slot_overflow_warning():
    """Verify exceeding Level 9 slot produces an overflow warning."""
    spell = {
        "isim": "Finger of Death",
        "seviye": 7
    }

    res = calculate_metamagic_spell(spell, applied_metamagic=["empower", "maximize"], caster_type="wizard")
    # 7 + 2 (empower) + 3 (maximize) = 12 > 9
    assert res["required_slot_level"] == 12
    assert res["is_valid"] is False
    assert any("tavanını aşıyor" in w for w in res["warnings"])


def test_metamagic_backend_api():
    """Verify /api/rules/metamagic-catalog and /api/rules/evaluate-metamagic."""
    client = TestClient(app)

    # 1. Catalog
    res_cat = client.get("/api/rules/metamagic-catalog")
    assert res_cat.status_code == 200
    catalog = res_cat.json()
    assert "empower" in catalog
    assert "quicken" in catalog

    # 2. Evaluate POST
    res_eval = client.post("/api/rules/evaluate-metamagic", json={
        "spell": {"name": "Cone of Cold", "level": 5},
        "applied_metamagic": ["extend"],
        "caster_type": "wizard",
        "casting_mod": 5
    })
    assert res_eval.status_code == 200
    data = res_eval.json()
    assert data["required_slot_level"] == 6
    assert data["is_valid"] is True
