from sqlalchemy import Column, Integer, String, DateTime
from ..database import Base
from datetime import datetime


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    username = Column(String(50), nullable=False)
    action = Column(String(255), nullable=False)
    details = Column(String(500))
    created_at = Column(DateTime, default=datetime.utcnow)