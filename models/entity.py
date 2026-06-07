"""
DiyargezenEntity — Evrensel TTRPG Veri Modeli
==============================================
Tüm sistemlerdeki ırk, sınıf, büyü, feat vb. kayıtlar için ortak şema.
"""

from __future__ import annotations

from typing import Any, Dict

from pydantic import BaseModel, Field, field_validator


class DiyargezenEntity(BaseModel):
    """FoundryVTT / yerel JSON'dan ETL ile üretilen standart kayıt."""

    isim: str = Field(..., min_length=1, description="Görünen ad")
    sistem: str = Field(..., description="dnd5e | pathfinder1e | mm3e")
    kategori: str = Field(..., description="race | class | spell | feat | power | ...")
    aciklama: str = Field(default="", description="Kısa açıklama metni")
    sistem_verisi: Dict[str, Any] = Field(
        default_factory=dict,
        description="Sisteme özgü ham/normalize edilmiş JSON",
    )

    @field_validator("isim")
    @classmethod
    def _strip_isim(cls, v: str) -> str:
        return v.strip()

    @field_validator("sistem", "kategori")
    @classmethod
    def _normalize_key(cls, v: str) -> str:
        return v.strip().lower().replace(" ", "").replace("-", "_")

    def to_db_row(self) -> tuple:
        """SQLite INSERT parametreleri."""
        import json

        return (
            self.isim,
            self.sistem,
            self.kategori,
            self.aciklama,
            json.dumps(self.sistem_verisi, ensure_ascii=False),
        )
