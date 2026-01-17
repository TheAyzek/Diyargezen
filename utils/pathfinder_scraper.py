"""
Pathfinder 1e Web Scraper
Sınıflar, ırklar, feat'ler, büyüler ve diğer kuralları web'den çeker.
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class PathfinderScraper:
    """Pathfinder 1e verilerini web'den çeken scraper"""
    
    # Desteklenen siteler
    SITES = {
        "aonprd": {
            "base_url": "https://aonprd.com",
            "races_url": "/Races.aspx",
            "classes_url": "/Classes.aspx",
            "feats_url": "/Feats.aspx",
            "spells_url": "/Spells.aspx",
            "items_url": "/Equipment.aspx"
        },
        "d20pfsrd": {
            "base_url": "https://www.d20pfsrd.com",
            "races_url": "/races/",
            "classes_url": "/classes/",
            "feats_url": "/feats/",
            "spells_url": "/spells/",
            "items_url": "/equipment/"
        }
    }
    
    def __init__(self, site: str = "aonprd", delay: float = 1.0):
        """
        Args:
            site: Kullanılacak site ("aonprd" veya "d20pfsrd")
            delay: İstekler arası bekleme süresi (saniye) - siteyi yormamak için
        """
        if site not in self.SITES:
            raise ValueError(f"Desteklenmeyen site: {site}. Desteklenenler: {list(self.SITES.keys())}")
        
        self.site_config = self.SITES[site]
        self.base_url = self.site_config["base_url"]
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """URL'den HTML içeriğini çek ve BeautifulSoup nesnesi döndür"""
        full_url = urljoin(self.base_url, url) if not url.startswith("http") else url
        
        for attempt in range(retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(full_url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"ERROR: {full_url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_races(self) -> Dict[str, Any]:
        """Tüm ırkları çek"""
        print("🏃 Irklar çekiliyor...")
        races = {}
        
        # Site yapısına göre parse et
        if "aonprd" in self.base_url:
            # Archives of Nethys yapısı - Core ve NonCore kategorilerini çek
            for category in ["Core", "NonCore"]:
                url = f"{self.site_config['races_url']}?Category={category}"
                soup = self._get(url)
                if not soup:
                    continue
                
                # RacesDisplay.aspx linklerini bul (Display değil, RacesDisplay!)
                race_links = soup.find_all('a', href=re.compile(r'RacesDisplay\.aspx\?ItemName='))
                for link in race_links:
                    race_name = link.get_text(strip=True)
                    if race_name and race_name not in races:
                        href = link.get('href', '')
                        # Göreceli URL'yi tam URL'ye çevir
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        race_data = self._scrape_race_detail(href)
                        if race_data:
                            races[race_name] = race_data
                            print(f"  ✓ {race_name}")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - ana sayfadan tüm ırk linklerini bul
            soup = self._get(self.site_config["races_url"])
            if soup:
                # /races/core-races/ veya /races/advanced-races/ gibi linkleri bul
                race_links = soup.find_all('a', href=re.compile(r'/races/[^/]+/[^/]+$'))
                seen_races = set()
                for link in race_links:
                    href = link.get('href', '')
                    race_name = link.get_text(strip=True)
                    # Duplicate'leri önle
                    if href and href not in seen_races and race_name:
                        seen_races.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        race_data = self._scrape_race_detail(href)
                        if race_data:
                            races[race_name] = race_data
                            print(f"  ✓ {race_name}")
        
        print(f"OK: {len(races)} irk cekildi")
        return races
    
    def _scrape_race_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir ırkın detay sayfasını çek - GELİŞTİRİLMİŞ VERSİYON"""
        soup = self._get(url)
        if not soup:
            return None
        
        race_data = {
            "ability_score_increase": {},
            "ability_score_increase_text": "",  # "+2 to One Ability Score" gibi metin
            "speed": 30,
            "speed_special": "",  # "30 feet" veya "30 feet, swim 30 feet" gibi
            "traits": [],  # Trait isimleri ve açıklamaları
            "traits_detailed": {},  # Her trait için detaylı bilgi
            "languages": [],
            "languages_automatic": [],  # Otomatik diller
            "languages_bonus": [],  # Bonus dil seçenekleri
            "size": "Medium",
            "source": url,
            "type": "",  # Humanoid, Outsider, etc.
            "subtype": "",  # Subtype bilgisi
            "favored_class_bonus": "",  # Favored class bonus açıklaması
            "favored_classes": [],  # Favored class'lar
            "vision": "normal",  # normal, low-light, darkvision, etc.
            "vision_range": 0,  # Darkvision range
            "skill_bonuses": {},  # Skill bonusları
            "weapon_proficiencies": [],  # Weapon proficiencies
            "armor_proficiencies": [],  # Armor proficiencies
            "racial_spells": [],  # Racial spell-like abilities
            "spell_resistance": None,  # Spell resistance
            "description": ""  # Irk açıklaması
        }
        
        # Tüm metni al
        full_text = soup.get_text()
        
        # Ana içerik alanını bul
        main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
        if main_content:
            full_text = main_content.get_text()
        
        # ABILITY SCORE INCREASES - Geliştirilmiş parsing
        # Pattern 1: "+2 to One Ability Score" (Human gibi)
        one_ability_pattern = re.search(r'\+(\d+)\s+to\s+One\s+Ability\s+Score', full_text, re.IGNORECASE)
        if one_ability_pattern:
            bonus = int(one_ability_pattern.group(1))
            race_data["ability_score_increase_text"] = f"+{bonus} to One Ability Score"
            race_data["ability_score_increase"] = {"any": bonus}
        
        # Pattern 2: "+2 Str, +2 Con" veya "+2 Strength, +2 Constitution"
        if not race_data["ability_score_increase"]:
            ability_patterns = [
                (r'\+(\d+)\s+(?:Str|Strength)', "strength"),
                (r'\+(\d+)\s+(?:Dex|Dexterity)', "dexterity"),
                (r'\+(\d+)\s+(?:Con|Constitution)', "constitution"),
                (r'\+(\d+)\s+(?:Int|Intelligence)', "intelligence"),
                (r'\+(\d+)\s+(?:Wis|Wisdom)', "wisdom"),
                (r'\+(\d+)\s+(?:Cha|Charisma)', "charisma"),
            ]
            
            for pattern, ability in ability_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    # En yüksek bonus'u al
                    max_bonus = max(int(m) for m in matches)
                    race_data["ability_score_increase"][ability] = max_bonus
                    if not race_data["ability_score_increase_text"]:
                        race_data["ability_score_increase_text"] = f"+{max_bonus} {ability.capitalize()}"
                    else:
                        race_data["ability_score_increase_text"] += f", +{max_bonus} {ability.capitalize()}"
        
        # SIZE
        size_patterns = [
            r'Size\s*:?\s*(\w+)',
            r'(\w+)\s+size',
        ]
        for pattern in size_patterns:
            size_match = re.search(pattern, full_text, re.IGNORECASE)
            if size_match:
                size = size_match.group(1).capitalize()
                if size.lower() in ["small", "medium", "large", "tiny", "diminutive", "fine", "huge", "gargantuan", "colossal"]:
                    race_data["size"] = size
                    break
        
        # SPEED - Geliştirilmiş
        speed_match = re.search(r'Speed\s*:?\s*([^\n]+?)(?:\n|$)', full_text, re.IGNORECASE)
        if speed_match:
            speed_text = speed_match.group(1).strip()
            # Sayısal değeri bul
            speed_num_match = re.search(r'(\d+)', speed_text)
            if speed_num_match:
                race_data["speed"] = int(speed_num_match.group(1))
            race_data["speed_special"] = speed_text[:200]
        
        # LANGUAGES - Düzeltilmiş parsing
        # Archives of Nethys'te Languages genellikle <strong>Languages</strong> şeklinde
        lang_header = soup.find('strong', string=re.compile(r'^Languages?$', re.I))
        if not lang_header:
            lang_header = soup.find('b', string=re.compile(r'^Languages?$', re.I))
        
        if lang_header:
            # Sonraki içeriği bul (aynı veya sonraki p/div)
            lang_content = ""
            
            # Önce parent'ı kontrol et
            parent = lang_header.find_parent(['p', 'div'])
            if parent:
                # Parent içindeki tüm metni al, ama "Languages" başlığını çıkar
                parent_text = parent.get_text()
                lang_content = parent_text.replace(lang_header.get_text(), "").strip()
            
            # Eğer parent'ta yeterli bilgi yoksa, sonraki sibling'leri kontrol et
            if not lang_content or len(lang_content) < 20:
                next_elem = lang_header.find_next_sibling(['p', 'div'])
                if next_elem:
                    lang_content = next_elem.get_text(strip=True)
            
            if lang_content:
                # "Automatic" ve "Bonus" bölümlerini ayır
                auto_match = re.search(r'(?:Automatic|begin play speaking|speak)\s*:?\s*([^.]*?)(?:\.|Bonus|$)', lang_content, re.IGNORECASE | re.DOTALL)
                bonus_match = re.search(r'(?:Bonus\s+Languages?|bonus languages?)\s*:?\s*([^.]*)', lang_content, re.IGNORECASE)
                
                if auto_match:
                    auto_text = auto_match.group(1)
                    # Dil isimlerini ayır (Common, Elven, Draconic, etc.)
                    # Büyük harfle başlayan kelimeleri bul (dil isimleri genellikle büyük harfle başlar)
                    auto_langs = []
                    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', auto_text)
                    known_languages = ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Giant', 'Draconic', 'Gnoll', 
                                     'Halfling', 'Gnome', 'Sylvan', 'Aquan', 'Auran', 'Ignan', 'Terran', 'Celestial',
                                     'Infernal', 'Abyssal', 'Aklo', 'Undercommon', 'Jotun', 'Tengu', 'Varisian',
                                     'Kelish', 'Vudrani', 'Osiriani', 'Tien', 'Taldane', 'Skald', 'Chelish']
                    for word in words:
                        # Bilinen dil isimlerini kontrol et veya benzer olanları bul
                        if any(known in word for known in known_languages) or word in known_languages:
                            if word not in auto_langs:
                                auto_langs.append(word)
                    
                    # Eğer pattern ile bulamadıysak, "speaking X" veya "X and Y" formatını dene
                    if not auto_langs:
                        # "speaking Common and Elven" gibi formatları bul
                        speaking_match = re.search(r'speaking\s+([^.]+)', lang_content, re.IGNORECASE)
                        if speaking_match:
                            speaking_text = speaking_match.group(1)
                            # "and", "or" ile ayrılmış dilleri bul
                            langs = re.split(r'\s+(?:and|or)\s+', speaking_text)
                            for lang in langs:
                                lang = lang.strip()
                                if lang and len(lang) < 30 and lang[0].isupper():
                                    auto_langs.append(lang)
                    
                    race_data["languages_automatic"] = auto_langs[:10]
                
                if bonus_match:
                    bonus_text = bonus_match.group(1)
                    # Bonus dilleri ayır
                    bonus_langs = []
                    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', bonus_text)
                    known_languages = ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Giant', 'Draconic', 'Gnoll',
                                     'Halfling', 'Gnome', 'Sylvan', 'Aquan', 'Auran', 'Ignan', 'Terran']
                    for word in words:
                        if any(known in word for known in known_languages) or word in known_languages:
                            if word not in bonus_langs:
                                bonus_langs.append(word)
                    race_data["languages_bonus"] = bonus_langs[:20]
                
                # Eğer otomatik/bonus bulunamadıysa, genel "Languages" içeriğinden çıkar
                if not race_data["languages_automatic"] and not race_data["languages_bonus"]:
                    # Basit pattern: "speaking X" veya "X, Y, and Z"
                    speaking_match = re.search(r'(?:speaking|speak)\s+([^.]{1,100})', lang_content, re.IGNORECASE)
                    if speaking_match:
                        speaking_text = speaking_match.group(1)
                        # Virgülle veya "and" ile ayrılmış dilleri bul
                        langs = re.split(r'[,;]\s*|\s+and\s+|\s+or\s+', speaking_text)
                        auto_langs = []
                        for lang in langs:
                            lang = lang.strip()
                            # Büyük harfle başlayan, bilinen dil isimleri
                            if lang and len(lang) < 30 and lang[0].isupper():
                                # Bilinen dillere benzer mi kontrol et
                                if any(known.lower() in lang.lower() or lang.lower() in known.lower() 
                                      for known in ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Draconic']):
                                    if lang not in auto_langs:
                                        auto_langs.append(lang)
                        if auto_langs:
                            race_data["languages_automatic"] = auto_langs[:10]
                
                # Genel languages listesi
                race_data["languages"] = race_data["languages_automatic"] + race_data["languages_bonus"][:5]
        
        # RACIAL TRAITS - Düzeltilmiş parsing (Archives of Nethys)
        if "aonprd" in self.base_url:
            # Archives of Nethys'te asıl racial traits <strong> veya <b> etiketlerinde
            # Sadece belirli anahtar kelimeleri içeren trait başlıklarını bul
            racial_trait_keywords = [
                'speed', 'feat', 'skilled', 'vision', 'immunity', 'trait', 'weapon', 'armor', 
                'spell', 'resistance', 'bonus', 'proficiency', 'skill', 'movement', 'racial',
                'low-light', 'darkvision', 'blindsight', 'tremorsense', 'keen senses', 'senses'
            ]
            
            # Genel başlıkları hariç tut (bunlar racial trait değil)
            exclude_keywords = [
                'source', 'languages', 'language', 'physical', 'society', 'relations', 
                'alignment', 'religion', 'adventurers', 'description', 'name', 'size',
                'type', 'subtype', 'favored class', 'racial traits', 'alternate'
            ]
            
            # <strong> ve <b> etiketlerini bul
            strong_tags = soup.find_all(['strong', 'b'])
            for tag in strong_tags:
                trait_name = tag.get_text(strip=True)
                
                # Genel başlıkları atla
                if any(exc.lower() in trait_name.lower() for exc in exclude_keywords):
                    continue
                
                # Trait başlığı mı kontrol et
                is_racial_trait = False
                
                # Anahtar kelime kontrolü
                if any(keyword.lower() in trait_name.lower() for keyword in racial_trait_keywords):
                    is_racial_trait = True
                
                # Kısa başlıklar da trait olabilir (ama uzun olmasın)
                elif len(trait_name) < 30 and len(trait_name) > 2:
                    # Sayı içermeyen, sadece harf içeren başlıklar genellikle trait'tir
                    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', trait_name):
                        # Ama genel başlıkları atla
                        if trait_name.lower() not in exclude_keywords:
                            is_racial_trait = True
                
                if is_racial_trait:
                    # Sonraki içeriği bul
                    trait_content = ""
                    
                    # Parent içindeki içeriği kontrol et
                    parent = tag.find_parent(['p', 'div'])
                    if parent:
                        parent_text = parent.get_text()
                        # Tag'dan sonraki kısmı al
                        parts = parent_text.split(trait_name, 1)
                        if len(parts) > 1:
                            after_trait = parts[1].strip()
                            # ":" işaretinden sonraki ilk cümleyi al
                            if ':' in after_trait:
                                after_trait = after_trait.split(':', 1)[1].strip()
                            # İlk cümleyi al (nokta, yeni satır veya başka trait öncesi)
                            trait_content = re.split(r'[.\n](?=\s*[A-Z])|(?=\n\s*[A-Z][a-z]+\s*:)', after_trait)[0].strip()
                            trait_content = trait_content[:300]  # Maksimum uzunluk
                    
                    # Eğer parent'ta yeterli içerik yoksa, sonraki sibling'i kontrol et
                    if not trait_content or len(trait_content) < 10:
                        next_elem = tag.find_next_sibling(['p', 'div'])
                        if next_elem:
                            if hasattr(next_elem, 'get_text'):
                                trait_text = next_elem.get_text(strip=True)
                                # İlk cümleyi al
                                trait_content = re.split(r'[.\n](?=\s*[A-Z])', trait_text)[0].strip()[:300]
                    
                    # İçerik varsa ve anlamlıysa ekle
                    if trait_content and len(trait_content) > 5 and len(trait_content) < 500:
                        # Duplicate kontrolü ve anlamlılık kontrolü
                        # Çok kısa veya çok genel içerikleri atla
                        # Sınıf isimlerini atla (bunlar favored class bonus, trait değil)
                        if (trait_name not in race_data["traits"] and 
                            len(trait_content) > 10 and
                            not any(exc.lower() in trait_content.lower()[:50] for exc in ['source', 'pg.', 'page']) and
                            trait_name not in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 
                                              'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 
                                              'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                                              'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                                              'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                                              'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']):
                            race_data["traits"].append(trait_name)
                            race_data["traits_detailed"][trait_name] = trait_content[:300]
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - dt/dd yapısı
            dl_tags = soup.find_all('dl')
            for dl in dl_tags:
                dt_tags = dl.find_all('dt')
                for dt in dt_tags:
                    term = dt.get_text(strip=True)
                    dd = dt.find_next_sibling('dd')
                    if dd and term and len(term) < 100:
                        definition = dd.get_text(strip=True)
                        if definition and len(definition) > 10:
                            # Sınıf isimlerini atla (bunlar favored class bonus, trait değil)
                            if term not in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler',
                                          'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter',
                                          'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                                          'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                                          'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                                          'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']:
                                race_data["traits"].append(term)
                                race_data["traits_detailed"][term] = definition[:500]
        
        # VISION - Traits parsing'inden SONRA yapılmalı (vision genellikle bir trait olarak geliyor)
        # Önce traits listesinde vision trait'ini ara - SADECE ASIL RACIAL TRAITS'ten (ilk 5-10 trait)
        # Alternatif traits'i atla (bunlar genellikle sayfanın sonunda gelir)
        core_traits = race_data.get("traits", [])[:10]  # İlk 10 trait'i al (asıl racial traits genellikle başta)
        
        # İlk birkaç trait'in gerçekten asıl racial trait olup olmadığını kontrol et
        # (Medium, Normal Speed, Bonus Feat gibi)
        core_racial_trait_keywords = ['medium', 'small', 'large', 'speed', 'feat', 'skilled', 'vision', 
                                     'immunity', 'magic', 'resistance', 'weapon', 'armor', 'movement']
        
        # Eğer ilk trait'lerde bu anahtar kelimeler varsa, bunlar asıl traits'tir
        # Alternatif traits genellikle bu anahtar kelimeleri içermez veya daha sonra gelir
        for trait_name in core_traits:
            trait_name_lower = trait_name.lower()
            
            # Alternatif trait kontrolü - eğer trait ismi bir sınıf ismi gibi görünüyorsa (Alchemist, Bard, etc.)
            # veya çok uzunsa, bu alternatif trait olabilir
            if (trait_name in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 'Cavalier',
                              'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 'Inquisitor', 'Investigator',
                              'Kineticist', 'Magus', 'Mesmerist', 'Monk', 'Occultist', 'Oracle', 'Paladin',
                              'Psychic', 'Ranger', 'Rogue', 'Shaman', 'Shifter', 'Skald', 'Slayer', 'Sorcerer',
                              'Spiritualist', 'Summoner', 'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']):
                continue  # Bu bir favored class bonus, trait değil
            
            # Vision trait'ini ara
            if 'low-light' in trait_name_lower or ('vision' in trait_name_lower and 'low' in trait_name_lower):
                # Ama bu trait'in alternate trait olmadığından emin ol
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                # Eğer trait detail "replaces" içeriyorsa, bu alternatif trait'tir, atla
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                race_data["vision"] = "low-light"
                race_data["vision_range"] = 0
                break
            elif 'darkvision' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                # Alternate trait kontrolü
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "darkvision"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 60
                break
            elif 'blindsight' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "blindsight"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                break
            elif 'tremorsense' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "tremorsense"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                break
        
        # Eğer traits listesinde bulunamadıysa, <strong> tag'lerinde direkt ara (backup)
        if race_data["vision"] == "normal":
            vision_strong = soup.find(['strong', 'b'], string=re.compile(r'^(?:Low-light\s+Vision|Darkvision|Blindsight|Tremorsense)$', re.I))
            if vision_strong:
                vision_text = vision_strong.get_text(strip=True)
                parent = vision_strong.find_parent(['p', 'div'])
                if parent:
                    parent_text = parent.get_text()
                    # "Alternate" veya "variant" kelimesi varsa, bu alternate trait'tir, atla
                    if not re.search(r'alternate|variant|optional', parent_text[:200], re.IGNORECASE):
                        if 'Darkvision' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "darkvision"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 60
                        elif 'Low-light' in vision_text:
                            race_data["vision"] = "low-light"
                            race_data["vision_range"] = 0
                        elif 'Blindsight' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "blindsight"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                        elif 'Tremorsense' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "tremorsense"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
        
        # FAVORED CLASS - Düzeltilmiş parsing
        # Favored class genellikle "Favored Class: Any" veya belirli class'lar şeklinde
        favored_patterns = [
            r'Favored\s+Class\s*:?\s*([^\n]+?)(?:\n|$)',
            r'Favored\s+Classes?\s*:?\s*([^\n]+?)(?:\n|$)',
        ]
        
        favored_text = ""
        for pattern in favored_patterns:
            favored_match = re.search(pattern, full_text, re.IGNORECASE)
            if favored_match:
                favored_text = favored_match.group(1).strip()
                break
        
        # Eğer regex ile bulunamadıysa, <strong>Favored Class</strong> etiketini ara
        if not favored_text:
            favored_strong = soup.find(['strong', 'b'], string=re.compile(r'^Favored\s+Class', re.I))
            if favored_strong:
                parent = favored_strong.find_parent(['p', 'div'])
                if parent:
                    parent_text = parent.get_text()
                    # "Favored Class" başlığından sonraki içeriği al
                    parts = parent_text.split(favored_strong.get_text(strip=True), 1)
                    if len(parts) > 1:
                        favored_text = parts[1].strip().split('\n')[0].strip()[:200]
        
        if favored_text:
            race_data["favored_class_bonus"] = favored_text[:200]
            
            # Favored class'ları ayır
            # "Any" ise tüm sınıflar
            if 'any' in favored_text.lower():
                race_data["favored_classes"] = ["Any"]
            else:
                # Belirli sınıf isimlerini bul
                known_classes = ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 
                               'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 
                               'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                               'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                               'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                               'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']
                
                found_classes = []
                for class_name in known_classes:
                    if class_name.lower() in favored_text.lower():
                        found_classes.append(class_name)
                
                if found_classes:
                    race_data["favored_classes"] = found_classes
                else:
                    # Virgülle ayrılmış sınıf isimlerini dene
                    classes = [c.strip() for c in re.split(r'[,;]', favored_text) if c.strip() and len(c.strip()) < 30]
                    race_data["favored_classes"] = classes[:10]
        
        # SPELL RESISTANCE
        sr_match = re.search(r'Spell\s+Resistance\s*:?\s*(\d+)', full_text, re.IGNORECASE)
        if sr_match:
            race_data["spell_resistance"] = int(sr_match.group(1))
        
        # DESCRIPTION - Düzeltilmiş parsing
        # Önce meta description tag'ini kontrol et (genellikle orada olur)
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc and meta_desc.get('content'):
            desc_content = meta_desc.get('content', '').strip()
            if len(desc_content) > 100:
                # HTML entity'leri temizle
                desc_content = desc_content.replace('&lt;br /&gt;', ' ').replace('&quot;', '"').replace('&amp;', '&')
                desc_content = re.sub(r'<[^>]+>', '', desc_content)  # HTML tag'lerini temizle
                # İlk cümleyi al (genellikle en önemli kısım)
                first_sentence = re.split(r'[.\n]', desc_content)[0].strip()
                if len(first_sentence) > 50:
                    race_data["description"] = first_sentence[:500]
                else:
                    race_data["description"] = desc_content[:500]
        
        # Eğer meta tag'de bulunamadıysa, başlıktan sonraki ilk paragrafı bul
        if not race_data["description"]:
            # H1 başlığını bul
            h1 = soup.find('h1', class_='title') or soup.find('h1')
            if h1:
                # Başlıktan sonraki ilk anlamlı paragrafı bul
                current = h1.find_next(['p', 'div'])
                count = 0
                while current and count < 5:
                    if hasattr(current, 'get_text'):
                        text = current.get_text(strip=True)
                        # Uzun ve anlamlı bir paragraf mı kontrol et
                        if (len(text) > 100 and 
                            not any(keyword in text.lower() for keyword in ['source', 'pg.', 'page', 'inner sea races', 'advanced race guide', 'core rulebook']) and
                            not re.match(r'^[A-Z][a-z]+\s+Source', text) and
                            'possess' in text.lower() or 'are' in text.lower() or 'have' in text.lower()):
                            # İlk cümleyi al
                            first_sentence = re.split(r'[.\n](?=\s*[A-Z])', text)[0].strip()
                            if len(first_sentence) > 50:
                                race_data["description"] = first_sentence[:500]
                            else:
                                race_data["description"] = text[:500]
                            break
                    current = current.find_next(['p', 'div'])
                    count += 1
        
        # Eğer hala bulunamadıysa, tüm paragrafları tara
        if not race_data["description"]:
            desc_paragraphs = soup.find_all('p')
            for p in desc_paragraphs[:15]:
                text = p.get_text(strip=True)
                # "possess", "are", "have" gibi kelimeler içeren, uzun paragraflar genellikle description'dur
                if (len(text) > 150 and 
                    not any(keyword in text.lower() for keyword in ['source', 'pg.', 'page', 'inner sea races', 'advanced race guide', 'core rulebook']) and
                    not re.match(r'^[A-Z][a-z]+\s+Source', text) and
                    any(keyword in text.lower() for keyword in ['possess', 'are currently', 'have', 'characterized', 'society', 'culture'])):
                    # İlk cümleyi al
                    first_sentence = re.split(r'[.\n](?=\s*[A-Z])', text)[0].strip()
                    if len(first_sentence) > 50:
                        race_data["description"] = first_sentence[:500]
                    else:
                        race_data["description"] = text[:500]
                    break
        
        return race_data
    
    def _parse_race_from_section(self, section) -> Optional[Dict[str, Any]]:
        """HTML section'dan ırk verisini parse et"""
        # d20pfsrd için özel parsing
        race_data = {
            "ability_score_increase": {},
            "speed": 30,
            "traits": [],
            "languages": [],
            "size": "Medium"
        }
        
        text = section.get_text()
        
        # Ability scores
        matches = re.findall(r'\+(\d+)\s+(\w+)', text)
        for bonus, ability in matches:
            ability_lower = ability.lower()
            if ability_lower in ["str", "strength"]:
                race_data["ability_score_increase"]["strength"] = int(bonus)
            elif ability_lower in ["dex", "dexterity"]:
                race_data["ability_score_increase"]["dexterity"] = int(bonus)
        
        return race_data
    
    def scrape_classes(self) -> Dict[str, Any]:
        """Tüm sınıfları çek"""
        print("⚔️ Sınıflar çekiliyor...")
        classes = {}
        
        # Site yapısına göre parse et
        if "aonprd" in self.base_url:
            # Archives of Nethys - Ana sayfadan tüm sınıfları çek
            soup = self._get(self.site_config["classes_url"])
            if soup:
                # ClassDisplay.aspx linklerini bul (ClassesDisplay değil, ClassDisplay!)
                class_links = soup.find_all('a', href=re.compile(r'ClassDisplay\.aspx\?ItemName='))
                # Ayrıca ClassesDisplay pattern'ini de kontrol et
                if not class_links:
                    class_links = soup.find_all('a', href=re.compile(r'ClassesDisplay\.aspx\?ItemName='))
                # Son çare: href'inde Class geçen ve Display geçen linkler
                if not class_links:
                    all_links = soup.find_all('a', href=True)
                    class_links = [l for l in all_links if 'Class' in l.get('href', '') and 'Display' in l.get('href', '')]
                
                for link in class_links:
                    class_name = link.get_text(strip=True)
                    if class_name and class_name not in classes and len(class_name) > 2:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        class_data = self._scrape_class_detail(href)
                        if class_data:
                            classes[class_name] = class_data
                            print(f"  ✓ {class_name}")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - /classes/ altındaki linkleri bul
            soup = self._get(self.site_config["classes_url"])
            if soup:
                # /classes/core-classes/ veya /classes/base-classes/ gibi linkleri bul
                class_links = soup.find_all('a', href=re.compile(r'/classes/[^/]+/[^/]+$'))
                seen_classes = set()
                for link in class_links:
                    href = link.get('href', '')
                    class_name = link.get_text(strip=True)
                    if href and href not in seen_classes and class_name:
                        seen_classes.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        class_data = self._scrape_class_detail(href)
                        if class_data:
                            classes[class_name] = class_data
                            print(f"  ✓ {class_name}")
        
        print(f"OK: {len(classes)} sinif cekildi")
        return classes
    
    def _scrape_class_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir sınıfın detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        class_data = {
            "hit_die": "d8",
            "skill_ranks_per_level": 2,
            "class_skills": [],
            "proficiencies": [],
            "spellcasting": False,
            "features": {},
            "source": url
        }
        
        full_text = soup.get_text()
        
        # Hit Die - daha kapsamlı pattern
        hit_die_patterns = [
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Dice[:\s]+d(\d+)',
            r'd(\d+)\s+Hit Die',
        ]
        for pattern in hit_die_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                class_data["hit_die"] = f"d{match.group(1)}"
                break
        
        # Skill Ranks Per Level
        skill_ranks_match = re.search(r'Skill Ranks[:\s]+(\d+)', full_text, re.IGNORECASE)
        if skill_ranks_match:
            class_data["skill_ranks_per_level"] = int(skill_ranks_match.group(1))
        
        # Class Skills - daha iyi parsing
        skills_section = soup.find(string=re.compile(r'Class Skills?', re.I))
        if skills_section:
            parent = skills_section.find_parent()
            # Sonraki paragraf veya liste
            next_elem = parent.find_next(['p', 'ul', 'ol', 'div'])
            if next_elem:
                skills_text = next_elem.get_text()
                # Virgülle ayrılmış skill'leri bul
                skills = [s.strip() for s in re.split(r'[,;]', skills_text) if s.strip() and len(s.strip()) < 30]
                class_data["class_skills"] = skills[:30]  # İlk 30 skill
        
        # Spellcasting - daha kapsamlı kontrol
        spellcasting_indicators = [
            r'Spellcasting',
            r'Spells per Day',
            r'Spell List',
            r'Caster Level',
        ]
        for indicator in spellcasting_indicators:
            if re.search(indicator, full_text, re.IGNORECASE):
                class_data["spellcasting"] = True
                break
        
        # Proficiencies
        prof_section = soup.find(string=re.compile(r'Proficiencies?', re.I))
        if prof_section:
            parent = prof_section.find_parent()
            next_elem = parent.find_next(['p', 'ul', 'ol'])
            if next_elem:
                prof_text = next_elem.get_text()
                proficiencies = [p.strip() for p in re.split(r'[,;]', prof_text) if p.strip()]
                class_data["proficiencies"] = proficiencies[:20]
        
        return class_data
    
    def _parse_class_from_section(self, section) -> Optional[Dict[str, Any]]:
        """HTML section'dan sınıf verisini parse et"""
        class_data = {
            "hit_die": "d8",
            "skill_ranks_per_level": 2,
            "class_skills": [],
            "proficiencies": [],
            "spellcasting": False,
            "features": {}
        }
        
        text = section.get_text()
        
        # Hit Die
        match = re.search(r'd(\d+)', text)
        if match:
            class_data["hit_die"] = f"d{match.group(1)}"
        
        return class_data
    
    def scrape_feats(self) -> Dict[str, Any]:
        """Tüm feat'leri çek"""
        print("⭐ Feat'ler çekiliyor...")
        feats = {}
        
        if "aonprd" in self.base_url:
            # Archives of Nethys - Feats.aspx sayfasından kategorileri çek
            soup = self._get(self.site_config["feats_url"])
            if soup:
                # Önce kategori linklerini bul (Feats.aspx?Category=...)
                category_links = soup.find_all('a', href=re.compile(r'Feats\.aspx\?Category='))
                categories = []
                for link in category_links:
                    href = link.get('href', '')
                    if 'Category=' in href and href not in categories:
                        # Boş kategoriyi atla
                        if href != 'Feats.aspx?Category=':
                            categories.append(href)
                
                print(f"  Bulunan kategori sayısı: {len(categories)}")
                
                # Her kategori sayfasından feat'leri çek
                for category_path in categories:
                    # URL'yi düzelt
                    if category_path.startswith('/'):
                        category_url = urljoin(self.base_url, category_path)
                    elif not category_path.startswith('http'):
                        category_url = urljoin(self.base_url + '/', category_path)
                    else:
                        category_url = category_path
                    
                    cat_soup = self._get(category_url)
                    if cat_soup:
                        # FeatsDisplay.aspx linklerini bul
                        feat_links = cat_soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx\?ItemName='))
                        for link in feat_links:
                            feat_name = link.get_text(strip=True)
                            if feat_name and feat_name not in feats and len(feat_name) > 1:
                                href = link.get('href', '')
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                feat_data = self._scrape_feat_detail(href)
                                if feat_data:
                                    feats[feat_name] = feat_data
                                    if len(feats) % 50 == 0:
                                        print(f"  ... {len(feats)} feat çekildi")
                
                # Ana sayfadan da direkt linkleri kontrol et (eğer varsa)
                feat_links = soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx\?ItemName='))
                for link in feat_links:
                    feat_name = link.get_text(strip=True)
                    if feat_name and feat_name not in feats:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        feat_data = self._scrape_feat_detail(href)
                        if feat_data:
                            feats[feat_name] = feat_data
                            if len(feats) % 50 == 0:
                                print(f"  ... {len(feats)} feat çekildi")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd - /feats/ altındaki linkleri bul
            soup = self._get(self.site_config["feats_url"])
            if soup:
                # /feats/ altındaki linkleri bul
                feat_links = soup.find_all('a', href=re.compile(r'/feats/[^/]+/[^/]+$'))
                seen_feats = set()
                for link in feat_links:
                    href = link.get('href', '')
                    feat_name = link.get_text(strip=True)
                    if href and href not in seen_feats and feat_name:
                        seen_feats.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        feat_data = self._scrape_feat_detail(href)
                        if feat_data:
                            feats[feat_name] = feat_data
                            if len(feats) % 10 == 0:
                                print(f"  ... {len(feats)} feat çekildi")
        
        print(f"OK: {len(feats)} feat cekildi")
        return feats
    
    def _scrape_feat_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir feat'in detay sayfasını çek"""
        if not url:
            return None
        
        soup = self._get(url)
        if not soup:
            return None
        
        feat_data = {
            "prerequisites": [],
            "benefit": "",
            "normal": "",
            "special": ""
        }
        
        # Prerequisites
        prereq_section = soup.find(string=re.compile(r'Prerequisite', re.I))
        if prereq_section:
            parent = prereq_section.find_parent()
            if parent:
                text = parent.get_text()
                feat_data["prerequisites"] = [t.strip() for t in text.split(',')]
        
        # Benefit
        benefit_section = soup.find(string=re.compile(r'Benefit', re.I))
        if benefit_section:
            parent = benefit_section.find_parent()
            if parent:
                feat_data["benefit"] = parent.get_text(strip=True)
        
        return feat_data
    
    def scrape_spells(self, max_spells: int = 500) -> Dict[str, Any]:
        """Büyüleri çek (max_spells ile limit)"""
        print(f"Spells cekiliyor (max {max_spells})...")
        spells = {}
        
        if "aonprd" in self.base_url:
            # Archives of Nethys - "All Spells" sayfasındaki tablodan çek
            all_spells_url = urljoin(self.base_url, "Spells.aspx?Class=All")
            all_soup = self._get(all_spells_url)
            
            if all_soup:
                # Tablo içindeki linkleri bul
                tables = all_soup.find_all('table')
                spell_links = []
                
                for table in tables:
                    # Tablo içindeki tüm linkleri bul
                    table_links = table.find_all('a', href=True)
                    # SpellsDisplay içeren veya spell içeren linkleri filtrele
                    for link in table_links:
                        href = link.get('href', '')
                        if 'SpellsDisplay' in href or ('Spell' in href and 'ItemName=' in href):
                            spell_links.append(link)
                
                # Eğer tablo içinde bulamadıysak, tüm sayfada ara
                if not spell_links:
                    spell_links = all_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx\?ItemName='))
                
                print(f"  'All Spells' sayfasında {len(spell_links)} büyü linki bulundu")
                
                for link in spell_links:
                    if len(spells) >= max_spells:
                        break
                    spell_name = link.get_text(strip=True)
                    if spell_name and spell_name not in spells and len(spell_name) > 1:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        spell_data = self._scrape_spell_detail(href)
                        if spell_data:
                            spells[spell_name] = spell_data
                            if len(spells) % 50 == 0:
                                print(f"  ... {len(spells)} büyü çekildi")
                
                # Eğer yeterli büyü çekilmediyse, diğer sınıf sayfalarını kontrol et
                if len(spells) < max_spells:
                    # Ana sayfadan sınıf linklerini bul
                    class_links = all_soup.find_all('a', href=re.compile(r'Spells\.aspx\?Class='))
                    seen_classes = set()
                    
                    for link in class_links:
                        if len(spells) >= max_spells:
                            break
                        
                        href = link.get('href', '')
                        if href and 'Class=' in href and href not in seen_classes:
                            seen_classes.add(href)
                            
                            if not href.startswith('http'):
                                category_url = urljoin(self.base_url, href)
                            else:
                                category_url = href
                            
                            cat_soup = self._get(category_url)
                            if cat_soup:
                                spell_links = cat_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx\?ItemName='))
                                for link in spell_links:
                                    if len(spells) >= max_spells:
                                        break
                                    spell_name = link.get_text(strip=True)
                                    if spell_name and spell_name not in spells:
                                        href = link.get('href', '')
                                        if not href.startswith('http'):
                                            href = urljoin(self.base_url, href)
                                        spell_data = self._scrape_spell_detail(href)
                                        if spell_data:
                                            spells[spell_name] = spell_data
                                            if len(spells) % 50 == 0:
                                                print(f"  ... {len(spells)} büyü çekildi")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd - /magic/all-spells/ sayfası + A-Z alt sayfalarından çek
            spells_list_url = urljoin(self.base_url, "/magic/all-spells/")
            soup = self._get(spells_list_url)
            
            if soup:
                seen_spells = set()
                letter_pages = set()
                
                # A-Z alt sayfalarını bul (örn: /magic/all-spells/a/)
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if re.match(r'/magic/all-spells/[a-z0-9-]+/?$', href) and href != "/magic/all-spells/":
                        letter_pages.add(href)
                
                if not letter_pages:
                    letter_pages.add("/magic/all-spells/")
                
                print(f"  {len(letter_pages)} harf/alt sayfa bulundu")
                
                for letter_href in sorted(letter_pages):
                    if len(spells) >= max_spells:
                        break
                    
                    page_url = urljoin(self.base_url, letter_href)
                    letter_soup = self._get(page_url)
                    if not letter_soup:
                        continue
                    
                    # Spell linkleri: /magic/all-spells/a/acid-arrow/
                    spell_links = letter_soup.find_all(
                        'a',
                        href=re.compile(r'/magic/all-spells/[a-z0-9-]+/.+/$', re.IGNORECASE)
                    )
                    print(f"  {letter_href}: {len(spell_links)} potansiyel büyü linki")
                    
                    for link in spell_links:
                        if len(spells) >= max_spells:
                            break
                        
                        href = link.get('href', '')
                        spell_name = link.get_text(strip=True)
                        
                        if href and href not in seen_spells and spell_name and len(spell_name) > 2:
                            seen_spells.add(href)
                            if not href.startswith('http'):
                                href = urljoin(self.base_url, href)
                            
                            spell_data = self._scrape_spell_detail(href)
                            if spell_data:
                                spells[spell_name] = spell_data
                                if len(spells) % 50 == 0:
                                    print(f"  ... {len(spells)} büyü çekildi")
        
        print(f"OK: {len(spells)} spell cekildi")
        return spells
    
    def _scrape_spell_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir büyünün detay sayfasını çek - GELİŞTİRİLMİŞ VERSİYON"""
        if not url:
            return None
        
        soup = self._get(url)
        if not soup:
            return None
        
        spell_data = {
            "level": 0,
            "levels_by_class": {},  # {"Wizard": 1, "Cleric": 2, ...}
            "school": "",
            "subschool": "",
            "descriptor": "",
            "casting_time": "",
            "components": "",
            "material_components": "",
            "focus": "",
            "range": "",
            "area": "",
            "target": "",
            "effect": "",
            "duration": "",
            "saving_throw": "",
            "spell_resistance": "",
            "description": "",
            "source": url
        }
        
        # Tüm metni al
        full_text = soup.get_text()
        
        # Ana içerik alanını bul
        main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
        if main_content:
            full_text = main_content.get_text()
        
        # LEVEL - IYILESTIRILMIS PARSING (Duzeltme: yanlis parse'lar icin)
        # Pattern 1: "Level bard 1, cleric 2, wizard 1"
        level_pattern = re.search(r'Level\s+([^;]+?)(?:;|$)', full_text, re.IGNORECASE)
        if level_pattern:
            level_text = level_pattern.group(1)
            # Her sınıf için level'ı bul - sadece geçerli class isimlerini kabul et
            valid_classes = [
                'alchemist', 'arcanist', 'bard', 'cleric', 'druid', 'inquisitor',
                'magus', 'oracle', 'paladin', 'ranger', 'sorcerer', 'summoner',
                'witch', 'wizard', 'antipaladin', 'bloodrager', 'hunter', 'investigator',
                'occultist', 'psychic', 'shaman', 'skald', 'warpriest', 'slayer',
                'swashbuckler', 'vigilante', 'brawler', 'cavalier', 'gunslinger',
                'samurai', 'ninja', 'rogue', 'fighter', 'barbarian', 'monk'
            ]
            
            # Pattern: "classname level" veya "classname/classname level"
            class_levels = re.findall(r'(\w+(?:/\w+)?)\s+(\d+)', level_text, re.IGNORECASE)
            for class_name, level in class_levels:
                # Class name'i normalize et ve kontrol et
                class_name_lower = class_name.lower().split('/')[0]  # "sorcerer/wizard" -> "sorcerer"
                if class_name_lower in valid_classes:
                    # Eğer "/" içeriyorsa, her iki class'a da ekle
                    if '/' in class_name:
                        for c in class_name.split('/'):
                            c_clean = c.strip().lower()
                            if c_clean in valid_classes:
                                spell_data["levels_by_class"][c.strip().capitalize()] = int(level)
                    else:
                        spell_data["levels_by_class"][class_name.capitalize()] = int(level)
            
            # İlk geçerli level'ı genel level olarak kullan
            if spell_data["levels_by_class"]:
                spell_data["level"] = list(spell_data["levels_by_class"].values())[0]
        
        # SCHOOL
        school_patterns = [
            r'School\s+([^;]+?)(?:;|$)',
            r'(\w+)\s+\[([^\]]+)\]',  # "Evocation [fire]"
        ]
        for pattern in school_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                school_text = match.group(1).strip()
                # School ve subschool'u ayır
                if '[' in school_text:
                    parts = school_text.split('[')
                    spell_data["school"] = parts[0].strip()
                    if len(parts) > 1:
                        spell_data["subschool"] = parts[1].replace(']', '').strip()
                else:
                    spell_data["school"] = school_text
                break
        
        # CASTING TIME - IYILESTIRILMIS PARSING (Duzeltme: "actionComponents" gibi birlestik metinler icin)
        # Pattern: "Casting Time" veya "1 standard actionComponents" gibi birlestik metin
        casting_patterns = [
            r'Casting Time\s+([^C]+?)(?:Components?|Effect|Range|Target|Area|Duration|$)',  # Components'ten once dur
            r'(?:^|\s)(\d+\s+(?:standard|move|full-round|swift|immediate|free)\s+action[^CEARTDS]*?)(?:Components?|Effect|Range|Target|Area|Duration|$)',  # Direkt action pattern
        ]
        for pattern in casting_patterns:
            casting_match = re.search(pattern, full_text, re.IGNORECASE)
            if casting_match:
                ct_text = casting_match.group(1).strip()
                # "action" kelimesinden sonra gelen harfleri temizle (örn: "actionComponents" -> "action")
                ct_text = re.sub(r'(action)[A-Z].*', r'\1', ct_text)
                spell_data["casting_time"] = ct_text
                break
        
        # COMPONENTS - IYILESTIRILMIS PARSING
        # Pattern: "Components V, S, DF" veya "V, S, DFEffect" gibi birlestik metin
        components_patterns = [
            r'Components?\s+([^EARTDS]+?)(?:Effect|Range|Target|Area|Duration|Saving|Spell|$)',  # Effect/Range/Target/Area/Duration'dan once dur
            r'(?:Components?\s+|^)([VSMDF,\s]+?)(?:Effect|Range|Target|Area|Duration|Saving|Spell|$)',  # Direkt V, S, M, D, F pattern
        ]
        for pattern in components_patterns:
            components_match = re.search(pattern, full_text, re.IGNORECASE)
            if components_match:
                comp_text = components_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "DFEffect" -> "DF")
                comp_text = re.sub(r'([VSMDF,\s]+?)([A-Z][a-z]+)', r'\1', comp_text)
                spell_data["components"] = comp_text
                
                # Material components'i ayir
                if 'M' in comp_text or 'material' in comp_text.lower():
                    material_match = re.search(r'M[,\s]*\(([^)]+)\)', comp_text, re.IGNORECASE)
                    if material_match:
                        spell_data["material_components"] = material_match.group(1).strip()
                
                # Focus'u ayir
                if 'F' in comp_text or 'focus' in comp_text.lower():
                    focus_match = re.search(r'F[,\s]*\(([^)]+)\)', comp_text, re.IGNORECASE)
                    if focus_match:
                        spell_data["focus"] = focus_match.group(1).strip()
                break
        
        # RANGE - IYILESTIRILMIS PARSING
        # Pattern: "Range touchTarget" gibi birlestik metin
        range_patterns = [
            r'Range\s+([^TEDAS]+?)(?:Target|Effect|Area|Duration|Saving|Spell|Description|$)',  # Target/Effect/Area/Duration'dan once dur
            r'(?:Range\s+|^)(touch|close|medium|long|unlimited|personal|see text|[0-9]+[^TEDAS]*?)(?:Target|Effect|Area|Duration|Saving|Spell|$)',  # Direkt range pattern
        ]
        for pattern in range_patterns:
            range_match = re.search(pattern, full_text, re.IGNORECASE)
            if range_match:
                range_text = range_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "touchTarget" -> "touch")
                range_text = re.sub(r'([a-z]+)([A-Z][a-z]+)', r'\1', range_text)
                spell_data["range"] = range_text
                break
        
        # AREA / TARGET / EFFECT - IYILESTIRILMIS PARSING
        target_patterns = [
            r'Target\s+([^EDAS]+?)(?:Effect|Duration|Area|Saving|Spell|Description|$)',  # Effect/Duration/Area'dan once dur
        ]
        for pattern in target_patterns:
            target_match = re.search(pattern, full_text, re.IGNORECASE)
            if target_match:
                target_text = target_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "creature touchedDuration" -> "creature touched")
                target_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', target_text)
                spell_data["target"] = target_text
                break
        
        area_patterns = [
            r'Area\s+([^TEDAS]+?)(?:Target|Effect|Duration|Saving|Spell|Description|$)',  # Target/Effect/Duration'dan once dur
        ]
        for pattern in area_patterns:
            area_match = re.search(pattern, full_text, re.IGNORECASE)
            if area_match:
                area_text = area_match.group(1).strip()
                area_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', area_text)
                spell_data["area"] = area_text
                break
        
        effect_patterns = [
            r'Effect\s+([^TEDAS]+?)(?:Target|Duration|Area|Saving|Spell|Description|$)',  # Target/Duration/Area'dan once dur
        ]
        for pattern in effect_patterns:
            effect_match = re.search(pattern, full_text, re.IGNORECASE)
            if effect_match:
                effect_text = effect_match.group(1).strip()
                effect_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', effect_text)
                spell_data["effect"] = effect_text
                break
        
        # DURATION - IYILESTIRILMIS PARSING
        # Pattern: "Duration 1 min./levelSaving" gibi birlestik metin
        duration_patterns = [
            r'Duration\s+([^STEDAS]+?)(?:Saving|Spell|Target|Effect|Area|Description|$)',  # Saving/Spell/Target/Effect/Area'dan once dur
        ]
        for pattern in duration_patterns:
            duration_match = re.search(pattern, full_text, re.IGNORECASE)
            if duration_match:
                duration_text = duration_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "1 min./levelSaving" -> "1 min./level")
                duration_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', duration_text)
                spell_data["duration"] = duration_text
                break
        
        # SAVING THROW - IYILESTIRILMIS PARSING
        saving_patterns = [
            r'Saving Throw\s+([^STEDAS]+?)(?:Spell|Target|Effect|Duration|Area|Description|$)',  # Spell/Target/Effect/Duration/Area'dan once dur
        ]
        for pattern in saving_patterns:
            saving_match = re.search(pattern, full_text, re.IGNORECASE)
            if saving_match:
                saving_text = saving_match.group(1).strip()
                saving_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', saving_text)
                spell_data["saving_throw"] = saving_text
                break
        
        # SPELL RESISTANCE - IYILESTIRILMIS PARSING
        sr_patterns = [
            r'Spell Resistance\s+([^STEDAS]+?)(?:Description|Target|Effect|Duration|Area|Saving|$)',  # Description/Target/Effect/Duration/Area'dan once dur
        ]
        for pattern in sr_patterns:
            sr_match = re.search(pattern, full_text, re.IGNORECASE)
            if sr_match:
                sr_text = sr_match.group(1).strip()
                sr_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', sr_text)
                spell_data["spell_resistance"] = sr_text
                break
        
        # DESCRIPTION - Daha iyi parsing
        # Önce meta description'ı kontrol et
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            spell_data["description"] = meta_desc.get('content')
        else:
            # Ana içerikten description'ı bul
            desc_section = soup.find('div', class_=re.compile(r'description|text|content', re.I))
            if not desc_section:
                # "Description" başlığından sonraki içeriği bul
                desc_header = soup.find(string=re.compile(r'^Description$', re.I))
                if desc_header:
                    parent = desc_header.find_parent()
                    if parent:
                        next_elem = parent.find_next_sibling(['p', 'div'])
                        if next_elem:
                            desc_section = next_elem
            
            if desc_section:
                desc_text = desc_section.get_text(strip=True)
                # İlk birkaç paragrafı al (çok uzun olmasın)
                paragraphs = desc_text.split('\n\n')[:3]
                spell_data["description"] = '\n\n'.join(paragraphs)
        
        return spell_data
    
    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tüm verileri çek ve birleştir"""
        print(f"Pathfinder 1e verileri cekiliyor ({self.base_url})...")
        print("Bu islem birkac dakika surebilir. Lutfen bekleyin...\n")
        
        data = {
            "system": "PATHFINDER_1E",
            "races": self.scrape_races(),
            "classes": self.scrape_classes(),
            "feats": self.scrape_feats(),
            "spells": self.scrape_spells(),
            "items": {}  # Ekipman için ayrı bir fonksiyon eklenebilir
        }
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\nOK: Veriler kaydedildi: {output_file}")
        
        return data


def _merge_dict_deep(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    İki dict'i derinlemesine birleştir (recursive merge).
    Primary önceliklidir, secondary eksikleri tamamlar.
    
    Args:
        primary: Birincil dict (öncelikli)
        secondary: İkincil dict (tamamlayıcı)
    
    Returns:
        Birleştirilmiş dict
    """
    result = primary.copy()
    
    for key, value in secondary.items():
        if key not in result:
            # Yeni key, direkt ekle
            result[key] = value
        else:
            # Var olan key, merge et
            existing = result[key]
            
            if isinstance(value, dict) and isinstance(existing, dict):
                # Nested dict'leri recursive merge et
                result[key] = _merge_dict_deep(existing, value)
            elif isinstance(value, list) and isinstance(existing, list):
                # Listeleri birleştir (duplicate'leri kaldırarak)
                merged_list = existing.copy()
                for item in value:
                    if item not in merged_list:
                        merged_list.append(item)
                result[key] = merged_list
            elif not existing or existing == "" or existing == [] or existing == {}:
                # Primary'de boş/eksik, secondary'den doldur
                result[key] = value
            elif isinstance(value, str) and isinstance(existing, str):
                # String'ler için: daha uzun veya daha detaylı olanı seç
                if len(value) > len(existing) * 1.2:  # %20 daha uzunsa
                    result[key] = value
                # Aksi halde primary'deki kalır
    
    return result


def _merge_category_data(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bir kategori için (örneğin races, classes) iki veri setini birleştir.
    Primary önceliklidir, secondary eksikleri tamamlar.
    
    Args:
        primary: Birincil kategori verisi (öncelikli)
        secondary: İkincil kategori verisi (tamamlayıcı)
    
    Returns:
        Birleştirilmiş kategori verisi
    """
    merged = {}
    
    # Primary'den tüm öğeleri al
    merged.update(primary)
    
    # Secondary'den eksik öğeleri ekle veya mevcut olanları geliştir
    for key, value in secondary.items():
        if key not in merged:
            # Yeni öğe, direkt ekle
            merged[key] = value
        else:
            # Var olan öğe, derinlemesine merge et
            existing = merged[key]
            if isinstance(value, dict) and isinstance(existing, dict):
                merged[key] = _merge_dict_deep(existing, value)
            elif isinstance(value, list) and isinstance(existing, list):
                # Listeleri birleştir (duplicate'leri kaldırarak)
                merged_list = existing.copy()
                for item in value:
                    if item not in merged_list:
                        merged_list.append(item)
                merged[key] = merged_list
            elif not existing or existing == "" or existing == [] or existing == {}:
                # Primary'de boş/eksik, secondary'den doldur
                merged[key] = value
    
    return merged


def scrape_pathfinder_data(site: str = "aonprd", output_dir: Path = None, merge_sites: bool = False) -> Path:
    """
    Pathfinder 1e verilerini çek ve kaydet
    
    Args:
        site: Kullanılacak site ("aonprd" veya "d20pfsrd") veya "both" (her ikisi)
        output_dir: Çıktı dizini (None ise data/ klasörü)
        merge_sites: True ise her iki siteden de veri çekip birleştir
    
    Returns:
        Kaydedilen JSON dosyasının yolu
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[1] / "data"
    
    output_file = output_dir / "pathfinder_1e_data.json"
    
    if merge_sites or site == "both":
        # Her iki siteden de veri çek ve birleştir
        print("🔄 Her iki siteden veri çekiliyor ve birleştiriliyor...\n")
        
        # Önce Archives of Nethys'ten çek (daha resmi)
        print("=" * 60)
        print("📚 1. Archives of Nethys (aonprd.com)")
        print("=" * 60)
        scraper_aon = PathfinderScraper(site="aonprd")
        data_aon = scraper_aon.scrape_all(output_file=None)
        
        print("\n" + "=" * 60)
        print("📚 2. d20pfsrd.com")
        print("=" * 60)
        scraper_d20 = PathfinderScraper(site="d20pfsrd")
        data_d20 = scraper_d20.scrape_all(output_file=None)
        
        # Verileri birleştir (aonprd öncelikli)
        print("\n" + "=" * 60)
        print("🔗 Veriler birleştiriliyor...")
        print("=" * 60)
        
        # Her kategori için birleştirme yap
        merged_races = _merge_category_data(data_aon.get("races", {}), data_d20.get("races", {}))
        merged_classes = _merge_category_data(data_aon.get("classes", {}), data_d20.get("classes", {}))
        merged_feats = _merge_category_data(data_aon.get("feats", {}), data_d20.get("feats", {}))
        merged_spells = _merge_category_data(data_aon.get("spells", {}), data_d20.get("spells", {}))
        merged_items = _merge_category_data(data_aon.get("items", {}), data_d20.get("items", {}))
        
        merged_data = {
            "system": "PATHFINDER_1E",
            "source": "merged (aonprd + d20pfsrd)",
            "races": merged_races,
            "classes": merged_classes,
            "feats": merged_feats,
            "spells": merged_spells,
            "items": merged_items
        }
        
        # İstatistikler
        print(f"\n📊 Birleştirme İstatistikleri:")
        print(f"   Irklar: {len(merged_data['races'])} (aonprd: {len(data_aon.get('races', {}))}, d20pfsrd: {len(data_d20.get('races', {}))})")
        print(f"   Sınıflar: {len(merged_data['classes'])} (aonprd: {len(data_aon.get('classes', {}))}, d20pfsrd: {len(data_d20.get('classes', {}))})")
        print(f"   Feat'ler: {len(merged_data['feats'])} (aonprd: {len(data_aon.get('feats', {}))}, d20pfsrd: {len(data_d20.get('feats', {}))})")
        print(f"   Büyüler: {len(merged_data['spells'])} (aonprd: {len(data_aon.get('spells', {}))}, d20pfsrd: {len(data_d20.get('spells', {}))})")
        
        # Kaydet
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"\nOK: Birlestirilmis veriler kaydedildi: {output_file}")
        
    else:
        # Tek siteden çek
        scraper = PathfinderScraper(site=site)
        scraper.scrape_all(output_file=output_file)
    
    return output_file


if __name__ == "__main__":
    # Test için
    import sys
    site = sys.argv[1] if len(sys.argv) > 1 else "aonprd"
    print(f"Test: {site} sitesinden veri çekiliyor...")
    scrape_pathfinder_data(site=site)


Sınıflar, ırklar, feat'ler, büyüler ve diğer kuralları web'den çeker.
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class PathfinderScraper:
    """Pathfinder 1e verilerini web'den çeken scraper"""
    
    # Desteklenen siteler
    SITES = {
        "aonprd": {
            "base_url": "https://aonprd.com",
            "races_url": "/Races.aspx",
            "classes_url": "/Classes.aspx",
            "feats_url": "/Feats.aspx",
            "spells_url": "/Spells.aspx",
            "items_url": "/Equipment.aspx"
        },
        "d20pfsrd": {
            "base_url": "https://www.d20pfsrd.com",
            "races_url": "/races/",
            "classes_url": "/classes/",
            "feats_url": "/feats/",
            "spells_url": "/spells/",
            "items_url": "/equipment/"
        }
    }
    
    def __init__(self, site: str = "aonprd", delay: float = 1.0):
        """
        Args:
            site: Kullanılacak site ("aonprd" veya "d20pfsrd")
            delay: İstekler arası bekleme süresi (saniye) - siteyi yormamak için
        """
        if site not in self.SITES:
            raise ValueError(f"Desteklenmeyen site: {site}. Desteklenenler: {list(self.SITES.keys())}")
        
        self.site_config = self.SITES[site]
        self.base_url = self.site_config["base_url"]
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """URL'den HTML içeriğini çek ve BeautifulSoup nesnesi döndür"""
        full_url = urljoin(self.base_url, url) if not url.startswith("http") else url
        
        for attempt in range(retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(full_url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"ERROR: {full_url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_races(self) -> Dict[str, Any]:
        """Tüm ırkları çek"""
        print("🏃 Irklar çekiliyor...")
        races = {}
        
        # Site yapısına göre parse et
        if "aonprd" in self.base_url:
            # Archives of Nethys yapısı - Core ve NonCore kategorilerini çek
            for category in ["Core", "NonCore"]:
                url = f"{self.site_config['races_url']}?Category={category}"
                soup = self._get(url)
                if not soup:
                    continue
                
                # RacesDisplay.aspx linklerini bul (Display değil, RacesDisplay!)
                race_links = soup.find_all('a', href=re.compile(r'RacesDisplay\.aspx\?ItemName='))
                for link in race_links:
                    race_name = link.get_text(strip=True)
                    if race_name and race_name not in races:
                        href = link.get('href', '')
                        # Göreceli URL'yi tam URL'ye çevir
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        race_data = self._scrape_race_detail(href)
                        if race_data:
                            races[race_name] = race_data
                            print(f"  ✓ {race_name}")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - ana sayfadan tüm ırk linklerini bul
            soup = self._get(self.site_config["races_url"])
            if soup:
                # /races/core-races/ veya /races/advanced-races/ gibi linkleri bul
                race_links = soup.find_all('a', href=re.compile(r'/races/[^/]+/[^/]+$'))
                seen_races = set()
                for link in race_links:
                    href = link.get('href', '')
                    race_name = link.get_text(strip=True)
                    # Duplicate'leri önle
                    if href and href not in seen_races and race_name:
                        seen_races.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        race_data = self._scrape_race_detail(href)
                        if race_data:
                            races[race_name] = race_data
                            print(f"  ✓ {race_name}")
        
        print(f"OK: {len(races)} irk cekildi")
        return races
    
    def _scrape_race_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir ırkın detay sayfasını çek - GELİŞTİRİLMİŞ VERSİYON"""
        soup = self._get(url)
        if not soup:
            return None
        
        race_data = {
            "ability_score_increase": {},
            "ability_score_increase_text": "",  # "+2 to One Ability Score" gibi metin
            "speed": 30,
            "speed_special": "",  # "30 feet" veya "30 feet, swim 30 feet" gibi
            "traits": [],  # Trait isimleri ve açıklamaları
            "traits_detailed": {},  # Her trait için detaylı bilgi
            "languages": [],
            "languages_automatic": [],  # Otomatik diller
            "languages_bonus": [],  # Bonus dil seçenekleri
            "size": "Medium",
            "source": url,
            "type": "",  # Humanoid, Outsider, etc.
            "subtype": "",  # Subtype bilgisi
            "favored_class_bonus": "",  # Favored class bonus açıklaması
            "favored_classes": [],  # Favored class'lar
            "vision": "normal",  # normal, low-light, darkvision, etc.
            "vision_range": 0,  # Darkvision range
            "skill_bonuses": {},  # Skill bonusları
            "weapon_proficiencies": [],  # Weapon proficiencies
            "armor_proficiencies": [],  # Armor proficiencies
            "racial_spells": [],  # Racial spell-like abilities
            "spell_resistance": None,  # Spell resistance
            "description": ""  # Irk açıklaması
        }
        
        # Tüm metni al
        full_text = soup.get_text()
        
        # Ana içerik alanını bul
        main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
        if main_content:
            full_text = main_content.get_text()
        
        # ABILITY SCORE INCREASES - Geliştirilmiş parsing
        # Pattern 1: "+2 to One Ability Score" (Human gibi)
        one_ability_pattern = re.search(r'\+(\d+)\s+to\s+One\s+Ability\s+Score', full_text, re.IGNORECASE)
        if one_ability_pattern:
            bonus = int(one_ability_pattern.group(1))
            race_data["ability_score_increase_text"] = f"+{bonus} to One Ability Score"
            race_data["ability_score_increase"] = {"any": bonus}
        
        # Pattern 2: "+2 Str, +2 Con" veya "+2 Strength, +2 Constitution"
        if not race_data["ability_score_increase"]:
            ability_patterns = [
                (r'\+(\d+)\s+(?:Str|Strength)', "strength"),
                (r'\+(\d+)\s+(?:Dex|Dexterity)', "dexterity"),
                (r'\+(\d+)\s+(?:Con|Constitution)', "constitution"),
                (r'\+(\d+)\s+(?:Int|Intelligence)', "intelligence"),
                (r'\+(\d+)\s+(?:Wis|Wisdom)', "wisdom"),
                (r'\+(\d+)\s+(?:Cha|Charisma)', "charisma"),
            ]
            
            for pattern, ability in ability_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    # En yüksek bonus'u al
                    max_bonus = max(int(m) for m in matches)
                    race_data["ability_score_increase"][ability] = max_bonus
                    if not race_data["ability_score_increase_text"]:
                        race_data["ability_score_increase_text"] = f"+{max_bonus} {ability.capitalize()}"
                    else:
                        race_data["ability_score_increase_text"] += f", +{max_bonus} {ability.capitalize()}"
        
        # SIZE
        size_patterns = [
            r'Size\s*:?\s*(\w+)',
            r'(\w+)\s+size',
        ]
        for pattern in size_patterns:
            size_match = re.search(pattern, full_text, re.IGNORECASE)
            if size_match:
                size = size_match.group(1).capitalize()
                if size.lower() in ["small", "medium", "large", "tiny", "diminutive", "fine", "huge", "gargantuan", "colossal"]:
                    race_data["size"] = size
                    break
        
        # SPEED - Geliştirilmiş
        speed_match = re.search(r'Speed\s*:?\s*([^\n]+?)(?:\n|$)', full_text, re.IGNORECASE)
        if speed_match:
            speed_text = speed_match.group(1).strip()
            # Sayısal değeri bul
            speed_num_match = re.search(r'(\d+)', speed_text)
            if speed_num_match:
                race_data["speed"] = int(speed_num_match.group(1))
            race_data["speed_special"] = speed_text[:200]
        
        # LANGUAGES - Düzeltilmiş parsing
        # Archives of Nethys'te Languages genellikle <strong>Languages</strong> şeklinde
        lang_header = soup.find('strong', string=re.compile(r'^Languages?$', re.I))
        if not lang_header:
            lang_header = soup.find('b', string=re.compile(r'^Languages?$', re.I))
        
        if lang_header:
            # Sonraki içeriği bul (aynı veya sonraki p/div)
            lang_content = ""
            
            # Önce parent'ı kontrol et
            parent = lang_header.find_parent(['p', 'div'])
            if parent:
                # Parent içindeki tüm metni al, ama "Languages" başlığını çıkar
                parent_text = parent.get_text()
                lang_content = parent_text.replace(lang_header.get_text(), "").strip()
            
            # Eğer parent'ta yeterli bilgi yoksa, sonraki sibling'leri kontrol et
            if not lang_content or len(lang_content) < 20:
                next_elem = lang_header.find_next_sibling(['p', 'div'])
                if next_elem:
                    lang_content = next_elem.get_text(strip=True)
            
            if lang_content:
                # "Automatic" ve "Bonus" bölümlerini ayır
                auto_match = re.search(r'(?:Automatic|begin play speaking|speak)\s*:?\s*([^.]*?)(?:\.|Bonus|$)', lang_content, re.IGNORECASE | re.DOTALL)
                bonus_match = re.search(r'(?:Bonus\s+Languages?|bonus languages?)\s*:?\s*([^.]*)', lang_content, re.IGNORECASE)
                
                if auto_match:
                    auto_text = auto_match.group(1)
                    # Dil isimlerini ayır (Common, Elven, Draconic, etc.)
                    # Büyük harfle başlayan kelimeleri bul (dil isimleri genellikle büyük harfle başlar)
                    auto_langs = []
                    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', auto_text)
                    known_languages = ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Giant', 'Draconic', 'Gnoll', 
                                     'Halfling', 'Gnome', 'Sylvan', 'Aquan', 'Auran', 'Ignan', 'Terran', 'Celestial',
                                     'Infernal', 'Abyssal', 'Aklo', 'Undercommon', 'Jotun', 'Tengu', 'Varisian',
                                     'Kelish', 'Vudrani', 'Osiriani', 'Tien', 'Taldane', 'Skald', 'Chelish']
                    for word in words:
                        # Bilinen dil isimlerini kontrol et veya benzer olanları bul
                        if any(known in word for known in known_languages) or word in known_languages:
                            if word not in auto_langs:
                                auto_langs.append(word)
                    
                    # Eğer pattern ile bulamadıysak, "speaking X" veya "X and Y" formatını dene
                    if not auto_langs:
                        # "speaking Common and Elven" gibi formatları bul
                        speaking_match = re.search(r'speaking\s+([^.]+)', lang_content, re.IGNORECASE)
                        if speaking_match:
                            speaking_text = speaking_match.group(1)
                            # "and", "or" ile ayrılmış dilleri bul
                            langs = re.split(r'\s+(?:and|or)\s+', speaking_text)
                            for lang in langs:
                                lang = lang.strip()
                                if lang and len(lang) < 30 and lang[0].isupper():
                                    auto_langs.append(lang)
                    
                    race_data["languages_automatic"] = auto_langs[:10]
                
                if bonus_match:
                    bonus_text = bonus_match.group(1)
                    # Bonus dilleri ayır
                    bonus_langs = []
                    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', bonus_text)
                    known_languages = ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Giant', 'Draconic', 'Gnoll',
                                     'Halfling', 'Gnome', 'Sylvan', 'Aquan', 'Auran', 'Ignan', 'Terran']
                    for word in words:
                        if any(known in word for known in known_languages) or word in known_languages:
                            if word not in bonus_langs:
                                bonus_langs.append(word)
                    race_data["languages_bonus"] = bonus_langs[:20]
                
                # Eğer otomatik/bonus bulunamadıysa, genel "Languages" içeriğinden çıkar
                if not race_data["languages_automatic"] and not race_data["languages_bonus"]:
                    # Basit pattern: "speaking X" veya "X, Y, and Z"
                    speaking_match = re.search(r'(?:speaking|speak)\s+([^.]{1,100})', lang_content, re.IGNORECASE)
                    if speaking_match:
                        speaking_text = speaking_match.group(1)
                        # Virgülle veya "and" ile ayrılmış dilleri bul
                        langs = re.split(r'[,;]\s*|\s+and\s+|\s+or\s+', speaking_text)
                        auto_langs = []
                        for lang in langs:
                            lang = lang.strip()
                            # Büyük harfle başlayan, bilinen dil isimleri
                            if lang and len(lang) < 30 and lang[0].isupper():
                                # Bilinen dillere benzer mi kontrol et
                                if any(known.lower() in lang.lower() or lang.lower() in known.lower() 
                                      for known in ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Draconic']):
                                    if lang not in auto_langs:
                                        auto_langs.append(lang)
                        if auto_langs:
                            race_data["languages_automatic"] = auto_langs[:10]
                
                # Genel languages listesi
                race_data["languages"] = race_data["languages_automatic"] + race_data["languages_bonus"][:5]
        
        # RACIAL TRAITS - Düzeltilmiş parsing (Archives of Nethys)
        if "aonprd" in self.base_url:
            # Archives of Nethys'te asıl racial traits <strong> veya <b> etiketlerinde
            # Sadece belirli anahtar kelimeleri içeren trait başlıklarını bul
            racial_trait_keywords = [
                'speed', 'feat', 'skilled', 'vision', 'immunity', 'trait', 'weapon', 'armor', 
                'spell', 'resistance', 'bonus', 'proficiency', 'skill', 'movement', 'racial',
                'low-light', 'darkvision', 'blindsight', 'tremorsense', 'keen senses', 'senses'
            ]
            
            # Genel başlıkları hariç tut (bunlar racial trait değil)
            exclude_keywords = [
                'source', 'languages', 'language', 'physical', 'society', 'relations', 
                'alignment', 'religion', 'adventurers', 'description', 'name', 'size',
                'type', 'subtype', 'favored class', 'racial traits', 'alternate'
            ]
            
            # <strong> ve <b> etiketlerini bul
            strong_tags = soup.find_all(['strong', 'b'])
            for tag in strong_tags:
                trait_name = tag.get_text(strip=True)
                
                # Genel başlıkları atla
                if any(exc.lower() in trait_name.lower() for exc in exclude_keywords):
                    continue
                
                # Trait başlığı mı kontrol et
                is_racial_trait = False
                
                # Anahtar kelime kontrolü
                if any(keyword.lower() in trait_name.lower() for keyword in racial_trait_keywords):
                    is_racial_trait = True
                
                # Kısa başlıklar da trait olabilir (ama uzun olmasın)
                elif len(trait_name) < 30 and len(trait_name) > 2:
                    # Sayı içermeyen, sadece harf içeren başlıklar genellikle trait'tir
                    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', trait_name):
                        # Ama genel başlıkları atla
                        if trait_name.lower() not in exclude_keywords:
                            is_racial_trait = True
                
                if is_racial_trait:
                    # Sonraki içeriği bul
                    trait_content = ""
                    
                    # Parent içindeki içeriği kontrol et
                    parent = tag.find_parent(['p', 'div'])
                    if parent:
                        parent_text = parent.get_text()
                        # Tag'dan sonraki kısmı al
                        parts = parent_text.split(trait_name, 1)
                        if len(parts) > 1:
                            after_trait = parts[1].strip()
                            # ":" işaretinden sonraki ilk cümleyi al
                            if ':' in after_trait:
                                after_trait = after_trait.split(':', 1)[1].strip()
                            # İlk cümleyi al (nokta, yeni satır veya başka trait öncesi)
                            trait_content = re.split(r'[.\n](?=\s*[A-Z])|(?=\n\s*[A-Z][a-z]+\s*:)', after_trait)[0].strip()
                            trait_content = trait_content[:300]  # Maksimum uzunluk
                    
                    # Eğer parent'ta yeterli içerik yoksa, sonraki sibling'i kontrol et
                    if not trait_content or len(trait_content) < 10:
                        next_elem = tag.find_next_sibling(['p', 'div'])
                        if next_elem:
                            if hasattr(next_elem, 'get_text'):
                                trait_text = next_elem.get_text(strip=True)
                                # İlk cümleyi al
                                trait_content = re.split(r'[.\n](?=\s*[A-Z])', trait_text)[0].strip()[:300]
                    
                    # İçerik varsa ve anlamlıysa ekle
                    if trait_content and len(trait_content) > 5 and len(trait_content) < 500:
                        # Duplicate kontrolü ve anlamlılık kontrolü
                        # Çok kısa veya çok genel içerikleri atla
                        # Sınıf isimlerini atla (bunlar favored class bonus, trait değil)
                        if (trait_name not in race_data["traits"] and 
                            len(trait_content) > 10 and
                            not any(exc.lower() in trait_content.lower()[:50] for exc in ['source', 'pg.', 'page']) and
                            trait_name not in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 
                                              'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 
                                              'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                                              'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                                              'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                                              'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']):
                            race_data["traits"].append(trait_name)
                            race_data["traits_detailed"][trait_name] = trait_content[:300]
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - dt/dd yapısı
            dl_tags = soup.find_all('dl')
            for dl in dl_tags:
                dt_tags = dl.find_all('dt')
                for dt in dt_tags:
                    term = dt.get_text(strip=True)
                    dd = dt.find_next_sibling('dd')
                    if dd and term and len(term) < 100:
                        definition = dd.get_text(strip=True)
                        if definition and len(definition) > 10:
                            # Sınıf isimlerini atla (bunlar favored class bonus, trait değil)
                            if term not in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler',
                                          'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter',
                                          'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                                          'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                                          'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                                          'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']:
                                race_data["traits"].append(term)
                                race_data["traits_detailed"][term] = definition[:500]
        
        # VISION - Traits parsing'inden SONRA yapılmalı (vision genellikle bir trait olarak geliyor)
        # Önce traits listesinde vision trait'ini ara - SADECE ASIL RACIAL TRAITS'ten (ilk 5-10 trait)
        # Alternatif traits'i atla (bunlar genellikle sayfanın sonunda gelir)
        core_traits = race_data.get("traits", [])[:10]  # İlk 10 trait'i al (asıl racial traits genellikle başta)
        
        # İlk birkaç trait'in gerçekten asıl racial trait olup olmadığını kontrol et
        # (Medium, Normal Speed, Bonus Feat gibi)
        core_racial_trait_keywords = ['medium', 'small', 'large', 'speed', 'feat', 'skilled', 'vision', 
                                     'immunity', 'magic', 'resistance', 'weapon', 'armor', 'movement']
        
        # Eğer ilk trait'lerde bu anahtar kelimeler varsa, bunlar asıl traits'tir
        # Alternatif traits genellikle bu anahtar kelimeleri içermez veya daha sonra gelir
        for trait_name in core_traits:
            trait_name_lower = trait_name.lower()
            
            # Alternatif trait kontrolü - eğer trait ismi bir sınıf ismi gibi görünüyorsa (Alchemist, Bard, etc.)
            # veya çok uzunsa, bu alternatif trait olabilir
            if (trait_name in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 'Cavalier',
                              'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 'Inquisitor', 'Investigator',
                              'Kineticist', 'Magus', 'Mesmerist', 'Monk', 'Occultist', 'Oracle', 'Paladin',
                              'Psychic', 'Ranger', 'Rogue', 'Shaman', 'Shifter', 'Skald', 'Slayer', 'Sorcerer',
                              'Spiritualist', 'Summoner', 'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']):
                continue  # Bu bir favored class bonus, trait değil
            
            # Vision trait'ini ara
            if 'low-light' in trait_name_lower or ('vision' in trait_name_lower and 'low' in trait_name_lower):
                # Ama bu trait'in alternate trait olmadığından emin ol
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                # Eğer trait detail "replaces" içeriyorsa, bu alternatif trait'tir, atla
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                race_data["vision"] = "low-light"
                race_data["vision_range"] = 0
                break
            elif 'darkvision' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                # Alternate trait kontrolü
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "darkvision"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 60
                break
            elif 'blindsight' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "blindsight"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                break
            elif 'tremorsense' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "tremorsense"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                break
        
        # Eğer traits listesinde bulunamadıysa, <strong> tag'lerinde direkt ara (backup)
        if race_data["vision"] == "normal":
            vision_strong = soup.find(['strong', 'b'], string=re.compile(r'^(?:Low-light\s+Vision|Darkvision|Blindsight|Tremorsense)$', re.I))
            if vision_strong:
                vision_text = vision_strong.get_text(strip=True)
                parent = vision_strong.find_parent(['p', 'div'])
                if parent:
                    parent_text = parent.get_text()
                    # "Alternate" veya "variant" kelimesi varsa, bu alternate trait'tir, atla
                    if not re.search(r'alternate|variant|optional', parent_text[:200], re.IGNORECASE):
                        if 'Darkvision' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "darkvision"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 60
                        elif 'Low-light' in vision_text:
                            race_data["vision"] = "low-light"
                            race_data["vision_range"] = 0
                        elif 'Blindsight' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "blindsight"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                        elif 'Tremorsense' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "tremorsense"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
        
        # FAVORED CLASS - Düzeltilmiş parsing
        # Favored class genellikle "Favored Class: Any" veya belirli class'lar şeklinde
        favored_patterns = [
            r'Favored\s+Class\s*:?\s*([^\n]+?)(?:\n|$)',
            r'Favored\s+Classes?\s*:?\s*([^\n]+?)(?:\n|$)',
        ]
        
        favored_text = ""
        for pattern in favored_patterns:
            favored_match = re.search(pattern, full_text, re.IGNORECASE)
            if favored_match:
                favored_text = favored_match.group(1).strip()
                break
        
        # Eğer regex ile bulunamadıysa, <strong>Favored Class</strong> etiketini ara
        if not favored_text:
            favored_strong = soup.find(['strong', 'b'], string=re.compile(r'^Favored\s+Class', re.I))
            if favored_strong:
                parent = favored_strong.find_parent(['p', 'div'])
                if parent:
                    parent_text = parent.get_text()
                    # "Favored Class" başlığından sonraki içeriği al
                    parts = parent_text.split(favored_strong.get_text(strip=True), 1)
                    if len(parts) > 1:
                        favored_text = parts[1].strip().split('\n')[0].strip()[:200]
        
        if favored_text:
            race_data["favored_class_bonus"] = favored_text[:200]
            
            # Favored class'ları ayır
            # "Any" ise tüm sınıflar
            if 'any' in favored_text.lower():
                race_data["favored_classes"] = ["Any"]
            else:
                # Belirli sınıf isimlerini bul
                known_classes = ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 
                               'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 
                               'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                               'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                               'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                               'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']
                
                found_classes = []
                for class_name in known_classes:
                    if class_name.lower() in favored_text.lower():
                        found_classes.append(class_name)
                
                if found_classes:
                    race_data["favored_classes"] = found_classes
                else:
                    # Virgülle ayrılmış sınıf isimlerini dene
                    classes = [c.strip() for c in re.split(r'[,;]', favored_text) if c.strip() and len(c.strip()) < 30]
                    race_data["favored_classes"] = classes[:10]
        
        # SPELL RESISTANCE
        sr_match = re.search(r'Spell\s+Resistance\s*:?\s*(\d+)', full_text, re.IGNORECASE)
        if sr_match:
            race_data["spell_resistance"] = int(sr_match.group(1))
        
        # DESCRIPTION - Düzeltilmiş parsing
        # Önce meta description tag'ini kontrol et (genellikle orada olur)
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc and meta_desc.get('content'):
            desc_content = meta_desc.get('content', '').strip()
            if len(desc_content) > 100:
                # HTML entity'leri temizle
                desc_content = desc_content.replace('&lt;br /&gt;', ' ').replace('&quot;', '"').replace('&amp;', '&')
                desc_content = re.sub(r'<[^>]+>', '', desc_content)  # HTML tag'lerini temizle
                # İlk cümleyi al (genellikle en önemli kısım)
                first_sentence = re.split(r'[.\n]', desc_content)[0].strip()
                if len(first_sentence) > 50:
                    race_data["description"] = first_sentence[:500]
                else:
                    race_data["description"] = desc_content[:500]
        
        # Eğer meta tag'de bulunamadıysa, başlıktan sonraki ilk paragrafı bul
        if not race_data["description"]:
            # H1 başlığını bul
            h1 = soup.find('h1', class_='title') or soup.find('h1')
            if h1:
                # Başlıktan sonraki ilk anlamlı paragrafı bul
                current = h1.find_next(['p', 'div'])
                count = 0
                while current and count < 5:
                    if hasattr(current, 'get_text'):
                        text = current.get_text(strip=True)
                        # Uzun ve anlamlı bir paragraf mı kontrol et
                        if (len(text) > 100 and 
                            not any(keyword in text.lower() for keyword in ['source', 'pg.', 'page', 'inner sea races', 'advanced race guide', 'core rulebook']) and
                            not re.match(r'^[A-Z][a-z]+\s+Source', text) and
                            'possess' in text.lower() or 'are' in text.lower() or 'have' in text.lower()):
                            # İlk cümleyi al
                            first_sentence = re.split(r'[.\n](?=\s*[A-Z])', text)[0].strip()
                            if len(first_sentence) > 50:
                                race_data["description"] = first_sentence[:500]
                            else:
                                race_data["description"] = text[:500]
                            break
                    current = current.find_next(['p', 'div'])
                    count += 1
        
        # Eğer hala bulunamadıysa, tüm paragrafları tara
        if not race_data["description"]:
            desc_paragraphs = soup.find_all('p')
            for p in desc_paragraphs[:15]:
                text = p.get_text(strip=True)
                # "possess", "are", "have" gibi kelimeler içeren, uzun paragraflar genellikle description'dur
                if (len(text) > 150 and 
                    not any(keyword in text.lower() for keyword in ['source', 'pg.', 'page', 'inner sea races', 'advanced race guide', 'core rulebook']) and
                    not re.match(r'^[A-Z][a-z]+\s+Source', text) and
                    any(keyword in text.lower() for keyword in ['possess', 'are currently', 'have', 'characterized', 'society', 'culture'])):
                    # İlk cümleyi al
                    first_sentence = re.split(r'[.\n](?=\s*[A-Z])', text)[0].strip()
                    if len(first_sentence) > 50:
                        race_data["description"] = first_sentence[:500]
                    else:
                        race_data["description"] = text[:500]
                    break
        
        return race_data
    
    def _parse_race_from_section(self, section) -> Optional[Dict[str, Any]]:
        """HTML section'dan ırk verisini parse et"""
        # d20pfsrd için özel parsing
        race_data = {
            "ability_score_increase": {},
            "speed": 30,
            "traits": [],
            "languages": [],
            "size": "Medium"
        }
        
        text = section.get_text()
        
        # Ability scores
        matches = re.findall(r'\+(\d+)\s+(\w+)', text)
        for bonus, ability in matches:
            ability_lower = ability.lower()
            if ability_lower in ["str", "strength"]:
                race_data["ability_score_increase"]["strength"] = int(bonus)
            elif ability_lower in ["dex", "dexterity"]:
                race_data["ability_score_increase"]["dexterity"] = int(bonus)
        
        return race_data
    
    def scrape_classes(self) -> Dict[str, Any]:
        """Tüm sınıfları çek"""
        print("⚔️ Sınıflar çekiliyor...")
        classes = {}
        
        # Site yapısına göre parse et
        if "aonprd" in self.base_url:
            # Archives of Nethys - Ana sayfadan tüm sınıfları çek
            soup = self._get(self.site_config["classes_url"])
            if soup:
                # ClassDisplay.aspx linklerini bul (ClassesDisplay değil, ClassDisplay!)
                class_links = soup.find_all('a', href=re.compile(r'ClassDisplay\.aspx\?ItemName='))
                # Ayrıca ClassesDisplay pattern'ini de kontrol et
                if not class_links:
                    class_links = soup.find_all('a', href=re.compile(r'ClassesDisplay\.aspx\?ItemName='))
                # Son çare: href'inde Class geçen ve Display geçen linkler
                if not class_links:
                    all_links = soup.find_all('a', href=True)
                    class_links = [l for l in all_links if 'Class' in l.get('href', '') and 'Display' in l.get('href', '')]
                
                for link in class_links:
                    class_name = link.get_text(strip=True)
                    if class_name and class_name not in classes and len(class_name) > 2:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        class_data = self._scrape_class_detail(href)
                        if class_data:
                            classes[class_name] = class_data
                            print(f"  ✓ {class_name}")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - /classes/ altındaki linkleri bul
            soup = self._get(self.site_config["classes_url"])
            if soup:
                # /classes/core-classes/ veya /classes/base-classes/ gibi linkleri bul
                class_links = soup.find_all('a', href=re.compile(r'/classes/[^/]+/[^/]+$'))
                seen_classes = set()
                for link in class_links:
                    href = link.get('href', '')
                    class_name = link.get_text(strip=True)
                    if href and href not in seen_classes and class_name:
                        seen_classes.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        class_data = self._scrape_class_detail(href)
                        if class_data:
                            classes[class_name] = class_data
                            print(f"  ✓ {class_name}")
        
        print(f"OK: {len(classes)} sinif cekildi")
        return classes
    
    def _scrape_class_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir sınıfın detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        class_data = {
            "hit_die": "d8",
            "skill_ranks_per_level": 2,
            "class_skills": [],
            "proficiencies": [],
            "spellcasting": False,
            "features": {},
            "source": url
        }
        
        full_text = soup.get_text()
        
        # Hit Die - daha kapsamlı pattern
        hit_die_patterns = [
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Dice[:\s]+d(\d+)',
            r'd(\d+)\s+Hit Die',
        ]
        for pattern in hit_die_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                class_data["hit_die"] = f"d{match.group(1)}"
                break
        
        # Skill Ranks Per Level
        skill_ranks_match = re.search(r'Skill Ranks[:\s]+(\d+)', full_text, re.IGNORECASE)
        if skill_ranks_match:
            class_data["skill_ranks_per_level"] = int(skill_ranks_match.group(1))
        
        # Class Skills - daha iyi parsing
        skills_section = soup.find(string=re.compile(r'Class Skills?', re.I))
        if skills_section:
            parent = skills_section.find_parent()
            # Sonraki paragraf veya liste
            next_elem = parent.find_next(['p', 'ul', 'ol', 'div'])
            if next_elem:
                skills_text = next_elem.get_text()
                # Virgülle ayrılmış skill'leri bul
                skills = [s.strip() for s in re.split(r'[,;]', skills_text) if s.strip() and len(s.strip()) < 30]
                class_data["class_skills"] = skills[:30]  # İlk 30 skill
        
        # Spellcasting - daha kapsamlı kontrol
        spellcasting_indicators = [
            r'Spellcasting',
            r'Spells per Day',
            r'Spell List',
            r'Caster Level',
        ]
        for indicator in spellcasting_indicators:
            if re.search(indicator, full_text, re.IGNORECASE):
                class_data["spellcasting"] = True
                break
        
        # Proficiencies
        prof_section = soup.find(string=re.compile(r'Proficiencies?', re.I))
        if prof_section:
            parent = prof_section.find_parent()
            next_elem = parent.find_next(['p', 'ul', 'ol'])
            if next_elem:
                prof_text = next_elem.get_text()
                proficiencies = [p.strip() for p in re.split(r'[,;]', prof_text) if p.strip()]
                class_data["proficiencies"] = proficiencies[:20]
        
        return class_data
    
    def _parse_class_from_section(self, section) -> Optional[Dict[str, Any]]:
        """HTML section'dan sınıf verisini parse et"""
        class_data = {
            "hit_die": "d8",
            "skill_ranks_per_level": 2,
            "class_skills": [],
            "proficiencies": [],
            "spellcasting": False,
            "features": {}
        }
        
        text = section.get_text()
        
        # Hit Die
        match = re.search(r'd(\d+)', text)
        if match:
            class_data["hit_die"] = f"d{match.group(1)}"
        
        return class_data
    
    def scrape_feats(self) -> Dict[str, Any]:
        """Tüm feat'leri çek"""
        print("⭐ Feat'ler çekiliyor...")
        feats = {}
        
        if "aonprd" in self.base_url:
            # Archives of Nethys - Feats.aspx sayfasından kategorileri çek
            soup = self._get(self.site_config["feats_url"])
            if soup:
                # Önce kategori linklerini bul (Feats.aspx?Category=...)
                category_links = soup.find_all('a', href=re.compile(r'Feats\.aspx\?Category='))
                categories = []
                for link in category_links:
                    href = link.get('href', '')
                    if 'Category=' in href and href not in categories:
                        # Boş kategoriyi atla
                        if href != 'Feats.aspx?Category=':
                            categories.append(href)
                
                print(f"  Bulunan kategori sayısı: {len(categories)}")
                
                # Her kategori sayfasından feat'leri çek
                for category_path in categories:
                    # URL'yi düzelt
                    if category_path.startswith('/'):
                        category_url = urljoin(self.base_url, category_path)
                    elif not category_path.startswith('http'):
                        category_url = urljoin(self.base_url + '/', category_path)
                    else:
                        category_url = category_path
                    
                    cat_soup = self._get(category_url)
                    if cat_soup:
                        # FeatsDisplay.aspx linklerini bul
                        feat_links = cat_soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx\?ItemName='))
                        for link in feat_links:
                            feat_name = link.get_text(strip=True)
                            if feat_name and feat_name not in feats and len(feat_name) > 1:
                                href = link.get('href', '')
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                feat_data = self._scrape_feat_detail(href)
                                if feat_data:
                                    feats[feat_name] = feat_data
                                    if len(feats) % 50 == 0:
                                        print(f"  ... {len(feats)} feat çekildi")
                
                # Ana sayfadan da direkt linkleri kontrol et (eğer varsa)
                feat_links = soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx\?ItemName='))
                for link in feat_links:
                    feat_name = link.get_text(strip=True)
                    if feat_name and feat_name not in feats:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        feat_data = self._scrape_feat_detail(href)
                        if feat_data:
                            feats[feat_name] = feat_data
                            if len(feats) % 50 == 0:
                                print(f"  ... {len(feats)} feat çekildi")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd - /feats/ altındaki linkleri bul
            soup = self._get(self.site_config["feats_url"])
            if soup:
                # /feats/ altındaki linkleri bul
                feat_links = soup.find_all('a', href=re.compile(r'/feats/[^/]+/[^/]+$'))
                seen_feats = set()
                for link in feat_links:
                    href = link.get('href', '')
                    feat_name = link.get_text(strip=True)
                    if href and href not in seen_feats and feat_name:
                        seen_feats.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        feat_data = self._scrape_feat_detail(href)
                        if feat_data:
                            feats[feat_name] = feat_data
                            if len(feats) % 10 == 0:
                                print(f"  ... {len(feats)} feat çekildi")
        
        print(f"OK: {len(feats)} feat cekildi")
        return feats
    
    def _scrape_feat_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir feat'in detay sayfasını çek"""
        if not url:
            return None
        
        soup = self._get(url)
        if not soup:
            return None
        
        feat_data = {
            "prerequisites": [],
            "benefit": "",
            "normal": "",
            "special": ""
        }
        
        # Prerequisites
        prereq_section = soup.find(string=re.compile(r'Prerequisite', re.I))
        if prereq_section:
            parent = prereq_section.find_parent()
            if parent:
                text = parent.get_text()
                feat_data["prerequisites"] = [t.strip() for t in text.split(',')]
        
        # Benefit
        benefit_section = soup.find(string=re.compile(r'Benefit', re.I))
        if benefit_section:
            parent = benefit_section.find_parent()
            if parent:
                feat_data["benefit"] = parent.get_text(strip=True)
        
        return feat_data
    
    def scrape_spells(self, max_spells: int = 500) -> Dict[str, Any]:
        """Büyüleri çek (max_spells ile limit)"""
        print(f"Spells cekiliyor (max {max_spells})...")
        spells = {}
        
        if "aonprd" in self.base_url:
            # Archives of Nethys - "All Spells" sayfasındaki tablodan çek
            all_spells_url = urljoin(self.base_url, "Spells.aspx?Class=All")
            all_soup = self._get(all_spells_url)
            
            if all_soup:
                # Tablo içindeki linkleri bul
                tables = all_soup.find_all('table')
                spell_links = []
                
                for table in tables:
                    # Tablo içindeki tüm linkleri bul
                    table_links = table.find_all('a', href=True)
                    # SpellsDisplay içeren veya spell içeren linkleri filtrele
                    for link in table_links:
                        href = link.get('href', '')
                        if 'SpellsDisplay' in href or ('Spell' in href and 'ItemName=' in href):
                            spell_links.append(link)
                
                # Eğer tablo içinde bulamadıysak, tüm sayfada ara
                if not spell_links:
                    spell_links = all_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx\?ItemName='))
                
                print(f"  'All Spells' sayfasında {len(spell_links)} büyü linki bulundu")
                
                for link in spell_links:
                    if len(spells) >= max_spells:
                        break
                    spell_name = link.get_text(strip=True)
                    if spell_name and spell_name not in spells and len(spell_name) > 1:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        spell_data = self._scrape_spell_detail(href)
                        if spell_data:
                            spells[spell_name] = spell_data
                            if len(spells) % 50 == 0:
                                print(f"  ... {len(spells)} büyü çekildi")
                
                # Eğer yeterli büyü çekilmediyse, diğer sınıf sayfalarını kontrol et
                if len(spells) < max_spells:
                    # Ana sayfadan sınıf linklerini bul
                    class_links = all_soup.find_all('a', href=re.compile(r'Spells\.aspx\?Class='))
                    seen_classes = set()
                    
                    for link in class_links:
                        if len(spells) >= max_spells:
                            break
                        
                        href = link.get('href', '')
                        if href and 'Class=' in href and href not in seen_classes:
                            seen_classes.add(href)
                            
                            if not href.startswith('http'):
                                category_url = urljoin(self.base_url, href)
                            else:
                                category_url = href
                            
                            cat_soup = self._get(category_url)
                            if cat_soup:
                                spell_links = cat_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx\?ItemName='))
                                for link in spell_links:
                                    if len(spells) >= max_spells:
                                        break
                                    spell_name = link.get_text(strip=True)
                                    if spell_name and spell_name not in spells:
                                        href = link.get('href', '')
                                        if not href.startswith('http'):
                                            href = urljoin(self.base_url, href)
                                        spell_data = self._scrape_spell_detail(href)
                                        if spell_data:
                                            spells[spell_name] = spell_data
                                            if len(spells) % 50 == 0:
                                                print(f"  ... {len(spells)} büyü çekildi")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd - /magic/all-spells/ sayfası + A-Z alt sayfalarından çek
            spells_list_url = urljoin(self.base_url, "/magic/all-spells/")
            soup = self._get(spells_list_url)
            
            if soup:
                seen_spells = set()
                letter_pages = set()
                
                # A-Z alt sayfalarını bul (örn: /magic/all-spells/a/)
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if re.match(r'/magic/all-spells/[a-z0-9-]+/?$', href) and href != "/magic/all-spells/":
                        letter_pages.add(href)
                
                if not letter_pages:
                    letter_pages.add("/magic/all-spells/")
                
                print(f"  {len(letter_pages)} harf/alt sayfa bulundu")
                
                for letter_href in sorted(letter_pages):
                    if len(spells) >= max_spells:
                        break
                    
                    page_url = urljoin(self.base_url, letter_href)
                    letter_soup = self._get(page_url)
                    if not letter_soup:
                        continue
                    
                    # Spell linkleri: /magic/all-spells/a/acid-arrow/
                    spell_links = letter_soup.find_all(
                        'a',
                        href=re.compile(r'/magic/all-spells/[a-z0-9-]+/.+/$', re.IGNORECASE)
                    )
                    print(f"  {letter_href}: {len(spell_links)} potansiyel büyü linki")
                    
                    for link in spell_links:
                        if len(spells) >= max_spells:
                            break
                        
                        href = link.get('href', '')
                        spell_name = link.get_text(strip=True)
                        
                        if href and href not in seen_spells and spell_name and len(spell_name) > 2:
                            seen_spells.add(href)
                            if not href.startswith('http'):
                                href = urljoin(self.base_url, href)
                            
                            spell_data = self._scrape_spell_detail(href)
                            if spell_data:
                                spells[spell_name] = spell_data
                                if len(spells) % 50 == 0:
                                    print(f"  ... {len(spells)} büyü çekildi")
        
        print(f"OK: {len(spells)} spell cekildi")
        return spells
    
    def _scrape_spell_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir büyünün detay sayfasını çek - GELİŞTİRİLMİŞ VERSİYON"""
        if not url:
            return None
        
        soup = self._get(url)
        if not soup:
            return None
        
        spell_data = {
            "level": 0,
            "levels_by_class": {},  # {"Wizard": 1, "Cleric": 2, ...}
            "school": "",
            "subschool": "",
            "descriptor": "",
            "casting_time": "",
            "components": "",
            "material_components": "",
            "focus": "",
            "range": "",
            "area": "",
            "target": "",
            "effect": "",
            "duration": "",
            "saving_throw": "",
            "spell_resistance": "",
            "description": "",
            "source": url
        }
        
        # Tüm metni al
        full_text = soup.get_text()
        
        # Ana içerik alanını bul
        main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
        if main_content:
            full_text = main_content.get_text()
        
        # LEVEL - IYILESTIRILMIS PARSING (Duzeltme: yanlis parse'lar icin)
        # Pattern 1: "Level bard 1, cleric 2, wizard 1"
        level_pattern = re.search(r'Level\s+([^;]+?)(?:;|$)', full_text, re.IGNORECASE)
        if level_pattern:
            level_text = level_pattern.group(1)
            # Her sınıf için level'ı bul - sadece geçerli class isimlerini kabul et
            valid_classes = [
                'alchemist', 'arcanist', 'bard', 'cleric', 'druid', 'inquisitor',
                'magus', 'oracle', 'paladin', 'ranger', 'sorcerer', 'summoner',
                'witch', 'wizard', 'antipaladin', 'bloodrager', 'hunter', 'investigator',
                'occultist', 'psychic', 'shaman', 'skald', 'warpriest', 'slayer',
                'swashbuckler', 'vigilante', 'brawler', 'cavalier', 'gunslinger',
                'samurai', 'ninja', 'rogue', 'fighter', 'barbarian', 'monk'
            ]
            
            # Pattern: "classname level" veya "classname/classname level"
            class_levels = re.findall(r'(\w+(?:/\w+)?)\s+(\d+)', level_text, re.IGNORECASE)
            for class_name, level in class_levels:
                # Class name'i normalize et ve kontrol et
                class_name_lower = class_name.lower().split('/')[0]  # "sorcerer/wizard" -> "sorcerer"
                if class_name_lower in valid_classes:
                    # Eğer "/" içeriyorsa, her iki class'a da ekle
                    if '/' in class_name:
                        for c in class_name.split('/'):
                            c_clean = c.strip().lower()
                            if c_clean in valid_classes:
                                spell_data["levels_by_class"][c.strip().capitalize()] = int(level)
                    else:
                        spell_data["levels_by_class"][class_name.capitalize()] = int(level)
            
            # İlk geçerli level'ı genel level olarak kullan
            if spell_data["levels_by_class"]:
                spell_data["level"] = list(spell_data["levels_by_class"].values())[0]
        
        # SCHOOL
        school_patterns = [
            r'School\s+([^;]+?)(?:;|$)',
            r'(\w+)\s+\[([^\]]+)\]',  # "Evocation [fire]"
        ]
        for pattern in school_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                school_text = match.group(1).strip()
                # School ve subschool'u ayır
                if '[' in school_text:
                    parts = school_text.split('[')
                    spell_data["school"] = parts[0].strip()
                    if len(parts) > 1:
                        spell_data["subschool"] = parts[1].replace(']', '').strip()
                else:
                    spell_data["school"] = school_text
                break
        
        # CASTING TIME - IYILESTIRILMIS PARSING (Duzeltme: "actionComponents" gibi birlestik metinler icin)
        # Pattern: "Casting Time" veya "1 standard actionComponents" gibi birlestik metin
        casting_patterns = [
            r'Casting Time\s+([^C]+?)(?:Components?|Effect|Range|Target|Area|Duration|$)',  # Components'ten once dur
            r'(?:^|\s)(\d+\s+(?:standard|move|full-round|swift|immediate|free)\s+action[^CEARTDS]*?)(?:Components?|Effect|Range|Target|Area|Duration|$)',  # Direkt action pattern
        ]
        for pattern in casting_patterns:
            casting_match = re.search(pattern, full_text, re.IGNORECASE)
            if casting_match:
                ct_text = casting_match.group(1).strip()
                # "action" kelimesinden sonra gelen harfleri temizle (örn: "actionComponents" -> "action")
                ct_text = re.sub(r'(action)[A-Z].*', r'\1', ct_text)
                spell_data["casting_time"] = ct_text
                break
        
        # COMPONENTS - IYILESTIRILMIS PARSING
        # Pattern: "Components V, S, DF" veya "V, S, DFEffect" gibi birlestik metin
        components_patterns = [
            r'Components?\s+([^EARTDS]+?)(?:Effect|Range|Target|Area|Duration|Saving|Spell|$)',  # Effect/Range/Target/Area/Duration'dan once dur
            r'(?:Components?\s+|^)([VSMDF,\s]+?)(?:Effect|Range|Target|Area|Duration|Saving|Spell|$)',  # Direkt V, S, M, D, F pattern
        ]
        for pattern in components_patterns:
            components_match = re.search(pattern, full_text, re.IGNORECASE)
            if components_match:
                comp_text = components_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "DFEffect" -> "DF")
                comp_text = re.sub(r'([VSMDF,\s]+?)([A-Z][a-z]+)', r'\1', comp_text)
                spell_data["components"] = comp_text
                
                # Material components'i ayir
                if 'M' in comp_text or 'material' in comp_text.lower():
                    material_match = re.search(r'M[,\s]*\(([^)]+)\)', comp_text, re.IGNORECASE)
                    if material_match:
                        spell_data["material_components"] = material_match.group(1).strip()
                
                # Focus'u ayir
                if 'F' in comp_text or 'focus' in comp_text.lower():
                    focus_match = re.search(r'F[,\s]*\(([^)]+)\)', comp_text, re.IGNORECASE)
                    if focus_match:
                        spell_data["focus"] = focus_match.group(1).strip()
                break
        
        # RANGE - IYILESTIRILMIS PARSING
        # Pattern: "Range touchTarget" gibi birlestik metin
        range_patterns = [
            r'Range\s+([^TEDAS]+?)(?:Target|Effect|Area|Duration|Saving|Spell|Description|$)',  # Target/Effect/Area/Duration'dan once dur
            r'(?:Range\s+|^)(touch|close|medium|long|unlimited|personal|see text|[0-9]+[^TEDAS]*?)(?:Target|Effect|Area|Duration|Saving|Spell|$)',  # Direkt range pattern
        ]
        for pattern in range_patterns:
            range_match = re.search(pattern, full_text, re.IGNORECASE)
            if range_match:
                range_text = range_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "touchTarget" -> "touch")
                range_text = re.sub(r'([a-z]+)([A-Z][a-z]+)', r'\1', range_text)
                spell_data["range"] = range_text
                break
        
        # AREA / TARGET / EFFECT - IYILESTIRILMIS PARSING
        target_patterns = [
            r'Target\s+([^EDAS]+?)(?:Effect|Duration|Area|Saving|Spell|Description|$)',  # Effect/Duration/Area'dan once dur
        ]
        for pattern in target_patterns:
            target_match = re.search(pattern, full_text, re.IGNORECASE)
            if target_match:
                target_text = target_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "creature touchedDuration" -> "creature touched")
                target_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', target_text)
                spell_data["target"] = target_text
                break
        
        area_patterns = [
            r'Area\s+([^TEDAS]+?)(?:Target|Effect|Duration|Saving|Spell|Description|$)',  # Target/Effect/Duration'dan once dur
        ]
        for pattern in area_patterns:
            area_match = re.search(pattern, full_text, re.IGNORECASE)
            if area_match:
                area_text = area_match.group(1).strip()
                area_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', area_text)
                spell_data["area"] = area_text
                break
        
        effect_patterns = [
            r'Effect\s+([^TEDAS]+?)(?:Target|Duration|Area|Saving|Spell|Description|$)',  # Target/Duration/Area'dan once dur
        ]
        for pattern in effect_patterns:
            effect_match = re.search(pattern, full_text, re.IGNORECASE)
            if effect_match:
                effect_text = effect_match.group(1).strip()
                effect_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', effect_text)
                spell_data["effect"] = effect_text
                break
        
        # DURATION - IYILESTIRILMIS PARSING
        # Pattern: "Duration 1 min./levelSaving" gibi birlestik metin
        duration_patterns = [
            r'Duration\s+([^STEDAS]+?)(?:Saving|Spell|Target|Effect|Area|Description|$)',  # Saving/Spell/Target/Effect/Area'dan once dur
        ]
        for pattern in duration_patterns:
            duration_match = re.search(pattern, full_text, re.IGNORECASE)
            if duration_match:
                duration_text = duration_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "1 min./levelSaving" -> "1 min./level")
                duration_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', duration_text)
                spell_data["duration"] = duration_text
                break
        
        # SAVING THROW - IYILESTIRILMIS PARSING
        saving_patterns = [
            r'Saving Throw\s+([^STEDAS]+?)(?:Spell|Target|Effect|Duration|Area|Description|$)',  # Spell/Target/Effect/Duration/Area'dan once dur
        ]
        for pattern in saving_patterns:
            saving_match = re.search(pattern, full_text, re.IGNORECASE)
            if saving_match:
                saving_text = saving_match.group(1).strip()
                saving_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', saving_text)
                spell_data["saving_throw"] = saving_text
                break
        
        # SPELL RESISTANCE - IYILESTIRILMIS PARSING
        sr_patterns = [
            r'Spell Resistance\s+([^STEDAS]+?)(?:Description|Target|Effect|Duration|Area|Saving|$)',  # Description/Target/Effect/Duration/Area'dan once dur
        ]
        for pattern in sr_patterns:
            sr_match = re.search(pattern, full_text, re.IGNORECASE)
            if sr_match:
                sr_text = sr_match.group(1).strip()
                sr_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', sr_text)
                spell_data["spell_resistance"] = sr_text
                break
        
        # DESCRIPTION - Daha iyi parsing
        # Önce meta description'ı kontrol et
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            spell_data["description"] = meta_desc.get('content')
        else:
            # Ana içerikten description'ı bul
            desc_section = soup.find('div', class_=re.compile(r'description|text|content', re.I))
            if not desc_section:
                # "Description" başlığından sonraki içeriği bul
                desc_header = soup.find(string=re.compile(r'^Description$', re.I))
                if desc_header:
                    parent = desc_header.find_parent()
                    if parent:
                        next_elem = parent.find_next_sibling(['p', 'div'])
                        if next_elem:
                            desc_section = next_elem
            
            if desc_section:
                desc_text = desc_section.get_text(strip=True)
                # İlk birkaç paragrafı al (çok uzun olmasın)
                paragraphs = desc_text.split('\n\n')[:3]
                spell_data["description"] = '\n\n'.join(paragraphs)
        
        return spell_data
    
    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tüm verileri çek ve birleştir"""
        print(f"Pathfinder 1e verileri cekiliyor ({self.base_url})...")
        print("Bu islem birkac dakika surebilir. Lutfen bekleyin...\n")
        
        data = {
            "system": "PATHFINDER_1E",
            "races": self.scrape_races(),
            "classes": self.scrape_classes(),
            "feats": self.scrape_feats(),
            "spells": self.scrape_spells(),
            "items": {}  # Ekipman için ayrı bir fonksiyon eklenebilir
        }
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\nOK: Veriler kaydedildi: {output_file}")
        
        return data


def _merge_dict_deep(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    İki dict'i derinlemesine birleştir (recursive merge).
    Primary önceliklidir, secondary eksikleri tamamlar.
    
    Args:
        primary: Birincil dict (öncelikli)
        secondary: İkincil dict (tamamlayıcı)
    
    Returns:
        Birleştirilmiş dict
    """
    result = primary.copy()
    
    for key, value in secondary.items():
        if key not in result:
            # Yeni key, direkt ekle
            result[key] = value
        else:
            # Var olan key, merge et
            existing = result[key]
            
            if isinstance(value, dict) and isinstance(existing, dict):
                # Nested dict'leri recursive merge et
                result[key] = _merge_dict_deep(existing, value)
            elif isinstance(value, list) and isinstance(existing, list):
                # Listeleri birleştir (duplicate'leri kaldırarak)
                merged_list = existing.copy()
                for item in value:
                    if item not in merged_list:
                        merged_list.append(item)
                result[key] = merged_list
            elif not existing or existing == "" or existing == [] or existing == {}:
                # Primary'de boş/eksik, secondary'den doldur
                result[key] = value
            elif isinstance(value, str) and isinstance(existing, str):
                # String'ler için: daha uzun veya daha detaylı olanı seç
                if len(value) > len(existing) * 1.2:  # %20 daha uzunsa
                    result[key] = value
                # Aksi halde primary'deki kalır
    
    return result


def _merge_category_data(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bir kategori için (örneğin races, classes) iki veri setini birleştir.
    Primary önceliklidir, secondary eksikleri tamamlar.
    
    Args:
        primary: Birincil kategori verisi (öncelikli)
        secondary: İkincil kategori verisi (tamamlayıcı)
    
    Returns:
        Birleştirilmiş kategori verisi
    """
    merged = {}
    
    # Primary'den tüm öğeleri al
    merged.update(primary)
    
    # Secondary'den eksik öğeleri ekle veya mevcut olanları geliştir
    for key, value in secondary.items():
        if key not in merged:
            # Yeni öğe, direkt ekle
            merged[key] = value
        else:
            # Var olan öğe, derinlemesine merge et
            existing = merged[key]
            if isinstance(value, dict) and isinstance(existing, dict):
                merged[key] = _merge_dict_deep(existing, value)
            elif isinstance(value, list) and isinstance(existing, list):
                # Listeleri birleştir (duplicate'leri kaldırarak)
                merged_list = existing.copy()
                for item in value:
                    if item not in merged_list:
                        merged_list.append(item)
                merged[key] = merged_list
            elif not existing or existing == "" or existing == [] or existing == {}:
                # Primary'de boş/eksik, secondary'den doldur
                merged[key] = value
    
    return merged


def scrape_pathfinder_data(site: str = "aonprd", output_dir: Path = None, merge_sites: bool = False) -> Path:
    """
    Pathfinder 1e verilerini çek ve kaydet
    
    Args:
        site: Kullanılacak site ("aonprd" veya "d20pfsrd") veya "both" (her ikisi)
        output_dir: Çıktı dizini (None ise data/ klasörü)
        merge_sites: True ise her iki siteden de veri çekip birleştir
    
    Returns:
        Kaydedilen JSON dosyasının yolu
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[1] / "data"
    
    output_file = output_dir / "pathfinder_1e_data.json"
    
    if merge_sites or site == "both":
        # Her iki siteden de veri çek ve birleştir
        print("🔄 Her iki siteden veri çekiliyor ve birleştiriliyor...\n")
        
        # Önce Archives of Nethys'ten çek (daha resmi)
        print("=" * 60)
        print("📚 1. Archives of Nethys (aonprd.com)")
        print("=" * 60)
        scraper_aon = PathfinderScraper(site="aonprd")
        data_aon = scraper_aon.scrape_all(output_file=None)
        
        print("\n" + "=" * 60)
        print("📚 2. d20pfsrd.com")
        print("=" * 60)
        scraper_d20 = PathfinderScraper(site="d20pfsrd")
        data_d20 = scraper_d20.scrape_all(output_file=None)
        
        # Verileri birleştir (aonprd öncelikli)
        print("\n" + "=" * 60)
        print("🔗 Veriler birleştiriliyor...")
        print("=" * 60)
        
        # Her kategori için birleştirme yap
        merged_races = _merge_category_data(data_aon.get("races", {}), data_d20.get("races", {}))
        merged_classes = _merge_category_data(data_aon.get("classes", {}), data_d20.get("classes", {}))
        merged_feats = _merge_category_data(data_aon.get("feats", {}), data_d20.get("feats", {}))
        merged_spells = _merge_category_data(data_aon.get("spells", {}), data_d20.get("spells", {}))
        merged_items = _merge_category_data(data_aon.get("items", {}), data_d20.get("items", {}))
        
        merged_data = {
            "system": "PATHFINDER_1E",
            "source": "merged (aonprd + d20pfsrd)",
            "races": merged_races,
            "classes": merged_classes,
            "feats": merged_feats,
            "spells": merged_spells,
            "items": merged_items
        }
        
        # İstatistikler
        print(f"\n📊 Birleştirme İstatistikleri:")
        print(f"   Irklar: {len(merged_data['races'])} (aonprd: {len(data_aon.get('races', {}))}, d20pfsrd: {len(data_d20.get('races', {}))})")
        print(f"   Sınıflar: {len(merged_data['classes'])} (aonprd: {len(data_aon.get('classes', {}))}, d20pfsrd: {len(data_d20.get('classes', {}))})")
        print(f"   Feat'ler: {len(merged_data['feats'])} (aonprd: {len(data_aon.get('feats', {}))}, d20pfsrd: {len(data_d20.get('feats', {}))})")
        print(f"   Büyüler: {len(merged_data['spells'])} (aonprd: {len(data_aon.get('spells', {}))}, d20pfsrd: {len(data_d20.get('spells', {}))})")
        
        # Kaydet
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"\nOK: Birlestirilmis veriler kaydedildi: {output_file}")
        
    else:
        # Tek siteden çek
        scraper = PathfinderScraper(site=site)
        scraper.scrape_all(output_file=output_file)
    
    return output_file


if __name__ == "__main__":
    # Test için
    import sys
    site = sys.argv[1] if len(sys.argv) > 1 else "aonprd"
    print(f"Test: {site} sitesinden veri çekiliyor...")
    scrape_pathfinder_data(site=site)


Sınıflar, ırklar, feat'ler, büyüler ve diğer kuralları web'den çeker.
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class PathfinderScraper:
    """Pathfinder 1e verilerini web'den çeken scraper"""
    
    # Desteklenen siteler
    SITES = {
        "aonprd": {
            "base_url": "https://aonprd.com",
            "races_url": "/Races.aspx",
            "classes_url": "/Classes.aspx",
            "feats_url": "/Feats.aspx",
            "spells_url": "/Spells.aspx",
            "items_url": "/Equipment.aspx"
        },
        "d20pfsrd": {
            "base_url": "https://www.d20pfsrd.com",
            "races_url": "/races/",
            "classes_url": "/classes/",
            "feats_url": "/feats/",
            "spells_url": "/spells/",
            "items_url": "/equipment/"
        }
    }
    
    def __init__(self, site: str = "aonprd", delay: float = 1.0):
        """
        Args:
            site: Kullanılacak site ("aonprd" veya "d20pfsrd")
            delay: İstekler arası bekleme süresi (saniye) - siteyi yormamak için
        """
        if site not in self.SITES:
            raise ValueError(f"Desteklenmeyen site: {site}. Desteklenenler: {list(self.SITES.keys())}")
        
        self.site_config = self.SITES[site]
        self.base_url = self.site_config["base_url"]
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """URL'den HTML içeriğini çek ve BeautifulSoup nesnesi döndür"""
        full_url = urljoin(self.base_url, url) if not url.startswith("http") else url
        
        for attempt in range(retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(full_url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"ERROR: {full_url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_races(self) -> Dict[str, Any]:
        """Tüm ırkları çek"""
        print("🏃 Irklar çekiliyor...")
        races = {}
        
        # Site yapısına göre parse et
        if "aonprd" in self.base_url:
            # Archives of Nethys yapısı - Core ve NonCore kategorilerini çek
            for category in ["Core", "NonCore"]:
                url = f"{self.site_config['races_url']}?Category={category}"
                soup = self._get(url)
                if not soup:
                    continue
                
                # RacesDisplay.aspx linklerini bul (Display değil, RacesDisplay!)
                race_links = soup.find_all('a', href=re.compile(r'RacesDisplay\.aspx\?ItemName='))
                for link in race_links:
                    race_name = link.get_text(strip=True)
                    if race_name and race_name not in races:
                        href = link.get('href', '')
                        # Göreceli URL'yi tam URL'ye çevir
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        race_data = self._scrape_race_detail(href)
                        if race_data:
                            races[race_name] = race_data
                            print(f"  ✓ {race_name}")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - ana sayfadan tüm ırk linklerini bul
            soup = self._get(self.site_config["races_url"])
            if soup:
                # /races/core-races/ veya /races/advanced-races/ gibi linkleri bul
                race_links = soup.find_all('a', href=re.compile(r'/races/[^/]+/[^/]+$'))
                seen_races = set()
                for link in race_links:
                    href = link.get('href', '')
                    race_name = link.get_text(strip=True)
                    # Duplicate'leri önle
                    if href and href not in seen_races and race_name:
                        seen_races.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        race_data = self._scrape_race_detail(href)
                        if race_data:
                            races[race_name] = race_data
                            print(f"  ✓ {race_name}")
        
        print(f"OK: {len(races)} irk cekildi")
        return races
    
    def _scrape_race_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir ırkın detay sayfasını çek - GELİŞTİRİLMİŞ VERSİYON"""
        soup = self._get(url)
        if not soup:
            return None
        
        race_data = {
            "ability_score_increase": {},
            "ability_score_increase_text": "",  # "+2 to One Ability Score" gibi metin
            "speed": 30,
            "speed_special": "",  # "30 feet" veya "30 feet, swim 30 feet" gibi
            "traits": [],  # Trait isimleri ve açıklamaları
            "traits_detailed": {},  # Her trait için detaylı bilgi
            "languages": [],
            "languages_automatic": [],  # Otomatik diller
            "languages_bonus": [],  # Bonus dil seçenekleri
            "size": "Medium",
            "source": url,
            "type": "",  # Humanoid, Outsider, etc.
            "subtype": "",  # Subtype bilgisi
            "favored_class_bonus": "",  # Favored class bonus açıklaması
            "favored_classes": [],  # Favored class'lar
            "vision": "normal",  # normal, low-light, darkvision, etc.
            "vision_range": 0,  # Darkvision range
            "skill_bonuses": {},  # Skill bonusları
            "weapon_proficiencies": [],  # Weapon proficiencies
            "armor_proficiencies": [],  # Armor proficiencies
            "racial_spells": [],  # Racial spell-like abilities
            "spell_resistance": None,  # Spell resistance
            "description": ""  # Irk açıklaması
        }
        
        # Tüm metni al
        full_text = soup.get_text()
        
        # Ana içerik alanını bul
        main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
        if main_content:
            full_text = main_content.get_text()
        
        # ABILITY SCORE INCREASES - Geliştirilmiş parsing
        # Pattern 1: "+2 to One Ability Score" (Human gibi)
        one_ability_pattern = re.search(r'\+(\d+)\s+to\s+One\s+Ability\s+Score', full_text, re.IGNORECASE)
        if one_ability_pattern:
            bonus = int(one_ability_pattern.group(1))
            race_data["ability_score_increase_text"] = f"+{bonus} to One Ability Score"
            race_data["ability_score_increase"] = {"any": bonus}
        
        # Pattern 2: "+2 Str, +2 Con" veya "+2 Strength, +2 Constitution"
        if not race_data["ability_score_increase"]:
            ability_patterns = [
                (r'\+(\d+)\s+(?:Str|Strength)', "strength"),
                (r'\+(\d+)\s+(?:Dex|Dexterity)', "dexterity"),
                (r'\+(\d+)\s+(?:Con|Constitution)', "constitution"),
                (r'\+(\d+)\s+(?:Int|Intelligence)', "intelligence"),
                (r'\+(\d+)\s+(?:Wis|Wisdom)', "wisdom"),
                (r'\+(\d+)\s+(?:Cha|Charisma)', "charisma"),
            ]
            
            for pattern, ability in ability_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    # En yüksek bonus'u al
                    max_bonus = max(int(m) for m in matches)
                    race_data["ability_score_increase"][ability] = max_bonus
                    if not race_data["ability_score_increase_text"]:
                        race_data["ability_score_increase_text"] = f"+{max_bonus} {ability.capitalize()}"
                    else:
                        race_data["ability_score_increase_text"] += f", +{max_bonus} {ability.capitalize()}"
        
        # SIZE
        size_patterns = [
            r'Size\s*:?\s*(\w+)',
            r'(\w+)\s+size',
        ]
        for pattern in size_patterns:
            size_match = re.search(pattern, full_text, re.IGNORECASE)
            if size_match:
                size = size_match.group(1).capitalize()
                if size.lower() in ["small", "medium", "large", "tiny", "diminutive", "fine", "huge", "gargantuan", "colossal"]:
                    race_data["size"] = size
                    break
        
        # SPEED - Geliştirilmiş
        speed_match = re.search(r'Speed\s*:?\s*([^\n]+?)(?:\n|$)', full_text, re.IGNORECASE)
        if speed_match:
            speed_text = speed_match.group(1).strip()
            # Sayısal değeri bul
            speed_num_match = re.search(r'(\d+)', speed_text)
            if speed_num_match:
                race_data["speed"] = int(speed_num_match.group(1))
            race_data["speed_special"] = speed_text[:200]
        
        # LANGUAGES - Düzeltilmiş parsing
        # Archives of Nethys'te Languages genellikle <strong>Languages</strong> şeklinde
        lang_header = soup.find('strong', string=re.compile(r'^Languages?$', re.I))
        if not lang_header:
            lang_header = soup.find('b', string=re.compile(r'^Languages?$', re.I))
        
        if lang_header:
            # Sonraki içeriği bul (aynı veya sonraki p/div)
            lang_content = ""
            
            # Önce parent'ı kontrol et
            parent = lang_header.find_parent(['p', 'div'])
            if parent:
                # Parent içindeki tüm metni al, ama "Languages" başlığını çıkar
                parent_text = parent.get_text()
                lang_content = parent_text.replace(lang_header.get_text(), "").strip()
            
            # Eğer parent'ta yeterli bilgi yoksa, sonraki sibling'leri kontrol et
            if not lang_content or len(lang_content) < 20:
                next_elem = lang_header.find_next_sibling(['p', 'div'])
                if next_elem:
                    lang_content = next_elem.get_text(strip=True)
            
            if lang_content:
                # "Automatic" ve "Bonus" bölümlerini ayır
                auto_match = re.search(r'(?:Automatic|begin play speaking|speak)\s*:?\s*([^.]*?)(?:\.|Bonus|$)', lang_content, re.IGNORECASE | re.DOTALL)
                bonus_match = re.search(r'(?:Bonus\s+Languages?|bonus languages?)\s*:?\s*([^.]*)', lang_content, re.IGNORECASE)
                
                if auto_match:
                    auto_text = auto_match.group(1)
                    # Dil isimlerini ayır (Common, Elven, Draconic, etc.)
                    # Büyük harfle başlayan kelimeleri bul (dil isimleri genellikle büyük harfle başlar)
                    auto_langs = []
                    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', auto_text)
                    known_languages = ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Giant', 'Draconic', 'Gnoll', 
                                     'Halfling', 'Gnome', 'Sylvan', 'Aquan', 'Auran', 'Ignan', 'Terran', 'Celestial',
                                     'Infernal', 'Abyssal', 'Aklo', 'Undercommon', 'Jotun', 'Tengu', 'Varisian',
                                     'Kelish', 'Vudrani', 'Osiriani', 'Tien', 'Taldane', 'Skald', 'Chelish']
                    for word in words:
                        # Bilinen dil isimlerini kontrol et veya benzer olanları bul
                        if any(known in word for known in known_languages) or word in known_languages:
                            if word not in auto_langs:
                                auto_langs.append(word)
                    
                    # Eğer pattern ile bulamadıysak, "speaking X" veya "X and Y" formatını dene
                    if not auto_langs:
                        # "speaking Common and Elven" gibi formatları bul
                        speaking_match = re.search(r'speaking\s+([^.]+)', lang_content, re.IGNORECASE)
                        if speaking_match:
                            speaking_text = speaking_match.group(1)
                            # "and", "or" ile ayrılmış dilleri bul
                            langs = re.split(r'\s+(?:and|or)\s+', speaking_text)
                            for lang in langs:
                                lang = lang.strip()
                                if lang and len(lang) < 30 and lang[0].isupper():
                                    auto_langs.append(lang)
                    
                    race_data["languages_automatic"] = auto_langs[:10]
                
                if bonus_match:
                    bonus_text = bonus_match.group(1)
                    # Bonus dilleri ayır
                    bonus_langs = []
                    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', bonus_text)
                    known_languages = ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Giant', 'Draconic', 'Gnoll',
                                     'Halfling', 'Gnome', 'Sylvan', 'Aquan', 'Auran', 'Ignan', 'Terran']
                    for word in words:
                        if any(known in word for known in known_languages) or word in known_languages:
                            if word not in bonus_langs:
                                bonus_langs.append(word)
                    race_data["languages_bonus"] = bonus_langs[:20]
                
                # Eğer otomatik/bonus bulunamadıysa, genel "Languages" içeriğinden çıkar
                if not race_data["languages_automatic"] and not race_data["languages_bonus"]:
                    # Basit pattern: "speaking X" veya "X, Y, and Z"
                    speaking_match = re.search(r'(?:speaking|speak)\s+([^.]{1,100})', lang_content, re.IGNORECASE)
                    if speaking_match:
                        speaking_text = speaking_match.group(1)
                        # Virgülle veya "and" ile ayrılmış dilleri bul
                        langs = re.split(r'[,;]\s*|\s+and\s+|\s+or\s+', speaking_text)
                        auto_langs = []
                        for lang in langs:
                            lang = lang.strip()
                            # Büyük harfle başlayan, bilinen dil isimleri
                            if lang and len(lang) < 30 and lang[0].isupper():
                                # Bilinen dillere benzer mi kontrol et
                                if any(known.lower() in lang.lower() or lang.lower() in known.lower() 
                                      for known in ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Draconic']):
                                    if lang not in auto_langs:
                                        auto_langs.append(lang)
                        if auto_langs:
                            race_data["languages_automatic"] = auto_langs[:10]
                
                # Genel languages listesi
                race_data["languages"] = race_data["languages_automatic"] + race_data["languages_bonus"][:5]
        
        # RACIAL TRAITS - Düzeltilmiş parsing (Archives of Nethys)
        if "aonprd" in self.base_url:
            # Archives of Nethys'te asıl racial traits <strong> veya <b> etiketlerinde
            # Sadece belirli anahtar kelimeleri içeren trait başlıklarını bul
            racial_trait_keywords = [
                'speed', 'feat', 'skilled', 'vision', 'immunity', 'trait', 'weapon', 'armor', 
                'spell', 'resistance', 'bonus', 'proficiency', 'skill', 'movement', 'racial',
                'low-light', 'darkvision', 'blindsight', 'tremorsense', 'keen senses', 'senses'
            ]
            
            # Genel başlıkları hariç tut (bunlar racial trait değil)
            exclude_keywords = [
                'source', 'languages', 'language', 'physical', 'society', 'relations', 
                'alignment', 'religion', 'adventurers', 'description', 'name', 'size',
                'type', 'subtype', 'favored class', 'racial traits', 'alternate'
            ]
            
            # <strong> ve <b> etiketlerini bul
            strong_tags = soup.find_all(['strong', 'b'])
            for tag in strong_tags:
                trait_name = tag.get_text(strip=True)
                
                # Genel başlıkları atla
                if any(exc.lower() in trait_name.lower() for exc in exclude_keywords):
                    continue
                
                # Trait başlığı mı kontrol et
                is_racial_trait = False
                
                # Anahtar kelime kontrolü
                if any(keyword.lower() in trait_name.lower() for keyword in racial_trait_keywords):
                    is_racial_trait = True
                
                # Kısa başlıklar da trait olabilir (ama uzun olmasın)
                elif len(trait_name) < 30 and len(trait_name) > 2:
                    # Sayı içermeyen, sadece harf içeren başlıklar genellikle trait'tir
                    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', trait_name):
                        # Ama genel başlıkları atla
                        if trait_name.lower() not in exclude_keywords:
                            is_racial_trait = True
                
                if is_racial_trait:
                    # Sonraki içeriği bul
                    trait_content = ""
                    
                    # Parent içindeki içeriği kontrol et
                    parent = tag.find_parent(['p', 'div'])
                    if parent:
                        parent_text = parent.get_text()
                        # Tag'dan sonraki kısmı al
                        parts = parent_text.split(trait_name, 1)
                        if len(parts) > 1:
                            after_trait = parts[1].strip()
                            # ":" işaretinden sonraki ilk cümleyi al
                            if ':' in after_trait:
                                after_trait = after_trait.split(':', 1)[1].strip()
                            # İlk cümleyi al (nokta, yeni satır veya başka trait öncesi)
                            trait_content = re.split(r'[.\n](?=\s*[A-Z])|(?=\n\s*[A-Z][a-z]+\s*:)', after_trait)[0].strip()
                            trait_content = trait_content[:300]  # Maksimum uzunluk
                    
                    # Eğer parent'ta yeterli içerik yoksa, sonraki sibling'i kontrol et
                    if not trait_content or len(trait_content) < 10:
                        next_elem = tag.find_next_sibling(['p', 'div'])
                        if next_elem:
                            if hasattr(next_elem, 'get_text'):
                                trait_text = next_elem.get_text(strip=True)
                                # İlk cümleyi al
                                trait_content = re.split(r'[.\n](?=\s*[A-Z])', trait_text)[0].strip()[:300]
                    
                    # İçerik varsa ve anlamlıysa ekle
                    if trait_content and len(trait_content) > 5 and len(trait_content) < 500:
                        # Duplicate kontrolü ve anlamlılık kontrolü
                        # Çok kısa veya çok genel içerikleri atla
                        # Sınıf isimlerini atla (bunlar favored class bonus, trait değil)
                        if (trait_name not in race_data["traits"] and 
                            len(trait_content) > 10 and
                            not any(exc.lower() in trait_content.lower()[:50] for exc in ['source', 'pg.', 'page']) and
                            trait_name not in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 
                                              'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 
                                              'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                                              'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                                              'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                                              'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']):
                            race_data["traits"].append(trait_name)
                            race_data["traits_detailed"][trait_name] = trait_content[:300]
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - dt/dd yapısı
            dl_tags = soup.find_all('dl')
            for dl in dl_tags:
                dt_tags = dl.find_all('dt')
                for dt in dt_tags:
                    term = dt.get_text(strip=True)
                    dd = dt.find_next_sibling('dd')
                    if dd and term and len(term) < 100:
                        definition = dd.get_text(strip=True)
                        if definition and len(definition) > 10:
                            # Sınıf isimlerini atla (bunlar favored class bonus, trait değil)
                            if term not in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler',
                                          'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter',
                                          'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                                          'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                                          'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                                          'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']:
                                race_data["traits"].append(term)
                                race_data["traits_detailed"][term] = definition[:500]
        
        # VISION - Traits parsing'inden SONRA yapılmalı (vision genellikle bir trait olarak geliyor)
        # Önce traits listesinde vision trait'ini ara - SADECE ASIL RACIAL TRAITS'ten (ilk 5-10 trait)
        # Alternatif traits'i atla (bunlar genellikle sayfanın sonunda gelir)
        core_traits = race_data.get("traits", [])[:10]  # İlk 10 trait'i al (asıl racial traits genellikle başta)
        
        # İlk birkaç trait'in gerçekten asıl racial trait olup olmadığını kontrol et
        # (Medium, Normal Speed, Bonus Feat gibi)
        core_racial_trait_keywords = ['medium', 'small', 'large', 'speed', 'feat', 'skilled', 'vision', 
                                     'immunity', 'magic', 'resistance', 'weapon', 'armor', 'movement']
        
        # Eğer ilk trait'lerde bu anahtar kelimeler varsa, bunlar asıl traits'tir
        # Alternatif traits genellikle bu anahtar kelimeleri içermez veya daha sonra gelir
        for trait_name in core_traits:
            trait_name_lower = trait_name.lower()
            
            # Alternatif trait kontrolü - eğer trait ismi bir sınıf ismi gibi görünüyorsa (Alchemist, Bard, etc.)
            # veya çok uzunsa, bu alternatif trait olabilir
            if (trait_name in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 'Cavalier',
                              'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 'Inquisitor', 'Investigator',
                              'Kineticist', 'Magus', 'Mesmerist', 'Monk', 'Occultist', 'Oracle', 'Paladin',
                              'Psychic', 'Ranger', 'Rogue', 'Shaman', 'Shifter', 'Skald', 'Slayer', 'Sorcerer',
                              'Spiritualist', 'Summoner', 'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']):
                continue  # Bu bir favored class bonus, trait değil
            
            # Vision trait'ini ara
            if 'low-light' in trait_name_lower or ('vision' in trait_name_lower and 'low' in trait_name_lower):
                # Ama bu trait'in alternate trait olmadığından emin ol
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                # Eğer trait detail "replaces" içeriyorsa, bu alternatif trait'tir, atla
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                race_data["vision"] = "low-light"
                race_data["vision_range"] = 0
                break
            elif 'darkvision' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                # Alternate trait kontrolü
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "darkvision"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 60
                break
            elif 'blindsight' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "blindsight"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                break
            elif 'tremorsense' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "tremorsense"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                break
        
        # Eğer traits listesinde bulunamadıysa, <strong> tag'lerinde direkt ara (backup)
        if race_data["vision"] == "normal":
            vision_strong = soup.find(['strong', 'b'], string=re.compile(r'^(?:Low-light\s+Vision|Darkvision|Blindsight|Tremorsense)$', re.I))
            if vision_strong:
                vision_text = vision_strong.get_text(strip=True)
                parent = vision_strong.find_parent(['p', 'div'])
                if parent:
                    parent_text = parent.get_text()
                    # "Alternate" veya "variant" kelimesi varsa, bu alternate trait'tir, atla
                    if not re.search(r'alternate|variant|optional', parent_text[:200], re.IGNORECASE):
                        if 'Darkvision' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "darkvision"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 60
                        elif 'Low-light' in vision_text:
                            race_data["vision"] = "low-light"
                            race_data["vision_range"] = 0
                        elif 'Blindsight' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "blindsight"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                        elif 'Tremorsense' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "tremorsense"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
        
        # FAVORED CLASS - Düzeltilmiş parsing
        # Favored class genellikle "Favored Class: Any" veya belirli class'lar şeklinde
        favored_patterns = [
            r'Favored\s+Class\s*:?\s*([^\n]+?)(?:\n|$)',
            r'Favored\s+Classes?\s*:?\s*([^\n]+?)(?:\n|$)',
        ]
        
        favored_text = ""
        for pattern in favored_patterns:
            favored_match = re.search(pattern, full_text, re.IGNORECASE)
            if favored_match:
                favored_text = favored_match.group(1).strip()
                break
        
        # Eğer regex ile bulunamadıysa, <strong>Favored Class</strong> etiketini ara
        if not favored_text:
            favored_strong = soup.find(['strong', 'b'], string=re.compile(r'^Favored\s+Class', re.I))
            if favored_strong:
                parent = favored_strong.find_parent(['p', 'div'])
                if parent:
                    parent_text = parent.get_text()
                    # "Favored Class" başlığından sonraki içeriği al
                    parts = parent_text.split(favored_strong.get_text(strip=True), 1)
                    if len(parts) > 1:
                        favored_text = parts[1].strip().split('\n')[0].strip()[:200]
        
        if favored_text:
            race_data["favored_class_bonus"] = favored_text[:200]
            
            # Favored class'ları ayır
            # "Any" ise tüm sınıflar
            if 'any' in favored_text.lower():
                race_data["favored_classes"] = ["Any"]
            else:
                # Belirli sınıf isimlerini bul
                known_classes = ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 
                               'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 
                               'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                               'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                               'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                               'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']
                
                found_classes = []
                for class_name in known_classes:
                    if class_name.lower() in favored_text.lower():
                        found_classes.append(class_name)
                
                if found_classes:
                    race_data["favored_classes"] = found_classes
                else:
                    # Virgülle ayrılmış sınıf isimlerini dene
                    classes = [c.strip() for c in re.split(r'[,;]', favored_text) if c.strip() and len(c.strip()) < 30]
                    race_data["favored_classes"] = classes[:10]
        
        # SPELL RESISTANCE
        sr_match = re.search(r'Spell\s+Resistance\s*:?\s*(\d+)', full_text, re.IGNORECASE)
        if sr_match:
            race_data["spell_resistance"] = int(sr_match.group(1))
        
        # DESCRIPTION - Düzeltilmiş parsing
        # Önce meta description tag'ini kontrol et (genellikle orada olur)
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc and meta_desc.get('content'):
            desc_content = meta_desc.get('content', '').strip()
            if len(desc_content) > 100:
                # HTML entity'leri temizle
                desc_content = desc_content.replace('&lt;br /&gt;', ' ').replace('&quot;', '"').replace('&amp;', '&')
                desc_content = re.sub(r'<[^>]+>', '', desc_content)  # HTML tag'lerini temizle
                # İlk cümleyi al (genellikle en önemli kısım)
                first_sentence = re.split(r'[.\n]', desc_content)[0].strip()
                if len(first_sentence) > 50:
                    race_data["description"] = first_sentence[:500]
                else:
                    race_data["description"] = desc_content[:500]
        
        # Eğer meta tag'de bulunamadıysa, başlıktan sonraki ilk paragrafı bul
        if not race_data["description"]:
            # H1 başlığını bul
            h1 = soup.find('h1', class_='title') or soup.find('h1')
            if h1:
                # Başlıktan sonraki ilk anlamlı paragrafı bul
                current = h1.find_next(['p', 'div'])
                count = 0
                while current and count < 5:
                    if hasattr(current, 'get_text'):
                        text = current.get_text(strip=True)
                        # Uzun ve anlamlı bir paragraf mı kontrol et
                        if (len(text) > 100 and 
                            not any(keyword in text.lower() for keyword in ['source', 'pg.', 'page', 'inner sea races', 'advanced race guide', 'core rulebook']) and
                            not re.match(r'^[A-Z][a-z]+\s+Source', text) and
                            'possess' in text.lower() or 'are' in text.lower() or 'have' in text.lower()):
                            # İlk cümleyi al
                            first_sentence = re.split(r'[.\n](?=\s*[A-Z])', text)[0].strip()
                            if len(first_sentence) > 50:
                                race_data["description"] = first_sentence[:500]
                            else:
                                race_data["description"] = text[:500]
                            break
                    current = current.find_next(['p', 'div'])
                    count += 1
        
        # Eğer hala bulunamadıysa, tüm paragrafları tara
        if not race_data["description"]:
            desc_paragraphs = soup.find_all('p')
            for p in desc_paragraphs[:15]:
                text = p.get_text(strip=True)
                # "possess", "are", "have" gibi kelimeler içeren, uzun paragraflar genellikle description'dur
                if (len(text) > 150 and 
                    not any(keyword in text.lower() for keyword in ['source', 'pg.', 'page', 'inner sea races', 'advanced race guide', 'core rulebook']) and
                    not re.match(r'^[A-Z][a-z]+\s+Source', text) and
                    any(keyword in text.lower() for keyword in ['possess', 'are currently', 'have', 'characterized', 'society', 'culture'])):
                    # İlk cümleyi al
                    first_sentence = re.split(r'[.\n](?=\s*[A-Z])', text)[0].strip()
                    if len(first_sentence) > 50:
                        race_data["description"] = first_sentence[:500]
                    else:
                        race_data["description"] = text[:500]
                    break
        
        return race_data
    
    def _parse_race_from_section(self, section) -> Optional[Dict[str, Any]]:
        """HTML section'dan ırk verisini parse et"""
        # d20pfsrd için özel parsing
        race_data = {
            "ability_score_increase": {},
            "speed": 30,
            "traits": [],
            "languages": [],
            "size": "Medium"
        }
        
        text = section.get_text()
        
        # Ability scores
        matches = re.findall(r'\+(\d+)\s+(\w+)', text)
        for bonus, ability in matches:
            ability_lower = ability.lower()
            if ability_lower in ["str", "strength"]:
                race_data["ability_score_increase"]["strength"] = int(bonus)
            elif ability_lower in ["dex", "dexterity"]:
                race_data["ability_score_increase"]["dexterity"] = int(bonus)
        
        return race_data
    
    def scrape_classes(self) -> Dict[str, Any]:
        """Tüm sınıfları çek"""
        print("⚔️ Sınıflar çekiliyor...")
        classes = {}
        
        # Site yapısına göre parse et
        if "aonprd" in self.base_url:
            # Archives of Nethys - Ana sayfadan tüm sınıfları çek
            soup = self._get(self.site_config["classes_url"])
            if soup:
                # ClassDisplay.aspx linklerini bul (ClassesDisplay değil, ClassDisplay!)
                class_links = soup.find_all('a', href=re.compile(r'ClassDisplay\.aspx\?ItemName='))
                # Ayrıca ClassesDisplay pattern'ini de kontrol et
                if not class_links:
                    class_links = soup.find_all('a', href=re.compile(r'ClassesDisplay\.aspx\?ItemName='))
                # Son çare: href'inde Class geçen ve Display geçen linkler
                if not class_links:
                    all_links = soup.find_all('a', href=True)
                    class_links = [l for l in all_links if 'Class' in l.get('href', '') and 'Display' in l.get('href', '')]
                
                for link in class_links:
                    class_name = link.get_text(strip=True)
                    if class_name and class_name not in classes and len(class_name) > 2:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        class_data = self._scrape_class_detail(href)
                        if class_data:
                            classes[class_name] = class_data
                            print(f"  ✓ {class_name}")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - /classes/ altındaki linkleri bul
            soup = self._get(self.site_config["classes_url"])
            if soup:
                # /classes/core-classes/ veya /classes/base-classes/ gibi linkleri bul
                class_links = soup.find_all('a', href=re.compile(r'/classes/[^/]+/[^/]+$'))
                seen_classes = set()
                for link in class_links:
                    href = link.get('href', '')
                    class_name = link.get_text(strip=True)
                    if href and href not in seen_classes and class_name:
                        seen_classes.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        class_data = self._scrape_class_detail(href)
                        if class_data:
                            classes[class_name] = class_data
                            print(f"  ✓ {class_name}")
        
        print(f"OK: {len(classes)} sinif cekildi")
        return classes
    
    def _scrape_class_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir sınıfın detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        class_data = {
            "hit_die": "d8",
            "skill_ranks_per_level": 2,
            "class_skills": [],
            "proficiencies": [],
            "spellcasting": False,
            "features": {},
            "source": url
        }
        
        full_text = soup.get_text()
        
        # Hit Die - daha kapsamlı pattern
        hit_die_patterns = [
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Dice[:\s]+d(\d+)',
            r'd(\d+)\s+Hit Die',
        ]
        for pattern in hit_die_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                class_data["hit_die"] = f"d{match.group(1)}"
                break
        
        # Skill Ranks Per Level
        skill_ranks_match = re.search(r'Skill Ranks[:\s]+(\d+)', full_text, re.IGNORECASE)
        if skill_ranks_match:
            class_data["skill_ranks_per_level"] = int(skill_ranks_match.group(1))
        
        # Class Skills - daha iyi parsing
        skills_section = soup.find(string=re.compile(r'Class Skills?', re.I))
        if skills_section:
            parent = skills_section.find_parent()
            # Sonraki paragraf veya liste
            next_elem = parent.find_next(['p', 'ul', 'ol', 'div'])
            if next_elem:
                skills_text = next_elem.get_text()
                # Virgülle ayrılmış skill'leri bul
                skills = [s.strip() for s in re.split(r'[,;]', skills_text) if s.strip() and len(s.strip()) < 30]
                class_data["class_skills"] = skills[:30]  # İlk 30 skill
        
        # Spellcasting - daha kapsamlı kontrol
        spellcasting_indicators = [
            r'Spellcasting',
            r'Spells per Day',
            r'Spell List',
            r'Caster Level',
        ]
        for indicator in spellcasting_indicators:
            if re.search(indicator, full_text, re.IGNORECASE):
                class_data["spellcasting"] = True
                break
        
        # Proficiencies
        prof_section = soup.find(string=re.compile(r'Proficiencies?', re.I))
        if prof_section:
            parent = prof_section.find_parent()
            next_elem = parent.find_next(['p', 'ul', 'ol'])
            if next_elem:
                prof_text = next_elem.get_text()
                proficiencies = [p.strip() for p in re.split(r'[,;]', prof_text) if p.strip()]
                class_data["proficiencies"] = proficiencies[:20]
        
        return class_data
    
    def _parse_class_from_section(self, section) -> Optional[Dict[str, Any]]:
        """HTML section'dan sınıf verisini parse et"""
        class_data = {
            "hit_die": "d8",
            "skill_ranks_per_level": 2,
            "class_skills": [],
            "proficiencies": [],
            "spellcasting": False,
            "features": {}
        }
        
        text = section.get_text()
        
        # Hit Die
        match = re.search(r'd(\d+)', text)
        if match:
            class_data["hit_die"] = f"d{match.group(1)}"
        
        return class_data
    
    def scrape_feats(self) -> Dict[str, Any]:
        """Tüm feat'leri çek"""
        print("⭐ Feat'ler çekiliyor...")
        feats = {}
        
        if "aonprd" in self.base_url:
            # Archives of Nethys - Feats.aspx sayfasından kategorileri çek
            soup = self._get(self.site_config["feats_url"])
            if soup:
                # Önce kategori linklerini bul (Feats.aspx?Category=...)
                category_links = soup.find_all('a', href=re.compile(r'Feats\.aspx\?Category='))
                categories = []
                for link in category_links:
                    href = link.get('href', '')
                    if 'Category=' in href and href not in categories:
                        # Boş kategoriyi atla
                        if href != 'Feats.aspx?Category=':
                            categories.append(href)
                
                print(f"  Bulunan kategori sayısı: {len(categories)}")
                
                # Her kategori sayfasından feat'leri çek
                for category_path in categories:
                    # URL'yi düzelt
                    if category_path.startswith('/'):
                        category_url = urljoin(self.base_url, category_path)
                    elif not category_path.startswith('http'):
                        category_url = urljoin(self.base_url + '/', category_path)
                    else:
                        category_url = category_path
                    
                    cat_soup = self._get(category_url)
                    if cat_soup:
                        # FeatsDisplay.aspx linklerini bul
                        feat_links = cat_soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx\?ItemName='))
                        for link in feat_links:
                            feat_name = link.get_text(strip=True)
                            if feat_name and feat_name not in feats and len(feat_name) > 1:
                                href = link.get('href', '')
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                feat_data = self._scrape_feat_detail(href)
                                if feat_data:
                                    feats[feat_name] = feat_data
                                    if len(feats) % 50 == 0:
                                        print(f"  ... {len(feats)} feat çekildi")
                
                # Ana sayfadan da direkt linkleri kontrol et (eğer varsa)
                feat_links = soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx\?ItemName='))
                for link in feat_links:
                    feat_name = link.get_text(strip=True)
                    if feat_name and feat_name not in feats:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        feat_data = self._scrape_feat_detail(href)
                        if feat_data:
                            feats[feat_name] = feat_data
                            if len(feats) % 50 == 0:
                                print(f"  ... {len(feats)} feat çekildi")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd - /feats/ altındaki linkleri bul
            soup = self._get(self.site_config["feats_url"])
            if soup:
                # /feats/ altındaki linkleri bul
                feat_links = soup.find_all('a', href=re.compile(r'/feats/[^/]+/[^/]+$'))
                seen_feats = set()
                for link in feat_links:
                    href = link.get('href', '')
                    feat_name = link.get_text(strip=True)
                    if href and href not in seen_feats and feat_name:
                        seen_feats.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        feat_data = self._scrape_feat_detail(href)
                        if feat_data:
                            feats[feat_name] = feat_data
                            if len(feats) % 10 == 0:
                                print(f"  ... {len(feats)} feat çekildi")
        
        print(f"OK: {len(feats)} feat cekildi")
        return feats
    
    def _scrape_feat_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir feat'in detay sayfasını çek"""
        if not url:
            return None
        
        soup = self._get(url)
        if not soup:
            return None
        
        feat_data = {
            "prerequisites": [],
            "benefit": "",
            "normal": "",
            "special": ""
        }
        
        # Prerequisites
        prereq_section = soup.find(string=re.compile(r'Prerequisite', re.I))
        if prereq_section:
            parent = prereq_section.find_parent()
            if parent:
                text = parent.get_text()
                feat_data["prerequisites"] = [t.strip() for t in text.split(',')]
        
        # Benefit
        benefit_section = soup.find(string=re.compile(r'Benefit', re.I))
        if benefit_section:
            parent = benefit_section.find_parent()
            if parent:
                feat_data["benefit"] = parent.get_text(strip=True)
        
        return feat_data
    
    def scrape_spells(self, max_spells: int = 500) -> Dict[str, Any]:
        """Büyüleri çek (max_spells ile limit)"""
        print(f"Spells cekiliyor (max {max_spells})...")
        spells = {}
        
        if "aonprd" in self.base_url:
            # Archives of Nethys - "All Spells" sayfasındaki tablodan çek
            all_spells_url = urljoin(self.base_url, "Spells.aspx?Class=All")
            all_soup = self._get(all_spells_url)
            
            if all_soup:
                # Tablo içindeki linkleri bul
                tables = all_soup.find_all('table')
                spell_links = []
                
                for table in tables:
                    # Tablo içindeki tüm linkleri bul
                    table_links = table.find_all('a', href=True)
                    # SpellsDisplay içeren veya spell içeren linkleri filtrele
                    for link in table_links:
                        href = link.get('href', '')
                        if 'SpellsDisplay' in href or ('Spell' in href and 'ItemName=' in href):
                            spell_links.append(link)
                
                # Eğer tablo içinde bulamadıysak, tüm sayfada ara
                if not spell_links:
                    spell_links = all_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx\?ItemName='))
                
                print(f"  'All Spells' sayfasında {len(spell_links)} büyü linki bulundu")
                
                for link in spell_links:
                    if len(spells) >= max_spells:
                        break
                    spell_name = link.get_text(strip=True)
                    if spell_name and spell_name not in spells and len(spell_name) > 1:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        spell_data = self._scrape_spell_detail(href)
                        if spell_data:
                            spells[spell_name] = spell_data
                            if len(spells) % 50 == 0:
                                print(f"  ... {len(spells)} büyü çekildi")
                
                # Eğer yeterli büyü çekilmediyse, diğer sınıf sayfalarını kontrol et
                if len(spells) < max_spells:
                    # Ana sayfadan sınıf linklerini bul
                    class_links = all_soup.find_all('a', href=re.compile(r'Spells\.aspx\?Class='))
                    seen_classes = set()
                    
                    for link in class_links:
                        if len(spells) >= max_spells:
                            break
                        
                        href = link.get('href', '')
                        if href and 'Class=' in href and href not in seen_classes:
                            seen_classes.add(href)
                            
                            if not href.startswith('http'):
                                category_url = urljoin(self.base_url, href)
                            else:
                                category_url = href
                            
                            cat_soup = self._get(category_url)
                            if cat_soup:
                                spell_links = cat_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx\?ItemName='))
                                for link in spell_links:
                                    if len(spells) >= max_spells:
                                        break
                                    spell_name = link.get_text(strip=True)
                                    if spell_name and spell_name not in spells:
                                        href = link.get('href', '')
                                        if not href.startswith('http'):
                                            href = urljoin(self.base_url, href)
                                        spell_data = self._scrape_spell_detail(href)
                                        if spell_data:
                                            spells[spell_name] = spell_data
                                            if len(spells) % 50 == 0:
                                                print(f"  ... {len(spells)} büyü çekildi")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd - /magic/all-spells/ sayfası + A-Z alt sayfalarından çek
            spells_list_url = urljoin(self.base_url, "/magic/all-spells/")
            soup = self._get(spells_list_url)
            
            if soup:
                seen_spells = set()
                letter_pages = set()
                
                # A-Z alt sayfalarını bul (örn: /magic/all-spells/a/)
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if re.match(r'/magic/all-spells/[a-z0-9-]+/?$', href) and href != "/magic/all-spells/":
                        letter_pages.add(href)
                
                if not letter_pages:
                    letter_pages.add("/magic/all-spells/")
                
                print(f"  {len(letter_pages)} harf/alt sayfa bulundu")
                
                for letter_href in sorted(letter_pages):
                    if len(spells) >= max_spells:
                        break
                    
                    page_url = urljoin(self.base_url, letter_href)
                    letter_soup = self._get(page_url)
                    if not letter_soup:
                        continue
                    
                    # Spell linkleri: /magic/all-spells/a/acid-arrow/
                    spell_links = letter_soup.find_all(
                        'a',
                        href=re.compile(r'/magic/all-spells/[a-z0-9-]+/.+/$', re.IGNORECASE)
                    )
                    print(f"  {letter_href}: {len(spell_links)} potansiyel büyü linki")
                    
                    for link in spell_links:
                        if len(spells) >= max_spells:
                            break
                        
                        href = link.get('href', '')
                        spell_name = link.get_text(strip=True)
                        
                        if href and href not in seen_spells and spell_name and len(spell_name) > 2:
                            seen_spells.add(href)
                            if not href.startswith('http'):
                                href = urljoin(self.base_url, href)
                            
                            spell_data = self._scrape_spell_detail(href)
                            if spell_data:
                                spells[spell_name] = spell_data
                                if len(spells) % 50 == 0:
                                    print(f"  ... {len(spells)} büyü çekildi")
        
        print(f"OK: {len(spells)} spell cekildi")
        return spells
    
    def _scrape_spell_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir büyünün detay sayfasını çek - GELİŞTİRİLMİŞ VERSİYON"""
        if not url:
            return None
        
        soup = self._get(url)
        if not soup:
            return None
        
        spell_data = {
            "level": 0,
            "levels_by_class": {},  # {"Wizard": 1, "Cleric": 2, ...}
            "school": "",
            "subschool": "",
            "descriptor": "",
            "casting_time": "",
            "components": "",
            "material_components": "",
            "focus": "",
            "range": "",
            "area": "",
            "target": "",
            "effect": "",
            "duration": "",
            "saving_throw": "",
            "spell_resistance": "",
            "description": "",
            "source": url
        }
        
        # Tüm metni al
        full_text = soup.get_text()
        
        # Ana içerik alanını bul
        main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
        if main_content:
            full_text = main_content.get_text()
        
        # LEVEL - IYILESTIRILMIS PARSING (Duzeltme: yanlis parse'lar icin)
        # Pattern 1: "Level bard 1, cleric 2, wizard 1"
        level_pattern = re.search(r'Level\s+([^;]+?)(?:;|$)', full_text, re.IGNORECASE)
        if level_pattern:
            level_text = level_pattern.group(1)
            # Her sınıf için level'ı bul - sadece geçerli class isimlerini kabul et
            valid_classes = [
                'alchemist', 'arcanist', 'bard', 'cleric', 'druid', 'inquisitor',
                'magus', 'oracle', 'paladin', 'ranger', 'sorcerer', 'summoner',
                'witch', 'wizard', 'antipaladin', 'bloodrager', 'hunter', 'investigator',
                'occultist', 'psychic', 'shaman', 'skald', 'warpriest', 'slayer',
                'swashbuckler', 'vigilante', 'brawler', 'cavalier', 'gunslinger',
                'samurai', 'ninja', 'rogue', 'fighter', 'barbarian', 'monk'
            ]
            
            # Pattern: "classname level" veya "classname/classname level"
            class_levels = re.findall(r'(\w+(?:/\w+)?)\s+(\d+)', level_text, re.IGNORECASE)
            for class_name, level in class_levels:
                # Class name'i normalize et ve kontrol et
                class_name_lower = class_name.lower().split('/')[0]  # "sorcerer/wizard" -> "sorcerer"
                if class_name_lower in valid_classes:
                    # Eğer "/" içeriyorsa, her iki class'a da ekle
                    if '/' in class_name:
                        for c in class_name.split('/'):
                            c_clean = c.strip().lower()
                            if c_clean in valid_classes:
                                spell_data["levels_by_class"][c.strip().capitalize()] = int(level)
                    else:
                        spell_data["levels_by_class"][class_name.capitalize()] = int(level)
            
            # İlk geçerli level'ı genel level olarak kullan
            if spell_data["levels_by_class"]:
                spell_data["level"] = list(spell_data["levels_by_class"].values())[0]
        
        # SCHOOL
        school_patterns = [
            r'School\s+([^;]+?)(?:;|$)',
            r'(\w+)\s+\[([^\]]+)\]',  # "Evocation [fire]"
        ]
        for pattern in school_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                school_text = match.group(1).strip()
                # School ve subschool'u ayır
                if '[' in school_text:
                    parts = school_text.split('[')
                    spell_data["school"] = parts[0].strip()
                    if len(parts) > 1:
                        spell_data["subschool"] = parts[1].replace(']', '').strip()
                else:
                    spell_data["school"] = school_text
                break
        
        # CASTING TIME - IYILESTIRILMIS PARSING (Duzeltme: "actionComponents" gibi birlestik metinler icin)
        # Pattern: "Casting Time" veya "1 standard actionComponents" gibi birlestik metin
        casting_patterns = [
            r'Casting Time\s+([^C]+?)(?:Components?|Effect|Range|Target|Area|Duration|$)',  # Components'ten once dur
            r'(?:^|\s)(\d+\s+(?:standard|move|full-round|swift|immediate|free)\s+action[^CEARTDS]*?)(?:Components?|Effect|Range|Target|Area|Duration|$)',  # Direkt action pattern
        ]
        for pattern in casting_patterns:
            casting_match = re.search(pattern, full_text, re.IGNORECASE)
            if casting_match:
                ct_text = casting_match.group(1).strip()
                # "action" kelimesinden sonra gelen harfleri temizle (örn: "actionComponents" -> "action")
                ct_text = re.sub(r'(action)[A-Z].*', r'\1', ct_text)
                spell_data["casting_time"] = ct_text
                break
        
        # COMPONENTS - IYILESTIRILMIS PARSING
        # Pattern: "Components V, S, DF" veya "V, S, DFEffect" gibi birlestik metin
        components_patterns = [
            r'Components?\s+([^EARTDS]+?)(?:Effect|Range|Target|Area|Duration|Saving|Spell|$)',  # Effect/Range/Target/Area/Duration'dan once dur
            r'(?:Components?\s+|^)([VSMDF,\s]+?)(?:Effect|Range|Target|Area|Duration|Saving|Spell|$)',  # Direkt V, S, M, D, F pattern
        ]
        for pattern in components_patterns:
            components_match = re.search(pattern, full_text, re.IGNORECASE)
            if components_match:
                comp_text = components_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "DFEffect" -> "DF")
                comp_text = re.sub(r'([VSMDF,\s]+?)([A-Z][a-z]+)', r'\1', comp_text)
                spell_data["components"] = comp_text
                
                # Material components'i ayir
                if 'M' in comp_text or 'material' in comp_text.lower():
                    material_match = re.search(r'M[,\s]*\(([^)]+)\)', comp_text, re.IGNORECASE)
                    if material_match:
                        spell_data["material_components"] = material_match.group(1).strip()
                
                # Focus'u ayir
                if 'F' in comp_text or 'focus' in comp_text.lower():
                    focus_match = re.search(r'F[,\s]*\(([^)]+)\)', comp_text, re.IGNORECASE)
                    if focus_match:
                        spell_data["focus"] = focus_match.group(1).strip()
                break
        
        # RANGE - IYILESTIRILMIS PARSING
        # Pattern: "Range touchTarget" gibi birlestik metin
        range_patterns = [
            r'Range\s+([^TEDAS]+?)(?:Target|Effect|Area|Duration|Saving|Spell|Description|$)',  # Target/Effect/Area/Duration'dan once dur
            r'(?:Range\s+|^)(touch|close|medium|long|unlimited|personal|see text|[0-9]+[^TEDAS]*?)(?:Target|Effect|Area|Duration|Saving|Spell|$)',  # Direkt range pattern
        ]
        for pattern in range_patterns:
            range_match = re.search(pattern, full_text, re.IGNORECASE)
            if range_match:
                range_text = range_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "touchTarget" -> "touch")
                range_text = re.sub(r'([a-z]+)([A-Z][a-z]+)', r'\1', range_text)
                spell_data["range"] = range_text
                break
        
        # AREA / TARGET / EFFECT - IYILESTIRILMIS PARSING
        target_patterns = [
            r'Target\s+([^EDAS]+?)(?:Effect|Duration|Area|Saving|Spell|Description|$)',  # Effect/Duration/Area'dan once dur
        ]
        for pattern in target_patterns:
            target_match = re.search(pattern, full_text, re.IGNORECASE)
            if target_match:
                target_text = target_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "creature touchedDuration" -> "creature touched")
                target_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', target_text)
                spell_data["target"] = target_text
                break
        
        area_patterns = [
            r'Area\s+([^TEDAS]+?)(?:Target|Effect|Duration|Saving|Spell|Description|$)',  # Target/Effect/Duration'dan once dur
        ]
        for pattern in area_patterns:
            area_match = re.search(pattern, full_text, re.IGNORECASE)
            if area_match:
                area_text = area_match.group(1).strip()
                area_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', area_text)
                spell_data["area"] = area_text
                break
        
        effect_patterns = [
            r'Effect\s+([^TEDAS]+?)(?:Target|Duration|Area|Saving|Spell|Description|$)',  # Target/Duration/Area'dan once dur
        ]
        for pattern in effect_patterns:
            effect_match = re.search(pattern, full_text, re.IGNORECASE)
            if effect_match:
                effect_text = effect_match.group(1).strip()
                effect_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', effect_text)
                spell_data["effect"] = effect_text
                break
        
        # DURATION - IYILESTIRILMIS PARSING
        # Pattern: "Duration 1 min./levelSaving" gibi birlestik metin
        duration_patterns = [
            r'Duration\s+([^STEDAS]+?)(?:Saving|Spell|Target|Effect|Area|Description|$)',  # Saving/Spell/Target/Effect/Area'dan once dur
        ]
        for pattern in duration_patterns:
            duration_match = re.search(pattern, full_text, re.IGNORECASE)
            if duration_match:
                duration_text = duration_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "1 min./levelSaving" -> "1 min./level")
                duration_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', duration_text)
                spell_data["duration"] = duration_text
                break
        
        # SAVING THROW - IYILESTIRILMIS PARSING
        saving_patterns = [
            r'Saving Throw\s+([^STEDAS]+?)(?:Spell|Target|Effect|Duration|Area|Description|$)',  # Spell/Target/Effect/Duration/Area'dan once dur
        ]
        for pattern in saving_patterns:
            saving_match = re.search(pattern, full_text, re.IGNORECASE)
            if saving_match:
                saving_text = saving_match.group(1).strip()
                saving_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', saving_text)
                spell_data["saving_throw"] = saving_text
                break
        
        # SPELL RESISTANCE - IYILESTIRILMIS PARSING
        sr_patterns = [
            r'Spell Resistance\s+([^STEDAS]+?)(?:Description|Target|Effect|Duration|Area|Saving|$)',  # Description/Target/Effect/Duration/Area'dan once dur
        ]
        for pattern in sr_patterns:
            sr_match = re.search(pattern, full_text, re.IGNORECASE)
            if sr_match:
                sr_text = sr_match.group(1).strip()
                sr_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', sr_text)
                spell_data["spell_resistance"] = sr_text
                break
        
        # DESCRIPTION - Daha iyi parsing
        # Önce meta description'ı kontrol et
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            spell_data["description"] = meta_desc.get('content')
        else:
            # Ana içerikten description'ı bul
            desc_section = soup.find('div', class_=re.compile(r'description|text|content', re.I))
            if not desc_section:
                # "Description" başlığından sonraki içeriği bul
                desc_header = soup.find(string=re.compile(r'^Description$', re.I))
                if desc_header:
                    parent = desc_header.find_parent()
                    if parent:
                        next_elem = parent.find_next_sibling(['p', 'div'])
                        if next_elem:
                            desc_section = next_elem
            
            if desc_section:
                desc_text = desc_section.get_text(strip=True)
                # İlk birkaç paragrafı al (çok uzun olmasın)
                paragraphs = desc_text.split('\n\n')[:3]
                spell_data["description"] = '\n\n'.join(paragraphs)
        
        return spell_data
    
    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tüm verileri çek ve birleştir"""
        print(f"Pathfinder 1e verileri cekiliyor ({self.base_url})...")
        print("Bu islem birkac dakika surebilir. Lutfen bekleyin...\n")
        
        data = {
            "system": "PATHFINDER_1E",
            "races": self.scrape_races(),
            "classes": self.scrape_classes(),
            "feats": self.scrape_feats(),
            "spells": self.scrape_spells(),
            "items": {}  # Ekipman için ayrı bir fonksiyon eklenebilir
        }
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\nOK: Veriler kaydedildi: {output_file}")
        
        return data


def _merge_dict_deep(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    İki dict'i derinlemesine birleştir (recursive merge).
    Primary önceliklidir, secondary eksikleri tamamlar.
    
    Args:
        primary: Birincil dict (öncelikli)
        secondary: İkincil dict (tamamlayıcı)
    
    Returns:
        Birleştirilmiş dict
    """
    result = primary.copy()
    
    for key, value in secondary.items():
        if key not in result:
            # Yeni key, direkt ekle
            result[key] = value
        else:
            # Var olan key, merge et
            existing = result[key]
            
            if isinstance(value, dict) and isinstance(existing, dict):
                # Nested dict'leri recursive merge et
                result[key] = _merge_dict_deep(existing, value)
            elif isinstance(value, list) and isinstance(existing, list):
                # Listeleri birleştir (duplicate'leri kaldırarak)
                merged_list = existing.copy()
                for item in value:
                    if item not in merged_list:
                        merged_list.append(item)
                result[key] = merged_list
            elif not existing or existing == "" or existing == [] or existing == {}:
                # Primary'de boş/eksik, secondary'den doldur
                result[key] = value
            elif isinstance(value, str) and isinstance(existing, str):
                # String'ler için: daha uzun veya daha detaylı olanı seç
                if len(value) > len(existing) * 1.2:  # %20 daha uzunsa
                    result[key] = value
                # Aksi halde primary'deki kalır
    
    return result


def _merge_category_data(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bir kategori için (örneğin races, classes) iki veri setini birleştir.
    Primary önceliklidir, secondary eksikleri tamamlar.
    
    Args:
        primary: Birincil kategori verisi (öncelikli)
        secondary: İkincil kategori verisi (tamamlayıcı)
    
    Returns:
        Birleştirilmiş kategori verisi
    """
    merged = {}
    
    # Primary'den tüm öğeleri al
    merged.update(primary)
    
    # Secondary'den eksik öğeleri ekle veya mevcut olanları geliştir
    for key, value in secondary.items():
        if key not in merged:
            # Yeni öğe, direkt ekle
            merged[key] = value
        else:
            # Var olan öğe, derinlemesine merge et
            existing = merged[key]
            if isinstance(value, dict) and isinstance(existing, dict):
                merged[key] = _merge_dict_deep(existing, value)
            elif isinstance(value, list) and isinstance(existing, list):
                # Listeleri birleştir (duplicate'leri kaldırarak)
                merged_list = existing.copy()
                for item in value:
                    if item not in merged_list:
                        merged_list.append(item)
                merged[key] = merged_list
            elif not existing or existing == "" or existing == [] or existing == {}:
                # Primary'de boş/eksik, secondary'den doldur
                merged[key] = value
    
    return merged


def scrape_pathfinder_data(site: str = "aonprd", output_dir: Path = None, merge_sites: bool = False) -> Path:
    """
    Pathfinder 1e verilerini çek ve kaydet
    
    Args:
        site: Kullanılacak site ("aonprd" veya "d20pfsrd") veya "both" (her ikisi)
        output_dir: Çıktı dizini (None ise data/ klasörü)
        merge_sites: True ise her iki siteden de veri çekip birleştir
    
    Returns:
        Kaydedilen JSON dosyasının yolu
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[1] / "data"
    
    output_file = output_dir / "pathfinder_1e_data.json"
    
    if merge_sites or site == "both":
        # Her iki siteden de veri çek ve birleştir
        print("🔄 Her iki siteden veri çekiliyor ve birleştiriliyor...\n")
        
        # Önce Archives of Nethys'ten çek (daha resmi)
        print("=" * 60)
        print("📚 1. Archives of Nethys (aonprd.com)")
        print("=" * 60)
        scraper_aon = PathfinderScraper(site="aonprd")
        data_aon = scraper_aon.scrape_all(output_file=None)
        
        print("\n" + "=" * 60)
        print("📚 2. d20pfsrd.com")
        print("=" * 60)
        scraper_d20 = PathfinderScraper(site="d20pfsrd")
        data_d20 = scraper_d20.scrape_all(output_file=None)
        
        # Verileri birleştir (aonprd öncelikli)
        print("\n" + "=" * 60)
        print("🔗 Veriler birleştiriliyor...")
        print("=" * 60)
        
        # Her kategori için birleştirme yap
        merged_races = _merge_category_data(data_aon.get("races", {}), data_d20.get("races", {}))
        merged_classes = _merge_category_data(data_aon.get("classes", {}), data_d20.get("classes", {}))
        merged_feats = _merge_category_data(data_aon.get("feats", {}), data_d20.get("feats", {}))
        merged_spells = _merge_category_data(data_aon.get("spells", {}), data_d20.get("spells", {}))
        merged_items = _merge_category_data(data_aon.get("items", {}), data_d20.get("items", {}))
        
        merged_data = {
            "system": "PATHFINDER_1E",
            "source": "merged (aonprd + d20pfsrd)",
            "races": merged_races,
            "classes": merged_classes,
            "feats": merged_feats,
            "spells": merged_spells,
            "items": merged_items
        }
        
        # İstatistikler
        print(f"\n📊 Birleştirme İstatistikleri:")
        print(f"   Irklar: {len(merged_data['races'])} (aonprd: {len(data_aon.get('races', {}))}, d20pfsrd: {len(data_d20.get('races', {}))})")
        print(f"   Sınıflar: {len(merged_data['classes'])} (aonprd: {len(data_aon.get('classes', {}))}, d20pfsrd: {len(data_d20.get('classes', {}))})")
        print(f"   Feat'ler: {len(merged_data['feats'])} (aonprd: {len(data_aon.get('feats', {}))}, d20pfsrd: {len(data_d20.get('feats', {}))})")
        print(f"   Büyüler: {len(merged_data['spells'])} (aonprd: {len(data_aon.get('spells', {}))}, d20pfsrd: {len(data_d20.get('spells', {}))})")
        
        # Kaydet
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"\nOK: Birlestirilmis veriler kaydedildi: {output_file}")
        
    else:
        # Tek siteden çek
        scraper = PathfinderScraper(site=site)
        scraper.scrape_all(output_file=output_file)
    
    return output_file


if __name__ == "__main__":
    # Test için
    import sys
    site = sys.argv[1] if len(sys.argv) > 1 else "aonprd"
    print(f"Test: {site} sitesinden veri çekiliyor...")
    scrape_pathfinder_data(site=site)


Sınıflar, ırklar, feat'ler, büyüler ve diğer kuralları web'den çeker.
"""

import json
import time
import re
from pathlib import Path
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse
import requests
from bs4 import BeautifulSoup


class PathfinderScraper:
    """Pathfinder 1e verilerini web'den çeken scraper"""
    
    # Desteklenen siteler
    SITES = {
        "aonprd": {
            "base_url": "https://aonprd.com",
            "races_url": "/Races.aspx",
            "classes_url": "/Classes.aspx",
            "feats_url": "/Feats.aspx",
            "spells_url": "/Spells.aspx",
            "items_url": "/Equipment.aspx"
        },
        "d20pfsrd": {
            "base_url": "https://www.d20pfsrd.com",
            "races_url": "/races/",
            "classes_url": "/classes/",
            "feats_url": "/feats/",
            "spells_url": "/spells/",
            "items_url": "/equipment/"
        }
    }
    
    def __init__(self, site: str = "aonprd", delay: float = 1.0):
        """
        Args:
            site: Kullanılacak site ("aonprd" veya "d20pfsrd")
            delay: İstekler arası bekleme süresi (saniye) - siteyi yormamak için
        """
        if site not in self.SITES:
            raise ValueError(f"Desteklenmeyen site: {site}. Desteklenenler: {list(self.SITES.keys())}")
        
        self.site_config = self.SITES[site]
        self.base_url = self.site_config["base_url"]
        self.delay = delay
        self.session = requests.Session()
        self.session.headers.update({
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        })
    
    def _get(self, url: str, retries: int = 3) -> Optional[BeautifulSoup]:
        """URL'den HTML içeriğini çek ve BeautifulSoup nesnesi döndür"""
        full_url = urljoin(self.base_url, url) if not url.startswith("http") else url
        
        for attempt in range(retries):
            try:
                time.sleep(self.delay)  # Rate limiting
                response = self.session.get(full_url, timeout=30)
                response.raise_for_status()
                return BeautifulSoup(response.content, 'html.parser')
            except requests.RequestException as e:
                if attempt == retries - 1:
                    print(f"ERROR: {full_url} - {e}")
                    return None
                time.sleep(2 ** attempt)  # Exponential backoff
        
        return None
    
    def scrape_races(self) -> Dict[str, Any]:
        """Tüm ırkları çek"""
        print("🏃 Irklar çekiliyor...")
        races = {}
        
        # Site yapısına göre parse et
        if "aonprd" in self.base_url:
            # Archives of Nethys yapısı - Core ve NonCore kategorilerini çek
            for category in ["Core", "NonCore"]:
                url = f"{self.site_config['races_url']}?Category={category}"
                soup = self._get(url)
                if not soup:
                    continue
                
                # RacesDisplay.aspx linklerini bul (Display değil, RacesDisplay!)
                race_links = soup.find_all('a', href=re.compile(r'RacesDisplay\.aspx\?ItemName='))
                for link in race_links:
                    race_name = link.get_text(strip=True)
                    if race_name and race_name not in races:
                        href = link.get('href', '')
                        # Göreceli URL'yi tam URL'ye çevir
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        race_data = self._scrape_race_detail(href)
                        if race_data:
                            races[race_name] = race_data
                            print(f"  ✓ {race_name}")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - ana sayfadan tüm ırk linklerini bul
            soup = self._get(self.site_config["races_url"])
            if soup:
                # /races/core-races/ veya /races/advanced-races/ gibi linkleri bul
                race_links = soup.find_all('a', href=re.compile(r'/races/[^/]+/[^/]+$'))
                seen_races = set()
                for link in race_links:
                    href = link.get('href', '')
                    race_name = link.get_text(strip=True)
                    # Duplicate'leri önle
                    if href and href not in seen_races and race_name:
                        seen_races.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        race_data = self._scrape_race_detail(href)
                        if race_data:
                            races[race_name] = race_data
                            print(f"  ✓ {race_name}")
        
        print(f"OK: {len(races)} irk cekildi")
        return races
    
    def _scrape_race_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir ırkın detay sayfasını çek - GELİŞTİRİLMİŞ VERSİYON"""
        soup = self._get(url)
        if not soup:
            return None
        
        race_data = {
            "ability_score_increase": {},
            "ability_score_increase_text": "",  # "+2 to One Ability Score" gibi metin
            "speed": 30,
            "speed_special": "",  # "30 feet" veya "30 feet, swim 30 feet" gibi
            "traits": [],  # Trait isimleri ve açıklamaları
            "traits_detailed": {},  # Her trait için detaylı bilgi
            "languages": [],
            "languages_automatic": [],  # Otomatik diller
            "languages_bonus": [],  # Bonus dil seçenekleri
            "size": "Medium",
            "source": url,
            "type": "",  # Humanoid, Outsider, etc.
            "subtype": "",  # Subtype bilgisi
            "favored_class_bonus": "",  # Favored class bonus açıklaması
            "favored_classes": [],  # Favored class'lar
            "vision": "normal",  # normal, low-light, darkvision, etc.
            "vision_range": 0,  # Darkvision range
            "skill_bonuses": {},  # Skill bonusları
            "weapon_proficiencies": [],  # Weapon proficiencies
            "armor_proficiencies": [],  # Armor proficiencies
            "racial_spells": [],  # Racial spell-like abilities
            "spell_resistance": None,  # Spell resistance
            "description": ""  # Irk açıklaması
        }
        
        # Tüm metni al
        full_text = soup.get_text()
        
        # Ana içerik alanını bul
        main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
        if main_content:
            full_text = main_content.get_text()
        
        # ABILITY SCORE INCREASES - Geliştirilmiş parsing
        # Pattern 1: "+2 to One Ability Score" (Human gibi)
        one_ability_pattern = re.search(r'\+(\d+)\s+to\s+One\s+Ability\s+Score', full_text, re.IGNORECASE)
        if one_ability_pattern:
            bonus = int(one_ability_pattern.group(1))
            race_data["ability_score_increase_text"] = f"+{bonus} to One Ability Score"
            race_data["ability_score_increase"] = {"any": bonus}
        
        # Pattern 2: "+2 Str, +2 Con" veya "+2 Strength, +2 Constitution"
        if not race_data["ability_score_increase"]:
            ability_patterns = [
                (r'\+(\d+)\s+(?:Str|Strength)', "strength"),
                (r'\+(\d+)\s+(?:Dex|Dexterity)', "dexterity"),
                (r'\+(\d+)\s+(?:Con|Constitution)', "constitution"),
                (r'\+(\d+)\s+(?:Int|Intelligence)', "intelligence"),
                (r'\+(\d+)\s+(?:Wis|Wisdom)', "wisdom"),
                (r'\+(\d+)\s+(?:Cha|Charisma)', "charisma"),
            ]
            
            for pattern, ability in ability_patterns:
                matches = re.findall(pattern, full_text, re.IGNORECASE)
                if matches:
                    # En yüksek bonus'u al
                    max_bonus = max(int(m) for m in matches)
                    race_data["ability_score_increase"][ability] = max_bonus
                    if not race_data["ability_score_increase_text"]:
                        race_data["ability_score_increase_text"] = f"+{max_bonus} {ability.capitalize()}"
                    else:
                        race_data["ability_score_increase_text"] += f", +{max_bonus} {ability.capitalize()}"
        
        # SIZE
        size_patterns = [
            r'Size\s*:?\s*(\w+)',
            r'(\w+)\s+size',
        ]
        for pattern in size_patterns:
            size_match = re.search(pattern, full_text, re.IGNORECASE)
            if size_match:
                size = size_match.group(1).capitalize()
                if size.lower() in ["small", "medium", "large", "tiny", "diminutive", "fine", "huge", "gargantuan", "colossal"]:
                    race_data["size"] = size
                    break
        
        # SPEED - Geliştirilmiş
        speed_match = re.search(r'Speed\s*:?\s*([^\n]+?)(?:\n|$)', full_text, re.IGNORECASE)
        if speed_match:
            speed_text = speed_match.group(1).strip()
            # Sayısal değeri bul
            speed_num_match = re.search(r'(\d+)', speed_text)
            if speed_num_match:
                race_data["speed"] = int(speed_num_match.group(1))
            race_data["speed_special"] = speed_text[:200]
        
        # LANGUAGES - Düzeltilmiş parsing
        # Archives of Nethys'te Languages genellikle <strong>Languages</strong> şeklinde
        lang_header = soup.find('strong', string=re.compile(r'^Languages?$', re.I))
        if not lang_header:
            lang_header = soup.find('b', string=re.compile(r'^Languages?$', re.I))
        
        if lang_header:
            # Sonraki içeriği bul (aynı veya sonraki p/div)
            lang_content = ""
            
            # Önce parent'ı kontrol et
            parent = lang_header.find_parent(['p', 'div'])
            if parent:
                # Parent içindeki tüm metni al, ama "Languages" başlığını çıkar
                parent_text = parent.get_text()
                lang_content = parent_text.replace(lang_header.get_text(), "").strip()
            
            # Eğer parent'ta yeterli bilgi yoksa, sonraki sibling'leri kontrol et
            if not lang_content or len(lang_content) < 20:
                next_elem = lang_header.find_next_sibling(['p', 'div'])
                if next_elem:
                    lang_content = next_elem.get_text(strip=True)
            
            if lang_content:
                # "Automatic" ve "Bonus" bölümlerini ayır
                auto_match = re.search(r'(?:Automatic|begin play speaking|speak)\s*:?\s*([^.]*?)(?:\.|Bonus|$)', lang_content, re.IGNORECASE | re.DOTALL)
                bonus_match = re.search(r'(?:Bonus\s+Languages?|bonus languages?)\s*:?\s*([^.]*)', lang_content, re.IGNORECASE)
                
                if auto_match:
                    auto_text = auto_match.group(1)
                    # Dil isimlerini ayır (Common, Elven, Draconic, etc.)
                    # Büyük harfle başlayan kelimeleri bul (dil isimleri genellikle büyük harfle başlar)
                    auto_langs = []
                    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', auto_text)
                    known_languages = ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Giant', 'Draconic', 'Gnoll', 
                                     'Halfling', 'Gnome', 'Sylvan', 'Aquan', 'Auran', 'Ignan', 'Terran', 'Celestial',
                                     'Infernal', 'Abyssal', 'Aklo', 'Undercommon', 'Jotun', 'Tengu', 'Varisian',
                                     'Kelish', 'Vudrani', 'Osiriani', 'Tien', 'Taldane', 'Skald', 'Chelish']
                    for word in words:
                        # Bilinen dil isimlerini kontrol et veya benzer olanları bul
                        if any(known in word for known in known_languages) or word in known_languages:
                            if word not in auto_langs:
                                auto_langs.append(word)
                    
                    # Eğer pattern ile bulamadıysak, "speaking X" veya "X and Y" formatını dene
                    if not auto_langs:
                        # "speaking Common and Elven" gibi formatları bul
                        speaking_match = re.search(r'speaking\s+([^.]+)', lang_content, re.IGNORECASE)
                        if speaking_match:
                            speaking_text = speaking_match.group(1)
                            # "and", "or" ile ayrılmış dilleri bul
                            langs = re.split(r'\s+(?:and|or)\s+', speaking_text)
                            for lang in langs:
                                lang = lang.strip()
                                if lang and len(lang) < 30 and lang[0].isupper():
                                    auto_langs.append(lang)
                    
                    race_data["languages_automatic"] = auto_langs[:10]
                
                if bonus_match:
                    bonus_text = bonus_match.group(1)
                    # Bonus dilleri ayır
                    bonus_langs = []
                    words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)?)\b', bonus_text)
                    known_languages = ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Giant', 'Draconic', 'Gnoll',
                                     'Halfling', 'Gnome', 'Sylvan', 'Aquan', 'Auran', 'Ignan', 'Terran']
                    for word in words:
                        if any(known in word for known in known_languages) or word in known_languages:
                            if word not in bonus_langs:
                                bonus_langs.append(word)
                    race_data["languages_bonus"] = bonus_langs[:20]
                
                # Eğer otomatik/bonus bulunamadıysa, genel "Languages" içeriğinden çıkar
                if not race_data["languages_automatic"] and not race_data["languages_bonus"]:
                    # Basit pattern: "speaking X" veya "X, Y, and Z"
                    speaking_match = re.search(r'(?:speaking|speak)\s+([^.]{1,100})', lang_content, re.IGNORECASE)
                    if speaking_match:
                        speaking_text = speaking_match.group(1)
                        # Virgülle veya "and" ile ayrılmış dilleri bul
                        langs = re.split(r'[,;]\s*|\s+and\s+|\s+or\s+', speaking_text)
                        auto_langs = []
                        for lang in langs:
                            lang = lang.strip()
                            # Büyük harfle başlayan, bilinen dil isimleri
                            if lang and len(lang) < 30 and lang[0].isupper():
                                # Bilinen dillere benzer mi kontrol et
                                if any(known.lower() in lang.lower() or lang.lower() in known.lower() 
                                      for known in ['Common', 'Elven', 'Dwarven', 'Goblin', 'Orc', 'Draconic']):
                                    if lang not in auto_langs:
                                        auto_langs.append(lang)
                        if auto_langs:
                            race_data["languages_automatic"] = auto_langs[:10]
                
                # Genel languages listesi
                race_data["languages"] = race_data["languages_automatic"] + race_data["languages_bonus"][:5]
        
        # RACIAL TRAITS - Düzeltilmiş parsing (Archives of Nethys)
        if "aonprd" in self.base_url:
            # Archives of Nethys'te asıl racial traits <strong> veya <b> etiketlerinde
            # Sadece belirli anahtar kelimeleri içeren trait başlıklarını bul
            racial_trait_keywords = [
                'speed', 'feat', 'skilled', 'vision', 'immunity', 'trait', 'weapon', 'armor', 
                'spell', 'resistance', 'bonus', 'proficiency', 'skill', 'movement', 'racial',
                'low-light', 'darkvision', 'blindsight', 'tremorsense', 'keen senses', 'senses'
            ]
            
            # Genel başlıkları hariç tut (bunlar racial trait değil)
            exclude_keywords = [
                'source', 'languages', 'language', 'physical', 'society', 'relations', 
                'alignment', 'religion', 'adventurers', 'description', 'name', 'size',
                'type', 'subtype', 'favored class', 'racial traits', 'alternate'
            ]
            
            # <strong> ve <b> etiketlerini bul
            strong_tags = soup.find_all(['strong', 'b'])
            for tag in strong_tags:
                trait_name = tag.get_text(strip=True)
                
                # Genel başlıkları atla
                if any(exc.lower() in trait_name.lower() for exc in exclude_keywords):
                    continue
                
                # Trait başlığı mı kontrol et
                is_racial_trait = False
                
                # Anahtar kelime kontrolü
                if any(keyword.lower() in trait_name.lower() for keyword in racial_trait_keywords):
                    is_racial_trait = True
                
                # Kısa başlıklar da trait olabilir (ama uzun olmasın)
                elif len(trait_name) < 30 and len(trait_name) > 2:
                    # Sayı içermeyen, sadece harf içeren başlıklar genellikle trait'tir
                    if re.match(r'^[A-Z][a-z]+(?:\s+[A-Z][a-z]+)*$', trait_name):
                        # Ama genel başlıkları atla
                        if trait_name.lower() not in exclude_keywords:
                            is_racial_trait = True
                
                if is_racial_trait:
                    # Sonraki içeriği bul
                    trait_content = ""
                    
                    # Parent içindeki içeriği kontrol et
                    parent = tag.find_parent(['p', 'div'])
                    if parent:
                        parent_text = parent.get_text()
                        # Tag'dan sonraki kısmı al
                        parts = parent_text.split(trait_name, 1)
                        if len(parts) > 1:
                            after_trait = parts[1].strip()
                            # ":" işaretinden sonraki ilk cümleyi al
                            if ':' in after_trait:
                                after_trait = after_trait.split(':', 1)[1].strip()
                            # İlk cümleyi al (nokta, yeni satır veya başka trait öncesi)
                            trait_content = re.split(r'[.\n](?=\s*[A-Z])|(?=\n\s*[A-Z][a-z]+\s*:)', after_trait)[0].strip()
                            trait_content = trait_content[:300]  # Maksimum uzunluk
                    
                    # Eğer parent'ta yeterli içerik yoksa, sonraki sibling'i kontrol et
                    if not trait_content or len(trait_content) < 10:
                        next_elem = tag.find_next_sibling(['p', 'div'])
                        if next_elem:
                            if hasattr(next_elem, 'get_text'):
                                trait_text = next_elem.get_text(strip=True)
                                # İlk cümleyi al
                                trait_content = re.split(r'[.\n](?=\s*[A-Z])', trait_text)[0].strip()[:300]
                    
                    # İçerik varsa ve anlamlıysa ekle
                    if trait_content and len(trait_content) > 5 and len(trait_content) < 500:
                        # Duplicate kontrolü ve anlamlılık kontrolü
                        # Çok kısa veya çok genel içerikleri atla
                        # Sınıf isimlerini atla (bunlar favored class bonus, trait değil)
                        if (trait_name not in race_data["traits"] and 
                            len(trait_content) > 10 and
                            not any(exc.lower() in trait_content.lower()[:50] for exc in ['source', 'pg.', 'page']) and
                            trait_name not in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 
                                              'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 
                                              'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                                              'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                                              'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                                              'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']):
                            race_data["traits"].append(trait_name)
                            race_data["traits_detailed"][trait_name] = trait_content[:300]
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - dt/dd yapısı
            dl_tags = soup.find_all('dl')
            for dl in dl_tags:
                dt_tags = dl.find_all('dt')
                for dt in dt_tags:
                    term = dt.get_text(strip=True)
                    dd = dt.find_next_sibling('dd')
                    if dd and term and len(term) < 100:
                        definition = dd.get_text(strip=True)
                        if definition and len(definition) > 10:
                            # Sınıf isimlerini atla (bunlar favored class bonus, trait değil)
                            if term not in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler',
                                          'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter',
                                          'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                                          'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                                          'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                                          'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']:
                                race_data["traits"].append(term)
                                race_data["traits_detailed"][term] = definition[:500]
        
        # VISION - Traits parsing'inden SONRA yapılmalı (vision genellikle bir trait olarak geliyor)
        # Önce traits listesinde vision trait'ini ara - SADECE ASIL RACIAL TRAITS'ten (ilk 5-10 trait)
        # Alternatif traits'i atla (bunlar genellikle sayfanın sonunda gelir)
        core_traits = race_data.get("traits", [])[:10]  # İlk 10 trait'i al (asıl racial traits genellikle başta)
        
        # İlk birkaç trait'in gerçekten asıl racial trait olup olmadığını kontrol et
        # (Medium, Normal Speed, Bonus Feat gibi)
        core_racial_trait_keywords = ['medium', 'small', 'large', 'speed', 'feat', 'skilled', 'vision', 
                                     'immunity', 'magic', 'resistance', 'weapon', 'armor', 'movement']
        
        # Eğer ilk trait'lerde bu anahtar kelimeler varsa, bunlar asıl traits'tir
        # Alternatif traits genellikle bu anahtar kelimeleri içermez veya daha sonra gelir
        for trait_name in core_traits:
            trait_name_lower = trait_name.lower()
            
            # Alternatif trait kontrolü - eğer trait ismi bir sınıf ismi gibi görünüyorsa (Alchemist, Bard, etc.)
            # veya çok uzunsa, bu alternatif trait olabilir
            if (trait_name in ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 'Cavalier',
                              'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 'Inquisitor', 'Investigator',
                              'Kineticist', 'Magus', 'Mesmerist', 'Monk', 'Occultist', 'Oracle', 'Paladin',
                              'Psychic', 'Ranger', 'Rogue', 'Shaman', 'Shifter', 'Skald', 'Slayer', 'Sorcerer',
                              'Spiritualist', 'Summoner', 'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']):
                continue  # Bu bir favored class bonus, trait değil
            
            # Vision trait'ini ara
            if 'low-light' in trait_name_lower or ('vision' in trait_name_lower and 'low' in trait_name_lower):
                # Ama bu trait'in alternate trait olmadığından emin ol
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                # Eğer trait detail "replaces" içeriyorsa, bu alternatif trait'tir, atla
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                race_data["vision"] = "low-light"
                race_data["vision_range"] = 0
                break
            elif 'darkvision' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                # Alternate trait kontrolü
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "darkvision"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 60
                break
            elif 'blindsight' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "blindsight"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                break
            elif 'tremorsense' in trait_name_lower:
                trait_detail = race_data.get("traits_detailed", {}).get(trait_name, "")
                if 'replaces' in trait_detail.lower() or 'in place of' in trait_detail.lower():
                    continue
                range_match = re.search(r'(\d+)\s+feet', trait_detail, re.IGNORECASE)
                race_data["vision"] = "tremorsense"
                race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                break
        
        # Eğer traits listesinde bulunamadıysa, <strong> tag'lerinde direkt ara (backup)
        if race_data["vision"] == "normal":
            vision_strong = soup.find(['strong', 'b'], string=re.compile(r'^(?:Low-light\s+Vision|Darkvision|Blindsight|Tremorsense)$', re.I))
            if vision_strong:
                vision_text = vision_strong.get_text(strip=True)
                parent = vision_strong.find_parent(['p', 'div'])
                if parent:
                    parent_text = parent.get_text()
                    # "Alternate" veya "variant" kelimesi varsa, bu alternate trait'tir, atla
                    if not re.search(r'alternate|variant|optional', parent_text[:200], re.IGNORECASE):
                        if 'Darkvision' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "darkvision"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 60
                        elif 'Low-light' in vision_text:
                            race_data["vision"] = "low-light"
                            race_data["vision_range"] = 0
                        elif 'Blindsight' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "blindsight"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
                        elif 'Tremorsense' in vision_text:
                            range_match = re.search(r'(\d+)\s+feet', parent_text, re.IGNORECASE)
                            race_data["vision"] = "tremorsense"
                            race_data["vision_range"] = int(range_match.group(1)) if range_match else 30
        
        # FAVORED CLASS - Düzeltilmiş parsing
        # Favored class genellikle "Favored Class: Any" veya belirli class'lar şeklinde
        favored_patterns = [
            r'Favored\s+Class\s*:?\s*([^\n]+?)(?:\n|$)',
            r'Favored\s+Classes?\s*:?\s*([^\n]+?)(?:\n|$)',
        ]
        
        favored_text = ""
        for pattern in favored_patterns:
            favored_match = re.search(pattern, full_text, re.IGNORECASE)
            if favored_match:
                favored_text = favored_match.group(1).strip()
                break
        
        # Eğer regex ile bulunamadıysa, <strong>Favored Class</strong> etiketini ara
        if not favored_text:
            favored_strong = soup.find(['strong', 'b'], string=re.compile(r'^Favored\s+Class', re.I))
            if favored_strong:
                parent = favored_strong.find_parent(['p', 'div'])
                if parent:
                    parent_text = parent.get_text()
                    # "Favored Class" başlığından sonraki içeriği al
                    parts = parent_text.split(favored_strong.get_text(strip=True), 1)
                    if len(parts) > 1:
                        favored_text = parts[1].strip().split('\n')[0].strip()[:200]
        
        if favored_text:
            race_data["favored_class_bonus"] = favored_text[:200]
            
            # Favored class'ları ayır
            # "Any" ise tüm sınıflar
            if 'any' in favored_text.lower():
                race_data["favored_classes"] = ["Any"]
            else:
                # Belirli sınıf isimlerini bul
                known_classes = ['Alchemist', 'Arcanist', 'Barbarian', 'Bard', 'Bloodrager', 'Brawler', 
                               'Cavalier', 'Cleric', 'Druid', 'Fighter', 'Gunslinger', 'Hunter', 
                               'Inquisitor', 'Investigator', 'Kineticist', 'Magus', 'Mesmerist', 'Monk',
                               'Occultist', 'Oracle', 'Paladin', 'Psychic', 'Ranger', 'Rogue', 'Shaman',
                               'Shifter', 'Skald', 'Slayer', 'Sorcerer', 'Spiritualist', 'Summoner',
                               'Swashbuckler', 'Vigilante', 'Warpriest', 'Witch', 'Wizard']
                
                found_classes = []
                for class_name in known_classes:
                    if class_name.lower() in favored_text.lower():
                        found_classes.append(class_name)
                
                if found_classes:
                    race_data["favored_classes"] = found_classes
                else:
                    # Virgülle ayrılmış sınıf isimlerini dene
                    classes = [c.strip() for c in re.split(r'[,;]', favored_text) if c.strip() and len(c.strip()) < 30]
                    race_data["favored_classes"] = classes[:10]
        
        # SPELL RESISTANCE
        sr_match = re.search(r'Spell\s+Resistance\s*:?\s*(\d+)', full_text, re.IGNORECASE)
        if sr_match:
            race_data["spell_resistance"] = int(sr_match.group(1))
        
        # DESCRIPTION - Düzeltilmiş parsing
        # Önce meta description tag'ini kontrol et (genellikle orada olur)
        meta_desc = soup.find('meta', attrs={'name': 'description'}) or soup.find('meta', attrs={'property': 'og:description'})
        if meta_desc and meta_desc.get('content'):
            desc_content = meta_desc.get('content', '').strip()
            if len(desc_content) > 100:
                # HTML entity'leri temizle
                desc_content = desc_content.replace('&lt;br /&gt;', ' ').replace('&quot;', '"').replace('&amp;', '&')
                desc_content = re.sub(r'<[^>]+>', '', desc_content)  # HTML tag'lerini temizle
                # İlk cümleyi al (genellikle en önemli kısım)
                first_sentence = re.split(r'[.\n]', desc_content)[0].strip()
                if len(first_sentence) > 50:
                    race_data["description"] = first_sentence[:500]
                else:
                    race_data["description"] = desc_content[:500]
        
        # Eğer meta tag'de bulunamadıysa, başlıktan sonraki ilk paragrafı bul
        if not race_data["description"]:
            # H1 başlığını bul
            h1 = soup.find('h1', class_='title') or soup.find('h1')
            if h1:
                # Başlıktan sonraki ilk anlamlı paragrafı bul
                current = h1.find_next(['p', 'div'])
                count = 0
                while current and count < 5:
                    if hasattr(current, 'get_text'):
                        text = current.get_text(strip=True)
                        # Uzun ve anlamlı bir paragraf mı kontrol et
                        if (len(text) > 100 and 
                            not any(keyword in text.lower() for keyword in ['source', 'pg.', 'page', 'inner sea races', 'advanced race guide', 'core rulebook']) and
                            not re.match(r'^[A-Z][a-z]+\s+Source', text) and
                            'possess' in text.lower() or 'are' in text.lower() or 'have' in text.lower()):
                            # İlk cümleyi al
                            first_sentence = re.split(r'[.\n](?=\s*[A-Z])', text)[0].strip()
                            if len(first_sentence) > 50:
                                race_data["description"] = first_sentence[:500]
                            else:
                                race_data["description"] = text[:500]
                            break
                    current = current.find_next(['p', 'div'])
                    count += 1
        
        # Eğer hala bulunamadıysa, tüm paragrafları tara
        if not race_data["description"]:
            desc_paragraphs = soup.find_all('p')
            for p in desc_paragraphs[:15]:
                text = p.get_text(strip=True)
                # "possess", "are", "have" gibi kelimeler içeren, uzun paragraflar genellikle description'dur
                if (len(text) > 150 and 
                    not any(keyword in text.lower() for keyword in ['source', 'pg.', 'page', 'inner sea races', 'advanced race guide', 'core rulebook']) and
                    not re.match(r'^[A-Z][a-z]+\s+Source', text) and
                    any(keyword in text.lower() for keyword in ['possess', 'are currently', 'have', 'characterized', 'society', 'culture'])):
                    # İlk cümleyi al
                    first_sentence = re.split(r'[.\n](?=\s*[A-Z])', text)[0].strip()
                    if len(first_sentence) > 50:
                        race_data["description"] = first_sentence[:500]
                    else:
                        race_data["description"] = text[:500]
                    break
        
        return race_data
    
    def _parse_race_from_section(self, section) -> Optional[Dict[str, Any]]:
        """HTML section'dan ırk verisini parse et"""
        # d20pfsrd için özel parsing
        race_data = {
            "ability_score_increase": {},
            "speed": 30,
            "traits": [],
            "languages": [],
            "size": "Medium"
        }
        
        text = section.get_text()
        
        # Ability scores
        matches = re.findall(r'\+(\d+)\s+(\w+)', text)
        for bonus, ability in matches:
            ability_lower = ability.lower()
            if ability_lower in ["str", "strength"]:
                race_data["ability_score_increase"]["strength"] = int(bonus)
            elif ability_lower in ["dex", "dexterity"]:
                race_data["ability_score_increase"]["dexterity"] = int(bonus)
        
        return race_data
    
    def scrape_classes(self) -> Dict[str, Any]:
        """Tüm sınıfları çek"""
        print("⚔️ Sınıflar çekiliyor...")
        classes = {}
        
        # Site yapısına göre parse et
        if "aonprd" in self.base_url:
            # Archives of Nethys - Ana sayfadan tüm sınıfları çek
            soup = self._get(self.site_config["classes_url"])
            if soup:
                # ClassDisplay.aspx linklerini bul (ClassesDisplay değil, ClassDisplay!)
                class_links = soup.find_all('a', href=re.compile(r'ClassDisplay\.aspx\?ItemName='))
                # Ayrıca ClassesDisplay pattern'ini de kontrol et
                if not class_links:
                    class_links = soup.find_all('a', href=re.compile(r'ClassesDisplay\.aspx\?ItemName='))
                # Son çare: href'inde Class geçen ve Display geçen linkler
                if not class_links:
                    all_links = soup.find_all('a', href=True)
                    class_links = [l for l in all_links if 'Class' in l.get('href', '') and 'Display' in l.get('href', '')]
                
                for link in class_links:
                    class_name = link.get_text(strip=True)
                    if class_name and class_name not in classes and len(class_name) > 2:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        class_data = self._scrape_class_detail(href)
                        if class_data:
                            classes[class_name] = class_data
                            print(f"  ✓ {class_name}")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd yapısı - /classes/ altındaki linkleri bul
            soup = self._get(self.site_config["classes_url"])
            if soup:
                # /classes/core-classes/ veya /classes/base-classes/ gibi linkleri bul
                class_links = soup.find_all('a', href=re.compile(r'/classes/[^/]+/[^/]+$'))
                seen_classes = set()
                for link in class_links:
                    href = link.get('href', '')
                    class_name = link.get_text(strip=True)
                    if href and href not in seen_classes and class_name:
                        seen_classes.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        class_data = self._scrape_class_detail(href)
                        if class_data:
                            classes[class_name] = class_data
                            print(f"  ✓ {class_name}")
        
        print(f"OK: {len(classes)} sinif cekildi")
        return classes
    
    def _scrape_class_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir sınıfın detay sayfasını çek"""
        soup = self._get(url)
        if not soup:
            return None
        
        class_data = {
            "hit_die": "d8",
            "skill_ranks_per_level": 2,
            "class_skills": [],
            "proficiencies": [],
            "spellcasting": False,
            "features": {},
            "source": url
        }
        
        full_text = soup.get_text()
        
        # Hit Die - daha kapsamlı pattern
        hit_die_patterns = [
            r'Hit Die[:\s]+d(\d+)',
            r'Hit Dice[:\s]+d(\d+)',
            r'd(\d+)\s+Hit Die',
        ]
        for pattern in hit_die_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                class_data["hit_die"] = f"d{match.group(1)}"
                break
        
        # Skill Ranks Per Level
        skill_ranks_match = re.search(r'Skill Ranks[:\s]+(\d+)', full_text, re.IGNORECASE)
        if skill_ranks_match:
            class_data["skill_ranks_per_level"] = int(skill_ranks_match.group(1))
        
        # Class Skills - daha iyi parsing
        skills_section = soup.find(string=re.compile(r'Class Skills?', re.I))
        if skills_section:
            parent = skills_section.find_parent()
            # Sonraki paragraf veya liste
            next_elem = parent.find_next(['p', 'ul', 'ol', 'div'])
            if next_elem:
                skills_text = next_elem.get_text()
                # Virgülle ayrılmış skill'leri bul
                skills = [s.strip() for s in re.split(r'[,;]', skills_text) if s.strip() and len(s.strip()) < 30]
                class_data["class_skills"] = skills[:30]  # İlk 30 skill
        
        # Spellcasting - daha kapsamlı kontrol
        spellcasting_indicators = [
            r'Spellcasting',
            r'Spells per Day',
            r'Spell List',
            r'Caster Level',
        ]
        for indicator in spellcasting_indicators:
            if re.search(indicator, full_text, re.IGNORECASE):
                class_data["spellcasting"] = True
                break
        
        # Proficiencies
        prof_section = soup.find(string=re.compile(r'Proficiencies?', re.I))
        if prof_section:
            parent = prof_section.find_parent()
            next_elem = parent.find_next(['p', 'ul', 'ol'])
            if next_elem:
                prof_text = next_elem.get_text()
                proficiencies = [p.strip() for p in re.split(r'[,;]', prof_text) if p.strip()]
                class_data["proficiencies"] = proficiencies[:20]
        
        return class_data
    
    def _parse_class_from_section(self, section) -> Optional[Dict[str, Any]]:
        """HTML section'dan sınıf verisini parse et"""
        class_data = {
            "hit_die": "d8",
            "skill_ranks_per_level": 2,
            "class_skills": [],
            "proficiencies": [],
            "spellcasting": False,
            "features": {}
        }
        
        text = section.get_text()
        
        # Hit Die
        match = re.search(r'd(\d+)', text)
        if match:
            class_data["hit_die"] = f"d{match.group(1)}"
        
        return class_data
    
    def scrape_feats(self) -> Dict[str, Any]:
        """Tüm feat'leri çek"""
        print("⭐ Feat'ler çekiliyor...")
        feats = {}
        
        if "aonprd" in self.base_url:
            # Archives of Nethys - Feats.aspx sayfasından kategorileri çek
            soup = self._get(self.site_config["feats_url"])
            if soup:
                # Önce kategori linklerini bul (Feats.aspx?Category=...)
                category_links = soup.find_all('a', href=re.compile(r'Feats\.aspx\?Category='))
                categories = []
                for link in category_links:
                    href = link.get('href', '')
                    if 'Category=' in href and href not in categories:
                        # Boş kategoriyi atla
                        if href != 'Feats.aspx?Category=':
                            categories.append(href)
                
                print(f"  Bulunan kategori sayısı: {len(categories)}")
                
                # Her kategori sayfasından feat'leri çek
                for category_path in categories:
                    # URL'yi düzelt
                    if category_path.startswith('/'):
                        category_url = urljoin(self.base_url, category_path)
                    elif not category_path.startswith('http'):
                        category_url = urljoin(self.base_url + '/', category_path)
                    else:
                        category_url = category_path
                    
                    cat_soup = self._get(category_url)
                    if cat_soup:
                        # FeatsDisplay.aspx linklerini bul
                        feat_links = cat_soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx\?ItemName='))
                        for link in feat_links:
                            feat_name = link.get_text(strip=True)
                            if feat_name and feat_name not in feats and len(feat_name) > 1:
                                href = link.get('href', '')
                                if not href.startswith('http'):
                                    href = urljoin(self.base_url, href)
                                feat_data = self._scrape_feat_detail(href)
                                if feat_data:
                                    feats[feat_name] = feat_data
                                    if len(feats) % 50 == 0:
                                        print(f"  ... {len(feats)} feat çekildi")
                
                # Ana sayfadan da direkt linkleri kontrol et (eğer varsa)
                feat_links = soup.find_all('a', href=re.compile(r'FeatsDisplay\.aspx\?ItemName='))
                for link in feat_links:
                    feat_name = link.get_text(strip=True)
                    if feat_name and feat_name not in feats:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        feat_data = self._scrape_feat_detail(href)
                        if feat_data:
                            feats[feat_name] = feat_data
                            if len(feats) % 50 == 0:
                                print(f"  ... {len(feats)} feat çekildi")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd - /feats/ altındaki linkleri bul
            soup = self._get(self.site_config["feats_url"])
            if soup:
                # /feats/ altındaki linkleri bul
                feat_links = soup.find_all('a', href=re.compile(r'/feats/[^/]+/[^/]+$'))
                seen_feats = set()
                for link in feat_links:
                    href = link.get('href', '')
                    feat_name = link.get_text(strip=True)
                    if href and href not in seen_feats and feat_name:
                        seen_feats.add(href)
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        feat_data = self._scrape_feat_detail(href)
                        if feat_data:
                            feats[feat_name] = feat_data
                            if len(feats) % 10 == 0:
                                print(f"  ... {len(feats)} feat çekildi")
        
        print(f"OK: {len(feats)} feat cekildi")
        return feats
    
    def _scrape_feat_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir feat'in detay sayfasını çek"""
        if not url:
            return None
        
        soup = self._get(url)
        if not soup:
            return None
        
        feat_data = {
            "prerequisites": [],
            "benefit": "",
            "normal": "",
            "special": ""
        }
        
        # Prerequisites
        prereq_section = soup.find(string=re.compile(r'Prerequisite', re.I))
        if prereq_section:
            parent = prereq_section.find_parent()
            if parent:
                text = parent.get_text()
                feat_data["prerequisites"] = [t.strip() for t in text.split(',')]
        
        # Benefit
        benefit_section = soup.find(string=re.compile(r'Benefit', re.I))
        if benefit_section:
            parent = benefit_section.find_parent()
            if parent:
                feat_data["benefit"] = parent.get_text(strip=True)
        
        return feat_data
    
    def scrape_spells(self, max_spells: int = 500) -> Dict[str, Any]:
        """Büyüleri çek (max_spells ile limit)"""
        print(f"Spells cekiliyor (max {max_spells})...")
        spells = {}
        
        if "aonprd" in self.base_url:
            # Archives of Nethys - "All Spells" sayfasındaki tablodan çek
            all_spells_url = urljoin(self.base_url, "Spells.aspx?Class=All")
            all_soup = self._get(all_spells_url)
            
            if all_soup:
                # Tablo içindeki linkleri bul
                tables = all_soup.find_all('table')
                spell_links = []
                
                for table in tables:
                    # Tablo içindeki tüm linkleri bul
                    table_links = table.find_all('a', href=True)
                    # SpellsDisplay içeren veya spell içeren linkleri filtrele
                    for link in table_links:
                        href = link.get('href', '')
                        if 'SpellsDisplay' in href or ('Spell' in href and 'ItemName=' in href):
                            spell_links.append(link)
                
                # Eğer tablo içinde bulamadıysak, tüm sayfada ara
                if not spell_links:
                    spell_links = all_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx\?ItemName='))
                
                print(f"  'All Spells' sayfasında {len(spell_links)} büyü linki bulundu")
                
                for link in spell_links:
                    if len(spells) >= max_spells:
                        break
                    spell_name = link.get_text(strip=True)
                    if spell_name and spell_name not in spells and len(spell_name) > 1:
                        href = link.get('href', '')
                        if not href.startswith('http'):
                            href = urljoin(self.base_url, href)
                        spell_data = self._scrape_spell_detail(href)
                        if spell_data:
                            spells[spell_name] = spell_data
                            if len(spells) % 50 == 0:
                                print(f"  ... {len(spells)} büyü çekildi")
                
                # Eğer yeterli büyü çekilmediyse, diğer sınıf sayfalarını kontrol et
                if len(spells) < max_spells:
                    # Ana sayfadan sınıf linklerini bul
                    class_links = all_soup.find_all('a', href=re.compile(r'Spells\.aspx\?Class='))
                    seen_classes = set()
                    
                    for link in class_links:
                        if len(spells) >= max_spells:
                            break
                        
                        href = link.get('href', '')
                        if href and 'Class=' in href and href not in seen_classes:
                            seen_classes.add(href)
                            
                            if not href.startswith('http'):
                                category_url = urljoin(self.base_url, href)
                            else:
                                category_url = href
                            
                            cat_soup = self._get(category_url)
                            if cat_soup:
                                spell_links = cat_soup.find_all('a', href=re.compile(r'SpellsDisplay\.aspx\?ItemName='))
                                for link in spell_links:
                                    if len(spells) >= max_spells:
                                        break
                                    spell_name = link.get_text(strip=True)
                                    if spell_name and spell_name not in spells:
                                        href = link.get('href', '')
                                        if not href.startswith('http'):
                                            href = urljoin(self.base_url, href)
                                        spell_data = self._scrape_spell_detail(href)
                                        if spell_data:
                                            spells[spell_name] = spell_data
                                            if len(spells) % 50 == 0:
                                                print(f"  ... {len(spells)} büyü çekildi")
        
        elif "d20pfsrd" in self.base_url:
            # d20pfsrd - /magic/all-spells/ sayfası + A-Z alt sayfalarından çek
            spells_list_url = urljoin(self.base_url, "/magic/all-spells/")
            soup = self._get(spells_list_url)
            
            if soup:
                seen_spells = set()
                letter_pages = set()
                
                # A-Z alt sayfalarını bul (örn: /magic/all-spells/a/)
                for link in soup.find_all('a', href=True):
                    href = link.get('href', '')
                    if re.match(r'/magic/all-spells/[a-z0-9-]+/?$', href) and href != "/magic/all-spells/":
                        letter_pages.add(href)
                
                if not letter_pages:
                    letter_pages.add("/magic/all-spells/")
                
                print(f"  {len(letter_pages)} harf/alt sayfa bulundu")
                
                for letter_href in sorted(letter_pages):
                    if len(spells) >= max_spells:
                        break
                    
                    page_url = urljoin(self.base_url, letter_href)
                    letter_soup = self._get(page_url)
                    if not letter_soup:
                        continue
                    
                    # Spell linkleri: /magic/all-spells/a/acid-arrow/
                    spell_links = letter_soup.find_all(
                        'a',
                        href=re.compile(r'/magic/all-spells/[a-z0-9-]+/.+/$', re.IGNORECASE)
                    )
                    print(f"  {letter_href}: {len(spell_links)} potansiyel büyü linki")
                    
                    for link in spell_links:
                        if len(spells) >= max_spells:
                            break
                        
                        href = link.get('href', '')
                        spell_name = link.get_text(strip=True)
                        
                        if href and href not in seen_spells and spell_name and len(spell_name) > 2:
                            seen_spells.add(href)
                            if not href.startswith('http'):
                                href = urljoin(self.base_url, href)
                            
                            spell_data = self._scrape_spell_detail(href)
                            if spell_data:
                                spells[spell_name] = spell_data
                                if len(spells) % 50 == 0:
                                    print(f"  ... {len(spells)} büyü çekildi")
        
        print(f"OK: {len(spells)} spell cekildi")
        return spells
    
    def _scrape_spell_detail(self, url: str) -> Optional[Dict[str, Any]]:
        """Belirli bir büyünün detay sayfasını çek - GELİŞTİRİLMİŞ VERSİYON"""
        if not url:
            return None
        
        soup = self._get(url)
        if not soup:
            return None
        
        spell_data = {
            "level": 0,
            "levels_by_class": {},  # {"Wizard": 1, "Cleric": 2, ...}
            "school": "",
            "subschool": "",
            "descriptor": "",
            "casting_time": "",
            "components": "",
            "material_components": "",
            "focus": "",
            "range": "",
            "area": "",
            "target": "",
            "effect": "",
            "duration": "",
            "saving_throw": "",
            "spell_resistance": "",
            "description": "",
            "source": url
        }
        
        # Tüm metni al
        full_text = soup.get_text()
        
        # Ana içerik alanını bul
        main_content = soup.find('div', id='main') or soup.find('div', class_='content') or soup.find('body')
        if main_content:
            full_text = main_content.get_text()
        
        # LEVEL - IYILESTIRILMIS PARSING (Duzeltme: yanlis parse'lar icin)
        # Pattern 1: "Level bard 1, cleric 2, wizard 1"
        level_pattern = re.search(r'Level\s+([^;]+?)(?:;|$)', full_text, re.IGNORECASE)
        if level_pattern:
            level_text = level_pattern.group(1)
            # Her sınıf için level'ı bul - sadece geçerli class isimlerini kabul et
            valid_classes = [
                'alchemist', 'arcanist', 'bard', 'cleric', 'druid', 'inquisitor',
                'magus', 'oracle', 'paladin', 'ranger', 'sorcerer', 'summoner',
                'witch', 'wizard', 'antipaladin', 'bloodrager', 'hunter', 'investigator',
                'occultist', 'psychic', 'shaman', 'skald', 'warpriest', 'slayer',
                'swashbuckler', 'vigilante', 'brawler', 'cavalier', 'gunslinger',
                'samurai', 'ninja', 'rogue', 'fighter', 'barbarian', 'monk'
            ]
            
            # Pattern: "classname level" veya "classname/classname level"
            class_levels = re.findall(r'(\w+(?:/\w+)?)\s+(\d+)', level_text, re.IGNORECASE)
            for class_name, level in class_levels:
                # Class name'i normalize et ve kontrol et
                class_name_lower = class_name.lower().split('/')[0]  # "sorcerer/wizard" -> "sorcerer"
                if class_name_lower in valid_classes:
                    # Eğer "/" içeriyorsa, her iki class'a da ekle
                    if '/' in class_name:
                        for c in class_name.split('/'):
                            c_clean = c.strip().lower()
                            if c_clean in valid_classes:
                                spell_data["levels_by_class"][c.strip().capitalize()] = int(level)
                    else:
                        spell_data["levels_by_class"][class_name.capitalize()] = int(level)
            
            # İlk geçerli level'ı genel level olarak kullan
            if spell_data["levels_by_class"]:
                spell_data["level"] = list(spell_data["levels_by_class"].values())[0]
        
        # SCHOOL
        school_patterns = [
            r'School\s+([^;]+?)(?:;|$)',
            r'(\w+)\s+\[([^\]]+)\]',  # "Evocation [fire]"
        ]
        for pattern in school_patterns:
            match = re.search(pattern, full_text, re.IGNORECASE)
            if match:
                school_text = match.group(1).strip()
                # School ve subschool'u ayır
                if '[' in school_text:
                    parts = school_text.split('[')
                    spell_data["school"] = parts[0].strip()
                    if len(parts) > 1:
                        spell_data["subschool"] = parts[1].replace(']', '').strip()
                else:
                    spell_data["school"] = school_text
                break
        
        # CASTING TIME - IYILESTIRILMIS PARSING (Duzeltme: "actionComponents" gibi birlestik metinler icin)
        # Pattern: "Casting Time" veya "1 standard actionComponents" gibi birlestik metin
        casting_patterns = [
            r'Casting Time\s+([^C]+?)(?:Components?|Effect|Range|Target|Area|Duration|$)',  # Components'ten once dur
            r'(?:^|\s)(\d+\s+(?:standard|move|full-round|swift|immediate|free)\s+action[^CEARTDS]*?)(?:Components?|Effect|Range|Target|Area|Duration|$)',  # Direkt action pattern
        ]
        for pattern in casting_patterns:
            casting_match = re.search(pattern, full_text, re.IGNORECASE)
            if casting_match:
                ct_text = casting_match.group(1).strip()
                # "action" kelimesinden sonra gelen harfleri temizle (örn: "actionComponents" -> "action")
                ct_text = re.sub(r'(action)[A-Z].*', r'\1', ct_text)
                spell_data["casting_time"] = ct_text
                break
        
        # COMPONENTS - IYILESTIRILMIS PARSING
        # Pattern: "Components V, S, DF" veya "V, S, DFEffect" gibi birlestik metin
        components_patterns = [
            r'Components?\s+([^EARTDS]+?)(?:Effect|Range|Target|Area|Duration|Saving|Spell|$)',  # Effect/Range/Target/Area/Duration'dan once dur
            r'(?:Components?\s+|^)([VSMDF,\s]+?)(?:Effect|Range|Target|Area|Duration|Saving|Spell|$)',  # Direkt V, S, M, D, F pattern
        ]
        for pattern in components_patterns:
            components_match = re.search(pattern, full_text, re.IGNORECASE)
            if components_match:
                comp_text = components_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "DFEffect" -> "DF")
                comp_text = re.sub(r'([VSMDF,\s]+?)([A-Z][a-z]+)', r'\1', comp_text)
                spell_data["components"] = comp_text
                
                # Material components'i ayir
                if 'M' in comp_text or 'material' in comp_text.lower():
                    material_match = re.search(r'M[,\s]*\(([^)]+)\)', comp_text, re.IGNORECASE)
                    if material_match:
                        spell_data["material_components"] = material_match.group(1).strip()
                
                # Focus'u ayir
                if 'F' in comp_text or 'focus' in comp_text.lower():
                    focus_match = re.search(r'F[,\s]*\(([^)]+)\)', comp_text, re.IGNORECASE)
                    if focus_match:
                        spell_data["focus"] = focus_match.group(1).strip()
                break
        
        # RANGE - IYILESTIRILMIS PARSING
        # Pattern: "Range touchTarget" gibi birlestik metin
        range_patterns = [
            r'Range\s+([^TEDAS]+?)(?:Target|Effect|Area|Duration|Saving|Spell|Description|$)',  # Target/Effect/Area/Duration'dan once dur
            r'(?:Range\s+|^)(touch|close|medium|long|unlimited|personal|see text|[0-9]+[^TEDAS]*?)(?:Target|Effect|Area|Duration|Saving|Spell|$)',  # Direkt range pattern
        ]
        for pattern in range_patterns:
            range_match = re.search(pattern, full_text, re.IGNORECASE)
            if range_match:
                range_text = range_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "touchTarget" -> "touch")
                range_text = re.sub(r'([a-z]+)([A-Z][a-z]+)', r'\1', range_text)
                spell_data["range"] = range_text
                break
        
        # AREA / TARGET / EFFECT - IYILESTIRILMIS PARSING
        target_patterns = [
            r'Target\s+([^EDAS]+?)(?:Effect|Duration|Area|Saving|Spell|Description|$)',  # Effect/Duration/Area'dan once dur
        ]
        for pattern in target_patterns:
            target_match = re.search(pattern, full_text, re.IGNORECASE)
            if target_match:
                target_text = target_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "creature touchedDuration" -> "creature touched")
                target_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', target_text)
                spell_data["target"] = target_text
                break
        
        area_patterns = [
            r'Area\s+([^TEDAS]+?)(?:Target|Effect|Duration|Saving|Spell|Description|$)',  # Target/Effect/Duration'dan once dur
        ]
        for pattern in area_patterns:
            area_match = re.search(pattern, full_text, re.IGNORECASE)
            if area_match:
                area_text = area_match.group(1).strip()
                area_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', area_text)
                spell_data["area"] = area_text
                break
        
        effect_patterns = [
            r'Effect\s+([^TEDAS]+?)(?:Target|Duration|Area|Saving|Spell|Description|$)',  # Target/Duration/Area'dan once dur
        ]
        for pattern in effect_patterns:
            effect_match = re.search(pattern, full_text, re.IGNORECASE)
            if effect_match:
                effect_text = effect_match.group(1).strip()
                effect_text = re.sub(r'([a-z\s]+)([A-Z][a-z]+)', r'\1', effect_text)
                spell_data["effect"] = effect_text
                break
        
        # DURATION - IYILESTIRILMIS PARSING
        # Pattern: "Duration 1 min./levelSaving" gibi birlestik metin
        duration_patterns = [
            r'Duration\s+([^STEDAS]+?)(?:Saving|Spell|Target|Effect|Area|Description|$)',  # Saving/Spell/Target/Effect/Area'dan once dur
        ]
        for pattern in duration_patterns:
            duration_match = re.search(pattern, full_text, re.IGNORECASE)
            if duration_match:
                duration_text = duration_match.group(1).strip()
                # Sonraki kelimenin ilk harfini temizle (örn: "1 min./levelSaving" -> "1 min./level")
                duration_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', duration_text)
                spell_data["duration"] = duration_text
                break
        
        # SAVING THROW - IYILESTIRILMIS PARSING
        saving_patterns = [
            r'Saving Throw\s+([^STEDAS]+?)(?:Spell|Target|Effect|Duration|Area|Description|$)',  # Spell/Target/Effect/Duration/Area'dan once dur
        ]
        for pattern in saving_patterns:
            saving_match = re.search(pattern, full_text, re.IGNORECASE)
            if saving_match:
                saving_text = saving_match.group(1).strip()
                saving_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', saving_text)
                spell_data["saving_throw"] = saving_text
                break
        
        # SPELL RESISTANCE - IYILESTIRILMIS PARSING
        sr_patterns = [
            r'Spell Resistance\s+([^STEDAS]+?)(?:Description|Target|Effect|Duration|Area|Saving|$)',  # Description/Target/Effect/Duration/Area'dan once dur
        ]
        for pattern in sr_patterns:
            sr_match = re.search(pattern, full_text, re.IGNORECASE)
            if sr_match:
                sr_text = sr_match.group(1).strip()
                sr_text = re.sub(r'([^A-Z]+)([A-Z][a-z]+)', r'\1', sr_text)
                spell_data["spell_resistance"] = sr_text
                break
        
        # DESCRIPTION - Daha iyi parsing
        # Önce meta description'ı kontrol et
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            spell_data["description"] = meta_desc.get('content')
        else:
            # Ana içerikten description'ı bul
            desc_section = soup.find('div', class_=re.compile(r'description|text|content', re.I))
            if not desc_section:
                # "Description" başlığından sonraki içeriği bul
                desc_header = soup.find(string=re.compile(r'^Description$', re.I))
                if desc_header:
                    parent = desc_header.find_parent()
                    if parent:
                        next_elem = parent.find_next_sibling(['p', 'div'])
                        if next_elem:
                            desc_section = next_elem
            
            if desc_section:
                desc_text = desc_section.get_text(strip=True)
                # İlk birkaç paragrafı al (çok uzun olmasın)
                paragraphs = desc_text.split('\n\n')[:3]
                spell_data["description"] = '\n\n'.join(paragraphs)
        
        return spell_data
    
    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tüm verileri çek ve birleştir"""
        print(f"Pathfinder 1e verileri cekiliyor ({self.base_url})...")
        print("Bu islem birkac dakika surebilir. Lutfen bekleyin...\n")
        
        data = {
            "system": "PATHFINDER_1E",
            "races": self.scrape_races(),
            "classes": self.scrape_classes(),
            "feats": self.scrape_feats(),
            "spells": self.scrape_spells(),
            "items": {}  # Ekipman için ayrı bir fonksiyon eklenebilir
        }
        
        if output_file:
            output_file.parent.mkdir(parents=True, exist_ok=True)
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
            print(f"\nOK: Veriler kaydedildi: {output_file}")
        
        return data


def _merge_dict_deep(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    İki dict'i derinlemesine birleştir (recursive merge).
    Primary önceliklidir, secondary eksikleri tamamlar.
    
    Args:
        primary: Birincil dict (öncelikli)
        secondary: İkincil dict (tamamlayıcı)
    
    Returns:
        Birleştirilmiş dict
    """
    result = primary.copy()
    
    for key, value in secondary.items():
        if key not in result:
            # Yeni key, direkt ekle
            result[key] = value
        else:
            # Var olan key, merge et
            existing = result[key]
            
            if isinstance(value, dict) and isinstance(existing, dict):
                # Nested dict'leri recursive merge et
                result[key] = _merge_dict_deep(existing, value)
            elif isinstance(value, list) and isinstance(existing, list):
                # Listeleri birleştir (duplicate'leri kaldırarak)
                merged_list = existing.copy()
                for item in value:
                    if item not in merged_list:
                        merged_list.append(item)
                result[key] = merged_list
            elif not existing or existing == "" or existing == [] or existing == {}:
                # Primary'de boş/eksik, secondary'den doldur
                result[key] = value
            elif isinstance(value, str) and isinstance(existing, str):
                # String'ler için: daha uzun veya daha detaylı olanı seç
                if len(value) > len(existing) * 1.2:  # %20 daha uzunsa
                    result[key] = value
                # Aksi halde primary'deki kalır
    
    return result


def _merge_category_data(primary: Dict[str, Any], secondary: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bir kategori için (örneğin races, classes) iki veri setini birleştir.
    Primary önceliklidir, secondary eksikleri tamamlar.
    
    Args:
        primary: Birincil kategori verisi (öncelikli)
        secondary: İkincil kategori verisi (tamamlayıcı)
    
    Returns:
        Birleştirilmiş kategori verisi
    """
    merged = {}
    
    # Primary'den tüm öğeleri al
    merged.update(primary)
    
    # Secondary'den eksik öğeleri ekle veya mevcut olanları geliştir
    for key, value in secondary.items():
        if key not in merged:
            # Yeni öğe, direkt ekle
            merged[key] = value
        else:
            # Var olan öğe, derinlemesine merge et
            existing = merged[key]
            if isinstance(value, dict) and isinstance(existing, dict):
                merged[key] = _merge_dict_deep(existing, value)
            elif isinstance(value, list) and isinstance(existing, list):
                # Listeleri birleştir (duplicate'leri kaldırarak)
                merged_list = existing.copy()
                for item in value:
                    if item not in merged_list:
                        merged_list.append(item)
                merged[key] = merged_list
            elif not existing or existing == "" or existing == [] or existing == {}:
                # Primary'de boş/eksik, secondary'den doldur
                merged[key] = value
    
    return merged


def scrape_pathfinder_data(site: str = "aonprd", output_dir: Path = None, merge_sites: bool = False) -> Path:
    """
    Pathfinder 1e verilerini çek ve kaydet
    
    Args:
        site: Kullanılacak site ("aonprd" veya "d20pfsrd") veya "both" (her ikisi)
        output_dir: Çıktı dizini (None ise data/ klasörü)
        merge_sites: True ise her iki siteden de veri çekip birleştir
    
    Returns:
        Kaydedilen JSON dosyasının yolu
    """
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[1] / "data"
    
    output_file = output_dir / "pathfinder_1e_data.json"
    
    if merge_sites or site == "both":
        # Her iki siteden de veri çek ve birleştir
        print("🔄 Her iki siteden veri çekiliyor ve birleştiriliyor...\n")
        
        # Önce Archives of Nethys'ten çek (daha resmi)
        print("=" * 60)
        print("📚 1. Archives of Nethys (aonprd.com)")
        print("=" * 60)
        scraper_aon = PathfinderScraper(site="aonprd")
        data_aon = scraper_aon.scrape_all(output_file=None)
        
        print("\n" + "=" * 60)
        print("📚 2. d20pfsrd.com")
        print("=" * 60)
        scraper_d20 = PathfinderScraper(site="d20pfsrd")
        data_d20 = scraper_d20.scrape_all(output_file=None)
        
        # Verileri birleştir (aonprd öncelikli)
        print("\n" + "=" * 60)
        print("🔗 Veriler birleştiriliyor...")
        print("=" * 60)
        
        # Her kategori için birleştirme yap
        merged_races = _merge_category_data(data_aon.get("races", {}), data_d20.get("races", {}))
        merged_classes = _merge_category_data(data_aon.get("classes", {}), data_d20.get("classes", {}))
        merged_feats = _merge_category_data(data_aon.get("feats", {}), data_d20.get("feats", {}))
        merged_spells = _merge_category_data(data_aon.get("spells", {}), data_d20.get("spells", {}))
        merged_items = _merge_category_data(data_aon.get("items", {}), data_d20.get("items", {}))
        
        merged_data = {
            "system": "PATHFINDER_1E",
            "source": "merged (aonprd + d20pfsrd)",
            "races": merged_races,
            "classes": merged_classes,
            "feats": merged_feats,
            "spells": merged_spells,
            "items": merged_items
        }
        
        # İstatistikler
        print(f"\n📊 Birleştirme İstatistikleri:")
        print(f"   Irklar: {len(merged_data['races'])} (aonprd: {len(data_aon.get('races', {}))}, d20pfsrd: {len(data_d20.get('races', {}))})")
        print(f"   Sınıflar: {len(merged_data['classes'])} (aonprd: {len(data_aon.get('classes', {}))}, d20pfsrd: {len(data_d20.get('classes', {}))})")
        print(f"   Feat'ler: {len(merged_data['feats'])} (aonprd: {len(data_aon.get('feats', {}))}, d20pfsrd: {len(data_d20.get('feats', {}))})")
        print(f"   Büyüler: {len(merged_data['spells'])} (aonprd: {len(data_aon.get('spells', {}))}, d20pfsrd: {len(data_d20.get('spells', {}))})")
        
        # Kaydet
        output_file.parent.mkdir(parents=True, exist_ok=True)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(merged_data, f, ensure_ascii=False, indent=2)
        print(f"\nOK: Birlestirilmis veriler kaydedildi: {output_file}")
        
    else:
        # Tek siteden çek
        scraper = PathfinderScraper(site=site)
        scraper.scrape_all(output_file=output_file)
    
    return output_file


if __name__ == "__main__":
    # Test için
    import sys
    site = sys.argv[1] if len(sys.argv) > 1 else "aonprd"
    print(f"Test: {site} sitesinden veri çekiliyor...")
    scrape_pathfinder_data(site=site)

