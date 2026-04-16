"""
Pathfinder 1e Spider — d20pfsrd.com
====================================
d20pfsrd.com'dan Pathfinder 1st Edition SRD verisi çeker.

Hedef sayfalar:
  - Races:   https://www.d20pfsrd.com/races/core-races/
  - Classes: https://www.d20pfsrd.com/classes/core-classes/
  - Feats:   https://www.d20pfsrd.com/feats/
  - Spells:  https://www.d20pfsrd.com/magic/all-spells/

KESİNLİKLE Pathfinder 1st Edition (1e) kuralları kullanılır.
2e kurallarını asla dahil etme.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag

from scraping.base_scraper import BaseScraper, sanitize_html, extract_text, extract_list_items
from scraping.models import (
    RaceModel, ClassModel, SpellModel, FeatModel,
    SystemDataBundle, SourceReference,
)

logger = logging.getLogger(__name__)


# ======================================================================
# Site-spesifik sabitler
# ======================================================================

_CORE_RACES_SLUGS = [
    "dwarf", "elf", "gnome", "half-elf", "half-orc", "halfling", "human",
]

_FEATURED_RACES_SLUGS = [
    "aasimar", "catfolk", "dhampir", "drow", "fetchling", "goblin",
    "hobgoblin", "ifrit", "kobold", "orc", "oread", "ratfolk",
    "sylph", "tengu", "tiefling", "undine",
]

_CORE_CLASSES_SLUGS = [
    "barbarian", "bard", "cleric", "druid", "fighter", "monk",
    "paladin", "ranger", "rogue", "sorcerer", "wizard",
]

_BASE_CLASSES_SLUGS = [
    "alchemist", "cavalier", "gunslinger", "inquisitor",
    "magus", "oracle", "summoner", "witch",
]

_SCHOOL_NAMES = {
    "abjuration", "conjuration", "divination", "enchantment",
    "evocation", "illusion", "necromancy", "transmutation", "universal",
}


class PF1eD20pfsrdSpider(BaseScraper):
    """d20pfsrd.com'dan PF 1e verisi çeken spider."""

    SYSTEM_KEY = "pathfinder1e"
    BASE_URL = "https://www.d20pfsrd.com"
    OUTPUT_FILE = "pathfinder_1e_data.json"

    def __init__(self, output_dir: Optional[Path] = None, **kwargs) -> None:
        super().__init__(output_dir=output_dir, **kwargs)

    # ------------------------------------------------------------------
    # Ana Scrape Metodu
    # ------------------------------------------------------------------

    def scrape(self) -> SystemDataBundle:
        """Tüm PF 1e verilerini çek ve doğrulanmış bundle döndür."""
        logger.info("═" * 60)
        logger.info("PF 1e Spider başlatılıyor — d20pfsrd.com")
        logger.info("═" * 60)

        races = self.scrape_races()
        logger.info("Irklar tamamlandı: %d kayıt", len(races))

        classes = self.scrape_classes()
        logger.info("Sınıflar tamamlandı: %d kayıt", len(classes))

        feats = self.scrape_feats()
        logger.info("Feats tamamlandı: %d kayıt", len(feats))

        stats = self.stats()
        logger.info(
            "Spider tamamlandı — %d istek, %d hata",
            stats["requests"], stats["errors"],
        )

        return SystemDataBundle(
            system="pathfinder1e",
            source="https://www.d20pfsrd.com",
            races=races,
            classes=classes,
            feats=feats,
        )

    # ------------------------------------------------------------------
    # Races
    # ------------------------------------------------------------------

    def scrape_races(self) -> Dict[str, Any]:
        """Core + Featured ırkları çek."""
        results: Dict[str, Any] = {}

        all_slugs = [("core-races", s) for s in _CORE_RACES_SLUGS] + \
                     [("other-races", s) for s in _FEATURED_RACES_SLUGS]

        for category, slug in all_slugs:
            url = f"{self.BASE_URL}/races/{category}/{slug}/"
            logger.info("  Irk çekiliyor: %s", slug)
            soup = self.fetch(url)
            if not soup:
                continue

            parsed = self._parse_race_page(soup, slug, url)
            if parsed:
                model = self.validate_item(parsed, RaceModel)
                if model:
                    results[model.name] = model.model_dump(exclude_none=True)

        return results

    def _parse_race_page(self, soup: BeautifulSoup, slug: str, url: str) -> Optional[Dict[str, Any]]:
        """Tek bir ırk sayfasını parse et."""
        content = soup.find("article") or soup.find("div", class_="article-content") or soup
        title = soup.find("h1")
        name = extract_text(title) if title else slug.replace("-", " ").title()

        data: Dict[str, Any] = {
            "name": name,
            "system": "pathfinder1e",
            "source": {"url": url, "book": "Core Rulebook"},
        }

        full_text = extract_text(content)

        ability_match = re.search(
            r"(?:Ability Score (?:Racial )?(?:Modifiers?|Adjustments?))[:\s]*([^\n.]+)",
            full_text, re.IGNORECASE,
        )
        if ability_match:
            data["ability_score_increase_text"] = ability_match.group(1).strip()
            data["ability_score_increase"] = self._parse_ability_bonuses(
                ability_match.group(1)
            )

        speed_match = re.search(r"(?:Base |Land )?Speed[:\s]*(\d+)\s*(?:ft|feet)", full_text, re.IGNORECASE)
        if speed_match:
            data["speed"] = int(speed_match.group(1))

        size_match = re.search(r"Size[:\s]*(Small|Medium|Large|Tiny)", full_text, re.IGNORECASE)
        if size_match:
            data["size"] = size_match.group(1).title()

        if "darkvision" in full_text.lower():
            data["vision"] = "Darkvision"
        elif "low-light vision" in full_text.lower():
            data["vision"] = "Low-Light"

        traits: List[str] = []
        trait_headers = content.find_all(["h3", "h4", "b", "strong"])
        for th in trait_headers:
            text = extract_text(th)
            if text and len(text) < 60 and text not in ("Description", "Physical Description",
                                                          "Society", "Relations", "Alignment and Religion",
                                                          "Adventurers", "Names", "Alternate Racial Traits",
                                                          "Favored Class Options"):
                traits.append(text)
        data["traits"] = traits[:20]

        lang_match = re.search(r"Languages?[:\s]*([^\n]+)", full_text, re.IGNORECASE)
        if lang_match:
            raw_langs = lang_match.group(1)
            data["languages"] = [l.strip().rstrip(".") for l in raw_langs.split(",") if l.strip()]

        desc_tag = content.find("p")
        if desc_tag:
            data["description"] = sanitize_html(str(desc_tag))[:500]

        return data

    @staticmethod
    def _parse_ability_bonuses(text: str) -> Dict[str, int]:
        """'+2 Constitution, +2 Wisdom, –2 Charisma' → {'constitution': 2, ...}"""
        bonuses: Dict[str, int] = {}
        pattern = re.compile(r"([+\-–]?\d+)\s+(Str(?:ength)?|Dex(?:terity)?|Con(?:stitution)?|"
                             r"Int(?:elligence)?|Wis(?:dom)?|Cha(?:risma)?)", re.IGNORECASE)
        ABILITY_MAP = {
            "str": "strength", "strength": "strength",
            "dex": "dexterity", "dexterity": "dexterity",
            "con": "constitution", "constitution": "constitution",
            "int": "intelligence", "intelligence": "intelligence",
            "wis": "wisdom", "wisdom": "wisdom",
            "cha": "charisma", "charisma": "charisma",
        }
        for match in pattern.finditer(text):
            val = int(match.group(1).replace("–", "-"))
            ability = ABILITY_MAP.get(match.group(2).lower(), "")
            if ability:
                bonuses[ability] = val
        return bonuses

    # ------------------------------------------------------------------
    # Classes
    # ------------------------------------------------------------------

    def scrape_classes(self) -> Dict[str, Any]:
        """Core + Base sınıfları çek."""
        results: Dict[str, Any] = {}

        all_slugs = [("core-classes", s) for s in _CORE_CLASSES_SLUGS] + \
                     [("base-classes", s) for s in _BASE_CLASSES_SLUGS]

        for category, slug in all_slugs:
            url = f"{self.BASE_URL}/classes/{category}/{slug}/"
            logger.info("  Sınıf çekiliyor: %s", slug)
            soup = self.fetch(url)
            if not soup:
                continue

            parsed = self._parse_class_page(soup, slug, url)
            if parsed:
                model = self.validate_item(parsed, ClassModel)
                if model:
                    results[model.name] = model.model_dump(exclude_none=True)

        return results

    def _parse_class_page(self, soup: BeautifulSoup, slug: str, url: str) -> Optional[Dict[str, Any]]:
        """Tek bir sınıf sayfasını parse et."""
        content = soup.find("article") or soup.find("div", class_="article-content") or soup
        title = soup.find("h1")
        name = extract_text(title) if title else slug.replace("-", " ").title()

        data: Dict[str, Any] = {
            "name": name,
            "system": "pathfinder1e",
            "source": {"url": url, "book": "Core Rulebook"},
        }

        full_text = extract_text(content)

        hd_match = re.search(r"Hit (?:Die|Dice)[:\s]*(d\d+)", full_text, re.IGNORECASE)
        if hd_match:
            data["hit_die"] = hd_match.group(1).lower()

        skill_match = re.search(r"Skill Ranks? (?:per|Per|each) Level[:\s]*(\d+)", full_text, re.IGNORECASE)
        if skill_match:
            data["skill_ranks_per_level"] = int(skill_match.group(1))

        skills_section = re.search(
            r"Class Skills?[:\s]*([^.]+(?:\.|\n))", full_text, re.IGNORECASE,
        )
        if skills_section:
            raw = skills_section.group(1)
            skills = re.findall(r"([A-Z][a-z]+(?:\s[A-Z][a-z]+)*)", raw)
            known_skills = {
                "Acrobatics", "Appraise", "Bluff", "Climb", "Craft",
                "Diplomacy", "Disable Device", "Disguise", "Escape Artist",
                "Fly", "Handle Animal", "Heal", "Intimidate",
                "Knowledge", "Linguistics", "Perception", "Perform",
                "Profession", "Ride", "Sense Motive", "Sleight of Hand",
                "Spellcraft", "Stealth", "Survival", "Swim",
                "Use Magic Device",
            }
            data["class_skills"] = [s for s in skills if s in known_skills]

        for kw in ("spells", "spellcasting", "Spells Per Day", "cantrip"):
            if kw.lower() in full_text.lower():
                data["spellcasting"] = True
                if "spontaneous" in full_text.lower() or "known" in full_text.lower():
                    data["spellcasting_type"] = "spontaneous"
                else:
                    data["spellcasting_type"] = "prepared"
                break

        features: Dict[str, List[str]] = {}
        level_pattern = re.compile(r"(\d+)(?:st|nd|rd|th)[- ]Level")
        for header in content.find_all(["h3", "h4"]):
            header_text = extract_text(header)
            level_m = level_pattern.search(header_text)
            if level_m:
                lvl = level_m.group(1)
                features.setdefault(lvl, []).append(header_text)
            elif header_text and len(header_text) < 60:
                features.setdefault("class_features", []).append(header_text)

        if features:
            data["features"] = features

        desc_tag = content.find("p")
        if desc_tag:
            data["description"] = sanitize_html(str(desc_tag))[:500]

        return data

    # ------------------------------------------------------------------
    # Feats
    # ------------------------------------------------------------------

    def scrape_feats(self, max_feats: int = 100) -> Dict[str, Any]:
        """Feat listesinden ilk N feat'i çek."""
        results: Dict[str, Any] = {}

        url = f"{self.BASE_URL}/feats/"
        logger.info("  Feat listesi çekiliyor...")
        soup = self.fetch(url)
        if not soup:
            return results

        feat_links: List[tuple[str, str]] = []
        table = soup.find("table")
        if table:
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if not cells:
                    continue
                link_tag = cells[0].find("a", href=True)
                if link_tag:
                    feat_name = extract_text(link_tag)
                    href = link_tag["href"]
                    if not href.startswith("http"):
                        href = self.build_url(href)
                    feat_type = extract_text(cells[1]) if len(cells) > 1 else "General"
                    feat_links.append((feat_name, href, feat_type))
        else:
            for link in soup.find_all("a", href=True):
                href = link["href"]
                if "/feats/" in href and href != url:
                    name = extract_text(link)
                    if name and len(name) < 60:
                        full = href if href.startswith("http") else self.build_url(href)
                        feat_links.append((name, full, "General"))

        feat_links = feat_links[:max_feats]
        logger.info("  %d feat bulundu, çekiliyor...", len(feat_links))

        for i, (name, href, *rest) in enumerate(feat_links):
            feat_type = rest[0] if rest else "General"
            logger.debug("    [%d/%d] %s", i + 1, len(feat_links), name)
            feat_soup = self.fetch(href)
            if not feat_soup:
                continue

            parsed = self._parse_feat_page(feat_soup, name, href, feat_type)
            if parsed:
                model = self.validate_item(parsed, FeatModel)
                if model:
                    results[model.name] = model.model_dump(exclude_none=True)

        return results

    def _parse_feat_page(
        self, soup: BeautifulSoup, name: str, url: str, feat_type: str,
    ) -> Optional[Dict[str, Any]]:
        """Tek bir feat sayfasını parse et."""
        content = soup.find("article") or soup
        full_text = extract_text(content)

        data: Dict[str, Any] = {
            "name": name,
            "system": "pathfinder1e",
            "feat_type": feat_type,
            "source": {"url": url},
        }

        prereq_match = re.search(r"Prerequisites?[:\s]*([^\n]+)", full_text, re.IGNORECASE)
        if prereq_match:
            raw = prereq_match.group(1).strip().rstrip(".")
            data["prerequisites"] = [p.strip() for p in raw.split(",") if p.strip()]

        benefit_match = re.search(
            r"Benefits?[:\s]*(.*?)(?:Normal|Special|$)",
            full_text, re.IGNORECASE | re.DOTALL,
        )
        if benefit_match:
            data["benefit"] = benefit_match.group(1).strip()[:500]

        normal_match = re.search(r"Normal[:\s]*(.*?)(?:Special|$)", full_text, re.IGNORECASE | re.DOTALL)
        if normal_match:
            data["normal"] = normal_match.group(1).strip()[:300]

        special_match = re.search(r"Special[:\s]*(.*?)$", full_text, re.IGNORECASE | re.DOTALL)
        if special_match:
            data["special"] = special_match.group(1).strip()[:300]

        return data

    # ------------------------------------------------------------------
    # Convenience: Çek + Kaydet
    # ------------------------------------------------------------------

    def scrape_and_save(self) -> Path:
        """Tüm verileri çek, doğrula ve JSON'a kaydet."""
        bundle = self.scrape()
        return self.merge_and_save(bundle, self.OUTPUT_FILE)
