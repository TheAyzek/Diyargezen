from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class BackgroundStep(Step):
    name: str = "background"
    description: str = "Arka plan ve beceri profilleri"
    backgrounds: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.backgrounds:
            return StepResult(False, "Arka plan verisi bulunamadı.")
        bg_name = select("Arka plan seç:", sorted(self.backgrounds.keys()), default=ctx.background)
        ctx.background = bg_name
        bg = self.backgrounds[bg_name]
        skills = bg.get("skill_proficiencies", [])
        ctx.proficiencies.setdefault("skills", [])
        for skill in skills:
            if skill not in ctx.proficiencies["skills"]:
                ctx.proficiencies["skills"].append(skill)
        ctx.metadata.setdefault("background", bg)
        return StepResult(True, "Arka plan kaydedildi.")








from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class BackgroundStep(Step):
    name: str = "background"
    description: str = "Arka plan ve beceri profilleri"
    backgrounds: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.backgrounds:
            return StepResult(False, "Arka plan verisi bulunamadı.")
        bg_name = select("Arka plan seç:", sorted(self.backgrounds.keys()), default=ctx.background)
        ctx.background = bg_name
        bg = self.backgrounds[bg_name]
        skills = bg.get("skill_proficiencies", [])
        ctx.proficiencies.setdefault("skills", [])
        for skill in skills:
            if skill not in ctx.proficiencies["skills"]:
                ctx.proficiencies["skills"].append(skill)
        ctx.metadata.setdefault("background", bg)
        return StepResult(True, "Arka plan kaydedildi.")










from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class BackgroundStep(Step):
    name: str = "background"
    description: str = "Arka plan ve beceri profilleri"
    backgrounds: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.backgrounds:
            return StepResult(False, "Arka plan verisi bulunamadı.")
        bg_name = select("Arka plan seç:", sorted(self.backgrounds.keys()), default=ctx.background)
        ctx.background = bg_name
        bg = self.backgrounds[bg_name]
        skills = bg.get("skill_proficiencies", [])
        ctx.proficiencies.setdefault("skills", [])
        for skill in skills:
            if skill not in ctx.proficiencies["skills"]:
                ctx.proficiencies["skills"].append(skill)
        ctx.metadata.setdefault("background", bg)
        return StepResult(True, "Arka plan kaydedildi.")








from dataclasses import dataclass
from typing import Dict

from ..context import CharacterContext
from ..io import select
from .base import Step, StepResult


@dataclass
class BackgroundStep(Step):
    name: str = "background"
    description: str = "Arka plan ve beceri profilleri"
    backgrounds: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.backgrounds:
            return StepResult(False, "Arka plan verisi bulunamadı.")
        bg_name = select("Arka plan seç:", sorted(self.backgrounds.keys()), default=ctx.background)
        ctx.background = bg_name
        bg = self.backgrounds[bg_name]
        skills = bg.get("skill_proficiencies", [])
        ctx.proficiencies.setdefault("skills", [])
        for skill in skills:
            if skill not in ctx.proficiencies["skills"]:
                ctx.proficiencies["skills"].append(skill)
        ctx.metadata.setdefault("background", bg)
        return StepResult(True, "Arka plan kaydedildi.")











