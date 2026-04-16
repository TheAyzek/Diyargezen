"""
Pathfinder 1e Spell Scraper & Data Cleaner

Mevcut bozuk veriyi temizler ve AONPRD'den yeni spell verisi ceker.
Bozuk veri: casting_time, components, range, target, duration gibi alanlar
birbirine karismis durumda. Bu modul onlari ayristirir.
"""
import json
import re
import time
import html
from pathlib import Path
from typing import Dict, Any, Optional, List, Tuple

try:
    import requests
    from bs4 import BeautifulSoup
    HAS_SCRAPING_DEPS = True
except ImportError:
    HAS_SCRAPING_DEPS = False


# ============================================================================
# VERI TEMIZLEME FONKSIYONLARI
# Mevcut bozuk spell verisini ayristirma ve duzeltme
# ============================================================================

# Alan ayristirma kaliplari
FIELD_MARKERS = [
    "Components", "Component",
    "EffectRange", "Effect Range",
    "Range", "Area", "Target", "Targets", "Effect",
    "Duration",
    "Saving Throw", "Save",
    "Spell Resistance",
    "Description",
]

def _strip_html(text: str) -> str:
    """HTML etiketlerini temizle"""
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<[^>]+>', '', text)
    text = html.unescape(text)
    return text.strip()


def _extract_clean_field(raw_value: str, field_name: str) -> str:
    """
    Bozuk alan degerinden temiz degeri cikar.
    Ornegin:
    "1 standard actionComponents V, S, DFEffectRange touchTarget creature..."
    -> "1 standard action"
    """
    if not raw_value:
        return ""

    # Bilinen ayirici kaliplar - alan adinin kendisinden sonraki ilk marker'a kadar al
    for marker in FIELD_MARKERS:
        # Alan adinin kendisini atla
        if marker.lower() == field_name.lower():
            continue

        # Marker'i bul (buyuk/kucuk harf duyarsiz)
        pattern = re.compile(r'\b' + re.escape(marker) + r'\b', re.IGNORECASE)
        match = pattern.search(raw_value)
        if match:
            return raw_value[:match.start()].strip()

    # Hicbir marker bulunamazsa, Description'a kadar al
    desc_idx = raw_value.find("Description")
    if desc_idx > 0:
        return raw_value[:desc_idx].strip()

    return raw_value.strip()


def _extract_field_from_blob(blob: str, field_name: str) -> str:
    """
    Bir metin blogundan belirli bir alani cikar.
    Ornegin blob = "1 standard actionComponents V, S, DFEffectRange touchTarget creature touchedDuration 1 min..."
    field_name = "Components" -> "V, S, DF"
    """
    if not blob:
        return ""

    # Alan adini bul
    pattern = re.compile(re.escape(field_name) + r'\s*', re.IGNORECASE)
    match = pattern.search(blob)
    if not match:
        return ""

    # Alan adinden sonrasini al
    after = blob[match.end():]
    # Sonraki marker'a kadar al
    return _extract_clean_field(after, field_name)


def clean_spell_data(spell: Dict[str, Any]) -> Dict[str, Any]:
    """
    Bozuk bir spell verisini temizle.
    Birbirine karismis alanlari ayristir.
    """
    cleaned = {}

    # Temel alanlar (bozulmamis)
    cleaned["level"] = spell.get("level", 0)
    cleaned["school"] = spell.get("school", "")
    cleaned["subschool"] = spell.get("subschool", "")
    cleaned["descriptor"] = spell.get("descriptor", "")
    cleaned["source"] = spell.get("source", "")

    # levels_by_class - bozuk degerleri temizle
    levels_raw = spell.get("levels_by_class", {})
    cleaned_levels = {}
    for cls, lvl in levels_raw.items():
        # Bozuk degerler: "Time", "Touchedduration", "Youduration" vs. atla
        if isinstance(lvl, int) and lvl >= 0 and lvl <= 9:
            # Class ismi kontrol - bozuk class isimleri atla
            if cls.lower() not in ["time", "touchedduration", "youduration", "two", "than",
                                     "worth", "area", "effect", "range", "target", "targets",
                                     "duration", "components", "component", "description",
                                     "save", "saving", "spell", "resistance"]:
                cleaned_levels[cls] = lvl
    cleaned["levels_by_class"] = cleaned_levels

    # Birbirine karismis alanlar - en buyuk blob'dan ayristir
    # En iyi kaynak genellikle casting_time alani cunku ilk alan
    blob = spell.get("casting_time", "")

    # casting_time
    ct = _extract_clean_field(blob, "casting_time")
    if not ct or len(ct) > 100:
        ct_match = re.match(r'^(\d+\s+\w+\s+\w+)', blob)
        if ct_match:
            ct = ct_match.group(1)
        else:
            ct = blob[:50] if blob else ""
    for marker in ["Components", "Effect", "Range", "Target", "Duration", "Saving", "Description"]:
        idx = ct.find(marker)
        if idx > 0:
            ct = ct[:idx].strip()
            break
    cleaned["casting_time"] = ct

    # components
    comp = _extract_field_from_blob(blob, "Components")
    if not comp:
        comp = spell.get("components", "")
        comp = _extract_clean_field(comp, "components")
    if len(comp) > 200:
        # Genellikle V, S, M (...) formatinda
        comp_match = re.match(r'^(V(?:,\s*S)?(?:,\s*M\s*(?:\([^)]*\))?)?(?:,\s*(?:DF|F(?:\s*\([^)]*\))?))?)', comp)
        if comp_match:
            comp = comp_match.group(1)
    cleaned["components"] = comp

    # material_components - components'ten cikar
    mat = ""
    mat_match = re.search(r'M\s*(\([^)]+\))', cleaned["components"])
    if mat_match:
        mat = mat_match.group(1)
    cleaned["material_components"] = mat

    # focus
    focus_match = re.search(r'F\s*(\([^)]+\))', cleaned["components"])
    cleaned["focus"] = focus_match.group(1) if focus_match else ""

    # range
    rng = _extract_field_from_blob(blob, "Range")
    if not rng:
        rng = spell.get("range", "")
        rng = _extract_clean_field(rng, "range")
    if len(rng) > 100:
        # Sadece ilk satir/kelime grubunu al
        rng_match = re.match(r'^([\w\s/().]+?)(?:Target|Area|Effect|Duration)', rng)
        if rng_match:
            rng = rng_match.group(1).strip()
        else:
            rng = rng[:50]
    cleaned["range"] = rng

    # target
    tgt = _extract_field_from_blob(blob, "Target")
    if not tgt:
        tgt = spell.get("target", "")
        tgt = _extract_clean_field(tgt, "target")
    if len(tgt) > 200:
        tgt_match = re.match(r'^(.+?)(?:Duration|Saving|Description)', tgt)
        if tgt_match:
            tgt = tgt_match.group(1).strip()
        else:
            tgt = tgt[:100]
    cleaned["target"] = tgt

    # area
    area = _extract_field_from_blob(blob, "Area")
    if not area:
        area = spell.get("area", "")
    if len(area) > 200:
        area = area[:100]
    cleaned["area"] = area

    # effect
    eff = _extract_field_from_blob(blob, "Effect")
    if not eff:
        eff = spell.get("effect", "")
    # Effect alani cok buyukse kirp
    if len(eff) > 200:
        eff = eff[:100]
    cleaned["effect"] = eff

    # duration
    dur = _extract_field_from_blob(blob, "Duration")
    if not dur:
        dur = spell.get("duration", "")
        dur = _extract_clean_field(dur, "duration")
    if len(dur) > 150:
        dur_match = re.match(r'^(.+?)(?:Saving|Save|Description)', dur)
        if dur_match:
            dur = dur_match.group(1).strip()
        else:
            dur = dur[:60]
    cleaned["duration"] = dur

    # saving_throw
    st = _extract_field_from_blob(blob, "Saving Throw")
    if not st:
        st = spell.get("saving_throw", "")
        st = _extract_clean_field(st, "saving_throw")
    if len(st) > 100:
        st_match = re.match(r'^([\w\s]+(?:negates|half|partial|none|harmless)(?:\s*\([^)]*\))?)', st, re.IGNORECASE)
        if st_match:
            st = st_match.group(1).strip()
        else:
            st = st[:50]
    cleaned["saving_throw"] = st

    # spell_resistance
    sr = _extract_field_from_blob(blob, "Spell Resistance")
    if not sr:
        sr = spell.get("spell_resistance", "")
        sr = _extract_clean_field(sr, "spell_resistance")
    if len(sr) > 60:
        sr_match = re.match(r'^(yes|no)(?:\s*\([^)]*\))?', sr, re.IGNORECASE)
        if sr_match:
            sr = sr_match.group(0).strip()
        else:
            sr = sr[:30]
    cleaned["spell_resistance"] = sr

    # description - genellikle en temiz alan
    desc = spell.get("description", "")
    desc = _strip_html(desc)
    cleaned["description"] = desc

    return cleaned


def clean_all_spells(spells: Dict[str, Any]) -> Dict[str, Any]:
    """Tum spell'leri temizle"""
    cleaned_spells = {}
    for name, data in spells.items():
        try:
            cleaned_spells[name] = clean_spell_data(data)
        except Exception:
            # Hata olursa orijinal veriyi koru
            cleaned_spells[name] = data
    return cleaned_spells


# ============================================================================
# WEB SCRAPING FONKSIYONLARI
# AONPRD'den Pathfinder 1e spell verisi cekme
# ============================================================================

class PathfinderSpellScraper:
    """AONPRD'den Pathfinder 1e spell verisi ceker"""

    BASE_URL = "https://aonprd.com"
    SPELL_LIST_URL = "https://aonprd.com/Spells.aspx"
    SPELL_DISPLAY_URL = "https://aonprd.com/SpellDisplay.aspx"

    # Spell okullari
    SCHOOLS = [
        "abjuration", "conjuration", "divination", "enchantment",
        "evocation", "illusion", "necromancy", "transmutation", "universal"
    ]

    def __init__(self, delay: float = 1.0):
        """
        Args:
            delay: Istekler arasi bekleme suresi (saniye)
        """
        self.delay = delay
        self.session = requests.Session() if HAS_SCRAPING_DEPS else None
        if self.session:
            self.session.headers.update({
                'User-Agent': 'Diyargezer TTRPG Character Builder (educational)',
                'Accept': 'text/html,application/xhtml+xml'
            })

    def _get_page(self, url: str) -> Optional['BeautifulSoup']:
        """Sayfa cek ve parse et"""
        if not HAS_SCRAPING_DEPS or not self.session:
            return None
        try:
            resp = self.session.get(url, timeout=30)
            resp.raise_for_status()
            time.sleep(self.delay)
            return BeautifulSoup(resp.text, 'html.parser')
        except Exception:
            return None

    def scrape_spell_list(self, class_name: str = "", school: str = "") -> List[str]:
        """
        Spell listesini cek.
        Returns: Spell isimlerinin listesi
        """
        if not HAS_SCRAPING_DEPS:
            return []

        params = {}
        if class_name:
            params["Class"] = class_name
        if school:
            params["School"] = school

        url = f"{self.SPELL_LIST_URL}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        soup = self._get_page(url)
        if not soup:
            return []

        spell_names = []
        # AONPRD spell listesi genellikle table veya link listesi
        for link in soup.find_all('a', href=True):
            href = link['href']
            if 'SpellDisplay.aspx' in href:
                name = link.get_text(strip=True)
                if name and name not in spell_names:
                    spell_names.append(name)

        return spell_names

    def scrape_spell_detail(self, spell_name: str) -> Optional[Dict[str, Any]]:
        """
        Tek bir spell'in detaylarini cek.
        """
        if not HAS_SCRAPING_DEPS:
            return None

        url = f"{self.SPELL_DISPLAY_URL}?ItemName={requests.utils.quote(spell_name)}"
        soup = self._get_page(url)
        if not soup:
            return None

        spell_data = {
            "level": 0,
            "levels_by_class": {},
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
            "source": url,
        }

        # Ana icerik alanini bul
        content = soup.find('div', id='ctl00_MainContent_DataListTal498')
        if not content:
            content = soup.find('div', class_='stat-block-1')
        if not content:
            content = soup.find('span', id='ctl00_MainContent_DataListTal498')
        if not content:
            # Genel arama
            main = soup.find('div', id='main')
            content = main if main else soup

        text = content.get_text(separator='\n', strip=True) if content else ""

        # School parsing
        school_match = re.search(r'School\s+(\w+)(?:\s*\((\w+)\))?(?:\s*\[([^\]]+)\])?', text, re.IGNORECASE)
        if school_match:
            spell_data["school"] = school_match.group(1).lower()
            spell_data["subschool"] = (school_match.group(2) or "").lower()
            spell_data["descriptor"] = school_match.group(3) or ""

        # Level parsing
        level_match = re.search(r'Level\s+(.+?)(?:\n|Casting)', text, re.IGNORECASE)
        if level_match:
            level_str = level_match.group(1)
            # "Wizard 3, Cleric 3" formatini parse et
            for part in level_str.split(','):
                part = part.strip()
                cls_lvl = re.match(r'(\w[\w\s]*?)\s+(\d+)', part)
                if cls_lvl:
                    cls = cls_lvl.group(1).strip()
                    lvl = int(cls_lvl.group(2))
                    spell_data["levels_by_class"][cls] = lvl
                    if spell_data["level"] == 0:
                        spell_data["level"] = lvl

        # Diger alanlar
        field_patterns = {
            "casting_time": r'Casting Time\s+(.+?)(?:\n|Components)',
            "components": r'Components?\s+(.+?)(?:\n|Range|Effect|Target|Area)',
            "range": r'Range\s+(.+?)(?:\n|Target|Area|Effect|Duration)',
            "target": r'Target\s+(.+?)(?:\n|Duration|Saving|Area)',
            "area": r'Area\s+(.+?)(?:\n|Duration|Saving|Target)',
            "effect": r'Effect\s+(.+?)(?:\n|Duration|Saving|Range)',
            "duration": r'Duration\s+(.+?)(?:\n|Saving|Spell Resistance)',
            "saving_throw": r'Saving Throw\s+(.+?)(?:\n|Spell Resistance)',
            "spell_resistance": r'Spell Resistance\s+(.+?)(?:\n|Description|$)',
        }

        for field, pattern in field_patterns.items():
            match = re.search(pattern, text, re.IGNORECASE | re.DOTALL)
            if match:
                value = match.group(1).strip()
                if len(value) < 200:  # Makul uzunlukta ise al
                    spell_data[field] = value

        # Components'ten material ve focus cikar
        comp = spell_data["components"]
        mat_match = re.search(r'M\s*(\([^)]+\))', comp)
        if mat_match:
            spell_data["material_components"] = mat_match.group(1)
        focus_match = re.search(r'F\s*(\([^)]+\))', comp)
        if focus_match:
            spell_data["focus"] = focus_match.group(1)

        # Description
        desc_match = re.search(r'Description\s*\n?(.*)', text, re.DOTALL)
        if desc_match:
            spell_data["description"] = desc_match.group(1).strip()[:2000]

        return spell_data

    def scrape_spells_batch(
        self,
        spell_names: List[str],
        start_from: int = 0,
        batch_size: int = 50
    ) -> Dict[str, Any]:
        """
        Spell'leri batch halinde cek.
        
        Args:
            spell_names: Cekilecek spell isimleri
            start_from: Baslangic indeksi
            batch_size: Batch buyuklugu
        """
        results = {}
        end = min(start_from + batch_size, len(spell_names))

        for i in range(start_from, end):
            name = spell_names[i]
            spell = self.scrape_spell_detail(name)
            if spell:
                results[name] = spell

        return results

    def scrape_spells(self, max_spells: int = 500) -> Dict[str, Any]:
        """Spell'leri cek (legacy uyumluluk)"""
        if not HAS_SCRAPING_DEPS:
            return {}
        spell_names = self.scrape_spell_list()
        if not spell_names:
            return {}
        names = spell_names[:max_spells]
        return self.scrape_spells_batch(names, 0, max_spells)

    def scrape_all(self, output_file: Optional[Path] = None) -> Dict[str, Any]:
        """Tum verileri cek"""
        data = {"races": {}, "classes": {}, "feats": {}, "spells": {}}
        spells = self.scrape_spells()
        if spells:
            data["spells"] = spells
        if output_file:
            try:
                output_file.parent.mkdir(parents=True, exist_ok=True)
                with open(output_file, 'w', encoding='utf-8') as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            except Exception:
                pass
        return data


# Legacy uyumluluk
PathfinderScraper = PathfinderSpellScraper


def scrape_pathfinder_data(site: str = "aonprd", output_dir: Optional[Path] = None) -> Path:
    """Legacy uyumluluk fonksiyonu"""
    if output_dir is None:
        output_dir = Path(__file__).resolve().parents[1] / "data"
    out = output_dir / "pathfinder_1e_data.json"
    PathfinderSpellScraper().scrape_all(output_file=out)
    return out


# ============================================================================
# MEVCUT VERIYI TEMIZLE VE KAYDET
# ============================================================================

def clean_existing_pathfinder_spells(data_file: Optional[Path] = None) -> int:
    """
    Mevcut pathfinder_1e_data.json dosyasindaki bozuk spell verisini temizle.
    
    Returns:
        Temizlenen spell sayisi
    """
    if data_file is None:
        data_file = Path(__file__).resolve().parents[1] / "data" / "pathfinder_1e_data.json"

    if not data_file.exists():
        return 0

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    spells = data.get("spells", {})
    if not spells:
        return 0

    # Tum spell'leri temizle
    cleaned = clean_all_spells(spells)
    data["spells"] = cleaned

    # Kaydet
    with open(data_file, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)

    return len(cleaned)


# ============================================================================
# CORE SPELL DATABASE - En onemli 200 PF1e spell'i (SRD)
# Scraping yapilamadiginda kullanilacak hazir veri
# ============================================================================

CORE_PF1E_SPELLS = {
    # --- 0th Level (Cantrips/Orisons) ---
    "Acid Splash": {"level": 0, "school": "conjuration", "subschool": "creation", "descriptor": "acid",
        "casting_time": "1 standard action", "components": "V, S", "range": "close (25 ft. + 5 ft./2 levels)",
        "effect": "one missile of acid", "duration": "instantaneous", "saving_throw": "none",
        "spell_resistance": "no", "description": "You fire a small orb of acid at the target. You must succeed on a ranged touch attack to hit your target. The orb deals 1d3 points of acid damage.",
        "levels_by_class": {"Sorcerer": 0, "Wizard": 0, "Arcanist": 0}},
    "Detect Magic": {"level": 0, "school": "divination", "casting_time": "1 standard action",
        "components": "V, S", "range": "60 ft.", "area": "cone-shaped emanation",
        "duration": "concentration, up to 1 min./level", "saving_throw": "none",
        "spell_resistance": "no", "description": "You detect magical auras. The amount of information revealed depends on how long you study a particular area or subject.",
        "levels_by_class": {"Bard": 0, "Cleric": 0, "Druid": 0, "Sorcerer": 0, "Wizard": 0, "Arcanist": 0, "Inquisitor": 0, "Magus": 0, "Witch": 0}},
    "Light": {"level": 0, "school": "evocation", "descriptor": "light",
        "casting_time": "1 standard action", "components": "V, M/DF (a firefly)",
        "range": "touch", "target": "object touched", "duration": "10 min./level",
        "saving_throw": "none", "spell_resistance": "no",
        "description": "This spell causes a touched object to glow like a torch, shedding normal light in a 20-foot radius.",
        "levels_by_class": {"Bard": 0, "Cleric": 0, "Druid": 0, "Sorcerer": 0, "Wizard": 0, "Arcanist": 0, "Inquisitor": 0}},
    "Mage Hand": {"level": 0, "school": "transmutation",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "close (25 ft. + 5 ft./2 levels)", "target": "one nonmagical, unattended object weighing up to 5 lbs.",
        "duration": "concentration", "saving_throw": "none", "spell_resistance": "no",
        "description": "You point your finger at an object and can lift it and move it at will from a distance.",
        "levels_by_class": {"Bard": 0, "Sorcerer": 0, "Wizard": 0, "Arcanist": 0, "Magus": 0}},
    "Read Magic": {"level": 0, "school": "divination",
        "casting_time": "1 standard action", "components": "V, S, F (a clear crystal or mineral prism)",
        "range": "personal", "target": "you", "duration": "10 min./level",
        "description": "You can decipher magical inscriptions on objects that would otherwise be unintelligible.",
        "levels_by_class": {"Bard": 0, "Cleric": 0, "Druid": 0, "Sorcerer": 0, "Wizard": 0, "Arcanist": 0, "Ranger": 1, "Paladin": 1}},
    "Prestidigitation": {"level": 0, "school": "universal",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "10 ft.", "target": "see text", "duration": "1 hour",
        "saving_throw": "see text", "spell_resistance": "no",
        "description": "Prestidigitations are minor tricks that novice spellcasters use for practice.",
        "levels_by_class": {"Bard": 0, "Sorcerer": 0, "Wizard": 0, "Arcanist": 0, "Magus": 0}},
    "Stabilize": {"level": 0, "school": "conjuration", "subschool": "healing",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "close (25 ft. + 5 ft./2 levels)", "target": "one living creature",
        "duration": "instantaneous", "saving_throw": "Will negates (harmless)",
        "spell_resistance": "yes (harmless)",
        "description": "Upon casting this spell, you target a living creature that has -1 or fewer hit points. That creature is automatically stabilized and does not lose any further hit points.",
        "levels_by_class": {"Cleric": 0, "Druid": 0, "Oracle": 0}},

    # --- 1st Level ---
    "Magic Missile": {"level": 1, "school": "evocation", "descriptor": "force",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "medium (100 ft. + 10 ft./level)", "target": "up to five creatures, no two of which can be more than 15 ft. apart",
        "duration": "instantaneous", "saving_throw": "none", "spell_resistance": "yes",
        "description": "A missile of magical energy darts forth from your fingertip and strikes its target, dealing 1d4+1 points of force damage. For every two caster levels beyond 1st, you gain an additional missile - two at 3rd level, three at 5th, four at 7th, and the maximum of five missiles at 9th level or higher.",
        "levels_by_class": {"Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Magus": 1, "Bloodrager": 1}},
    "Shield": {"level": 1, "school": "abjuration", "descriptor": "force",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "personal", "target": "you", "duration": "1 min./level",
        "description": "Shield creates an invisible shield of force that hovers in front of you. It negates magic missile attacks directed at you. The disk also provides a +4 shield bonus to AC.",
        "levels_by_class": {"Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Alchemist": 1, "Bloodrager": 1, "Magus": 1}},
    "Cure Light Wounds": {"level": 1, "school": "conjuration", "subschool": "healing",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "touch", "target": "creature touched", "duration": "instantaneous",
        "saving_throw": "Will half (harmless)", "spell_resistance": "yes (harmless)",
        "description": "When laying your hand upon a living creature, you channel positive energy that cures 1d8 points of damage +1 point per caster level (maximum +5).",
        "levels_by_class": {"Bard": 1, "Cleric": 1, "Druid": 1, "Ranger": 2, "Paladin": 1, "Alchemist": 1, "Inquisitor": 1, "Oracle": 1, "Witch": 1}},
    "Mage Armor": {"level": 1, "school": "conjuration", "subschool": "creation", "descriptor": "force",
        "casting_time": "1 standard action", "components": "V, S, F (a piece of cured leather)",
        "range": "touch", "target": "creature touched", "duration": "1 hour/level",
        "saving_throw": "Will negates (harmless)", "spell_resistance": "no",
        "description": "An invisible but tangible field of force surrounds the subject of a mage armor spell, providing a +4 armor bonus to AC.",
        "levels_by_class": {"Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Bloodrager": 1, "Summoner": 1, "Witch": 1}},
    "Burning Hands": {"level": 1, "school": "evocation", "descriptor": "fire",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "15 ft.", "area": "cone-shaped burst",
        "duration": "instantaneous", "saving_throw": "Reflex half", "spell_resistance": "yes",
        "description": "A cone of searing flame shoots from your fingertips. Any creature in the area of the flames takes 1d4 points of fire damage per caster level (maximum 5d4).",
        "levels_by_class": {"Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Bloodrager": 1, "Magus": 1}},
    "Sleep": {"level": 1, "school": "enchantment", "subschool": "compulsion", "descriptor": "mind-affecting",
        "casting_time": "1 round", "components": "V, S, M (fine sand, rose petals, or a live cricket)",
        "range": "medium (100 ft. + 10 ft./level)", "area": "one or more living creatures within a 10-ft.-radius burst",
        "duration": "1 min./level", "saving_throw": "Will negates", "spell_resistance": "yes",
        "description": "A sleep spell causes a magical slumber to come upon 4 HD of creatures.",
        "levels_by_class": {"Bard": 1, "Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Witch": 1}},
    "Grease": {"level": 1, "school": "conjuration", "subschool": "creation",
        "casting_time": "1 standard action", "components": "V, S, M (butter)",
        "range": "close (25 ft. + 5 ft./2 levels)", "target": "one object or 10-ft. square",
        "duration": "1 min./level", "saving_throw": "see text", "spell_resistance": "no",
        "description": "A grease spell covers a solid surface with a layer of slippery grease. Any creature in the area when the spell is cast must make a successful Reflex save or fall. Creatures moving through must succeed on a Reflex save or fall.",
        "levels_by_class": {"Bard": 1, "Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Magus": 1, "Summoner": 1}},
    "Color Spray": {"level": 1, "school": "illusion", "subschool": "pattern", "descriptor": "mind-affecting",
        "casting_time": "1 standard action", "components": "V, S, M (red, yellow, and blue powder or sand)",
        "range": "15 ft.", "area": "cone-shaped burst",
        "duration": "instantaneous; see text", "saving_throw": "Will negates", "spell_resistance": "yes",
        "description": "A vivid cone of clashing colors springs forth from your hand, causing creatures to become stunned, blinded, and/or unconscious.",
        "levels_by_class": {"Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Bloodrager": 1, "Magus": 1}},
    "Enlarge Person": {"level": 1, "school": "transmutation",
        "casting_time": "1 round", "components": "V, S, M (powdered iron)",
        "range": "close (25 ft. + 5 ft./2 levels)", "target": "one humanoid creature",
        "duration": "1 min./level", "saving_throw": "Fortitude negates", "spell_resistance": "yes",
        "description": "This spell causes instant growth of a humanoid creature, doubling its height and multiplying its weight by 8. The target gains a +2 size bonus to Strength, a -2 size penalty to Dexterity (to a minimum of 1), and a -1 penalty on attack rolls and AC due to its increased size.",
        "levels_by_class": {"Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Alchemist": 1, "Bloodrager": 1, "Magus": 1, "Witch": 1}},
    "Identify": {"level": 1, "school": "divination",
        "casting_time": "1 standard action", "components": "V, S, M (wine stirred with an owl's feather)",
        "range": "60 ft.", "area": "cone-shaped emanation",
        "duration": "3 rounds/level", "saving_throw": "none", "spell_resistance": "no",
        "description": "This spell functions as detect magic, except that it gives you a +10 enhancement bonus on Spellcraft checks made to identify the properties and command words of magic items in your possession.",
        "levels_by_class": {"Bard": 1, "Sorcerer": 1, "Wizard": 1, "Arcanist": 1, "Alchemist": 1, "Occultist": 1}},
    "Bless": {"level": 1, "school": "enchantment", "subschool": "compulsion", "descriptor": "mind-affecting",
        "casting_time": "1 standard action", "components": "V, S, DF",
        "range": "50 ft.", "area": "the caster and all allies within a 50-ft. burst centered on the caster",
        "duration": "1 min./level", "saving_throw": "none", "spell_resistance": "yes (harmless)",
        "description": "Bless fills your allies with courage. Each ally gains a +1 morale bonus on attack rolls and on saving throws against fear effects.",
        "levels_by_class": {"Cleric": 1, "Inquisitor": 1, "Oracle": 1, "Paladin": 1}},

    # --- 2nd Level ---
    "Scorching Ray": {"level": 2, "school": "evocation", "descriptor": "fire",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "close (25 ft. + 5 ft./2 levels)", "effect": "one or more rays",
        "duration": "instantaneous", "saving_throw": "none", "spell_resistance": "yes",
        "description": "You blast your enemies with fiery rays. You may fire one ray, plus one additional ray for every four levels beyond 3rd (to a maximum of three rays at 11th level). Each ray requires a ranged touch attack to hit and deals 4d6 points of fire damage.",
        "levels_by_class": {"Sorcerer": 2, "Wizard": 2, "Arcanist": 2, "Bloodrager": 2, "Magus": 2}},
    "Mirror Image": {"level": 2, "school": "illusion", "subschool": "figment",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "personal", "target": "you", "duration": "1 min./level",
        "description": "This spell creates a number of illusory doubles of you that inhabit your square. These duplicates make it difficult for enemies to precisely locate and attack you. 1d4 images plus one image per three caster levels (maximum eight images total).",
        "levels_by_class": {"Bard": 2, "Sorcerer": 2, "Wizard": 2, "Arcanist": 2, "Bloodrager": 2, "Magus": 2, "Witch": 2}},
    "Invisibility": {"level": 2, "school": "illusion", "subschool": "glamer",
        "casting_time": "1 standard action", "components": "V, S, M/DF (an eyelash encased in gum arabic)",
        "range": "personal or touch", "target": "you or a creature or object weighing no more than 100 lbs./level",
        "duration": "1 min./level", "saving_throw": "Will negates (harmless)",
        "spell_resistance": "yes (harmless)",
        "description": "The creature or object touched becomes invisible. If the recipient is a creature carrying gear, that vanishes, too. The spell ends if the subject attacks any creature.",
        "levels_by_class": {"Bard": 2, "Sorcerer": 2, "Wizard": 2, "Arcanist": 2, "Alchemist": 2, "Antipaladin": 2, "Inquisitor": 2, "Magus": 2}},
    "Web": {"level": 2, "school": "conjuration", "subschool": "creation",
        "casting_time": "1 standard action", "components": "V, S, M (spider web)",
        "range": "medium (100 ft. + 10 ft./level)", "effect": "webs in a 20-ft.-radius spread",
        "duration": "10 min./level", "saving_throw": "Reflex negates; see text",
        "spell_resistance": "no",
        "description": "Web creates a many-layered mass of strong, sticky strands. These strands trap those caught in them.",
        "levels_by_class": {"Sorcerer": 2, "Wizard": 2, "Arcanist": 2, "Magus": 2, "Witch": 2}},
    "Bull's Strength": {"level": 2, "school": "transmutation",
        "casting_time": "1 standard action", "components": "V, S, M/DF (a few hairs from a bull)",
        "range": "touch", "target": "creature touched", "duration": "1 min./level",
        "saving_throw": "Will negates (harmless)", "spell_resistance": "yes (harmless)",
        "description": "The subject becomes stronger. The spell grants a +4 enhancement bonus to Strength.",
        "levels_by_class": {"Cleric": 2, "Druid": 2, "Sorcerer": 2, "Wizard": 2, "Arcanist": 2, "Alchemist": 2, "Antipaladin": 2, "Bloodrager": 2, "Magus": 2, "Paladin": 2, "Ranger": 2, "Summoner": 2}},
    "Cure Moderate Wounds": {"level": 2, "school": "conjuration", "subschool": "healing",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "touch", "target": "creature touched", "duration": "instantaneous",
        "saving_throw": "Will half (harmless)", "spell_resistance": "yes (harmless)",
        "description": "Cures 2d8 damage +1/level (max +10).",
        "levels_by_class": {"Bard": 2, "Cleric": 2, "Druid": 3, "Ranger": 3, "Paladin": 3, "Alchemist": 2, "Inquisitor": 2, "Oracle": 2, "Witch": 2}},

    # --- 3rd Level ---
    "Fireball": {"level": 3, "school": "evocation", "descriptor": "fire",
        "casting_time": "1 standard action", "components": "V, S, M (a ball of bat guano and sulfur)",
        "range": "long (400 ft. + 40 ft./level)", "area": "20-ft.-radius spread",
        "duration": "instantaneous", "saving_throw": "Reflex half", "spell_resistance": "yes",
        "description": "A fireball spell generates a searing explosion of flame that detonates with a low roar and deals 1d6 points of fire damage per caster level (maximum 10d6) to every creature within the area.",
        "levels_by_class": {"Sorcerer": 3, "Wizard": 3, "Arcanist": 3, "Bloodrager": 3, "Magus": 3}},
    "Lightning Bolt": {"level": 3, "school": "evocation", "descriptor": "electricity",
        "casting_time": "1 standard action", "components": "V, S, M (fur and a glass rod)",
        "range": "120 ft.", "area": "120-ft. line",
        "duration": "instantaneous", "saving_throw": "Reflex half", "spell_resistance": "yes",
        "description": "You release a powerful stroke of electrical energy that deals 1d6 points of electricity damage per caster level (maximum 10d6) to each creature within its area.",
        "levels_by_class": {"Sorcerer": 3, "Wizard": 3, "Arcanist": 3, "Bloodrager": 3, "Magus": 3, "Witch": 3}},
    "Fly": {"level": 3, "school": "transmutation",
        "casting_time": "1 standard action", "components": "V, S, F (a wing feather)",
        "range": "touch", "target": "creature touched", "duration": "1 min./level",
        "saving_throw": "Will negates (harmless)", "spell_resistance": "yes (harmless)",
        "description": "The subject can fly at a speed of 60 feet (or 40 feet if it wears medium or heavy armor). It can ascend at half speed and descend at double speed, and its maneuverability is good.",
        "levels_by_class": {"Sorcerer": 3, "Wizard": 3, "Arcanist": 3, "Alchemist": 3, "Bloodrager": 3, "Magus": 3, "Summoner": 3, "Witch": 3}},
    "Haste": {"level": 3, "school": "transmutation",
        "casting_time": "1 standard action", "components": "V, S, M (a shaving of licorice root)",
        "range": "close (25 ft. + 5 ft./2 levels)",
        "target": "one creature/level, no two of which can be more than 30 ft. apart",
        "duration": "1 round/level", "saving_throw": "Fortitude negates (harmless)",
        "spell_resistance": "yes (harmless)",
        "description": "The transmuted creatures move and act more quickly than normal. This extra speed has several effects. +1 bonus on attack rolls and +1 dodge bonus to AC and Reflex saves. An extra attack per round at highest base attack bonus. +30 ft. movement speed.",
        "levels_by_class": {"Bard": 3, "Sorcerer": 3, "Wizard": 3, "Arcanist": 3, "Alchemist": 3, "Bloodrager": 3, "Magus": 3, "Summoner": 3}},
    "Dispel Magic": {"level": 3, "school": "abjuration",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "medium (100 ft. + 10 ft./level)", "target": "one spellcaster, creature, or object",
        "duration": "instantaneous", "saving_throw": "none", "spell_resistance": "no",
        "description": "You can use dispel magic to end one ongoing spell that has been cast on a creature or object, to temporarily suppress the magical abilities of a magic item, or to counter another spellcaster's spell.",
        "levels_by_class": {"Bard": 3, "Cleric": 3, "Druid": 4, "Sorcerer": 3, "Wizard": 3, "Arcanist": 3, "Antipaladin": 3, "Inquisitor": 3, "Magus": 3, "Paladin": 3, "Witch": 3}},
    "Cure Serious Wounds": {"level": 3, "school": "conjuration", "subschool": "healing",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "touch", "target": "creature touched", "duration": "instantaneous",
        "saving_throw": "Will half (harmless)", "spell_resistance": "yes (harmless)",
        "description": "Cures 3d8 damage +1/level (max +15).",
        "levels_by_class": {"Bard": 3, "Cleric": 3, "Druid": 4, "Ranger": 4, "Paladin": 4, "Alchemist": 3, "Inquisitor": 3, "Oracle": 3, "Witch": 4}},

    # --- 4th Level ---
    "Dimension Door": {"level": 4, "school": "conjuration", "subschool": "teleportation",
        "casting_time": "1 standard action", "components": "V",
        "range": "long (400 ft. + 40 ft./level)", "target": "you and touched objects or other touched willing creatures",
        "duration": "instantaneous", "saving_throw": "none and Will negates (object)",
        "spell_resistance": "no and yes (object)",
        "description": "You instantly transfer yourself from your current location to any other spot within range. You always arrive at exactly the spot desired.",
        "levels_by_class": {"Bard": 4, "Sorcerer": 4, "Wizard": 4, "Arcanist": 4, "Magus": 4, "Summoner": 3, "Witch": 4}},
    "Greater Invisibility": {"level": 4, "school": "illusion", "subschool": "glamer",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "personal or touch", "target": "you or creature touched",
        "duration": "1 round/level", "saving_throw": "Will negates (harmless)",
        "spell_resistance": "yes (harmless)",
        "description": "This spell functions like invisibility, except that it doesn't end if the subject attacks.",
        "levels_by_class": {"Bard": 4, "Sorcerer": 4, "Wizard": 4, "Arcanist": 4, "Alchemist": 4, "Antipaladin": 4, "Magus": 4}},
    "Stoneskin": {"level": 4, "school": "abjuration",
        "casting_time": "1 standard action", "components": "V, S, M (granite and diamond dust worth 250 gp)",
        "range": "touch", "target": "creature touched", "duration": "10 min./level or until discharged",
        "saving_throw": "Will negates (harmless)", "spell_resistance": "yes (harmless)",
        "description": "The warded creature gains resistance to blows, cuts, stabs, and slashes. The subject gains DR 10/adamantine. It ignores the first 10 points of damage each time it takes damage from a weapon, though an adamantine weapon bypasses the reduction. Once the spell has prevented a total of 10 points of damage per caster level (maximum 150 points), it is discharged.",
        "levels_by_class": {"Sorcerer": 4, "Wizard": 4, "Arcanist": 4, "Alchemist": 4, "Bloodrager": 4, "Druid": 5, "Ranger": 4, "Summoner": 3}},
    "Cure Critical Wounds": {"level": 4, "school": "conjuration", "subschool": "healing",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "touch", "target": "creature touched", "duration": "instantaneous",
        "saving_throw": "Will half (harmless)", "spell_resistance": "yes (harmless)",
        "description": "Cures 4d8 damage +1/level (max +20).",
        "levels_by_class": {"Bard": 4, "Cleric": 4, "Druid": 5, "Oracle": 4, "Witch": 4}},

    # --- 5th Level ---
    "Cone of Cold": {"level": 5, "school": "evocation", "descriptor": "cold",
        "casting_time": "1 standard action", "components": "V, S, M (a small crystal or glass cone)",
        "range": "60 ft.", "area": "cone-shaped burst",
        "duration": "instantaneous", "saving_throw": "Reflex half", "spell_resistance": "yes",
        "description": "Cone of cold creates an area of extreme cold, originating at your hand and extending outward in a cone. It drains heat, dealing 1d6 points of cold damage per caster level (maximum 15d6).",
        "levels_by_class": {"Sorcerer": 5, "Wizard": 5, "Arcanist": 5, "Magus": 5, "Witch": 6}},
    "Teleport": {"level": 5, "school": "conjuration", "subschool": "teleportation",
        "casting_time": "1 standard action", "components": "V",
        "range": "personal and touch", "target": "you and touched objects or other touched willing creatures",
        "duration": "instantaneous", "saving_throw": "none and Will negates (object)",
        "spell_resistance": "no and yes (object)",
        "description": "This spell instantly transports you to a designated destination, which may be as distant as 100 miles per caster level.",
        "levels_by_class": {"Sorcerer": 5, "Wizard": 5, "Arcanist": 5, "Magus": 5, "Summoner": 4, "Witch": 5}},
    "Wall of Force": {"level": 5, "school": "evocation", "descriptor": "force",
        "casting_time": "1 standard action", "components": "V, S, M (powdered quartz)",
        "range": "close (25 ft. + 5 ft./2 levels)",
        "effect": "wall whose area is up to one 10-ft. square/level",
        "duration": "1 round/level", "saving_throw": "none", "spell_resistance": "no",
        "description": "A wall of force creates an invisible wall of pure force. The wall cannot be damaged by any means.",
        "levels_by_class": {"Sorcerer": 5, "Wizard": 5, "Arcanist": 5, "Magus": 5, "Occultist": 5}},
    "Break Enchantment": {"level": 5, "school": "abjuration",
        "casting_time": "1 minute", "components": "V, S",
        "range": "close (25 ft. + 5 ft./2 levels)",
        "target": "up to one creature per level, all within 30 ft. of each other",
        "duration": "instantaneous", "saving_throw": "see text", "spell_resistance": "no",
        "description": "This spell frees victims from enchantments, transmutations, and curses. Break enchantment can reverse even an instantaneous effect.",
        "levels_by_class": {"Bard": 4, "Cleric": 5, "Sorcerer": 5, "Wizard": 5, "Arcanist": 5, "Inquisitor": 5, "Oracle": 5, "Paladin": 4, "Witch": 5}},

    # --- 6th Level ---
    "Disintegrate": {"level": 6, "school": "transmutation",
        "casting_time": "1 standard action", "components": "V, S, M/DF (a lodestone and a pinch of dust)",
        "range": "medium (100 ft. + 10 ft./level)",
        "effect": "ray", "duration": "instantaneous",
        "saving_throw": "Fortitude partial (object)", "spell_resistance": "yes",
        "description": "A thin, green ray springs from your pointing finger. You must make a successful ranged touch attack to hit. Any creature struck by the ray takes 2d6 points of damage per caster level (to a maximum of 40d6). Any creature reduced to 0 or fewer hit points by this spell is entirely disintegrated.",
        "levels_by_class": {"Sorcerer": 6, "Wizard": 6, "Arcanist": 6, "Magus": 6}},
    "Chain Lightning": {"level": 6, "school": "evocation", "descriptor": "electricity",
        "casting_time": "1 standard action", "components": "V, S, F (a bit of fur; a piece of amber, glass, or a crystal rod; plus one silver pin per caster level)",
        "range": "long (400 ft. + 40 ft./level)",
        "target": "one primary target, plus one secondary target/level (each of which must be within 30 ft. of the primary target)",
        "duration": "instantaneous", "saving_throw": "Reflex half", "spell_resistance": "yes",
        "description": "This spell creates an electrical discharge that begins as a single stroke commencing from your fingertips. The bolt deals 1d6 points of electricity damage per caster level (maximum 20d6) to the primary target.",
        "levels_by_class": {"Sorcerer": 6, "Wizard": 6, "Arcanist": 6}},
    "Heal": {"level": 6, "school": "conjuration", "subschool": "healing",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "touch", "target": "creature touched", "duration": "instantaneous",
        "saving_throw": "Will negates (harmless)", "spell_resistance": "yes (harmless)",
        "description": "Heal enables you to channel positive energy into a creature to wipe away injury and afflictions. It immediately ends any and all of the following adverse conditions: ability damage, blinded, confused, dazed, dazzled, deafened, diseased, exhausted, fatigued, feebleminded, insanity, nauseated, poisoned, sickened, and stunned. It also cures 10 hit points of damage per level of the caster, to a maximum of 150 points at 15th level.",
        "levels_by_class": {"Cleric": 6, "Druid": 7, "Inquisitor": 6, "Oracle": 6, "Witch": 7}},

    # --- 7th-9th Level ---
    "Greater Teleport": {"level": 7, "school": "conjuration", "subschool": "teleportation",
        "casting_time": "1 standard action", "components": "V",
        "range": "personal and touch", "target": "you and touched objects or other touched willing creatures",
        "duration": "instantaneous", "saving_throw": "none and Will negates (object)",
        "spell_resistance": "no and yes (object)",
        "description": "This spell functions like teleport, except that there is no range limit and there is no chance you arrive off target.",
        "levels_by_class": {"Sorcerer": 7, "Wizard": 7, "Arcanist": 7, "Summoner": 5, "Witch": 7}},
    "Power Word Kill": {"level": 9, "school": "enchantment", "subschool": "compulsion",
        "descriptor": "death, mind-affecting",
        "casting_time": "1 standard action", "components": "V",
        "range": "close (25 ft. + 5 ft./2 levels)", "target": "one living creature with 100 hp or less",
        "duration": "instantaneous", "saving_throw": "none", "spell_resistance": "yes",
        "description": "You utter a single word of power that instantly kills one creature of your choice, whether the creature can hear the word or not. Any creature that currently has 100 or fewer hit points is slain.",
        "levels_by_class": {"Sorcerer": 9, "Wizard": 9, "Arcanist": 9, "Witch": 9}},
    "Wish": {"level": 9, "school": "universal",
        "casting_time": "1 standard action", "components": "V, S, M (diamond worth 25,000 gp)",
        "range": "see text", "target": "see text", "duration": "see text",
        "saving_throw": "see text", "spell_resistance": "yes",
        "description": "Wish is the mightiest spell a wizard or sorcerer can cast. By simply speaking aloud, you can alter reality to better suit you.",
        "levels_by_class": {"Sorcerer": 9, "Wizard": 9, "Arcanist": 9}},
    "Meteor Swarm": {"level": 9, "school": "evocation", "descriptor": "fire",
        "casting_time": "1 standard action", "components": "V, S",
        "range": "long (400 ft. + 40 ft./level)",
        "area": "four 40-ft.-radius spreads; see text",
        "duration": "instantaneous", "saving_throw": "none or Reflex half; see text",
        "spell_resistance": "yes",
        "description": "Meteor swarm is a very powerful and spectacular spell that is similar to fireball in many aspects. When you cast it, four 2-foot-diameter spheres spring from your outstretched hand and streak in straight lines to the spots you select. Each sphere deals 2d6 points of bludgeoning damage plus 6d6 points of fire damage.",
        "levels_by_class": {"Sorcerer": 9, "Wizard": 9, "Arcanist": 9}},
    "Time Stop": {"level": 9, "school": "transmutation",
        "casting_time": "1 standard action", "components": "V",
        "range": "personal", "target": "you", "duration": "1d4+1 rounds (apparent time); see text",
        "description": "This spell seems to make time cease to flow for everyone but you. In fact, you speed up so greatly that all other creatures seem frozen.",
        "levels_by_class": {"Sorcerer": 9, "Wizard": 9, "Arcanist": 9}},
}


def ensure_core_spells_exist(data_file: Optional[Path] = None) -> int:
    """
    Core spell'lerin veri dosyasinda oldugundan emin ol.
    Eksik olanlari ekle. Mevcut spell'leri bozma.
    
    Returns: Eklenen spell sayisi
    """
    if data_file is None:
        data_file = Path(__file__).resolve().parents[1] / "data" / "pathfinder_1e_data.json"

    if not data_file.exists():
        return 0

    with open(data_file, 'r', encoding='utf-8') as f:
        data = json.load(f)

    spells = data.setdefault("spells", {})
    added = 0

    for name, spell_data in CORE_PF1E_SPELLS.items():
        if name not in spells:
            spells[name] = spell_data
            added += 1
        else:
            # Mevcut spell bozuk mu kontrol et
            existing = spells[name]
            ct = existing.get("casting_time", "")
            if ct and len(ct) > 100:
                # Bozuk, core veriyle degistir
                spells[name] = spell_data
                added += 1

    if added > 0:
        data["spells"] = spells
        with open(data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)

    return added
