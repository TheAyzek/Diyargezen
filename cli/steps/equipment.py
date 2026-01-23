from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

from ..context import CharacterContext
from ..io import checkbox
from .base import Step, StepResult


@dataclass
class EquipmentStep(Step):
    name: str = "equipment"
    description: str = "Başlangıç ekipmanı"
    equipment_data: Dict[str, Any] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.equipment_data:
            return StepResult(True, "Ekipman verisi yok.")
        options: List[str] = list(self.equipment_data.keys())
        picked = checkbox("Hangi başlangıç ekipmanını almak istersiniz?", choices=options)
        if not picked:
            return StepResult(True, "Hiçbir ekipman seçilmedi.")
        # Basit şekilde seçilen ekipmanları özellikler listesine ekleyelim
        for p in picked:
            if p not in ctx.features:
                ctx.features.append(p)
        return StepResult(True, "Ekipman seçimi kaydedildi.")












