from sqlalchemy.dialects.postgresql import insert
from worker.celery_app import celery_app
from worker.core.db import SessionLocal
from worker.db_models import Finding, RemediationAction, ActionStatus
from worker.detectors.backlog_aging import BacklogAgingDetector
from worker.detectors.crashloop_restarts import CrashLoopRestartsDetector
import uuid

def _upsert_finding(db, f: dict):
    # Extract proposed action if present
    proposed_action = f.pop("proposed_action", None)
    
    stmt = insert(Finding).values(**f)
    update_cols = {k: stmt.excluded[k] for k in f.keys() if k != "id"}
    result = db.execute(stmt.on_conflict_do_update(constraint="uq_findings_type_fingerprint", set_=update_cols))
    
    # Create remediation action if proposed
    if proposed_action:
        # Only insert if doesn't exist (simple check by finding_id + action_type for now)
        # TODO: Add proper status filter after fixing enum handling
        existing = db.query(RemediationAction).filter(
            RemediationAction.finding_id == f["id"],
            RemediationAction.action_type == proposed_action["action_type"]
        ).first()
        
        if not existing:
            action = RemediationAction(
                id=str(uuid.uuid4()),
                finding_id=f["id"],
                action_type=proposed_action["action_type"],
                status=ActionStatus.PROPOSED,
                title=proposed_action["title"],
                description=proposed_action.get("description"),
                params=proposed_action["params"]
            )
            db.add(action)

@celery_app.task
def run_detectors():
    upserted = 0
    with SessionLocal() as db:
        for detector in (BacklogAgingDetector(db), CrashLoopRestartsDetector(db)):
            for f in detector.run():
                _upsert_finding(db, f)
                upserted += 1
        db.commit()
    return {"findings_upserted": upserted}
