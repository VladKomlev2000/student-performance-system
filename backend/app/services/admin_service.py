from sqlalchemy.orm import Session
from ..models.user import User, UserRole
from ..models.student import Student
from ..models.teacher import Teacher
from ..models.group import Group
from ..models.subject import Subject
from ..utils.security import hash_password


# ========== ГРУППЫ ==========

def create_group(db: Session, name: str, course: int, faculty: str):
    """Создать учебную группу"""
    group = Group(name=name, course=course, faculty=faculty)
    db.add(group)
    db.commit()
    db.refresh(group)
    return group


def get_all_groups(db: Session):
    """Получить все группы"""
    return db.query(Group).all()


def get_group(db: Session, group_id: int):
    """Получить группу по ID"""
    return db.query(Group).filter(Group.id == group_id).first()


def delete_group(db: Session, group_id: int):
    """Удалить группу"""
    group = db.query(Group).filter(Group.id == group_id).first()
    if group:
        db.delete(group)
        db.commit()
        return True
    return False


# ========== СТУДЕНТЫ ==========

def create_student(db: Session, username: str, email: str, password: str,
                   full_name: str, group_id: int, student_card: str,
                   enrollment_date: str, parent_username: str = None):
    """Создать студента и опционально привязать родителя"""

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
        group_id=group_id,
        student_card_number=student_card,
        enrollment_date=enrollment_date
    )
    db.add(student)
    db.flush()

    # Если указан родитель — привязываем
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
    """Получить всех студентов с данными пользователей и групп"""
    return db.query(Student).join(User).join(Group).all()


def get_students_by_group(db: Session, group_id: int):
    """Получить студентов по группе"""
    return db.query(Student).filter(Student.group_id == group_id).join(User).all()


def delete_student(db: Session, student_id: int):
    """Удалить студента и его пользователя"""
    student = db.query(Student).filter(Student.id == student_id).first()
    if student:
        user_id = student.user_id
        db.delete(student)
        db.query(User).filter(User.id == user_id).delete()
        db.commit()
        return True
    return False


# ========== ПРЕПОДАВАТЕЛИ ==========

def create_teacher(db: Session, username: str, email: str, password: str,
                   full_name: str, department: str, position: str):
    """Создать преподавателя"""

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
        department=department,
        position=position
    )
    db.add(teacher)
    db.commit()
    db.refresh(teacher)
    return teacher


def get_all_teachers(db: Session):
    """Получить всех преподавателей"""
    return db.query(Teacher).join(User).all()


def delete_teacher(db: Session, teacher_id: int):
    """Удалить преподавателя"""
    teacher = db.query(Teacher).filter(Teacher.id == teacher_id).first()
    if teacher:
        user_id = teacher.user_id
        db.delete(teacher)
        db.query(User).filter(User.id == user_id).delete()
        db.commit()
        return True
    return False


# ========== ПРЕДМЕТЫ ==========

def create_subject(db: Session, name: str, teacher_id: int, group_id: int,
                   semester: int, hours: int):
    """Создать предмет"""
    subject = Subject(
        name=name,
        teacher_id=teacher_id,
        group_id=group_id,
        semester=semester,
        hours=hours
    )
    db.add(subject)
    db.commit()
    db.refresh(subject)
    return subject


def get_all_subjects(db: Session):
    """Получить все предметы"""
    return db.query(Subject).join(Teacher).join(Group).all()


def get_subjects_by_group(db: Session, group_id: int):
    """Получить предметы по группе"""
    return db.query(Subject).filter(Subject.group_id == group_id).all()


def delete_subject(db: Session, subject_id: int):
    """Удалить предмет"""
    subject = db.query(Subject).filter(Subject.id == subject_id).first()
    if subject:
        db.delete(subject)
        db.commit()
        return True
    return False