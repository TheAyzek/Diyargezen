#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Çekim ilerlemesini kontrol et"""

import sys
from pathlib import Path
import json
from datetime import datetime

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

print("=" * 70)
print("ÇEKİM İLERLEME KONTROLÜ")
print("=" * 70)
print()

# Cache dosyasını kontrol et
cache_file = Path("data/cache/spells_cache.json")
if cache_file.exists():
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache_data = json.load(f)
    spells_in_cache = cache_data.get('spells', {})
    print(f"Cache'deki spell sayısı: {len(spells_in_cache)}")
    if spells_in_cache:
        scraped_at = cache_data.get('scraped_at', 'Bilinmiyor')
        print(f"Son çekim zamanı: {scraped_at}")
        print(f"\nİlk 5 spell:")
        for i, name in enumerate(list(spells_in_cache.keys())[:5], 1):
            print(f"  {i}. {name}")
else:
    print("Cache dosyası bulunamadı")

print()

# dnd_data.json'daki spell sayısını kontrol et
dnd_file = Path("data/dnd_data.json")
if dnd_file.exists():
    with open(dnd_file, 'r', encoding='utf-8') as f:
        dnd_data = json.load(f)
    spells_in_dnd = dnd_data.get('spells', {})
    print(f"dnd_data.json'daki spell sayısı: {len(spells_in_dnd)}")
    
    # Tam veriye sahip spell sayısı
    complete = 0
    required_fields = ['level', 'school', 'casting_time', 'range', 'components', 'duration', 'description']
    for name, spell in spells_in_dnd.items():
        if all(spell.get(field) for field in required_fields):
            complete += 1
    
    print(f"Tam veriye sahip spell: {complete} ({complete*100/len(spells_in_dnd):.1f}%)" if spells_in_dnd else "0")

print()
print("=" * 70)


