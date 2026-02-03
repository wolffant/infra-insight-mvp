import uuid
from datetime import datetime, timezone, timedelta
from sqlalchemy import select
from worker.detectors.base import Detector
from worker.core.config import settings
from worker.db_models import JiraIssue

class BacklogAgingDetector(Detector):
    name = "backlog_aging"

    def __init__(self, db):
        self.db = db

    def run(self):
        cutoff = datetime.now(timezone.utc) - timedelta(days=settings.BACKLOG_AGING_DAYS)
        q = select(JiraIssue).where(
            JiraIssue.status_category == "To Do",
            JiraIssue.created_at_jira != None,
            JiraIssue.created_at_jira < cutoff,
        ).limit(500)
        issues = self.db.execute(q).scalars().all()
        if not issues:
            return []

        buckets = {}
        for i in issues:
            buckets.setdefault(i.project_key, []).append(i)

        findings = []
        for project_key, arr in buckets.items():
            sample = [x.key for x in arr[:20]]
            fingerprint = f"{project_key}:todo_older_than_{settings.BACKLOG_AGING_DAYS}d"
            findings.append({
                "id": str(uuid.uuid4()),
                "type": self.name,
                "fingerprint": fingerprint,
                "severity": 2 if len(arr) > 20 else 3,
                "confidence": 80,
                "service_id": None,
                "title": f"Backlog aging in {project_key}: {len(arr)} To Do items older than {settings.BACKLOG_AGING_DAYS} days",
                "summary": "Stale tickets in To Do suggest triage debt and unclear prioritisation.",
                "evidence": {
                    "rule": f"status_category == 'To Do' AND created_at < now-{settings.BACKLOG_AGING_DAYS}d",
                    "count": len(arr),
                    "sample_issue_keys": sample
                },
                "remediation": {
                    "steps": [
                        "Define triage SLA by priority.",
                        "Run weekly backlog grooming with explicit close/park decisions.",
                        "Enforce required fields at intake (priority, owner, acceptance criteria)."
                    ]
                }
            })
        return findings
