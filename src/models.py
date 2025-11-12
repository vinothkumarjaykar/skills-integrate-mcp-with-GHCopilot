from typing import Optional, List
from sqlmodel import SQLModel, Field, Relationship
from datetime import datetime

class Enrollment(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    student_email: str
    activity_id: Optional[int] = Field(default=None, foreign_key="activity.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Activity(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    description: Optional[str] = None
    schedule: Optional[str] = None
    max_participants: int = 0
    participants: List[Enrollment] = Relationship(back_populates="activity")


Enrollment.activity = Relationship(back_populates="participants")


class Student(SQLModel, table=True):
    email: str = Field(primary_key=True, index=True)
    name: Optional[str] = None
    grade: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
