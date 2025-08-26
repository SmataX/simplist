from sqlmodel import SQLModel, Field, Relationship
from typing import Optional

from .user import User

class Task(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id")
    content: str = Field(min_length=3, max_length=128)
    completed: bool = Field(default=False)

    user: Optional["User"] = Relationship(back_populates="tasks")