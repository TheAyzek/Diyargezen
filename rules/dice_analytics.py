"""
Pathfinder 1st Edition Advanced Dice & Point Buy Analytics Engine
=================================================================
References:
- PF1e Core Rulebook p. 15-16 (Determining Ability Scores, Table 1-1: Ability Score Point Costs)
- PF1e Core Rulebook p. 16 (Point Buy Fantasy Tiers)

Tiers:
- Low Fantasy: 10 Points
- Standard Fantasy: 15 Points
- High Fantasy: 20 Points
- Epic Fantasy: 25 Points
"""

import math
from typing import Dict, Any, List, Optional


POINT_BUY_COST_TABLE = {
    7: -4,
    8: -2,
    9: -1,
    10: 0,
    11: 1,
    12: 2,
    13: 3,
    14: 5,
    15: 7,
    16: 10,
    17: 13,
    18: 17,
}


def get_point_cost_for_score(score: int) -> int:
    """Returns point buy cost for a given base score (extrapolating outside 7-18)."""
    s = int(score)
    if s in POINT_BUY_COST_TABLE:
        return POINT_BUY_COST_TABLE[s]
    if s < 7:
        # Below 7: penalize additional -2 per point below 7
        return -4 - (7 - s) * 2
    # Above 18: +4 points per point above 18
    return 17 + (s - 18) * 4


def calculate_point_buy_equivalent(ability_scores: Dict[str, Any]) -> Dict[str, Any]:
    """Evaluates 6 ability scores to determine total point buy cost and fantasy tier."""
    STANDARD_ABILITIES = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]

    scores_cleaned = {}
    details = {}
    total_points = 0
    scores_list = []

    for ab in STANDARD_ABILITIES:
        val = 10
        for k, v in (ability_scores or {}).items():
            if str(k).lower().strip() == ab:
                try:
                    val = int(v)
                except (ValueError, TypeError):
                    val = 10
                break

        scores_cleaned[ab] = val
        cost = get_point_cost_for_score(val)
        mod = (val - 10) // 2
        total_points += cost
        scores_list.append(val)

        details[ab.title()] = {
            "score": val,
            "modifier": mod,
            "point_cost": cost
        }

    # Determine Fantasy Tier
    if total_points <= 10:
        tier_code = "low"
        tier_name = "Low Fantasy (Düşük Fantezi)"
        badge_color = "#38bdf8"
    elif total_points <= 15:
        tier_code = "standard"
        tier_name = "Standard Fantasy (Standart Fantezi)"
        badge_color = "#4ec9b0"
    elif total_points <= 20:
        tier_code = "high"
        tier_name = "High Fantasy (Yüksek Fantezi)"
        badge_color = "#ffd700"
    elif total_points <= 25:
        tier_code = "epic"
        tier_name = "Epic Fantasy (Epik Fantezi)"
        badge_color = "#a594ff"
    else:
        tier_code = "transcendent"
        tier_name = "Transcendent (Olağanüstü / Efsanevi)"
        badge_color = "#e94560"

    score_sum = sum(scores_list)
    score_mean = round(score_sum / len(scores_list), 2)
    score_min = min(scores_list)
    score_max = max(scores_list)

    # Standard deviation
    variance = sum((x - score_mean) ** 2 for x in scores_list) / len(scores_list)
    std_dev = round(math.sqrt(variance), 2)

    return {
        "total_points": total_points,
        "tier_code": tier_code,
        "tier_name": tier_name,
        "badge_color": badge_color,
        "total_score_sum": score_sum,
        "average_score": score_mean,
        "highest_score": score_max,
        "lowest_score": score_min,
        "std_deviation": std_dev,
        "details": details
    }


def get_dice_generation_stats() -> Dict[str, Any]:
    """Returns probabilistic distribution stats for common PF1e dice generation methods."""
    return {
        "4d6_drop_lowest": {
            "name": "4d6 Drop Lowest (PF1e Standart)",
            "mean": 12.24,
            "min": 3,
            "max": 18,
            "std_dev": 2.85,
            "average_sum": 73.47,
            "description": "4 adet altı yüzlü zar atılır, en düşük zar elenir."
        },
        "3d6_classic": {
            "name": "3d6 (Klasik / Hardcore)",
            "mean": 10.50,
            "min": 3,
            "max": 18,
            "std_dev": 2.96,
            "average_sum": 63.00,
            "description": "Doğrudan 3 adet altı yüzlü zar atılır."
        },
        "2d6_plus_6": {
            "name": "2d6 + 6 (Kahramanca / Heroic)",
            "mean": 13.00,
            "min": 8,
            "max": 18,
            "std_dev": 2.42,
            "average_sum": 78.00,
            "description": "2d6 atılıp üzerine 6 eklenir (Minimum 8, garanti ortalama üzeri)."
        },
        "4d6_drop_reroll_1": {
            "name": "4d6 Drop Lowest Reroll 1s (Cömert)",
            "mean": 13.43,
            "min": 6,
            "max": 18,
            "std_dev": 2.53,
            "average_sum": 80.58,
            "description": "4d6 atılır, 1'ler tekrar atılır, en düşük elenir."
        }
    }


def get_stat_array_templates() -> List[Dict[str, Any]]:
    """Returns official and balanced pre-built stat arrays for various point buy tiers."""
    return [
        {
            "name": "Standart Dizi (Standard Array)",
            "points": 15,
            "tier": "Standard Fantasy",
            "scores": [15, 14, 13, 12, 10, 8],
            "description": "CRB resmi dengeli 15 puan başlangıç dizilimi."
        },
        {
            "name": "Yüksek Fantezi - Dengeli (High Fantasy Balanced)",
            "points": 20,
            "tier": "High Fantasy",
            "scores": [16, 14, 14, 12, 10, 8],
            "description": "Güçlü bir ana stat ve dengeli ikincil statlar (20 Puan)."
        },
        {
            "name": "Yüksek Fantezi - Uzman (High Fantasy Specialist)",
            "points": 20,
            "tier": "High Fantasy",
            "scores": [17, 14, 12, 12, 10, 8],
            "description": "17 ana stat odaklı büyücü veya uzman dizilimi."
        },
        {
            "name": "Epik Fantezi - Dengeli (Epic Fantasy Balanced)",
            "points": 25,
            "tier": "Epic Fantasy",
            "scores": [17, 15, 14, 12, 10, 8],
            "description": "Geniş stat dağılımlı epik başlangıç (25 Puan)."
        },
        {
            "name": "Epik Fantezi - Güç Merkezi (Epic Powerhouse)",
            "points": 25,
            "tier": "Epic Fantasy",
            "scores": [18, 14, 14, 12, 10, 8],
            "description": "18 tavan stat ile başlayan epik güç dizilimi."
        },
        {
            "name": "Düşük Fantezi (Low Fantasy)",
            "points": 10,
            "tier": "Low Fantasy",
            "scores": [13, 12, 12, 11, 10, 8],
            "description": "Zorlu, mütevazı 10 puanlık macera dizilimi."
        }
    ]
