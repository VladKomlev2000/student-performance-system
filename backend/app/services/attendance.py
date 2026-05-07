from pydantic import BaseModel, Field
from typing import Optional
from datetime import date, datetime


class AttendanceCreate(BaseModel):
    student_id: int
    subject_id: int
    status: str = Field(..., pattern="^(present|absent|late|excused)$")
    lesson_date: Optional[date] = None


class AttendanceResponse(BaseModel):
    id: int
    student_id: int
    subject_id: int
    date: date
    status: str
    marked_by: int
    created_at: datetime

    class Config:
        from_attributes = True


class AttendanceStats(BaseModel):
    total: int
    present: int
    absent: int
    late: int
    excused: int
    attendance_rate: float