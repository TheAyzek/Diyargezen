#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archives of Nethys büyü sayfasını detaylı analiz et"""

import requests
from bs4 import BeautifulSoup
import re
from urllib.parse import urljoin

def analyze_spells_page():
    print("=" * 60)
    print("Archives of Nethys - Spells.aspx Detaylı Analiz")
    print("=" * 60)
    
    url = "https://aonprd.com/Spells.aspx"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    print("\n[1] Ana sayfa HTML yapısı:")
    print(f"  Title: {soup.title.string if soup.title else 'N/A'}")
    
    # Tüm linkleri bul
    print("\n[2] Tüm linkler (spell/Spell içeren):")
    all_links = soup.find_all('a', href=True)
    spell_links = [l for l in all_links if 'spell' in l.get('href', '').lower() or 'Spell' in l.get_text()]
    print(f"  Toplam {len(spell_links)} link bulundu")
    
    for i, link in enumerate(spell_links[:30]):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        print(f"  {i+1}. {text[:50]} -> {href[:60]}")
    
    # SpellsDisplay linklerini bul
    print("\n[3] SpellsDisplay.aspx linkleri:")
    display_links = soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx'))
    print(f"  Direkt SpellsDisplay linkleri: {len(display_links)}")
    for i, link in enumerate(display_links[:20]):
        print(f"    {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")
    
    # Kategori/Level/Class linkleri
    print("\n[4] Kategori linkleri (Spells.aspx? ile başlayan):")
    category_links = soup.find_all('a', href=re.compile(r'Spells\.aspx\?'))
    print(f"  Kategori sayısı: {len(category_links)}")
    for i, link in enumerate(category_links[:30]):
        href = link.get('href', '')
        text = link.get_text(strip=True)
        print(f"    {i+1}. {text[:40]} -> {href[:70]}")
    
    # "All Spells" sayfasını test et (en kapsamlı)
    test_category = None
    for link in category_links:
        if 'All' in link.get_text():
            test_category = link
            break
    
    # Eğer All bulunamazsa, Cleric'i test et
    if not test_category:
        for link in category_links:
            if 'Cleric' in link.get_text():
                test_category = link
                break
    
    # Hala bulunamazsa ilkini al
    if not test_category and category_links:
        test_category = category_links[0]
        test_href = test_category.get('href', '')
        if test_href:
            if not test_href.startswith('http'):
                test_url = urljoin("https://aonprd.com/", test_href)
            else:
                test_url = test_href
            
            print(f"\n[5] Test kategori sayfası: {test_url}")
            cat_response = requests.get(test_url, timeout=30)
            cat_soup = BeautifulSoup(cat_response.content, 'html.parser')
            
            # Bu sayfadaki SpellsDisplay linkleri
            cat_display_links = cat_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx'))
            print(f"  Bu kategoride {len(cat_display_links)} büyü bulundu (ilk 10):")
            for i, link in enumerate(cat_display_links[:10]):
                print(f"    {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")
            
            # Eğer direkt linkler varsa, birini test et
            if cat_display_links:
                test_spell = cat_display_links[0]
                spell_href = test_spell.get('href', '')
                if not spell_href.startswith('http'):
                    spell_url = urljoin("https://aonprd.com/", spell_href)
                else:
                    spell_url = spell_href
                
                    # Eğer direkt linkler yoksa, sayfanın içeriğini analiz et
                if len(cat_display_links) == 0:
                    print("  Direkt linkler yok, sayfa yapısını analiz ediyoruz...")
                    # Table, div, list gibi yapıları kontrol et
                    tables = cat_soup.find_all('table')
                    print(f"    Tablolar: {len(tables)}")
                    
                    # Tüm linkleri tekrar kontrol et (belki farklı bir pattern var)
                    all_cat_links = cat_soup.find_all('a', href=True)
                    spell_related = [l for l in all_cat_links if 'spell' in l.get('href', '').lower() or 'Spell' in l.get_text()]
                    print(f"    Spell ile ilgili linkler: {len(spell_related)} (ilk 10):")
                    for i, link in enumerate(spell_related[:10]):
                        print(f"      {i+1}. {link.get_text(strip=True)[:40]} -> {link.get('href')[:60]}")
                    
                    # HTML'i kaydet
                    with open("test_cleric_spells_page.html", "w", encoding="utf-8") as f:
                        f.write(cat_soup.prettify())
                    print("    HTML kaydedildi: test_cleric_spells_page.html")
                else:
                    print(f"\n[6] Test büyü sayfası: {spell_url}")
                    spell_response = requests.get(spell_url, timeout=30)
                    spell_soup = BeautifulSoup(spell_response.content, 'html.parser')
                    
                    # Büyü bilgilerini bul
                    print("  Büyü bilgileri:")
                    title = spell_soup.find('title')
                    if title:
                        print(f"    Başlık: {title.string}")
                    
                    # Level bilgisi
                    full_text = spell_soup.get_text()
                    level_match = re.search(r'Level\s*:?\s*(\d+)', full_text, re.IGNORECASE)
                    if level_match:
                        print(f"    Level: {level_match.group(1)}")
                    
                    # School bilgisi
                    school_match = re.search(r'School\s*:?\s*(\w+)', full_text, re.IGNORECASE)
                    if school_match:
                        print(f"    School: {school_match.group(1)}")

if __name__ == "__main__":
    analyze_spells_page()

