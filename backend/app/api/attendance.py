from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from datetime import date
from ..database import get_db
from ..services.attendance_service import (
    mark_attendance, get_student_attendance,
    get_group_attendance, get_attendance_stats
)
from ..schemas.attendance import AttendanceCreate, AttendanceResponse, AttendanceStats
from ..utils.security import verify_token

router = APIRouter()


def get_current_user(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    return int(payload["sub"]), payload["role"]


@router.post("/", response_model=AttendanceResponse, status_code=201)
def create_attendance(
        attendance_data: AttendanceCreate,
        authorization: str = Header(None),
        db: Session = Depends(get_db)
):
    user_id, role = get_current_user(authorization)
    if role != "teacher":
        raise HTTPException(status_code=403, detail="Только преподаватель может отмечать посещаемость")

    from ..models.teacher import Teacher
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")

    record = mark_attendance(
        db=db,
        student_id=attendance_data.student_id,
        subject_id=attendance_data.subject_id,
        teacher_id=teacher.id,
        status=attendance_data.status,
        lesson_date=attendance_data.lesson_date
    )

    # Логирование
    from ..models.user import User
    from ..services.audit_service import log_action
    user = db.query(User).filter(User.id == user_id).first()
    status_map = {'present': 'Присутствовал', 'absent': 'Отсутствовал', 'late': 'Опоздал', 'excused': 'Уваж. причина'}
    log_action(db, user_id, user.full_name if user else str(user_id),
               "Отметил посещаемость",
               f"Студент ID:{attendance_data.student_id}, Предмет ID:{attendance_data.subject_id}, Статус:{status_map.get(attendance_data.status, attendance_data.status)}")

    return record


@router.get("/student/{student_id}")
def get_student_attendance_route(student_id: int, subject_id: int = None, db: Session = Depends(get_db)):
    from ..models.student import Student as StudentModel
    from ..models.user import User as UserModel
    from ..models.subject import Subject as SubjectModel

    student = db.query(StudentModel).filter(StudentModel.user_id == student_id).first()
    if not student:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        return []

    records = get_student_attendance(db, student.id, subject_id)
    result = []
    for r in records:
        subject = db.query(SubjectModel).filter(SubjectModel.id == r.subject_id).first()
        student_user = db.query(UserModel).filter(UserModel.id == student.user_id).first()
        result.append({
            "id": r.id,
            "student_id": r.student_id,
            "subject_id": r.subject_id,
            "date": r.date.isoformat() if r.date else None,
            "status": r.status,
            "marked_by": r.marked_by,
            "student_name": student_user.full_name if student_user else "-",
            "subject_name": subject.name if subject else "-"
        })
    return result


@router.get("/teacher/my")
def get_my_attendance(authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id, role = get_current_user(authorization)
    if role != "teacher":
        raise HTTPException(status_code=403, detail="Только для преподавателя")

    from ..models.teacher import Teacher
    from ..models.attendance import Attendance
    from ..models.student import Student as StudentModel
    from ..models.user import User as UserModel
    from ..models.subject import Subject as SubjectModel

    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        return []

    records = db.query(Attendance).filter(Attendance.marked_by == teacher.id).order_by(Attendance.date.desc()).all()
    result = []
    for r in records:
        student = db.query(StudentModel).filter(StudentModel.id == r.student_id).first()
        student_user = db.query(UserModel).filter(UserModel.id == student.user_id).first() if student else None
        subject = db.query(SubjectModel).filter(SubjectModel.id == r.subject_id).first()
        result.append({
            "id": r.id,
            "student_id": r.student_id,
            "subject_id": r.subject_id,
            "date": r.date.isoformat() if r.date else None,
            "status": r.status,
            "marked_by": r.marked_by,
            "student_name": student_user.full_name if student_user else "-",
            "subject_name": subject.name if subject else "-"
        })
    return result


@router.get("/group/{group_id}/subject/{subject_id}")
def get_group_attendance_route(group_id: int, subject_id: int, lesson_date: date = None, db: Session = Depends(get_db)):
    return get_group_attendance(db, group_id, subject_id, lesson_date)


@router.get("/stats/{student_id}/subject/{subject_id}")
def get_stats(student_id: int, subject_id: int, db: Session = Depends(get_db)):
    return get_attendance_stats(db, student_id, subject_id)