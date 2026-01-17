#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test class scraping - Fighter class"""

import sys
import io
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper
import json

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

print("=" * 70)
print("CLASS SCRAPING TEST - Fighter")
print("=" * 70)
print()

scraper = Dnd5eSrdScraper(rate_limit=2.0)  # Daha yavaş (2 saniye delay)

# Fighter class'ını scrape et
fighter_url = "https://www.5esrd.com/database/class/fighter/"
print(f"Fighter URL: {fighter_url}")
print("Scraping başlıyor...\n")

fighter_data = scraper.scrape_class_detail(fighter_url, "Fighter")

if fighter_data:
    print("✅ Fighter class başarıyla scrape edildi!\n")
    print("Scraped Data:")
    print("-" * 70)
    print(json.dumps(fighter_data, indent=2, ensure_ascii=False))
    print("-" * 70)
    
    # Mevcut Fighter verisi ile karşılaştır
    data_file = Path("data/dnd_data.json")
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_fighter = existing_data.get("classes", {}).get("Fighter", {})
            
            print("\nMevcut Fighter Verisi ile Karşılaştırma:")
            print("-" * 70)
            print(f"Hit Die - Scraped: {fighter_data.get('hit_die')}, Existing: {existing_fighter.get('hit_die')}")
            print(f"Primary Ability - Scraped: {fighter_data.get('primary_ability')}, Existing: {existing_fighter.get('primary_ability')}")
            print(f"Saving Throws - Scraped: {fighter_data.get('saving_throws')}, Existing: {existing_fighter.get('saving_throws')}")
            print(f"Class Skills - Scraped: {len(fighter_data.get('class_skills', []))}, Existing: {len(existing_fighter.get('class_skills', []))}")
            print(f"Class Features - Scraped: {len(fighter_data.get('class_features', {}))} levels, Existing: {len(existing_fighter.get('class_features', {}))} levels")
            print(f"Proficiencies Weapons - Scraped: {fighter_data.get('proficiencies', {}).get('weapons', [])}, Existing: {existing_fighter.get('proficiencies', {}).get('weapons', [])}")
            print(f"Spellcasting - Scraped: {fighter_data.get('spellcasting')}, Existing: {existing_fighter.get('spellcasting', 'None')}")
            print(f"Starting Equipment - Scraped: {len(fighter_data.get('starting_equipment_options', []))} options, Existing: {len(existing_fighter.get('starting_equipment_options', []))} options")
            
            # İlk birkaç level feature'ını göster
            scraped_features = fighter_data.get('class_features', {})
            if scraped_features:
                print("\nScraped Features (ilk 5 level):")
                for level in sorted([int(k) for k in scraped_features.keys()])[:5]:
                    features = scraped_features[str(level)].get('features', [])
                    print(f"  Level {level}: {features}")
else:
    print("❌ Fighter class scrape edilemedi!")

print("\n" + "=" * 70)

