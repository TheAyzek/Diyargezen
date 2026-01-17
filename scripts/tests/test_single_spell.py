#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Tek bir spell'i detaylı test et"""

import sys
from pathlib import Path

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.dnd_5esrd_scraper import Dnd5eSrdScraper

scraper = Dnd5eSrdScraper(rate_limit=1.0)

# Bilinen spell'leri test et
test_spells = [
    ("acid-splash", "Acid Splash"),
    ("fireball", "Fireball"),
    ("bless", "Bless"),
]

print("=" * 70)
print("SINGLE SPELL TEST")
print("=" * 70)
print()

for slug, name in test_spells:
    url = f"https://www.5esrd.com/database/spell/{slug}/"
    print(f"\n📖 {name.upper()}")
    print("-" * 70)
    
    spell = scraper.scrape_spell_detail(url, name)
    if spell:
        print(f"  ✅ Level: {spell.get('level', '?')}")
        print(f"  ✅ School: {spell.get('school', '?')}")
        print(f"  ✅ Casting Time: {spell.get('casting_time', '?')}")
        print(f"  ✅ Range: {spell.get('range', '?')}")
        print(f"  ✅ Components: {spell.get('components', '?')}")
        print(f"  ✅ Duration: {spell.get('duration', '?')}")
        print(f"  ✅ Concentration: {spell.get('concentration', False)}")
        print(f"  ✅ Ritual: {spell.get('ritual', False)}")
        print(f"  ✅ Description: {len(spell.get('description', ''))} karakter")
    else:
        print(f"  ❌ Spell çekilemedi")


