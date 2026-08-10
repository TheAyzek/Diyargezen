import sqlite3
conn = sqlite3.connect(r"c:\Users\dnssh\OneDrive\Belgeler\Diyargezenweb\data\characters.db")
cur = conn.cursor()
cur.execute("SELECT isim FROM entities WHERE kategori='race' AND isim NOT LIKE 'Race:%' ORDER BY isim LIMIT 30")
for r in cur.fetchall():
    print(r[0])
conn.close()
