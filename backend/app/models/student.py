from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Student(Base):
    __tablename__ = "students"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    class_id = Column(Integer, ForeignKey("classes.id"), nullable=False)

    user = relationship("User")
    class_ref = relationship("Class", back_populates="students")
    grades = relationship("Grade", back_populates="student")
    attendance_records = relationship("Attendance", back_populates="student")