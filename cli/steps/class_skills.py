from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import checkbox
from .base import Step, StepResult


@dataclass
class ClassSkillsStep(Step):
    name: str = "class_skills"
    description: str = "Sınıf beceri uzmanlıkları"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf belirtilmedi, sınıf becerileri atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi yok, beceriler atlandı.")

        all_class_skills: List[str] = cls.get("class_skills") or []
        choice_count: int = int(cls.get("skill_choices") or 0)

        if not all_class_skills or choice_count <= 0:
            return StepResult(True, "Bu sınıf için beceri seçimi tanımlı değil.")

        already = set(ctx.proficiencies.get("skills", []))
        available = [s for s in all_class_skills if s not in already]
        if not available:
            return StepResult(True, "Seçilebilir ek beceri kalmadı.")

        picked = checkbox(
            f"{ctx.char_class} için {choice_count} sınıf becerisi seç:",
            available,
            min_selected=choice_count,
            max_selected=choice_count,
        )

        ctx.proficiencies.setdefault("skills", [])
        for skill in picked:
            if skill not in ctx.proficiencies["skills"]:
                ctx.proficiencies["skills"].append(skill)

        return StepResult(True, "Sınıf becerileri seçildi.")









from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import checkbox
from .base import Step, StepResult


@dataclass
class ClassSkillsStep(Step):
    name: str = "class_skills"
    description: str = "Sınıf beceri uzmanlıkları"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf belirtilmedi, sınıf becerileri atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi yok, beceriler atlandı.")

        all_class_skills: List[str] = cls.get("class_skills") or []
        choice_count: int = int(cls.get("skill_choices") or 0)

        if not all_class_skills or choice_count <= 0:
            return StepResult(True, "Bu sınıf için beceri seçimi tanımlı değil.")

        already = set(ctx.proficiencies.get("skills", []))
        available = [s for s in all_class_skills if s not in already]
        if not available:
            return StepResult(True, "Seçilebilir ek beceri kalmadı.")

        picked = checkbox(
            f"{ctx.char_class} için {choice_count} sınıf becerisi seç:",
            available,
            min_selected=choice_count,
            max_selected=choice_count,
        )

        ctx.proficiencies.setdefault("skills", [])
        for skill in picked:
            if skill not in ctx.proficiencies["skills"]:
                ctx.proficiencies["skills"].append(skill)

        return StepResult(True, "Sınıf becerileri seçildi.")











from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import checkbox
from .base import Step, StepResult


@dataclass
class ClassSkillsStep(Step):
    name: str = "class_skills"
    description: str = "Sınıf beceri uzmanlıkları"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf belirtilmedi, sınıf becerileri atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi yok, beceriler atlandı.")

        all_class_skills: List[str] = cls.get("class_skills") or []
        choice_count: int = int(cls.get("skill_choices") or 0)

        if not all_class_skills or choice_count <= 0:
            return StepResult(True, "Bu sınıf için beceri seçimi tanımlı değil.")

        already = set(ctx.proficiencies.get("skills", []))
        available = [s for s in all_class_skills if s not in already]
        if not available:
            return StepResult(True, "Seçilebilir ek beceri kalmadı.")

        picked = checkbox(
            f"{ctx.char_class} için {choice_count} sınıf becerisi seç:",
            available,
            min_selected=choice_count,
            max_selected=choice_count,
        )

        ctx.proficiencies.setdefault("skills", [])
        for skill in picked:
            if skill not in ctx.proficiencies["skills"]:
                ctx.proficiencies["skills"].append(skill)

        return StepResult(True, "Sınıf becerileri seçildi.")









from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import checkbox
from .base import Step, StepResult


@dataclass
class ClassSkillsStep(Step):
    name: str = "class_skills"
    description: str = "Sınıf beceri uzmanlıkları"
    classes: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        if not ctx.char_class or not self.classes:
            return StepResult(True, "Sınıf belirtilmedi, sınıf becerileri atlandı.")

        cls = self.classes.get(ctx.char_class)
        if not cls:
            return StepResult(True, "Sınıf verisi yok, beceriler atlandı.")

        all_class_skills: List[str] = cls.get("class_skills") or []
        choice_count: int = int(cls.get("skill_choices") or 0)

        if not all_class_skills or choice_count <= 0:
            return StepResult(True, "Bu sınıf için beceri seçimi tanımlı değil.")

        already = set(ctx.proficiencies.get("skills", []))
        available = [s for s in all_class_skills if s not in already]
        if not available:
            return StepResult(True, "Seçilebilir ek beceri kalmadı.")

        picked = checkbox(
            f"{ctx.char_class} için {choice_count} sınıf becerisi seç:",
            available,
            min_selected=choice_count,
            max_selected=choice_count,
        )

        ctx.proficiencies.setdefault("skills", [])
        for skill in picked:
            if skill not in ctx.proficiencies["skills"]:
                ctx.proficiencies["skills"].append(skill)

        return StepResult(True, "Sınıf becerileri seçildi.")











