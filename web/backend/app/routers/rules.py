from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from app.schemas.entity import EntityResponseSchema
from app.services.rules_service import RulesService

router = APIRouter(prefix="/rules", tags=["Rules"])
service = RulesService()

@router.get("/{system}/races", response_model=List[EntityResponseSchema])
def get_races(system: str):
    """Retrieve playable races for the specified system."""
    races = service.get_races(system)
    return [EntityResponseSchema.model_validate(r, from_attributes=True) for r in races]

@router.get("/{system}/subraces", response_model=List[EntityResponseSchema])
def get_subraces(system: str, parent_race: str):
    """Retrieve heritages/subraces for a given parent race."""
    subraces = service.get_subraces(system, parent_race)
    return [EntityResponseSchema.model_validate(r, from_attributes=True) for r in subraces]

@router.get("/{system}/classes", response_model=List[EntityResponseSchema])
def get_classes(system: str):
    """Retrieve playable classes or archetypes for the specified system."""
    classes = service.get_classes(system)
    return [EntityResponseSchema.model_validate(c, from_attributes=True) for c in classes]

@router.get("/{system}/feats", response_model=List[EntityResponseSchema])
def search_feats(system: str, query: str = Query("", description="Search query")):
    """Retrieve and search feats, traits, or advantages."""
    feats = service.get_feats_or_advantages(system, query)
    return [EntityResponseSchema.model_validate(f, from_attributes=True) for f in feats]

@router.get("/{system}/equipment", response_model=List[EntityResponseSchema])
def search_equipment(system: str, query: str = Query("", description="Search query")):
    """Retrieve and search gear, weapons, shield, and armor."""
    items = service.get_equipment(system, query)
    return [EntityResponseSchema.model_validate(i, from_attributes=True) for i in items]

@router.get("/{system}/spells", response_model=List[EntityResponseSchema])
def search_spells(system: str, query: str = Query("", description="Search query")):
    """Retrieve and search magic spells."""
    spells = service.get_spells(system, query)
    return [EntityResponseSchema.model_validate(s, from_attributes=True) for s in spells]

@router.get("/{system}/powers", response_model=List[EntityResponseSchema])
def search_powers(system: str, query: str = Query("", description="Search query")):
    """Retrieve and search superpower descriptions (Mutants & Masterminds)."""
    powers = service.get_powers(system, query)
    return [EntityResponseSchema.model_validate(p, from_attributes=True) for p in powers]

@router.get("/{system}/search", response_model=List[EntityResponseSchema])
def search_all_entities(
    system: str,
    category: str = Query(..., description="Entity category (e.g. race, class, feat, spell, item)"),
    query: str = Query("", description="Search query text")
):
    """Generic search endpoint for any rulebook entity category."""
    entities = service.search_entities(system, category, query)
    return [EntityResponseSchema.model_validate(e, from_attributes=True) for e in entities]
