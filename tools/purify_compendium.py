import sqlite3
import json
import re
from pathlib import Path
from html import unescape

def sanitize_text(text: str) -> str:
    if not text:
        return ""
    
    # 1. Unescape HTML entities
    s = unescape(str(text))
    
    # 2. Convert Foundry VTT @Compendium[...]{Label} -> Label
    s = re.sub(r'@Compendium\[[^\]]+\]\{([^}]+)\}', r'\1', s)
    s = re.sub(r'@Compendium\[[^\]]+\]', '', s)

    # 3. Remove ASP.NET scraper tags like <span id="ctl00_MainContent_DataListTypes_...">
    s = re.sub(r'<span[^>]*>', '', s)
    s = s.replace('</span>', '')

    # 4. Fix broken Description header tags like <h2></b>Description</b></h2>
    s = re.sub(r'<h[1-6]>[^<]*Description[^<]*</h[1-6]>', '', s, flags=re.I)

    # 5. Remove remaining HTML tags
    s = re.sub(r'<[^>]+>', ' ', s)

    # 6. Normalize whitespace & quotes
    s = s.replace('&rsquo;', "'").replace('&lsquo;', "'").replace('&quot;', '"').replace('&nbsp;', ' ').replace('&ndash;', '-').replace('&mdash;', '—')
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n', '\n\n', s)
    
    return s.strip()

def purify_single_db(db_path: Path):
    print(f"\n==========================================")
    print(f"Purifying Database: {db_path}")
    print(f"==========================================")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if 'entities' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
        if not cursor.fetchone():
            print(f"Skipping {db_path} (no 'entities' table).")
            conn.close()
            return

        # 1. Delete fake spell index table rows
        FAKE_SPELL_PATTERNS = [
            "%Potions%", "%Wands%", "%Scrolls%", "%Special Abilities%",
            "%Requirement%", "%Common Level%", "%Potions and Oils%", "%Specific Magic Shields%"
        ]
        deleted_spells = 0
        for pat in FAKE_SPELL_PATTERNS:
            cursor.execute("DELETE FROM entities WHERE kategori = 'spell' AND isim LIKE ?", (pat,))
            deleted_spells += cursor.rowcount
        if deleted_spells > 0:
            print(f"Deleted {deleted_spells} fake spell index rows.")

        # 2. Delete fake rule rows
        FAKE_RULE_NAMES = [
            "pf-content", "foundry-compendium-merge", "Pathfinder Wiki",
            "- Change Formulas", "README"
        ]
        deleted_rules = 0
        for rname in FAKE_RULE_NAMES:
            cursor.execute("DELETE FROM entities WHERE kategori = 'rule' AND isim = ?", (rname,))
            deleted_rules += cursor.rowcount
        if deleted_rules > 0:
            print(f"Deleted {deleted_rules} fake rule rows.")

        # 3. Process entity descriptions and payloads
        cursor.execute("SELECT id, isim, aciklama, sistem_verisi FROM entities")
        rows = cursor.fetchall()
        print(f"Total entities to process in {db_path.name}: {len(rows)}")

        updated_count = 0
        for row in rows:
            entity_id, name, raw_desc, sv_raw = row[0], row[1], row[2] or "", row[3]

            clean_desc = sanitize_text(raw_desc)
            clean_name = sanitize_text(name)

            try:
                sv = json.loads(sv_raw) if (sv_raw and sv_raw != "null") else {}
            except Exception:
                sv = {}

            sv_changed = False
            if isinstance(sv, dict):
                if "description" in sv and isinstance(sv["description"], str):
                    sv["description"] = sanitize_text(sv["description"])
                    sv_changed = True
                elif "description" in sv and isinstance(sv["description"], dict):
                    if "value" in sv["description"]:
                        sv["description"]["value"] = sanitize_text(sv["description"]["value"])
                        sv_changed = True

                if "benefit" in sv and isinstance(sv["benefit"], str):
                    sv["benefit"] = sanitize_text(sv["benefit"])
                    sv_changed = True

                if "description" in sv and (not sv["description"] or sv["description"] == clean_desc):
                    del sv["description"]
                    sv_changed = True

            if clean_desc != raw_desc or clean_name != name or sv_changed:
                cursor.execute(
                    "UPDATE entities SET isim = ?, aciklama = ?, sistem_verisi = ? WHERE id = ?",
                    (clean_name, clean_desc, json.dumps(sv, ensure_ascii=False) if sv else sv_raw, entity_id)
                )
                updated_count += 1

        conn.commit()
        conn.close()
        print(f"Successfully purified {updated_count} entities in {db_path.name}.")
    except Exception as e:
        print(f"Error purifying {db_path}: {e}")

def purify_all_databases():
    project_root = Path(".")
    candidate_dbs = [
        project_root / "data" / "characters.db",
        project_root / "desktop" / "data" / "offline_pf1e.db",
        project_root / "dist" / "Diyargezen" / "_internal" / "data" / "characters.db"
    ]

    for db_path in candidate_dbs:
        if db_path.exists():
            purify_single_db(db_path)

if __name__ == "__main__":
    purify_all_databases()
