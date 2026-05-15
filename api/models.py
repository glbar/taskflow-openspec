from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Index
from sqlalchemy.orm import relationship
from .database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, autoincrement=True)
    email = Column(String(255), unique=True, nullable=False, index=True)
    password_hash = Column(String(255), nullable=False)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=True)
    team_joined_at = Column(DateTime, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    team = relationship("Team", foreign_keys=[team_id], back_populates="members")
    owned_teams = relationship("Team", foreign_keys="Team.owner_id", back_populates="owner")
    created_tasks = relationship("Task", foreign_keys="Task.creator_id", back_populates="creator")
    assigned_tasks = relationship("Task", foreign_keys="Task.assignee_id", back_populates="assignee")
    messages = relationship("Message", back_populates="user")


class Team(Base):
    __tablename__ = "teams"

    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(30), nullable=False)
    invite_code = Column(String(9), unique=True, nullable=False, index=True)
    # use_alter=True resolves circular FK with users.team_id
    owner_id = Column(
        Integer,
        ForeignKey("users.id", use_alter=True, name="fk_teams_owner_id"),
        nullable=False,
    )
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    owner = relationship("User", foreign_keys=[owner_id], back_populates="owned_teams")
    members = relationship("User", foreign_keys="User.team_id", back_populates="team")
    tasks = relationship("Task", back_populates="team", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="team", cascade="all, delete-orphan")


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    title = Column(String(100), nullable=False)
    status = Column(String(10), nullable=False, default="TODO")
    creator_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    assignee_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    team = relationship("Team", back_populates="tasks")
    creator = relationship("User", foreign_keys=[creator_id], back_populates="created_tasks")
    assignee = relationship("User", foreign_keys=[assignee_id], back_populates="assigned_tasks")


class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, autoincrement=True)
    team_id = Column(Integer, ForeignKey("teams.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    content = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow, nullable=False)

    team = relationship("Team", back_populates="messages")
    user = relationship("User", back_populates="messages")


# Composite indexes for polling and sorting
Index("ix_tasks_team_created", Task.team_id, Task.created_at)
Index("ix_messages_team_created", Message.team_id, Message.created_at)
