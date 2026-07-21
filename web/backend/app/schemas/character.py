from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class CharacterCreateUpdate(BaseModel):
    system: str = Field(..., description="System key (e.g. pf1e, dnd5e, mnm)")
    name: str = Field(..., description="Name of the character")
    data: Dict[str, Any] = Field(default_factory=dict, description="Raw character sheet data containing abilities, items, etc.")

class CharacterResponse(BaseModel):
    id: int
    system: str
    name: str
    data: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None

class RecalculateRequest(BaseModel):
    data: Dict[str, Any]

class RecalculateResponse(BaseModel):
    data: Dict[str, Any]
    warnings: List[str]

class ValidationResponse(BaseModel):
    valid: bool
    warnings: List[str]
