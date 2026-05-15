from __future__ import annotations

from fastapi import FastAPI, HTTPException
from fastapi.responses import HTMLResponse

from app.render import (
    render_audit_log,
    render_bundles,
    render_docs,
    render_integrations,
    render_methodology,
    render_overview,
    render_pipeline_board,
)
from app.services.evidence_pipeline_service import build_service

app = FastAPI(
    title="ServiceNow CyberArk Evidence Pipeline",
    version="0.1.0",
    description=(
        "FastAPI pipeline for collecting ServiceNow and CyberArk access-change events into "
        "audit-ready evidence records and privileged-review approval artifacts."
    ),
)

SERVICE = build_service()


@app.get("/", response_class=HTMLResponse)
def overview() -> str:
    return render_overview()


@app.get("/pipeline-board", response_class=HTMLResponse)
def pipeline_board() -> str:
    return render_pipeline_board()


@app.get("/bundles", response_class=HTMLResponse)
def bundles() -> str:
    return render_bundles()


@app.get("/audit-log", response_class=HTMLResponse)
def audit_log() -> str:
    return render_audit_log()


@app.get("/integrations", response_class=HTMLResponse)
def integrations() -> str:
    return render_integrations()


@app.get("/methodology", response_class=HTMLResponse)
def methodology() -> str:
    return render_methodology()


@app.get("/docs", response_class=HTMLResponse)
def docs() -> str:
    return render_docs()


@app.get("/api/dashboard/summary")
def dashboard_summary() -> dict:
    return SERVICE.summary()


@app.get("/api/incidents")
def incidents() -> list[dict]:
    return SERVICE.incident_catalog()


@app.get("/api/incidents/{incident_id}")
def incident_detail(incident_id: str) -> dict:
    incident = SERVICE.incident_detail(incident_id)
    if incident is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return incident


@app.get("/api/pipeline-board")
def pipeline_board_api() -> list[dict]:
    return SERVICE.pipeline_board()


@app.get("/api/bundles")
def bundles_api() -> list[dict]:
    return SERVICE.evidence_bundles()


@app.get("/api/audit")
def audit_api() -> list[dict]:
    return SERVICE.audit_log()


@app.get("/api/integrations")
def integrations_api() -> dict:
    return SERVICE.integration_posture()


@app.get("/api/sample")
def sample() -> dict:
    return SERVICE.sample_payload()


if __name__ == "__main__":
    import os
    import uvicorn

    port = int(os.environ.get("PORT", "5059"))
    uvicorn.run("app.main:app", host="127.0.0.1", port=port, reload=False)
