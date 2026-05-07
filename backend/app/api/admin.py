from ..models.user import User, UserRole
from ..models.student import Student
from fastapi import APIRouter, Depends, HTTPException, Header
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.admin_service import (
    create_group, get_all_groups, delete_group,
    create_student, get_all_students, get_students_by_group, delete_student,
    create_teacher, get_all_teachers, delete_teacher,
    create_subject, get_all_subjects, get_subjects_by_group, delete_subject
)
from ..schemas.admin import (
    GroupCreate, GroupResponse,
    StudentCreate, StudentResponse,
    TeacherCreate, TeacherResponse,
    SubjectCreate, SubjectResponse
)
from ..models.group import Group
from ..utils.security import verify_token

router = APIRouter()


def check_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Доступно только администратору")
    return int(payload["sub"])


# ==================== GROUPS ====================

@router.post("/groups", response_model=GroupResponse, status_code=201)
def add_group(group_data: GroupCreate, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    group = create_group(db, group_data.name, group_data.course, group_data.faculty)
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Создал группу", f"Название:{group_data.name}, Курс:{group_data.course}")
    return group


@router.get("/groups", response_model=list[GroupResponse])
def list_groups(db: Session = Depends(get_db)):
    return get_all_groups(db)


@router.delete("/groups/{group_id}")
def remove_group(group_id: int, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    if delete_group(db, group_id):
        from ..services.audit_service import log_action
        log_action(db, admin_id, "admin", "Удалил группу", f"ID:{group_id}")
        return {"message": "Группа удалена"}
    raise HTTPException(status_code=404, detail="Группа не найдена")


# ==================== STUDENTS ====================

@router.post("/students", response_model=StudentResponse, status_code=201)
def add_student(student_data: StudentCreate, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    student = create_student(db=db, username=student_data.username, email=student_data.email,
                             password=student_data.password, full_name=student_data.full_name,
                             group_id=student_data.group_id, student_card=student_data.student_card_number,
                             enrollment_date=student_data.enrollment_date)
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Создал студента", f"Логин:{student_data.username}, ФИО:{student_data.full_name}")
    return student


@router.get("/students", response_model=list[dict])
def list_students(group_id: int = None, db: Session = Depends(get_db)):
    if group_id: students = get_students_by_group(db, group_id)
    else: students = get_all_students(db)
    result = []
    for s in students:
        result.append({"id": s.id, "user_id": s.user_id, "group_id": s.group_id,
                       "student_card_number": s.student_card_number, "enrollment_date": s.enrollment_date,
                       "username": s.user.username, "email": s.user.email, "full_name": s.user.full_name,
                       "group_name": s.group.name if s.group else "-"})
    return result


@router.delete("/students/{student_id}")
def remove_student(student_id: int, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    if delete_student(db, student_id):
        from ..services.audit_service import log_action
        log_action(db, admin_id, "admin", "Удалил студента", f"ID:{student_id}")
        return {"message": "Студент удалён"}
    raise HTTPException(status_code=404, detail="Студент не найден")


# ==================== TEACHERS ====================

@router.post("/teachers", response_model=TeacherResponse, status_code=201)
def add_teacher(teacher_data: TeacherCreate, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    teacher = create_teacher(db=db, username=teacher_data.username, email=teacher_data.email,
                             password=teacher_data.password, full_name=teacher_data.full_name,
                             department=teacher_data.department, position=teacher_data.position)
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Создал преподавателя", f"Логин:{teacher_data.username}, ФИО:{teacher_data.full_name}")
    return teacher


@router.get("/teachers", response_model=list[dict])
def list_teachers(db: Session = Depends(get_db)):
    teachers = get_all_teachers(db)
    result = []
    for t in teachers:
        result.append({"id": t.id, "user_id": t.user_id, "department": t.department, "position": t.position,
                       "username": t.user.username, "email": t.user.email, "full_name": t.user.full_name})
    return result


@router.delete("/teachers/{teacher_id}")
def remove_teacher(teacher_id: int, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    if delete_teacher(db, teacher_id):
        from ..services.audit_service import log_action
        log_action(db, admin_id, "admin", "Удалил преподавателя", f"ID:{teacher_id}")
        return {"message": "Преподаватель удалён"}
    raise HTTPException(status_code=404, detail="Преподаватель не найден")


# ==================== SUBJECTS ====================

@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def add_subject(subject_data: SubjectCreate, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    subject = create_subject(db=db, name=subject_data.name, teacher_id=subject_data.teacher_id,
                             group_id=subject_data.group_id, semester=subject_data.semester, hours=subject_data.hours)
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Создал предмет", f"Название:{subject_data.name}")
    return subject


@router.get("/subjects", response_model=list[dict])
def list_subjects(group_id: int = None, db: Session = Depends(get_db)):
    if group_id: subjects = get_subjects_by_group(db, group_id)
    else: subjects = get_all_subjects(db)
    result = []
    for subj in subjects:
        teacher_user = db.query(User).filter(User.id == subj.teacher.user_id).first()
        group = db.query(Group).filter(Group.id == subj.group_id).first()
        result.append({"id": subj.id, "name": subj.name, "teacher_id": subj.teacher_id, "group_id": subj.group_id,
                       "semester": subj.semester, "hours": subj.hours,
                       "teacher_name": teacher_user.full_name if teacher_user else "-",
                       "group_name": group.name if group else "-"})
    return result


@router.delete("/subjects/{subject_id}")
def remove_subject(subject_id: int, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    if delete_subject(db, subject_id):
        from ..services.audit_service import log_action
        log_action(db, admin_id, "admin", "Удалил предмет", f"ID:{subject_id}")
        return {"message": "Предмет удалён"}
    raise HTTPException(status_code=404, detail="Предмет не найден")


# ==================== РОДИТЕЛИ ====================

@router.post("/parents", status_code=201)
def add_parent(username: str, email: str, password: str, full_name: str, student_user_ids: str = "",
               db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    from ..utils.security import hash_password
    from ..services.audit_service import log_action
    existing = db.query(User).filter(User.username == username).first()
    if existing: raise HTTPException(status_code=400, detail="Логин уже занят")
    parent = User(username=username, email=email, hashed_password=hash_password(password),
                  full_name=full_name, role=UserRole.PARENT, linked_student_id=None)
    db.add(parent)
    db.flush()
    children = []
    if student_user_ids:
        for uid in student_user_ids.split(","):
            uid = uid.strip()
            if uid:
                su = db.query(User).filter(User.id == int(uid), User.role == UserRole.STUDENT).first()
                if su:
                    if parent.linked_student_id is None: parent.linked_student_id = int(uid)
                    children.append(su.full_name)
    db.commit()
    log_action(db, admin_id, "admin", "Создал родителя", f"Логин:{username}, Дети:{', '.join(children) if children else 'нет'}")
    return {"message": "Родитель создан", "parent_id": parent.id, "children": children}


@router.get("/parents")
def list_parents(db: Session = Depends(get_db)):
    parents = db.query(User).filter(User.role == UserRole.PARENT).all()
    result = []
    for p in parents:
        children = []
        student = db.query(Student).filter(Student.user_id == p.linked_student_id).first()
        if student:
            su = db.query(User).filter(User.id == student.user_id).first()
            if su: children.append({"id": su.id, "name": su.full_name})
        result.append({"id": p.id, "username": p.username, "email": p.email, "full_name": p.full_name,
                       "children": children, "children_count": len(children)})
    return result


@router.delete("/users/{user_id}")
def remove_user(user_id: int, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user: raise HTTPException(status_code=404, detail="Пользователь не найден")
    db.delete(user)
    db.commit()
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Удалил пользователя", f"ID:{user_id}")
    return {"message": "Пользователь удалён"}


# ==================== USERS ====================

@router.get("/users", response_model=list[dict])
def list_users(db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    users = db.query(User).all()
    return [{"id": u.id, "username": u.username, "email": u.email, "full_name": u.full_name,
             "role": u.role.value if hasattr(u.role, 'value') else u.role, "linked_student_id": u.linked_student_id} for u in users]