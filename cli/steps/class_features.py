from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from rich import print as rprint

from ..context import CharacterContext
from .base import Step, StepResult


@dataclass
class ClassFeaturesStep(Step):
    """Yeni seviye ile gelen sınıf özelliklerini uygular."""

    name: str = "class_features"
    description: str = "Yeni sınıf özellikleri"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf veya veri yok, class features atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi bulunamadı, class features atlandı.")

        features_by_level: Dict[str, Dict[str, List[str]]] = cls.get("class_features", {})
        if not features_by_level:
            return StepResult(True, "Bu sınıf için class_features tanımlı değil.")

        prev_level = int(ctx.metadata.get("previous_level", ctx.level or 1))
        new_level = ctx.level or 1

        gained: List[str] = []
        for lvl in range(prev_level + 1, new_level + 1):
            level_data = features_by_level.get(str(lvl), {})
            gained.extend(level_data.get("features", []))

        if not gained:
            return StepResult(True, "Bu level-up için yeni sınıf özelliği yok.")

        ctx.features.extend(gained)
        rprint("\n[bold cyan]Yeni Sınıf Özellikleri:[/bold cyan]")
        for feat in gained:
            rprint(f" • {feat}")

        return StepResult(True, "Sınıf özellikleri eklendi.")





