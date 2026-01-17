#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Fighter class HTML analizi"""

import sys
import io
import requests
from bs4 import BeautifulSoup
import re

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

url = "https://www.5esrd.com/database/class/fighter/"
print("=" * 70)
print("FIGHTER CLASS HTML ANALİZİ")
print("=" * 70)
print(f"URL: {url}\n")

response = requests.get(url, timeout=30)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Main content alanını bul
    main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
    if not main_content:
        main_content = soup.find('body')
    
    if main_content:
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        # İlk 2000 karakteri göster
        text_content = main_content.get_text()
        print("İlk 1000 karakter:")
        print("-" * 70)
        print(text_content[:1000])
        print("-" * 70)
        
        # HTML structure'ı analiz et
        print("\nHTML Yapısı:")
        print("-" * 70)
        
        # H2, H3 başlıklarını bul
        headings = main_content.find_all(['h1', 'h2', 'h3', 'h4'])
        print("Başlıklar:")
        for h in headings[:20]:
            text = h.get_text(strip=True)
            if text:
                print(f"  {h.name}: {text}")
        
        # Tüm <p> taglarını kontrol et
        paragraphs = main_content.find_all('p')
        print(f"\nParagraf sayısı: {len(paragraphs)}")
        print("İlk 10 paragraf:")
        for i, p in enumerate(paragraphs[:10], 1):
            text = p.get_text(strip=True)
            if text and len(text) > 20:
                print(f"  {i}. {text[:150]}")
        
        # Tabloları kontrol et
        tables = main_content.find_all('table')
        print(f"\nTablo sayısı: {len(tables)}")
        if tables:
            print("İlk tablo yapısı:")
            first_table = tables[0]
            rows = first_table.find_all('tr')
            print(f"  Satır sayısı: {len(rows)}")
            if rows:
                print("  İlk 5 satır:")
                for i, row in enumerate(rows[:5], 1):
                    cells = row.find_all(['td', 'th'])
                    cell_texts = [c.get_text(strip=True) for c in cells]
                    print(f"    {i}. {cell_texts}")
        
        # Hit Die pattern'lerini ara
        print("\nHit Die Pattern Arama:")
        print("-" * 70)
        hit_die_patterns = [
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Dice[:\s]+d(\d+)',
            r'd(\d+)\s+Hit Die',
            r'Hit Die[:\s]+(\d+)',
            r'(\d+)\s+Hit Die',
        ]
        for pattern in hit_die_patterns:
            matches = re.finditer(pattern, text_content, re.I)
            for match in list(matches)[:3]:
                print(f"  Pattern '{pattern}': '{match.group(0)}' (value: {match.group(1)})")
                # Context göster
                start = max(0, match.start() - 50)
                end = min(len(text_content), match.end() + 50)
                print(f"    Context: ...{text_content[start:end]}...")

print("\n" + "=" * 70)

