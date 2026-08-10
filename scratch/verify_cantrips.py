import sys
sys.path.insert(0, '.')
from pathlib import Path
from rules.character_manager import CharacterManager

cm = CharacterManager(Path("data/characters.db"))

for cls in ["Wizard", "Cleric", "Druid", "Bard", "Inquisitor", "Magus", "Witch"]:
    spells = cm.get_spells("pathfinder1e", level=0, caster_class=cls)
    print(f"Level 0 Spells for {cls}: {len(spells)} spells found!")
    print(f"   Sample: {[s.isim for s in spells[:8]]}\n")
