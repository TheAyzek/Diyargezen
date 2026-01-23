from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

from ..context import CharacterContext
from ..io import checkbox
from .base import Step, StepResult


@dataclass
class FeatsStep(Step):
    name: str = "feats"
    description: str = "Feat seçimleri"
    feats_data: Dict[str, Any] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.feats_data:
            return StepResult(True, "Feat verisi yok.")
        options: List[str] = list(self.feats_data.keys())
        if not options:
            return StepResult(True, "Kullanılabilir feat yok.")
        picked = checkbox("Hangi feat(ler) uygulanacak?", choices=options)
        if not picked:
            return StepResult(True, "Hiçbir feat seçilmedi.")
        for p in picked:
            if p not in ctx.features:
                ctx.features.append(p)
        return StepResult(True, "Featler uygulandı.")


