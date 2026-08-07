import sqlite3
import json
import re

CANTRIP_CLASS_MAP = {
    # Arcane Cantrips (Wizard, Sorcerer, Arcanist, Magus, Witch, Bard)
    "acid splash": ["Arcanist", "Sorcerer", "Wizard", "Magus", "Inquisitor", "Summoner"],
    "arcane mark": ["Arcanist", "Sorcerer", "Wizard", "Magus", "Witch", "Bard", "Summoner"],
    "bleed": ["Cleric", "Oracle", "Warpriest", "Inquisitor", "Witch", "Sorcerer", "Wizard", "Arcanist", "Medium", "Mesmerist", "Occultist", "Psychic", "Shaman", "Spiritualist"],
    "breeze": ["Arcanist", "Sorcerer", "Wizard", "Druid", "Witch"],
    "claws of darkness": ["Sorcerer", "Wizard", "Arcanist", "Witch"],
    "daze": ["Arcanist", "Sorcerer", "Wizard", "Bard", "Inquisitor", "Magus", "Witch", "Mesmerist"],
    "dancing lights": ["Arcanist", "Sorcerer", "Wizard", "Bard", "Witch", "Magus"],
    "detect magic": ["Arcanist", "Sorcerer", "Wizard", "Cleric", "Oracle", "Warpriest", "Druid", "Bard", "Inquisitor", "Magus", "Witch", "Shaman", "Summoner", "Psychic"],
    "detect poison": ["Cleric", "Oracle", "Warpriest", "Druid", "Paladin", "Ranger", "Sorcerer", "Wizard", "Arcanist", "Inquisitor", "Witch", "Shaman"],
    "disrupt undead": ["Arcanist", "Sorcerer", "Wizard", "Magus", "Inquisitor"],
    "flare": ["Arcanist", "Sorcerer", "Wizard", "Bard", "Druid", "Magus"],
    "ghost sound": ["Arcanist", "Sorcerer", "Wizard", "Bard", "Magus", "Witch"],
    "jolt": ["Arcanist", "Sorcerer", "Wizard", "Magus"],
    "light": ["Arcanist", "Sorcerer", "Wizard", "Cleric", "Oracle", "Warpriest", "Druid", "Bard", "Inquisitor", "Magus", "Witch", "Shaman"],
    "lullaby": ["Bard", "Mesmerist", "Witch"],
    "mage hand": ["Arcanist", "Sorcerer", "Wizard", "Bard", "Magus", "Summoner"],
    "mending": ["Arcanist", "Sorcerer", "Wizard", "Cleric", "Oracle", "Warpriest", "Druid", "Bard", "Inquisitor", "Magus", "Witch", "Shaman"],
    "message": ["Arcanist", "Sorcerer", "Wizard", "Bard", "Witch"],
    "open/close": ["Arcanist", "Sorcerer", "Wizard", "Bard", "Magus", "Summoner"],
    "penumbra": ["Arcanist", "Sorcerer", "Wizard", "Cleric", "Oracle", "Witch"],
    "prestidigitation": ["Arcanist", "Sorcerer", "Wizard", "Bard", "Magus"],
    "ray of frost": ["Arcanist", "Sorcerer", "Wizard", "Magus"],
    "read magic": ["Arcanist", "Sorcerer", "Wizard", "Cleric", "Oracle", "Warpriest", "Druid", "Bard", "Inquisitor", "Magus", "Witch", "Shaman", "Paladin", "Ranger"],
    "resistance": ["Arcanist", "Sorcerer", "Wizard", "Cleric", "Oracle", "Warpriest", "Druid", "Bard", "Inquisitor", "Magus", "Witch", "Paladin"],
    "root": ["Druid", "Ranger", "Witch"],
    "scoop": ["Arcanist", "Sorcerer", "Wizard", "Bard"],
    "spark": ["Arcanist", "Sorcerer", "Wizard", "Cleric", "Oracle", "Druid", "Bard", "Inquisitor", "Magus", "Witch"],
    "touch of fatigue": ["Arcanist", "Sorcerer", "Wizard", "Witch", "Magus"],
    
    # Divine Orisons (Cleric, Oracle, Warpriest, Druid, Hunter, Inquisitor)
    "brand": ["Inquisitor"],
    "brand, greater": ["Inquisitor"],
    "create water": ["Cleric", "Oracle", "Warpriest", "Druid", "Hunter", "Paladin"],
    "guidance": ["Cleric", "Oracle", "Warpriest", "Druid", "Hunter", "Inquisitor", "Shaman", "Witch"],
    "know direction": ["Druid", "Hunter", "Bard"],
    "purify food and drink": ["Cleric", "Oracle", "Warpriest", "Druid", "Hunter"],
    "sift": ["Inquisitor", "Bard"],
    "stabilize": ["Cleric", "Oracle", "Warpriest", "Druid", "Hunter", "Inquisitor", "Shaman"],
    "summon instrument": ["Bard"],
    "virtue": ["Cleric", "Oracle", "Warpriest", "Druid", "Paladin", "Inquisitor"]
}

CLASS_NAME_VARIANTS = {
    "arcanist": "Arcanist", "barbarian": "Barbarian", "bard": "Bard", "bloodrager": "Bloodrager",
    "cleric": "Cleric", "druid": "Druid", "hunter": "Hunter", "inquisitor": "Inquisitor",
    "investigator": "Investigator", "magus": "Magus", "oracle": "Oracle", "paladin": "Paladin",
    "ranger": "Ranger", "shaman": "Shaman", "sorcerer": "Sorcerer", "summoner": "Summoner",
    "warpriest": "Warpriest", "witch": "Witch", "wizard": "Wizard", "alchemist": "Alchemist"
}

def enrich_cantrip_db():
    conn = sqlite3.connect('data/characters.db')
    cur = conn.cursor()

    cur.execute("SELECT id, isim, siniflar, aciklama FROM spells WHERE seviye = 0")
    rows = cur.fetchall()

    spell_updates = []

    for spell_id, name, siniflar_raw, desc in rows:
        name_clean = name.lower().strip()
        classes_dict = {}

        if siniflar_raw and siniflar_raw.startswith('{'):
            try:
                parsed = json.loads(siniflar_raw)
                if isinstance(parsed, dict) and len(parsed) > 0:
                    classes_dict = parsed
            except Exception:
                pass

        if not classes_dict and name_clean in CANTRIP_CLASS_MAP:
            for cls in CANTRIP_CLASS_MAP[name_clean]:
                classes_dict[cls] = 0

        if not classes_dict and desc:
            m = re.search(r'(?:class(?:es)?|sınıf(?:lar)?)\s*[:\(]?\s*([a-zA-Z\s,]+)[\)\n\.]?', desc, re.IGNORECASE)
            if m:
                found_str = m.group(1).lower()
                for c_key, c_name in CLASS_NAME_VARIANTS.items():
                    if c_key in found_str:
                        classes_dict[c_name] = 0

        if not classes_dict:
            classes_dict = {
                "Arcanist": 0, "Sorcerer": 0, "Wizard": 0, "Bard": 0,
                "Cleric": 0, "Oracle": 0, "Warpriest": 0, "Druid": 0,
                "Inquisitor": 0, "Magus": 0, "Witch": 0, "Shaman": 0
            }

        spell_updates.append((json.dumps(classes_dict), spell_id))

    cur.executemany("UPDATE spells SET siniflar = ? WHERE id = ?", spell_updates)
    conn.commit()

    # Now update entities table using executemany / fast batch
    cur.execute("SELECT isim, siniflar, aciklama FROM spells WHERE seviye = 0")
    cantrip_rows = cur.fetchall()

    entity_inserts = []
    
    # First, get existing spell names in entities
    cur.execute("SELECT LOWER(isim) FROM entities WHERE kategori = 'spell'")
    existing_entities = set(r[0] for r in cur.fetchall())

    for c_name, c_siniflar, c_desc in cantrip_rows:
        c_name_lower = c_name.lower().strip()
        try:
            cls_dict = json.loads(c_siniflar)
        except Exception:
            cls_dict = {"Wizard": 0, "Cleric": 0, "Druid": 0, "Sorcerer": 0, "Bard": 0}

        sv_data = {
            "name": c_name,
            "level": 0,
            "spell_level": 0,
            "seviye": 0,
            "school": "Universal",
            "description": c_desc or f"{c_name} (Level 0 Cantrip)",
            "levels_by_class": cls_dict
        }
        sv_json = json.dumps(sv_data)

        if c_name_lower not in existing_entities:
            entity_inserts.append((c_name, 'pathfinder1e', 'spell', c_desc or f"{c_name} (Level 0 Cantrip)", sv_json))
            existing_entities.add(c_name_lower)

    if entity_inserts:
        cur.executemany(
            "INSERT INTO entities (isim, sistem, kategori, aciklama, sistem_verisi) VALUES (?, ?, ?, ?, ?)",
            entity_inserts
        )
        conn.commit()

    conn.close()
    print(f"Enriched {len(spell_updates)} cantrips in spells table & inserted {len(entity_inserts)} new cantrip entities!")

if __name__ == "__main__":
    enrich_cantrip_db()
