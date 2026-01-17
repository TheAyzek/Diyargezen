#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Power Effects sayfasını analiz et"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import re

# Windows konsol encoding hatası için
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.d20herosrd.com"
url = BASE_URL + "/6-powers/effects/effect-descriptions/"

print("Power Effects sayfası analiz ediliyor...")
response = requests.get(url, timeout=30)
if response.status_code != 200:
    print(f"❌ Sayfa bulunamadı: {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.content, 'html.parser')

# Ana içeriği bul
main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')

if main_content:
    # Navigation ve footer'ı temizle
    for nav in main_content.find_all(['nav', 'header', 'footer']):
        nav.decompose()
    
    print("\n📊 Sayfa Yapısı:")
    print(f"  Toplam başlık: {len(main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5']))}")
    
    # Tüm linkleri bul
    all_links = main_content.find_all('a', href=True)
    print(f"  Toplam link: {len(all_links)}")
    
    # Effect linklerini bul
    effect_links = main_content.find_all('a', href=re.compile(r'#TOC-|/6-powers/effects/effect-descriptions/[^/]+/$'))
    print(f"  Effect linkleri: {len(effect_links)}")
    
    print("\n🔍 İlk 20 Effect Linki:")
    for i, link in enumerate(effect_links[:20]):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        print(f"  {i+1}. {text[:60]}: {href[:80]}")
    
    # Başlıkları bul
    headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
    print(f"\n📋 İlk 20 Başlık:")
    for i, header in enumerate(headers[:20]):
        text = header.get_text(strip=True)
        if len(text) > 0 and len(text) < 100:
            print(f"  {i+1}. {header.name}: {text}")
    
    # Category başlıklarını bul (ATTACK, DEFENSE, MOVEMENT, etc.)
    print("\n🔍 Category Başlıkları:")
    category_headers = main_content.find_all(['h2', 'h3'], string=re.compile(r'(ATTACK|DEFENSE|MOVEMENT|CONTROL|GENERAL|SENSORY)', re.I))
    for header in category_headers:
        print(f"  - {header.get_text(strip=True)}")
    
    # Category'ye göre effect'leri bul
    categories = ["ATTACK", "DEFENSE", "MOVEMENT", "CONTROL", "GENERAL", "SENSORY"]
    for category in categories:
        print(f"\n📋 {category} Category:")
        # Bu category başlığını bul
        category_header = main_content.find(['h2', 'h3'], string=re.compile(rf'^{category}', re.I))
        if category_header:
            # Sonraki effect'leri bul (bir sonraki category'ye kadar)
            next_elem = category_header.find_next_sibling()
            count = 0
            while next_elem and count < 20:
                if next_elem.name in ['h2', 'h3']:
                    next_text = next_elem.get_text(strip=True).upper()
                    # Bir sonraki category mi?
                    if any(cat in next_text for cat in categories if cat != category):
                        break
                
                # Effect linklerini bul
                if next_elem.name in ['p', 'div', 'ul', 'ol']:
                    links = next_elem.find_all('a', href=True)
                    for link in links:
                        text = link.get_text(strip=True)
                        if text and len(text) < 100 and text[0].isupper():
                            print(f"    - {text}")
                            count += 1
                
                next_elem = next_elem.find_next_sibling()
                if count >= 10:
                    break

