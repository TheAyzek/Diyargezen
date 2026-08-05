"""
Diyargezen Pathfinder 1st Edition (PF1e) Rule Engine Validator

Architecture Overview & Soft-Block Philosophy:
----------------------------------------------
This module implements the primary diagnostic validation engine for Pathfinder 1e character sheets.
In alignment with the project's 'Soft-Block / Game Master Override' paradigm (Rule 3), the validator
evaluates character choices (Ability Scores, Skill Ranks, Feat Prerequisites, Trait Categories)
against official PF1e OGL rulesets without throwing hard runtime exceptions.

Key Algorithmic Principles:
1. Non-blocking Soft Warnings: Produces diagnostic warning strings rather than hard errors.
2. GM Override Bypass (`is_overridden` / `gm_override`): If the character payload sets an override flag,
   rule warnings are suppressed to honor tabletop GM discretion.
3. Feat Prerequisite Verification: Checks stat (STR, DEX, INT) and BAB requirements for iconic PF1e feats.
4. Trait Category Conflict Detection: Ensures players select no more than 1 trait per category (Combat, Social, Magic, Faith, Regional)
   unless explicit overrides exist.
"""

from .base_validator import BaseValidator
from typing import Dict, Any, List, Set, Optional

class PF1EValidator(BaseValidator):
    """
    Pathfinder 1e kural doğrulayıcı sınıfı.
    
    Karakter oluşturma ve seviye atlama aşamalarında kural ihlallerini tespit eder
    ancak "Soft-Block" prensibi gereği oyunu kilitlemeyip uyarı dizisi döner.
    """

    CORE_ABILITIES = {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
        "str", "dex", "con", "int", "wis", "cha"
    }

    # Iconic Feat prerequisite dictionary
    FEAT_PREREQUISITES: Dict[str, Dict[str, Any]] = {
        "power attack": {"str": 13, "bab": 1},
        "cleave": {"str": 13, "bab": 1, "feats": ["power attack"]},
        "great cleave": {"str": 13, "bab": 4, "feats": ["power attack", "cleave"]},
        "dodge": {"dex": 13},
        "mobility": {"dex": 13, "feats": ["dodge"]},
        "spring attack": {"dex": 13, "bab": 4, "feats": ["dodge", "mobility"]},
        "combat expertise": {"int": 13},
        "improved trip": {"int": 13, "feats": ["combat expertise"]},
        "improved disarm": {"int": 13, "feats": ["combat expertise"]},
        "deadly aim": {"dex": 13, "bab": 1},
        "weapon finesse": {"bab": 1},
        "point-blank shot": {},
        "precise shot": {"feats": ["point-blank shot"]},
        "rapid shot": {"dex": 13, "feats": ["point-blank shot"]},
        "manyshot": {"dex": 17, "bab": 6, "feats": ["point-blank shot", "rapid shot"]},
        "vital strike": {"bab": 6},
        "improved vital strike": {"bab": 11, "feats": ["vital strike"]},
        "greater vital strike": {"bab": 16, "feats": ["vital strike", "improved vital strike"]},
    }

    def __init__(self):
        super().__init__("Pathfinder 1e")

    def validate(self, character: Dict[str, Any], system_data: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        Karakter verisini PF1e kurallarına göre denetler.
        
        Args:
            character (Dict[str, Any]): Karakter verisi sözlüğü.
            system_data (Optional[Dict[str, Any]]): Ek sistem veya veri kümesi parametreleri.
            
        Returns:
            List[str]: Karakterdeki kural uyarılarının listesi (GM Override varsa boş döner).
        """
        # Soft-Block Check: If GM Override is enabled, bypass warnings
        if character.get("is_overridden") is True or character.get("gm_override") is True:
            return []

        warnings: List[str] = []
        level = character.get("level", 1)
        abilities = character.get("abilities", {})
        
        # Helper to safely extract stat scores
        def get_stat(stat_name: str) -> int:
            return abilities.get(stat_name, abilities.get(stat_name[:3], 10))

        str_score = get_stat("strength")
        dex_score = get_stat("dexterity")
        int_score = get_stat("intelligence")
        bab = character.get("bab", 0)

        # Rule 1: Base ability score limits (Point buy standard is 7-18 at level 1)
        if level == 1:
            for ability, score in abilities.items():
                if ability.lower() in self.CORE_ABILITIES and isinstance(score, int) and not (7 <= score <= 18):
                    warnings.append(f"PF1e başlangıç kurallarına göre yetenek puanları 7-18 arasında olmalıdır: {ability.title()} = {score}.")

        # Rule 2: Skill rank allocation warning (cannot allocate more ranks in a skill than character level)
        skill_ranks = character.get("skill_ranks", {})
        if skill_ranks:
            for skill, ranks in skill_ranks.items():
                if isinstance(ranks, int) and ranks > level:
                    warnings.append(f"Bir yeteneğe verilen puan ({ranks}) karakter seviyesini ({level}) aşamaz: {skill}.")

        # Rule 3: BAB limit for level 1
        if level == 1 and bab > 1:
            warnings.append(f"Seviye 1 Pathfinder karakterinin Temel Saldırı Bonusu (BAB) en fazla 1 olabilir (Mevcut: {bab}).")

        # Rule 4: Feat Prerequisite Verification
        feats = character.get("feats", [])
        feat_names_lower = {f.get("name", "").lower() if isinstance(f, dict) else str(f).lower() for f in feats}

        for feat_raw in feats:
            fname = feat_raw.get("name", "") if isinstance(feat_raw, dict) else str(feat_raw)
            fname_lower = fname.lower()

            if fname_lower in self.FEAT_PREREQUISITES:
                reqs = self.FEAT_PREREQUISITES[fname_lower]

                if "str" in reqs and str_score < reqs["str"]:
                    warnings.append(f"'{fname}' başarımını seçmek için Güç (STR) en az {reqs['str']} olmalıdır (Mevcut: {str_score}).")
                
                if "dex" in reqs and dex_score < reqs["dex"]:
                    warnings.append(f"'{fname}' başarımını seçmek için Çeviklik (DEX) en az {reqs['dex']} olmalıdır (Mevcut: {dex_score}).")

                if "int" in reqs and int_score < reqs["int"]:
                    warnings.append(f"'{fname}' başarımını seçmek için Zeka (INT) en az {reqs['int']} olmalıdır (Mevcut: {int_score}).")

                if "bab" in reqs and bab < reqs["bab"]:
                    warnings.append(f"'{fname}' başarımını seçmek için BAB en az +{reqs['bab']} olmalıdır (Mevcut: +{bab}).")

                if "feats" in reqs:
                    for req_f in reqs["feats"]:
                        if req_f not in feat_names_lower:
                            warnings.append(f"'{fname}' başarımını seçmek için öncelikle '{req_f.title()}' başarımına sahip olmalısınız.")

        # Rule 5: Trait Category Conflict Check
        traits = character.get("traits", [])
        seen_trait_categories: Set[str] = set()
        for trait in traits:
            cat = trait.get("trait_category", "").lower() if isinstance(trait, dict) else ""
            if cat and cat not in {"all", "general", "misc"}:
                if cat in seen_trait_categories:
                    warnings.append(f"PF1e kurallarına göre aynı kategoriden ({cat.title()}) birden fazla trait seçilemez.")
                seen_trait_categories.add(cat)

        return warnings

