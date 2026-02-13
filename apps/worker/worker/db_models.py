from sqlalchemy.orm import DeclarativeBase
from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, UniqueConstraint, ForeignKey, Enum
from sqlalchemy.sql import func
import enum

class Base(DeclarativeBase):
    pass

class ActionStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"

class JiraIssue(Base):
    __tablename__ = "jira_issues"
    key = Column(String, primary_key=True)
    issue_id = Column(String, nullable=False)
    project_key = Column(String, nullable=False)
    issue_type = Column(String, nullable=True)
    status = Column(String, nullable=True)
    status_category = Column(String, nullable=True)
    priority = Column(String, nullable=True)
    summary = Column(Text, nullable=True)
    assignee = Column(String, nullable=True)
    reporter = Column(String, nullable=True)
    created_at_jira = Column(DateTime(timezone=True), nullable=True)
    updated_at_jira = Column(DateTime(timezone=True), nullable=True)
    raw = Column(JSON, nullable=False, default=dict)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

class JiraChangelogEvent(Base):
    __tablename__ = "jira_changelog_events"
    id = Column(String, primary_key=True)
    issue_key = Column(String, nullable=False)
    history_id = Column(String, nullable=False)
    author = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), nullable=True)
    field = Column(String, nullable=True)
    from_string = Column(String, nullable=True)
    to_string = Column(String, nullable=True)
    raw = Column(JSON, nullable=False, default=dict)
    ingested_at = Column(DateTime(timezone=True), server_default=func.now())

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

class Finding(Base):
    __tablename__ = "findings"
    __table_args__ = (UniqueConstraint("type", "fingerprint", name="uq_findings_type_fingerprint"),)

    id = Column(String, primary_key=True)
    type = Column(String, nullable=False)
    fingerprint = Column(String, nullable=False)
    severity = Column(Integer, nullable=False)
    confidence = Column(Integer, nullable=False)
    service_id = Column(String, nullable=True)
    title = Column(String, nullable=False)
    summary = Column(Text, nullable=True)
    evidence = Column(JSON, nullable=False, default=dict)
    remediation = Column(JSON, nullable=False, default=dict)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    id = Column(String, primary_key=True)
    finding_id = Column(String, ForeignKey("findings.id"), nullable=False)
    action_type = Column(String, nullable=False)
    status = Column(Enum(ActionStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=ActionStatus.PROPOSED)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    params = Column(JSON, nullable=False, default=dict)
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    proposed_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String, nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)

