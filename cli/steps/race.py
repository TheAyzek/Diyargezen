from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class RaceStep(Step):
    name: str = "race"
    description: str = "Irk ve irksal özellikler"
    races: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.races:
            return StepResult(False, "Irk verisi bulunamadı.")
        race_name = select("Irk seç:", sorted(self.races.keys()), default=ctx.race)
        ctx.race = race_name
        race_data = self.races[race_name]
        ctx.features.extend(race_data.get("traits", []))
        ctx.metadata.setdefault("race", race_data)
        return StepResult(True, "Irk seçildi.")




