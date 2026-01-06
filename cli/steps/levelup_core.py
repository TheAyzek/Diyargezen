from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext, ability_modifier
from ..io import select, text
from .base import Step, StepResult


@dataclass
class LevelSelectionStep(Step):
    """Mevcut seviye ve hedef seviye seçimi."""

    name: str = "level_select"
    description: str = "Seviye belirleme"

    def run(self, ctx: CharacterContext) -> StepResult:
        # Varsayılan mevcut seviye 1
        current_level = ctx.level or 1
        raw_current = text("Mevcut seviye:", default=str(current_level))
        if not raw_current.isdigit():
            return StepResult(False, "Mevcut seviye sayısal olmalı.")
        current_level = int(raw_current)
        if current_level < 1:
            current_level = 1

        # Hedef seviye
        raw_target = text("Yeni (hedef) seviye:", default=str(current_level + 1))
        if not raw_target.isdigit():
            return StepResult(False, "Hedef seviye sayısal olmalı.")
        target_level = int(raw_target)
        if target_level <= current_level:
            return StepResult(False, "Hedef seviye mevcut seviyeden büyük olmalı.")

        ctx.level = target_level
        ctx.metadata["previous_level"] = current_level
        return StepResult(True, "Seviye bilgisi güncellendi.")


@dataclass
class HitPointStep(Step):
    """Seviye artışına göre HP artışını hesaplar."""

    name: str = "hp"
    description: str = "HP artışı"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf bilgisi yok, HP adımı atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi bulunamadı, HP adımı atlandı.")

        hit_die = int(str(cls.get("hit_die", "8")).lstrip("dD") or 8)
        con_score = ctx.abilities.scores.get("constitution", 10)
        con_mod = ability_modifier(con_score)

        # Ortalama zar: (hit_die // 2) + 1
        avg_roll = (hit_die // 2) + 1
        hp_gain = avg_roll + con_mod
        if hp_gain < 1:
            hp_gain = 1

        # Kullanıcı isterse override edebilir
        raw = text(
            f"HP artışı (önerilen {hp_gain}, zar {hit_die} + CON {con_mod:+d}):",
            default=str(hp_gain),
        )
        if raw.isdigit():
            hp_gain = int(raw)

        ctx.metadata.setdefault("levelup", {})
        ctx.metadata["levelup"]["hp_gain"] = hp_gain
        return StepResult(True, "HP artışı kaydedildi.")





