import re
import random
import string
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_team_member

router = APIRouter(prefix="/teams", tags=["teams"])
INVITE_RE = re.compile(r"^[A-Z]{4}-[0-9]{4}$")


def _gen_invite_code(db: Session) -> str:
    while True:
        code = "".join(random.choices(string.ascii_uppercase, k=4)) + "-" + "".join(random.choices(string.digits, k=4))
        if not db.query(models.Team).filter(models.Team.invite_code == code).first():
            return code


@router.post("", status_code=201)
def create_team(data: schemas.TeamCreate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.team_id is not None:
        raise HTTPException(409, detail={"code": "ALREADY_IN_TEAM", "message": "이미 팀에 소속되어 있습니다"})
    if not 1 <= len(data.name.strip()) <= 30:
        raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "팀 이름은 1~30자여야 합니다"})

    team = models.Team(name=data.name.strip(), invite_code=_gen_invite_code(db), owner_id=current_user.id)
    db.add(team)
    db.flush()

    current_user.team_id = team.id
    current_user.team_joined_at = datetime.utcnow()
    db.commit()
    db.refresh(team)

    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "owner_id": team.owner_id, "created_at": team.created_at}


@router.post("/join")
def join_team(data: schemas.TeamJoin, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if not INVITE_RE.match(data.invite_code):
        raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "형식이 올바르지 않습니다"})
    if current_user.team_id is not None:
        raise HTTPException(409, detail={"code": "ALREADY_IN_TEAM", "message": "이미 다른 팀에 소속되어 있습니다"})

    team = db.query(models.Team).filter(models.Team.invite_code == data.invite_code).first()
    if not team:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "해당 초대코드를 찾을 수 없습니다"})

    current_user.team_id = team.id
    current_user.team_joined_at = datetime.utcnow()
    db.commit()

    member_count = db.query(models.User).filter(models.User.team_id == team.id).count()
    return {"team": {"id": team.id, "name": team.name, "member_count": member_count}, "redirect": f"/teams/{team.id}"}


@router.get("/{team_id}")
def get_team(team_id: int, current_user: models.User = Depends(get_current_team_member), db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    if not team:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "팀을 찾을 수 없습니다"})
    return {"id": team.id, "name": team.name, "invite_code": team.invite_code, "owner_id": team.owner_id, "created_at": team.created_at}


@router.get("/{team_id}/members")
def get_members(team_id: int, current_user: models.User = Depends(get_current_team_member), db: Session = Depends(get_db)):
    team = db.query(models.Team).filter(models.Team.id == team_id).first()
    members = db.query(models.User).filter(models.User.team_id == team_id).all()
    members.sort(key=lambda m: (m.id != team.owner_id, m.id))
    return [
        {"id": m.id, "email": m.email, "is_owner": m.id == team.owner_id, "team_joined_at": m.team_joined_at}
        for m in members
    ]


@router.delete("/{team_id}/leave")
def leave_team(team_id: int, current_user: models.User = Depends(get_current_team_member), db: Session = Depends(get_db)):
    current_user.team_id = None
    current_user.team_joined_at = None
    db.commit()
    return {}
