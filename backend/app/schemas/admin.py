from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ===== ГРУППЫ =====
class GroupCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    course: int = Field(..., ge=1, le=5)
    faculty: str = Field(..., min_length=2, max_length=100)


class GroupResponse(BaseModel):
    id: int
    name: str
    course: int
    faculty: str

    class Config:
        from_attributes = True


# ===== СТУДЕНТЫ =====
class StudentCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    group_id: int
    student_card_number: str = Field(..., min_length=1, max_length=20)
    enrollment_date: str = Field(..., pattern=r"^\d{4}-\d{2}-\d{2}$")
    parent_username: Optional[str] = None  # <-- новое поле


class StudentResponse(BaseModel):
    id: int
    user_id: int
    group_id: int
    student_card_number: str
    enrollment_date: str
    # Доп. поля
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    group_name: Optional[str] = None

    class Config:
        from_attributes = True


# ===== ПРЕПОДАВАТЕЛИ =====
class TeacherCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    department: str = Field(..., min_length=2, max_length=100)
    position: Optional[str] = None


class TeacherResponse(BaseModel):
    id: int
    user_id: int
    department: str
    position: Optional[str] = None
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None

    class Config:
        from_attributes = True


# ===== ПРЕДМЕТЫ =====
class SubjectCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=100)
    teacher_id: int
    group_id: int
    semester: int = Field(..., ge=1, le=2)
    hours: int = Field(..., ge=1)


class SubjectResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    group_id: int
    semester: int
    hours: int
    teacher_name: Optional[str] = None
    group_name: Optional[str] = None

    class Config:
        from_attributes = True


# ===== ПОЛЬЗОВАТЕЛИ (для списка) =====
class UserListItem(BaseModel):
    id: int
    username: str
    email: str
    full_name: str
    role: str

    class Config:
        from_attributes = True