from sqlalchemy import Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from ..database import Base


class Group(Base):
    __tablename__ = "groups"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(50), nullable=False, unique=True)  # Например "ИС-301"
    course = Column(Integer, nullable=False)  # 1-5 курс
    faculty = Column(String(100), nullable=False)

    students = relationship("Student", back_populates="group")