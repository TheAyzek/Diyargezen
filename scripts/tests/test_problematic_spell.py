#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Sorunlu spell'leri test et"""

import sys
from pathlib import Path

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

scraper = Dnd5eSrdScraper(rate_limit=1.0)

# Eksik verili spell'leri test et
problematic = [
    "claws-of-darkness",
    "curse-of-whispered-secrets",
    "fuel-charge",
    "rum-rations",
]

print("=" * 70)
print("SORUNLU SPELL TESTİ")
print("=" * 70)
print()

for slug in problematic:
    url = f"https://www.5esrd.com/database/spell/{slug}/"
    name = slug.replace('-', ' ').title()
    print(f"\n{'='*70}")
    print(f"📖 {name.upper()}")
    print("-" * 70)
    
    spell = scraper.scrape_spell_detail(url, name)
    if spell:
        print(f"  Level: {spell.get('level', '❌ None')}")
        print(f"  School: {spell.get('school', '❌ None')}")
        print(f"  Casting Time: {spell.get('casting_time', '❌ None')}")
        print(f"  Range: {spell.get('range', '❌ None')}")
        print(f"  Components: {spell.get('components', '❌ None')}")
        print(f"  Duration: {spell.get('duration', '❌ None')}")
        print(f"  Description: {len(spell.get('description', ''))} karakter")
    else:
        print("  ❌ Spell çekilemedi")

print("\n" + "=" * 70)


