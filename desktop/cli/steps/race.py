from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class RaceStep(Step):
    name: str = "race"
    description: str = "Irk ve irksal özellikler"
    races: Optional[List[str]] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.races:
            return StepResult(False, "Irk verisi yok.")
        picked = select("Irk seçin:", choices=self.races)
        if not picked:
            return StepResult(False, "Irk seçilmedi.")
        ctx.race = picked
        return StepResult(True, "Irk bilgisi kaydedildi.")











