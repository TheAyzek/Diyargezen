"""
Sync Router for FastAPI Backend
==============================
Masaüstü ve Web istemcileri için çevrimdışı öncelikli (Offline-First)
karakter senkronizasyon endpoint'i (`POST /api/sync`).
"""

from __future__ import annotations

import json
import uuid
import logging
from datetime import datetime, timezone
from typing import List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User, Character
from app.schemas.character import (
    SyncRequest,
    SyncResponse,
    CharacterResponse,
    SyncCharacterItem
)
from app.services.auth_service import get_current_user
from app.services.character_service import CharacterService

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["Sync"])
char_service = CharacterService()


@router.post(
    "",
    response_model=SyncResponse,
    summary="Masaüstü & Bulut Karakter Senkronizasyonu",
    description="""
Çevrimdışı öncelikli (Offline-First) çift yönlü senkronizasyon endpoint'i:
- Masaüstü istemcisinde internetsiz değiştirilen (`is_dirty=True`) karakterler buluta aktarılır (**PUSH**).
- Çakışmalar zaman damgası (**Last-Write-Wins**) mantığıyla çözülür.
- Sunucudaki en güncel karakter değişiklikleri masaüstüne indirilir (**PULL**).
"""
)
def sync_characters(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    now_str = datetime.now(timezone.utc).isoformat()

    # 1. Process dirty characters pushed from client
    for item in payload.dirty_characters:
        server_id = item.server_id or str(uuid.uuid4())
        
        # Check if record exists in cloud DB for this user
        db_char = db.query(Character).filter(
            Character.server_id == server_id,
            Character.user_id == current_user.id
        ).first()

        data_json = json.dumps(item.data, ensure_ascii=False) if isinstance(item.data, dict) else item.data

        if not db_char:
            # Create new character in Cloud DB if not deleted
            if not item.is_deleted:
                db_char = Character(
                    user_id=current_user.id,
                    server_id=server_id,
                    system=item.system,
                    name=item.name,
                    data=data_json,
                    created_at=item.created_at or now_str,
                    updated_at=item.updated_at or now_str,
                    is_deleted=False
                )
                db.add(db_char)
        else:
            # Conflict resolution: Compare updated_at timestamps
            client_updated = item.updated_at or ""
            server_updated = db_char.updated_at or ""

            if client_updated >= server_updated:
                db_char.system = item.system
                db_char.name = item.name
                db_char.data = data_json
                db_char.updated_at = client_updated
                db_char.is_deleted = item.is_deleted

    db.commit()

    # 2. Fetch updated characters for client PULL
    query = db.query(Character).filter(Character.user_id == current_user.id)
    if payload.last_sync_timestamp:
        query = query.filter(Character.updated_at >= payload.last_sync_timestamp)

    all_records = query.all()

    updated_chars: List[CharacterResponse] = []
    deleted_ids: List[str] = []

    for rec in all_records:
        if rec.is_deleted:
            if rec.server_id:
                deleted_ids.append(rec.server_id)
        else:
            c_data = json.loads(rec.data) if isinstance(rec.data, str) else rec.data
            updated_chars.append(
                CharacterResponse(
                    id=rec.id,
                    server_id=rec.server_id,
                    system=rec.system,
                    name=rec.name,
                    data=c_data,
                    created_at=rec.created_at,
                    updated_at=rec.updated_at,
                    is_deleted=rec.is_deleted or False
                )
            )

    return SyncResponse(
        status="ok",
        synced_at=now_str,
        updated_characters=updated_chars,
        deleted_server_ids=deleted_ids
    )
