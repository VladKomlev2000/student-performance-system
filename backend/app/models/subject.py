from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False)
    teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=False)
    group_id = Column(Integer, ForeignKey("groups.id"), nullable=False)
    semester = Column(Integer, nullable=False)  # 1 или 2
    hours = Column(Integer)  # Количество часов

    teacher = relationship("Teacher", back_populates="subjects")
    grades = relationship("Grade", back_populates="subject")
    attendance_records = relationship("Attendance", back_populates="subject")