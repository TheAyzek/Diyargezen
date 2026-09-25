"""Revision-based sync. Client clocks never decide which change wins.

This first protocol returns a full account snapshot (including tombstones).
Incremental change cursors can be added later without timestamp-based gaps.
"""
import hashlib
import json
from datetime import datetime, timezone
from typing import Literal

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field, model_validator
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from app.core.database import get_db
from app.models.user import Character, User
from app.models.sync_operation import SyncOperation
from app.services.auth_service import get_current_user

router = APIRouter(prefix="/sync/v2", tags=["Sync v2"])


class Operation(BaseModel):
    operation_id: str = Field(min_length=1, max_length=128)
    server_id: str = Field(min_length=1, max_length=128)
    base_revision: int = Field(ge=0)
    system: Literal["pf1e", "pathfinder1e"]
    name: str = Field(min_length=1, max_length=200)
    data: dict = Field(default_factory=dict)
    is_deleted: bool = False


class SyncV2Request(BaseModel):
    operations: list[Operation] = Field(default_factory=list, max_length=100)

    @model_validator(mode="after")
    def unique_operations(self):
        ids = [op.operation_id for op in self.operations]
        if len(ids) != len(set(ids)):
            raise ValueError("Bir pakette işlem kimlikleri benzersiz olmalı")
        return self


def snapshot(record):
    return {
        "id": record.id, "server_id": record.server_id,
        "revision": record.revision, "system": record.system,
        "name": record.name, "data": json.loads(record.data),
        "is_deleted": bool(record.is_deleted),
        "created_at": record.created_at, "updated_at": record.updated_at,
    }


@router.post("")
def sync_v2(payload: SyncV2Request, db: Session = Depends(get_db),
            current_user: User = Depends(get_current_user)):
    results = []
    try:
        for operation in payload.operations:
            digest = hashlib.sha256(json.dumps(
                operation.model_dump(), sort_keys=True, separators=(",", ":"),
                ensure_ascii=False,
            ).encode("utf-8")).hexdigest()
            receipt = db.query(SyncOperation).filter_by(
                user_id=current_user.id, operation_id=operation.operation_id,
            ).first()
            if receipt:
                if receipt.payload_hash != digest:
                    raise HTTPException(409, "İşlem kimliği farklı içerikle yeniden kullanılamaz.")
                results.append(json.loads(receipt.response_json))
                continue

            record = db.query(Character).filter_by(server_id=operation.server_id).first()
            if record is not None and record.user_id != current_user.id:
                raise HTTPException(409, "Bu kayıt kimliği için işlem yapılamıyor.")

            actual_revision = record.revision if record else 0
            if operation.base_revision != actual_revision:
                result = {
                    "operation_id": operation.operation_id, "server_id": operation.server_id,
                    "status": "conflict", "expected_revision": operation.base_revision,
                    "actual_revision": actual_revision,
                    "server_character": snapshot(record) if record else None,
                }
            else:
                now = datetime.now(timezone.utc).isoformat()
                if record is None:
                    record = Character(user_id=current_user.id, server_id=operation.server_id,
                                       created_at=now)
                    db.add(record)
                record.system = operation.system
                record.name = operation.name
                record.data = json.dumps(operation.data, ensure_ascii=False)
                record.is_deleted = operation.is_deleted
                record.updated_at = now
                # SQLAlchemy's version predicate rejects concurrent stale writes.
                db.flush()
                result = {
                    "operation_id": operation.operation_id, "server_id": operation.server_id,
                    "status": "accepted", "revision": record.revision,
                    "server_character": snapshot(record),
                }
            db.add(SyncOperation(
                user_id=current_user.id, operation_id=operation.operation_id,
                payload_hash=digest, response_json=json.dumps(result, ensure_ascii=False),
            ))
            db.flush()
            results.append(result)

        characters = [snapshot(record) for record in db.query(Character).filter_by(
            user_id=current_user.id,
        ).order_by(Character.id).all()]
        db.commit()
        return {"protocol_version": 2, "results": results, "characters": characters,
                "snapshot_mode": "full"}
    except (IntegrityError, StaleDataError):
        db.rollback()
        raise HTTPException(409, "Eşzamanlı değişiklik algılandı; aynı işlem kimlikleriyle tekrar deneyin.")
    except Exception:
        db.rollback()
        raise
