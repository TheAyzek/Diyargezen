#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archetype sayfasını analiz et"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.d20herosrd.com"
url = BASE_URL + "/character-creation/archetypes/battlesuit/"

print("Battlesuit sayfası analiz ediliyor...")
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
    print(f"  Toplam paragraf: {len(main_content.find_all('p'))}")
    print(f"  Toplam liste: {len(main_content.find_all(['ul', 'ol']))}")
    
    # İlk paragrafları göster
    print("\n📝 İlk 5 paragraf:")
    paragraphs = main_content.find_all('p')
    for i, p in enumerate(paragraphs[:5]):
        text = p.get_text(strip=True)
        if len(text) > 20 and 'Green Ronin' not in text:
            print(f"  {i+1}. {text[:150]}...")
    
    # Başlıkları göster
    print("\n📋 Başlıklar:")
    headers = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
    for i, header in enumerate(headers[:10]):
        text = header.get_text(strip=True)
        if len(text) > 0:
            print(f"  {i+1}. {header.name}: {text[:80]}")
    
    # Powers, Advantages, Skills bölümlerini bul
    print("\n🔍 Powers/Advantages/Skills Bölümleri:")
    text = main_content.get_text()
    
    # Powers bölümünü bul
    powers_match = re.search(r'(Suggested|Recommended|Powers?)[^.]*?(?:\.|\n)', text, re.IGNORECASE)
    if powers_match:
        print(f"  Powers bölümü bulundu: {powers_match.group(0)[:100]}...")
    
    # Advantages bölümünü bul
    advantages_match = re.search(r'[Aa]dvantages?[^.]*?(?:\.|\n)', text, re.IGNORECASE)
    if advantages_match:
        print(f"  Advantages bölümü bulundu: {advantages_match.group(0)[:100]}...")
    
    # Skills bölümünü bul
    skills_match = re.search(r'[Ss]kills?[^.]*?(?:\.|\n)', text, re.IGNORECASE)
    if skills_match:
        print(f"  Skills bölümü bulundu: {skills_match.group(0)[:100]}...")
    
    # Liste öğelerini göster
    print("\n📋 Listeler:")
    lists = main_content.find_all(['ul', 'ol'])
    for i, lst in enumerate(lists[:3]):
        items = lst.find_all('li')
        print(f"  Liste {i+1}: {len(items)} öğe")
        for j, item in enumerate(items[:5]):
            text = item.get_text(strip=True)
            print(f"    {j+1}. {text[:80]}")


