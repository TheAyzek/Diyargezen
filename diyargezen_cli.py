from __future__ import annotations

"""
Tek giriş noktalı Diyargezen CLI.

Alt komutlar:
- D&D 5e karakter oluşturma
- D&D 5e level-up
- D&D 5e envanter yönetimi
- Kural dosyalarını listeleme / önizleme
- Şablon oluşturma / şablondan karakter yaratma
"""

from InquirerPy import inquirer

from dnd_cli import main as dnd_create_main
from dnd_inventory_cli import manage_inventory as dnd_inventory_main
from dnd_levelup_cli import main as dnd_levelup_main
from dnd_rules_cli import main as dnd_rules_main
from dnd_templates_cli import main as dnd_templates_main


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
    else:
        return


if __name__ == "__main__":
    main()









"""
Tek giriş noktalı Diyargezen CLI.

Alt komutlar:
- D&D 5e karakter oluşturma
- D&D 5e level-up
- D&D 5e envanter yönetimi
- Kural dosyalarını listeleme / önizleme
- Şablon oluşturma / şablondan karakter yaratma
"""

from InquirerPy import inquirer

from dnd_cli import main as dnd_create_main
from dnd_inventory_cli import manage_inventory as dnd_inventory_main
from dnd_levelup_cli import main as dnd_levelup_main
from dnd_rules_cli import main as dnd_rules_main
from dnd_templates_cli import main as dnd_templates_main


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
    else:
        return


if __name__ == "__main__":
    main()











"""
Tek giriş noktalı Diyargezen CLI.

Alt komutlar:
- D&D 5e karakter oluşturma
- D&D 5e level-up
- D&D 5e envanter yönetimi
- Kural dosyalarını listeleme / önizleme
- Şablon oluşturma / şablondan karakter yaratma
"""

from InquirerPy import inquirer

from dnd_cli import main as dnd_create_main
from dnd_inventory_cli import manage_inventory as dnd_inventory_main
from dnd_levelup_cli import main as dnd_levelup_main
from dnd_rules_cli import main as dnd_rules_main
from dnd_templates_cli import main as dnd_templates_main


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
    else:
        return


if __name__ == "__main__":
    main()









"""
Tek giriş noktalı Diyargezen CLI.

Alt komutlar:
- D&D 5e karakter oluşturma
- D&D 5e level-up
- D&D 5e envanter yönetimi
- Kural dosyalarını listeleme / önizleme
- Şablon oluşturma / şablondan karakter yaratma
"""

from InquirerPy import inquirer

from dnd_cli import main as dnd_create_main
from dnd_inventory_cli import manage_inventory as dnd_inventory_main
from dnd_levelup_cli import main as dnd_levelup_main
from dnd_rules_cli import main as dnd_rules_main
from dnd_templates_cli import main as dnd_templates_main


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
    else:
        return


if __name__ == "__main__":
    main()












