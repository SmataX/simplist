from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from .task import Task

class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str = Field(min_length=3, max_length=50, unique=True)
    email: str = Field(min_length=5, max_length=100, unique=True)
    password: str = Field(min_length=6)
    created_at: datetime = Field(default_factory=datetime.now)

    tasks: list["Task"] = Relationship(back_populates="user")