from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from cli import CharacterContext, CharacterWizard
from cli.steps import (
    AsiChoiceStep,
    AsiIncreaseStep,
    ClassFeaturesStep,
    FeatsStep,
    SpellsStep,
)
from cli.steps.levelup_core import HitPointStep, LevelSelectionStep
from utils.data_loader import load_dnd_data


def _load_character(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _pick_character(base_dir: Path) -> Path:
    from InquirerPy import inquirer

    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        raise SystemExit("Hiç kayıtlı karakter bulunamadı.")

    choices = [f.name for f in files]
    picked = inquirer.select(message="Seviye atlatılacak karakteri seç:", choices=choices).execute()
    return chars_dir / picked


def build_levelup_wizard(base_dir: Path, data: Dict[str, Any], ctx: CharacterContext) -> CharacterWizard:
    classes = data.get("classes", {})
    feats = data.get("equipment", {}).get("feats", {})

    steps = [
        LevelSelectionStep(),
        HitPointStep(classes=classes),
        AsiChoiceStep(),
        AsiIncreaseStep(abilities=list(data.get("abilities", []))),
        FeatsStep(feats_data=feats),
        ClassFeaturesStep(classes=classes),
        SpellsStep(classes=classes, all_spells=data.get("spells", {})),
    ]
    return CharacterWizard(steps)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_dnd_data(base_dir)

    char_path = _pick_character(base_dir)
    raw = _load_character(char_path)

    ctx = CharacterContext()
    # Eski veriden context'e temel alanları aktar
    ctx.name = raw.get("name")
    ctx.race = raw.get("race")
    ctx.char_class = raw.get("class")
    ctx.background = raw.get("background")
    ctx.level = raw.get("level", 1)
    # Ability skorları varsa yükle
    abil_scores = raw.get("abilities", {}).get("scores") or raw.get("abilities", {})
    if isinstance(abil_scores, dict):
        ctx.set_ability_scores({k: int(v) for k, v in abil_scores.items()})
    ctx.spells = raw.get("spells", {})
    ctx.features = raw.get("features", [])

    wizard = build_levelup_wizard(base_dir, data, ctx)
    ctx = wizard.run(ctx)

    # HP artışını uygula
    hp_gain = ctx.metadata.get("levelup", {}).get("hp_gain")
    if hp_gain is not None:
        current_hp = raw.get("hp", 0)
        raw["hp"] = current_hp + int(hp_gain)

    # Yeni level, feat ve spell'leri kaydet
    raw["level"] = ctx.level
    if ctx.spells:
        raw["spells"] = ctx.spells
    if ctx.features:
        raw["features"] = ctx.features

    _save_character(char_path, raw)
    print(f"\nKarakter güncellendi: {char_path}")


if __name__ == "__main__":
    main()



import json
from pathlib import Path
from typing import Any, Dict

from cli import CharacterContext, CharacterWizard
from cli.steps import (
    AsiChoiceStep,
    AsiIncreaseStep,
    ClassFeaturesStep,
    FeatsStep,
    SpellsStep,
)
from cli.steps.levelup_core import HitPointStep, LevelSelectionStep
from utils.data_loader import load_dnd_data


def _load_character(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _pick_character(base_dir: Path) -> Path:
    from InquirerPy import inquirer

    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        raise SystemExit("Hiç kayıtlı karakter bulunamadı.")

    choices = [f.name for f in files]
    picked = inquirer.select(message="Seviye atlatılacak karakteri seç:", choices=choices).execute()
    return chars_dir / picked


def build_levelup_wizard(base_dir: Path, data: Dict[str, Any], ctx: CharacterContext) -> CharacterWizard:
    classes = data.get("classes", {})
    feats = data.get("equipment", {}).get("feats", {})

    steps = [
        LevelSelectionStep(),
        HitPointStep(classes=classes),
        AsiChoiceStep(),
        AsiIncreaseStep(abilities=list(data.get("abilities", []))),
        FeatsStep(feats_data=feats),
        ClassFeaturesStep(classes=classes),
        SpellsStep(classes=classes, all_spells=data.get("spells", {})),
    ]
    return CharacterWizard(steps)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_dnd_data(base_dir)

    char_path = _pick_character(base_dir)
    raw = _load_character(char_path)

    ctx = CharacterContext()
    # Eski veriden context'e temel alanları aktar
    ctx.name = raw.get("name")
    ctx.race = raw.get("race")
    ctx.char_class = raw.get("class")
    ctx.background = raw.get("background")
    ctx.level = raw.get("level", 1)
    # Ability skorları varsa yükle
    abil_scores = raw.get("abilities", {}).get("scores") or raw.get("abilities", {})
    if isinstance(abil_scores, dict):
        ctx.set_ability_scores({k: int(v) for k, v in abil_scores.items()})
    ctx.spells = raw.get("spells", {})
    ctx.features = raw.get("features", [])

    wizard = build_levelup_wizard(base_dir, data, ctx)
    ctx = wizard.run(ctx)

    # HP artışını uygula
    hp_gain = ctx.metadata.get("levelup", {}).get("hp_gain")
    if hp_gain is not None:
        current_hp = raw.get("hp", 0)
        raw["hp"] = current_hp + int(hp_gain)

    # Yeni level, feat ve spell'leri kaydet
    raw["level"] = ctx.level
    if ctx.spells:
        raw["spells"] = ctx.spells
    if ctx.features:
        raw["features"] = ctx.features

    _save_character(char_path, raw)
    print(f"\nKarakter güncellendi: {char_path}")


if __name__ == "__main__":
    main()



import json
from pathlib import Path
from typing import Any, Dict

from cli import CharacterContext, CharacterWizard
from cli.steps import (
    AsiChoiceStep,
    AsiIncreaseStep,
    ClassFeaturesStep,
    FeatsStep,
    SpellsStep,
)
from cli.steps.levelup_core import HitPointStep, LevelSelectionStep
from utils.data_loader import load_dnd_data


def _load_character(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _pick_character(base_dir: Path) -> Path:
    from InquirerPy import inquirer

    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        raise SystemExit("Hiç kayıtlı karakter bulunamadı.")

    choices = [f.name for f in files]
    picked = inquirer.select(message="Seviye atlatılacak karakteri seç:", choices=choices).execute()
    return chars_dir / picked


def build_levelup_wizard(base_dir: Path, data: Dict[str, Any], ctx: CharacterContext) -> CharacterWizard:
    classes = data.get("classes", {})
    feats = data.get("equipment", {}).get("feats", {})

    steps = [
        LevelSelectionStep(),
        HitPointStep(classes=classes),
        AsiChoiceStep(),
        AsiIncreaseStep(abilities=list(data.get("abilities", []))),
        FeatsStep(feats_data=feats),
        ClassFeaturesStep(classes=classes),
        SpellsStep(classes=classes, all_spells=data.get("spells", {})),
    ]
    return CharacterWizard(steps)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_dnd_data(base_dir)

    char_path = _pick_character(base_dir)
    raw = _load_character(char_path)

    ctx = CharacterContext()
    # Eski veriden context'e temel alanları aktar
    ctx.name = raw.get("name")
    ctx.race = raw.get("race")
    ctx.char_class = raw.get("class")
    ctx.background = raw.get("background")
    ctx.level = raw.get("level", 1)
    # Ability skorları varsa yükle
    abil_scores = raw.get("abilities", {}).get("scores") or raw.get("abilities", {})
    if isinstance(abil_scores, dict):
        ctx.set_ability_scores({k: int(v) for k, v in abil_scores.items()})
    ctx.spells = raw.get("spells", {})
    ctx.features = raw.get("features", [])

    wizard = build_levelup_wizard(base_dir, data, ctx)
    ctx = wizard.run(ctx)

    # HP artışını uygula
    hp_gain = ctx.metadata.get("levelup", {}).get("hp_gain")
    if hp_gain is not None:
        current_hp = raw.get("hp", 0)
        raw["hp"] = current_hp + int(hp_gain)

    # Yeni level, feat ve spell'leri kaydet
    raw["level"] = ctx.level
    if ctx.spells:
        raw["spells"] = ctx.spells
    if ctx.features:
        raw["features"] = ctx.features

    _save_character(char_path, raw)
    print(f"\nKarakter güncellendi: {char_path}")


if __name__ == "__main__":
    main()



import json
from pathlib import Path
from typing import Any, Dict

from cli import CharacterContext, CharacterWizard
from cli.steps import (
    AsiChoiceStep,
    AsiIncreaseStep,
    ClassFeaturesStep,
    FeatsStep,
    SpellsStep,
)
from cli.steps.levelup_core import HitPointStep, LevelSelectionStep
from utils.data_loader import load_dnd_data


def _load_character(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _pick_character(base_dir: Path) -> Path:
    from InquirerPy import inquirer

    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        raise SystemExit("Hiç kayıtlı karakter bulunamadı.")

    choices = [f.name for f in files]
    picked = inquirer.select(message="Seviye atlatılacak karakteri seç:", choices=choices).execute()
    return chars_dir / picked


def build_levelup_wizard(base_dir: Path, data: Dict[str, Any], ctx: CharacterContext) -> CharacterWizard:
    classes = data.get("classes", {})
    feats = data.get("equipment", {}).get("feats", {})

    steps = [
        LevelSelectionStep(),
        HitPointStep(classes=classes),
        AsiChoiceStep(),
        AsiIncreaseStep(abilities=list(data.get("abilities", []))),
        FeatsStep(feats_data=feats),
        ClassFeaturesStep(classes=classes),
        SpellsStep(classes=classes, all_spells=data.get("spells", {})),
    ]
    return CharacterWizard(steps)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_dnd_data(base_dir)

    char_path = _pick_character(base_dir)
    raw = _load_character(char_path)

    ctx = CharacterContext()
    # Eski veriden context'e temel alanları aktar
    ctx.name = raw.get("name")
    ctx.race = raw.get("race")
    ctx.char_class = raw.get("class")
    ctx.background = raw.get("background")
    ctx.level = raw.get("level", 1)
    # Ability skorları varsa yükle
    abil_scores = raw.get("abilities", {}).get("scores") or raw.get("abilities", {})
    if isinstance(abil_scores, dict):
        ctx.set_ability_scores({k: int(v) for k, v in abil_scores.items()})
    ctx.spells = raw.get("spells", {})
    ctx.features = raw.get("features", [])

    wizard = build_levelup_wizard(base_dir, data, ctx)
    ctx = wizard.run(ctx)

    # HP artışını uygula
    hp_gain = ctx.metadata.get("levelup", {}).get("hp_gain")
    if hp_gain is not None:
        current_hp = raw.get("hp", 0)
        raw["hp"] = current_hp + int(hp_gain)

    # Yeni level, feat ve spell'leri kaydet
    raw["level"] = ctx.level
    if ctx.spells:
        raw["spells"] = ctx.spells
    if ctx.features:
        raw["features"] = ctx.features

    _save_character(char_path, raw)
    print(f"\nKarakter güncellendi: {char_path}")


if __name__ == "__main__":
    main()


