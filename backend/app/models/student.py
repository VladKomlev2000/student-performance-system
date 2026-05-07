from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    student_card_number = Column(String(20), unique=True, nullable=False)  # Номер студенческого
    enrollment_date = Column(String(10), nullable=False)  # Дата зачисления YYYY-MM-DD

    user = relationship("User")
    group = relationship("Group", back_populates="students")
    grades = relationship("Grade", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")