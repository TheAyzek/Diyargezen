import sqlite3
import json

conn = sqlite3.connect('data/characters.db')
cur = conn.cursor()

cur.execute("SELECT COUNT(1) FROM spells WHERE seviye = 0")
print("spells table level 0 count:", cur.fetchone()[0])

cur.execute("SELECT COUNT(1) FROM spells")
print("spells table total:", cur.fetchone()[0])

cur.execute("SELECT isim, sistem_verisi FROM entities WHERE kategori = 'spell' AND sistem = 'pathfinder1e'")
rows = cur.fetchall()

cantrips = []
for r_name, r_data in rows:
    try:
        p = json.loads(r_data) if r_data else {}
        lvl = p.get('level')
        if lvl is None:
            lvl = p.get('spell_level')
        if lvl is None:
            lvl = p.get('seviye')
        
        # Check levels_by_class for 0
        lvl_by_cls = p.get('levels_by_class', {})
        has_0 = (lvl == 0 or lvl == '0' or any(v == 0 or v == '0' for v in lvl_by_cls.values()))
        if has_0:
            cantrips.append((r_name, lvl, lvl_by_cls))
    except Exception as e:
        pass

print(f"entities table level 0 spells (total: {len(cantrips)}):")
for name, lvl, cls_map in cantrips[:30]:
    print(f" - {name} (level: {lvl}, classes: {cls_map})")

conn.close()
