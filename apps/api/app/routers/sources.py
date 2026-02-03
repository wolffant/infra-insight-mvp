from fastapi import APIRouter
router = APIRouter()

@router.get("/")
def sources():
    return {"jira": "configured via env", "kubernetes": "configured via env"}
