from sqlalchemy import Column, String, DateTime, JSON
from sqlalchemy.sql import func
from app.models.base import Base

class Service(Base):
    __tablename__ = "services"
    id = Column(String, primary_key=True)
    name = Column(String, unique=True, nullable=False)
    owner = Column(String, nullable=True)
    selectors = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
