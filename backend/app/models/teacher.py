from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Teacher(Base):
    __tablename__ = "teachers"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    position = Column(String(100))  # Преподаваемый предмет

    user = relationship("User")
    subjects = relationship("Subject", back_populates="teacher")
    supervised_class = relationship("Class", back_populates="class_teacher", uselist=False)