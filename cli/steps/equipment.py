from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class EquipmentStep(Step):
    name: str = "equipment"
    description: str = "Başlangıç ekipmanı"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf belirlenmedi, ekipman atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi bulunamadı, ekipman atlandı.")

        options: List[List[str]] = cls.get("starting_equipment_options") or []
        if not options:
            return StepResult(True, "Bu sınıf için tanımlı ekipman seçeneği yok.")

        labels = [", ".join(opt) for opt in options]
        chosen_label = select("Başlangıç ekipmanını seç:", labels)
        idx = labels.index(chosen_label)
        chosen_items = options[idx]
        ctx.add_equipment(chosen_items)
        return StepResult(True, "Ekipman seçildi.")









from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class EquipmentStep(Step):
    name: str = "equipment"
    description: str = "Başlangıç ekipmanı"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf belirlenmedi, ekipman atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi bulunamadı, ekipman atlandı.")

        options: List[List[str]] = cls.get("starting_equipment_options") or []
        if not options:
            return StepResult(True, "Bu sınıf için tanımlı ekipman seçeneği yok.")

        labels = [", ".join(opt) for opt in options]
        chosen_label = select("Başlangıç ekipmanını seç:", labels)
        idx = labels.index(chosen_label)
        chosen_items = options[idx]
        ctx.add_equipment(chosen_items)
        return StepResult(True, "Ekipman seçildi.")











from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class EquipmentStep(Step):
    name: str = "equipment"
    description: str = "Başlangıç ekipmanı"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf belirlenmedi, ekipman atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi bulunamadı, ekipman atlandı.")

        options: List[List[str]] = cls.get("starting_equipment_options") or []
        if not options:
            return StepResult(True, "Bu sınıf için tanımlı ekipman seçeneği yok.")

        labels = [", ".join(opt) for opt in options]
        chosen_label = select("Başlangıç ekipmanını seç:", labels)
        idx = labels.index(chosen_label)
        chosen_items = options[idx]
        ctx.add_equipment(chosen_items)
        return StepResult(True, "Ekipman seçildi.")









from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class EquipmentStep(Step):
    name: str = "equipment"
    description: str = "Başlangıç ekipmanı"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf belirlenmedi, ekipman atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi bulunamadı, ekipman atlandı.")

        options: List[List[str]] = cls.get("starting_equipment_options") or []
        if not options:
            return StepResult(True, "Bu sınıf için tanımlı ekipman seçeneği yok.")

        labels = [", ".join(opt) for opt in options]
        chosen_label = select("Başlangıç ekipmanını seç:", labels)
        idx = labels.index(chosen_label)
        chosen_items = options[idx]
        ctx.add_equipment(chosen_items)
        return StepResult(True, "Ekipman seçildi.")











