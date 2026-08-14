"""
Unit Tests for PF1e Two-Weapon Fighting (TWF) Attack Engine
===========================================================
Verifies:
- Light weapon categorization (Dagger, Shortsword, Kukri vs Longsword)
- Table 8-10 TWF penalties (No feat vs TWF feat, Light vs Normal off-hand)
- Off-hand damage calculation (Half STR vs Double Slice full STR)
- Iterative attacks with Improved and Greater TWF
- Backend API endpoints
"""

import sys
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "web" / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

import pytest
from rules.two_weapon_fighting import (
    is_light_weapon,
    calculate_twf_penalties,
    calculate_twf_attack_profile
)
from fastapi.testclient import TestClient
from app.main import app


def test_light_weapon_categorization():
    """Verify light weapon identification."""
    assert is_light_weapon("Dagger") is True
    assert is_light_weapon("Shortsword") is True
    assert is_light_weapon("Kukri") is True
    assert is_light_weapon("El Baltası") is True
    assert is_light_weapon("Longsword") is False
    assert is_light_weapon("Greatsword") is False


def test_twf_penalties_table_8_10():
    """Verify Table 8-10 penalty matrix."""
    # 1. No Feat + Light Off-hand -> -4 / -8
    assert calculate_twf_penalties(is_offhand_light=True, has_twf_feat=False) == (-4, -8)

    # 2. No Feat + Normal Off-hand -> -6 / -10
    assert calculate_twf_penalties(is_offhand_light=False, has_twf_feat=False) == (-6, -10)

    # 3. TWF Feat + Light Off-hand -> -2 / -2
    assert calculate_twf_penalties(is_offhand_light=True, has_twf_feat=True) == (-2, -2)

    # 4. TWF Feat + Normal Off-hand -> -4 / -4
    assert calculate_twf_penalties(is_offhand_light=False, has_twf_feat=True) == (-4, -4)


def test_twf_damage_and_double_slice():
    """Verify primary vs off-hand damage and Double Slice benefit."""
    primary = {"name": "Longsword", "damage": "1d8", "enhancement": 0}
    offhand = {"name": "Shortsword", "damage": "1d6", "enhancement": 0}

    # Standard (Half STR to off-hand: +3 // 2 = +1)
    res_std = calculate_twf_attack_profile(
        bab=1, str_mod=3, dex_mod=2,
        primary_weapon=primary, offhand_weapon=offhand,
        feats=["Two-Weapon Fighting"]
    )
    assert res_std["primary_damage_string"] == "1d8+3"
    assert res_std["offhand_damage_string"] == "1d6+1"
    assert res_std["primary_penalty"] == -2
    assert res_std["offhand_penalty"] == -2

    # Double Slice (Full STR to off-hand: +3)
    res_ds = calculate_twf_attack_profile(
        bab=1, str_mod=3, dex_mod=2,
        primary_weapon=primary, offhand_weapon=offhand,
        feats=["Two-Weapon Fighting", "Double Slice"]
    )
    assert res_ds["offhand_damage_string"] == "1d6+3"


def test_iterative_attacks_improved_and_greater_twf():
    """Verify Level 11 Fighter full attack sequence (3 primary + 3 off-hand)."""
    primary = {"name": "Longsword", "damage": "1d8", "enhancement": 1}
    offhand = {"name": "Shortsword", "damage": "1d6", "enhancement": 1}

    res = calculate_twf_attack_profile(
        bab=11, str_mod=4, dex_mod=3,
        primary_weapon=primary, offhand_weapon=offhand,
        feats=["Two-Weapon Fighting", "Improved Two-Weapon Fighting", "Greater Two-Weapon Fighting", "Double Slice"]
    )

    # Primary: BAB 11, 6, 1 -> +4 STR -2 TWF +1 ENH = +14 / +9 / +4
    assert res["primary_attacks"] == [14, 9, 4]
    # Off-hand: BAB 11, 6, 1 -> +4 STR -2 TWF +1 ENH = +14 / +9 / +4
    assert res["offhand_attacks"] == [14, 9, 4]
    assert "+14/+9/+4" in res["primary_attack_string"]
    assert "+14/+9/+4" in res["offhand_attack_string"]


def test_twf_backend_api():
    """Verify /api/rules/evaluate-twf endpoint."""
    client = TestClient(app)

    res = client.post("/api/rules/evaluate-twf", json={
        "bab": 6,
        "str_mod": 3,
        "dex_mod": 2,
        "primary_weapon": {"name": "Scimitar", "damage": "1d6"},
        "offhand_weapon": {"name": "Dagger", "damage": "1d4"},
        "feats": ["Two-Weapon Fighting", "Improved Two-Weapon Fighting"]
    })

    assert res.status_code == 200
    data = res.json()
    assert len(data["primary_attacks"]) == 2 # BAB 6, 1
    assert len(data["offhand_attacks"]) == 2 # BAB 6, 1 (ITWF)
    assert "Ana El" in data["full_attack_summary"]
