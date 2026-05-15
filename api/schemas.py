from datetime import datetime
from typing import Optional
from pydantic import BaseModel, EmailStr


class UserCreate(BaseModel):
    email: str
    password: str


class UserLogin(BaseModel):
    email: str
    password: str


class UserResponse(BaseModel):
    id: int
    email: str
    team_id: Optional[int] = None

    model_config = {"from_attributes": True}


class TeamCreate(BaseModel):
    name: str


class TeamJoin(BaseModel):
    invite_code: str


class TaskCreate(BaseModel):
    title: str
    assignee_id: Optional[int] = None


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    assignee_id: Optional[int] = None


class TaskStatusUpdate(BaseModel):
    status: str


class MessageCreate(BaseModel):
    content: str
