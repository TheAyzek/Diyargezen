"""
Archives of Nethys (aonprd.com) Complete Equipment, Weapon & Armor Scraper
===========================================================================
Bu betik Archives of Nethys (aonprd.com) portalındaki:
1. Tüm Genel & Simyasal Ekipmanları (EquipmentMisc.aspx)
2. Tüm Silahları (EquipmentWeapons.aspx - Simple, Martial, Exotic, Ammo, Firearm, Siege vb.)
3. Tüm Zırh & Kalkanları (EquipmentArmor.aspx - Light, Medium, Heavy, Shield vb.)

birebir ayrıştırarak `data/pf1e_scraped_items.json` dosyasına ekler ve SQLite veritabanına aktarır.

Kullanım:
    python scraper/aon_equipment_scraper.py [--max-items 500]
"""

import json
import logging
import re
import sys
import time
import requests
from pathlib import Path
from typing import Dict, List, Any, Optional
from bs4 import BeautifulSoup

# Logging Setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger("aon_equipment_scraper")

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_JSON = DATA_DIR / "pf1e_scraped_items.json"

AON_BASE_URL = "https://aonprd.com/"

MISC_CATEGORIES = [
    "AdventuringGear", "AlchemicalRemedies", "AlchemicalTools", "AlchemicalWeapons",
    "AnimalGear", "BlackMarket", "ChannelFoci", "Clothing", "Concoction",
    "Dragoncraft", "DungeonGuides", "Entertainment", "FoodDrink", "Herbs",
    "Kit", "MountsPets", "Tincture", "Tools", "TransportAir", "TransportLand", "TransportSea"
]

WEAPON_PROFICIENCIES = [
    "Simple", "Martial", "Exotic", "Ammo", "Firearm", "Mod", "Siege", "Special"
]

ARMOR_CATEGORIES = [
    "Light", "Medium", "Heavy", "Shield", "Extra", "Mod"
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Pathfinder1eDiyargezen/2.0"
}


def parse_price_gp(price_str: str) -> float:
    """Fiyat metnini (örn: '15 gp', '5 sp', '1,500 gp') altın (gp) değerine çevirir."""
    if not price_str:
        return 0.0
    clean = price_str.replace(',', '').lower()
    m = re.search(r'([\d\.\/]+)\s*(gp|sp|cp|pp)', clean)
    if not m:
        return 0.0
    val_str, unit = m.groups()
    val = float(val_str.split('/')[0]) / float(val_str.split('/')[1]) if '/' in val_str else float(val_str)
    if unit == 'gp':
        return val
    elif unit == 'sp':
        return val * 0.1
    elif unit == 'cp':
        return val * 0.01
    elif unit == 'pp':
        return val * 10.0
    return val


def parse_weight_lbs(weight_str: str) -> float:
    """Ağırlık metnini (örn: '1/2 lb.', '10 lbs.', '-') pound değerine çevirir."""
    if not weight_str or weight_str in ('-', '—'):
        return 0.0
    clean = weight_str.replace(',', '').lower()
    m = re.search(r'([\d\.\/]+)', clean)
    if not m:
        return 0.0
    val_str = m.group(1)
    return float(val_str.split('/')[0]) / float(val_str.split('/')[1]) if '/' in val_str else float(val_str)


def parse_int_safe(val_str: str) -> int:
    """Metin içindeki ilk tam sayıyı okur (örn: '+6' -> 6, '-5' -> -5, '30%' -> 30)."""
    if not val_str:
        return 0
    m = re.search(r'([+-]?\d+)', val_str)
    return int(m.group(1)) if m else 0


# ==================== MISC EQUIPMENT SCRAPER ====================

def scrape_misc_links(category: str, session: requests.Session) -> List[tuple]:
    url = f"{AON_BASE_URL}EquipmentMisc.aspx?Category={category}"
    logger.info(f"Ekipman Kategori: {category}")
    try:
        r = session.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "EquipmentMiscDisplay.aspx?ItemName=" in href:
                item_name = a.text.strip()
                if item_name and (item_name, href) not in items:
                    items.append((item_name, href))
        return items
    except Exception as exc:
        logger.error(f"Kategori {category} hata: {exc}")
        return []


def scrape_misc_detail(item_name: str, rel_href: str, session: requests.Session) -> Optional[Dict[str, Any]]:
    full_url = f"{AON_BASE_URL}{rel_href}" if not rel_href.startswith("http") else rel_href
    try:
        r = session.get(full_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        span = soup.find('span', id=lambda i: i and 'MainContent_DataListTypes_LabelName' in i)
        if not span:
            return None
        
        h1 = span.find('h1')
        raw_name = h1.text.strip() if h1 else item_name
        
        meta = {}
        for b in span.find_all('b'):
            key = b.text.strip()
            next_node = b.next_sibling
            val_parts = []
            while next_node and next_node.name not in ('b', 'h3'):
                val_parts.append(next_node.text if hasattr(next_node, 'text') else str(next_node))
                next_node = next_node.next_sibling
            meta[key] = ''.join(val_parts).strip().rstrip(';')

        desc_h3 = span.find('h3', class_='framing')
        if desc_h3:
            desc_parts = [s.text if hasattr(s, 'text') else str(s) for s in desc_h3.next_siblings]
            description_raw = ''.join(desc_parts).strip()
        else:
            description_raw = f"{raw_name} - Pathfinder 1e Equipment."

        price_raw = meta.get("Price", "0 gp")
        weight_raw = meta.get("Weight", "0 lb.")
        category_raw = meta.get("Category", "Adventuring Gear")
        
        return {
            "isim": raw_name,
            "sistem": "pathfinder1e",
            "kategori": "item",
            "aciklama": description_raw or f"{raw_name} - Pathfinder 1e Equipment.",
            "sistem_verisi": {
                "type": "equipment",
                "subType": "gear",
                "price": price_raw,
                "price_gp": parse_price_gp(price_raw),
                "weight": {"value": parse_weight_lbs(weight_raw)},
                "category": category_raw,
                "source": meta.get("Source", "Archives of Nethys (aonprd.com)"),
                "source_url": full_url,
                "data_source": "aon_scraper"
            }
        }
    except Exception:
        return None


# ==================== WEAPONS SCRAPER ====================

def scrape_weapon_links(prof: str, session: requests.Session) -> List[tuple]:
    url = f"{AON_BASE_URL}EquipmentWeapons.aspx?Proficiency={prof}"
    logger.info(f"Silah Türü: {prof}")
    try:
        r = session.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "EquipmentWeaponsDisplay.aspx?ItemName=" in href:
                item_name = a.text.strip()
                if item_name and (item_name, href) not in items:
                    items.append((item_name, href))
        return items
    except Exception as exc:
        logger.error(f"Silah Türü {prof} hata: {exc}")
        return []


def scrape_weapon_detail(item_name: str, rel_href: str, session: requests.Session) -> Optional[Dict[str, Any]]:
    full_url = f"{AON_BASE_URL}{rel_href}" if not rel_href.startswith("http") else rel_href
    try:
        r = session.get(full_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        span = soup.find('span', id=lambda i: i and 'MainContent_DataListTypes_LabelName' in i)
        if not span:
            return None
        
        h1 = span.find('h1')
        raw_name = h1.text.strip() if h1 else item_name
        
        meta = {}
        for b in span.find_all('b'):
            key = b.text.strip()
            next_node = b.next_sibling
            val_parts = []
            while next_node and next_node.name not in ('b', 'h3'):
                val_parts.append(next_node.text if hasattr(next_node, 'text') else str(next_node))
                next_node = next_node.next_sibling
            meta[key] = ''.join(val_parts).strip().rstrip(';')

        desc_h3 = span.find('h3', class_='framing')
        if desc_h3:
            desc_parts = [s.text if hasattr(s, 'text') else str(s) for s in desc_h3.next_siblings]
            description_raw = ''.join(desc_parts).strip()
        else:
            description_raw = ""

        dmg_raw = meta.get("Damage", "")
        # Standard medium damage parsing e.g. "1d6 (small), 1d8 (medium)" -> "1d8"
        med_dmg_match = re.search(r'([\d\+d]+)\s*\(\s*medium\s*\)', dmg_raw, re.I)
        if med_dmg_match:
            damage = med_dmg_match.group(1)
        elif dmg_raw:
            damage = dmg_raw.split(',')[0].strip()
        else:
            damage = "1d6"

        cost_raw = meta.get("Cost", meta.get("Price", "0 gp"))
        weight_raw = meta.get("Weight", "0 lbs.")
        crit_raw = meta.get("Critical", "x2")
        range_raw = meta.get("Range", "Melee")
        type_raw = meta.get("Type", "")
        prof_raw = meta.get("Proficiency", "Martial")
        cat_raw = meta.get("Category", "One-Handed")
        groups_raw = meta.get("Weapon Groups", "")

        desc_full = f"Pathfinder 1e {prof_raw} {cat_raw} Weapon. Cost: {cost_raw}, Weight: {weight_raw}, Damage: {damage}, Crit: {crit_raw}, Range: {range_raw}, Type: {type_raw}."
        if description_raw:
            desc_full += f"\n\n{description_raw}"

        # Subtype mapping
        sub_type = "oneHanded"
        if "light" in cat_raw.lower(): sub_type = "light"
        elif "two-handed" in cat_raw.lower() or "two handed" in cat_raw.lower(): sub_type = "twoHanded"
        elif "ranged" in cat_raw.lower() or "ranged" in prof_raw.lower() or "ammo" in prof_raw.lower(): sub_type = "ranged"

        return {
            "isim": raw_name,
            "sistem": "pathfinder1e",
            "kategori": "item",
            "aciklama": desc_full,
            "sistem_verisi": {
                "type": "weapon",
                "subType": sub_type,
                "price": cost_raw,
                "price_gp": parse_price_gp(cost_raw),
                "weight": {"value": parse_weight_lbs(weight_raw)},
                "damage": damage,
                "crit": crit_raw,
                "dmgType": type_raw,
                "range": range_raw,
                "proficiency": prof_raw,
                "category": f"{prof_raw} Weapons",
                "weapon_groups": groups_raw,
                "source": meta.get("Source", "Archives of Nethys (aonprd.com)"),
                "source_url": full_url,
                "data_source": "aon_scraper"
            }
        }
    except Exception:
        return None


# ==================== ARMOR SCRAPER ====================

def scrape_armor_links(cat: str, session: requests.Session) -> List[tuple]:
    url = f"{AON_BASE_URL}EquipmentArmor.aspx?Category={cat}"
    logger.info(f"Zırh Kategorisi: {cat}")
    try:
        r = session.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            return []
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "EquipmentArmorDisplay.aspx?ItemName=" in href:
                item_name = a.text.strip()
                if item_name and (item_name, href) not in items:
                    items.append((item_name, href))
        return items
    except Exception as exc:
        logger.error(f"Zırh Kategorisi {cat} hata: {exc}")
        return []


def scrape_armor_detail(item_name: str, rel_href: str, category_name: str, session: requests.Session) -> Optional[Dict[str, Any]]:
    full_url = f"{AON_BASE_URL}{rel_href}" if not rel_href.startswith("http") else rel_href
    try:
        r = session.get(full_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        soup = BeautifulSoup(r.text, "html.parser")
        span = soup.find('span', id=lambda i: i and 'MainContent_DataListTypes_LabelName' in i)
        if not span:
            return None
        
        h1 = span.find('h1')
        raw_name = h1.text.strip() if h1 else item_name
        
        meta = {}
        for b in span.find_all('b'):
            key = b.text.strip()
            next_node = b.next_sibling
            val_parts = []
            while next_node and next_node.name not in ('b', 'h3'):
                val_parts.append(next_node.text if hasattr(next_node, 'text') else str(next_node))
                next_node = next_node.next_sibling
            meta[key] = ''.join(val_parts).strip().rstrip(';')

        desc_h3 = span.find('h3', class_='framing')
        if desc_h3:
            desc_parts = [s.text if hasattr(s, 'text') else str(s) for s in desc_h3.next_siblings]
            description_raw = ''.join(desc_parts).strip()
        else:
            description_raw = ""

        cost_raw = meta.get("Cost", meta.get("Price", "0 gp"))
        weight_raw = meta.get("Weight", "0 lbs.")
        ac_raw = meta.get("Armor Bonus", meta.get("Shield Bonus", "0"))
        max_dex_raw = meta.get("Max Dex Bonus", "999")
        acp_raw = meta.get("Armor Check Penalty", "0")
        asf_raw = meta.get("Arcane Spell Failure Chance", "0%")

        sub_type = "shield" if "shield" in category_name.lower() or "shield" in raw_name.lower() else "armor"
        desc_full = f"Pathfinder 1e {category_name} Armor. Cost: {cost_raw}, Weight: {weight_raw}, AC Bonus: {ac_raw}, Max Dex: {max_dex_raw}, ACP: {acp_raw}, ASF: {asf_raw}."
        if description_raw:
            desc_full += f"\n\n{description_raw}"

        return {
            "isim": raw_name,
            "sistem": "pathfinder1e",
            "kategori": "item",
            "aciklama": desc_full,
            "sistem_verisi": {
                "type": "equipment",
                "subType": sub_type,
                "price": cost_raw,
                "price_gp": parse_price_gp(cost_raw),
                "weight": {"value": parse_weight_lbs(weight_raw)},
                "acBonus": parse_int_safe(ac_raw),
                "maxDex": parse_int_safe(max_dex_raw) if max_dex_raw != '999' else 999,
                "acp": parse_int_safe(acp_raw),
                "asf": parse_int_safe(asf_raw),
                "category": f"{category_name} Armor",
                "source": meta.get("Source", "Archives of Nethys (aonprd.com)"),
                "source_url": full_url,
                "data_source": "aon_scraper"
            }
        }
    except Exception:
        return None


def run_aon_equipment_scraper(max_per_category: Optional[int] = None):
    """AoN üzerindeki Genel Ekipmanları, Silahları ve Zırhları tarar."""
    logger.info("=== Archives of Nethys (AoN) Complete Scraper Başlatılıyor ===")
    
    existing_items = []
    if OUTPUT_JSON.exists():
        try:
            with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                existing_items = json.load(f)
            logger.info(f"Mevcut json dosyasında {len(existing_items)} adet kayıt bulundu.")
        except Exception:
            existing_items = []

    seen_keys = {
        (d.get("sistem", "pathfinder1e"), d.get("kategori", "item"), d.get("isim", "").lower().strip())
        for d in existing_items
    }
    
    session = requests.Session()
    new_scraped = []

    # 1. SCRAPE MISC EQUIPMENT
    logger.info("--- Phase 1: General & Alchemical Equipment ---")
    for cat in MISC_CATEGORIES:
        links = scrape_misc_links(cat, session)
        if max_per_category and len(links) > max_per_category:
            links = links[:max_per_category]
        for name, href in links:
            key = ("pathfinder1e", "item", name.lower().strip())
            if key in seen_keys: continue
            detail = scrape_misc_detail(name, href, session)
            if detail:
                new_scraped.append(detail)
                seen_keys.add(key)
            time.sleep(0.04)

    # 2. SCRAPE WEAPONS (Simple, Martial, Exotic, Firearms, Siege, Ammo etc.)
    logger.info("--- Phase 2: All PF1e Weapons ---")
    for prof in WEAPON_PROFICIENCIES:
        links = scrape_weapon_links(prof, session)
        if max_per_category and len(links) > max_per_category:
            links = links[:max_per_category]
        for name, href in links:
            key = ("pathfinder1e", "item", name.lower().strip())
            if key in seen_keys: continue
            detail = scrape_weapon_detail(name, href, session)
            if detail:
                new_scraped.append(detail)
                seen_keys.add(key)
            time.sleep(0.04)

    # 3. SCRAPE ARMORS & SHIELDS
    logger.info("--- Phase 3: All PF1e Armors & Shields ---")
    for cat in ARMOR_CATEGORIES:
        links = scrape_armor_links(cat, session)
        if max_per_category and len(links) > max_per_category:
            links = links[:max_per_category]
        for name, href in links:
            key = ("pathfinder1e", "item", name.lower().strip())
            if key in seen_keys: continue
            detail = scrape_armor_detail(name, href, cat, session)
            if detail:
                new_scraped.append(detail)
                seen_keys.add(key)
            time.sleep(0.04)

    if new_scraped:
        all_combined = existing_items + new_scraped
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(all_combined, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Başarıyla {len(new_scraped)} yeni varlık (silah, zırh, teçhizat) eklendi. Toplam kayıt: {len(all_combined)}")
    else:
        logger.info("Yeni eklenecek benzersiz varlık bulunamadı. Tüm varlıklar zaten güncel.")


if __name__ == "__main__":
    max_limit = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        max_limit = int(sys.argv[1])
    run_aon_equipment_scraper(max_per_category=max_limit)
