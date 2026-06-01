from fastapi import APIRouter, Depends, HTTPException, Header, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.grade_service import get_student_grades, get_grades_for_parent
from ..services.attendance_service import get_student_attendance, get_attendance_for_parent
from ..services.export_service import (
    export_grades_to_excel, export_attendance_to_excel,
    export_grades_to_word, export_attendance_to_word
)
from ..utils.security import verify_token
from ..models.user import User
from ..models.student import Student

router = APIRouter()


def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    return int(payload["sub"]), payload["role"]


def _get_grades_data(user_id: int, role: str, subject_id: int, db: Session):
    """Общая логика получения оценок для экспорта."""
    user = db.query(User).filter(User.id == user_id).first()
    student_name = user.full_name if user else "Ученик"

    if role == "parent":
        grades = get_grades_for_parent(db, user_id, subject_id)
        parent = db.query(User).filter(User.id == user_id).first()
        child = db.query(Student).filter(Student.user_id == parent.linked_student_id).first()
        child_user = db.query(User).filter(User.id == child.user_id).first() if child else None
        student_name = child_user.full_name if child_user else "Ученик"
    elif role == "teacher":
        from ..models.teacher import Teacher
        from ..models.grade import Grade
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        if teacher:
            grades = db.query(Grade).filter(Grade.teacher_id == teacher.id).all()
        else:
            grades = []
    else:
        student = db.query(Student).filter(Student.user_id == user_id).first()
        student_id = student.id if student else user_id
        grades = get_student_grades(db, student_id, subject_id)

    return grades, student_name, user


def _get_attendance_data(user_id: int, role: str, subject_id: int, db: Session):
    """Общая логика получения посещаемости для экспорта."""
    user = db.query(User).filter(User.id == user_id).first()
    student_name = user.full_name if user else "Ученик"

    if role == "parent":
        records = get_attendance_for_parent(db, user_id, subject_id)
        parent = db.query(User).filter(User.id == user_id).first()
        child = db.query(Student).filter(Student.user_id == parent.linked_student_id).first()
        child_user = db.query(User).filter(User.id == child.user_id).first() if child else None
        student_name = child_user.full_name if child_user else "Ученик"
    elif role == "teacher":
        from ..models.teacher import Teacher
        from ..models.attendance import Attendance
        teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
        if teacher:
            records = db.query(Attendance).filter(Attendance.marked_by == teacher.id).all()
        else:
            records = []
    else:
        student = db.query(Student).filter(Student.user_id == user_id).first()
        student_id = student.id if student else user_id
        records = get_student_attendance(db, student_id, subject_id)

    return records, student_name, user


# ==================== GRADES ====================

@router.get("/grades")
def download_grades(
        token: str = None,
        authorization: str = Header(None),
        subject_id: int = None,
        format: str = Query("excel", description="Формат: excel или word"),
        db: Session = Depends(get_db)
):
    if token:
        user_id, role = get_current_user(f"Bearer {token}")
    else:
        user_id, role = get_current_user(authorization)

    grades, student_name, user = _get_grades_data(user_id, role, subject_id, db)

    safe_name = "student" if not student_name else "".join(
        c if c.isascii() and c.isalnum() else "_" for c in student_name)

    if format == "word":
        file_data = export_grades_to_word(grades, student_name)
        filename = f"grades_{safe_name}.docx"
        media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        action = "Экспортировал оценки в Word"
    else:
        file_data = export_grades_to_excel(grades, student_name)
        filename = f"grades_{safe_name}.xlsx"
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        action = "Экспортировал оценки в Excel"

    from ..services.audit_service import log_action
    log_action(db, user_id, user.full_name if user else str(user_id), action, f"Файл: {filename}")

    return StreamingResponse(
        file_data,
        media_type=media_type,
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
    )


# ==================== ATTENDANCE ====================

@router.get("/attendance")
def download_attendance(
        token: str = None,
        authorization: str = Header(None),
        subject_id: int = None,
        format: str = Query("excel", description="Формат: excel или word"),
        db: Session = Depends(get_db)
):
    if token:
        user_id, role = get_current_user(f"Bearer {token}")
    else:
        user_id, role = get_current_user(authorization)

    records, student_name, user = _get_attendance_data(user_id, role, subject_id, db)

    safe_name = "student" if not student_name else "".join(
        c if c.isascii() and c.isalnum() else "_" for c in student_name)

    if format == "word":
        file_data = export_attendance_to_word(records, student_name)
        filename = f"attendance_{safe_name}.docx"
        media_type = 'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        action = "Экспортировал посещаемость в Word"
    else:
        file_data = export_attendance_to_excel(records, student_name)
        filename = f"attendance_{safe_name}.xlsx"
        media_type = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        action = "Экспортировал посещаемость в Excel"

    from ..services.audit_service import log_action
    log_action(db, user_id, user.full_name if user else str(user_id), action, f"Файл: {filename}")

    return StreamingResponse(
        file_data,
        media_type=media_type,
        headers={
            'Content-Disposition': f'attachment; filename={filename}',
            'Access-Control-Allow-Origin': '*',
            'Access-Control-Expose-Headers': 'Content-Disposition'
        }
    )