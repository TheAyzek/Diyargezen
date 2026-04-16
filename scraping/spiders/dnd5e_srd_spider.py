"""
D&D 5e Spider — 5e SRD API + 5esrd.com
========================================
D&D 5e açık SRD verisi çeker.

Birincil kaynak: 5e SRD REST API (https://www.dnd5eapi.co)
  - Temiz JSON API, HTML parse gerektirmez
  - Rate limit dostu, CORS açık

İkincil kaynak: 5esrd.com (HTML scraping gerektiğinde)

Yalnızca SRD (System Reference Document) kapsamındaki içerik çekilir;
üçüncü parti veya ücretli kitap verileri dahil edilmez.
"""

from __future__ import annotations

import logging
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from bs4 import BeautifulSoup

from scraping.base_scraper import BaseScraper, sanitize_html, extract_text
from scraping.models import (
    RaceModel, ClassModel, SpellModel, FeatModel,
    SystemDataBundle, SourceReference,
)

logger = logging.getLogger(__name__)

API_BASE = "https://www.dnd5eapi.co/api"


class DnD5eSRDSpider(BaseScraper):
    """D&D 5e SRD verisi çeken spider (API öncelikli)."""

    SYSTEM_KEY = "dnd5e"
    BASE_URL = "https://www.dnd5eapi.co"
    OUTPUT_FILE = "dnd_data.json"

    def __init__(self, output_dir: Optional[Path] = None, **kwargs) -> None:
        super().__init__(output_dir=output_dir, delay_range=(0.3, 1.0), **kwargs)

    # ------------------------------------------------------------------
    # JSON API Yardımcısı
    # ------------------------------------------------------------------

    def fetch_api(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """5e SRD REST API'den JSON çek."""
        url = f"{API_BASE}/{endpoint.lstrip('/')}"
        for attempt in range(1, self._max_retries + 1):
            try:
                self._rate_limit_wait()
                resp = self._session.get(url, timeout=self._timeout)
                self._request_count += 1
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                logger.warning("[dnd5e] API hatası %s (deneme %d): %s", url, attempt, exc)
                if attempt < self._max_retries:
                    import time, random
                    time.sleep(2 ** attempt + random.uniform(0, 1))
                else:
                    self._error_count += 1
        return None

    # ------------------------------------------------------------------
    # Ana Scrape
    # ------------------------------------------------------------------

    def scrape(self) -> SystemDataBundle:
        logger.info("═" * 60)
        logger.info("D&D 5e Spider başlatılıyor — dnd5eapi.co")
        logger.info("═" * 60)

        races = self.scrape_races()
        logger.info("Irklar tamamlandı: %d kayıt", len(races))

        classes = self.scrape_classes()
        logger.info("Sınıflar tamamlandı: %d kayıt", len(classes))

        spells = self.scrape_spells()
        logger.info("Büyüler tamamlandı: %d kayıt", len(spells))

        feats = self.scrape_feats()
        logger.info("Feats tamamlandı: %d kayıt", len(feats))

        stats = self.stats()
        logger.info(
            "Spider tamamlandı — %d istek, %d hata",
            stats["requests"], stats["errors"],
        )

        return SystemDataBundle(
            system="dnd5e",
            source="https://www.dnd5eapi.co",
            races=races,
            classes=classes,
            spells=spells,
            feats=feats,
        )

    # ------------------------------------------------------------------
    # Races
    # ------------------------------------------------------------------

    def scrape_races(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        index = self.fetch_api("races")
        if not index or "results" not in index:
            return results

        for entry in index["results"]:
            idx = entry.get("index", "")
            logger.info("  Irk çekiliyor: %s", idx)
            detail = self.fetch_api(f"races/{idx}")
            if not detail:
                continue

            parsed = self._api_race_to_model(detail)
            model = self.validate_item(parsed, RaceModel)
            if model:
                results[model.name] = model.model_dump(exclude_none=True)

            for sub in detail.get("subraces", []):
                sub_idx = sub.get("index", "")
                sub_detail = self.fetch_api(f"subraces/{sub_idx}")
                if not sub_detail:
                    continue
                sub_parsed = self._api_subrace_to_model(sub_detail, detail)
                sub_model = self.validate_item(sub_parsed, RaceModel)
                if sub_model:
                    results[sub_model.name] = sub_model.model_dump(exclude_none=True)

        return results

    def _api_race_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        bonuses: Dict[str, int] = {}
        for ab in data.get("ability_bonuses", []):
            key = ab.get("ability_score", {}).get("name", "").lower()
            if key:
                REMAP = {"str": "strength", "dex": "dexterity", "con": "constitution",
                         "int": "intelligence", "wis": "wisdom", "cha": "charisma"}
                key = REMAP.get(key, key)
                bonuses[key] = ab.get("bonus", 0)

        traits = [t.get("name", "") for t in data.get("traits", [])]
        languages = [l.get("name", "") for l in data.get("languages", [])]

        vision = "Normal"
        for t in traits:
            if "darkvision" in t.lower():
                vision = "Darkvision"
                break

        return {
            "name": data.get("name", ""),
            "system": "dnd5e",
            "description": data.get("alignment", ""),
            "ability_score_increase": bonuses,
            "speed": data.get("speed", 30),
            "size": data.get("size", "Medium"),
            "traits": traits,
            "languages": languages,
            "extra_languages": data.get("language_options", {}).get("choose", 0),
            "vision": vision,
            "source": {"url": f"{API_BASE}/races/{data.get('index', '')}"},
        }

    def _api_subrace_to_model(
        self, sub: Dict[str, Any], parent: Dict[str, Any],
    ) -> Dict[str, Any]:
        parent_bonuses = {}
        for ab in parent.get("ability_bonuses", []):
            key = ab.get("ability_score", {}).get("name", "").lower()
            REMAP = {"str": "strength", "dex": "dexterity", "con": "constitution",
                     "int": "intelligence", "wis": "wisdom", "cha": "charisma"}
            parent_bonuses[REMAP.get(key, key)] = ab.get("bonus", 0)

        for ab in sub.get("ability_bonuses", []):
            key = ab.get("ability_score", {}).get("name", "").lower()
            REMAP = {"str": "strength", "dex": "dexterity", "con": "constitution",
                     "int": "intelligence", "wis": "wisdom", "cha": "charisma"}
            parent_bonuses[REMAP.get(key, key)] = ab.get("bonus", 0)

        traits = [t.get("name", "") for t in parent.get("traits", [])]
        traits += [t.get("name", "") for t in sub.get("racial_traits", [])]
        languages = [l.get("name", "") for l in parent.get("languages", [])]

        return {
            "name": sub.get("name", ""),
            "system": "dnd5e",
            "description": sub.get("desc", ""),
            "ability_score_increase": parent_bonuses,
            "speed": parent.get("speed", 30),
            "size": parent.get("size", "Medium"),
            "traits": traits,
            "languages": languages,
            "source": {"url": f"{API_BASE}/subraces/{sub.get('index', '')}"},
        }

    # ------------------------------------------------------------------
    # Classes
    # ------------------------------------------------------------------

    def scrape_classes(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        index = self.fetch_api("classes")
        if not index or "results" not in index:
            return results

        for entry in index["results"]:
            idx = entry.get("index", "")
            logger.info("  Sınıf çekiliyor: %s", idx)
            detail = self.fetch_api(f"classes/{idx}")
            if not detail:
                continue

            parsed = self._api_class_to_model(detail)
            model = self.validate_item(parsed, ClassModel)
            if model:
                results[model.name] = model.model_dump(exclude_none=True)

        return results

    def _api_class_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        saves = [s.get("name", "") for s in data.get("saving_throws", [])]
        proficiencies = [p.get("name", "") for p in data.get("proficiencies", [])]
        skills = [s.get("name", "") for s in data.get("proficiency_choices", [{}])[0].get("from", {}).get("options", [])]

        has_spellcasting = "spellcasting" in data
        sc_type = ""
        if has_spellcasting:
            sc_info = data.get("spellcasting", {})
            sc_type = "prepared" if data.get("index") in ("cleric", "druid", "paladin", "wizard") else "spontaneous"

        return {
            "name": data.get("name", ""),
            "system": "dnd5e",
            "hit_die": f"d{data.get('hit_die', 8)}",
            "saving_throws": saves,
            "proficiencies": proficiencies,
            "class_skills": skills,
            "spellcasting": has_spellcasting,
            "spellcasting_type": sc_type,
            "source": {"url": f"{API_BASE}/classes/{data.get('index', '')}"},
        }

    # ------------------------------------------------------------------
    # Spells
    # ------------------------------------------------------------------

    def scrape_spells(self, max_spells: int = 500) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        index = self.fetch_api("spells")
        if not index or "results" not in index:
            return results

        entries = index["results"][:max_spells]
        logger.info("  %d büyü çekilecek...", len(entries))

        for i, entry in enumerate(entries):
            idx = entry.get("index", "")
            if i % 50 == 0:
                logger.info("    [%d/%d] ...", i, len(entries))

            detail = self.fetch_api(f"spells/{idx}")
            if not detail:
                continue

            parsed = self._api_spell_to_model(detail)
            model = self.validate_item(parsed, SpellModel)
            if model:
                results[model.name] = model.model_dump(exclude_none=True, by_alias=False)

        return results

    def _api_spell_to_model(self, data: Dict[str, Any]) -> Dict[str, Any]:
        desc_parts = data.get("desc", [])
        description = "\n".join(desc_parts) if isinstance(desc_parts, list) else str(desc_parts)

        higher = data.get("higher_level", [])
        higher_text = "\n".join(higher) if isinstance(higher, list) else str(higher or "")

        components = ", ".join(data.get("components", []))
        material = data.get("material", "")
        if material:
            components += f" ({material})"

        school_info = data.get("school", {})
        school = school_info.get("name", "") if isinstance(school_info, dict) else str(school_info)

        classes_for_spell: Dict[str, int] = {}
        for cls in data.get("classes", []):
            cls_name = cls.get("name", "")
            if cls_name:
                classes_for_spell[cls_name] = data.get("level", 0)

        concentration = data.get("concentration", False)
        is_ritual = data.get("ritual", False)

        return {
            "name": data.get("name", ""),
            "system": "dnd5e",
            "level": data.get("level", 0),
            "school": school.lower(),
            "casting_time": data.get("casting_time", ""),
            "components": components,
            "material_components": material,
            "range": data.get("range", ""),
            "duration": data.get("duration", ""),
            "description": description[:2000],
            "higher_levels": higher_text[:500],
            "concentration": concentration,
            "is_ritual": is_ritual,
            "levels_by_class": classes_for_spell,
            "source": {"url": f"{API_BASE}/spells/{data.get('index', '')}"},
        }

    # ------------------------------------------------------------------
    # Feats
    # ------------------------------------------------------------------

    def scrape_feats(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}

        index = self.fetch_api("feats")
        if not index or "results" not in index:
            return results

        for entry in index["results"]:
            idx = entry.get("index", "")
            logger.info("  Feat çekiliyor: %s", idx)
            detail = self.fetch_api(f"feats/{idx}")
            if not detail:
                continue

            prereqs: List[str] = []
            for p in detail.get("prerequisites", []):
                if "ability_score" in p:
                    ab = p["ability_score"].get("name", "")
                    val = p.get("minimum_score", 0)
                    prereqs.append(f"{ab} {val}+")
                elif "proficiency" in p:
                    prereqs.append(p["proficiency"].get("name", ""))

            desc_parts = detail.get("desc", [])
            description = "\n".join(desc_parts) if isinstance(desc_parts, list) else str(desc_parts)

            parsed = {
                "name": detail.get("name", ""),
                "system": "dnd5e",
                "description": description[:1000],
                "benefit": description[:500],
                "prerequisites": prereqs,
                "source": {"url": f"{API_BASE}/feats/{idx}"},
            }

            model = self.validate_item(parsed, FeatModel)
            if model:
                results[model.name] = model.model_dump(exclude_none=True)

        return results

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def scrape_and_save(self) -> Path:
        bundle = self.scrape()
        return self.merge_and_save(bundle, self.OUTPUT_FILE)
