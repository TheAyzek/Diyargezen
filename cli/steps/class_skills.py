from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List

from ..context import CharacterContext
from .base import Step, StepResult


@dataclass
class ClassSkillsStep(Step):
    name: str = "class_skills"
    description: str = "Sınıf yeteneklerini karaktere uygular"
    classes: Dict[str, Any] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not self.classes:
            return StepResult(False, "Sınıf verisi bulunamadı.")
        cls = ctx.char_class
        if not cls:
            return StepResult(False, "Karakter sınıfı ayarlı değil.")
        skills: List[str] = self.classes.get(cls, {}).get("skills", [])
        if skills:
            for s in skills:
                if s not in ctx.skills:
                    ctx.skills.append(s)
        return StepResult(True, "Sınıf yetenekleri eklendi.")












