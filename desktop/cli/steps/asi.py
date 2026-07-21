from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..context import CharacterContext
from ..io import checkbox
from .base import Step, StepResult


@dataclass
class AsiChoiceStep(Step):
    name: str = "asi_choice"
    description: str = "Ability Score Increase seçimleri"
    choices: List[str] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.choices:
            return StepResult(False, "ASI için seçenek yok.")
        selected = checkbox("Hangi yetenekleri artırmak istersiniz?", choices=self.choices)
        if not selected:
            return StepResult(False, "Hiçbir seçim yapılmadı.")
        for abil in selected:
            ctx.increase_ability(abil, 1)
        return StepResult(True, "Yetenek artışları uygulandı.")


@dataclass
class AsiIncreaseStep(Step):
    name: str = "asi_increase"
    description: str = "Doğrudan yetenek puanı artırma"
    amount: int = 2

    def run(self, ctx: CharacterContext) -> StepResult:
        top = sorted(ctx.get_ability_scores().items(), key=lambda kv: kv[1], reverse=True)
        for i in range(self.amount):
            abil = top[i % len(top)][0]
            ctx.increase_ability(abil, 1)
        return StepResult(True, "Yetenek artışları otomatik uygulandı.")












