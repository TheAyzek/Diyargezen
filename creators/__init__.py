# creators/__init__.py
"""
Diyargezer TTRPG Creator Paketi
================================
Farklı RPG sistemleri için karakter oluşturucu modüllerini içerir.
Factory Pattern ile her sistem tek bir anahtarla erişilebilir.
"""

__version__ = "2.0.0"
__author__ = "Diyargezer Team"

from .base_creator import CreatorFactory, CharacterFactory, BaseCharacterCreator
from .dnd5e_creator import DND5ECreator
from .pathfinder1e_creator import Pathfinder1ECreator
from .vtm5e_creator import VTM5ECreator
from .mm3e_creator import MM3ECreator

# D&D 5e (d20 system)
CreatorFactory.register("dnd5e", DND5ECreator)
CreatorFactory.register("dungeonsanddragons", DND5ECreator)
CreatorFactory.register("d&d", DND5ECreator)

# Pathfinder 1e (d20 system)
CreatorFactory.register("pathfinder1e", Pathfinder1ECreator)
CreatorFactory.register("pathfinder", Pathfinder1ECreator)
CreatorFactory.register("pf1e", Pathfinder1ECreator)

# Vampire: The Masquerade 5e (d10 pool system)
CreatorFactory.register("vtm5e", VTM5ECreator)
CreatorFactory.register("vampire", VTM5ECreator)
CreatorFactory.register("vtm", VTM5ECreator)

# Mutants & Masterminds 3e (d20 system with d6 effect rolls)
CreatorFactory.register("mm3e", MM3ECreator)
CreatorFactory.register("mutantsandmasterminds", MM3ECreator)
CreatorFactory.register("m&m", MM3ECreator)
