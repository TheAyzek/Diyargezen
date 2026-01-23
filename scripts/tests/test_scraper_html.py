#!/usr/bin/env python3
"""
Scraper HTML yapısını test etmek için script
Gerçek HTML yapısını görmek için kullanılır
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(project_root))

import requests
from bs4 import BeautifulSoup

def test_aonprd_races():
    """Archives of Nethys ırk sayfasını test et"""
    print("=" * 60)
    print("Archives of Nethys - Races Test")
    print("=" * 60)
    
    # Core Races sayfasını test et
    print("\n📋 Core Races:")
    url = "https://aonprd.com/Races.aspx?Category=Core"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Display.aspx linklerini bul
    print("\n🔍 Display.aspx links:")
    display_links = soup.find_all('a', href=re.compile(r'Display\.aspx.*ItemName'))
    for i, link in enumerate(display_links[:20]):
        print(f"  {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")
    
    # NonCore Races sayfasını test et
    print("\n📋 NonCore Races:")
    url = "https://aonprd.com/Races.aspx?Category=NonCore"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Display.aspx linklerini bul
    print("\n🔍 Display.aspx links:")
    display_links = soup.find_all('a', href=re.compile(r'Display\.aspx.*ItemName'))
    for i, link in enumerate(display_links[:20]):
        print(f"  {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")

def test_aonprd_classes():
    """Archives of Nethys sınıf sayfasını test et"""
    print("\n" + "=" * 60)
    print("Archives of Nethys - Classes Test")
    print("=" * 60)
    
    url = "https://aonprd.com/Classes.aspx"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # Tüm linkleri bul
    print("\n🔍 Tüm linkler (Class/Display içeren):")
    links = soup.find_all('a', href=True)
    class_links = [l for l in links if 'Class' in l.get('href', '') or 'Display' in l.get('href', '')]
    for i, link in enumerate(class_links[:30]):
        print(f"  {i+1}. {link.get_text(strip=True)[:40]} -> {link.get('href')[:60]}")
    
    # ClassesDisplay pattern
    print("\n🔍 ClassesDisplay.aspx pattern:")
    display_links = soup.find_all('a', href=re.compile(r'ClassesDisplay\.aspx'))
    for i, link in enumerate(display_links[:20]):
        print(f"  {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")

def test_aonprd_feats():
    """Archives of Nethys feat sayfasını test et"""
    print("\n" + "=" * 60)
    print("Archives of Nethys - Feats Test")
    print("=" * 60)
    
    url = "https://aonprd.com/Feats.aspx"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # FeatsDisplay.aspx linklerini bul
    print("\n🔍 FeatsDisplay.aspx links:")
    display_links = soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx'))
    for i, link in enumerate(display_links[:20]):
        print(f"  {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")

def test_aonprd_spells():
    """Archives of Nethys büyü sayfasını test et"""
    print("\n" + "=" * 60)
    print("Archives of Nethys - Spells Test")
    print("=" * 60)
    
    url = "https://aonprd.com/Spells.aspx"
    response = requests.get(url, timeout=30)
    soup = BeautifulSoup(response.content, 'html.parser')
    
    # SpellsDisplay.aspx linklerini bul
    print("\n🔍 SpellsDisplay.aspx links:")
    display_links = soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx'))
    for i, link in enumerate(display_links[:20]):
        print(f"  {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")

def test_d20pfsrd_races():
    """d20pfsrd ırk sayfasını test et"""
    print("\n" + "=" * 60)
    print("d20pfsrd - Races Test")
    print("=" * 60)
    
    url = "https://www.d20pfsrd.com/races"
    try:
        response = requests.get(url, timeout=30)
        soup = BeautifulSoup(response.content, 'html.parser')
        
        print(f"Status: {response.status_code}")
        print(f"Title: {soup.title.string if soup.title else 'N/A'}")
        
        # Tüm linkleri bul
        print("\n🔍 Tüm linkler:")
        links = soup.find_all('a', href=True)
        race_links = [l for l in links if 'race' in l.get('href', '').lower()]
        for i, link in enumerate(race_links[:20]):
            print(f"  {i+1}. {link.get_text(strip=True)} -> {link.get('href')}")
        
        # HTML'i kaydet
        with open("test_d20pfsrd_races.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("\n✅ HTML kaydedildi: test_d20pfsrd_races.html")
    except Exception as e:
        print(f"❌ Hata: {e}")

if __name__ == "__main__":
    import re
    test_aonprd_races()
    test_aonprd_classes()
    test_aonprd_feats()
    test_aonprd_spells()
    test_d20pfsrd_races()

