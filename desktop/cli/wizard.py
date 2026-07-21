from __future__ import annotations

from typing import Iterable, List

from .context import CharacterContext
from .steps import Step, StepResult


class CharacterWizard:
    """Adım bazlı step yöneticisi."""

    def __init__(self, steps: Iterable[Step]):
        self.steps: List[Step] = list(steps)

    def run(self, ctx: CharacterContext) -> CharacterContext:
        for step in self.steps:
            result: StepResult = step.run(ctx)
            if not result.success:
                raise RuntimeError(result.message or f"{step.name} başarısız oldu.")
        return ctx
