#!/usr/bin/env python3
"""Feat ve Spell sayfalarının HTML yapısını debug et"""

import requests
from bs4 import BeautifulSoup
import re

print("=" * 60)
print("Archives of Nethys - Feats.aspx Debug")
print("=" * 60)

url = "https://aonprd.com/Feats.aspx"
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

# Tüm linkleri bul
print("\n[DEBUG] Tum linkler (Feat iceren):")
all_links = soup.find_all('a', href=True)
feat_links = [l for l in all_links if 'feat' in l.get('href', '').lower() or 'Feat' in l.get_text()]
for i, link in enumerate(feat_links[:30]):
    print(f"  {i+1}. {link.get_text(strip=True)[:50]} -> {link.get('href')[:70]}")

# Category linkleri
print("\n[DEBUG] Category linkleri:")
cat_links = soup.find_all('a', href=re.compile(r'Feats\.aspx\?Category='))
for i, link in enumerate(cat_links[:20]):
    print(f"  {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")

# Bir kategoriyi test et
if cat_links:
    test_cat = cat_links[1].get('href')  # İlk "General" boş, ikinciyi al
    print(f"\n📋 Test kategori: {test_cat}")
    # Göreceli URL'yi tam URL'ye çevir
    if test_cat.startswith('/'):
        cat_url = f"https://aonprd.com{test_cat}"
    elif not test_cat.startswith('http'):
        cat_url = f"https://aonprd.com/{test_cat}"
    else:
        cat_url = test_cat
    
    print(f"  URL: {cat_url}")
    cat_response = requests.get(cat_url, timeout=30)
    cat_soup = BeautifulSoup(cat_response.content, 'html.parser')
    
    display_links = cat_soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx'))
    print(f"  Bu kategoride {len(display_links)} feat bulundu:")
    for i, link in enumerate(display_links[:10]):
        print(f"    {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")

print("\n" + "=" * 60)
print("Archives of Nethys - Spells.aspx Debug")
print("=" * 60)

url = "https://aonprd.com/Spells.aspx"
response = requests.get(url, timeout=30)
soup = BeautifulSoup(response.content, 'html.parser')

# Tüm linkleri bul
print("\n[DEBUG] Tum linkler (Spell iceren):")
all_links = soup.find_all('a', href=True)
spell_links = [l for l in all_links if 'spell' in l.get('href', '').lower() or 'Spell' in l.get_text()]
for i, link in enumerate(spell_links[:30]):
    print(f"  {i+1}. {link.get_text(strip=True)[:50]} -> {link.get('href')[:70]}")

# Category/Level/Class linkleri
print("\n[DEBUG] Kategori linkleri:")
cat_links = soup.find_all('a', href=re.compile(r'Spells\.aspx\?[CL]'))
for i, link in enumerate(cat_links[:30]):
    print(f"  {i+1}. {link.get_text(strip=True)[:40]} -> {link.get('href')[:60]}")

# Direkt SpellsDisplay linkleri
print("\n[DEBUG] Direkt SpellsDisplay linkleri:")
display_links = soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx'))
print(f"  Toplam {len(display_links)} büyü linki bulundu (ilk 10):")
for i, link in enumerate(display_links[:10]):
    print(f"    {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")

