from app.database import SessionLocal
from app.models.grade import Grade
from app.models.student import Student
from app.models.user import User
from app.models.subject import Subject

db = SessionLocal()

students = db.query(Student).filter(Student.group_id == 1).all()

all_grades = []
for student in students:
    user = db.query(User).filter(User.id == student.user_id).first()
    query = db.query(Grade).filter(Grade.student_id == student.id, Grade.subject_id == 3)
    for g in query.all():
        item = {
            'value': g.value,
            'type': g.type,
            'date': g.date,
            'comment': g.comment,
            'student_name': user.full_name if user else '-',
            'subject_name': 'Информатика'
        }
        all_grades.append(item)
        print(f"Grade: value={g.value}, type={g.type}, student={item['student_name']}")

print(f"\nTotal: {len(all_grades)}")

from app.services.export_service import export_grades_to_excel
excel = export_grades_to_excel(all_grades, 'Test')
print(f"Excel size: {len(excel.getvalue())} bytes")

db.close()