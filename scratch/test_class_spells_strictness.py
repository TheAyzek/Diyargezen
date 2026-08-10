import sys
sys.path.insert(0, '.')
from pathlib import Path
from rules.character_manager import CharacterManager

cm = CharacterManager(Path("data/characters.db"))

print("--- TESTING CLASS SPELL EXCLUSIVITY ---")

wizard_spells = set(s.isim for s in cm.get_spells("pathfinder1e", caster_class="Wizard"))
cleric_spells = set(s.isim for s in cm.get_spells("pathfinder1e", caster_class="Cleric"))
druid_spells = set(s.isim for s in cm.get_spells("pathfinder1e", caster_class="Druid"))
paladin_spells = set(s.isim for s in cm.get_spells("pathfinder1e", caster_class="Paladin"))

print(f"Total Wizard Spells: {len(wizard_spells)}")
print(f"Total Cleric Spells: {len(cleric_spells)}")
print(f"Total Druid Spells: {len(druid_spells)}")
print(f"Total Paladin Spells: {len(paladin_spells)}")

print("\nChecking specific class exclusive spells:")
print(" - Fireball (Wizard exclusive vs Cleric/Druid):", "Fireball" in wizard_spells, "in Wizard |", "Fireball" in cleric_spells, "in Cleric |", "Fireball" in druid_spells, "in Druid")
print(" - Entangle (Druid exclusive vs Wizard/Cleric):", "Entangle" in druid_spells, "in Druid |", "Entangle" in wizard_spells, "in Wizard |", "Entangle" in cleric_spells, "in Cleric")
print(" - Cure Light Wounds (Cleric/Druid vs Wizard):", "Cure Light Wounds" in cleric_spells, "in Cleric |", "Cure Light Wounds" in druid_spells, "in Druid |", "Cure Light Wounds" in wizard_spells, "in Wizard")
