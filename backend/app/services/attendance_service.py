from sqlalchemy.orm import Session
from datetime import date, datetime
from ..models.attendance import Attendance
from ..models.student import Student
from ..models.user import UserRole


def mark_attendance(db: Session, student_id: int, subject_id: int,
                    teacher_id: int, status: str, lesson_date: date = None):
    """Отметить посещаемость"""
    if not lesson_date:
        lesson_date = date.today()

    # Проверяем, нет ли уже отметки за эту дату
    existing = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.subject_id == subject_id,
        Attendance.date == lesson_date
    ).first()

    if existing:
        # Обновляем статус
        existing.status = status
        db.commit()
        db.refresh(existing)
        return existing

    attendance = Attendance(
        student_id=student_id,
        subject_id=subject_id,
        date=lesson_date,
        status=status,
        marked_by=teacher_id
    )
    db.add(attendance)
    db.commit()
    db.refresh(attendance)
    return attendance


def get_student_attendance(db: Session, student_id: int, subject_id: int = None):
    """Получить посещаемость студента"""
    query = db.query(Attendance).filter(Attendance.student_id == student_id)
    if subject_id:
        query = query.filter(Attendance.subject_id == subject_id)
    return query.order_by(Attendance.date.desc()).all()


def get_group_attendance(db: Session, group_id: int, subject_id: int, lesson_date: date = None):
    """Получить посещаемость группы по предмету на дату"""
    if not lesson_date:
        lesson_date = date.today()

    return db.query(Attendance).join(Student).filter(
        Student.group_id == group_id,
        Attendance.subject_id == subject_id,
        Attendance.date == lesson_date
    ).all()


def get_attendance_stats(db: Session, student_id: int, subject_id: int):
    """Статистика посещаемости: сколько пропусков, опозданий и т.д."""
    records = db.query(Attendance).filter(
        Attendance.student_id == student_id,
        Attendance.subject_id == subject_id
    ).all()

    total = len(records)
    if total == 0:
        return {"total": 0, "present": 0, "absent": 0, "late": 0, "excused": 0, "attendance_rate": 0}

    stats = {"total": total}
    for status in ["present", "absent", "late", "excused"]:
        count = sum(1 for r in records if r.status == status)
        stats[status] = count

    stats["attendance_rate"] = round((stats["present"] + stats["late"]) / total * 100, 1)
    return stats


def get_attendance_for_parent(db: Session, parent_user_id: int, subject_id: int = None):
    """
    Получить посещаемость студента, к которому привязан родитель.
    """
    from ..models.user import User
    from ..models.student import Student

    parent = db.query(User).filter(User.id == parent_user_id, User.role == UserRole.PARENT).first()
    if not parent or not parent.linked_student_id:
        return []

    student = db.query(Student).filter(Student.user_id == parent.linked_student_id).first()
    if not student:
        return []

    return get_student_attendance(db, student.id, subject_id)