#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Scraped class'ları kontrol et"""

import json
from pathlib import Path

print("=" * 70)
print("SCRAPED CLASSES KONTROLÜ")
print("=" * 70)
print()

# Cache dosyasını kontrol et
cache_file = Path("data/cache/classes_cache.json")
if cache_file.exists():
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    classes = cache.get('classes', {})
    print(f"📦 Cache'deki class sayısı: {len(classes)}")
    print(f"Class'lar: {', '.join(sorted(classes.keys()))}")
    print()

# dnd_data.json'ı kontrol et
data_file = Path("data/dnd_data.json")
if data_file.exists():
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    classes = data.get('classes', {})
    print(f"📦 dnd_data.json'daki class sayısı: {len(classes)}")
    print(f"Class'lar: {', '.join(sorted(classes.keys()))}")
    print()

print("=" * 70)

