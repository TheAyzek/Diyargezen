/**
 * Universal Equipment Category Classifier for Diyargezen Web & Desktop
 * Classifies PF1e equipment entities into clean human-readable categories.
 */

export const EQUIPMENT_CATEGORIES = [
  { id: 'all', label: 'Tüm Ekipmanlar', icon: '🎒' },
  { id: 'weapons', label: '⚔ Silahlar (Tümü)', icon: '⚔' },
  { id: 'weapons_simple', label: '🗡 Basit Silahlar', icon: '🗡' },
  { id: 'weapons_martial', label: '⚔ Savaş Silahları', icon: '⚔' },
  { id: 'weapons_exotic', label: '🥷 Ezoterik / Özel Silahlar', icon: '🥷' },
  { id: 'weapons_firearm', label: '💥 Ateşli Silahlar & Mühimmat', icon: '💥' },
  { id: 'weapons_siege', label: '🏰 Kuşatma Silahları', icon: '🏰' },
  { id: 'armor', label: '🛡 Zırhlar & Kalkanlar (Tümü)', icon: '🛡' },
  { id: 'armor_light', label: '🎽 Hafif Zırhlar', icon: '🎽' },
  { id: 'armor_medium', label: '🛡 Orta Zırhlar', icon: '🛡' },
  { id: 'armor_heavy', label: '🧱 Ağır Zırhlar', icon: '🧱' },
  { id: 'armor_shield', label: '🛡 Kalkanlar', icon: '🛡' },
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

  const eqType = (sys.equipmentType || sys.type || sv.equipment_type || sv.type || '').toLowerCase();
  const eqSubtype = (sys.equipmentSubtype || sys.weaponSubtype || sys.slot || sv.subType || '').toLowerCase();
  const prof = (sv.proficiency || sv.category || '').toLowerCase();
  const catText = (sv.category || '').toLowerCase();

  // 1. Weapons & Subcategories
  if (kat === 'weapon' || eqType === 'weapon' || eqSubtype === 'martial' || eqSubtype === 'simple' || eqSubtype === 'exotic' ||
      /\b(weapon|sword|greatsword|longsword|shortsword|rapier|scimitar|dagger|knife|axe|greataxe|handaxe|halberd|spear|lance|bow|longbow|shortbow|crossbow|mace|hammer|warhammer|flail|scythe|club|staff|blade|glaive|trident|katana|musket|pistol|blunderbuss|rifle|bullet|bolt|arrow)\b/i.test(name)) {
    
    if (prof.includes('firearm') || prof.includes('ammo') || catText.includes('firearm') || /\b(musket|pistol|blunderbuss|rifle|bullet|powder)\b/i.test(name)) {
      return 'weapons_firearm';
    }
    if (prof.includes('siege') || catText.includes('siege')) {
      return 'weapons_siege';
    }
    if (prof.includes('simple') || catText.includes('simple') || eqSubtype === 'simple') {
      return 'weapons_simple';
    }
    if (prof.includes('martial') || catText.includes('martial') || eqSubtype === 'martial') {
      return 'weapons_martial';
    }
    if (prof.includes('exotic') || catText.includes('exotic') || eqSubtype === 'exotic') {
      return 'weapons_exotic';
    }
    return 'weapons';
  }

  // 2. Armor & Shields Subcategories
  if (kat === 'armor' || eqType === 'armor' || eqSubtype === 'shield' || eqSubtype === 'light' || eqSubtype === 'medium' || eqSubtype === 'heavy' ||
      /\b(armor|armour|shield|buckler|chainmail|leather|plate|breastplate|helmet|helm|barding|greaves|cuirass|hauberk|gauntlet)\b/i.test(name)) {
    
    if (eqSubtype === 'shield' || catText.includes('shield') || /\b(shield|buckler)\b/i.test(name)) {
      return 'armor_shield';
    }
    if (catText.includes('light') || eqSubtype === 'light' || /\b(padded|leather|chain shirt)\b/i.test(name)) {
      return 'armor_light';
    }
    if (catText.includes('medium') || eqSubtype === 'medium' || /\b(breastplate|hide|scale mail)\b/i.test(name)) {
      return 'armor_medium';
    }
    if (catText.includes('heavy') || eqSubtype === 'heavy' || /\b(full plate|chainmail|splint mail|half-plate)\b/i.test(name)) {
      return 'armor_heavy';
    }
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
  if (eqType === 'ring' || eqType === 'wondrous' || ['ring', 'head', 'headband', 'neck', 'shoulders', 'body', 'chest', 'belt', 'wrists', 'hands', 'feet', 'eyes'].includes(eqSubtype) ||
      /\b(ring|amulet|necklace|cloak|belt|boots|bracers|pendant|diadem|crown|stone|ioun|talisman|emblem|tunic|robe|circlet|brooch)\b/i.test(name)) {
    return 'rings_wondrous';
  }

  return 'gear';
}

export function matchesEquipmentSubfilter(itemCategory, selectedFilter) {
  if (!selectedFilter || selectedFilter === 'all') return true;
  if (selectedFilter === itemCategory) return true;
  if (selectedFilter === 'weapons' && itemCategory.startsWith('weapons')) return true;
  if (selectedFilter === 'armor' && itemCategory.startsWith('armor')) return true;
  return false;
}
