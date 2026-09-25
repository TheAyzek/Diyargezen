"""Deprecated read-only v1 sync. All PUSH writes must use /api/sync/v2."""

from __future__ import annotations

import json
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

)
from app.services.auth_service import get_current_user


logger = logging.getLogger(__name__)

router = APIRouter(prefix="/sync", tags=["Sync"])



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
    deprecated=True,
    response_model=SyncResponse,
    summary="Masaüstü & Bulut Karakter Senkronizasyonu",
    description="Eski salt okunur PULL arayüzü. Yazmalar için /api/sync/v2 kullanın."
)
def sync_characters(
    payload: SyncRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Return legacy account changes without accepting unversioned writes."""
    now = datetime.now(timezone.utc)
    now_str = now.isoformat()

    # Legacy clients must not bypass v2 revision/operation checks.
    if payload.dirty_characters:
        raise HTTPException(426, "Eski senkronizasyon yazmaları kapatıldı; /api/sync/v2 kullanın.")
    pushed_ids = set()

    # 2. PULL Phase: Fetch updated characters for client
    query = db.query(Character).filter(Character.user_id == current_user.id)
    if payload.last_sync_timestamp:
        last_sync_dt = parse_iso_timestamp(payload.last_sync_timestamp)
        # Compare timestamps safely
        all_user_chars = query.all()
        filtered_records = []
        for rec in all_user_chars:
            rec_dt = parse_iso_timestamp(rec.updated_at)
            if rec_dt >= last_sync_dt or rec.server_id in pushed_ids:
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
                    revision=rec.revision,
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
