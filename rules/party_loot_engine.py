"""
Pathfinder 1st Edition Party Loot & Treasure Splitter Engine
============================================================
References:
- PF1e Core Rulebook Chapter 15 (Currency: Copper, Silver, Gold, Platinum)

Conversions:
- 1 PP = 10 GP
- 1 GP = 10 SP = 100 CP
"""

import math
from typing import Dict, Any, List, Optional


def convert_currency_to_gp(coins: Dict[str, Any]) -> float:
    """Converts mixed coin quantities (PP, GP, SP, CP) into total GP value."""
    pp = int(coins.get("pp", 0) or 0)
    gp = int(coins.get("gp", 0) or 0)
    sp = int(coins.get("sp", 0) or 0)
    cp = int(coins.get("cp", 0) or 0)

    total_gp = (pp * 10) + gp + (sp / 10.0) + (cp / 100.0)
    return round(total_gp, 2)


def convert_gp_to_optimal_coins(gp_amount: float) -> Dict[str, int]:
    """Converts a total GP value into optimal PP, GP, SP, CP distribution."""
    total_cp = int(round(gp_amount * 100))

    pp = total_cp // 1000
    remainder = total_cp % 1000

    gp = remainder // 100
    remainder = remainder % 100

    sp = remainder // 10
    cp = remainder % 10

    return {
        "pp": pp,
        "gp": gp,
        "sp": sp,
        "cp": cp
    }


def calculate_party_loot_split(
    coins: Dict[str, Any],
    gems_art: Optional[List[Dict[str, Any]]] = None,
    items: Optional[List[Dict[str, Any]]] = None,
    party_members: Optional[List[str]] = None,
    include_party_fund: bool = True
) -> Dict[str, Any]:
    """
    Calculates fair treasure distribution among party members plus common party fund.
    """
    members = party_members or ["Oyuncu 1", "Oyuncu 2", "Oyuncu 3", "Oyuncu 4"]
    member_count = max(1, len(members))

    gems = gems_art or []
    gear_items = items or []

    # 1. Total Coin Value
    coin_gp = convert_currency_to_gp(coins)

    # 2. Total Gems & Art Value
    gems_gp = 0.0
    for g in gems:
        qty = int(g.get("qty", 1) or 1)
        val = float(g.get("value_gp", 0) or 0)
        gems_gp += qty * val

    # 3. Total Magic Items / Equipment Value
    items_gp = 0.0
    for it in gear_items:
        qty = int(it.get("qty", 1) or 1)
        val = float(it.get("value_gp", 0) or 0)
        items_gp += qty * val

    total_liquid_gp = round(coin_gp + gems_gp, 2)
    total_overall_gp = round(total_liquid_gp + items_gp, 2)

    # 4. Shares calculation
    shares_count = member_count + (1 if include_party_fund else 0)

    # Split liquid wealth
    gp_per_share = math.floor(total_liquid_gp / shares_count)
    total_distributed = gp_per_share * shares_count
    leftover_gp = round(total_liquid_gp - total_distributed, 2)

    party_fund_gp = (gp_per_share if include_party_fund else 0) + leftover_gp

    # 5. Member breakdown
    member_shares = []
    for m in members:
        # Check claimed items by this member
        claimed = [it for it in gear_items if str(it.get("claimed_by", "")).lower() == m.lower()]
        member_shares.append({
            "member_name": m,
            "cash_gp": gp_per_share,
            "claimed_items": claimed
        })

    unclaimed_items = [it for it in gear_items if not it.get("claimed_by")]

    return {
        "party_size": member_count,
        "include_party_fund": include_party_fund,
        "total_shares": shares_count,
        "coin_value_gp": coin_gp,
        "gems_value_gp": round(gems_gp, 2),
        "total_liquid_gp": total_liquid_gp,
        "total_item_value_gp": round(items_gp, 2),
        "total_loot_value_gp": total_overall_gp,
        "gp_per_member": gp_per_share,
        "party_fund_gp": round(party_fund_gp, 2),
        "leftover_coins_gp": leftover_gp,
        "member_shares": member_shares,
        "unclaimed_items": unclaimed_items
    }
