/**
 * Universal Equipment Category Classifier for Diyargezen Web & Desktop
 * Classifies PF1e equipment entities into clean human-readable categories & subcategories.
 */

export const MAIN_EQUIPMENT_CATEGORIES = [
  { id: 'all', label: '🎒 Tüm Ekipmanlar', icon: '🎒' },
  { id: 'weapons', label: '⚔ Silahlar', icon: '⚔' },
  { id: 'armor', label: '🛡 Zırhlar & Kalkanlar', icon: '🛡' },
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
    { id: 'weapons_simple', label: '🗡 Basit Silahlar' },
    { id: 'weapons_martial', label: '⚔ Savaş Silahları' },
    { id: 'weapons_exotic', label: '🥷 Ezoterik / Özel Silahlar' },
    { id: 'weapons_firearm', label: '💥 Ateşli Silahlar & Mühimmat' },
    { id: 'weapons_siege', label: '🏰 Kuşatma Silahları' }
  ],
  armor: [
    { id: 'armor', label: '🛡 Zırhlar & Kalkanlar (Tümü)' },
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

  // 1. Weapons & Subcategories
  if (kat === 'weapon' || eqType === 'weapon' || eqSubtype === 'martial' || eqSubtype === 'simple' || eqSubtype === 'exotic' ||
      /\b(weapon|sword|greatsword|longsword|shortsword|rapier|scimitar|dagger|knife|axe|greataxe|handaxe|halberd|spear|lance|bow|longbow|shortbow|crossbow|mace|hammer|warhammer|flail|scythe|club|staff|blade|glaive|trident|katana|musket|pistol|blunderbuss|rifle|bullet|bolt|arrow)\b/i.test(name)) {
    
    if (prof.includes('firearm') || prof.includes('ammo') || catText.includes('firearm') || catText.includes('ammunition') || /\b(musket|pistol|blunderbuss|rifle|bullet|powder|ammo)\b/i.test(name)) {
      return 'weapons_firearm';
    }
    if (prof.includes('siege') || catText.includes('siege')) {
      return 'weapons_siege';
    }
    if (prof.includes('simple') || catText.includes('simple') || eqSubtype === 'simple' || /\b(dagger|club|mace|sickle|spear|quarterstaff|javelin|dart|sling|crossbow)\b/i.test(name)) {
      return 'weapons_simple';
    }
    if (prof.includes('martial') || catText.includes('martial') || eqSubtype === 'martial' || /\b(longsword|greatsword|shortsword|rapier|scimitar|falchion|greataxe|battleaxe|handaxe|halberd|lance|longbow|shortbow|warhammer|flail|glaive|trident|ranseur|guisarme|bardiche|scythe)\b/i.test(name)) {
      return 'weapons_martial';
    }
    if (prof.includes('exotic') || catText.includes('exotic') || eqSubtype === 'exotic' || /\b(katana|whip|nunchaku|shuriken|bolas|kama|sai|urumi|katar|elven curve blade|dwarven waraxe|orc double axe|bastard sword)\b/i.test(name)) {
      return 'weapons_exotic';
    }
    return 'weapons_martial';
  }

  // 2. Armor & Shields Subcategories
  if (kat === 'armor' || eqType === 'armor' || eqSubtype === 'shield' || eqSubtype === 'light' || eqSubtype === 'medium' || eqSubtype === 'heavy' ||
      /\b(armor|armour|shield|buckler|chainmail|leather|plate|breastplate|helmet|helm|barding|greaves|cuirass|hauberk|gauntlet)\b/i.test(name)) {
    
    if (eqSubtype === 'shield' || catText.includes('shield') || /\b(shield|buckler)\b/i.test(name)) {
      return 'armor_shield';
    }
    if (catText.includes('light') || eqSubtype === 'light' || /\b(padded|leather|chain shirt|stud)\b/i.test(name)) {
      return 'armor_light';
    }
    if (catText.includes('medium') || eqSubtype === 'medium' || /\b(breastplate|hide|scale mail|chainmail)\b/i.test(name)) {
      return 'armor_medium';
    }
    if (catText.includes('heavy') || eqSubtype === 'heavy' || /\b(full plate|splint mail|half-plate|banded mail)\b/i.test(name)) {
      return 'armor_heavy';
    }
    return 'armor_medium';
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

export function matchesEquipmentSubfilter(itemCategory, selectedFilter) {
  if (!selectedFilter || selectedFilter === 'all') return true;
  if (selectedFilter === itemCategory) return true;
  
  if (selectedFilter === 'weapons' && itemCategory.startsWith('weapons')) return true;
  if (selectedFilter === 'armor' && itemCategory.startsWith('armor')) return true;
  if (selectedFilter === 'potions' && itemCategory.startsWith('potions')) return true;
  if (selectedFilter === 'scrolls_wands' && itemCategory.startsWith('scrolls')) return true;
  if (selectedFilter === 'rings_wondrous' && (itemCategory.startsWith('rings') || itemCategory.startsWith('wondrous') || itemCategory.startsWith('rings_'))) return true;
  if (selectedFilter === 'tools' && itemCategory.startsWith('tools')) return true;
  if (selectedFilter === 'mounts' && itemCategory.startsWith('mounts')) return true;
  if (selectedFilter === 'gear' && itemCategory.startsWith('gear')) return true;

  return false;
}
