/**
 * Universal Equipment Category Classifier for Diyargezen Web & Desktop
 * Classifies PF1e equipment entities into clean human-readable categories.
 */

export const EQUIPMENT_CATEGORIES = [
  { id: 'all', label: 'Tüm Ekipmanlar', icon: '🎒' },
  { id: 'weapons', label: '⚔ Silahlar', icon: '⚔' },
  { id: 'armor', label: '🛡 Zırhlar & Kalkanlar', icon: '🛡' },
  { id: 'potions', label: '🧪 İksirler & Simya', icon: '🧪' },
  { id: 'scrolls_wands', label: '📜 Parşömenler & Asalar', icon: '📜' },
  { id: 'rings_wondrous', label: '💍 Yüzükler & Takılar', icon: '💍' },
  { id: 'gear', label: '🎒 Maceracı Teçhizatı', icon: '🎒' }
];

export function getEquipmentCategory(item) {
  if (!item) return 'gear';

  const name = (item.isim || item.name || '').toLowerCase();
  const kat = (item.kategori || '').toLowerCase();
  const sv = item.sistem_verisi || {};
  const sys = sv.system || {};

  const eqType = (sys.equipmentType || sys.type || sv.equipment_type || '').toLowerCase();
  const eqSubtype = (sys.equipmentSubtype || sys.weaponSubtype || sys.slot || '').toLowerCase();

  // 1. Weapons
  if (kat === 'weapon' || eqType === 'weapon' || eqSubtype === 'martial' || eqSubtype === 'simple' || eqSubtype === 'exotic') {
    return 'weapons';
  }
  if (/\b(sword|greatsword|longsword|shortsword|rapier|scimitar|dagger|knife|axe|greataxe|handaxe|halberd|spear|lance|bow|longbow|shortbow|crossbow|mace|hammer|warhammer|flail|scythe|club|staff|blade|glaive|trident|katana|weapon)\b/i.test(name)) {
    return 'weapons';
  }

  // 2. Armor & Shields
  if (kat === 'armor' || eqType === 'armor' || eqSubtype === 'shield' || eqSubtype === 'light' || eqSubtype === 'medium' || eqSubtype === 'heavy') {
    return 'armor';
  }
  if (/\b(armor|armour|shield|buckler|chainmail|leather|plate|breastplate|helmet|helm|barding|greaves|cuirass|hauberk|gauntlet)\b/i.test(name)) {
    return 'armor';
  }

  // 3. Potions & Alchemy
  if (eqType === 'potion' || /\b(potion|elixir|oil|flask|vial|alchemist|antitoxin|brew|tonic)\b/i.test(name)) {
    return 'potions';
  }

  // 4. Scrolls, Wands, Rods, Staves
  if (eqType === 'scroll' || eqType === 'wand' || eqType === 'rod' || eqType === 'staff' || /\b(scroll|wand|rod|scepter|staff|grimoire|tome)\b/i.test(name)) {
    return 'scrolls_wands';
  }

  // 5. Rings & Wondrous Items
  if (eqType === 'ring' || eqType === 'wondrous' || ['ring', 'head', 'headband', 'neck', 'shoulders', 'body', 'chest', 'belt', 'wrists', 'hands', 'feet', 'eyes'].includes(eqSubtype)) {
    return 'rings_wondrous';
  }
  if (/\b(ring|amulet|necklace|cloak|belt|boots|bracers|pendant|diadem|crown|stone|ioun|talisman|emblem|tunic|robe|circlet|brooch)\b/i.test(name)) {
    return 'rings_wondrous';
  }

  // 6. Adventuring Gear & General Fallback
  return 'gear';
}
