#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com feat URL yapısını analiz et"""

import sys
import codecs
import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

# UTF-8 encoding fix for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "https://www.5esrd.com"

def analyze_feat_urls():
    """Feat URL'lerini analiz et"""
    print("=" * 70)
    print("5ESRD.COM FEAT URL ANALİZİ")
    print("=" * 70)
    
    # Olası URL'ler
    test_urls = [
        f"{BASE_URL}/feats/",
        f"{BASE_URL}/database/feat/",
        f"{BASE_URL}/feats",
        f"{BASE_URL}/database/feats/",
        f"{BASE_URL}/",
    ]
    
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    for url in test_urls:
        print(f"\n🔍 Test ediliyor: {url}")
        try:
            response = session.get(url, timeout=10)
            print(f"  Status: {response.status_code}")
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Tüm linkleri bul
                all_links = soup.find_all('a', href=True)
                feat_links = []
                
                for link in all_links:
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    
                    # Feat içeren linkleri bul
                    if 'feat' in href.lower() or 'feat' in text.lower():
                        if href.startswith('/'):
                            full_url = BASE_URL + href
                        elif href.startswith('http'):
                            full_url = href
                        else:
                            full_url = urljoin(url, href)
                        
                        feat_links.append((text[:50], full_url))
                
                print(f"  ✅ {len(feat_links)} feat linki bulundu")
                
                if feat_links:
                    print("\n  📋 İlk 10 feat linki:")
                    for i, (text, href) in enumerate(feat_links[:10], 1):
                        print(f"    {i}. {text[:40]:40s} -> {href[:80]}")
                    
                    # Eğer feat linkleri bulunduysa, bu URL'yi kullan
                    if len(feat_links) > 5:
                        print(f"\n  ✅ Geçerli URL bulundu: {url}")
                        return url, feat_links
                        
        except Exception as e:
            print(f"  ❌ Hata: {e}")
    
    # Ana sayfadan navigation'ı kontrol et
    print(f"\n🔍 Ana sayfadan navigation kontrol ediliyor...")
    try:
        response = session.get(f"{BASE_URL}/", timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Navigation linklerini bul
            nav_links = soup.find_all('a', href=re.compile(r'feat', re.I))
            print(f"  ✅ {len(nav_links)} navigation linki bulundu")
            
            for link in nav_links[:10]:
                href = link.get('href', '')
                text = link.get_text(strip=True)
                if href.startswith('/'):
                    full_url = BASE_URL + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    continue
                print(f"    - {text[:40]:40s} -> {full_url[:80]}")
    except Exception as e:
        print(f"  ❌ Hata: {e}")
    
    return None, []

if __name__ == "__main__":
    url, links = analyze_feat_urls()
    if url:
        print(f"\n✅ Geçerli URL: {url}")
        print(f"   Toplam {len(links)} feat linki bulundu")
    else:
        print("\n❌ Geçerli feat URL'si bulunamadı")


