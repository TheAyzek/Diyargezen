import json
import base64
import tempfile
from pathlib import Path
from typing import List, Optional, Dict, Any
from fastapi import APIRouter, HTTPException, Query, Response, status, UploadFile, File, Depends
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session
from pydantic import BaseModel, Field

from utils.export_pdf import export_pdf
from app.core.database import get_db
from app.services.auth_service import get_current_user
from app.models.user import User, Character
from app.models.gm import CharacterModifier, GMOverride, LevelUpSession
from app.schemas.character import (
    CharacterCreateUpdate,
    CharacterResponse,
    RecalculateRequest,
    RecalculateResponse,
    ValidationResponse
    ,PrerequisiteCheckRequest, PrerequisiteCheckResponse, CustomModifierPayload,
    OverridePayload, LevelUpSessionPayload
)
from app.services.character_service import CharacterService

router = APIRouter(prefix="/characters", tags=["Characters"])
service = CharacterService()

class LevelUpPayload(BaseModel):
    class_name: str = Field(..., description="The name of the class chosen for this level")
    skill_ranks: Dict[str, int] = Field(default_factory=dict, description="Skill ranks allocated in this level")
    feats: List[str] = Field(default_factory=list, description="Feats selected in this level")
    ability_increase: Optional[str] = Field(None, description="Ability score increased in this level (+1)")
    hp_added: int = Field(default=6, description="Base hit die roll/added for this level")
    spells_learned: List[str] = Field(default_factory=list, description="Spells learned in this level")

@router.get("", response_model=List[CharacterResponse])
def list_characters(system: Optional[str] = Query(None), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """List all character sheets belonging to the user in the database."""
    records = service.list_characters(db, current_user.id, system)
    return [
        CharacterResponse(
            id=r.id,
            system=r.system,
            name=r.name,
            data=json.loads(r.data) if isinstance(r.data, str) else r.data,
            created_at=r.created_at,
            updated_at=r.updated_at
        ) for r in records
    ]

@router.get("/{character_id}", response_model=CharacterResponse)
def get_character(character_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve details for a specific character by ID, enforcing user ownership."""
    record = service.get_character(db, character_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character ID {character_id} not found."
        )
    if record.user_id and record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu karaktere erişim yetkiniz yok."
        )
    return CharacterResponse(
        id=record.id,
        system=record.system,
        name=record.name,
        data=json.loads(record.data) if isinstance(record.data, str) else record.data,
        created_at=record.created_at,
        updated_at=record.updated_at
    )

@router.post("", response_model=CharacterResponse, status_code=status.HTTP_201_CREATED)
def create_character(payload: CharacterCreateUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Create and save a new character sheet, associated with the current user."""
    try:
        record = service.create_character(db, payload.system, payload.name, payload.data, current_user.id)
        return CharacterResponse(
            id=record.id,
            system=record.system,
            name=record.name,
            data=json.loads(record.data) if isinstance(record.data, str) else record.data,
            created_at=record.created_at,
            updated_at=record.updated_at
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to create character: {str(exc)}"
        )

@router.put("/{character_id}")
def update_character(character_id: int, payload: CharacterCreateUpdate, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Update an existing character sheet, checking user ownership."""
    record = service.get_character(db, character_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character ID {character_id} not found."
        )
    if record.user_id and record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu karakteri güncelleme yetkiniz yok."
        )
    success = service.update_character(db, character_id, payload.name, payload.data)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update character."
        )
    return {"message": "Character updated successfully"}

@router.delete("/{character_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_character(character_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Delete a character sheet by ID, checking ownership."""
    record = service.get_character(db, character_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character ID {character_id} not found."
        )
    if record.user_id and record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu karakteri silme yetkiniz yok."
        )
    service.delete_character(db, character_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)

@router.post("/recalculate", response_model=RecalculateResponse)
def recalculate_stats(payload: RecalculateRequest):
    """Statelessly compute derived statistics and check rules on the fly."""
    try:
        recalced_data = service.recalculate(payload.data)
        warnings = service.validate(recalced_data)
        diagnostics = service.gm_diagnostics(recalced_data)
        return RecalculateResponse(data=recalced_data, warnings=warnings, diagnostics=diagnostics)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Stat recalculation failed: {str(exc)}"
        )

@router.post("/validate", response_model=ValidationResponse)
def validate_rules(payload: RecalculateRequest):
    """Check rule compliance for a given character sheet."""
    try:
        warnings = service.validate(payload.data)
        return ValidationResponse(valid=len(warnings) == 0, warnings=warnings)
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Rule validation failed: {str(exc)}"
        )

@router.post("/check-prerequisites", response_model=PrerequisiteCheckResponse)
def check_prerequisites(payload: PrerequisiteCheckRequest):
    """Soft-block check for feat/spell/item choices; never prevents a GM override."""
    from app.services.pf1e_gm_engine import PF1eGMEngine
    diagnostics = PF1eGMEngine().check_prerequisites(
        payload.data, payload.prerequisites, payload.is_overridden
    )
    result = [item.__dict__ for item in diagnostics]
    return PrerequisiteCheckResponse(
        valid=not any(item["severity"] == "warning" and not item["overridden"] for item in result),
        diagnostics=result,
    )

def _owned_character(db: Session, character_id: int, user_id: int) -> Character:
    record = service.get_character(db, character_id)
    if not record:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Karakter bulunamadı.")
    if record.user_id != user_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Bu karakter için yetkiniz yok.")
    if record.system.lower() not in {"pf1e", "pathfinder1e"}:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Yalnızca PF1e desteklenir.")
    return record

@router.post("/{character_id}/gm/modifiers", status_code=status.HTTP_201_CREATED)
def add_custom_modifier(character_id: int, payload: CustomModifierPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Persist an explainable +X/-X GM adjustment and mirror it into sheet data."""
    record = _owned_character(db, character_id, current_user.id)
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    modifier = CharacterModifier(character_id=character_id, **payload.model_dump(), created_at=now, updated_at=now)
    data = json.loads(record.data)
    data.setdefault("custom_modifiers", []).append({**payload.model_dump(), "id": None})
    recalculated = service.recalculate(data)
    record.data = json.dumps(recalculated, ensure_ascii=False)
    record.updated_at = now
    db.add(modifier)
    db.commit()
    db.refresh(modifier)
    return {"id": modifier.id, "data": recalculated}

@router.post("/{character_id}/gm/overrides", status_code=status.HTTP_201_CREATED)
def record_override(character_id: int, payload: OverridePayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Record a GM-approved exception; this is audit data, never a silent bypass."""
    _owned_character(db, character_id, current_user.id)
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    override = GMOverride(
        character_id=character_id, selection_type=payload.selection_type,
        selection_key=payload.selection_key, violated_rules=json.dumps(payload.violated_rules, ensure_ascii=False),
        reason=payload.reason, is_overridden=True, created_at=now,
    )
    db.add(override)
    db.commit()
    db.refresh(override)
    return {"id": override.id, "is_overridden": True}

@router.put("/{character_id}/level-up-session")
def save_level_up_session(character_id: int, payload: LevelUpSessionPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Save a resumable state-machine checkpoint; commit still uses the level-up endpoint."""
    record = _owned_character(db, character_id, current_user.id)
    current_level = int(json.loads(record.data).get("level", 1))
    if payload.target_level != current_level + 1:
        raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY, detail="Hedef seviye tam olarak sonraki seviye olmalıdır.")
    now = __import__("datetime").datetime.now(__import__("datetime").timezone.utc).isoformat()
    session = db.query(LevelUpSession).filter(
        LevelUpSession.character_id == character_id, LevelUpSession.target_level == payload.target_level
    ).first()
    if session is None:
        session = LevelUpSession(
            character_id=character_id,
            target_level=payload.target_level,
            state=payload.state,
            choices=json.dumps(payload.choices, ensure_ascii=False),
            is_overridden=payload.is_overridden,
            created_at=now,
            updated_at=now,
        )
        db.add(session)
    else:
        session.state = payload.state
        session.choices = json.dumps(payload.choices, ensure_ascii=False)
        session.is_overridden = payload.is_overridden
        session.updated_at = now
    db.commit()
    db.refresh(session)
    return {"id": session.id, "state": session.state, "target_level": session.target_level}

@router.get("/{character_id}/pdf")
def export_character_to_pdf(character_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Retrieve character, compute derived statistics, check ownership, and export as filled PDF."""
    record = service.get_character(db, character_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character ID {character_id} not found."
        )
    if record.user_id and record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu karakterin PDF belgesini dışa aktarma yetkiniz yok."
        )
        
    char_data = json.loads(record.data) if isinstance(record.data, str) else record.data
    recalced_data = service.recalculate(char_data)
    
    temp_dir = tempfile.gettempdir()
    pdf_path = Path(temp_dir) / f"character_{character_id}.pdf"
    
    try:
        char_dict = recalced_data.copy()
        char_dict["name"] = record.name
        char_dict["system"] = record.system
        
        export_pdf(char_dict, pdf_path)
        return FileResponse(
            path=str(pdf_path),
            filename=f"{record.name.replace(' ', '_')}_sheet.pdf",
            media_type="application/pdf"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF export failed: {str(exc)}"
        )

@router.post("/export/pdf")
def export_raw_data_to_pdf(payload: RecalculateRequest):
    """Statelessly compute derived statistics and export raw JSON character data to PDF."""
    try:
        recalced_data = service.recalculate(payload.data)
        
        temp_dir = tempfile.gettempdir()
        name_clean = recalced_data.get("name", "character").replace(" ", "_")
        pdf_path = Path(temp_dir) / f"{name_clean}_temp.pdf"
        
        char_dict = recalced_data.copy()
        
        export_pdf(char_dict, pdf_path)
        return FileResponse(
            path=str(pdf_path),
            filename=f"{name_clean}_sheet.pdf",
            media_type="application/pdf"
        )
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"PDF export failed: {str(exc)}"
        )

@router.post("/{character_id}/portrait")
def upload_character_portrait(character_id: int, file: UploadFile = File(...), db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Upload an image file as character portrait, convert to base64, and save it in character data, checking ownership."""
    if not file.content_type.startswith("image/"):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file must be an image."
        )
        
    record = service.get_character(db, character_id)
    if not record:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Character ID {character_id} not found."
        )
    if record.user_id and record.user_id != current_user.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu karakterin portresini değiştirme yetkiniz yok."
        )
        
    try:
        content = file.file.read()
        if len(content) > 5 * 1024 * 1024:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Image file size must be less than 5MB."
            )
            
        b64_data = base64.b64encode(content).decode("utf-8")
        data_url = f"data:{file.content_type};base64,{b64_data}"
        
        char_data = json.loads(record.data) if isinstance(record.data, str) else record.data
        char_data["portrait"] = data_url
        
        success = service.update_character(db, character_id, record.name, char_data)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Failed to update character with portrait."
            )
            
        return {"message": "Portrait uploaded successfully", "portrait": data_url}
    except Exception as exc:
        if isinstance(exc, HTTPException):
            raise exc
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Portrait upload failed: {str(exc)}"
        )

@router.post("/{character_id}/level-up", response_model=RecalculateResponse)
def level_up(character_id: int, payload: LevelUpPayload, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Level up the character by one step, processing and validating choices."""
    try:
        choices_dict = payload.model_dump()
        recalced_data = service.level_up(db, character_id, payload.class_name, choices_dict, current_user.id)
        warnings = service.validate(recalced_data)
        return RecalculateResponse(data=recalced_data, warnings=warnings)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Level-up process failed: {str(exc)}"
        )

@router.post("/{character_id}/level-undo", response_model=RecalculateResponse)
def level_undo(character_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    """Revert the highest level progression, reverting character stats to previous level."""
    try:
        recalced_data = service.level_undo(db, character_id, current_user.id)
        warnings = service.validate(recalced_data)
        return RecalculateResponse(data=recalced_data, warnings=warnings)
    except HTTPException as exc:
        raise exc
    except Exception as exc:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Level-undo process failed: {str(exc)}"
        )
