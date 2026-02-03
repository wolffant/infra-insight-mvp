import base64
import requests
from dateutil import parser as dtparser
from worker.core.config import settings

def _auth_header():
    token = base64.b64encode(f"{settings.JIRA_EMAIL}:{settings.JIRA_API_TOKEN}".encode("utf-8")).decode("utf-8")
    return {"Authorization": f"Basic {token}", "Accept": "application/json"}

def search_issues(jql: str, start_at: int = 0, max_results: int = 50):
    url = f"{settings.JIRA_BASE_URL}/rest/api/3/search"
    params = {
        "jql": jql,
        "startAt": start_at,
        "maxResults": max_results,
        "expand": "changelog",
        "fields": "summary,issuetype,status,priority,assignee,reporter,created,updated,project",
    }
    r = requests.get(url, headers=_auth_header(), params=params, timeout=60)
    r.raise_for_status()
    return r.json()

def parse_dt(s):
    if not s:
        return None
    try:
        return dtparser.isoparse(s)
    except Exception:
        return None
