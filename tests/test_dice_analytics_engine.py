"""
Unit Tests for PF1e Advanced Dice & Point Buy Analytics Engine
==============================================================
Verifies:
- Official PF1e Point Cost calculations (CRB Table 1-1)
- Fantasy Tier detection (Low, Standard, High, Epic, Transcendent)
- Probabilistic dice generation metrics (4d6 drop lowest, 3d6, 2d6+6)
- Pre-built stat array templates
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.dice_analytics import (
    calculate_point_buy_equivalent,
    get_dice_generation_stats,
    get_stat_array_templates,
    get_point_cost_for_score
)
from fastapi.testclient import TestClient
from app.main import app


def test_standard_array_point_buy_15():
    """Verify standard array [15, 14, 13, 12, 10, 8] computes strictly to 15 points."""
    abilities = {
        "strength": 15,
        "dexterity": 14,
        "constitution": 13,
        "intelligence": 12,
        "wisdom": 10,
        "charisma": 8
    }
    res = calculate_point_buy_equivalent(abilities)

    assert res["total_points"] == 15
    assert res["tier_code"] == "standard"
    assert res["total_score_sum"] == 72
    assert res["average_score"] == 12.0
    assert res["highest_score"] == 15
    assert res["lowest_score"] == 8


def test_high_and_epic_fantasy_tiers():
    """Verify 20 pts (High Fantasy) and 25 pts (Epic Fantasy) evaluation."""
    # 20 Points High Fantasy [16, 14, 14, 12, 10, 8] -> 10 + 5 + 5 + 2 + 0 - 2 = 20
    high_ab = {
        "strength": 16, "dexterity": 14, "constitution": 14,
        "intelligence": 12, "wisdom": 10, "charisma": 8
    }
    res_high = calculate_point_buy_equivalent(high_ab)
    assert res_high["total_points"] == 20
    assert res_high["tier_code"] == "high"

    # 25 Points Epic Fantasy [17, 15, 14, 12, 10, 8] -> 13 + 7 + 5 + 2 + 0 - 2 = 25
    epic_ab = {
        "strength": 17, "dexterity": 15, "constitution": 14,
        "intelligence": 12, "wisdom": 10, "charisma": 8
    }
    res_epic = calculate_point_buy_equivalent(epic_ab)
    assert res_epic["total_points"] == 25
    assert res_epic["tier_code"] == "epic"


def test_dice_generation_stats_and_templates():
    """Verify dice probability averages and template structures."""
    stats = get_dice_generation_stats()
    assert stats["4d6_drop_lowest"]["mean"] == 12.24
    assert stats["3d6_classic"]["mean"] == 10.50
    assert stats["2d6_plus_6"]["mean"] == 13.00

    templates = get_stat_array_templates()
    assert len(templates) >= 5
    assert any(t["points"] == 15 for t in templates)
    assert any(t["points"] == 20 for t in templates)
    assert any(t["points"] == 25 for t in templates)


def test_point_buy_backend_api():
    """Verify /api/rules/point-buy-eval and /api/rules/dice-arrays endpoints."""
    client = TestClient(app)

    # 1. Point Buy Eval
    res_eval = client.post("/api/rules/point-buy-eval", json={
        "ability_scores": {
            "strength": 16, "dexterity": 14, "constitution": 14,
            "intelligence": 12, "wisdom": 10, "charisma": 8
        }
    })
    assert res_eval.status_code == 200
    data_e = res_eval.json()
    assert data_e["total_points"] == 20
    assert data_e["tier_code"] == "high"

    # 2. Dice Arrays & Stats
    res_arrays = client.get("/api/rules/dice-arrays")
    assert res_arrays.status_code == 200
    data_a = res_arrays.json()
    assert "templates" in data_a
    assert "dice_stats" in data_a
