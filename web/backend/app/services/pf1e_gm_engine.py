"""Explainable, soft-blocking PF1e rules orchestration.

This layer deliberately sits above the calculator.  A calculator answers
"what is the value?"; the GM engine also explains why a selection is unusual
and records whether it was explicitly allowed by the table's GM.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, asdict
from typing import Any, Dict, Iterable, List


ABILITY_NAMES = {
    "str": "strength", "dex": "dexterity", "con": "constitution",
    "int": "intelligence", "wis": "wisdom", "cha": "charisma",
}


@dataclass
class RuleDiagnostic:
    code: str
    message: str
    severity: str = "warning"
    can_override: bool = True
    overridden: bool = False


class PF1eGMEngine:
    """Validates selection prerequisites without hard-blocking a player."""

    def check_prerequisites(
        self, character: Dict[str, Any], prerequisites: Iterable[str], is_overridden: bool = False
    ) -> List[RuleDiagnostic]:
        abilities = {k.lower(): int(v) for k, v in (character.get("abilities") or {}).items() if isinstance(v, (int, float))}
        bab = int(character.get("bab", character.get("base_attack_bonus", 0)) or 0)
        level = int(character.get("level", 1) or 1)
        feats = {self._normalise_name(x) for x in character.get("feats", [])}
        diagnostics: List[RuleDiagnostic] = []

        if isinstance(prerequisites, str):
            prerequisites = [prerequisites]
        clauses = []
        for raw in prerequisites or []:
            if isinstance(raw, dict) and 'prerequisite' in raw:
                raw = f"{raw['prerequisite']} {raw.get('value', '')}"
            if re.search(r'\bor\b', str(raw), re.I):
                diagnostics.append(RuleDiagnostic('unparsed_prerequisite', f'Alternatif koşullar GM incelemesi gerektirir: {raw}', 'warning', True, is_overridden))
                continue
            clauses.extend(re.split(r'\s*(?:[,;]|\band\b)\s*', str(raw)))
        for raw in clauses:
            text = str(raw).strip()
            lower = text.lower()
            ability_match = re.search(r"\b(str|dex|con|int|wis|cha)(?:ength|terity|stitution|elligence|dom|risma)?\s*(?:>=|≥)?\s*(\d+)", lower)
            bab_match = re.search(r"(?:base attack bonus|bab)\s*\+?(\d+)", lower)
            level_match = re.search(r"(?:character )?level\s*(\d+)", lower)
            feat_match = re.search(r"(?:feat|özellik)\s*[:\-]?\s*(.+)", text, re.I)

            if ability_match:
                ability = ABILITY_NAMES[ability_match.group(1)]
                required = int(ability_match.group(2))
                actual = abilities.get(ability, abilities.get(ability[:3], 10))
                if actual < required:
                    diagnostics.append(self._diagnostic("ability_prerequisite", f"{ability.title()} {required} gerekir (mevcut: {actual}).", is_overridden))
            elif bab_match:
                required = int(bab_match.group(1))
                if bab < required:
                    diagnostics.append(self._diagnostic("bab_prerequisite", f"BAB +{required} gerekir (mevcut: +{bab}).", is_overridden))
            elif level_match:
                required = int(level_match.group(1))
                if level < required:
                    diagnostics.append(self._diagnostic("level_prerequisite", f"Seviye {required} gerekir (mevcut: {level}).", is_overridden))
            elif feat_match:
                required = self._normalise_name(feat_match.group(1))
                if required not in feats:
                    diagnostics.append(self._diagnostic("feat_prerequisite", f"Ön koşul feat eksik: {feat_match.group(1).strip()}.", is_overridden))
            elif text:
                diagnostics.append(RuleDiagnostic("unparsed_prerequisite", f"Manuel GM incelemesi gerekli ön koşul: {text}", "warning", True, is_overridden))
        return diagnostics

    def evaluate_character(self, character: Dict[str, Any]) -> List[Dict[str, Any]]:
        diagnostics: List[RuleDiagnostic] = []
        for selection in character.get("selections", []) or []:
            diagnostics.extend(self.check_prerequisites(
                character,
                selection.get("prerequisites", []),
                bool(selection.get("is_overridden", False) and str(selection.get('reason', '')).strip()),
            ))
        for group in ('feats', 'spells'):
            for selection in character.get(group, []) or []:
                if not isinstance(selection, dict):
                    continue
                data = selection.get('sistem_verisi') or selection
                prerequisites = data.get('raw_prerequisites') or (data.get('system') or {}).get('prerequisites') or data.get('prerequisites') or []
                diagnostics.extend(self.check_prerequisites(character, prerequisites,
                    bool(selection.get('is_overridden') and str(selection.get('override_reason', '')).strip())))
        def inspect_sources(value):
            if isinstance(value, dict):
                provenance = value.get('_provenance') or {}
                if provenance.get('fallback_fields'):
                    diagnostics.append(RuleDiagnostic('scraper_fallback',
                        'Foundry eksikleri scraper verisinden tamamlandı: ' + ', '.join(provenance['fallback_fields']),
                        'info', False, False))
                if provenance.get('conflicts'):
                    diagnostics.append(RuleDiagnostic('source_conflict',
                        'Kural kaynakları arasında çelişki var; Foundry önceliği kullanıldı. GM incelemesi önerilir.',
                        'info', False, False))
                for key, child in value.items():
                    if key != '_provenance':
                        inspect_sources(child)
            elif isinstance(value, list):
                for child in value:
                    inspect_sources(child)
        inspect_sources(character)
        return [asdict(item) for item in diagnostics]

    @staticmethod
    def _diagnostic(code: str, message: str, overridden: bool) -> RuleDiagnostic:
        suffix = " GM override kaydı nedeniyle seçim uygulanacak." if overridden else " GM izniyle uygulanabilir."
        return RuleDiagnostic(code, message + suffix, "warning", True, overridden)

    @staticmethod
    def _normalise_name(value: Any) -> str:
        if isinstance(value, dict):
            value = value.get('isim') or value.get('name') or ''
        return " ".join(str(value).lower().split())
