"""
Diyargezen Distributed Offline-First Synchronization Router

Architecture & Replication Paradigm:
------------------------------------
This router provides the RESTful synchronization gateway (`POST /api/sync`) for the desktop PySide6 client
and web frontend applications in an Offline-First, Eventually Consistent distributed system.

Replication Protocol & Algorithmic State Transitions:
1. PUSH Phase (Client -> Cloud):
   - Ingests local dirty records (`is_dirty=True`) modified while offline.
   - Handles both newly created entities and soft-deleted (`is_deleted=True`) tombstone records.
2. Conflict Resolution (Last-Write-Wins / LWW):
   - Converts ISO-8601 string timestamps to UTC `datetime` objects to prevent ISO-format string comparison discrepancies.
   - Evaluates `client_updated >= server_updated`. If True, updates cloud state; otherwise retains authoritative cloud record.
3. Tombstone & Soft-Delete Protocol:
   - Soft-deleted entities retain their `server_id` and timestamp in the database to guarantee idempotent replication across multi-device sync topologies.
4. PULL Phase (Cloud -> Client):
   - Queries all user records updated on or after `last_sync_timestamp`.
   - Streams active entities in `updated_characters` and soft-deleted entity keys in `deleted_server_ids`.
5. Authoritative Checkpoint Management:
   - Yields a synchronized ISO-8601 `synced_at` timestamp used by the client for incremental checkpointing.
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


def parse_iso_timestamp(ts_str: Optional[str]) -> datetime:
    """
    ISO-8601 zaman damgası dizesini UTC datetime objesine dönüştürür.
    Zaman dilimi bilgisi yoksa varsayılan olarak UTC kabul eder.
    
    Args:
        ts_str: ISO-8601 formatında zaman damgası dizesi.
        
    Returns:
        datetime: UTC zaman diliminde datetime nesnesi.
    """
    if not ts_str:
        return datetime.min.replace(tzinfo=timezone.utc)
    try:
        dt = datetime.fromisoformat(ts_str.replace("Z", "+00:00"))
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=timezone.utc)
        return dt.astimezone(timezone.utc)
    except (ValueError, TypeError):
        return datetime.min.replace(tzinfo=timezone.utc)


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
    """
    Çevrimdışı öncelikli (Offline-First) senkronizasyon iş mantığı.
    
    İşlem Adımları:
    1. İstemciden gelen `dirty_characters` dizisini dönerek PUSH aşamasını yürütür.
    2. Karakter bulutta yoksa oluşturur; varsa Last-Write-Wins (LWW) algoritmasıyla günceller.
    3. `last_sync_timestamp` değerinden daha yeni olan sunucu kayıtlarını PULL aşaması için sorgular.
    4. Silinmiş kayıtları `deleted_server_ids` dizisine, aktif kayıtları `updated_characters` dizisine ekleyerek yanıt döner.
    """
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()

    # 1. PUSH Phase: Process dirty characters pushed from client
    for item in payload.dirty_characters:
        server_id = item.server_id or str(uuid.uuid4())
        
        # Check if record exists in cloud DB for this user
        db_char = db.query(Character).filter(
            Character.server_id == server_id,
            Character.user_id == current_user.id
        ).first()

        data_json = json.dumps(item.data, ensure_ascii=False) if isinstance(item.data, dict) else item.data

        client_dt = parse_iso_timestamp(item.updated_at or now_str)

        if not db_char:
            # Create new character record (even if tombstoned to propagate deletion to other clients)
            db_char = Character(
                user_id=current_user.id,
                server_id=server_id,
                system=item.system,
                name=item.name,
                data=data_json,
                created_at=item.created_at or now_str,
                updated_at=item.updated_at or now_str,
                is_deleted=item.is_deleted or False
            )
            db.add(db_char)
        else:
            # Conflict resolution: Compare updated_at timestamps (LWW)
            server_dt = parse_iso_timestamp(db_char.updated_at)

            if client_dt >= server_dt:
                db_char.system = item.system
                db_char.name = item.name
                db_char.data = data_json
                db_char.updated_at = item.updated_at or now_str
                db_char.is_deleted = item.is_deleted or False

    db.commit()

    # 2. PULL Phase: Fetch updated characters for client
    query = db.query(Character).filter(Character.user_id == current_user.id)
    if payload.last_sync_timestamp:
        last_sync_dt = parse_iso_timestamp(payload.last_sync_timestamp)
        # Compare timestamps safely
        all_user_chars = query.all()
        filtered_records = []
        for rec in all_user_chars:
            rec_dt = parse_iso_timestamp(rec.updated_at)
            if rec_dt >= last_sync_dt:
                filtered_records.append(rec)
        all_records = filtered_records
    else:
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

