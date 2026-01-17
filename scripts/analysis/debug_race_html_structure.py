#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Archives of Nethys ırk sayfasının HTML yapısını detaylı analiz et"""

from bs4 import BeautifulSoup
import re

def analyze_html_structure():
    print("=" * 60)
    print("Archives of Nethys - Human Race HTML Structure Analysis")
    print("=" * 60)
    
    with open("human_race_aonprd.html", "r", encoding="utf-8") as f:
        soup = BeautifulSoup(f, 'html.parser')
    
    # Languages bölümünü bul
    print("\n[1] LANGUAGES - Detayli Analiz:")
    print("-" * 60)
    
    # "Language" veya "Languages" başlığını bul
    lang_headers = soup.find_all(string=re.compile(r'^Languages?$', re.I))
    print(f"  'Languages' basligi bulundu: {len(lang_headers)}")
    
    for i, lang_header in enumerate(lang_headers[:3]):
        print(f"\n  {i+1}. 'Languages' basligi:")
        parent = lang_header.find_parent(['p', 'div', 'td', 'dt', 'strong', 'b', 'h3', 'h4'])
        if parent:
            print(f"     Parent: {parent.name}")
            print(f"     Parent text: {parent.get_text(strip=True)[:200]}")
            
            # Sonraki kardeşleri kontrol et
            print(f"     Sonraki kardesler:")
            next_sib = parent.next_sibling
            count = 0
            while next_sib and count < 5:
                if hasattr(next_sib, 'name'):
                    print(f"       {count+1}. <{next_sib.name}>: {next_sib.get_text(strip=True)[:150]}")
                    count += 1
                next_sib = next_sib.next_sibling
    
    # Tüm <strong> ve <b> etiketlerini bul (Languages başlığı için)
    print("\n[2] STRONG/B etiketleri (potansiyel basliklar):")
    print("-" * 60)
    strong_tags = soup.find_all(['strong', 'b'])
    for i, tag in enumerate(strong_tags[:20]):
        text = tag.get_text(strip=True)
        if len(text) < 50 and text:
            # Sonraki içeriği göster
            next_content = ""
            next_elem = tag.next_sibling
            if next_elem:
                if hasattr(next_elem, 'get_text'):
                    next_content = next_elem.get_text(strip=True)[:100]
                else:
                    next_content = str(next_elem)[:100]
            
            print(f"  {i+1}. '{text}' -> {next_content[:100]}")
    
    # Racial Traits bölümünü bul
    print("\n[3] RACIAL TRAITS - Detayli Analiz:")
    print("-" * 60)
    
    # H3/H4 başlıklarını bul
    h3_h4 = soup.find_all(['h3', 'h4'])
    print(f"  H3/H4 basliklari: {len(h3_h4)}")
    
    trait_keywords = ['trait', 'racial', 'special', 'ability', 'skill', 'feat', 'vision', 'immunity']
    
    for i, header in enumerate(h3_h4[:15]):
        header_text = header.get_text(strip=True)
        if any(keyword in header_text.lower() for keyword in trait_keywords) or len(header_text) < 60:
            print(f"\n  {i+1}. [{header.name}] '{header_text}'")
            
            # Sonraki içeriği bul
            current = header.next_sibling
            content_parts = []
            depth = 0
            while current and depth < 5:
                if hasattr(current, 'name'):
                    if current.name in ['p', 'div', 'li']:
                        text = current.get_text(strip=True)
                        if text and len(text) > 10:
                            content_parts.append(text[:200])
                            depth += 1
                    elif current.name in ['h3', 'h4', 'h2']:
                        break  # Yeni başlık
                    elif current.name == 'ul':
                        # Liste içeriğini al
                        for li in current.find_all('li')[:3]:
                            li_text = li.get_text(strip=True)
                            if li_text:
                                content_parts.append(f"  • {li_text[:150]}")
                                depth += 1
                                if depth >= 5:
                                    break
                current = getattr(current, 'next_sibling', None)
            
            for j, part in enumerate(content_parts[:3]):
                print(f"      {j+1}. {part}")
    
    # Vision bölümünü bul
    print("\n[4] VISION - Detayli Analiz:")
    print("-" * 60)
    vision_patterns = [
        r'Low-light\s+Vision',
        r'Darkvision\s*(\d+)',
        r'Vision\s*:?\s*([^\n]+)',
    ]
    
    full_text = soup.get_text()
    for pattern in vision_patterns:
        matches = list(re.finditer(pattern, full_text, re.IGNORECASE))
        if matches:
            print(f"  Pattern '{pattern}' bulundu: {len(matches)}")
            for match in matches[:3]:
                context_start = max(0, match.start() - 50)
                context_end = min(len(full_text), match.end() + 100)
                context = full_text[context_start:context_end]
                print(f"    -> {context}")
    
    # Table yapısını kontrol et (bazı sayfalarda bilgiler tabloda olabilir)
    print("\n[5] TABLE YAPISI:")
    print("-" * 60)
    tables = soup.find_all('table')
    print(f"  Tablolar: {len(tables)}")
    for i, table in enumerate(tables[:3]):
        print(f"\n  Tablo {i+1}:")
        rows = table.find_all('tr')
        for j, row in enumerate(rows[:5]):
            cells = row.find_all(['td', 'th'])
            cell_texts = [cell.get_text(strip=True)[:50] for cell in cells]
            print(f"    Satir {j+1}: {cell_texts}")

if __name__ == "__main__":
    try:
        analyze_html_structure()
        print("\n[OK] Analiz tamamlandi!")
    except Exception as e:
        print(f"[HATA] Hata: {e}")
        import traceback
        traceback.print_exc()


