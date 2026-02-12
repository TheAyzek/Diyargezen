# creators/base_creator.py
"""
Base Character Creator - Abstract Base Class
Tüm TTRPG sistemleri için ortak interface ve temel fonksiyonlar
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from pathlib import Path
import json


class BaseCharacterCreator(ABC):
    """Abstract base class for all TTRPG character creators"""

    def __init__(self, system_name: str, data_file: str):
        self.system_name = system_name
        self.data_file = data_file
        self.data = self._load_data()

    def _load_data(self) -> Dict[str, Any]:
        """Load system-specific data from JSON file"""
        data_path = Path(__file__).parent.parent / "data" / self.data_file
        with data_path.open("r", encoding="utf-8") as f:
            return json.load(f)

    @abstractmethod
    def create_character(self) -> Dict[str, Any]:
        """Create a new character for this system"""
        pass

    @abstractmethod
    def validate_character(self, character: Dict[str, Any]) -> List[str]:
        """Validate character data and return list of errors"""
        pass

    @abstractmethod
    def calculate_derived_stats(self, character: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate derived statistics (HP, AC, saves, etc.)"""
        pass

    def save_character(self, character: Dict[str, Any], filename: str) -> bool:
        """Save character to JSON file"""
        try:
            characters_dir = Path(__file__).parent.parent / "characters"
            characters_dir.mkdir(exist_ok=True)

            filepath = characters_dir / f"{filename}.json"
            with filepath.open("w", encoding="utf-8") as f:
                json.dump(character, f, indent=2, ensure_ascii=False)
            return True
        except Exception as e:
            print(f"Error saving character: {e}")
            return False

    def load_character(self, filename: str) -> Dict[str, Any]:
        """Load character from JSON file"""
        try:
            characters_dir = Path(__file__).parent.parent / "characters"
            filepath = characters_dir / f"{filename}.json"

            with filepath.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            raise FileNotFoundError(f"Character file {filename} not found")


class CharacterFactory:
    """Factory pattern for creating character creators"""

    _creators = {}

    @classmethod
    def register_creator(cls, system_key: str, creator_class):
        """Register a creator class for a system"""
        cls._creators[system_key.lower()] = creator_class

    @classmethod
    def create_creator(cls, system_key: str) -> BaseCharacterCreator:
        """Create a character creator instance for the given system"""
        system_key = system_key.lower()
        if system_key not in cls._creators:
            raise ValueError(f"Unknown system: {system_key}")

        return cls._creators[system_key]()

    @classmethod
    def get_available_systems(cls) -> List[str]:
        """Get list of available systems"""
        return list(cls._creators.keys())