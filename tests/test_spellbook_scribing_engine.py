"""
Unit Tests for PF1e Spellbook Scribing & Scroll Crafting Cost Engine
====================================================================
Verifies:
- 100-page spellbook capacity and volume calculation
- Scribing ink cost (Level^2 * 10 gp, 5 gp for Level 0)
- Spellcraft DC requirements (Decipher 20+L, Write 15+L)
- Scribe Scroll feat crafting cost and market pricing
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.spellbook_scribing import (
    calculate_spellbook_pages_and_cost,
    calculate_scroll_crafting_cost,
    extract_spell_level
)
from rules.calculators import PF1e_Calculator
from fastapi.testclient import TestClient
from app.main import app


def test_spellbook_mixed_levels_scribing():
    """Verify pages and gp cost for a wizard's initial spellbook."""
    spells = [
        {"name": "Detect Magic", "level": 0},
        {"name": "Read Magic", "level": 0},
        {"name": "Light", "level": 0},
        {"name": "Magic Missile", "level": 1},
        {"name": "Mage Armor", "level": 1},
        {"name": "Shield", "level": 1},
        {"name": "Color Spray", "level": 1},
        {"name": "Invisibility", "level": 2},
        {"name": "Mirror Image", "level": 2},
        {"name": "Fireball", "level": 3}
    ]

    res = calculate_spellbook_pages_and_cost(spells)

    # 3 Cantrips = 3 pages, 15 gp
    # 4 Level 1 = 4 pages, 40 gp
    # 2 Level 2 = 4 pages, 80 gp
    # 1 Level 3 = 3 pages, 90 gp
    # Total = 14 pages, 225 gp
    assert res["total_spells"] == 10
    assert res["total_pages_used"] == 14
    assert res["total_cost_gp"] == 225.0
    assert res["books_needed"] == 1
    assert res["percentage"] == 14.0
    assert res["is_overflow"] is False

    # Check Fireball breakdown
    fb = [s for s in res["spells_breakdown"] if s["name"] == "Fireball"][0]
    assert fb["pages"] == 3
    assert fb["cost_gp"] == 90.0
    assert fb["dc_write"] == 18 # 15 + 3
    assert fb["dc_decipher"] == 23 # 20 + 3
    assert fb["time_hours"] == 3.0


def test_spellbook_overflow_multiple_volumes():
    """Verify when total pages exceed 100, multiple books are calculated."""
    # 15 Level 8 spells = 120 pages
    spells = [{"name": f"High Spell {i}", "level": 8} for i in range(15)]
    res = calculate_spellbook_pages_and_cost(spells)

    assert res["total_pages_used"] == 120
    assert res["books_needed"] == 2
    assert res["is_overflow"] is True
    assert res["total_cost_gp"] == 15 * 640.0


def test_scroll_crafting_costs():
    """Verify Scribe Scroll market price and crafting cost formulas."""
    # Cantrip
    sc_0 = calculate_scroll_crafting_cost(spell_level=0, caster_level=1)
    assert sc_0["market_price_gp"] == 12.5
    assert sc_0["crafting_cost_gp"] == 6.25

    # Level 1 (CL 1): 1 * 1 * 25 = 25 gp market, 12.5 gp craft
    sc_1 = calculate_scroll_crafting_cost(spell_level=1, caster_level=1)
    assert sc_1["market_price_gp"] == 25.0
    assert sc_1["crafting_cost_gp"] == 12.5

    # Level 3 (CL 5): 3 * 5 * 25 = 375 gp market, 187.5 gp craft
    sc_3 = calculate_scroll_crafting_cost(spell_level=3, caster_level=5)
    assert sc_3["market_price_gp"] == 375.0
    assert sc_3["crafting_cost_gp"] == 187.5


def test_spellbook_scribing_backend_api():
    """Verify /api/rules/spellbook-scribing and /api/rules/scroll-crafting endpoints."""
    client = TestClient(app)

    # 1. Spellbook scribing
    res_book = client.post("/api/rules/spellbook-scribing", json={
        "spells": [{"name": "Haste", "level": 3}, {"name": "Fly", "level": 3}],
        "book_size": 100
    })
    assert res_book.status_code == 200
    data_b = res_book.json()
    assert data_b["total_pages_used"] == 6
    assert data_b["total_cost_gp"] == 180.0

    # 2. Scroll crafting
    res_scroll = client.post("/api/rules/scroll-crafting", json={
        "spell_level": 2,
        "caster_level": 3
    })
    assert res_scroll.status_code == 200
    data_s = res_scroll.json()
    assert data_s["market_price_gp"] == 150.0
    assert data_s["crafting_cost_gp"] == 75.0
