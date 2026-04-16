"""
Mutants & Masterminds 3e Spider — d20herosrd.com
==================================================
d20herosrd.com'dan M&M 3e SRD verisi ceker (HTML scraping).

Hedef sayfalar:
  Powers:      /powers/
  Advantages:  /advantages/
  Skills:      /skills/
  Abilities:   /abilities/
  Archetypes:  /archetypes/

HTML tablolari ve listeler BeautifulSoup4 ile parse edilir,
sonuclar Pydantic modelleriyle dogrulanarak data/mm_data.json'a kaydedilir.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag

from scraping.base_scraper import BaseScraper, sanitize_html, extract_text, extract_list_items
from scraping.models import (
    ClassModel, PowerModel, AdvantageModel, FeatModel,
    SystemDataBundle,
)

logger = logging.getLogger(__name__)


class MM3eSpider(BaseScraper):
    """d20herosrd.com'dan M&M 3e SRD verisi ceker."""

    SYSTEM_KEY = "mm3e"
    BASE_URL = "https://www.d20herosrd.com"
    OUTPUT_FILE = "mm_data.json"

    def __init__(self, output_dir: Optional[Path] = None, **kwargs) -> None:
        super().__init__(output_dir=output_dir, delay_range=(1.5, 3.5), **kwargs)

    def _log_progress(self, section: str, current: int, total: int) -> None:
        pct = (current / total * 100) if total else 0
        logger.info("  [M&M 3e] %s %d/%d (%%%.0f)", section, current, total, pct)

    # ------------------------------------------------------------------
    # Ana Scrape
    # ------------------------------------------------------------------

    def scrape(self) -> SystemDataBundle:
        logger.info("=" * 60)
        logger.info("[M&M 3e] Spider baslatiliyor — d20herosrd.com")
        logger.info("=" * 60)

        abilities = self._scrape_abilities()
        logger.info("[M&M 3e] Yetenekler: %d kayit", len(abilities))

        powers = self._scrape_powers()
        logger.info("[M&M 3e] Gucler: %d kayit", len(powers))

        advantages = self._scrape_advantages()
        logger.info("[M&M 3e] Avantajlar: %d kayit", len(advantages))

        skills = self._scrape_skills()
        logger.info("[M&M 3e] Beceriler: %d kayit", len(skills))

        archetypes = self._scrape_archetypes()
        logger.info("[M&M 3e] Arketipler: %d kayit", len(archetypes))

        s = self.stats()
        logger.info("[M&M 3e] Toplam: %d istek, %d hata", s["requests"], s["errors"])

        return SystemDataBundle(
            system="mm3e",
            source="https://www.d20herosrd.com",
            extra={
                "abilities": abilities,
                "powers": powers,
                "advantages": advantages,
                "skills": skills,
                "archetypes": archetypes,
            },
        )

    def scrape_races(self) -> Dict[str, Any]:
        return {}

    def scrape_classes(self) -> Dict[str, Any]:
        return {}

    # ------------------------------------------------------------------
    # Abilities (STR, STA, AGL, DEX, FGT, INT, AWE, PRE)
    # ------------------------------------------------------------------

    def _scrape_abilities(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        soup = self.fetch(f"{self.BASE_URL}/6-abilities/")
        if not soup:
            return results

        content = soup.find("article") or soup.find("div", class_="entry-content") or soup
        for header in content.find_all(["h2", "h3"]):
            name = extract_text(header).strip()
            if not name or len(name) > 40:
                continue

            desc_parts: List[str] = []
            sibling = header.find_next_sibling()
            while sibling and sibling.name not in ("h2", "h3"):
                txt = extract_text(sibling)
                if txt:
                    desc_parts.append(txt)
                sibling = sibling.find_next_sibling()

            if not desc_parts:
                continue

            results[name] = {
                "name": name,
                "description": " ".join(desc_parts)[:500],
                "cost_per_rank": 2,
                "source": f"{self.BASE_URL}/6-abilities/",
            }

        return results

    # ------------------------------------------------------------------
    # Powers
    # ------------------------------------------------------------------

    def _scrape_powers(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        index_soup = self.fetch(f"{self.BASE_URL}/6-powers/")
        if not index_soup:
            return results

        power_links: List[tuple[str, str]] = []
        content = index_soup.find("article") or index_soup.find("div", class_="entry-content") or index_soup
        for link in content.find_all("a", href=True):
            href = link["href"]
            name = extract_text(link)
            if name and "/6-powers/" in href and href != f"{self.BASE_URL}/6-powers/" and len(name) < 60:
                full_url = href if href.startswith("http") else self.build_url(href)
                power_links.append((name, full_url))

        seen = set()
        unique_links = []
        for name, url in power_links:
            if url not in seen:
                seen.add(url)
                unique_links.append((name, url))

        total = len(unique_links)
        for i, (name, url) in enumerate(unique_links):
            if i % 10 == 0:
                self._log_progress("Gucler", i, total)

            try:
                soup = self.fetch(url)
                if not soup:
                    continue

                parsed = self._parse_power_page(soup, name, url)
                if parsed:
                    model = self.validate_item(parsed, PowerModel)
                    if model:
                        results[model.name] = model.model_dump(exclude_none=True)
            except Exception as exc:
                logger.warning("[M&M 3e] Power parse hatasi '%s': %s", name, exc)

        return results

    def _parse_power_page(self, soup: BeautifulSoup, name: str, url: str) -> Optional[Dict[str, Any]]:
        content = soup.find("article") or soup.find("div", class_="entry-content") or soup
        full_text = extract_text(content)

        data: Dict[str, Any] = {
            "name": name,
            "system": "mm3e",
            "source": {"url": url},
        }

        cost_match = re.search(r"(?:Cost|Point)[:\s]*(\d+)\s*(?:point|per rank|pp)", full_text, re.IGNORECASE)
        if cost_match:
            data["cost_per_rank"] = int(cost_match.group(1))

        action_match = re.search(r"Action[:\s]*(\w[\w\s]*?)(?:\n|Range|Duration|Cost)", full_text, re.IGNORECASE)
        if action_match:
            data["action"] = action_match.group(1).strip()[:50]

        range_match = re.search(r"Range[:\s]*(\w[\w\s/]*?)(?:\n|Duration|Action|Cost)", full_text, re.IGNORECASE)
        if range_match:
            data["range"] = range_match.group(1).strip()[:50]

        dur_match = re.search(r"Duration[:\s]*(\w[\w\s/]*?)(?:\n|Range|Action|Cost)", full_text, re.IGNORECASE)
        if dur_match:
            data["duration"] = dur_match.group(1).strip()[:50]

        desc_tag = content.find("p")
        if desc_tag:
            data["description"] = sanitize_html(str(desc_tag))[:500]

        extras_header = content.find(string=re.compile(r"Extra", re.IGNORECASE))
        if extras_header:
            ul = extras_header.find_next("ul") if hasattr(extras_header, "find_next") else None
            if ul:
                data["extras"] = extract_list_items(ul)[:15]

        flaws_header = content.find(string=re.compile(r"Flaw", re.IGNORECASE))
        if flaws_header:
            ul = flaws_header.find_next("ul") if hasattr(flaws_header, "find_next") else None
            if ul:
                data["flaws"] = extract_list_items(ul)[:15]

        return data

    # ------------------------------------------------------------------
    # Advantages
    # ------------------------------------------------------------------

    def _scrape_advantages(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        soup = self.fetch(f"{self.BASE_URL}/6-advantages/")
        if not soup:
            return results

        content = soup.find("article") or soup.find("div", class_="entry-content") or soup

        table = content.find("table")
        if table:
            for row in table.find_all("tr")[1:]:
                cells = row.find_all("td")
                if len(cells) < 2:
                    continue
                try:
                    name = extract_text(cells[0]).strip()
                    if not name:
                        continue
                    cost_text = extract_text(cells[1]).strip()
                    adv_type = extract_text(cells[2]).strip() if len(cells) > 2 else "General"
                    desc = extract_text(cells[3]).strip() if len(cells) > 3 else ""

                    parsed = {
                        "name": name,
                        "system": "mm3e",
                        "cost": cost_text,
                        "advantage_type": adv_type,
                        "ranked": "ranked" in cost_text.lower() or "rank" in cost_text.lower(),
                        "description": desc[:300],
                        "source": {"url": f"{self.BASE_URL}/6-advantages/"},
                    }
                    model = self.validate_item(parsed, AdvantageModel)
                    if model:
                        results[model.name] = model.model_dump(exclude_none=True)
                except Exception as exc:
                    logger.debug("[M&M 3e] Advantage satiri atlandi: %s", exc)
        else:
            for header in content.find_all(["h3", "h4", "strong", "b"]):
                name = extract_text(header).strip()
                if not name or len(name) > 50:
                    continue
                desc = ""
                sibling = header.find_next_sibling()
                if sibling:
                    desc = extract_text(sibling)[:300]
                results[name] = {
                    "name": name,
                    "description": desc,
                    "cost": "1",
                    "source": f"{self.BASE_URL}/6-advantages/",
                }

        return results

    # ------------------------------------------------------------------
    # Skills
    # ------------------------------------------------------------------

    def _scrape_skills(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        soup = self.fetch(f"{self.BASE_URL}/6-skills/")
        if not soup:
            return results

        content = soup.find("article") or soup.find("div", class_="entry-content") or soup

        for header in content.find_all(["h2", "h3"]):
            name = extract_text(header).strip()
            if not name or len(name) > 50 or name.lower() in ("skills", "skill descriptions", "table"):
                continue

            desc_parts: List[str] = []
            key_ability = ""
            sibling = header.find_next_sibling()
            while sibling and sibling.name not in ("h2", "h3"):
                txt = extract_text(sibling)
                if txt:
                    desc_parts.append(txt)
                    ab_match = re.search(
                        r"(?:Key Ability|Based on)[:\s]*(Str|Sta|Agl|Dex|Fgt|Int|Awe|Pre)",
                        txt, re.IGNORECASE,
                    )
                    if ab_match and not key_ability:
                        key_ability = ab_match.group(1).upper()
                sibling = sibling.find_next_sibling()

            if not desc_parts:
                continue

            results[name] = {
                "name": name,
                "key_ability": key_ability,
                "cost_per_rank": 1,
                "description": " ".join(desc_parts)[:500],
                "source": f"{self.BASE_URL}/6-skills/",
            }

        return results

    # ------------------------------------------------------------------
    # Archetypes
    # ------------------------------------------------------------------

    def _scrape_archetypes(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        soup = self.fetch(f"{self.BASE_URL}/6-archetypes/")
        if not soup:
            return results

        content = soup.find("article") or soup.find("div", class_="entry-content") or soup

        for header in content.find_all(["h2", "h3"]):
            name = extract_text(header).strip()
            if not name or len(name) > 50 or name.lower() in ("archetypes",):
                continue

            desc_parts: List[str] = []
            sibling = header.find_next_sibling()
            while sibling and sibling.name not in ("h2", "h3"):
                txt = extract_text(sibling)
                if txt:
                    desc_parts.append(txt)
                sibling = sibling.find_next_sibling()

            results[name] = {
                "name": name,
                "summary": " ".join(desc_parts)[:500],
                "source": f"{self.BASE_URL}/6-archetypes/",
            }

        return results

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def scrape_and_save(self) -> Path:
        bundle = self.scrape()
        return self.merge_and_save(bundle, self.OUTPUT_FILE)
