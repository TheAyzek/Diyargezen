"""
Vampire: The Masquerade 5e Spider — Wiki Scraping
===================================================
VtM 5e'nin resmi bir SRD'si olmadigindan, fan wiki kaynaklarindan
veri cekilir. HTML yapisi standart disinda olabilecegi icin
agresif try-except bloklari ile graceful degradation uygulanir.

Hedef kaynaklar (oncelik sirasina gore):
  1. vtm.paradoxwikis.com (resmi Paradox wiki)
  2. whitewolf.fandom.com  (yedek — Fandom wiki)

Cekilen veri:
  - Clans        -> ClanModel (disiplinler, bane, compulsion)
  - Disciplines  -> DisciplineModel (seviye basamaklari)
  - Predator Types -> ekstra dict
  - Loresheets    -> ekstra dict

ONEMLI: Bu spider diger spider'lara kiyasla cok daha savunmaci
yazilmistir. Beklenen HTML yapisi bulunmazsa o bolum atlanir,
program cokmez.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup, Tag

from scraping.base_scraper import BaseScraper, sanitize_html, extract_text, extract_list_items
from scraping.models import (
    ClanModel, DisciplineModel, SystemDataBundle,
)

logger = logging.getLogger(__name__)

_KNOWN_CLANS = [
    "Brujah", "Gangrel", "Malkavian", "Nosferatu",
    "Toreador", "Tremere", "Ventrue", "Caitiff",
    "Thin-Blood", "Banu Haqim", "Hecata", "Lasombra",
    "Ministry", "Ravnos", "Salubri", "Tzimisce",
]

_KNOWN_DISCIPLINES = [
    "Animalism", "Auspex", "Blood Sorcery", "Celerity",
    "Dominate", "Fortitude", "Obfuscate", "Oblivion",
    "Potence", "Presence", "Protean", "Thin-Blood Alchemy",
]


class VtM5eSpider(BaseScraper):
    """VtM 5e wiki kaynaklarindan veri ceker (graceful degradation)."""

    SYSTEM_KEY = "vtm5e"
    BASE_URL = "https://vtm.paradoxwikis.com"
    FALLBACK_URL = "https://whitewolf.fandom.com/wiki"
    OUTPUT_FILE = "vtm_data.json"

    def __init__(self, output_dir: Optional[Path] = None, **kwargs) -> None:
        super().__init__(output_dir=output_dir, delay_range=(2.0, 4.0), **kwargs)

    def _log_progress(self, section: str, current: int, total: int) -> None:
        pct = (current / total * 100) if total else 0
        logger.info("  [VtM 5e] %s %d/%d (%%%.0f)", section, current, total, pct)

    def _safe_fetch(self, url: str, context: str = "") -> Optional[BeautifulSoup]:
        """Guvenli fetch — hata durumunda None doner, loglama yapar."""
        try:
            return self.fetch(url)
        except Exception as exc:
            logger.warning("[VtM 5e] %s fetch hatasi (%s): %s", context, url, exc)
            return None

    # ------------------------------------------------------------------
    # Ana Scrape
    # ------------------------------------------------------------------

    def scrape(self) -> SystemDataBundle:
        logger.info("=" * 60)
        logger.info("[VtM 5e] Spider baslatiliyor — Wiki Scraping")
        logger.info("  Birincil: %s", self.BASE_URL)
        logger.info("  Yedek:    %s", self.FALLBACK_URL)
        logger.info("=" * 60)

        clans = self.scrape_races()
        logger.info("[VtM 5e] Clan'lar: %d kayit", len(clans))

        disciplines = self._scrape_disciplines()
        logger.info("[VtM 5e] Disiplinler: %d kayit", len(disciplines))

        predator_types = self._scrape_predator_types()
        logger.info("[VtM 5e] Predator Type'lar: %d kayit", len(predator_types))

        s = self.stats()
        logger.info("[VtM 5e] Toplam: %d istek, %d hata", s["requests"], s["errors"])

        return SystemDataBundle(
            system="vtm5e",
            source=self.BASE_URL,
            extra={
                "clans": clans,
                "disciplines": disciplines,
                "predator_types": predator_types,
            },
        )

    def scrape_classes(self) -> Dict[str, Any]:
        return {}

    # ------------------------------------------------------------------
    # Clans
    # ------------------------------------------------------------------

    def scrape_races(self) -> Dict[str, Any]:
        """Clan'lari cek — VtM'de 'race' yerine 'clan' kullanilir."""
        results: Dict[str, Any] = {}
        total = len(_KNOWN_CLANS)

        for i, clan_name in enumerate(_KNOWN_CLANS):
            self._log_progress("Clan'lar", i + 1, total)

            parsed = self._fetch_clan(clan_name)
            if not parsed:
                continue

            try:
                model = self.validate_item(parsed, ClanModel)
                if model:
                    results[model.name] = model.model_dump(exclude_none=True)
            except Exception as exc:
                logger.warning("[VtM 5e] Clan dogrulama hatasi '%s': %s", clan_name, exc)

        return results

    def _fetch_clan(self, clan_name: str) -> Optional[Dict[str, Any]]:
        """Tek bir clan'in verisini wiki'den cek. Fallback destegi."""
        slug = clan_name.replace(" ", "_")

        soup = self._safe_fetch(
            f"{self.BASE_URL}/wiki/{slug}_(VtM)", f"Clan {clan_name}",
        )
        if not soup:
            soup = self._safe_fetch(
                f"{self.BASE_URL}/wiki/{slug}", f"Clan {clan_name} (alt)",
            )
        if not soup:
            soup = self._safe_fetch(
                f"{self.FALLBACK_URL}/{slug}_(VtM)", f"Clan {clan_name} (fallback)",
            )
        if not soup:
            logger.info("  [VtM 5e] '%s' bulunamadi — atlanıyor", clan_name)
            return None

        return self._parse_clan_page(soup, clan_name)

    def _parse_clan_page(self, soup: BeautifulSoup, clan_name: str) -> Dict[str, Any]:
        """Wiki sayfasindan clan verisini parse et — agresif try-except."""
        data: Dict[str, Any] = {
            "name": clan_name,
            "system": "vtm5e",
            "source": {"url": f"{self.BASE_URL}/wiki/{clan_name.replace(' ', '_')}"},
        }

        content = (
            soup.find("div", class_="mw-parser-output")
            or soup.find("div", id="mw-content-text")
            or soup.find("article")
            or soup
        )

        try:
            first_p = content.find("p")
            if first_p:
                data["description"] = sanitize_html(str(first_p))[:500]
        except Exception:
            pass

        try:
            self._extract_infobox(content, data)
        except Exception:
            pass

        try:
            self._extract_disciplines_from_page(content, data)
        except Exception:
            pass

        try:
            self._extract_bane(content, data)
        except Exception:
            pass

        try:
            self._extract_compulsion(content, data)
        except Exception:
            pass

        return data

    def _extract_infobox(self, content: Tag, data: Dict[str, Any]) -> None:
        """Wiki infobox tablosundan veri cek."""
        infobox = content.find("table", class_=re.compile(r"infobox|sidebar|wikitable", re.IGNORECASE))
        if not infobox:
            return

        for row in infobox.find_all("tr"):
            header = row.find("th")
            value = row.find("td")
            if not header or not value:
                continue

            key = extract_text(header).lower().strip()
            val = extract_text(value).strip()

            if "discipline" in key:
                data["disciplines"] = [d.strip() for d in re.split(r"[,\n]", val) if d.strip()]
            elif "bane" in key or "curse" in key:
                data["bane"] = val[:300]
            elif "compulsion" in key:
                data["compulsion"] = val[:300]
            elif "favored" in key and "attribute" in key:
                data["favored_attributes"] = [a.strip() for a in val.split(",") if a.strip()]

    def _extract_disciplines_from_page(self, content: Tag, data: Dict[str, Any]) -> None:
        """Govde metninden disiplin isimlerini cikar."""
        if "disciplines" in data and data["disciplines"]:
            return

        found: List[str] = []
        full_text = extract_text(content)
        for disc in _KNOWN_DISCIPLINES:
            pattern = re.compile(
                r"(?:Discipline|in-clan|clan discipline)[s]?[:\s].*?" + re.escape(disc),
                re.IGNORECASE,
            )
            if pattern.search(full_text):
                found.append(disc)

        if not found:
            for disc in _KNOWN_DISCIPLINES:
                if disc.lower() in full_text.lower():
                    found.append(disc)

        if found:
            data["disciplines"] = list(dict.fromkeys(found))[:5]

    def _extract_bane(self, content: Tag, data: Dict[str, Any]) -> None:
        """Bane/Curse bilgisini header'dan cikar."""
        if data.get("bane"):
            return
        for header in content.find_all(["h2", "h3", "h4"]):
            if re.search(r"bane|curse|weakness", extract_text(header), re.IGNORECASE):
                sibling = header.find_next_sibling()
                if sibling:
                    data["bane"] = extract_text(sibling)[:300]
                    return

    def _extract_compulsion(self, content: Tag, data: Dict[str, Any]) -> None:
        """Compulsion bilgisini cikar."""
        if data.get("compulsion"):
            return
        for header in content.find_all(["h2", "h3", "h4"]):
            if re.search(r"compulsion", extract_text(header), re.IGNORECASE):
                sibling = header.find_next_sibling()
                if sibling:
                    data["compulsion"] = extract_text(sibling)[:300]
                    return

    # ------------------------------------------------------------------
    # Disciplines
    # ------------------------------------------------------------------

    def _scrape_disciplines(self) -> Dict[str, Any]:
        """Disiplin sayfalarindan detayli guc bilgisi cek."""
        results: Dict[str, Any] = {}
        total = len(_KNOWN_DISCIPLINES)

        for i, disc_name in enumerate(_KNOWN_DISCIPLINES):
            self._log_progress("Disiplinler", i + 1, total)

            try:
                parsed = self._fetch_discipline(disc_name)
                if not parsed:
                    continue
                model = self.validate_item(parsed, DisciplineModel)
                if model:
                    results[model.name] = model.model_dump(exclude_none=True)
            except Exception as exc:
                logger.warning("[VtM 5e] Discipline hatasi '%s': %s", disc_name, exc)

        return results

    def _fetch_discipline(self, disc_name: str) -> Optional[Dict[str, Any]]:
        slug = disc_name.replace(" ", "_")

        soup = self._safe_fetch(
            f"{self.BASE_URL}/wiki/{slug}_(VtM)", f"Discipline {disc_name}",
        )
        if not soup:
            soup = self._safe_fetch(
                f"{self.BASE_URL}/wiki/{slug}", f"Discipline {disc_name} (alt)",
            )
        if not soup:
            soup = self._safe_fetch(
                f"{self.FALLBACK_URL}/{slug}_(VtM)", f"Discipline {disc_name} (fallback)",
            )
        if not soup:
            return None

        return self._parse_discipline_page(soup, disc_name)

    def _parse_discipline_page(self, soup: BeautifulSoup, name: str) -> Dict[str, Any]:
        data: Dict[str, Any] = {
            "name": name,
            "system": "vtm5e",
            "source": {"url": f"{self.BASE_URL}/wiki/{name.replace(' ', '_')}"},
        }

        content = (
            soup.find("div", class_="mw-parser-output")
            or soup.find("div", id="mw-content-text")
            or soup.find("article")
            or soup
        )

        try:
            first_p = content.find("p")
            if first_p:
                data["description"] = sanitize_html(str(first_p))[:500]
        except Exception:
            pass

        powers: Dict[str, str] = {}
        try:
            level_pattern = re.compile(r"(?:Level|Dot)\s*(\d)")
            for header in content.find_all(["h2", "h3", "h4"]):
                text = extract_text(header)
                level_match = level_pattern.search(text)
                if level_match:
                    level = level_match.group(1)
                    power_name_tag = header.find_next_sibling()
                    if power_name_tag:
                        power_name = extract_text(power_name_tag)
                        if power_name and len(power_name) < 80:
                            powers[level] = power_name
                elif text and len(text) < 60 and not any(
                    kw in text.lower() for kw in ("contents", "edit", "reference", "see also", "navigation")
                ):
                    sibling = header.find_next_sibling()
                    if sibling:
                        desc = extract_text(sibling)
                        if desc and len(desc) > 10:
                            level_from_order = str(len(powers) + 1)
                            if level_from_order not in powers:
                                powers[level_from_order] = text
        except Exception:
            pass

        if powers:
            data["powers"] = powers

        return data

    # ------------------------------------------------------------------
    # Predator Types
    # ------------------------------------------------------------------

    def _scrape_predator_types(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        soup = self._safe_fetch(
            f"{self.BASE_URL}/wiki/Predator_Type_(VtM)", "Predator Types",
        )
        if not soup:
            soup = self._safe_fetch(
                f"{self.FALLBACK_URL}/Predator_Type_(VtM)", "Predator Types (fallback)",
            )
        if not soup:
            return results

        content = (
            soup.find("div", class_="mw-parser-output")
            or soup.find("div", id="mw-content-text")
            or soup
        )

        try:
            for header in content.find_all(["h2", "h3"]):
                name = extract_text(header).strip()
                if not name or len(name) > 40 or name.lower() in (
                    "contents", "references", "see also", "navigation",
                    "predator types", "predator type",
                ):
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
                    "description": " ".join(desc_parts)[:400],
                }
        except Exception as exc:
            logger.warning("[VtM 5e] Predator type parse hatasi: %s", exc)

        return results

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def scrape_and_save(self) -> Path:
        bundle = self.scrape()
        return self.merge_and_save(bundle, self.OUTPUT_FILE)
