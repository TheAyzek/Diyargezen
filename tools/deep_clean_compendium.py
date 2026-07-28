import sqlite3
import json
import re
from pathlib import Path
from html import unescape

# Internal Foundry VTT keys that should NEVER be exposed in sistem_verisi
VTT_JUNK_KEYS = {
    'flags', 'data', 'img', '_id', 'chat', 'unidentified', 'tags', 'actions',
    'uses', 'per', 'maxFormula', 'autoDeductChargesCost', 'attackNotes', 'effectNotes',
    'changes', 'changeFlags', 'loseDexToAC', 'noEncumbrance', 'mediumArmorFullSpeed',
    'heavyArmorFullSpeed', 'links', 'charges', 'tag', 'useCustomTag', 'armorProf',
    'weaponProf', 'languages', 'scriptCalls', 'featType', 'associations', 'classes',
    'showInQuickbar', 'abilityType', 'crOffset', 'disabled', 'classSkills',
    'activation', 'unchainedAction', 'duration', 'actionType', 'ability',
    'damageMult', 'critMult', 'range', 'maxIncrements', 'standard_mechanics',
    'source', 'source_ref', 'schema_version'
}

def fix_concatenated_words(text: str) -> str:
    if not text:
        return ""
    
    s = unescape(str(text))

    # 1. Strip Foundry VTT link codes e.g. @Compendium[...]
    s = re.sub(r'@Compendium\[[^\]]+\]\{([^}]+)\}', r'\1', s)
    s = re.sub(r'@Compendium\[[^\]]+\]', '', s)

    # 2. Remove HTML tags & ASP.NET tags
    s = re.sub(r'<span[^>]*>', '', s)
    s = s.replace('</span>', '')
    s = re.sub(r'<h[1-6]>[^<]*Description[^<]*</h[1-6]>', '', s, flags=re.I)
    s = re.sub(r'<[^>]+>', ' ', s)

    # 3. Specific concatenated typos in scraped PF1e descriptions
    s = s.replace('beparalyzedby', 'be paralyzed by')
    s = s.replace('savingthrow', 'saving throw')
    s = s.replace('spellattack', 'spell attack')
    s = s.replace('meleeattack', 'melee attack')
    s = s.replace('rangedattack', 'ranged attack')
    s = s.replace('hitpoints', 'hit points')
    s = s.replace('casterlevel', 'caster level')
    s = s.replace('spellresistance', 'spell resistance')

    # 4. Split concatenated CamelCase e.g. aWisdom -> a Wisdom, aConstitution -> a Constitution
    s = re.sub(r'([a-z])([A-Z])', r'\1 \2', s)

    # 5. Split word + stat/saving throw e.g. aWisdomsaving -> a Wisdom saving
    s = re.sub(r'(\b[a-zA-Z]+)(saving|throw|attack|damage|target|duration|range|radius|paralyzed|poisoned|stunned|blinded|deafened)', r'\1 \2', s, flags=re.I)
    s = re.sub(r'(saving|throw|attack|damage|target|duration|range|radius|paralyzed|poisoned|stunned|blinded|deafened)(\b[a-zA-Z]+)', r'\1 \2', s, flags=re.I)

    # 6. Split number + unit e.g. 10feet -> 10 feet, 1d6damage -> 1d6 damage, 1round -> 1 round
    s = re.sub(r'(\d+)(feet|ft|d4|d6|d8|d10|d12|d20|rounds?|minutes?|hours?|days?|level|levels|damage)', r'\1 \2', s, flags=re.I)

    # 7. Clean quotes and whitespace
    s = s.replace('&rsquo;', "'").replace('&lsquo;', "'").replace('&quot;', '"').replace('&nbsp;', ' ').replace('&ndash;', '-').replace('&mdash;', '—')
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r'\n\s*\n', '\n\n', s)

    return s.strip()

def sanitize_sistem_verisi(sv_dict: dict) -> dict:
    if not isinstance(sv_dict, dict):
        return {}

    cleaned_sv = {}
    for k, v in sv_dict.items():
        # Skip raw VTT internal junk keys
        if k in VTT_JUNK_KEYS or k.lower() in VTT_JUNK_KEYS:
            continue

        if isinstance(v, str):
            cleaned_sv[k] = fix_concatenated_words(v)
        elif isinstance(v, dict):
            sub_clean = sanitize_sistem_verisi(v)
            if sub_clean:
                cleaned_sv[k] = sub_clean
        elif isinstance(v, list):
            cleaned_list = []
            for item in v:
                if isinstance(item, str):
                    cleaned_list.append(fix_concatenated_words(item))
                elif isinstance(item, dict):
                    cleaned_list.append(sanitize_sistem_verisi(item))
                else:
                    cleaned_list.append(item)
            cleaned_sv[k] = cleaned_list
        else:
            cleaned_sv[k] = v

    return cleaned_sv

def deep_clean_database(db_path: Path):
    print(f"\n==========================================")
    print(f"Deep Cleaning Database: {db_path}")
    print(f"==========================================")

    if not db_path.exists():
        print(f"File not found: {db_path}")
        return

    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()

        # Check if 'entities' table exists
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='entities'")
        if not cursor.fetchone():
            print(f"Skipping {db_path} (no 'entities' table).")
            conn.close()
            return

        cursor.execute("SELECT id, isim, aciklama, sistem_verisi FROM entities")
        rows = cursor.fetchall()
        print(f"Total entities to deep clean in {db_path.name}: {len(rows)}")

        updated_count = 0
        for row in rows:
            entity_id, name, raw_desc, sv_raw = row[0], row[1], row[2] or "", row[3]

            clean_name = fix_concatenated_words(name)
            clean_desc = fix_concatenated_words(raw_desc)

            try:
                sv = json.loads(sv_raw) if (sv_raw and sv_raw != "null") else {}
            except Exception:
                sv = {}

            clean_sv = sanitize_sistem_verisi(sv) if isinstance(sv, dict) else {}

            if clean_name != name or clean_desc != raw_desc or clean_sv != sv:
                cursor.execute(
                    "UPDATE entities SET isim = ?, aciklama = ?, sistem_verisi = ? WHERE id = ?",
                    (clean_name, clean_desc, json.dumps(clean_sv, ensure_ascii=False) if clean_sv else sv_raw, entity_id)
                )
                updated_count += 1

        conn.commit()
        conn.close()
        print(f"Successfully deep cleaned {updated_count} entities in {db_path.name}.")
    except Exception as e:
        print(f"Error deep cleaning {db_path}: {e}")

def run_deep_clean():
    project_root = Path(".")
    candidate_dbs = [
        project_root / "data" / "characters.db",
        project_root / "desktop" / "data" / "offline_pf1e.db",
        project_root / "dist" / "Diyargezen" / "_internal" / "data" / "characters.db"
    ]

    for db_path in candidate_dbs:
        if db_path.exists():
            deep_clean_database(db_path)

if __name__ == "__main__":
    run_deep_clean()
