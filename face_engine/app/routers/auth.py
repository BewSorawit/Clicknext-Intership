from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import User
from app.security.jwt import decode_token
from typing import Optional

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


def check_quota(user):
    return user.api_quota_limit > 0
