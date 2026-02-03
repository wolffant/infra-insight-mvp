from fastapi import FastAPI
from app.core.logging import setup_logging
from app.routers import health, findings, services, reports, sources

setup_logging()

app = FastAPI(title="Infra Insight MVP", version="0.1.0")

app.include_router(health.router, prefix="/health", tags=["health"])
app.include_router(findings.router, prefix="/findings", tags=["findings"])
app.include_router(services.router, prefix="/services", tags=["services"])
app.include_router(reports.router, prefix="/reports", tags=["reports"])
app.include_router(sources.router, prefix="/sources", tags=["sources"])
