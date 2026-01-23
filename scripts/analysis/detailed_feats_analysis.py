#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com feat sayfasını detaylı analiz et"""

import sys
import codecs
import requests
from bs4 import BeautifulSoup

# UTF-8 encoding fix for Windows console
if sys.platform == 'win32':
    sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
    sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')

BASE_URL = "https://www.5esrd.com"

def analyze_feats_page():
    """Feats sayfasını detaylı analiz et"""
    print("=" * 70)
    print("DETAYLI FEATS ANALİZİ")
    print("=" * 70)
    
    url = f"{BASE_URL}/database/feats"
    session = requests.Session()
    session.headers.update({
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    })
    
    try:
        response = session.get(url, timeout=10)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Sayfanın yapısını anla
        print("\n📋 Sayfa Yapısı:")
        
        # Başlıkları bul
        headings = soup.find_all(['h1', 'h2', 'h3', 'h4'])
        print(f"\nBaşlıklar ({len(headings)} adet):")
        for i, heading in enumerate(headings[:10], 1):
            print(f"  {i}. {heading.name}: {heading.get_text(strip=True)[:60]}")
        
        # Listeleri bul (ul, ol)
        lists = soup.find_all(['ul', 'ol'])
        print(f"\nListeler ({len(lists)} adet):")
        for i, list_elem in enumerate(lists[:5], 1):
            items = list_elem.find_all('li')
            print(f"  {i}. {len(items)} öğe içeren {list_elem.name}")
            if items:
                first_item = items[0].get_text(strip=True)[:50]
                print(f"     İlk öğe: {first_item}")
        
        # Tüm linkleri bul ve "feat" içerenleri göster
        all_links = soup.find_all('a', href=True)
        print(f"\nTüm linkler ({len(all_links)} adet)")
        
        # Feat içeren linkleri bul (case-insensitive)
        feat_related = []
        for link in all_links:
            href = link.get('href', '').lower()
            text = link.get_text(strip=True).lower()
            if 'feat' in href or 'feat' in text:
                feat_related.append(link)
        
        print(f"Feat içeren linkler: {len(feat_related)}")
        if feat_related:
            print("\nİlk 15 feat linki:")
            for i, link in enumerate(feat_related[:15], 1):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"  {i:2d}. {text[:40]:40s} -> {href[:70]}")
        
        # Belirli pattern'lerle ara
        print("\n🔍 Pattern araması:")
        
        # /database/feat/ ile başlayan linkler
        db_feat_links = [a for a in all_links if '/database/feat/' in a.get('href', '').lower()]
        print(f"  /database/feat/ linkleri: {len(db_feat_links)}")
        if db_feat_links[:5]:
            for i, link in enumerate(db_feat_links[:5], 1):
                print(f"    {i}. {link.get_text(strip=True)[:40]} -> {link.get('href')[:70]}")
        
        # /feats/ ile başlayan linkler
        feats_links = [a for a in all_links if '/feats/' in a.get('href', '').lower()]
        print(f"  /feats/ linkleri: {len(feats_links)}")
        if feats_links[:5]:
            for i, link in enumerate(feats_links[:5], 1):
                print(f"    {i}. {link.get_text(strip=True)[:40]} -> {link.get('href')[:70]}")
        
        # İçerik alanını bul
        print("\n📄 İçerik Alanı:")
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article') or soup.find('body')
        if main_content:
            # İlk 500 karakteri göster
            text_preview = main_content.get_text()[:500]
            print(f"  İçerik önizleme (ilk 500 karakter):\n{text_preview}")
            
    except Exception as e:
        print(f"❌ Hata: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    analyze_feats_page()


