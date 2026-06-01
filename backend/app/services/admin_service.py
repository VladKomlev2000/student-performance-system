from sqlalchemy.orm import Session
from ..models.user import User, UserRole
from ..models.student import Student
from ..models.teacher import Teacher
from ..models.group import Class
from ..models.subject import Subject
from ..utils.security import hash_password


# ========== КЛАССЫ ==========

def create_class(db: Session, name: str, grade_number: int, grade_letter: str, class_teacher_id: int = None):
    """Создать класс"""
    cls = Class(
        name=name,
        grade_number=grade_number,
        grade_letter=grade_letter,
        class_teacher_id=class_teacher_id
    )
    db.add(cls)
    db.commit()
    db.refresh(cls)
    return cls


def get_all_classes(db: Session):
    """Получить все классы"""
    return db.query(Class).all()


def get_class(db: Session, class_id: int):
    """Получить класс по ID"""
    return db.query(Class).filter(Class.id == class_id).first()


def delete_class(db: Session, class_id: int):
    """Удалить класс"""
    cls = db.query(Class).filter(Class.id == class_id).first()
    if cls:
        db.delete(cls)
        db.commit()
        return True
    return False


# ========== УЧЕНИКИ ==========

def create_student(db: Session, username: str, email: str, password: str,
                   full_name: str, class_id: int, parent_username: str = None):
    """Создать ученика и опционально привязать родителя"""

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=UserRole.STUDENT
    )
    db.add(user)
    db.flush()

    student = Student(
        user_id=user.id,
        class_id=class_id
    )
    db.add(student)
    db.flush()

    if parent_username:
        parent = db.query(User).filter(
            User.username == parent_username,
            User.role == UserRole.PARENT
        ).first()
        if parent:
            parent.linked_student_id = user.id
            db.commit()

    db.commit()
    db.refresh(student)
    return student


def get_all_students(db: Session):
    """Получить всех учеников с данными пользователей и классов"""
    return db.query(Student).join(User).join(Class).all()


def get_students_by_class(db: Session, class_id: int):
    """Получить учеников по классу"""
    return db.query(Student).filter(Student.class_id == class_id).join(User).all()


def delete_student(db: Session, student_id: int):
    """Удалить ученика и его пользователя"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        user_id = student.user_id
        db.delete(student)
        db.query(User).filter(User.id == user_id).delete()
        db.commit()
        return True
    return False


# ========== УЧИТЕЛЯ ==========

def create_teacher(db: Session, username: str, email: str, password: str,
                   full_name: str, position: str = None):
    """Создать учителя"""

    user = User(
        username=username,
        email=email,
        hashed_password=hash_password(password),
        full_name=full_name,
        role=UserRole.TEACHER
    )
    db.add(user)
    db.flush()

    teacher = Teacher(
        user_id=user.id,
        position=position
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


def get_all_teachers(db: Session):
    """Получить всех учителей"""
    return db.query(Teacher).join(User).all()


def delete_teacher(db: Session, teacher_id: int):
    """Удалить учителя"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher:
        user_id = teacher.user_id
        db.delete(teacher)
        db.query(User).filter(User.id == user_id).delete()
        db.commit()
        return True
    return False


# ========== ПРЕДМЕТЫ ==========

def create_subject(db: Session, name: str, teacher_id: int, class_id: int,
                   quarter: int, hours: int):
    """Создать предмет"""
    subject = Subject(
        name=name,
        teacher_id=teacher_id,
        class_id=class_id,
        quarter=quarter,
        hours=hours
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def get_all_subjects(db: Session):
    """Получить все предметы"""
    return db.query(Subject).join(Teacher).join(Class).all()


def get_subjects_by_class(db: Session, class_id: int):
    """Получить предметы по классу"""
    return db.query(Subject).filter(Subject.class_id == class_id).all()


def delete_subject(db: Session, subject_id: int):
    """Удалить предмет"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject:
        db.delete(subject)
        db.commit()
        return True
    return False