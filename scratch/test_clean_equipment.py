import sqlite3
import json
import re

conn = sqlite3.connect('data/characters.db')

def test_wep(category_name):
    c = conn.cursor()
    c.execute("""SELECT isim, aciklama, sistem_verisi FROM entities 
                 WHERE sistem='pathfinder1e' AND kategori IN ('item','equipment') 
                 AND isim NOT LIKE '+%' AND isim NOT LIKE '#%' AND isim NOT LIKE '[%' AND isim NOT LIKE '*%' 
                 AND isim NOT LIKE '%[Artifact]%' AND isim NOT LIKE '%[Cursed]%' AND isim NOT LIKE '%(Spellbook%' """)
    results = []
    for row in c.fetchall():
        name = row[0]
        desc = row[1] or ''
        payload = json.loads(row[2]) if row[2] else {}
        sys_obj = payload.get('system', {}) if isinstance(payload.get('system'), dict) else {}
        p_prof = (str(sys_obj.get('weaponType') or '') + ' ' + str(sys_obj.get('armorType') or '') + ' ' + str(sys_obj.get('proficiency') or '') + ' ' + str(payload.get('proficiency') or '') + ' ' + str(payload.get('category') or '') + ' ' + desc).lower()
        p_sub = str(sys_obj.get('subType') or sys_obj.get('equipmentSubtype') or '').lower()
        n_lower = name.lower()

        if category_name.startswith('weapon'):
            is_wep = 'weapon' in p_prof or 'weapon' in p_sub or sys_obj.get('type') == 'weapon' or re.search(r'\b(weapon|sword|greatsword|longsword|shortsword|rapier|scimitar|dagger|knife|axe|greataxe|handaxe|halberd|spear|lance|bow|longbow|shortbow|crossbow|mace|hammer|warhammer|flail|scythe|club|staff|blade|glaive|trident|katana|musket|pistol|blunderbuss|rifle|bullet|bolt|arrow)\b', n_lower)
            if not is_wep: continue
            if category_name == 'weapons_simple' and not ('simple' in p_prof or 'simple' in p_sub or re.search(r'\b(dagger|mace|spear|crossbow|club|staff|sickle|javelin|dart|sling)\b', n_lower)): continue
            if category_name == 'weapons_martial' and not ('martial' in p_prof or 'martial' in p_sub or re.search(r'\b(longsword|greatsword|greataxe|battleaxe|warhammer|rapier|scimitar|halberd|shortbow|longbow|lance|glaive|flail|falchion|kukri|starknife|trident)\b', n_lower)): continue
            if category_name == 'weapons_exotic' and not ('exotic' in p_prof or 'exotic' in p_sub or re.search(r'\b(katana|whip|nunchaku|shuriken|kama|bastard|sai|bolas|chain|hookhammer|waraxe|curve)\b', n_lower)): continue
            if category_name == 'weapons_firearm' and not ('firearm' in p_prof or 'ammo' in p_prof or re.search(r'\b(musket|pistol|blunderbuss|rifle|bullet|powder|ammo)\b', n_lower)): continue

        elif category_name.startswith('armor'):
            is_arm = 'armor' in p_prof or 'shield' in p_prof or sys_obj.get('type') in ('armor', 'shield') or p_sub in ('armor', 'shield') or re.search(r'\b(armor|shield|leather|padded|studded|chainmail|breastplate|plate|splint|scale|hauberk|buckler)\b', n_lower)
            if not is_arm: continue
            if category_name == 'armor_light' and not ('light' in p_prof or 'light' in p_sub or re.search(r'\b(leather|padded|studded|hide|shirt)\b', n_lower)): continue
            if category_name == 'armor_medium' and not ('medium' in p_prof or 'medium' in p_sub or re.search(r'\b(hide|scale|chainmail|breastplate)\b', n_lower)): continue
            if category_name == 'armor_heavy' and not ('heavy' in p_prof or 'heavy' in p_sub or re.search(r'\b(splint|banded|half-plate|full plate|plate)\b', n_lower)): continue
            if category_name == 'armor_shield' and not ('shield' in p_prof or 'shield' in p_sub or 'buckler' in n_lower or 'shield' in n_lower): continue

        results.append(name)
    print(f'Cat [{category_name:15s}]: count={len(results):4d} | sample={results[:8]}')

for c in ['weapons', 'weapons_simple', 'weapons_martial', 'weapons_exotic', 'weapons_firearm', 'armor', 'armor_light', 'armor_medium', 'armor_heavy', 'armor_shield']:
    test_wep(c)
