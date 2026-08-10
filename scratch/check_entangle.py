import sqlite3, json

conn = sqlite3.connect("data/characters.db")
cur = conn.cursor()

cur.execute("SELECT isim, seviye, siniflar FROM spells WHERE LOWER(isim) LIKE '%entangle%'")
print("spells table entangle:", cur.fetchall())

cur.execute("SELECT isim, sistem_verisi FROM entities WHERE kategori='spell' AND LOWER(isim) LIKE '%entangle%'")
for r in cur.fetchall():
    print("entities entangle:", r[0], json.loads(r[1]).get("levels_by_class"))

conn.close()
