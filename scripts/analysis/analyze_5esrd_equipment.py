"""
5esrd.com equipment sayfalarını analiz et
"""
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BASE_URL = "https://www.5esrd.com"

# Weapons sayfasını detaylı analiz et
test_url = f"{BASE_URL}/equipment/weapons/"

print("=" * 70)
print("5ESRD.COM WEAPONS SAYFASI DETAYLI ANALİZ")
print("=" * 70)
print()

response = requests.get(test_url, timeout=30)
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')
    main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
    
    if main_content:
        # Tüm linkleri bul
        all_links = main_content.find_all('a', href=True)
        print(f"Toplam link sayısı: {len(all_links)}")
        print()
        
        # Tüm linkleri listele
        print("Tüm linkler (ilk 30):")
        for i, link in enumerate(all_links[:30], 1):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            full_url = urljoin(BASE_URL, href) if not href.startswith('http') else href
            print(f"  {i}. {text[:50]:<50} {full_url[:70]}")
        
        print()
        print("=" * 70)
        print("TABLOLAR")
        print("=" * 70)
        
        # Tabloları bul
        tables = main_content.find_all('table')
        print(f"Tablo sayısı: {len(tables)}")
        
        for i, table in enumerate(tables, 1):
            print(f"\nTablo {i}:")
            rows = table.find_all('tr')
            print(f"  Satır sayısı: {len(rows)}")
            
            # İlk 5 satırı göster
            for j, row in enumerate(rows[:5], 1):
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                print(f"    Satır {j}: {' | '.join(cell_texts)}")
        
        print()
        print("=" * 70)
        print("LİSTELER (ul, ol)")
        print("=" * 70)
        
        # Listeleri bul
        lists = main_content.find_all(['ul', 'ol'])
        print(f"Liste sayısı: {len(lists)}")
        
        for i, list_elem in enumerate(lists[:3], 1):
            items = list_elem.find_all('li')
            print(f"\nListe {i}: {len(items)} item")
            for j, item in enumerate(items[:5], 1):
                text = item.get_text(strip=True)
                links_in_item = item.find_all('a', href=True)
                if links_in_item:
                    for link in links_in_item:
                        href = link.get('href', '')
                        link_text = link.get_text(strip=True)
                        print(f"    {j}. {link_text} -> {href[:60]}")
                else:
                    print(f"    {j}. {text[:60]}")
        
        print()
        print("=" * 70)
        print("METIN İÇERİĞİ (ilk 2000 karakter)")
        print("=" * 70)
        
        text_content = main_content.get_text()
        print(text_content[:2000])
