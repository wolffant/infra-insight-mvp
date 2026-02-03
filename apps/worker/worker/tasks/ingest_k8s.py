import uuid
from sqlalchemy.dialects.postgresql import insert
from worker.celery_app import celery_app
from worker.core.db import SessionLocal
from worker.core.config import settings
from worker.connectors.k8s import load_client, namespace_filter
from worker.db_models import K8sPodSnapshot, K8sEvent

def _restart_count(pod) -> int:
    total = 0
    statuses = (pod.status.container_statuses or []) + (pod.status.init_container_statuses or [])
    for s in statuses:
        total += int(getattr(s, "restart_count", 0) or 0)
    return total

def _reason(pod):
    statuses = pod.status.container_statuses or []
    for s in statuses:
        st = getattr(s, "state", None)
        if st and st.waiting and st.waiting.reason:
            return st.waiting.reason
    return None

@celery_app.task
def ingest_k8s():
    v1 = load_client()
    ns_allow = namespace_filter()

    # Pods snapshot
    pods = v1.list_pod_for_all_namespaces(watch=False)
    pod_rows = 0
    with SessionLocal() as db:
        for pod in pods.items:
            ns = pod.metadata.namespace
            if ns_allow and ns not in ns_allow:
                continue
            row = {
                "id": str(uuid.uuid4()),
                "cluster": None,
                "namespace": ns,
                "pod": pod.metadata.name,
                "node": pod.spec.node_name,
                "phase": pod.status.phase,
                "restart_count": _restart_count(pod),
                "reason": _reason(pod),
                "raw": {
                    "labels": pod.metadata.labels or {},
                    "owner_refs": [r.to_dict() for r in (pod.metadata.owner_references or [])],
                },
            }
            db.execute(insert(K8sPodSnapshot).values(**row))
            pod_rows += 1
        db.commit()

    # Events upsert
    ev_rows = 0
    events = v1.list_event_for_all_namespaces(limit=settings.K8S_MAX_EVENTS)
    with SessionLocal() as db:
        for ev in events.items:
            ns = ev.metadata.namespace or "default"
            if ns_allow and ns not in ns_allow:
                continue
            ev_id = f"{ns}:{ev.metadata.name}"
            row = {
                "id": ev_id,
                "cluster": None,
                "namespace": ns,
                "name": ev.metadata.name,
                "type": ev.type,
                "reason": ev.reason,
                "message": ev.message,
                "involved_kind": ev.involved_object.kind if ev.involved_object else None,
                "involved_name": ev.involved_object.name if ev.involved_object else None,
                "first_timestamp": getattr(ev, "first_timestamp", None),
                "last_timestamp": getattr(ev, "last_timestamp", None),
                "count": int(ev.count or 0),
                "raw": ev.to_dict(),
            }
            stmt = insert(K8sEvent).values(**row)
            update_cols = {k: stmt.excluded[k] for k in row.keys() if k != "id"}
            db.execute(stmt.on_conflict_do_update(index_elements=[K8sEvent.id], set_=update_cols))
            ev_rows += 1
        db.commit()

    return {"pod_snapshots_added": pod_rows, "events_upserted": ev_rows}
