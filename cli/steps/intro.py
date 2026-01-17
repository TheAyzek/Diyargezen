from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select, text
from .base import Step, StepResult


@dataclass
class IntroStep(Step):
    name: str = "intro"
    description: str = "İsim ve sınıf seçimi"
    classes: List[str] = None

    def __post_init__(self):
        if not self.classes:
            raise ValueError("IntroStep için sınıf listesi gerekiyor.")

    def run(self, ctx: CharacterContext) -> StepResult:
        name = text("Karakter ismi:", default=ctx.name or "")
        char_class = select("Sınıf seç:", self.classes, default=ctx.char_class)
        ctx.name = name.strip() or ctx.name
        ctx.char_class = char_class
        return StepResult(True, "İsim ve sınıf kaydedildi.")


from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select, text
from .base import Step, StepResult


@dataclass
class IntroStep(Step):
    name: str = "intro"
    description: str = "İsim ve sınıf seçimi"
    classes: List[str] = None

    def __post_init__(self):
        if not self.classes:
            raise ValueError("IntroStep için sınıf listesi gerekiyor.")

    def run(self, ctx: CharacterContext) -> StepResult:
        name = text("Karakter ismi:", default=ctx.name or "")
        char_class = select("Sınıf seç:", self.classes, default=ctx.char_class)
        ctx.name = name.strip() or ctx.name
        ctx.char_class = char_class
        return StepResult(True, "İsim ve sınıf kaydedildi.")


from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select, text
from .base import Step, StepResult


@dataclass
class IntroStep(Step):
    name: str = "intro"
    description: str = "İsim ve sınıf seçimi"
    classes: List[str] = None

    def __post_init__(self):
        if not self.classes:
            raise ValueError("IntroStep için sınıf listesi gerekiyor.")

    def run(self, ctx: CharacterContext) -> StepResult:
        name = text("Karakter ismi:", default=ctx.name or "")
        char_class = select("Sınıf seç:", self.classes, default=ctx.char_class)
        ctx.name = name.strip() or ctx.name
        ctx.char_class = char_class
        return StepResult(True, "İsim ve sınıf kaydedildi.")


from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import select, text
from .base import Step, StepResult


@dataclass
class IntroStep(Step):
    name: str = "intro"
    description: str = "İsim ve sınıf seçimi"
    classes: List[str] = None

    def __post_init__(self):
        if not self.classes:
            raise ValueError("IntroStep için sınıf listesi gerekiyor.")

    def run(self, ctx: CharacterContext) -> StepResult:
        name = text("Karakter ismi:", default=ctx.name or "")
        char_class = select("Sınıf seç:", self.classes, default=ctx.char_class)
        ctx.name = name.strip() or ctx.name
        ctx.char_class = char_class
        return StepResult(True, "İsim ve sınıf kaydedildi.")

