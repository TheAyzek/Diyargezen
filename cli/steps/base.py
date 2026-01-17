from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..context import CharacterContext


@dataclass
class StepResult:
    success: bool
    message: Optional[str] = None


class Step(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, ctx: CharacterContext) -> StepResult:
        """Step'i çalıştır ve sonucu dön."""
        raise NotImplementedError








from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..context import CharacterContext


@dataclass
class StepResult:
    success: bool
    message: Optional[str] = None


class Step(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, ctx: CharacterContext) -> StepResult:
        """Step'i çalıştır ve sonucu dön."""
        raise NotImplementedError










from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..context import CharacterContext


@dataclass
class StepResult:
    success: bool
    message: Optional[str] = None


class Step(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, ctx: CharacterContext) -> StepResult:
        """Step'i çalıştır ve sonucu dön."""
        raise NotImplementedError








from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Optional

from ..context import CharacterContext


@dataclass
class StepResult:
    success: bool
    message: Optional[str] = None


class Step(ABC):
    name: str
    description: str

    @abstractmethod
    def run(self, ctx: CharacterContext) -> StepResult:
        """Step'i çalıştır ve sonucu dön."""
        raise NotImplementedError











