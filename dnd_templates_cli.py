from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict

from InquirerPy import inquirer

from utils.template_manager import (
    create_character_from_template,
    list_templates,
    save_template,
)


def _pick_character(base_dir: Path) -> Dict[str, Any] | None:
    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        print("Hiç kayıtlı karakter yok.")
        return None
    choice = inquirer.select(
        message="Şablon oluşturmak için karakter seç:",
        choices=[f.name for f in files],
    ).execute()
    path = chars_dir / choice
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(base_dir: Path, character: Dict[str, Any]) -> None:
    from utils.storage import _safe_name  # type: ignore

    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    safe = _safe_name(character.get("name", "template_char"))
    out_path = chars_dir / f"{safe}_from_template.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False, indent=2)
    print(f"Karakter kaydedildi: {out_path}")


def create_template_cli(base_dir: Path) -> None:
    character = _pick_character(base_dir)
    if not character:
        return
    name = inquirer.text(message="Şablon adı:").execute()
    desc = inquirer.text(message="Şablon açıklaması (opsiyonel):").execute()
    path = save_template(character, base_dir, name, desc)
    print(f"Şablon kaydedildi: {path}")


def use_template_cli(base_dir: Path) -> None:
    templates = list_templates(base_dir, system_filter="DND5E")
    if not templates:
        print("Hiç DND5E şablonu yok.")
        return
    choice = inquirer.select(
        message="Şablon seç:",
        choices=[t["template_name"] for t in templates],
    ).execute()
    tmpl = next(t for t in templates if t["template_name"] == choice)
    char_name = inquirer.text(message="Yeni karakter adı:").execute()
    character = create_character_from_template(tmpl, char_name)
    _save_character(base_dir, character)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    action = inquirer.select(
        message="Şablon işlemi:",
        choices=["Şablon Oluştur", "Şablondan Karakter Yarat", "Çık"],
    ).execute()

    if action == "Şablon Oluştur":
        create_template_cli(base_dir)
    elif action == "Şablondan Karakter Yarat":
        use_template_cli(base_dir)


if __name__ == "__main__":
    main()









import json
from pathlib import Path
from typing import Any, Dict

from InquirerPy import inquirer

from utils.template_manager import (
    create_character_from_template,
    list_templates,
    save_template,
)


def _pick_character(base_dir: Path) -> Dict[str, Any] | None:
    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        print("Hiç kayıtlı karakter yok.")
        return None
    choice = inquirer.select(
        message="Şablon oluşturmak için karakter seç:",
        choices=[f.name for f in files],
    ).execute()
    path = chars_dir / choice
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(base_dir: Path, character: Dict[str, Any]) -> None:
    from utils.storage import _safe_name  # type: ignore

    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    safe = _safe_name(character.get("name", "template_char"))
    out_path = chars_dir / f"{safe}_from_template.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False, indent=2)
    print(f"Karakter kaydedildi: {out_path}")


def create_template_cli(base_dir: Path) -> None:
    character = _pick_character(base_dir)
    if not character:
        return
    name = inquirer.text(message="Şablon adı:").execute()
    desc = inquirer.text(message="Şablon açıklaması (opsiyonel):").execute()
    path = save_template(character, base_dir, name, desc)
    print(f"Şablon kaydedildi: {path}")


def use_template_cli(base_dir: Path) -> None:
    templates = list_templates(base_dir, system_filter="DND5E")
    if not templates:
        print("Hiç DND5E şablonu yok.")
        return
    choice = inquirer.select(
        message="Şablon seç:",
        choices=[t["template_name"] for t in templates],
    ).execute()
    tmpl = next(t for t in templates if t["template_name"] == choice)
    char_name = inquirer.text(message="Yeni karakter adı:").execute()
    character = create_character_from_template(tmpl, char_name)
    _save_character(base_dir, character)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    action = inquirer.select(
        message="Şablon işlemi:",
        choices=["Şablon Oluştur", "Şablondan Karakter Yarat", "Çık"],
    ).execute()

    if action == "Şablon Oluştur":
        create_template_cli(base_dir)
    elif action == "Şablondan Karakter Yarat":
        use_template_cli(base_dir)


if __name__ == "__main__":
    main()











import json
from pathlib import Path
from typing import Any, Dict

from InquirerPy import inquirer

from utils.template_manager import (
    create_character_from_template,
    list_templates,
    save_template,
)


def _pick_character(base_dir: Path) -> Dict[str, Any] | None:
    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        print("Hiç kayıtlı karakter yok.")
        return None
    choice = inquirer.select(
        message="Şablon oluşturmak için karakter seç:",
        choices=[f.name for f in files],
    ).execute()
    path = chars_dir / choice
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(base_dir: Path, character: Dict[str, Any]) -> None:
    from utils.storage import _safe_name  # type: ignore

    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    safe = _safe_name(character.get("name", "template_char"))
    out_path = chars_dir / f"{safe}_from_template.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False, indent=2)
    print(f"Karakter kaydedildi: {out_path}")


def create_template_cli(base_dir: Path) -> None:
    character = _pick_character(base_dir)
    if not character:
        return
    name = inquirer.text(message="Şablon adı:").execute()
    desc = inquirer.text(message="Şablon açıklaması (opsiyonel):").execute()
    path = save_template(character, base_dir, name, desc)
    print(f"Şablon kaydedildi: {path}")


def use_template_cli(base_dir: Path) -> None:
    templates = list_templates(base_dir, system_filter="DND5E")
    if not templates:
        print("Hiç DND5E şablonu yok.")
        return
    choice = inquirer.select(
        message="Şablon seç:",
        choices=[t["template_name"] for t in templates],
    ).execute()
    tmpl = next(t for t in templates if t["template_name"] == choice)
    char_name = inquirer.text(message="Yeni karakter adı:").execute()
    character = create_character_from_template(tmpl, char_name)
    _save_character(base_dir, character)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    action = inquirer.select(
        message="Şablon işlemi:",
        choices=["Şablon Oluştur", "Şablondan Karakter Yarat", "Çık"],
    ).execute()

    if action == "Şablon Oluştur":
        create_template_cli(base_dir)
    elif action == "Şablondan Karakter Yarat":
        use_template_cli(base_dir)


if __name__ == "__main__":
    main()









import json
from pathlib import Path
from typing import Any, Dict

from InquirerPy import inquirer

from utils.template_manager import (
    create_character_from_template,
    list_templates,
    save_template,
)


def _pick_character(base_dir: Path) -> Dict[str, Any] | None:
    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        print("Hiç kayıtlı karakter yok.")
        return None
    choice = inquirer.select(
        message="Şablon oluşturmak için karakter seç:",
        choices=[f.name for f in files],
    ).execute()
    path = chars_dir / choice
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(base_dir: Path, character: Dict[str, Any]) -> None:
    from utils.storage import _safe_name  # type: ignore

    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    safe = _safe_name(character.get("name", "template_char"))
    out_path = chars_dir / f"{safe}_from_template.json"
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(character, f, ensure_ascii=False, indent=2)
    print(f"Karakter kaydedildi: {out_path}")


def create_template_cli(base_dir: Path) -> None:
    character = _pick_character(base_dir)
    if not character:
        return
    name = inquirer.text(message="Şablon adı:").execute()
    desc = inquirer.text(message="Şablon açıklaması (opsiyonel):").execute()
    path = save_template(character, base_dir, name, desc)
    print(f"Şablon kaydedildi: {path}")


def use_template_cli(base_dir: Path) -> None:
    templates = list_templates(base_dir, system_filter="DND5E")
    if not templates:
        print("Hiç DND5E şablonu yok.")
        return
    choice = inquirer.select(
        message="Şablon seç:",
        choices=[t["template_name"] for t in templates],
    ).execute()
    tmpl = next(t for t in templates if t["template_name"] == choice)
    char_name = inquirer.text(message="Yeni karakter adı:").execute()
    character = create_character_from_template(tmpl, char_name)
    _save_character(base_dir, character)


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    action = inquirer.select(
        message="Şablon işlemi:",
        choices=["Şablon Oluştur", "Şablondan Karakter Yarat", "Çık"],
    ).execute()

    if action == "Şablon Oluştur":
        create_template_cli(base_dir)
    elif action == "Şablondan Karakter Yarat":
        use_template_cli(base_dir)


if __name__ == "__main__":
    main()












