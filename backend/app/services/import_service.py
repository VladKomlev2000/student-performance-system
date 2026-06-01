from io import BytesIO
from sqlalchemy.orm import Session
from openpyxl import load_workbook
from ..models.user import User, UserRole
from ..models.student import Student
from ..models.teacher import Teacher
from ..models.group import Class
from ..models.subject import Subject
from ..utils.security import hash_password


def import_students_from_excel(db: Session, file_bytes: bytes) -> dict:
    """Импорт учеников из Excel-файла.
    Формат: ФИО | Логин | Email | Пароль | Класс"""
    wb = load_workbook(BytesIO(file_bytes))
    ws = wb.active

    created = 0
    skipped = 0
    errors = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue

        try:
            full_name = str(row[0]).strip()
            username = str(row[1]).strip() if len(row) > 1 and row[1] else full_name.split()[0].lower()
            email = str(row[2]).strip() if len(row) > 2 and row[2] else f"{username}@school.ru"
            password = str(row[3]).strip() if len(row) > 3 and row[3] else "123456"
            class_name = str(row[4]).strip() if len(row) > 4 and row[4] else None

            if db.query(User).filter(User.username == username).first():
                skipped += 1
                errors.append(f"Пропущен: {full_name} (логин {username} занят)")
                continue

            class_id = None
            if class_name:
                cls = db.query(Class).filter(Class.name == class_name).first()
                if cls:
                    class_id = cls.id
                else:
                    skipped += 1
                    errors.append(f"Пропущен: {full_name} (класс {class_name} не найден)")
                    continue

            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
                role=UserRole.STUDENT
            )
            db.add(user)
            db.flush()

            student = Student(user_id=user.id, class_id=class_id)
            db.add(student)
            created += 1

        except Exception as e:
            errors.append(f"Ошибка в строке: {str(e)}")
            continue

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors[:10]}


def import_classes_from_excel(db: Session, file_bytes: bytes) -> dict:
    """Импорт классов из Excel-файла.
    Формат: Название | Номер | Буква"""
    wb = load_workbook(BytesIO(file_bytes))
    ws = wb.active

    created = 0
    skipped = 0
    errors = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue

        try:
            name = str(row[0]).strip()
            grade_number = int(row[1]) if len(row) > 1 and row[1] else 1
            grade_letter = str(row[2]).strip() if len(row) > 2 and row[2] else "А"

            if db.query(Class).filter(Class.name == name).first():
                skipped += 1
                errors.append(f"Пропущен: {name} (уже существует)")
                continue

            cls = Class(name=name, grade_number=grade_number, grade_letter=grade_letter)
            db.add(cls)
            created += 1

        except Exception as e:
            errors.append(f"Ошибка в строке: {str(e)}")
            continue

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors[:10]}


def import_teachers_from_excel(db: Session, file_bytes: bytes) -> dict:
    """Импорт учителей из Excel-файла.
    Формат: ФИО | Логин | Email | Пароль | Предмет"""
    wb = load_workbook(BytesIO(file_bytes))
    ws = wb.active

    created = 0
    skipped = 0
    errors = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue

        try:
            full_name = str(row[0]).strip()
            username = str(row[1]).strip() if len(row) > 1 and row[1] else full_name.split()[0].lower()
            email = str(row[2]).strip() if len(row) > 2 and row[2] else f"{username}@school.ru"
            password = str(row[3]).strip() if len(row) > 3 and row[3] else "123456"
            position = str(row[4]).strip() if len(row) > 4 and row[4] else None

            if db.query(User).filter(User.username == username).first():
                skipped += 1
                errors.append(f"Пропущен: {full_name} (логин {username} занят)")
                continue

            user = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
                role=UserRole.TEACHER
            )
            db.add(user)
            db.flush()

            teacher = Teacher(user_id=user.id, position=position)
            db.add(teacher)
            created += 1

        except Exception as e:
            errors.append(f"Ошибка в строке с {full_name if full_name else '?'}: {str(e)}")
            continue

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors[:10]}


def import_subjects_from_excel(db: Session, file_bytes: bytes) -> dict:
    """Импорт предметов из Excel-файла.
    Формат: Название | ФИО учителя | Класс | Четверть | Часы"""
    wb = load_workbook(BytesIO(file_bytes))
    ws = wb.active

    created = 0
    skipped = 0
    errors = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue

        try:
            name = str(row[0]).strip()
            teacher_name = str(row[1]).strip() if len(row) > 1 and row[1] else None
            class_name = str(row[2]).strip() if len(row) > 2 and row[2] else None
            quarter = int(row[3]) if len(row) > 3 and row[3] else 1
            hours = int(row[4]) if len(row) > 4 and row[4] else 68

            # Ищем учителя по ФИО
            teacher_id = None
            if teacher_name:
                teacher_user = db.query(User).filter(
                    User.full_name.ilike(f"%{teacher_name}%"),
                    User.role == UserRole.TEACHER
                ).first()
                if teacher_user:
                    teacher = db.query(Teacher).filter(Teacher.user_id == teacher_user.id).first()
                    if teacher:
                        teacher_id = teacher.id

            if not teacher_id:
                skipped += 1
                errors.append(f"Пропущен: {name} (учитель '{teacher_name}' не найден)")
                continue

            # Ищем класс
            class_id = None
            if class_name:
                cls = db.query(Class).filter(Class.name == class_name).first()
                if cls:
                    class_id = cls.id
                else:
                    skipped += 1
                    errors.append(f"Пропущен: {name} (класс '{class_name}' не найден)")
                    continue

            # Проверяем дубликат
            existing = db.query(Subject).filter(
                Subject.name == name,
                Subject.teacher_id == teacher_id,
                Subject.class_id == class_id,
                Subject.quarter == quarter
            ).first()
            if existing:
                skipped += 1
                errors.append(f"Пропущен: {name} для класса {class_name} (уже существует)")
                continue

            subject = Subject(
                name=name,
                teacher_id=teacher_id,
                class_id=class_id,
                quarter=quarter,
                hours=hours
            )
            db.add(subject)
            created += 1

        except Exception as e:
            errors.append(f"Ошибка в строке с {name if name else '?'}: {str(e)}")
            continue

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors[:10]}


def import_parents_from_excel(db: Session, file_bytes: bytes) -> dict:
    """Импорт родителей из Excel-файла.
    Формат: ФИО | Логин | Email | Пароль | ФИО ученика"""
    wb = load_workbook(BytesIO(file_bytes))
    ws = wb.active

    created = 0
    skipped = 0
    errors = []

    for row in ws.iter_rows(min_row=2, values_only=True):
        if not row or not row[0]:
            continue

        try:
            full_name = str(row[0]).strip()
            username = str(row[1]).strip() if len(row) > 1 and row[1] else full_name.split()[0].lower()
            email = str(row[2]).strip() if len(row) > 2 and row[2] else f"{username}@school.ru"
            password = str(row[3]).strip() if len(row) > 3 and row[3] else "123456"
            student_name = str(row[4]).strip() if len(row) > 4 and row[4] else None

            if db.query(User).filter(User.username == username).first():
                skipped += 1
                errors.append(f"Пропущен: {full_name} (логин {username} занят)")
                continue

            # Ищем ученика по ФИО
            linked_student_id = None
            if student_name:
                student_user = db.query(User).filter(
                    User.full_name.ilike(f"%{student_name}%"),
                    User.role == UserRole.STUDENT
                ).first()
                if student_user:
                    linked_student_id = student_user.id
                else:
                    skipped += 1
                    errors.append(f"Пропущен: {full_name} (ученик '{student_name}' не найден)")
                    continue

            parent = User(
                username=username,
                email=email,
                hashed_password=hash_password(password),
                full_name=full_name,
                role=UserRole.PARENT,
                linked_student_id=linked_student_id
            )
            db.add(parent)
            created += 1

        except Exception as e:
            errors.append(f"Ошибка в строке с {full_name if full_name else '?'}: {str(e)}")
            continue

    db.commit()
    return {"created": created, "skipped": skipped, "errors": errors[:10]}