import sqlite3
import re

conn = sqlite3.connect('data/characters.db')
cur = conn.cursor()

cur.execute("SELECT id, isim, aciklama FROM spells WHERE seviye = 0 AND (siniflar IS NULL OR siniflar = '' OR siniflar = '{}') LIMIT 30")
rows = cur.fetchall()

print("Sample cantrips with empty classes:")
for r_id, name, desc in rows:
    # Look for Level / School / Class keywords in description
    print(f"ID {r_id}: {name} | Desc: {desc[:120]}...")

conn.close()
