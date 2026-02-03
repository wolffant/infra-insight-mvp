from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.core.db import get_db
from app.models.finding import Finding

router = APIRouter()

@router.get("/")
def list_findings(limit: int = 200, db: Session = Depends(get_db)):
    rows = db.query(Finding).order_by(Finding.created_at.desc()).limit(limit).all()
    return [{
        "id": r.id,
        "type": r.type,
        "fingerprint": r.fingerprint,
        "severity": r.severity,
        "confidence": r.confidence,
        "title": r.title,
        "summary": r.summary,
        "service_id": r.service_id,
        "created_at": r.created_at
    } for r in rows]

@router.get("/{finding_id}")
def get_finding(finding_id: str, db: Session = Depends(get_db)):
    r = db.query(Finding).filter(Finding.id == finding_id).first()
    if not r:
        return {"error": "not_found"}
    return {
        "id": r.id,
        "type": r.type,
        "fingerprint": r.fingerprint,
        "severity": r.severity,
        "confidence": r.confidence,
        "title": r.title,
        "summary": r.summary,
        "service_id": r.service_id,
        "evidence": r.evidence,
        "remediation": r.remediation,
        "created_at": r.created_at,
        "updated_at": r.updated_at
    }

@router.get("/trends/daily")
def daily_trends(days: int = 14, db: Session = Depends(get_db)):
    # counts per day & severity for last N days
    q = db.query(
        func.date_trunc('day', Finding.created_at).label("day"),
        Finding.severity,
        func.count(Finding.id).label("count")
    ).filter(Finding.created_at >= func.now() - func.make_interval(0, 0, 0, days))      .group_by("day", Finding.severity).order_by("day")

    out = {}
    for day, sev, cnt in q:
        k = day.date().isoformat()
        out.setdefault(k, {0: 0, 1: 0, 2: 0, 3: 0})
        out[k][int(sev)] = int(cnt)

    return [{"day": d, "p0": v[0], "p1": v[1], "p2": v[2], "p3": v[3]} for d, v in out.items()]
