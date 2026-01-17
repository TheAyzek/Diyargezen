from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import checkbox, select
from .base import Step, StepResult


SPELLCASTING_CLASSES = [
    "Wizard",
    "Sorcerer",
    "Warlock",
    "Cleric",
    "Druid",
    "Bard",
    "Paladin",
    "Ranger",
    "Artificer",
    "Blood Hunter",
]


@dataclass
class SpellsStep(Step):
    name: str = "spells"
    description: str = "Sınıf büyülerini seç"
    classes: Dict[str, dict] = None
    all_spells: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        cls_name = ctx.char_class
        if not cls_name or not self.classes or cls_name not in self.classes:
            return StepResult(True, "Sınıf belirtilmedi, büyü adımı atlandı.")

        if cls_name not in SPELLCASTING_CLASSES:
            return StepResult(True, f"{cls_name} büyü kullanmaz, büyü adımı atlandı.")

        class_data = self.classes[cls_name]
        spell_map: Dict[str, List[str]] = class_data.get("spells") or {}
        if not spell_map:
            return StepResult(True, "Bu sınıf için büyü listesi tanımlı değil.")

        # Kullanıcı istediği seviye için büyü seçebilsin, bitirene kadar döngü
        keys = []
        labels = []
        if "cantrips" in spell_map:
            keys.append("cantrips")
            labels.append("Cantrip")
        for level_key in sorted(k for k in spell_map.keys() if k.startswith("level_")):
            lvl = level_key.split("_", 1)[1]
            keys.append(level_key)
            labels.append(f"{lvl}. Seviye")

        while True:
            choice_labels = labels + ["Bitti"]
            level_label = select("Hangi büyü seviyesinden seçim yapacaksınız?", choice_labels)
            if level_label == "Bitti":
                break

            key_index = labels.index(level_label)
            spell_key = keys[key_index]
            class_spells = spell_map.get(spell_key, [])
            if not class_spells:
                continue

            already = set(ctx.spells.get(spell_key, []))
            available = [s for s in class_spells if s not in already]
            if not available:
                continue

            picked = checkbox(
                f"{cls_name} için {level_label} büyülerini seç (boş bırakmak için sadece Enter):",
                available,
                min_selected=0,
            )
            for spell_name in picked:
                ctx.add_spell(spell_key, spell_name)

        return StepResult(True, "Büyü seçimi tamamlandı.")









from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import checkbox, select
from .base import Step, StepResult


SPELLCASTING_CLASSES = [
    "Wizard",
    "Sorcerer",
    "Warlock",
    "Cleric",
    "Druid",
    "Bard",
    "Paladin",
    "Ranger",
    "Artificer",
    "Blood Hunter",
]


@dataclass
class SpellsStep(Step):
    name: str = "spells"
    description: str = "Sınıf büyülerini seç"
    classes: Dict[str, dict] = None
    all_spells: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        cls_name = ctx.char_class
        if not cls_name or not self.classes or cls_name not in self.classes:
            return StepResult(True, "Sınıf belirtilmedi, büyü adımı atlandı.")

        if cls_name not in SPELLCASTING_CLASSES:
            return StepResult(True, f"{cls_name} büyü kullanmaz, büyü adımı atlandı.")

        class_data = self.classes[cls_name]
        spell_map: Dict[str, List[str]] = class_data.get("spells") or {}
        if not spell_map:
            return StepResult(True, "Bu sınıf için büyü listesi tanımlı değil.")

        # Kullanıcı istediği seviye için büyü seçebilsin, bitirene kadar döngü
        keys = []
        labels = []
        if "cantrips" in spell_map:
            keys.append("cantrips")
            labels.append("Cantrip")
        for level_key in sorted(k for k in spell_map.keys() if k.startswith("level_")):
            lvl = level_key.split("_", 1)[1]
            keys.append(level_key)
            labels.append(f"{lvl}. Seviye")

        while True:
            choice_labels = labels + ["Bitti"]
            level_label = select("Hangi büyü seviyesinden seçim yapacaksınız?", choice_labels)
            if level_label == "Bitti":
                break

            key_index = labels.index(level_label)
            spell_key = keys[key_index]
            class_spells = spell_map.get(spell_key, [])
            if not class_spells:
                continue

            already = set(ctx.spells.get(spell_key, []))
            available = [s for s in class_spells if s not in already]
            if not available:
                continue

            picked = checkbox(
                f"{cls_name} için {level_label} büyülerini seç (boş bırakmak için sadece Enter):",
                available,
                min_selected=0,
            )
            for spell_name in picked:
                ctx.add_spell(spell_key, spell_name)

        return StepResult(True, "Büyü seçimi tamamlandı.")











from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import checkbox, select
from .base import Step, StepResult


SPELLCASTING_CLASSES = [
    "Wizard",
    "Sorcerer",
    "Warlock",
    "Cleric",
    "Druid",
    "Bard",
    "Paladin",
    "Ranger",
    "Artificer",
    "Blood Hunter",
]


@dataclass
class SpellsStep(Step):
    name: str = "spells"
    description: str = "Sınıf büyülerini seç"
    classes: Dict[str, dict] = None
    all_spells: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        cls_name = ctx.char_class
        if not cls_name or not self.classes or cls_name not in self.classes:
            return StepResult(True, "Sınıf belirtilmedi, büyü adımı atlandı.")

        if cls_name not in SPELLCASTING_CLASSES:
            return StepResult(True, f"{cls_name} büyü kullanmaz, büyü adımı atlandı.")

        class_data = self.classes[cls_name]
        spell_map: Dict[str, List[str]] = class_data.get("spells") or {}
        if not spell_map:
            return StepResult(True, "Bu sınıf için büyü listesi tanımlı değil.")

        # Kullanıcı istediği seviye için büyü seçebilsin, bitirene kadar döngü
        keys = []
        labels = []
        if "cantrips" in spell_map:
            keys.append("cantrips")
            labels.append("Cantrip")
        for level_key in sorted(k for k in spell_map.keys() if k.startswith("level_")):
            lvl = level_key.split("_", 1)[1]
            keys.append(level_key)
            labels.append(f"{lvl}. Seviye")

        while True:
            choice_labels = labels + ["Bitti"]
            level_label = select("Hangi büyü seviyesinden seçim yapacaksınız?", choice_labels)
            if level_label == "Bitti":
                break

            key_index = labels.index(level_label)
            spell_key = keys[key_index]
            class_spells = spell_map.get(spell_key, [])
            if not class_spells:
                continue

            already = set(ctx.spells.get(spell_key, []))
            available = [s for s in class_spells if s not in already]
            if not available:
                continue

            picked = checkbox(
                f"{cls_name} için {level_label} büyülerini seç (boş bırakmak için sadece Enter):",
                available,
                min_selected=0,
            )
            for spell_name in picked:
                ctx.add_spell(spell_key, spell_name)

        return StepResult(True, "Büyü seçimi tamamlandı.")









from dataclasses import dataclass
from typing import Dict, List

from ..context import CharacterContext
from ..io import checkbox, select
from .base import Step, StepResult


SPELLCASTING_CLASSES = [
    "Wizard",
    "Sorcerer",
    "Warlock",
    "Cleric",
    "Druid",
    "Bard",
    "Paladin",
    "Ranger",
    "Artificer",
    "Blood Hunter",
]


@dataclass
class SpellsStep(Step):
    name: str = "spells"
    description: str = "Sınıf büyülerini seç"
    classes: Dict[str, dict] = None
    all_spells: Dict[str, dict] = None

    def run(self, ctx: CharacterContext) -> StepResult:
        cls_name = ctx.char_class
        if not cls_name or not self.classes or cls_name not in self.classes:
            return StepResult(True, "Sınıf belirtilmedi, büyü adımı atlandı.")

        if cls_name not in SPELLCASTING_CLASSES:
            return StepResult(True, f"{cls_name} büyü kullanmaz, büyü adımı atlandı.")

        class_data = self.classes[cls_name]
        spell_map: Dict[str, List[str]] = class_data.get("spells") or {}
        if not spell_map:
            return StepResult(True, "Bu sınıf için büyü listesi tanımlı değil.")

        # Kullanıcı istediği seviye için büyü seçebilsin, bitirene kadar döngü
        keys = []
        labels = []
        if "cantrips" in spell_map:
            keys.append("cantrips")
            labels.append("Cantrip")
        for level_key in sorted(k for k in spell_map.keys() if k.startswith("level_")):
            lvl = level_key.split("_", 1)[1]
            keys.append(level_key)
            labels.append(f"{lvl}. Seviye")

        while True:
            choice_labels = labels + ["Bitti"]
            level_label = select("Hangi büyü seviyesinden seçim yapacaksınız?", choice_labels)
            if level_label == "Bitti":
                break

            key_index = labels.index(level_label)
            spell_key = keys[key_index]
            class_spells = spell_map.get(spell_key, [])
            if not class_spells:
                continue

            already = set(ctx.spells.get(spell_key, []))
            available = [s for s in class_spells if s not in already]
            if not available:
                continue

            picked = checkbox(
                f"{cls_name} için {level_label} büyülerini seç (boş bırakmak için sadece Enter):",
                available,
                min_selected=0,
            )
            for spell_name in picked:
                ctx.add_spell(spell_key, spell_name)

        return StepResult(True, "Büyü seçimi tamamlandı.")












