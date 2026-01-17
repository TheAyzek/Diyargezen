#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com yapısını analiz et"""

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
print("5ESRD.COM YAPI ANALİZİ")
print("=" * 70)
print()

# Ana sayfayı çek
print("Ana sayfa analiz ediliyor...")
response = requests.get(BASE_URL, timeout=30)
if response.status_code != 200:
    print(f"❌ Sayfa bulunamadı: {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.content, 'html.parser')

# Navigation menüsünden linkleri bul
print("\n📋 NAVİGASYON MENÜSÜ:")
print("-" * 70)

nav_links = {}
main_nav = soup.find('nav') or soup.find('ul', class_=re.compile(r'nav|menu'))

if main_nav:
    links = main_nav.find_all('a', href=True)
    for link in links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        if text and href:
            # Relatif URL'leri tam URL'e çevir
            if href.startswith('/'):
                full_url = BASE_URL + href
            elif href.startswith('http'):
                full_url = href
            else:
                full_url = BASE_URL + '/' + href
            
            # Kategoriye göre grupla
            if '/races/' in href.lower() or 'race' in text.lower():
                if 'races' not in nav_links:
                    nav_links['races'] = []
                nav_links['races'].append((text, full_url))
            elif '/classes/' in href.lower() or 'class' in text.lower():
                if 'classes' not in nav_links:
                    nav_links['classes'] = []
                nav_links['classes'].append((text, full_url))
            elif '/spells/' in href.lower() or 'spell' in text.lower():
                if 'spells' not in nav_links:
                    nav_links['spells'] = []
                nav_links['spells'].append((text, full_url))
            elif '/feats/' in href.lower() or 'feat' in text.lower():
                if 'feats' not in nav_links:
                    nav_links['feats'] = []
                nav_links['feats'].append((text, full_url))
            elif '/backgrounds/' in href.lower() or 'background' in text.lower():
                if 'backgrounds' not in nav_links:
                    nav_links['backgrounds'] = []
                nav_links['backgrounds'].append((text, full_url))
            elif '/equipment/' in href.lower() or 'equipment' in text.lower() or 'armor' in text.lower() or 'weapon' in text.lower():
                if 'equipment' not in nav_links:
                    nav_links['equipment'] = []
                nav_links['equipment'].append((text, full_url))

# Tüm linkleri liste
all_links = soup.find_all('a', href=True)
print(f"\nToplam link sayısı: {len(all_links)}")

# Önemli kategorileri bul
categories = {
    'races': [],
    'classes': [],
    'spells': [],
    'feats': [],
    'backgrounds': [],
    'equipment': []
}

for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    if not text or len(text) > 100:
        continue
    
    if href.startswith('/'):
        full_url = BASE_URL + href
    elif href.startswith('http'):
        full_url = href
    else:
        continue
    
    # Races
    if '/races/' in href.lower() and text:
        categories['races'].append((text, full_url))
    # Classes
    elif '/classes/' in href.lower() and text and text not in ['Classes', 'Classes Database']:
        categories['classes'].append((text, full_url))
    # Spells
    elif '/spells/' in href.lower() and text:
        categories['spells'].append((text, full_url))
    # Feats
    elif '/feats/' in href.lower() and text:
        categories['feats'].append((text, full_url))
    # Backgrounds
    elif '/backgrounds/' in href.lower() and text:
        categories['backgrounds'].append((text, full_url))
    # Equipment
    elif ('/equipment/' in href.lower() or '/armor/' in href.lower() or '/weapons/' in href.lower()) and text:
        categories['equipment'].append((text, full_url))

# Sonuçları göster
print("\n📊 BULUNAN KATEGORİLER:")
print("=" * 70)

for category, items in categories.items():
    unique_items = list(set(items))  # Tekrar edenleri kaldır
    if unique_items:
        print(f"\n{category.upper()}: {len(unique_items)} öğe")
        for i, (name, url) in enumerate(unique_items[:10], 1):  # İlk 10'unu göster
            print(f"  {i:2d}. {name:40s} | {url[:60]}...")
        if len(unique_items) > 10:
            print(f"  ... ve {len(unique_items) - 10} tane daha")

print("\n" + "=" * 70)
print("✅ ANALİZ TAMAMLANDI")
print("=" * 70)

# Örnek sayfa analizi
print("\n🔍 ÖRNEK SAYFA ANALİZİ:")
print("-" * 70)

# Races sayfasını kontrol et
races_url = BASE_URL + "/races/"
print(f"\nRaces sayfası: {races_url}")
response = requests.get(races_url, timeout=30)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    race_links = soup.find_all('a', href=re.compile(r'/races/[^/]+/?$'))
    print(f"  ✅ {len(race_links)} race linki bulundu")
    for i, link in enumerate(race_links[:5], 1):
        print(f"    {i}. {link.get_text(strip=True)}: {link.get('href', '')}")
else:
    print(f"  ❌ Sayfa bulunamadı: {response.status_code}")

# Classes sayfasını kontrol et
classes_url = BASE_URL + "/classes/"
print(f"\nClasses sayfası: {classes_url}")
response = requests.get(classes_url, timeout=30)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    class_links = soup.find_all('a', href=re.compile(r'/classes/[^/]+/?$'))
    print(f"  ✅ {len(class_links)} class linki bulundu")
    for i, link in enumerate(class_links[:5], 1):
        print(f"    {i}. {link.get_text(strip=True)}: {link.get('href', '')}")
else:
    print(f"  ❌ Sayfa bulunamadı: {response.status_code}")


