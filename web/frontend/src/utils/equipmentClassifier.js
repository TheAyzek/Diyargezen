/**
 * Universal Equipment Category Classifier for Diyargezen Web & Desktop
 * Classifies PF1e equipment entities into clean human-readable categories & subcategories.
 */

export function isItemMagical(item) {
  if (!item) return false;
  if (item.is_magical === true || item.magical === true) return true;
  if (item.rarity === 'magic' || item.rarity === 'magical') return true;

  const sv = item.sistem_verisi || {};
  if (sv.is_magical === true || sv.magical === true) return true;
  if (sv.rarity === 'magic' || sv.rarity === 'magical') return true;
  if (parseInt(sv.enhancement || 0) > 0) return true;

  const kat = (item.kategori || '').toLowerCase();
  if (kat.includes('magic') || kat.includes('büyülü') || kat.includes('buyulu')) return true;

  const name = (item.isim || item.name || '').toLowerCase();
  if (/(\+\d+|büyülü|buyulu|magic|magical|flaming|keen|frost|shock|holy|unholy|bane|vorpal|defending|fortification|speed|ghost touch|wounding|enhancement|adamantine|mithral)/i.test(name)) {
    return true;
  }

  return false;
}

export const MAIN_EQUIPMENT_CATEGORIES = [
  { id: 'all', label: '🎒 Tüm Ekipmanlar', icon: '🎒' },
  { id: 'weapons_normal', label: '🗡 Normal Silahlar', icon: '🗡' },
  { id: 'weapons_magic', label: '✨ Büyülü Silahlar', icon: '✨' },
  { id: 'armor_normal', label: '🛡 Normal Zırhlar & Kalkanlar', icon: '🛡' },
  { id: 'armor_magic', label: '✨ Büyülü Zırhlar & Kalkanlar', icon: '✨' },
  { id: 'potions', label: '🧪 İksirler & Simya', icon: '🧪' },
  { id: 'scrolls_wands', label: '📜 Parşömenler & Asalar', icon: '📜' },
  { id: 'rings_wondrous', label: '💍 Yüzükler & Takılar', icon: '💍' },
  { id: 'tools', label: '🛠 Aletler & Kitler', icon: '🛠' },
  { id: 'mounts', label: '🐎 Binekler & Taşıtlar', icon: '🐎' },
  { id: 'gear', label: '⛺ Macera Teçhizatı', icon: '⛺' }
];

export const SUB_EQUIPMENT_CATEGORIES = {
  weapons: [
    { id: 'weapons', label: '⚔ Silahlar (Tümü)' },
    { id: 'weapons_normal', label: '🗡 Normal Silahlar' },
    { id: 'weapons_magic', label: '✨ Büyülü Silahlar' },
    { id: 'weapons_simple', label: '🗡 Basit Silahlar' },
    { id: 'weapons_martial', label: '⚔ Savaş Silahları' },
    { id: 'weapons_exotic', label: '🥷 Ezoterik / Özel Silahlar' },
    { id: 'weapons_firearm', label: '💥 Ateşli Silahlar & Mühimmat' },
    { id: 'weapons_siege', label: '🏰 Kuşatma Silahları' }
  ],
  armor: [
    { id: 'armor', label: '🛡 Zırhlar & Kalkanlar (Tümü)' },
    { id: 'armor_normal', label: '🛡 Normal Zırhlar & Kalkanlar' },
    { id: 'armor_magic', label: '✨ Büyülü Zırhlar & Kalkanlar' },
    { id: 'armor_light', label: '🎽 Hafif Zırhlar' },
    { id: 'armor_medium', label: '🛡 Orta Zırhlar' },
    { id: 'armor_heavy', label: '🧱 Ağır Zırhlar' },
    { id: 'armor_shield', label: '🛡 Kalkanlar' }
  ],
  potions: [
    { id: 'potions', label: '🧪 Tüm Simya & İksirler' },
    { id: 'potions_remedies', label: '🧪 Simyasal İlaçlar & Aletler' },
    { id: 'potions_weapons', label: '💥 Simyasal Silahlar & Maddeler' },
    { id: 'potions_elixirs', label: '🫙 İksirler & İksir Yağları' }
  ],
  scrolls_wands: [
    { id: 'scrolls_wands', label: '📜 Tüm Parşömen & Asalar' },
    { id: 'scrolls_scroll', label: '📜 Büyü Parşömenleri' },
    { id: 'scrolls_wand', label: '🪄 Büyü Asaları & Değnekler' },
    { id: 'scrolls_tome', label: '📖 Büyü Kitapları & Rehberler' }
  ],
  rings_wondrous: [
    { id: 'rings_wondrous', label: '💍 Tüm Yüzük & Takılar' },
    { id: 'rings_ring', label: '💍 Yüzükler' },
    { id: 'rings_accessories', label: '📿 Büyülü Aksesuarlar' },
    { id: 'rings_wondrous_items', label: '✨ Harika Büyülü Eşyalar' }
  ],
  tools: [
    { id: 'tools', label: '🛠 Tüm Aletler & Kitler' },
    { id: 'tools_kits', label: '🧰 Sınıf & Beceri Kitleri' },
    { id: 'tools_instruments', label: '🪕 Müzik Aletleri' },
    { id: 'tools_foci', label: '✝ Kutsal Semboller & Odaklar' }
  ],
  mounts: [
    { id: 'mounts', label: '🐎 Tüm Binek & Taşıtlar' },
    { id: 'mounts_pets', label: '🐎 Binekler & Evcil Hayvanlar' },
    { id: 'mounts_harness', label: '🛷 Hayvan Takımları & Semerler' },
    { id: 'mounts_vehicles', label: '⛵ Kara, Deniz & Hava Taşıtları' }
  ],
  gear: [
    { id: 'gear', label: '⛺ Tüm Macera Teçhizatı' },
    { id: 'gear_general', label: '⛺ Genel Macera Malzemeleri' },
    { id: 'gear_containers', label: '🎒 Konteyner & Çantalar' },
    { id: 'gear_clothing', label: '👘 Giysiler & Kıyafetler' },
    { id: 'gear_food', label: '🍖 Yiyecek, İçecek & Erzak' }
  ]
};

// Backward-compatible flat list export
export const EQUIPMENT_CATEGORIES = MAIN_EQUIPMENT_CATEGORIES;

export function getEquipmentCategory(item) {
  if (!item) return 'gear_general';

  const name = (item.isim || item.name || '').toLowerCase();
  const kat = (item.kategori || '').toLowerCase();
  const sv = item.sistem_verisi || {};
  const sys = sv.system || {};
  const flags = sv.flags || {};
  const dictCat = (flags.dictionary && flags.dictionary.Category) ? flags.dictionary.Category : '';

  const eqType = (sys.equipmentType || sys.type || sv.equipment_type || sv.type || '').toLowerCase();
  const eqSubtype = (sys.equipmentSubtype || sys.weaponSubtype || sys.slot || sv.subType || '').toLowerCase();
  const prof = (sv.proficiency || sv.category || dictCat || '').toLowerCase();
  const catText = (sv.category || sv.proficiency || dictCat || '').toLowerCase();
  const magical = isItemMagical(item);

  // 1. Weapons & Subcategories
  if (kat === 'weapon' || kat.startsWith('weapon') || kat === 'silah' || eqType === 'weapon' || eqSubtype === 'martial' || eqSubtype === 'simple' || eqSubtype === 'exotic' ||
      /\b(weapon|sword|greatsword|longsword|shortsword|rapier|scimitar|dagger|knife|axe|greataxe|handaxe|halberd|spear|lance|bow|longbow|shortbow|crossbow|mace|hammer|warhammer|flail|scythe|club|staff|blade|glaive|trident|katana|musket|pistol|blunderbuss|rifle|bullet|bolt|arrow|silah|kılıç|kilic|hançer|hancer|mızrak|mizrak|balta|gürz|gurz|yay|arbalet|tüfek|tufek|top)\b/i.test(name)) {
    
    if (kat === 'weapons_magic' || magical) {
      return 'weapons_magic';
    }
    if (kat === 'weapons_firearm' || prof.includes('firearm') || prof.includes('ammo') || catText.includes('firearm') || catText.includes('ammunition') || /\b(musket|pistol|blunderbuss|rifle|bullet|powder|ammo|tüfek|tufek|tabanca|kurşun|kursun|mermi|barut)\b/i.test(name)) {
      return 'weapons_firearm';
    }
    if (kat === 'weapons_siege' || prof.includes('siege') || catText.includes('siege') || /\b(siege|kuşatma|kusatma|mancınık|mancinik|top)\b/i.test(name)) {
      return 'weapons_siege';
    }
    if (kat === 'weapons_simple' || prof.includes('simple') || catText.includes('simple') || catText.includes('basit') || eqSubtype === 'simple' || /\b(dagger|club|mace|sickle|spear|quarterstaff|javelin|dart|sling|crossbow|hançer|hancer|gürz|gurz|mızrak|mizrak|orak|arbalet|sapan)\b/i.test(name)) {
      return 'weapons_simple';
    }
    if (kat === 'weapons_exotic' || prof.includes('exotic') || catText.includes('exotic') || catText.includes('ezoterik') || catText.includes('özel') || eqSubtype === 'exotic' || /\b(katana|whip|nunchaku|shuriken|bolas|kama|sai|urumi|katar|elven curve blade|dwarven waraxe|orc double axe|bastard sword|kamçı|kamci)\b/i.test(name)) {
      return 'weapons_exotic';
    }
    return 'weapons_normal';
  }

  // 2. Armor & Shields Subcategories
  if (kat === 'armor' || kat.startsWith('armor') || kat === 'zırh' || kat === 'zirh' || kat === 'kalkan' || eqType === 'armor' || eqSubtype === 'shield' || eqSubtype === 'light' || eqSubtype === 'medium' || eqSubtype === 'heavy' ||
      /\b(armor|armour|zırh|zirh|kalkan|shield|buckler|chainmail|leather|plate|breastplate|helmet|helm|barding|greaves|cuirass|hauberk|gauntlet|deri|zincir|göğüslük|gogusluk|pullu|halka|plaka|çivili|civili|kapitone|oluklu|bantlı|pantlı)\b/i.test(name)) {
    
    if (kat === 'armor_magic' || magical) {
      return 'armor_magic';
    }
    if (kat === 'armor_shield' || eqSubtype === 'shield' || catText.includes('shield') || catText.includes('kalkan') || /\b(shield|buckler|kalkan)\b/i.test(name)) {
      return 'armor_shield';
    }
    if (kat === 'armor_light' || catText.includes('light') || catText.includes('hafif') || eqSubtype === 'light' || /\b(padded|leather|chain shirt|stud|deri|çivili|civili|kapitone|hafif)\b/i.test(name)) {
      return 'armor_light';
    }
    if (kat === 'armor_heavy' || catText.includes('heavy') || catText.includes('ağır') || catText.includes('agir') || eqSubtype === 'heavy' || /\b(full plate|splint|half-plate|banded|plaka|tam plaka|yarım plaka|yarim plaka|oluklu|bantlı|bantli|ağır|agir)\b/i.test(name)) {
      return 'armor_heavy';
    }
    if (kat === 'armor_medium' || catText.includes('medium') || catText.includes('orta') || eqSubtype === 'medium' || /\b(breastplate|hide|scale|chainmail|zincir|göğüslük|gogusluk|pullu|kürk|post|orta)\b/i.test(name)) {
      return 'armor_medium';
    }
    return 'armor_normal';
  }

  // 3. Potions & Alchemy
  if (eqType === 'potion' || catText.includes('alchem') || catText.includes('remedy') || /\b(potion|elixir|oil|flask|vial|alchemist|antitoxin|brew|tonic|salve|tincture|concoction)\b/i.test(name)) {
    if (catText.includes('weapon') || /\b(alchemist's fire|acid|bomb|tanglefoot|holy water|thunderstone)\b/i.test(name)) {
      return 'potions_weapons';
    }
    if (eqType === 'potion' || /\b(potion|elixir|oil)\b/i.test(name)) {
      return 'potions_elixirs';
    }
    return 'potions_remedies';
  }

  // 4. Scrolls, Wands, Rods & Tomes
  if (eqType === 'scroll' || eqType === 'wand' || eqType === 'rod' || eqType === 'staff' || catText.includes('scroll') || catText.includes('wand') ||
      /\b(scroll|wand|rod|scepter|staff|grimoire|tome|spellbook|journal)\b/i.test(name)) {
    if (eqType === 'scroll' || /\b(scroll)\b/i.test(name)) return 'scrolls_scroll';
    if (eqType === 'wand' || eqType === 'rod' || /\b(wand|rod|scepter)\b/i.test(name)) return 'scrolls_wand';
    if (/\b(tome|grimoire|spellbook|book|journal)\b/i.test(name)) return 'scrolls_tome';
    return 'scrolls_scroll';
  }

  // 5. Rings & Wondrous Accessories
  if (eqType === 'ring' || eqType === 'wondrous' || ['ring', 'head', 'headband', 'neck', 'shoulders', 'body', 'chest', 'belt', 'wrists', 'hands', 'feet', 'eyes'].includes(eqSubtype) ||
      /\b(ring|amulet|necklace|cloak|belt|boots|bracers|pendant|diadem|crown|stone|ioun|talisman|emblem|tunic|robe|circlet|brooch)\b/i.test(name)) {
    if (eqType === 'ring' || /\b(ring)\b/i.test(name)) return 'rings_ring';
    if (/\b(amulet|necklace|cloak|belt|boots|bracers|pendant|diadem|crown|circlet)\b/i.test(name)) return 'rings_accessories';
    return 'rings_wondrous_items';
  }

  // 6. Tools, Kits & Foci
  if (catText.includes('tool') || catText.includes('kit') || catText.includes('foci') ||
      /\b(tool|kit|pouch|symbol|focus|instrument|lute|flute|harp|drum|thieves'|healer's)\b/i.test(name)) {
    if (/\b(lute|flute|harp|drum|horn|instrument|lyre|pipe)\b/i.test(name)) return 'tools_instruments';
    if (/\b(symbol|focus|foci|holy symbol)\b/i.test(name)) return 'tools_foci';
    if (catText.includes('kit') || /\b(kit|pouch|set|tools)\b/i.test(name)) return 'tools_kits';
    return 'tools_kits';
  }

  // 7. Mounts, Pets & Vehicles
  if (catText.includes('mount') || catText.includes('pet') || catText.includes('transport') || catText.includes('vehicle') ||
      /\b(horse|pony|dog|mule|camel|harness|saddle|cart|wagon|carriage|ship|boat|barding|feed)\b/i.test(name)) {
    if (/\b(cart|wagon|carriage|ship|boat|galley|vehicle|airship)\b/i.test(name)) return 'mounts_vehicles';
    if (/\b(harness|saddle|bridle|barding|bit and bridle)\b/i.test(name)) return 'mounts_harness';
    return 'mounts_pets';
  }

  // 8. Adventuring Gear, Containers & Food
  if (catText.includes('container') || /\b(backpack|bag|pouch|sack|chest|case|box|canteen|skin)\b/i.test(name)) {
    return 'gear_containers';
  }
  if (catText.includes('clothing') || /\b(outfit|robe|cloak|dress|boots|hat|cap|vest|tunic|clothes)\b/i.test(name)) {
    return 'gear_clothing';
  }
  if (catText.includes('food') || /\b(ration|rations|food|wine|ale|bread|meat|cheese|water)\b/i.test(name)) {
    return 'gear_food';
  }

  return 'gear_general';
}

export function matchesEquipmentSubfilter(itemCategory, selectedFilter, item) {
  if (!selectedFilter || selectedFilter === 'all') return true;
  if (selectedFilter === itemCategory) return true;
  
  const isMagic = isItemMagical(item);

  if (selectedFilter === 'weapons') return itemCategory.startsWith('weapons');
  if (selectedFilter === 'weapons_normal') return itemCategory.startsWith('weapons') && !isMagic;
  if (selectedFilter === 'weapons_magic') return itemCategory.startsWith('weapons') && isMagic;

  if (selectedFilter === 'armor') return itemCategory.startsWith('armor');
  if (selectedFilter === 'armor_normal') return itemCategory.startsWith('armor') && !isMagic;
  if (selectedFilter === 'armor_magic') return itemCategory.startsWith('armor') && isMagic;

  if (selectedFilter === 'potions') return itemCategory.startsWith('potions');
  if (selectedFilter === 'scrolls_wands') return itemCategory.startsWith('scrolls');
  if (selectedFilter === 'rings_wondrous') return itemCategory.startsWith('rings') || itemCategory.startsWith('wondrous') || itemCategory.startsWith('rings_');
  if (selectedFilter === 'tools') return itemCategory.startsWith('tools');
  if (selectedFilter === 'mounts') return itemCategory.startsWith('mounts');
  if (selectedFilter === 'gear') return itemCategory.startsWith('gear');

  return false;
}
