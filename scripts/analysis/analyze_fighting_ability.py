#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fighting ability'yi analiz et"""

import requests
from bs4 import BeautifulSoup
import re
import sys
import io

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.d20herosrd.com"
url = BASE_URL + "/character-creation/3-abilities/"

print("Fighting ability analiz ediliyor...")
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
    
    # Fighting başlığını bul (H3: FIGHTING (FGT))
    fighting_header = None
    headers = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
    
    for header in headers:
        header_text = header.get_text(strip=True).upper()
        if 'FIGHTING' in header_text and 'FGT' in header_text:
            fighting_header = header
            print(f"✅ Fighting başlığı bulundu: {header.get_text(strip=True)}")
            break
    
    if fighting_header:
        # Sonraki içeriği al
        description_parts = []
        next_elem = fighting_header.find_next_sibling()
        next_ability = "INTELLECT"  # Bir sonraki ability
        
        while next_elem:
            # Bir sonraki ability başlığına gelince dur
            if next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                next_text = next_elem.get_text(strip=True).upper()
                if next_ability in next_text or 'INTELLECT' in next_text:
                    print("  Bir sonraki ability başlığına gelindi, durduruldu")
                    break
            
            # İçeriği al
            if next_elem.name in ['p', 'div']:
                text = next_elem.get_text(strip=True)
                # Footer linklerini filtrele
                if (len(text) > 20 and 
                    'Green Ronin' not in text and 
                    'Mutants & Masterminds' not in text and
                    'OGN' not in text and
                    'd20pfsrd' not in text.lower() and
                    'Open Gaming' not in text):
                    description_parts.append(text)
                    print(f"  Paragraf eklendi: {text[:100]}...")
            
            # Liste öğelerini de al
            elif next_elem.name in ['ul', 'ol']:
                items = next_elem.find_all('li')
                for item in items:
                    text = item.get_text(strip=True)
                    if len(text) > 20 and 'Green Ronin' not in text:
                        description_parts.append(text)
                        print(f"  Liste öğesi eklendi: {text[:100]}...")
            
            next_elem = next_elem.find_next_sibling()
            
            # Limit
            if len(description_parts) >= 15:
                print("  Limit'e ulaşıldı, durduruldu")
                break
        
        if description_parts:
            full_description = "\n\n".join(description_parts)
            print(f"\n✅ Fighting açıklaması: {len(full_description)} karakter")
            print(f"\nİçerik:\n{full_description[:500]}...")
        else:
            print("\n❌ Fighting için açıklama bulunamadı!")
            # Text'ten parse et
            text = main_content.get_text()
            pattern = r'FIGHTING[:\s(]*FGT[:\s)]*([^A-Z]{100,1000}?)(?=INTELLECT|AWARENESS|$)'
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                print(f"\n✅ Text'ten bulundu: {len(match.group(1))} karakter")
                print(f"\nİçerik:\n{match.group(1)[:500]}...")
    else:
        print("❌ Fighting başlığı bulunamadı!")


