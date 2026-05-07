from sqlalchemy import Column, Integer, String, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from ..database import Base
from datetime import datetime


class Grade(Base):
    __tablename__ = "grades"

    id = Column(Integer, primary_key=True, index=True)
    student_id = Column(Integer, ForeignKey("students.id"), nullable=False)
    subject_id = Column(Integer, ForeignKey("subjects.id"), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    value = Column(Integer, nullable=False)  # Оценка 2-5
    type = Column(String(20), nullable=False)  # "exam", "test", "coursework", "practice"
    date = Column(DateTime, default=datetime.utcnow)
    comment = Column(String(255))  # Комментарий преподавателя

    student = relationship("Student", back_populates="grades")
    subject = relationship("Subject", back_populates="grades")