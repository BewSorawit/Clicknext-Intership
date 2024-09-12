from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.security.jwt import create_access_token, create_refresh_token, decode_token, ACCESS_TOKEN_EXPIRE_MINUTES, REFRESH_TOKEN_EXPIRE_DAYS
from app.security.password import get_password_hash, verify_password
from pydantic import BaseModel
from typing import Optional
from datetime import timedelta

router = APIRouter(prefix='/user', tags=['user'])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


def get_user_by_username(user_name: str, db: Session) -> User:
    return db.query(User).filter(User.user_name == user_name).first()


def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    try:
        payload = decode_token(token)
        user_name = payload.get("user_name")
        if user_name is None:
            raise HTTPException(status_code=401, detail="Invalid token")

        user = get_user_by_username(user_name, db)
        if user is None:
            raise HTTPException(status_code=401, detail="User not found")
        return {"user_id": user.id}
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid token")


class UserCreate(BaseModel):
    user_name: str
    email: str
    password: str
    api_quota_limit: Optional[int] = 100


class UserLogin(BaseModel):
    user_name: str
    password: str


class Token(BaseModel):
    access_token: str
    refresh_token: str
    token_type: str


class TokenRefresh(BaseModel):
    refresh_token: str


@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    user_in_db = db.query(User).filter(
        User.email == user.email or User.user_name == user.user_name
    ).first()
    if user_in_db:
        raise HTTPException(
            status_code=400, detail="Username or email already registered"
        )

    hashed_password = get_password_hash(user.password)
    new_user = User(
        user_name=user.user_name,
        email=user.email,
        password=hashed_password,
        api_quota_limit=user.api_quota_limit
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {"msg": "User created successfully"}


@router.post('/login', response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    user_in_db = db.query(User).filter(
        User.user_name == user.user_name
    ).first()

    if not user_in_db or not verify_password(user.password, user_in_db.password):
        raise HTTPException(
            status_code=401, detail="Invalid username or password"
        )

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)

    access_token = create_access_token(
        data={"user_name": user_in_db.user_name},
        expires_delta=access_token_expires
    )
    refresh_token = create_refresh_token(
        data={"user_name": user_in_db.user_name},
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }


@router.post('/refresh', response_model=Token)
def refresh_token(token: TokenRefresh, db: Session = Depends(get_db)):
    try:
        payload = decode_token(token.refresh_token)
        user_name: str = payload.get('user_name')
        if user_name is None:
            raise HTTPException(
                status_code=401, detail="Invalid refresh token"
            )
    except JWTError:
        raise HTTPException(status_code=401, detail="Invalid refresh token")

    user_in_db = db.query(User).filter(User.user_name == user_name).first()

    if user_in_db is None:
        raise HTTPException(status_code=404, detail="User not found")

    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"user_name": user_in_db.user_name},
        expires_delta=access_token_expires
    )
    refresh_token_expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
    refresh_token = create_refresh_token(
        data={"user_name": user_in_db.user_name},
        expires_delta=refresh_token_expires
    )

    return {
        "access_token": access_token,
        "refresh_token": refresh_token,
        "token_type": "bearer"
    }
