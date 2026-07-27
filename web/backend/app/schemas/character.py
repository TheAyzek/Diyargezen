from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional, Literal

class CharacterCreateUpdate(BaseModel):
    system: Literal["pf1e", "pathfinder1e"] = Field(..., description="PF1e system key")
    name: str = Field(..., description="Name of the character")
    data: Dict[str, Any] = Field(default_factory=dict, description="Raw character sheet data containing abilities, items, etc.")
    server_id: Optional[str] = None

class CharacterResponse(BaseModel):
    id: int
    server_id: Optional[str] = None
    system: str
    name: str
    data: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_deleted: bool = False

class SyncCharacterItem(BaseModel):
    server_id: Optional[str] = None
    system: Literal["pf1e", "pathfinder1e"]
    name: str
    data: Dict[str, Any]
    created_at: Optional[str] = None
    updated_at: Optional[str] = None
    is_deleted: bool = False

class SyncRequest(BaseModel):
    last_sync_timestamp: Optional[str] = None
    dirty_characters: List[SyncCharacterItem] = Field(default_factory=list)

class SyncResponse(BaseModel):
    status: str = "ok"
    synced_at: str
    updated_characters: List[CharacterResponse] = Field(default_factory=list)
    deleted_server_ids: List[str] = Field(default_factory=list)

class RecalculateRequest(BaseModel):
    data: Dict[str, Any]

class RecalculateResponse(BaseModel):
    data: Dict[str, Any]
    warnings: List[str]
    diagnostics: List[Dict[str, Any]] = Field(default_factory=list)

class PrerequisiteCheckRequest(BaseModel):
    data: Dict[str, Any]
    prerequisites: List[str] = Field(default_factory=list)
    is_overridden: bool = False

class PrerequisiteCheckResponse(BaseModel):
    valid: bool
    diagnostics: List[Dict[str, Any]]
    can_override: bool = True

class CustomModifierPayload(BaseModel):
    stat: str = Field(pattern=r"^(ac|hp|bab|fortitude|reflex|will|skill:.+)$")
    value: int = Field(ge=-100, le=100)
    name: str = Field(min_length=1, max_length=100)
    reason: str = Field(default="", max_length=500)
    is_active: bool = True

class OverridePayload(BaseModel):
    selection_type: str = Field(pattern=r"^(feat|spell|item|level_up)$")
    selection_key: str = Field(min_length=1, max_length=200)
    violated_rules: List[str] = Field(default_factory=list)
    reason: str = Field(min_length=1, max_length=500)

class LevelUpSessionPayload(BaseModel):
    target_level: int = Field(ge=2, le=20)
    state: str = Field(default="started", pattern=r"^(started|hp|skills|feat|ability_score|review)$")
    choices: Dict[str, Any] = Field(default_factory=dict)
    is_overridden: bool = False

class ValidationResponse(BaseModel):
    valid: bool
    warnings: List[str]
