from .base_validator import BaseValidator
from typing import Dict, Any, List

class PF1EValidator(BaseValidator):
    """Pathfinder 1e rule validator implementation."""

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
