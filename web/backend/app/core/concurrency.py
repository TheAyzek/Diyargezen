"""Revision preconditions for legacy numeric-ID mutation routes."""
from typing import Optional
from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError
from sqlalchemy.exc import IntegrityError
from app.core.database import get_db
from app.models.user import Character, User
from app.services.auth_service import get_current_user


def revision_guard(character_id: int, if_match: Optional[str] = Header(None),
                   db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    record = db.query(Character).filter_by(id=character_id).first()
    if record is None or record.is_deleted:
        raise HTTPException(404, 'Karakter bulunamadı.')
    if record.user_id != current_user.id:
        raise HTTPException(403, 'Bu karakter için yetkiniz yok.')
    if if_match is None:
        raise HTTPException(428, 'If-Match başlığında karakter revizyonu gerekli; kaydı yeniden yükleyin.')
    value = if_match
    if len(value) >= 2 and value.startswith('"') and value.endswith('"'):
        value = value[1:-1]
    if len(value) > 20 or not value.isascii() or not value.isdecimal() or int(value) < 1:
        raise HTTPException(400, 'If-Match pozitif bir revizyon numarası olmalı.')
    if record.revision != int(value):
        raise HTTPException(409, 'Karakter başka bir işlemde değişti; yerel düzenlemeyi koruyup yeniden senkronize edin.')
    return record


def commit_revision(db):
    try:
        db.commit()
    except (StaleDataError, IntegrityError):
        db.rollback()
        raise HTTPException(409, 'Eşzamanlı değişiklik algılandı; işlem uygulanmadı.')
