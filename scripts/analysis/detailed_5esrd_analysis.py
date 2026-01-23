#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com detaylı analiz - Classes ve Spells"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.5esrd.com"

print("=" * 70)
print("5ESRD.COM DETAYLI ANALİZ")
print("=" * 70)
print()

# Classes sayfasını analiz et
print("1. CLASSES SAYFASI ANALİZİ")
print("-" * 70)
classes_url = BASE_URL + "/classes/"
response = requests.get(classes_url, timeout=30)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Classes Database linkini bul
    db_links = soup.find_all('a', href=re.compile(r'/database/classes', re.I))
    print(f"  Classes Database linkleri: {len(db_links)}")
    
    # Tüm class linklerini bul
    class_links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        # Class sayfalarını bul
        if '/classes/' in href.lower() and text and len(text) < 50:
            # Database veya 3rd party linklerini filtrele
            if 'database' not in href.lower() and '3rd-party' not in href.lower() and 'prestige' not in href.lower():
                full_url = urljoin(BASE_URL, href)
                class_links.append((text, full_url))
    
    # Tekrar edenleri kaldır
    unique_classes = list(set(class_links))
    print(f"  Toplam unique class linki: {len(unique_classes)}")
    for name, url in unique_classes[:15]:
        print(f"    - {name}: {url}")
    
    # Database sayfasını kontrol et
    db_url = BASE_URL + "/database/classes/"
    print(f"\n  Database sayfası: {db_url}")
    response_db = requests.get(db_url, timeout=30)
    if response_db.status_code == 200:
        soup_db = BeautifulSoup(response_db.content, 'html.parser')
        db_class_links = soup_db.find_all('a', href=re.compile(r'/classes/[^/]+/?$'))
        print(f"    ✅ Database'de {len(db_class_links)} class linki bulundu")
        for i, link in enumerate(db_class_links[:12], 1):
            print(f"      {i:2d}. {link.get_text(strip=True):30s} | {link.get('href', '')}")
else:
    print(f"  ❌ Classes sayfası bulunamadı: {response.status_code}")

print("\n" + "=" * 70)

# Spells sayfasını analiz et
print("\n2. SPELLS SAYFASI ANALİZİ")
print("-" * 70)
spells_url = BASE_URL + "/spells-a-z/"
response = requests.get(spells_url, timeout=30)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tüm spell linklerini bul
    spell_links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        # Spell sayfalarını bul
        if '/spells/' in href.lower() and text and len(text) < 100:
            full_url = urljoin(BASE_URL, href)
            spell_links.append((text, full_url))
    
    # Tekrar edenleri kaldır
    unique_spells = list(set(spell_links))
    print(f"  Toplam unique spell linki: {len(unique_spells)}")
    print("  İlk 20 spell:")
    for i, (name, url) in enumerate(unique_spells[:20], 1):
        print(f"    {i:2d}. {name:40s} | {url[:60]}...")
    
    # Database sayfasını kontrol et
    db_url = BASE_URL + "/database/spells/"
    print(f"\n  Database sayfası: {db_url}")
    response_db = requests.get(db_url, timeout=30)
    if response_db.status_code == 200:
        soup_db = BeautifulSoup(response_db.content, 'html.parser')
        db_spell_links = soup_db.find_all('a', href=re.compile(r'/spells/[^/]+/?$'))
        print(f"    ✅ Database'de {len(db_spell_links)} spell linki bulundu")
else:
    print(f"  ❌ Spells sayfası bulunamadı: {response.status_code}")

print("\n" + "=" * 70)
print("✅ ANALİZ TAMAMLANDI")
print("=" * 70)


