from __future__ import annotations

from pathlib import Path

from InquirerPy import inquirer
from rich import print as rprint

from utils.rule_storage import load_rules, save_rules, list_available_rules
from utils.rule_preview import format_rule_preview


def _pick_system() -> str:
    return inquirer.select(
        message="Sistem seç:",
        choices=["DND5E", "MUTANTS_AND_MASTERMINDS", "VTM5E"],
    ).execute()


def show_rules(base_dir: Path) -> None:
    system = _pick_system()
    rules = load_rules(base_dir, system)
    if not rules:
        rprint("[yellow]Bu sistem için kayıtlı kural bulunamadı.[/yellow]")
        return
    text = format_rule_preview(rules)
    rprint(text)


def list_rules_files(base_dir: Path) -> None:
    available = list_available_rules(base_dir)
    rprint("Mevcut kural dosyaları:")
    for system, exists in available.items():
        mark = "✅" if exists else "❌"
        rprint(f" {mark} {system}")


def main() -> None:
    base_dir = Path(__file__).resolve().parent
    action = inquirer.select(
        message="Kural işlemi:",
        choices=["Kuralları Listele", "Kural Önizleme", "Çık"],
    ).execute()

    if action == "Kuralları Listele":
        list_rules_files(base_dir)
    elif action == "Kural Önizleme":
        show_rules(base_dir)


if __name__ == "__main__":
    main()





