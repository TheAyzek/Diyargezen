from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..context import CharacterContext
from ..io import checkbox, select
from ..utils.feats import calculate_available_feat_count
from .base import Step, StepResult


ASI_LEVELS = [4, 6, 8, 12, 14, 16, 19]


@dataclass
class AsiChoiceStep(Step):
    """ASI mi feat mi kararını ver."""

    name: str = "asi_choice"
    description: str = "ASI / Feat tercihi"

    def run(self, ctx: CharacterContext) -> StepResult:
        prev_level = int(ctx.metadata.get("previous_level", ctx.level or 1))
        new_level = ctx.level or 1

        # Yeni seviyeler içinde ASI seviyeleri var mı?
        asi_available = any(lvl in ASI_LEVELS for lvl in range(prev_level + 1, new_level + 1))

        # Seviye 1'de sadece Variant Human extra feat olabilir; ASI yok.
        if not asi_available and new_level not in ASI_LEVELS:
            ctx.metadata["asi_mode"] = "none"
            return StepResult(True, "Bu level-up için ASI/feat seçimi zorunlu değil.")

        choice = select(
            "Bu level-up için ne yapmak istersiniz?",
            ["Ability Score Increase (ASI)", "Feat", "Hiçbiri"],
        )
        if choice.startswith("Ability"):
            ctx.metadata["asi_mode"] = "ASI"
        elif choice.startswith("Feat"):
            ctx.metadata["asi_mode"] = "Feat"
        else:
            ctx.metadata["asi_mode"] = "none"

        return StepResult(True, "ASI/Feat tercihi kaydedildi.")


@dataclass
class AsiIncreaseStep(Step):
    """ASI seçildiyse ability skorlarını artır."""

    name: str = "asi_increase"
    description: str = "Ability Score Increase uygulaması"
    abilities: List[str] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        mode = ctx.metadata.get("asi_mode")
        if mode != "ASI":
            return StepResult(True, "ASI seçilmedi, adım atlandı.")

        if not self.abilities:
            return StepResult(False, "Yetenek listesi bulunamadı.")

        picked = checkbox(
            "Hangi ability skorlarını +1 yapmak istiyorsunuz? (1 veya 2 seçim)",
            self.abilities,
            min_selected=1,
            max_selected=2,
        )

        for ability in picked:
            current = ctx.abilities.scores.get(ability, 10)
            ctx.abilities.update_modifier(ability, current + 1)

        return StepResult(True, "ASI uygulandı.")





