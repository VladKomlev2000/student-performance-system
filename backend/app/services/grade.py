from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class GradeCreate(BaseModel):
    student_id: int
    subject_id: int
    value: int = Field(..., ge=2, le=5)
    type: str = Field(..., pattern="^(exam|test|coursework|practice)$")
    comment: Optional[str] = None


class GradeUpdate(BaseModel):
    value: Optional[int] = Field(None, ge=2, le=5)
    comment: Optional[str] = None


class GradeResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    teacher_id: int
    value: int
    type: str
    date: datetime
    comment: Optional[str] = None

    class Config:
        from_attributes = True


class AverageGradeResponse(BaseModel):
    student_id: int
    subject_id: Optional[int] = None
    average_grade: float