from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from ..context import CharacterContext
from .base import Step, StepResult


@dataclass
class ClassFeaturesStep(Step):
    name: str = "class_features"
    description: str = "Sınıf özelliklerini karaktere uygular"
    classes: Dict[str, Any] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.classes:
            return StepResult(False, "Sınıf verisi bulunamadı.")
        cls = ctx.char_class
        if not cls:
            return StepResult(False, "Karakter sınıfı ayarlı değil.")
        features = self.classes.get(cls, {}).get("features", [])
        if features:
            for f in features:
                if f not in ctx.features:
                    ctx.features.append(f)
        return StepResult(True, "Sınıf özellikleri güncellendi.")












