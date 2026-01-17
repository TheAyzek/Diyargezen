#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""HTML dosyalarından ırk detaylarını çıkar"""

from bs4 import BeautifulSoup
import re

def extract_aonprd_race_details():
    """Archives of Nethys HTML'den detayları çıkar"""
    print("=" * 60)
    print("Archives of Nethys - Human Race Details")
    print("=" * 60)
    
    with open("human_race_aonprd.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Başlık
    h1 = soup.find('h1', class_='title') or soup.find('h1')
    if h1:
        print(f"\n[Title] {h1.get_text(strip=True)}")
    
    # Ana içerik alanını bul
    main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
    
    if main_content:
        text = main_content.get_text()
        
        # Ability Score Increases - daha detaylı
        print("\n[Ability Score Increases]")
        # Pattern: "+2 to One Ability Score" veya "+2 Strength, +2 Constitution"
        ability_matches = re.findall(r'\+(\d+)\s+(?:to\s+)?(?:One\s+)?(?:Ability\s+Score|Str|Dex|Con|Int|Wis|Cha|Strength|Dexterity|Constitution|Intelligence|Wisdom|Charisma)', text, re.IGNORECASE)
        for match in ability_matches[:10]:
            print(f"  Found: +{match[0]} {match[1] if len(match) > 1 else 'Ability'}")
        
        # Size
        print("\n[Size]")
        size_match = re.search(r'Size\s*:?\s*(\w+)', text, re.IGNORECASE)
        if size_match:
            print(f"  {size_match.group(1)}")
        
        # Speed
        print("\n[Speed]")
        speed_match = re.search(r'Speed\s*:?\s*(\d+)', text, re.IGNORECASE)
        if speed_match:
            print(f"  {speed_match.group(1)} feet")
        
        # Languages
        print("\n[Languages]")
        lang_match = re.search(r'Languages?\s*:?\s*([^\n]+)', text, re.IGNORECASE)
        if lang_match:
            lang_text = lang_match.group(1)[:300]
            print(f"  {lang_text}")
        
        # Racial Traits - başlıklar ve içerikleri
        print("\n[Racial Traits]")
        # H3/H4 başlıklarını bul
        trait_headers = soup.find_all(['h3', 'h4'], string=re.compile(r'.+', re.I))
        for header in trait_headers[:15]:
            header_text = header.get_text(strip=True)
            if len(header_text) < 100:  # Çok uzun olmasın
                print(f"\n  [{header_text}]")
                # Sonraki paragraf/div'leri bul
                current = header.next_sibling
                trait_content = []
                count = 0
                while current and count < 3:
                    if hasattr(current, 'name'):
                        if current.name in ['p', 'div', 'ul', 'ol', 'li']:
                            text_content = current.get_text(strip=True)
                            if text_content and len(text_content) > 10:
                                trait_content.append(text_content[:200])
                                count += 1
                    elif isinstance(current, str) and current.strip():
                        trait_content.append(current.strip()[:200])
                        count += 1
                    current = getattr(current, 'next_sibling', None)
                for content in trait_content[:2]:
                    print(f"    {content}")

def extract_d20pfsrd_race_details():
    """d20pfsrd HTML'den detayları çıkar"""
    print("\n" + "=" * 60)
    print("d20pfsrd.com - Human Race Details")
    print("=" * 60)
    
    with open("human_race_d20pfsrd.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Başlık
    h1 = soup.find('h1', class_='article-title') or soup.find('h1')
    if h1:
        print(f"\n[Title] {h1.get_text(strip=True)}")
    
    # Definition lists (dt/dd) yapısını kullan
    print("\n[Racial Details - dt/dd structure]")
    dl_tags = soup.find_all('dl')
    for dl in dl_tags[:3]:  # İlk 3 dl
        dt_tags = dl.find_all('dt')
        for dt in dt_tags[:10]:  # İlk 10 dt
            term = dt.get_text(strip=True)
            dd = dt.find_next_sibling('dd')
            if dd:
                definition = dd.get_text(strip=True)[:300]
                if term and definition:
                    print(f"\n  [{term}]")
                    print(f"    {definition}")

if __name__ == "__main__":
    try:
        extract_aonprd_race_details()
        extract_d20pfsrd_race_details()
        print("\n[OK] Detaylar cikarildi!")
    except Exception as e:
        print(f"[HATA] Hata: {e}")
        import traceback
        traceback.print_exc()

