#!/usr/bin/env python3
"""
Diyargezen CLI - Komut satırı arayüzü
D&D 5e karakter oluşturma, level-up, envanter, kural ve şablon işlemleri
"""
import sys
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent.parent
if str(BASE_DIR) not in sys.path:
    sys.path.insert(0, str(BASE_DIR))
desktop_dir = Path(__file__).resolve().parent.parent
if str(desktop_dir) not in sys.path:
    sys.path.insert(0, str(desktop_dir))

from InquirerPy import inquirer

from desktop.cli.dnd_cli import main as dnd_create_main
from desktop.cli.dnd_inventory_cli import manage_inventory as dnd_inventory_main
from desktop.cli.dnd_levelup_cli import main as dnd_levelup_main
from desktop.cli.dnd_rules_cli import main as dnd_rules_main
from desktop.cli.dnd_templates_cli import main as dnd_templates_main


def main() -> None:
    action = inquirer.select(
        message="Diyargezen CLI - İşlem seçin:",
        choices=[
            "🧙 Yeni D&D Karakteri Oluştur",
            "📈 D&D Karakterini Level-Up Yap",
            "🎒 D&D Envanterini Yönet",
            "📚 Kuralları Listele / Önizle",
            "🧩 Şablon İşlemleri",
            "Çık",
        ],
    ).execute()

    if action.startswith("🧙"):
        dnd_create_main()
    elif action.startswith("📈"):
        dnd_levelup_main()
    elif action.startswith("🎒"):
        dnd_inventory_main()
    elif action.startswith("📚"):
        dnd_rules_main()
    elif action.startswith("🧩"):
        dnd_templates_main()


if __name__ == "__main__":
    main()
