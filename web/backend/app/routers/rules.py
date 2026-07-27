from fastapi import APIRouter, Query, HTTPException
from typing import List, Optional
from pydantic import BaseModel
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
def search_feats(
    system: str,
    query: str = Query("", description="Search query"),
    category: str = Query("", description="Feat category filter: Combat, Teamwork, Metamagic, etc.")
):
    """Retrieve and search feats with optional category filtering."""
    feats = service.get_feats(system, query, category)
    return [EntityResponseSchema.model_validate(f, from_attributes=True) for f in feats]

@router.get("/{system}/equipment", response_model=List[EntityResponseSchema])
def search_equipment(system: str, query: str = Query("", description="Search query")):
    """Retrieve and search gear, weapons, shield, and armor."""
    items = service.get_equipment(system, query)
    return [EntityResponseSchema.model_validate(i, from_attributes=True) for i in items]

@router.get("/{system}/spells", response_model=List[EntityResponseSchema])
def search_spells(
    system: str,
    query: str = Query("", description="Search query"),
    level: Optional[int] = Query(None, description="Filter by spell level (0-9)"),
    caster_class: str = Query("", description="Filter by spellcaster class (e.g. Wizard, Cleric, Sorcerer)"),
    school: str = Query("", description="Filter by magic school (e.g. Evocation, Abjuration)")
):
    """Retrieve and search magic spells with level, class, and school filtering."""
    spells = service.get_spells(system, query=query, level=level, caster_class=caster_class, school=school)
    return [EntityResponseSchema.model_validate(s, from_attributes=True) for s in spells]

@router.get("/{system}/powers", response_model=List[EntityResponseSchema])
def search_powers(system: str, query: str = Query("", description="Search query")):
    """Retrieve and search superpower descriptions (Mutants & Masterminds)."""
    powers = service.get_powers(system, query)
    return [EntityResponseSchema.model_validate(p, from_attributes=True) for p in powers]

@router.get("/{system}/traits", response_model=List[EntityResponseSchema])
def search_traits(system: str, query: str = Query("", description="Search query"), category: str = Query("", description="Trait category filter")):
    """Retrieve and search character traits for PF1e (grouped by category)."""
    traits = service.get_traits(system, query, category)
    return [EntityResponseSchema.model_validate(t, from_attributes=True) for t in traits]

@router.get("/{system}/search", response_model=List[EntityResponseSchema])
def search_all_entities(
    system: str,
    category: str = Query(..., description="Entity category (e.g. race, class, feat, spell, item)"),
    query: str = Query("", description="Search query text")
):
    """Generic search endpoint for any rulebook entity category."""
    entities = service.search_entities(system, category, query)
    return [EntityResponseSchema.model_validate(e, from_attributes=True) for e in entities]


class PrereqCheckRequest(BaseModel):
    character: dict
    entity_data: dict
    is_overridden: bool = False

@router.post("/validate-prerequisites")
def validate_prerequisites(payload: PrereqCheckRequest):
    """Validate entity prerequisites with GM soft-block & override capability."""
    from rules.calculators import PF1e_Calculator
    calc = PF1e_Calculator()
    return calc.check_prerequisites(payload.character, payload.entity_data, payload.is_overridden)

