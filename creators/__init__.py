# creators/__init__.py
"""
Diyargezen TTRPG Creator Paketi
================================
Pathfinder 1st Edition (PF1e) Karakter Oluşturucu Modülü.
"""

__version__ = "2.0.0"
__author__ = "Diyargezen Team"

from .base_creator import CreatorFactory, CharacterFactory, BaseCharacterCreator
from .pathfinder1e_creator import Pathfinder1ECreator

# Pathfinder 1e (d20 system)
CreatorFactory.register("pathfinder1e", Pathfinder1ECreator)
CreatorFactory.register("pathfinder", Pathfinder1ECreator)
CreatorFactory.register("pf1e", Pathfinder1ECreator)

