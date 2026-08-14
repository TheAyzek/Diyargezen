"""
Pathfinder 1st Edition Prestige Classes & Prerequisites Engine
==============================================================
References:
- PF1e Core Rulebook Chapter 11 (Prestige Classes, p. 374-394)

10 Official Core Prestige Classes:
- Arcane Archer, Arcane Trickster, Assassin, Dragon Disciple, Duelist,
  Eldritch Knight, Loremaster, Mystic Theurge, Pathfinder Chronicler, Shadowdancer
"""

from typing import Dict, Any, List, Optional


PRESTIGE_CLASSES_CATALOG: Dict[str, Dict[str, Any]] = {
    "arcane_archer": {
        "name": "Arcane Archer",
        "turkish_name": "Gizemli Okçu",
        "hit_die": "d10",
        "bab_progression": "Full",
        "good_saves": ["Fort", "Ref"],
        "description": "Oklarını ölümcül büyü güçleriyle birleştiren usta savaşçı büyücüler.",
        "prerequisites": {
            "min_bab": 6,
            "required_feats": ["Point-Blank Shot", "Precise Shot", "Weapon Focus"],
            "spells": "1st-level arcane spells",
            "race": "Elf or Half-Elf (Standard lore, flexible)"
        }
    },
    "arcane_trickster": {
        "name": "Arcane Trickster",
        "turkish_name": "Gizemli Düzenbaz",
        "hit_die": "d6",
        "bab_progression": "Half",
        "good_saves": ["Ref", "Will"],
        "description": "Gizlilik, hırsızlık numaraları ve büyü sanatlarını harmanlayan sinsi büyücüler.",
        "prerequisites": {
            "alignment": "Non-Lawful",
            "skills": {"disable device": 4, "escape artist": 4, "knowledge (arcana)": 4},
            "spells": "2nd-level arcane spells and mage hand",
            "special": "Sneak attack +2d6"
        }
    },
    "assassin": {
        "name": "Assassin",
        "turkish_name": "Suikastçı",
        "hit_die": "d8",
        "bab_progression": "Medium",
        "good_saves": ["Ref"],
        "description": "Zehirler, pusu ve ölümcül darbeler (Death Attack) konusunda uzmanlaşmış kiralık katiller.",
        "prerequisites": {
            "alignment": "Evil (LE, NE, CE)",
            "skills": {"disguise": 2, "escape artist": 2, "stealth": 5},
            "special": "Must kill someone in cold blood"
        }
    },
    "dragon_disciple": {
        "name": "Dragon Disciple",
        "turkish_name": "Ejderha Mürit",
        "hit_die": "d12",
        "bab_progression": "Medium",
        "good_saves": ["Fort", "Will"],
        "description": "İçlerindeki kadim ejderha soyunu uyandırarak nefes silahı ve doğal zırh kazanan büyücüler.",
        "prerequisites": {
            "skills": {"knowledge (arcana)": 5},
            "languages": ["Draconic"],
            "spells": "1st-level arcane spells cast spontaneously (Sorcerer / Bloodrager)"
        }
    },
    "duelist": {
        "name": "Duelist",
        "turkish_name": "Düellocu",
        "hit_die": "d10",
        "bab_progression": "Full",
        "good_saves": ["Ref"],
        "description": "Hafif silahlar, çevik savunma (Canny Defense) ve hassas darbeler konusunda usta kılıçşinaslar.",
        "prerequisites": {
            "min_bab": 6,
            "skills": {"acrobatics": 2, "perform": 2},
            "required_feats": ["Dodge", "Mobility", "Weapon Finesse"]
        }
    },
    "eldritch_knight": {
        "name": "Eldritch Knight",
        "turkish_name": "Büyülü Şövalye",
        "hit_die": "d10",
        "bab_progression": "Full",
        "good_saves": ["Fort"],
        "description": "Ağır silah ustalığı ile yüksek kademe büyücülüğü kusursuzca harmanlayan hibrit savaşçılar.",
        "prerequisites": {
            "martial_weapon_proficiency": True,
            "spells": "3rd-level arcane spells"
        }
    },
    "loremaster": {
        "name": "Loremaster",
        "turkish_name": "İlim Üstadı",
        "hit_die": "d6",
        "bab_progression": "Half",
        "good_saves": ["Will"],
        "description": "Evrenin sırlarını, kadim büyüleri ve unutulmuş dilleri araştıran büyük bilgeler.",
        "prerequisites": {
            "skills": {"knowledge": 7}, # 7 ranks in any two knowledge skills
            "required_feats": ["Skill Focus (Knowledge)"],
            "spells": "7 different divination spells, one 3rd-level or higher"
        }
    },
    "mystic_theurge": {
        "name": "Mystic Theurge",
        "turkish_name": "Mistik Teurg",
        "hit_die": "d6",
        "bab_progression": "Half",
        "good_saves": ["Will"],
        "description": "İlahi (Divine) ve Gizemli (Arcane) büyü ekollerini aynı anda zirveye taşıyan kudretli büyüdökücüler.",
        "prerequisites": {
            "skills": {"knowledge (arcana)": 3, "knowledge (religion)": 3},
            "spells": "2nd-level arcane spells AND 2nd-level divine spells"
        }
    },
    "pathfinder_chronicler": {
        "name": "Pathfinder Chronicler",
        "turkish_name": "Diyargezen Vakanüvisi",
        "hit_die": "d8",
        "bab_progression": "Medium",
        "good_saves": ["Will"],
        "description": "Golarion'un kayıp harabelerini keşfeden, efsaneleri toplayan ve zengin parti kaynakları sağlayan gezginler.",
        "prerequisites": {
            "skills": {"perform (oratory)": 5, "profession (scribe)": 5, "linguistics": 3},
            "special": "Bardic knowledge or Extra Performance feat"
        }
    },
    "shadowdancer": {
        "name": "Shadowdancer",
        "turkish_name": "Gölge Dansçısı",
        "hit_die": "d8",
        "bab_progression": "Medium",
        "good_saves": ["Ref"],
        "description": "Gölgelerin içinden sıyrılan, gölge illüzyonları yaratan ve görüş alanında bile gizlenebilen (Hide in Plain Sight) ustalar.",
        "prerequisites": {
            "skills": {"stealth": 5, "perform (dance)": 2},
            "required_feats": ["Combat Reflexes", "Dodge", "Mobility"]
        }
    }
}


def _normalize_str_list(items: Optional[List[Any]]) -> List[str]:
    """Helper to convert list of dicts/strings into clean lowercase string list."""
    res = []
    if not items:
        return res
    for item in items:
        if isinstance(item, dict):
            val = item.get("isim") or item.get("name") or str(item)
        else:
            val = str(item)
        res.append(val.lower().strip())
    return res


def validate_prestige_class_prerequisites(character_data: Dict[str, Any], prestige_id: str) -> Dict[str, Any]:
    """
    Validates a character's eligibility for a specific prestige class.
    Returns eligibility boolean, met requirements, and missing prerequisites.
    """
    p_id = (prestige_id or "").lower().strip().replace(" ", "_")
    if p_id not in PRESTIGE_CLASSES_CATALOG:
        return {
            "is_eligible": False,
            "error": f"Bilinmeyen prestij sınıfı: {prestige_id}",
            "met_prerequisites": [],
            "missing_prerequisites": [f"Sınıf bulunamadı: {prestige_id}"]
        }

    p_info = PRESTIGE_CLASSES_CATALOG[p_id]
    prereqs = p_info["prerequisites"]

    met = []
    missing = []

    # 1. BAB Check
    char_bab = int(character_data.get("bab", 0) or character_data.get("base_attack_bonus", 0) or 0)
    if "min_bab" in prereqs:
        min_bab = prereqs["min_bab"]
        if char_bab >= min_bab:
            met.append(f"Base Attack Bonus: +{char_bab} (Gereken: +{min_bab})")
        else:
            missing.append(f"Base Attack Bonus yetersiz: +{char_bab} (Gereken: +{min_bab})")

    # 2. Feats Check
    char_feats = _normalize_str_list(character_data.get("feats", []))
    if "required_feats" in prereqs:
        for rf in prereqs["required_feats"]:
            rf_clean = rf.lower().strip()
            # Check if any character feat matches
            if any(rf_clean in cf for cf in char_feats):
                met.append(f"Hüner: {rf}")
            else:
                missing.append(f"Eksik Hüner: {rf}")

    # 3. Skills Check
    char_skills = character_data.get("skills", {})
    if "skills" in prereqs:
        for req_sk, req_rank in prereqs["skills"].items():
            req_sk_clean = req_sk.lower().strip()
            # Find matching skill rank in character
            matched_rank = 0
            for sk_name, sk_data in char_skills.items():
                if req_sk_clean in sk_name.lower():
                    if isinstance(sk_data, dict):
                        matched_rank = max(matched_rank, int(sk_data.get("ranks", 0) or 0))
                    elif isinstance(sk_data, (int, float)):
                        matched_rank = max(matched_rank, int(sk_data))

            if matched_rank >= req_rank:
                met.append(f"Beceri: {req_sk.title()} {matched_rank} Rank (Gereken: {req_rank})")
            else:
                missing.append(f"Eksik Beceri: {req_sk.title()} {matched_rank} Rank (Gereken: {req_rank})")

    # 4. Alignment Check
    char_align = str(character_data.get("alignment", "TN")).upper().strip()
    if "alignment" in prereqs:
        req_align = prereqs["alignment"].lower()
        if "non-lawful" in req_align:
            if char_align not in ["LG", "LN", "LE"]:
                met.append(f"Hizalanış: {char_align} (Non-Lawful)")
            else:
                missing.append(f"Hizalanış uyumsuz: {char_align} (Non-Lawful olmalı)")
        elif "evil" in req_align:
            if char_align in ["LE", "NE", "CE"]:
                met.append(f"Hizalanış: {char_align} (Evil)")
            else:
                missing.append(f"Hizalanış uyumsuz: {char_align} (Evil [LE/NE/CE] olmalı)")

    # 5. Languages Check
    char_langs = _normalize_str_list(character_data.get("languages", []))
    if "languages" in prereqs:
        for r_lang in prereqs["languages"]:
            if any(r_lang.lower() in cl for cl in char_langs):
                met.append(f"Dil: {r_lang}")
            else:
                missing.append(f"Eksik Dil: {r_lang}")

    # 6. Informative requirements (Spells & Special)
    if "spells" in prereqs:
        met.append(f"Büyü Gereksinimi: {prereqs['spells']}")
    if "special" in prereqs:
        met.append(f"Özel Gereksinim: {prereqs['special']}")

    is_eligible = len(missing) == 0

    return {
        "prestige_id": p_id,
        "name": p_info["name"],
        "turkish_name": p_info["turkish_name"],
        "hit_die": p_info["hit_die"],
        "bab_progression": p_info["bab_progression"],
        "good_saves": p_info["good_saves"],
        "description": p_info["description"],
        "is_eligible": is_eligible,
        "met_prerequisites": met,
        "missing_prerequisites": missing
    }


def get_eligible_prestige_classes(character_data: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Evaluates all 10 prestige classes against a character and returns full report."""
    results = []
    for pid in PRESTIGE_CLASSES_CATALOG.keys():
        results.append(validate_prestige_class_prerequisites(character_data, pid))
    return results


def get_all_prestige_classes_catalog() -> Dict[str, Any]:
    """Returns catalog of all 10 core prestige classes."""
    return PRESTIGE_CLASSES_CATALOG
