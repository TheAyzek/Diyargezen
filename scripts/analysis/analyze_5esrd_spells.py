#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com Spells yapısını analiz et"""

import sys
import io
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.5esrd.com"

print("=" * 70)
print("5ESRD.COM SPELLS ANALİZİ")
print("=" * 70)
print()

# Spellcasting ana sayfası
print("1. SPELLCASTING ANA SAYFASI")
print("-" * 70)
spellcasting_url = BASE_URL + "/spellcasting/"
response = requests.get(spellcasting_url, timeout=30)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tüm linkleri bul
    all_links = soup.find_all('a', href=True)
    spell_links = []
    
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
        
        # Spell ile ilgili linkleri bul
        if '/spell' in href.lower() or 'spell' in text.lower():
            spell_links.append((text, full_url))
    
    unique_spells = list(set(spell_links))
    print(f"  Toplam spell linki: {len(unique_spells)}")
    print("  İlk 15 link:")
    for i, (name, url) in enumerate(unique_spells[:15], 1):
        print(f"    {i:2d}. {name:40s} | {url}")
else:
    print(f"  ❌ Sayfa bulunamadı: {response.status_code}")

# Database/spell sayfasını kontrol et
print("\n" + "=" * 70)
print("2. DATABASE/SPELL SAYFASI")
print("-" * 70)

# Önce database/spell ana sayfasını kontrol et
db_spell_urls = [
    BASE_URL + "/database/spell/",
    BASE_URL + "/database/spells/",
]

for url in db_spell_urls:
    print(f"\n  Test: {url}")
    response = requests.head(url, timeout=10, allow_redirects=True)
    print(f"    Status: {response.status_code}")
    if response.status_code == 200:
        # Sayfa içeriğini çek
        response_full = requests.get(url, timeout=30)
        soup = BeautifulSoup(response_full.content, 'html.parser')
        
        # Spell linklerini bul
        spell_db_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            if '/spell/' in href.lower() and text and len(text) < 100:
                if href.startswith('/'):
                    full_url = BASE_URL + href
                else:
                    full_url = urljoin(url, href)
                spell_db_links.append((text, full_url))
        
        unique_db = list(set(spell_db_links))
        print(f"    ✅ {len(unique_db)} spell linki bulundu")
        if unique_db:
            print("    İlk 10:")
            for i, (name, url_link) in enumerate(unique_db[:10], 1):
                print(f"      {i:2d}. {name:35s} | {url_link[:70]}...")

# Spells by Class sayfasını kontrol et
print("\n" + "=" * 70)
print("3. SPELLS BY CLASS")
print("-" * 70)
spells_by_class_url = BASE_URL + "/spellcasting/spell-lists/"
response = requests.get(spells_by_class_url, timeout=30)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Class linklerini bul
    class_spell_links = []
    for link in soup.find_all('a', href=True):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if '/spellcasting/' in href.lower() and text and len(text) < 50:
            full_url = urljoin(BASE_URL, href)
            class_spell_links.append((text, full_url))
    
    unique_classes = list(set(class_spell_links))
    print(f"  ✅ {len(unique_classes)} class spell listesi bulundu")
    for name, url in unique_classes[:12]:
        print(f"    - {name:25s} | {url}")
else:
    print(f"  ❌ Sayfa bulunamadı: {response.status_code}")

# Örnek spell sayfasını analiz et
print("\n" + "=" * 70)
print("4. ÖRNEK SPELL SAYFASI ANALİZİ")
print("-" * 70)

# Önce bir spell URL'i bulmaya çalışalım
test_spell_urls = [
    BASE_URL + "/database/spell/acid-splash/",
    BASE_URL + "/spellcasting/spells/acid-splash/",
    BASE_URL + "/spells/acid-splash/",
]

for url in test_spell_urls:
    print(f"\n  Test: {url}")
    response = requests.head(url, timeout=10, allow_redirects=True)
    if response.status_code == 200:
        print(f"    ✅ Çalışıyor! Status: {response.status_code}")
        # Sayfa içeriğini analiz et
        response_full = requests.get(url, timeout=30)
        soup = BeautifulSoup(response_full.content, 'html.parser')
        
        # İçeriği göster
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if main_content:
            # Başlığı bul
            title = soup.find('h1') or soup.find('h2') or soup.find('title')
            if title:
                print(f"    Başlık: {title.get_text(strip=True)}")
            
            # Spell detaylarını bul
            paragraphs = main_content.find_all('p')
            print(f"    Paragraf sayısı: {len(paragraphs)}")
            if paragraphs:
                print(f"    İlk paragraf: {paragraphs[0].get_text(strip=True)[:100]}...")
        
        break
    else:
        print(f"    ❌ Status: {response.status_code}")

print("\n" + "=" * 70)
print("✅ ANALİZ TAMAMLANDI")
print("=" * 70)


