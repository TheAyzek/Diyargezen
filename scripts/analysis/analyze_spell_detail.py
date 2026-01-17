#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spell detay sayfası analizi"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.5esrd.com"

def analyze_spell_page(url):
    """Spell sayfasını analiz et"""
    print(f"\n{'='*70}")
    print(f"Analiz: {url}")
    print("="*70)
    
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(f"❌ Sayfa bulunamadı: {response.status_code}")
        return None
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Ana içerik
    main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
    if not main_content:
        main_content = soup.find('body')
    
    # Başlık
    title = soup.find('h1') or soup.find('h2') or soup.find('title')
    spell_name = title.get_text(strip=True) if title else "Unknown"
    print(f"📖 Spell Adı: {spell_name}")
    
    # İçeriği analiz et
    text_content = main_content.get_text() if main_content else ""
    
    # Spell bilgilerini bul (level, school, casting time, range, etc.)
    spell_info = {}
    
    # Level ve School bulma
    level_match = re.search(r'(\d+)(st|nd|rd|th)?\s*level\s+(\w+)', text_content, re.I)
    if level_match:
        spell_info['level'] = level_match.group(1)
        spell_info['school'] = level_match.group(3)
        print(f"  Level: {spell_info['level']}")
        print(f"  School: {spell_info['school']}")
    
    # Cantrip kontrolü
    if 'cantrip' in text_content.lower():
        spell_info['level'] = 0
        spell_info['school'] = re.search(r'cantrip.*?(\w+)', text_content, re.I)
        if spell_info['school']:
            spell_info['school'] = spell_info['school'].group(1)
        print(f"  Cantrip: Yes")
    
    # Casting Time
    casting_match = re.search(r'casting\s+time[:\s]+([^\n]+)', text_content, re.I)
    if casting_match:
        spell_info['casting_time'] = casting_match.group(1).strip()
        print(f"  Casting Time: {spell_info['casting_time']}")
    
    # Range
    range_match = re.search(r'range[:\s]+([^\n]+)', text_content, re.I)
    if range_match:
        spell_info['range'] = range_match.group(1).strip()
        print(f"  Range: {spell_info['range']}")
    
    # Components
    components_match = re.search(r'components[:\s]+([^\n]+)', text_content, re.I)
    if components_match:
        components = components_match.group(1).strip()
        spell_info['components'] = components
        print(f"  Components: {components}")
    
    # Duration
    duration_match = re.search(r'duration[:\s]+([^\n]+)', text_content, re.I)
    if duration_match:
        spell_info['duration'] = duration_match.group(1).strip()
        print(f"  Duration: {spell_info['duration']}")
    
    # Description
    # Tüm paragrafları al
    paragraphs = main_content.find_all('p') if main_content else []
    description_parts = []
    for p in paragraphs:
        text = p.get_text(strip=True)
        if len(text) > 50 and 'Green Ronin' not in text and 'OGN' not in text:
            description_parts.append(text)
    
    if description_parts:
        spell_info['description'] = '\n\n'.join(description_parts)
        print(f"  Description: {len(spell_info['description'])} karakter")
    
    # Classes (hangi sınıflar bu büyüyü kullanabilir)
    classes_found = []
    class_names = ['Bard', 'Cleric', 'Druid', 'Paladin', 'Ranger', 'Sorcerer', 'Warlock', 'Wizard', 'Artificer']
    for class_name in class_names:
        if class_name.lower() in text_content.lower():
            classes_found.append(class_name)
    
    if classes_found:
        spell_info['classes'] = classes_found
        print(f"  Classes: {', '.join(classes_found)}")
    
    return spell_info

# Test spell'leri analiz et
test_spells = [
    "https://www.5esrd.com/database/spell/acid-splash/",
    "https://www.5esrd.com/database/spell/fireball/",
    "https://www.5esrd.com/database/spell/magic-missile/",
    "https://www.5esrd.com/database/spell/bless/",
]

print("=" * 70)
print("SPELL DETAY ANALİZİ")
print("=" * 70)

for url in test_spells:
    analyze_spell_page(url)

print("\n" + "=" * 70)
print("✅ ANALİZ TAMAMLANDI")
print("=" * 70)


