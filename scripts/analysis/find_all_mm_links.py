#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M&M için tüm linkleri bul"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.d20herosrd.com"

def find_all_links():
    """Character Creation sayfasından tüm önemli linkleri bul"""
    print("=" * 70)
    print("MUTANTS & MASTERMINDS TÜM LİNKLER")
    print("=" * 70)
    
    # Character Creation sayfası
    url = BASE_URL + "/character-creation/"
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(f"❌ Sayfa bulunamadı: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tüm linkleri bul
    all_links = soup.find_all('a', href=True)
    
    print(f"\n📊 Toplam link: {len(all_links)}")
    
    # Kategorilere göre filtrele
    sections = {
        'abilities': [],
        'skills': [],
        'advantages': [],
        'powers': [],
        'archetypes': [],
        'power_effects': [],
        'sample_powers': [],
        'descriptors': [],
        'modifiers': [],
    }
    
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        href_lower = href.lower()
        text_lower = text.lower()
        
        if '/character-creation/3-abilities/' in href_lower or ('3.' in text_lower and 'abilit' in text_lower):
            sections['abilities'].append((text, href))
        elif '/character-creation/4-skills/' in href_lower or ('4.' in text_lower and 'skill' in text_lower):
            sections['skills'].append((text, href))
        elif '/character-creation/5-advantages/' in href_lower or ('5.' in text_lower and 'advantage' in text_lower):
            sections['advantages'].append((text, href))
        elif '/6-powers/' in href_lower or ('6.' in text_lower and 'power' in text_lower):
            sections['powers'].append((text, href))
        elif '/character-creation/archetypes/' in href_lower:
            sections['archetypes'].append((text, href))
        elif 'sample-power' in href_lower:
            sections['sample_powers'].append((text, href))
        elif 'power-effect' in href_lower or 'effect-description' in href_lower:
            sections['power_effects'].append((text, href))
        elif 'descriptor' in href_lower:
            sections['descriptors'].append((text, href))
        elif 'modifier' in href_lower:
            sections['modifiers'].append((text, href))
    
    # Sonuçları göster
    print("\n💪 ABILITIES:")
    for name, url in sections['abilities'][:5]:
        print(f"  {name}: {url}")
    
    print("\n🎯 SKILLS:")
    for name, url in sections['skills'][:5]:
        print(f"  {name}: {url}")
    
    print("\n⭐ ADVANTAGES:")
    for name, url in sections['advantages'][:5]:
        print(f"  {name}: {url}")
    
    print("\n⚡ POWERS:")
    for name, url in sections['powers'][:5]:
        print(f"  {name}: {url}")
    
    print("\n🎭 ARCHETYPES:")
    print(f"  Toplam: {len(sections['archetypes'])}")
    for name, url in sections['archetypes'][:5]:
        print(f"  {name}: {url}")
    
    print("\n⚡ SAMPLE POWERS:")
    print(f"  Toplam: {len(sections['sample_powers'])}")
    for name, url in sections['sample_powers'][:5]:
        print(f"  {name}: {url}")
    
    print("\n✨ POWER EFFECTS:")
    print(f"  Toplam: {len(sections['power_effects'])}")
    for name, url in sections['power_effects'][:5]:
        print(f"  {name}: {url}")
    
    # Direkt URL'leri test et
    print("\n" + "=" * 70)
    print("URL TEST")
    print("=" * 70)
    
    test_urls = [
        ("Abilities", "/character-creation/3-abilities/"),
        ("Skills", "/character-creation/4-skills/"),
        ("Advantages", "/character-creation/5-advantages/"),
        ("Powers", "/6-powers/"),
        ("Sample Powers", "/6-powers/sample-powers/"),
        ("Power Effects", "/6-powers/effects/"),
        ("Effect Descriptions", "/6-powers/effects/effect-descriptions/"),
    ]
    
    for name, url_path in test_urls:
        full_url = BASE_URL + url_path
        try:
            resp = requests.get(full_url, timeout=10)
            status = "✅" if resp.status_code == 200 else f"❌ {resp.status_code}"
            print(f"  {status} {name}: {url_path}")
        except Exception as e:
            print(f"  ❌ {name}: {url_path} - {e}")

if __name__ == "__main__":
    find_all_links()


