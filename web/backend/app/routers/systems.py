from fastapi import APIRouter
from typing import List, Dict, Any
from app.core.config import DB_PATH
import utils.storage as storage

router = APIRouter(prefix="/systems", tags=["Systems"])

@router.get("", response_model=List[Dict[str, Any]])
def list_rpg_systems():
    """Retrieve all supported TTRPG systems with description and dice mechanisms."""
    try:
        systems = storage.list_systems(DB_PATH)
        if systems:
            return systems
    except Exception:
        pass
        
    # Fallback to defaults
    return [
        {
            "key": "dnd5e",
            "name": "D&D 5th Edition",
            "dice_system": "d20",
            "description": "Dungeons & Dragons 5e SRD ruleset, level-based character progression."
        },
        {
            "key": "pf1e",
            "name": "Pathfinder 1st Edition",
            "dice_system": "d20",
            "description": "Pathfinder 1st Edition Core ruleset, class-and-level modular progression."
        },
        {
            "key": "mnm",
            "name": "Mutants & Masterminds 3e",
            "dice_system": "d20",
            "description": "Mutants & Masterminds 3rd Edition classless point-buy character creation."
        }
    ]
