#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""5esrd.com D&D 5e scraper"""

import time
import json
import requests
from bs4 import BeautifulSoup
import re
from pathlib import Path
from typing import Dict, List, Optional, Any
from urllib.parse import urljoin


class Dnd5eSrdScraper:
    """5esrd.com'dan D&D 5e verilerini çeken scraper"""
    
    BASE_URL = "https://www.5esrd.com"
    
    def __init__(self, rate_limit: float = 1.5):
        """
        Args:
            rate_limit: İstekler arası bekleme süresi (saniye)
        """
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """HTTP GET isteği yap ve BeautifulSoup döndür"""
        for attempt in range(retries):
            try:
                time.sleep(self.rate_limit)
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')
                elif response.status_code == 404:
                    return None
                else:
                    print(f"  ⚠️  Status {response.status_code} for {url}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"  ⚠️  Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None
    
    def scrape_all_spell_links(self) -> List[tuple]:
        """Tüm spell linklerini çek"""
        print("🔍 Spell linkleri çekiliyor...")
        url = f"{self.BASE_URL}/database/spell/"
        
        soup = self._get(url)
        if not soup:
            print("❌ Spell database sayfası bulunamadı!")
            return []
        
        spell_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Spell linklerini bul
            if '/spell/' in href.lower() and text and len(text) < 100:
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                else:
                    full_url = urljoin(url, href)
                spell_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_links = list(set(spell_links))
        print(f"  ✅ {len(unique_links)} unique spell linki bulundu")
        return unique_links
    
    def scrape_spell_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Spell detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        spell_data = {
            "name": name,
            "level": None,
            "school": None,
            "casting_time": None,
            "range": None,
            "components": None,
            "duration": None,
            "description": "",
            "classes": [],
            "ritual": False,
            "concentration": False,
            "source": url
        }
        
        # Tüm paragrafları al
        paragraphs = main_content.find_all('p')
        
        # Metni al
        text_content = main_content.get_text()
        
        # İlk paragrafı al (genellikle level ve school burada)
        first_p = paragraphs[0] if paragraphs else None
        first_para_text = first_p.get_text(strip=True) if first_p else ""
        
        # Level ve School - DÜZELTİLDİ
        # Format: "3rd-levelevocation" veya "Conjurationcantrip" (boşluk yok!)
        # Önce ilk paragraftan bulmaya çalış
        level_school_patterns = [
            r'(\d+)(st|nd|rd|th)[\s-]*level([a-z]+)',  # "3rd-levelevocation"
            r'([a-z]+)cantrip',  # "Conjurationcantrip"
            r'(\d+)(st|nd|rd|th)[\s-]*level\s+([a-z]+)',  # "3rd-level evocation" (boşluklu)
            r'cantrip\s+([a-z]+)',  # "cantrip evocation" (boşluklu)
        ]
        
        found = False
        for pattern in level_school_patterns:
            match = re.search(pattern, first_para_text, re.I)
            if not match:
                match = re.search(pattern, text_content[:500], re.I)  # İlk 500 karakterde ara
            
            if match:
                if 'cantrip' in pattern.lower():
                    spell_data['level'] = 0
                    spell_data['school'] = match.group(1).capitalize() if match.lastindex >= 1 else None
                    found = True
                else:
                    level_num = match.group(1)
                    school = match.group(match.lastindex)  # Son grup school
                    spell_data['level'] = int(level_num)
                    spell_data['school'] = school.capitalize()
                    found = True
                break
        
        # Eğer bulunamadıysa, text'ten daha geniş arama yap
        if not found:
            # "3rd level" veya "1st level" gibi formatları ara
            level_match = re.search(r'(\d+)(st|nd|rd|th)\s*level', text_content, re.I)
            if level_match:
                spell_data['level'] = int(level_match.group(1))
                # School'u bul
                school_match = re.search(r'(?:level|spell)[\s-]+([a-z]+)', text_content[level_match.end():level_match.end()+50], re.I)
                if school_match:
                    spell_data['school'] = school_match.group(1).capitalize()
        
        # Casting Time, Range, Components, Duration - DÜZELTİLDİ (V2)
        # Format: "Casting Time:1 actionRange:60 feetComponents:V, SDuration:Instantaneous"
        # İkinci paragraf genellikle bu bilgileri içerir, ama bazı spell'lerde description'da olabilir
        
        # Önce ikinci paragraftan bulmaya çalış
        second_p = paragraphs[1] if len(paragraphs) > 1 else None
        stats_text = second_p.get_text(strip=True) if second_p else ""
        
        # Eğer ikinci paragrafta yeterli bilgi yoksa, text'in başından ara
        if not stats_text or 'Casting Time' not in stats_text:
            stats_match = re.search(r'Casting\s+Time[:\s]+.+?(?=You |A |Target|$)', text_content[:2000], re.I | re.DOTALL)
            if stats_match:
                stats_text = stats_match.group(0)
        
        # Eğer hala bulunamadıysa, description'dan da çıkarmaya çalış
        if not stats_text or len(stats_text) < 30:
            # Description paragraflarından ara
            for p in paragraphs[2:5] if len(paragraphs) > 2 else []:
                p_text = p.get_text(strip=True)
                if 'Casting Time' in p_text or 'Range:' in p_text or 'Components:' in p_text:
                    stats_text = p_text
                    break
        
        if stats_text:
            # Casting Time - Daha esnek regex
            if not spell_data.get('casting_time'):
                ct_patterns = [
                    r'Casting\s+Time[:\s]+([^R]+?)(?:Range|Components|Duration|$|You |A |Target)',
                    r'Casting\s+Time[:\s]+([^R]+?)(?=Range|$)',
                ]
                for pattern in ct_patterns:
                    ct_match = re.search(pattern, stats_text, re.I)
                    if ct_match:
                        casting_time = ct_match.group(1).strip()
                        spell_data['casting_time'] = re.sub(r'\s+', ' ', casting_time)
                        break
            
            # Range - DÜZELTİLDİ (case-insensitive ve daha akıllı)
            if not spell_data.get('range'):
                # "Range:" veya "Range :" sonrası, "Components" öncesi veya satır sonu
                range_patterns = [
                    r'Range[:\s]+([^C\n]+?)(?:Components|Duration|$)',  # Components veya Duration'a kadar
                    r'Range[:\s]+([a-zA-Z0-9\s\'-]+?)(?=Components|Duration|$)',  # Kelimeler ve boşluklar
                ]
                for pattern in range_patterns:
                    range_match = re.search(pattern, stats_text, re.I)
                    if range_match:
                        range_text = range_match.group(1).strip()
                        # "touch" gibi küçük harfli değerleri düzelt
                        range_text = range_text.capitalize() if range_text.islower() else range_text
                        spell_data['range'] = re.sub(r'\s+', ' ', range_text)
                        break
            
            # Components - DÜZELTİLDİ V4 (position-based, parantez desteği)
            if not spell_data.get('components'):
                # Components başlangıcını bul
                comp_start_match = re.search(r'Components[:\s]+', stats_text, re.I)
                if comp_start_match:
                    start_pos = comp_start_match.end()
                    
                    # Duration'un başlangıcını bul
                    dur_start_match = re.search(r'Duration[:\s]+', stats_text[start_pos:], re.I)
                    if dur_start_match:
                        end_pos = start_pos + dur_start_match.start()
                    else:
                        # Duration yoksa, "You" veya satır sonuna kadar
                        you_match = re.search(r'\bYou\s+', stats_text[start_pos:], re.I)
                        if you_match:
                            end_pos = start_pos + you_match.start()
                        else:
                            end_pos = start_pos + 200  # Fallback: 200 karakter
                    
                    components_raw = stats_text[start_pos:end_pos].strip()
                    
                    # Parantez kontrolü - açık parantez varsa kapatmayı bul
                    open_paren_pos = components_raw.find('(')
                    if open_paren_pos != -1:
                        # Kapanış parantezini bul
                        close_paren_pos = components_raw.find(')', open_paren_pos)
                        if close_paren_pos == -1:
                            # Kapanış parantezi components_raw içinde yok, stats_text'ten devam et
                            remaining_text = stats_text[end_pos:end_pos + 300]
                            close_in_remaining = remaining_text.find(')')
                            if close_in_remaining != -1:
                                # Kapanış parantezi bulundu, components'i genişlet
                                components_raw = stats_text[start_pos:end_pos + close_in_remaining + 1].strip()
                    
                    components = re.sub(r'\s+', ' ', components_raw)
                    spell_data['components'] = components
                    
                    # V, S, M kontrolü
                    if 'V' in components.upper():
                        spell_data['verbal'] = True
                    if 'S' in components.upper():
                        spell_data['somatic'] = True
                    if 'M' in components.upper():
                        spell_data['material'] = True
                        # Material component açıklamasını çıkar
                        m_match = re.search(r'M\s*\(([^)]+)\)', components, re.I)
                        if m_match:
                            spell_data['material_component'] = m_match.group(1).strip()
            
            # Duration - DÜZELTİLDİ V3 (daha akıllı temizleme)
            if not spell_data.get('duration'):
                # Duration başlangıcını bul
                dur_start_match = re.search(r'Duration[:\s]+', stats_text, re.I)
                if dur_start_match:
                    start_pos = dur_start_match.end()
                    # "You", "Your", "A ", "At Higher", "This spell" veya satır sonuna kadar
                    dur_end_patterns = [
                        r'(?:You |Your |A [a-z]+|At Higher|This spell|$)',
                        r'(?=You |Your |At Higher|This spell|$)',
                    ]
                    
                    for end_pattern in dur_end_patterns:
                        dur_end_match = re.search(end_pattern, stats_text[start_pos:], re.I)
                        if dur_end_match:
                            duration_raw = stats_text[start_pos:start_pos + dur_end_match.start()].strip()
                            
                            # "You" ile başlayan cümleleri temizle
                            duration = re.sub(r'\s+You\s+.*$', '', duration_raw, flags=re.DOTALL)
                            duration = re.sub(r'\s+Your\s+.*$', '', duration, flags=re.DOTALL)
                            duration = re.sub(r'\s+A\s+[a-z]+\s+.*$', '', duration, flags=re.DOTALL)
                            duration = duration.strip()
                            
                            # Çok uzun olmamalı (200 karakter limit)
                            if duration and len(duration) <= 200:
                                spell_data['duration'] = re.sub(r'\s+', ' ', duration)
                                if 'concentration' in duration.lower():
                                    spell_data['concentration'] = True
                                if 'ritual' in duration.lower():
                                    spell_data['ritual'] = True
                                break
        
        # Eğer hala eksik veriler varsa, description'dan çıkarmaya çalış
        # (Bazı spell'lerde bu bilgiler description'ın başında olabilir)
        if not spell_data.get('casting_time') or not spell_data.get('range') or not spell_data.get('components') or not spell_data.get('duration'):
            # Tüm metni tekrar tara
            full_text_search = text_content[:3000]  # İlk 3000 karakter yeterli
            
            if not spell_data.get('casting_time'):
                ct_match = re.search(r'Casting\s+Time[:\s]+([^R\n]+?)(?:Range|$|You|A |Target)', full_text_search, re.I)
                if ct_match:
                    spell_data['casting_time'] = ct_match.group(1).strip()
            
            if not spell_data.get('range'):
                range_match = re.search(r'Range[:\s]+([^C\n]+?)(?:Components|Duration|$|You|A |Target)', full_text_search, re.I)
                if range_match:
                    spell_data['range'] = range_match.group(1).strip()
            
            if not spell_data.get('components'):
                comp_match = re.search(r'Components[:\s]+([^D\n]+?(?:\([^)]+\))?[^D]*?)(?:Duration|$|You|A |Target|Concentration)', full_text_search, re.I)
                if comp_match:
                    components = comp_match.group(1).strip()
                    # Parantez kapatılmamışsa düzelt
                    if components.count('(') > components.count(')'):
                        remaining = full_text_search[comp_match.end():comp_match.end()+100]
                        close_match = re.search(r'([^)]+)\)', remaining, re.I)
                        if close_match:
                            components += close_match.group(0)
                    spell_data['components'] = re.sub(r'\s+', ' ', components)
                    # V, S, M kontrolü
                    if 'V' in components.upper():
                        spell_data['verbal'] = True
                    if 'S' in components.upper():
                        spell_data['somatic'] = True
                    if 'M' in components.upper():
                        spell_data['material'] = True
                        m_match = re.search(r'M\s*\(([^)]+)\)', components, re.I)
                        if m_match:
                            spell_data['material_component'] = m_match.group(1).strip()
            
            if not spell_data.get('duration'):
                dur_match = re.search(r'Duration[:\s]+([^Y\n]+?)(?:You |A |Target|At Higher|This spell|$)', full_text_search, re.I | re.DOTALL)
                if dur_match:
                    duration = dur_match.group(1).strip()
                    # "You" ile başlayan cümleleri temizle
                    duration = re.sub(r'\s*You\s+.*$', '', duration, flags=re.DOTALL)
                    duration = re.sub(r'\s*Your\s+.*$', '', duration, flags=re.DOTALL)
                    duration = re.sub(r'\s*A\s+[a-z]+.*$', '', duration, flags=re.DOTALL)
                    duration = duration.strip()
                    if duration and len(duration) < 200:
                        spell_data['duration'] = re.sub(r'\s+', ' ', duration)
                        if 'concentration' in duration.lower():
                            spell_data['concentration'] = True
                        if 'ritual' in duration.lower():
                            spell_data['ritual'] = True
        
        # Description - 3. paragraftan itibaren al (ilk iki paragraf level/school ve stats)
        description_parts = []
        for i, p in enumerate(paragraphs):
            if i < 2:  # İlk iki paragrafı atla
                continue
            text = p.get_text(strip=True)
            if (len(text) > 30 and 
                'Green Ronin' not in text and 
                'OGN' not in text and
                'Open Gaming' not in text and
                'Copyright' not in text and
                'Join Our Discord' not in text and
                'Subscribe' not in text and
                'Casting Time' not in text and  # Stats'ı description'dan çıkar
                'Range:' not in text and
                'Components:' not in text and
                'Duration:' not in text):
                description_parts.append(text)
        
        if description_parts:
            spell_data['description'] = '\n\n'.join(description_parts)
        
        # Classes - Spell lists sayfalarından bulunmalı, şimdilik boş bırak
        # (Daha sonra spell lists'ten çekilecek)
        spell_data['classes'] = []
        
        return spell_data
    
    def scrape_all_spells(self, max_spells: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm spell'leri çek"""
        print("=" * 70)
        print("5ESRD.COM SPELLS ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü - DÜZELTİLDİ (cache'deki spell'leri kullan, eksikleri çek)
        cache_file = Path("data/cache/spells_cache.json")
        spells = {}
        cached_spells = {}
        
        if not force_refresh and cache_file.exists():
            print(f"📦 Cache dosyası bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('spells'):
                    cached_spells = cached['spells']
                    spells.update(cached_spells)
                    print(f"  ✅ {len(cached_spells)} spell cache'den yüklendi")
        
        # Spell linklerini çek
        spell_links = self.scrape_all_spell_links()
        
        # Eğer max_spells varsa, sadece ilk N spell'i al
        if max_spells:
            spell_links = spell_links[:max_spells]
            print(f"  ⚠️  İlk {max_spells} spell çekilecek (test modu)")
        else:
            # Cache'de olmayan spell'leri filtrele - DÜZELTİLDİ
            cached_names = set(cached_spells.keys())
            spell_links = [(name, url) for name, url in spell_links if name not in cached_names]
            if spell_links:
                print(f"  🔄 {len(spell_links)} yeni spell çekilecek ({len(cached_names)} zaten cache'de)")
            else:
                print("  ✅ Tüm spell'ler zaten cache'de!")
                return cached_spells
        
        total = len(spell_links)
        
        print(f"\n📖 {total} spell detayı çekiliyor...")
        print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(spell_links, 1):
            if i % 10 == 0:
                successful = len(spells)
                print(f"  ... {i}/{total} spell çekildi ({successful} başarılı)")
                # Her 50 spell'de bir cache'e kaydet (ilerlemeyi koru)
                if i % 50 == 0:
                    all_spells_temp = {**cached_spells, **spells}
                    cache_data = {
                        'total': len(all_spells_temp),
                        'spells': all_spells_temp,
                        'source': '5esrd.com',
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'progress': f'{i}/{total}'
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 İlerleme kaydedildi: {successful} yeni spell, toplam {len(all_spells_temp)}")
            
            spell_data = self.scrape_spell_detail(url, name)
            if spell_data and spell_data.get('name'):
                spells[spell_data['name']] = spell_data
        
        print(f"\n✅ {len(spells)} yeni spell başarıyla çekildi")
        print(f"   Toplam: {len(spells) + len(cached_spells)} spell (cache dahil)")
        
        # Final cache'e kaydet
        all_spells = {**cached_spells, **spells}
        cache_data = {
            'total': len(all_spells),
            'spells': all_spells,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache'e kaydedildi: {cache_file}")
        
        return all_spells
    
    def scrape_all_feat_links(self) -> List[tuple]:
        """Tüm feat linklerini çek - DÜZELTİLDİ (Feats Scraping)"""
        print("🔍 Feat linkleri çekiliyor...")
        
        # 5esrd.com'da feat'ler /database/feats/ altında
        url = f"{self.BASE_URL}/database/feats"
        
        soup = self._get(url)
        if not soup:
            print("❌ Feats database sayfası bulunamadı!")
            return []
        
        feat_links = []
        
        # Feat linklerini bul - /database/feats/ içeren ve anlamlı text'i olan linkler
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # /database/feats/ içeren ve feat detay sayfası olan linkler
            # Format: /database/feats/[feat-name]/
            if '/database/feats/' in href.lower() and text and len(text) < 100 and text != 'Feats':
                # List/index sayfalarını filtrele
                if any(skip in href.lower() for skip in ['/feats', '/database/feats', 'list', 'index', 'category']):
                    # Eğer /database/feats/ ile bitmiyorsa ve bir feat adı içeriyorsa (kısa çizgi ile ayrılmış)
                    if not href.lower().endswith('/feats/') and not href.lower().endswith('/feats'):
                        # Feat detay sayfası gibi görünüyor (örn: /database/feats/a-taste-of-power/)
                        pass  # Devam et
                    else:
                        continue  # List sayfası, atla
                
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(url, href)
                
                # Feat detay sayfası kontrolü - URL'de feat adı olmalı (kısa çizgi ile ayrılmış kelimeler)
                if '/database/feats/' in full_url.lower() and full_url.lower().count('/') >= 4:
                    # Örnek: /database/feats/a-taste-of-power/ -> 4+ slash var
                    feat_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_links = list(set(feat_links))
        print(f"  ✅ {len(unique_links)} unique feat linki bulundu")
        return unique_links
    
    def scrape_feat_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Feat detay sayfasını çek - DÜZELTİLDİ (Feats Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        feat_data = {
            "name": name,
            "prerequisite": None,
            "description": "",
            "source": url
        }
        
        # Tüm paragrafları al
        paragraphs = main_content.find_all('p')
        
        # Metni al
        text_content = main_content.get_text()
        
        # Prerequisite - DÜZELTİLDİ (Feats Scraping)
        # Format: "Prerequisite: Strength 13 or higher" veya "Prerequisite: None"
        prereq_patterns = [
            r'Prerequisite[:\s]+([^D\n]+?)(?:Description|$|You |A |At Higher|This feat|Benefits|Special)',
            r'Prerequisites?[:\s]+([^D\n]+?)(?:Description|$|You |A |Benefits|Special)',
            r'Prerequisite[:\s]+(.+?)(?:\n\n|$|Description)',
        ]
        
        for pattern in prereq_patterns:
            prereq_match = re.search(pattern, text_content[:1000], re.I)
            if prereq_match:
                prerequisite = prereq_match.group(1).strip()
                # "None" veya boş değilse kaydet
                if prerequisite and prerequisite.lower() not in ['none', 'none.', '']:
                    feat_data['prerequisite'] = prerequisite
                break
        
        # Description - DÜZELTİLDİ V2 (Feats Scraping - iyileştirildi)
        description_parts = []
        
        # İlk olarak, "Benefit(s):" veya "Description:" gibi başlıkları ara
        benefit_pattern = re.search(r'(?:Benefit|Benefits|Description)[:\s]+(.+?)(?:\n\n|$)', text_content, re.I | re.DOTALL)
        if benefit_pattern:
            description_text = benefit_pattern.group(1).strip()
            # İlk 2000 karakteri al
            description_text = description_text[:2000]
            description_parts.append(description_text)
        else:
            # Benefit bulunamadıysa, paragrafları kontrol et
            start_collecting = False
            found_prerequisite = False
            
            for i, p in enumerate(paragraphs):
                text = p.get_text(strip=True)
                
                # Prerequisite paragrafını işaretle
                if 'prerequisite' in text.lower() and i < 5:
                    found_prerequisite = True
                    start_collecting = True
                    continue
                
                # Description/Benefit başlığı varsa, ondan sonraki paragrafları al
                if 'benefit' in text.lower() or 'description' in text.lower():
                    if i < 10:  # İlk 10 paragrafta olmalı
                        start_collecting = True
                        # Benefit text'ini de ekle
                        if len(text) > 50:
                            description_parts.append(text)
                        continue
                
                # Copyright, footer metinlerini atla
                skip_texts = [
                    'Green Ronin', 'OGN', 'Open Gaming', 'Copyright',
                    'Join Our Discord', 'Subscribe', 'license attribution',
                    'see the full license', 'This is not the complete license'
                ]
                
                should_skip = any(skip in text for skip in skip_texts)
                
                if (len(text) > 20 and not should_skip and
                    'Prerequisite' not in text and 'Prerequisites' not in text):
                    
                    # Prerequisite'ten sonra veya 3. paragraftan itibaren topla
                    if start_collecting or (found_prerequisite and i > 1) or (not found_prerequisite and i >= 1):
                        description_parts.append(text)
        
        # Description'ı temizle ve birleştir
        if description_parts:
            # Lisans metinlerini temizle
            cleaned_parts = []
            for part in description_parts:
                # Lisans metinlerini filtrele
                if any(skip in part for skip in ['license attribution', 'see the full license', 'This is not the complete']):
                    continue
                # Çok kısa paragrafları atla (genellikle navigation/header)
                if len(part) > 20:
                    cleaned_parts.append(part)
            
            if cleaned_parts:
                feat_data['description'] = '\n\n'.join(cleaned_parts[:10])  # En fazla 10 paragraf
        
        return feat_data
    
    def scrape_all_feats(self, max_feats: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm feat'leri çek - DÜZELTİLDİ (Feats Scraping)"""
        print("=" * 70)
        print("5ESRD.COM FEATS ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü
        cache_file = Path("data/cache/feats_cache.json")
        feats = {}
        cached_feats = {}
        
        if not force_refresh and cache_file.exists():
            print(f"📦 Cache dosyası bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('feats'):
                    cached_feats = cached['feats']
                    feats.update(cached_feats)
                    print(f"  ✅ {len(cached_feats)} feat cache'den yüklendi")
        
        # Feat linklerini çek
        feat_links = self.scrape_all_feat_links()
        
        if not feat_links:
            print("  ⚠️  Feat linkleri bulunamadı! Mevcut cache'i döndürüyoruz.")
            return cached_feats
        
        # Eğer max_feats varsa, sadece ilk N feat'i al
        if max_feats:
            feat_links = feat_links[:max_feats]
            print(f"  ⚠️  İlk {max_feats} feat çekilecek (test modu)")
        else:
            # Cache'de olmayan feat'leri filtrele
            cached_names = set(cached_feats.keys())
            feat_links = [(name, url) for name, url in feat_links if name not in cached_names]
            if feat_links:
                print(f"  🔄 {len(feat_links)} yeni feat çekilecek ({len(cached_names)} zaten cache'de)")
            else:
                print("  ✅ Tüm feat'ler zaten cache'de!")
                return cached_feats
        
        total = len(feat_links)
        
        print(f"\n📖 {total} feat detayı çekiliyor...")
        print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(feat_links, 1):
            if i % 10 == 0:
                successful = len(feats)
                print(f"  ... {i}/{total} feat çekildi ({successful} başarılı)")
                # Her 50 feat'te bir cache'e kaydet (ilerlemeyi koru)
                if i % 50 == 0:
                    all_feats_temp = {**cached_feats, **feats}
                    cache_data = {
                        'total': len(all_feats_temp),
                        'feats': all_feats_temp,
                        'source': '5esrd.com',
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'progress': f'{i}/{total}'
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 İlerleme kaydedildi: {successful} yeni feat, toplam {len(all_feats_temp)}")
            
            feat_data = self.scrape_feat_detail(url, name)
            if feat_data and feat_data.get('name'):
                feats[feat_data['name']] = feat_data
        
        print(f"\n✅ {len(feats)} yeni feat başarıyla çekildi")
        print(f"   Toplam: {len(feats) + len(cached_feats)} feat (cache dahil)")
        
        # Final cache'e kaydet
        all_feats = {**cached_feats, **feats}
        cache_data = {
            'total': len(all_feats),
            'feats': all_feats,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache'e kaydedildi: {cache_file}")
        
        return all_feats
    
    def scrape_all_class_links(self) -> List[tuple]:
        """Tüm class linklerini çek - DÜZELTİLDİ (Classes Scraping)"""
        print("🔍 Class linkleri çekiliyor...")
        url = f"{self.BASE_URL}/classes/"
        
        soup = self._get(url)
        if not soup:
            print("❌ Classes sayfası bulunamadı!")
            return []
        
        class_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Core classes için: /database/class/class-name/ pattern'ini kullan
            if '/database/class/' in href.lower() and text and len(text) < 50 and len(text) > 1:
                # 3rd party veya prestige class'ları filtrele
                if '3rd-party' not in href.lower() and 'prestige' not in href.lower():
                    if href.endswith('/'):
                        if href.startswith('/'):
                            full_url = self.BASE_URL + href
                        else:
                            full_url = urljoin(url, href)
                        class_links.append((text, full_url))
        
        # Tekrar edenleri kaldır ve sırala
        unique_links = list(set(class_links))
        unique_links.sort(key=lambda x: x[0])  # İsme göre sırala
        print(f"  ✅ {len(unique_links)} unique core class linki bulundu")
        return unique_links
    
    def scrape_class_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Class detay sayfasını çek - DÜZELTİLDİ (Classes Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        class_data = {
            "name": name,
            "hit_die": "d8",  # Default
            "primary_ability": [],
            "saving_throws": [],
            "class_skills": [],
            "skill_choices": 2,  # Default
            "proficiencies": {
                "armor": [],
                "weapons": [],
                "tools": [],
                "languages": []
            },
            "starting_equipment_options": [],
            "class_features": {},
            "spellcasting": None,  # Spellcaster class'lar için
            "source": url
        }
        
        # Tüm metni al
        text_content = main_content.get_text()
        
        # Paragrafları al (structured parsing için)
        paragraphs = main_content.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        
        # Hit Die - DÜZELTİLDİ (Classes Scraping - iyileştirildi)
        hit_die_patterns = [
            r'Hit Dice[:\s]+1d(\d+)\s+per',
            r'Hit Dice[:\s]+d(\d+)',
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Die[:\s]+(\d+)',
            r'(\d+)d(\d+)\s+Hit Die',
        ]
        
        # Önce paragraflarda ara
        for para_text in paragraph_texts:
            for pattern in hit_die_patterns:
                match = re.search(pattern, para_text, re.I)
                if match:
                    hit_die_val = match.group(1) if match.lastindex >= 1 else match.group(2)
                    class_data['hit_die'] = f"d{hit_die_val}"
                    break
            if class_data['hit_die'] != "d8":
                break
        
        # Paragraflarda bulunamazsa, tüm metinde ara
        if class_data['hit_die'] == "d8":
            for pattern in hit_die_patterns:
                match = re.search(pattern, text_content[:3000], re.I)
                if match:
                    hit_die_val = match.group(1) if match.lastindex >= 1 else (match.group(2) if match.lastindex >= 2 else None)
                    if hit_die_val:
                        class_data['hit_die'] = f"d{hit_die_val}"
                        break
        
        # Primary Ability - DÜZELTİLDİ (Classes Scraping)
        ability_names = {
            "strength": "Strength",
            "dexterity": "Dexterity",
            "constitution": "Constitution",
            "intelligence": "Intelligence",
            "wisdom": "Wisdom",
            "charisma": "Charisma"
        }
        
        primary_ability_patterns = [
            r'Primary Ability[:\s]+([A-Za-z, ]+?)(?:\n|$)',
            r'Primary Abilities?[:\s]+([A-Za-z, ]+?)(?:\n|$)',
        ]
        
        for pattern in primary_ability_patterns:
            match = re.search(pattern, text_content[:2000], re.I)
            if match:
                abilities_text = match.group(1).strip()
                # Virgülle veya "and" ile ayrılmış ability'leri parse et
                abilities = re.split(r'[,and]+', abilities_text, flags=re.I)
                for ab in abilities:
                    ab_clean = ab.strip().lower().capitalize()
                    if ab_clean in ability_names.values():
                        if ab_clean not in class_data['primary_ability']:
                            class_data['primary_ability'].append(ab_clean)
                break
        
        # Primary Ability - DÜZELTİLDİ (Classes Scraping - eğer paragrafta bulunamazsa, mevcut veriden tahmin et)
        # Genellikle spellcasting ability ile aynı veya class'a göre belirlenir
        if not class_data['primary_ability']:
            # Class name'e göre default primary ability
            class_name_lower = name.lower()
            if 'barbarian' in class_name_lower:
                class_data['primary_ability'] = ["Strength"]
            elif 'bard' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'cleric' in class_name_lower:
                class_data['primary_ability'] = ["Wisdom"]
            elif 'druid' in class_name_lower:
                class_data['primary_ability'] = ["Wisdom"]
            elif 'fighter' in class_name_lower:
                class_data['primary_ability'] = ["Strength", "Dexterity"]
            elif 'monk' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity", "Wisdom"]
            elif 'paladin' in class_name_lower:
                class_data['primary_ability'] = ["Strength", "Charisma"]
            elif 'ranger' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity", "Wisdom"]
            elif 'rogue' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity"]
            elif 'sorcerer' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'warlock' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'wizard' in class_name_lower:
                class_data['primary_ability'] = ["Intelligence"]
        
        # Proficiencies - DÜZELTİLDİ (Classes Scraping - iyileştirildi)
        # Proficiencies genellikle tek bir paragrafta: "Armor: ... Weapons: ... Tools: ... Saving Throws: ... Skills: ..."
        proficiencies_para = None
        for para_text in paragraph_texts:
            if 'Armor:' in para_text and ('Weapons:' in para_text or 'Saving Throws:' in para_text):
                proficiencies_para = para_text
                break
        
        # Skill names list (all D&D 5e skills)
        skill_names = [
            "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
            "History", "Insight", "Intimidation", "Investigation", "Medicine",
            "Nature", "Perception", "Performance", "Persuasion", "Religion",
            "Sleight of Hand", "Stealth", "Survival"
        ]
        
        if proficiencies_para:
            # Armor
            armor_match = re.search(r'Armor[:\s]+([^W]+?)(?:Weapons|Tools|Saving|Skills|$)', proficiencies_para, re.I)
            if armor_match:
                armor_text = armor_match.group(1).strip()
                if 'all armor' in armor_text.lower() or 'all' in armor_text.lower():
                    class_data['proficiencies']['armor'] = ["All armor", "Shields"]
                elif 'shields' in armor_text.lower():
                    armor_types = re.split(r'[,]', armor_text)
                    for armor in armor_types:
                        armor_clean = armor.strip()
                        if armor_clean:
                            if 'shield' in armor_clean.lower():
                                if "Shields" not in class_data['proficiencies']['armor']:
                                    class_data['proficiencies']['armor'].append("Shields")
                            elif armor_clean and armor_clean not in class_data['proficiencies']['armor']:
                                class_data['proficiencies']['armor'].append(armor_clean)
            
            # Weapons - DÜZELTİLDİ (iyileştirildi - pattern düzeltildi)
            # Format: "Weapons: Simple weapons, martial weaponsTools:..." (boşluk olmayabilir)
            weapon_patterns = [
                r'Weapons?[:\s]+([^T]+?)(?:Tools|Saving|Skills|$)',
                r'Weapons?[:\s]+([A-Za-z\s,]+?)(?:Tools|Saving|Skills|$)',
            ]
            
            for pattern in weapon_patterns:
                weapon_match = re.search(pattern, proficiencies_para, re.I)
                if weapon_match:
                    weapon_text = weapon_match.group(1).strip()
                    # "Simple weapons, martial weapons" veya "Simple weapons,martial weapons" gibi formatları parse et
                    if 'simple' in weapon_text.lower() and 'martial' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Simple weapons", "Martial weapons"]
                        break
                    elif 'simple' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Simple weapons"]
                        break
                    elif 'martial' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Martial weapons"]
                        break
                    else:
                        # Virgülle ayrılmış weapon'ları parse et
                        weapon_types = re.split(r'[,]', weapon_text)
                        for weapon in weapon_types:
                            weapon_clean = weapon.strip()
                            if weapon_clean and weapon_clean not in class_data['proficiencies']['weapons']:
                                class_data['proficiencies']['weapons'].append(weapon_clean)
                        if class_data['proficiencies']['weapons']:
                            break
            
            # Tools
            tool_match = re.search(r'Tools?[:\s]+([^S]+?)(?:Saving|Skills|$)', proficiencies_para, re.I)
            if tool_match:
                tool_text = tool_match.group(1).strip()
                if 'none' not in tool_text.lower():
                    tool_types = re.split(r'[,]', tool_text)
                    for tool in tool_types:
                        tool_clean = tool.strip()
                        if tool_clean and tool_clean not in class_data['proficiencies']['tools']:
                            class_data['proficiencies']['tools'].append(tool_clean)
            
            # Saving Throws - DÜZELTİLDİ (paragraftan parse - iyileştirildi)
            # Format: "Saving Throws:Strength,ConstitutionSkills:..." (boşluk olmayabilir, Skills ile bitiyor)
            saving_throws_patterns = [
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+)*?)(?:Skills|$)',
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+,\s*[A-Z][a-z]+)(?:Skills|$)',
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+,\s*[A-Z][a-z]+)',
            ]
            
            for pattern in saving_throws_patterns:
                saving_throws_match = re.search(pattern, proficiencies_para, re.I)
                if saving_throws_match:
                    throws_text = saving_throws_match.group(1).strip()
                    # Virgül veya boşlukla ayrılmış ability'leri parse et
                    throws = re.split(r'[,]+', throws_text)
                    for throw in throws:
                        throw_clean = throw.strip()
                        # Ability name'i tam olarak eşleştir (capitalize etmeden önce kontrol et)
                        for ability in ability_names.values():
                            if (ability.lower() == throw_clean.lower() or 
                                throw_clean.lower() == ability.lower()[:len(throw_clean)] or
                                ability.lower().startswith(throw_clean.lower())):
                                if ability not in class_data['saving_throws']:
                                    class_data['saving_throws'].append(ability)
                                break
                    if len(class_data['saving_throws']) >= 2:  # En az 2 saving throw olmalı
                        break
            
            # Class Skills - DÜZELTİLDİ (paragraftan parse - iyileştirildi)
            # Format: "Skills: Choose two skills fromAcrobatic..." veya "Skills: Choose from Acrobatics, Animal Handling..."
            skills_patterns = [
                r'Skills?[:\s]+Choose\s+(\d+)\s+skills?\s+from\s+([A-Z][a-z\s,]+?)(?:\n|$)',
                r'Skills?[:\s]+Choose\s+(\d+)\s+from\s+([A-Z][a-z\s,]+?)(?:\n|$)',
                r'Skills?[:\s]+([A-Z][a-z\s,]+?)(?:\n\n|\n[A-Z]|$)',
            ]
            
            for pattern in skills_patterns:
                skills_match = re.search(pattern, proficiencies_para, re.I | re.DOTALL)
                if skills_match:
                    # Skill count
                    if skills_match.lastindex >= 1 and skills_match.group(1).isdigit():
                        class_data['skill_choices'] = int(skills_match.group(1))
                    
                    # Skills text
                    skills_text = skills_match.group(2) if skills_match.lastindex >= 2 else skills_match.group(1)
                    if skills_text:
                        # Skills listesini parse et (virgül veya "and" ile ayrılmış)
                        skills_list = re.split(r'[,and]+', skills_text, flags=re.I)
                        for skill in skills_list:
                            skill_clean = skill.strip()
                            if skill_clean:
                                # Skill ismini eşleştir (tam isim veya kısmi)
                                for known_skill in skill_names:
                                    # Exact match veya substring match
                                    if (known_skill.lower() == skill_clean.lower() or 
                                        known_skill.lower().startswith(skill_clean.lower()) or
                                        skill_clean.lower() in known_skill.lower()):
                                        if known_skill not in class_data['class_skills']:
                                            class_data['class_skills'].append(known_skill)
                                        break
                    if class_data['class_skills']:
                        break
        
        # Class Features - DÜZELTİLDİ (Classes Scraping - Level bazlı tablo parsing)
        # Level table'ını bul (1-20 level features)
        tables = main_content.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 5:  # En az birkaç satır olmalı
                # İlk satır header olabilir
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                # "Level" veya "Features" kolonunu bul
                level_col = None
                features_col = None
                
                for i, header in enumerate(headers):
                    if 'level' in header.lower():
                        level_col = i
                    if 'feature' in header.lower() or 'class' in header.lower():
                        features_col = i
                
                # Eğer header yoksa, ilk kolon level, son kolon features olabilir
                if level_col is None:
                    level_col = 0
                if features_col is None:
                    features_col = len(headers) - 1
                
                # Satırları parse et
                for row in rows[1:]:  # İlk satır header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) > max(level_col, features_col):
                        level_text = cells[level_col].get_text(strip=True) if level_col < len(cells) else ""
                        features_text = cells[features_col].get_text(strip=True) if features_col < len(cells) else ""
                        
                        # Level numarasını çıkar (örn: "1st", "2nd", "3rd", "4th" -> 1, 2, 3, 4)
                        level_match = re.search(r'(\d+)', level_text)
                        if level_match and features_text:
                            level = int(level_match.group(1))
                            # Features'ları parse et (virgülle ayrılmış)
                            features = [f.strip() for f in re.split(r'[,]', features_text) if f.strip()]
                            
                            if level not in class_data['class_features']:
                                class_data['class_features'][str(level)] = {
                                    "features": features,
                                    "choices": {}
                                }
                            else:
                                # Mevcut features'lara ekle
                                existing_features = class_data['class_features'][str(level)].get("features", [])
                                for feature in features:
                                    if feature not in existing_features:
                                        existing_features.append(feature)
                                class_data['class_features'][str(level)]["features"] = existing_features
                
                # Tablo bulundu, diğer tablolara bakmaya gerek yok
                if class_data['class_features']:
                    break
        
        # Starting Equipment - DÜZELTİLDİ (Classes Scraping)
        # "You start with the following equipment" veya "Starting Equipment" bölümünü bul
        equipment_section_patterns = [
            r'You start with the following equipment[:\s]+(.+?)(?:\n\n|\n[A-Z]|Class Features|$)',
            r'Starting Equipment[:\s]+(.+?)(?:\n\n|\n[A-Z]|Class Features|$)',
        ]
        
        for pattern in equipment_section_patterns:
            equipment_match = re.search(pattern, text_content[:5000], re.I | re.DOTALL)
            if equipment_match:
                equipment_text = equipment_match.group(1).strip()
                # Equipment options'ları parse et (genellikle liste halinde)
                # Format: "(a) item1, item2 or (b) item3, item4"
                options = re.split(r'\([a-z]\)', equipment_text, flags=re.I)
                for option in options:
                    option_clean = option.strip()
                    if option_clean and len(option_clean) > 10:
                        # "or" ile ayrılmış alternatifleri bul
                        items = re.split(r'\s+or\s+', option_clean, flags=re.I)
                        equipment_list = []
                        for item_text in items:
                            # Virgülle ayrılmış item'ları parse et
                            item_parts = re.split(r'[,]', item_text)
                            for item_part in item_parts:
                                item_clean = item_part.strip()
                                if item_clean and len(item_clean) > 2:
                                    equipment_list.append(item_clean)
                        if equipment_list:
                            class_data['starting_equipment_options'].append(equipment_list)
                break
        
        # Spellcasting - eğer spellcaster ise - DÜZELTİLDİ (daha iyi detection)
        # Spellcaster class'lar: Wizard, Sorcerer, Warlock, Cleric, Druid, Bard, Paladin, Ranger, Artificer
        spellcaster_classes = ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard', 'paladin', 'ranger', 'artificer']
        class_name_lower = name.lower()
        
        # Önce class name'e göre kontrol et (en güvenilir)
        is_spellcaster = class_name_lower in spellcaster_classes
        
        # Eğer class name'e göre spellcaster değilse, content'te spellcasting section'ı ara
        if not is_spellcaster:
            spellcasting_indicators = [
                r'Spellcasting\s+Ability',  # "Spellcasting Ability" başlığı
                r'Spell\s+Slots\s+per\s+Level',  # Spell slots tablosu
                r'Spells\s+Known',  # Spells Known section
                r'Spells\s+Prepared',  # Spells Prepared section
                r'Cantrips?\s+Known',  # Cantrips section
            ]
            
            # Sadece başlık veya section başlığı olarak geçiyorsa spellcaster
            for indicator in spellcasting_indicators:
                if re.search(indicator, text_content[:10000], re.I):
                    is_spellcaster = True
                    break
        
        if is_spellcaster:
            # Spellcasting ability'yi belirle
            spellcasting_ability = "Intelligence"  # Default
            if class_name_lower in ['wizard', 'artificer']:
                spellcasting_ability = "Intelligence"
            elif class_name_lower in ['sorcerer', 'warlock', 'bard', 'paladin']:
                spellcasting_ability = "Charisma"
            elif class_name_lower in ['cleric', 'druid', 'ranger']:
                spellcasting_ability = "Wisdom"
            elif class_data['primary_ability']:
                spellcasting_ability = class_data['primary_ability'][0]
            
            class_data['spellcasting'] = {
                "spellcasting_ability": spellcasting_ability,
                "spell_save_dc": 8,  # Base (8 + proficiency + ability modifier)
                "spell_attack_bonus": 0  # Base (proficiency + ability modifier)
            }
        else:
            class_data['spellcasting'] = None
        
        return class_data
    
    def scrape_all_race_links(self) -> List[tuple]:
        """Tüm core race linklerini çek - DÜZELTİLDİ (Races Scraping)"""
        print("[*] Race linkleri cekiliyor...")
        
        # Core races listesi (bilinen D&D 5e core races)
        core_races = [
            ("Dragonborn", f"{self.BASE_URL}/races/dragonborn/"),
            ("Dwarf", f"{self.BASE_URL}/races/dwarf/"),
            ("Elf", f"{self.BASE_URL}/races/elf/"),
            ("Gnome", f"{self.BASE_URL}/races/gnome/"),
            ("Halfling", f"{self.BASE_URL}/races/halfling/"),
            ("Half-Elf", f"{self.BASE_URL}/races/half-elf/"),
            ("Half-Orc", f"{self.BASE_URL}/races/half-orc/"),
            ("Human", f"{self.BASE_URL}/races/human/"),
            ("Tiefling", f"{self.BASE_URL}/races/tiefling/"),
        ]
        
        print(f"  [OK] {len(core_races)} core race linki hazir")
        return core_races
    
    def scrape_race_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Race detay sayfasını çek - DÜZELTİLDİ (Races Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        race_data = {
            "name": name,
            "ability_score_increase": {},
            "speed": 30,  # Default
            "traits": [],
            "languages": [],
            "extra_languages": 0,
            "size": "Medium",  # Default
            "source": url
        }
        
        # Tüm metni al
        text_content = main_content.get_text()
        
        # Paragrafları al (structured parsing için)
        paragraphs = main_content.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        
        # Ability Score Increase - DÜZELTİLDİ (Races Scraping)
        ability_names = {
            "strength": "strength", "dexterity": "dexterity", "constitution": "constitution",
            "intelligence": "intelligence", "wisdom": "wisdom", "charisma": "charisma"
        }
        
        asi_patterns = [
            r'Ability\s+Score\s+Increase[:\s]+(.+?)(?:\n\n|\n[A-Z]|Age|Alignment|Size|Speed|Traits|Languages|$)',
            r'ASI[:\s]+(.+?)(?:\n|$)',
        ]
        
        # Önce paragraflarda ara
        for para_text in paragraph_texts:
            for pattern in asi_patterns:
                match = re.search(pattern, para_text, re.I | re.DOTALL)
                if match:
                    asi_text = match.group(1).strip()
                    
                    # "Your Strength score increases by 2, and your Charisma score increases by 1."
                    # veya "Your all ability scores increase by 1"
                    # veya "Strength +2, Charisma +1"
                    
                    # "all" kontrolü
                    if 'all' in asi_text.lower() or 'each' in asi_text.lower():
                        all_match = re.search(r'(\d+)', asi_text)
                        if all_match:
                            race_data['ability_score_increase'] = {"all": int(all_match.group(1))}
                            break
                    else:
                        # Individual ability increases
                        ability_increases = {}
                        # Pattern: "YourStrengthscore increases by 2" (boşluk olmayabilir!)
                        # veya "Strength score increases by 2" (boşluklu)
                        # veya "Strength +2"
                        
                        # Önce "YourXxxscore increases by Y" formatını parse et (boşluksuz)
                        no_space_pattern = r'Your(\w+)score\s+increases?\s+by\s+(\d+)'
                        matches = re.finditer(no_space_pattern, asi_text, re.I)
                        for m in matches:
                            ability_word = m.group(1).lower()
                            value = int(m.group(2))
                            
                            # Ability name'i normalize et
                            for known_ability, key in ability_names.items():
                                if known_ability in ability_word or ability_word in known_ability:
                                    ability_increases[key] = value
                                    break
                        
                        # Eğer boşluksuz pattern çalışmadıysa, boşluklu pattern'leri dene
                        if not ability_increases:
                            ability_patterns = [
                                r'(\w+)\s+score\s+increases?\s+by\s+(\d+)',
                                r'(\w+)\s+(\d+)',
                                r'\+(\d+)\s+(\w+)',
                            ]
                            
                            for ab_pattern in ability_patterns:
                                matches = re.finditer(ab_pattern, asi_text, re.I)
                                for m in matches:
                                    if len(m.groups()) >= 2:
                                        # İki format var: (ability, value) veya (value, ability)
                                        if m.group(1).isdigit():
                                            value = int(m.group(1))
                                            ability = m.group(2).lower()
                                        else:
                                            ability = m.group(1).lower()
                                            value = int(m.group(2))
                                        
                                        # Ability name'i normalize et
                                        for known_ability, key in ability_names.items():
                                            if known_ability in ability or ability in known_ability:
                                                ability_increases[key] = value
                                                break
                                if ability_increases:
                                    break
                        
                        if ability_increases:
                            race_data['ability_score_increase'] = ability_increases
                            break
                    
                    if race_data['ability_score_increase']:
                        break
            if race_data['ability_score_increase']:
                break
        
        # Speed - DÜZELTİLDİ (Races Scraping)
        speed_patterns = [
            r'Speed[:\s]+Your\s+base\s+walking\s+speed\s+is\s+(\d+)\s+feet?',
            r'Speed[:\s]+(\d+)\s+ft',
            r'Base\s+Speed[:\s]+(\d+)',
            r'(\d+)\s+feet?\s+speed',
        ]
        
        for para_text in paragraph_texts:
            for pattern in speed_patterns:
                match = re.search(pattern, para_text, re.I)
                if match:
                    speed_val = int(match.group(1))
                    race_data['speed'] = speed_val
                    break
            if race_data['speed'] != 30:
                break
        
        # Traits - DÜZELTİLDİ (Races Scraping - iyileştirildi)
        # Traits hem başlık (H3, H4) hem de paragraf içinde olabilir
        # Örnek: "Draconic Ancestry", "Breath Weapon", "Damage Resistance"
        known_trait_names = [
            'Draconic Ancestry', 'Breath Weapon', 'Damage Resistance',
            'Darkvision', 'Fey Ancestry', 'Trance', 'Keen Senses',
            'Lucky', 'Brave', 'Halfling Nimbleness', 'Naturally Stealthy',
            'Stonecunning', 'Dwarven Toughness', 'Dwarven Resilience',
            'Gnome Cunning', 'Artificer\'s Lore', 'Tinker',
            'Mask of the Wild', 'Fleet of Foot', 'Elf Weapon Training',
            'Extra Language', 'Versatility', 'Skill Versatility',
            'Menacing', 'Relentless Endurance', 'Savage Attacks',
            'Hellish Resistance', 'Infernal Legacy'
        ]
        
        # Önce başlıklardan trait'leri bul
        headings = main_content.find_all(['h3', 'h4'])
        skip_headings = ['traits', 'variants', 'subrace', 'subraces', 'race features', 'race feature']
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            heading_lower = heading_text.lower()
            
            # Genel başlıkları atla
            if heading_lower in skip_headings:
                continue
            
            # "Dragonborn Traits" gibi race-specific genel başlıkları atla
            if heading_lower == 'traits' or (heading_lower.endswith('traits') and len(heading_lower.split()) <= 2):
                continue
            
            # Bilinen trait isimleri ile eşleştir
            for trait_name in known_trait_names:
                if trait_name.lower() == heading_lower or heading_lower.startswith(trait_name.lower()):
                    if trait_name not in race_data['traits']:
                        race_data['traits'].append(trait_name)
                    break
        
        # Sonra paragraflardan trait'leri bul (örn: "Draconic Ancestry: You have...")
        for para_text in paragraph_texts:
            # Pattern: "Trait Name: Description" formatını ara
            for trait_name in known_trait_names:
                # Trait name ile başlayan paragrafları bul
                trait_pattern = r'^' + re.escape(trait_name) + r'[:\s]+'
                if re.search(trait_pattern, para_text, re.I):
                    if trait_name not in race_data['traits']:
                        race_data['traits'].append(trait_name)
        
        # Languages - DÜZELTİLDİ (Races Scraping - iyileştirildi)
        language_names = [
            "Common", "Elvish", "Dwarvish", "Gnomish", "Halfling",
            "Orc", "Draconic", "Infernal", "Celestial", "Abyssal",
            "Giant", "Primordial", "Deep Speech", "Undercommon"
        ]
        
        # Languages paragrafını bul
        for para_text in paragraph_texts:
            if 'language' not in para_text.lower():
                continue
            
            # "Languages: You can speak, read, and write Common and Draconic."
            # Pattern: "Common and Draconic" kısmını yakala
            # Önce tüm language names'leri ara
            found_languages = []
            for lang_name in language_names:
                # Language name'i paragrafta ara (kelime sınırları ile)
                lang_pattern = r'\b' + re.escape(lang_name) + r'\b'
                if re.search(lang_pattern, para_text, re.I):
                    found_languages.append(lang_name)
            
            if found_languages:
                race_data['languages'] = found_languages
                break
        
        # Extra Languages
        extra_lang_patterns = [
            r'Extra\s+Languages?[:\s]+(\d+)',
            r'one\s+additional\s+language',
            r'additional\s+language',
        ]
        
        for pattern in extra_lang_patterns:
            match = re.search(pattern, text_content[:3000], re.I)
            if match:
                if match.group(1) if match.lastindex >= 1 else None:
                    race_data['extra_languages'] = int(match.group(1))
                else:
                    race_data['extra_languages'] = 1
                break
        
        # Size - DÜZELTİLDİ (Races Scraping)
        size_patterns = [
            r'Size[:\s]+(.+?)(?:\n|$)',
            r'Yoursizeis\s+(\w+)',
            r'size\s+is\s+(\w+)',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text_content[:2000], re.I)
            if match:
                size_text = match.group(1).strip().capitalize()
                if size_text in ["Small", "Medium", "Large", "Tiny", "Huge"]:
                    race_data['size'] = size_text
                    break
        
        return race_data
    
    def scrape_all_races(self, max_races: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm core races'leri scrape et - DÜZELTİLDİ (Races Scraping)"""
        print("[*] Tum core races scrape ediliyor...")
        
        # Cache kontrolü
        cache_file = Path("data/cache/races_cache.json")
        races = {}
        cached_races = {}
        
        if cache_file.exists() and not force_refresh:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    if cached.get('races'):
                        cached_races = cached['races']
                        races.update(cached_races)
                        print(f"  [OK] {len(cached_races)} race cache'den yuklendi")
            except Exception as e:
                print(f"  [UYARI] Cache yuklenemedi: {e}")
        
        # Race linklerini çek
        race_links = self.scrape_all_race_links()
        
        if not race_links:
            print("  [UYARI] Race linkleri bulunamadi! Mevcut cache'i donduruyoruz.")
            return races
        
        print(f"\n[*] {len(race_links)} race bulundu")
        
        # Cache'de olmayan race'leri filtrele
        cached_names = set(cached_races.keys())
        new_race_links = [(name, url) for name, url in race_links if name not in cached_names]
        
        if new_race_links:
            print(f"\n[*] {len(new_race_links)} yeni race cekilecek ({len(cached_names)} zaten cache'de)")
        else:
            print("\n[OK] Tum race'ler zaten cache'de!")
            return races
        
        # Max races limiti
        if max_races:
            new_race_links = new_race_links[:max_races]
        
        total = len(new_race_links)
        print(f"\n[*] {total} race detayi cekiliyor...")
        print("  (Bu islem uzun surebilir, lutfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(new_race_links, 1):
            if i % 2 == 0:
                successful = len([k for k in races.keys() if k not in cached_names])
                print(f"  ... {i}/{total} race cekildi ({successful} basarili)")
            
            race_data = self.scrape_race_detail(url, name)
            if race_data and race_data.get('name'):
                races[race_data['name']] = race_data
            else:
                print(f"  [UYARI] {name} scrape edilemedi")
        
        print(f"\n[OK] {len([k for k in races.keys() if k not in cached_names])} yeni race basariyla cekildi")
        print(f"   Toplam: {len(races)} race (cache dahil)")
        
        # Cache'e kaydet
        cache_data = {
            'total': len(races),
            'races': races,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"[*] Cache'e kaydedildi: {cache_file}")
        
        return races
    
    def scrape_equipment_from_table(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Equipment tablosundan verileri çek - DÜZELTİLDİ (Equipment Scraping)"""
        soup = self._get(url)
        if not soup:
            return []
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            return []
        
        equipment_list = []
        
        # Tüm tabloları bul
        tables = main_content.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:  # En az header + 1 data row
                continue
            
            # Header row'u bul (ilk row)
            header_row = rows[0]
            header_cells = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            # Header'da hangi kolonlar var?
            # Olası kolonlar: name, cost, damage, range, weight, properties, armor_class, strength_requirement, stealth, etc.
            
            # Kolon indexlerini bul
            name_idx = None
            cost_idx = None
            damage_idx = None
            range_idx = None
            weight_idx = None
            properties_idx = None
            ac_idx = None  # Armor Class (armor için)
            strength_idx = None  # Strength requirement (armor için)
            stealth_idx = None  # Stealth disadvantage (armor için)
            
            for i, header in enumerate(header_cells):
                if 'name' in header or header == '':
                    name_idx = i
                elif 'cost' in header or 'price' in header:
                    cost_idx = i
                elif 'damage' in header:
                    damage_idx = i
                elif 'range' in header:
                    range_idx = i
                elif 'weight' in header:
                    weight_idx = i
                elif 'properties' in header or 'property' in header:
                    properties_idx = i
                elif 'armor' in header and 'class' in header or 'ac' in header:
                    ac_idx = i
                elif 'strength' in header:
                    strength_idx = i
                elif 'stealth' in header:
                    stealth_idx = i
            
            # Eğer name_idx yoksa, ilk kolonu name olarak kabul et
            if name_idx is None:
                name_idx = 0
            
            # Data row'larını parse et (ikinci row'dan başla)
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                if len(cell_texts) <= name_idx:
                    continue
                
                # Name'i al
                name = cell_texts[name_idx].strip()
                
                # Eğer name boşsa veya başlık satırıysa atla
                if not name or name.lower() in ['(simple)', '(martial)', 'simple melee weapons', 'martial melee weapons', 
                                                 'simple ranged weapons', 'martial ranged weapons']:
                    continue
                
                # Equipment item oluştur
                item = {
                    "name": name,
                    "type": category.lower(),  # "weapon", "armor", "gear", "tool"
                    "category": category,
                    "source": url
                }
                
                # Cost
                if cost_idx is not None and cost_idx < len(cell_texts):
                    cost_text = cell_texts[cost_idx].strip()
                    if cost_text and cost_text not in ['—', '–', '-', '']:
                        item["cost"] = cost_text
                
                # Damage (weapon için)
                if damage_idx is not None and damage_idx < len(cell_texts):
                    damage_text = cell_texts[damage_idx].strip()
                    if damage_text and damage_text not in ['—', '–', '-', '']:
                        item["damage"] = damage_text
                
                # Range (ranged weapon için)
                if range_idx is not None and range_idx < len(cell_texts):
                    range_text = cell_texts[range_idx].strip()
                    if range_text and range_text not in ['—', '–', '-', '']:
                        item["range"] = range_text
                
                # Weight
                if weight_idx is not None and weight_idx < len(cell_texts):
                    weight_text = cell_texts[weight_idx].strip()
                    if weight_text and weight_text not in ['—', '–', '-', '']:
                        # "4 lb." veya "4 lb" veya "4" formatını parse et
                        weight_match = re.search(r'(\d+(?:\.\d+)?)', weight_text)
                        if weight_match:
                            try:
                                item["weight"] = float(weight_match.group(1))
                            except ValueError:
                                item["weight"] = weight_text
                        else:
                            item["weight"] = weight_text
                
                # Properties (weapon için)
                if properties_idx is not None and properties_idx < len(cell_texts):
                    properties_text = cell_texts[properties_idx].strip()
                    if properties_text and properties_text not in ['—', '–', '-', '']:
                        # "finesse,light,thrown" veya "versatile(1d10)" formatını parse et
                        properties = [p.strip() for p in re.split(r'[,;]', properties_text) if p.strip()]
                        if properties:
                            item["properties"] = properties
                
                # Armor Class (armor için)
                if ac_idx is not None and ac_idx < len(cell_texts):
                    ac_text = cell_texts[ac_idx].strip()
                    if ac_text and ac_text not in ['—', '–', '-', '']:
                        # "11 + Dex modifier" veya "18" formatını parse et
                        item["armor_class"] = ac_text
                
                # Strength requirement (armor için)
                if strength_idx is not None and strength_idx < len(cell_texts):
                    strength_text = cell_texts[strength_idx].strip()
                    if strength_text and strength_text not in ['—', '–', '-', '']:
                        strength_match = re.search(r'(\d+)', strength_text)
                        if strength_match:
                            item["strength_requirement"] = int(strength_match.group(1))
                
                # Stealth disadvantage (armor için)
                if stealth_idx is not None and stealth_idx < len(cell_texts):
                    stealth_text = cell_texts[stealth_idx].strip()
                    if 'disadvantage' in stealth_text.lower():
                        item["stealth_disadvantage"] = True
                
                equipment_list.append(item)
        
        return equipment_list
    
    def scrape_all_equipment_links(self) -> List[tuple]:
        """Tüm equipment kategorilerinin linklerini çek - DÜZELTİLDİ (Equipment Scraping)"""
        print("[*] Equipment kategori linkleri cekiliyor...")
        
        # Equipment kategorileri
        equipment_categories = [
            ("Weapons", f"{self.BASE_URL}/equipment/weapons/"),
            ("Armor", f"{self.BASE_URL}/equipment/armor/"),
            ("Adventuring Gear", f"{self.BASE_URL}/equipment/adventuring-gear/"),
            ("Tools", f"{self.BASE_URL}/equipment/tools/"),
        ]
        
        print(f"  [OK] {len(equipment_categories)} equipment kategori linki hazir")
        return equipment_categories
    
    def scrape_all_equipment(self, max_items: Optional[int] = None, force_refresh: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Tüm equipment'leri çek - DÜZELTİLDİ (Equipment Scraping)"""
        print("=" * 70)
        print("5ESRD.COM EQUIPMENT ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü
        cache_file = Path("data/cache/equipment_cache.json")
        equipment_data = {}
        cached_equipment = {}
        
        if not force_refresh and cache_file.exists():
            print(f"[*] Cache dosyasi bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('equipment'):
                    cached_equipment = cached['equipment']
                    equipment_data.update(cached_equipment)
                    print(f"  [OK] {sum(len(items) for items in cached_equipment.values())} equipment item cache'den yuklendi")
        
        # Equipment kategori linklerini çek
        equipment_links = self.scrape_all_equipment_links()
        
        if not equipment_links:
            print("  [UYARI] Equipment kategori linkleri bulunamadi! Mevcut cache'i donduruyoruz.")
            return cached_equipment
        
        # Her kategori için equipment'leri çek
        for category_name, url in equipment_links:
            if category_name in equipment_data and not force_refresh:
                print(f"  [ATLA] {category_name} zaten cache'de, atlaniyor...")
                continue
            
            print(f"\n[*] {category_name} cekiliyor...")
            print(f"   URL: {url}")
            
            items = self.scrape_equipment_from_table(url, category_name)
            
            if items:
                equipment_data[category_name] = items
                print(f"   [OK] {len(items)} {category_name.lower()} item cekildi")
            else:
                print(f"   [UYARI] {category_name} icin item bulunamadi")
        
        # Cache'e kaydet
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({"equipment": equipment_data}, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Equipment data '{cache_file}' dosyasina kaydedildi!")
        print(f"[*] Toplam {sum(len(items) for items in equipment_data.values())} equipment item cekildi.")
        
        return equipment_data


"""5esrd.com D&D 5e scraper"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any


class Dnd5eSrdScraper:
    """5esrd.com'dan D&D 5e verilerini çeken scraper"""
    
    BASE_URL = "https://www.5esrd.com"
    
    def __init__(self, rate_limit: float = 1.5):
        """
        Args:
            rate_limit: İstekler arası bekleme süresi (saniye)
        """
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """HTTP GET isteği yap ve BeautifulSoup döndür"""
        for attempt in range(retries):
            try:
                time.sleep(self.rate_limit)
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')
                elif response.status_code == 404:
                    return None
                else:
                    print(f"  ⚠️  Status {response.status_code} for {url}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"  ⚠️  Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None
    
    def scrape_all_spell_links(self) -> List[tuple]:
        """Tüm spell linklerini çek"""
        print("🔍 Spell linkleri çekiliyor...")
        url = f"{self.BASE_URL}/database/spell/"
        
        soup = self._get(url)
        if not soup:
            print("❌ Spell database sayfası bulunamadı!")
            return []
        
        spell_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Spell linklerini bul
            if '/spell/' in href.lower() and text and len(text) < 100:
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                else:
                    full_url = urljoin(url, href)
                spell_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_links = list(set(spell_links))
        print(f"  ✅ {len(unique_links)} unique spell linki bulundu")
        return unique_links
    
    def scrape_spell_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Spell detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        spell_data = {
            "name": name,
            "level": None,
            "school": None,
            "casting_time": None,
            "range": None,
            "components": None,
            "duration": None,
            "description": "",
            "classes": [],
            "ritual": False,
            "concentration": False,
            "source": url
        }
        
        # Tüm paragrafları al
        paragraphs = main_content.find_all('p')
        
        # Metni al
        text_content = main_content.get_text()
        
        # İlk paragrafı al (genellikle level ve school burada)
        first_p = paragraphs[0] if paragraphs else None
        first_para_text = first_p.get_text(strip=True) if first_p else ""
        
        # Level ve School - DÜZELTİLDİ
        # Format: "3rd-levelevocation" veya "Conjurationcantrip" (boşluk yok!)
        # Önce ilk paragraftan bulmaya çalış
        level_school_patterns = [
            r'(\d+)(st|nd|rd|th)[\s-]*level([a-z]+)',  # "3rd-levelevocation"
            r'([a-z]+)cantrip',  # "Conjurationcantrip"
            r'(\d+)(st|nd|rd|th)[\s-]*level\s+([a-z]+)',  # "3rd-level evocation" (boşluklu)
            r'cantrip\s+([a-z]+)',  # "cantrip evocation" (boşluklu)
        ]
        
        found = False
        for pattern in level_school_patterns:
            match = re.search(pattern, first_para_text, re.I)
            if not match:
                match = re.search(pattern, text_content[:500], re.I)  # İlk 500 karakterde ara
            
            if match:
                if 'cantrip' in pattern.lower():
                    spell_data['level'] = 0
                    spell_data['school'] = match.group(1).capitalize() if match.lastindex >= 1 else None
                    found = True
                else:
                    level_num = match.group(1)
                    school = match.group(match.lastindex)  # Son grup school
                    spell_data['level'] = int(level_num)
                    spell_data['school'] = school.capitalize()
                    found = True
                break
        
        # Eğer bulunamadıysa, text'ten daha geniş arama yap
        if not found:
            # "3rd level" veya "1st level" gibi formatları ara
            level_match = re.search(r'(\d+)(st|nd|rd|th)\s*level', text_content, re.I)
            if level_match:
                spell_data['level'] = int(level_match.group(1))
                # School'u bul
                school_match = re.search(r'(?:level|spell)[\s-]+([a-z]+)', text_content[level_match.end():level_match.end()+50], re.I)
                if school_match:
                    spell_data['school'] = school_match.group(1).capitalize()
        
        # Casting Time, Range, Components, Duration - DÜZELTİLDİ (V2)
        # Format: "Casting Time:1 actionRange:60 feetComponents:V, SDuration:Instantaneous"
        # İkinci paragraf genellikle bu bilgileri içerir, ama bazı spell'lerde description'da olabilir
        
        # Önce ikinci paragraftan bulmaya çalış
        second_p = paragraphs[1] if len(paragraphs) > 1 else None
        stats_text = second_p.get_text(strip=True) if second_p else ""
        
        # Eğer ikinci paragrafta yeterli bilgi yoksa, text'in başından ara
        if not stats_text or 'Casting Time' not in stats_text:
            stats_match = re.search(r'Casting\s+Time[:\s]+.+?(?=You |A |Target|$)', text_content[:2000], re.I | re.DOTALL)
            if stats_match:
                stats_text = stats_match.group(0)
        
        # Eğer hala bulunamadıysa, description'dan da çıkarmaya çalış
        if not stats_text or len(stats_text) < 30:
            # Description paragraflarından ara
            for p in paragraphs[2:5] if len(paragraphs) > 2 else []:
                p_text = p.get_text(strip=True)
                if 'Casting Time' in p_text or 'Range:' in p_text or 'Components:' in p_text:
                    stats_text = p_text
                    break
        
        if stats_text:
            # Casting Time - Daha esnek regex
            if not spell_data.get('casting_time'):
                ct_patterns = [
                    r'Casting\s+Time[:\s]+([^R]+?)(?:Range|Components|Duration|$|You |A |Target)',
                    r'Casting\s+Time[:\s]+([^R]+?)(?=Range|$)',
                ]
                for pattern in ct_patterns:
                    ct_match = re.search(pattern, stats_text, re.I)
                    if ct_match:
                        casting_time = ct_match.group(1).strip()
                        spell_data['casting_time'] = re.sub(r'\s+', ' ', casting_time)
                        break
            
            # Range - DÜZELTİLDİ (case-insensitive ve daha akıllı)
            if not spell_data.get('range'):
                # "Range:" veya "Range :" sonrası, "Components" öncesi veya satır sonu
                range_patterns = [
                    r'Range[:\s]+([^C\n]+?)(?:Components|Duration|$)',  # Components veya Duration'a kadar
                    r'Range[:\s]+([a-zA-Z0-9\s\'-]+?)(?=Components|Duration|$)',  # Kelimeler ve boşluklar
                ]
                for pattern in range_patterns:
                    range_match = re.search(pattern, stats_text, re.I)
                    if range_match:
                        range_text = range_match.group(1).strip()
                        # "touch" gibi küçük harfli değerleri düzelt
                        range_text = range_text.capitalize() if range_text.islower() else range_text
                        spell_data['range'] = re.sub(r'\s+', ' ', range_text)
                        break
            
            # Components - DÜZELTİLDİ V4 (position-based, parantez desteği)
            if not spell_data.get('components'):
                # Components başlangıcını bul
                comp_start_match = re.search(r'Components[:\s]+', stats_text, re.I)
                if comp_start_match:
                    start_pos = comp_start_match.end()
                    
                    # Duration'un başlangıcını bul
                    dur_start_match = re.search(r'Duration[:\s]+', stats_text[start_pos:], re.I)
                    if dur_start_match:
                        end_pos = start_pos + dur_start_match.start()
                    else:
                        # Duration yoksa, "You" veya satır sonuna kadar
                        you_match = re.search(r'\bYou\s+', stats_text[start_pos:], re.I)
                        if you_match:
                            end_pos = start_pos + you_match.start()
                        else:
                            end_pos = start_pos + 200  # Fallback: 200 karakter
                    
                    components_raw = stats_text[start_pos:end_pos].strip()
                    
                    # Parantez kontrolü - açık parantez varsa kapatmayı bul
                    open_paren_pos = components_raw.find('(')
                    if open_paren_pos != -1:
                        # Kapanış parantezini bul
                        close_paren_pos = components_raw.find(')', open_paren_pos)
                        if close_paren_pos == -1:
                            # Kapanış parantezi components_raw içinde yok, stats_text'ten devam et
                            remaining_text = stats_text[end_pos:end_pos + 300]
                            close_in_remaining = remaining_text.find(')')
                            if close_in_remaining != -1:
                                # Kapanış parantezi bulundu, components'i genişlet
                                components_raw = stats_text[start_pos:end_pos + close_in_remaining + 1].strip()
                    
                    components = re.sub(r'\s+', ' ', components_raw)
                    spell_data['components'] = components
                    
                    # V, S, M kontrolü
                    if 'V' in components.upper():
                        spell_data['verbal'] = True
                    if 'S' in components.upper():
                        spell_data['somatic'] = True
                    if 'M' in components.upper():
                        spell_data['material'] = True
                        # Material component açıklamasını çıkar
                        m_match = re.search(r'M\s*\(([^)]+)\)', components, re.I)
                        if m_match:
                            spell_data['material_component'] = m_match.group(1).strip()
            
            # Duration - DÜZELTİLDİ V3 (daha akıllı temizleme)
            if not spell_data.get('duration'):
                # Duration başlangıcını bul
                dur_start_match = re.search(r'Duration[:\s]+', stats_text, re.I)
                if dur_start_match:
                    start_pos = dur_start_match.end()
                    # "You", "Your", "A ", "At Higher", "This spell" veya satır sonuna kadar
                    dur_end_patterns = [
                        r'(?:You |Your |A [a-z]+|At Higher|This spell|$)',
                        r'(?=You |Your |At Higher|This spell|$)',
                    ]
                    
                    for end_pattern in dur_end_patterns:
                        dur_end_match = re.search(end_pattern, stats_text[start_pos:], re.I)
                        if dur_end_match:
                            duration_raw = stats_text[start_pos:start_pos + dur_end_match.start()].strip()
                            
                            # "You" ile başlayan cümleleri temizle
                            duration = re.sub(r'\s+You\s+.*$', '', duration_raw, flags=re.DOTALL)
                            duration = re.sub(r'\s+Your\s+.*$', '', duration, flags=re.DOTALL)
                            duration = re.sub(r'\s+A\s+[a-z]+\s+.*$', '', duration, flags=re.DOTALL)
                            duration = duration.strip()
                            
                            # Çok uzun olmamalı (200 karakter limit)
                            if duration and len(duration) <= 200:
                                spell_data['duration'] = re.sub(r'\s+', ' ', duration)
                                if 'concentration' in duration.lower():
                                    spell_data['concentration'] = True
                                if 'ritual' in duration.lower():
                                    spell_data['ritual'] = True
                                break
        
        # Eğer hala eksik veriler varsa, description'dan çıkarmaya çalış
        # (Bazı spell'lerde bu bilgiler description'ın başında olabilir)
        if not spell_data.get('casting_time') or not spell_data.get('range') or not spell_data.get('components') or not spell_data.get('duration'):
            # Tüm metni tekrar tara
            full_text_search = text_content[:3000]  # İlk 3000 karakter yeterli
            
            if not spell_data.get('casting_time'):
                ct_match = re.search(r'Casting\s+Time[:\s]+([^R\n]+?)(?:Range|$|You|A |Target)', full_text_search, re.I)
                if ct_match:
                    spell_data['casting_time'] = ct_match.group(1).strip()
            
            if not spell_data.get('range'):
                range_match = re.search(r'Range[:\s]+([^C\n]+?)(?:Components|Duration|$|You|A |Target)', full_text_search, re.I)
                if range_match:
                    spell_data['range'] = range_match.group(1).strip()
            
            if not spell_data.get('components'):
                comp_match = re.search(r'Components[:\s]+([^D\n]+?(?:\([^)]+\))?[^D]*?)(?:Duration|$|You|A |Target|Concentration)', full_text_search, re.I)
                if comp_match:
                    components = comp_match.group(1).strip()
                    # Parantez kapatılmamışsa düzelt
                    if components.count('(') > components.count(')'):
                        remaining = full_text_search[comp_match.end():comp_match.end()+100]
                        close_match = re.search(r'([^)]+)\)', remaining, re.I)
                        if close_match:
                            components += close_match.group(0)
                    spell_data['components'] = re.sub(r'\s+', ' ', components)
                    # V, S, M kontrolü
                    if 'V' in components.upper():
                        spell_data['verbal'] = True
                    if 'S' in components.upper():
                        spell_data['somatic'] = True
                    if 'M' in components.upper():
                        spell_data['material'] = True
                        m_match = re.search(r'M\s*\(([^)]+)\)', components, re.I)
                        if m_match:
                            spell_data['material_component'] = m_match.group(1).strip()
            
            if not spell_data.get('duration'):
                dur_match = re.search(r'Duration[:\s]+([^Y\n]+?)(?:You |A |Target|At Higher|This spell|$)', full_text_search, re.I | re.DOTALL)
                if dur_match:
                    duration = dur_match.group(1).strip()
                    # "You" ile başlayan cümleleri temizle
                    duration = re.sub(r'\s*You\s+.*$', '', duration, flags=re.DOTALL)
                    duration = re.sub(r'\s*Your\s+.*$', '', duration, flags=re.DOTALL)
                    duration = re.sub(r'\s*A\s+[a-z]+.*$', '', duration, flags=re.DOTALL)
                    duration = duration.strip()
                    if duration and len(duration) < 200:
                        spell_data['duration'] = re.sub(r'\s+', ' ', duration)
                        if 'concentration' in duration.lower():
                            spell_data['concentration'] = True
                        if 'ritual' in duration.lower():
                            spell_data['ritual'] = True
        
        # Description - 3. paragraftan itibaren al (ilk iki paragraf level/school ve stats)
        description_parts = []
        for i, p in enumerate(paragraphs):
            if i < 2:  # İlk iki paragrafı atla
                continue
            text = p.get_text(strip=True)
            if (len(text) > 30 and 
                'Green Ronin' not in text and 
                'OGN' not in text and
                'Open Gaming' not in text and
                'Copyright' not in text and
                'Join Our Discord' not in text and
                'Subscribe' not in text and
                'Casting Time' not in text and  # Stats'ı description'dan çıkar
                'Range:' not in text and
                'Components:' not in text and
                'Duration:' not in text):
                description_parts.append(text)
        
        if description_parts:
            spell_data['description'] = '\n\n'.join(description_parts)
        
        # Classes - Spell lists sayfalarından bulunmalı, şimdilik boş bırak
        # (Daha sonra spell lists'ten çekilecek)
        spell_data['classes'] = []
        
        return spell_data
    
    def scrape_all_spells(self, max_spells: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm spell'leri çek"""
        print("=" * 70)
        print("5ESRD.COM SPELLS ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü - DÜZELTİLDİ (cache'deki spell'leri kullan, eksikleri çek)
        cache_file = Path("data/cache/spells_cache.json")
        spells = {}
        cached_spells = {}
        
        if not force_refresh and cache_file.exists():
            print(f"📦 Cache dosyası bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('spells'):
                    cached_spells = cached['spells']
                    spells.update(cached_spells)
                    print(f"  ✅ {len(cached_spells)} spell cache'den yüklendi")
        
        # Spell linklerini çek
        spell_links = self.scrape_all_spell_links()
        
        # Eğer max_spells varsa, sadece ilk N spell'i al
        if max_spells:
            spell_links = spell_links[:max_spells]
            print(f"  ⚠️  İlk {max_spells} spell çekilecek (test modu)")
        else:
            # Cache'de olmayan spell'leri filtrele - DÜZELTİLDİ
            cached_names = set(cached_spells.keys())
            spell_links = [(name, url) for name, url in spell_links if name not in cached_names]
            if spell_links:
                print(f"  🔄 {len(spell_links)} yeni spell çekilecek ({len(cached_names)} zaten cache'de)")
            else:
                print("  ✅ Tüm spell'ler zaten cache'de!")
                return cached_spells
        
        total = len(spell_links)
        
        print(f"\n📖 {total} spell detayı çekiliyor...")
        print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(spell_links, 1):
            if i % 10 == 0:
                successful = len(spells)
                print(f"  ... {i}/{total} spell çekildi ({successful} başarılı)")
                # Her 50 spell'de bir cache'e kaydet (ilerlemeyi koru)
                if i % 50 == 0:
                    all_spells_temp = {**cached_spells, **spells}
                    cache_data = {
                        'total': len(all_spells_temp),
                        'spells': all_spells_temp,
                        'source': '5esrd.com',
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'progress': f'{i}/{total}'
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 İlerleme kaydedildi: {successful} yeni spell, toplam {len(all_spells_temp)}")
            
            spell_data = self.scrape_spell_detail(url, name)
            if spell_data and spell_data.get('name'):
                spells[spell_data['name']] = spell_data
        
        print(f"\n✅ {len(spells)} yeni spell başarıyla çekildi")
        print(f"   Toplam: {len(spells) + len(cached_spells)} spell (cache dahil)")
        
        # Final cache'e kaydet
        all_spells = {**cached_spells, **spells}
        cache_data = {
            'total': len(all_spells),
            'spells': all_spells,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache'e kaydedildi: {cache_file}")
        
        return all_spells
    
    def scrape_all_feat_links(self) -> List[tuple]:
        """Tüm feat linklerini çek - DÜZELTİLDİ (Feats Scraping)"""
        print("🔍 Feat linkleri çekiliyor...")
        
        # 5esrd.com'da feat'ler /database/feats/ altında
        url = f"{self.BASE_URL}/database/feats"
        
        soup = self._get(url)
        if not soup:
            print("❌ Feats database sayfası bulunamadı!")
            return []
        
        feat_links = []
        
        # Feat linklerini bul - /database/feats/ içeren ve anlamlı text'i olan linkler
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # /database/feats/ içeren ve feat detay sayfası olan linkler
            # Format: /database/feats/[feat-name]/
            if '/database/feats/' in href.lower() and text and len(text) < 100 and text != 'Feats':
                # List/index sayfalarını filtrele
                if any(skip in href.lower() for skip in ['/feats', '/database/feats', 'list', 'index', 'category']):
                    # Eğer /database/feats/ ile bitmiyorsa ve bir feat adı içeriyorsa (kısa çizgi ile ayrılmış)
                    if not href.lower().endswith('/feats/') and not href.lower().endswith('/feats'):
                        # Feat detay sayfası gibi görünüyor (örn: /database/feats/a-taste-of-power/)
                        pass  # Devam et
                    else:
                        continue  # List sayfası, atla
                
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(url, href)
                
                # Feat detay sayfası kontrolü - URL'de feat adı olmalı (kısa çizgi ile ayrılmış kelimeler)
                if '/database/feats/' in full_url.lower() and full_url.lower().count('/') >= 4:
                    # Örnek: /database/feats/a-taste-of-power/ -> 4+ slash var
                    feat_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_links = list(set(feat_links))
        print(f"  ✅ {len(unique_links)} unique feat linki bulundu")
        return unique_links
    
    def scrape_feat_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Feat detay sayfasını çek - DÜZELTİLDİ (Feats Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        feat_data = {
            "name": name,
            "prerequisite": None,
            "description": "",
            "source": url
        }
        
        # Tüm paragrafları al
        paragraphs = main_content.find_all('p')
        
        # Metni al
        text_content = main_content.get_text()
        
        # Prerequisite - DÜZELTİLDİ (Feats Scraping)
        # Format: "Prerequisite: Strength 13 or higher" veya "Prerequisite: None"
        prereq_patterns = [
            r'Prerequisite[:\s]+([^D\n]+?)(?:Description|$|You |A |At Higher|This feat|Benefits|Special)',
            r'Prerequisites?[:\s]+([^D\n]+?)(?:Description|$|You |A |Benefits|Special)',
            r'Prerequisite[:\s]+(.+?)(?:\n\n|$|Description)',
        ]
        
        for pattern in prereq_patterns:
            prereq_match = re.search(pattern, text_content[:1000], re.I)
            if prereq_match:
                prerequisite = prereq_match.group(1).strip()
                # "None" veya boş değilse kaydet
                if prerequisite and prerequisite.lower() not in ['none', 'none.', '']:
                    feat_data['prerequisite'] = prerequisite
                break
        
        # Description - DÜZELTİLDİ V2 (Feats Scraping - iyileştirildi)
        description_parts = []
        
        # İlk olarak, "Benefit(s):" veya "Description:" gibi başlıkları ara
        benefit_pattern = re.search(r'(?:Benefit|Benefits|Description)[:\s]+(.+?)(?:\n\n|$)', text_content, re.I | re.DOTALL)
        if benefit_pattern:
            description_text = benefit_pattern.group(1).strip()
            # İlk 2000 karakteri al
            description_text = description_text[:2000]
            description_parts.append(description_text)
        else:
            # Benefit bulunamadıysa, paragrafları kontrol et
            start_collecting = False
            found_prerequisite = False
            
            for i, p in enumerate(paragraphs):
                text = p.get_text(strip=True)
                
                # Prerequisite paragrafını işaretle
                if 'prerequisite' in text.lower() and i < 5:
                    found_prerequisite = True
                    start_collecting = True
                    continue
                
                # Description/Benefit başlığı varsa, ondan sonraki paragrafları al
                if 'benefit' in text.lower() or 'description' in text.lower():
                    if i < 10:  # İlk 10 paragrafta olmalı
                        start_collecting = True
                        # Benefit text'ini de ekle
                        if len(text) > 50:
                            description_parts.append(text)
                        continue
                
                # Copyright, footer metinlerini atla
                skip_texts = [
                    'Green Ronin', 'OGN', 'Open Gaming', 'Copyright',
                    'Join Our Discord', 'Subscribe', 'license attribution',
                    'see the full license', 'This is not the complete license'
                ]
                
                should_skip = any(skip in text for skip in skip_texts)
                
                if (len(text) > 20 and not should_skip and
                    'Prerequisite' not in text and 'Prerequisites' not in text):
                    
                    # Prerequisite'ten sonra veya 3. paragraftan itibaren topla
                    if start_collecting or (found_prerequisite and i > 1) or (not found_prerequisite and i >= 1):
                        description_parts.append(text)
        
        # Description'ı temizle ve birleştir
        if description_parts:
            # Lisans metinlerini temizle
            cleaned_parts = []
            for part in description_parts:
                # Lisans metinlerini filtrele
                if any(skip in part for skip in ['license attribution', 'see the full license', 'This is not the complete']):
                    continue
                # Çok kısa paragrafları atla (genellikle navigation/header)
                if len(part) > 20:
                    cleaned_parts.append(part)
            
            if cleaned_parts:
                feat_data['description'] = '\n\n'.join(cleaned_parts[:10])  # En fazla 10 paragraf
        
        return feat_data
    
    def scrape_all_feats(self, max_feats: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm feat'leri çek - DÜZELTİLDİ (Feats Scraping)"""
        print("=" * 70)
        print("5ESRD.COM FEATS ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü
        cache_file = Path("data/cache/feats_cache.json")
        feats = {}
        cached_feats = {}
        
        if not force_refresh and cache_file.exists():
            print(f"📦 Cache dosyası bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('feats'):
                    cached_feats = cached['feats']
                    feats.update(cached_feats)
                    print(f"  ✅ {len(cached_feats)} feat cache'den yüklendi")
        
        # Feat linklerini çek
        feat_links = self.scrape_all_feat_links()
        
        if not feat_links:
            print("  ⚠️  Feat linkleri bulunamadı! Mevcut cache'i döndürüyoruz.")
            return cached_feats
        
        # Eğer max_feats varsa, sadece ilk N feat'i al
        if max_feats:
            feat_links = feat_links[:max_feats]
            print(f"  ⚠️  İlk {max_feats} feat çekilecek (test modu)")
        else:
            # Cache'de olmayan feat'leri filtrele
            cached_names = set(cached_feats.keys())
            feat_links = [(name, url) for name, url in feat_links if name not in cached_names]
            if feat_links:
                print(f"  🔄 {len(feat_links)} yeni feat çekilecek ({len(cached_names)} zaten cache'de)")
            else:
                print("  ✅ Tüm feat'ler zaten cache'de!")
                return cached_feats
        
        total = len(feat_links)
        
        print(f"\n📖 {total} feat detayı çekiliyor...")
        print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(feat_links, 1):
            if i % 10 == 0:
                successful = len(feats)
                print(f"  ... {i}/{total} feat çekildi ({successful} başarılı)")
                # Her 50 feat'te bir cache'e kaydet (ilerlemeyi koru)
                if i % 50 == 0:
                    all_feats_temp = {**cached_feats, **feats}
                    cache_data = {
                        'total': len(all_feats_temp),
                        'feats': all_feats_temp,
                        'source': '5esrd.com',
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'progress': f'{i}/{total}'
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 İlerleme kaydedildi: {successful} yeni feat, toplam {len(all_feats_temp)}")
            
            feat_data = self.scrape_feat_detail(url, name)
            if feat_data and feat_data.get('name'):
                feats[feat_data['name']] = feat_data
        
        print(f"\n✅ {len(feats)} yeni feat başarıyla çekildi")
        print(f"   Toplam: {len(feats) + len(cached_feats)} feat (cache dahil)")
        
        # Final cache'e kaydet
        all_feats = {**cached_feats, **feats}
        cache_data = {
            'total': len(all_feats),
            'feats': all_feats,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache'e kaydedildi: {cache_file}")
        
        return all_feats
    
    def scrape_all_class_links(self) -> List[tuple]:
        """Tüm class linklerini çek - DÜZELTİLDİ (Classes Scraping)"""
        print("🔍 Class linkleri çekiliyor...")
        url = f"{self.BASE_URL}/classes/"
        
        soup = self._get(url)
        if not soup:
            print("❌ Classes sayfası bulunamadı!")
            return []
        
        class_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Core classes için: /database/class/class-name/ pattern'ini kullan
            if '/database/class/' in href.lower() and text and len(text) < 50 and len(text) > 1:
                # 3rd party veya prestige class'ları filtrele
                if '3rd-party' not in href.lower() and 'prestige' not in href.lower():
                    if href.endswith('/'):
                        if href.startswith('/'):
                            full_url = self.BASE_URL + href
                        else:
                            full_url = urljoin(url, href)
                        class_links.append((text, full_url))
        
        # Tekrar edenleri kaldır ve sırala
        unique_links = list(set(class_links))
        unique_links.sort(key=lambda x: x[0])  # İsme göre sırala
        print(f"  ✅ {len(unique_links)} unique core class linki bulundu")
        return unique_links
    
    def scrape_class_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Class detay sayfasını çek - DÜZELTİLDİ (Classes Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        class_data = {
            "name": name,
            "hit_die": "d8",  # Default
            "primary_ability": [],
            "saving_throws": [],
            "class_skills": [],
            "skill_choices": 2,  # Default
            "proficiencies": {
                "armor": [],
                "weapons": [],
                "tools": [],
                "languages": []
            },
            "starting_equipment_options": [],
            "class_features": {},
            "spellcasting": None,  # Spellcaster class'lar için
            "source": url
        }
        
        # Tüm metni al
        text_content = main_content.get_text()
        
        # Paragrafları al (structured parsing için)
        paragraphs = main_content.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        
        # Hit Die - DÜZELTİLDİ (Classes Scraping - iyileştirildi)
        hit_die_patterns = [
            r'Hit Dice[:\s]+1d(\d+)\s+per',
            r'Hit Dice[:\s]+d(\d+)',
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Die[:\s]+(\d+)',
            r'(\d+)d(\d+)\s+Hit Die',
        ]
        
        # Önce paragraflarda ara
        for para_text in paragraph_texts:
            for pattern in hit_die_patterns:
                match = re.search(pattern, para_text, re.I)
                if match:
                    hit_die_val = match.group(1) if match.lastindex >= 1 else match.group(2)
                    class_data['hit_die'] = f"d{hit_die_val}"
                    break
            if class_data['hit_die'] != "d8":
                break
        
        # Paragraflarda bulunamazsa, tüm metinde ara
        if class_data['hit_die'] == "d8":
            for pattern in hit_die_patterns:
                match = re.search(pattern, text_content[:3000], re.I)
                if match:
                    hit_die_val = match.group(1) if match.lastindex >= 1 else (match.group(2) if match.lastindex >= 2 else None)
                    if hit_die_val:
                        class_data['hit_die'] = f"d{hit_die_val}"
                        break
        
        # Primary Ability - DÜZELTİLDİ (Classes Scraping)
        ability_names = {
            "strength": "Strength",
            "dexterity": "Dexterity",
            "constitution": "Constitution",
            "intelligence": "Intelligence",
            "wisdom": "Wisdom",
            "charisma": "Charisma"
        }
        
        primary_ability_patterns = [
            r'Primary Ability[:\s]+([A-Za-z, ]+?)(?:\n|$)',
            r'Primary Abilities?[:\s]+([A-Za-z, ]+?)(?:\n|$)',
        ]
        
        for pattern in primary_ability_patterns:
            match = re.search(pattern, text_content[:2000], re.I)
            if match:
                abilities_text = match.group(1).strip()
                # Virgülle veya "and" ile ayrılmış ability'leri parse et
                abilities = re.split(r'[,and]+', abilities_text, flags=re.I)
                for ab in abilities:
                    ab_clean = ab.strip().lower().capitalize()
                    if ab_clean in ability_names.values():
                        if ab_clean not in class_data['primary_ability']:
                            class_data['primary_ability'].append(ab_clean)
                break
        
        # Primary Ability - DÜZELTİLDİ (Classes Scraping - eğer paragrafta bulunamazsa, mevcut veriden tahmin et)
        # Genellikle spellcasting ability ile aynı veya class'a göre belirlenir
        if not class_data['primary_ability']:
            # Class name'e göre default primary ability
            class_name_lower = name.lower()
            if 'barbarian' in class_name_lower:
                class_data['primary_ability'] = ["Strength"]
            elif 'bard' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'cleric' in class_name_lower:
                class_data['primary_ability'] = ["Wisdom"]
            elif 'druid' in class_name_lower:
                class_data['primary_ability'] = ["Wisdom"]
            elif 'fighter' in class_name_lower:
                class_data['primary_ability'] = ["Strength", "Dexterity"]
            elif 'monk' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity", "Wisdom"]
            elif 'paladin' in class_name_lower:
                class_data['primary_ability'] = ["Strength", "Charisma"]
            elif 'ranger' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity", "Wisdom"]
            elif 'rogue' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity"]
            elif 'sorcerer' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'warlock' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'wizard' in class_name_lower:
                class_data['primary_ability'] = ["Intelligence"]
        
        # Proficiencies - DÜZELTİLDİ (Classes Scraping - iyileştirildi)
        # Proficiencies genellikle tek bir paragrafta: "Armor: ... Weapons: ... Tools: ... Saving Throws: ... Skills: ..."
        proficiencies_para = None
        for para_text in paragraph_texts:
            if 'Armor:' in para_text and ('Weapons:' in para_text or 'Saving Throws:' in para_text):
                proficiencies_para = para_text
                break
        
        # Skill names list (all D&D 5e skills)
        skill_names = [
            "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
            "History", "Insight", "Intimidation", "Investigation", "Medicine",
            "Nature", "Perception", "Performance", "Persuasion", "Religion",
            "Sleight of Hand", "Stealth", "Survival"
        ]
        
        if proficiencies_para:
            # Armor
            armor_match = re.search(r'Armor[:\s]+([^W]+?)(?:Weapons|Tools|Saving|Skills|$)', proficiencies_para, re.I)
            if armor_match:
                armor_text = armor_match.group(1).strip()
                if 'all armor' in armor_text.lower() or 'all' in armor_text.lower():
                    class_data['proficiencies']['armor'] = ["All armor", "Shields"]
                elif 'shields' in armor_text.lower():
                    armor_types = re.split(r'[,]', armor_text)
                    for armor in armor_types:
                        armor_clean = armor.strip()
                        if armor_clean:
                            if 'shield' in armor_clean.lower():
                                if "Shields" not in class_data['proficiencies']['armor']:
                                    class_data['proficiencies']['armor'].append("Shields")
                            elif armor_clean and armor_clean not in class_data['proficiencies']['armor']:
                                class_data['proficiencies']['armor'].append(armor_clean)
            
            # Weapons - DÜZELTİLDİ (iyileştirildi - pattern düzeltildi)
            # Format: "Weapons: Simple weapons, martial weaponsTools:..." (boşluk olmayabilir)
            weapon_patterns = [
                r'Weapons?[:\s]+([^T]+?)(?:Tools|Saving|Skills|$)',
                r'Weapons?[:\s]+([A-Za-z\s,]+?)(?:Tools|Saving|Skills|$)',
            ]
            
            for pattern in weapon_patterns:
                weapon_match = re.search(pattern, proficiencies_para, re.I)
                if weapon_match:
                    weapon_text = weapon_match.group(1).strip()
                    # "Simple weapons, martial weapons" veya "Simple weapons,martial weapons" gibi formatları parse et
                    if 'simple' in weapon_text.lower() and 'martial' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Simple weapons", "Martial weapons"]
                        break
                    elif 'simple' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Simple weapons"]
                        break
                    elif 'martial' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Martial weapons"]
                        break
                    else:
                        # Virgülle ayrılmış weapon'ları parse et
                        weapon_types = re.split(r'[,]', weapon_text)
                        for weapon in weapon_types:
                            weapon_clean = weapon.strip()
                            if weapon_clean and weapon_clean not in class_data['proficiencies']['weapons']:
                                class_data['proficiencies']['weapons'].append(weapon_clean)
                        if class_data['proficiencies']['weapons']:
                            break
            
            # Tools
            tool_match = re.search(r'Tools?[:\s]+([^S]+?)(?:Saving|Skills|$)', proficiencies_para, re.I)
            if tool_match:
                tool_text = tool_match.group(1).strip()
                if 'none' not in tool_text.lower():
                    tool_types = re.split(r'[,]', tool_text)
                    for tool in tool_types:
                        tool_clean = tool.strip()
                        if tool_clean and tool_clean not in class_data['proficiencies']['tools']:
                            class_data['proficiencies']['tools'].append(tool_clean)
            
            # Saving Throws - DÜZELTİLDİ (paragraftan parse - iyileştirildi)
            # Format: "Saving Throws:Strength,ConstitutionSkills:..." (boşluk olmayabilir, Skills ile bitiyor)
            saving_throws_patterns = [
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+)*?)(?:Skills|$)',
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+,\s*[A-Z][a-z]+)(?:Skills|$)',
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+,\s*[A-Z][a-z]+)',
            ]
            
            for pattern in saving_throws_patterns:
                saving_throws_match = re.search(pattern, proficiencies_para, re.I)
                if saving_throws_match:
                    throws_text = saving_throws_match.group(1).strip()
                    # Virgül veya boşlukla ayrılmış ability'leri parse et
                    throws = re.split(r'[,]+', throws_text)
                    for throw in throws:
                        throw_clean = throw.strip()
                        # Ability name'i tam olarak eşleştir (capitalize etmeden önce kontrol et)
                        for ability in ability_names.values():
                            if (ability.lower() == throw_clean.lower() or 
                                throw_clean.lower() == ability.lower()[:len(throw_clean)] or
                                ability.lower().startswith(throw_clean.lower())):
                                if ability not in class_data['saving_throws']:
                                    class_data['saving_throws'].append(ability)
                                break
                    if len(class_data['saving_throws']) >= 2:  # En az 2 saving throw olmalı
                        break
            
            # Class Skills - DÜZELTİLDİ (paragraftan parse - iyileştirildi)
            # Format: "Skills: Choose two skills fromAcrobatic..." veya "Skills: Choose from Acrobatics, Animal Handling..."
            skills_patterns = [
                r'Skills?[:\s]+Choose\s+(\d+)\s+skills?\s+from\s+([A-Z][a-z\s,]+?)(?:\n|$)',
                r'Skills?[:\s]+Choose\s+(\d+)\s+from\s+([A-Z][a-z\s,]+?)(?:\n|$)',
                r'Skills?[:\s]+([A-Z][a-z\s,]+?)(?:\n\n|\n[A-Z]|$)',
            ]
            
            for pattern in skills_patterns:
                skills_match = re.search(pattern, proficiencies_para, re.I | re.DOTALL)
                if skills_match:
                    # Skill count
                    if skills_match.lastindex >= 1 and skills_match.group(1).isdigit():
                        class_data['skill_choices'] = int(skills_match.group(1))
                    
                    # Skills text
                    skills_text = skills_match.group(2) if skills_match.lastindex >= 2 else skills_match.group(1)
                    if skills_text:
                        # Skills listesini parse et (virgül veya "and" ile ayrılmış)
                        skills_list = re.split(r'[,and]+', skills_text, flags=re.I)
                        for skill in skills_list:
                            skill_clean = skill.strip()
                            if skill_clean:
                                # Skill ismini eşleştir (tam isim veya kısmi)
                                for known_skill in skill_names:
                                    # Exact match veya substring match
                                    if (known_skill.lower() == skill_clean.lower() or 
                                        known_skill.lower().startswith(skill_clean.lower()) or
                                        skill_clean.lower() in known_skill.lower()):
                                        if known_skill not in class_data['class_skills']:
                                            class_data['class_skills'].append(known_skill)
                                        break
                    if class_data['class_skills']:
                        break
        
        # Class Features - DÜZELTİLDİ (Classes Scraping - Level bazlı tablo parsing)
        # Level table'ını bul (1-20 level features)
        tables = main_content.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 5:  # En az birkaç satır olmalı
                # İlk satır header olabilir
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                # "Level" veya "Features" kolonunu bul
                level_col = None
                features_col = None
                
                for i, header in enumerate(headers):
                    if 'level' in header.lower():
                        level_col = i
                    if 'feature' in header.lower() or 'class' in header.lower():
                        features_col = i
                
                # Eğer header yoksa, ilk kolon level, son kolon features olabilir
                if level_col is None:
                    level_col = 0
                if features_col is None:
                    features_col = len(headers) - 1
                
                # Satırları parse et
                for row in rows[1:]:  # İlk satır header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) > max(level_col, features_col):
                        level_text = cells[level_col].get_text(strip=True) if level_col < len(cells) else ""
                        features_text = cells[features_col].get_text(strip=True) if features_col < len(cells) else ""
                        
                        # Level numarasını çıkar (örn: "1st", "2nd", "3rd", "4th" -> 1, 2, 3, 4)
                        level_match = re.search(r'(\d+)', level_text)
                        if level_match and features_text:
                            level = int(level_match.group(1))
                            # Features'ları parse et (virgülle ayrılmış)
                            features = [f.strip() for f in re.split(r'[,]', features_text) if f.strip()]
                            
                            if level not in class_data['class_features']:
                                class_data['class_features'][str(level)] = {
                                    "features": features,
                                    "choices": {}
                                }
                            else:
                                # Mevcut features'lara ekle
                                existing_features = class_data['class_features'][str(level)].get("features", [])
                                for feature in features:
                                    if feature not in existing_features:
                                        existing_features.append(feature)
                                class_data['class_features'][str(level)]["features"] = existing_features
                
                # Tablo bulundu, diğer tablolara bakmaya gerek yok
                if class_data['class_features']:
                    break
        
        # Starting Equipment - DÜZELTİLDİ (Classes Scraping)
        # "You start with the following equipment" veya "Starting Equipment" bölümünü bul
        equipment_section_patterns = [
            r'You start with the following equipment[:\s]+(.+?)(?:\n\n|\n[A-Z]|Class Features|$)',
            r'Starting Equipment[:\s]+(.+?)(?:\n\n|\n[A-Z]|Class Features|$)',
        ]
        
        for pattern in equipment_section_patterns:
            equipment_match = re.search(pattern, text_content[:5000], re.I | re.DOTALL)
            if equipment_match:
                equipment_text = equipment_match.group(1).strip()
                # Equipment options'ları parse et (genellikle liste halinde)
                # Format: "(a) item1, item2 or (b) item3, item4"
                options = re.split(r'\([a-z]\)', equipment_text, flags=re.I)
                for option in options:
                    option_clean = option.strip()
                    if option_clean and len(option_clean) > 10:
                        # "or" ile ayrılmış alternatifleri bul
                        items = re.split(r'\s+or\s+', option_clean, flags=re.I)
                        equipment_list = []
                        for item_text in items:
                            # Virgülle ayrılmış item'ları parse et
                            item_parts = re.split(r'[,]', item_text)
                            for item_part in item_parts:
                                item_clean = item_part.strip()
                                if item_clean and len(item_clean) > 2:
                                    equipment_list.append(item_clean)
                        if equipment_list:
                            class_data['starting_equipment_options'].append(equipment_list)
                break
        
        # Spellcasting - eğer spellcaster ise - DÜZELTİLDİ (daha iyi detection)
        # Spellcaster class'lar: Wizard, Sorcerer, Warlock, Cleric, Druid, Bard, Paladin, Ranger, Artificer
        spellcaster_classes = ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard', 'paladin', 'ranger', 'artificer']
        class_name_lower = name.lower()
        
        # Önce class name'e göre kontrol et (en güvenilir)
        is_spellcaster = class_name_lower in spellcaster_classes
        
        # Eğer class name'e göre spellcaster değilse, content'te spellcasting section'ı ara
        if not is_spellcaster:
            spellcasting_indicators = [
                r'Spellcasting\s+Ability',  # "Spellcasting Ability" başlığı
                r'Spell\s+Slots\s+per\s+Level',  # Spell slots tablosu
                r'Spells\s+Known',  # Spells Known section
                r'Spells\s+Prepared',  # Spells Prepared section
                r'Cantrips?\s+Known',  # Cantrips section
            ]
            
            # Sadece başlık veya section başlığı olarak geçiyorsa spellcaster
            for indicator in spellcasting_indicators:
                if re.search(indicator, text_content[:10000], re.I):
                    is_spellcaster = True
                    break
        
        if is_spellcaster:
            # Spellcasting ability'yi belirle
            spellcasting_ability = "Intelligence"  # Default
            if class_name_lower in ['wizard', 'artificer']:
                spellcasting_ability = "Intelligence"
            elif class_name_lower in ['sorcerer', 'warlock', 'bard', 'paladin']:
                spellcasting_ability = "Charisma"
            elif class_name_lower in ['cleric', 'druid', 'ranger']:
                spellcasting_ability = "Wisdom"
            elif class_data['primary_ability']:
                spellcasting_ability = class_data['primary_ability'][0]
            
            class_data['spellcasting'] = {
                "spellcasting_ability": spellcasting_ability,
                "spell_save_dc": 8,  # Base (8 + proficiency + ability modifier)
                "spell_attack_bonus": 0  # Base (proficiency + ability modifier)
            }
        else:
            class_data['spellcasting'] = None
        
        return class_data
    
    def scrape_all_race_links(self) -> List[tuple]:
        """Tüm core race linklerini çek - DÜZELTİLDİ (Races Scraping)"""
        print("[*] Race linkleri cekiliyor...")
        
        # Core races listesi (bilinen D&D 5e core races)
        core_races = [
            ("Dragonborn", f"{self.BASE_URL}/races/dragonborn/"),
            ("Dwarf", f"{self.BASE_URL}/races/dwarf/"),
            ("Elf", f"{self.BASE_URL}/races/elf/"),
            ("Gnome", f"{self.BASE_URL}/races/gnome/"),
            ("Halfling", f"{self.BASE_URL}/races/halfling/"),
            ("Half-Elf", f"{self.BASE_URL}/races/half-elf/"),
            ("Half-Orc", f"{self.BASE_URL}/races/half-orc/"),
            ("Human", f"{self.BASE_URL}/races/human/"),
            ("Tiefling", f"{self.BASE_URL}/races/tiefling/"),
        ]
        
        print(f"  [OK] {len(core_races)} core race linki hazir")
        return core_races
    
    def scrape_race_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Race detay sayfasını çek - DÜZELTİLDİ (Races Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        race_data = {
            "name": name,
            "ability_score_increase": {},
            "speed": 30,  # Default
            "traits": [],
            "languages": [],
            "extra_languages": 0,
            "size": "Medium",  # Default
            "source": url
        }
        
        # Tüm metni al
        text_content = main_content.get_text()
        
        # Paragrafları al (structured parsing için)
        paragraphs = main_content.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        
        # Ability Score Increase - DÜZELTİLDİ (Races Scraping)
        ability_names = {
            "strength": "strength", "dexterity": "dexterity", "constitution": "constitution",
            "intelligence": "intelligence", "wisdom": "wisdom", "charisma": "charisma"
        }
        
        asi_patterns = [
            r'Ability\s+Score\s+Increase[:\s]+(.+?)(?:\n\n|\n[A-Z]|Age|Alignment|Size|Speed|Traits|Languages|$)',
            r'ASI[:\s]+(.+?)(?:\n|$)',
        ]
        
        # Önce paragraflarda ara
        for para_text in paragraph_texts:
            for pattern in asi_patterns:
                match = re.search(pattern, para_text, re.I | re.DOTALL)
                if match:
                    asi_text = match.group(1).strip()
                    
                    # "Your Strength score increases by 2, and your Charisma score increases by 1."
                    # veya "Your all ability scores increase by 1"
                    # veya "Strength +2, Charisma +1"
                    
                    # "all" kontrolü
                    if 'all' in asi_text.lower() or 'each' in asi_text.lower():
                        all_match = re.search(r'(\d+)', asi_text)
                        if all_match:
                            race_data['ability_score_increase'] = {"all": int(all_match.group(1))}
                            break
                    else:
                        # Individual ability increases
                        ability_increases = {}
                        # Pattern: "YourStrengthscore increases by 2" (boşluk olmayabilir!)
                        # veya "Strength score increases by 2" (boşluklu)
                        # veya "Strength +2"
                        
                        # Önce "YourXxxscore increases by Y" formatını parse et (boşluksuz)
                        no_space_pattern = r'Your(\w+)score\s+increases?\s+by\s+(\d+)'
                        matches = re.finditer(no_space_pattern, asi_text, re.I)
                        for m in matches:
                            ability_word = m.group(1).lower()
                            value = int(m.group(2))
                            
                            # Ability name'i normalize et
                            for known_ability, key in ability_names.items():
                                if known_ability in ability_word or ability_word in known_ability:
                                    ability_increases[key] = value
                                    break
                        
                        # Eğer boşluksuz pattern çalışmadıysa, boşluklu pattern'leri dene
                        if not ability_increases:
                            ability_patterns = [
                                r'(\w+)\s+score\s+increases?\s+by\s+(\d+)',
                                r'(\w+)\s+(\d+)',
                                r'\+(\d+)\s+(\w+)',
                            ]
                            
                            for ab_pattern in ability_patterns:
                                matches = re.finditer(ab_pattern, asi_text, re.I)
                                for m in matches:
                                    if len(m.groups()) >= 2:
                                        # İki format var: (ability, value) veya (value, ability)
                                        if m.group(1).isdigit():
                                            value = int(m.group(1))
                                            ability = m.group(2).lower()
                                        else:
                                            ability = m.group(1).lower()
                                            value = int(m.group(2))
                                        
                                        # Ability name'i normalize et
                                        for known_ability, key in ability_names.items():
                                            if known_ability in ability or ability in known_ability:
                                                ability_increases[key] = value
                                                break
                                if ability_increases:
                                    break
                        
                        if ability_increases:
                            race_data['ability_score_increase'] = ability_increases
                            break
                    
                    if race_data['ability_score_increase']:
                        break
            if race_data['ability_score_increase']:
                break
        
        # Speed - DÜZELTİLDİ (Races Scraping)
        speed_patterns = [
            r'Speed[:\s]+Your\s+base\s+walking\s+speed\s+is\s+(\d+)\s+feet?',
            r'Speed[:\s]+(\d+)\s+ft',
            r'Base\s+Speed[:\s]+(\d+)',
            r'(\d+)\s+feet?\s+speed',
        ]
        
        for para_text in paragraph_texts:
            for pattern in speed_patterns:
                match = re.search(pattern, para_text, re.I)
                if match:
                    speed_val = int(match.group(1))
                    race_data['speed'] = speed_val
                    break
            if race_data['speed'] != 30:
                break
        
        # Traits - DÜZELTİLDİ (Races Scraping - iyileştirildi)
        # Traits hem başlık (H3, H4) hem de paragraf içinde olabilir
        # Örnek: "Draconic Ancestry", "Breath Weapon", "Damage Resistance"
        known_trait_names = [
            'Draconic Ancestry', 'Breath Weapon', 'Damage Resistance',
            'Darkvision', 'Fey Ancestry', 'Trance', 'Keen Senses',
            'Lucky', 'Brave', 'Halfling Nimbleness', 'Naturally Stealthy',
            'Stonecunning', 'Dwarven Toughness', 'Dwarven Resilience',
            'Gnome Cunning', 'Artificer\'s Lore', 'Tinker',
            'Mask of the Wild', 'Fleet of Foot', 'Elf Weapon Training',
            'Extra Language', 'Versatility', 'Skill Versatility',
            'Menacing', 'Relentless Endurance', 'Savage Attacks',
            'Hellish Resistance', 'Infernal Legacy'
        ]
        
        # Önce başlıklardan trait'leri bul
        headings = main_content.find_all(['h3', 'h4'])
        skip_headings = ['traits', 'variants', 'subrace', 'subraces', 'race features', 'race feature']
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            heading_lower = heading_text.lower()
            
            # Genel başlıkları atla
            if heading_lower in skip_headings:
                continue
            
            # "Dragonborn Traits" gibi race-specific genel başlıkları atla
            if heading_lower == 'traits' or (heading_lower.endswith('traits') and len(heading_lower.split()) <= 2):
                continue
            
            # Bilinen trait isimleri ile eşleştir
            for trait_name in known_trait_names:
                if trait_name.lower() == heading_lower or heading_lower.startswith(trait_name.lower()):
                    if trait_name not in race_data['traits']:
                        race_data['traits'].append(trait_name)
                    break
        
        # Sonra paragraflardan trait'leri bul (örn: "Draconic Ancestry: You have...")
        for para_text in paragraph_texts:
            # Pattern: "Trait Name: Description" formatını ara
            for trait_name in known_trait_names:
                # Trait name ile başlayan paragrafları bul
                trait_pattern = r'^' + re.escape(trait_name) + r'[:\s]+'
                if re.search(trait_pattern, para_text, re.I):
                    if trait_name not in race_data['traits']:
                        race_data['traits'].append(trait_name)
        
        # Languages - DÜZELTİLDİ (Races Scraping - iyileştirildi)
        language_names = [
            "Common", "Elvish", "Dwarvish", "Gnomish", "Halfling",
            "Orc", "Draconic", "Infernal", "Celestial", "Abyssal",
            "Giant", "Primordial", "Deep Speech", "Undercommon"
        ]
        
        # Languages paragrafını bul
        for para_text in paragraph_texts:
            if 'language' not in para_text.lower():
                continue
            
            # "Languages: You can speak, read, and write Common and Draconic."
            # Pattern: "Common and Draconic" kısmını yakala
            # Önce tüm language names'leri ara
            found_languages = []
            for lang_name in language_names:
                # Language name'i paragrafta ara (kelime sınırları ile)
                lang_pattern = r'\b' + re.escape(lang_name) + r'\b'
                if re.search(lang_pattern, para_text, re.I):
                    found_languages.append(lang_name)
            
            if found_languages:
                race_data['languages'] = found_languages
                break
        
        # Extra Languages
        extra_lang_patterns = [
            r'Extra\s+Languages?[:\s]+(\d+)',
            r'one\s+additional\s+language',
            r'additional\s+language',
        ]
        
        for pattern in extra_lang_patterns:
            match = re.search(pattern, text_content[:3000], re.I)
            if match:
                if match.group(1) if match.lastindex >= 1 else None:
                    race_data['extra_languages'] = int(match.group(1))
                else:
                    race_data['extra_languages'] = 1
                break
        
        # Size - DÜZELTİLDİ (Races Scraping)
        size_patterns = [
            r'Size[:\s]+(.+?)(?:\n|$)',
            r'Yoursizeis\s+(\w+)',
            r'size\s+is\s+(\w+)',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text_content[:2000], re.I)
            if match:
                size_text = match.group(1).strip().capitalize()
                if size_text in ["Small", "Medium", "Large", "Tiny", "Huge"]:
                    race_data['size'] = size_text
                    break
        
        return race_data
    
    def scrape_all_races(self, max_races: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm core races'leri scrape et - DÜZELTİLDİ (Races Scraping)"""
        print("[*] Tum core races scrape ediliyor...")
        
        # Cache kontrolü
        cache_file = Path("data/cache/races_cache.json")
        races = {}
        cached_races = {}
        
        if cache_file.exists() and not force_refresh:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    if cached.get('races'):
                        cached_races = cached['races']
                        races.update(cached_races)
                        print(f"  [OK] {len(cached_races)} race cache'den yuklendi")
            except Exception as e:
                print(f"  [UYARI] Cache yuklenemedi: {e}")
        
        # Race linklerini çek
        race_links = self.scrape_all_race_links()
        
        if not race_links:
            print("  [UYARI] Race linkleri bulunamadi! Mevcut cache'i donduruyoruz.")
            return races
        
        print(f"\n[*] {len(race_links)} race bulundu")
        
        # Cache'de olmayan race'leri filtrele
        cached_names = set(cached_races.keys())
        new_race_links = [(name, url) for name, url in race_links if name not in cached_names]
        
        if new_race_links:
            print(f"\n[*] {len(new_race_links)} yeni race cekilecek ({len(cached_names)} zaten cache'de)")
        else:
            print("\n[OK] Tum race'ler zaten cache'de!")
            return races
        
        # Max races limiti
        if max_races:
            new_race_links = new_race_links[:max_races]
        
        total = len(new_race_links)
        print(f"\n[*] {total} race detayi cekiliyor...")
        print("  (Bu islem uzun surebilir, lutfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(new_race_links, 1):
            if i % 2 == 0:
                successful = len([k for k in races.keys() if k not in cached_names])
                print(f"  ... {i}/{total} race cekildi ({successful} basarili)")
            
            race_data = self.scrape_race_detail(url, name)
            if race_data and race_data.get('name'):
                races[race_data['name']] = race_data
            else:
                print(f"  [UYARI] {name} scrape edilemedi")
        
        print(f"\n[OK] {len([k for k in races.keys() if k not in cached_names])} yeni race basariyla cekildi")
        print(f"   Toplam: {len(races)} race (cache dahil)")
        
        # Cache'e kaydet
        cache_data = {
            'total': len(races),
            'races': races,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"[*] Cache'e kaydedildi: {cache_file}")
        
        return races
    
    def scrape_equipment_from_table(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Equipment tablosundan verileri çek - DÜZELTİLDİ (Equipment Scraping)"""
        soup = self._get(url)
        if not soup:
            return []
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            return []
        
        equipment_list = []
        
        # Tüm tabloları bul
        tables = main_content.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:  # En az header + 1 data row
                continue
            
            # Header row'u bul (ilk row)
            header_row = rows[0]
            header_cells = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            # Header'da hangi kolonlar var?
            # Olası kolonlar: name, cost, damage, range, weight, properties, armor_class, strength_requirement, stealth, etc.
            
            # Kolon indexlerini bul
            name_idx = None
            cost_idx = None
            damage_idx = None
            range_idx = None
            weight_idx = None
            properties_idx = None
            ac_idx = None  # Armor Class (armor için)
            strength_idx = None  # Strength requirement (armor için)
            stealth_idx = None  # Stealth disadvantage (armor için)
            
            for i, header in enumerate(header_cells):
                if 'name' in header or header == '':
                    name_idx = i
                elif 'cost' in header or 'price' in header:
                    cost_idx = i
                elif 'damage' in header:
                    damage_idx = i
                elif 'range' in header:
                    range_idx = i
                elif 'weight' in header:
                    weight_idx = i
                elif 'properties' in header or 'property' in header:
                    properties_idx = i
                elif 'armor' in header and 'class' in header or 'ac' in header:
                    ac_idx = i
                elif 'strength' in header:
                    strength_idx = i
                elif 'stealth' in header:
                    stealth_idx = i
            
            # Eğer name_idx yoksa, ilk kolonu name olarak kabul et
            if name_idx is None:
                name_idx = 0
            
            # Data row'larını parse et (ikinci row'dan başla)
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                if len(cell_texts) <= name_idx:
                    continue
                
                # Name'i al
                name = cell_texts[name_idx].strip()
                
                # Eğer name boşsa veya başlık satırıysa atla
                if not name or name.lower() in ['(simple)', '(martial)', 'simple melee weapons', 'martial melee weapons', 
                                                 'simple ranged weapons', 'martial ranged weapons']:
                    continue
                
                # Equipment item oluştur
                item = {
                    "name": name,
                    "type": category.lower(),  # "weapon", "armor", "gear", "tool"
                    "category": category,
                    "source": url
                }
                
                # Cost
                if cost_idx is not None and cost_idx < len(cell_texts):
                    cost_text = cell_texts[cost_idx].strip()
                    if cost_text and cost_text not in ['—', '–', '-', '']:
                        item["cost"] = cost_text
                
                # Damage (weapon için)
                if damage_idx is not None and damage_idx < len(cell_texts):
                    damage_text = cell_texts[damage_idx].strip()
                    if damage_text and damage_text not in ['—', '–', '-', '']:
                        item["damage"] = damage_text
                
                # Range (ranged weapon için)
                if range_idx is not None and range_idx < len(cell_texts):
                    range_text = cell_texts[range_idx].strip()
                    if range_text and range_text not in ['—', '–', '-', '']:
                        item["range"] = range_text
                
                # Weight
                if weight_idx is not None and weight_idx < len(cell_texts):
                    weight_text = cell_texts[weight_idx].strip()
                    if weight_text and weight_text not in ['—', '–', '-', '']:
                        # "4 lb." veya "4 lb" veya "4" formatını parse et
                        weight_match = re.search(r'(\d+(?:\.\d+)?)', weight_text)
                        if weight_match:
                            try:
                                item["weight"] = float(weight_match.group(1))
                            except ValueError:
                                item["weight"] = weight_text
                        else:
                            item["weight"] = weight_text
                
                # Properties (weapon için)
                if properties_idx is not None and properties_idx < len(cell_texts):
                    properties_text = cell_texts[properties_idx].strip()
                    if properties_text and properties_text not in ['—', '–', '-', '']:
                        # "finesse,light,thrown" veya "versatile(1d10)" formatını parse et
                        properties = [p.strip() for p in re.split(r'[,;]', properties_text) if p.strip()]
                        if properties:
                            item["properties"] = properties
                
                # Armor Class (armor için)
                if ac_idx is not None and ac_idx < len(cell_texts):
                    ac_text = cell_texts[ac_idx].strip()
                    if ac_text and ac_text not in ['—', '–', '-', '']:
                        # "11 + Dex modifier" veya "18" formatını parse et
                        item["armor_class"] = ac_text
                
                # Strength requirement (armor için)
                if strength_idx is not None and strength_idx < len(cell_texts):
                    strength_text = cell_texts[strength_idx].strip()
                    if strength_text and strength_text not in ['—', '–', '-', '']:
                        strength_match = re.search(r'(\d+)', strength_text)
                        if strength_match:
                            item["strength_requirement"] = int(strength_match.group(1))
                
                # Stealth disadvantage (armor için)
                if stealth_idx is not None and stealth_idx < len(cell_texts):
                    stealth_text = cell_texts[stealth_idx].strip()
                    if 'disadvantage' in stealth_text.lower():
                        item["stealth_disadvantage"] = True
                
                equipment_list.append(item)
        
        return equipment_list
    
    def scrape_all_equipment_links(self) -> List[tuple]:
        """Tüm equipment kategorilerinin linklerini çek - DÜZELTİLDİ (Equipment Scraping)"""
        print("[*] Equipment kategori linkleri cekiliyor...")
        
        # Equipment kategorileri
        equipment_categories = [
            ("Weapons", f"{self.BASE_URL}/equipment/weapons/"),
            ("Armor", f"{self.BASE_URL}/equipment/armor/"),
            ("Adventuring Gear", f"{self.BASE_URL}/equipment/adventuring-gear/"),
            ("Tools", f"{self.BASE_URL}/equipment/tools/"),
        ]
        
        print(f"  [OK] {len(equipment_categories)} equipment kategori linki hazir")
        return equipment_categories
    
    def scrape_all_equipment(self, max_items: Optional[int] = None, force_refresh: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Tüm equipment'leri çek - DÜZELTİLDİ (Equipment Scraping)"""
        print("=" * 70)
        print("5ESRD.COM EQUIPMENT ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü
        cache_file = Path("data/cache/equipment_cache.json")
        equipment_data = {}
        cached_equipment = {}
        
        if not force_refresh and cache_file.exists():
            print(f"[*] Cache dosyasi bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('equipment'):
                    cached_equipment = cached['equipment']
                    equipment_data.update(cached_equipment)
                    print(f"  [OK] {sum(len(items) for items in cached_equipment.values())} equipment item cache'den yuklendi")
        
        # Equipment kategori linklerini çek
        equipment_links = self.scrape_all_equipment_links()
        
        if not equipment_links:
            print("  [UYARI] Equipment kategori linkleri bulunamadi! Mevcut cache'i donduruyoruz.")
            return cached_equipment
        
        # Her kategori için equipment'leri çek
        for category_name, url in equipment_links:
            if category_name in equipment_data and not force_refresh:
                print(f"  [ATLA] {category_name} zaten cache'de, atlaniyor...")
                continue
            
            print(f"\n[*] {category_name} cekiliyor...")
            print(f"   URL: {url}")
            
            items = self.scrape_equipment_from_table(url, category_name)
            
            if items:
                equipment_data[category_name] = items
                print(f"   [OK] {len(items)} {category_name.lower()} item cekildi")
            else:
                print(f"   [UYARI] {category_name} icin item bulunamadi")
        
        # Cache'e kaydet
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({"equipment": equipment_data}, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Equipment data '{cache_file}' dosyasina kaydedildi!")
        print(f"[*] Toplam {sum(len(items) for items in equipment_data.values())} equipment item cekildi.")
        
        return equipment_data


"""5esrd.com D&D 5e scraper"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any


class Dnd5eSrdScraper:
    """5esrd.com'dan D&D 5e verilerini çeken scraper"""
    
    BASE_URL = "https://www.5esrd.com"
    
    def __init__(self, rate_limit: float = 1.5):
        """
        Args:
            rate_limit: İstekler arası bekleme süresi (saniye)
        """
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """HTTP GET isteği yap ve BeautifulSoup döndür"""
        for attempt in range(retries):
            try:
                time.sleep(self.rate_limit)
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')
                elif response.status_code == 404:
                    return None
                else:
                    print(f"  ⚠️  Status {response.status_code} for {url}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"  ⚠️  Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None
    
    def scrape_all_spell_links(self) -> List[tuple]:
        """Tüm spell linklerini çek"""
        print("🔍 Spell linkleri çekiliyor...")
        url = f"{self.BASE_URL}/database/spell/"
        
        soup = self._get(url)
        if not soup:
            print("❌ Spell database sayfası bulunamadı!")
            return []
        
        spell_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Spell linklerini bul
            if '/spell/' in href.lower() and text and len(text) < 100:
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                else:
                    full_url = urljoin(url, href)
                spell_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_links = list(set(spell_links))
        print(f"  ✅ {len(unique_links)} unique spell linki bulundu")
        return unique_links
    
    def scrape_spell_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Spell detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        spell_data = {
            "name": name,
            "level": None,
            "school": None,
            "casting_time": None,
            "range": None,
            "components": None,
            "duration": None,
            "description": "",
            "classes": [],
            "ritual": False,
            "concentration": False,
            "source": url
        }
        
        # Tüm paragrafları al
        paragraphs = main_content.find_all('p')
        
        # Metni al
        text_content = main_content.get_text()
        
        # İlk paragrafı al (genellikle level ve school burada)
        first_p = paragraphs[0] if paragraphs else None
        first_para_text = first_p.get_text(strip=True) if first_p else ""
        
        # Level ve School - DÜZELTİLDİ
        # Format: "3rd-levelevocation" veya "Conjurationcantrip" (boşluk yok!)
        # Önce ilk paragraftan bulmaya çalış
        level_school_patterns = [
            r'(\d+)(st|nd|rd|th)[\s-]*level([a-z]+)',  # "3rd-levelevocation"
            r'([a-z]+)cantrip',  # "Conjurationcantrip"
            r'(\d+)(st|nd|rd|th)[\s-]*level\s+([a-z]+)',  # "3rd-level evocation" (boşluklu)
            r'cantrip\s+([a-z]+)',  # "cantrip evocation" (boşluklu)
        ]
        
        found = False
        for pattern in level_school_patterns:
            match = re.search(pattern, first_para_text, re.I)
            if not match:
                match = re.search(pattern, text_content[:500], re.I)  # İlk 500 karakterde ara
            
            if match:
                if 'cantrip' in pattern.lower():
                    spell_data['level'] = 0
                    spell_data['school'] = match.group(1).capitalize() if match.lastindex >= 1 else None
                    found = True
                else:
                    level_num = match.group(1)
                    school = match.group(match.lastindex)  # Son grup school
                    spell_data['level'] = int(level_num)
                    spell_data['school'] = school.capitalize()
                    found = True
                break
        
        # Eğer bulunamadıysa, text'ten daha geniş arama yap
        if not found:
            # "3rd level" veya "1st level" gibi formatları ara
            level_match = re.search(r'(\d+)(st|nd|rd|th)\s*level', text_content, re.I)
            if level_match:
                spell_data['level'] = int(level_match.group(1))
                # School'u bul
                school_match = re.search(r'(?:level|spell)[\s-]+([a-z]+)', text_content[level_match.end():level_match.end()+50], re.I)
                if school_match:
                    spell_data['school'] = school_match.group(1).capitalize()
        
        # Casting Time, Range, Components, Duration - DÜZELTİLDİ (V2)
        # Format: "Casting Time:1 actionRange:60 feetComponents:V, SDuration:Instantaneous"
        # İkinci paragraf genellikle bu bilgileri içerir, ama bazı spell'lerde description'da olabilir
        
        # Önce ikinci paragraftan bulmaya çalış
        second_p = paragraphs[1] if len(paragraphs) > 1 else None
        stats_text = second_p.get_text(strip=True) if second_p else ""
        
        # Eğer ikinci paragrafta yeterli bilgi yoksa, text'in başından ara
        if not stats_text or 'Casting Time' not in stats_text:
            stats_match = re.search(r'Casting\s+Time[:\s]+.+?(?=You |A |Target|$)', text_content[:2000], re.I | re.DOTALL)
            if stats_match:
                stats_text = stats_match.group(0)
        
        # Eğer hala bulunamadıysa, description'dan da çıkarmaya çalış
        if not stats_text or len(stats_text) < 30:
            # Description paragraflarından ara
            for p in paragraphs[2:5] if len(paragraphs) > 2 else []:
                p_text = p.get_text(strip=True)
                if 'Casting Time' in p_text or 'Range:' in p_text or 'Components:' in p_text:
                    stats_text = p_text
                    break
        
        if stats_text:
            # Casting Time - Daha esnek regex
            if not spell_data.get('casting_time'):
                ct_patterns = [
                    r'Casting\s+Time[:\s]+([^R]+?)(?:Range|Components|Duration|$|You |A |Target)',
                    r'Casting\s+Time[:\s]+([^R]+?)(?=Range|$)',
                ]
                for pattern in ct_patterns:
                    ct_match = re.search(pattern, stats_text, re.I)
                    if ct_match:
                        casting_time = ct_match.group(1).strip()
                        spell_data['casting_time'] = re.sub(r'\s+', ' ', casting_time)
                        break
            
            # Range - DÜZELTİLDİ (case-insensitive ve daha akıllı)
            if not spell_data.get('range'):
                # "Range:" veya "Range :" sonrası, "Components" öncesi veya satır sonu
                range_patterns = [
                    r'Range[:\s]+([^C\n]+?)(?:Components|Duration|$)',  # Components veya Duration'a kadar
                    r'Range[:\s]+([a-zA-Z0-9\s\'-]+?)(?=Components|Duration|$)',  # Kelimeler ve boşluklar
                ]
                for pattern in range_patterns:
                    range_match = re.search(pattern, stats_text, re.I)
                    if range_match:
                        range_text = range_match.group(1).strip()
                        # "touch" gibi küçük harfli değerleri düzelt
                        range_text = range_text.capitalize() if range_text.islower() else range_text
                        spell_data['range'] = re.sub(r'\s+', ' ', range_text)
                        break
            
            # Components - DÜZELTİLDİ V4 (position-based, parantez desteği)
            if not spell_data.get('components'):
                # Components başlangıcını bul
                comp_start_match = re.search(r'Components[:\s]+', stats_text, re.I)
                if comp_start_match:
                    start_pos = comp_start_match.end()
                    
                    # Duration'un başlangıcını bul
                    dur_start_match = re.search(r'Duration[:\s]+', stats_text[start_pos:], re.I)
                    if dur_start_match:
                        end_pos = start_pos + dur_start_match.start()
                    else:
                        # Duration yoksa, "You" veya satır sonuna kadar
                        you_match = re.search(r'\bYou\s+', stats_text[start_pos:], re.I)
                        if you_match:
                            end_pos = start_pos + you_match.start()
                        else:
                            end_pos = start_pos + 200  # Fallback: 200 karakter
                    
                    components_raw = stats_text[start_pos:end_pos].strip()
                    
                    # Parantez kontrolü - açık parantez varsa kapatmayı bul
                    open_paren_pos = components_raw.find('(')
                    if open_paren_pos != -1:
                        # Kapanış parantezini bul
                        close_paren_pos = components_raw.find(')', open_paren_pos)
                        if close_paren_pos == -1:
                            # Kapanış parantezi components_raw içinde yok, stats_text'ten devam et
                            remaining_text = stats_text[end_pos:end_pos + 300]
                            close_in_remaining = remaining_text.find(')')
                            if close_in_remaining != -1:
                                # Kapanış parantezi bulundu, components'i genişlet
                                components_raw = stats_text[start_pos:end_pos + close_in_remaining + 1].strip()
                    
                    components = re.sub(r'\s+', ' ', components_raw)
                    spell_data['components'] = components
                    
                    # V, S, M kontrolü
                    if 'V' in components.upper():
                        spell_data['verbal'] = True
                    if 'S' in components.upper():
                        spell_data['somatic'] = True
                    if 'M' in components.upper():
                        spell_data['material'] = True
                        # Material component açıklamasını çıkar
                        m_match = re.search(r'M\s*\(([^)]+)\)', components, re.I)
                        if m_match:
                            spell_data['material_component'] = m_match.group(1).strip()
            
            # Duration - DÜZELTİLDİ V3 (daha akıllı temizleme)
            if not spell_data.get('duration'):
                # Duration başlangıcını bul
                dur_start_match = re.search(r'Duration[:\s]+', stats_text, re.I)
                if dur_start_match:
                    start_pos = dur_start_match.end()
                    # "You", "Your", "A ", "At Higher", "This spell" veya satır sonuna kadar
                    dur_end_patterns = [
                        r'(?:You |Your |A [a-z]+|At Higher|This spell|$)',
                        r'(?=You |Your |At Higher|This spell|$)',
                    ]
                    
                    for end_pattern in dur_end_patterns:
                        dur_end_match = re.search(end_pattern, stats_text[start_pos:], re.I)
                        if dur_end_match:
                            duration_raw = stats_text[start_pos:start_pos + dur_end_match.start()].strip()
                            
                            # "You" ile başlayan cümleleri temizle
                            duration = re.sub(r'\s+You\s+.*$', '', duration_raw, flags=re.DOTALL)
                            duration = re.sub(r'\s+Your\s+.*$', '', duration, flags=re.DOTALL)
                            duration = re.sub(r'\s+A\s+[a-z]+\s+.*$', '', duration, flags=re.DOTALL)
                            duration = duration.strip()
                            
                            # Çok uzun olmamalı (200 karakter limit)
                            if duration and len(duration) <= 200:
                                spell_data['duration'] = re.sub(r'\s+', ' ', duration)
                                if 'concentration' in duration.lower():
                                    spell_data['concentration'] = True
                                if 'ritual' in duration.lower():
                                    spell_data['ritual'] = True
                                break
        
        # Eğer hala eksik veriler varsa, description'dan çıkarmaya çalış
        # (Bazı spell'lerde bu bilgiler description'ın başında olabilir)
        if not spell_data.get('casting_time') or not spell_data.get('range') or not spell_data.get('components') or not spell_data.get('duration'):
            # Tüm metni tekrar tara
            full_text_search = text_content[:3000]  # İlk 3000 karakter yeterli
            
            if not spell_data.get('casting_time'):
                ct_match = re.search(r'Casting\s+Time[:\s]+([^R\n]+?)(?:Range|$|You|A |Target)', full_text_search, re.I)
                if ct_match:
                    spell_data['casting_time'] = ct_match.group(1).strip()
            
            if not spell_data.get('range'):
                range_match = re.search(r'Range[:\s]+([^C\n]+?)(?:Components|Duration|$|You|A |Target)', full_text_search, re.I)
                if range_match:
                    spell_data['range'] = range_match.group(1).strip()
            
            if not spell_data.get('components'):
                comp_match = re.search(r'Components[:\s]+([^D\n]+?(?:\([^)]+\))?[^D]*?)(?:Duration|$|You|A |Target|Concentration)', full_text_search, re.I)
                if comp_match:
                    components = comp_match.group(1).strip()
                    # Parantez kapatılmamışsa düzelt
                    if components.count('(') > components.count(')'):
                        remaining = full_text_search[comp_match.end():comp_match.end()+100]
                        close_match = re.search(r'([^)]+)\)', remaining, re.I)
                        if close_match:
                            components += close_match.group(0)
                    spell_data['components'] = re.sub(r'\s+', ' ', components)
                    # V, S, M kontrolü
                    if 'V' in components.upper():
                        spell_data['verbal'] = True
                    if 'S' in components.upper():
                        spell_data['somatic'] = True
                    if 'M' in components.upper():
                        spell_data['material'] = True
                        m_match = re.search(r'M\s*\(([^)]+)\)', components, re.I)
                        if m_match:
                            spell_data['material_component'] = m_match.group(1).strip()
            
            if not spell_data.get('duration'):
                dur_match = re.search(r'Duration[:\s]+([^Y\n]+?)(?:You |A |Target|At Higher|This spell|$)', full_text_search, re.I | re.DOTALL)
                if dur_match:
                    duration = dur_match.group(1).strip()
                    # "You" ile başlayan cümleleri temizle
                    duration = re.sub(r'\s*You\s+.*$', '', duration, flags=re.DOTALL)
                    duration = re.sub(r'\s*Your\s+.*$', '', duration, flags=re.DOTALL)
                    duration = re.sub(r'\s*A\s+[a-z]+.*$', '', duration, flags=re.DOTALL)
                    duration = duration.strip()
                    if duration and len(duration) < 200:
                        spell_data['duration'] = re.sub(r'\s+', ' ', duration)
                        if 'concentration' in duration.lower():
                            spell_data['concentration'] = True
                        if 'ritual' in duration.lower():
                            spell_data['ritual'] = True
        
        # Description - 3. paragraftan itibaren al (ilk iki paragraf level/school ve stats)
        description_parts = []
        for i, p in enumerate(paragraphs):
            if i < 2:  # İlk iki paragrafı atla
                continue
            text = p.get_text(strip=True)
            if (len(text) > 30 and 
                'Green Ronin' not in text and 
                'OGN' not in text and
                'Open Gaming' not in text and
                'Copyright' not in text and
                'Join Our Discord' not in text and
                'Subscribe' not in text and
                'Casting Time' not in text and  # Stats'ı description'dan çıkar
                'Range:' not in text and
                'Components:' not in text and
                'Duration:' not in text):
                description_parts.append(text)
        
        if description_parts:
            spell_data['description'] = '\n\n'.join(description_parts)
        
        # Classes - Spell lists sayfalarından bulunmalı, şimdilik boş bırak
        # (Daha sonra spell lists'ten çekilecek)
        spell_data['classes'] = []
        
        return spell_data
    
    def scrape_all_spells(self, max_spells: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm spell'leri çek"""
        print("=" * 70)
        print("5ESRD.COM SPELLS ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü - DÜZELTİLDİ (cache'deki spell'leri kullan, eksikleri çek)
        cache_file = Path("data/cache/spells_cache.json")
        spells = {}
        cached_spells = {}
        
        if not force_refresh and cache_file.exists():
            print(f"📦 Cache dosyası bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('spells'):
                    cached_spells = cached['spells']
                    spells.update(cached_spells)
                    print(f"  ✅ {len(cached_spells)} spell cache'den yüklendi")
        
        # Spell linklerini çek
        spell_links = self.scrape_all_spell_links()
        
        # Eğer max_spells varsa, sadece ilk N spell'i al
        if max_spells:
            spell_links = spell_links[:max_spells]
            print(f"  ⚠️  İlk {max_spells} spell çekilecek (test modu)")
        else:
            # Cache'de olmayan spell'leri filtrele - DÜZELTİLDİ
            cached_names = set(cached_spells.keys())
            spell_links = [(name, url) for name, url in spell_links if name not in cached_names]
            if spell_links:
                print(f"  🔄 {len(spell_links)} yeni spell çekilecek ({len(cached_names)} zaten cache'de)")
            else:
                print("  ✅ Tüm spell'ler zaten cache'de!")
                return cached_spells
        
        total = len(spell_links)
        
        print(f"\n📖 {total} spell detayı çekiliyor...")
        print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(spell_links, 1):
            if i % 10 == 0:
                successful = len(spells)
                print(f"  ... {i}/{total} spell çekildi ({successful} başarılı)")
                # Her 50 spell'de bir cache'e kaydet (ilerlemeyi koru)
                if i % 50 == 0:
                    all_spells_temp = {**cached_spells, **spells}
                    cache_data = {
                        'total': len(all_spells_temp),
                        'spells': all_spells_temp,
                        'source': '5esrd.com',
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'progress': f'{i}/{total}'
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 İlerleme kaydedildi: {successful} yeni spell, toplam {len(all_spells_temp)}")
            
            spell_data = self.scrape_spell_detail(url, name)
            if spell_data and spell_data.get('name'):
                spells[spell_data['name']] = spell_data
        
        print(f"\n✅ {len(spells)} yeni spell başarıyla çekildi")
        print(f"   Toplam: {len(spells) + len(cached_spells)} spell (cache dahil)")
        
        # Final cache'e kaydet
        all_spells = {**cached_spells, **spells}
        cache_data = {
            'total': len(all_spells),
            'spells': all_spells,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache'e kaydedildi: {cache_file}")
        
        return all_spells
    
    def scrape_all_feat_links(self) -> List[tuple]:
        """Tüm feat linklerini çek - DÜZELTİLDİ (Feats Scraping)"""
        print("🔍 Feat linkleri çekiliyor...")
        
        # 5esrd.com'da feat'ler /database/feats/ altında
        url = f"{self.BASE_URL}/database/feats"
        
        soup = self._get(url)
        if not soup:
            print("❌ Feats database sayfası bulunamadı!")
            return []
        
        feat_links = []
        
        # Feat linklerini bul - /database/feats/ içeren ve anlamlı text'i olan linkler
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # /database/feats/ içeren ve feat detay sayfası olan linkler
            # Format: /database/feats/[feat-name]/
            if '/database/feats/' in href.lower() and text and len(text) < 100 and text != 'Feats':
                # List/index sayfalarını filtrele
                if any(skip in href.lower() for skip in ['/feats', '/database/feats', 'list', 'index', 'category']):
                    # Eğer /database/feats/ ile bitmiyorsa ve bir feat adı içeriyorsa (kısa çizgi ile ayrılmış)
                    if not href.lower().endswith('/feats/') and not href.lower().endswith('/feats'):
                        # Feat detay sayfası gibi görünüyor (örn: /database/feats/a-taste-of-power/)
                        pass  # Devam et
                    else:
                        continue  # List sayfası, atla
                
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(url, href)
                
                # Feat detay sayfası kontrolü - URL'de feat adı olmalı (kısa çizgi ile ayrılmış kelimeler)
                if '/database/feats/' in full_url.lower() and full_url.lower().count('/') >= 4:
                    # Örnek: /database/feats/a-taste-of-power/ -> 4+ slash var
                    feat_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_links = list(set(feat_links))
        print(f"  ✅ {len(unique_links)} unique feat linki bulundu")
        return unique_links
    
    def scrape_feat_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Feat detay sayfasını çek - DÜZELTİLDİ (Feats Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        feat_data = {
            "name": name,
            "prerequisite": None,
            "description": "",
            "source": url
        }
        
        # Tüm paragrafları al
        paragraphs = main_content.find_all('p')
        
        # Metni al
        text_content = main_content.get_text()
        
        # Prerequisite - DÜZELTİLDİ (Feats Scraping)
        # Format: "Prerequisite: Strength 13 or higher" veya "Prerequisite: None"
        prereq_patterns = [
            r'Prerequisite[:\s]+([^D\n]+?)(?:Description|$|You |A |At Higher|This feat|Benefits|Special)',
            r'Prerequisites?[:\s]+([^D\n]+?)(?:Description|$|You |A |Benefits|Special)',
            r'Prerequisite[:\s]+(.+?)(?:\n\n|$|Description)',
        ]
        
        for pattern in prereq_patterns:
            prereq_match = re.search(pattern, text_content[:1000], re.I)
            if prereq_match:
                prerequisite = prereq_match.group(1).strip()
                # "None" veya boş değilse kaydet
                if prerequisite and prerequisite.lower() not in ['none', 'none.', '']:
                    feat_data['prerequisite'] = prerequisite
                break
        
        # Description - DÜZELTİLDİ V2 (Feats Scraping - iyileştirildi)
        description_parts = []
        
        # İlk olarak, "Benefit(s):" veya "Description:" gibi başlıkları ara
        benefit_pattern = re.search(r'(?:Benefit|Benefits|Description)[:\s]+(.+?)(?:\n\n|$)', text_content, re.I | re.DOTALL)
        if benefit_pattern:
            description_text = benefit_pattern.group(1).strip()
            # İlk 2000 karakteri al
            description_text = description_text[:2000]
            description_parts.append(description_text)
        else:
            # Benefit bulunamadıysa, paragrafları kontrol et
            start_collecting = False
            found_prerequisite = False
            
            for i, p in enumerate(paragraphs):
                text = p.get_text(strip=True)
                
                # Prerequisite paragrafını işaretle
                if 'prerequisite' in text.lower() and i < 5:
                    found_prerequisite = True
                    start_collecting = True
                    continue
                
                # Description/Benefit başlığı varsa, ondan sonraki paragrafları al
                if 'benefit' in text.lower() or 'description' in text.lower():
                    if i < 10:  # İlk 10 paragrafta olmalı
                        start_collecting = True
                        # Benefit text'ini de ekle
                        if len(text) > 50:
                            description_parts.append(text)
                        continue
                
                # Copyright, footer metinlerini atla
                skip_texts = [
                    'Green Ronin', 'OGN', 'Open Gaming', 'Copyright',
                    'Join Our Discord', 'Subscribe', 'license attribution',
                    'see the full license', 'This is not the complete license'
                ]
                
                should_skip = any(skip in text for skip in skip_texts)
                
                if (len(text) > 20 and not should_skip and
                    'Prerequisite' not in text and 'Prerequisites' not in text):
                    
                    # Prerequisite'ten sonra veya 3. paragraftan itibaren topla
                    if start_collecting or (found_prerequisite and i > 1) or (not found_prerequisite and i >= 1):
                        description_parts.append(text)
        
        # Description'ı temizle ve birleştir
        if description_parts:
            # Lisans metinlerini temizle
            cleaned_parts = []
            for part in description_parts:
                # Lisans metinlerini filtrele
                if any(skip in part for skip in ['license attribution', 'see the full license', 'This is not the complete']):
                    continue
                # Çok kısa paragrafları atla (genellikle navigation/header)
                if len(part) > 20:
                    cleaned_parts.append(part)
            
            if cleaned_parts:
                feat_data['description'] = '\n\n'.join(cleaned_parts[:10])  # En fazla 10 paragraf
        
        return feat_data
    
    def scrape_all_feats(self, max_feats: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm feat'leri çek - DÜZELTİLDİ (Feats Scraping)"""
        print("=" * 70)
        print("5ESRD.COM FEATS ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü
        cache_file = Path("data/cache/feats_cache.json")
        feats = {}
        cached_feats = {}
        
        if not force_refresh and cache_file.exists():
            print(f"📦 Cache dosyası bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('feats'):
                    cached_feats = cached['feats']
                    feats.update(cached_feats)
                    print(f"  ✅ {len(cached_feats)} feat cache'den yüklendi")
        
        # Feat linklerini çek
        feat_links = self.scrape_all_feat_links()
        
        if not feat_links:
            print("  ⚠️  Feat linkleri bulunamadı! Mevcut cache'i döndürüyoruz.")
            return cached_feats
        
        # Eğer max_feats varsa, sadece ilk N feat'i al
        if max_feats:
            feat_links = feat_links[:max_feats]
            print(f"  ⚠️  İlk {max_feats} feat çekilecek (test modu)")
        else:
            # Cache'de olmayan feat'leri filtrele
            cached_names = set(cached_feats.keys())
            feat_links = [(name, url) for name, url in feat_links if name not in cached_names]
            if feat_links:
                print(f"  🔄 {len(feat_links)} yeni feat çekilecek ({len(cached_names)} zaten cache'de)")
            else:
                print("  ✅ Tüm feat'ler zaten cache'de!")
                return cached_feats
        
        total = len(feat_links)
        
        print(f"\n📖 {total} feat detayı çekiliyor...")
        print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(feat_links, 1):
            if i % 10 == 0:
                successful = len(feats)
                print(f"  ... {i}/{total} feat çekildi ({successful} başarılı)")
                # Her 50 feat'te bir cache'e kaydet (ilerlemeyi koru)
                if i % 50 == 0:
                    all_feats_temp = {**cached_feats, **feats}
                    cache_data = {
                        'total': len(all_feats_temp),
                        'feats': all_feats_temp,
                        'source': '5esrd.com',
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'progress': f'{i}/{total}'
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 İlerleme kaydedildi: {successful} yeni feat, toplam {len(all_feats_temp)}")
            
            feat_data = self.scrape_feat_detail(url, name)
            if feat_data and feat_data.get('name'):
                feats[feat_data['name']] = feat_data
        
        print(f"\n✅ {len(feats)} yeni feat başarıyla çekildi")
        print(f"   Toplam: {len(feats) + len(cached_feats)} feat (cache dahil)")
        
        # Final cache'e kaydet
        all_feats = {**cached_feats, **feats}
        cache_data = {
            'total': len(all_feats),
            'feats': all_feats,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache'e kaydedildi: {cache_file}")
        
        return all_feats
    
    def scrape_all_class_links(self) -> List[tuple]:
        """Tüm class linklerini çek - DÜZELTİLDİ (Classes Scraping)"""
        print("🔍 Class linkleri çekiliyor...")
        url = f"{self.BASE_URL}/classes/"
        
        soup = self._get(url)
        if not soup:
            print("❌ Classes sayfası bulunamadı!")
            return []
        
        class_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Core classes için: /database/class/class-name/ pattern'ini kullan
            if '/database/class/' in href.lower() and text and len(text) < 50 and len(text) > 1:
                # 3rd party veya prestige class'ları filtrele
                if '3rd-party' not in href.lower() and 'prestige' not in href.lower():
                    if href.endswith('/'):
                        if href.startswith('/'):
                            full_url = self.BASE_URL + href
                        else:
                            full_url = urljoin(url, href)
                        class_links.append((text, full_url))
        
        # Tekrar edenleri kaldır ve sırala
        unique_links = list(set(class_links))
        unique_links.sort(key=lambda x: x[0])  # İsme göre sırala
        print(f"  ✅ {len(unique_links)} unique core class linki bulundu")
        return unique_links
    
    def scrape_class_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Class detay sayfasını çek - DÜZELTİLDİ (Classes Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        class_data = {
            "name": name,
            "hit_die": "d8",  # Default
            "primary_ability": [],
            "saving_throws": [],
            "class_skills": [],
            "skill_choices": 2,  # Default
            "proficiencies": {
                "armor": [],
                "weapons": [],
                "tools": [],
                "languages": []
            },
            "starting_equipment_options": [],
            "class_features": {},
            "spellcasting": None,  # Spellcaster class'lar için
            "source": url
        }
        
        # Tüm metni al
        text_content = main_content.get_text()
        
        # Paragrafları al (structured parsing için)
        paragraphs = main_content.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        
        # Hit Die - DÜZELTİLDİ (Classes Scraping - iyileştirildi)
        hit_die_patterns = [
            r'Hit Dice[:\s]+1d(\d+)\s+per',
            r'Hit Dice[:\s]+d(\d+)',
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Die[:\s]+(\d+)',
            r'(\d+)d(\d+)\s+Hit Die',
        ]
        
        # Önce paragraflarda ara
        for para_text in paragraph_texts:
            for pattern in hit_die_patterns:
                match = re.search(pattern, para_text, re.I)
                if match:
                    hit_die_val = match.group(1) if match.lastindex >= 1 else match.group(2)
                    class_data['hit_die'] = f"d{hit_die_val}"
                    break
            if class_data['hit_die'] != "d8":
                break
        
        # Paragraflarda bulunamazsa, tüm metinde ara
        if class_data['hit_die'] == "d8":
            for pattern in hit_die_patterns:
                match = re.search(pattern, text_content[:3000], re.I)
                if match:
                    hit_die_val = match.group(1) if match.lastindex >= 1 else (match.group(2) if match.lastindex >= 2 else None)
                    if hit_die_val:
                        class_data['hit_die'] = f"d{hit_die_val}"
                        break
        
        # Primary Ability - DÜZELTİLDİ (Classes Scraping)
        ability_names = {
            "strength": "Strength",
            "dexterity": "Dexterity",
            "constitution": "Constitution",
            "intelligence": "Intelligence",
            "wisdom": "Wisdom",
            "charisma": "Charisma"
        }
        
        primary_ability_patterns = [
            r'Primary Ability[:\s]+([A-Za-z, ]+?)(?:\n|$)',
            r'Primary Abilities?[:\s]+([A-Za-z, ]+?)(?:\n|$)',
        ]
        
        for pattern in primary_ability_patterns:
            match = re.search(pattern, text_content[:2000], re.I)
            if match:
                abilities_text = match.group(1).strip()
                # Virgülle veya "and" ile ayrılmış ability'leri parse et
                abilities = re.split(r'[,and]+', abilities_text, flags=re.I)
                for ab in abilities:
                    ab_clean = ab.strip().lower().capitalize()
                    if ab_clean in ability_names.values():
                        if ab_clean not in class_data['primary_ability']:
                            class_data['primary_ability'].append(ab_clean)
                break
        
        # Primary Ability - DÜZELTİLDİ (Classes Scraping - eğer paragrafta bulunamazsa, mevcut veriden tahmin et)
        # Genellikle spellcasting ability ile aynı veya class'a göre belirlenir
        if not class_data['primary_ability']:
            # Class name'e göre default primary ability
            class_name_lower = name.lower()
            if 'barbarian' in class_name_lower:
                class_data['primary_ability'] = ["Strength"]
            elif 'bard' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'cleric' in class_name_lower:
                class_data['primary_ability'] = ["Wisdom"]
            elif 'druid' in class_name_lower:
                class_data['primary_ability'] = ["Wisdom"]
            elif 'fighter' in class_name_lower:
                class_data['primary_ability'] = ["Strength", "Dexterity"]
            elif 'monk' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity", "Wisdom"]
            elif 'paladin' in class_name_lower:
                class_data['primary_ability'] = ["Strength", "Charisma"]
            elif 'ranger' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity", "Wisdom"]
            elif 'rogue' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity"]
            elif 'sorcerer' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'warlock' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'wizard' in class_name_lower:
                class_data['primary_ability'] = ["Intelligence"]
        
        # Proficiencies - DÜZELTİLDİ (Classes Scraping - iyileştirildi)
        # Proficiencies genellikle tek bir paragrafta: "Armor: ... Weapons: ... Tools: ... Saving Throws: ... Skills: ..."
        proficiencies_para = None
        for para_text in paragraph_texts:
            if 'Armor:' in para_text and ('Weapons:' in para_text or 'Saving Throws:' in para_text):
                proficiencies_para = para_text
                break
        
        # Skill names list (all D&D 5e skills)
        skill_names = [
            "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
            "History", "Insight", "Intimidation", "Investigation", "Medicine",
            "Nature", "Perception", "Performance", "Persuasion", "Religion",
            "Sleight of Hand", "Stealth", "Survival"
        ]
        
        if proficiencies_para:
            # Armor
            armor_match = re.search(r'Armor[:\s]+([^W]+?)(?:Weapons|Tools|Saving|Skills|$)', proficiencies_para, re.I)
            if armor_match:
                armor_text = armor_match.group(1).strip()
                if 'all armor' in armor_text.lower() or 'all' in armor_text.lower():
                    class_data['proficiencies']['armor'] = ["All armor", "Shields"]
                elif 'shields' in armor_text.lower():
                    armor_types = re.split(r'[,]', armor_text)
                    for armor in armor_types:
                        armor_clean = armor.strip()
                        if armor_clean:
                            if 'shield' in armor_clean.lower():
                                if "Shields" not in class_data['proficiencies']['armor']:
                                    class_data['proficiencies']['armor'].append("Shields")
                            elif armor_clean and armor_clean not in class_data['proficiencies']['armor']:
                                class_data['proficiencies']['armor'].append(armor_clean)
            
            # Weapons - DÜZELTİLDİ (iyileştirildi - pattern düzeltildi)
            # Format: "Weapons: Simple weapons, martial weaponsTools:..." (boşluk olmayabilir)
            weapon_patterns = [
                r'Weapons?[:\s]+([^T]+?)(?:Tools|Saving|Skills|$)',
                r'Weapons?[:\s]+([A-Za-z\s,]+?)(?:Tools|Saving|Skills|$)',
            ]
            
            for pattern in weapon_patterns:
                weapon_match = re.search(pattern, proficiencies_para, re.I)
                if weapon_match:
                    weapon_text = weapon_match.group(1).strip()
                    # "Simple weapons, martial weapons" veya "Simple weapons,martial weapons" gibi formatları parse et
                    if 'simple' in weapon_text.lower() and 'martial' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Simple weapons", "Martial weapons"]
                        break
                    elif 'simple' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Simple weapons"]
                        break
                    elif 'martial' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Martial weapons"]
                        break
                    else:
                        # Virgülle ayrılmış weapon'ları parse et
                        weapon_types = re.split(r'[,]', weapon_text)
                        for weapon in weapon_types:
                            weapon_clean = weapon.strip()
                            if weapon_clean and weapon_clean not in class_data['proficiencies']['weapons']:
                                class_data['proficiencies']['weapons'].append(weapon_clean)
                        if class_data['proficiencies']['weapons']:
                            break
            
            # Tools
            tool_match = re.search(r'Tools?[:\s]+([^S]+?)(?:Saving|Skills|$)', proficiencies_para, re.I)
            if tool_match:
                tool_text = tool_match.group(1).strip()
                if 'none' not in tool_text.lower():
                    tool_types = re.split(r'[,]', tool_text)
                    for tool in tool_types:
                        tool_clean = tool.strip()
                        if tool_clean and tool_clean not in class_data['proficiencies']['tools']:
                            class_data['proficiencies']['tools'].append(tool_clean)
            
            # Saving Throws - DÜZELTİLDİ (paragraftan parse - iyileştirildi)
            # Format: "Saving Throws:Strength,ConstitutionSkills:..." (boşluk olmayabilir, Skills ile bitiyor)
            saving_throws_patterns = [
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+)*?)(?:Skills|$)',
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+,\s*[A-Z][a-z]+)(?:Skills|$)',
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+,\s*[A-Z][a-z]+)',
            ]
            
            for pattern in saving_throws_patterns:
                saving_throws_match = re.search(pattern, proficiencies_para, re.I)
                if saving_throws_match:
                    throws_text = saving_throws_match.group(1).strip()
                    # Virgül veya boşlukla ayrılmış ability'leri parse et
                    throws = re.split(r'[,]+', throws_text)
                    for throw in throws:
                        throw_clean = throw.strip()
                        # Ability name'i tam olarak eşleştir (capitalize etmeden önce kontrol et)
                        for ability in ability_names.values():
                            if (ability.lower() == throw_clean.lower() or 
                                throw_clean.lower() == ability.lower()[:len(throw_clean)] or
                                ability.lower().startswith(throw_clean.lower())):
                                if ability not in class_data['saving_throws']:
                                    class_data['saving_throws'].append(ability)
                                break
                    if len(class_data['saving_throws']) >= 2:  # En az 2 saving throw olmalı
                        break
            
            # Class Skills - DÜZELTİLDİ (paragraftan parse - iyileştirildi)
            # Format: "Skills: Choose two skills fromAcrobatic..." veya "Skills: Choose from Acrobatics, Animal Handling..."
            skills_patterns = [
                r'Skills?[:\s]+Choose\s+(\d+)\s+skills?\s+from\s+([A-Z][a-z\s,]+?)(?:\n|$)',
                r'Skills?[:\s]+Choose\s+(\d+)\s+from\s+([A-Z][a-z\s,]+?)(?:\n|$)',
                r'Skills?[:\s]+([A-Z][a-z\s,]+?)(?:\n\n|\n[A-Z]|$)',
            ]
            
            for pattern in skills_patterns:
                skills_match = re.search(pattern, proficiencies_para, re.I | re.DOTALL)
                if skills_match:
                    # Skill count
                    if skills_match.lastindex >= 1 and skills_match.group(1).isdigit():
                        class_data['skill_choices'] = int(skills_match.group(1))
                    
                    # Skills text
                    skills_text = skills_match.group(2) if skills_match.lastindex >= 2 else skills_match.group(1)
                    if skills_text:
                        # Skills listesini parse et (virgül veya "and" ile ayrılmış)
                        skills_list = re.split(r'[,and]+', skills_text, flags=re.I)
                        for skill in skills_list:
                            skill_clean = skill.strip()
                            if skill_clean:
                                # Skill ismini eşleştir (tam isim veya kısmi)
                                for known_skill in skill_names:
                                    # Exact match veya substring match
                                    if (known_skill.lower() == skill_clean.lower() or 
                                        known_skill.lower().startswith(skill_clean.lower()) or
                                        skill_clean.lower() in known_skill.lower()):
                                        if known_skill not in class_data['class_skills']:
                                            class_data['class_skills'].append(known_skill)
                                        break
                    if class_data['class_skills']:
                        break
        
        # Class Features - DÜZELTİLDİ (Classes Scraping - Level bazlı tablo parsing)
        # Level table'ını bul (1-20 level features)
        tables = main_content.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 5:  # En az birkaç satır olmalı
                # İlk satır header olabilir
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                # "Level" veya "Features" kolonunu bul
                level_col = None
                features_col = None
                
                for i, header in enumerate(headers):
                    if 'level' in header.lower():
                        level_col = i
                    if 'feature' in header.lower() or 'class' in header.lower():
                        features_col = i
                
                # Eğer header yoksa, ilk kolon level, son kolon features olabilir
                if level_col is None:
                    level_col = 0
                if features_col is None:
                    features_col = len(headers) - 1
                
                # Satırları parse et
                for row in rows[1:]:  # İlk satır header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) > max(level_col, features_col):
                        level_text = cells[level_col].get_text(strip=True) if level_col < len(cells) else ""
                        features_text = cells[features_col].get_text(strip=True) if features_col < len(cells) else ""
                        
                        # Level numarasını çıkar (örn: "1st", "2nd", "3rd", "4th" -> 1, 2, 3, 4)
                        level_match = re.search(r'(\d+)', level_text)
                        if level_match and features_text:
                            level = int(level_match.group(1))
                            # Features'ları parse et (virgülle ayrılmış)
                            features = [f.strip() for f in re.split(r'[,]', features_text) if f.strip()]
                            
                            if level not in class_data['class_features']:
                                class_data['class_features'][str(level)] = {
                                    "features": features,
                                    "choices": {}
                                }
                            else:
                                # Mevcut features'lara ekle
                                existing_features = class_data['class_features'][str(level)].get("features", [])
                                for feature in features:
                                    if feature not in existing_features:
                                        existing_features.append(feature)
                                class_data['class_features'][str(level)]["features"] = existing_features
                
                # Tablo bulundu, diğer tablolara bakmaya gerek yok
                if class_data['class_features']:
                    break
        
        # Starting Equipment - DÜZELTİLDİ (Classes Scraping)
        # "You start with the following equipment" veya "Starting Equipment" bölümünü bul
        equipment_section_patterns = [
            r'You start with the following equipment[:\s]+(.+?)(?:\n\n|\n[A-Z]|Class Features|$)',
            r'Starting Equipment[:\s]+(.+?)(?:\n\n|\n[A-Z]|Class Features|$)',
        ]
        
        for pattern in equipment_section_patterns:
            equipment_match = re.search(pattern, text_content[:5000], re.I | re.DOTALL)
            if equipment_match:
                equipment_text = equipment_match.group(1).strip()
                # Equipment options'ları parse et (genellikle liste halinde)
                # Format: "(a) item1, item2 or (b) item3, item4"
                options = re.split(r'\([a-z]\)', equipment_text, flags=re.I)
                for option in options:
                    option_clean = option.strip()
                    if option_clean and len(option_clean) > 10:
                        # "or" ile ayrılmış alternatifleri bul
                        items = re.split(r'\s+or\s+', option_clean, flags=re.I)
                        equipment_list = []
                        for item_text in items:
                            # Virgülle ayrılmış item'ları parse et
                            item_parts = re.split(r'[,]', item_text)
                            for item_part in item_parts:
                                item_clean = item_part.strip()
                                if item_clean and len(item_clean) > 2:
                                    equipment_list.append(item_clean)
                        if equipment_list:
                            class_data['starting_equipment_options'].append(equipment_list)
                break
        
        # Spellcasting - eğer spellcaster ise - DÜZELTİLDİ (daha iyi detection)
        # Spellcaster class'lar: Wizard, Sorcerer, Warlock, Cleric, Druid, Bard, Paladin, Ranger, Artificer
        spellcaster_classes = ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard', 'paladin', 'ranger', 'artificer']
        class_name_lower = name.lower()
        
        # Önce class name'e göre kontrol et (en güvenilir)
        is_spellcaster = class_name_lower in spellcaster_classes
        
        # Eğer class name'e göre spellcaster değilse, content'te spellcasting section'ı ara
        if not is_spellcaster:
            spellcasting_indicators = [
                r'Spellcasting\s+Ability',  # "Spellcasting Ability" başlığı
                r'Spell\s+Slots\s+per\s+Level',  # Spell slots tablosu
                r'Spells\s+Known',  # Spells Known section
                r'Spells\s+Prepared',  # Spells Prepared section
                r'Cantrips?\s+Known',  # Cantrips section
            ]
            
            # Sadece başlık veya section başlığı olarak geçiyorsa spellcaster
            for indicator in spellcasting_indicators:
                if re.search(indicator, text_content[:10000], re.I):
                    is_spellcaster = True
                    break
        
        if is_spellcaster:
            # Spellcasting ability'yi belirle
            spellcasting_ability = "Intelligence"  # Default
            if class_name_lower in ['wizard', 'artificer']:
                spellcasting_ability = "Intelligence"
            elif class_name_lower in ['sorcerer', 'warlock', 'bard', 'paladin']:
                spellcasting_ability = "Charisma"
            elif class_name_lower in ['cleric', 'druid', 'ranger']:
                spellcasting_ability = "Wisdom"
            elif class_data['primary_ability']:
                spellcasting_ability = class_data['primary_ability'][0]
            
            class_data['spellcasting'] = {
                "spellcasting_ability": spellcasting_ability,
                "spell_save_dc": 8,  # Base (8 + proficiency + ability modifier)
                "spell_attack_bonus": 0  # Base (proficiency + ability modifier)
            }
        else:
            class_data['spellcasting'] = None
        
        return class_data
    
    def scrape_all_race_links(self) -> List[tuple]:
        """Tüm core race linklerini çek - DÜZELTİLDİ (Races Scraping)"""
        print("[*] Race linkleri cekiliyor...")
        
        # Core races listesi (bilinen D&D 5e core races)
        core_races = [
            ("Dragonborn", f"{self.BASE_URL}/races/dragonborn/"),
            ("Dwarf", f"{self.BASE_URL}/races/dwarf/"),
            ("Elf", f"{self.BASE_URL}/races/elf/"),
            ("Gnome", f"{self.BASE_URL}/races/gnome/"),
            ("Halfling", f"{self.BASE_URL}/races/halfling/"),
            ("Half-Elf", f"{self.BASE_URL}/races/half-elf/"),
            ("Half-Orc", f"{self.BASE_URL}/races/half-orc/"),
            ("Human", f"{self.BASE_URL}/races/human/"),
            ("Tiefling", f"{self.BASE_URL}/races/tiefling/"),
        ]
        
        print(f"  [OK] {len(core_races)} core race linki hazir")
        return core_races
    
    def scrape_race_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Race detay sayfasını çek - DÜZELTİLDİ (Races Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        race_data = {
            "name": name,
            "ability_score_increase": {},
            "speed": 30,  # Default
            "traits": [],
            "languages": [],
            "extra_languages": 0,
            "size": "Medium",  # Default
            "source": url
        }
        
        # Tüm metni al
        text_content = main_content.get_text()
        
        # Paragrafları al (structured parsing için)
        paragraphs = main_content.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        
        # Ability Score Increase - DÜZELTİLDİ (Races Scraping)
        ability_names = {
            "strength": "strength", "dexterity": "dexterity", "constitution": "constitution",
            "intelligence": "intelligence", "wisdom": "wisdom", "charisma": "charisma"
        }
        
        asi_patterns = [
            r'Ability\s+Score\s+Increase[:\s]+(.+?)(?:\n\n|\n[A-Z]|Age|Alignment|Size|Speed|Traits|Languages|$)',
            r'ASI[:\s]+(.+?)(?:\n|$)',
        ]
        
        # Önce paragraflarda ara
        for para_text in paragraph_texts:
            for pattern in asi_patterns:
                match = re.search(pattern, para_text, re.I | re.DOTALL)
                if match:
                    asi_text = match.group(1).strip()
                    
                    # "Your Strength score increases by 2, and your Charisma score increases by 1."
                    # veya "Your all ability scores increase by 1"
                    # veya "Strength +2, Charisma +1"
                    
                    # "all" kontrolü
                    if 'all' in asi_text.lower() or 'each' in asi_text.lower():
                        all_match = re.search(r'(\d+)', asi_text)
                        if all_match:
                            race_data['ability_score_increase'] = {"all": int(all_match.group(1))}
                            break
                    else:
                        # Individual ability increases
                        ability_increases = {}
                        # Pattern: "YourStrengthscore increases by 2" (boşluk olmayabilir!)
                        # veya "Strength score increases by 2" (boşluklu)
                        # veya "Strength +2"
                        
                        # Önce "YourXxxscore increases by Y" formatını parse et (boşluksuz)
                        no_space_pattern = r'Your(\w+)score\s+increases?\s+by\s+(\d+)'
                        matches = re.finditer(no_space_pattern, asi_text, re.I)
                        for m in matches:
                            ability_word = m.group(1).lower()
                            value = int(m.group(2))
                            
                            # Ability name'i normalize et
                            for known_ability, key in ability_names.items():
                                if known_ability in ability_word or ability_word in known_ability:
                                    ability_increases[key] = value
                                    break
                        
                        # Eğer boşluksuz pattern çalışmadıysa, boşluklu pattern'leri dene
                        if not ability_increases:
                            ability_patterns = [
                                r'(\w+)\s+score\s+increases?\s+by\s+(\d+)',
                                r'(\w+)\s+(\d+)',
                                r'\+(\d+)\s+(\w+)',
                            ]
                            
                            for ab_pattern in ability_patterns:
                                matches = re.finditer(ab_pattern, asi_text, re.I)
                                for m in matches:
                                    if len(m.groups()) >= 2:
                                        # İki format var: (ability, value) veya (value, ability)
                                        if m.group(1).isdigit():
                                            value = int(m.group(1))
                                            ability = m.group(2).lower()
                                        else:
                                            ability = m.group(1).lower()
                                            value = int(m.group(2))
                                        
                                        # Ability name'i normalize et
                                        for known_ability, key in ability_names.items():
                                            if known_ability in ability or ability in known_ability:
                                                ability_increases[key] = value
                                                break
                                if ability_increases:
                                    break
                        
                        if ability_increases:
                            race_data['ability_score_increase'] = ability_increases
                            break
                    
                    if race_data['ability_score_increase']:
                        break
            if race_data['ability_score_increase']:
                break
        
        # Speed - DÜZELTİLDİ (Races Scraping)
        speed_patterns = [
            r'Speed[:\s]+Your\s+base\s+walking\s+speed\s+is\s+(\d+)\s+feet?',
            r'Speed[:\s]+(\d+)\s+ft',
            r'Base\s+Speed[:\s]+(\d+)',
            r'(\d+)\s+feet?\s+speed',
        ]
        
        for para_text in paragraph_texts:
            for pattern in speed_patterns:
                match = re.search(pattern, para_text, re.I)
                if match:
                    speed_val = int(match.group(1))
                    race_data['speed'] = speed_val
                    break
            if race_data['speed'] != 30:
                break
        
        # Traits - DÜZELTİLDİ (Races Scraping - iyileştirildi)
        # Traits hem başlık (H3, H4) hem de paragraf içinde olabilir
        # Örnek: "Draconic Ancestry", "Breath Weapon", "Damage Resistance"
        known_trait_names = [
            'Draconic Ancestry', 'Breath Weapon', 'Damage Resistance',
            'Darkvision', 'Fey Ancestry', 'Trance', 'Keen Senses',
            'Lucky', 'Brave', 'Halfling Nimbleness', 'Naturally Stealthy',
            'Stonecunning', 'Dwarven Toughness', 'Dwarven Resilience',
            'Gnome Cunning', 'Artificer\'s Lore', 'Tinker',
            'Mask of the Wild', 'Fleet of Foot', 'Elf Weapon Training',
            'Extra Language', 'Versatility', 'Skill Versatility',
            'Menacing', 'Relentless Endurance', 'Savage Attacks',
            'Hellish Resistance', 'Infernal Legacy'
        ]
        
        # Önce başlıklardan trait'leri bul
        headings = main_content.find_all(['h3', 'h4'])
        skip_headings = ['traits', 'variants', 'subrace', 'subraces', 'race features', 'race feature']
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            heading_lower = heading_text.lower()
            
            # Genel başlıkları atla
            if heading_lower in skip_headings:
                continue
            
            # "Dragonborn Traits" gibi race-specific genel başlıkları atla
            if heading_lower == 'traits' or (heading_lower.endswith('traits') and len(heading_lower.split()) <= 2):
                continue
            
            # Bilinen trait isimleri ile eşleştir
            for trait_name in known_trait_names:
                if trait_name.lower() == heading_lower or heading_lower.startswith(trait_name.lower()):
                    if trait_name not in race_data['traits']:
                        race_data['traits'].append(trait_name)
                    break
        
        # Sonra paragraflardan trait'leri bul (örn: "Draconic Ancestry: You have...")
        for para_text in paragraph_texts:
            # Pattern: "Trait Name: Description" formatını ara
            for trait_name in known_trait_names:
                # Trait name ile başlayan paragrafları bul
                trait_pattern = r'^' + re.escape(trait_name) + r'[:\s]+'
                if re.search(trait_pattern, para_text, re.I):
                    if trait_name not in race_data['traits']:
                        race_data['traits'].append(trait_name)
        
        # Languages - DÜZELTİLDİ (Races Scraping - iyileştirildi)
        language_names = [
            "Common", "Elvish", "Dwarvish", "Gnomish", "Halfling",
            "Orc", "Draconic", "Infernal", "Celestial", "Abyssal",
            "Giant", "Primordial", "Deep Speech", "Undercommon"
        ]
        
        # Languages paragrafını bul
        for para_text in paragraph_texts:
            if 'language' not in para_text.lower():
                continue
            
            # "Languages: You can speak, read, and write Common and Draconic."
            # Pattern: "Common and Draconic" kısmını yakala
            # Önce tüm language names'leri ara
            found_languages = []
            for lang_name in language_names:
                # Language name'i paragrafta ara (kelime sınırları ile)
                lang_pattern = r'\b' + re.escape(lang_name) + r'\b'
                if re.search(lang_pattern, para_text, re.I):
                    found_languages.append(lang_name)
            
            if found_languages:
                race_data['languages'] = found_languages
                break
        
        # Extra Languages
        extra_lang_patterns = [
            r'Extra\s+Languages?[:\s]+(\d+)',
            r'one\s+additional\s+language',
            r'additional\s+language',
        ]
        
        for pattern in extra_lang_patterns:
            match = re.search(pattern, text_content[:3000], re.I)
            if match:
                if match.group(1) if match.lastindex >= 1 else None:
                    race_data['extra_languages'] = int(match.group(1))
                else:
                    race_data['extra_languages'] = 1
                break
        
        # Size - DÜZELTİLDİ (Races Scraping)
        size_patterns = [
            r'Size[:\s]+(.+?)(?:\n|$)',
            r'Yoursizeis\s+(\w+)',
            r'size\s+is\s+(\w+)',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text_content[:2000], re.I)
            if match:
                size_text = match.group(1).strip().capitalize()
                if size_text in ["Small", "Medium", "Large", "Tiny", "Huge"]:
                    race_data['size'] = size_text
                    break
        
        return race_data
    
    def scrape_all_races(self, max_races: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm core races'leri scrape et - DÜZELTİLDİ (Races Scraping)"""
        print("[*] Tum core races scrape ediliyor...")
        
        # Cache kontrolü
        cache_file = Path("data/cache/races_cache.json")
        races = {}
        cached_races = {}
        
        if cache_file.exists() and not force_refresh:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    if cached.get('races'):
                        cached_races = cached['races']
                        races.update(cached_races)
                        print(f"  [OK] {len(cached_races)} race cache'den yuklendi")
            except Exception as e:
                print(f"  [UYARI] Cache yuklenemedi: {e}")
        
        # Race linklerini çek
        race_links = self.scrape_all_race_links()
        
        if not race_links:
            print("  [UYARI] Race linkleri bulunamadi! Mevcut cache'i donduruyoruz.")
            return races
        
        print(f"\n[*] {len(race_links)} race bulundu")
        
        # Cache'de olmayan race'leri filtrele
        cached_names = set(cached_races.keys())
        new_race_links = [(name, url) for name, url in race_links if name not in cached_names]
        
        if new_race_links:
            print(f"\n[*] {len(new_race_links)} yeni race cekilecek ({len(cached_names)} zaten cache'de)")
        else:
            print("\n[OK] Tum race'ler zaten cache'de!")
            return races
        
        # Max races limiti
        if max_races:
            new_race_links = new_race_links[:max_races]
        
        total = len(new_race_links)
        print(f"\n[*] {total} race detayi cekiliyor...")
        print("  (Bu islem uzun surebilir, lutfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(new_race_links, 1):
            if i % 2 == 0:
                successful = len([k for k in races.keys() if k not in cached_names])
                print(f"  ... {i}/{total} race cekildi ({successful} basarili)")
            
            race_data = self.scrape_race_detail(url, name)
            if race_data and race_data.get('name'):
                races[race_data['name']] = race_data
            else:
                print(f"  [UYARI] {name} scrape edilemedi")
        
        print(f"\n[OK] {len([k for k in races.keys() if k not in cached_names])} yeni race basariyla cekildi")
        print(f"   Toplam: {len(races)} race (cache dahil)")
        
        # Cache'e kaydet
        cache_data = {
            'total': len(races),
            'races': races,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"[*] Cache'e kaydedildi: {cache_file}")
        
        return races
    
    def scrape_equipment_from_table(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Equipment tablosundan verileri çek - DÜZELTİLDİ (Equipment Scraping)"""
        soup = self._get(url)
        if not soup:
            return []
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            return []
        
        equipment_list = []
        
        # Tüm tabloları bul
        tables = main_content.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:  # En az header + 1 data row
                continue
            
            # Header row'u bul (ilk row)
            header_row = rows[0]
            header_cells = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            # Header'da hangi kolonlar var?
            # Olası kolonlar: name, cost, damage, range, weight, properties, armor_class, strength_requirement, stealth, etc.
            
            # Kolon indexlerini bul
            name_idx = None
            cost_idx = None
            damage_idx = None
            range_idx = None
            weight_idx = None
            properties_idx = None
            ac_idx = None  # Armor Class (armor için)
            strength_idx = None  # Strength requirement (armor için)
            stealth_idx = None  # Stealth disadvantage (armor için)
            
            for i, header in enumerate(header_cells):
                if 'name' in header or header == '':
                    name_idx = i
                elif 'cost' in header or 'price' in header:
                    cost_idx = i
                elif 'damage' in header:
                    damage_idx = i
                elif 'range' in header:
                    range_idx = i
                elif 'weight' in header:
                    weight_idx = i
                elif 'properties' in header or 'property' in header:
                    properties_idx = i
                elif 'armor' in header and 'class' in header or 'ac' in header:
                    ac_idx = i
                elif 'strength' in header:
                    strength_idx = i
                elif 'stealth' in header:
                    stealth_idx = i
            
            # Eğer name_idx yoksa, ilk kolonu name olarak kabul et
            if name_idx is None:
                name_idx = 0
            
            # Data row'larını parse et (ikinci row'dan başla)
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                if len(cell_texts) <= name_idx:
                    continue
                
                # Name'i al
                name = cell_texts[name_idx].strip()
                
                # Eğer name boşsa veya başlık satırıysa atla
                if not name or name.lower() in ['(simple)', '(martial)', 'simple melee weapons', 'martial melee weapons', 
                                                 'simple ranged weapons', 'martial ranged weapons']:
                    continue
                
                # Equipment item oluştur
                item = {
                    "name": name,
                    "type": category.lower(),  # "weapon", "armor", "gear", "tool"
                    "category": category,
                    "source": url
                }
                
                # Cost
                if cost_idx is not None and cost_idx < len(cell_texts):
                    cost_text = cell_texts[cost_idx].strip()
                    if cost_text and cost_text not in ['—', '–', '-', '']:
                        item["cost"] = cost_text
                
                # Damage (weapon için)
                if damage_idx is not None and damage_idx < len(cell_texts):
                    damage_text = cell_texts[damage_idx].strip()
                    if damage_text and damage_text not in ['—', '–', '-', '']:
                        item["damage"] = damage_text
                
                # Range (ranged weapon için)
                if range_idx is not None and range_idx < len(cell_texts):
                    range_text = cell_texts[range_idx].strip()
                    if range_text and range_text not in ['—', '–', '-', '']:
                        item["range"] = range_text
                
                # Weight
                if weight_idx is not None and weight_idx < len(cell_texts):
                    weight_text = cell_texts[weight_idx].strip()
                    if weight_text and weight_text not in ['—', '–', '-', '']:
                        # "4 lb." veya "4 lb" veya "4" formatını parse et
                        weight_match = re.search(r'(\d+(?:\.\d+)?)', weight_text)
                        if weight_match:
                            try:
                                item["weight"] = float(weight_match.group(1))
                            except ValueError:
                                item["weight"] = weight_text
                        else:
                            item["weight"] = weight_text
                
                # Properties (weapon için)
                if properties_idx is not None and properties_idx < len(cell_texts):
                    properties_text = cell_texts[properties_idx].strip()
                    if properties_text and properties_text not in ['—', '–', '-', '']:
                        # "finesse,light,thrown" veya "versatile(1d10)" formatını parse et
                        properties = [p.strip() for p in re.split(r'[,;]', properties_text) if p.strip()]
                        if properties:
                            item["properties"] = properties
                
                # Armor Class (armor için)
                if ac_idx is not None and ac_idx < len(cell_texts):
                    ac_text = cell_texts[ac_idx].strip()
                    if ac_text and ac_text not in ['—', '–', '-', '']:
                        # "11 + Dex modifier" veya "18" formatını parse et
                        item["armor_class"] = ac_text
                
                # Strength requirement (armor için)
                if strength_idx is not None and strength_idx < len(cell_texts):
                    strength_text = cell_texts[strength_idx].strip()
                    if strength_text and strength_text not in ['—', '–', '-', '']:
                        strength_match = re.search(r'(\d+)', strength_text)
                        if strength_match:
                            item["strength_requirement"] = int(strength_match.group(1))
                
                # Stealth disadvantage (armor için)
                if stealth_idx is not None and stealth_idx < len(cell_texts):
                    stealth_text = cell_texts[stealth_idx].strip()
                    if 'disadvantage' in stealth_text.lower():
                        item["stealth_disadvantage"] = True
                
                equipment_list.append(item)
        
        return equipment_list
    
    def scrape_all_equipment_links(self) -> List[tuple]:
        """Tüm equipment kategorilerinin linklerini çek - DÜZELTİLDİ (Equipment Scraping)"""
        print("[*] Equipment kategori linkleri cekiliyor...")
        
        # Equipment kategorileri
        equipment_categories = [
            ("Weapons", f"{self.BASE_URL}/equipment/weapons/"),
            ("Armor", f"{self.BASE_URL}/equipment/armor/"),
            ("Adventuring Gear", f"{self.BASE_URL}/equipment/adventuring-gear/"),
            ("Tools", f"{self.BASE_URL}/equipment/tools/"),
        ]
        
        print(f"  [OK] {len(equipment_categories)} equipment kategori linki hazir")
        return equipment_categories
    
    def scrape_all_equipment(self, max_items: Optional[int] = None, force_refresh: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Tüm equipment'leri çek - DÜZELTİLDİ (Equipment Scraping)"""
        print("=" * 70)
        print("5ESRD.COM EQUIPMENT ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü
        cache_file = Path("data/cache/equipment_cache.json")
        equipment_data = {}
        cached_equipment = {}
        
        if not force_refresh and cache_file.exists():
            print(f"[*] Cache dosyasi bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('equipment'):
                    cached_equipment = cached['equipment']
                    equipment_data.update(cached_equipment)
                    print(f"  [OK] {sum(len(items) for items in cached_equipment.values())} equipment item cache'den yuklendi")
        
        # Equipment kategori linklerini çek
        equipment_links = self.scrape_all_equipment_links()
        
        if not equipment_links:
            print("  [UYARI] Equipment kategori linkleri bulunamadi! Mevcut cache'i donduruyoruz.")
            return cached_equipment
        
        # Her kategori için equipment'leri çek
        for category_name, url in equipment_links:
            if category_name in equipment_data and not force_refresh:
                print(f"  [ATLA] {category_name} zaten cache'de, atlaniyor...")
                continue
            
            print(f"\n[*] {category_name} cekiliyor...")
            print(f"   URL: {url}")
            
            items = self.scrape_equipment_from_table(url, category_name)
            
            if items:
                equipment_data[category_name] = items
                print(f"   [OK] {len(items)} {category_name.lower()} item cekildi")
            else:
                print(f"   [UYARI] {category_name} icin item bulunamadi")
        
        # Cache'e kaydet
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({"equipment": equipment_data}, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Equipment data '{cache_file}' dosyasina kaydedildi!")
        print(f"[*] Toplam {sum(len(items) for items in equipment_data.values())} equipment item cekildi.")
        
        return equipment_data


"""5esrd.com D&D 5e scraper"""

from bs4 import BeautifulSoup
from typing import Dict, List, Optional, Any


class Dnd5eSrdScraper:
    """5esrd.com'dan D&D 5e verilerini çeken scraper"""
    
    BASE_URL = "https://www.5esrd.com"
    
    def __init__(self, rate_limit: float = 1.5):
        """
        Args:
            rate_limit: İstekler arası bekleme süresi (saniye)
        """
        self.rate_limit = rate_limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """HTTP GET isteği yap ve BeautifulSoup döndür"""
        for attempt in range(retries):
            try:
                time.sleep(self.rate_limit)
                response = self.session.get(url, timeout=30)
                if response.status_code == 200:
                    return BeautifulSoup(response.content, 'html.parser')
                elif response.status_code == 404:
                    return None
                else:
                    print(f"  ⚠️  Status {response.status_code} for {url}")
                    if attempt < retries - 1:
                        time.sleep(2 ** attempt)  # Exponential backoff
            except Exception as e:
                print(f"  ⚠️  Error fetching {url}: {e}")
                if attempt < retries - 1:
                    time.sleep(2 ** attempt)
        return None
    
    def scrape_all_spell_links(self) -> List[tuple]:
        """Tüm spell linklerini çek"""
        print("🔍 Spell linkleri çekiliyor...")
        url = f"{self.BASE_URL}/database/spell/"
        
        soup = self._get(url)
        if not soup:
            print("❌ Spell database sayfası bulunamadı!")
            return []
        
        spell_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Spell linklerini bul
            if '/spell/' in href.lower() and text and len(text) < 100:
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                else:
                    full_url = urljoin(url, href)
                spell_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_links = list(set(spell_links))
        print(f"  ✅ {len(unique_links)} unique spell linki bulundu")
        return unique_links
    
    def scrape_spell_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Spell detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        spell_data = {
            "name": name,
            "level": None,
            "school": None,
            "casting_time": None,
            "range": None,
            "components": None,
            "duration": None,
            "description": "",
            "classes": [],
            "ritual": False,
            "concentration": False,
            "source": url
        }
        
        # Tüm paragrafları al
        paragraphs = main_content.find_all('p')
        
        # Metni al
        text_content = main_content.get_text()
        
        # İlk paragrafı al (genellikle level ve school burada)
        first_p = paragraphs[0] if paragraphs else None
        first_para_text = first_p.get_text(strip=True) if first_p else ""
        
        # Level ve School - DÜZELTİLDİ
        # Format: "3rd-levelevocation" veya "Conjurationcantrip" (boşluk yok!)
        # Önce ilk paragraftan bulmaya çalış
        level_school_patterns = [
            r'(\d+)(st|nd|rd|th)[\s-]*level([a-z]+)',  # "3rd-levelevocation"
            r'([a-z]+)cantrip',  # "Conjurationcantrip"
            r'(\d+)(st|nd|rd|th)[\s-]*level\s+([a-z]+)',  # "3rd-level evocation" (boşluklu)
            r'cantrip\s+([a-z]+)',  # "cantrip evocation" (boşluklu)
        ]
        
        found = False
        for pattern in level_school_patterns:
            match = re.search(pattern, first_para_text, re.I)
            if not match:
                match = re.search(pattern, text_content[:500], re.I)  # İlk 500 karakterde ara
            
            if match:
                if 'cantrip' in pattern.lower():
                    spell_data['level'] = 0
                    spell_data['school'] = match.group(1).capitalize() if match.lastindex >= 1 else None
                    found = True
                else:
                    level_num = match.group(1)
                    school = match.group(match.lastindex)  # Son grup school
                    spell_data['level'] = int(level_num)
                    spell_data['school'] = school.capitalize()
                    found = True
                break
        
        # Eğer bulunamadıysa, text'ten daha geniş arama yap
        if not found:
            # "3rd level" veya "1st level" gibi formatları ara
            level_match = re.search(r'(\d+)(st|nd|rd|th)\s*level', text_content, re.I)
            if level_match:
                spell_data['level'] = int(level_match.group(1))
                # School'u bul
                school_match = re.search(r'(?:level|spell)[\s-]+([a-z]+)', text_content[level_match.end():level_match.end()+50], re.I)
                if school_match:
                    spell_data['school'] = school_match.group(1).capitalize()
        
        # Casting Time, Range, Components, Duration - DÜZELTİLDİ (V2)
        # Format: "Casting Time:1 actionRange:60 feetComponents:V, SDuration:Instantaneous"
        # İkinci paragraf genellikle bu bilgileri içerir, ama bazı spell'lerde description'da olabilir
        
        # Önce ikinci paragraftan bulmaya çalış
        second_p = paragraphs[1] if len(paragraphs) > 1 else None
        stats_text = second_p.get_text(strip=True) if second_p else ""
        
        # Eğer ikinci paragrafta yeterli bilgi yoksa, text'in başından ara
        if not stats_text or 'Casting Time' not in stats_text:
            stats_match = re.search(r'Casting\s+Time[:\s]+.+?(?=You |A |Target|$)', text_content[:2000], re.I | re.DOTALL)
            if stats_match:
                stats_text = stats_match.group(0)
        
        # Eğer hala bulunamadıysa, description'dan da çıkarmaya çalış
        if not stats_text or len(stats_text) < 30:
            # Description paragraflarından ara
            for p in paragraphs[2:5] if len(paragraphs) > 2 else []:
                p_text = p.get_text(strip=True)
                if 'Casting Time' in p_text or 'Range:' in p_text or 'Components:' in p_text:
                    stats_text = p_text
                    break
        
        if stats_text:
            # Casting Time - Daha esnek regex
            if not spell_data.get('casting_time'):
                ct_patterns = [
                    r'Casting\s+Time[:\s]+([^R]+?)(?:Range|Components|Duration|$|You |A |Target)',
                    r'Casting\s+Time[:\s]+([^R]+?)(?=Range|$)',
                ]
                for pattern in ct_patterns:
                    ct_match = re.search(pattern, stats_text, re.I)
                    if ct_match:
                        casting_time = ct_match.group(1).strip()
                        spell_data['casting_time'] = re.sub(r'\s+', ' ', casting_time)
                        break
            
            # Range - DÜZELTİLDİ (case-insensitive ve daha akıllı)
            if not spell_data.get('range'):
                # "Range:" veya "Range :" sonrası, "Components" öncesi veya satır sonu
                range_patterns = [
                    r'Range[:\s]+([^C\n]+?)(?:Components|Duration|$)',  # Components veya Duration'a kadar
                    r'Range[:\s]+([a-zA-Z0-9\s\'-]+?)(?=Components|Duration|$)',  # Kelimeler ve boşluklar
                ]
                for pattern in range_patterns:
                    range_match = re.search(pattern, stats_text, re.I)
                    if range_match:
                        range_text = range_match.group(1).strip()
                        # "touch" gibi küçük harfli değerleri düzelt
                        range_text = range_text.capitalize() if range_text.islower() else range_text
                        spell_data['range'] = re.sub(r'\s+', ' ', range_text)
                        break
            
            # Components - DÜZELTİLDİ V4 (position-based, parantez desteği)
            if not spell_data.get('components'):
                # Components başlangıcını bul
                comp_start_match = re.search(r'Components[:\s]+', stats_text, re.I)
                if comp_start_match:
                    start_pos = comp_start_match.end()
                    
                    # Duration'un başlangıcını bul
                    dur_start_match = re.search(r'Duration[:\s]+', stats_text[start_pos:], re.I)
                    if dur_start_match:
                        end_pos = start_pos + dur_start_match.start()
                    else:
                        # Duration yoksa, "You" veya satır sonuna kadar
                        you_match = re.search(r'\bYou\s+', stats_text[start_pos:], re.I)
                        if you_match:
                            end_pos = start_pos + you_match.start()
                        else:
                            end_pos = start_pos + 200  # Fallback: 200 karakter
                    
                    components_raw = stats_text[start_pos:end_pos].strip()
                    
                    # Parantez kontrolü - açık parantez varsa kapatmayı bul
                    open_paren_pos = components_raw.find('(')
                    if open_paren_pos != -1:
                        # Kapanış parantezini bul
                        close_paren_pos = components_raw.find(')', open_paren_pos)
                        if close_paren_pos == -1:
                            # Kapanış parantezi components_raw içinde yok, stats_text'ten devam et
                            remaining_text = stats_text[end_pos:end_pos + 300]
                            close_in_remaining = remaining_text.find(')')
                            if close_in_remaining != -1:
                                # Kapanış parantezi bulundu, components'i genişlet
                                components_raw = stats_text[start_pos:end_pos + close_in_remaining + 1].strip()
                    
                    components = re.sub(r'\s+', ' ', components_raw)
                    spell_data['components'] = components
                    
                    # V, S, M kontrolü
                    if 'V' in components.upper():
                        spell_data['verbal'] = True
                    if 'S' in components.upper():
                        spell_data['somatic'] = True
                    if 'M' in components.upper():
                        spell_data['material'] = True
                        # Material component açıklamasını çıkar
                        m_match = re.search(r'M\s*\(([^)]+)\)', components, re.I)
                        if m_match:
                            spell_data['material_component'] = m_match.group(1).strip()
            
            # Duration - DÜZELTİLDİ V3 (daha akıllı temizleme)
            if not spell_data.get('duration'):
                # Duration başlangıcını bul
                dur_start_match = re.search(r'Duration[:\s]+', stats_text, re.I)
                if dur_start_match:
                    start_pos = dur_start_match.end()
                    # "You", "Your", "A ", "At Higher", "This spell" veya satır sonuna kadar
                    dur_end_patterns = [
                        r'(?:You |Your |A [a-z]+|At Higher|This spell|$)',
                        r'(?=You |Your |At Higher|This spell|$)',
                    ]
                    
                    for end_pattern in dur_end_patterns:
                        dur_end_match = re.search(end_pattern, stats_text[start_pos:], re.I)
                        if dur_end_match:
                            duration_raw = stats_text[start_pos:start_pos + dur_end_match.start()].strip()
                            
                            # "You" ile başlayan cümleleri temizle
                            duration = re.sub(r'\s+You\s+.*$', '', duration_raw, flags=re.DOTALL)
                            duration = re.sub(r'\s+Your\s+.*$', '', duration, flags=re.DOTALL)
                            duration = re.sub(r'\s+A\s+[a-z]+\s+.*$', '', duration, flags=re.DOTALL)
                            duration = duration.strip()
                            
                            # Çok uzun olmamalı (200 karakter limit)
                            if duration and len(duration) <= 200:
                                spell_data['duration'] = re.sub(r'\s+', ' ', duration)
                                if 'concentration' in duration.lower():
                                    spell_data['concentration'] = True
                                if 'ritual' in duration.lower():
                                    spell_data['ritual'] = True
                                break
        
        # Eğer hala eksik veriler varsa, description'dan çıkarmaya çalış
        # (Bazı spell'lerde bu bilgiler description'ın başında olabilir)
        if not spell_data.get('casting_time') or not spell_data.get('range') or not spell_data.get('components') or not spell_data.get('duration'):
            # Tüm metni tekrar tara
            full_text_search = text_content[:3000]  # İlk 3000 karakter yeterli
            
            if not spell_data.get('casting_time'):
                ct_match = re.search(r'Casting\s+Time[:\s]+([^R\n]+?)(?:Range|$|You|A |Target)', full_text_search, re.I)
                if ct_match:
                    spell_data['casting_time'] = ct_match.group(1).strip()
            
            if not spell_data.get('range'):
                range_match = re.search(r'Range[:\s]+([^C\n]+?)(?:Components|Duration|$|You|A |Target)', full_text_search, re.I)
                if range_match:
                    spell_data['range'] = range_match.group(1).strip()
            
            if not spell_data.get('components'):
                comp_match = re.search(r'Components[:\s]+([^D\n]+?(?:\([^)]+\))?[^D]*?)(?:Duration|$|You|A |Target|Concentration)', full_text_search, re.I)
                if comp_match:
                    components = comp_match.group(1).strip()
                    # Parantez kapatılmamışsa düzelt
                    if components.count('(') > components.count(')'):
                        remaining = full_text_search[comp_match.end():comp_match.end()+100]
                        close_match = re.search(r'([^)]+)\)', remaining, re.I)
                        if close_match:
                            components += close_match.group(0)
                    spell_data['components'] = re.sub(r'\s+', ' ', components)
                    # V, S, M kontrolü
                    if 'V' in components.upper():
                        spell_data['verbal'] = True
                    if 'S' in components.upper():
                        spell_data['somatic'] = True
                    if 'M' in components.upper():
                        spell_data['material'] = True
                        m_match = re.search(r'M\s*\(([^)]+)\)', components, re.I)
                        if m_match:
                            spell_data['material_component'] = m_match.group(1).strip()
            
            if not spell_data.get('duration'):
                dur_match = re.search(r'Duration[:\s]+([^Y\n]+?)(?:You |A |Target|At Higher|This spell|$)', full_text_search, re.I | re.DOTALL)
                if dur_match:
                    duration = dur_match.group(1).strip()
                    # "You" ile başlayan cümleleri temizle
                    duration = re.sub(r'\s*You\s+.*$', '', duration, flags=re.DOTALL)
                    duration = re.sub(r'\s*Your\s+.*$', '', duration, flags=re.DOTALL)
                    duration = re.sub(r'\s*A\s+[a-z]+.*$', '', duration, flags=re.DOTALL)
                    duration = duration.strip()
                    if duration and len(duration) < 200:
                        spell_data['duration'] = re.sub(r'\s+', ' ', duration)
                        if 'concentration' in duration.lower():
                            spell_data['concentration'] = True
                        if 'ritual' in duration.lower():
                            spell_data['ritual'] = True
        
        # Description - 3. paragraftan itibaren al (ilk iki paragraf level/school ve stats)
        description_parts = []
        for i, p in enumerate(paragraphs):
            if i < 2:  # İlk iki paragrafı atla
                continue
            text = p.get_text(strip=True)
            if (len(text) > 30 and 
                'Green Ronin' not in text and 
                'OGN' not in text and
                'Open Gaming' not in text and
                'Copyright' not in text and
                'Join Our Discord' not in text and
                'Subscribe' not in text and
                'Casting Time' not in text and  # Stats'ı description'dan çıkar
                'Range:' not in text and
                'Components:' not in text and
                'Duration:' not in text):
                description_parts.append(text)
        
        if description_parts:
            spell_data['description'] = '\n\n'.join(description_parts)
        
        # Classes - Spell lists sayfalarından bulunmalı, şimdilik boş bırak
        # (Daha sonra spell lists'ten çekilecek)
        spell_data['classes'] = []
        
        return spell_data
    
    def scrape_all_spells(self, max_spells: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm spell'leri çek"""
        print("=" * 70)
        print("5ESRD.COM SPELLS ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü - DÜZELTİLDİ (cache'deki spell'leri kullan, eksikleri çek)
        cache_file = Path("data/cache/spells_cache.json")
        spells = {}
        cached_spells = {}
        
        if not force_refresh and cache_file.exists():
            print(f"📦 Cache dosyası bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('spells'):
                    cached_spells = cached['spells']
                    spells.update(cached_spells)
                    print(f"  ✅ {len(cached_spells)} spell cache'den yüklendi")
        
        # Spell linklerini çek
        spell_links = self.scrape_all_spell_links()
        
        # Eğer max_spells varsa, sadece ilk N spell'i al
        if max_spells:
            spell_links = spell_links[:max_spells]
            print(f"  ⚠️  İlk {max_spells} spell çekilecek (test modu)")
        else:
            # Cache'de olmayan spell'leri filtrele - DÜZELTİLDİ
            cached_names = set(cached_spells.keys())
            spell_links = [(name, url) for name, url in spell_links if name not in cached_names]
            if spell_links:
                print(f"  🔄 {len(spell_links)} yeni spell çekilecek ({len(cached_names)} zaten cache'de)")
            else:
                print("  ✅ Tüm spell'ler zaten cache'de!")
                return cached_spells
        
        total = len(spell_links)
        
        print(f"\n📖 {total} spell detayı çekiliyor...")
        print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(spell_links, 1):
            if i % 10 == 0:
                successful = len(spells)
                print(f"  ... {i}/{total} spell çekildi ({successful} başarılı)")
                # Her 50 spell'de bir cache'e kaydet (ilerlemeyi koru)
                if i % 50 == 0:
                    all_spells_temp = {**cached_spells, **spells}
                    cache_data = {
                        'total': len(all_spells_temp),
                        'spells': all_spells_temp,
                        'source': '5esrd.com',
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'progress': f'{i}/{total}'
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 İlerleme kaydedildi: {successful} yeni spell, toplam {len(all_spells_temp)}")
            
            spell_data = self.scrape_spell_detail(url, name)
            if spell_data and spell_data.get('name'):
                spells[spell_data['name']] = spell_data
        
        print(f"\n✅ {len(spells)} yeni spell başarıyla çekildi")
        print(f"   Toplam: {len(spells) + len(cached_spells)} spell (cache dahil)")
        
        # Final cache'e kaydet
        all_spells = {**cached_spells, **spells}
        cache_data = {
            'total': len(all_spells),
            'spells': all_spells,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache'e kaydedildi: {cache_file}")
        
        return all_spells
    
    def scrape_all_feat_links(self) -> List[tuple]:
        """Tüm feat linklerini çek - DÜZELTİLDİ (Feats Scraping)"""
        print("🔍 Feat linkleri çekiliyor...")
        
        # 5esrd.com'da feat'ler /database/feats/ altında
        url = f"{self.BASE_URL}/database/feats"
        
        soup = self._get(url)
        if not soup:
            print("❌ Feats database sayfası bulunamadı!")
            return []
        
        feat_links = []
        
        # Feat linklerini bul - /database/feats/ içeren ve anlamlı text'i olan linkler
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # /database/feats/ içeren ve feat detay sayfası olan linkler
            # Format: /database/feats/[feat-name]/
            if '/database/feats/' in href.lower() and text and len(text) < 100 and text != 'Feats':
                # List/index sayfalarını filtrele
                if any(skip in href.lower() for skip in ['/feats', '/database/feats', 'list', 'index', 'category']):
                    # Eğer /database/feats/ ile bitmiyorsa ve bir feat adı içeriyorsa (kısa çizgi ile ayrılmış)
                    if not href.lower().endswith('/feats/') and not href.lower().endswith('/feats'):
                        # Feat detay sayfası gibi görünüyor (örn: /database/feats/a-taste-of-power/)
                        pass  # Devam et
                    else:
                        continue  # List sayfası, atla
                
                if href.startswith('/'):
                    full_url = self.BASE_URL + href
                elif href.startswith('http'):
                    full_url = href
                else:
                    full_url = urljoin(url, href)
                
                # Feat detay sayfası kontrolü - URL'de feat adı olmalı (kısa çizgi ile ayrılmış kelimeler)
                if '/database/feats/' in full_url.lower() and full_url.lower().count('/') >= 4:
                    # Örnek: /database/feats/a-taste-of-power/ -> 4+ slash var
                    feat_links.append((text, full_url))
        
        # Tekrar edenleri kaldır
        unique_links = list(set(feat_links))
        print(f"  ✅ {len(unique_links)} unique feat linki bulundu")
        return unique_links
    
    def scrape_feat_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Feat detay sayfasını çek - DÜZELTİLDİ (Feats Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        feat_data = {
            "name": name,
            "prerequisite": None,
            "description": "",
            "source": url
        }
        
        # Tüm paragrafları al
        paragraphs = main_content.find_all('p')
        
        # Metni al
        text_content = main_content.get_text()
        
        # Prerequisite - DÜZELTİLDİ (Feats Scraping)
        # Format: "Prerequisite: Strength 13 or higher" veya "Prerequisite: None"
        prereq_patterns = [
            r'Prerequisite[:\s]+([^D\n]+?)(?:Description|$|You |A |At Higher|This feat|Benefits|Special)',
            r'Prerequisites?[:\s]+([^D\n]+?)(?:Description|$|You |A |Benefits|Special)',
            r'Prerequisite[:\s]+(.+?)(?:\n\n|$|Description)',
        ]
        
        for pattern in prereq_patterns:
            prereq_match = re.search(pattern, text_content[:1000], re.I)
            if prereq_match:
                prerequisite = prereq_match.group(1).strip()
                # "None" veya boş değilse kaydet
                if prerequisite and prerequisite.lower() not in ['none', 'none.', '']:
                    feat_data['prerequisite'] = prerequisite
                break
        
        # Description - DÜZELTİLDİ V2 (Feats Scraping - iyileştirildi)
        description_parts = []
        
        # İlk olarak, "Benefit(s):" veya "Description:" gibi başlıkları ara
        benefit_pattern = re.search(r'(?:Benefit|Benefits|Description)[:\s]+(.+?)(?:\n\n|$)', text_content, re.I | re.DOTALL)
        if benefit_pattern:
            description_text = benefit_pattern.group(1).strip()
            # İlk 2000 karakteri al
            description_text = description_text[:2000]
            description_parts.append(description_text)
        else:
            # Benefit bulunamadıysa, paragrafları kontrol et
            start_collecting = False
            found_prerequisite = False
            
            for i, p in enumerate(paragraphs):
                text = p.get_text(strip=True)
                
                # Prerequisite paragrafını işaretle
                if 'prerequisite' in text.lower() and i < 5:
                    found_prerequisite = True
                    start_collecting = True
                    continue
                
                # Description/Benefit başlığı varsa, ondan sonraki paragrafları al
                if 'benefit' in text.lower() or 'description' in text.lower():
                    if i < 10:  # İlk 10 paragrafta olmalı
                        start_collecting = True
                        # Benefit text'ini de ekle
                        if len(text) > 50:
                            description_parts.append(text)
                        continue
                
                # Copyright, footer metinlerini atla
                skip_texts = [
                    'Green Ronin', 'OGN', 'Open Gaming', 'Copyright',
                    'Join Our Discord', 'Subscribe', 'license attribution',
                    'see the full license', 'This is not the complete license'
                ]
                
                should_skip = any(skip in text for skip in skip_texts)
                
                if (len(text) > 20 and not should_skip and
                    'Prerequisite' not in text and 'Prerequisites' not in text):
                    
                    # Prerequisite'ten sonra veya 3. paragraftan itibaren topla
                    if start_collecting or (found_prerequisite and i > 1) or (not found_prerequisite and i >= 1):
                        description_parts.append(text)
        
        # Description'ı temizle ve birleştir
        if description_parts:
            # Lisans metinlerini temizle
            cleaned_parts = []
            for part in description_parts:
                # Lisans metinlerini filtrele
                if any(skip in part for skip in ['license attribution', 'see the full license', 'This is not the complete']):
                    continue
                # Çok kısa paragrafları atla (genellikle navigation/header)
                if len(part) > 20:
                    cleaned_parts.append(part)
            
            if cleaned_parts:
                feat_data['description'] = '\n\n'.join(cleaned_parts[:10])  # En fazla 10 paragraf
        
        return feat_data
    
    def scrape_all_feats(self, max_feats: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm feat'leri çek - DÜZELTİLDİ (Feats Scraping)"""
        print("=" * 70)
        print("5ESRD.COM FEATS ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü
        cache_file = Path("data/cache/feats_cache.json")
        feats = {}
        cached_feats = {}
        
        if not force_refresh and cache_file.exists():
            print(f"📦 Cache dosyası bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('feats'):
                    cached_feats = cached['feats']
                    feats.update(cached_feats)
                    print(f"  ✅ {len(cached_feats)} feat cache'den yüklendi")
        
        # Feat linklerini çek
        feat_links = self.scrape_all_feat_links()
        
        if not feat_links:
            print("  ⚠️  Feat linkleri bulunamadı! Mevcut cache'i döndürüyoruz.")
            return cached_feats
        
        # Eğer max_feats varsa, sadece ilk N feat'i al
        if max_feats:
            feat_links = feat_links[:max_feats]
            print(f"  ⚠️  İlk {max_feats} feat çekilecek (test modu)")
        else:
            # Cache'de olmayan feat'leri filtrele
            cached_names = set(cached_feats.keys())
            feat_links = [(name, url) for name, url in feat_links if name not in cached_names]
            if feat_links:
                print(f"  🔄 {len(feat_links)} yeni feat çekilecek ({len(cached_names)} zaten cache'de)")
            else:
                print("  ✅ Tüm feat'ler zaten cache'de!")
                return cached_feats
        
        total = len(feat_links)
        
        print(f"\n📖 {total} feat detayı çekiliyor...")
        print("  (Bu işlem uzun sürebilir, lütfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(feat_links, 1):
            if i % 10 == 0:
                successful = len(feats)
                print(f"  ... {i}/{total} feat çekildi ({successful} başarılı)")
                # Her 50 feat'te bir cache'e kaydet (ilerlemeyi koru)
                if i % 50 == 0:
                    all_feats_temp = {**cached_feats, **feats}
                    cache_data = {
                        'total': len(all_feats_temp),
                        'feats': all_feats_temp,
                        'source': '5esrd.com',
                        'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S'),
                        'progress': f'{i}/{total}'
                    }
                    with open(cache_file, 'w', encoding='utf-8') as f:
                        json.dump(cache_data, f, ensure_ascii=False, indent=2)
                    print(f"  💾 İlerleme kaydedildi: {successful} yeni feat, toplam {len(all_feats_temp)}")
            
            feat_data = self.scrape_feat_detail(url, name)
            if feat_data and feat_data.get('name'):
                feats[feat_data['name']] = feat_data
        
        print(f"\n✅ {len(feats)} yeni feat başarıyla çekildi")
        print(f"   Toplam: {len(feats) + len(cached_feats)} feat (cache dahil)")
        
        # Final cache'e kaydet
        all_feats = {**cached_feats, **feats}
        cache_data = {
            'total': len(all_feats),
            'feats': all_feats,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"💾 Cache'e kaydedildi: {cache_file}")
        
        return all_feats
    
    def scrape_all_class_links(self) -> List[tuple]:
        """Tüm class linklerini çek - DÜZELTİLDİ (Classes Scraping)"""
        print("🔍 Class linkleri çekiliyor...")
        url = f"{self.BASE_URL}/classes/"
        
        soup = self._get(url)
        if not soup:
            print("❌ Classes sayfası bulunamadı!")
            return []
        
        class_links = []
        for link in soup.find_all('a', href=True):
            href = link.get('href', '')
            text = link.get_text(strip=True)
            
            # Core classes için: /database/class/class-name/ pattern'ini kullan
            if '/database/class/' in href.lower() and text and len(text) < 50 and len(text) > 1:
                # 3rd party veya prestige class'ları filtrele
                if '3rd-party' not in href.lower() and 'prestige' not in href.lower():
                    if href.endswith('/'):
                        if href.startswith('/'):
                            full_url = self.BASE_URL + href
                        else:
                            full_url = urljoin(url, href)
                        class_links.append((text, full_url))
        
        # Tekrar edenleri kaldır ve sırala
        unique_links = list(set(class_links))
        unique_links.sort(key=lambda x: x[0])  # İsme göre sırala
        print(f"  ✅ {len(unique_links)} unique core class linki bulundu")
        return unique_links
    
    def scrape_class_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Class detay sayfasını çek - DÜZELTİLDİ (Classes Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        class_data = {
            "name": name,
            "hit_die": "d8",  # Default
            "primary_ability": [],
            "saving_throws": [],
            "class_skills": [],
            "skill_choices": 2,  # Default
            "proficiencies": {
                "armor": [],
                "weapons": [],
                "tools": [],
                "languages": []
            },
            "starting_equipment_options": [],
            "class_features": {},
            "spellcasting": None,  # Spellcaster class'lar için
            "source": url
        }
        
        # Tüm metni al
        text_content = main_content.get_text()
        
        # Paragrafları al (structured parsing için)
        paragraphs = main_content.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        
        # Hit Die - DÜZELTİLDİ (Classes Scraping - iyileştirildi)
        hit_die_patterns = [
            r'Hit Dice[:\s]+1d(\d+)\s+per',
            r'Hit Dice[:\s]+d(\d+)',
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Die[:\s]+(\d+)',
            r'(\d+)d(\d+)\s+Hit Die',
        ]
        
        # Önce paragraflarda ara
        for para_text in paragraph_texts:
            for pattern in hit_die_patterns:
                match = re.search(pattern, para_text, re.I)
                if match:
                    hit_die_val = match.group(1) if match.lastindex >= 1 else match.group(2)
                    class_data['hit_die'] = f"d{hit_die_val}"
                    break
            if class_data['hit_die'] != "d8":
                break
        
        # Paragraflarda bulunamazsa, tüm metinde ara
        if class_data['hit_die'] == "d8":
            for pattern in hit_die_patterns:
                match = re.search(pattern, text_content[:3000], re.I)
                if match:
                    hit_die_val = match.group(1) if match.lastindex >= 1 else (match.group(2) if match.lastindex >= 2 else None)
                    if hit_die_val:
                        class_data['hit_die'] = f"d{hit_die_val}"
                        break
        
        # Primary Ability - DÜZELTİLDİ (Classes Scraping)
        ability_names = {
            "strength": "Strength",
            "dexterity": "Dexterity",
            "constitution": "Constitution",
            "intelligence": "Intelligence",
            "wisdom": "Wisdom",
            "charisma": "Charisma"
        }
        
        primary_ability_patterns = [
            r'Primary Ability[:\s]+([A-Za-z, ]+?)(?:\n|$)',
            r'Primary Abilities?[:\s]+([A-Za-z, ]+?)(?:\n|$)',
        ]
        
        for pattern in primary_ability_patterns:
            match = re.search(pattern, text_content[:2000], re.I)
            if match:
                abilities_text = match.group(1).strip()
                # Virgülle veya "and" ile ayrılmış ability'leri parse et
                abilities = re.split(r'[,and]+', abilities_text, flags=re.I)
                for ab in abilities:
                    ab_clean = ab.strip().lower().capitalize()
                    if ab_clean in ability_names.values():
                        if ab_clean not in class_data['primary_ability']:
                            class_data['primary_ability'].append(ab_clean)
                break
        
        # Primary Ability - DÜZELTİLDİ (Classes Scraping - eğer paragrafta bulunamazsa, mevcut veriden tahmin et)
        # Genellikle spellcasting ability ile aynı veya class'a göre belirlenir
        if not class_data['primary_ability']:
            # Class name'e göre default primary ability
            class_name_lower = name.lower()
            if 'barbarian' in class_name_lower:
                class_data['primary_ability'] = ["Strength"]
            elif 'bard' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'cleric' in class_name_lower:
                class_data['primary_ability'] = ["Wisdom"]
            elif 'druid' in class_name_lower:
                class_data['primary_ability'] = ["Wisdom"]
            elif 'fighter' in class_name_lower:
                class_data['primary_ability'] = ["Strength", "Dexterity"]
            elif 'monk' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity", "Wisdom"]
            elif 'paladin' in class_name_lower:
                class_data['primary_ability'] = ["Strength", "Charisma"]
            elif 'ranger' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity", "Wisdom"]
            elif 'rogue' in class_name_lower:
                class_data['primary_ability'] = ["Dexterity"]
            elif 'sorcerer' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'warlock' in class_name_lower:
                class_data['primary_ability'] = ["Charisma"]
            elif 'wizard' in class_name_lower:
                class_data['primary_ability'] = ["Intelligence"]
        
        # Proficiencies - DÜZELTİLDİ (Classes Scraping - iyileştirildi)
        # Proficiencies genellikle tek bir paragrafta: "Armor: ... Weapons: ... Tools: ... Saving Throws: ... Skills: ..."
        proficiencies_para = None
        for para_text in paragraph_texts:
            if 'Armor:' in para_text and ('Weapons:' in para_text or 'Saving Throws:' in para_text):
                proficiencies_para = para_text
                break
        
        # Skill names list (all D&D 5e skills)
        skill_names = [
            "Acrobatics", "Animal Handling", "Arcana", "Athletics", "Deception",
            "History", "Insight", "Intimidation", "Investigation", "Medicine",
            "Nature", "Perception", "Performance", "Persuasion", "Religion",
            "Sleight of Hand", "Stealth", "Survival"
        ]
        
        if proficiencies_para:
            # Armor
            armor_match = re.search(r'Armor[:\s]+([^W]+?)(?:Weapons|Tools|Saving|Skills|$)', proficiencies_para, re.I)
            if armor_match:
                armor_text = armor_match.group(1).strip()
                if 'all armor' in armor_text.lower() or 'all' in armor_text.lower():
                    class_data['proficiencies']['armor'] = ["All armor", "Shields"]
                elif 'shields' in armor_text.lower():
                    armor_types = re.split(r'[,]', armor_text)
                    for armor in armor_types:
                        armor_clean = armor.strip()
                        if armor_clean:
                            if 'shield' in armor_clean.lower():
                                if "Shields" not in class_data['proficiencies']['armor']:
                                    class_data['proficiencies']['armor'].append("Shields")
                            elif armor_clean and armor_clean not in class_data['proficiencies']['armor']:
                                class_data['proficiencies']['armor'].append(armor_clean)
            
            # Weapons - DÜZELTİLDİ (iyileştirildi - pattern düzeltildi)
            # Format: "Weapons: Simple weapons, martial weaponsTools:..." (boşluk olmayabilir)
            weapon_patterns = [
                r'Weapons?[:\s]+([^T]+?)(?:Tools|Saving|Skills|$)',
                r'Weapons?[:\s]+([A-Za-z\s,]+?)(?:Tools|Saving|Skills|$)',
            ]
            
            for pattern in weapon_patterns:
                weapon_match = re.search(pattern, proficiencies_para, re.I)
                if weapon_match:
                    weapon_text = weapon_match.group(1).strip()
                    # "Simple weapons, martial weapons" veya "Simple weapons,martial weapons" gibi formatları parse et
                    if 'simple' in weapon_text.lower() and 'martial' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Simple weapons", "Martial weapons"]
                        break
                    elif 'simple' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Simple weapons"]
                        break
                    elif 'martial' in weapon_text.lower():
                        class_data['proficiencies']['weapons'] = ["Martial weapons"]
                        break
                    else:
                        # Virgülle ayrılmış weapon'ları parse et
                        weapon_types = re.split(r'[,]', weapon_text)
                        for weapon in weapon_types:
                            weapon_clean = weapon.strip()
                            if weapon_clean and weapon_clean not in class_data['proficiencies']['weapons']:
                                class_data['proficiencies']['weapons'].append(weapon_clean)
                        if class_data['proficiencies']['weapons']:
                            break
            
            # Tools
            tool_match = re.search(r'Tools?[:\s]+([^S]+?)(?:Saving|Skills|$)', proficiencies_para, re.I)
            if tool_match:
                tool_text = tool_match.group(1).strip()
                if 'none' not in tool_text.lower():
                    tool_types = re.split(r'[,]', tool_text)
                    for tool in tool_types:
                        tool_clean = tool.strip()
                        if tool_clean and tool_clean not in class_data['proficiencies']['tools']:
                            class_data['proficiencies']['tools'].append(tool_clean)
            
            # Saving Throws - DÜZELTİLDİ (paragraftan parse - iyileştirildi)
            # Format: "Saving Throws:Strength,ConstitutionSkills:..." (boşluk olmayabilir, Skills ile bitiyor)
            saving_throws_patterns = [
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+)*?)(?:Skills|$)',
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+,\s*[A-Z][a-z]+)(?:Skills|$)',
                r'Saving\s+Throws?[:\s]+([A-Z][a-z]+,\s*[A-Z][a-z]+)',
            ]
            
            for pattern in saving_throws_patterns:
                saving_throws_match = re.search(pattern, proficiencies_para, re.I)
                if saving_throws_match:
                    throws_text = saving_throws_match.group(1).strip()
                    # Virgül veya boşlukla ayrılmış ability'leri parse et
                    throws = re.split(r'[,]+', throws_text)
                    for throw in throws:
                        throw_clean = throw.strip()
                        # Ability name'i tam olarak eşleştir (capitalize etmeden önce kontrol et)
                        for ability in ability_names.values():
                            if (ability.lower() == throw_clean.lower() or 
                                throw_clean.lower() == ability.lower()[:len(throw_clean)] or
                                ability.lower().startswith(throw_clean.lower())):
                                if ability not in class_data['saving_throws']:
                                    class_data['saving_throws'].append(ability)
                                break
                    if len(class_data['saving_throws']) >= 2:  # En az 2 saving throw olmalı
                        break
            
            # Class Skills - DÜZELTİLDİ (paragraftan parse - iyileştirildi)
            # Format: "Skills: Choose two skills fromAcrobatic..." veya "Skills: Choose from Acrobatics, Animal Handling..."
            skills_patterns = [
                r'Skills?[:\s]+Choose\s+(\d+)\s+skills?\s+from\s+([A-Z][a-z\s,]+?)(?:\n|$)',
                r'Skills?[:\s]+Choose\s+(\d+)\s+from\s+([A-Z][a-z\s,]+?)(?:\n|$)',
                r'Skills?[:\s]+([A-Z][a-z\s,]+?)(?:\n\n|\n[A-Z]|$)',
            ]
            
            for pattern in skills_patterns:
                skills_match = re.search(pattern, proficiencies_para, re.I | re.DOTALL)
                if skills_match:
                    # Skill count
                    if skills_match.lastindex >= 1 and skills_match.group(1).isdigit():
                        class_data['skill_choices'] = int(skills_match.group(1))
                    
                    # Skills text
                    skills_text = skills_match.group(2) if skills_match.lastindex >= 2 else skills_match.group(1)
                    if skills_text:
                        # Skills listesini parse et (virgül veya "and" ile ayrılmış)
                        skills_list = re.split(r'[,and]+', skills_text, flags=re.I)
                        for skill in skills_list:
                            skill_clean = skill.strip()
                            if skill_clean:
                                # Skill ismini eşleştir (tam isim veya kısmi)
                                for known_skill in skill_names:
                                    # Exact match veya substring match
                                    if (known_skill.lower() == skill_clean.lower() or 
                                        known_skill.lower().startswith(skill_clean.lower()) or
                                        skill_clean.lower() in known_skill.lower()):
                                        if known_skill not in class_data['class_skills']:
                                            class_data['class_skills'].append(known_skill)
                                        break
                    if class_data['class_skills']:
                        break
        
        # Class Features - DÜZELTİLDİ (Classes Scraping - Level bazlı tablo parsing)
        # Level table'ını bul (1-20 level features)
        tables = main_content.find_all('table')
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) > 5:  # En az birkaç satır olmalı
                # İlk satır header olabilir
                headers = [th.get_text(strip=True) for th in rows[0].find_all(['th', 'td'])]
                
                # "Level" veya "Features" kolonunu bul
                level_col = None
                features_col = None
                
                for i, header in enumerate(headers):
                    if 'level' in header.lower():
                        level_col = i
                    if 'feature' in header.lower() or 'class' in header.lower():
                        features_col = i
                
                # Eğer header yoksa, ilk kolon level, son kolon features olabilir
                if level_col is None:
                    level_col = 0
                if features_col is None:
                    features_col = len(headers) - 1
                
                # Satırları parse et
                for row in rows[1:]:  # İlk satır header
                    cells = row.find_all(['td', 'th'])
                    if len(cells) > max(level_col, features_col):
                        level_text = cells[level_col].get_text(strip=True) if level_col < len(cells) else ""
                        features_text = cells[features_col].get_text(strip=True) if features_col < len(cells) else ""
                        
                        # Level numarasını çıkar (örn: "1st", "2nd", "3rd", "4th" -> 1, 2, 3, 4)
                        level_match = re.search(r'(\d+)', level_text)
                        if level_match and features_text:
                            level = int(level_match.group(1))
                            # Features'ları parse et (virgülle ayrılmış)
                            features = [f.strip() for f in re.split(r'[,]', features_text) if f.strip()]
                            
                            if level not in class_data['class_features']:
                                class_data['class_features'][str(level)] = {
                                    "features": features,
                                    "choices": {}
                                }
                            else:
                                # Mevcut features'lara ekle
                                existing_features = class_data['class_features'][str(level)].get("features", [])
                                for feature in features:
                                    if feature not in existing_features:
                                        existing_features.append(feature)
                                class_data['class_features'][str(level)]["features"] = existing_features
                
                # Tablo bulundu, diğer tablolara bakmaya gerek yok
                if class_data['class_features']:
                    break
        
        # Starting Equipment - DÜZELTİLDİ (Classes Scraping)
        # "You start with the following equipment" veya "Starting Equipment" bölümünü bul
        equipment_section_patterns = [
            r'You start with the following equipment[:\s]+(.+?)(?:\n\n|\n[A-Z]|Class Features|$)',
            r'Starting Equipment[:\s]+(.+?)(?:\n\n|\n[A-Z]|Class Features|$)',
        ]
        
        for pattern in equipment_section_patterns:
            equipment_match = re.search(pattern, text_content[:5000], re.I | re.DOTALL)
            if equipment_match:
                equipment_text = equipment_match.group(1).strip()
                # Equipment options'ları parse et (genellikle liste halinde)
                # Format: "(a) item1, item2 or (b) item3, item4"
                options = re.split(r'\([a-z]\)', equipment_text, flags=re.I)
                for option in options:
                    option_clean = option.strip()
                    if option_clean and len(option_clean) > 10:
                        # "or" ile ayrılmış alternatifleri bul
                        items = re.split(r'\s+or\s+', option_clean, flags=re.I)
                        equipment_list = []
                        for item_text in items:
                            # Virgülle ayrılmış item'ları parse et
                            item_parts = re.split(r'[,]', item_text)
                            for item_part in item_parts:
                                item_clean = item_part.strip()
                                if item_clean and len(item_clean) > 2:
                                    equipment_list.append(item_clean)
                        if equipment_list:
                            class_data['starting_equipment_options'].append(equipment_list)
                break
        
        # Spellcasting - eğer spellcaster ise - DÜZELTİLDİ (daha iyi detection)
        # Spellcaster class'lar: Wizard, Sorcerer, Warlock, Cleric, Druid, Bard, Paladin, Ranger, Artificer
        spellcaster_classes = ['wizard', 'sorcerer', 'warlock', 'cleric', 'druid', 'bard', 'paladin', 'ranger', 'artificer']
        class_name_lower = name.lower()
        
        # Önce class name'e göre kontrol et (en güvenilir)
        is_spellcaster = class_name_lower in spellcaster_classes
        
        # Eğer class name'e göre spellcaster değilse, content'te spellcasting section'ı ara
        if not is_spellcaster:
            spellcasting_indicators = [
                r'Spellcasting\s+Ability',  # "Spellcasting Ability" başlığı
                r'Spell\s+Slots\s+per\s+Level',  # Spell slots tablosu
                r'Spells\s+Known',  # Spells Known section
                r'Spells\s+Prepared',  # Spells Prepared section
                r'Cantrips?\s+Known',  # Cantrips section
            ]
            
            # Sadece başlık veya section başlığı olarak geçiyorsa spellcaster
            for indicator in spellcasting_indicators:
                if re.search(indicator, text_content[:10000], re.I):
                    is_spellcaster = True
                    break
        
        if is_spellcaster:
            # Spellcasting ability'yi belirle
            spellcasting_ability = "Intelligence"  # Default
            if class_name_lower in ['wizard', 'artificer']:
                spellcasting_ability = "Intelligence"
            elif class_name_lower in ['sorcerer', 'warlock', 'bard', 'paladin']:
                spellcasting_ability = "Charisma"
            elif class_name_lower in ['cleric', 'druid', 'ranger']:
                spellcasting_ability = "Wisdom"
            elif class_data['primary_ability']:
                spellcasting_ability = class_data['primary_ability'][0]
            
            class_data['spellcasting'] = {
                "spellcasting_ability": spellcasting_ability,
                "spell_save_dc": 8,  # Base (8 + proficiency + ability modifier)
                "spell_attack_bonus": 0  # Base (proficiency + ability modifier)
            }
        else:
            class_data['spellcasting'] = None
        
        return class_data
    
    def scrape_all_race_links(self) -> List[tuple]:
        """Tüm core race linklerini çek - DÜZELTİLDİ (Races Scraping)"""
        print("[*] Race linkleri cekiliyor...")
        
        # Core races listesi (bilinen D&D 5e core races)
        core_races = [
            ("Dragonborn", f"{self.BASE_URL}/races/dragonborn/"),
            ("Dwarf", f"{self.BASE_URL}/races/dwarf/"),
            ("Elf", f"{self.BASE_URL}/races/elf/"),
            ("Gnome", f"{self.BASE_URL}/races/gnome/"),
            ("Halfling", f"{self.BASE_URL}/races/halfling/"),
            ("Half-Elf", f"{self.BASE_URL}/races/half-elf/"),
            ("Half-Orc", f"{self.BASE_URL}/races/half-orc/"),
            ("Human", f"{self.BASE_URL}/races/human/"),
            ("Tiefling", f"{self.BASE_URL}/races/tiefling/"),
        ]
        
        print(f"  [OK] {len(core_races)} core race linki hazir")
        return core_races
    
    def scrape_race_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Race detay sayfasını çek - DÜZELTİLDİ (Races Scraping)"""
        soup = self._get(url)
        if not soup:
            return None
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            main_content = soup.find('body')
        
        if not main_content:
            return None
        
        # Navigation ve footer'ı temizle
        for nav in main_content.find_all(['nav', 'header', 'footer']):
            nav.decompose()
        
        race_data = {
            "name": name,
            "ability_score_increase": {},
            "speed": 30,  # Default
            "traits": [],
            "languages": [],
            "extra_languages": 0,
            "size": "Medium",  # Default
            "source": url
        }
        
        # Tüm metni al
        text_content = main_content.get_text()
        
        # Paragrafları al (structured parsing için)
        paragraphs = main_content.find_all('p')
        paragraph_texts = [p.get_text(strip=True) for p in paragraphs]
        
        # Ability Score Increase - DÜZELTİLDİ (Races Scraping)
        ability_names = {
            "strength": "strength", "dexterity": "dexterity", "constitution": "constitution",
            "intelligence": "intelligence", "wisdom": "wisdom", "charisma": "charisma"
        }
        
        asi_patterns = [
            r'Ability\s+Score\s+Increase[:\s]+(.+?)(?:\n\n|\n[A-Z]|Age|Alignment|Size|Speed|Traits|Languages|$)',
            r'ASI[:\s]+(.+?)(?:\n|$)',
        ]
        
        # Önce paragraflarda ara
        for para_text in paragraph_texts:
            for pattern in asi_patterns:
                match = re.search(pattern, para_text, re.I | re.DOTALL)
                if match:
                    asi_text = match.group(1).strip()
                    
                    # "Your Strength score increases by 2, and your Charisma score increases by 1."
                    # veya "Your all ability scores increase by 1"
                    # veya "Strength +2, Charisma +1"
                    
                    # "all" kontrolü
                    if 'all' in asi_text.lower() or 'each' in asi_text.lower():
                        all_match = re.search(r'(\d+)', asi_text)
                        if all_match:
                            race_data['ability_score_increase'] = {"all": int(all_match.group(1))}
                            break
                    else:
                        # Individual ability increases
                        ability_increases = {}
                        # Pattern: "YourStrengthscore increases by 2" (boşluk olmayabilir!)
                        # veya "Strength score increases by 2" (boşluklu)
                        # veya "Strength +2"
                        
                        # Önce "YourXxxscore increases by Y" formatını parse et (boşluksuz)
                        no_space_pattern = r'Your(\w+)score\s+increases?\s+by\s+(\d+)'
                        matches = re.finditer(no_space_pattern, asi_text, re.I)
                        for m in matches:
                            ability_word = m.group(1).lower()
                            value = int(m.group(2))
                            
                            # Ability name'i normalize et
                            for known_ability, key in ability_names.items():
                                if known_ability in ability_word or ability_word in known_ability:
                                    ability_increases[key] = value
                                    break
                        
                        # Eğer boşluksuz pattern çalışmadıysa, boşluklu pattern'leri dene
                        if not ability_increases:
                            ability_patterns = [
                                r'(\w+)\s+score\s+increases?\s+by\s+(\d+)',
                                r'(\w+)\s+(\d+)',
                                r'\+(\d+)\s+(\w+)',
                            ]
                            
                            for ab_pattern in ability_patterns:
                                matches = re.finditer(ab_pattern, asi_text, re.I)
                                for m in matches:
                                    if len(m.groups()) >= 2:
                                        # İki format var: (ability, value) veya (value, ability)
                                        if m.group(1).isdigit():
                                            value = int(m.group(1))
                                            ability = m.group(2).lower()
                                        else:
                                            ability = m.group(1).lower()
                                            value = int(m.group(2))
                                        
                                        # Ability name'i normalize et
                                        for known_ability, key in ability_names.items():
                                            if known_ability in ability or ability in known_ability:
                                                ability_increases[key] = value
                                                break
                                if ability_increases:
                                    break
                        
                        if ability_increases:
                            race_data['ability_score_increase'] = ability_increases
                            break
                    
                    if race_data['ability_score_increase']:
                        break
            if race_data['ability_score_increase']:
                break
        
        # Speed - DÜZELTİLDİ (Races Scraping)
        speed_patterns = [
            r'Speed[:\s]+Your\s+base\s+walking\s+speed\s+is\s+(\d+)\s+feet?',
            r'Speed[:\s]+(\d+)\s+ft',
            r'Base\s+Speed[:\s]+(\d+)',
            r'(\d+)\s+feet?\s+speed',
        ]
        
        for para_text in paragraph_texts:
            for pattern in speed_patterns:
                match = re.search(pattern, para_text, re.I)
                if match:
                    speed_val = int(match.group(1))
                    race_data['speed'] = speed_val
                    break
            if race_data['speed'] != 30:
                break
        
        # Traits - DÜZELTİLDİ (Races Scraping - iyileştirildi)
        # Traits hem başlık (H3, H4) hem de paragraf içinde olabilir
        # Örnek: "Draconic Ancestry", "Breath Weapon", "Damage Resistance"
        known_trait_names = [
            'Draconic Ancestry', 'Breath Weapon', 'Damage Resistance',
            'Darkvision', 'Fey Ancestry', 'Trance', 'Keen Senses',
            'Lucky', 'Brave', 'Halfling Nimbleness', 'Naturally Stealthy',
            'Stonecunning', 'Dwarven Toughness', 'Dwarven Resilience',
            'Gnome Cunning', 'Artificer\'s Lore', 'Tinker',
            'Mask of the Wild', 'Fleet of Foot', 'Elf Weapon Training',
            'Extra Language', 'Versatility', 'Skill Versatility',
            'Menacing', 'Relentless Endurance', 'Savage Attacks',
            'Hellish Resistance', 'Infernal Legacy'
        ]
        
        # Önce başlıklardan trait'leri bul
        headings = main_content.find_all(['h3', 'h4'])
        skip_headings = ['traits', 'variants', 'subrace', 'subraces', 'race features', 'race feature']
        
        for heading in headings:
            heading_text = heading.get_text(strip=True)
            heading_lower = heading_text.lower()
            
            # Genel başlıkları atla
            if heading_lower in skip_headings:
                continue
            
            # "Dragonborn Traits" gibi race-specific genel başlıkları atla
            if heading_lower == 'traits' or (heading_lower.endswith('traits') and len(heading_lower.split()) <= 2):
                continue
            
            # Bilinen trait isimleri ile eşleştir
            for trait_name in known_trait_names:
                if trait_name.lower() == heading_lower or heading_lower.startswith(trait_name.lower()):
                    if trait_name not in race_data['traits']:
                        race_data['traits'].append(trait_name)
                    break
        
        # Sonra paragraflardan trait'leri bul (örn: "Draconic Ancestry: You have...")
        for para_text in paragraph_texts:
            # Pattern: "Trait Name: Description" formatını ara
            for trait_name in known_trait_names:
                # Trait name ile başlayan paragrafları bul
                trait_pattern = r'^' + re.escape(trait_name) + r'[:\s]+'
                if re.search(trait_pattern, para_text, re.I):
                    if trait_name not in race_data['traits']:
                        race_data['traits'].append(trait_name)
        
        # Languages - DÜZELTİLDİ (Races Scraping - iyileştirildi)
        language_names = [
            "Common", "Elvish", "Dwarvish", "Gnomish", "Halfling",
            "Orc", "Draconic", "Infernal", "Celestial", "Abyssal",
            "Giant", "Primordial", "Deep Speech", "Undercommon"
        ]
        
        # Languages paragrafını bul
        for para_text in paragraph_texts:
            if 'language' not in para_text.lower():
                continue
            
            # "Languages: You can speak, read, and write Common and Draconic."
            # Pattern: "Common and Draconic" kısmını yakala
            # Önce tüm language names'leri ara
            found_languages = []
            for lang_name in language_names:
                # Language name'i paragrafta ara (kelime sınırları ile)
                lang_pattern = r'\b' + re.escape(lang_name) + r'\b'
                if re.search(lang_pattern, para_text, re.I):
                    found_languages.append(lang_name)
            
            if found_languages:
                race_data['languages'] = found_languages
                break
        
        # Extra Languages
        extra_lang_patterns = [
            r'Extra\s+Languages?[:\s]+(\d+)',
            r'one\s+additional\s+language',
            r'additional\s+language',
        ]
        
        for pattern in extra_lang_patterns:
            match = re.search(pattern, text_content[:3000], re.I)
            if match:
                if match.group(1) if match.lastindex >= 1 else None:
                    race_data['extra_languages'] = int(match.group(1))
                else:
                    race_data['extra_languages'] = 1
                break
        
        # Size - DÜZELTİLDİ (Races Scraping)
        size_patterns = [
            r'Size[:\s]+(.+?)(?:\n|$)',
            r'Yoursizeis\s+(\w+)',
            r'size\s+is\s+(\w+)',
        ]
        
        for pattern in size_patterns:
            match = re.search(pattern, text_content[:2000], re.I)
            if match:
                size_text = match.group(1).strip().capitalize()
                if size_text in ["Small", "Medium", "Large", "Tiny", "Huge"]:
                    race_data['size'] = size_text
                    break
        
        return race_data
    
    def scrape_all_races(self, max_races: Optional[int] = None, force_refresh: bool = False) -> Dict[str, Dict[str, Any]]:
        """Tüm core races'leri scrape et - DÜZELTİLDİ (Races Scraping)"""
        print("[*] Tum core races scrape ediliyor...")
        
        # Cache kontrolü
        cache_file = Path("data/cache/races_cache.json")
        races = {}
        cached_races = {}
        
        if cache_file.exists() and not force_refresh:
            try:
                with open(cache_file, 'r', encoding='utf-8') as f:
                    cached = json.load(f)
                    if cached.get('races'):
                        cached_races = cached['races']
                        races.update(cached_races)
                        print(f"  [OK] {len(cached_races)} race cache'den yuklendi")
            except Exception as e:
                print(f"  [UYARI] Cache yuklenemedi: {e}")
        
        # Race linklerini çek
        race_links = self.scrape_all_race_links()
        
        if not race_links:
            print("  [UYARI] Race linkleri bulunamadi! Mevcut cache'i donduruyoruz.")
            return races
        
        print(f"\n[*] {len(race_links)} race bulundu")
        
        # Cache'de olmayan race'leri filtrele
        cached_names = set(cached_races.keys())
        new_race_links = [(name, url) for name, url in race_links if name not in cached_names]
        
        if new_race_links:
            print(f"\n[*] {len(new_race_links)} yeni race cekilecek ({len(cached_names)} zaten cache'de)")
        else:
            print("\n[OK] Tum race'ler zaten cache'de!")
            return races
        
        # Max races limiti
        if max_races:
            new_race_links = new_race_links[:max_races]
        
        total = len(new_race_links)
        print(f"\n[*] {total} race detayi cekiliyor...")
        print("  (Bu islem uzun surebilir, lutfen bekleyin...)\n")
        
        for i, (name, url) in enumerate(new_race_links, 1):
            if i % 2 == 0:
                successful = len([k for k in races.keys() if k not in cached_names])
                print(f"  ... {i}/{total} race cekildi ({successful} basarili)")
            
            race_data = self.scrape_race_detail(url, name)
            if race_data and race_data.get('name'):
                races[race_data['name']] = race_data
            else:
                print(f"  [UYARI] {name} scrape edilemedi")
        
        print(f"\n[OK] {len([k for k in races.keys() if k not in cached_names])} yeni race basariyla cekildi")
        print(f"   Toplam: {len(races)} race (cache dahil)")
        
        # Cache'e kaydet
        cache_data = {
            'total': len(races),
            'races': races,
            'source': '5esrd.com',
            'scraped_at': time.strftime('%Y-%m-%d %H:%M:%S')
        }
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        print(f"[*] Cache'e kaydedildi: {cache_file}")
        
        return races
    
    def scrape_equipment_from_table(self, url: str, category: str) -> List[Dict[str, Any]]:
        """Equipment tablosundan verileri çek - DÜZELTİLDİ (Equipment Scraping)"""
        soup = self._get(url)
        if not soup:
            return []
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('article')
        if not main_content:
            return []
        
        equipment_list = []
        
        # Tüm tabloları bul
        tables = main_content.find_all('table')
        
        for table in tables:
            rows = table.find_all('tr')
            if len(rows) < 2:  # En az header + 1 data row
                continue
            
            # Header row'u bul (ilk row)
            header_row = rows[0]
            header_cells = [th.get_text(strip=True).lower() for th in header_row.find_all(['th', 'td'])]
            
            # Header'da hangi kolonlar var?
            # Olası kolonlar: name, cost, damage, range, weight, properties, armor_class, strength_requirement, stealth, etc.
            
            # Kolon indexlerini bul
            name_idx = None
            cost_idx = None
            damage_idx = None
            range_idx = None
            weight_idx = None
            properties_idx = None
            ac_idx = None  # Armor Class (armor için)
            strength_idx = None  # Strength requirement (armor için)
            stealth_idx = None  # Stealth disadvantage (armor için)
            
            for i, header in enumerate(header_cells):
                if 'name' in header or header == '':
                    name_idx = i
                elif 'cost' in header or 'price' in header:
                    cost_idx = i
                elif 'damage' in header:
                    damage_idx = i
                elif 'range' in header:
                    range_idx = i
                elif 'weight' in header:
                    weight_idx = i
                elif 'properties' in header or 'property' in header:
                    properties_idx = i
                elif 'armor' in header and 'class' in header or 'ac' in header:
                    ac_idx = i
                elif 'strength' in header:
                    strength_idx = i
                elif 'stealth' in header:
                    stealth_idx = i
            
            # Eğer name_idx yoksa, ilk kolonu name olarak kabul et
            if name_idx is None:
                name_idx = 0
            
            # Data row'larını parse et (ikinci row'dan başla)
            for row in rows[1:]:
                cells = row.find_all(['td', 'th'])
                cell_texts = [cell.get_text(strip=True) for cell in cells]
                
                if len(cell_texts) <= name_idx:
                    continue
                
                # Name'i al
                name = cell_texts[name_idx].strip()
                
                # Eğer name boşsa veya başlık satırıysa atla
                if not name or name.lower() in ['(simple)', '(martial)', 'simple melee weapons', 'martial melee weapons', 
                                                 'simple ranged weapons', 'martial ranged weapons']:
                    continue
                
                # Equipment item oluştur
                item = {
                    "name": name,
                    "type": category.lower(),  # "weapon", "armor", "gear", "tool"
                    "category": category,
                    "source": url
                }
                
                # Cost
                if cost_idx is not None and cost_idx < len(cell_texts):
                    cost_text = cell_texts[cost_idx].strip()
                    if cost_text and cost_text not in ['—', '–', '-', '']:
                        item["cost"] = cost_text
                
                # Damage (weapon için)
                if damage_idx is not None and damage_idx < len(cell_texts):
                    damage_text = cell_texts[damage_idx].strip()
                    if damage_text and damage_text not in ['—', '–', '-', '']:
                        item["damage"] = damage_text
                
                # Range (ranged weapon için)
                if range_idx is not None and range_idx < len(cell_texts):
                    range_text = cell_texts[range_idx].strip()
                    if range_text and range_text not in ['—', '–', '-', '']:
                        item["range"] = range_text
                
                # Weight
                if weight_idx is not None and weight_idx < len(cell_texts):
                    weight_text = cell_texts[weight_idx].strip()
                    if weight_text and weight_text not in ['—', '–', '-', '']:
                        # "4 lb." veya "4 lb" veya "4" formatını parse et
                        weight_match = re.search(r'(\d+(?:\.\d+)?)', weight_text)
                        if weight_match:
                            try:
                                item["weight"] = float(weight_match.group(1))
                            except ValueError:
                                item["weight"] = weight_text
                        else:
                            item["weight"] = weight_text
                
                # Properties (weapon için)
                if properties_idx is not None and properties_idx < len(cell_texts):
                    properties_text = cell_texts[properties_idx].strip()
                    if properties_text and properties_text not in ['—', '–', '-', '']:
                        # "finesse,light,thrown" veya "versatile(1d10)" formatını parse et
                        properties = [p.strip() for p in re.split(r'[,;]', properties_text) if p.strip()]
                        if properties:
                            item["properties"] = properties
                
                # Armor Class (armor için)
                if ac_idx is not None and ac_idx < len(cell_texts):
                    ac_text = cell_texts[ac_idx].strip()
                    if ac_text and ac_text not in ['—', '–', '-', '']:
                        # "11 + Dex modifier" veya "18" formatını parse et
                        item["armor_class"] = ac_text
                
                # Strength requirement (armor için)
                if strength_idx is not None and strength_idx < len(cell_texts):
                    strength_text = cell_texts[strength_idx].strip()
                    if strength_text and strength_text not in ['—', '–', '-', '']:
                        strength_match = re.search(r'(\d+)', strength_text)
                        if strength_match:
                            item["strength_requirement"] = int(strength_match.group(1))
                
                # Stealth disadvantage (armor için)
                if stealth_idx is not None and stealth_idx < len(cell_texts):
                    stealth_text = cell_texts[stealth_idx].strip()
                    if 'disadvantage' in stealth_text.lower():
                        item["stealth_disadvantage"] = True
                
                equipment_list.append(item)
        
        return equipment_list
    
    def scrape_all_equipment_links(self) -> List[tuple]:
        """Tüm equipment kategorilerinin linklerini çek - DÜZELTİLDİ (Equipment Scraping)"""
        print("[*] Equipment kategori linkleri cekiliyor...")
        
        # Equipment kategorileri
        equipment_categories = [
            ("Weapons", f"{self.BASE_URL}/equipment/weapons/"),
            ("Armor", f"{self.BASE_URL}/equipment/armor/"),
            ("Adventuring Gear", f"{self.BASE_URL}/equipment/adventuring-gear/"),
            ("Tools", f"{self.BASE_URL}/equipment/tools/"),
        ]
        
        print(f"  [OK] {len(equipment_categories)} equipment kategori linki hazir")
        return equipment_categories
    
    def scrape_all_equipment(self, max_items: Optional[int] = None, force_refresh: bool = False) -> Dict[str, List[Dict[str, Any]]]:
        """Tüm equipment'leri çek - DÜZELTİLDİ (Equipment Scraping)"""
        print("=" * 70)
        print("5ESRD.COM EQUIPMENT ÇEKİLİYOR")
        print("=" * 70)
        
        # Cache kontrolü
        cache_file = Path("data/cache/equipment_cache.json")
        equipment_data = {}
        cached_equipment = {}
        
        if not force_refresh and cache_file.exists():
            print(f"[*] Cache dosyasi bulundu: {cache_file}")
            with open(cache_file, 'r', encoding='utf-8') as f:
                cached = json.load(f)
                if cached.get('equipment'):
                    cached_equipment = cached['equipment']
                    equipment_data.update(cached_equipment)
                    print(f"  [OK] {sum(len(items) for items in cached_equipment.values())} equipment item cache'den yuklendi")
        
        # Equipment kategori linklerini çek
        equipment_links = self.scrape_all_equipment_links()
        
        if not equipment_links:
            print("  [UYARI] Equipment kategori linkleri bulunamadi! Mevcut cache'i donduruyoruz.")
            return cached_equipment
        
        # Her kategori için equipment'leri çek
        for category_name, url in equipment_links:
            if category_name in equipment_data and not force_refresh:
                print(f"  [ATLA] {category_name} zaten cache'de, atlaniyor...")
                continue
            
            print(f"\n[*] {category_name} cekiliyor...")
            print(f"   URL: {url}")
            
            items = self.scrape_equipment_from_table(url, category_name)
            
            if items:
                equipment_data[category_name] = items
                print(f"   [OK] {len(items)} {category_name.lower()} item cekildi")
            else:
                print(f"   [UYARI] {category_name} icin item bulunamadi")
        
        # Cache'e kaydet
        cache_file.parent.mkdir(parents=True, exist_ok=True)
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump({"equipment": equipment_data}, f, indent=2, ensure_ascii=False)
        
        print(f"\n[OK] Equipment data '{cache_file}' dosyasina kaydedildi!")
        print(f"[*] Toplam {sum(len(items) for items in equipment_data.values())} equipment item cekildi.")
        
        return equipment_data

