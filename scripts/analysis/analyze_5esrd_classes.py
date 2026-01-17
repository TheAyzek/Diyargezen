#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com Classes analizi"""

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
print("5ESRD.COM CLASSES ANALİZİ")
print("=" * 70)
print()

# Classes sayfasını analiz et - farklı URL'leri dene
print("1. CLASSES SAYFASI ANALİZİ")
print("-" * 70)

test_urls = [
    BASE_URL + "/database/classes/",
    BASE_URL + "/classes/",
    BASE_URL + "/database/class/",
]

classes_url = None
response = None

for test_url in test_urls:
    print(f"Test URL: {test_url}")
    try:
        test_response = requests.get(test_url, timeout=30)
        print(f"  Status: {test_response.status_code}")
        if test_response.status_code == 200:
            classes_url = test_url
            response = test_response
            print(f"  ✅ Başarılı!")
            break
    except Exception as e:
        print(f"  ❌ Hata: {e}")
    print()

if response and response.status_code == 200:
    try:
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Class linklerini bul - farklı pattern'leri dene
        class_links = []
        all_links = soup.find_all('a', href=True)
        print(f"  Toplam link sayısı: {len(all_links)}\n")
        
        for link in all_links:
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Class linklerini bul - farklı pattern'ler
            patterns = [
                '/database/classes/',
                '/classes/',
                '/database/class/',
            ]
            
            # Core classes için: /database/class/class-name/ pattern'ini kullan
            if '/database/class/' in href.lower() and text and len(text) < 50 and len(text) > 1:
                # 3rd party veya prestige class'ları filtrele
                if '3rd-party' not in href.lower() and 'prestige' not in href.lower():
                    if href.endswith('/'):
                        if href.startswith('/'):
                            full_url = BASE_URL + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(classes_url, href)
                        
                        # Duplicate kontrolü
                        if (text, full_url) not in class_links:
                            class_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_classes = list(set(class_links))
        print(f"  ✅ Toplam {len(unique_classes)} unique class linki bulundu\n")
        
        print("  İlk 20 class:")
        for i, (name, url) in enumerate(unique_classes[:20], 1):
            print(f"    {i:2d}. {name}")
            print(f"        {url}")
        
        if len(unique_classes) > 20:
            print(f"\n    ... ve {len(unique_classes) - 20} tane daha")
        
        # Core class'ları filtrele (database/class/ olanlar)
        core_classes = [(n, u) for n, u in unique_classes if '/database/class/' in u.lower() and '3rd-party' not in u.lower() and 'prestige' not in u.lower()]
        print(f"  ✅ Toplam {len(core_classes)} core class bulundu\n")
        
        # İlk core class'ın detay sayfasını analiz et
        if core_classes:
            print("\n2. ÖRNEK CORE CLASS DETAY SAYFASI ANALİZİ")
            print("-" * 70)
            test_name, test_url = core_classes[0]
            print(f"Class: {test_name}")
            print(f"URL: {test_url}\n")
            
            test_response = requests.get(test_url, timeout=30)
            if test_response.status_code == 200:
                test_soup = BeautifulSoup(test_response.content, 'html.parser')
                
                # Main content alanını bul
                main_content = test_soup.find('div', class_='content') or test_soup.find('main') or test_soup.find('article')
                if not main_content:
                    main_content = test_soup.find('body')
                
                if main_content:
                    # Navigation ve footer'ı temizle
                    for nav in main_content.find_all(['nav', 'header', 'footer']):
                        nav.decompose()
                    
                    # İlk 1000 karakteri göster
                    text_content = main_content.get_text()
                    print("İlk 500 karakter:")
                    print("-" * 70)
                    print(text_content[:500])
                    print("-" * 70)
                    
                    # Hit Dice pattern'ini ara
                    hit_die_patterns = [
                        r'Hit Die[:\s]+d(\d+)',
                        r'Hit Dice[:\s]+d(\d+)',
                        r'd(\d+)\s+Hit Die',
                    ]
                    for pattern in hit_die_patterns:
                        match = re.search(pattern, text_content, re.I)
                        if match:
                            print(f"\n✅ Hit Dice bulundu: d{match.group(1)}")
                            break
                    
                    # Primary Ability pattern'ini ara
                    ability_patterns = [
                        r'Primary Ability[:\s]+([A-Za-z, ]+)',
                        r'Ability[:\s]+([A-Za-z, ]+)',
                    ]
                    for pattern in ability_patterns:
                        match = re.search(pattern, text_content[:500], re.I)
                        if match:
                            print(f"✅ Primary Ability bulundu: {match.group(1)}")
                            break
    except Exception as e:
        print(f"  ❌ Hata: {e}")
        import traceback
        traceback.print_exc()
else:
    if response:
        print(f"  ❌ Status {response.status_code}")
    else:
        print("  ❌ Hiçbir URL çalışmadı")

print("\n" + "=" * 70)

