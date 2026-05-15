import os
from datetime import datetime, timedelta
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from .database import get_db
from . import models

SECRET_KEY = os.getenv("JWT_SECRET_KEY", "dev-secret-key")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_HOURS = 24

security = HTTPBearer()


def create_access_token(user_id: int) -> str:
    expire = datetime.utcnow() + timedelta(hours=ACCESS_TOKEN_EXPIRE_HOURS)
    return jwt.encode({"sub": str(user_id), "exp": expire}, SECRET_KEY, algorithm=ALGORITHM)


def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db),
) -> models.User:
    exc = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail={"code": "TOKEN_EXPIRED", "message": "인증이 만료되었습니다"},
    )
    try:
        payload = jwt.decode(credentials.credentials, SECRET_KEY, algorithms=[ALGORITHM])
        user_id = int(payload["sub"])
    except (JWTError, KeyError, ValueError):
        raise exc

    user = db.query(models.User).filter(models.User.id == user_id).first()
    if not user:
        raise exc
    return user


def get_current_team_member(
    team_id: int,
    current_user: models.User = Depends(get_current_user),
) -> models.User:
    if current_user.team_id != team_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"code": "FORBIDDEN", "message": "이 팀의 멤버가 아닙니다"},
        )
    return current_user
