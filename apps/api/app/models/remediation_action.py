from sqlalchemy import Column, String, Integer, DateTime, JSON, Text, ForeignKey, Enum
from sqlalchemy.sql import func
import enum
from app.models.base import Base


class ActionStatus(str, enum.Enum):
    PROPOSED = "proposed"
    APPROVED = "approved"
    EXECUTING = "executing"
    COMPLETED = "completed"
    FAILED = "failed"
    REJECTED = "rejected"


class RemediationAction(Base):
    __tablename__ = "remediation_actions"

    id = Column(String, primary_key=True)
    finding_id = Column(String, ForeignKey("findings.id"), nullable=False)
    
    action_type = Column(String, nullable=False)  # "close_jira_ticket", "restart_pod", etc.
    status = Column(Enum(ActionStatus, values_callable=lambda obj: [e.value for e in obj]), nullable=False, default=ActionStatus.PROPOSED)
    
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    
    # Action parameters (what to execute)
    params = Column(JSON, nullable=False, default=dict)
    
    # Execution results
    result = Column(JSON, nullable=True)
    error_message = Column(Text, nullable=True)
    
    # Audit trail
    proposed_at = Column(DateTime(timezone=True), server_default=func.now())
    approved_at = Column(DateTime(timezone=True), nullable=True)
    approved_by = Column(String, nullable=True)
    executed_at = Column(DateTime(timezone=True), nullable=True)
    completed_at = Column(DateTime(timezone=True), nullable=True)
