from .base_validator import BaseValidator
from typing import Dict, Any, List

class DND5EValidator(BaseValidator):
    """D&D 5e rule validator implementation."""
    
    def __init__(self):
        super().__init__("D&D 5e")

    def validate(self, character: Dict[str, Any], system_data: Dict[str, Any]) -> List[str]:
        warnings = []
        level = character.get("level", 1)
        
        # Rule 1: Level cap of 20
        if level > 20:
            warnings.append(f"D&D 5e kurallarına göre karakter seviyesi en fazla 20 olabilir (Mevcut Seviye: {level}).")
            
        # Rule 2: Base ability score limits (typically max 20)
        abilities = character.get("abilities", {})
        for ability, score in abilities.items():
            if isinstance(score, int) and score > 20:
                warnings.append(f"D&D 5e başlangıç kurallarına göre yetenek puanları 20'yi aşmamalıdır: {ability.title()} = {score}.")
                
        # Rule 3: Multiclass level sum consistency
        if character.get("is_multiclass"):
            class_levels = character.get("class_levels", {})
            if class_levels:
                total_level = sum(class_levels.values())
                if total_level != level:
                    warnings.append(f"Multiclass sınıf seviyeleri toplamı ({total_level}) genel karakter seviyesi ({level}) ile uyuşmuyor.")
                    
        return warnings
