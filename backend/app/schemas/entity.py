from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from models.entity import DiyargezenEntity

class EntityResponseSchema(BaseModel):
    name: str = Field(..., alias="isim")
    system: str = Field(..., alias="sistem")
    category: str = Field(..., alias="kategori")
    description: str = Field(..., alias="aciklama")
    system_data: Dict[str, Any] = Field(..., alias="sistem_verisi")
    parsed_modifiers: Optional[List[Dict[str, Any]]] = Field(default=None)

    class Config:
        populate_by_name = True

class EntityListResponse(BaseModel):
    count: int
    entities: List[EntityResponseSchema]
