from __future__ import annotations

from dataclasses import dataclass
from typing import List, Optional

from ..context import CharacterContext
from ..io import text, select
from .base import Step, StepResult


@dataclass
class IntroStep(Step):
    name: str = "intro"
    description: str = "İsim ve sınıf seçimi"
    classes: Optional[List[str]] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        name = text("Karakter ismi:", default=ctx.name or "")
        if not name:
            return StepResult(False, "İsim girilmedi.")
        ctx.name = name

        if self.classes:
            picked = select("Sınıf seçin:", choices=self.classes)
            if not picked:
                return StepResult(False, "Sınıf seçilmedi.")
            ctx.char_class = picked
        return StepResult(True, "Giriş bilgileri kaydedildi.")

