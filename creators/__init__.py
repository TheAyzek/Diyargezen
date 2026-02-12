# FRP Karakter Oluşturucu Modülleri
# Bu paket farklı rol yapma oyunu sistemleri için karakter oluşturucu modüllerini içerir

__version__ = "1.0.0"
__author__ = "Diyargezer Team"

# Import creators for factory registration
from .base_creator import CharacterFactory
from .dnd5e_creator import DND5ECreator
from .pathfinder1e_creator import Pathfinder1ECreator
from .vtm5e_creator import VTM5ECreator
from .mm3e_creator import MM3ECreator

# Register creators with factory
CharacterFactory.register_creator("dnd5e", DND5ECreator)
CharacterFactory.register_creator("dungeonsanddragons", DND5ECreator)
CharacterFactory.register_creator("d&d", DND5ECreator)

CharacterFactory.register_creator("pathfinder1e", Pathfinder1ECreator)
CharacterFactory.register_creator("pathfinder", Pathfinder1ECreator)
CharacterFactory.register_creator("pf1e", Pathfinder1ECreator)

CharacterFactory.register_creator("vtm5e", VTM5ECreator)
CharacterFactory.register_creator("vampire", VTM5ECreator)
CharacterFactory.register_creator("vtm", VTM5ECreator)

CharacterFactory.register_creator("mm3e", MM3ECreator)
CharacterFactory.register_creator("mutantsandmasterminds", MM3ECreator)
CharacterFactory.register_creator("m&m", MM3ECreator)
