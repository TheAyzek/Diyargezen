#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com Races analizi - Core races"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.5esrd.com"

print("=" * 70)
print("5ESRD.COM RACES ANALİZİ - CORE RACES")
print("=" * 70)
print()

# Core races listesi (bilinen D&D 5e core races)
core_races = [
    ("Dragonborn", f"{BASE_URL}/races/dragonborn/"),
    ("Dwarf", f"{BASE_URL}/races/dwarf/"),
    ("Elf", f"{BASE_URL}/races/elf/"),
    ("Gnome", f"{BASE_URL}/races/gnome/"),
    ("Halfling", f"{BASE_URL}/races/halfling/"),
    ("Half-Elf", f"{BASE_URL}/races/half-elf/"),
    ("Half-Orc", f"{BASE_URL}/races/half-orc/"),
    ("Human", f"{BASE_URL}/races/human/"),
    ("Tiefling", f"{BASE_URL}/races/tiefling/"),
]

print(f"📋 {len(core_races)} core race test ediliyor...\n")

working_races = []
for name, url in core_races:
    print(f"  Test: {name} - {url}")
    try:
        response = requests.get(url, timeout=30)
        if response.status_code == 200:
            print(f"    ✅ Status 200")
            working_races.append((name, url))
        else:
            print(f"    ❌ Status {response.status_code}")
    except Exception as e:
        print(f"    ❌ Hata: {e}")
    print()

print(f"\n✅ {len(working_races)} core race URL'i çalışıyor\n")

# İlk working race'in detay sayfasını analiz et
if working_races:
    print("2. ÖRNEK RACE DETAY SAYFASI ANALİZİ")
    print("-" * 70)
    test_name, test_url = working_races[0]
    print(f"Race: {test_name}")
    print(f"URL: {test_url}\n")
    
    test_response = requests.get(test_url, timeout=30)
    if test_response.status_code == 200:
        test_soup = BeautifulSoup(test_response.content, 'html.parser')
        
        # Main content alanını bul
        main_content = test_soup.find('div', class_='content') or test_soup.find('main') or test_soup.find('article')
        if not main_content:
            main_content = test_soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Paragrafları al
            paragraphs = main_content.find_all('p')
            print(f"Paragraf sayısı: {len(paragraphs)}\n")
            
            # İlk 10 paragrafı göster
            print("İlk 10 paragraf:")
            print("-" * 70)
            for i, p in enumerate(paragraphs[:10], 1):
                text = p.get_text(strip=True)
                if text and len(text) > 20:
                    print(f"  {i}. {text[:200]}")
            
            # Text content al
            text_content = main_content.get_text()
            
            # Speed pattern'ini ara
            print("\n" + "-" * 70)
            speed_patterns = [
                r'Speed[:\s]+(\d+)\s*ft',
                r'Base\s+Speed[:\s]+(\d+)',
                r'(\d+)\s*ft.*speed',
            ]
            for pattern in speed_patterns:
                match = re.search(pattern, text_content[:3000], re.I)
                if match:
                    print(f"✅ Speed bulundu: {match.group(1)} ft")
                    break
            
            # Ability Score Increase pattern'ini ara
            asi_patterns = [
                r'Ability\s+Score\s+Increase[:\s]+(.+?)(?:\n\n|\n[A-Z]|Traits|Languages|Size|$)',
                r'ASI[:\s]+(.+?)(?:\n|$)',
            ]
            for pattern in asi_patterns:
                match = re.search(pattern, text_content[:3000], re.I | re.DOTALL)
                if match:
                    asi_text = match.group(1).strip()[:200]
                    print(f"✅ Ability Score Increase bulundu: {asi_text}")
                    break

print("\n" + "=" * 70)
