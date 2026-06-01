from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Class(Base):
    __tablename__ = "classes"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)  # Например "11-А"
    grade_number = Column(Integer, nullable=False)  # Номер класса: 1-11
    grade_letter = Column(String(5), nullable=False)  # Буква класса: А, Б, В, Г
    class_teacher_id = Column(Integer, ForeignKey("teachers.id"), nullable=True)  # Классный руководитель

    students = relationship("Student", back_populates="class_ref")
    class_teacher = relationship("Teacher", back_populates="supervised_class")