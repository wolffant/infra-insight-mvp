import uuid
from sqlalchemy import select, desc
from worker.detectors.base import Detector
from worker.core.config import settings
from worker.db_models import K8sPodSnapshot

class CrashLoopRestartsDetector(Detector):
    name = "crashloop_restarts"

    def __init__(self, db):
        self.db = db

    def run(self):
        q = select(K8sPodSnapshot).order_by(desc(K8sPodSnapshot.created_at)).limit(5000)
        pods = self.db.execute(q).scalars().all()
        if not pods:
            return []

        bad = [p for p in pods if p.reason == "CrashLoopBackOff" or (p.restart_count or 0) >= settings.POD_RESTART_THRESHOLD]
        if not bad:
            return []

        by_ns = {}
        for p in bad:
            by_ns.setdefault(p.namespace, []).append(p)

        findings = []
        for ns, arr in by_ns.items():
            arr_sorted = sorted(arr, key=lambda x: (x.restart_count or 0), reverse=True)
            sample = [{"pod": x.pod, "restarts": x.restart_count, "reason": x.reason} for x in arr_sorted[:20]]
            fingerprint = f"{ns}:pod_restarts_or_crashloop"
            sev = 1 if any(x.reason == "CrashLoopBackOff" for x in arr) else 2
            findings.append({
                "id": str(uuid.uuid4()),
                "type": self.name,
                "fingerprint": fingerprint,
                "severity": sev,
                "confidence": 85,
                "service_id": None,
                "title": f"Kubernetes instability in {ns}: {len(arr)} pods restarting / CrashLoopBackOff",
                "summary": "Frequent restarts usually indicate failing containers, bad config, or insufficient resources.",
                "evidence": {
                    "rule": f"reason == CrashLoopBackOff OR restart_count >= {settings.POD_RESTART_THRESHOLD}",
                    "count": len(arr),
                    "top_pods": sample
                },
                "remediation": {
                    "steps": [
                        "Check failing pod logs and recent deploys.",
                        "Verify CPU/memory requests & limits are set.",
                        "Add readiness/liveness probes and safe startup.",
                        "Ensure replicas > 1 for critical workloads and add PDB."
                    ]
                }
            })
        return findings
