from __future__ import annotations

from typing import Dict

from ..context import CharacterContext


def check_feat_prerequisites(ctx: CharacterContext, prerequisites: Dict) -> bool:
    """CLI karşılığı: feat önkoşullarını kontrol et."""
    if not prerequisites:
        return True

    scores = ctx.abilities.scores
    level = ctx.level or 1

    for req_type, req_value in prerequisites.items():
        if req_type == "ability_score_minimum":
            for ability, minimum in req_value.items():
                if scores.get(ability, 0) < int(minimum):
                    return False
        elif req_type == "level":
            if level < int(req_value):
                return False
        elif req_type == "proficiency":
            # Şimdilik yoksay
            continue

    return True


def calculate_available_feat_count(level: int, race: str) -> int:
    """Seviye ve ırka göre alınabilir feat sayısını hesapla."""
    feat_count = 0
    for feat_level in [4, 6, 8, 12, 14, 16, 19]:
        if level >= feat_level:
            feat_count += 1

    if race == "Human":
        feat_count += 1

    return feat_count












