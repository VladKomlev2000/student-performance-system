from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.grade_service import get_grades_for_parent, get_average_grade
from ..services.attendance_service import get_attendance_for_parent, get_attendance_stats
from ..schemas.grade import GradeResponse, AverageGradeResponse
from ..schemas.attendance import AttendanceResponse, AttendanceStats
from ..utils.security import verify_token
from ..models.user import User

router = APIRouter()


def get_parent_user(authorization: str = Header(None)):
    """Извлечь родителя из токена и проверить роль"""
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")

    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Недействительный токен")

    if payload.get("role") != "parent":
        raise HTTPException(status_code=403, detail="Доступно только для родителей")

    return int(payload["sub"])


@router.get("/child/grades", response_model=list[GradeResponse])
def get_child_grades(
        subject_id: int = None,
        db: Session = Depends(get_db),
        parent_id: int = Depends(get_parent_user)
):
    """Получить оценки своего ребёнка"""
    grades = get_grades_for_parent(db, parent_id, subject_id)
    return grades


@router.get("/child/grades/average", response_model=AverageGradeResponse)
def get_child_average(
        subject_id: int = None,
        db: Session = Depends(get_db),
        parent_id: int = Depends(get_parent_user)
):
    """Получить средний балл ребёнка"""
    from ..models.student import Student

    parent = db.query(User).filter(User.id == parent_id).first()
    student = db.query(Student).filter(Student.user_id == parent.linked_student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    avg = get_average_grade(db, student.id, subject_id)
    return AverageGradeResponse(
        student_id=student.id,
        subject_id=subject_id,
        average_grade=avg
    )


@router.get("/child/attendance", response_model=list[AttendanceResponse])
def get_child_attendance(
        subject_id: int = None,
        db: Session = Depends(get_db),
        parent_id: int = Depends(get_parent_user)
):
    """Получить посещаемость своего ребёнка"""
    records = get_attendance_for_parent(db, parent_id, subject_id)
    return records


@router.get("/child/attendance/stats/{subject_id}", response_model=AttendanceStats)
def get_child_attendance_stats(
        subject_id: int,
        db: Session = Depends(get_db),
        parent_id: int = Depends(get_parent_user)
):
    """Получить статистику посещаемости ребёнка по предмету"""
    from ..models.student import Student

    parent = db.query(User).filter(User.id == parent_id).first()
    student = db.query(Student).filter(Student.user_id == parent.linked_student_id).first()

    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    return get_attendance_stats(db, student.id, subject_id)


@router.get("/child/info")
def get_child_info(
        db: Session = Depends(get_db),
        parent_id: int = Depends(get_parent_user)
):
    """Получить информацию о ребёнке"""
    from ..models.student import Student
    from ..models.group import Group

    parent = db.query(User).filter(User.id == parent_id).first()
    if not parent or not parent.linked_student_id:
        raise HTTPException(status_code=404, detail="Ребёнок не привязан к аккаунту")

    student = db.query(Student).filter(Student.user_id == parent.linked_student_id).first()
    if not student:
        raise HTTPException(status_code=404, detail="Студент не найден")

    child_user = db.query(User).filter(User.id == student.user_id).first()
    group = db.query(Group).filter(Group.id == student.group_id).first()

    return {
        "student_id": student.id,
        "full_name": child_user.full_name,
        "email": child_user.email,
        "student_card": student.student_card_number,
        "group_name": group.name if group else "Не указана",
        "enrollment_date": student.enrollment_date
    }