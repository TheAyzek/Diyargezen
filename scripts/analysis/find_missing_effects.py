#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Eksik effect'leri bul"""

import json
import requests
from bs4 import BeautifulSoup
import re
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.d20herosrd.com"
url = BASE_URL + "/6-powers/effects/effect-descriptions/"

print("Eksik effect'ler bulunuyor...")
response = requests.get(url, timeout=30)
if response.status_code != 200:
    print(f"❌ Sayfa bulunamadı: {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.content, 'html.parser')
main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')

# Mevcut effect'leri yükle
data_file = "data/mm_data.json"
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

existing_effects = set(data.get('power_effects', {}).keys())
print(f"📊 Mevcut effect'ler: {len(existing_effects)}")

# Tüm effect linklerini bul
effect_links = main_content.find_all('a', href=re.compile(r'/6-powers/effects/effect-descriptions/[^/]+/$'))
print(f"📊 Toplam effect linki: {len(effect_links)}")

# Effect isimlerini çıkar
found_effects = set()
for link in effect_links:
    effect_name = link.get_text(strip=True)
    # Parantez içindeki category'yi kaldır
    clean_name = re.sub(r'\s*\([^)]+\)', '', effect_name).strip()
    if clean_name and len(clean_name) < 100:
        found_effects.add(clean_name)

print(f"📊 Bulunan effect'ler: {len(found_effects)}")

# Eksik effect'leri bul
missing_effects = found_effects - existing_effects
print(f"\n❌ Eksik effect'ler: {len(missing_effects)}")

if missing_effects:
    print("\nEksik effect listesi:")
    for i, effect in enumerate(sorted(missing_effects), 1):
        print(f"  {i:2d}. {effect}")
        
    # Eksik effect linklerini bul
    print("\n🔍 Eksik effect linkleri:")
    missing_links = []
    for link in effect_links:
        effect_name = link.get_text(strip=True)
        clean_name = re.sub(r'\s*\([^)]+\)', '', effect_name).strip()
        if clean_name in missing_effects:
            href = link.get('href', '')
            missing_links.append((clean_name, href))
            print(f"  - {clean_name}: {href}")
    
    print(f"\n📋 Toplam eksik link: {len(missing_links)}")
else:
    print("✅ Tüm effect'ler mevcut!")


