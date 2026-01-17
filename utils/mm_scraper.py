#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Mutants & Masterminds Web Scraper
d20herosrd.com sitesinden tüm kuralları ve karakter oluşturma bilgilerini çeker.
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class MMScraper:
    """Mutants & Masterminds verilerini d20herosrd.com'dan çeken scraper"""
    
    BASE_URL = "https://www.d20herosrd.com"
    
    # Ana bölümler - Doğru URL'ler (test edilmiş)
    SECTIONS = {
        "character_creation": "/character-creation/",
        "abilities": "/character-creation/3-abilities/",
        "advancement": "/character-creation/advancement/",
        "archetypes": "/character-creation/archetypes/",
        "skills": "/4-skills/",  # Doğru URL - sayı ile başlıyor, /character-creation/ yok
        "advantages": "/5-advantages/",  # Doğru URL - sayı ile başlıyor, /character-creation/ yok
        "powers": "/6-powers/",
        "sample_powers": "/6-powers/sample-powers/",
        "power_effects": "/6-powers/effects/",
        "effect_descriptions": "/6-powers/effects/effect-descriptions/",
        "descriptors": "/6-powers/descriptors/",
        "modifiers": "/6-powers/modifiers/",
        "gadgets": "/gadgets-gear/",
        "conditions": "/gamemastering/conditions/",
        "npcs": "/gamemastering/npcs/",
        "basics": "/the-basics/",
    }
    
    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: İstekler arası bekleme süresi (saniye) - siteyi yormamak için
        """
        self.base_url = self.BASE_URL
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """URL'den HTML içeriğini çek ve BeautifulSoup nesnesi döndür"""
        if not url:
            return None
        full_url = urljoin(self.base_url, url) if not url.startswith("http") else url
        
        for attempt in range(retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(full_url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"❌ Hata: {full_url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_abilities(self) -> Dict[str, Any]:
        """Abilities (Yetenekler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("💪 Abilities çekiliyor...")
        abilities_data = {}
        
        soup = self._get(self.SECTIONS["abilities"])
        if not soup:
            return abilities_data
        
        # Ana içeriği bul
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Tüm abilities'leri bul (8 temel ability)
            abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
            ability_abbrevs = {"Strength": "STR", "Stamina": "STA", "Agility": "AGL", "Dexterity": "DEX", 
                             "Fighting": "FGT", "Intellect": "INT", "Awareness": "AWE", "Presence": "PRE"}
            
            # H3 başlıklarını bul (STRENGTH (STR) formatında)
            h3_headers = main_content.find_all('h3')
            
            for ability_name in abilities:
                ability_header = None
                description_parts = []
                
                # H3 başlıklarında ara (STRENGTH (STR) formatı)
                abbrev = ability_abbrevs.get(ability_name, "")
                for header in h3_headers:
                    header_text = header.get_text(strip=True).upper()
                    # "STRENGTH (STR)" veya "STRENGTH" formatını kontrol et
                    if (ability_name.upper() in header_text or 
                        (abbrev and abbrev in header_text and len(header_text) < 30)):
                        ability_header = header
                        break
                
                # Başlık bulunduysa, sonraki içeriği al
                if ability_header:
                    # Bir sonraki ability başlığını bul (durma noktası)
                    next_ability_index = abilities.index(ability_name) + 1
                    next_ability_name = abilities[next_ability_index] if next_ability_index < len(abilities) else None
                    
                    # Sonraki elementleri al
                    current = ability_header.find_next_sibling()
                    while current:
                        # Bir sonraki H3 başlığına gelince dur (diğer ability başlığı)
                        if current.name == 'h3':
                            current_text = current.get_text(strip=True).upper()
                            # Bir sonraki ability başlığı mı?
                            if next_ability_name and next_ability_name.upper() in current_text:
                                break
                            # Başka bir ability başlığı mı?
                            if any(ab.upper() in current_text and ab != ability_name for ab in abilities):
                                break
                        
                        # İçeriği al (paragraflar)
                        if current.name in ['p', 'div']:
                            text = current.get_text(strip=True)
                            # Footer linklerini filtrele
                            if (len(text) > 30 and 
                                'Green Ronin' not in text and 
                                'Mutants & Masterminds' not in text and
                                'OGN' not in text and
                                'd20pfsrd' not in text.lower() and
                                'Open Gaming' not in text):
                                description_parts.append(text)
                        
                        # Liste öğelerini de al
                        elif current.name in ['ul', 'ol']:
                            items = current.find_all('li')
                            for item in items:
                                text = item.get_text(strip=True)
                                if len(text) > 20 and 'Green Ronin' not in text:
                                    description_parts.append(text)
                        
                        current = current.find_next_sibling()
                        
                        # Çok fazla içerik çekmemek için limit
                        if len(description_parts) >= 15:
                            break
                
                # Başlık bulunamadıysa, text'ten parse et
                if not ability_header or not description_parts:
                    text = main_content.get_text()
                    # Ability adından sonraki metni bul (bir sonraki H3 başlığına kadar)
                    next_ability_pattern = ""
                    if next_ability_name:
                        next_abbrev = ability_abbrevs.get(next_ability_name, "")
                        next_ability_pattern = f"|{next_ability_name.upper()}|{next_abbrev}"
                    
                    pattern = rf'{ability_name.upper()}[:\s(]*{abbrev}[:\s)]*([^A-Z]{{100,2000}}?)(?={next_ability_pattern}|$)'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        description_text = match.group(1).strip()
                        # Çok kısa veya geçersiz metinleri filtrele
                        if len(description_text) > 50:
                            description_parts.append(description_text)
                
                # Ability verisini oluştur
                if description_parts:
                    full_description = "\n\n".join(description_parts)
                    # Çok uzun olanları kısalt
                    if len(full_description) > 2000:
                        full_description = full_description[:2000] + "..."
                    abilities_data[ability_name] = {
                        "name": ability_name,
                        "description": full_description,
                        "cost_per_rank": 1,  # Her ability 1 cost per rank
                        "source": urljoin(self.base_url, self.SECTIONS["abilities"])
                    }
                else:
                    # En azından temel bilgiyi ekle
                    abilities_data[ability_name] = {
                        "name": ability_name,
                        "description": f"{ability_name} is one of the eight core abilities in Mutants & Masterminds.",
                        "cost_per_rank": 1,
                        "source": urljoin(self.base_url, self.SECTIONS["abilities"])
                    }
            
            print(f"  ... {len(abilities_data)} ability bulundu")
        
        print(f"✅ {len(abilities_data)} ability çekildi")
        return abilities_data
    
    def scrape_archetypes(self) -> Dict[str, Any]:
        """Archetypes (Arketipler) bilgilerini çek"""
        print("🎭 Archetypes çekiliyor...")
        archetypes_data = {}
        
        soup = self._get(self.SECTIONS["archetypes"])
        if not soup:
            return archetypes_data
        
        # Ana içeriği bul
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Archetype linklerini bul
            archetype_links = main_content.find_all('a', href=re.compile(r'/character-creation/archetypes/[^/]+/$'))
            
            for link in archetype_links:
                archetype_name = link.get_text(strip=True)
                if archetype_name and archetype_name not in archetypes_data:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    archetype_data = self._scrape_archetype_detail(href, archetype_name)
                    if archetype_data:
                        archetypes_data[archetype_name] = archetype_data
                        print(f"  ✓ {archetype_name}")
        
        print(f"✅ {len(archetypes_data)} archetype çekildi")
        return archetypes_data
    
    def _scrape_archetype_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir archetype'in detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        archetype_data = {
            "name": name,
            "summary": "",
            "suggested_powers": [],
            "suggested_advantages": [],
            "suggested_skills": [],
            "ability_suggestions": {},
            "source": url
        }
        
        # Ana içeriği bul - navigation ve footer'ı hariç tut
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # İlk anlamlı paragrafı bul (çok kısa olmayan)
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Footer linklerini filtrele
                if len(text) > 50 and 'Green Ronin' not in text and 'Mutants & Masterminds' not in text:
                    archetype_data["summary"] = text
                    break
            
            # Powers, Advantages, Skills bölümlerini bul - GELİŞTİRİLMİŞ
            # Tüm metni al
            full_text = main_content.get_text()
            
            # Powers bölümünü bul
            # Pattern 1: "Powers:" veya "Suggested Powers:" başlığından sonra
            powers_section = main_content.find(string=re.compile(r'[Pp]owers?[:\s]', re.I))
            if powers_section:
                parent = powers_section.find_parent()
                if parent:
                    # Sonraki içeriği al (liste veya paragraf)
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            powers = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_powers"] = powers[:30]
                        else:
                            # Paragraftan power isimlerini çıkar
                            text = next_elem.get_text(strip=True)
                            # Power isimleri genellikle büyük harfle başlar
                            powers = re.findall(r'\b([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\b', text)
                            archetype_data["suggested_powers"] = [p.strip() for p in powers if len(p.strip()) < 50][:30]
            
            # Eğer bulunamadıysa, text'ten parse et
            if not archetype_data["suggested_powers"]:
                # "Powers:" veya "Powers" başlığından sonraki metni bul
                powers_match = re.search(r'[Pp]owers?[:\s]+([^A-Z]{20,500}?)(?=[Aa]dvantages?|[Ss]kills?|$)', full_text, re.IGNORECASE | re.DOTALL)
                if powers_match:
                    powers_text = powers_match.group(1)
                    # Power isimlerini çıkar (büyük harfle başlayan, virgülle ayrılmış)
                    powers = re.findall(r'\b([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\b', powers_text)
                    archetype_data["suggested_powers"] = [p.strip() for p in powers if len(p.strip()) < 50 and p.strip() != name][:30]
            
            # Advantages bölümünü bul - DÜZELTİLDİ (virgülle ayrılmış format)
            advantages_section = main_content.find(string=re.compile(r'[Aa]dvantages?[:\s]', re.I))
            if advantages_section:
                parent = advantages_section.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            advantages = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_advantages"] = advantages[:30]
                        else:
                            text = next_elem.get_text(strip=True)
                            # Virgülle ayrılmış advantage listesi
                            advantages = [a.strip() for a in text.split(',') if a.strip() and len(a.strip()) < 80]
                            archetype_data["suggested_advantages"] = advantages[:30]
            
            # Eğer bulunamadıysa, text'ten parse et - DÜZELTİLDİ
            if not archetype_data["suggested_advantages"]:
                # "Advantages:" başlığından sonraki satırı bul
                advantages_match = re.search(r'[Aa]dvantages?[:\s]*\n\s*([^\n]{20,500}?)(?=\n[A-Z]|\n\n|$)', full_text, re.IGNORECASE | re.DOTALL)
                if advantages_match:
                    advantages_text = advantages_match.group(1).strip()
                    # Virgülle ayrılmış advantage listesi
                    advantages = [a.strip() for a in advantages_text.split(',') if a.strip() and len(a.strip()) < 80]
                    # Çok kısa veya geçersiz olanları filtrele
                    advantages = [a for a in advantages if len(a) > 3 and not a.startswith('(') and not a.endswith(')')]
                    archetype_data["suggested_advantages"] = advantages[:30]
            
            # Skills bölümünü bul - DÜZELTİLDİ
            skills_section = main_content.find(string=re.compile(r'[Ss]kills?[:\s]', re.I))
            if skills_section:
                parent = skills_section.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            skills = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_skills"] = skills[:30]
                        else:
                            text = next_elem.get_text(strip=True)
                            # Skill formatı: "Skill Name: X (+Y)" veya "Skill Name X (+Y)", virgülle ayrılmış
                            # Önce virgülle ayır, sonra skill isimlerini çıkar
                            skills_parts = text.split(',')
                            skills = []
                            for part in skills_parts:
                                part = part.strip()
                                # Skill ismini çıkar (başında rakam veya parantez varsa öncesini al)
                                # "Insight 4 (+6)" -> "Insight"
                                skill_match = re.match(r'^([A-Z][A-Za-z\s]+(?:\([^)]+\))?)', part)
                                if skill_match:
                                    skill_name = skill_match.group(1).strip()
                                    # Parantez içindeki "Choose one of" gibi açıklamaları dahil et
                                    if '(' in skill_name and 'Choose' in skill_name:
                                        # "Expertise: (Choose one of Business, Engineering, or Science)" -> "Expertise (Choose one of Business, Engineering, or Science)"
                                        pass
                                    # Çok uzun olanları filtrele
                                    if len(skill_name) < 80:
                                        skills.append(skill_name)
                            archetype_data["suggested_skills"] = skills[:30]
            
            # Eğer bulunamadıysa, text'ten parse et - DÜZELTİLDİ
            if not archetype_data["suggested_skills"]:
                # "Skills:" başlığından sonraki satırı bul
                skills_match = re.search(r'[Ss]kills?[:\s]*\n\s*([^\n]{50,1000}?)(?=\n[A-Z]|\n\n|$)', full_text, re.IGNORECASE | re.DOTALL)
                if skills_match:
                    skills_text = skills_match.group(1).strip()
                    # Virgülle ayrılmış skill listesi
                    skills_parts = skills_text.split(',')
                    skills = []
                    for part in skills_parts:
                        part = part.strip()
                        # Skill ismini çıkar (rakam ve parantez öncesi)
                        # "Insight 4 (+6)" -> "Insight"
                        skill_match = re.match(r'^([A-Z][A-Za-z\s]+(?:\([^)]+\))?)', part)
                        if skill_match:
                            skill_name = skill_match.group(1).strip()
                            # "Expertise: (Choose one of...)" formatını koru
                            if ':' in skill_name:
                                skill_name = skill_name.replace(':', '').strip()
                            if len(skill_name) < 80 and skill_name not in skills:
                                skills.append(skill_name)
                    archetype_data["suggested_skills"] = skills[:30]
            
            # Ability suggestions - genellikle tablo veya liste formatında
            # Örneğin: "Strength 8, Stamina 4, Agility 2, Dexterity 2, Fighting 4, Intellect 6, Awareness 4, Presence 2"
            ability_match = re.search(r'(Strength|Stamina|Agility|Dexterity|Fighting|Intellect|Awareness|Presence)\s+(\d+)', full_text, re.I)
            if ability_match:
                # Tüm ability'leri bul
                abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
                for ability in abilities:
                    pattern = rf'{ability}\s+(\d+)'
                    match = re.search(pattern, full_text, re.I)
                    if match:
                        archetype_data["ability_suggestions"][ability] = int(match.group(1))
        
        return archetype_data
    
    def _find_section_url(self, section_name: str, base_url: str = None) -> Optional[str]:
        """Belirli bir bölümün URL'ini bul"""
        if base_url is None:
            base_url = self.SECTIONS["character_creation"]
        
        soup = self._get(base_url)
        if not soup:
            return None
        
        # Section name'i içeren linkleri bul
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            if section_name.lower() in text or section_name.lower().replace(' ', '-') in href.lower():
                if href.startswith('/'):
                    return href
                elif href.startswith('http'):
                    return href.replace(self.base_url, '')
        
        return None
    
    def scrape_skills(self) -> Dict[str, Any]:
        """Skills (Beceriler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("🎯 Skills çekiliyor...")
        skills_data = {}
        
        # Doğru URL'i kullan
        skills_url = self.SECTIONS["skills"]
        
        soup = self._get(skills_url)
        if not soup:
            return skills_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Skills sayfasında genellikle tablo veya liste formatında skill'ler var
            # Skill linklerini bul (anchor linkleri)
            skill_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
            
            # Eğer anchor linkleri varsa, skill isimlerini çıkar
            if skill_links:
                for link in skill_links:
                    skill_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    # "Skill Name (Ability)" formatını parse et
                    match = re.match(r'([A-Z][A-Z\s]+(?:\([^)]+\))?)\s*\(?([A-Z][a-z]+)\)?', skill_text)
                    if match:
                        skill_name = match.group(1).strip()
                        ability = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""
                    else:
                        skill_name = skill_text
                        ability = ""
                    
                    # Ability'yi href'ten de çıkarabiliriz
                    ability_match = re.search(r'#TOC-[A-Z]+-([A-Z][a-z]+)', href)
                    if ability_match:
                        ability = ability_match.group(1)
                    
                    if skill_name and len(skill_name) < 50 and skill_name not in skills_data:
                        skills_data[skill_name] = {
                            "name": skill_name,
                            "key_ability": ability,
                            "cost_per_rank": 1,  # Varsayılan
                            "description": "",
                            "source": urljoin(self.base_url, skills_url + href)
                        }
            
            # Eğer link yoksa, tablo veya liste formatında skill'leri bul
            if not skills_data:
                text = main_content.get_text()
                # Skill pattern'i: "Skill Name (Ability)" veya "Skill Name: Ability"
                skill_patterns = [
                    r'([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\s+\(([A-Z][a-z]+)\)',  # "Skill Name (Ability)"
                    r'([A-Z][A-Za-z\s]+):\s+([A-Z][a-z]+)',  # "Skill Name: Ability"
                ]
                
                for pattern in skill_patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        skill_name = match.group(1).strip()
                        ability = match.group(2) if len(match.groups()) > 1 else ""
                        
                        # Çok uzun veya geçersiz olanları filtrele
                        if (skill_name and len(skill_name) < 50 and 
                            skill_name not in skills_data and
                            skill_name[0].isupper() and
                            ability in ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]):
                            skills_data[skill_name] = {
                                "name": skill_name,
                                "key_ability": ability,
                                "cost_per_rank": 1,
                                "description": "",
                                "source": urljoin(self.base_url, skills_url)
                            }
            
            print(f"  ... {len(skills_data)} skill bulundu")
        
        print(f"✅ {len(skills_data)} skill çekildi")
        return skills_data
    
    def scrape_advantages(self) -> Dict[str, Any]:
        """Advantages (Avantajlar) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("⭐ Advantages çekiliyor...")
        advantages_data = {}
        
        # Doğru URL'i kullan
        advantages_url = self.SECTIONS["advantages"]
        
        soup = self._get(advantages_url)
        if not soup:
            return advantages_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Advantages sayfasında genellikle anchor linkleri veya liste formatında advantage'ler var
            # Advantage linklerini bul (anchor linkleri)
            advantage_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
            
            # Eğer anchor linkleri varsa, advantage isimlerini çıkar
            if advantage_links:
                for link in advantage_links:
                    advantage_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # "Advantage Name" veya "Advantage Name (Cost)" formatını parse et
                    match = re.match(r'([A-Z][A-Z\s&()-]+(?:\([^)]+\))?)', advantage_text)
                    if match:
                        advantage_name = match.group(1).strip()
                        # Cost bilgisini çıkar
                        cost_match = re.search(r'\(([0-9]+)\s*(?:rank|point)', advantage_text, re.I)
                        cost = int(cost_match.group(1)) if cost_match else 1
                    else:
                        advantage_name = advantage_text
                        cost = 1
                    
                    if advantage_name and len(advantage_name) < 80 and advantage_name not in advantages_data:
                        advantages_data[advantage_name] = {
                            "name": advantage_name,
                            "cost": cost,
                            "description": "",
                            "source": urljoin(self.base_url, advantages_url + href)
                        }
                        
                        # Detay sayfasından açıklama çek (eğer varsa)
                        if href.startswith('#'):
                            # Anchor link, aynı sayfada detay bul
                            anchor_id = href.replace('#', '').replace('TOC-', '')
                            # Anchor'a git ve sonraki içeriği al
                            anchor = main_content.find('a', {'name': anchor_id}) or main_content.find('a', {'id': anchor_id})
                            if anchor:
                                parent = anchor.find_parent(['h2', 'h3', 'h4', 'p', 'div'])
                                if parent:
                                    next_elem = parent.find_next_sibling('p')
                                    if next_elem:
                                        advantages_data[advantage_name]["description"] = next_elem.get_text(strip=True)
            
            # Eğer anchor linkleri yoksa, direkt advantage'leri bul
            if not advantages_data:
                # Tüm başlıkları ve altındaki içeriği bul
                headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
                for header in headers:
                    header_text = header.get_text(strip=True)
                    # Geçersiz başlıkları filtrele
                    if (len(header_text) < 80 and 
                        header_text[0].isupper() and
                        'Advantage' not in header_text and
                        not header_text.startswith('Table') and
                        not header_text.startswith('See')):
                        
                        # Sonraki paragrafı al
                        next_elem = header.find_next_sibling(['p', 'div'])
                        if next_elem:
                            description = next_elem.get_text(strip=True)
                            # Cost bilgisini çıkar
                            cost_match = re.search(r'Cost[:\s]+(\d+)', description, re.I)
                            cost = int(cost_match.group(1)) if cost_match else 1
                            
                            advantages_data[header_text] = {
                                "name": header_text,
                                "cost": cost,
                                "description": description[:500],  # İlk 500 karakter
                                "source": urljoin(self.base_url, advantages_url)
                            }
            
            print(f"  ... {len(advantages_data)} advantage bulundu")
        
        print(f"✅ {len(advantages_data)} advantage çekildi")
        return advantages_data
    
    def _scrape_advantage_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir advantage'in detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        advantage_data = {
            "name": name,
            "cost": 1,  # Varsayılan
            "description": "",
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Cost bilgisini bul
            cost_match = re.search(r'Cost[:\s]+(\d+)', main_content.get_text(), re.IGNORECASE)
            if cost_match:
                advantage_data["cost"] = int(cost_match.group(1))
            
            # Description'ı bul
            desc_p = main_content.find('p')
            if desc_p:
                advantage_data["description"] = desc_p.get_text(strip=True)
        
        return advantage_data
    
    def scrape_powers(self) -> Dict[str, Any]:
        """Powers (Güçler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("⚡ Powers çekiliyor...")
        powers_data = {}
        
        # Sample Powers sayfasından başla
        sample_powers_url = self.SECTIONS["sample_powers"]
        
        soup = self._get(sample_powers_url)
        if not soup:
            return powers_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Power linklerini bul - hem /sample-powers/ hem de /6-powers/ altında olabilir
            power_links = main_content.find_all('a', href=re.compile(r'/6-powers/sample-powers/[^/]+/$'))
            
            # Eğer link bulunamazsa, anchor linkleri dene
            if not power_links:
                power_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
                # Power isimlerini çıkar
                for link in power_links:
                    power_text = link.get_text(strip=True)
                    # Çok uzun veya geçersiz olanları filtrele
                    if (power_text and len(power_text) < 80 and 
                        power_text[0].isupper() and
                        power_text not in powers_data):
                        # Power detayını aynı sayfadan çek
                        power_data = self._scrape_power_detail_from_same_page(main_content, power_text)
                        if power_data:
                            powers_data[power_text] = power_data
            
            # Direkt linkler varsa, detay sayfalarını çek
            for link in power_links:
                power_name = link.get_text(strip=True)
                if power_name and power_name not in powers_data and len(power_name) < 80:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    power_data = self._scrape_power_detail(href, power_name)
                    if power_data:
                        powers_data[power_name] = power_data
                        if len(powers_data) % 10 == 0:
                            print(f"  ... {len(powers_data)} power çekildi")
            
            print(f"  ... {len(powers_data)} power bulundu")
        
        print(f"✅ {len(powers_data)} power çekildi")
        return powers_data
    
    def _scrape_power_detail_from_same_page(self, main_content, power_name: str) -> Optional[Dict[str, Any]]:
        """Aynı sayfadan power detayını çek (anchor linkler için)"""
        power_data = {
            "name": power_name,
            "cost_per_rank": 1,
            "description": "",
            "source": urljoin(self.base_url, self.SECTIONS["sample_powers"])
        }
        
        # Power adını içeren başlığı bul
        headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
        for header in headers:
            header_text = header.get_text(strip=True)
            if power_name.lower() in header_text.lower() or header_text.lower() in power_name.lower():
                # Sonraki paragrafları al
                description_parts = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 20:
                        description_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    # Bir sonraki başlığa gelince dur
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if len(description_parts) >= 10:
                        break
                
                power_data["description"] = "\n\n".join(description_parts)
                break
        
        return power_data
    
    def _scrape_power_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir power'ın detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        power_data = {
            "name": name,
            "cost_per_rank": 1,  # Varsayılan
            "description": "",
            "effects": [],
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Cost bilgisini bul
            cost_match = re.search(r'Cost[:\s]+(\d+)', main_content.get_text(), re.IGNORECASE)
            if cost_match:
                power_data["cost_per_rank"] = int(cost_match.group(1))
            
            # Description'ı bul
            desc_p = main_content.find('p')
            if desc_p:
                power_data["description"] = desc_p.get_text(strip=True)
        
        return power_data
    
    def scrape_power_effects(self) -> Dict[str, Any]:
        """Power Effects bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("✨ Power Effects çekiliyor...")
        effects_data = {}
        
        # Effect Descriptions sayfasından başla
        effects_url = self.SECTIONS["effect_descriptions"]
        
        soup = self._get(effects_url)
        if not soup:
            # Alternatif URL dene
            effects_url = self.SECTIONS["power_effects"]
            soup = self._get(effects_url)
        
        if not soup:
            return effects_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Effect linklerini bul - DÜZELTİLDİ (doğru pattern)
            # Format: /6-powers/effects/effect-descriptions/[effect-name]/
            effect_links = main_content.find_all('a', href=re.compile(r'/6-powers/effects/effect-descriptions/[^/]+/$'))
            
            print(f"  ... {len(effect_links)} effect linki bulundu")
            
            # Her effect linkini işle
            for link in effect_links:
                effect_name = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Geçersiz linkleri filtrele
                if not effect_name or len(effect_name) > 100 or effect_name in effects_data:
                    continue
                
                # Effect adını temizle (örn: "AFFLICTION (ATTACK)" -> "AFFLICTION")
                # Category'yi parantez içinden çıkar
                category_match = re.search(r'\(([A-Z]+)\)', effect_name)
                category = category_match.group(1) if category_match else ""
                # Category mapping
                category_map = {
                    "ATTACK": "Attack",
                    "DEFENSE": "Defense",
                    "MOVEMENT": "Movement",
                    "CONTROL": "Control",
                    "GENERAL": "General",
                    "SENSORY": "Sensory"
                }
                category = category_map.get(category, "")
                
                # Effect adını temizle (parantez ve category'yi kaldır)
                clean_name = re.sub(r'\s*\([^)]+\)', '', effect_name).strip()
                
                # Detay sayfasını çek
                if not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                
                effect_data = self._scrape_effect_detail(href, clean_name)
                if effect_data:
                    # Category'yi ekle (eğer detay sayfasında yoksa)
                    if category and not effect_data.get("category"):
                        effect_data["category"] = category
                    # Effect name'i güncelle
                    effect_data["name"] = clean_name
                    effects_data[clean_name] = effect_data
                    
                    if len(effects_data) % 10 == 0:
                        print(f"    ... {len(effects_data)} effect çekildi")
                else:
                    # Eğer detay sayfası çekilemediyse, en azından temel bilgiyi kaydet
                    effects_data[clean_name] = {
                        "name": clean_name,
                        "category": category,
                        "cost_per_rank": 1,
                        "description": f"{clean_name} is a power effect in Mutants & Masterminds.",
                        "source": href if href.startswith('http') else urljoin(self.base_url, href)
                    }
            
            # Eğer link bulunamadıysa, başlıklardan çek
            if not effects_data:
                headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
                for header in headers:
                    header_text = header.get_text(strip=True)
                    # Geçersiz başlıkları filtrele
                    if (len(header_text) < 100 and 
                        header_text[0].isupper() and
                        not header_text.startswith('Table') and
                        not header_text.startswith('See') and
                        '(' not in header_text):  # "(ATTACK)" gibi formatları filtrele
                        
                        # Sonraki paragrafları al
                        description_parts = []
                        next_elem = header.find_next_sibling()
                        while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                            text = next_elem.get_text(strip=True)
                            if len(text) > 20:
                                description_parts.append(text)
                            next_elem = next_elem.find_next_sibling()
                            # Bir sonraki başlığa gelince dur
                            if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                                break
                            if len(description_parts) >= 10:
                                break
                        
                        # Category'yi header'dan çıkar
                        category = ""
                        if 'ATTACK' in header_text.upper():
                            category = "Attack"
                        elif 'DEFENSE' in header_text.upper():
                            category = "Defense"
                        elif 'MOVEMENT' in header_text.upper():
                            category = "Movement"
                        elif 'CONTROL' in header_text.upper():
                            category = "Control"
                        elif 'GENERAL' in header_text.upper():
                            category = "General"
                        elif 'SENSORY' in header_text.upper():
                            category = "Sensory"
                        
                        effects_data[header_text] = {
                            "name": header_text,
                            "category": category,
                            "cost_per_rank": 1,
                            "description": "\n\n".join(description_parts),
                            "source": urljoin(self.base_url, effects_url)
                        }
            
            print(f"  ... {len(effects_data)} effect bulundu")
        
        print(f"✅ {len(effects_data)} power effect çekildi")
        return effects_data
    
    def _scrape_effect_detail_from_same_page(self, main_content, effect_name: str) -> Optional[Dict[str, Any]]:
        """Aynı sayfadan effect detayını çek"""
        effect_data = {
            "name": effect_name,
            "category": "",
            "cost_per_rank": 1,
            "description": "",
            "source": urljoin(self.base_url, self.SECTIONS["effect_descriptions"])
        }
        
        # Effect adını içeren başlığı bul
        headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
        for header in headers:
            header_text = header.get_text(strip=True)
            if effect_name.lower() in header_text.lower() or header_text.lower() in effect_name.lower():
                # Category'yi belirle
                if 'ATTACK' in header_text.upper():
                    effect_data["category"] = "Attack"
                elif 'DEFENSE' in header_text.upper():
                    effect_data["category"] = "Defense"
                elif 'MOVEMENT' in header_text.upper():
                    effect_data["category"] = "Movement"
                elif 'CONTROL' in header_text.upper():
                    effect_data["category"] = "Control"
                elif 'GENERAL' in header_text.upper():
                    effect_data["category"] = "General"
                elif 'SENSORY' in header_text.upper():
                    effect_data["category"] = "Sensory"
                
                # Sonraki paragrafları al
                description_parts = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 20:
                        description_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if len(description_parts) >= 10:
                        break
                
                effect_data["description"] = "\n\n".join(description_parts)
                break
        
        return effect_data
    
    def _scrape_effect_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir effect'in detay sayfasını çek - GELİŞTİRİLMİŞ"""
        soup = self._get(url)
        if not soup:
            return None
        
        effect_data = {
            "name": name,
            "category": "",  # Attack, Defense, Movement, etc.
            "cost_per_rank": 1,
            "description": "",
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Effect başlığını bul (h1, h2, h3)
            effect_header = None
            headers = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
            for header in headers:
                header_text = header.get_text(strip=True).upper()
                if name.upper() in header_text or header_text.startswith(name.upper()):
                    effect_header = header
                    # Category'yi header'dan çıkar
                    category_match = re.search(r'\(([A-Z]+)\)', header_text)
                    if category_match:
                        category_map = {
                            "ATTACK": "Attack",
                            "DEFENSE": "Defense",
                            "MOVEMENT": "Movement",
                            "CONTROL": "Control",
                            "GENERAL": "General",
                            "SENSORY": "Sensory"
                        }
                        category = category_match.group(1)
                        effect_data["category"] = category_map.get(category, "")
                    break
            
            # Category'yi bul (eğer header'da yoksa)
            if not effect_data["category"]:
                category_match = re.search(r'(Attack|Defense|Movement|Control|General|Sensory)', main_content.get_text(), re.I)
                if category_match:
                    effect_data["category"] = category_match.group(1).capitalize()
            
            # Description'ı bul - başlıktan sonraki paragrafları al
            description_parts = []
            start_elem = effect_header if effect_header else main_content
            
            # İlk paragrafları al
            next_elem = start_elem.find_next_sibling() if effect_header else main_content.find('p')
            while next_elem:
                if next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    # Bir sonraki başlığa gelince dur
                    break
                
                if next_elem.name in ['p', 'div']:
                    text = next_elem.get_text(strip=True)
                    # Footer linklerini filtrele
                    if (len(text) > 30 and 
                        'Green Ronin' not in text and 
                        'Mutants & Masterminds' not in text and
                        'OGN' not in text and
                        'd20pfsrd' not in text.lower()):
                        description_parts.append(text)
                
                next_elem = next_elem.find_next_sibling()
                
                # Çok fazla içerik çekmemek için limit
                if len(description_parts) >= 15:
                    break
            
            # Eğer paragraflar bulunamadıysa, ilk paragrafı al
            if not description_parts:
                # Tüm paragrafları bul
                all_paragraphs = main_content.find_all('p')
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    # Footer linklerini filtrele
                    if (len(text) > 30 and 
                        'Green Ronin' not in text and 
                        'Mutants & Masterminds' not in text and
                        'OGN' not in text and
                        'd20pfsrd' not in text.lower() and
                        'Open Gaming' not in text):
                        description_parts.append(text)
                        if len(description_parts) >= 5:
                            break
            
            # Eğer hala açıklama yoksa, tüm içeriği al
            if not description_parts:
                full_text = main_content.get_text()
                # Effect adından sonraki metni bul
                pattern = rf'{re.escape(name)}[:\s]*([^A-Z]{{100,1500}}?)(?=[A-Z]{{3,}}|\n\n|$)'
                match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
                if match:
                    description_parts.append(match.group(1).strip())
            
            if description_parts:
                effect_data["description"] = "\n\n".join(description_parts)[:2000]  # İlk 2000 karakter
            else:
                effect_data["description"] = f"{name} is a power effect in Mutants & Masterminds."
        
        return effect_data
    
    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tüm M&M verilerini çek ve birleştir"""
        print("🚀 Mutants & Masterminds verileri çekiliyor...")
        print("⚠️  Bu işlem birkaç dakika sürebilir. Lütfen bekleyin...\n")
        
        data = {
            "system": "MUTANTS_AND_MASTERMINDS",
            "source": "d20herosrd.com",
            "abilities": self.scrape_abilities(),
            "archetypes": self.scrape_archetypes(),
            "skills": self.scrape_skills(),
            "advantages": self.scrape_advantages(),
            "powers": self.scrape_powers(),
            "power_effects": self.scrape_power_effects(),
            "power_levels": {  # Sabit değerler
                "PL8": {"attack_bonus_cap": 8, "effect_rank_cap": 10, "defense_cap": 8, "toughness_cap": 10},
                "PL10": {"attack_bonus_cap": 10, "effect_rank_cap": 10, "defense_cap": 10, "toughness_cap": 10},
                "PL12": {"attack_bonus_cap": 12, "effect_rank_cap": 12, "defense_cap": 12, "toughness_cap": 12},
                "PL15": {"attack_bonus_cap": 15, "effect_rank_cap": 15, "defense_cap": 15, "toughness_cap": 15},
            }
        }
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Veriler kaydedildi: {output_file}")
        
        return data


if __name__ == "__main__":
    # Test için
    scraper = MMScraper(delay=1.0)
    output = Path(__file__).resolve().parents[1] / "data" / "mm_data.json"
    scraper.scrape_all(output_file=output)


"""
Mutants & Masterminds Web Scraper
d20herosrd.com sitesinden tüm kuralları ve karakter oluşturma bilgilerini çeker.
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class MMScraper:
    """Mutants & Masterminds verilerini d20herosrd.com'dan çeken scraper"""
    
    BASE_URL = "https://www.d20herosrd.com"
    
    # Ana bölümler - Doğru URL'ler (test edilmiş)
    SECTIONS = {
        "character_creation": "/character-creation/",
        "abilities": "/character-creation/3-abilities/",
        "advancement": "/character-creation/advancement/",
        "archetypes": "/character-creation/archetypes/",
        "skills": "/4-skills/",  # Doğru URL - sayı ile başlıyor, /character-creation/ yok
        "advantages": "/5-advantages/",  # Doğru URL - sayı ile başlıyor, /character-creation/ yok
        "powers": "/6-powers/",
        "sample_powers": "/6-powers/sample-powers/",
        "power_effects": "/6-powers/effects/",
        "effect_descriptions": "/6-powers/effects/effect-descriptions/",
        "descriptors": "/6-powers/descriptors/",
        "modifiers": "/6-powers/modifiers/",
        "gadgets": "/gadgets-gear/",
        "conditions": "/gamemastering/conditions/",
        "npcs": "/gamemastering/npcs/",
        "basics": "/the-basics/",
    }
    
    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: İstekler arası bekleme süresi (saniye) - siteyi yormamak için
        """
        self.base_url = self.BASE_URL
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """URL'den HTML içeriğini çek ve BeautifulSoup nesnesi döndür"""
        if not url:
            return None
        full_url = urljoin(self.base_url, url) if not url.startswith("http") else url
        
        for attempt in range(retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(full_url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"❌ Hata: {full_url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_abilities(self) -> Dict[str, Any]:
        """Abilities (Yetenekler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("💪 Abilities çekiliyor...")
        abilities_data = {}
        
        soup = self._get(self.SECTIONS["abilities"])
        if not soup:
            return abilities_data
        
        # Ana içeriği bul
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Tüm abilities'leri bul (8 temel ability)
            abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
            ability_abbrevs = {"Strength": "STR", "Stamina": "STA", "Agility": "AGL", "Dexterity": "DEX", 
                             "Fighting": "FGT", "Intellect": "INT", "Awareness": "AWE", "Presence": "PRE"}
            
            # H3 başlıklarını bul (STRENGTH (STR) formatında)
            h3_headers = main_content.find_all('h3')
            
            for ability_name in abilities:
                ability_header = None
                description_parts = []
                
                # H3 başlıklarında ara (STRENGTH (STR) formatı)
                abbrev = ability_abbrevs.get(ability_name, "")
                for header in h3_headers:
                    header_text = header.get_text(strip=True).upper()
                    # "STRENGTH (STR)" veya "STRENGTH" formatını kontrol et
                    if (ability_name.upper() in header_text or 
                        (abbrev and abbrev in header_text and len(header_text) < 30)):
                        ability_header = header
                        break
                
                # Başlık bulunduysa, sonraki içeriği al
                if ability_header:
                    # Bir sonraki ability başlığını bul (durma noktası)
                    next_ability_index = abilities.index(ability_name) + 1
                    next_ability_name = abilities[next_ability_index] if next_ability_index < len(abilities) else None
                    
                    # Sonraki elementleri al
                    current = ability_header.find_next_sibling()
                    while current:
                        # Bir sonraki H3 başlığına gelince dur (diğer ability başlığı)
                        if current.name == 'h3':
                            current_text = current.get_text(strip=True).upper()
                            # Bir sonraki ability başlığı mı?
                            if next_ability_name and next_ability_name.upper() in current_text:
                                break
                            # Başka bir ability başlığı mı?
                            if any(ab.upper() in current_text and ab != ability_name for ab in abilities):
                                break
                        
                        # İçeriği al (paragraflar)
                        if current.name in ['p', 'div']:
                            text = current.get_text(strip=True)
                            # Footer linklerini filtrele
                            if (len(text) > 30 and 
                                'Green Ronin' not in text and 
                                'Mutants & Masterminds' not in text and
                                'OGN' not in text and
                                'd20pfsrd' not in text.lower() and
                                'Open Gaming' not in text):
                                description_parts.append(text)
                        
                        # Liste öğelerini de al
                        elif current.name in ['ul', 'ol']:
                            items = current.find_all('li')
                            for item in items:
                                text = item.get_text(strip=True)
                                if len(text) > 20 and 'Green Ronin' not in text:
                                    description_parts.append(text)
                        
                        current = current.find_next_sibling()
                        
                        # Çok fazla içerik çekmemek için limit
                        if len(description_parts) >= 15:
                            break
                
                # Başlık bulunamadıysa, text'ten parse et
                if not ability_header or not description_parts:
                    text = main_content.get_text()
                    # Ability adından sonraki metni bul (bir sonraki H3 başlığına kadar)
                    next_ability_pattern = ""
                    if next_ability_name:
                        next_abbrev = ability_abbrevs.get(next_ability_name, "")
                        next_ability_pattern = f"|{next_ability_name.upper()}|{next_abbrev}"
                    
                    pattern = rf'{ability_name.upper()}[:\s(]*{abbrev}[:\s)]*([^A-Z]{{100,2000}}?)(?={next_ability_pattern}|$)'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        description_text = match.group(1).strip()
                        # Çok kısa veya geçersiz metinleri filtrele
                        if len(description_text) > 50:
                            description_parts.append(description_text)
                
                # Ability verisini oluştur
                if description_parts:
                    full_description = "\n\n".join(description_parts)
                    # Çok uzun olanları kısalt
                    if len(full_description) > 2000:
                        full_description = full_description[:2000] + "..."
                    abilities_data[ability_name] = {
                        "name": ability_name,
                        "description": full_description,
                        "cost_per_rank": 1,  # Her ability 1 cost per rank
                        "source": urljoin(self.base_url, self.SECTIONS["abilities"])
                    }
                else:
                    # En azından temel bilgiyi ekle
                    abilities_data[ability_name] = {
                        "name": ability_name,
                        "description": f"{ability_name} is one of the eight core abilities in Mutants & Masterminds.",
                        "cost_per_rank": 1,
                        "source": urljoin(self.base_url, self.SECTIONS["abilities"])
                    }
            
            print(f"  ... {len(abilities_data)} ability bulundu")
        
        print(f"✅ {len(abilities_data)} ability çekildi")
        return abilities_data
    
    def scrape_archetypes(self) -> Dict[str, Any]:
        """Archetypes (Arketipler) bilgilerini çek"""
        print("🎭 Archetypes çekiliyor...")
        archetypes_data = {}
        
        soup = self._get(self.SECTIONS["archetypes"])
        if not soup:
            return archetypes_data
        
        # Ana içeriği bul
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Archetype linklerini bul
            archetype_links = main_content.find_all('a', href=re.compile(r'/character-creation/archetypes/[^/]+/$'))
            
            for link in archetype_links:
                archetype_name = link.get_text(strip=True)
                if archetype_name and archetype_name not in archetypes_data:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    archetype_data = self._scrape_archetype_detail(href, archetype_name)
                    if archetype_data:
                        archetypes_data[archetype_name] = archetype_data
                        print(f"  ✓ {archetype_name}")
        
        print(f"✅ {len(archetypes_data)} archetype çekildi")
        return archetypes_data
    
    def _scrape_archetype_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir archetype'in detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        archetype_data = {
            "name": name,
            "summary": "",
            "suggested_powers": [],
            "suggested_advantages": [],
            "suggested_skills": [],
            "ability_suggestions": {},
            "source": url
        }
        
        # Ana içeriği bul - navigation ve footer'ı hariç tut
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # İlk anlamlı paragrafı bul (çok kısa olmayan)
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Footer linklerini filtrele
                if len(text) > 50 and 'Green Ronin' not in text and 'Mutants & Masterminds' not in text:
                    archetype_data["summary"] = text
                    break
            
            # Powers, Advantages, Skills bölümlerini bul - GELİŞTİRİLMİŞ
            # Tüm metni al
            full_text = main_content.get_text()
            
            # Powers bölümünü bul
            # Pattern 1: "Powers:" veya "Suggested Powers:" başlığından sonra
            powers_section = main_content.find(string=re.compile(r'[Pp]owers?[:\s]', re.I))
            if powers_section:
                parent = powers_section.find_parent()
                if parent:
                    # Sonraki içeriği al (liste veya paragraf)
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            powers = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_powers"] = powers[:30]
                        else:
                            # Paragraftan power isimlerini çıkar
                            text = next_elem.get_text(strip=True)
                            # Power isimleri genellikle büyük harfle başlar
                            powers = re.findall(r'\b([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\b', text)
                            archetype_data["suggested_powers"] = [p.strip() for p in powers if len(p.strip()) < 50][:30]
            
            # Eğer bulunamadıysa, text'ten parse et
            if not archetype_data["suggested_powers"]:
                # "Powers:" veya "Powers" başlığından sonraki metni bul
                powers_match = re.search(r'[Pp]owers?[:\s]+([^A-Z]{20,500}?)(?=[Aa]dvantages?|[Ss]kills?|$)', full_text, re.IGNORECASE | re.DOTALL)
                if powers_match:
                    powers_text = powers_match.group(1)
                    # Power isimlerini çıkar (büyük harfle başlayan, virgülle ayrılmış)
                    powers = re.findall(r'\b([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\b', powers_text)
                    archetype_data["suggested_powers"] = [p.strip() for p in powers if len(p.strip()) < 50 and p.strip() != name][:30]
            
            # Advantages bölümünü bul - DÜZELTİLDİ (virgülle ayrılmış format)
            advantages_section = main_content.find(string=re.compile(r'[Aa]dvantages?[:\s]', re.I))
            if advantages_section:
                parent = advantages_section.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            advantages = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_advantages"] = advantages[:30]
                        else:
                            text = next_elem.get_text(strip=True)
                            # Virgülle ayrılmış advantage listesi
                            advantages = [a.strip() for a in text.split(',') if a.strip() and len(a.strip()) < 80]
                            archetype_data["suggested_advantages"] = advantages[:30]
            
            # Eğer bulunamadıysa, text'ten parse et - DÜZELTİLDİ
            if not archetype_data["suggested_advantages"]:
                # "Advantages:" başlığından sonraki satırı bul
                advantages_match = re.search(r'[Aa]dvantages?[:\s]*\n\s*([^\n]{20,500}?)(?=\n[A-Z]|\n\n|$)', full_text, re.IGNORECASE | re.DOTALL)
                if advantages_match:
                    advantages_text = advantages_match.group(1).strip()
                    # Virgülle ayrılmış advantage listesi
                    advantages = [a.strip() for a in advantages_text.split(',') if a.strip() and len(a.strip()) < 80]
                    # Çok kısa veya geçersiz olanları filtrele
                    advantages = [a for a in advantages if len(a) > 3 and not a.startswith('(') and not a.endswith(')')]
                    archetype_data["suggested_advantages"] = advantages[:30]
            
            # Skills bölümünü bul - DÜZELTİLDİ
            skills_section = main_content.find(string=re.compile(r'[Ss]kills?[:\s]', re.I))
            if skills_section:
                parent = skills_section.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            skills = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_skills"] = skills[:30]
                        else:
                            text = next_elem.get_text(strip=True)
                            # Skill formatı: "Skill Name: X (+Y)" veya "Skill Name X (+Y)", virgülle ayrılmış
                            # Önce virgülle ayır, sonra skill isimlerini çıkar
                            skills_parts = text.split(',')
                            skills = []
                            for part in skills_parts:
                                part = part.strip()
                                # Skill ismini çıkar (başında rakam veya parantez varsa öncesini al)
                                # "Insight 4 (+6)" -> "Insight"
                                skill_match = re.match(r'^([A-Z][A-Za-z\s]+(?:\([^)]+\))?)', part)
                                if skill_match:
                                    skill_name = skill_match.group(1).strip()
                                    # Parantez içindeki "Choose one of" gibi açıklamaları dahil et
                                    if '(' in skill_name and 'Choose' in skill_name:
                                        # "Expertise: (Choose one of Business, Engineering, or Science)" -> "Expertise (Choose one of Business, Engineering, or Science)"
                                        pass
                                    # Çok uzun olanları filtrele
                                    if len(skill_name) < 80:
                                        skills.append(skill_name)
                            archetype_data["suggested_skills"] = skills[:30]
            
            # Eğer bulunamadıysa, text'ten parse et - DÜZELTİLDİ
            if not archetype_data["suggested_skills"]:
                # "Skills:" başlığından sonraki satırı bul
                skills_match = re.search(r'[Ss]kills?[:\s]*\n\s*([^\n]{50,1000}?)(?=\n[A-Z]|\n\n|$)', full_text, re.IGNORECASE | re.DOTALL)
                if skills_match:
                    skills_text = skills_match.group(1).strip()
                    # Virgülle ayrılmış skill listesi
                    skills_parts = skills_text.split(',')
                    skills = []
                    for part in skills_parts:
                        part = part.strip()
                        # Skill ismini çıkar (rakam ve parantez öncesi)
                        # "Insight 4 (+6)" -> "Insight"
                        skill_match = re.match(r'^([A-Z][A-Za-z\s]+(?:\([^)]+\))?)', part)
                        if skill_match:
                            skill_name = skill_match.group(1).strip()
                            # "Expertise: (Choose one of...)" formatını koru
                            if ':' in skill_name:
                                skill_name = skill_name.replace(':', '').strip()
                            if len(skill_name) < 80 and skill_name not in skills:
                                skills.append(skill_name)
                    archetype_data["suggested_skills"] = skills[:30]
            
            # Ability suggestions - genellikle tablo veya liste formatında
            # Örneğin: "Strength 8, Stamina 4, Agility 2, Dexterity 2, Fighting 4, Intellect 6, Awareness 4, Presence 2"
            ability_match = re.search(r'(Strength|Stamina|Agility|Dexterity|Fighting|Intellect|Awareness|Presence)\s+(\d+)', full_text, re.I)
            if ability_match:
                # Tüm ability'leri bul
                abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
                for ability in abilities:
                    pattern = rf'{ability}\s+(\d+)'
                    match = re.search(pattern, full_text, re.I)
                    if match:
                        archetype_data["ability_suggestions"][ability] = int(match.group(1))
        
        return archetype_data
    
    def _find_section_url(self, section_name: str, base_url: str = None) -> Optional[str]:
        """Belirli bir bölümün URL'ini bul"""
        if base_url is None:
            base_url = self.SECTIONS["character_creation"]
        
        soup = self._get(base_url)
        if not soup:
            return None
        
        # Section name'i içeren linkleri bul
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            if section_name.lower() in text or section_name.lower().replace(' ', '-') in href.lower():
                if href.startswith('/'):
                    return href
                elif href.startswith('http'):
                    return href.replace(self.base_url, '')
        
        return None
    
    def scrape_skills(self) -> Dict[str, Any]:
        """Skills (Beceriler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("🎯 Skills çekiliyor...")
        skills_data = {}
        
        # Doğru URL'i kullan
        skills_url = self.SECTIONS["skills"]
        
        soup = self._get(skills_url)
        if not soup:
            return skills_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Skills sayfasında genellikle tablo veya liste formatında skill'ler var
            # Skill linklerini bul (anchor linkleri)
            skill_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
            
            # Eğer anchor linkleri varsa, skill isimlerini çıkar
            if skill_links:
                for link in skill_links:
                    skill_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    # "Skill Name (Ability)" formatını parse et
                    match = re.match(r'([A-Z][A-Z\s]+(?:\([^)]+\))?)\s*\(?([A-Z][a-z]+)\)?', skill_text)
                    if match:
                        skill_name = match.group(1).strip()
                        ability = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""
                    else:
                        skill_name = skill_text
                        ability = ""
                    
                    # Ability'yi href'ten de çıkarabiliriz
                    ability_match = re.search(r'#TOC-[A-Z]+-([A-Z][a-z]+)', href)
                    if ability_match:
                        ability = ability_match.group(1)
                    
                    if skill_name and len(skill_name) < 50 and skill_name not in skills_data:
                        skills_data[skill_name] = {
                            "name": skill_name,
                            "key_ability": ability,
                            "cost_per_rank": 1,  # Varsayılan
                            "description": "",
                            "source": urljoin(self.base_url, skills_url + href)
                        }
            
            # Eğer link yoksa, tablo veya liste formatında skill'leri bul
            if not skills_data:
                text = main_content.get_text()
                # Skill pattern'i: "Skill Name (Ability)" veya "Skill Name: Ability"
                skill_patterns = [
                    r'([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\s+\(([A-Z][a-z]+)\)',  # "Skill Name (Ability)"
                    r'([A-Z][A-Za-z\s]+):\s+([A-Z][a-z]+)',  # "Skill Name: Ability"
                ]
                
                for pattern in skill_patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        skill_name = match.group(1).strip()
                        ability = match.group(2) if len(match.groups()) > 1 else ""
                        
                        # Çok uzun veya geçersiz olanları filtrele
                        if (skill_name and len(skill_name) < 50 and 
                            skill_name not in skills_data and
                            skill_name[0].isupper() and
                            ability in ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]):
                            skills_data[skill_name] = {
                                "name": skill_name,
                                "key_ability": ability,
                                "cost_per_rank": 1,
                                "description": "",
                                "source": urljoin(self.base_url, skills_url)
                            }
            
            print(f"  ... {len(skills_data)} skill bulundu")
        
        print(f"✅ {len(skills_data)} skill çekildi")
        return skills_data
    
    def scrape_advantages(self) -> Dict[str, Any]:
        """Advantages (Avantajlar) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("⭐ Advantages çekiliyor...")
        advantages_data = {}
        
        # Doğru URL'i kullan
        advantages_url = self.SECTIONS["advantages"]
        
        soup = self._get(advantages_url)
        if not soup:
            return advantages_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Advantages sayfasında genellikle anchor linkleri veya liste formatında advantage'ler var
            # Advantage linklerini bul (anchor linkleri)
            advantage_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
            
            # Eğer anchor linkleri varsa, advantage isimlerini çıkar
            if advantage_links:
                for link in advantage_links:
                    advantage_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # "Advantage Name" veya "Advantage Name (Cost)" formatını parse et
                    match = re.match(r'([A-Z][A-Z\s&()-]+(?:\([^)]+\))?)', advantage_text)
                    if match:
                        advantage_name = match.group(1).strip()
                        # Cost bilgisini çıkar
                        cost_match = re.search(r'\(([0-9]+)\s*(?:rank|point)', advantage_text, re.I)
                        cost = int(cost_match.group(1)) if cost_match else 1
                    else:
                        advantage_name = advantage_text
                        cost = 1
                    
                    if advantage_name and len(advantage_name) < 80 and advantage_name not in advantages_data:
                        advantages_data[advantage_name] = {
                            "name": advantage_name,
                            "cost": cost,
                            "description": "",
                            "source": urljoin(self.base_url, advantages_url + href)
                        }
                        
                        # Detay sayfasından açıklama çek (eğer varsa)
                        if href.startswith('#'):
                            # Anchor link, aynı sayfada detay bul
                            anchor_id = href.replace('#', '').replace('TOC-', '')
                            # Anchor'a git ve sonraki içeriği al
                            anchor = main_content.find('a', {'name': anchor_id}) or main_content.find('a', {'id': anchor_id})
                            if anchor:
                                parent = anchor.find_parent(['h2', 'h3', 'h4', 'p', 'div'])
                                if parent:
                                    next_elem = parent.find_next_sibling('p')
                                    if next_elem:
                                        advantages_data[advantage_name]["description"] = next_elem.get_text(strip=True)
            
            # Eğer anchor linkleri yoksa, direkt advantage'leri bul
            if not advantages_data:
                # Tüm başlıkları ve altındaki içeriği bul
                headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
                for header in headers:
                    header_text = header.get_text(strip=True)
                    # Geçersiz başlıkları filtrele
                    if (len(header_text) < 80 and 
                        header_text[0].isupper() and
                        'Advantage' not in header_text and
                        not header_text.startswith('Table') and
                        not header_text.startswith('See')):
                        
                        # Sonraki paragrafı al
                        next_elem = header.find_next_sibling(['p', 'div'])
                        if next_elem:
                            description = next_elem.get_text(strip=True)
                            # Cost bilgisini çıkar
                            cost_match = re.search(r'Cost[:\s]+(\d+)', description, re.I)
                            cost = int(cost_match.group(1)) if cost_match else 1
                            
                            advantages_data[header_text] = {
                                "name": header_text,
                                "cost": cost,
                                "description": description[:500],  # İlk 500 karakter
                                "source": urljoin(self.base_url, advantages_url)
                            }
            
            print(f"  ... {len(advantages_data)} advantage bulundu")
        
        print(f"✅ {len(advantages_data)} advantage çekildi")
        return advantages_data
    
    def _scrape_advantage_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir advantage'in detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        advantage_data = {
            "name": name,
            "cost": 1,  # Varsayılan
            "description": "",
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Cost bilgisini bul
            cost_match = re.search(r'Cost[:\s]+(\d+)', main_content.get_text(), re.IGNORECASE)
            if cost_match:
                advantage_data["cost"] = int(cost_match.group(1))
            
            # Description'ı bul
            desc_p = main_content.find('p')
            if desc_p:
                advantage_data["description"] = desc_p.get_text(strip=True)
        
        return advantage_data
    
    def scrape_powers(self) -> Dict[str, Any]:
        """Powers (Güçler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("⚡ Powers çekiliyor...")
        powers_data = {}
        
        # Sample Powers sayfasından başla
        sample_powers_url = self.SECTIONS["sample_powers"]
        
        soup = self._get(sample_powers_url)
        if not soup:
            return powers_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Power linklerini bul - hem /sample-powers/ hem de /6-powers/ altında olabilir
            power_links = main_content.find_all('a', href=re.compile(r'/6-powers/sample-powers/[^/]+/$'))
            
            # Eğer link bulunamazsa, anchor linkleri dene
            if not power_links:
                power_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
                # Power isimlerini çıkar
                for link in power_links:
                    power_text = link.get_text(strip=True)
                    # Çok uzun veya geçersiz olanları filtrele
                    if (power_text and len(power_text) < 80 and 
                        power_text[0].isupper() and
                        power_text not in powers_data):
                        # Power detayını aynı sayfadan çek
                        power_data = self._scrape_power_detail_from_same_page(main_content, power_text)
                        if power_data:
                            powers_data[power_text] = power_data
            
            # Direkt linkler varsa, detay sayfalarını çek
            for link in power_links:
                power_name = link.get_text(strip=True)
                if power_name and power_name not in powers_data and len(power_name) < 80:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    power_data = self._scrape_power_detail(href, power_name)
                    if power_data:
                        powers_data[power_name] = power_data
                        if len(powers_data) % 10 == 0:
                            print(f"  ... {len(powers_data)} power çekildi")
            
            print(f"  ... {len(powers_data)} power bulundu")
        
        print(f"✅ {len(powers_data)} power çekildi")
        return powers_data
    
    def _scrape_power_detail_from_same_page(self, main_content, power_name: str) -> Optional[Dict[str, Any]]:
        """Aynı sayfadan power detayını çek (anchor linkler için)"""
        power_data = {
            "name": power_name,
            "cost_per_rank": 1,
            "description": "",
            "source": urljoin(self.base_url, self.SECTIONS["sample_powers"])
        }
        
        # Power adını içeren başlığı bul
        headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
        for header in headers:
            header_text = header.get_text(strip=True)
            if power_name.lower() in header_text.lower() or header_text.lower() in power_name.lower():
                # Sonraki paragrafları al
                description_parts = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 20:
                        description_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    # Bir sonraki başlığa gelince dur
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if len(description_parts) >= 10:
                        break
                
                power_data["description"] = "\n\n".join(description_parts)
                break
        
        return power_data
    
    def _scrape_power_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir power'ın detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        power_data = {
            "name": name,
            "cost_per_rank": 1,  # Varsayılan
            "description": "",
            "effects": [],
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Cost bilgisini bul
            cost_match = re.search(r'Cost[:\s]+(\d+)', main_content.get_text(), re.IGNORECASE)
            if cost_match:
                power_data["cost_per_rank"] = int(cost_match.group(1))
            
            # Description'ı bul
            desc_p = main_content.find('p')
            if desc_p:
                power_data["description"] = desc_p.get_text(strip=True)
        
        return power_data
    
    def scrape_power_effects(self) -> Dict[str, Any]:
        """Power Effects bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("✨ Power Effects çekiliyor...")
        effects_data = {}
        
        # Effect Descriptions sayfasından başla
        effects_url = self.SECTIONS["effect_descriptions"]
        
        soup = self._get(effects_url)
        if not soup:
            # Alternatif URL dene
            effects_url = self.SECTIONS["power_effects"]
            soup = self._get(effects_url)
        
        if not soup:
            return effects_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Effect linklerini bul - DÜZELTİLDİ (doğru pattern)
            # Format: /6-powers/effects/effect-descriptions/[effect-name]/
            effect_links = main_content.find_all('a', href=re.compile(r'/6-powers/effects/effect-descriptions/[^/]+/$'))
            
            print(f"  ... {len(effect_links)} effect linki bulundu")
            
            # Her effect linkini işle
            for link in effect_links:
                effect_name = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Geçersiz linkleri filtrele
                if not effect_name or len(effect_name) > 100 or effect_name in effects_data:
                    continue
                
                # Effect adını temizle (örn: "AFFLICTION (ATTACK)" -> "AFFLICTION")
                # Category'yi parantez içinden çıkar
                category_match = re.search(r'\(([A-Z]+)\)', effect_name)
                category = category_match.group(1) if category_match else ""
                # Category mapping
                category_map = {
                    "ATTACK": "Attack",
                    "DEFENSE": "Defense",
                    "MOVEMENT": "Movement",
                    "CONTROL": "Control",
                    "GENERAL": "General",
                    "SENSORY": "Sensory"
                }
                category = category_map.get(category, "")
                
                # Effect adını temizle (parantez ve category'yi kaldır)
                clean_name = re.sub(r'\s*\([^)]+\)', '', effect_name).strip()
                
                # Detay sayfasını çek
                if not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                
                effect_data = self._scrape_effect_detail(href, clean_name)
                if effect_data:
                    # Category'yi ekle (eğer detay sayfasında yoksa)
                    if category and not effect_data.get("category"):
                        effect_data["category"] = category
                    # Effect name'i güncelle
                    effect_data["name"] = clean_name
                    effects_data[clean_name] = effect_data
                    
                    if len(effects_data) % 10 == 0:
                        print(f"    ... {len(effects_data)} effect çekildi")
                else:
                    # Eğer detay sayfası çekilemediyse, en azından temel bilgiyi kaydet
                    effects_data[clean_name] = {
                        "name": clean_name,
                        "category": category,
                        "cost_per_rank": 1,
                        "description": f"{clean_name} is a power effect in Mutants & Masterminds.",
                        "source": href if href.startswith('http') else urljoin(self.base_url, href)
                    }
            
            # Eğer link bulunamadıysa, başlıklardan çek
            if not effects_data:
                headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
                for header in headers:
                    header_text = header.get_text(strip=True)
                    # Geçersiz başlıkları filtrele
                    if (len(header_text) < 100 and 
                        header_text[0].isupper() and
                        not header_text.startswith('Table') and
                        not header_text.startswith('See') and
                        '(' not in header_text):  # "(ATTACK)" gibi formatları filtrele
                        
                        # Sonraki paragrafları al
                        description_parts = []
                        next_elem = header.find_next_sibling()
                        while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                            text = next_elem.get_text(strip=True)
                            if len(text) > 20:
                                description_parts.append(text)
                            next_elem = next_elem.find_next_sibling()
                            # Bir sonraki başlığa gelince dur
                            if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                                break
                            if len(description_parts) >= 10:
                                break
                        
                        # Category'yi header'dan çıkar
                        category = ""
                        if 'ATTACK' in header_text.upper():
                            category = "Attack"
                        elif 'DEFENSE' in header_text.upper():
                            category = "Defense"
                        elif 'MOVEMENT' in header_text.upper():
                            category = "Movement"
                        elif 'CONTROL' in header_text.upper():
                            category = "Control"
                        elif 'GENERAL' in header_text.upper():
                            category = "General"
                        elif 'SENSORY' in header_text.upper():
                            category = "Sensory"
                        
                        effects_data[header_text] = {
                            "name": header_text,
                            "category": category,
                            "cost_per_rank": 1,
                            "description": "\n\n".join(description_parts),
                            "source": urljoin(self.base_url, effects_url)
                        }
            
            print(f"  ... {len(effects_data)} effect bulundu")
        
        print(f"✅ {len(effects_data)} power effect çekildi")
        return effects_data
    
    def _scrape_effect_detail_from_same_page(self, main_content, effect_name: str) -> Optional[Dict[str, Any]]:
        """Aynı sayfadan effect detayını çek"""
        effect_data = {
            "name": effect_name,
            "category": "",
            "cost_per_rank": 1,
            "description": "",
            "source": urljoin(self.base_url, self.SECTIONS["effect_descriptions"])
        }
        
        # Effect adını içeren başlığı bul
        headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
        for header in headers:
            header_text = header.get_text(strip=True)
            if effect_name.lower() in header_text.lower() or header_text.lower() in effect_name.lower():
                # Category'yi belirle
                if 'ATTACK' in header_text.upper():
                    effect_data["category"] = "Attack"
                elif 'DEFENSE' in header_text.upper():
                    effect_data["category"] = "Defense"
                elif 'MOVEMENT' in header_text.upper():
                    effect_data["category"] = "Movement"
                elif 'CONTROL' in header_text.upper():
                    effect_data["category"] = "Control"
                elif 'GENERAL' in header_text.upper():
                    effect_data["category"] = "General"
                elif 'SENSORY' in header_text.upper():
                    effect_data["category"] = "Sensory"
                
                # Sonraki paragrafları al
                description_parts = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 20:
                        description_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if len(description_parts) >= 10:
                        break
                
                effect_data["description"] = "\n\n".join(description_parts)
                break
        
        return effect_data
    
    def _scrape_effect_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir effect'in detay sayfasını çek - GELİŞTİRİLMİŞ"""
        soup = self._get(url)
        if not soup:
            return None
        
        effect_data = {
            "name": name,
            "category": "",  # Attack, Defense, Movement, etc.
            "cost_per_rank": 1,
            "description": "",
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Effect başlığını bul (h1, h2, h3)
            effect_header = None
            headers = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
            for header in headers:
                header_text = header.get_text(strip=True).upper()
                if name.upper() in header_text or header_text.startswith(name.upper()):
                    effect_header = header
                    # Category'yi header'dan çıkar
                    category_match = re.search(r'\(([A-Z]+)\)', header_text)
                    if category_match:
                        category_map = {
                            "ATTACK": "Attack",
                            "DEFENSE": "Defense",
                            "MOVEMENT": "Movement",
                            "CONTROL": "Control",
                            "GENERAL": "General",
                            "SENSORY": "Sensory"
                        }
                        category = category_match.group(1)
                        effect_data["category"] = category_map.get(category, "")
                    break
            
            # Category'yi bul (eğer header'da yoksa)
            if not effect_data["category"]:
                category_match = re.search(r'(Attack|Defense|Movement|Control|General|Sensory)', main_content.get_text(), re.I)
                if category_match:
                    effect_data["category"] = category_match.group(1).capitalize()
            
            # Description'ı bul - başlıktan sonraki paragrafları al
            description_parts = []
            start_elem = effect_header if effect_header else main_content
            
            # İlk paragrafları al
            next_elem = start_elem.find_next_sibling() if effect_header else main_content.find('p')
            while next_elem:
                if next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    # Bir sonraki başlığa gelince dur
                    break
                
                if next_elem.name in ['p', 'div']:
                    text = next_elem.get_text(strip=True)
                    # Footer linklerini filtrele
                    if (len(text) > 30 and 
                        'Green Ronin' not in text and 
                        'Mutants & Masterminds' not in text and
                        'OGN' not in text and
                        'd20pfsrd' not in text.lower()):
                        description_parts.append(text)
                
                next_elem = next_elem.find_next_sibling()
                
                # Çok fazla içerik çekmemek için limit
                if len(description_parts) >= 15:
                    break
            
            # Eğer paragraflar bulunamadıysa, ilk paragrafı al
            if not description_parts:
                # Tüm paragrafları bul
                all_paragraphs = main_content.find_all('p')
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    # Footer linklerini filtrele
                    if (len(text) > 30 and 
                        'Green Ronin' not in text and 
                        'Mutants & Masterminds' not in text and
                        'OGN' not in text and
                        'd20pfsrd' not in text.lower() and
                        'Open Gaming' not in text):
                        description_parts.append(text)
                        if len(description_parts) >= 5:
                            break
            
            # Eğer hala açıklama yoksa, tüm içeriği al
            if not description_parts:
                full_text = main_content.get_text()
                # Effect adından sonraki metni bul
                pattern = rf'{re.escape(name)}[:\s]*([^A-Z]{{100,1500}}?)(?=[A-Z]{{3,}}|\n\n|$)'
                match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
                if match:
                    description_parts.append(match.group(1).strip())
            
            if description_parts:
                effect_data["description"] = "\n\n".join(description_parts)[:2000]  # İlk 2000 karakter
            else:
                effect_data["description"] = f"{name} is a power effect in Mutants & Masterminds."
        
        return effect_data
    
    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tüm M&M verilerini çek ve birleştir"""
        print("🚀 Mutants & Masterminds verileri çekiliyor...")
        print("⚠️  Bu işlem birkaç dakika sürebilir. Lütfen bekleyin...\n")
        
        data = {
            "system": "MUTANTS_AND_MASTERMINDS",
            "source": "d20herosrd.com",
            "abilities": self.scrape_abilities(),
            "archetypes": self.scrape_archetypes(),
            "skills": self.scrape_skills(),
            "advantages": self.scrape_advantages(),
            "powers": self.scrape_powers(),
            "power_effects": self.scrape_power_effects(),
            "power_levels": {  # Sabit değerler
                "PL8": {"attack_bonus_cap": 8, "effect_rank_cap": 10, "defense_cap": 8, "toughness_cap": 10},
                "PL10": {"attack_bonus_cap": 10, "effect_rank_cap": 10, "defense_cap": 10, "toughness_cap": 10},
                "PL12": {"attack_bonus_cap": 12, "effect_rank_cap": 12, "defense_cap": 12, "toughness_cap": 12},
                "PL15": {"attack_bonus_cap": 15, "effect_rank_cap": 15, "defense_cap": 15, "toughness_cap": 15},
            }
        }
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Veriler kaydedildi: {output_file}")
        
        return data


if __name__ == "__main__":
    # Test için
    scraper = MMScraper(delay=1.0)
    output = Path(__file__).resolve().parents[1] / "data" / "mm_data.json"
    scraper.scrape_all(output_file=output)


"""
Mutants & Masterminds Web Scraper
d20herosrd.com sitesinden tüm kuralları ve karakter oluşturma bilgilerini çeker.
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class MMScraper:
    """Mutants & Masterminds verilerini d20herosrd.com'dan çeken scraper"""
    
    BASE_URL = "https://www.d20herosrd.com"
    
    # Ana bölümler - Doğru URL'ler (test edilmiş)
    SECTIONS = {
        "character_creation": "/character-creation/",
        "abilities": "/character-creation/3-abilities/",
        "advancement": "/character-creation/advancement/",
        "archetypes": "/character-creation/archetypes/",
        "skills": "/4-skills/",  # Doğru URL - sayı ile başlıyor, /character-creation/ yok
        "advantages": "/5-advantages/",  # Doğru URL - sayı ile başlıyor, /character-creation/ yok
        "powers": "/6-powers/",
        "sample_powers": "/6-powers/sample-powers/",
        "power_effects": "/6-powers/effects/",
        "effect_descriptions": "/6-powers/effects/effect-descriptions/",
        "descriptors": "/6-powers/descriptors/",
        "modifiers": "/6-powers/modifiers/",
        "gadgets": "/gadgets-gear/",
        "conditions": "/gamemastering/conditions/",
        "npcs": "/gamemastering/npcs/",
        "basics": "/the-basics/",
    }
    
    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: İstekler arası bekleme süresi (saniye) - siteyi yormamak için
        """
        self.base_url = self.BASE_URL
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """URL'den HTML içeriğini çek ve BeautifulSoup nesnesi döndür"""
        if not url:
            return None
        full_url = urljoin(self.base_url, url) if not url.startswith("http") else url
        
        for attempt in range(retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(full_url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"❌ Hata: {full_url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_abilities(self) -> Dict[str, Any]:
        """Abilities (Yetenekler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("💪 Abilities çekiliyor...")
        abilities_data = {}
        
        soup = self._get(self.SECTIONS["abilities"])
        if not soup:
            return abilities_data
        
        # Ana içeriği bul
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Tüm abilities'leri bul (8 temel ability)
            abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
            ability_abbrevs = {"Strength": "STR", "Stamina": "STA", "Agility": "AGL", "Dexterity": "DEX", 
                             "Fighting": "FGT", "Intellect": "INT", "Awareness": "AWE", "Presence": "PRE"}
            
            # H3 başlıklarını bul (STRENGTH (STR) formatında)
            h3_headers = main_content.find_all('h3')
            
            for ability_name in abilities:
                ability_header = None
                description_parts = []
                
                # H3 başlıklarında ara (STRENGTH (STR) formatı)
                abbrev = ability_abbrevs.get(ability_name, "")
                for header in h3_headers:
                    header_text = header.get_text(strip=True).upper()
                    # "STRENGTH (STR)" veya "STRENGTH" formatını kontrol et
                    if (ability_name.upper() in header_text or 
                        (abbrev and abbrev in header_text and len(header_text) < 30)):
                        ability_header = header
                        break
                
                # Başlık bulunduysa, sonraki içeriği al
                if ability_header:
                    # Bir sonraki ability başlığını bul (durma noktası)
                    next_ability_index = abilities.index(ability_name) + 1
                    next_ability_name = abilities[next_ability_index] if next_ability_index < len(abilities) else None
                    
                    # Sonraki elementleri al
                    current = ability_header.find_next_sibling()
                    while current:
                        # Bir sonraki H3 başlığına gelince dur (diğer ability başlığı)
                        if current.name == 'h3':
                            current_text = current.get_text(strip=True).upper()
                            # Bir sonraki ability başlığı mı?
                            if next_ability_name and next_ability_name.upper() in current_text:
                                break
                            # Başka bir ability başlığı mı?
                            if any(ab.upper() in current_text and ab != ability_name for ab in abilities):
                                break
                        
                        # İçeriği al (paragraflar)
                        if current.name in ['p', 'div']:
                            text = current.get_text(strip=True)
                            # Footer linklerini filtrele
                            if (len(text) > 30 and 
                                'Green Ronin' not in text and 
                                'Mutants & Masterminds' not in text and
                                'OGN' not in text and
                                'd20pfsrd' not in text.lower() and
                                'Open Gaming' not in text):
                                description_parts.append(text)
                        
                        # Liste öğelerini de al
                        elif current.name in ['ul', 'ol']:
                            items = current.find_all('li')
                            for item in items:
                                text = item.get_text(strip=True)
                                if len(text) > 20 and 'Green Ronin' not in text:
                                    description_parts.append(text)
                        
                        current = current.find_next_sibling()
                        
                        # Çok fazla içerik çekmemek için limit
                        if len(description_parts) >= 15:
                            break
                
                # Başlık bulunamadıysa, text'ten parse et
                if not ability_header or not description_parts:
                    text = main_content.get_text()
                    # Ability adından sonraki metni bul (bir sonraki H3 başlığına kadar)
                    next_ability_pattern = ""
                    if next_ability_name:
                        next_abbrev = ability_abbrevs.get(next_ability_name, "")
                        next_ability_pattern = f"|{next_ability_name.upper()}|{next_abbrev}"
                    
                    pattern = rf'{ability_name.upper()}[:\s(]*{abbrev}[:\s)]*([^A-Z]{{100,2000}}?)(?={next_ability_pattern}|$)'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        description_text = match.group(1).strip()
                        # Çok kısa veya geçersiz metinleri filtrele
                        if len(description_text) > 50:
                            description_parts.append(description_text)
                
                # Ability verisini oluştur
                if description_parts:
                    full_description = "\n\n".join(description_parts)
                    # Çok uzun olanları kısalt
                    if len(full_description) > 2000:
                        full_description = full_description[:2000] + "..."
                    abilities_data[ability_name] = {
                        "name": ability_name,
                        "description": full_description,
                        "cost_per_rank": 1,  # Her ability 1 cost per rank
                        "source": urljoin(self.base_url, self.SECTIONS["abilities"])
                    }
                else:
                    # En azından temel bilgiyi ekle
                    abilities_data[ability_name] = {
                        "name": ability_name,
                        "description": f"{ability_name} is one of the eight core abilities in Mutants & Masterminds.",
                        "cost_per_rank": 1,
                        "source": urljoin(self.base_url, self.SECTIONS["abilities"])
                    }
            
            print(f"  ... {len(abilities_data)} ability bulundu")
        
        print(f"✅ {len(abilities_data)} ability çekildi")
        return abilities_data
    
    def scrape_archetypes(self) -> Dict[str, Any]:
        """Archetypes (Arketipler) bilgilerini çek"""
        print("🎭 Archetypes çekiliyor...")
        archetypes_data = {}
        
        soup = self._get(self.SECTIONS["archetypes"])
        if not soup:
            return archetypes_data
        
        # Ana içeriği bul
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Archetype linklerini bul
            archetype_links = main_content.find_all('a', href=re.compile(r'/character-creation/archetypes/[^/]+/$'))
            
            for link in archetype_links:
                archetype_name = link.get_text(strip=True)
                if archetype_name and archetype_name not in archetypes_data:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    archetype_data = self._scrape_archetype_detail(href, archetype_name)
                    if archetype_data:
                        archetypes_data[archetype_name] = archetype_data
                        print(f"  ✓ {archetype_name}")
        
        print(f"✅ {len(archetypes_data)} archetype çekildi")
        return archetypes_data
    
    def _scrape_archetype_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir archetype'in detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        archetype_data = {
            "name": name,
            "summary": "",
            "suggested_powers": [],
            "suggested_advantages": [],
            "suggested_skills": [],
            "ability_suggestions": {},
            "source": url
        }
        
        # Ana içeriği bul - navigation ve footer'ı hariç tut
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # İlk anlamlı paragrafı bul (çok kısa olmayan)
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Footer linklerini filtrele
                if len(text) > 50 and 'Green Ronin' not in text and 'Mutants & Masterminds' not in text:
                    archetype_data["summary"] = text
                    break
            
            # Powers, Advantages, Skills bölümlerini bul - GELİŞTİRİLMİŞ
            # Tüm metni al
            full_text = main_content.get_text()
            
            # Powers bölümünü bul
            # Pattern 1: "Powers:" veya "Suggested Powers:" başlığından sonra
            powers_section = main_content.find(string=re.compile(r'[Pp]owers?[:\s]', re.I))
            if powers_section:
                parent = powers_section.find_parent()
                if parent:
                    # Sonraki içeriği al (liste veya paragraf)
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            powers = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_powers"] = powers[:30]
                        else:
                            # Paragraftan power isimlerini çıkar
                            text = next_elem.get_text(strip=True)
                            # Power isimleri genellikle büyük harfle başlar
                            powers = re.findall(r'\b([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\b', text)
                            archetype_data["suggested_powers"] = [p.strip() for p in powers if len(p.strip()) < 50][:30]
            
            # Eğer bulunamadıysa, text'ten parse et
            if not archetype_data["suggested_powers"]:
                # "Powers:" veya "Powers" başlığından sonraki metni bul
                powers_match = re.search(r'[Pp]owers?[:\s]+([^A-Z]{20,500}?)(?=[Aa]dvantages?|[Ss]kills?|$)', full_text, re.IGNORECASE | re.DOTALL)
                if powers_match:
                    powers_text = powers_match.group(1)
                    # Power isimlerini çıkar (büyük harfle başlayan, virgülle ayrılmış)
                    powers = re.findall(r'\b([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\b', powers_text)
                    archetype_data["suggested_powers"] = [p.strip() for p in powers if len(p.strip()) < 50 and p.strip() != name][:30]
            
            # Advantages bölümünü bul - DÜZELTİLDİ (virgülle ayrılmış format)
            advantages_section = main_content.find(string=re.compile(r'[Aa]dvantages?[:\s]', re.I))
            if advantages_section:
                parent = advantages_section.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            advantages = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_advantages"] = advantages[:30]
                        else:
                            text = next_elem.get_text(strip=True)
                            # Virgülle ayrılmış advantage listesi
                            advantages = [a.strip() for a in text.split(',') if a.strip() and len(a.strip()) < 80]
                            archetype_data["suggested_advantages"] = advantages[:30]
            
            # Eğer bulunamadıysa, text'ten parse et - DÜZELTİLDİ
            if not archetype_data["suggested_advantages"]:
                # "Advantages:" başlığından sonraki satırı bul
                advantages_match = re.search(r'[Aa]dvantages?[:\s]*\n\s*([^\n]{20,500}?)(?=\n[A-Z]|\n\n|$)', full_text, re.IGNORECASE | re.DOTALL)
                if advantages_match:
                    advantages_text = advantages_match.group(1).strip()
                    # Virgülle ayrılmış advantage listesi
                    advantages = [a.strip() for a in advantages_text.split(',') if a.strip() and len(a.strip()) < 80]
                    # Çok kısa veya geçersiz olanları filtrele
                    advantages = [a for a in advantages if len(a) > 3 and not a.startswith('(') and not a.endswith(')')]
                    archetype_data["suggested_advantages"] = advantages[:30]
            
            # Skills bölümünü bul - DÜZELTİLDİ
            skills_section = main_content.find(string=re.compile(r'[Ss]kills?[:\s]', re.I))
            if skills_section:
                parent = skills_section.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            skills = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_skills"] = skills[:30]
                        else:
                            text = next_elem.get_text(strip=True)
                            # Skill formatı: "Skill Name: X (+Y)" veya "Skill Name X (+Y)", virgülle ayrılmış
                            # Önce virgülle ayır, sonra skill isimlerini çıkar
                            skills_parts = text.split(',')
                            skills = []
                            for part in skills_parts:
                                part = part.strip()
                                # Skill ismini çıkar (başında rakam veya parantez varsa öncesini al)
                                # "Insight 4 (+6)" -> "Insight"
                                skill_match = re.match(r'^([A-Z][A-Za-z\s]+(?:\([^)]+\))?)', part)
                                if skill_match:
                                    skill_name = skill_match.group(1).strip()
                                    # Parantez içindeki "Choose one of" gibi açıklamaları dahil et
                                    if '(' in skill_name and 'Choose' in skill_name:
                                        # "Expertise: (Choose one of Business, Engineering, or Science)" -> "Expertise (Choose one of Business, Engineering, or Science)"
                                        pass
                                    # Çok uzun olanları filtrele
                                    if len(skill_name) < 80:
                                        skills.append(skill_name)
                            archetype_data["suggested_skills"] = skills[:30]
            
            # Eğer bulunamadıysa, text'ten parse et - DÜZELTİLDİ
            if not archetype_data["suggested_skills"]:
                # "Skills:" başlığından sonraki satırı bul
                skills_match = re.search(r'[Ss]kills?[:\s]*\n\s*([^\n]{50,1000}?)(?=\n[A-Z]|\n\n|$)', full_text, re.IGNORECASE | re.DOTALL)
                if skills_match:
                    skills_text = skills_match.group(1).strip()
                    # Virgülle ayrılmış skill listesi
                    skills_parts = skills_text.split(',')
                    skills = []
                    for part in skills_parts:
                        part = part.strip()
                        # Skill ismini çıkar (rakam ve parantez öncesi)
                        # "Insight 4 (+6)" -> "Insight"
                        skill_match = re.match(r'^([A-Z][A-Za-z\s]+(?:\([^)]+\))?)', part)
                        if skill_match:
                            skill_name = skill_match.group(1).strip()
                            # "Expertise: (Choose one of...)" formatını koru
                            if ':' in skill_name:
                                skill_name = skill_name.replace(':', '').strip()
                            if len(skill_name) < 80 and skill_name not in skills:
                                skills.append(skill_name)
                    archetype_data["suggested_skills"] = skills[:30]
            
            # Ability suggestions - genellikle tablo veya liste formatında
            # Örneğin: "Strength 8, Stamina 4, Agility 2, Dexterity 2, Fighting 4, Intellect 6, Awareness 4, Presence 2"
            ability_match = re.search(r'(Strength|Stamina|Agility|Dexterity|Fighting|Intellect|Awareness|Presence)\s+(\d+)', full_text, re.I)
            if ability_match:
                # Tüm ability'leri bul
                abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
                for ability in abilities:
                    pattern = rf'{ability}\s+(\d+)'
                    match = re.search(pattern, full_text, re.I)
                    if match:
                        archetype_data["ability_suggestions"][ability] = int(match.group(1))
        
        return archetype_data
    
    def _find_section_url(self, section_name: str, base_url: str = None) -> Optional[str]:
        """Belirli bir bölümün URL'ini bul"""
        if base_url is None:
            base_url = self.SECTIONS["character_creation"]
        
        soup = self._get(base_url)
        if not soup:
            return None
        
        # Section name'i içeren linkleri bul
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            if section_name.lower() in text or section_name.lower().replace(' ', '-') in href.lower():
                if href.startswith('/'):
                    return href
                elif href.startswith('http'):
                    return href.replace(self.base_url, '')
        
        return None
    
    def scrape_skills(self) -> Dict[str, Any]:
        """Skills (Beceriler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("🎯 Skills çekiliyor...")
        skills_data = {}
        
        # Doğru URL'i kullan
        skills_url = self.SECTIONS["skills"]
        
        soup = self._get(skills_url)
        if not soup:
            return skills_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Skills sayfasında genellikle tablo veya liste formatında skill'ler var
            # Skill linklerini bul (anchor linkleri)
            skill_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
            
            # Eğer anchor linkleri varsa, skill isimlerini çıkar
            if skill_links:
                for link in skill_links:
                    skill_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    # "Skill Name (Ability)" formatını parse et
                    match = re.match(r'([A-Z][A-Z\s]+(?:\([^)]+\))?)\s*\(?([A-Z][a-z]+)\)?', skill_text)
                    if match:
                        skill_name = match.group(1).strip()
                        ability = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""
                    else:
                        skill_name = skill_text
                        ability = ""
                    
                    # Ability'yi href'ten de çıkarabiliriz
                    ability_match = re.search(r'#TOC-[A-Z]+-([A-Z][a-z]+)', href)
                    if ability_match:
                        ability = ability_match.group(1)
                    
                    if skill_name and len(skill_name) < 50 and skill_name not in skills_data:
                        skills_data[skill_name] = {
                            "name": skill_name,
                            "key_ability": ability,
                            "cost_per_rank": 1,  # Varsayılan
                            "description": "",
                            "source": urljoin(self.base_url, skills_url + href)
                        }
            
            # Eğer link yoksa, tablo veya liste formatında skill'leri bul
            if not skills_data:
                text = main_content.get_text()
                # Skill pattern'i: "Skill Name (Ability)" veya "Skill Name: Ability"
                skill_patterns = [
                    r'([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\s+\(([A-Z][a-z]+)\)',  # "Skill Name (Ability)"
                    r'([A-Z][A-Za-z\s]+):\s+([A-Z][a-z]+)',  # "Skill Name: Ability"
                ]
                
                for pattern in skill_patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        skill_name = match.group(1).strip()
                        ability = match.group(2) if len(match.groups()) > 1 else ""
                        
                        # Çok uzun veya geçersiz olanları filtrele
                        if (skill_name and len(skill_name) < 50 and 
                            skill_name not in skills_data and
                            skill_name[0].isupper() and
                            ability in ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]):
                            skills_data[skill_name] = {
                                "name": skill_name,
                                "key_ability": ability,
                                "cost_per_rank": 1,
                                "description": "",
                                "source": urljoin(self.base_url, skills_url)
                            }
            
            print(f"  ... {len(skills_data)} skill bulundu")
        
        print(f"✅ {len(skills_data)} skill çekildi")
        return skills_data
    
    def scrape_advantages(self) -> Dict[str, Any]:
        """Advantages (Avantajlar) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("⭐ Advantages çekiliyor...")
        advantages_data = {}
        
        # Doğru URL'i kullan
        advantages_url = self.SECTIONS["advantages"]
        
        soup = self._get(advantages_url)
        if not soup:
            return advantages_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Advantages sayfasında genellikle anchor linkleri veya liste formatında advantage'ler var
            # Advantage linklerini bul (anchor linkleri)
            advantage_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
            
            # Eğer anchor linkleri varsa, advantage isimlerini çıkar
            if advantage_links:
                for link in advantage_links:
                    advantage_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # "Advantage Name" veya "Advantage Name (Cost)" formatını parse et
                    match = re.match(r'([A-Z][A-Z\s&()-]+(?:\([^)]+\))?)', advantage_text)
                    if match:
                        advantage_name = match.group(1).strip()
                        # Cost bilgisini çıkar
                        cost_match = re.search(r'\(([0-9]+)\s*(?:rank|point)', advantage_text, re.I)
                        cost = int(cost_match.group(1)) if cost_match else 1
                    else:
                        advantage_name = advantage_text
                        cost = 1
                    
                    if advantage_name and len(advantage_name) < 80 and advantage_name not in advantages_data:
                        advantages_data[advantage_name] = {
                            "name": advantage_name,
                            "cost": cost,
                            "description": "",
                            "source": urljoin(self.base_url, advantages_url + href)
                        }
                        
                        # Detay sayfasından açıklama çek (eğer varsa)
                        if href.startswith('#'):
                            # Anchor link, aynı sayfada detay bul
                            anchor_id = href.replace('#', '').replace('TOC-', '')
                            # Anchor'a git ve sonraki içeriği al
                            anchor = main_content.find('a', {'name': anchor_id}) or main_content.find('a', {'id': anchor_id})
                            if anchor:
                                parent = anchor.find_parent(['h2', 'h3', 'h4', 'p', 'div'])
                                if parent:
                                    next_elem = parent.find_next_sibling('p')
                                    if next_elem:
                                        advantages_data[advantage_name]["description"] = next_elem.get_text(strip=True)
            
            # Eğer anchor linkleri yoksa, direkt advantage'leri bul
            if not advantages_data:
                # Tüm başlıkları ve altındaki içeriği bul
                headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
                for header in headers:
                    header_text = header.get_text(strip=True)
                    # Geçersiz başlıkları filtrele
                    if (len(header_text) < 80 and 
                        header_text[0].isupper() and
                        'Advantage' not in header_text and
                        not header_text.startswith('Table') and
                        not header_text.startswith('See')):
                        
                        # Sonraki paragrafı al
                        next_elem = header.find_next_sibling(['p', 'div'])
                        if next_elem:
                            description = next_elem.get_text(strip=True)
                            # Cost bilgisini çıkar
                            cost_match = re.search(r'Cost[:\s]+(\d+)', description, re.I)
                            cost = int(cost_match.group(1)) if cost_match else 1
                            
                            advantages_data[header_text] = {
                                "name": header_text,
                                "cost": cost,
                                "description": description[:500],  # İlk 500 karakter
                                "source": urljoin(self.base_url, advantages_url)
                            }
            
            print(f"  ... {len(advantages_data)} advantage bulundu")
        
        print(f"✅ {len(advantages_data)} advantage çekildi")
        return advantages_data
    
    def _scrape_advantage_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir advantage'in detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        advantage_data = {
            "name": name,
            "cost": 1,  # Varsayılan
            "description": "",
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Cost bilgisini bul
            cost_match = re.search(r'Cost[:\s]+(\d+)', main_content.get_text(), re.IGNORECASE)
            if cost_match:
                advantage_data["cost"] = int(cost_match.group(1))
            
            # Description'ı bul
            desc_p = main_content.find('p')
            if desc_p:
                advantage_data["description"] = desc_p.get_text(strip=True)
        
        return advantage_data
    
    def scrape_powers(self) -> Dict[str, Any]:
        """Powers (Güçler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("⚡ Powers çekiliyor...")
        powers_data = {}
        
        # Sample Powers sayfasından başla
        sample_powers_url = self.SECTIONS["sample_powers"]
        
        soup = self._get(sample_powers_url)
        if not soup:
            return powers_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Power linklerini bul - hem /sample-powers/ hem de /6-powers/ altında olabilir
            power_links = main_content.find_all('a', href=re.compile(r'/6-powers/sample-powers/[^/]+/$'))
            
            # Eğer link bulunamazsa, anchor linkleri dene
            if not power_links:
                power_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
                # Power isimlerini çıkar
                for link in power_links:
                    power_text = link.get_text(strip=True)
                    # Çok uzun veya geçersiz olanları filtrele
                    if (power_text and len(power_text) < 80 and 
                        power_text[0].isupper() and
                        power_text not in powers_data):
                        # Power detayını aynı sayfadan çek
                        power_data = self._scrape_power_detail_from_same_page(main_content, power_text)
                        if power_data:
                            powers_data[power_text] = power_data
            
            # Direkt linkler varsa, detay sayfalarını çek
            for link in power_links:
                power_name = link.get_text(strip=True)
                if power_name and power_name not in powers_data and len(power_name) < 80:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    power_data = self._scrape_power_detail(href, power_name)
                    if power_data:
                        powers_data[power_name] = power_data
                        if len(powers_data) % 10 == 0:
                            print(f"  ... {len(powers_data)} power çekildi")
            
            print(f"  ... {len(powers_data)} power bulundu")
        
        print(f"✅ {len(powers_data)} power çekildi")
        return powers_data
    
    def _scrape_power_detail_from_same_page(self, main_content, power_name: str) -> Optional[Dict[str, Any]]:
        """Aynı sayfadan power detayını çek (anchor linkler için)"""
        power_data = {
            "name": power_name,
            "cost_per_rank": 1,
            "description": "",
            "source": urljoin(self.base_url, self.SECTIONS["sample_powers"])
        }
        
        # Power adını içeren başlığı bul
        headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
        for header in headers:
            header_text = header.get_text(strip=True)
            if power_name.lower() in header_text.lower() or header_text.lower() in power_name.lower():
                # Sonraki paragrafları al
                description_parts = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 20:
                        description_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    # Bir sonraki başlığa gelince dur
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if len(description_parts) >= 10:
                        break
                
                power_data["description"] = "\n\n".join(description_parts)
                break
        
        return power_data
    
    def _scrape_power_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir power'ın detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        power_data = {
            "name": name,
            "cost_per_rank": 1,  # Varsayılan
            "description": "",
            "effects": [],
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Cost bilgisini bul
            cost_match = re.search(r'Cost[:\s]+(\d+)', main_content.get_text(), re.IGNORECASE)
            if cost_match:
                power_data["cost_per_rank"] = int(cost_match.group(1))
            
            # Description'ı bul
            desc_p = main_content.find('p')
            if desc_p:
                power_data["description"] = desc_p.get_text(strip=True)
        
        return power_data
    
    def scrape_power_effects(self) -> Dict[str, Any]:
        """Power Effects bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("✨ Power Effects çekiliyor...")
        effects_data = {}
        
        # Effect Descriptions sayfasından başla
        effects_url = self.SECTIONS["effect_descriptions"]
        
        soup = self._get(effects_url)
        if not soup:
            # Alternatif URL dene
            effects_url = self.SECTIONS["power_effects"]
            soup = self._get(effects_url)
        
        if not soup:
            return effects_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Effect linklerini bul - DÜZELTİLDİ (doğru pattern)
            # Format: /6-powers/effects/effect-descriptions/[effect-name]/
            effect_links = main_content.find_all('a', href=re.compile(r'/6-powers/effects/effect-descriptions/[^/]+/$'))
            
            print(f"  ... {len(effect_links)} effect linki bulundu")
            
            # Her effect linkini işle
            for link in effect_links:
                effect_name = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Geçersiz linkleri filtrele
                if not effect_name or len(effect_name) > 100 or effect_name in effects_data:
                    continue
                
                # Effect adını temizle (örn: "AFFLICTION (ATTACK)" -> "AFFLICTION")
                # Category'yi parantez içinden çıkar
                category_match = re.search(r'\(([A-Z]+)\)', effect_name)
                category = category_match.group(1) if category_match else ""
                # Category mapping
                category_map = {
                    "ATTACK": "Attack",
                    "DEFENSE": "Defense",
                    "MOVEMENT": "Movement",
                    "CONTROL": "Control",
                    "GENERAL": "General",
                    "SENSORY": "Sensory"
                }
                category = category_map.get(category, "")
                
                # Effect adını temizle (parantez ve category'yi kaldır)
                clean_name = re.sub(r'\s*\([^)]+\)', '', effect_name).strip()
                
                # Detay sayfasını çek
                if not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                
                effect_data = self._scrape_effect_detail(href, clean_name)
                if effect_data:
                    # Category'yi ekle (eğer detay sayfasında yoksa)
                    if category and not effect_data.get("category"):
                        effect_data["category"] = category
                    # Effect name'i güncelle
                    effect_data["name"] = clean_name
                    effects_data[clean_name] = effect_data
                    
                    if len(effects_data) % 10 == 0:
                        print(f"    ... {len(effects_data)} effect çekildi")
                else:
                    # Eğer detay sayfası çekilemediyse, en azından temel bilgiyi kaydet
                    effects_data[clean_name] = {
                        "name": clean_name,
                        "category": category,
                        "cost_per_rank": 1,
                        "description": f"{clean_name} is a power effect in Mutants & Masterminds.",
                        "source": href if href.startswith('http') else urljoin(self.base_url, href)
                    }
            
            # Eğer link bulunamadıysa, başlıklardan çek
            if not effects_data:
                headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
                for header in headers:
                    header_text = header.get_text(strip=True)
                    # Geçersiz başlıkları filtrele
                    if (len(header_text) < 100 and 
                        header_text[0].isupper() and
                        not header_text.startswith('Table') and
                        not header_text.startswith('See') and
                        '(' not in header_text):  # "(ATTACK)" gibi formatları filtrele
                        
                        # Sonraki paragrafları al
                        description_parts = []
                        next_elem = header.find_next_sibling()
                        while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                            text = next_elem.get_text(strip=True)
                            if len(text) > 20:
                                description_parts.append(text)
                            next_elem = next_elem.find_next_sibling()
                            # Bir sonraki başlığa gelince dur
                            if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                                break
                            if len(description_parts) >= 10:
                                break
                        
                        # Category'yi header'dan çıkar
                        category = ""
                        if 'ATTACK' in header_text.upper():
                            category = "Attack"
                        elif 'DEFENSE' in header_text.upper():
                            category = "Defense"
                        elif 'MOVEMENT' in header_text.upper():
                            category = "Movement"
                        elif 'CONTROL' in header_text.upper():
                            category = "Control"
                        elif 'GENERAL' in header_text.upper():
                            category = "General"
                        elif 'SENSORY' in header_text.upper():
                            category = "Sensory"
                        
                        effects_data[header_text] = {
                            "name": header_text,
                            "category": category,
                            "cost_per_rank": 1,
                            "description": "\n\n".join(description_parts),
                            "source": urljoin(self.base_url, effects_url)
                        }
            
            print(f"  ... {len(effects_data)} effect bulundu")
        
        print(f"✅ {len(effects_data)} power effect çekildi")
        return effects_data
    
    def _scrape_effect_detail_from_same_page(self, main_content, effect_name: str) -> Optional[Dict[str, Any]]:
        """Aynı sayfadan effect detayını çek"""
        effect_data = {
            "name": effect_name,
            "category": "",
            "cost_per_rank": 1,
            "description": "",
            "source": urljoin(self.base_url, self.SECTIONS["effect_descriptions"])
        }
        
        # Effect adını içeren başlığı bul
        headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
        for header in headers:
            header_text = header.get_text(strip=True)
            if effect_name.lower() in header_text.lower() or header_text.lower() in effect_name.lower():
                # Category'yi belirle
                if 'ATTACK' in header_text.upper():
                    effect_data["category"] = "Attack"
                elif 'DEFENSE' in header_text.upper():
                    effect_data["category"] = "Defense"
                elif 'MOVEMENT' in header_text.upper():
                    effect_data["category"] = "Movement"
                elif 'CONTROL' in header_text.upper():
                    effect_data["category"] = "Control"
                elif 'GENERAL' in header_text.upper():
                    effect_data["category"] = "General"
                elif 'SENSORY' in header_text.upper():
                    effect_data["category"] = "Sensory"
                
                # Sonraki paragrafları al
                description_parts = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 20:
                        description_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if len(description_parts) >= 10:
                        break
                
                effect_data["description"] = "\n\n".join(description_parts)
                break
        
        return effect_data
    
    def _scrape_effect_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir effect'in detay sayfasını çek - GELİŞTİRİLMİŞ"""
        soup = self._get(url)
        if not soup:
            return None
        
        effect_data = {
            "name": name,
            "category": "",  # Attack, Defense, Movement, etc.
            "cost_per_rank": 1,
            "description": "",
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Effect başlığını bul (h1, h2, h3)
            effect_header = None
            headers = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
            for header in headers:
                header_text = header.get_text(strip=True).upper()
                if name.upper() in header_text or header_text.startswith(name.upper()):
                    effect_header = header
                    # Category'yi header'dan çıkar
                    category_match = re.search(r'\(([A-Z]+)\)', header_text)
                    if category_match:
                        category_map = {
                            "ATTACK": "Attack",
                            "DEFENSE": "Defense",
                            "MOVEMENT": "Movement",
                            "CONTROL": "Control",
                            "GENERAL": "General",
                            "SENSORY": "Sensory"
                        }
                        category = category_match.group(1)
                        effect_data["category"] = category_map.get(category, "")
                    break
            
            # Category'yi bul (eğer header'da yoksa)
            if not effect_data["category"]:
                category_match = re.search(r'(Attack|Defense|Movement|Control|General|Sensory)', main_content.get_text(), re.I)
                if category_match:
                    effect_data["category"] = category_match.group(1).capitalize()
            
            # Description'ı bul - başlıktan sonraki paragrafları al
            description_parts = []
            start_elem = effect_header if effect_header else main_content
            
            # İlk paragrafları al
            next_elem = start_elem.find_next_sibling() if effect_header else main_content.find('p')
            while next_elem:
                if next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    # Bir sonraki başlığa gelince dur
                    break
                
                if next_elem.name in ['p', 'div']:
                    text = next_elem.get_text(strip=True)
                    # Footer linklerini filtrele
                    if (len(text) > 30 and 
                        'Green Ronin' not in text and 
                        'Mutants & Masterminds' not in text and
                        'OGN' not in text and
                        'd20pfsrd' not in text.lower()):
                        description_parts.append(text)
                
                next_elem = next_elem.find_next_sibling()
                
                # Çok fazla içerik çekmemek için limit
                if len(description_parts) >= 15:
                    break
            
            # Eğer paragraflar bulunamadıysa, ilk paragrafı al
            if not description_parts:
                # Tüm paragrafları bul
                all_paragraphs = main_content.find_all('p')
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    # Footer linklerini filtrele
                    if (len(text) > 30 and 
                        'Green Ronin' not in text and 
                        'Mutants & Masterminds' not in text and
                        'OGN' not in text and
                        'd20pfsrd' not in text.lower() and
                        'Open Gaming' not in text):
                        description_parts.append(text)
                        if len(description_parts) >= 5:
                            break
            
            # Eğer hala açıklama yoksa, tüm içeriği al
            if not description_parts:
                full_text = main_content.get_text()
                # Effect adından sonraki metni bul
                pattern = rf'{re.escape(name)}[:\s]*([^A-Z]{{100,1500}}?)(?=[A-Z]{{3,}}|\n\n|$)'
                match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
                if match:
                    description_parts.append(match.group(1).strip())
            
            if description_parts:
                effect_data["description"] = "\n\n".join(description_parts)[:2000]  # İlk 2000 karakter
            else:
                effect_data["description"] = f"{name} is a power effect in Mutants & Masterminds."
        
        return effect_data
    
    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tüm M&M verilerini çek ve birleştir"""
        print("🚀 Mutants & Masterminds verileri çekiliyor...")
        print("⚠️  Bu işlem birkaç dakika sürebilir. Lütfen bekleyin...\n")
        
        data = {
            "system": "MUTANTS_AND_MASTERMINDS",
            "source": "d20herosrd.com",
            "abilities": self.scrape_abilities(),
            "archetypes": self.scrape_archetypes(),
            "skills": self.scrape_skills(),
            "advantages": self.scrape_advantages(),
            "powers": self.scrape_powers(),
            "power_effects": self.scrape_power_effects(),
            "power_levels": {  # Sabit değerler
                "PL8": {"attack_bonus_cap": 8, "effect_rank_cap": 10, "defense_cap": 8, "toughness_cap": 10},
                "PL10": {"attack_bonus_cap": 10, "effect_rank_cap": 10, "defense_cap": 10, "toughness_cap": 10},
                "PL12": {"attack_bonus_cap": 12, "effect_rank_cap": 12, "defense_cap": 12, "toughness_cap": 12},
                "PL15": {"attack_bonus_cap": 15, "effect_rank_cap": 15, "defense_cap": 15, "toughness_cap": 15},
            }
        }
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Veriler kaydedildi: {output_file}")
        
        return data


if __name__ == "__main__":
    # Test için
    scraper = MMScraper(delay=1.0)
    output = Path(__file__).resolve().parents[1] / "data" / "mm_data.json"
    scraper.scrape_all(output_file=output)


"""
Mutants & Masterminds Web Scraper
d20herosrd.com sitesinden tüm kuralları ve karakter oluşturma bilgilerini çeker.
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class MMScraper:
    """Mutants & Masterminds verilerini d20herosrd.com'dan çeken scraper"""
    
    BASE_URL = "https://www.d20herosrd.com"
    
    # Ana bölümler - Doğru URL'ler (test edilmiş)
    SECTIONS = {
        "character_creation": "/character-creation/",
        "abilities": "/character-creation/3-abilities/",
        "advancement": "/character-creation/advancement/",
        "archetypes": "/character-creation/archetypes/",
        "skills": "/4-skills/",  # Doğru URL - sayı ile başlıyor, /character-creation/ yok
        "advantages": "/5-advantages/",  # Doğru URL - sayı ile başlıyor, /character-creation/ yok
        "powers": "/6-powers/",
        "sample_powers": "/6-powers/sample-powers/",
        "power_effects": "/6-powers/effects/",
        "effect_descriptions": "/6-powers/effects/effect-descriptions/",
        "descriptors": "/6-powers/descriptors/",
        "modifiers": "/6-powers/modifiers/",
        "gadgets": "/gadgets-gear/",
        "conditions": "/gamemastering/conditions/",
        "npcs": "/gamemastering/npcs/",
        "basics": "/the-basics/",
    }
    
    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: İstekler arası bekleme süresi (saniye) - siteyi yormamak için
        """
        self.base_url = self.BASE_URL
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """URL'den HTML içeriğini çek ve BeautifulSoup nesnesi döndür"""
        if not url:
            return None
        full_url = urljoin(self.base_url, url) if not url.startswith("http") else url
        
        for attempt in range(retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(full_url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"❌ Hata: {full_url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_abilities(self) -> Dict[str, Any]:
        """Abilities (Yetenekler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("💪 Abilities çekiliyor...")
        abilities_data = {}
        
        soup = self._get(self.SECTIONS["abilities"])
        if not soup:
            return abilities_data
        
        # Ana içeriği bul
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Tüm abilities'leri bul (8 temel ability)
            abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
            ability_abbrevs = {"Strength": "STR", "Stamina": "STA", "Agility": "AGL", "Dexterity": "DEX", 
                             "Fighting": "FGT", "Intellect": "INT", "Awareness": "AWE", "Presence": "PRE"}
            
            # H3 başlıklarını bul (STRENGTH (STR) formatında)
            h3_headers = main_content.find_all('h3')
            
            for ability_name in abilities:
                ability_header = None
                description_parts = []
                
                # H3 başlıklarında ara (STRENGTH (STR) formatı)
                abbrev = ability_abbrevs.get(ability_name, "")
                for header in h3_headers:
                    header_text = header.get_text(strip=True).upper()
                    # "STRENGTH (STR)" veya "STRENGTH" formatını kontrol et
                    if (ability_name.upper() in header_text or 
                        (abbrev and abbrev in header_text and len(header_text) < 30)):
                        ability_header = header
                        break
                
                # Başlık bulunduysa, sonraki içeriği al
                if ability_header:
                    # Bir sonraki ability başlığını bul (durma noktası)
                    next_ability_index = abilities.index(ability_name) + 1
                    next_ability_name = abilities[next_ability_index] if next_ability_index < len(abilities) else None
                    
                    # Sonraki elementleri al
                    current = ability_header.find_next_sibling()
                    while current:
                        # Bir sonraki H3 başlığına gelince dur (diğer ability başlığı)
                        if current.name == 'h3':
                            current_text = current.get_text(strip=True).upper()
                            # Bir sonraki ability başlığı mı?
                            if next_ability_name and next_ability_name.upper() in current_text:
                                break
                            # Başka bir ability başlığı mı?
                            if any(ab.upper() in current_text and ab != ability_name for ab in abilities):
                                break
                        
                        # İçeriği al (paragraflar)
                        if current.name in ['p', 'div']:
                            text = current.get_text(strip=True)
                            # Footer linklerini filtrele
                            if (len(text) > 30 and 
                                'Green Ronin' not in text and 
                                'Mutants & Masterminds' not in text and
                                'OGN' not in text and
                                'd20pfsrd' not in text.lower() and
                                'Open Gaming' not in text):
                                description_parts.append(text)
                        
                        # Liste öğelerini de al
                        elif current.name in ['ul', 'ol']:
                            items = current.find_all('li')
                            for item in items:
                                text = item.get_text(strip=True)
                                if len(text) > 20 and 'Green Ronin' not in text:
                                    description_parts.append(text)
                        
                        current = current.find_next_sibling()
                        
                        # Çok fazla içerik çekmemek için limit
                        if len(description_parts) >= 15:
                            break
                
                # Başlık bulunamadıysa, text'ten parse et
                if not ability_header or not description_parts:
                    text = main_content.get_text()
                    # Ability adından sonraki metni bul (bir sonraki H3 başlığına kadar)
                    next_ability_pattern = ""
                    if next_ability_name:
                        next_abbrev = ability_abbrevs.get(next_ability_name, "")
                        next_ability_pattern = f"|{next_ability_name.upper()}|{next_abbrev}"
                    
                    pattern = rf'{ability_name.upper()}[:\s(]*{abbrev}[:\s)]*([^A-Z]{{100,2000}}?)(?={next_ability_pattern}|$)'
                    match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
                    if match:
                        description_text = match.group(1).strip()
                        # Çok kısa veya geçersiz metinleri filtrele
                        if len(description_text) > 50:
                            description_parts.append(description_text)
                
                # Ability verisini oluştur
                if description_parts:
                    full_description = "\n\n".join(description_parts)
                    # Çok uzun olanları kısalt
                    if len(full_description) > 2000:
                        full_description = full_description[:2000] + "..."
                    abilities_data[ability_name] = {
                        "name": ability_name,
                        "description": full_description,
                        "cost_per_rank": 1,  # Her ability 1 cost per rank
                        "source": urljoin(self.base_url, self.SECTIONS["abilities"])
                    }
                else:
                    # En azından temel bilgiyi ekle
                    abilities_data[ability_name] = {
                        "name": ability_name,
                        "description": f"{ability_name} is one of the eight core abilities in Mutants & Masterminds.",
                        "cost_per_rank": 1,
                        "source": urljoin(self.base_url, self.SECTIONS["abilities"])
                    }
            
            print(f"  ... {len(abilities_data)} ability bulundu")
        
        print(f"✅ {len(abilities_data)} ability çekildi")
        return abilities_data
    
    def scrape_archetypes(self) -> Dict[str, Any]:
        """Archetypes (Arketipler) bilgilerini çek"""
        print("🎭 Archetypes çekiliyor...")
        archetypes_data = {}
        
        soup = self._get(self.SECTIONS["archetypes"])
        if not soup:
            return archetypes_data
        
        # Ana içeriği bul
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Archetype linklerini bul
            archetype_links = main_content.find_all('a', href=re.compile(r'/character-creation/archetypes/[^/]+/$'))
            
            for link in archetype_links:
                archetype_name = link.get_text(strip=True)
                if archetype_name and archetype_name not in archetypes_data:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    archetype_data = self._scrape_archetype_detail(href, archetype_name)
                    if archetype_data:
                        archetypes_data[archetype_name] = archetype_data
                        print(f"  ✓ {archetype_name}")
        
        print(f"✅ {len(archetypes_data)} archetype çekildi")
        return archetypes_data
    
    def _scrape_archetype_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir archetype'in detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        archetype_data = {
            "name": name,
            "summary": "",
            "suggested_powers": [],
            "suggested_advantages": [],
            "suggested_skills": [],
            "ability_suggestions": {},
            "source": url
        }
        
        # Ana içeriği bul - navigation ve footer'ı hariç tut
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # İlk anlamlı paragrafı bul (çok kısa olmayan)
            paragraphs = main_content.find_all('p')
            for p in paragraphs:
                text = p.get_text(strip=True)
                # Footer linklerini filtrele
                if len(text) > 50 and 'Green Ronin' not in text and 'Mutants & Masterminds' not in text:
                    archetype_data["summary"] = text
                    break
            
            # Powers, Advantages, Skills bölümlerini bul - GELİŞTİRİLMİŞ
            # Tüm metni al
            full_text = main_content.get_text()
            
            # Powers bölümünü bul
            # Pattern 1: "Powers:" veya "Suggested Powers:" başlığından sonra
            powers_section = main_content.find(string=re.compile(r'[Pp]owers?[:\s]', re.I))
            if powers_section:
                parent = powers_section.find_parent()
                if parent:
                    # Sonraki içeriği al (liste veya paragraf)
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            powers = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_powers"] = powers[:30]
                        else:
                            # Paragraftan power isimlerini çıkar
                            text = next_elem.get_text(strip=True)
                            # Power isimleri genellikle büyük harfle başlar
                            powers = re.findall(r'\b([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\b', text)
                            archetype_data["suggested_powers"] = [p.strip() for p in powers if len(p.strip()) < 50][:30]
            
            # Eğer bulunamadıysa, text'ten parse et
            if not archetype_data["suggested_powers"]:
                # "Powers:" veya "Powers" başlığından sonraki metni bul
                powers_match = re.search(r'[Pp]owers?[:\s]+([^A-Z]{20,500}?)(?=[Aa]dvantages?|[Ss]kills?|$)', full_text, re.IGNORECASE | re.DOTALL)
                if powers_match:
                    powers_text = powers_match.group(1)
                    # Power isimlerini çıkar (büyük harfle başlayan, virgülle ayrılmış)
                    powers = re.findall(r'\b([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\b', powers_text)
                    archetype_data["suggested_powers"] = [p.strip() for p in powers if len(p.strip()) < 50 and p.strip() != name][:30]
            
            # Advantages bölümünü bul - DÜZELTİLDİ (virgülle ayrılmış format)
            advantages_section = main_content.find(string=re.compile(r'[Aa]dvantages?[:\s]', re.I))
            if advantages_section:
                parent = advantages_section.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            advantages = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_advantages"] = advantages[:30]
                        else:
                            text = next_elem.get_text(strip=True)
                            # Virgülle ayrılmış advantage listesi
                            advantages = [a.strip() for a in text.split(',') if a.strip() and len(a.strip()) < 80]
                            archetype_data["suggested_advantages"] = advantages[:30]
            
            # Eğer bulunamadıysa, text'ten parse et - DÜZELTİLDİ
            if not archetype_data["suggested_advantages"]:
                # "Advantages:" başlığından sonraki satırı bul
                advantages_match = re.search(r'[Aa]dvantages?[:\s]*\n\s*([^\n]{20,500}?)(?=\n[A-Z]|\n\n|$)', full_text, re.IGNORECASE | re.DOTALL)
                if advantages_match:
                    advantages_text = advantages_match.group(1).strip()
                    # Virgülle ayrılmış advantage listesi
                    advantages = [a.strip() for a in advantages_text.split(',') if a.strip() and len(a.strip()) < 80]
                    # Çok kısa veya geçersiz olanları filtrele
                    advantages = [a for a in advantages if len(a) > 3 and not a.startswith('(') and not a.endswith(')')]
                    archetype_data["suggested_advantages"] = advantages[:30]
            
            # Skills bölümünü bul - DÜZELTİLDİ
            skills_section = main_content.find(string=re.compile(r'[Ss]kills?[:\s]', re.I))
            if skills_section:
                parent = skills_section.find_parent()
                if parent:
                    next_elem = parent.find_next_sibling(['ul', 'ol', 'p', 'div'])
                    if next_elem:
                        if next_elem.name in ['ul', 'ol']:
                            skills = [li.get_text(strip=True) for li in next_elem.find_all('li')]
                            archetype_data["suggested_skills"] = skills[:30]
                        else:
                            text = next_elem.get_text(strip=True)
                            # Skill formatı: "Skill Name: X (+Y)" veya "Skill Name X (+Y)", virgülle ayrılmış
                            # Önce virgülle ayır, sonra skill isimlerini çıkar
                            skills_parts = text.split(',')
                            skills = []
                            for part in skills_parts:
                                part = part.strip()
                                # Skill ismini çıkar (başında rakam veya parantez varsa öncesini al)
                                # "Insight 4 (+6)" -> "Insight"
                                skill_match = re.match(r'^([A-Z][A-Za-z\s]+(?:\([^)]+\))?)', part)
                                if skill_match:
                                    skill_name = skill_match.group(1).strip()
                                    # Parantez içindeki "Choose one of" gibi açıklamaları dahil et
                                    if '(' in skill_name and 'Choose' in skill_name:
                                        # "Expertise: (Choose one of Business, Engineering, or Science)" -> "Expertise (Choose one of Business, Engineering, or Science)"
                                        pass
                                    # Çok uzun olanları filtrele
                                    if len(skill_name) < 80:
                                        skills.append(skill_name)
                            archetype_data["suggested_skills"] = skills[:30]
            
            # Eğer bulunamadıysa, text'ten parse et - DÜZELTİLDİ
            if not archetype_data["suggested_skills"]:
                # "Skills:" başlığından sonraki satırı bul
                skills_match = re.search(r'[Ss]kills?[:\s]*\n\s*([^\n]{50,1000}?)(?=\n[A-Z]|\n\n|$)', full_text, re.IGNORECASE | re.DOTALL)
                if skills_match:
                    skills_text = skills_match.group(1).strip()
                    # Virgülle ayrılmış skill listesi
                    skills_parts = skills_text.split(',')
                    skills = []
                    for part in skills_parts:
                        part = part.strip()
                        # Skill ismini çıkar (rakam ve parantez öncesi)
                        # "Insight 4 (+6)" -> "Insight"
                        skill_match = re.match(r'^([A-Z][A-Za-z\s]+(?:\([^)]+\))?)', part)
                        if skill_match:
                            skill_name = skill_match.group(1).strip()
                            # "Expertise: (Choose one of...)" formatını koru
                            if ':' in skill_name:
                                skill_name = skill_name.replace(':', '').strip()
                            if len(skill_name) < 80 and skill_name not in skills:
                                skills.append(skill_name)
                    archetype_data["suggested_skills"] = skills[:30]
            
            # Ability suggestions - genellikle tablo veya liste formatında
            # Örneğin: "Strength 8, Stamina 4, Agility 2, Dexterity 2, Fighting 4, Intellect 6, Awareness 4, Presence 2"
            ability_match = re.search(r'(Strength|Stamina|Agility|Dexterity|Fighting|Intellect|Awareness|Presence)\s+(\d+)', full_text, re.I)
            if ability_match:
                # Tüm ability'leri bul
                abilities = ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]
                for ability in abilities:
                    pattern = rf'{ability}\s+(\d+)'
                    match = re.search(pattern, full_text, re.I)
                    if match:
                        archetype_data["ability_suggestions"][ability] = int(match.group(1))
        
        return archetype_data
    
    def _find_section_url(self, section_name: str, base_url: str = None) -> Optional[str]:
        """Belirli bir bölümün URL'ini bul"""
        if base_url is None:
            base_url = self.SECTIONS["character_creation"]
        
        soup = self._get(base_url)
        if not soup:
            return None
        
        # Section name'i içeren linkleri bul
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            text = link.get_text(strip=True).lower()
            if section_name.lower() in text or section_name.lower().replace(' ', '-') in href.lower():
                if href.startswith('/'):
                    return href
                elif href.startswith('http'):
                    return href.replace(self.base_url, '')
        
        return None
    
    def scrape_skills(self) -> Dict[str, Any]:
        """Skills (Beceriler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("🎯 Skills çekiliyor...")
        skills_data = {}
        
        # Doğru URL'i kullan
        skills_url = self.SECTIONS["skills"]
        
        soup = self._get(skills_url)
        if not soup:
            return skills_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Skills sayfasında genellikle tablo veya liste formatında skill'ler var
            # Skill linklerini bul (anchor linkleri)
            skill_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
            
            # Eğer anchor linkleri varsa, skill isimlerini çıkar
            if skill_links:
                for link in skill_links:
                    skill_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    # "Skill Name (Ability)" formatını parse et
                    match = re.match(r'([A-Z][A-Z\s]+(?:\([^)]+\))?)\s*\(?([A-Z][a-z]+)\)?', skill_text)
                    if match:
                        skill_name = match.group(1).strip()
                        ability = match.group(2) if len(match.groups()) > 1 and match.group(2) else ""
                    else:
                        skill_name = skill_text
                        ability = ""
                    
                    # Ability'yi href'ten de çıkarabiliriz
                    ability_match = re.search(r'#TOC-[A-Z]+-([A-Z][a-z]+)', href)
                    if ability_match:
                        ability = ability_match.group(1)
                    
                    if skill_name and len(skill_name) < 50 and skill_name not in skills_data:
                        skills_data[skill_name] = {
                            "name": skill_name,
                            "key_ability": ability,
                            "cost_per_rank": 1,  # Varsayılan
                            "description": "",
                            "source": urljoin(self.base_url, skills_url + href)
                        }
            
            # Eğer link yoksa, tablo veya liste formatında skill'leri bul
            if not skills_data:
                text = main_content.get_text()
                # Skill pattern'i: "Skill Name (Ability)" veya "Skill Name: Ability"
                skill_patterns = [
                    r'([A-Z][A-Za-z\s]+(?:\([^)]+\))?)\s+\(([A-Z][a-z]+)\)',  # "Skill Name (Ability)"
                    r'([A-Z][A-Za-z\s]+):\s+([A-Z][a-z]+)',  # "Skill Name: Ability"
                ]
                
                for pattern in skill_patterns:
                    matches = re.finditer(pattern, text)
                    for match in matches:
                        skill_name = match.group(1).strip()
                        ability = match.group(2) if len(match.groups()) > 1 else ""
                        
                        # Çok uzun veya geçersiz olanları filtrele
                        if (skill_name and len(skill_name) < 50 and 
                            skill_name not in skills_data and
                            skill_name[0].isupper() and
                            ability in ["Strength", "Stamina", "Agility", "Dexterity", "Fighting", "Intellect", "Awareness", "Presence"]):
                            skills_data[skill_name] = {
                                "name": skill_name,
                                "key_ability": ability,
                                "cost_per_rank": 1,
                                "description": "",
                                "source": urljoin(self.base_url, skills_url)
                            }
            
            print(f"  ... {len(skills_data)} skill bulundu")
        
        print(f"✅ {len(skills_data)} skill çekildi")
        return skills_data
    
    def scrape_advantages(self) -> Dict[str, Any]:
        """Advantages (Avantajlar) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("⭐ Advantages çekiliyor...")
        advantages_data = {}
        
        # Doğru URL'i kullan
        advantages_url = self.SECTIONS["advantages"]
        
        soup = self._get(advantages_url)
        if not soup:
            return advantages_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Advantages sayfasında genellikle anchor linkleri veya liste formatında advantage'ler var
            # Advantage linklerini bul (anchor linkleri)
            advantage_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
            
            # Eğer anchor linkleri varsa, advantage isimlerini çıkar
            if advantage_links:
                for link in advantage_links:
                    advantage_text = link.get_text(strip=True)
                    href = link.get('href', '')
                    
                    # "Advantage Name" veya "Advantage Name (Cost)" formatını parse et
                    match = re.match(r'([A-Z][A-Z\s&()-]+(?:\([^)]+\))?)', advantage_text)
                    if match:
                        advantage_name = match.group(1).strip()
                        # Cost bilgisini çıkar
                        cost_match = re.search(r'\(([0-9]+)\s*(?:rank|point)', advantage_text, re.I)
                        cost = int(cost_match.group(1)) if cost_match else 1
                    else:
                        advantage_name = advantage_text
                        cost = 1
                    
                    if advantage_name and len(advantage_name) < 80 and advantage_name not in advantages_data:
                        advantages_data[advantage_name] = {
                            "name": advantage_name,
                            "cost": cost,
                            "description": "",
                            "source": urljoin(self.base_url, advantages_url + href)
                        }
                        
                        # Detay sayfasından açıklama çek (eğer varsa)
                        if href.startswith('#'):
                            # Anchor link, aynı sayfada detay bul
                            anchor_id = href.replace('#', '').replace('TOC-', '')
                            # Anchor'a git ve sonraki içeriği al
                            anchor = main_content.find('a', {'name': anchor_id}) or main_content.find('a', {'id': anchor_id})
                            if anchor:
                                parent = anchor.find_parent(['h2', 'h3', 'h4', 'p', 'div'])
                                if parent:
                                    next_elem = parent.find_next_sibling('p')
                                    if next_elem:
                                        advantages_data[advantage_name]["description"] = next_elem.get_text(strip=True)
            
            # Eğer anchor linkleri yoksa, direkt advantage'leri bul
            if not advantages_data:
                # Tüm başlıkları ve altındaki içeriği bul
                headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
                for header in headers:
                    header_text = header.get_text(strip=True)
                    # Geçersiz başlıkları filtrele
                    if (len(header_text) < 80 and 
                        header_text[0].isupper() and
                        'Advantage' not in header_text and
                        not header_text.startswith('Table') and
                        not header_text.startswith('See')):
                        
                        # Sonraki paragrafı al
                        next_elem = header.find_next_sibling(['p', 'div'])
                        if next_elem:
                            description = next_elem.get_text(strip=True)
                            # Cost bilgisini çıkar
                            cost_match = re.search(r'Cost[:\s]+(\d+)', description, re.I)
                            cost = int(cost_match.group(1)) if cost_match else 1
                            
                            advantages_data[header_text] = {
                                "name": header_text,
                                "cost": cost,
                                "description": description[:500],  # İlk 500 karakter
                                "source": urljoin(self.base_url, advantages_url)
                            }
            
            print(f"  ... {len(advantages_data)} advantage bulundu")
        
        print(f"✅ {len(advantages_data)} advantage çekildi")
        return advantages_data
    
    def _scrape_advantage_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir advantage'in detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        advantage_data = {
            "name": name,
            "cost": 1,  # Varsayılan
            "description": "",
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Cost bilgisini bul
            cost_match = re.search(r'Cost[:\s]+(\d+)', main_content.get_text(), re.IGNORECASE)
            if cost_match:
                advantage_data["cost"] = int(cost_match.group(1))
            
            # Description'ı bul
            desc_p = main_content.find('p')
            if desc_p:
                advantage_data["description"] = desc_p.get_text(strip=True)
        
        return advantage_data
    
    def scrape_powers(self) -> Dict[str, Any]:
        """Powers (Güçler) bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("⚡ Powers çekiliyor...")
        powers_data = {}
        
        # Sample Powers sayfasından başla
        sample_powers_url = self.SECTIONS["sample_powers"]
        
        soup = self._get(sample_powers_url)
        if not soup:
            return powers_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Power linklerini bul - hem /sample-powers/ hem de /6-powers/ altında olabilir
            power_links = main_content.find_all('a', href=re.compile(r'/6-powers/sample-powers/[^/]+/$'))
            
            # Eğer link bulunamazsa, anchor linkleri dene
            if not power_links:
                power_links = main_content.find_all('a', href=re.compile(r'#TOC-[A-Z]'))
                # Power isimlerini çıkar
                for link in power_links:
                    power_text = link.get_text(strip=True)
                    # Çok uzun veya geçersiz olanları filtrele
                    if (power_text and len(power_text) < 80 and 
                        power_text[0].isupper() and
                        power_text not in powers_data):
                        # Power detayını aynı sayfadan çek
                        power_data = self._scrape_power_detail_from_same_page(main_content, power_text)
                        if power_data:
                            powers_data[power_text] = power_data
            
            # Direkt linkler varsa, detay sayfalarını çek
            for link in power_links:
                power_name = link.get_text(strip=True)
                if power_name and power_name not in powers_data and len(power_name) < 80:
                    href = link.get('href', '')
                    if not href.startswith('http'):
                        href = urljoin(self.base_url, href)
                    
                    power_data = self._scrape_power_detail(href, power_name)
                    if power_data:
                        powers_data[power_name] = power_data
                        if len(powers_data) % 10 == 0:
                            print(f"  ... {len(powers_data)} power çekildi")
            
            print(f"  ... {len(powers_data)} power bulundu")
        
        print(f"✅ {len(powers_data)} power çekildi")
        return powers_data
    
    def _scrape_power_detail_from_same_page(self, main_content, power_name: str) -> Optional[Dict[str, Any]]:
        """Aynı sayfadan power detayını çek (anchor linkler için)"""
        power_data = {
            "name": power_name,
            "cost_per_rank": 1,
            "description": "",
            "source": urljoin(self.base_url, self.SECTIONS["sample_powers"])
        }
        
        # Power adını içeren başlığı bul
        headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
        for header in headers:
            header_text = header.get_text(strip=True)
            if power_name.lower() in header_text.lower() or header_text.lower() in power_name.lower():
                # Sonraki paragrafları al
                description_parts = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 20:
                        description_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    # Bir sonraki başlığa gelince dur
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if len(description_parts) >= 10:
                        break
                
                power_data["description"] = "\n\n".join(description_parts)
                break
        
        return power_data
    
    def _scrape_power_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir power'ın detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        power_data = {
            "name": name,
            "cost_per_rank": 1,  # Varsayılan
            "description": "",
            "effects": [],
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Cost bilgisini bul
            cost_match = re.search(r'Cost[:\s]+(\d+)', main_content.get_text(), re.IGNORECASE)
            if cost_match:
                power_data["cost_per_rank"] = int(cost_match.group(1))
            
            # Description'ı bul
            desc_p = main_content.find('p')
            if desc_p:
                power_data["description"] = desc_p.get_text(strip=True)
        
        return power_data
    
    def scrape_power_effects(self) -> Dict[str, Any]:
        """Power Effects bilgilerini çek - GELİŞTİRİLMİŞ"""
        print("✨ Power Effects çekiliyor...")
        effects_data = {}
        
        # Effect Descriptions sayfasından başla
        effects_url = self.SECTIONS["effect_descriptions"]
        
        soup = self._get(effects_url)
        if not soup:
            # Alternatif URL dene
            effects_url = self.SECTIONS["power_effects"]
            soup = self._get(effects_url)
        
        if not soup:
            return effects_data
        
        main_content = soup.find('div', class_='content') or soup.find('main') or soup.find('body')
        if main_content:
            # Effect linklerini bul - DÜZELTİLDİ (doğru pattern)
            # Format: /6-powers/effects/effect-descriptions/[effect-name]/
            effect_links = main_content.find_all('a', href=re.compile(r'/6-powers/effects/effect-descriptions/[^/]+/$'))
            
            print(f"  ... {len(effect_links)} effect linki bulundu")
            
            # Her effect linkini işle
            for link in effect_links:
                effect_name = link.get_text(strip=True)
                href = link.get('href', '')
                
                # Geçersiz linkleri filtrele
                if not effect_name or len(effect_name) > 100 or effect_name in effects_data:
                    continue
                
                # Effect adını temizle (örn: "AFFLICTION (ATTACK)" -> "AFFLICTION")
                # Category'yi parantez içinden çıkar
                category_match = re.search(r'\(([A-Z]+)\)', effect_name)
                category = category_match.group(1) if category_match else ""
                # Category mapping
                category_map = {
                    "ATTACK": "Attack",
                    "DEFENSE": "Defense",
                    "MOVEMENT": "Movement",
                    "CONTROL": "Control",
                    "GENERAL": "General",
                    "SENSORY": "Sensory"
                }
                category = category_map.get(category, "")
                
                # Effect adını temizle (parantez ve category'yi kaldır)
                clean_name = re.sub(r'\s*\([^)]+\)', '', effect_name).strip()
                
                # Detay sayfasını çek
                if not href.startswith('http'):
                    href = urljoin(self.base_url, href)
                
                effect_data = self._scrape_effect_detail(href, clean_name)
                if effect_data:
                    # Category'yi ekle (eğer detay sayfasında yoksa)
                    if category and not effect_data.get("category"):
                        effect_data["category"] = category
                    # Effect name'i güncelle
                    effect_data["name"] = clean_name
                    effects_data[clean_name] = effect_data
                    
                    if len(effects_data) % 10 == 0:
                        print(f"    ... {len(effects_data)} effect çekildi")
                else:
                    # Eğer detay sayfası çekilemediyse, en azından temel bilgiyi kaydet
                    effects_data[clean_name] = {
                        "name": clean_name,
                        "category": category,
                        "cost_per_rank": 1,
                        "description": f"{clean_name} is a power effect in Mutants & Masterminds.",
                        "source": href if href.startswith('http') else urljoin(self.base_url, href)
                    }
            
            # Eğer link bulunamadıysa, başlıklardan çek
            if not effects_data:
                headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
                for header in headers:
                    header_text = header.get_text(strip=True)
                    # Geçersiz başlıkları filtrele
                    if (len(header_text) < 100 and 
                        header_text[0].isupper() and
                        not header_text.startswith('Table') and
                        not header_text.startswith('See') and
                        '(' not in header_text):  # "(ATTACK)" gibi formatları filtrele
                        
                        # Sonraki paragrafları al
                        description_parts = []
                        next_elem = header.find_next_sibling()
                        while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                            text = next_elem.get_text(strip=True)
                            if len(text) > 20:
                                description_parts.append(text)
                            next_elem = next_elem.find_next_sibling()
                            # Bir sonraki başlığa gelince dur
                            if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                                break
                            if len(description_parts) >= 10:
                                break
                        
                        # Category'yi header'dan çıkar
                        category = ""
                        if 'ATTACK' in header_text.upper():
                            category = "Attack"
                        elif 'DEFENSE' in header_text.upper():
                            category = "Defense"
                        elif 'MOVEMENT' in header_text.upper():
                            category = "Movement"
                        elif 'CONTROL' in header_text.upper():
                            category = "Control"
                        elif 'GENERAL' in header_text.upper():
                            category = "General"
                        elif 'SENSORY' in header_text.upper():
                            category = "Sensory"
                        
                        effects_data[header_text] = {
                            "name": header_text,
                            "category": category,
                            "cost_per_rank": 1,
                            "description": "\n\n".join(description_parts),
                            "source": urljoin(self.base_url, effects_url)
                        }
            
            print(f"  ... {len(effects_data)} effect bulundu")
        
        print(f"✅ {len(effects_data)} power effect çekildi")
        return effects_data
    
    def _scrape_effect_detail_from_same_page(self, main_content, effect_name: str) -> Optional[Dict[str, Any]]:
        """Aynı sayfadan effect detayını çek"""
        effect_data = {
            "name": effect_name,
            "category": "",
            "cost_per_rank": 1,
            "description": "",
            "source": urljoin(self.base_url, self.SECTIONS["effect_descriptions"])
        }
        
        # Effect adını içeren başlığı bul
        headers = main_content.find_all(['h2', 'h3', 'h4', 'h5'])
        for header in headers:
            header_text = header.get_text(strip=True)
            if effect_name.lower() in header_text.lower() or header_text.lower() in effect_name.lower():
                # Category'yi belirle
                if 'ATTACK' in header_text.upper():
                    effect_data["category"] = "Attack"
                elif 'DEFENSE' in header_text.upper():
                    effect_data["category"] = "Defense"
                elif 'MOVEMENT' in header_text.upper():
                    effect_data["category"] = "Movement"
                elif 'CONTROL' in header_text.upper():
                    effect_data["category"] = "Control"
                elif 'GENERAL' in header_text.upper():
                    effect_data["category"] = "General"
                elif 'SENSORY' in header_text.upper():
                    effect_data["category"] = "Sensory"
                
                # Sonraki paragrafları al
                description_parts = []
                next_elem = header.find_next_sibling()
                while next_elem and next_elem.name in ['p', 'ul', 'ol', 'div']:
                    text = next_elem.get_text(strip=True)
                    if len(text) > 20:
                        description_parts.append(text)
                    next_elem = next_elem.find_next_sibling()
                    if next_elem and next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                        break
                    if len(description_parts) >= 10:
                        break
                
                effect_data["description"] = "\n\n".join(description_parts)
                break
        
        return effect_data
    
    def _scrape_effect_detail(self, url: str, name: str) -> Optional[Dict[str, Any]]:
        """Belirli bir effect'in detay sayfasını çek - GELİŞTİRİLMİŞ"""
        soup = self._get(url)
        if not soup:
            return None
        
        effect_data = {
            "name": name,
            "category": "",  # Attack, Defense, Movement, etc.
            "cost_per_rank": 1,
            "description": "",
            "source": url
        }
        
        main_content = soup.find('div', class_='content') or soup.find('main')
        if not main_content:
            main_content = soup.find('body')
        
        if main_content:
            # Navigation ve footer'ı temizle
            for nav in main_content.find_all(['nav', 'header', 'footer']):
                nav.decompose()
            
            # Effect başlığını bul (h1, h2, h3)
            effect_header = None
            headers = main_content.find_all(['h1', 'h2', 'h3', 'h4', 'h5'])
            for header in headers:
                header_text = header.get_text(strip=True).upper()
                if name.upper() in header_text or header_text.startswith(name.upper()):
                    effect_header = header
                    # Category'yi header'dan çıkar
                    category_match = re.search(r'\(([A-Z]+)\)', header_text)
                    if category_match:
                        category_map = {
                            "ATTACK": "Attack",
                            "DEFENSE": "Defense",
                            "MOVEMENT": "Movement",
                            "CONTROL": "Control",
                            "GENERAL": "General",
                            "SENSORY": "Sensory"
                        }
                        category = category_match.group(1)
                        effect_data["category"] = category_map.get(category, "")
                    break
            
            # Category'yi bul (eğer header'da yoksa)
            if not effect_data["category"]:
                category_match = re.search(r'(Attack|Defense|Movement|Control|General|Sensory)', main_content.get_text(), re.I)
                if category_match:
                    effect_data["category"] = category_match.group(1).capitalize()
            
            # Description'ı bul - başlıktan sonraki paragrafları al
            description_parts = []
            start_elem = effect_header if effect_header else main_content
            
            # İlk paragrafları al
            next_elem = start_elem.find_next_sibling() if effect_header else main_content.find('p')
            while next_elem:
                if next_elem.name in ['h1', 'h2', 'h3', 'h4', 'h5']:
                    # Bir sonraki başlığa gelince dur
                    break
                
                if next_elem.name in ['p', 'div']:
                    text = next_elem.get_text(strip=True)
                    # Footer linklerini filtrele
                    if (len(text) > 30 and 
                        'Green Ronin' not in text and 
                        'Mutants & Masterminds' not in text and
                        'OGN' not in text and
                        'd20pfsrd' not in text.lower()):
                        description_parts.append(text)
                
                next_elem = next_elem.find_next_sibling()
                
                # Çok fazla içerik çekmemek için limit
                if len(description_parts) >= 15:
                    break
            
            # Eğer paragraflar bulunamadıysa, ilk paragrafı al
            if not description_parts:
                # Tüm paragrafları bul
                all_paragraphs = main_content.find_all('p')
                for p in all_paragraphs:
                    text = p.get_text(strip=True)
                    # Footer linklerini filtrele
                    if (len(text) > 30 and 
                        'Green Ronin' not in text and 
                        'Mutants & Masterminds' not in text and
                        'OGN' not in text and
                        'd20pfsrd' not in text.lower() and
                        'Open Gaming' not in text):
                        description_parts.append(text)
                        if len(description_parts) >= 5:
                            break
            
            # Eğer hala açıklama yoksa, tüm içeriği al
            if not description_parts:
                full_text = main_content.get_text()
                # Effect adından sonraki metni bul
                pattern = rf'{re.escape(name)}[:\s]*([^A-Z]{{100,1500}}?)(?=[A-Z]{{3,}}|\n\n|$)'
                match = re.search(pattern, full_text, re.IGNORECASE | re.DOTALL)
                if match:
                    description_parts.append(match.group(1).strip())
            
            if description_parts:
                effect_data["description"] = "\n\n".join(description_parts)[:2000]  # İlk 2000 karakter
            else:
                effect_data["description"] = f"{name} is a power effect in Mutants & Masterminds."
        
        return effect_data
    
    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tüm M&M verilerini çek ve birleştir"""
        print("🚀 Mutants & Masterminds verileri çekiliyor...")
        print("⚠️  Bu işlem birkaç dakika sürebilir. Lütfen bekleyin...\n")
        
        data = {
            "system": "MUTANTS_AND_MASTERMINDS",
            "source": "d20herosrd.com",
            "abilities": self.scrape_abilities(),
            "archetypes": self.scrape_archetypes(),
            "skills": self.scrape_skills(),
            "advantages": self.scrape_advantages(),
            "powers": self.scrape_powers(),
            "power_effects": self.scrape_power_effects(),
            "power_levels": {  # Sabit değerler
                "PL8": {"attack_bonus_cap": 8, "effect_rank_cap": 10, "defense_cap": 8, "toughness_cap": 10},
                "PL10": {"attack_bonus_cap": 10, "effect_rank_cap": 10, "defense_cap": 10, "toughness_cap": 10},
                "PL12": {"attack_bonus_cap": 12, "effect_rank_cap": 12, "defense_cap": 12, "toughness_cap": 12},
                "PL15": {"attack_bonus_cap": 15, "effect_rank_cap": 15, "defense_cap": 15, "toughness_cap": 15},
            }
        }
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\n✅ Veriler kaydedildi: {output_file}")
        
        return data


if __name__ == "__main__":
    # Test için
    scraper = MMScraper(delay=1.0)
    output = Path(__file__).resolve().parents[1] / "data" / "mm_data.json"
    scraper.scrape_all(output_file=output)

