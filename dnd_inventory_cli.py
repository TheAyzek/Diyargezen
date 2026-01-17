from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from InquirerPy import inquirer
from rich import print as rprint
from rich.table import Table

from cli import CharacterContext
from utils.data_loader import load_dnd_data


def _pick_character(base_dir: Path) -> Path:
    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        raise SystemExit("Hiç kayıtlı karakter bulunamadı.")
    choice = inquirer.select(
        message="Envanteri yönetilecek karakteri seç:",
        choices=[f.name for f in files],
    ).execute()
    return chars_dir / choice


def _load_character(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _select_item(items: List[str], title: str) -> str | None:
    if not items:
        print("Seçilebilir eşya yok.")
        return None
    return inquirer.select(message=title, choices=items + ["İptal"]).execute()


def _parse_cost(cost: Any) -> float:
    """
    '10 gp' gibi maliyetleri sayıya çevir (sadece gp bazında).
    """
    if isinstance(cost, (int, float)):
        return float(cost)
    if not isinstance(cost, str):
        return 0.0
    parts = cost.split()
    try:
        return float(parts[0])
    except (ValueError, IndexError):
        return 0.0


def _parse_weight(weight: Any) -> float:
    try:
        return float(weight)
    except (TypeError, ValueError):
        return 0.0


def _build_item_lookup(equip_data: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
    """
    İsim → (weight, cost) şeklinde hızlı lookup tablosu oluştur.
    """
    lookup: Dict[str, Tuple[float, float]] = {}

    for cat in ("weapons", "armor"):
        for name, info in equip_data.get(cat, {}).items():
            lookup[name] = (_parse_weight(info.get("weight", 0)), _parse_cost(info.get("cost", "0 gp")))

    for name, info in equip_data.get("adventuring_gear", {}).items():
        lookup[name] = (_parse_weight(info.get("weight", 0)), _parse_cost(info.get("cost", "0 gp")))

    return lookup


def _print_inventory(ctx: CharacterContext, item_lookup: Dict[str, Tuple[float, float]]) -> None:
    if not ctx.equipment:
        rprint("[yellow]Envanter boş.[/yellow]")
        return

    table = Table(title="📦 Envanter", show_lines=False)
    table.add_column("Eşya")
    table.add_column("Ağırlık (lb)", justify="right")
    table.add_column("Maliyet (gp)", justify="right")

    total_weight = 0.0
    total_cost = 0.0

    for item in ctx.equipment:
        w, c = item_lookup.get(item, (0.0, 0.0))
        total_weight += w
        total_cost += c
        table.add_row(item, f"{w:.1f}" if w else "-", f"{c:.1f}" if c else "-")

    rprint(table)
    rprint(f"[bold]Toplam ağırlık:[/bold] {total_weight:.1f} lb")
    rprint(f"[bold]Toplam maliyet:[/bold] {total_cost:.1f} gp\n")


def manage_inventory() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_dnd_data(base_dir)
    equip_data = data.get("equipment", {})
    item_lookup = _build_item_lookup(equip_data)

    char_path = _pick_character(base_dir)
    raw = _load_character(char_path)

    ctx = CharacterContext()
    ctx.equipment = [e for e in raw.get("equipment", []) if isinstance(e, str)]

    while True:
        action = inquirer.select(
            message="Envanter işlemi:",
            choices=["Eşya Ekle", "Eşya Çıkar", "Listele (toplam ağırlık/altın)", "Kaydet ve Çık"],
        ).execute()

        if action == "Eşya Ekle":
            category = inquirer.select(
                message="Kategori seç:",
                choices=["weapons", "armor", "adventuring_gear", "İptal"],
            ).execute()
            if category == "İptal":
                continue
            items_dict = equip_data.get(category, {})
            item_names = sorted(items_dict.keys())
            picked = _select_item(item_names, "Eklenecek eşyayı seç:")
            if picked and picked != "İptal":
                ctx.add_equipment([picked])
                rprint(f"[green]➕ {picked} eklendi.[/green]")

        elif action == "Eşya Çıkar":
            if not ctx.equipment:
                rprint("[yellow]Envanter boş.[/yellow]")
                continue
            picked = _select_item(ctx.equipment, "Çıkarılacak eşyayı seç:")
            if picked and picked != "İptal":
                ctx.equipment.remove(picked)
                rprint(f"[red]➖ {picked} çıkarıldı.[/red]")

        elif action.startswith("Listele"):
            _print_inventory(ctx, item_lookup)

        elif action == "Kaydet ve Çık":
            break

    raw["equipment"] = ctx.equipment
    _save_character(char_path, raw)
    print(f"\nEnvanter güncellendi: {char_path}")


if __name__ == "__main__":
    manage_inventory()



import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from InquirerPy import inquirer
from rich import print as rprint
from rich.table import Table

from cli import CharacterContext
from utils.data_loader import load_dnd_data


def _pick_character(base_dir: Path) -> Path:
    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        raise SystemExit("Hiç kayıtlı karakter bulunamadı.")
    choice = inquirer.select(
        message="Envanteri yönetilecek karakteri seç:",
        choices=[f.name for f in files],
    ).execute()
    return chars_dir / choice


def _load_character(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _select_item(items: List[str], title: str) -> str | None:
    if not items:
        print("Seçilebilir eşya yok.")
        return None
    return inquirer.select(message=title, choices=items + ["İptal"]).execute()


def _parse_cost(cost: Any) -> float:
    """
    '10 gp' gibi maliyetleri sayıya çevir (sadece gp bazında).
    """
    if isinstance(cost, (int, float)):
        return float(cost)
    if not isinstance(cost, str):
        return 0.0
    parts = cost.split()
    try:
        return float(parts[0])
    except (ValueError, IndexError):
        return 0.0


def _parse_weight(weight: Any) -> float:
    try:
        return float(weight)
    except (TypeError, ValueError):
        return 0.0


def _build_item_lookup(equip_data: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
    """
    İsim → (weight, cost) şeklinde hızlı lookup tablosu oluştur.
    """
    lookup: Dict[str, Tuple[float, float]] = {}

    for cat in ("weapons", "armor"):
        for name, info in equip_data.get(cat, {}).items():
            lookup[name] = (_parse_weight(info.get("weight", 0)), _parse_cost(info.get("cost", "0 gp")))

    for name, info in equip_data.get("adventuring_gear", {}).items():
        lookup[name] = (_parse_weight(info.get("weight", 0)), _parse_cost(info.get("cost", "0 gp")))

    return lookup


def _print_inventory(ctx: CharacterContext, item_lookup: Dict[str, Tuple[float, float]]) -> None:
    if not ctx.equipment:
        rprint("[yellow]Envanter boş.[/yellow]")
        return

    table = Table(title="📦 Envanter", show_lines=False)
    table.add_column("Eşya")
    table.add_column("Ağırlık (lb)", justify="right")
    table.add_column("Maliyet (gp)", justify="right")

    total_weight = 0.0
    total_cost = 0.0

    for item in ctx.equipment:
        w, c = item_lookup.get(item, (0.0, 0.0))
        total_weight += w
        total_cost += c
        table.add_row(item, f"{w:.1f}" if w else "-", f"{c:.1f}" if c else "-")

    rprint(table)
    rprint(f"[bold]Toplam ağırlık:[/bold] {total_weight:.1f} lb")
    rprint(f"[bold]Toplam maliyet:[/bold] {total_cost:.1f} gp\n")


def manage_inventory() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_dnd_data(base_dir)
    equip_data = data.get("equipment", {})
    item_lookup = _build_item_lookup(equip_data)

    char_path = _pick_character(base_dir)
    raw = _load_character(char_path)

    ctx = CharacterContext()
    ctx.equipment = [e for e in raw.get("equipment", []) if isinstance(e, str)]

    while True:
        action = inquirer.select(
            message="Envanter işlemi:",
            choices=["Eşya Ekle", "Eşya Çıkar", "Listele (toplam ağırlık/altın)", "Kaydet ve Çık"],
        ).execute()

        if action == "Eşya Ekle":
            category = inquirer.select(
                message="Kategori seç:",
                choices=["weapons", "armor", "adventuring_gear", "İptal"],
            ).execute()
            if category == "İptal":
                continue
            items_dict = equip_data.get(category, {})
            item_names = sorted(items_dict.keys())
            picked = _select_item(item_names, "Eklenecek eşyayı seç:")
            if picked and picked != "İptal":
                ctx.add_equipment([picked])
                rprint(f"[green]➕ {picked} eklendi.[/green]")

        elif action == "Eşya Çıkar":
            if not ctx.equipment:
                rprint("[yellow]Envanter boş.[/yellow]")
                continue
            picked = _select_item(ctx.equipment, "Çıkarılacak eşyayı seç:")
            if picked and picked != "İptal":
                ctx.equipment.remove(picked)
                rprint(f"[red]➖ {picked} çıkarıldı.[/red]")

        elif action.startswith("Listele"):
            _print_inventory(ctx, item_lookup)

        elif action == "Kaydet ve Çık":
            break

    raw["equipment"] = ctx.equipment
    _save_character(char_path, raw)
    print(f"\nEnvanter güncellendi: {char_path}")


if __name__ == "__main__":
    manage_inventory()



import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from InquirerPy import inquirer
from rich import print as rprint
from rich.table import Table

from cli import CharacterContext
from utils.data_loader import load_dnd_data


def _pick_character(base_dir: Path) -> Path:
    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        raise SystemExit("Hiç kayıtlı karakter bulunamadı.")
    choice = inquirer.select(
        message="Envanteri yönetilecek karakteri seç:",
        choices=[f.name for f in files],
    ).execute()
    return chars_dir / choice


def _load_character(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _select_item(items: List[str], title: str) -> str | None:
    if not items:
        print("Seçilebilir eşya yok.")
        return None
    return inquirer.select(message=title, choices=items + ["İptal"]).execute()


def _parse_cost(cost: Any) -> float:
    """
    '10 gp' gibi maliyetleri sayıya çevir (sadece gp bazında).
    """
    if isinstance(cost, (int, float)):
        return float(cost)
    if not isinstance(cost, str):
        return 0.0
    parts = cost.split()
    try:
        return float(parts[0])
    except (ValueError, IndexError):
        return 0.0


def _parse_weight(weight: Any) -> float:
    try:
        return float(weight)
    except (TypeError, ValueError):
        return 0.0


def _build_item_lookup(equip_data: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
    """
    İsim → (weight, cost) şeklinde hızlı lookup tablosu oluştur.
    """
    lookup: Dict[str, Tuple[float, float]] = {}

    for cat in ("weapons", "armor"):
        for name, info in equip_data.get(cat, {}).items():
            lookup[name] = (_parse_weight(info.get("weight", 0)), _parse_cost(info.get("cost", "0 gp")))

    for name, info in equip_data.get("adventuring_gear", {}).items():
        lookup[name] = (_parse_weight(info.get("weight", 0)), _parse_cost(info.get("cost", "0 gp")))

    return lookup


def _print_inventory(ctx: CharacterContext, item_lookup: Dict[str, Tuple[float, float]]) -> None:
    if not ctx.equipment:
        rprint("[yellow]Envanter boş.[/yellow]")
        return

    table = Table(title="📦 Envanter", show_lines=False)
    table.add_column("Eşya")
    table.add_column("Ağırlık (lb)", justify="right")
    table.add_column("Maliyet (gp)", justify="right")

    total_weight = 0.0
    total_cost = 0.0

    for item in ctx.equipment:
        w, c = item_lookup.get(item, (0.0, 0.0))
        total_weight += w
        total_cost += c
        table.add_row(item, f"{w:.1f}" if w else "-", f"{c:.1f}" if c else "-")

    rprint(table)
    rprint(f"[bold]Toplam ağırlık:[/bold] {total_weight:.1f} lb")
    rprint(f"[bold]Toplam maliyet:[/bold] {total_cost:.1f} gp\n")


def manage_inventory() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_dnd_data(base_dir)
    equip_data = data.get("equipment", {})
    item_lookup = _build_item_lookup(equip_data)

    char_path = _pick_character(base_dir)
    raw = _load_character(char_path)

    ctx = CharacterContext()
    ctx.equipment = [e for e in raw.get("equipment", []) if isinstance(e, str)]

    while True:
        action = inquirer.select(
            message="Envanter işlemi:",
            choices=["Eşya Ekle", "Eşya Çıkar", "Listele (toplam ağırlık/altın)", "Kaydet ve Çık"],
        ).execute()

        if action == "Eşya Ekle":
            category = inquirer.select(
                message="Kategori seç:",
                choices=["weapons", "armor", "adventuring_gear", "İptal"],
            ).execute()
            if category == "İptal":
                continue
            items_dict = equip_data.get(category, {})
            item_names = sorted(items_dict.keys())
            picked = _select_item(item_names, "Eklenecek eşyayı seç:")
            if picked and picked != "İptal":
                ctx.add_equipment([picked])
                rprint(f"[green]➕ {picked} eklendi.[/green]")

        elif action == "Eşya Çıkar":
            if not ctx.equipment:
                rprint("[yellow]Envanter boş.[/yellow]")
                continue
            picked = _select_item(ctx.equipment, "Çıkarılacak eşyayı seç:")
            if picked and picked != "İptal":
                ctx.equipment.remove(picked)
                rprint(f"[red]➖ {picked} çıkarıldı.[/red]")

        elif action.startswith("Listele"):
            _print_inventory(ctx, item_lookup)

        elif action == "Kaydet ve Çık":
            break

    raw["equipment"] = ctx.equipment
    _save_character(char_path, raw)
    print(f"\nEnvanter güncellendi: {char_path}")


if __name__ == "__main__":
    manage_inventory()



import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

from InquirerPy import inquirer
from rich import print as rprint
from rich.table import Table

from cli import CharacterContext
from utils.data_loader import load_dnd_data


def _pick_character(base_dir: Path) -> Path:
    chars_dir = base_dir / "characters"
    chars_dir.mkdir(exist_ok=True)
    files = sorted(p for p in chars_dir.glob("*.json") if p.is_file())
    if not files:
        raise SystemExit("Hiç kayıtlı karakter bulunamadı.")
    choice = inquirer.select(
        message="Envanteri yönetilecek karakteri seç:",
        choices=[f.name for f in files],
    ).execute()
    return chars_dir / choice


def _load_character(path: Path) -> Dict[str, Any]:
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def _save_character(path: Path, data: Dict[str, Any]) -> None:
    with path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def _select_item(items: List[str], title: str) -> str | None:
    if not items:
        print("Seçilebilir eşya yok.")
        return None
    return inquirer.select(message=title, choices=items + ["İptal"]).execute()


def _parse_cost(cost: Any) -> float:
    """
    '10 gp' gibi maliyetleri sayıya çevir (sadece gp bazında).
    """
    if isinstance(cost, (int, float)):
        return float(cost)
    if not isinstance(cost, str):
        return 0.0
    parts = cost.split()
    try:
        return float(parts[0])
    except (ValueError, IndexError):
        return 0.0


def _parse_weight(weight: Any) -> float:
    try:
        return float(weight)
    except (TypeError, ValueError):
        return 0.0


def _build_item_lookup(equip_data: Dict[str, Any]) -> Dict[str, Tuple[float, float]]:
    """
    İsim → (weight, cost) şeklinde hızlı lookup tablosu oluştur.
    """
    lookup: Dict[str, Tuple[float, float]] = {}

    for cat in ("weapons", "armor"):
        for name, info in equip_data.get(cat, {}).items():
            lookup[name] = (_parse_weight(info.get("weight", 0)), _parse_cost(info.get("cost", "0 gp")))

    for name, info in equip_data.get("adventuring_gear", {}).items():
        lookup[name] = (_parse_weight(info.get("weight", 0)), _parse_cost(info.get("cost", "0 gp")))

    return lookup


def _print_inventory(ctx: CharacterContext, item_lookup: Dict[str, Tuple[float, float]]) -> None:
    if not ctx.equipment:
        rprint("[yellow]Envanter boş.[/yellow]")
        return

    table = Table(title="📦 Envanter", show_lines=False)
    table.add_column("Eşya")
    table.add_column("Ağırlık (lb)", justify="right")
    table.add_column("Maliyet (gp)", justify="right")

    total_weight = 0.0
    total_cost = 0.0

    for item in ctx.equipment:
        w, c = item_lookup.get(item, (0.0, 0.0))
        total_weight += w
        total_cost += c
        table.add_row(item, f"{w:.1f}" if w else "-", f"{c:.1f}" if c else "-")

    rprint(table)
    rprint(f"[bold]Toplam ağırlık:[/bold] {total_weight:.1f} lb")
    rprint(f"[bold]Toplam maliyet:[/bold] {total_cost:.1f} gp\n")


def manage_inventory() -> None:
    base_dir = Path(__file__).resolve().parent
    data = load_dnd_data(base_dir)
    equip_data = data.get("equipment", {})
    item_lookup = _build_item_lookup(equip_data)

    char_path = _pick_character(base_dir)
    raw = _load_character(char_path)

    ctx = CharacterContext()
    ctx.equipment = [e for e in raw.get("equipment", []) if isinstance(e, str)]

    while True:
        action = inquirer.select(
            message="Envanter işlemi:",
            choices=["Eşya Ekle", "Eşya Çıkar", "Listele (toplam ağırlık/altın)", "Kaydet ve Çık"],
        ).execute()

        if action == "Eşya Ekle":
            category = inquirer.select(
                message="Kategori seç:",
                choices=["weapons", "armor", "adventuring_gear", "İptal"],
            ).execute()
            if category == "İptal":
                continue
            items_dict = equip_data.get(category, {})
            item_names = sorted(items_dict.keys())
            picked = _select_item(item_names, "Eklenecek eşyayı seç:")
            if picked and picked != "İptal":
                ctx.add_equipment([picked])
                rprint(f"[green]➕ {picked} eklendi.[/green]")

        elif action == "Eşya Çıkar":
            if not ctx.equipment:
                rprint("[yellow]Envanter boş.[/yellow]")
                continue
            picked = _select_item(ctx.equipment, "Çıkarılacak eşyayı seç:")
            if picked and picked != "İptal":
                ctx.equipment.remove(picked)
                rprint(f"[red]➖ {picked} çıkarıldı.[/red]")

        elif action.startswith("Listele"):
            _print_inventory(ctx, item_lookup)

        elif action == "Kaydet ve Çık":
            break

    raw["equipment"] = ctx.equipment
    _save_character(char_path, raw)
    print(f"\nEnvanter güncellendi: {char_path}")


if __name__ == "__main__":
    manage_inventory()


