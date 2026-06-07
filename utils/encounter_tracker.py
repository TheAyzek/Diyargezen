"""
Universal Encounter Tracker
Tum TTRPG sistemleri icin savas/encounter takip sistemi
D&D 5e, Pathfinder 1e, M&M 3e destegi
"""

import json
from typing import Dict, Any, List, Optional
from pathlib import Path
from datetime import datetime


# ============================================================================
# Sistem bazli combat kurallar
# ============================================================================

SYSTEM_RULES = {
    "dnd5e": {
        "name": "D&D 5e",
        "initiative_stat": "Dexterity",
        "initiative_formula": "DEX modifier + d20",
        "round_phases": ["Initiative", "Tur (Aksiyon, Bonus Aksiyon, Hareket)", "Reaksiyon"],
        "hp_based": True,
        "turn_actions": ["Aksiyon", "Bonus Aksiyon", "Hareket", "Reaksiyon", "Free Action"],
        "death_saves": True,
        "concentration": True,
    },
    "pathfinder1e": {
        "name": "Pathfinder 1e",
        "initiative_stat": "Dexterity",
        "initiative_formula": "DEX modifier + d20 + misc bonuses",
        "round_phases": ["Initiative", "Full-Round / Standard + Move", "Swift/Immediate"],
        "hp_based": True,
        "turn_actions": ["Full-Round Action", "Standard Action", "Move Action", "Swift Action", "Free Action", "Immediate Action"],
        "death_saves": False,  # PF1e'de dying farklı çalışır
        "concentration": True,
    },
    "mm3e": {
        "name": "Mutants & Masterminds 3e",
        "initiative_stat": "Agility",
        "initiative_formula": "Agility rank + d20",
        "round_phases": ["Initiative", "Standard + Move + Free"],
        "hp_based": False,  # M&M uses Toughness saves, not HP
        "turn_actions": ["Standard Action", "Move Action", "Free Action"],
        "death_saves": False,
        "concentration": True,
        "special": {
            "hero_points": True,
            "conditions_track": True,  # Bruised, Staggered, Incapacitated
        }
    },
}


class Combatant:
    """Encounter'daki bir katilimci"""

    def __init__(self, name: str, initiative: int = 0, system: str = "dnd5e",
                 max_hp: int = 0, current_hp: int = 0, ac: int = 10,
                 is_player: bool = True, notes: str = "", **kwargs):
        self.name = name
        self.initiative = initiative
        self.system = system
        self.max_hp = max_hp
        self.current_hp = current_hp
        self.ac = ac
        self.is_player = is_player
        self.notes = notes
        self.conditions: List[str] = []
        self.is_active = True
        self.death_saves = {"successes": 0, "failures": 0}
        self.concentration_spell = ""
        self.extra = kwargs  # Sisteme ozel ek veriler

    def take_damage(self, amount: int) -> str:
        """Hasar al"""
        self.current_hp = max(0, self.current_hp - amount)
        if self.current_hp == 0:
            if self.system == "dnd5e":
                return f"{self.name} bayildi! (Death Saves basliyor)"
            return f"{self.name} devre disi!"
        return f"{self.name}: {amount} hasar aldi (HP: {self.current_hp}/{self.max_hp})"

    def heal(self, amount: int) -> str:
        """Sifa al"""
        old_hp = self.current_hp
        self.current_hp = min(self.max_hp, self.current_hp + amount)
        healed = self.current_hp - old_hp
        return f"{self.name}: {healed} HP iyilesti (HP: {self.current_hp}/{self.max_hp})"

    def add_condition(self, condition: str):
        if condition not in self.conditions:
            self.conditions.append(condition)

    def remove_condition(self, condition: str):
        if condition in self.conditions:
            self.conditions.remove(condition)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "initiative": self.initiative,
            "system": self.system,
            "max_hp": self.max_hp,
            "current_hp": self.current_hp,
            "ac": self.ac,
            "is_player": self.is_player,
            "notes": self.notes,
            "conditions": self.conditions,
            "is_active": self.is_active,
            "death_saves": self.death_saves,
            "concentration_spell": self.concentration_spell,
            "extra": self.extra,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Combatant':
        c = cls(
            name=data.get("name", "Unknown"),
            initiative=data.get("initiative", 0),
            system=data.get("system", "dnd5e"),
            max_hp=data.get("max_hp", 0),
            current_hp=data.get("current_hp", 0),
            ac=data.get("ac", 10),
            is_player=data.get("is_player", True),
            notes=data.get("notes", ""),
        )
        c.conditions = data.get("conditions", [])
        c.is_active = data.get("is_active", True)
        c.death_saves = data.get("death_saves", {"successes": 0, "failures": 0})
        c.concentration_spell = data.get("concentration_spell", "")
        c.extra = data.get("extra", {})
        return c

    @classmethod
    def from_character(cls, character: Dict[str, Any]) -> 'Combatant':
        """Karakter verisinden Combatant olustur"""
        system = character.get("system", "dnd5e").lower()
        name = character.get("name", "Unknown")

        if system in ["dnd5e", "dnd", "d&d"]:
            hp = character.get("hit_points", character.get("hp", 10))
            ac = character.get("armor_class", 10)
            dex = character.get("abilities", {}).get("Dexterity", 10)
            init = (dex - 10) // 2
            return cls(name=name, initiative=init, system="dnd5e",
                       max_hp=hp, current_hp=hp, ac=ac, is_player=True)

        elif system in ["pathfinder1e", "pathfinder", "pf1e"]:
            hp = character.get("hit_points", character.get("hp", 10))
            ac = character.get("armor_class", 10)
            dex = character.get("abilities", {}).get("Dexterity", 10)
            init = (dex - 10) // 2
            return cls(name=name, initiative=init, system="pathfinder1e",
                       max_hp=hp, current_hp=hp, ac=ac, is_player=True)

        elif system in ["mm3e", "mutantsandmasterminds", "m&m"]:
            abilities = character.get("abilities", {})
            agility = abilities.get("Agility", 0)
            toughness = character.get("defenses", {}).get("Toughness", 0)
            return cls(name=name, initiative=agility, system="mm3e",
                       max_hp=0, current_hp=0, ac=0, is_player=True,
                       toughness=toughness,
                       hero_points=character.get("hero_points", 1))

        return cls(name=name, system=system, is_player=True)


class EncounterTracker:
    """Ana encounter takip motoru"""

    def __init__(self, system: str = "dnd5e"):
        self.system = system
        self.combatants: List[Combatant] = []
        self.current_round = 0
        self.current_turn_index = 0
        self.is_active = False
        self.log: List[str] = []
        self.created_at = datetime.now().isoformat()

    def add_combatant(self, combatant: Combatant):
        """Katilimci ekle"""
        self.combatants.append(combatant)
        self._log(f"+ {combatant.name} eklendi (Init: {combatant.initiative})")

    def remove_combatant(self, name: str):
        """Katilimci cikar"""
        self.combatants = [c for c in self.combatants if c.name != name]
        self._log(f"- {name} cikarildi")

    def add_monster(self, name: str, hp: int, ac: int = 10, initiative: int = 0):
        """Hizli canavar ekleme"""
        monster = Combatant(
            name=name, initiative=initiative, system=self.system,
            max_hp=hp, current_hp=hp, ac=ac, is_player=False
        )
        self.add_combatant(monster)

    def sort_by_initiative(self):
        """Initiative sirasina gore sirala (yuksekten dusuge)"""
        self.combatants.sort(key=lambda c: c.initiative, reverse=True)

    def start_encounter(self):
        """Encounter'i baslat"""
        self.sort_by_initiative()
        self.current_round = 1
        self.current_turn_index = 0
        self.is_active = True
        self._log(f"=== ENCOUNTER BASLADI (Round {self.current_round}) ===")
        if self.combatants:
            self._log(f"Sira: {self.combatants[0].name}")

    def next_turn(self) -> Optional[Combatant]:
        """Siradaki tura gec"""
        if not self.is_active or not self.combatants:
            return None

        self.current_turn_index += 1
        if self.current_turn_index >= len(self.combatants):
            self.current_turn_index = 0
            self.current_round += 1
            self._log(f"=== ROUND {self.current_round} ===")

        current = self.get_current_combatant()
        if current:
            status = f" [{'aktif' if current.is_active else 'devre disi'}]"
            hp_info = f" (HP: {current.current_hp}/{current.max_hp})" if current.max_hp > 0 else ""
            self._log(f"Sira: {current.name}{hp_info}{status}")

        return current

    def get_current_combatant(self) -> Optional[Combatant]:
        """Su anki tur sahibini dondur"""
        if not self.combatants or self.current_turn_index >= len(self.combatants):
            return None
        return self.combatants[self.current_turn_index]

    def apply_damage(self, target_name: str, amount: int) -> str:
        """Hedef'e hasar uygula"""
        for c in self.combatants:
            if c.name == target_name:
                result = c.take_damage(amount)
                self._log(result)
                return result
        return f"{target_name} bulunamadi"

    def apply_heal(self, target_name: str, amount: int) -> str:
        """Hedef'e sifa uygula"""
        for c in self.combatants:
            if c.name == target_name:
                result = c.heal(amount)
                self._log(result)
                return result
        return f"{target_name} bulunamadi"

    def end_encounter(self):
        """Encounter'i bitir"""
        self.is_active = False
        self._log(f"=== ENCOUNTER BITTI (Round {self.current_round}) ===")

    def get_initiative_order(self) -> List[Dict[str, Any]]:
        """Initiative sirasini dondur"""
        result = []
        for i, c in enumerate(self.combatants):
            entry = c.to_dict()
            entry["is_current_turn"] = (i == self.current_turn_index and self.is_active)
            result.append(entry)
        return result

    def _log(self, message: str):
        self.log.append(f"[R{self.current_round}] {message}")

    def to_dict(self) -> Dict[str, Any]:
        return {
            "system": self.system,
            "combatants": [c.to_dict() for c in self.combatants],
            "current_round": self.current_round,
            "current_turn_index": self.current_turn_index,
            "is_active": self.is_active,
            "log": self.log,
            "created_at": self.created_at,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'EncounterTracker':
        tracker = cls(system=data.get("system", "dnd5e"))
        tracker.combatants = [Combatant.from_dict(c) for c in data.get("combatants", [])]
        tracker.current_round = data.get("current_round", 0)
        tracker.current_turn_index = data.get("current_turn_index", 0)
        tracker.is_active = data.get("is_active", False)
        tracker.log = data.get("log", [])
        tracker.created_at = data.get("created_at", "")
        return tracker

    def save(self, filepath: Path):
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    @classmethod
    def load(cls, filepath: Path) -> 'EncounterTracker':
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return cls.from_dict(data)

