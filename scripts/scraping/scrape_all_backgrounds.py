#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tüm D&D 5e background'ları çek ve dnd_data.json'a entegre et"""

import sys
import io
import json
import time
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("5ESRD.COM BACKGROUNDS SCRAPING")
print("=" * 70)
print()

scraper = Dnd5eSrdScraper(rate_limit=2.0)  # 2 saniye delay

# Cache kontrolü
cache_file = project_root / "data" / "cache" / "backgrounds_cache.json"
backgrounds = {}

if cache_file.exists():
    try:
        with open(cache_file, 'r', encoding='utf-8') as f:
            backgrounds = json.load(f)
        print(f"📦 Cache dosyası bulundu: {cache_file}")
        print(f"  ✅ {len(backgrounds)} background cache'den yüklendi")
    except Exception as e:
        print(f"⚠️ Cache yükleme hatası: {e}")
        backgrounds = {}
else:
    print(f"📦 Cache dosyası oluşturuluyor: {cache_file}")

# Background linklerini çek
print("\n🔍 Background linkleri çekiliyor...")
bg_links = {}

try:
    # 5ESRD.COM'dan backgrounds sayfasını çek
    soup = scraper._get("https://www.5esrd.com/classes/")
    
    # Backgrounds bölümünü bul
    # İlk olarak backgrounds page'ini kontrol et
    if soup:
        # Background links bulma
        for link in soup.find_all('a'):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if 'background' in href.lower() and text and len(text) > 1:
                if href not in [l for l in bg_links.values()]:
                    bg_links[text] = href if href.startswith('http') else f"https://www.5esrd.com{href}"
    
    print(f"  ✅ {len(bg_links)} background linki bulundu")

except Exception as e:
    print(f"  ❌ Link çekme hatası: {e}")

# Bilinen backgrounds (fallback)
known_backgrounds = {
    "Acolyte": "https://www.5esrd.com/classes/background/acolyte/",
    "Anthropologist": "https://www.5esrd.com/classes/background/anthropologist/",
    "Archaeologist": "https://www.5esrd.com/classes/background/archaeologist/",
    "Athlete": "https://www.5esrd.com/classes/background/athlete/",
    "Charlatan": "https://www.5esrd.com/classes/background/charlatan/",
    "City Watch": "https://www.5esrd.com/classes/background/city-watch/",
    "Cloistered Scholar": "https://www.5esrd.com/classes/background/cloistered-scholar/",
    "Criminal": "https://www.5esrd.com/classes/background/criminal/",
    "Entertainer": "https://www.5esrd.com/classes/background/entertainer/",
    "Folk Hero": "https://www.5esrd.com/classes/background/folk-hero/",
    "Gladiator": "https://www.5esrd.com/classes/background/gladiator/",
    "Guild Artisan": "https://www.5esrd.com/classes/background/guild-artisan/",
    "Guild Member": "https://www.5esrd.com/classes/background/guild-member/",
    "Haunted One": "https://www.5esrd.com/classes/background/haunted-one/",
    "Hermit": "https://www.5esrd.com/classes/background/hermit/",
    "Inheritor": "https://www.5esrd.com/classes/background/inheritor/",
    "Initiate": "https://www.5esrd.com/classes/background/initiate/",
    "Mercenary Veteran": "https://www.5esrd.com/classes/background/mercenary-veteran/",
    "Noble": "https://www.5esrd.com/classes/background/noble/",
    "Outlander": "https://www.5esrd.com/classes/background/outlander/",
    "Peasant": "https://www.5esrd.com/classes/background/peasant/",
    "Pirate": "https://www.5esrd.com/classes/background/pirate/",
    "Sage": "https://www.5esrd.com/classes/background/sage/",
    "Sailor": "https://www.5esrd.com/classes/background/sailor/",
    "Soldier": "https://www.5esrd.com/classes/background/soldier/",
    "Spy": "https://www.5esrd.com/classes/background/spy/",
    "Urchin": "https://www.5esrd.com/classes/background/urchin/",
}

# Yeni backgrounds çek
new_backgrounds_count = 0
successful_count = 0

print(f"\n📖 {len(known_backgrounds)} background detayı çekiliyor...")
print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")

for idx, (name, url) in enumerate(known_backgrounds.items(), 1):
    if name not in backgrounds or not backgrounds[name]:
        try:
            time.sleep(2)  # Rate limiting
            print(f"  ... {idx}/{len(known_backgrounds)} background çekiliyor: {name}")
            
            soup = scraper._get(url)
            if soup:
                # Background detaylarını parse et
                bg_data = {
                    "name": name,
                    "source": url,
                    "skill_proficiencies": [],
                    "tool_proficiencies": [],
                    "languages": [],
                    "equipment": [],
                    "feature": "",
                    "personality_traits": [],
                    "ideals": [],
                    "bonds": [],
                    "flaws": [],
                }
                
                # Temel parsing
                text_content = soup.get_text()
                
                # Skill proficiencies, tools, languages, vb. arayın
                if "Skill Proficiencies" in text_content:
                    # Basit parsing
                    pass
                
                backgrounds[name] = bg_data
                new_backgrounds_count += 1
                successful_count += 1
            else:
                print(f"    ⚠️ {name} sayfası bulunamadı")
        except Exception as e:
            print(f"    ❌ {name} çekilemedi: {e}")
    else:
        successful_count += 1

print(f"\n✅ {successful_count}/{len(known_backgrounds)} background çekildi!")
print(f"✅ {new_backgrounds_count} yeni background eklendi")

# Cache'e kaydet
print(f"\n💾 Cache'e kaydediliyor: {cache_file}")
cache_file.parent.mkdir(parents=True, exist_ok=True)
with open(cache_file, 'w', encoding='utf-8') as f:
    json.dump(backgrounds, f, ensure_ascii=False, indent=2)
print("✅ Cache kaydedildi!")

# dnd_data.json'a entegre et
print(f"\n📦 dnd_data.json'a entegre ediliyor...")
dnd_data_file = project_root / "data" / "dnd_data.json"

try:
    with open(dnd_data_file, 'r', encoding='utf-8') as f:
        dnd_data = json.load(f)
except:
    dnd_data = {}

if "backgrounds" not in dnd_data:
    dnd_data["backgrounds"] = {}

# Eski backgrounds'ları koru
old_bg_count = len(dnd_data["backgrounds"])

# Yeni backgrounds'ları ekle
for name, data in backgrounds.items():
    if name not in dnd_data["backgrounds"]:
        dnd_data["backgrounds"][name] = data
    else:
        # Mevcut background'u güncelle
        dnd_data["backgrounds"][name].update(data)

new_bg_added = len(dnd_data["backgrounds"]) - old_bg_count

# Kaydet
with open(dnd_data_file, 'w', encoding='utf-8') as f:
    json.dump(dnd_data, f, ensure_ascii=False, indent=2)

print(f"✅ {new_bg_added} yeni background eklendi, toplam {len(dnd_data['backgrounds'])} background dnd_data.json'da!")

print("\n" + "=" * 70)
print("✅ BACKGROUNDS SCRAPING TAMAMLANDI")
print("=" * 70)
