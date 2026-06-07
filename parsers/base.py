"""Parser yardımcıları — eksik key'lerde çökmez."""

from __future__ import annotations

import logging
from typing import Any, Dict, Iterable, List, Optional

from models.entity import DiyargezenEntity

logger = logging.getLogger(__name__)

# kategori → creators'ın beklediği dict anahtarı
CATEGORY_TO_SECTION: Dict[str, str] = {
    "race": "races",
    "class": "classes",
    "spell": "spells",
    "feat": "feats",
    "background": "backgrounds",
    "skill": "skills",
    "item": "items",
    "equipment": "equipment",
    "power": "powers",
    "advantage": "advantages",
    "ability": "abilities",
    "archetype": "archetypes",
    "complication": "complications",
    "language": "languages",
}


def safe_str(value: Any, default: str = "") -> str:
    try:
        if value is None:
            return default
        return str(value).strip()
    except Exception:
        return default


def safe_dict(value: Any) -> Dict[str, Any]:
    return value if isinstance(value, dict) else {}


def extract_description(payload: Dict[str, Any]) -> str:
    for key in ("description", "desc", "benefit", "text", "summary"):
        text = safe_str(payload.get(key))
        if text:
            return text[:4000]
    return ""


def make_entity(
    isim: str,
    sistem: str,
    kategori: str,
    payload: Any,
) -> Optional[DiyargezenEntity]:
    """Tek bir kaydı güvenli şekilde DiyargezenEntity'ye dönüştür."""
    try:
        name = safe_str(isim)
        if not name:
            return None
        data = safe_dict(payload)
        if not data.get("name"):
            data = {**data, "name": name}
        return DiyargezenEntity(
            isim=name,
            sistem=sistem,
            kategori=kategori,
            aciklama=extract_description(data),
            sistem_verisi=data,
        )
    except Exception as exc:
        logger.debug("Entity atlandı (%s/%s): %s", kategori, isim, exc)
        return None


def parse_section(
    raw: Any,
    sistem: str,
    kategori: str,
) -> List[DiyargezenEntity]:
    """Dict veya list formatındaki bir bölümü entity listesine çevir."""
    entities: List[DiyargezenEntity] = []

    if isinstance(raw, dict):
        for key, val in raw.items():
            ent = make_entity(safe_str(key), sistem, kategori, val)
            if ent:
                entities.append(ent)
    elif isinstance(raw, list):
        for item in raw:
            if isinstance(item, str):
                ent = make_entity(item, sistem, kategori, {"name": item})
            elif isinstance(item, dict):
                name = safe_str(item.get("name") or item.get("id") or item.get("key"))
                ent = make_entity(name, sistem, kategori, item)
            else:
                continue
            if ent:
                entities.append(ent)

    return entities


def parse_sections(
    data: Dict[str, Any],
    sistem: str,
    mapping: Dict[str, str],
) -> List[DiyargezenEntity]:
    """Birden fazla JSON bölümünü tek seferde parse et."""
    out: List[DiyargezenEntity] = []
    for json_key, kategori in mapping.items():
        try:
            section = data.get(json_key)
            if section:
                out.extend(parse_section(section, sistem, kategori))
        except Exception as exc:
            logger.warning("%s → %s parse hatası: %s", sistem, json_key, exc)
    return out
