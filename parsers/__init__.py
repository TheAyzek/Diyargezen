"""JSON → DiyargezenEntity parser'ları (PF1e Focus)."""

from .pf1e_parser import parse_pf1e

PARSERS = {
    "pathfinder1e": parse_pf1e,
    "pf1e": parse_pf1e,
}

__all__ = ["PARSERS", "parse_pf1e"]

