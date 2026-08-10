import sqlite3
import json

conn = sqlite3.connect('data/characters.db')
cur = conn.cursor()

cur.execute("SELECT id, isim, siniflar, aciklama FROM spells WHERE seviye = 0")
spell_rows = cur.fetchall()
print(f"Total level 0 spells in spells table: {len(spell_rows)}")

with_classes = 0
without_classes = 0

for r in spell_rows:
    classes_str = r[2] or ""
    if classes_str.strip():
        with_classes += 1
    else:
        without_classes += 1

print(f"With classes: {with_classes}, Without classes: {without_classes}")

cur.execute("SELECT isim, sistem_verisi FROM entities WHERE kategori = 'spell'")
ent_rows = cur.fetchall()
print(f"Total spell entities in entities table: {len(ent_rows)}")

conn.close()
