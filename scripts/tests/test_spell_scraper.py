#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spell scraper test"""

import sys
from pathlib import Path

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

print("=" * 70)
print("SPELL SCRAPER TEST")
print("=" * 70)
print()

# Scraper oluştur
scraper = Dnd5eSrdScraper(rate_limit=1.0)

# Test: İlk 5 spell'i çek
print("Test: İlk 5 spell çekiliyor...")
print()

spells = scraper.scrape_all_spells(max_spells=5, force_refresh=True)

print()
print("=" * 70)
print("SONUÇLAR")
print("=" * 70)
print(f"\n✅ {len(spells)} spell çekildi\n")

for name, spell in spells.items():
    print(f"📖 {name}")
    print(f"   Level: {spell.get('level', '?')}")
    print(f"   School: {spell.get('school', '?')}")
    print(f"   Casting Time: {spell.get('casting_time', '?')}")
    print(f"   Range: {spell.get('range', '?')}")
    print(f"   Components: {spell.get('components', '?')}")
    print(f"   Duration: {spell.get('duration', '?')}")
    print(f"   Classes: {', '.join(spell.get('classes', []))}")
    print(f"   Description: {len(spell.get('description', ''))} karakter")
    print()

