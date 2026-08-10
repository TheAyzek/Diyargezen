import sqlite3
import json

db_path = r'C:\Users\dnssh\OneDrive\Belgeler\Diyargezenweb\data\characters.db'
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. Classes count
cursor.execute("SELECT isim FROM entities WHERE kategori = 'class' AND sistem = 'pathfinder1e' ORDER BY isim")
classes = [row[0] for row in cursor.fetchall()]
print(f"=== PATHFINDER 1E TEMEL SINIFLARI ({len(classes)} Sınıf) ===")
print(", ".join(classes))

# 2. Archetypes count & breakdown
cursor.execute("""
    SELECT 
        json_extract(sistem_verisi, '$.parent_class') as parent,
        COUNT(*) as cnt
    FROM entities 
    WHERE kategori = 'archetype' AND sistem = 'pathfinder1e'
    GROUP BY parent
    ORDER BY cnt DESC
""")
rows = cursor.fetchall()
total_archs = sum(r[1] for r in rows)

print(f"\n=== ARKETİP VERİTABANI ÖZETİ (Toplam {total_archs} Arketip) ===")
for parent, cnt in rows:
    pname = parent if parent else "Belirtilmemiş / Genel"
    print(f"  • {pname:<20}: {cnt} arketip")

# 3. Check JSON dataset pathfinder_1e_data.json
print("\n=== JSON VERİ SETİ (pathfinder_1e_data.json) ===")
try:
    with open('data/pathfinder_1e_data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)
        json_classes = data.get('classes', {})
        json_archetypes = data.get('archetypes', {})
        print(f"JSON Tanımlı Sınıflar : {len(json_classes)}")
        print(f"JSON Tanımlı Arketipler: {len(json_archetypes)}")
        
        # Sample archetypes for Fighter, Wizard, Rogue, Barbarian
        sample_parents = ['Fighter', 'Rogue', 'Wizard', 'Barbarian', 'Cleric', 'Paladin']
        for sp in sample_parents:
            matched = [a for a, av in json_archetypes.items() if av.get('parent_class', '').lower() == sp.lower()]
            print(f"  - {sp} Arketipleri (Örnek {len(matched)} adet): {', '.join(matched[:5])}")

except Exception as e:
    print("JSON okuma hatası:", e)
