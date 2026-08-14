"""
Pathfinder 1st Edition Weapon Special Abilities & Elemental Damage Engine
=========================================================================
References:
- PF1e Core Rulebook Chapter 15 (Table 15-9: Weapon Special Abilities, p. 468-472)
- Ultimate Equipment (Magic Weapons)

Rules:
- Base enhancement bonus must be at least +1 before special abilities can be added.
- Total effective bonus (Enhancement + Abilities) cannot exceed +10.
- Price: (Total Effective Bonus)^2 * 2,000 gp + 300 gp (Masterwork) + Base Weapon Cost.
- Keen: Doubles threat range (18-20 -> 15-20, 19-20 -> 17-20, 20 -> 19-20). Does not stack with Improved Critical.
"""

import re
from typing import Dict, Any, List, Optional


WEAPON_SPECIAL_ABILITIES_REGISTRY: Dict[str, Dict[str, Any]] = {
    "flaming": {
        "name": "Flaming",
        "name_tr": "Alevli (Flaming)",
        "bonus_equivalent": 1,
        "extra_damage_type": "Ateş (Fire)",
        "extra_damage_dice": "1d6",
        "desc": "Başarılı her vuruşta fazladan +1d6 Ateş hasarı verir."
    },
    "frost": {
        "name": "Frost",
        "name_tr": "Buzlu (Frost)",
        "bonus_equivalent": 1,
        "extra_damage_type": "Soğuk (Cold)",
        "extra_damage_dice": "1d6",
        "desc": "Başarılı her vuruşta fazladan +1d6 Soğuk hasarı verir."
    },
    "shock": {
        "name": "Shock",
        "name_tr": "Şok (Shock)",
        "bonus_equivalent": 1,
        "extra_damage_type": "Elektrik (Electricity)",
        "extra_damage_dice": "1d6",
        "desc": "Başarılı her vuruşta fazladan +1d6 Elektrik hasarı verir."
    },
    "corrosive": {
        "name": "Corrosive",
        "name_tr": "Asitli (Corrosive)",
        "bonus_equivalent": 1,
        "extra_damage_type": "Asit (Acid)",
        "extra_damage_dice": "1d6",
        "desc": "Başarılı her vuruşta fazladan +1d6 Asit hasarı verir."
    },
    "ghost_touch": {
        "name": "Ghost Touch",
        "name_tr": "Hayalet Dokunuşu (Ghost Touch)",
        "bonus_equivalent": 1,
        "desc": "Cisimsiz (Incorporeal) hayalet ve tayflara karşı %100 tam hasar verir."
    },
    "keen": {
        "name": "Keen",
        "name_tr": "Keskin (Keen)",
        "bonus_equivalent": 1,
        "desc": "Silahın kritik tehdit aralığını iki katına çıkarır (Örn: 18-20 -> 15-20, 19-20 -> 17-20)."
    },
    "flaming_burst": {
        "name": "Flaming Burst",
        "name_tr": "Alev Patlaması (Flaming Burst)",
        "bonus_equivalent": 2,
        "extra_damage_type": "Ateş (Fire)",
        "extra_damage_dice": "1d6",
        "crit_extra_dice": "1d10 per crit multiplier",
        "desc": "Normalde +1d6 Ateş, kritik vuruşta ise çarpan başına +1d10 patlama ateşi hasarı verir."
    },
    "icy_burst": {
        "name": "Icy Burst",
        "name_tr": "Buz Patlaması (Icy Burst)",
        "bonus_equivalent": 2,
        "extra_damage_type": "Soğuk (Cold)",
        "extra_damage_dice": "1d6",
        "crit_extra_dice": "1d10 per crit multiplier",
        "desc": "Normalde +1d6 Soğuk, kritik vuruşta çarpan başına +1d10 patlama soğuğu hasarı verir."
    },
    "shocking_burst": {
        "name": "Shocking Burst",
        "name_tr": "Şok Patlaması (Shocking Burst)",
        "bonus_equivalent": 2,
        "extra_damage_type": "Elektrik (Electricity)",
        "extra_damage_dice": "1d6",
        "crit_extra_dice": "1d10 per crit multiplier",
        "desc": "Normalde +1d6 Elektrik, kritik vuruşta çarpan başına +1d10 patlama elektriği hasarı verir."
    },
    "holy": {
        "name": "Holy",
        "name_tr": "Kutsal (Holy)",
        "bonus_equivalent": 2,
        "extra_damage_type": "Kutsal (Holy)",
        "extra_damage_dice": "2d6",
        "desc": "Kötü (Evil) hizalanıştaki yaratıklara karşı fazladan +2d6 hasar verir."
    },
    "unholy": {
        "name": "Unholy",
        "name_tr": "Kutsalsız (Unholy)",
        "bonus_equivalent": 2,
        "extra_damage_type": "Kutsalsız (Unholy)",
        "extra_damage_dice": "2d6",
        "desc": "İyi (Good) hizalanıştaki yaratıklara karşı fazladan +2d6 hasar verir."
    },
    "anarchic": {
        "name": "Anarchic",
        "name_tr": "Anarşik (Anarchic)",
        "bonus_equivalent": 2,
        "extra_damage_type": "Kaos (Chaos)",
        "extra_damage_dice": "2d6",
        "desc": "Düzenli (Lawful) yaratıklara karşı fazladan +2d6 hasar verir."
    },
    "axiomatic": {
        "name": "Axiomatic",
        "name_tr": "Aksiyomatik (Axiomatic)",
        "bonus_equivalent": 2,
        "extra_damage_type": "Düzen (Order)",
        "extra_damage_dice": "2d6",
        "desc": "Kaotik (Chaotic) yaratıklara karşı fazladan +2d6 hasar verir."
    },
    "bane": {
        "name": "Bane",
        "name_tr": "Can Düşmanı (Bane)",
        "bonus_equivalent": 1,
        "extra_damage_type": "Bane Hasarı",
        "extra_damage_dice": "2d6",
        "desc": "Seçili yaratık türüne karşı saldırı bonusu +2 artar ve fazladan +2d6 hasar verir."
    },
    "speed": {
        "name": "Speed",
        "name_tr": "Hız (Speed)",
        "bonus_equivalent": 3,
        "desc": "Tam tur saldırısı (Full Attack) yaparken en yüksek BAB ile 1 ekstra saldırı hakkı verir."
    },
    "vicious": {
        "name": "Vicious",
        "name_tr": "Acımasız (Vicious)",
        "bonus_equivalent": 1,
        "extra_damage_type": "Saf Hasar",
        "extra_damage_dice": "2d6",
        "self_damage_dice": "1d6",
        "desc": "Düşmana fazladan +2d6 hasar verir; her başarılı vuruşta kullanıcıya 1d6 hasar geri teper."
    },
    "defending": {
        "name": "Defending",
        "name_tr": "Savunmacı (Defending)",
        "bonus_equivalent": 1,
        "desc": "Tur başında silahın geliştirme bonusunun bir kısmını veya tamamını AC'ye aktarabilir."
    },
    "disruption": {
        "name": "Disruption",
        "name_tr": "Yıkıcı (Disruption)",
        "bonus_equivalent": 2,
        "desc": "Ezici silahlar: Vurulan Hortlak (Undead) varlıklar DC 14 Will kurtarma zarı atamazsa yok olur."
    },
    "vorpal": {
        "name": "Vorpal",
        "name_tr": "Kelle Uçuran (Vorpal)",
        "bonus_equivalent": 5,
        "desc": "Kesici silahlar: Doğal 20 kritik vuruş teyit edildiğinde hedefin kafasını anında koparır."
    }
}


def expand_critical_threat_range(base_crit: str) -> str:
    """
    Doubles critical threat range (e.g. 18-20/x2 -> 15-20/x2, 19-20/x2 -> 17-20/x2, 20/x2 -> 19-20/x2).
    """
    if not base_crit:
        return "19-20/x2"

    crit_str = str(base_crit).strip()

    # Match pattern like "18-20/x2" or "19-20" or "x3" or "20/x3"
    match = re.match(r"(?:(\d+)-)?(\d+)(?:/(x\d+))?", crit_str, re.IGNORECASE)
    if not match:
        return crit_str

    low_bound = match.group(1)
    high_bound = int(match.group(2) or 20)
    multiplier = match.group(3) or "x2"

    if low_bound:
        threat_width = (high_bound - int(low_bound) + 1)
    else:
        threat_width = 1

    doubled_width = threat_width * 2
    new_low = max(1, high_bound - doubled_width + 1)

    return f"{new_low}-20/{multiplier}"


def calculate_weapon_magical_properties(
    weapon: Dict[str, Any],
    base_enhancement: int = 1,
    applied_abilities: Optional[List[str]] = None,
    is_bane_active: bool = False
) -> Dict[str, Any]:
    """
    Calculates combined magical weapon bonuses, elemental dice, critical range and GP market price.
    """
    applied = applied_abilities or []
    base_enh = max(0, int(base_enhancement or 0))
    weapon_name = weapon.get("name") or weapon.get("isim") or "Büyülü Silah"
    base_damage = weapon.get("damage") or weapon.get("hasar") or "1d8"
    base_crit = weapon.get("crit") or weapon.get("kritik") or "20/x2"
    base_cost = int(weapon.get("cost_gp") or weapon.get("fiyat") or 15)

    warnings = []

    if base_enh < 1 and len(applied) > 0:
        warnings.append("Özel nitelik eklenebilmesi için silahın en az +1 temel geliştirme bonusuna sahip olması gerekir.")

    total_ability_bonus = 0
    extra_damage_dice = []
    has_keen = False
    has_speed = False

    for ab_key in applied:
        clean_key = ab_key.lower().strip()
        if clean_key in WEAPON_SPECIAL_ABILITIES_REGISTRY:
            data = WEAPON_SPECIAL_ABILITIES_REGISTRY[clean_key]
            total_ability_bonus += data["bonus_equivalent"]

            if "extra_damage_dice" in data:
                extra_damage_dice.append({
                    "name": data["name_tr"],
                    "type": data["extra_damage_type"],
                    "dice": data["extra_damage_dice"]
                })

            if clean_key == "keen":
                has_keen = True
            if clean_key == "speed":
                has_speed = True

    total_effective_bonus = base_enh + total_ability_bonus

    if total_effective_bonus > 10:
        warnings.append(f"Toplam eşdeğer geliştirme bonusu (+{total_effective_bonus}) izin verilen +10 tavanını aşıyor.")

    # Bane active bonus
    eff_atk_bonus = base_enh + (2 if is_bane_active else 0)
    eff_dmg_bonus = base_enh + (2 if is_bane_active else 0)

    # Critical threat range
    effective_crit = expand_critical_threat_range(base_crit) if has_keen else base_crit

    # Formatted damage string
    damage_parts = [f"{base_damage}+{eff_dmg_bonus}" if eff_dmg_bonus > 0 else str(base_damage)]
    for ex in extra_damage_dice:
        damage_parts.append(f"+{ex['dice']} {ex['type']}")

    if is_bane_active and "bane" in applied:
        damage_parts.append("+2d6 Bane Hasarı")

    combined_damage_str = " ".join(damage_parts)

    # Market Price in GP (CRB Table 15-9)
    # Masterwork component = 300 gp
    if total_effective_bonus > 0:
        market_price = (total_effective_bonus ** 2) * 2000 + 300 + base_cost
    else:
        market_price = base_cost

    crafting_cost = market_price // 2

    return {
        "weapon_name": weapon_name,
        "base_enhancement": base_enh,
        "total_effective_bonus": total_effective_bonus,
        "effective_attack_bonus": eff_atk_bonus,
        "effective_damage_bonus": eff_dmg_bonus,
        "base_damage": base_damage,
        "extra_damage_dice": extra_damage_dice,
        "combined_damage_string": combined_damage_str,
        "critical": effective_crit,
        "has_keen": has_keen,
        "has_speed": has_speed,
        "extra_full_attacks": 1 if has_speed else 0,
        "market_price_gp": market_price,
        "crafting_cost_gp": crafting_cost,
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }


def get_weapon_abilities_catalog() -> Dict[str, Any]:
    """Returns complete catalog of weapon special abilities."""
    return {
        "abilities": WEAPON_SPECIAL_ABILITIES_REGISTRY
    }
