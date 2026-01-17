#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Battlesuit sayfasını detaylı analiz et - Advantages ve Skills bul"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.d20herosrd.com"
url = BASE_URL + "/character-creation/archetypes/battlesuit/"

print("Battlesuit sayfası detaylı analiz ediliyor...")
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
    
    full_text = main_content.get_text()
    
    print("\n🔍 ADVANTAGES BÖLÜMÜ:")
    print("-" * 70)
    
    # Advantages kelimesini içeren tüm metni bul
    advantages_patterns = [
        r'[Aa]dvantages?[:\s]+([^PpSs]{50,1000}?)(?=[Pp]owers?|[Ss]kills?|$)',
        r'[Aa]dvantages?[:\s]*\n([^\n]{20,500}?)(?=\n[A-Z]|\n\n|$)',
    ]
    
    for i, pattern in enumerate(advantages_patterns):
        match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
        if match:
            print(f"  Pattern {i+1} bulundu:")
            advantages_text = match.group(1).strip()
            print(f"    {advantages_text[:300]}...")
            
            # Advantage isimlerini çıkar
            # Virgülle ayrılmış liste formatı
            advantages_list = [a.strip() for a in advantages_text.split(',') if a.strip()]
            print(f"    Virgülle ayrılmış: {len(advantages_list)} öğe")
            for j, adv in enumerate(advantages_list[:10]):
                print(f"      {j+1}. {adv[:60]}")
            
            # Büyük harfle başlayan kelimeler
            advantages_caps = re.findall(r'\b([A-Z][A-Za-z\s&()]+)\b', advantages_text)
            print(f"    Büyük harfle başlayan: {len(advantages_caps)} öğe")
            for j, adv in enumerate(advantages_caps[:10]):
                print(f"      {j+1}. {adv[:60]}")
            break
    
    print("\n🔍 SKILLS BÖLÜMÜ:")
    print("-" * 70)
    
    # Skills kelimesini içeren tüm metni bul
    skills_patterns = [
        r'[Ss]kills?[:\s]+([^PpAa]{50,1000}?)(?=[Pp]owers?|[Aa]dvantages?|$)',
        r'[Ss]kills?[:\s]*\n([^\n]{20,500}?)(?=\n[A-Z]|\n\n|$)',
    ]
    
    for i, pattern in enumerate(skills_patterns):
        match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
        if match:
            print(f"  Pattern {i+1} bulundu:")
            skills_text = match.group(1).strip()
            print(f"    {skills_text[:300]}...")
            
            # Skill isimlerini çıkar
            skills_list = [s.strip() for s in skills_text.split(',') if s.strip()]
            print(f"    Virgülle ayrılmış: {len(skills_list)} öğe")
            for j, skill in enumerate(skills_list[:10]):
                print(f"      {j+1}. {skill[:60]}")
            
            # Skill formatı: "Skill Name (Ability)" veya "Skill Name: X"
            skills_format = re.findall(r'([A-Z][A-Za-z\s]+(?:\([A-Za-z]+\))?)', skills_text)
            print(f"    Format pattern: {len(skills_format)} öğe")
            for j, skill in enumerate(skills_format[:10]):
                print(f"      {j+1}. {skill[:60]}")
            break
    
    print("\n📋 TÜM METNİN İLGİLİ KISIMLARI:")
    print("-" * 70)
    
    # "Advantages" ve "Skills" kelimelerini içeren cümleleri bul
    lines = full_text.split('\n')
    for i, line in enumerate(lines):
        line_lower = line.lower()
        if 'advantage' in line_lower or 'skill' in line_lower:
            # Önceki ve sonraki birkaç satırı göster
            start = max(0, i-2)
            end = min(len(lines), i+3)
            print(f"\n  Satır {i}:")
            for j in range(start, end):
                marker = ">>> " if j == i else "    "
                print(f"  {marker}{lines[j][:100]}")


