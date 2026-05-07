from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.grade_service import (
    get_student_grades, get_group_grades, get_average_grade,
    add_grade, update_grade, delete_grade
)
from ..schemas.grade import GradeCreate, GradeUpdate, GradeResponse, AverageGradeResponse
from ..utils.security import verify_token
from ..models.user import User

router = APIRouter()


def get_current_user_id(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Недействительный токен")
    return int(payload["sub"]), payload["role"]


@router.get("/student/{student_id}", response_model=list[dict])
def get_grades(student_id: int, subject_id: int = None, db: Session = Depends(get_db)):
    from ..models.student import Student as StudentModel
    from ..models.subject import Subject as SubjectModel
    student = db.query(StudentModel).filter(StudentModel.user_id == student_id).first()
    if not student:
        student = db.query(StudentModel).filter(StudentModel.id == student_id).first()
    if not student:
        return []
    grades = get_student_grades(db, student.id, subject_id)
    result = []
    for g in grades:
        subject = db.query(SubjectModel).filter(SubjectModel.id == g.subject_id).first()
        student_user = db.query(User).filter(User.id == student.user_id).first()
        result.append({
            "id": g.id, "student_id": g.student_id, "subject_id": g.subject_id,
            "teacher_id": g.teacher_id, "value": g.value, "type": g.type,
            "date": g.date.isoformat() if g.date else None, "comment": g.comment,
            "student_name": student_user.full_name if student_user else "-",
            "subject_name": subject.name if subject else "-"
        })
    return result


@router.get("/student/{student_id}/average", response_model=AverageGradeResponse)
def get_average(student_id: int, subject_id: int = None, db: Session = Depends(get_db)):
    avg = get_average_grade(db, student_id, subject_id)
    return AverageGradeResponse(student_id=student_id, subject_id=subject_id, average_grade=avg)


@router.get("/group/{group_id}/subject/{subject_id}", response_model=list[GradeResponse])
def get_group_grades_route(group_id: int, subject_id: int, db: Session = Depends(get_db)):
    return get_group_grades(db, group_id, subject_id)


@router.post("/", response_model=GradeResponse, status_code=201)
def create_grade(grade_data: GradeCreate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id, role = get_current_user_id(authorization)
    if role != "teacher":
        raise HTTPException(status_code=403, detail="Только преподаватель может ставить оценки")
    from ..models.teacher import Teacher
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    grade = add_grade(db=db, student_id=grade_data.student_id, subject_id=grade_data.subject_id,
                      teacher_id=teacher.id, value=grade_data.value, grade_type=grade_data.type, comment=grade_data.comment)
    user = db.query(User).filter(User.id == user_id).first()
    from ..services.audit_service import log_action
    log_action(db, user_id, user.full_name if user else str(user_id),
               "Выставил оценку", f"Студент ID:{grade_data.student_id}, Предмет ID:{grade_data.subject_id}, Оценка:{grade_data.value}")
    return grade


@router.put("/{grade_id}", response_model=GradeResponse)
def update_grade_route(grade_id: int, grade_data: GradeUpdate, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id, role = get_current_user_id(authorization)
    if role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    grade = update_grade(db, grade_id, grade_data.value, grade_data.comment)
    if not grade:
        raise HTTPException(status_code=404, detail="Оценка не найдена")
    user = db.query(User).filter(User.id == user_id).first()
    from ..services.audit_service import log_action
    log_action(db, user_id, user.full_name if user else str(user_id),
               "Изменил оценку", f"ID:{grade_id}, Новое значение:{grade_data.value}, Комментарий:{grade_data.comment}")
    return grade


@router.delete("/{grade_id}")
def delete_grade_route(grade_id: int, authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id, role = get_current_user_id(authorization)
    if role not in ["teacher", "admin"]:
        raise HTTPException(status_code=403, detail="Недостаточно прав")
    if delete_grade(db, grade_id):
        user = db.query(User).filter(User.id == user_id).first()
        from ..services.audit_service import log_action
        log_action(db, user_id, user.full_name if user else str(user_id), "Удалил оценку", f"ID:{grade_id}")
        return {"message": "Оценка удалена"}
    raise HTTPException(status_code=404, detail="Оценка не найдена")


@router.get("/teacher/my")
def get_my_grades(authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id, role = get_current_user_id(authorization)
    if role != "teacher":
        raise HTTPException(status_code=403, detail="Только для преподавателя")
    from ..models.teacher import Teacher
    from ..models.grade import Grade
    from ..models.student import Student
    from ..models.subject import Subject
    from ..models.group import Group
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    grades = db.query(Grade).filter(Grade.teacher_id == teacher.id).order_by(Grade.date.desc()).all()
    result = []
    for g in grades:
        student = db.query(Student).filter(Student.id == g.student_id).first()
        student_user = db.query(User).filter(User.id == student.user_id).first() if student else None
        subject = db.query(Subject).filter(Subject.id == g.subject_id).first()
        group = db.query(Group).filter(Group.id == student.group_id).first() if student else None
        result.append({
            "id": g.id, "student_id": g.student_id, "subject_id": g.subject_id,
            "teacher_id": g.teacher_id, "value": g.value, "type": g.type,
            "date": g.date.isoformat() if g.date else None, "comment": g.comment,
            "student_name": student_user.full_name if student_user else f"ID: {g.student_id}",
            "subject_name": subject.name if subject else f"ID: {g.subject_id}",
            "group_name": group.name if group else "-"
        })
    return result


@router.get("/teacher/subjects")
def get_teacher_subjects(authorization: str = Header(None), db: Session = Depends(get_db)):
    user_id, role = get_current_user_id(authorization)
    if role != "teacher":
        raise HTTPException(status_code=403, detail="Только для преподавателя")
    from ..models.teacher import Teacher
    from ..models.subject import Subject
    from ..models.group import Group
    teacher = db.query(Teacher).filter(Teacher.user_id == user_id).first()
    if not teacher:
        raise HTTPException(status_code=404, detail="Преподаватель не найден")
    subjects = db.query(Subject).filter(Subject.teacher_id == teacher.id).all()
    result = []
    for s in subjects:
        group = db.query(Group).filter(Group.id == s.group_id).first()
        result.append({"id": s.id, "name": s.name, "group_name": group.name if group else "-", "semester": s.semester})
    return result