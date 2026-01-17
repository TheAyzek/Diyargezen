#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archives of Nethys ve d20pfsrd'den örnek ırk sayfalarını detaylı analiz et"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def analyze_aonprd_race():
    """Archives of Nethys'ten bir ırk sayfasını analiz et"""
    print("=" * 60)
    print("Archives of Nethys - Human Race Page Analysis")
    print("=" * 60)
    
    # Human ırkı sayfası
    url = "https://aonprd.com/RacesDisplay.aspx?ItemName=Human"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("\n[1] HTML Yapısı:")
    print(f"  Title: {soup.title.string if soup.title else 'N/A'}")
    
    # Ana başlık
    main_title = soup.find('h1') or soup.find('h2')
    if main_title:
        print(f"  Main Title: {main_title.get_text(strip=True)}")
    
    # Ability Score Increases bölümü
    print("\n[2] Ability Score Increases:")
    ability_section = soup.find(string=re.compile(r'Ability.*Score|Ability.*Increase', re.I))
    if ability_section:
        parent = ability_section.find_parent(['p', 'div', 'li', 'td'])
        if parent:
            print(f"  Found: {parent.get_text(strip=True)[:200]}")
            # Tüm yakın içeriği göster
            for sibling in parent.find_next_siblings(['p', 'div', 'li'])[:3]:
                print(f"    -> {sibling.get_text(strip=True)[:150]}")
    
    # Size bölümü
    print("\n[3] Size:")
    size_section = soup.find(string=re.compile(r'^Size', re.I))
    if size_section:
        parent = size_section.find_parent(['p', 'div', 'li', 'td'])
        if parent:
            print(f"  Found: {parent.get_text(strip=True)[:200]}")
    
    # Speed bölümü
    print("\n[4] Speed:")
    speed_section = soup.find(string=re.compile(r'^Speed', re.I))
    if speed_section:
        parent = speed_section.find_parent(['p', 'div', 'li', 'td'])
        if parent:
            print(f"  Found: {parent.get_text(strip=True)[:200]}")
    
    # Languages bölümü
    print("\n[5] Languages:")
    lang_section = soup.find(string=re.compile(r'^Languages?', re.I))
    if lang_section:
        parent = lang_section.find_parent(['p', 'div', 'li', 'td'])
        if parent:
            print(f"  Found: {parent.get_text(strip=True)[:300]}")
    
    # Traits/Racial Traits bölümü
    print("\n[6] Racial Traits:")
    trait_headers = soup.find_all(['h3', 'h4', 'strong', 'b'], string=re.compile(r'Trait|Racial|Special|Ability', re.I))
    print(f"  Found {len(trait_headers)} trait headers:")
    for i, header in enumerate(trait_headers[:10]):
        print(f"    {i+1}. {header.get_text(strip=True)}")
        # Header'ın sonrasındaki içeriği göster
        parent = header.find_parent(['div', 'p', 'li']) or header.parent
        if parent:
            next_sibling = header.find_next_sibling(['p', 'div', 'li', 'ul'])
            if next_sibling:
                trait_text = next_sibling.get_text(strip=True)[:200]
                if trait_text:
                    print(f"       -> {trait_text}")
    
    # Favored Class bölümü
    print("\n[7] Favored Class:")
    favored_section = soup.find(string=re.compile(r'Favored.*Class', re.I))
    if favored_section:
        parent = favored_section.find_parent(['p', 'div', 'li', 'td'])
        if parent:
            print(f"  Found: {parent.get_text(strip=True)[:300]}")
    
    # HTML'i kaydet (detaylı inceleme için)
    with open("human_race_aonprd.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print("\n  HTML kaydedildi: human_race_aonprd.html")

def analyze_d20pfsrd_race():
    """d20pfsrd'den bir ırk sayfasını analiz et"""
    print("\n" + "=" * 60)
    print("d20pfsrd.com - Human Race Page Analysis")
    print("=" * 60)
    
    # Human ırkı sayfası
    url = "https://www.d20pfsrd.com/races/core-races/human"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("\n[1] HTML Yapısı:")
    print(f"  Title: {soup.title.string if soup.title else 'N/A'}")
    
    # Ana başlık
    main_title = soup.find('h1') or soup.find('h2', class_='article-title')
    if main_title:
        print(f"  Main Title: {main_title.get_text(strip=True)}")
    
    # Ability Score Increases
    print("\n[2] Ability Score Increases:")
    ability_patterns = [
        soup.find(string=re.compile(r'Ability.*Score.*Increase', re.I)),
        soup.find(string=re.compile(r'\+2.*Ability', re.I)),
        soup.find('dt', string=re.compile(r'Ability', re.I)),
    ]
    for pattern in ability_patterns:
        if pattern:
            parent = pattern.find_parent(['dl', 'p', 'div', 'li']) or pattern.parent
            if parent:
                text = parent.get_text(strip=True)[:300]
                print(f"  Found: {text}")
                break
    
    # Tüm dt (definition term) başlıklarını göster
    print("\n[3] All Section Headers (dt tags):")
    dt_tags = soup.find_all('dt')
    for i, dt in enumerate(dt_tags[:15]):
        dd = dt.find_next_sibling('dd')
        dd_text = dd.get_text(strip=True)[:150] if dd else "N/A"
        print(f"    {i+1}. {dt.get_text(strip=True)}: {dd_text}")
    
    # HTML'i kaydet
    with open("human_race_d20pfsrd.html", "w", encoding="utf-8") as f:
        f.write(soup.prettify())
    print("\n  HTML kaydedildi: human_race_d20pfsrd.html")

if __name__ == "__main__":
    try:
        analyze_aonprd_race()
        analyze_d20pfsrd_race()
        print("\n✅ Analiz tamamlandı!")
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()


