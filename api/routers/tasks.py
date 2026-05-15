from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from .. import models, schemas
from ..database import get_db
from ..auth import get_current_user, get_current_team_member

router = APIRouter(tags=["tasks"])
VALID_STATUSES = {"TODO", "DOING", "DONE"}


def _task_out(task: models.Task, db: Session):
    assignee_email = None
    if task.assignee_id:
        u = db.query(models.User).filter(models.User.id == task.assignee_id).first()
        assignee_email = u.email if u else None
    return {
        "id": task.id, "team_id": task.team_id, "title": task.title,
        "status": task.status, "creator_id": task.creator_id,
        "assignee_id": task.assignee_id, "assignee_email": assignee_email,
        "created_at": task.created_at,
    }


@router.get("/teams/{team_id}/tasks")
def get_tasks(
    team_id: int,
    filter: Optional[str] = Query(None),
    current_user: models.User = Depends(get_current_team_member),
    db: Session = Depends(get_db),
):
    q = db.query(models.Task).filter(models.Task.team_id == team_id)
    if filter == "me":
        q = q.filter(models.Task.assignee_id == current_user.id)
    elif filter == "unassigned":
        q = q.filter(models.Task.assignee_id == None)
    tasks = q.order_by(models.Task.created_at.desc()).all()
    return [_task_out(t, db) for t in tasks]


@router.post("/teams/{team_id}/tasks", status_code=201)
def create_task(
    team_id: int,
    data: schemas.TaskCreate,
    current_user: models.User = Depends(get_current_team_member),
    db: Session = Depends(get_db),
):
    if not 1 <= len(data.title.strip()) <= 100:
        raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "제목은 1~100자여야 합니다"})

    task = models.Task(
        team_id=team_id, title=data.title.strip(), status="TODO",
        creator_id=current_user.id, assignee_id=data.assignee_id,
    )
    db.add(task)
    db.commit()
    db.refresh(task)
    return _task_out(task, db)


@router.get("/tasks/{task_id}")
def get_task(task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "태스크를 찾을 수 없습니다"})
    if current_user.team_id != task.team_id:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "권한이 없습니다"})
    return _task_out(task, db)


@router.put("/tasks/{task_id}")
def update_task(task_id: int, data: schemas.TaskUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "태스크를 찾을 수 없습니다"})
    if current_user.team_id != task.team_id:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "권한이 없습니다"})

    if data.title is not None:
        if not 1 <= len(data.title.strip()) <= 100:
            raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "제목은 1~100자여야 합니다"})
        task.title = data.title.strip()
    if "assignee_id" in data.model_fields_set:
        task.assignee_id = data.assignee_id

    db.commit()
    db.refresh(task)
    return _task_out(task, db)


@router.patch("/tasks/{task_id}/status")
def update_status(task_id: int, data: schemas.TaskStatusUpdate, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    if data.status not in VALID_STATUSES:
        raise HTTPException(400, detail={"code": "VALIDATION_ERROR", "message": "유효하지 않은 상태입니다 (TODO/DOING/DONE)"})

    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "태스크를 찾을 수 없습니다"})
    if current_user.team_id != task.team_id:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "권한이 없습니다"})

    task.status = data.status
    db.commit()
    db.refresh(task)
    return _task_out(task, db)


@router.delete("/tasks/{task_id}")
def delete_task(task_id: int, current_user: models.User = Depends(get_current_user), db: Session = Depends(get_db)):
    task = db.query(models.Task).filter(models.Task.id == task_id).first()
    if not task:
        raise HTTPException(404, detail={"code": "NOT_FOUND", "message": "태스크를 찾을 수 없습니다"})
    if current_user.team_id != task.team_id:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "권한이 없습니다"})

    team = db.query(models.Team).filter(models.Team.id == task.team_id).first()
    if task.creator_id != current_user.id and team.owner_id != current_user.id:
        raise HTTPException(403, detail={"code": "FORBIDDEN", "message": "권한이 없습니다"})

    db.delete(task)
    db.commit()
    return {}
