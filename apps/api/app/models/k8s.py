from sqlalchemy import Column, String, DateTime, Integer, JSON, Index
from sqlalchemy.sql import func
from app.models.base import Base

class K8sPodSnapshot(Base):
    __tablename__ = "k8s_pod_snapshots"
    id = Column(String, primary_key=True)
    cluster = Column(String, nullable=True)
    namespace = Column(String, nullable=False)
    pod = Column(String, nullable=False)
    node = Column(String, nullable=True)
    phase = Column(String, nullable=True)
    restart_count = Column(Integer, nullable=False, default=0)
    reason = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    raw = Column(JSON, nullable=False, default=dict)

Index("ix_k8s_pod_ns_pod", K8sPodSnapshot.namespace, K8sPodSnapshot.pod)

class K8sEvent(Base):
    __tablename__ = "k8s_events"
    id = Column(String, primary_key=True)
    cluster = Column(String, nullable=True)
    namespace = Column(String, nullable=False)
    name = Column(String, nullable=False)
    type = Column(String, nullable=True)
    reason = Column(String, nullable=True)
    message = Column(String, nullable=True)
    involved_kind = Column(String, nullable=True)
    involved_name = Column(String, nullable=True)
    first_timestamp = Column(DateTime(timezone=True), nullable=True)
    last_timestamp = Column(DateTime(timezone=True), nullable=True)
    count = Column(Integer, nullable=False, default=0)
    raw = Column(JSON, nullable=False, default=dict)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

Index("ix_k8s_events_ns_type", K8sEvent.namespace, K8sEvent.type)
