#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com doğru URL'leri bul"""

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
print("5ESRD.COM DOĞRU URL'LERİ BULMA")
print("=" * 70)
print()

# Ana sayfayı çek ve tüm linkleri analiz et
print("Ana sayfa analiz ediliyor...")
response = requests.get(BASE_URL, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

# İlgili linkleri bul
important_links = {
    'spells_database': [],
    'spells_az': [],
    'spells_by_class': [],
    'classes_database': [],
    'classes_list': [],
    'races': [],
    'feats': [],
    'backgrounds': [],
    'equipment': []
}

all_links = soup.find_all('a', href=True)
print(f"Toplam link: {len(all_links)}")

for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True).lower()
    
    if not href or not text:
        continue
    
    # Relatif URL'leri tam URL'e çevir
    if href.startswith('/'):
        full_url = BASE_URL + href
    elif href.startswith('http'):
        full_url = href
    else:
        continue
    
    # Spells
    if 'spell' in text or '/spell' in href.lower():
        if 'database' in text or 'database' in href.lower():
            important_links['spells_database'].append((link.get_text(strip=True), full_url))
        elif 'a-z' in text or 'alphabetical' in text:
            important_links['spells_az'].append((link.get_text(strip=True), full_url))
        elif 'by class' in text or 'class' in text:
            important_links['spells_by_class'].append((link.get_text(strip=True), full_url))
    
    # Classes
    if 'class' in text and '/class' in href.lower():
        if 'database' in text or 'database' in href.lower():
            important_links['classes_database'].append((link.get_text(strip=True), full_url))
        else:
            important_links['classes_list'].append((link.get_text(strip=True), full_url))
    
    # Races
    if 'race' in text or '/race' in href.lower():
        important_links['races'].append((link.get_text(strip=True), full_url))
    
    # Feats
    if 'feat' in text or '/feat' in href.lower():
        important_links['feats'].append((link.get_text(strip=True), full_url))
    
    # Backgrounds
    if 'background' in text or '/background' in href.lower():
        important_links['backgrounds'].append((link.get_text(strip=True), full_url))
    
    # Equipment
    if 'equipment' in text or '/equipment' in href.lower() or 'armor' in text or 'weapon' in text:
        important_links['equipment'].append((link.get_text(strip=True), full_url))

# Sonuçları göster
print("\n" + "=" * 70)
print("BULUNAN URL'LER")
print("=" * 70)

for category, links in important_links.items():
    unique_links = list(set(links))
    if unique_links:
        print(f"\n{category.upper()}: {len(unique_links)} link")
        for name, url in unique_links[:5]:
            # URL'in çalışıp çalışmadığını test et
            test_response = requests.head(url, timeout=10, allow_redirects=True)
            status = "✅" if test_response.status_code == 200 else f"❌ {test_response.status_code}"
            print(f"  {status} {name:40s} | {url}")

# Özel test: Classes Database
print("\n" + "=" * 70)
print("CLASSES DATABASE TEST")
print("=" * 70)
test_urls = [
    "https://www.5esrd.com/database/classes/",
    "https://www.5esrd.com/classes/",
    "https://www.5esrd.com/character-creation/classes/"
]

for url in test_urls:
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        print(f"{'✅' if response.status_code == 200 else '❌'} {url} - {response.status_code}")
    except:
        print(f"❌ {url} - ERROR")

# Özel test: Spells Database
print("\n" + "=" * 70)
print("SPELLS DATABASE TEST")
print("=" * 70)
test_urls = [
    "https://www.5esrd.com/database/spells/",
    "https://www.5esrd.com/spellcasting/",
    "https://www.5esrd.com/spells/",
    "https://www.5esrd.com/spellcasting/spells/"
]

for url in test_urls:
    try:
        response = requests.head(url, timeout=10, allow_redirects=True)
        print(f"{'✅' if response.status_code == 200 else '❌'} {url} - {response.status_code}")
    except:
        print(f"❌ {url} - ERROR")


