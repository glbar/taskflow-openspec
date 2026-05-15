import re
import bcrypt
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import create_access_token, get_current_user

router = APIRouter(prefix="/auth", tags=["auth"])
EMAIL_RE = re.compile(r"^[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}$")


def hash_password(password: str) -> str:
    return bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(password: str, hashed: str) -> bool:
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))


def _user_out(user: models.User, token: str = None):
    out = {"user": {"id": user.id, "email": user.email, "team_id": user.team_id}}
    if token:
        out["token"] = token
    return out


@router.post("/signup", status_code=201)
def signup(data: schemas.UserCreate, db: Session = Depends(get_db)):
    if not EMAIL_RE.match(data.email):
        raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "올바른 이메일 형식이 아닙니다"})
    if len(data.password) < 8:
        raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "비밀번호는 8자 이상이어야 합니다"})
    if db.query(models.User).filter(models.User.email == data.email).first():
        raise HTTPException(409, detail={"code": "EMAIL_TAKEN", "message": "이미 가입된 이메일입니다"})

    user = models.User(email=data.email, password_hash=hash_password(data.password))
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_out(user, create_access_token(user.id))


@router.post("/login")
def login(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(models.User.email == data.email).first()
    if not user or not verify_password(data.password, user.password_hash):
        raise HTTPException(401, detail={"code": "INVALID_CREDENTIALS", "message": "이메일 또는 비밀번호가 일치하지 않습니다"})
    return _user_out(user, create_access_token(user.id))


@router.post("/logout")
def logout(current_user: models.User = Depends(get_current_user)):
    return {}


@router.get("/me")
def me(current_user: models.User = Depends(get_current_user)):
    return {"id": current_user.id, "email": current_user.email, "team_id": current_user.team_id}
