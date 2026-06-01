from pydantic import BaseModel, Field, EmailStr
from typing import Optional
from datetime import datetime


# ===== КЛАССЫ =====
class ClassCreate(BaseModel):
    name: str = Field(..., min_length=2, max_length=50)
    grade_number: int = Field(..., ge=1, le=11)
    grade_letter: str = Field(..., min_length=1, max_length=5)
    class_teacher_id: Optional[int] = None


class ClassResponse(BaseModel):
    id: int
    name: str
    grade_number: int
    grade_letter: str
    class_teacher_id: Optional[int] = None
    class_teacher_name: Optional[str] = None

    class Config:
        from_attributes = True


# ===== УЧЕНИКИ =====
class StudentCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    class_id: int
    parent_username: Optional[str] = None


class StudentResponse(BaseModel):
    id: int
    user_id: int
    class_id: int
    username: Optional[str] = None
    email: Optional[str] = None
    full_name: Optional[str] = None
    class_name: Optional[str] = None

    class Config:
        from_attributes = True


# ===== УЧИТЕЛЯ =====
class TeacherCreate(BaseModel):
    username: str = Field(..., min_length=3, max_length=50)
    email: EmailStr
    password: str = Field(..., min_length=6)
    full_name: str = Field(..., min_length=1, max_length=100)
    position: Optional[str] = None


class TeacherResponse(BaseModel):
    id: int
    user_id: int
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
    class_id: int
    quarter: int = Field(..., ge=1, le=4)
    hours: int = Field(..., ge=1)


class SubjectResponse(BaseModel):
    id: int
    name: str
    teacher_id: int
    class_id: int
    quarter: int
    hours: int
    teacher_name: Optional[str] = None
    class_name: Optional[str] = None

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