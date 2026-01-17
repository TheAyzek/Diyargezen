#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test race scraping - Dragonborn race"""

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
print("RACE SCRAPING TEST - Dragonborn")
print("=" * 70)
print()

scraper = Dnd5eSrdScraper(rate_limit=2.0)

# Dragonborn race'ini scrape et
dragonborn_url = "https://www.5esrd.com/races/dragonborn/"
print(f"Dragonborn URL: {dragonborn_url}")
print("Scraping başlıyor...\n")

dragonborn_data = scraper.scrape_race_detail(dragonborn_url, "Dragonborn")

if dragonborn_data:
    print("✅ Dragonborn race başarıyla scrape edildi!\n")
    print("Scraped Data:")
    print("-" * 70)
    print(json.dumps(dragonborn_data, indent=2, ensure_ascii=False))
    print("-" * 70)
    
    # Mevcut Dragonborn verisi ile karşılaştır
    data_file = Path("data/dnd_data.json")
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_races = existing_data.get("races", {})
            
            # Dragonborn'u bul (subrace olabilir)
            existing_dragonborn = existing_races.get("Dragonborn") or existing_races.get("Dragonborn (Standard)")
            
            if existing_dragonborn:
                print("\nMevcut Dragonborn Verisi ile Karşılaştırma:")
                print("-" * 70)
                print(f"Speed - Scraped: {dragonborn_data.get('speed')}, Existing: {existing_dragonborn.get('speed')}")
                print(f"ASI - Scraped: {dragonborn_data.get('ability_score_increase')}, Existing: {existing_dragonborn.get('ability_score_increase')}")
                print(f"Traits - Scraped: {len(dragonborn_data.get('traits', []))}, Existing: {len(existing_dragonborn.get('traits', []))}")
                print(f"Languages - Scraped: {dragonborn_data.get('languages')}, Existing: {existing_dragonborn.get('languages')}")
else:
    print("❌ Dragonborn race scrape edilemedi!")

print("\n" + "=" * 70)

