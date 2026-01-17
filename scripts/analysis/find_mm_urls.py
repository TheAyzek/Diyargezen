#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""M&M için doğru URL'leri bul"""

import requests
from bs4 import BeautifulSoup

BASE_URL = "https://www.d20herosrd.com"

def find_urls():
    """Character Creation sayfasından tüm linkleri bul"""
    print("Character Creation sayfasından linkler bulunuyor...\n")
    
    url = BASE_URL + "/character-creation/"
    response = requests.get(url, timeout=30)
    if response.status_code != 200:
        print(f"❌ Sayfa bulunamadı: {response.status_code}")
        return
    
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tüm linkleri bul
    all_links = soup.find_all('a', href=True)
    
    print("="*60)
    print("TÜM CHARACTER CREATION LİNKLERİ")
    print("="*60)
    
    sections = {}
    for link in all_links:
        href = link.get('href', '')
        text = link.get_text(strip=True)
        
        if '/character-creation/' in href and text:
            sections[text] = href
    
    # Abilities
    abilities_links = {k: v for k, v in sections.items() if 'abilit' in k.lower()}
    print("\n💪 ABILITIES:")
    for name, url in abilities_links.items():
        print(f"  {name}: {url}")
    
    # Skills
    skills_links = {k: v for k, v in sections.items() if 'skill' in k.lower()}
    print("\n🎯 SKILLS:")
    for name, url in skills_links.items():
        print(f"  {name}: {url}")
    
    # Advantages
    advantages_links = {k: v for k, v in sections.items() if 'advantage' in k.lower()}
    print("\n⭐ ADVANTAGES:")
    for name, url in advantages_links.items():
        print(f"  {name}: {url}")
    
    # Powers (ana sayfadan)
    print("\n⚡ POWERS (Ana sayfadan):")
    main_response = requests.get(BASE_URL, timeout=30)
    if main_response.status_code == 200:
        main_soup = BeautifulSoup(main_response.content, 'html.parser')
        power_links = main_soup.find_all('a', href=True, string=lambda x: x and 'power' in x.lower())
        for link in power_links[:5]:
            print(f"  {link.get_text(strip=True)}: {link.get('href', '')}")

if __name__ == "__main__":
    find_urls()


