from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.db import get_db
from app.models.finding import Finding

router = APIRouter()

@router.get("/weekly")
def weekly_exec_summary(db: Session = Depends(get_db)):
    counts = db.query(Finding.severity, func.count(Finding.id)).group_by(Finding.severity).all()
    severity_counts = {int(sev): int(cnt) for sev, cnt in counts}
    top = db.query(Finding).order_by(Finding.severity.asc(), Finding.created_at.desc()).limit(10).all()
    return {
        "summary": {
            "total_findings": sum(severity_counts.values()),
            "by_severity": {
                "p0": severity_counts.get(0, 0),
                "p1": severity_counts.get(1, 0),
                "p2": severity_counts.get(2, 0),
                "p3": severity_counts.get(3, 0)
            }
        },
        "top_findings": [{"id": r.id, "severity": r.severity, "title": r.title, "type": r.type} for r in top]
    }
