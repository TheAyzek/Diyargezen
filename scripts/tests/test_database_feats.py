#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com /database/feats sayfasını test et"""

import sys
import codecs
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

# UTF-8 encoding fix for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "https://www.5esrd.com"

def test_database_feats():
    """Database feats sayfasını test et"""
    print("=" * 70)
    print("TEST: /database/feats")
    print("=" * 70)
    
    url = f"{BASE_URL}/database/feats"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=10)
        print(f"Status: {response.status_code}")
        
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Tüm linkleri bul
            all_links = soup.find_all('a', href=True)
            print(f"\nToplam link sayısı: {len(all_links)}")
            
            # Feat linklerini filtrele
            feat_links = []
            for link in all_links:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                
                # /feat/ içeren ve anlamlı text'i olan linkler
                if '/feat/' in href.lower() and text and len(text) < 100 and text != 'Feats':
                    if href.startswith('/'):
                        full_url = BASE_URL + href
                    elif href.startswith('http'):
                        full_url = href
                    else:
                        full_url = urljoin(url, href)
                    
                    feat_links.append((text, full_url))
            
            print(f"\n✅ {len(feat_links)} feat linki bulundu")
            
            if feat_links:
                print("\n📋 İlk 20 feat linki:")
                for i, (text, href) in enumerate(feat_links[:20], 1):
                    print(f"  {i:2d}. {text[:45]:45s} -> {href[:80]}")
            
            return feat_links
        else:
            print(f"❌ Status code: {response.status_code}")
            return []
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()
        return []

if __name__ == "__main__":
    links = test_database_feats()
    print(f"\n✅ Toplam {len(links)} feat linki bulundu")


