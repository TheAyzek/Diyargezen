#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Parsing sorunlarını analiz et"""

import sys
import requests
from bs4 import BeautifulSoup
import re

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "https://www.5esrd.com"

# Çeşitli spell'leri test et (farklı formatlar için)
test_spells = [
    ("acid-splash", "Cantrip test"),
    ("fireball", "3rd level test"),
    ("bless", "1st level with M component"),
    ("magic-missile", "1st level simple"),
    ("wish", "9th level"),
    ("heal", "6th level"),
    ("cure-wounds", "1st level"),
    ("mage-armor", "1st level"),
    ("shield", "1st level reaction"),
    ("identify", "1st level ritual"),
]

print("=" * 70)
print("PARSING SORUNLARI ANALİZİ")
print("=" * 70)
print()

issues_found = []

for slug, test_name in test_spells:
    url = f"{BASE_URL}/database/spell/{slug}/"
    print(f"\n{'='*70}")
    print(f"📖 {test_name}: {slug}")
    print("-" * 70)
    
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print("❌ Sayfa bulunamadı")
        continue
    
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article') or soup.find('body')
    
    if not main_content:
        print("❌ İçerik bulunamadı")
        continue
    
    paragraphs = main_content.find_all('p')
    
    # İlk iki paragrafı göster
    print("\nİlk 3 paragraf:")
    for i, p in enumerate(paragraphs[:3], 1):
        text = p.get_text(strip=True)
        print(f"  P{i}: {text[:150]}")
    
    # Stats text'i bul
    stats_text = ""
    if len(paragraphs) > 1:
        stats_text = paragraphs[1].get_text(strip=True)
    
    print(f"\nStats Text: {stats_text[:200]}")
    
    # Parsing testi
    print("\n🔍 Parsing Test:")
    
    # Casting Time
    ct_match = re.search(r'Casting\s+Time[:\s]+([^R]+?)(?:Range|$|You|A |Target)', stats_text, re.I)
    if ct_match:
        print(f"  ✅ Casting Time: '{ct_match.group(1).strip()}'")
    else:
        print("  ❌ Casting Time: BULUNAMADI")
        issues_found.append((slug, "Casting Time"))
    
    # Range
    range_match = re.search(r'Range[:\s]+([^C]+?)(?:Components|Duration|$|You|A |Target)', stats_text, re.I)
    if range_match:
        print(f"  ✅ Range: '{range_match.group(1).strip()}'")
    else:
        print("  ❌ Range: BULUNAMADI")
        issues_found.append((slug, "Range"))
    
    # Components
    comp_match = re.search(r'Components[:\s]+([^D]+?(?:\([^)]+\))?[^D]*?)(?:Duration|$|You|A |Target|Concentration)', stats_text, re.I)
    if comp_match:
        comp_text = comp_match.group(1).strip()
        print(f"  ✅ Components: '{comp_text[:80]}'")
        if comp_text.count('(') > comp_text.count(')'):
            print("     ⚠️  Açık parantez var!")
            issues_found.append((slug, "Components (open parenthesis)"))
    else:
        print("  ❌ Components: BULUNAMADI")
        issues_found.append((slug, "Components"))
    
    # Duration
    dur_match = re.search(r'Duration[:\s]+([^Y]+?)(?:You |A |Target|At Higher|This spell|$)', stats_text, re.I | re.DOTALL)
    if dur_match:
        dur_text = dur_match.group(1).strip()
        # "You" ile başlayan metni kontrol et
        if 'You ' in dur_text or 'Your ' in dur_text or 'A ' in dur_text and len(dur_text.split('A ')[0].strip()) < 50:
            print(f"  ⚠️  Duration: '{dur_text[:80]}' (İçerik kirliliği var)")
            issues_found.append((slug, "Duration (content pollution)"))
        else:
            print(f"  ✅ Duration: '{dur_text[:80]}'")
    else:
        print("  ❌ Duration: BULUNAMADI")
        issues_found.append((slug, "Duration"))

print("\n" + "=" * 70)
print("BULUNAN SORUNLAR")
print("=" * 70)
if issues_found:
    for spell, issue in issues_found:
        print(f"  ⚠️  {spell}: {issue}")
else:
    print("  ✅ Hiç sorun bulunamadı!")
print()
print("=" * 70)


