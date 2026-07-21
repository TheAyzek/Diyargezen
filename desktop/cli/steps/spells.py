from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, Optional

from ..context import CharacterContext
from ..io import checkbox
from .base import Step, StepResult


@dataclass
class SpellsStep(Step):
    name: str = "spells"
    description: str = "Sınıf büyülerini seç"
    classes: Optional[Dict[str, Any]] = None
    all_spells: Optional[Dict[str, Any]] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        # Basit: kullanıcının sınıfına uygun büyüleri listeler ve seçimine izin verir
        cls = ctx.char_class
        if not cls:
            return StepResult(False, "Karakter sınıfı ayarlı değil.")
        class_info = (self.classes or {}).get(cls, {})
        available = class_info.get("spells", []) if class_info else []
        if not available:
            # fallback: tüm büyülerden cantrips/mantıklı bir set sun
            available = list((self.all_spells or {}).keys())[:20]
        picked = checkbox("Hangi büyüleri seçmek istersiniz?", choices=available)
        if picked:
            # organize spells by level in ctx.spells
            spells_by_level = ctx.spells or {}
            for p in picked:
                # default to cantrip if not present in data
                lvl = (self.all_spells or {}).get(p, {}).get("level", 0) if self.all_spells else 0
                key = "cantrips" if lvl == 0 else f"level{lvl}"
                spells_by_level.setdefault(key, []).append(p)
            ctx.spells = spells_by_level
        return StepResult(True, "Büyü seçimleri güncellendi.")












