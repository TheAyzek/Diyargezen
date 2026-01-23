#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Duplicate class'ları temizle"""

import json
from pathlib import Path

# Cache dosyasını temizle
cache_file = Path("data/cache/classes_cache.json")
if cache_file.exists():
    with open(cache_file, 'r', encoding='utf-8') as f:
        cache = json.load(f)
    
    classes = cache.get('classes', {})
    if 'cleric' in classes and 'Cleric' in classes:
        del classes['cleric']
        cache['classes'] = classes
        cache['total'] = len(classes)
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache, f, ensure_ascii=False, indent=2)
        print("✅ Cache'den duplicate 'cleric' temizlendi")

# dnd_data.json'ı temizle
data_file = Path("data/dnd_data.json")
if data_file.exists():
    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    classes = data.get('classes', {})
    if 'cleric' in classes:
        del classes['cleric']
        data['classes'] = classes
        
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        print("✅ dnd_data.json'dan duplicate 'cleric' temizlendi")

print("✅ Duplicate temizleme tamamlandı!")

