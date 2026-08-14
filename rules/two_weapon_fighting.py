"""
Pathfinder 1st Edition Two-Weapon Fighting & Off-Hand Attack Engine
===================================================================
References:
- PF1e Core Rulebook Chapter 8 (Combat: Table 8-10: Two-Weapon Fighting Penalties, p. 202)
- PF1e Core Rulebook Chapter 5 (Feats: Two-Weapon Fighting, Double Slice, Improved TWF, Greater TWF)

Penalties (Table 8-10):
- Normal (No Feat): Primary -6, Off-Hand -10 (or -4 / -8 if off-hand is light)
- With Two-Weapon Fighting Feat: Primary -4, Off-Hand -4 (or -2 / -2 if off-hand is light)

Damage:
- Primary Hand: Full STR modifier (+1.0x STR)
- Off-Hand: Half STR modifier (+0.5x STR, round down)
- Double Slice Feat: Full STR modifier to Off-Hand (+1.0x STR)

Iterative Off-Hand Attacks:
- Base: 1 off-hand attack at full BAB
- Improved Two-Weapon Fighting (BAB +6, Dex 17): 2nd off-hand attack at BAB - 5
- Greater Two-Weapon Fighting (BAB +11, Dex 19): 3rd off-hand attack at BAB - 10
"""

from typing import Dict, Any, List, Optional, Tuple


LIGHT_WEAPONS_SET = {
    "dagger", "hançer",
    "shortsword", "kısa kılıç", "short sword",
    "kukri",
    "light mace", "hafif gürz",
    "handaxe", "el baltası",
    "sickle", "orak",
    "kama",
    "nunchaku",
    "sai",
    "siangham",
    "spiked gauntlet", "çivili eldiven",
    "cestus",
    "claw", "pençe",
    "punching dagger",
    "sap", "cop",
    "starknife", "yıldız bıçak",
    "light hammer", "hafif çekiç",
    "whip", "kırbaç",
    "light pick", "hafif kazma",
    "unarmed strike", "silahsız vuruş"
}


def is_light_weapon(weapon_name: str, weapon_type: str = "") -> bool:
    """Checks whether a weapon qualifies as a Light weapon."""
    w_name = str(weapon_name or "").lower().strip()
    w_type = str(weapon_type or "").lower().strip()

    if "light" in w_type or "hafif" in w_type:
        return True

    for lw in LIGHT_WEAPONS_SET:
        if lw in w_name:
            return True

    return False


def calculate_twf_penalties(is_offhand_light: bool, has_twf_feat: bool) -> Tuple[int, int]:
    """Calculates primary and off-hand attack roll penalties."""
    if has_twf_feat:
        return (-2, -2) if is_offhand_light else (-4, -4)
    else:
        return (-4, -8) if is_offhand_light else (-6, -10)


def calculate_twf_attack_profile(
    bab: int = 1,
    str_mod: int = 0,
    dex_mod: int = 0,
    primary_weapon: Optional[Dict[str, Any]] = None,
    offhand_weapon: Optional[Dict[str, Any]] = None,
    feats: Optional[List[Any]] = None,
    is_weapon_finesse: bool = False
) -> Dict[str, Any]:
    """
    Calculates complete primary and off-hand iterative attacks, attack bonuses, damage, and formatted full attack strings.
    """
    p_wep = primary_weapon or {"name": "Longsword", "damage": "1d8", "crit": "19-20/x2", "enhancement": 0}
    o_wep = offhand_weapon or {"name": "Shortsword", "damage": "1d6", "crit": "19-20/x2", "enhancement": 0}

    # Normalize feats list
    feat_list = []
    if feats:
        for f in feats:
            f_name = f.get("isim") or f.get("name") if isinstance(f, dict) else str(f)
            feat_list.append(str(f_name).lower().strip())

    has_twf = any("two-weapon fighting" in f or "iki silahla dövüş" in f for f in feat_list)
    has_double_slice = any("double slice" in f or "çift dilim" in f for f in feat_list)
    has_itwf = any("improved two-weapon fighting" in f or "gelişmiş iki silah" in f for f in feat_list)
    has_gtwf = any("greater two-weapon fighting" in f or "üstün iki silah" in f for f in feat_list)

    # Check if off-hand weapon is light
    o_is_light = is_light_weapon(o_wep.get("name", ""), o_wep.get("type", ""))

    # Calculate penalties (Table 8-10)
    p_penalty, o_penalty = calculate_twf_penalties(o_is_light, has_twf)

    # Stat mod for attack rolls
    p_is_light = is_light_weapon(p_wep.get("name", ""), p_wep.get("type", ""))
    p_atk_stat = dex_mod if (is_weapon_finesse and p_is_light) else str_mod
    o_atk_stat = dex_mod if (is_weapon_finesse and o_is_light) else str_mod

    p_enh = int(p_wep.get("enhancement", 0) or 0)
    o_enh = int(o_wep.get("enhancement", 0) or 0)

    # 1. Primary Hand Iterative Attacks
    p_attacks = []
    curr_bab = bab
    while curr_bab > 0:
        total_p_atk = curr_bab + p_atk_stat + p_penalty + p_enh
        p_attacks.append(total_p_atk)
        curr_bab -= 5

    # 2. Off-Hand Attacks
    o_attacks = []
    # 1st off-hand attack (full BAB)
    o_attacks.append(bab + o_atk_stat + o_penalty + o_enh)

    # 2nd off-hand attack (Improved TWF at BAB - 5)
    if has_itwf and bab >= 6:
        o_attacks.append((bab - 5) + o_atk_stat + o_penalty + o_enh)

    # 3rd off-hand attack (Greater TWF at BAB - 10)
    if has_gtwf and bab >= 11:
        o_attacks.append((bab - 10) + o_atk_stat + o_penalty + o_enh)

    # 3. Damage Modifiers
    p_dmg_mod = str_mod + p_enh
    if str_mod < 0:
        o_dmg_mod = str_mod + o_enh # Negative STR applies fully to off-hand
    else:
        o_str_contribution = str_mod if has_double_slice else (str_mod // 2)
        o_dmg_mod = o_str_contribution + o_enh

    # 4. Formatted Strings
    p_atk_str = "/".join([f"+{a}" if a >= 0 else str(a) for a in p_attacks])
    o_atk_str = "/".join([f"+{a}" if a >= 0 else str(a) for a in o_attacks])

    p_dmg_str = f"{p_wep.get('damage', '1d8')}{'+' + str(p_dmg_mod) if p_dmg_mod > 0 else str(p_dmg_mod) if p_dmg_mod < 0 else ''}"
    o_dmg_str = f"{o_wep.get('damage', '1d6')}{'+' + str(o_dmg_mod) if o_dmg_mod > 0 else str(o_dmg_mod) if o_dmg_mod < 0 else ''}"

    full_attack_summary = f"Ana El: {p_atk_str} ({p_dmg_str}), Yan El: {o_atk_str} ({o_dmg_str})"

    return {
        "is_offhand_light": o_is_light,
        "has_twf_feat": has_twf,
        "has_double_slice": has_double_slice,
        "has_improved_twf": has_itwf,
        "has_greater_twf": has_gtwf,
        "primary_penalty": p_penalty,
        "offhand_penalty": o_penalty,
        "primary_attacks": p_attacks,
        "offhand_attacks": o_attacks,
        "primary_attack_string": p_atk_str,
        "offhand_attack_string": o_atk_str,
        "primary_damage_string": p_dmg_str,
        "offhand_damage_string": o_dmg_str,
        "full_attack_summary": full_attack_summary
    }
