#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Power Effects'i kontrol et"""

import sys
import io
import json
from pathlib import Path

# Windows konsol encoding hatası için
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

data_file = Path("data/mm_data.json")
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

effects = data.get('power_effects', {})
print(f"Power Effects: {len(effects)}")
print("\nEffect isimleri ve kategorileri:")
for i, (name, eff) in enumerate(list(effects.items())[:40], 1):
    category = eff.get('category', 'N/A')
    desc_len = len(eff.get('description', ''))
    status = "✅" if desc_len > 50 else "⚠️"
    print(f"  {i:2d}. {status} {name:30s} | Category: {category:10s} | Desc: {desc_len:3d} chars")

