from fastapi import APIRouter
from typing import List, Dict, Any

router = APIRouter(prefix="/systems", tags=["Systems"])

@router.get("", response_model=List[Dict[str, Any]])
def list_rpg_systems():
    """Retrieve all supported TTRPG systems (PF1e Primary, others locked)."""
    return [
        {
            "key": "pf1e",
            "name": "Pathfinder 1st Edition",
            "dice_system": "d20",
            "description": "Pathfinder 1st Edition Core ruleset, class-and-level modular progression (Aktif & Tam Destek).",
            "is_active": True,
            "badge": "Aktif (Tam Destek)"
        },
        {
            "key": "dnd5e",
            "name": "D&D 5th Edition",
            "dice_system": "d20",
            "description": "Dungeons & Dragons 5e SRD ruleset (Donduruldu).",
            "is_active": False,
            "badge": "Yakında Gelecek"
        },
        {
            "key": "mnm",
            "name": "Mutants & Masterminds 3e",
            "dice_system": "d20",
            "description": "Mutants & Masterminds 3rd Edition point-buy system (Donduruldu).",
            "is_active": False,
            "badge": "Yakında Gelecek"
        }
    ]
