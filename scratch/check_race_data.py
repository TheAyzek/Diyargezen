import sqlite3, json

db_path = r"c:\Users\dnssh\OneDrive\Belgeler\Diyargezenweb\data\characters.db"
conn = sqlite3.connect(db_path)
cur = conn.cursor()

cur.execute("SELECT isim, sistem_verisi FROM entities WHERE kategori='race' LIMIT 20")
rows = cur.fetchall()

for name, sv_raw in rows:
    try:
        sv = json.loads(sv_raw) if sv_raw else {}
    except:
        sv = {}
    
    asi = sv.get("ability_score_increase", "N/A")
    asi_text = sv.get("ability_score_increase_text", "N/A")
    print(f"Race: {name}")
    print(f"  ability_score_increase: {json.dumps(asi, ensure_ascii=False) if isinstance(asi, dict) else asi}")
    print(f"  ability_score_increase_text: {asi_text}")
    print()

conn.close()
