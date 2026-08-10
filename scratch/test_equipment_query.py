import sqlite3
import json
import re

conn = sqlite3.connect('data/characters.db')
c = conn.cursor()

def test_category(cat_norm):
    where_clauses = ["sistem = 'pathfinder1e'", "kategori IN ('item','equipment')"]
    where_clauses.append("isim NOT LIKE '+%'")
    where_clauses.append("isim NOT LIKE '(%)%'")
    where_clauses.append("isim NOT LIKE '#%'")
    where_clauses.append("isim NOT LIKE '[%'")
    where_clauses.append("isim NOT LIKE '*%'")
    where_clauses.append("isim NOT LIKE '- %'")

    if cat_norm.startswith('weapon'):
        where_clauses.append("(sistem_verisi LIKE '%weapon%' OR isim LIKE '%sword%' OR isim LIKE '%axe%' OR isim LIKE '%bow%' OR isim LIKE '%dagger%' OR isim LIKE '%spear%' OR isim LIKE '%mace%' OR isim LIKE '%hammer%' OR isim LIKE '%flail%' OR isim LIKE '%staff%' OR isim LIKE '%blade%' OR isim LIKE '%pistol%' OR isim LIKE '%musket%' OR isim LIKE '%rifle%' OR isim LIKE '%crossbow%' OR isim LIKE '%scimitar%' OR isim LIKE '%rapier%' OR isim LIKE '%halberd%' OR isim LIKE '%lance%' OR isim LIKE '%club%')")
    elif cat_norm.startswith('armor'):
        where_clauses.append("(sistem_verisi LIKE '%armor%' OR sistem_verisi LIKE '%shield%' OR isim LIKE '%armor%' OR isim LIKE '%shield%' OR isim LIKE '%plate%' OR isim LIKE '%chainmail%' OR isim LIKE '%leather%' OR isim LIKE '%hauberk%' OR isim LIKE '%buckler%' OR isim LIKE '%cuirass%')")

    sql = "SELECT isim, sistem, kategori, aciklama, sistem_verisi FROM entities WHERE " + " AND ".join(where_clauses) + " ORDER BY isim COLLATE NOCASE"
    c.execute(sql)
    rows = c.fetchall()

    results = []
    VALID_TYPES = {"weapon", "armor", "equipment", "consumable", "gear", "shield", "loot"}

    for r in rows:
        name = r[0]
        payload = json.loads(r[4]) if r[4] else {}
        sys_obj = payload.get('system', {}) if isinstance(payload.get('system'), dict) else {}
        inner_type = str(sys_obj.get('type') or payload.get('type') or '').lower()
        if inner_type and inner_type not in VALID_TYPES:
            continue

        p_prof = str(sys_obj.get('weaponType') or sys_obj.get('armorType') or sys_obj.get('proficiency') or payload.get('proficiency') or payload.get('category') or '').lower()
        p_sub = str(sys_obj.get('subType') or sys_obj.get('equipmentSubtype') or '').lower()
        n_lower = name.lower()

        if cat_norm.startswith('weapon'):
            is_wep = inner_type == 'weapon' or 'weapon' in p_prof or 'weapon' in p_sub or re.search(r'\b(weapon|sword|greatsword|longsword|shortsword|rapier|scimitar|dagger|knife|axe|greataxe|handaxe|halberd|spear|lance|bow|longbow|shortbow|crossbow|mace|hammer|warhammer|flail|scythe|club|staff|blade|glaive|trident|katana|musket|pistol|blunderbuss|rifle|bullet|bolt|arrow)\b', n_lower)
            if not is_wep:
                continue
            if cat_norm == 'weapons_simple':
                if not ('simple' in p_prof or 'simple' in p_sub or re.search(r'\b(dagger|mace|spear|crossbow|club|staff|sickle|javelin|dart|sling)\b', n_lower)):
                    continue
            elif cat_norm == 'weapons_martial':
                if not ('martial' in p_prof or 'martial' in p_sub or re.search(r'\b(longsword|greatsword|greataxe|battleaxe|warhammer|rapier|scimitar|halberd|shortbow|longbow|lance|glaive|flail|falchion|kukri|starknife|trident)\b', n_lower)):
                    continue
            elif cat_norm == 'weapons_exotic':
                if not ('exotic' in p_prof or 'exotic' in p_sub or re.search(r'\b(katana|whip|nunchaku|shuriken|kama|bastard|sai|bolas|chain|hookhammer|waraxe|curve)\b', n_lower)):
                    continue
            elif cat_norm == 'weapons_firearm':
                if not ('firearm' in p_prof or 'ammo' in p_prof or re.search(r'\b(musket|pistol|blunderbuss|rifle|bullet|powder|ammo)\b', n_lower)):
                    continue

        elif cat_norm.startswith('armor'):
            is_arm = inner_type in ('armor', 'shield') or 'armor' in p_prof or 'shield' in p_prof or re.search(r'\b(armor|shield|leather|padded|studded|chainmail|breastplate|plate|splint|scale|hauberk|buckler)\b', n_lower)
            if not is_arm:
                continue
            if cat_norm == 'armor_light':
                if not ('light' in p_prof or 'light' in p_sub or re.search(r'\b(leather|padded|studded|hide|shirt)\b', n_lower)):
                    continue
            elif cat_norm == 'armor_medium':
                if not ('medium' in p_prof or 'medium' in p_sub or re.search(r'\b(hide|scale|chainmail|breastplate)\b', n_lower)):
                    continue
            elif cat_norm == 'armor_heavy':
                if not ('heavy' in p_prof or 'heavy' in p_sub or re.search(r'\b(splint|banded|half-plate|full plate|plate)\b', n_lower)):
                    continue
            elif cat_norm == 'armor_shield':
                if not (inner_type == 'shield' or 'shield' in p_prof or 'buckler' in n_lower or 'shield' in n_lower):
                    continue

        results.append(name)

    print(f"Category [{cat_norm}]: Total = {len(results)}. Sample: {results[:6]}")

for cat in ['weapons', 'weapons_simple', 'weapons_martial', 'weapons_exotic', 'weapons_firearm', 'armor', 'armor_light', 'armor_medium', 'armor_heavy', 'armor_shield']:
    test_category(cat)
