"""JSON → DiyargezenEntity parser'ları."""

from .dnd5e_parser import parse_dnd5e
from .pf1e_parser import parse_pf1e
from .mm3e_parser import parse_mm3e

PARSERS = {
    "dnd5e": parse_dnd5e,
    "pathfinder1e": parse_pf1e,
    "mm3e": parse_mm3e,
}

__all__ = ["PARSERS", "parse_dnd5e", "parse_pf1e", "parse_mm3e"]
