from sqlalchemy.dialects.postgresql import insert
from worker.celery_app import celery_app
from worker.core.db import SessionLocal
from worker.core.config import settings
from worker.connectors.jira import search_issues, parse_dt
from worker.db_models import JiraIssue, JiraChangelogEvent

def _project_jql():
    projects = [p.strip() for p in settings.JIRA_PROJECT_KEYS.split(",") if p.strip()]
    if not projects:
        raise RuntimeError("JIRA_PROJECT_KEYS is empty")
    base = f"project in ({','.join(projects)})"
    extra = (settings.JIRA_JQL_EXTRA or "").strip()
    if extra:
        base = f"({base}) AND ({extra})"
    base = f"{base} AND updated >= -30d ORDER BY updated DESC"
    return base

def _upsert_issue(db, issue_payload: dict):
    fields = issue_payload.get("fields", {}) or {}
    issue = {
        "key": issue_payload["key"],
        "issue_id": issue_payload.get("id"),
        "project_key": (fields.get("project") or {}).get("key"),
        "issue_type": (fields.get("issuetype") or {}).get("name"),
        "status": (fields.get("status") or {}).get("name"),
        "status_category": ((fields.get("status") or {}).get("statusCategory") or {}).get("name"),
        "priority": (fields.get("priority") or {}).get("name"),
        "summary": fields.get("summary"),
        "assignee": (fields.get("assignee") or {}).get("displayName") if fields.get("assignee") else None,
        "reporter": (fields.get("reporter") or {}).get("displayName") if fields.get("reporter") else None,
        "created_at_jira": parse_dt(fields.get("created")),
        "updated_at_jira": parse_dt(fields.get("updated")),
        "raw": issue_payload,
    }
    stmt = insert(JiraIssue).values(**issue)
    update_cols = {k: stmt.excluded[k] for k in issue.keys() if k != "key"}
    db.execute(stmt.on_conflict_do_update(index_elements=[JiraIssue.key], set_=update_cols))

def _upsert_changelog(db, issue_key: str, changelog: dict):
    histories = (changelog or {}).get("histories", []) or []
    for h in histories:
        history_id = str(h.get("id"))
        author = ((h.get("author") or {}).get("displayName")) if h.get("author") else None
        created_at = parse_dt(h.get("created"))
        items = h.get("items", []) or []
        for idx, it in enumerate(items):
            event_id = f"{issue_key}:{history_id}:{idx}"
            row = {
                "id": event_id,
                "issue_key": issue_key,
                "history_id": history_id,
                "author": author,
                "created_at": created_at,
                "field": it.get("field"),
                "from_string": it.get("fromString"),
                "to_string": it.get("toString"),
                "raw": {"history": h, "item": it},
            }
            stmt = insert(JiraChangelogEvent).values(**row)
            update_cols = {k: stmt.excluded[k] for k in row.keys() if k != "id"}
            db.execute(stmt.on_conflict_do_update(index_elements=[JiraChangelogEvent.id], set_=update_cols))

@celery_app.task
def ingest_jira():
    jql = _project_jql()
    total = 0
    start_at = 0
    max_results = 50
    with SessionLocal() as db:
        while total < settings.JIRA_MAX_ISSUES:
            page = search_issues(jql=jql, start_at=start_at, max_results=max_results)
            issues = page.get("issues", []) or []
            if not issues:
                break
            for issue in issues:
                _upsert_issue(db, issue)
                _upsert_changelog(db, issue["key"], issue.get("changelog"))
                total += 1
                if total >= settings.JIRA_MAX_ISSUES:
                    break
            db.commit()
            start_at += len(issues)
            if start_at >= int(page.get("total", 0) or 0):
                break
    return {"ingested_issues": total, "jql": jql}
