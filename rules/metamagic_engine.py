"""
Pathfinder 1st Edition Metamagic & Spell Slot Engine
====================================================
References:
- PF1e Core Rulebook Chapter 5 (Metamagic Feats)
- PF1e Core Rulebook Chapter 9 (Magic & Spellcasting)
- Advanced Player's Guide (APG) & Ultimate Magic (UM)

Mechanics:
- Prepared Casters: Must prepare metamagic spells in higher-level slots in advance (normal casting time).
- Spontaneous Casters: Apply metamagic at cast time, expending higher-level slot (standard action spells become Full-Round Actions).
- Heighten Spell increases the actual effective spell level and DC.
- Quicken Spell reduces casting time to Swift Action (+4 slot adjustment).
- Adjusted spell level cannot exceed Level 9 (or caster's maximum spell level).
"""

from typing import Dict, Any, List, Optional, Union


OFFICIAL_METAMAGIC_FEATS: Dict[str, Dict[str, Any]] = {
    "empower": {
        "name": "Empower Spell",
        "isim_tr": "Güçlendirilmiş Büyü (Empower)",
        "level_adjustment": 2,
        "source": "CRB",
        "description": "Büyünün tüm değişken sayısal etkileri (hasar, iyileştirme vb.) %50 artar (1.5x).",
        "effect_type": "variable_numerical_boost"
    },
    "maximize": {
        "name": "Maximize Spell",
        "isim_tr": "Maksimum Büyü (Maximize)",
        "level_adjustment": 3,
        "source": "CRB",
        "description": "Büyünün değişken sayısal zarları en yüksek değerlerini verir.",
        "effect_type": "maximize_dice"
    },
    "quicken": {
        "name": "Quicken Spell",
        "isim_tr": "Hızlı Büyü (Quicken)",
        "level_adjustment": 4,
        "source": "CRB",
        "description": "Büyü Hızlı Eylem (Swift Action) olarak dökülür. Bir turda ek bir büyü dökülmesini sağlar.",
        "effect_type": "swift_action"
    },
    "extend": {
        "name": "Extend Spell",
        "isim_tr": "Uzatılmış Büyü (Extend)",
        "level_adjustment": 1,
        "source": "CRB",
        "description": "Büyünün etki süresi 2 katına (2x) çıkar. Anlık (Instantaneous) ve kalıcı büyülere uygulanamaz.",
        "effect_type": "double_duration"
    },
    "enlarge": {
        "name": "Enlarge Spell",
        "isim_tr": "Genişletilmiş Menzil (Enlarge)",
        "level_adjustment": 1,
        "source": "CRB",
        "description": "Büyünün menzili 2 katına (2x) çıkar (Close, Medium, Long menziller).",
        "effect_type": "double_range"
    },
    "silent": {
        "name": "Silent Spell",
        "isim_tr": "Sessiz Büyü (Silent)",
        "level_adjustment": 1,
        "source": "CRB",
        "description": "Büyü sözlü (Verbal) bileşen olmadan dökülür (Sessizlik alanı veya gizlilikte etkili).",
        "effect_type": "remove_verbal"
    },
    "still": {
        "name": "Still Spell",
        "isim_tr": "Hareketsiz Büyü (Still)",
        "level_adjustment": 1,
        "source": "CRB",
        "description": "Büyü somatik (Somatic) el hareketi olmadan dökülür (Zırh büyü bozma riskini sıfırlar).",
        "effect_type": "remove_somatic"
    },
    "widen": {
        "name": "Widen Spell",
        "isim_tr": "Geniş Alanlı Büyü (Widen)",
        "level_adjustment": 3,
        "source": "CRB",
        "description": "Büyünün alan etkisi çapı/yarıçapı %50 artar.",
        "effect_type": "area_boost"
    },
    "heighten": {
        "name": "Heighten Spell",
        "isim_tr": "Yükseltilmiş Büyü (Heighten)",
        "level_adjustment": 1, # Variable per level
        "source": "CRB",
        "description": "Büyünün hem slotunu hem de gerçek büyü seviyesini ve kurtarma zarı DC'sini yükseltir.",
        "effect_type": "increase_spell_level_and_dc"
    },
    "intensified": {
        "name": "Intensified Spell",
        "isim_tr": "Yoğunlaştırılmış Büyü (Intensified)",
        "level_adjustment": 1,
        "source": "APG",
        "description": "Büyünün hasar zar tavanı +5 büyücü seviyesi (CL) kadar yükselir (Örn: Shocking Grasp 5d6 -> 10d6).",
        "effect_type": "increase_damage_cap"
    },
    "persistent": {
        "name": "Persistent Spell",
        "isim_tr": "Israrcı Büyü (Persistent)",
        "level_adjustment": 2,
        "source": "APG",
        "description": "Hedef kurtarma zarını 2 kez atmak ve daha düşük (kötü) olanı kabul etmek zorundadır.",
        "effect_type": "disadvantage_saving_throw"
    },
    "dazing": {
        "name": "Dazing Spell",
        "isim_tr": "Sersemletici Büyü (Dazing)",
        "level_adjustment": 3,
        "source": "APG",
        "description": "Hasar alan hedefler başarısız kurtarma zarında büyü seviyesi kadar tur Sersemler (Dazed).",
        "effect_type": "inflict_dazed"
    },
    "toppling": {
        "name": "Toppling Spell",
        "isim_tr": "Devirici Büyü (Toppling)",
        "level_adjustment": 1,
        "source": "UM",
        "description": "Kuvvet (Force) büyüsü hasar verdiğinde hedefi Yere Yıkma (Trip) manevrası dener.",
        "effect_type": "free_trip_maneuver"
    },
    "rime": {
        "name": "Rime Spell",
        "isim_tr": "Kırağı Büyüsü (Rime)",
        "level_adjustment": 1,
        "source": "UM",
        "description": "Soğuk (Cold) büyüsü hasar verdiğinde hedef büyü seviyesi kadar tur Dolaşık (Entangled) kalır.",
        "effect_type": "inflict_entangled"
    },
    "ectoplasmic": {
        "name": "Ectoplasmic Spell",
        "isim_tr": "Ektoplazmik Büyü (Ectoplasmic)",
        "level_adjustment": 1,
        "source": "APG",
        "description": "Büyü bedensiz (Incorporeal) ve eterik varlıklara tam (%100) etki eder.",
        "effect_type": "incorporeal_full_effect"
    }
}


def get_metamagic_catalog() -> Dict[str, Any]:
    """Returns official Metamagic feats catalog."""
    return OFFICIAL_METAMAGIC_FEATS


def calculate_metamagic_spell(
    spell: Dict[str, Any],
    applied_metamagic: List[Union[str, Dict[str, Any]]],
    caster_type: str = "prepared",
    casting_mod: int = 0
) -> Dict[str, Any]:
    """
    Calculates adjusted spell level, slot requirement, casting time, and DC.
    """
    spell_name = str(spell.get("isim") or spell.get("name") or "Büyü").strip()

    # Determine Base Spell Level
    raw_lvl = spell.get("seviye")
    if raw_lvl is None:
        raw_lvl = spell.get("level", 1)
    try:
        base_level = int(raw_lvl)
    except (ValueError, TypeError):
        base_level = 1

    caster_type_norm = (caster_type or "prepared").lower().strip()
    is_spontaneous = caster_type_norm in {"spontaneous", "sorcerer", "oracle", "bard", "inquisitor", "bloodrager"}

    total_level_adj = 0
    heighten_bonus = 0
    has_quicken = False
    has_silent = False
    has_still = False
    effect_notes: List[str] = []
    warnings: List[str] = []
    applied_meta_details: List[Dict[str, Any]] = []

    for item in applied_metamagic:
        meta_key = ""
        heighten_target = 0

        if isinstance(item, str):
            meta_key = item.lower().strip()
        elif isinstance(item, dict):
            meta_key = str(item.get("key") or item.get("name") or "").lower().strip()
            heighten_target = int(item.get("target_level") or item.get("heighten_level") or 0)

        # Normalize key
        clean_key = meta_key.replace(" spell", "").replace(" ", "_")

        meta_info = OFFICIAL_METAMAGIC_FEATS.get(clean_key)
        if not meta_info:
            # Fallback search by name
            for k, v in OFFICIAL_METAMAGIC_FEATS.items():
                if k in clean_key or clean_key in v["name"].lower():
                    meta_info = v
                    clean_key = k
                    break

        if meta_info:
            adj = meta_info["level_adjustment"]

            if clean_key == "heighten":
                if heighten_target > base_level:
                    adj = heighten_target - base_level
                    heighten_bonus = adj
                else:
                    adj = 1
                    heighten_bonus = 1

            if clean_key == "quicken":
                has_quicken = True
            if clean_key == "silent":
                has_silent = True
            if clean_key == "still":
                has_still = True

            total_level_adj += adj
            effect_notes.append(f"{meta_info['name']}: {meta_info['description']}")
            applied_meta_details.append({
                "key": clean_key,
                "name": meta_info["name"],
                "isim_tr": meta_info["isim_tr"],
                "level_adjustment": adj
            })

    # Calculations
    required_slot_level = base_level + total_level_adj
    effective_spell_level = base_level + heighten_bonus
    effective_dc = 10 + effective_spell_level + casting_mod

    # Determine Casting Time
    base_casting_time = str(spell.get("casting_time") or spell.get("dokum_suresi") or "1 standard action").lower()

    if has_quicken:
        casting_time = "Swift Action (Hızlı Eylem)"
        if is_spontaneous:
            warnings.append("Spontaneous büyücüler Quicken Feat'ini ek yetenek olmadan doğrudan kullanamaz.")
    elif is_spontaneous and len(applied_meta_details) > 0:
        if "1 standard action" in base_casting_time or "1 eylem" in base_casting_time or "standart" in base_casting_time:
            casting_time = "Full-Round Action (Tam Tur Eylem)"
        else:
            casting_time = f"Normal süreden +1 Tam Tur daha uzun ({base_casting_time})"
    else:
        casting_time = base_casting_time.title() if base_casting_time else "1 Standart Eylem"

    # Validation Checks
    if required_slot_level > 9:
        warnings.append(f"Gerekli büyü slotu ({required_slot_level}. Seviye) 9. seviye tavanını aşıyor!")

    if has_silent and "bard" in caster_type_norm:
        warnings.append("Bard sınıfı Silent Spell feat'ini kullanamaz (Tüm bard büyüleri müzikal/sözlüdür).")

    return {
        "spell_name": spell_name,
        "base_level": base_level,
        "caster_type": "Spontaneous" if is_spontaneous else "Prepared",
        "applied_metamagic": applied_meta_details,
        "total_level_adjustment": total_level_adj,
        "required_slot_level": required_slot_level,
        "effective_spell_level": effective_spell_level,
        "base_dc": 10 + base_level + casting_mod,
        "effective_dc": effective_dc,
        "casting_time": casting_time,
        "has_silent": has_silent,
        "has_still": has_still,
        "effect_notes": effect_notes,
        "warnings": warnings,
        "is_valid": len(warnings) == 0
    }
