import logging
from datetime import datetime, timedelta, timezone
from typing import Optional
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
import bcrypt
from sqlalchemy.orm import Session

from app.core.database import get_db
from app.models.user import User

logger = logging.getLogger(__name__)

# Security config
SECRET_KEY = "diyargezen_super_secret_key_9988776655"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 24 * 60  # 24 hours

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/token")

class AuthService:
    @staticmethod
    def hash_password(password: str) -> str:
        pwd_bytes = password.encode('utf-8')
        salt = bcrypt.gensalt()
        hashed_bytes = bcrypt.hashpw(pwd_bytes, salt)
        return hashed_bytes.decode('utf-8')

    @staticmethod
    def verify_password(plain_password: str, hashed_password: str) -> bool:
        try:
            plain_bytes = plain_password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(plain_bytes, hashed_bytes)
        except Exception:
            return False

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(timezone.utc) + expires_delta
        else:
            expire = datetime.now(timezone.utc) + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    def get_user_by_username(db: Session, username: str) -> Optional[User]:
        return db.query(User).filter(User.username == username).first()

    @staticmethod
    def register_user(db: Session, username: str, password: str) -> User:
        # Check if already exists
        existing = AuthService.get_user_by_username(db, username)
        if existing:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Username already registered."
            )
        hashed = AuthService.hash_password(password)
        db_user = User(
            username=username,
            hashed_password=hashed,
            created_at=datetime.now(timezone.utc).isoformat()
        )
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
        return db_user


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)) -> User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except jwt.PyJWTError:
        raise credentials_exception
        
    user = AuthService.get_user_by_username(db, username)
    if user is None:
        raise credentials_exception
    return user
