#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Test class scraping - Wizard class (spellcasting test)"""

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
print("CLASS SCRAPING TEST - Wizard (Spellcasting Test)")
print("=" * 70)
print()

scraper = Dnd5eSrdScraper(rate_limit=2.0)

# Wizard class'ını scrape et
wizard_url = "https://www.5esrd.com/database/class/wizard/"
print(f"Wizard URL: {wizard_url}")
print("Scraping başlıyor...\n")

wizard_data = scraper.scrape_class_detail(wizard_url, "Wizard")

if wizard_data:
    print("✅ Wizard class başarıyla scrape edildi!\n")
    
    # Mevcut Wizard verisi ile karşılaştır
    data_file = Path("data/dnd_data.json")
    if data_file.exists():
        with open(data_file, 'r', encoding='utf-8') as f:
            existing_data = json.load(f)
            existing_wizard = existing_data.get("classes", {}).get("Wizard", {})
            
            print("Mevcut Wizard Verisi ile Karşılaştırma:")
            print("-" * 70)
            print(f"Hit Die - Scraped: {wizard_data.get('hit_die')}, Existing: {existing_wizard.get('hit_die')}")
            print(f"Primary Ability - Scraped: {wizard_data.get('primary_ability')}, Existing: {existing_wizard.get('primary_ability')}")
            print(f"Spellcasting - Scraped: {wizard_data.get('spellcasting')}, Existing: {existing_wizard.get('spellcasting', 'None')}")
            print(f"Class Features - Scraped: {len(wizard_data.get('class_features', {}))} levels, Existing: {len(existing_wizard.get('class_features', {}))} levels")
            
            if wizard_data.get('spellcasting'):
                print(f"\n✅ Spellcasting detected!")
                print(f"   Ability: {wizard_data['spellcasting'].get('spellcasting_ability')}")
            else:
                print("\n❌ Spellcasting NOT detected (should be detected for Wizard)")
else:
    print("❌ Wizard class scrape edilemedi!")

print("\n" + "=" * 70)

