"""
Minimal, safe implementation of equipment comparison helpers.
This file replaces a previously corrupted/garbled implementation so the
project can be linted and imported. The functions here provide a small
but functional subset of the original API used elsewhere.
"""
from __future__ import annotations
import re
from typing import Any, Dict


def compare_equipment_items(item1: Dict[str, Any], item2: Dict[str, Any], item_type: str = "auto") -> Dict[str, Any]:
    """Compare two equipment items and return a summary dict.

    The returned dict has these keys:
    - differences: list of dicts describing differing fields
    - advantages_item1: list[str] describing why item1 may be preferable
    - advantages_item2: list[str] describing why item2 may be preferable

    This implementation is intentionally small and safe; it compares a few
    common fields (name, weight, cost, damage) and is resilient to missing
    keys and malformed values.
    """

    result = {
        "differences": [],
        "advantages_item1": [],
        "advantages_item2": [],
    }

    if not item1 or not item2:
        return result

    # Name
    name1 = str(item1.get("name", "")).strip()
    name2 = str(item2.get("name", "")).strip()
    if name1 and name2 and name1 != name2:
        result["differences"].append({"field": "name", "item1_value": name1, "item2_value": name2})

    # Weight (numeric comparison)
    try:
        w1 = float(item1.get("weight", 0) or 0)
    except Exception:
        w1 = 0.0
    try:
        w2 = float(item2.get("weight", 0) or 0)
    except Exception:
        w2 = 0.0
    if w1 != w2:
        result["differences"].append({"field": "weight", "item1_value": w1, "item2_value": w2})
        if w1 < w2:
            result["advantages_item1"].append("Lighter (better carry)")
        elif w2 < w1:
            result["advantages_item2"].append("Lighter (better carry)")

    # Cost (parse simple gp values like '10 gp' or numeric)
    c1 = _parse_gp_cost(item1.get("cost", "0"))
    c2 = _parse_gp_cost(item2.get("cost", "0"))
    if c1 != c2:
        result["differences"].append({"field": "cost", "item1_value": c1, "item2_value": c2})
        if c1 < c2:
            result["advantages_item1"].append("Cheaper")
        else:
            result["advantages_item2"].append("Cheaper")

    # Damage (basic numeric comparison using average when possible)
    dmg1 = str(item1.get("damage", ""))
    dmg2 = str(item2.get("damage", ""))
    if dmg1 or dmg2:
        score = _compare_damage(dmg1, dmg2)
        if score != 0:
            result["differences"].append({"field": "damage", "item1_value": dmg1, "item2_value": dmg2})
            if score > 0:
                result["advantages_item1"].append("Higher average damage")
            elif score < 0:
                result["advantages_item2"].append("Higher average damage")

    return result


def _parse_gp_cost(cost_val: Any) -> float:
    """Parse a cost value into a float number of gp.

    Accepts numeric values or strings like '10 gp', '1,000 gp', '2pp' (platinum = 10 gp)
    and returns a float. On error returns 0.0.
    """
    if cost_val is None:
        return 0.0
    if isinstance(cost_val, (int, float)):
        return float(cost_val)
    s = str(cost_val).lower().strip()
    # common currency abbreviations
    try:
        # remove commas
        s = s.replace(",", "")
        # platinum (pp) roughly 10 gp
        if s.endswith("pp"):
            return float(re.sub(r"[^0-9.]+", "", s)) * 10.0
        # gold
        if s.endswith("gp"):
            return float(re.sub(r"[^0-9.]+", "", s))
        # silver -> 0.1 gp
        if s.endswith("sp"):
            return float(re.sub(r"[^0-9.]+", "", s)) * 0.1
        # copper -> 0.01 gp
        if s.endswith("cp"):
            return float(re.sub(r"[^0-9.]+", "", s)) * 0.01
        # fallback: try to extract a number
        num = re.search(r"[0-9]+(?:\.[0-9]+)?", s)
        if num:
            return float(num.group(0))
    except Exception:
        pass
    return 0.0


def _compare_damage(dmg1: str, dmg2: str) -> int:
    """Return 1 if dmg1 > dmg2, -1 if dmg1 < dmg2, 0 if equal.

    This function extracts an approximate average value from strings like '1d8+2', '2d6', or '7'.
    """
    def avg_damage(s: str) -> float:
        if not s:
            return 0.0
        s = s.strip()
        # match XdY+Z
        m = re.search(r"(\d+)d(\d+)(?:\s*\+\s*(\d+))?", s)
        if m:
            count = int(m.group(1))
            size = int(m.group(2))
            bonus = int(m.group(3) or 0)
            return count * (size + 1) / 2.0 + bonus
        # numeric fallback
        m2 = re.search(r"(\d+(?:\.\d+)?)", s)
        if m2:
            return float(m2.group(1))
        return 0.0

    a1 = avg_damage(dmg1)
    a2 = avg_damage(dmg2)
    if a1 > a2:
        return 1
    if a1 < a2:
        return -1
    return 0






