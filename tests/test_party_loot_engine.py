"""
Unit Tests for PF1e Party Loot & Treasure Splitter Engine
=========================================================
Verifies:
- Currency conversion math (PP, GP, SP, CP)
- Liquid treasure calculation (Coins + Gems & Art)
- Party member share splitting and Party Fund allocation
- Leftover coin distribution
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.party_loot_engine import (
    convert_currency_to_gp,
    convert_gp_to_optimal_coins,
    calculate_party_loot_split
)
from fastapi.testclient import TestClient
from app.main import app


def test_currency_conversion_math():
    """Verify PP, GP, SP, CP conversions."""
    coins = {"pp": 10, "gp": 500, "sp": 200, "cp": 50}
    # 10*10 (100) + 500 + 20 + 0.50 = 620.50 GP
    assert convert_currency_to_gp(coins) == 620.50

    # Optimal coin packing
    opt = convert_gp_to_optimal_coins(125.75)
    assert opt["pp"] == 12
    assert opt["gp"] == 5
    assert opt["sp"] == 7
    assert opt["cp"] == 5


def test_party_loot_split_with_party_fund():
    """Verify 4 players + 1 Party Fund share for 1500 GP."""
    coins = {"gp": 1000}
    gems = [{"name": "Ruby", "value_gp": 250, "qty": 2}] # 500 GP
    members = ["Valeros", "Seoni", "Kyra", "Merisiel"]

    res = calculate_party_loot_split(
        coins=coins,
        gems_art=gems,
        party_members=members,
        include_party_fund=True
    )

    assert res["total_shares"] == 5 # 4 players + 1 fund
    assert res["total_liquid_gp"] == 1500.0
    assert res["gp_per_member"] == 300
    assert res["party_fund_gp"] == 300
    assert len(res["member_shares"]) == 4


def test_party_loot_split_with_leftovers():
    """Verify non-divisible amounts correctly credit leftover to party fund."""
    coins = {"gp": 1003}
    members = ["A", "B", "C", "D"]

    res = calculate_party_loot_split(
        coins=coins,
        party_members=members,
        include_party_fund=False # 4 shares
    )

    assert res["total_shares"] == 4
    assert res["gp_per_member"] == 250
    assert res["leftover_coins_gp"] == 3.0
    assert res["party_fund_gp"] == 3.0 # leftovers go to fund


def test_party_loot_backend_api():
    """Verify /api/rules/split-party-loot endpoint."""
    client = TestClient(app)

    res = client.post("/api/rules/split-party-loot", json={
        "coins": {"pp": 5, "gp": 200, "sp": 50, "cp": 0},
        "gems_art": [{"name": "Diamond", "value_gp": 500, "qty": 1}],
        "items": [{"name": "+1 Shield", "value_gp": 1170, "qty": 1, "claimed_by": "Fighter"}],
        "party_members": ["Fighter", "Wizard", "Cleric"],
        "include_party_fund": True
    })

    assert res.status_code == 200
    data = res.json()
    assert data["total_shares"] == 4
    assert data["total_loot_value_gp"] > 1500
