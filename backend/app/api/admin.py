from ..models.user import User, UserRole
from ..models.student import Student
from fastapi import APIRouter, Depends, HTTPException, Header, UploadFile, File
from sqlalchemy.orm import Session
from ..database import get_db
from ..services.admin_service import (
    create_class, get_all_classes, delete_class,
    create_student, get_all_students, get_students_by_class, delete_student,
    create_teacher, get_all_teachers, delete_teacher,
    create_subject, get_all_subjects, get_subjects_by_class, delete_subject
)
from ..schemas.admin import (
    ClassCreate, ClassResponse,
    StudentCreate, StudentResponse,
    TeacherCreate, TeacherResponse,
    SubjectCreate, SubjectResponse
)
from ..models.group import Class
from ..models.teacher import Teacher
from ..utils.security import verify_token
from ..services.import_service import (
    import_students_from_excel, import_classes_from_excel,
    import_teachers_from_excel, import_subjects_from_excel,
    import_parents_from_excel
)

router = APIRouter()


def check_admin(authorization: str = Header(None)):
    if not authorization or not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Требуется авторизация")
    token = authorization.replace("Bearer ", "")
    payload = verify_token(token)
    if not payload or payload.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Доступно только администратору")
    return int(payload["sub"])


# ==================== ИМПОРТ ИЗ EXCEL ====================

@router.post("/import/students")
async def import_students(file: UploadFile = File(...), db: Session = Depends(get_db),
                          admin_id: int = Depends(check_admin)):
    """Импорт учеников из Excel (.xlsx)."""
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Поддерживаются только файлы .xlsx")

    content = await file.read()
    result = import_students_from_excel(db, content)

    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Импортировал учеников",
               f"Создано: {result['created']}, пропущено: {result['skipped']}")

    return result


@router.post("/import/classes")
async def import_classes(file: UploadFile = File(...), db: Session = Depends(get_db),
                         admin_id: int = Depends(check_admin)):
    """Импорт классов из Excel (.xlsx)."""
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Поддерживаются только файлы .xlsx")

    content = await file.read()
    result = import_classes_from_excel(db, content)

    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Импортировал классы",
               f"Создано: {result['created']}, пропущено: {result['skipped']}")

    return result


@router.post("/import/teachers")
async def import_teachers(file: UploadFile = File(...), db: Session = Depends(get_db),
                          admin_id: int = Depends(check_admin)):
    """Импорт учителей из Excel (.xlsx)."""
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Поддерживаются только файлы .xlsx")

    content = await file.read()
    result = import_teachers_from_excel(db, content)

    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Импортировал учителей",
               f"Создано: {result['created']}, пропущено: {result['skipped']}")

    return result


@router.post("/import/subjects")
async def import_subjects(file: UploadFile = File(...), db: Session = Depends(get_db),
                          admin_id: int = Depends(check_admin)):
    """Импорт предметов из Excel (.xlsx)."""
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Поддерживаются только файлы .xlsx")

    content = await file.read()
    result = import_subjects_from_excel(db, content)

    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Импортировал предметы",
               f"Создано: {result['created']}, пропущено: {result['skipped']}")

    return result


@router.post("/import/parents")
async def import_parents(file: UploadFile = File(...), db: Session = Depends(get_db),
                         admin_id: int = Depends(check_admin)):
    """Импорт родителей из Excel (.xlsx)."""
    if not file.filename.endswith('.xlsx'):
        raise HTTPException(status_code=400, detail="Поддерживаются только файлы .xlsx")

    content = await file.read()
    result = import_parents_from_excel(db, content)

    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Импортировал родителей",
               f"Создано: {result['created']}, пропущено: {result['skipped']}")

    return result


# ==================== CLASSES ====================

@router.post("/groups", response_model=ClassResponse, status_code=201)
def add_class(class_data: ClassCreate, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    cls = create_class(db, class_data.name, class_data.grade_number,
                       class_data.grade_letter, class_data.class_teacher_id)
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Создал класс",
               f"Название:{class_data.name}, Класс:{class_data.grade_number}{class_data.grade_letter}")
    return cls


@router.get("/groups", response_model=list[dict])
def list_classes(db: Session = Depends(get_db)):
    classes = get_all_classes(db)
    result = []
    for c in classes:
        teacher_name = None
        if c.class_teacher_id:
            teacher = db.query(Teacher).filter(Teacher.id == c.class_teacher_id).first()
            if teacher:
                teacher_user = db.query(User).filter(User.id == teacher.user_id).first()
                teacher_name = teacher_user.full_name if teacher_user else None
        result.append({
            "id": c.id,
            "name": c.name,
            "grade_number": c.grade_number,
            "grade_letter": c.grade_letter,
            "class_teacher_id": c.class_teacher_id,
            "class_teacher_name": teacher_name
        })
    return result


@router.delete("/groups/{class_id}")
def remove_class(class_id: int, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    if delete_class(db, class_id):
        from ..services.audit_service import log_action
        log_action(db, admin_id, "admin", "Удалил класс", f"ID:{class_id}")
        return {"message": "Класс удалён"}
    raise HTTPException(status_code=404, detail="Класс не найден")


# ==================== STUDENTS ====================

@router.post("/students", response_model=StudentResponse, status_code=201)
def add_student(student_data: StudentCreate, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    student = create_student(db=db, username=student_data.username, email=student_data.email,
                             password=student_data.password, full_name=student_data.full_name,
                             class_id=student_data.class_id)
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Создал ученика", f"Логин:{student_data.username}, ФИО:{student_data.full_name}")
    return student


@router.get("/students", response_model=list[dict])
def list_students(class_id: int = None, db: Session = Depends(get_db)):
    if class_id:
        students = get_students_by_class(db, class_id)
    else:
        students = get_all_students(db)
    result = []
    for s in students:
        result.append({"id": s.id, "user_id": s.user_id, "class_id": s.class_id,
                       "username": s.user.username, "email": s.user.email, "full_name": s.user.full_name,
                       "class_name": s.class_ref.name if s.class_ref else "-"})
    return result


@router.delete("/students/{student_id}")
def remove_student(student_id: int, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    if delete_student(db, student_id):
        from ..services.audit_service import log_action
        log_action(db, admin_id, "admin", "Удалил ученика", f"ID:{student_id}")
        return {"message": "Ученик удалён"}
    raise HTTPException(status_code=404, detail="Ученик не найден")


# ==================== TEACHERS ====================

@router.post("/teachers", response_model=TeacherResponse, status_code=201)
def add_teacher(teacher_data: TeacherCreate, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    teacher = create_teacher(db=db, username=teacher_data.username, email=teacher_data.email,
                             password=teacher_data.password, full_name=teacher_data.full_name,
                             position=teacher_data.position)
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Создал учителя", f"Логин:{teacher_data.username}, ФИО:{teacher_data.full_name}")
    return teacher


@router.get("/teachers", response_model=list[dict])
def list_teachers(db: Session = Depends(get_db)):
    teachers = get_all_teachers(db)
    result = []
    for t in teachers:
        result.append({"id": t.id, "user_id": t.user_id, "position": t.position,
                       "username": t.user.username, "email": t.user.email, "full_name": t.user.full_name})
    return result


@router.delete("/teachers/{teacher_id}")
def remove_teacher(teacher_id: int, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    if delete_teacher(db, teacher_id):
        from ..services.audit_service import log_action
        log_action(db, admin_id, "admin", "Удалил учителя", f"ID:{teacher_id}")
        return {"message": "Учитель удалён"}
    raise HTTPException(status_code=404, detail="Учитель не найден")


# ==================== SUBJECTS ====================

@router.post("/subjects", response_model=SubjectResponse, status_code=201)
def add_subject(subject_data: SubjectCreate, db: Session = Depends(get_db), admin_id: int = Depends(check_admin)):
    subject = create_subject(db=db, name=subject_data.name, teacher_id=subject_data.teacher_id,
                             class_id=subject_data.class_id, quarter=subject_data.quarter, hours=subject_data.hours)
    from ..services.audit_service import log_action
    log_action(db, admin_id, "admin", "Создал предмет", f"Название:{subject_data.name}")
    return subject


@router.get("/subjects", response_model=list[dict])
def list_subjects(class_id: int = None, db: Session = Depends(get_db)):
    if class_id:
        subjects = get_subjects_by_class(db, class_id)
    else:
        subjects = get_all_subjects(db)
    result = []
    for subj in subjects:
        teacher_user = db.query(User).filter(User.id == subj.teacher.user_id).first()
        cls = db.query(Class).filter(Class.id == subj.class_id).first()
        result.append({"id": subj.id, "name": subj.name, "teacher_id": subj.teacher_id, "class_id": subj.class_id,
                       "quarter": subj.quarter, "hours": subj.hours,
                       "teacher_name": teacher_user.full_name if teacher_user else "-",
                       "class_name": cls.name if cls else "-"})
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
    log_action(db, admin_id, "admin", "Создал родителя",
               f"Логин:{username}, Дети:{', '.join(children) if children else 'нет'}")
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
             "role": u.role.value if hasattr(u.role, 'value') else u.role, "linked_student_id": u.linked_student_id} for
            u in users]