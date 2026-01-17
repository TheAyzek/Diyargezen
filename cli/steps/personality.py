from __future__ import annotations

from dataclasses import dataclass
from typing import List

from ..context import CharacterContext
from ..io import checkbox, text
from .base import Step, StepResult


@dataclass
class PersonalityStep(Step):
    name: str = "personality"
    description: str = "Diller, kişilik ve görünüm"
    available_languages: List[str] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        langs = []
        if self.available_languages:
            langs = checkbox("Ek dilleri seçin (En az 1)", self.available_languages, min_selected=1)

        ctx.languages = langs
        ctx.personality = {
            "trait": text("Personality Trait:", default=ctx.personality.get("trait", "")),
            "ideal": text("Ideal:", default=ctx.personality.get("ideal", "")),
            "bond": text("Bond:", default=ctx.personality.get("bond", "")),
            "flaw": text("Flaw:", default=ctx.personality.get("flaw", "")),
            "alignment": text("Alignment:", default=ctx.personality.get("alignment", "")),
        }
        ctx.appearance = {
            "height": text("Boy (örn 5'8\"):", default=ctx.appearance.get("height", "")),
            "weight": text("Kilo:", default=ctx.appearance.get("weight", "")),
            "age": text("Yaş:", default=ctx.appearance.get("age", "")),
            "hair": text("Saç rengi:", default=ctx.appearance.get("hair", "")),
            "eyes": text("Göz rengi:", default=ctx.appearance.get("eyes", "")),
            "skin": text("Ten rengi:", default=ctx.appearance.get("skin", "")),
            "description": text("Görünüm açıklaması:", default=ctx.appearance.get("description", "")),
        }
        return StepResult(True, "Kişisel bilgiler kaydedildi.")








from dataclasses import dataclass
from typing import List

from ..context import CharacterContext
from ..io import checkbox, text
from .base import Step, StepResult


@dataclass
class PersonalityStep(Step):
    name: str = "personality"
    description: str = "Diller, kişilik ve görünüm"
    available_languages: List[str] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        langs = []
        if self.available_languages:
            langs = checkbox("Ek dilleri seçin (En az 1)", self.available_languages, min_selected=1)

        ctx.languages = langs
        ctx.personality = {
            "trait": text("Personality Trait:", default=ctx.personality.get("trait", "")),
            "ideal": text("Ideal:", default=ctx.personality.get("ideal", "")),
            "bond": text("Bond:", default=ctx.personality.get("bond", "")),
            "flaw": text("Flaw:", default=ctx.personality.get("flaw", "")),
            "alignment": text("Alignment:", default=ctx.personality.get("alignment", "")),
        }
        ctx.appearance = {
            "height": text("Boy (örn 5'8\"):", default=ctx.appearance.get("height", "")),
            "weight": text("Kilo:", default=ctx.appearance.get("weight", "")),
            "age": text("Yaş:", default=ctx.appearance.get("age", "")),
            "hair": text("Saç rengi:", default=ctx.appearance.get("hair", "")),
            "eyes": text("Göz rengi:", default=ctx.appearance.get("eyes", "")),
            "skin": text("Ten rengi:", default=ctx.appearance.get("skin", "")),
            "description": text("Görünüm açıklaması:", default=ctx.appearance.get("description", "")),
        }
        return StepResult(True, "Kişisel bilgiler kaydedildi.")










from dataclasses import dataclass
from typing import List

from ..context import CharacterContext
from ..io import checkbox, text
from .base import Step, StepResult


@dataclass
class PersonalityStep(Step):
    name: str = "personality"
    description: str = "Diller, kişilik ve görünüm"
    available_languages: List[str] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        langs = []
        if self.available_languages:
            langs = checkbox("Ek dilleri seçin (En az 1)", self.available_languages, min_selected=1)

        ctx.languages = langs
        ctx.personality = {
            "trait": text("Personality Trait:", default=ctx.personality.get("trait", "")),
            "ideal": text("Ideal:", default=ctx.personality.get("ideal", "")),
            "bond": text("Bond:", default=ctx.personality.get("bond", "")),
            "flaw": text("Flaw:", default=ctx.personality.get("flaw", "")),
            "alignment": text("Alignment:", default=ctx.personality.get("alignment", "")),
        }
        ctx.appearance = {
            "height": text("Boy (örn 5'8\"):", default=ctx.appearance.get("height", "")),
            "weight": text("Kilo:", default=ctx.appearance.get("weight", "")),
            "age": text("Yaş:", default=ctx.appearance.get("age", "")),
            "hair": text("Saç rengi:", default=ctx.appearance.get("hair", "")),
            "eyes": text("Göz rengi:", default=ctx.appearance.get("eyes", "")),
            "skin": text("Ten rengi:", default=ctx.appearance.get("skin", "")),
            "description": text("Görünüm açıklaması:", default=ctx.appearance.get("description", "")),
        }
        return StepResult(True, "Kişisel bilgiler kaydedildi.")








from dataclasses import dataclass
from typing import List

from ..context import CharacterContext
from ..io import checkbox, text
from .base import Step, StepResult


@dataclass
class PersonalityStep(Step):
    name: str = "personality"
    description: str = "Diller, kişilik ve görünüm"
    available_languages: List[str] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        langs = []
        if self.available_languages:
            langs = checkbox("Ek dilleri seçin (En az 1)", self.available_languages, min_selected=1)

        ctx.languages = langs
        ctx.personality = {
            "trait": text("Personality Trait:", default=ctx.personality.get("trait", "")),
            "ideal": text("Ideal:", default=ctx.personality.get("ideal", "")),
            "bond": text("Bond:", default=ctx.personality.get("bond", "")),
            "flaw": text("Flaw:", default=ctx.personality.get("flaw", "")),
            "alignment": text("Alignment:", default=ctx.personality.get("alignment", "")),
        }
        ctx.appearance = {
            "height": text("Boy (örn 5'8\"):", default=ctx.appearance.get("height", "")),
            "weight": text("Kilo:", default=ctx.appearance.get("weight", "")),
            "age": text("Yaş:", default=ctx.appearance.get("age", "")),
            "hair": text("Saç rengi:", default=ctx.appearance.get("hair", "")),
            "eyes": text("Göz rengi:", default=ctx.appearance.get("eyes", "")),
            "skin": text("Ten rengi:", default=ctx.appearance.get("skin", "")),
            "description": text("Görünüm açıklaması:", default=ctx.appearance.get("description", "")),
        }
        return StepResult(True, "Kişisel bilgiler kaydedildi.")










