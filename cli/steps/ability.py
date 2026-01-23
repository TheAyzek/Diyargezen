from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import text
from .base import Step, StepResult


POINT_COST = {8: 0, 9: 1, 10: 2, 11: 3, 12: 4, 13: 5, 14: 7, 15: 9}


@dataclass
class AbilityStep(Step):
    name: str = "ability"
    description: str = "Point-buy ile yetenek puanları"
    abilities: List[str] = None
    point_budget: int = 27

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.abilities:
            return StepResult(False, "Yetenek listesi bulunamadı.")

        while True:
            scores: Dict[str, int] = {}
            spent = 0
            for ability in self.abilities:
                raw = text(f"{ability} (8-15):", default="8")
                if not raw.isdigit():
                    return StepResult(False, "Geçersiz sayı girildi.")
                val = int(raw)
                if val < 8 or val > 15:
                    return StepResult(False, f"{ability} için 8-15 arası değer girilmeli.")
                spent += POINT_COST[val]
                scores[ability] = val
            if spent > self.point_budget:
                print(f"Harcanan puan {spent}, limit {self.point_budget}. Tekrar deneyin.")
                continue
            ctx.set_ability_scores(scores)
            ctx.metadata["point_buy_spent"] = spent
            return StepResult(True, "Yetenek puanları kaydedildi.")











