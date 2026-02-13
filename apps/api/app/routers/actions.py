from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session
from sqlalchemy import select
from typing import List, Optional
from datetime import datetime
from app.core.db import get_db
from app.models.remediation_action import RemediationAction, ActionStatus

router = APIRouter(prefix="/actions", tags=["remediation"])


class ActionResponse(BaseModel):
    id: str
    finding_id: str
    action_type: str
    status: str
    title: str
    description: Optional[str]
    params: dict
    result: Optional[dict]
    error_message: Optional[str]
    proposed_at: datetime
    approved_at: Optional[datetime]
    approved_by: Optional[str]
    executed_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True


class ApproveActionRequest(BaseModel):
    approved_by: str = "system"


@router.get("/", response_model=List[ActionResponse])
def list_actions(
    status: Optional[str] = None,
    finding_id: Optional[str] = None,
    db: Session = Depends(get_db)
):
    """List all remediation actions with optional filters"""
    query = select(RemediationAction)
    
    if status:
        query = query.where(RemediationAction.status == status)
    if finding_id:
        query = query.where(RemediationAction.finding_id == finding_id)
    
    query = query.order_by(RemediationAction.proposed_at.desc())
    actions = db.execute(query).scalars().all()
    return actions


@router.get("/{action_id}", response_model=ActionResponse)
def get_action(action_id: str, db: Session = Depends(get_db)):
    """Get a specific remediation action"""
    action = db.get(RemediationAction, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    return action


@router.post("/{action_id}/approve", response_model=ActionResponse)
def approve_action(
    action_id: str,
    request: ApproveActionRequest,
    db: Session = Depends(get_db)
):
    """Approve a remediation action for execution"""
    action = db.get(RemediationAction, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if action.status != ActionStatus.PROPOSED:
        raise HTTPException(
            status_code=400,
            detail=f"Action cannot be approved (current status: {action.status})"
        )
    
    action.status = ActionStatus.APPROVED
    action.approved_at = datetime.now()
    action.approved_by = request.approved_by
    
    db.commit()
    db.refresh(action)
    
    # TODO: Trigger async execution via Celery
    
    return action


@router.post("/{action_id}/reject", response_model=ActionResponse)
def reject_action(
    action_id: str,
    request: ApproveActionRequest,
    db: Session = Depends(get_db)
):
    """Reject a remediation action"""
    action = db.get(RemediationAction, action_id)
    if not action:
        raise HTTPException(status_code=404, detail="Action not found")
    
    if action.status != ActionStatus.PROPOSED:
        raise HTTPException(
            status_code=400,
            detail=f"Action cannot be rejected (current status: {action.status})"
        )
    
    action.status = ActionStatus.REJECTED
    action.approved_by = request.approved_by
    
    db.commit()
    db.refresh(action)
    
    return action
