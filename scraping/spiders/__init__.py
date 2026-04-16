"""Site-spesifik spider implementasyonlari."""

from .pf1e_d20pfsrd_spider import PF1eD20pfsrdSpider
from .dnd5e_spider import DnD5eSpider
from .mm3e_spider import MM3eSpider
from .vtm5e_spider import VtM5eSpider

__all__ = [
    "PF1eD20pfsrdSpider",
    "DnD5eSpider",
    "MM3eSpider",
    "VtM5eSpider",
]
