from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class CharacterCreateUpdate(BaseModel):
    system: str = Field(..., description="System key (e.g. pf1e, dnd5e, mnm)")
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
    system: str
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

class ValidationResponse(BaseModel):
    valid: bool
    warnings: List[str]
