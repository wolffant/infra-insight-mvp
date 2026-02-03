from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, UniqueConstraint
from sqlalchemy.sql import func
from app.models.base import Base

class Finding(Base):
    __tablename__ = "findings"
    __table_args__ = (UniqueConstraint("type", "fingerprint", name="uq_findings_type_fingerprint"),)

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    fingerprint = Column(String, nullable=False)
    severity = Column(Integer, nullable=False)     # 0..3 (P0..P3)
    confidence = Column(Integer, nullable=False)   # 0..100
    service_id = Column(String, nullable=True)

    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)

    evidence = Column(JSON, nullable=False, default=dict)
    remediation = Column(JSON, nullable=False, default=dict)

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
