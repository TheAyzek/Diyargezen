"""
Unit Tests for PF1e Alchemy & Magic Item Crafting Engine
========================================================
Verifies:
- Potion crafting costs, times, and Spellcraft DCs
- Magic item crafting costs, days, and missing prereq DCs
- Alchemist Mutagen stat modifications and duration scaling
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.alchemy_crafting import (
    calculate_potion_crafting,
    calculate_magic_item_crafting,
    calculate_mutagen_effects,
    get_crafting_catalog
)
from fastapi.testclient import TestClient
from app.main import app


def test_potion_crafting_formulas():
    """Verify level 1, level 2 and cantrip potion costs and DCs."""
    # Level 1 Cure Light Wounds (CL 1): 1 * 1 * 50 = 50 gp, Raw = 25 gp, 2 hours, DC 6
    p1 = calculate_potion_crafting("Cure Light Wounds", spell_level=1, caster_level=1)
    assert p1["market_price_gp"] == 50
    assert p1["raw_cost_gp"] == 25
    assert p1["crafting_time"] == "2 Saat"
    assert p1["spellcraft_dc"] == 6
    assert p1["is_valid"] is True

    # Level 2 Cure Moderate Wounds (CL 3): 2 * 3 * 50 = 300 gp, Raw = 150 gp, 1 day, DC 8
    p2 = calculate_potion_crafting("Cure Moderate Wounds", spell_level=2, caster_level=3)
    assert p2["market_price_gp"] == 300
    assert p2["raw_cost_gp"] == 150
    assert p2["crafting_time"] == "1 Gün"
    assert p2["spellcraft_dc"] == 8

    # Cantrip (Level 0): 25 gp * 1 = 25 gp, Raw = 12 gp
    p0 = calculate_potion_crafting("Light", spell_level=0, caster_level=1)
    assert p0["market_price_gp"] == 25
    assert p0["raw_cost_gp"] == 12

    # Level 4 spell warning
    p4 = calculate_potion_crafting("Stoneskin", spell_level=4, caster_level=7)
    assert p4["is_valid"] is False
    assert any("en fazla 3" in w for w in p4["warnings"])


def test_magic_item_crafting_formulas_and_missing_prereq_dc():
    """Verify Cloak of Resistance +2 crafting costs, days, and DC."""
    # Cloak of Resistance +2: Market 4000 gp, CL 6 -> Raw 2000 gp, 4 days, Base DC 11
    item = calculate_magic_item_crafting(
        item_name="Cloak of Resistance +2",
        item_type="wondrous",
        market_price_gp=4000,
        item_cl=6,
        missing_prereqs_count=0
    )
    assert item["raw_cost_gp"] == 2000
    assert item["crafting_days"] == 4
    assert item["base_spellcraft_dc"] == 11
    assert item["final_spellcraft_dc"] == 11

    # 1 Missing Prerequisite (+5 DC -> DC 16)
    item_missing = calculate_magic_item_crafting(
        item_name="Cloak of Resistance +2",
        item_type="wondrous",
        market_price_gp=4000,
        item_cl=6,
        missing_prereqs_count=1
    )
    assert item_missing["final_spellcraft_dc"] == 16


def test_alchemist_mutagen_scaling():
    """Verify Alchemist Mutagen stat modifications and duration."""
    # Level 5 Strength Mutagen: +4 Str, +2 Nat AC, -2 Int, 50 minutes
    m5 = calculate_mutagen_effects("strength", alchemist_level=5)
    assert m5["physical_bonus"] == {"Strength": 4}
    assert m5["mental_penalty"] == {"Intelligence": -2}
    assert m5["natural_armor_bonus"] == 2
    assert m5["duration_minutes"] == 50

    # Grand Mutagen at Level 16: +8 Str, +6 Dex, +4 Con, +6 Nat AC, 160 minutes
    grand = calculate_mutagen_effects("grand_mutagen", alchemist_level=16)
    assert grand["physical_bonus"]["Strength"] == 8
    assert grand["natural_armor_bonus"] == 6
    assert grand["duration_minutes"] == 160


def test_alchemy_crafting_backend_api():
    """Verify /api/rules/crafting-catalog, /api/rules/calculate-potion, /calculate-item-crafting, /evaluate-mutagen."""
    client = TestClient(app)

    # 1. Catalog
    res_cat = client.get("/api/rules/crafting-catalog")
    assert res_cat.status_code == 200
    assert "brew_potion" in res_cat.json()["crafting_feats"]

    # 2. Potion API
    res_pot = client.post("/api/rules/calculate-potion", json={
        "spell_name": "Invisibility",
        "spell_level": 2,
        "caster_level": 3
    })
    assert res_pot.status_code == 200
    assert res_pot.json()["market_price_gp"] == 300

    # 3. Mutagen API
    res_mut = client.post("/api/rules/evaluate-mutagen", json={
        "mutagen_type": "dexterity",
        "alchemist_level": 3
    })
    assert res_mut.status_code == 200
    assert res_mut.json()["physical_bonus"]["Dexterity"] == 4
