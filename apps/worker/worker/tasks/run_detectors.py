from sqlalchemy.dialects.postgresql import insert
from worker.celery_app import celery_app
from worker.core.db import SessionLocal
from worker.db_models import Finding
from worker.detectors.backlog_aging import BacklogAgingDetector
from worker.detectors.crashloop_restarts import CrashLoopRestartsDetector

def _upsert_finding(db, f: dict):
    stmt = insert(Finding).values(**f)
    update_cols = {k: stmt.excluded[k] for k in f.keys() if k != "id"}
    db.execute(stmt.on_conflict_do_update(constraint="uq_findings_type_fingerprint", set_=update_cols))

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
