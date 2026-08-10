import sqlite3

conn = sqlite3.connect('data/characters.db')
cur = conn.cursor()

cur.execute("SELECT isim, seviye, siniflar, aciklama FROM spells WHERE seviye = 0 LIMIT 20")
rows = cur.fetchall()

print("\nSample level 0 spells in spells table:")
for r in rows:
    print(r[0], "| level:", r[1], "| classes:", r[2])

conn.close()
