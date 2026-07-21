import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
desktop_dir = Path(__file__).resolve().parent.parent
if str(desktop_dir) not in sys.path:
    sys.path.insert(0, str(desktop_dir))

from desktop.cli import CharacterContext, CharacterWizard
from desktop.cli.steps import (
    AbilityStep,
    BackgroundStep,
    ClassSkillsStep,
    EquipmentStep,
    IntroStep,
    PersonalityStep,
    RaceStep,
    SpellsStep,
    SummaryStep,
)
from utils.data_loader import load_dnd_data


def build_wizard(base_dir: Path) -> CharacterWizard:
    data = load_dnd_data(base_dir)
    races = data.get("races", {})
    classes = data.get("classes", {})
    backgrounds = data.get("backgrounds", {})
    abilities = list(data.get("abilities", []))
    languages = list(data.get("languages", {}).keys()) if isinstance(data.get("languages"), dict) else []

    steps = [
        IntroStep(classes=sorted(classes.keys())),
        RaceStep(races=races),
        BackgroundStep(backgrounds=backgrounds),
        AbilityStep(abilities=abilities),
        PersonalityStep(available_languages=languages),
        ClassSkillsStep(classes=classes),
        SpellsStep(classes=classes, all_spells=data.get("spells", {})),
        EquipmentStep(classes=classes),
        SummaryStep(),
    ]
    return CharacterWizard(steps)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    ctx = CharacterContext()
    wizard = build_wizard(base_dir)
    ctx = wizard.run(ctx)

    # Basit JSON kayıt (ileride GUI ile aynı storage modülüne taşınabilir)
    from utils.storage import _safe_name  # type: ignore
    import json

    safe = _safe_name(ctx.name or "dnd_karakter")
    out_dir = base_dir / "characters"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{safe}_cli.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(ctx.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"\nKarakter kaydedildi: {out_path}")


if __name__ == "__main__":
    main()






def build_wizard(base_dir: Path) -> CharacterWizard:
    data = load_dnd_data(base_dir)
    races = data.get("races", {})
    classes = data.get("classes", {})
    backgrounds = data.get("backgrounds", {})
    abilities = list(data.get("abilities", []))
    languages = list(data.get("languages", {}).keys()) if isinstance(data.get("languages"), dict) else []

    steps = [
        IntroStep(classes=sorted(classes.keys())),
        RaceStep(races=races),
        BackgroundStep(backgrounds=backgrounds),
        AbilityStep(abilities=abilities),
        PersonalityStep(available_languages=languages),
        ClassSkillsStep(classes=classes),
        SpellsStep(classes=classes, all_spells=data.get("spells", {})),
        EquipmentStep(classes=classes),
        SummaryStep(),
    ]
    return CharacterWizard(steps)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    ctx = CharacterContext()
    wizard = build_wizard(base_dir)
    ctx = wizard.run(ctx)

    # Basit JSON kayıt (ileride GUI ile aynı storage modülüne taşınabilir)
    from utils.storage import _safe_name  # type: ignore
    import json

    safe = _safe_name(ctx.name or "dnd_karakter")
    out_dir = base_dir / "characters"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{safe}_cli.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(ctx.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"\nKarakter kaydedildi: {out_path}")


if __name__ == "__main__":
    main()






def build_wizard(base_dir: Path) -> CharacterWizard:
    data = load_dnd_data(base_dir)
    races = data.get("races", {})
    classes = data.get("classes", {})
    backgrounds = data.get("backgrounds", {})
    abilities = list(data.get("abilities", []))
    languages = list(data.get("languages", {}).keys()) if isinstance(data.get("languages"), dict) else []

    steps = [
        IntroStep(classes=sorted(classes.keys())),
        RaceStep(races=races),
        BackgroundStep(backgrounds=backgrounds),
        AbilityStep(abilities=abilities),
        PersonalityStep(available_languages=languages),
        ClassSkillsStep(classes=classes),
        SpellsStep(classes=classes, all_spells=data.get("spells", {})),
        EquipmentStep(classes=classes),
        SummaryStep(),
    ]
    return CharacterWizard(steps)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    ctx = CharacterContext()
    wizard = build_wizard(base_dir)
    ctx = wizard.run(ctx)

    # Basit JSON kayıt (ileride GUI ile aynı storage modülüne taşınabilir)
    from utils.storage import _safe_name  # type: ignore
    import json

    safe = _safe_name(ctx.name or "dnd_karakter")
    out_dir = base_dir / "characters"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{safe}_cli.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(ctx.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"\nKarakter kaydedildi: {out_path}")


if __name__ == "__main__":
    main()






def build_wizard(base_dir: Path) -> CharacterWizard:
    data = load_dnd_data(base_dir)
    races = data.get("races", {})
    classes = data.get("classes", {})
    backgrounds = data.get("backgrounds", {})
    abilities = list(data.get("abilities", []))
    languages = list(data.get("languages", {}).keys()) if isinstance(data.get("languages"), dict) else []

    steps = [
        IntroStep(classes=sorted(classes.keys())),
        RaceStep(races=races),
        BackgroundStep(backgrounds=backgrounds),
        AbilityStep(abilities=abilities),
        PersonalityStep(available_languages=languages),
        ClassSkillsStep(classes=classes),
        SpellsStep(classes=classes, all_spells=data.get("spells", {})),
        EquipmentStep(classes=classes),
        SummaryStep(),
    ]
    return CharacterWizard(steps)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    ctx = CharacterContext()
    wizard = build_wizard(base_dir)
    ctx = wizard.run(ctx)

    # Basit JSON kayıt (ileride GUI ile aynı storage modülüne taşınabilir)
    from utils.storage import _safe_name  # type: ignore
    import json

    safe = _safe_name(ctx.name or "dnd_karakter")
    out_dir = base_dir / "characters"
    out_dir.mkdir(parents=True, exist_ok=True)
    out_path = out_dir / f"{safe}_cli.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(ctx.to_dict(), f, ensure_ascii=False, indent=2)
    print(f"\nKarakter kaydedildi: {out_path}")


if __name__ == "__main__":
    main()


