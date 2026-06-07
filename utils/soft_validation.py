"""
Soft Validation (Esnek Doğrulama)
===================================
Kural ihlallerinde çökmez; uyarı döndürür. GUI popup ile homebrew onayı alır.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


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


def validate_character_soft(
    char: Dict[str, Any],
    system_key: str,
    data: Optional[Dict[str, Any]] = None,
) -> SoftValidationResult:
    """Sistem anahtarına göre soft validation."""
    key = system_key.lower().replace("_", "")
    if key in ("dnd5e", "dnd", "dungeonsanddragons"):
        return validate_dnd5e_soft(char, data)
    if key in ("pathfinder1e", "pathfinder", "pf1e"):
        return validate_pf1e_soft(char, data)
    if key in ("mm3e", "mm", "mutantsandmasterminds"):
        return validate_mm3e_soft(char, data)
    return SoftValidationResult()


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
    lines = ["Bu seçim kural setine tam uymuyor:", ""]
    for w in warnings:
        lines.append(f"  • {w}")
    lines.append("")
    lines.append("Ev kuralı (Homebrew) olarak eklemek istiyor musunuz?")
    return "\n".join(lines)
