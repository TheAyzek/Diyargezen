"""
Pathfinder 1st Edition Alignment & Class Restrictions Engine
============================================================
References:
- PF1e Core Rulebook Chapter 3 (Alignments: Table 3-2 & p. 166-167)
- PF1e Core Rulebook Chapter 4 (Class Alignment Restrictions)
- Advanced Player's Guide (Antipaladin, Inquisitor)

Rules:
- Paladin: Must be Lawful Good (LG).
- Antipaladin: Must be Chaotic Evil (CE).
- Monk: Must be Lawful (LG, LN, LE).
- Barbarian: Must be Non-Lawful (NG, CG, TN, CN, NE, CE).
- Druid: Must be Neutral on at least one axis (NG, LN, TN, CN, NE).
- Cleric & Inquisitor: Must be within one step of their deity's alignment.
"""

from typing import Dict, Any, List, Optional, Tuple


ALIGNMENT_GRID: Dict[str, Tuple[int, int]] = {
    "LG": (0, 0), "NG": (1, 0), "CG": (2, 0),
    "LN": (0, 1), "TN": (1, 1), "CN": (2, 1),
    "LE": (0, 2), "NE": (1, 2), "CE": (2, 2)
}


DEITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "iomedae": {"name": "Iomedae", "alignment": "LG", "title": "The Inheritor"},
    "torag": {"name": "Torag", "alignment": "LG", "title": "Father of Creation"},
    "sarenrae": {"name": "Sarenrae", "alignment": "NG", "title": "The Dawnflower"},
    "shelyn": {"name": "Shelyn", "alignment": "NG", "title": "The Eternal Rose"},
    "desna": {"name": "Desna", "alignment": "CG", "title": "Song of the Spheres"},
    "cayden cailean": {"name": "Cayden Cailean", "alignment": "CG", "title": "The Accidental God"},
    "abadar": {"name": "Abadar", "alignment": "LN", "title": "Master of the First Vault"},
    "irori": {"name": "Irori", "alignment": "LN", "title": "Master of Masters"},
    "pharasma": {"name": "Pharasma", "alignment": "TN", "title": "Lady of Graves"},
    "gozreh": {"name": "Gozreh", "alignment": "TN", "title": "The Wind and the Waves"},
    "nethys": {"name": "Nethys", "alignment": "TN", "title": "The All-Seeing Eye"},
    "gorum": {"name": "Gorum", "alignment": "CN", "title": "Our Lord in Iron"},
    "calistria": {"name": "Calistria", "alignment": "CN", "title": "The Savored Sting"},
    "asmodeus": {"name": "Asmodeus", "alignment": "LE", "title": "Prince of Darkness"},
    "zon-kuthon": {"name": "Zon-Kuthon", "alignment": "LE", "title": "The Midnight Lord"},
    "urgathoa": {"name": "Urgathoa", "alignment": "NE", "title": "The Pallid Princess"},
    "norgorber": {"name": "Norgorber", "alignment": "NE", "title": "The Reaper of Reputation"},
    "rovagug": {"name": "Rovagug", "alignment": "CE", "title": "The Rough Beast"},
    "lamashtu": {"name": "Lamashtu", "alignment": "CE", "title": "Mother of Monsters"}
}


CLASS_ALIGNMENT_RULES: Dict[str, Dict[str, Any]] = {
    "paladin": {
        "allowed": ["LG"],
        "message": "Paladinler resmi kurallara göre yalnızca Lawful Good (LG) hizalanışında olabilirler."
    },
    "antipaladin": {
        "allowed": ["CE"],
        "message": "Antipaladinler resmi kurallara göre yalnızca Chaotic Evil (CE) hizalanışında olabilirler."
    },
    "monk": {
        "allowed": ["LG", "LN", "LE"],
        "message": "Keşişler (Monk) katı içsel disiplinleri nedeniyle Lawful (LG, LN, LE) olmak zorundadır."
    },
    "barbarian": {
        "allowed": ["NG", "CG", "TN", "CN", "NE", "CE"],
        "message": "Barbarlar içlerindeki kontrolsüz öfke nedeniyle Non-Lawful olmak zorundadır (Lawful olamazlar)."
    },
    "druid": {
        "allowed": ["NG", "LN", "TN", "CN", "NE"],
        "message": "Druidler doğanın tarafsız dengesini korumak için en az bir eksende Neutral (NG, LN, TN, CN, NE) olmak zorundadır."
    }
}


def is_within_one_step(align1: str, align2: str) -> bool:
    """
    Checks if two alignments are within 1 step (orthogonal or identical) on the 3x3 alignment grid.
    """
    a1 = (align1 or "").upper().strip()
    a2 = (align2 or "").upper().strip()

    if a1 not in ALIGNMENT_GRID or a2 not in ALIGNMENT_GRID:
        return True # fallback permissive

    x1, y1 = ALIGNMENT_GRID[a1]
    x2, y2 = ALIGNMENT_GRID[a2]

    # In Pathfinder 1e, 1 step means: delta_x + delta_y <= 1 (e.g. NG -> LG, CG, TN, NG are all 1 step or identical)
    return (abs(x1 - x2) + abs(y1 - y2)) <= 1


def get_allowed_alignments_for_deity(deity_alignment: str) -> List[str]:
    """Returns all alignments within 1 step of deity's alignment."""
    d_align = (deity_alignment or "").upper().strip()
    if d_align not in ALIGNMENT_GRID:
        return list(ALIGNMENT_GRID.keys())

    allowed = []
    for align in ALIGNMENT_GRID.keys():
        if is_within_one_step(align, d_align):
            allowed.append(align)
    return allowed


def validate_character_alignment(
    char_class: str = "Fighter",
    alignment: str = "TN",
    deity_name: str = "",
    archetype: str = ""
) -> Dict[str, Any]:
    """
    Validates character alignment against class rules and deity one-step rule.
    Returns status, allowed alignments list, and soft-block warnings.
    """
    c_class = (char_class or "Fighter").lower().strip()
    c_align = (alignment or "TN").upper().strip()
    d_name = (deity_name or "").lower().strip()

    warnings = []
    allowed_alignments = list(ALIGNMENT_GRID.keys())

    # 1. Class Specific Alignment Rule
    if c_class in CLASS_ALIGNMENT_RULES:
        rule = CLASS_ALIGNMENT_RULES[c_class]
        allowed_alignments = rule["allowed"]
        if c_align not in allowed_alignments:
            warnings.append(rule["message"])

    # 2. Cleric / Inquisitor Deity One-Step Rule
    if c_class in ["cleric", "inquisitor", "rahip"]:
        deity_info = None
        for k, v in DEITIES_REGISTRY.items():
            if k in d_name or d_name in k:
                deity_info = v
                break

        if deity_info:
            d_align = deity_info["alignment"]
            deity_allowed = get_allowed_alignments_for_deity(d_align)
            
            # Intersection with existing class allowed
            allowed_alignments = [a for a in allowed_alignments if a in deity_allowed]

            if not is_within_one_step(c_align, d_align):
                warnings.append(
                    f"{c_class.capitalize()} sınıfı, tapındığı tanrının ({deity_info['name']} - {d_align}) "
                    f"hizalanışından en fazla 1 adım uzaklıkta olabilir (İzin verilenler: {', '.join(deity_allowed)})."
                )

    is_valid = len(warnings) == 0

    return {
        "class": char_class,
        "alignment": c_align,
        "deity": deity_name,
        "is_valid": is_valid,
        "allowed_alignments": allowed_alignments,
        "warnings": warnings,
        "gm_override_allowed": True
    }


def get_all_alignment_rules() -> Dict[str, Any]:
    """Returns complete catalog of class alignment restrictions and deities."""
    return {
        "class_rules": CLASS_ALIGNMENT_RULES,
        "deities": DEITIES_REGISTRY,
        "all_alignments": list(ALIGNMENT_GRID.keys())
    }
