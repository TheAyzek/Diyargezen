"""
Archives of Nethys (aonprd.com) Equipment Scraper & ETL Ingestion Engine
==========================================================================
Bu betik Archives of Nethys (aonprd.com) portalındaki tüm non-magical ve alchemical
ekipman kategorilerini tarar, fiyat, ağırlık ve açıklamalarını ayrıştırıp
`data/pf1e_scraped_items.json` dosyasına ekler ve SQLite veritabanına aktarır.

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
CATEGORIES = [
    "AdventuringGear",
    "AlchemicalRemedies",
    "AlchemicalTools",
    "AlchemicalWeapons",
    "AnimalGear",
    "BlackMarket",
    "ChannelFoci",
    "Clothing",
    "Concoction",
    "Dragoncraft",
    "DungeonGuides",
    "Entertainment",
    "FoodDrink",
    "Herbs",
    "Kit",
    "MountsPets",
    "Tincture",
    "Tools",
    "TransportAir",
    "TransportLand",
    "TransportSea"
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


def scrape_category_item_links(category: str, session: requests.Session) -> List[tuple]:
    """AoN kategori sayfasından tüm eşya bağlantılarını çeker."""
    url = f"{AON_BASE_URL}EquipmentMisc.aspx?Category={category}"
    logger.info(f"Kategori taranıyor: {category} -> {url}")
    try:
        r = session.get(url, headers=HEADERS, timeout=12)
        if r.status_code != 200:
            logger.warning(f"Kategori {category} isteği başarısız: HTTP {r.status_code}")
            return []
        
        soup = BeautifulSoup(r.text, "html.parser")
        items = []
        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "EquipmentMiscDisplay.aspx?ItemName=" in href:
                item_name = a.text.strip()
                if item_name and (item_name, href) not in items:
                    items.append((item_name, href))
        logger.info(f"Kategori [{category}]: {len(items)} adet eşya bağlantısı bulundu.")
        return items
    except Exception as exc:
        logger.error(f"Kategori {category} çekilirken hata: {exc}")
        return []


def scrape_item_details(item_name: str, rel_href: str, session: requests.Session) -> Optional[Dict[str, Any]]:
    """Eşyanın detay sayfasından açıklama, fiyat, ağırlık ve kategori bilgilerini çeker."""
    full_url = f"{AON_BASE_URL}{rel_href}" if not rel_href.startswith("http") else rel_href
    try:
        r = session.get(full_url, headers=HEADERS, timeout=10)
        if r.status_code != 200:
            return None
        
        soup = BeautifulSoup(r.text, "html.parser")
        span = soup.find('span', id=lambda i: i and 'MainContent_DataListTypes_LabelName' in i)
        if not span:
            return None
        
        # Item title
        h1 = span.find('h1')
        raw_name = h1.text.strip() if h1 else item_name
        
        # Extract bold meta fields (Source, Price, Weight, Category, Recipe, etc.)
        meta = {}
        for b in span.find_all('b'):
            key = b.text.strip()
            next_node = b.next_sibling
            val_parts = []
            while next_node and next_node.name not in ('b', 'h3'):
                val_parts.append(next_node.text if hasattr(next_node, 'text') else str(next_node))
                next_node = next_node.next_sibling
            meta[key] = ''.join(val_parts).strip().rstrip(';')

        # Extract description text after Description H3
        desc_h3 = span.find('h3', class_='framing')
        if desc_h3:
            desc_parts = []
            for sibling in desc_h3.next_siblings:
                if hasattr(sibling, 'text'):
                    desc_parts.append(sibling.text)
                elif isinstance(sibling, str):
                    desc_parts.append(sibling)
            description_raw = ''.join(desc_parts).strip()
        else:
            description_raw = f"{raw_name} - Pathfinder 1e Equipment item."

        price_raw = meta.get("Price", "0 gp")
        weight_raw = meta.get("Weight", "0 lb.")
        category_raw = meta.get("Category", "Adventuring Gear")
        
        price_gp = parse_price_gp(price_raw)
        weight_lbs = parse_weight_lbs(weight_raw)
        
        return {
            "isim": raw_name,
            "sistem": "pathfinder1e",
            "kategori": "item",
            "aciklama": description_raw or f"{raw_name} - Pathfinder 1e Equipment.",
            "sistem_verisi": {
                "type": "equipment",
                "subType": "gear",
                "price": price_raw,
                "price_gp": price_gp,
                "weight": {
                    "value": weight_lbs
                },
                "category": category_raw,
                "source": meta.get("Source", "Archives of Nethys (aonprd.com)"),
                "source_url": full_url,
                "data_source": "aon_scraper"
            }
        }
    except Exception as exc:
        logger.warning(f"Eşya detay çekimi başarısız [{item_name}]: {exc}")
        return None


def run_aon_equipment_scraper(max_per_category: Optional[int] = None):
    """Tüm AoN ekipman kategorilerini tarar ve pf1e_scraped_items.json dosyasına aktarır."""
    logger.info("=== Archives of Nethys (AoN) Ekipman Scraper Başlatılıyor ===")
    
    existing_items = []
    if OUTPUT_JSON.exists():
        try:
            with open(OUTPUT_JSON, "r", encoding="utf-8") as f:
                existing_items = json.load(f)
            logger.info(f"Mevcut json dosyasında {len(existing_items)} adet kayıt bulundu.")
        except Exception:
            existing_items = []

    # Map existing items by lowercase (sistem, kategori, isim)
    seen_keys = {
        (d.get("sistem", "pathfinder1e"), d.get("kategori", "item"), d.get("isim", "").lower().strip())
        for d in existing_items
    }
    
    session = requests.Session()
    new_scraped = []

    for cat in CATEGORIES:
        links = scrape_category_item_links(cat, session)
        if max_per_category and len(links) > max_per_category:
            links = links[:max_per_category]
        
        count_cat = 0
        for name, href in links:
            key = ("pathfinder1e", "item", name.lower().strip())
            if key in seen_keys:
                continue
            
            detail = scrape_item_details(name, href, session)
            if detail:
                new_scraped.append(detail)
                seen_keys.add(key)
                count_cat += 1
                if count_cat % 20 == 0:
                    logger.info(f"[{cat}] {count_cat} eşya çekildi ve işlendi.")
            
            # Etik rate-limiting (0.05sn hızlı & etik gecikme)
            time.sleep(0.05)

        logger.info(f"Kategori [{cat}] tamamlandı. Toplam {count_cat} yeni eşya eklendi.")

    if new_scraped:
        all_combined = existing_items + new_scraped
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
            json.dump(all_combined, f, ensure_ascii=False, indent=2)
        logger.info(f"✅ Başarıyla {len(new_scraped)} yeni ekipman eklendi. Toplam kayıt: {len(all_combined)}")
    else:
        logger.info("Yeni eklenecek benzersiz ekipman bulunamadı veya tümü zaten veritabanında mevcut.")


if __name__ == "__main__":
    max_limit = None
    if len(sys.argv) > 1 and sys.argv[1].isdigit():
        max_limit = int(sys.argv[1])
    run_aon_equipment_scraper(max_per_category=max_limit)
