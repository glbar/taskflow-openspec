from datetime import datetime
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_team_member

router = APIRouter(tags=["messages"])


def _msg_out(msg: models.Message, db: Session):
    user = db.query(models.User).filter(models.User.id == msg.user_id).first()
    return {
        "id": msg.id, "user_id": msg.user_id,
        "user_email": user.email if user else "",
        "content": msg.content, "created_at": msg.created_at,
    }


@router.get("/teams/{team_id}/messages")
def get_messages(
    team_id: int,
    since: Optional[str] = Query(None),
    current_user: models.User = Depends(get_current_team_member),
    db: Session = Depends(get_db),
):
    q = db.query(models.Message).filter(models.Message.team_id == team_id)
    if since:
        try:
            since_dt = datetime.fromisoformat(since.replace("Z", "+00:00")).replace(tzinfo=None)
            msgs = q.filter(models.Message.created_at > since_dt).order_by(models.Message.created_at.asc()).all()
        except ValueError:
            raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "since 형식이 올바르지 않습니다"})
    else:
        rows = q.order_by(models.Message.created_at.desc()).limit(50).all()
        msgs = list(reversed(rows))
    return [_msg_out(m, db) for m in msgs]


@router.post("/teams/{team_id}/messages", status_code=201)
def create_message(
    team_id: int,
    data: schemas.MessageCreate,
    current_user: models.User = Depends(get_current_team_member),
    db: Session = Depends(get_db),
):
    content = data.content.strip() if data.content else ""
    if not content:
        raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "메시지를 입력해주세요"})
    if len(content) > 1000:
        raise HTTPException(400, detail={"code": "TOO_LONG", "message": "메시지는 1000자 이내로 입력하세요", "limit": 1000, "actual": len(content)})

    msg = models.Message(team_id=team_id, user_id=current_user.id, content=content)
    db.add(msg)
    db.commit()
    db.refresh(msg)
    return _msg_out(msg, db)


@router.delete("/messages/{message_id}")
def delete_message(message_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    msg = db.query(models.Message).filter(models.Message.id == message_id).first()
    if not msg:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "메시지를 찾을 수 없습니다"})
    if msg.user_id != current_user.id:
        raise HTTPException(403, detail={"code": "NOT_OWNER", "message": "본인의 메시지만 삭제할 수 있습니다"})
    db.delete(msg)
    db.commit()
    return {}
