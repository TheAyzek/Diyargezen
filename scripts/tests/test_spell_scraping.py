#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Spell scraping'i test et"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

from bs4 import BeautifulSoup
import requests


def test_spell_page_structure():
    """Spells sayfasının yapısını test et"""
    print("=" * 60)
    print("SPELL PAGE STRUCTURE TEST")
    print("=" * 60)
    
    # Archives of Nethys
    print("\n📚 Archives of Nethys:")
    url = "https://aonprd.com/Spells.aspx"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tüm linkleri bul
        all_links = soup.find_all('a', href=True)
        spell_links = [l for l in all_links if 'Spell' in l.get('href', '')]
        
        print(f"  Toplam link: {len(all_links)}")
        print(f"  Spell içeren link: {len(spell_links)}")
        
        # İlk birkaç spell linkini göster
        print("\n  İlk 10 spell linki:")
        for i, link in enumerate(spell_links[:10]):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"    {i+1}. {text[:50]} -> {href[:80]}")
        
        # "All Spells" sayfasını kontrol et
        print("\n  'All Spells' sayfası kontrol ediliyor...")
        all_spells_url = "https://aonprd.com/Spells.aspx?Class=All"
        try:
            all_response = requests.get(all_spells_url, timeout=30)
            all_response.raise_for_status()
            all_soup = BeautifulSoup(all_response.content, 'html.parser')
            
            # SpellsDisplay linklerini bul
            display_links = all_soup.find_all('a', href=lambda x: x and 'SpellsDisplay' in x)
            print(f"  SpellsDisplay linkleri: {len(display_links)}")
            if display_links:
                print("  İlk 5 SpellsDisplay linki:")
                for i, link in enumerate(display_links[:5]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    print(f"    {i+1}. {text[:50]} -> {href[:80]}")
            else:
                # Tüm linkleri kontrol et
                all_links_all = all_soup.find_all('a', href=True)
                print(f"  Toplam link (All Spells): {len(all_links_all)}")
                
                # SpellsDisplay içeren linkleri bul
                spells_display = [l for l in all_links_all if 'SpellsDisplay' in l.get('href', '')]
                print(f"  SpellsDisplay içeren linkler: {len(spells_display)}")
                if spells_display:
                    print("  İlk 5 SpellsDisplay linki:")
                    for i, link in enumerate(spells_display[:5]):
                        href = link.get('href', '')
                        text = link.get_text(strip=True)
                        print(f"    {i+1}. {text[:50]} -> {href[:80]}")
                
                # Tablo içindeki linkleri kontrol et
                tables = all_soup.find_all('table')
                print(f"\n  Tablo sayısı: {len(tables)}")
                if tables:
                    for i, table in enumerate(tables[:3]):
                        table_links = table.find_all('a', href=True)
                        spells_links = [l for l in table_links if 'Spell' in l.get('href', '')]
                        print(f"    Tablo {i+1}: {len(table_links)} link, {len(spells_links)} spell linki")
                        if spells_links:
                            print(f"      İlk 3: {[l.get_text(strip=True)[:30] for l in spells_links[:3]]}")
                
                print("\n  İlk 20 link (href kontrolü):")
                for i, link in enumerate(all_links_all[:20]):
                    href = link.get('href', '')
                    text = link.get_text(strip=True)
                    if 'Spell' in href or 'spell' in href.lower():
                        print(f"    {i+1}. {text[:50]} -> {href[:80]}")
        except Exception as e:
            print(f"  ❌ All Spells sayfası hatası: {e}")
        
        # Kategori linklerini bul
        category_links = soup.find_all('a', href=lambda x: x and ('Category=' in x or 'Level=' in x or 'Class=' in x))
        print(f"\n  Kategori linkleri: {len(category_links)}")
        if category_links:
            print("  İlk 5 kategori linki:")
            for i, link in enumerate(category_links[:5]):
                href = link.get('href', '')
                text = link.get_text(strip=True)
                print(f"    {i+1}. {text[:50]} -> {href[:80]}")
        
    except Exception as e:
        print(f"  ❌ Hata: {e}")
    
    # d20pfsrd
    print("\n📚 d20pfsrd.com:")
    url = "https://www.d20pfsrd.com/magic/all-spells/"
    try:
        response = requests.get(url, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Tüm linkleri bul
        all_links = soup.find_all('a', href=True)
        spell_links = [l for l in all_links if '/spells/' in l.get('href', '').lower()]
        
        print(f"  Toplam link: {len(all_links)}")
        print(f"  /spells/ içeren link: {len(spell_links)}")
        
        # İlk birkaç spell linkini göster
        print("\n  İlk 10 spell linki:")
        for i, link in enumerate(spell_links[:10]):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            print(f"    {i+1}. {text[:50]} -> {href[:80]}")
        
    except Exception as e:
        print(f"  ❌ Hata: {e}")


if __name__ == "__main__":
    test_spell_page_structure()

