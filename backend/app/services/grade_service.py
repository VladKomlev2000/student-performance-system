from sqlalchemy.orm import Session
from sqlalchemy import func
from ..models.grade import Grade
from ..models.student import Student
from ..models.subject import Subject
from ..models.user import UserRole


def get_student_grades(db: Session, student_id: int, subject_id: int = None):
    """Получить все оценки студента (опционально по предмету)"""
    query = db.query(Grade).filter(Grade.student_id == student_id)
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    return query.order_by(Grade.date.desc()).all()


def get_group_grades(db: Session, group_id: int, subject_id: int):
    """Получить оценки всей группы по предмету"""
    return db.query(Grade).join(Student).filter(
        Student.group_id == group_id,
        Grade.subject_id == subject_id
    ).order_by(Grade.date.desc()).all()


def get_average_grade(db: Session, student_id: int, subject_id: int = None):
    """Рассчитать средний балл студента"""
    query = db.query(func.avg(Grade.value)).filter(Grade.student_id == student_id)
    if subject_id:
        query = query.filter(Grade.subject_id == subject_id)
    result = query.scalar()
    return round(float(result), 2) if result else 0.0


def add_grade(db: Session, student_id: int, subject_id: int, teacher_id: int,
              value: int, grade_type: str, comment: str = None):
    """Добавить оценку студенту"""
    grade = Grade(
        student_id=student_id,
        subject_id=subject_id,
        teacher_id=teacher_id,
        value=value,
        type=grade_type,
        comment=comment
    )
    db.add(grade)
    db.commit()
    db.refresh(grade)
    return grade


def update_grade(db: Session, grade_id: int, value: int = None, comment: str = None):
    """Обновить оценку"""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if not grade:
        return None
    if value:
        grade.value = value
    if comment is not None:
        grade.comment = comment
    db.commit()
    db.refresh(grade)
    return grade


def delete_grade(db: Session, grade_id: int):
    """Удалить оценку"""
    grade = db.query(Grade).filter(Grade.id == grade_id).first()
    if grade:
        db.delete(grade)
        db.commit()
        return True
    return False


def get_grades_for_parent(db: Session, parent_user_id: int, subject_id: int = None):
    """
    Получить оценки студента, к которому привязан родитель.
    parent_user_id — это id пользователя с ролью parent.
    """
    from ..models.user import User

    # Находим родителя и его linked_student_id
    parent = db.query(User).filter(User.id == parent_user_id, User.role == UserRole.PARENT).first()
    if not parent or not parent.linked_student_id:
        return []

    # Получаем student_id по user_id
    from ..models.student import Student
    student = db.query(Student).filter(Student.user_id == parent.linked_student_id).first()
    if not student:
        return []

    # Возвращаем оценки этого студента
    return get_student_grades(db, student.id, subject_id)