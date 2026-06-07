from .base_validator import BaseValidator
from typing import Dict, Any, List

class MM3EValidator(BaseValidator):
    """Mutants & Masterminds 3e rule validator implementation."""

    def __init__(self):
        super().__init__("Mutants & Masterminds 3e")

    def validate(self, character: Dict[str, Any], system_data: Dict[str, Any]) -> List[str]:
        warnings = []
        pl = character.get("pl_value", 10)
        
        # Rule 1: Power Points overflow (remaining points < 0)
        remaining = character.get("remaining_power_points", 0)
        if remaining < 0:
            warnings.append(f"Harcanan güç puanları sınırı aştı! Kalan güç puanı: {remaining}.")
            
        # Rule 2: Abilities PL cap (abilities shouldn't be extremely high for typical PL)
        abilities = character.get("abilities", {})
        for ability, score in abilities.items():
            if isinstance(score, int) and score > pl + 5:
                warnings.append(f"Yetenek puanı PL sınırına göre çok yüksek görünüyor: {ability.title()} = {score} (Limit ~{pl + 5}).")
                
        # Rule 3: Defense check (e.g. Toughness + Dodge/Parry PL constraints)
        defenses = character.get("defenses", {})
        toughness = defenses.get("Toughness", 0)
        dodge = defenses.get("Dodge", 0)
        if isinstance(toughness, int) and isinstance(dodge, int):
            if toughness + dodge > 2 * pl:
                warnings.append(f"Toughness ({toughness}) ve Dodge ({dodge}) toplamı PL sınırını ({2 * pl}) aşıyor.")
                
        return warnings
