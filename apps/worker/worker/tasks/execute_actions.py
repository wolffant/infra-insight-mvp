"""
Worker task to execute approved remediation actions
"""
from worker.celery_app import celery_app
from worker.core.db import SessionLocal
from worker.db_models import RemediationAction, ActionStatus
from worker.core.config import settings
from worker.executors import EXECUTOR_REGISTRY, CloseJiraTicketExecutor, RestartPodExecutor
from datetime import datetime
import logging

logger = logging.getLogger(__name__)


async def _execute_action(action: RemediationAction) -> dict:
    """Execute a single remediation action"""
    
    # Get executor
    executor_class = EXECUTOR_REGISTRY.get(action.action_type)
    if not executor_class:
        raise ValueError(f"Unknown action type: {action.action_type}")
    
    # Initialize executor with appropriate config
    if action.action_type == "close_jira_tickets":
        executor = executor_class(
            jira_base_url=settings.JIRA_BASE_URL,
            jira_email=settings.JIRA_EMAIL,
            jira_api_token=settings.JIRA_API_TOKEN
        )
    elif action.action_type in ["restart_pods", "scale_deployment"]:
        # Initialize K8s client
        from worker.connectors.k8s import get_k8s_client
        k8s_client = get_k8s_client()
        if not k8s_client:
            raise ValueError("Kubernetes client not available")
        executor = executor_class(k8s_client)
    else:
        raise ValueError(f"Unsupported action type: {action.action_type}")
    
    # Execute action
    result = await executor.execute(action.params)
    return result


@celery_app.task
def execute_approved_actions():
    """
    Execute all approved remediation actions.
    Called periodically or triggered when actions are approved.
    """
    import asyncio
    
    executed = 0
    failed = 0
    
    with SessionLocal() as db:
        # Get all approved actions
        actions = db.query(RemediationAction).filter(
            RemediationAction.status == ActionStatus.APPROVED
        ).all()
        
        for action in actions:
            try:
                # Mark as executing
                action.status = ActionStatus.EXECUTING
                action.executed_at = datetime.now()
                db.commit()
                
                # Execute action
                result = asyncio.run(_execute_action(action))
                
                # Mark as completed
                action.status = ActionStatus.COMPLETED
                action.completed_at = datetime.now()
                action.result = result
                action.error_message = None
                executed += 1
                
                logger.info(f"Executed action {action.id}: {action.title}")
                
            except Exception as e:
                # Mark as failed
                action.status = ActionStatus.FAILED
                action.completed_at = datetime.now()
                action.error_message = str(e)
                failed += 1
                
                logger.error(f"Failed to execute action {action.id}: {str(e)}")
            
            finally:
                db.commit()
    
    return {
        "executed": executed,
        "failed": failed,
        "total": executed + failed
    }


@celery_app.task
def execute_single_action(action_id: str):
    """Execute a specific action by ID"""
    import asyncio
    
    with SessionLocal() as db:
        action = db.get(RemediationAction, action_id)
        
        if not action:
            return {"error": "Action not found"}
        
        if action.status != ActionStatus.APPROVED:
            return {"error": f"Action not approved (status: {action.status})"}
        
        try:
            # Mark as executing
            action.status = ActionStatus.EXECUTING
            action.executed_at = datetime.now()
            db.commit()
            
            # Execute action
            result = asyncio.run(_execute_action(action))
            
            # Mark as completed
            action.status = ActionStatus.COMPLETED
            action.completed_at = datetime.now()
            action.result = result
            action.error_message = None
            db.commit()
            
            return {"success": True, "result": result}
            
        except Exception as e:
            # Mark as failed
            action.status = ActionStatus.FAILED
            action.completed_at = datetime.now()
            action.error_message = str(e)
            db.commit()
            
            return {"success": False, "error": str(e)}
