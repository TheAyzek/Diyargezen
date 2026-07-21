from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any

from ..context import CharacterContext
from ..io import text
from .base import Step, StepResult


@dataclass
class LevelSelectionStep(Step):
    name: str = "level_select"
    description: str = "Yeni seviye seçimi"

    def run(self, ctx: CharacterContext) -> StepResult:
        current = ctx.level or 1
        raw = text(f"Yeni seviye (mevcut: {current}):", default=str(current + 1))
        try:
            lvl = int(raw)
        except (TypeError, ValueError):
            return StepResult(False, "Geçersiz seviye.")
        if lvl <= current:
            return StepResult(False, "Seviye artışı olmalı.")
        ctx.level = lvl
        return StepResult(True, "Seviye güncellendi.")


@dataclass
class HitPointStep(Step):
    name: str = "hitpoint"
    description: str = "HP artışı hesaplama"
    classes: Dict[str, Any] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        # Basit yaklaşım: kullanıcıdan HP artışını al ve metadata'ya kaydet
        raw = text("Bu seviyede kazandığınız HP ne kadar?", default="0")
        try:
            hp_gain = int(raw)
        except (TypeError, ValueError):
            return StepResult(False, "Geçersiz HP değeri.")
        meta = ctx.metadata.setdefault("levelup", {})
        meta["hp_gain"] = hp_gain
        return StepResult(True, "HP artışı kaydedildi.")












