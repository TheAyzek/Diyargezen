"""
D&D 5e Spider — dnd5eapi.co REST API
======================================
D&D 5e SRD verisini resmi acik kaynak REST API uzerinden ceker.
HTML scraping yerine yapilandirilmis JSON kullanir — daha hizli ve guvenilir.

Endpoint'ler:
  /api/races        -> Irklar + subrace'ler
  /api/classes      -> Siniflar + hit_die, saving_throws, proficiencies
  /api/spells       -> Buyuler (tum SRD spell'leri)
  /api/feats        -> Feat'ler
  /api/backgrounds  -> Background'lar (ekstra veri)
  /api/equipment    -> Ekipman (ekstra veri)
  /api/skills       -> Beceri listesi

Tum ciktilar Pydantic modelleriyle dogrulanir.
"""

from __future__ import annotations

import logging
import random
import time
from pathlib import Path
from typing import Any, Dict, List, Optional

from scraping.base_scraper import BaseScraper
from scraping.models import (
    RaceModel, ClassModel, SpellModel, FeatModel,
    SystemDataBundle,
)

logger = logging.getLogger(__name__)

API_BASE = "https://www.dnd5eapi.co/api"

_ABILITY_REMAP = {
    "str": "strength", "dex": "dexterity", "con": "constitution",
    "int": "intelligence", "wis": "wisdom", "cha": "charisma",
    "strength": "strength", "dexterity": "dexterity",
    "constitution": "constitution", "intelligence": "intelligence",
    "wisdom": "wisdom", "charisma": "charisma",
}

_PREPARED_CASTERS = {"cleric", "druid", "paladin", "wizard", "ranger", "artificer"}


class DnD5eSpider(BaseScraper):
    """dnd5eapi.co REST API uzerinden D&D 5e SRD verisi ceker."""

    SYSTEM_KEY = "dnd5e"
    BASE_URL = "https://www.dnd5eapi.co"
    OUTPUT_FILE = "dnd_data.json"

    def __init__(self, output_dir: Optional[Path] = None, **kwargs) -> None:
        super().__init__(output_dir=output_dir, delay_range=(0.2, 0.6), **kwargs)

    # ------------------------------------------------------------------
    # API Yardimcisi
    # ------------------------------------------------------------------

    def fetch_api(self, endpoint: str) -> Optional[Dict[str, Any]]:
        """REST API'den JSON cek (retry + rate-limit)."""
        url = f"{API_BASE}/{endpoint.lstrip('/')}"
        for attempt in range(1, self._max_retries + 1):
            try:
                self._rate_limit_wait()
                resp = self._session.get(url, timeout=self._timeout)
                self._request_count += 1
                if resp.status_code == 429:
                    wait = int(resp.headers.get("Retry-After", 5))
                    logger.warning("[dnd5e] 429 Rate Limited — %ds bekleniyor", wait)
                    time.sleep(wait)
                    continue
                resp.raise_for_status()
                return resp.json()
            except Exception as exc:
                logger.warning("[dnd5e] API hatasi %s (deneme %d): %s", url, attempt, exc)
                if attempt < self._max_retries:
                    time.sleep(2 ** attempt + random.uniform(0, 1))
                else:
                    self._error_count += 1
        return None

    def _fetch_index(self, endpoint: str) -> List[Dict[str, Any]]:
        """Bir index endpoint'inden tum sonuclari al."""
        data = self.fetch_api(endpoint)
        if not data:
            return []
        return data.get("results", [])

    def _log_progress(self, section: str, current: int, total: int) -> None:
        pct = (current / total * 100) if total else 0
        logger.info("  [D&D 5e] %s %d/%d (%%%.0f)", section, current, total, pct)

    # ------------------------------------------------------------------
    # Ana Scrape
    # ------------------------------------------------------------------

    def scrape(self) -> SystemDataBundle:
        logger.info("=" * 60)
        logger.info("[D&D 5e] Spider baslatiliyor — dnd5eapi.co REST API")
        logger.info("=" * 60)

        races = self.scrape_races()
        logger.info("[D&D 5e] Irklar tamamlandi: %d kayit", len(races))

        classes = self.scrape_classes()
        logger.info("[D&D 5e] Siniflar tamamlandi: %d kayit", len(classes))

        spells = self.scrape_spells()
        logger.info("[D&D 5e] Buyuler tamamlandi: %d kayit", len(spells))

        feats = self.scrape_feats()
        logger.info("[D&D 5e] Feat'ler tamamlandi: %d kayit", len(feats))

        backgrounds = self._scrape_backgrounds()
        skills = self._scrape_skills()
        equipment = self._scrape_equipment()

        s = self.stats()
        logger.info("[D&D 5e] Toplam: %d istek, %d hata", s["requests"], s["errors"])

        return SystemDataBundle(
            system="dnd5e",
            source="https://www.dnd5eapi.co",
            races=races,
            classes=classes,
            spells=spells,
            feats=feats,
            skills=skills,
            extra={"backgrounds": backgrounds, "equipment": equipment},
        )

    # ------------------------------------------------------------------
    # Races
    # ------------------------------------------------------------------

    def scrape_races(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        entries = self._fetch_index("races")
        total = len(entries)

        for i, entry in enumerate(entries):
            idx = entry.get("index", "")
            self._log_progress("Irklar", i + 1, total)

            detail = self.fetch_api(f"races/{idx}")
            if not detail:
                continue

            parsed = self._map_race(detail)
            model = self.validate_item(parsed, RaceModel)
            if model:
                results[model.name] = model.model_dump(exclude_none=True)

            for sub in detail.get("subraces", []):
                sub_idx = sub.get("index", "")
                sub_detail = self.fetch_api(f"subraces/{sub_idx}")
                if not sub_detail:
                    continue
                sub_parsed = self._map_subrace(sub_detail, detail)
                sub_model = self.validate_item(sub_parsed, RaceModel)
                if sub_model:
                    results[sub_model.name] = sub_model.model_dump(exclude_none=True)

        return results

    def _map_race(self, data: Dict[str, Any]) -> Dict[str, Any]:
        bonuses = self._extract_ability_bonuses(data.get("ability_bonuses", []))
        traits = [t.get("name", "") for t in data.get("traits", [])]
        languages = [l.get("name", "") for l in data.get("languages", [])]
        vision = "Darkvision" if any("darkvision" in t.lower() for t in traits) else "Normal"

        desc_parts = []
        if data.get("alignment"):
            desc_parts.append(data["alignment"])
        if data.get("age"):
            desc_parts.append(data["age"])
        if data.get("size_description"):
            desc_parts.append(data["size_description"])

        return {
            "name": data.get("name", ""),
            "system": "dnd5e",
            "description": " ".join(desc_parts)[:500],
            "ability_score_increase": bonuses,
            "speed": data.get("speed", 30),
            "size": data.get("size", "Medium"),
            "traits": traits,
            "languages": languages,
            "extra_languages": data.get("language_options", {}).get("choose", 0),
            "vision": vision,
            "source": {"url": f"{API_BASE}/races/{data.get('index', '')}"},
        }

    def _map_subrace(self, sub: Dict[str, Any], parent: Dict[str, Any]) -> Dict[str, Any]:
        bonuses = self._extract_ability_bonuses(parent.get("ability_bonuses", []))
        bonuses.update(self._extract_ability_bonuses(sub.get("ability_bonuses", [])))

        traits = [t.get("name", "") for t in parent.get("traits", [])]
        traits += [t.get("name", "") for t in sub.get("racial_traits", [])]
        languages = [l.get("name", "") for l in parent.get("languages", [])]

        return {
            "name": sub.get("name", ""),
            "system": "dnd5e",
            "description": sub.get("desc", ""),
            "ability_score_increase": bonuses,
            "speed": parent.get("speed", 30),
            "size": parent.get("size", "Medium"),
            "traits": traits,
            "languages": languages,
            "source": {"url": f"{API_BASE}/subraces/{sub.get('index', '')}"},
        }

    @staticmethod
    def _extract_ability_bonuses(bonuses_list: List[Dict]) -> Dict[str, int]:
        result: Dict[str, int] = {}
        for ab in bonuses_list:
            key = ab.get("ability_score", {}).get("name", "").lower()
            mapped = _ABILITY_REMAP.get(key, key)
            if mapped:
                result[mapped] = ab.get("bonus", 0)
        return result

    # ------------------------------------------------------------------
    # Classes
    # ------------------------------------------------------------------

    def scrape_classes(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        entries = self._fetch_index("classes")
        total = len(entries)

        for i, entry in enumerate(entries):
            idx = entry.get("index", "")
            self._log_progress("Siniflar", i + 1, total)

            detail = self.fetch_api(f"classes/{idx}")
            if not detail:
                continue

            parsed = self._map_class(detail)
            model = self.validate_item(parsed, ClassModel)
            if model:
                results[model.name] = model.model_dump(exclude_none=True)

        return results

    def _map_class(self, data: Dict[str, Any]) -> Dict[str, Any]:
        saves = [s.get("name", "") for s in data.get("saving_throws", [])]
        profs = [p.get("name", "") for p in data.get("proficiencies", [])]

        skills: List[str] = []
        for choice in data.get("proficiency_choices", []):
            for opt in choice.get("from", {}).get("options", []):
                item = opt.get("item", opt)
                if isinstance(item, dict):
                    skills.append(item.get("name", ""))

        has_spell = "spellcasting" in data
        idx = data.get("index", "")
        sc_type = "prepared" if idx in _PREPARED_CASTERS else ("spontaneous" if has_spell else "")

        return {
            "name": data.get("name", ""),
            "system": "dnd5e",
            "hit_die": f"d{data.get('hit_die', 8)}",
            "saving_throws": saves,
            "proficiencies": profs,
            "class_skills": skills,
            "spellcasting": has_spell,
            "spellcasting_type": sc_type,
            "source": {"url": f"{API_BASE}/classes/{idx}"},
        }

    # ------------------------------------------------------------------
    # Spells
    # ------------------------------------------------------------------

    def scrape_spells(self, max_spells: int = 500) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        entries = self._fetch_index("spells")[:max_spells]
        total = len(entries)

        for i, entry in enumerate(entries):
            idx = entry.get("index", "")
            if i % 50 == 0:
                self._log_progress("Buyuler", i, total)

            detail = self.fetch_api(f"spells/{idx}")
            if not detail:
                continue

            parsed = self._map_spell(detail)
            model = self.validate_item(parsed, SpellModel)
            if model:
                results[model.name] = model.model_dump(exclude_none=True, by_alias=False)

        return results

    def _map_spell(self, data: Dict[str, Any]) -> Dict[str, Any]:
        desc = data.get("desc", [])
        description = "\n".join(desc) if isinstance(desc, list) else str(desc)

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
            "concentration": data.get("concentration", False),
            "is_ritual": data.get("ritual", False),
            "levels_by_class": classes_for_spell,
            "source": {"url": f"{API_BASE}/spells/{data.get('index', '')}"},
        }

    # ------------------------------------------------------------------
    # Feats
    # ------------------------------------------------------------------

    def scrape_feats(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        entries = self._fetch_index("feats")
        total = len(entries)

        for i, entry in enumerate(entries):
            idx = entry.get("index", "")
            self._log_progress("Feat'ler", i + 1, total)

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
                elif "level" in p:
                    prereqs.append(f"Level {p['level']}+")

            desc = detail.get("desc", [])
            description = "\n".join(desc) if isinstance(desc, list) else str(desc)

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
    # Ekstra Veriler (backgrounds, skills, equipment)
    # ------------------------------------------------------------------

    def _scrape_backgrounds(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        entries = self._fetch_index("backgrounds")
        for entry in entries:
            idx = entry.get("index", "")
            detail = self.fetch_api(f"backgrounds/{idx}")
            if not detail:
                continue
            profs = [p.get("name", "") for p in detail.get("starting_proficiencies", [])]
            equip = [e.get("equipment", {}).get("name", "") for e in detail.get("starting_equipment", [])]
            feature = detail.get("feature", {})
            results[detail.get("name", idx)] = {
                "name": detail.get("name", ""),
                "proficiencies": profs,
                "equipment": equip,
                "feature": feature.get("name", "") if isinstance(feature, dict) else "",
                "feature_desc": "\n".join(feature.get("desc", [])) if isinstance(feature, dict) else "",
            }
        logger.info("[D&D 5e] Background'lar: %d kayit", len(results))
        return results

    def _scrape_skills(self) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        entries = self._fetch_index("skills")
        for entry in entries:
            idx = entry.get("index", "")
            detail = self.fetch_api(f"skills/{idx}")
            if not detail:
                continue
            desc = detail.get("desc", [])
            results[detail.get("name", idx)] = {
                "name": detail.get("name", ""),
                "key_ability": detail.get("ability_score", {}).get("name", ""),
                "description": "\n".join(desc) if isinstance(desc, list) else str(desc),
            }
        logger.info("[D&D 5e] Beceriler: %d kayit", len(results))
        return results

    def _scrape_equipment(self, max_items: int = 250) -> Dict[str, Any]:
        results: Dict[str, Any] = {}
        entries = self._fetch_index("equipment")[:max_items]
        total = len(entries)
        for i, entry in enumerate(entries):
            idx = entry.get("index", "")
            if i % 50 == 0:
                self._log_progress("Ekipman", i, total)
            detail = self.fetch_api(f"equipment/{idx}")
            if not detail:
                continue
            results[detail.get("name", idx)] = {
                "name": detail.get("name", ""),
                "equipment_category": detail.get("equipment_category", {}).get("name", ""),
                "cost": detail.get("cost", {}),
                "weight": detail.get("weight", 0),
            }
        logger.info("[D&D 5e] Ekipman: %d kayit", len(results))
        return results

    # ------------------------------------------------------------------
    # Convenience
    # ------------------------------------------------------------------

    def scrape_and_save(self) -> Path:
        bundle = self.scrape()
        return self.merge_and_save(bundle, self.OUTPUT_FILE)
