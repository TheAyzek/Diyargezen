#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""d20herosrd.com site yapısını test et"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.d20herosrd.com"

def test_url(url):
    """URL'i test et"""
    try:
        response = requests.get(url, timeout=30)
        print(f"{'✅' if response.status_code == 200 else '❌'} {response.status_code}: {url}")
        return response.status_code == 200
    except Exception as e:
        print(f"❌ Hata: {url} - {e}")
        return False

def explore_page(url, name):
    """Sayfayı keşfet ve linkleri bul"""
    print(f"\n{'='*60}")
    print(f"🔍 {name}: {url}")
    print('='*60)
    
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            print(f"❌ Sayfa bulunamadı: {response.status_code}")
            return
        
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tüm linkleri bul
        all_links = soup.find_all('a', href=True)
        print(f"\n📊 Toplam link: {len(all_links)}")
        
        # İlgili linkleri filtrele
        character_links = [l for l in all_links if '/character-creation/' in l.get('href', '').lower()]
        power_links = [l for l in all_links if '/powers/' in l.get('href', '').lower()]
        archetype_links = [l for l in all_links if 'archetype' in l.get('href', '').lower()]
        skill_links = [l for l in all_links if 'skill' in l.get('href', '').lower()]
        advantage_links = [l for l in all_links if 'advantage' in l.get('href', '').lower()]
        
        print(f"  - Character Creation linkleri: {len(character_links)}")
        print(f"  - Power linkleri: {len(power_links)}")
        print(f"  - Archetype linkleri: {len(archetype_links)}")
        print(f"  - Skill linkleri: {len(skill_links)}")
        print(f"  - Advantage linkleri: {len(advantage_links)}")
        
        # İlk birkaç linki göster
        if character_links:
            print("\n  İlk 5 Character Creation linki:")
            for i, link in enumerate(character_links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"    {i+1}. {text[:50]} -> {href[:80]}")
        
        if archetype_links:
            print("\n  İlk 5 Archetype linki:")
            for i, link in enumerate(archetype_links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"    {i+1}. {text[:50]} -> {href[:80]}")
        
        # Ana menü linklerini bul
        nav_links = soup.find_all('a', href=True)
        main_sections = {}
        for link in nav_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            if href.startswith('/') and text:
                # Ana bölüm linklerini bul
                parts = href.strip('/').split('/')
                if len(parts) <= 2 and parts[0]:
                    main_sections[parts[0]] = href
        
        if main_sections:
            print(f"\n📋 Ana bölümler:")
            for section, url in sorted(main_sections.items()):
                print(f"  - {section}: {BASE_URL}{url}")
                
    except Exception as e:
        print(f"❌ Hata: {e}")

# Ana sayfayı test et
print("="*60)
print("D20HEROSRD.COM SITE YAPISI TEST")
print("="*60)

# Ana sayfayı keşfet
explore_page(BASE_URL, "Ana Sayfa")

# Bilinen bölümleri test et
test_urls = [
    ("/character-creation/", "Character Creation"),
    ("/character-creation/archetypes/", "Archetypes"),
    ("/the-basics/", "The Basics"),
    ("/powers/", "Powers"),
]

print("\n" + "="*60)
print("BİLİNEN URL'LER TEST")
print("="*60)

for url_path, name in test_urls:
    full_url = BASE_URL + url_path
    test_url(full_url)
    if test_url(full_url):
        explore_page(full_url, name)


