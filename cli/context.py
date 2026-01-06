from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


def ability_modifier(score: int) -> int:
    """D&D 5e mod hesaplamasını tek bir yerde toplar."""
    return (score - 10) // 2


@dataclass
class AbilityBlock:
    scores: Dict[str, int] = field(default_factory=dict)
    modifiers: Dict[str, int] = field(default_factory=dict)

    def update_modifier(self, ability: str, value: int) -> None:
        self.scores[ability] = value
        self.modifiers[ability] = ability_modifier(value)

    def to_dict(self) -> Dict[str, Dict[str, int]]:
        return {"scores": self.scores, "modifiers": self.modifiers}


@dataclass
class CharacterContext:
    """CLI adımları arasında taşınacak tüm bilgileri saklar."""

    name: Optional[str] = None
    race: Optional[str] = None
    char_class: Optional[str] = None
    background: Optional[str] = None
    level: int = 1

    abilities: AbilityBlock = field(default_factory=AbilityBlock)
    languages: List[str] = field(default_factory=list)
    proficiencies: Dict[str, List[str]] = field(default_factory=lambda: {"skills": [], "tools": [], "weapons": []})
    equipment: List[str] = field(default_factory=list)
    spells: Dict[str, List[str]] = field(default_factory=dict)
    features: List[str] = field(default_factory=list)

    appearance: Dict[str, Any] = field(default_factory=dict)
    personality: Dict[str, str] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)

    def set_identity(self, *, name: str, race: str, char_class: str, background: str) -> None:
        self.name = name
        self.race = race
        self.char_class = char_class
        self.background = background

    def set_ability_scores(self, scores: Dict[str, int]) -> None:
        for ability, value in scores.items():
            self.abilities.update_modifier(ability, value)

    def add_equipment(self, items: List[str]) -> None:
        for item in items:
            if item not in self.equipment:
                self.equipment.append(item)

    def add_spell(self, level_key: str, spell_name: str) -> None:
        self.spells.setdefault(level_key, [])
        if spell_name not in self.spells[level_key]:
            self.spells[level_key].append(spell_name)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "race": self.race,
            "class": self.char_class,
            "background": self.background,
            "level": self.level,
            "abilities": self.abilities.to_dict(),
            "languages": self.languages,
            "proficiencies": self.proficiencies,
            "equipment": self.equipment,
            "spells": self.spells,
            "features": self.features,
            "appearance": self.appearance,
            "personality": self.personality,
            "metadata": self.metadata,
        }

