from pydantic import BaseModel, Field, ConfigDict
from typing import Dict, Any, List, Optional
from models.entity import DiyargezenEntity

class EntityResponseSchema(BaseModel):
    model_config = ConfigDict(populate_by_name=True)

    isim: str
    sistem: str
    kategori: str
    aciklama: str
    sistem_verisi: Dict[str, Any]
    parsed_modifiers: Optional[List[Dict[str, Any]]] = Field(default=None)

class EntityListResponse(BaseModel):
    count: int
    entities: List[EntityResponseSchema]
