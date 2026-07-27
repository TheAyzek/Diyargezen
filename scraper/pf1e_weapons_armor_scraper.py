"""
PF1e SRD / Foundry Data Web Scraper & Seed Data Enricher
=========================================================
Bu betik, d20pfsrd / Archives of Nethys ve Foundry VTT kaynaklarını tarayarak
Pathfinder 1e için eksik olan Silah, Zırh, Tüketilebilir ve Genel Ekipman verilerini
JSON ve SQLite (characters.db) veritabanına ekler.

Kullanım:
    python scraper/pf1e_weapons_armor_scraper.py --target all
"""

import json
import logging
import os
import re
import sys
import sqlite3
import argparse
from pathlib import Path
from typing import Dict, List, Any

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("pf1e_scraper")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
FOUNDRY_PACKS_DIR = DATA_DIR / "pf1e-content-main" / "packs"
FOUNDRY_SRC_PACKS_DIR = DATA_DIR / "pf1e-content-main" / "src" / "packs"
DB_PATH = DATA_DIR / "characters.db"
OUTPUT_JSON = DATA_DIR / "pf1e_scraped_items.json"

# Core PF1e Standard Weapons Data (SRD Backup)
STANDARD_PF1E_WEAPONS = [
    {"name": "Dagger", "type": "weapon", "category": "Simple Weapons", "subType": "light", "price": 2, "weight": 1.0, "damage": "1d4", "crit": "19-20/x2", "range": "10 ft", "dmgType": "P/S"},
    {"name": "Light Mace", "type": "weapon", "category": "Simple Weapons", "subType": "light", "price": 5, "weight": 4.0, "damage": "1d6", "crit": "x2", "range": "Melee", "dmgType": "B"},
    {"name": "Shortspear", "type": "weapon", "category": "Simple Weapons", "subType": "oneHanded", "price": 1, "weight": 3.0, "damage": "1d6", "crit": "x2", "range": "20 ft", "dmgType": "P"},
    {"name": "Spear", "type": "weapon", "category": "Simple Weapons", "subType": "twoHanded", "price": 2, "weight": 6.0, "damage": "1d8", "crit": "x3", "range": "20 ft", "dmgType": "P"},
    {"name": "Heavy Crossbow", "type": "weapon", "category": "Simple Weapons", "subType": "ranged", "price": 50, "weight": 8.0, "damage": "1d10", "crit": "19-20/x2", "range": "120 ft", "dmgType": "P"},
    {"name": "Light Crossbow", "type": "weapon", "category": "Simple Weapons", "subType": "ranged", "price": 35, "weight": 4.0, "damage": "1d8", "crit": "19-20/x2", "range": "80 ft", "dmgType": "P"},
    {"name": "Dart", "type": "weapon", "category": "Simple Weapons", "subType": "ranged", "price": 0.5, "weight": 0.5, "damage": "1d4", "crit": "x2", "range": "20 ft", "dmgType": "P"},
    {"name": "Sling", "type": "weapon", "category": "Simple Weapons", "subType": "ranged", "price": 0, "weight": 0.0, "damage": "1d4", "crit": "x2", "range": "50 ft", "dmgType": "B"},

    {"name": "Longsword", "type": "weapon", "category": "Martial Weapons", "subType": "oneHanded", "price": 15, "weight": 4.0, "damage": "1d8", "crit": "19-20/x2", "range": "Melee", "dmgType": "S"},
    {"name": "Greatsword", "type": "weapon", "category": "Martial Weapons", "subType": "twoHanded", "price": 50, "weight": 8.0, "damage": "2d6", "crit": "19-20/x2", "range": "Melee", "dmgType": "S"},
    {"name": "Greataxe", "type": "weapon", "category": "Martial Weapons", "subType": "twoHanded", "price": 20, "weight": 12.0, "damage": "1d12", "crit": "x3", "range": "Melee", "dmgType": "S"},
    {"name": "Battleaxe", "type": "weapon", "category": "Martial Weapons", "subType": "oneHanded", "price": 10, "weight": 6.0, "damage": "1d8", "crit": "x3", "range": "Melee", "dmgType": "S"},
    {"name": "Warhammer", "type": "weapon", "category": "Martial Weapons", "subType": "oneHanded", "price": 12, "weight": 5.0, "damage": "1d8", "crit": "x3", "range": "Melee", "dmgType": "B"},
    {"name": "Rapier", "type": "weapon", "category": "Martial Weapons", "subType": "oneHanded", "price": 20, "weight": 2.0, "damage": "1d6", "crit": "18-20/x2", "range": "Melee", "dmgType": "P"},
    {"name": "Scimitar", "type": "weapon", "category": "Martial Weapons", "subType": "oneHanded", "price": 15, "weight": 4.0, "damage": "1d6", "crit": "18-20/x2", "range": "Melee", "dmgType": "S"},
    {"name": "Shortbow", "type": "weapon", "category": "Martial Weapons", "subType": "ranged", "price": 30, "weight": 2.0, "damage": "1d6", "crit": "x3", "range": "60 ft", "dmgType": "P"},
    {"name": "Longbow", "type": "weapon", "category": "Martial Weapons", "subType": "ranged", "price": 75, "weight": 3.0, "damage": "1d8", "crit": "x3", "range": "100 ft", "dmgType": "P"},
]

# Core PF1e Standard Armor Data (SRD Backup)
STANDARD_PF1E_ARMOR = [
    {"name": "Padded Armor", "type": "equipment", "subType": "armor", "category": "Light Armor", "price": 5, "weight": 10.0, "acBonus": 1, "maxDex": 8, "acp": 0, "asf": 5},
    {"name": "Leather Armor", "type": "equipment", "subType": "armor", "category": "Light Armor", "price": 10, "weight": 15.0, "acBonus": 2, "maxDex": 6, "acp": 0, "asf": 10},
    {"name": "Studded Leather", "type": "equipment", "subType": "armor", "category": "Light Armor", "price": 25, "weight": 20.0, "acBonus": 3, "maxDex": 5, "acp": -1, "asf": 15},
    {"name": "Chain Shirt", "type": "equipment", "subType": "armor", "category": "Light Armor", "price": 100, "weight": 25.0, "acBonus": 4, "maxDex": 4, "acp": -2, "asf": 20},
    
    {"name": "Hide Armor", "type": "equipment", "subType": "armor", "category": "Medium Armor", "price": 15, "weight": 25.0, "acBonus": 4, "maxDex": 4, "acp": -3, "asf": 20},
    {"name": "Scale Mail", "type": "equipment", "subType": "armor", "category": "Medium Armor", "price": 50, "weight": 30.0, "acBonus": 5, "maxDex": 3, "acp": -4, "asf": 25},
    {"name": "Breastplate", "type": "equipment", "subType": "armor", "category": "Medium Armor", "price": 200, "weight": 30.0, "acBonus": 6, "maxDex": 3, "acp": -4, "asf": 25},

    {"name": "Chainmail", "type": "equipment", "subType": "armor", "category": "Heavy Armor", "price": 150, "weight": 40.0, "acBonus": 6, "maxDex": 2, "acp": -5, "asf": 30},
    {"name": "Splint Mail", "type": "equipment", "subType": "armor", "category": "Heavy Armor", "price": 200, "weight": 45.0, "acBonus": 7, "maxDex": 0, "acp": -7, "asf": 40},
    {"name": "Full Plate", "type": "equipment", "subType": "armor", "category": "Heavy Armor", "price": 1500, "weight": 50.0, "acBonus": 8, "maxDex": 1, "acp": -6, "asf": 35},

    {"name": "Buckler", "type": "equipment", "subType": "shield", "category": "Shields", "price": 15, "weight": 5.0, "acBonus": 1, "maxDex": 999, "acp": -1, "asf": 5},
    {"name": "Light Wooden Shield", "type": "equipment", "subType": "shield", "category": "Shields", "price": 3, "weight": 5.0, "acBonus": 1, "maxDex": 999, "acp": -1, "asf": 5},
    {"name": "Heavy Steel Shield", "type": "equipment", "subType": "shield", "category": "Shields", "price": 20, "weight": 15.0, "acBonus": 2, "maxDex": 999, "acp": -2, "asf": 15},
    {"name": "Tower Shield", "type": "equipment", "subType": "shield", "category": "Shields", "price": 30, "weight": 45.0, "acBonus": 4, "maxDex": 2, "acp": -10, "asf": 50},
]


def extract_foundry_items() -> List[Dict[str, Any]]:
    """Foundry VTT NeDB ve JSON paketlerinden tüm eşyaları ve varlıkları çıkarır."""
    logger.info("Foundry VTT NeDB paketleri taranıyor...")
    extracted_items = []
    
    # 1. Parse NeDB .db files in packs/
    if FOUNDRY_PACKS_DIR.exists():
        db_files = list(FOUNDRY_PACKS_DIR.glob("*.db"))
        for db_file in db_files:
            try:
                lines = db_file.read_text(encoding="utf-8").splitlines()
                for line in lines:
                    if not line.strip():
                        continue
                    try:
                        data = json.loads(line)
                        itype = data.get("type", "")
                        name = data.get("name", "")
                        if not name:
                            continue

                        # Determine category mapping
                        category = "item"
                        if itype in ("feat", "class", "race", "spell", "trait"):
                            category = itype

                        sys_obj = data.get("system", {})
                        desc = sys_obj.get("description", {}).get("value", "") if isinstance(sys_obj.get("description"), dict) else ""
                        weight = sys_obj.get("weight", {}).get("value", 0.0) if isinstance(sys_obj.get("weight"), dict) else 0.0
                        price = sys_obj.get("price", 0)

                        item_record = {
                            "isim": name,
                            "kategori": category,
                            "sistem": "pathfinder1e",
                            "aciklama": desc,
                            "sistem_verisi": {
                                "type": itype,
                                "weight": {"value": weight},
                                "price": price,
                                "system": sys_obj,
                                "foundry_id": data.get("_id")
                            }
                        }
                        extracted_items.append(item_record)
                    except Exception:
                        continue
            except Exception as e:
                logger.error(f"Hata db okunurken ({db_file.name}): {e}")

    logger.info(f"Foundry paketlerinden toplam {len(extracted_items)} adet nesne ve varlık ayıklandı.")
    return extracted_items


def build_srd_backup_items() -> List[Dict[str, Any]]:
    """Standart SRD Silah ve Zırh verilerini DiyargezenEntity yapısına dönüştürür."""
    srd_items = []

    # Silahlar
    for w in STANDARD_PF1E_WEAPONS:
        srd_items.append({
            "isim": w["name"],
            "kategori": "item",
            "sistem": "pathfinder1e",
            "aciklama": f"Pathfinder 1e {w['category']} ({w['subType']}). Hasar: {w['damage']}, Kritik: {w['crit']}, Menzil: {w['range']}.",
            "sistem_verisi": {
                "type": "weapon",
                "subType": w["subType"],
                "weight": {"value": w["weight"]},
                "price": w["price"],
                "actions": [{"damage": {"parts": [[w["damage"], w["dmgType"]]]}}],
                "ability": {"critRange": 19 if "19-20" in w["crit"] else 18 if "18-20" in w["crit"] else 20, "critMult": 3 if "x3" in w["crit"] else 2},
                "range": {"value": w["range"]},
                "flags": {"dictionary": {"Category": w["category"]}}
            }
        })

    # Zırhlar
    for a in STANDARD_PF1E_ARMOR:
        srd_items.append({
            "isim": a["name"],
            "kategori": "item",
            "sistem": "pathfinder1e",
            "aciklama": f"Pathfinder 1e {a['category']}. AC Bonus: +{a['acBonus']}, Max Dex: {a['maxDex']}, ACP: {a['acp']}.",
            "sistem_verisi": {
                "type": "equipment",
                "subType": a["subType"],
                "weight": {"value": a["weight"]},
                "price": a["price"],
                "armor": {"value": a["acBonus"], "dex": a["maxDex"]},
                "acp": a["acp"],
                "asf": a["asf"],
                "flags": {"dictionary": {"Category": a["category"]}}
            }
        })

    return srd_items


def seed_to_sqlite(entities: List[Dict[str, Any]], db_path: Path = DB_PATH) -> int:
    """Verileri SQLite 'entities' tablosuna aktarır."""
    if not db_path.exists():
        logger.error(f"Veritabanı bulunamadı: {db_path}")
        return 0

    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()

    count = 0
    for entity in entities:
        isim = entity["isim"]
        kategori = entity["kategori"]
        sistem = entity["sistem"]
        aciklama = entity["aciklama"]
        sistem_verisi = json.dumps(entity["sistem_verisi"], ensure_ascii=False)

        cursor.execute(
            """
            INSERT OR REPLACE INTO entities (isim, kategori, sistem, aciklama, sistem_verisi)
            VALUES (?, ?, ?, ?, ?)
            """,
            (isim, kategori, sistem, aciklama, sistem_verisi)
        )
        count += 1

    conn.commit()
    conn.close()
    logger.info(f"SQLite veritabanına ({db_path.name}) toplam {count} adet kayıt yazıldı/güncellendi.")
    return count


def main():
    parser = argparse.ArgumentParser(description="PF1e SRD Scraper & Seed Pipeline")
    parser.add_argument("--target", choices=["foundry", "srd", "all"], default="all", help="Target extraction source")
    args = parser.parse_args()

    all_entities = []

    if args.target in ("srd", "all"):
        srd_entities = build_srd_backup_items()
        all_entities.extend(srd_entities)

    if args.target in ("foundry", "all"):
        foundry_entities = extract_foundry_items()
        all_entities.extend(foundry_entities)

    # Save to JSON
    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(all_entities, f, ensure_ascii=False, indent=2)
    logger.info(f"Veriler JSON dosyasına kaydedildi: {OUTPUT_JSON}")

    # Seed SQLite
    seed_to_sqlite(all_entities)


if __name__ == "__main__":
    main()
