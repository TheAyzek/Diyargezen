"""
Soft Validation (Esnek Doğrulama)
===================================
Kural ihlallerinde çökmez; uyarı döndürür. GUI popup ile homebrew onayı alır.
"""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class SoftValidationResult:
    """Doğrulama sonucu."""
    warnings: List[str] = field(default_factory=list)
    is_blocking: bool = False  # MVP'de hiçbir uyarı kaydı engellemez

    @property
    def has_warnings(self) -> bool:
        return len(self.warnings) > 0


# D&D 5e — seviyeye göre bilinen büyü slot üst sınırı (basitleştirilmiş)
_DND_SPELL_SLOTS: Dict[int, int] = {
    1: 2, 2: 3, 3: 4, 4: 4, 5: 6,
}


def _spell_count(char: Dict[str, Any]) -> int:
    spells = char.get("spells") or char.get("known_spells") or []
    if isinstance(spells, dict):
        return len(spells)
    if isinstance(spells, list):
        return len(spells)
    return 0


def _feat_count(char: Dict[str, Any]) -> int:
    feats = char.get("feats") or []
    return len(feats) if isinstance(feats, (list, dict)) else 0


def validate_dnd5e_soft(char: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> SoftValidationResult:
    result = SoftValidationResult()
    level = char.get("level", 1)
    if not isinstance(level, int):
        level = 1

    spell_n = _spell_count(char)
    max_spells = _DND_SPELL_SLOTS.get(level, level + 1)
    if spell_n > max_spells:
        result.warnings.append(
            f"Seviye {level} için {spell_n} büyü seçildi (önerilen üst sınır ~{max_spells})"
        )

    feat_n = _feat_count(char)
    expected_feats = max(0, (level // 4))  # ASI/feat seviyeleri (yaklaşık)
    if feat_n > expected_feats + 1:
        result.warnings.append(
            f"Seviye {level} için {feat_n} feat seçildi (kurallara göre genelde ≤{expected_feats + 1})"
        )

    race = char.get("race", "")
    cls = char.get("class", "")
    if data:
        if race and race not in data.get("races", {}):
            result.warnings.append(f"Irk '{race}' resmi veride yok")
        if cls and cls not in data.get("classes", {}):
            result.warnings.append(f"Sınıf '{cls}' resmi veride yok")

    abilities = char.get("abilities", {})
    for ab, score in abilities.items():
        if isinstance(score, int) and score > 20 and level < 10:
            result.warnings.append(f"{ab.title()} = {score} (seviye {level} için olağanüstü yüksek)")

    return result


def validate_pf1e_soft(char: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> SoftValidationResult:
    result = SoftValidationResult()
    level = char.get("level", 1)
    spell_n = _spell_count(char)
    if spell_n > level * 4:
        result.warnings.append(f"Seviye {level} için {spell_n} büyü (olası kural aşımı)")

    abilities = char.get("abilities", {})
    for ab, score in abilities.items():
        if isinstance(score, int) and not (7 <= score <= 18) and level == 1:
            result.warnings.append(f"PF1e başlangıç puanı dışı: {ab} = {score} (genelde 7-18)")

    return result


def validate_mm3e_soft(char: Dict[str, Any], data: Optional[Dict[str, Any]] = None) -> SoftValidationResult:
    result = SoftValidationResult()
    pl = char.get("pl_value", 10)
    remaining = char.get("remaining_power_points", 0)
    if remaining < 0:
        result.warnings.append(f"Negatif kalan power point: {remaining}")

    powers = char.get("powers", {})
    if isinstance(powers, dict) and len(powers) > pl * 3:
        result.warnings.append(f"PL{pl} için {len(powers)} güç (yoğun build — PL limitlerini kontrol edin)")

    return result


def validate_prerequisites(char: Dict[str, Any], db_path: Path) -> List[str]:
    # GM Override Bypass: If GM override is enabled, suppress all prerequisite warnings
    if char.get("is_overridden") is True or char.get("gm_override") is True:
        return []

    import sqlite3
    import json
    
    warnings = []
    
    # Standardize system name
    sys_key = char.get("system", "").lower().replace("_", "").replace("-", "")
    if "pf" in sys_key or "pathfinder" in sys_key:
        sys_db = "pathfinder1e"
    elif "mm" in sys_key:
        sys_db = "mm3e"
    else:
        sys_db = "dnd5e"
        
    abilities = {}
    is_mm = "mm" in sys_key
    default_val = 0 if is_mm else 10
    
    ab_list = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
    if is_mm:
        ab_list = ["strength", "stamina", "agility", "dexterity", "fighting", "intellect", "awareness", "presence"]
        
    for ab in ab_list:
        val = char.get("abilities", {}).get(ab)
        if val is None:
            for k, v in char.get("abilities", {}).items():
                if k.lower() == ab:
                    val = v
                    break
        if val is None:
            val = default_val
        try:
            abilities[ab] = int(val)
        except:
            abilities[ab] = default_val

    names_to_query = []
    
    def process_prereqs(entity: Any):
        if isinstance(entity, dict):
            sys_ver = entity.get("sistem_verisi") or entity.get("system") or entity.get("data")
            name = entity.get("name") or entity.get("isim") or ""
            if isinstance(sys_ver, dict):
                prereqs = sys_ver.get("prerequisites", [])
                for p in prereqs:
                    prereq_name = p.get("prerequisite", "").lower()
                    required_val = p.get("value")
                    if prereq_name and required_val is not None:
                        char_val = abilities.get(prereq_name, default_val)
                        if char_val < int(required_val):
                            warnings.append(
                                f"'{name}' gereksinimi karşılanamadı: "
                                f"{prereq_name.upper()} en az {required_val} olmalı (Mevcut: {char_val})"
                            )
                return True
        return False

    race = char.get("race")
    race_data = char.get("race_data")
    if not process_prereqs(race_data) and isinstance(race, str) and race:
        names_to_query.append(race)
        
    cls = char.get("class")
    class_data = char.get("class_data")
    if not process_prereqs(class_data) and isinstance(cls, str) and cls:
        names_to_query.append(cls)
        
    raw_feats = char.get("feats", [])
    if isinstance(raw_feats, list):
        for f in raw_feats:
            if not process_prereqs(f):
                if isinstance(f, str) and f:
                    names_to_query.append(f)
                elif isinstance(f, dict) and f.get("name"):
                    names_to_query.append(f["name"])
                    
    raw_items = char.get("equipment", [])
    if isinstance(raw_items, list):
        for item in raw_items:
            if not process_prereqs(item):
                if isinstance(item, str) and item:
                    names_to_query.append(item)
                elif isinstance(item, dict) and item.get("name"):
                    names_to_query.append(item["name"])
                    
    # Query database for remaining names
    if names_to_query:
        try:
            conn = sqlite3.connect(str(db_path))
            cursor = conn.cursor()
            placeholders = ",".join("?" for _ in names_to_query)
            cursor.execute(
                f"SELECT isim, sistem_verisi FROM entities WHERE sistem = ? AND isim IN ({placeholders})",
                [sys_db] + names_to_query
            )
            rows = cursor.fetchall()
            for row in rows:
                name, raw_json = row
                try:
                    payload = json.loads(raw_json) if raw_json else {}
                    prereqs = payload.get("prerequisites", [])
                    for p in prereqs:
                        prereq_name = p.get("prerequisite", "").lower()
                        required_val = p.get("value")
                        if prereq_name and required_val is not None:
                            char_val = abilities.get(prereq_name, default_val)
                            if char_val < int(required_val):
                                warnings.append(
                                    f"'{name}' gereksinimi karşılanamadı: "
                                    f"{prereq_name.upper()} en az {required_val} olmalı (Mevcut: {char_val})"
                                )
                except Exception:
                    pass
            conn.close()
        except Exception:
            pass
            
    return warnings


def validate_character_soft(
    char: Dict[str, Any],
    system_key: str,
    data: Optional[Dict[str, Any]] = None,
) -> SoftValidationResult:
    """Sistem anahtarına göre soft validation."""
    try:
        from app.core.config import DB_PATH as DEFAULT_DB_PATH
    except ImportError:
        try:
            from web.backend.app.core.config import DB_PATH as DEFAULT_DB_PATH
        except ImportError:
            DEFAULT_DB_PATH = Path(__file__).resolve().parent.parent / "data" / "characters.db"

    db_path = DEFAULT_DB_PATH

    
    key = system_key.lower().replace("_", "").replace("-", "")
    result = SoftValidationResult()

    # 1. Run legacy soft validation
    if key in ("dnd5e", "dnd", "dungeonsanddragons"):
        result = validate_dnd5e_soft(char, data)
    elif key in ("pathfinder1e", "pathfinder", "pf1e"):
        result = validate_pf1e_soft(char, data)
    elif key in ("mm3e", "mm", "mutantsandmasterminds"):
        result = validate_mm3e_soft(char, data)

    # 2. Run prerequisites check
    prereq_warnings = validate_prerequisites(char, db_path)
    for pw in prereq_warnings:
        if pw not in result.warnings:
            result.warnings.append(pw)

    # 3. Run modular validators from /rules
    try:
        from rules.pf1e_rules import PF1EValidator
        validator = PF1EValidator()
        new_warnings = validator.validate(char, data or {})
        for w in new_warnings:
            if w not in result.warnings:
                result.warnings.append(w)
    except Exception as e:
        logger.warning(f"Error running modular rules: {e}")

    return result


def mark_homebrew(char: Dict[str, Any], warnings: List[str]) -> Dict[str, Any]:
    """Kullanıcı onayladığında karaktere homebrew etiketi ekle."""
    char = dict(char)
    hb = char.setdefault("homebrew", [])
    if not isinstance(hb, list):
        hb = []
        char["homebrew"] = hb
    for w in warnings:
        entry = {"note": w, "source": "soft_validation"}
        if entry not in hb:
            hb.append(entry)
    char["is_homebrew"] = True
    return char


def format_warning_message(warnings: List[str]) -> str:
    lines = ["Uyarı: Bu seçim kural setine tam uymuyor.", ""]
    for w in warnings:
        lines.append(f"  • {w}")
    lines.append("")
    lines.append("Ev kuralı (Homebrew) olarak eklemek istiyor musunuz?")
    return "\n".join(lines)
