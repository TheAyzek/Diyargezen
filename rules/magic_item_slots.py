"""
Pathfinder 1st Edition Magic Item Body Slots & Wealth by Level (WBL) Engine
=============================================================================
References:
- PF1e Core Rulebook p. 458-459 (Magic Item Body Slots & Slot Limit Rules)
- PF1e Core Rulebook p. 399 (Table 12-4: Character Wealth by Level)
- PF1e Core Rulebook p. 549-553 (Magic Item Pricing Formulas)

Architecture:
- Provides 12 standard Paizo body slot classifications.
- Detects slot assignments and equipment slot conflicts (e.g. 2 belts or >2 rings).
- Extracts and infers item prices in Gold Pieces (gp).
- Calculates Wealth by Level (WBL) metrics and budget analysis.
"""

import re
from typing import Dict, Any, List, Optional, Tuple


# ---------------------------------------------------------------------------
# 1. Official 12 Magic Item Body Slots (PF1e CRB p. 458-459)
# ---------------------------------------------------------------------------
MAGIC_BODY_SLOTS = [
    "armor",       # Suit of armor or robes (e.g. Mithral Full Plate, Robe of the Archmagi)
    "belts",       # Belt (e.g. Belt of Giant Strength)
    "body",        # Body/Vestment (e.g. Monk's Robe, Druid's Vestment)
    "chest",       # Chest (e.g. Quick Runner's Shirt, Vest of Resistance)
    "eyes",        # Eyes (e.g. Goggles of Night, Eyes of the Eagle)
    "feet",        # Feet (e.g. Boots of Speed, Slippers of Spider Climbing)
    "hands",       # Hands (e.g. Gauntlets of Ogre Power, Gloves of Storing)
    "head",        # Head (e.g. Helm of Telepathy, Hat of Disguise)
    "headband",    # Headband (e.g. Headband of Vast Intelligence)
    "neck",        # Neck (e.g. Amulet of Natural Armor, Periapt of Wound Closure)
    "ring_1",      # First Magic Ring (e.g. Ring of Protection)
    "ring_2",      # Second Magic Ring
    "shoulders",   # Shoulders (e.g. Cloak of Resistance)
    "wrists",      # Wrists (e.g. Bracers of Armor)
    "slotless",    # Slotless items (e.g. Ioun Stones, Bag of Holding, Potions)
]

SLOT_DISPLAY_NAMES: Dict[str, str] = {
    "armor": "Zırh / Cübbe (Armor)",
    "belts": "Kemer (Belt)",
    "body": "Beden / Kaftan (Body)",
    "chest": "Göğüs / Gömlek (Chest)",
    "eyes": "Göz / Gözlük (Eyes)",
    "feet": "Ayak / Bot (Feet)",
    "hands": "El / Eldiven (Hands)",
    "head": "Baş / Miğfer (Head)",
    "headband": "Alınlık / Taç (Headband)",
    "neck": "Boyun / Muska (Neck)",
    "ring_1": "Yüzük 1 (Ring 1)",
    "ring_2": "Yüzük 2 (Ring 2)",
    "shoulders": "Omuz / Pelerin (Shoulders)",
    "wrists": "Bilek / Bileklik (Wrists)",
    "slotless": "Slotsuz (Slotless)",
}


# ---------------------------------------------------------------------------
# 2. Wealth by Level (WBL) Standards (PF1e CRB Table 12-4)
# ---------------------------------------------------------------------------
PF1E_WEALTH_BY_LEVEL: Dict[int, int] = {
    1: 150,        # Average starting gold for level 1
    2: 1000,
    3: 3000,
    4: 6000,
    5: 10500,
    6: 16000,
    7: 23500,
    8: 33000,
    9: 46000,
    10: 62000,
    11: 82000,
    12: 108000,
    13: 140000,
    14: 185000,
    15: 240000,
    16: 315000,
    17: 410000,
    18: 530000,
    19: 685000,
    20: 880000,
}


# ---------------------------------------------------------------------------
# 3. Item Body Slot Inference
# ---------------------------------------------------------------------------
def infer_item_body_slot(item: Dict[str, Any]) -> str:
    """Infers the PF1e magic body slot from item attributes, category, or name."""
    if not isinstance(item, dict):
        return "slotless"

    # 1. Check explicit slot field in item or sistem_verisi
    sv = item.get("sistem_verisi") or item.get("system_data") or {}
    if not isinstance(sv, dict):
        sv = {}
    sys_obj = sv.get("system", {}) if isinstance(sv.get("system"), dict) else {}

    raw_slot = str(item.get("slot") or item.get("body_slot") or sv.get("slot") or sys_obj.get("slot") or "").strip().lower()
    if raw_slot:
        for known_slot in ("armor", "belts", "body", "chest", "eyes", "feet", "hands", "head", "headband", "neck", "ring", "shoulders", "wrists", "slotless"):
            if known_slot in raw_slot:
                return "belts" if known_slot == "belt" else known_slot

    name = str(item.get("name") or item.get("isim") or "").strip().lower()
    cat = str(item.get("kategori") or item.get("category") or sv.get("category") or "").strip().lower()
    itype = str(item.get("type") or sv.get("type") or "").strip().lower()

    # 2. Check by item name patterns
    if "headband" in name or "circlet" in name or "crown" in name or "diadem" in name or "phylactery" in name:
        return "headband"
    if "belt" in name or "girdle" in name or "sash" in name:
        return "belts"
    if "cloak" in name or "cape" in name or "mantle" in name or "shawl" in name or "pauldrons" in name or "spaulders" in name:
        return "shoulders"
    if "amulet" in name or "necklace" in name or "periapt" in name or "medallion" in name or "brooch" in name or "talisman" in name or "pendant" in name or "torc" in name or "choker" in name:
        return "neck"
    if "ring" in name:
        return "ring"
    if "boots" in name or "slippers" in name or "shoes" in name or "sandals" in name or "greaves" in name:
        return "feet"
    if "gloves" in name or "gauntlets" in name or "mitts" in name:
        return "hands"
    if "bracers" in name or "bracelet" in name or "armbands" in name or "cuffs" in name:
        return "wrists"
    if "helm" in name or "hat" in name or "cap" in name or "mask" in name or "hood" in name or "helmet" in name or "coif" in name or "goggles" in name or "spectacles" in name or "lenses" in name or "monocle" in name:
        if any(e in name for e in ("goggles", "eyes", "spectacles", "lenses", "monocle")):
            return "eyes"
        return "head"
    if "shirt" in name or "vest" in name or "tunic" in name or "corset" in name or "waistcoat" in name:
        return "chest"
    if "robe" in name or "vestment" in name or "cassock" in name:
        return "body"
    if itype in ("armor", "shield") or "armor" in cat or "zırh" in cat or any(w in name for w in ("plate", "mail", "leather", "breastplate", "shield", "buckler", "zırh", "kalkan")):
        return "armor"

    # Consumables / Weapons / General gear
    if itype in ("weapon", "consumable", "potion", "scroll", "wand") or any(c in cat for c in ("weapon", "silah", "potion", "scroll", "wand", "iksir")):
        return "slotless"

    return "slotless"


# ---------------------------------------------------------------------------
# 4. Item Price Extraction & Valuation (PF1e CRB p. 549-553)
# ---------------------------------------------------------------------------
def parse_price_value(price_val: Any) -> float:
    """Safely converts numeric or string price (e.g. '15 gp', '2,000 gp', 250) to gp float."""
    if price_val is None:
        return 0.0
    if isinstance(price_val, (int, float)):
        return float(price_val)
    price_str = str(price_val).replace(',', '').strip().lower()
    m = re.search(r'([\d\.\/]+)\s*(gp|sp|cp|pp)?', price_str)
    if not m:
        return 0.0
    val_str, unit = m.groups()
    try:
        val = float(val_str.split('/')[0]) / float(val_str.split('/')[1]) if '/' in val_str else float(val_str)
    except (ValueError, ZeroDivisionError):
        return 0.0
    if unit == 'sp':
        return val * 0.1
    elif unit == 'cp':
        return val * 0.01
    elif unit == 'pp':
        return val * 10.0
    return val


def infer_magic_item_price_gp(item: Dict[str, Any]) -> float:
    """Extracts explicit price or infers standard Paizo CRB magic item price in gold pieces (gp)."""
    if not isinstance(item, dict):
        return 0.0

    # 1. Check explicit price fields
    sv = item.get("sistem_verisi") or item.get("system_data") or {}
    if not isinstance(sv, dict):
        sv = {}
    sys_obj = sv.get("system", {}) if isinstance(sv.get("system"), dict) else {}

    raw_price = item.get("price_gp") or item.get("price") or item.get("fiyat") or item.get("cost") or sv.get("price_gp") or sv.get("price") or sys_obj.get("price")
    explicit_val = parse_price_value(raw_price)
    if explicit_val > 0:
        return explicit_val

    # 2. Check formulaic magic item pricing from name
    name = str(item.get("name") or item.get("isim") or "").strip().lower()

    # Cloak of Resistance +1..+5 (bonus^2 * 1,000 gp)
    m_cloak = re.search(r'cloak of resistance \+([1-5])', name)
    if m_cloak:
        return float(int(m_cloak.group(1)) ** 2 * 1000)

    # Ring of Protection +1..+5 (bonus^2 * 2,000 gp)
    m_ring = re.search(r'ring of protection \+([1-5])', name)
    if m_ring:
        return float(int(m_ring.group(1)) ** 2 * 2000)

    # Amulet of Natural Armor +1..+5 (bonus^2 * 2,000 gp)
    m_amulet = re.search(r'amulet of natural armor \+([1-5])', name)
    if m_amulet:
        return float(int(m_amulet.group(1)) ** 2 * 2000)

    # Belts / Headbands (+2: 4k, +4: 16k, +6: 36k)
    m_stat = re.search(r'(?:belt of|headband of)\s+(?:giant|incredible|mighty|vast|inspired|alluring)?\s*\w+\s*\+([246])', name)
    if m_stat:
        val = int(m_stat.group(1))
        if val == 2: return 4000.0
        elif val == 4: return 16000.0
        elif val == 6: return 36000.0

    # Multi-attribute Belts/Headbands (Physical Perfection / Mental Superiority)
    if "physical perfection" in name or "mental superiority" in name:
        m_all = re.search(r'\+([246])', name)
        if m_all:
            val = int(m_all.group(1))
            if val == 2: return 16000.0
            elif val == 4: return 64000.0
            elif val == 6: return 144000.0

    # Physical Might / Mental Prowess (2 stats +2: 10k, +4: 40k, +6: 90k)
    if "physical might" in name or "mental prowess" in name:
        m_two = re.search(r'\+([246])', name)
        if m_two:
            val = int(m_two.group(1))
            if val == 2: return 10000.0
            elif val == 4: return 40000.0
            elif val == 6: return 90000.0

    # Magic Weapons (+1: 2k, +2: 8k, +3: 18k, +4: 32k, +5: 50k + 300 gp masterwork + base)
    m_weap = re.search(r'\+([1-5])\s+(?:longsword|greatsword|dagger|shortsword|battleaxe|bow|crossbow|scimitar|spear|halberd|falchion|rapier|mace)', name)
    if m_weap:
        enh = int(m_weap.group(1))
        return float((enh ** 2 * 2000) + 300 + 15)

    # Magic Armor (+1: 1k, +2: 4k, +3: 9k, +4: 16k, +5: 25k + 150 gp masterwork + base)
    m_arm = re.search(r'\+([1-5])\s+(?:mithral\s+)?(?:breastplate|full plate|chainmail|leather|studded|shield)', name)
    if m_arm:
        enh = int(m_arm.group(1))
        mithral_bonus = 4000 if "mithral" in name else 0
        return float((enh ** 2 * 1000) + 150 + 200 + mithral_bonus)

    # Boots of Speed (12,000 gp)
    if "boots of speed" in name:
        return 12000.0

    # Handy Haversack (2,000 gp)
    if "handy haversack" in name:
        return 2000.0

    # Bag of Holding Type I..IV (2.5k, 5k, 7.4k, 10k)
    if "bag of holding" in name:
        if "iv" in name or "4" in name: return 10000.0
        if "iii" in name or "3" in name: return 7400.0
        if "ii" in name or "2" in name: return 5000.0
        return 2500.0

    return 0.0


# ---------------------------------------------------------------------------
# 5. Slot Conflict Detection & Wealth Engine
# ---------------------------------------------------------------------------
def evaluate_magic_item_slots_and_wealth(
    equipment_list: List[Dict[str, Any]],
    level: int = 1
) -> Dict[str, Any]:
    """Calculates equipped magic item slots, flags conflicts, and analyzes Wealth by Level (WBL)."""
    lvl = max(1, min(20, int(level or 1)))
    expected_wbl = PF1E_WEALTH_BY_LEVEL.get(lvl, 150)

    occupied_slots: Dict[str, Optional[Dict[str, Any]]] = {s: None for s in MAGIC_BODY_SLOTS if s != "slotless"}
    slotless_items: List[Dict[str, Any]] = []
    slot_conflicts: List[Dict[str, Any]] = []

    total_wealth_gp = 0.0
    equipped_items_count = 0

    # Group items by their deduced slot
    slot_groups: Dict[str, List[Dict[str, Any]]] = {}

    for item in equipment_list:
        if not isinstance(item, dict):
            continue

        item_name = str(item.get("name") or item.get("isim") or "Bilinmeyen Eşya").strip()
        price_gp = infer_magic_item_price_gp(item)
        qty = int(item.get("quantity") or item.get("adet") or 1)
        total_wealth_gp += price_gp * qty

        # Check if equipped (default to True if not specified, strictly False if set to False)
        if "is_equipped" in item:
            is_equipped = bool(item["is_equipped"])
        elif "equipped" in item:
            is_equipped = bool(item["equipped"])
        elif isinstance(item.get("sistem_verisi"), dict) and "is_equipped" in item["sistem_verisi"]:
            is_equipped = bool(item["sistem_verisi"]["is_equipped"])
        elif isinstance(item.get("sistem_verisi"), dict) and "equipped" in item["sistem_verisi"]:
            is_equipped = bool(item["sistem_verisi"]["equipped"])
        else:
            is_equipped = True

        item_info = {
            "name": item_name,
            "slot": infer_item_body_slot(item),
            "price_gp": price_gp,
            "quantity": qty,
            "is_equipped": is_equipped,
            "raw_item": item
        }

        if is_equipped:
            equipped_items_count += 1
            s = item_info["slot"]
            if s == "slotless":
                slotless_items.append(item_info)
            else:
                if s not in slot_groups:
                    slot_groups[s] = []
                slot_groups[s].append(item_info)

    # Assign to official 12 slots and detect conflicts
    for slot_name, items in slot_groups.items():
        if slot_name == "ring":
            # Rings: Max 2 equipped
            if len(items) >= 1:
                occupied_slots["ring_1"] = items[0]
            if len(items) >= 2:
                occupied_slots["ring_2"] = items[1]
            if len(items) > 2:
                conflict_names = [it["name"] for it in items]
                slot_conflicts.append({
                    "slot": "ring",
                    "slot_display": "Yüzükler (Rings)",
                    "items": conflict_names,
                    "max_allowed": 2,
                    "equipped_count": len(items),
                    "message": f"Yüzük slotu en fazla 2 eşyaya izin verir. Şu an {len(items)} yüzük takılı: {', '.join(conflict_names)}."
                })
        else:
            # Single item slots (armor, belts, body, chest, eyes, feet, hands, head, headband, neck, shoulders, wrists)
            occupied_slots[slot_name] = items[0] if items else None
            if len(items) > 1:
                conflict_names = [it["name"] for it in items]
                slot_display = SLOT_DISPLAY_NAMES.get(slot_name, slot_name.title())
                slot_conflicts.append({
                    "slot": slot_name,
                    "slot_display": slot_display,
                    "items": conflict_names,
                    "max_allowed": 1,
                    "equipped_count": len(items),
                    "message": f"{slot_display} slotu sadece 1 eşyaya izin verir. Şu an {len(items)} eşya takılı: {', '.join(conflict_names)}."
                })

    # WBL Budget Analysis
    wbl_diff = total_wealth_gp - expected_wbl
    wbl_pct = round((total_wealth_gp / expected_wbl * 100), 1) if expected_wbl > 0 else 100.0

    if wbl_pct < 80.0:
        wbl_status = "Bütçe Altı (Under Wealth)"
        wbl_status_code = "under"
    elif wbl_pct <= 125.0:
        wbl_status = "Dengeli (Balanced Wealth)"
        wbl_status_code = "balanced"
    else:
        wbl_status = "Bütçe Üstü (Over Wealth)"
        wbl_status_code = "over"

    return {
        "occupied_slots": occupied_slots,
        "slotless_items": slotless_items,
        "slot_conflicts": slot_conflicts,
        "has_conflicts": len(slot_conflicts) > 0,
        "equipped_items_count": equipped_items_count,
        "wealth": {
            "total_wealth_gp": total_wealth_gp,
            "expected_wbl_gp": expected_wbl,
            "difference_gp": wbl_diff,
            "percentage": wbl_pct,
            "status": wbl_status,
            "status_code": wbl_status_code,
            "level": lvl
        }
    }
