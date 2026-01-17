#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Kısa açıklamalı effect'leri düzelt"""

import sys
import io
import json
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path

if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

BASE_URL = "https://www.d20herosrd.com"

def scrape_effect_detail(url: str, name: str) -> dict:
    """Effect detay sayfasını çek"""
    try:
        response = requests.get(url, timeout=30)
        if response.status_code != 200:
            return None
        
        soup = BeautifulSoup(response.content, 'html.parser')
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        # Effect başlığını bul
        headers = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
        effect_header = None
        
        for header in headers:
            header_text = header.get_text(strip=True).upper()
            if name.upper() in header_text or header_text.startswith(name.upper()):
                effect_header = header
                break
        
        # Description'ı bul
        description_parts = []
        start_elem = effect_header if effect_header else main_content
        
        next_elem = start_elem.find_next_sibling() if effect_header else main_content.find('p')
        while next_elem:
            if next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                break
            
            if next_elem.name in ['p', 'div']:
                text = next_elem.get_text(strip=True)
                if (len(text) > 30 and 
                    'Green Ronin' not in text and 
                    'Mutants & Masterminds' not in text and
                    'OGN' not in text and
                    'd20pfsrd' not in text.lower() and
                    'Open Gaming' not in text):
                    description_parts.append(text)
            
            next_elem = next_elem.find_next_sibling()
            if len(description_parts) >= 15:
                break
        
        if not description_parts:
            # Tüm paragrafları bul
            all_paragraphs = main_content.find_all('p')
            for p in all_paragraphs:
                text = p.get_text(strip=True)
                if (len(text) > 30 and 
                    'Green Ronin' not in text and 
                    'Mutants & Masterminds' not in text and
                    'OGN' not in text):
                    description_parts.append(text)
                    if len(description_parts) >= 5:
                        break
        
        if description_parts:
            return "\n\n".join(description_parts)[:2000]
        return None
        
    except Exception as e:
        print(f"  Hata: {e}")
        return None

# Kısa açıklamalı effect'leri düzelt
data_file = Path("data/mm_data.json")
with open(data_file, 'r', encoding='utf-8') as f:
    data = json.load(f)

power_effects = data.get('power_effects', {})
short_effects = []

for name, eff in power_effects.items():
    desc_len = len(eff.get('description', ''))
    if desc_len < 500:  # 500 karakterden az olanları düzelt
        short_effects.append((name, eff, desc_len))

print(f"Kısa açıklamalı effect'ler: {len(short_effects)}")
print()

# Her birini düzelt
for name, eff, desc_len in short_effects:
    print(f"Düzeltiliyor: {name} ({desc_len} karakter)...")
    url = eff.get('source', '')
    if url:
        new_description = scrape_effect_detail(url, name)
        if new_description and len(new_description) > desc_len:
            eff['description'] = new_description
            print(f"  ✅ Güncellendi: {len(new_description)} karakter")
        else:
            print(f"  ⚠️  Değişmedi")
    print()

# Archetype'lardaki "Effect Descriptions" string'ini temizle
print("Archetype'lar temizleniyor...")
archetypes = data.get('archetypes', {})
cleaned_count = 0

for arch_name, arch_data in archetypes.items():
    suggested_powers = arch_data.get('suggested_powers', [])
    if suggested_powers:
        # "Effect Descriptions" ile başlayan string'i bul ve kaldır
        cleaned = [p for p in suggested_powers if not p.startswith('Effect Descriptions') and len(p) < 100]
        if len(cleaned) != len(suggested_powers):
            arch_data['suggested_powers'] = cleaned
            cleaned_count += 1
            print(f"  ✅ {arch_name}: {len(suggested_powers) - len(cleaned)} yanlış entry kaldırıldı")

print(f"\n✅ {cleaned_count} archetype temizlendi")
print()

# Kaydet
print("Veriler kaydediliyor...")
with open(data_file, 'w', encoding='utf-8') as f:
    json.dump(data, f, ensure_ascii=False, indent=2)

print("✅ Tamamlandı!")


