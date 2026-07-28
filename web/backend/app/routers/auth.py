from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["Auth"])

class AuthPayload(BaseModel):
    username: str = Field(..., min_length=3, description="Kullanıcı adı (min 3 karakter)")
    password: str = Field(..., min_length=4, description="Şifre (min 4 karakter)")

class TokenResponse(BaseModel):
    access_token: str = Field(..., description="JWT erişim anahtarı")
    token_type: str = Field("bearer", description="Token türü (Bearer)")
    username: str = Field(..., description="Oturum açan kullanıcı adı")

@router.post(
    "/register",
    response_model=TokenResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Yeni Kullanıcı Kaydı",
    description="Sisteme yeni bir kullanıcı hesabı oluşturur ve geçerli JWT erişim anahtarını döndürür."
)
def register(payload: AuthPayload, db: Session = Depends(get_db)):
    user = AuthService.register_user(db, payload.username, payload.password)
    access_token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

@router.post(
    "/token",
    response_model=TokenResponse,
    summary="OAuth2 Form ile Login",
    description="OAuth2 Form standartlarına uygun kullanıcı adı ve şifre ile JWT oturum anahtarı alır."
)
def login_for_access_token(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = AuthService.get_user_by_username(db, form_data.username)
    if not user or not AuthService.verify_password(form_data.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}

@router.post(
    "/login-json",
    response_model=TokenResponse,
    summary="JSON Payload ile Login",
    description="JSON gövdesi (username/password) göndererek JWT token alır (Web/Masaüstü istemciler için)."
)
def login_json(payload: AuthPayload, db: Session = Depends(get_db)):
    user = AuthService.get_user_by_username(db, payload.username)
    if not user or not AuthService.verify_password(payload.password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = AuthService.create_access_token(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer", "username": user.username}
