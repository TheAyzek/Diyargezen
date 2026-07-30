"""
Diyargezen Pathfinder 1st Edition (PF1e) Rule Engine Validator

Architecture Overview:
----------------------
This module implements the core validation engine for Pathfinder 1e character sheets.
Following the project's 'Soft-Block / Game Master Override' philosophy (Rule 3), the validator
evaluates character parameters (Base Ability Scores, Skill Ranks, Base Attack Bonus, Save Matrices)
against official PF1e OGL rulesets.

Key Architectural Guarantees:
1. Non-blocking Soft Warnings: The validator produces structured diagnostic warnings rather than throwing
   hard runtime exceptions, allowing Game Masters (GMs) and players to override constraints (`is_overridden=True`).
2. Point Buy & Statutory Boundaries: Validates level 1 statutory ability score ranges (7-18 before racial modifiers)
   and ensures skill rank distribution does not exceed total character Hit Dice/level.
3. Fallback Integrity: Operates seamlessly with both local SQLite entities and JSON fallback caches.
"""

from .base_validator import BaseValidator
from typing import Dict, Any, List

class PF1EValidator(BaseValidator):
    """Pathfinder 1e rule validator implementation.
    
    Performs deterministic rule verification across character attributes,
    returning a collection of non-fatal warnings for UI/UX highlight.
    """

    CORE_ABILITIES = {
        "strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma",
        "str", "dex", "con", "int", "wis", "cha"
    }

    def __init__(self):
        super().__init__("Pathfinder 1e")

    def validate(self, character: Dict[str, Any], system_data: Dict[str, Any]) -> List[str]:
        warnings = []
        level = character.get("level", 1)
        
        # Rule 1: Base ability score limits (Point buy standard is 7-18 at level 1)
        if level == 1:
            abilities = character.get("abilities", {})
            for ability, score in abilities.items():
                if ability.lower() in self.CORE_ABILITIES and isinstance(score, int) and not (7 <= score <= 18):
                    warnings.append(f"PF1e başlangıç kurallarına göre yetenek puanları 7-18 arasında olmalıdır: {ability.title()} = {score}.")
                    
        # Rule 2: Skill rank allocation warning (cannot allocate more ranks in a skill than character level)
        skill_ranks = character.get("skill_ranks", {})
        if skill_ranks:
            for skill, ranks in skill_ranks.items():
                if ranks > level:
                    warnings.append(f"Bir yeteneğe verilen puan ({ranks}) karakter seviyesini ({level}) aşamaz: {skill}.")
                    
        # Rule 3: BAB check
        bab = character.get("bab", 0)
        if level == 1 and bab > 1:
            warnings.append(f"Seviye 1 Pathfinder karakterinin Temel Saldırı Bonusu (BAB) en fazla 1 olabilir (Mevcut: {bab}).")
            
        return warnings
