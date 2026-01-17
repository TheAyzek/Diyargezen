from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict

from rich import print as rprint
from rich.table import Table

from ..context import CharacterContext, ability_modifier
from .base import Step, StepResult


@dataclass
class SummaryStep(Step):
    name: str = "summary"
    description: str = "Karakter özetini göster"

    def run(self, ctx: CharacterContext) -> StepResult:
        data: Dict[str, Any] = ctx.to_dict()

        table = Table(title="D&D 5e Karakter Özeti")
        table.add_column("Alan")
        table.add_column("Değer")
        table.add_row("İsim", data.get("name") or "-")
        table.add_row("Irk", data.get("race") or "-")
        table.add_row("Sınıf", data.get("class") or "-")
        table.add_row("Arka Plan", data.get("background") or "-")
        table.add_row("Seviye", str(data.get("level", 1)))
        rprint(table)

        abilities = data.get("abilities", {}).get("scores", {})
        if abilities:
            abil_table = Table(title="Yetenek Puanları")
            abil_table.add_column("Yetenek")
            abil_table.add_column("Puan")
            abil_table.add_column("Mod")
            for name, score in abilities.items():
                abil_table.add_row(name, str(score), f"{ability_modifier(score):+d}")
            rprint(abil_table)

        if ctx.equipment:
            eq_table = Table(title="Ekipman")
            eq_table.add_column("Eşya")
            for item in ctx.equipment:
                eq_table.add_row(item)
            rprint(eq_table)

        return StepResult(True, "Özet gösterildi.")









from dataclasses import dataclass
from typing import Any, Dict

from rich import print as rprint
from rich.table import Table

from ..context import CharacterContext, ability_modifier
from .base import Step, StepResult


@dataclass
class SummaryStep(Step):
    name: str = "summary"
    description: str = "Karakter özetini göster"

    def run(self, ctx: CharacterContext) -> StepResult:
        data: Dict[str, Any] = ctx.to_dict()

        table = Table(title="D&D 5e Karakter Özeti")
        table.add_column("Alan")
        table.add_column("Değer")
        table.add_row("İsim", data.get("name") or "-")
        table.add_row("Irk", data.get("race") or "-")
        table.add_row("Sınıf", data.get("class") or "-")
        table.add_row("Arka Plan", data.get("background") or "-")
        table.add_row("Seviye", str(data.get("level", 1)))
        rprint(table)

        abilities = data.get("abilities", {}).get("scores", {})
        if abilities:
            abil_table = Table(title="Yetenek Puanları")
            abil_table.add_column("Yetenek")
            abil_table.add_column("Puan")
            abil_table.add_column("Mod")
            for name, score in abilities.items():
                abil_table.add_row(name, str(score), f"{ability_modifier(score):+d}")
            rprint(abil_table)

        if ctx.equipment:
            eq_table = Table(title="Ekipman")
            eq_table.add_column("Eşya")
            for item in ctx.equipment:
                eq_table.add_row(item)
            rprint(eq_table)

        return StepResult(True, "Özet gösterildi.")











from dataclasses import dataclass
from typing import Any, Dict

from rich import print as rprint
from rich.table import Table

from ..context import CharacterContext, ability_modifier
from .base import Step, StepResult


@dataclass
class SummaryStep(Step):
    name: str = "summary"
    description: str = "Karakter özetini göster"

    def run(self, ctx: CharacterContext) -> StepResult:
        data: Dict[str, Any] = ctx.to_dict()

        table = Table(title="D&D 5e Karakter Özeti")
        table.add_column("Alan")
        table.add_column("Değer")
        table.add_row("İsim", data.get("name") or "-")
        table.add_row("Irk", data.get("race") or "-")
        table.add_row("Sınıf", data.get("class") or "-")
        table.add_row("Arka Plan", data.get("background") or "-")
        table.add_row("Seviye", str(data.get("level", 1)))
        rprint(table)

        abilities = data.get("abilities", {}).get("scores", {})
        if abilities:
            abil_table = Table(title="Yetenek Puanları")
            abil_table.add_column("Yetenek")
            abil_table.add_column("Puan")
            abil_table.add_column("Mod")
            for name, score in abilities.items():
                abil_table.add_row(name, str(score), f"{ability_modifier(score):+d}")
            rprint(abil_table)

        if ctx.equipment:
            eq_table = Table(title="Ekipman")
            eq_table.add_column("Eşya")
            for item in ctx.equipment:
                eq_table.add_row(item)
            rprint(eq_table)

        return StepResult(True, "Özet gösterildi.")









from dataclasses import dataclass
from typing import Any, Dict

from rich import print as rprint
from rich.table import Table

from ..context import CharacterContext, ability_modifier
from .base import Step, StepResult


@dataclass
class SummaryStep(Step):
    name: str = "summary"
    description: str = "Karakter özetini göster"

    def run(self, ctx: CharacterContext) -> StepResult:
        data: Dict[str, Any] = ctx.to_dict()

        table = Table(title="D&D 5e Karakter Özeti")
        table.add_column("Alan")
        table.add_column("Değer")
        table.add_row("İsim", data.get("name") or "-")
        table.add_row("Irk", data.get("race") or "-")
        table.add_row("Sınıf", data.get("class") or "-")
        table.add_row("Arka Plan", data.get("background") or "-")
        table.add_row("Seviye", str(data.get("level", 1)))
        rprint(table)

        abilities = data.get("abilities", {}).get("scores", {})
        if abilities:
            abil_table = Table(title="Yetenek Puanları")
            abil_table.add_column("Yetenek")
            abil_table.add_column("Puan")
            abil_table.add_column("Mod")
            for name, score in abilities.items():
                abil_table.add_row(name, str(score), f"{ability_modifier(score):+d}")
            rprint(abil_table)

        if ctx.equipment:
            eq_table = Table(title="Ekipman")
            eq_table.add_column("Eşya")
            for item in ctx.equipment:
                eq_table.add_row(item)
            rprint(eq_table)

        return StepResult(True, "Özet gösterildi.")











