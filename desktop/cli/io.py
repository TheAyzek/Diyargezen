"""
Kullanıcı girdileri için ortak yardımcılar.
InquirerPy/PromptToolkit kullanımı bu katmanda soyutlanır.
"""
from __future__ import annotations

from typing import Callable, Iterable, List, Optional

from InquirerPy import inquirer


def select(title: str, choices: Iterable[str], default: Optional[str] = None) -> str:
    return inquirer.select(
        message=title,
        choices=list(choices),
        default=default,
        pointer="❯",
    ).execute()


def checkbox(title: str, choices: Iterable[str], min_selected: int = 1, max_selected: Optional[int] = None) -> List[str]:
    selected = inquirer.checkbox(
        message=title,
        choices=list(choices),
        validate=lambda result: len(result) >= min_selected,
    ).execute()
    if max_selected is not None and len(selected) > max_selected:
        return selected[:max_selected]
    return selected


def text(title: str, default: str | None = None, validate: Optional[Callable[[str], bool]] = None) -> str:
    return inquirer.text(
        message=title,
        default=default or "",
        validate=validate,
    ).execute()











