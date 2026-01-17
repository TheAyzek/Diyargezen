#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Character Creation sayfasını detaylı analiz et"""

import requests
from bs4 import BeautifulSoup
import re

BASE_URL = "https://www.d20herosrd.com"
url = BASE_URL + "/character-creation/"

print("Character Creation sayfası analiz ediliyor...")
response = requests.get(url, timeout=30)
if response.status_code != 200:
    print(f"❌ Sayfa bulunamadı: {response.status_code}")
    exit(1)

soup = BeautifulSoup(response.content, 'html.parser')

# Tüm başlıkları bul
headers = soup.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
print(f"\n📊 Toplam başlık: {len(headers)}")

print("\n🔍 İlgili başlıklar:")
for header in headers:
    text = header.get_text(strip=True)
    if any(keyword in text.lower() for keyword in ['skill', 'advantage', 'ability', 'power', 'archetype']):
        print(f"  {header.name}: {text}")

# Tüm linkleri bul ve kategorize et
print("\n📋 Tüm ilgili linkler:")
all_links = soup.find_all('a', href=True)

sections = {
    'abilities': [],
    'skills': [],
    'advantages': [],
    'powers': [],
    'archetypes': []
}

for link in all_links:
    href = link.get('href', '')
    text = link.get_text(strip=True)
    
    href_lower = href.lower()
    text_lower = text.lower()
    
    # Abilities
    if ('3-abilities' in href_lower or ('3.' in text_lower and 'abilit' in text_lower)) and href:
        sections['abilities'].append((text, href))
    
    # Skills - farklı pattern'ler dene
    if '4-' in href_lower and 'skill' in href_lower:
        sections['skills'].append((text, href))
    elif '4.' in text_lower and 'skill' in text_lower:
        sections['skills'].append((text, href))
    elif href_lower.endswith('skills/') or href_lower.endswith('/skills'):
        sections['skills'].append((text, href))
    
    # Advantages
    if '5-' in href_lower and 'advantage' in href_lower:
        sections['advantages'].append((text, href))
    elif '5.' in text_lower and 'advantage' in text_lower:
        sections['advantages'].append((text, href))
    elif href_lower.endswith('advantages/') or href_lower.endswith('/advantages'):
        sections['advantages'].append((text, href))
    
    # Powers
    if '/6-powers/' in href_lower or ('6.' in text_lower and 'power' in text_lower):
        sections['powers'].append((text, href))
    
    # Archetypes
    if '/archetypes/' in href_lower:
        sections['archetypes'].append((text, href))

# Sonuçları göster
print("\n💪 ABILITIES:")
for name, url in sections['abilities'][:5]:
    print(f"  {name}: {url}")

print("\n🎯 SKILLS:")
if sections['skills']:
    for name, url in sections['skills'][:5]:
        print(f"  {name}: {url}")
else:
    print("  ❌ Skills linki bulunamadı!")
    # Sayı ile başlayan linkleri ara
    numbered_links = [l for l in all_links if '4-' in l.get('href', '').lower() or '/4/' in l.get('href', '').lower()]
    print(f"  '4-' içeren linkler: {len(numbered_links)}")
    for link in numbered_links[:5]:
        print(f"    {link.get_text(strip=True)}: {link.get('href', '')}")

print("\n⭐ ADVANTAGES:")
if sections['advantages']:
    for name, url in sections['advantages'][:5]:
        print(f"  {name}: {url}")
else:
    print("  ❌ Advantages linki bulunamadı!")
    # Sayı ile başlayan linkleri ara
    numbered_links = [l for l in all_links if '5-' in l.get('href', '').lower() or '/5/' in l.get('href', '').lower()]
    print(f"  '5-' içeren linkler: {len(numbered_links)}")
    for link in numbered_links[:5]:
        print(f"    {link.get_text(strip=True)}: {link.get('href', '')}")

print("\n⚡ POWERS:")
for name, url in sections['powers'][:5]:
    print(f"  {name}: {url}")

# Sayı ile başlayan tüm linkleri listele
print("\n📊 Sayı ile başlayan linkler:")
numbered_all = [l for l in all_links if re.match(r'/\d+-', l.get('href', '')) or re.match(r'/\d+\.', l.get('href', ''))]
for link in numbered_all[:10]:
    print(f"  {link.get_text(strip=True)}: {link.get('href', '')}")


