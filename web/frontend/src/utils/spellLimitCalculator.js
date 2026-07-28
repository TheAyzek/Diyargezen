/**
 * Pathfinder 1e Spell Limit & Max Spell Level Calculator
 * Computes maximum spell level available and maximum spells known/prepared
 * based on official Pathfinder 1e SRD rules.
 */

export function getMaxSpellLevel(className, level) {
  if (!className) return 1;
  const cls = className.toLowerCase().trim();
  const lvl = parseInt(level) || 1;

  // 4-Level Casters (Paladin, Ranger, Bloodrager)
  if (['paladin', 'ranger', 'bloodrager'].some(c => cls.includes(c))) {
    if (lvl < 4) return 0;
    return Math.min(4, Math.floor((lvl - 1) / 3));
  }

  // 6-Level Casters (Bard, Magus, Alchemist, Inquisitor, Summoner, Hunter, Investigator, Warpriest, Skald)
  if (['bard', 'magus', 'alchemist', 'inquisitor', 'summoner', 'hunter', 'investigator', 'warpriest', 'skald'].some(c => cls.includes(c))) {
    return Math.min(6, Math.floor((lvl + 2) / 3));
  }

  // Full 9-Level Casters (Wizard, Sorcerer, Cleric, Druid, Witch, Oracle, Arcanist, Shaman, Psychic)
  return Math.min(9, Math.ceil(lvl / 2));
}

export function getMaxSpellsAllowed(className, level, intWisMod = 0) {
  if (!className) return 4;
  const cls = className.toLowerCase().trim();
  const lvl = parseInt(level) || 1;
  const mod = parseInt(intWisMod) || 0;

  // Paladin / Ranger
  if (['paladin', 'ranger', 'bloodrager'].some(c => cls.includes(c))) {
    if (lvl < 4) return 0;
    return Math.max(1, lvl - 3 + (mod > 0 ? mod : 0));
  }

  // Spontaneous 6-Level / 9-Level Casters (Sorcerer, Bard, Oracle, Inquisitor, Summoner)
  if (['sorcerer', 'bard', 'oracle', 'inquisitor', 'summoner'].some(c => cls.includes(c))) {
    return Math.min(30, 4 + lvl * 2);
  }

  // Prepared Casters (Wizard, Alchemist, Witch, Cleric, Druid)
  return Math.max(4, 3 + (mod > 0 ? mod : 0) + (lvl - 1) * 2);
}
