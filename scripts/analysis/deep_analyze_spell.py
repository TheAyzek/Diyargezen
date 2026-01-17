#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spell sayfalarını derinlemesine analiz et"""

import sys
from pathlib import Path
import requests
from bs4 import BeautifulSoup
import re

if sys.platform == 'win32':
    import codecs
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "https://www.5esrd.com"

test_spells = [
    "acid-splash",  # Cantrip
    "fireball",     # 3rd level
    "bless",        # 1st level
    "magic-missile", # 1st level
    "wish",         # 9th level
]

print("=" * 70)
print("DERİNLEMESİNE SPELL ANALİZİ")
print("=" * 70)
print()

for spell_slug in test_spells:
    url = f"{BASE_URL}/database/spell/{spell_slug}/"
    print(f"\n{'='*70}")
    print(f"📖 {spell_slug.upper()}")
    print("="*70)
    
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(f"❌ Sayfa bulunamadı: {response.status_code}")
        continue
    
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article') or soup.find('body')
    
    if not main_content:
        print("❌ İçerik bulunamadı")
        continue
    
    # HTML yapısını göster
    print("\n📋 HTML YAPISI:")
    print("-" * 70)
    
    # Başlık
    h1 = soup.find('h1')
    if h1:
        print(f"H1: {h1.get_text(strip=True)}")
    
    # Tüm başlıkları bul
    headers = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
    print(f"\nBaşlık sayısı: {len(headers)}")
    for i, h in enumerate(headers[:10], 1):
        print(f"  {i}. <{h.name}> {h.get_text(strip=True)[:60]}")
    
    # İlk paragrafları göster
    paragraphs = main_content.find_all('p')
    print(f"\nParagraf sayısı: {len(paragraphs)}")
    print("\nİlk 5 paragraf:")
    for i, p in enumerate(paragraphs[:5], 1):
        text = p.get_text(strip=True)
        print(f"  {i}. {text[:150]}")
        if len(text) > 150:
            print(f"      ... ({len(text)} karakter)")
    
    # Metin içeriğini analiz et
    full_text = main_content.get_text()
    
    print("\n📝 METİN ANALİZİ:")
    print("-" * 70)
    
    # Level ve School bul
    print("\nLevel/School Pattern Matching:")
    patterns = [
        r'(\d+)(st|nd|rd|th)[\s-]*level[\s]+(\w+)',
        r'cantrip[\s]+(\w+)',
        r'(\d+)[\s-]*level[\s]+(\w+)',
    ]
    
    for pattern in patterns:
        matches = re.finditer(pattern, full_text, re.I)
        for match in matches:
            print(f"  Pattern '{pattern}': {match.group(0)}")
    
    # Casting Time bul
    print("\nCasting Time Patterns:")
    ct_patterns = [
        r'casting\s+time[:\s]+([^\n\r]+?)(?:\n|Range|Components|Duration|$)',
        r'Casting\s+Time[:\s]+([^\n\r]+)',
    ]
    for pattern in ct_patterns:
        match = re.search(pattern, full_text, re.I | re.DOTALL)
        if match:
            print(f"  Found: '{match.group(1).strip()}'")
    
    # Structured data bul (table veya div içinde)
    print("\n📊 YAPISAL VERİ:")
    print("-" * 70)
    
    # Tabloları bul
    tables = main_content.find_all('table')
    print(f"Tablo sayısı: {len(tables)}")
    for i, table in enumerate(tables[:3], 1):
        rows = table.find_all('tr')
        print(f"  Tablo {i}: {len(rows)} satır")
        for row in rows[:3]:
            cells = [cell.get_text(strip=True) for cell in row.find_all(['td', 'th'])]
            if cells:
                print(f"    {' | '.join(cells)}")
    
    # Div'leri kontrol et (spell bilgisi için)
    info_divs = main_content.find_all('div', class_=re.compile(r'spell|info|data', re.I))
    print(f"\nInfo div sayısı: {len(info_divs)}")
    for i, div in enumerate(info_divs[:5], 1):
        print(f"  {i}. Class: {div.get('class')}, Text: {div.get_text(strip=True)[:100]}")

print("\n" + "=" * 70)
print("✅ ANALİZ TAMAMLANDI")
print("=" * 70)


