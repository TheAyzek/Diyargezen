from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class BackgroundStep(Step):
    name: str = "background"
    description: str = "Arka plan ve beceri profilleri"
    backgrounds: List[str] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.backgrounds:
            return StepResult(False, "Arka plan verisi yok.")
        picked = select("Arka plan seç:", choices=self.backgrounds)
        if not picked:
            return StepResult(False, "Arka plan seçilmedi.")
        ctx.background = picked
        # Örnek: arka plana bağlı beceri profilleri uygulama
        # (detailed mapping veri dosyasında tutulur)
        # Eğer profile'lar varsa ekle
        return StepResult(True, "Arka plan uygulandı.")











