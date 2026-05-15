# Architecture

ServiceNow CyberArk Evidence Pipeline is a Python + FastAPI service that models privileged-review evidence packaging as an operator-facing workflow instead of leaving it split between ticketing, vault metadata, and audit follow-up.

## Core flow

1. Sample ServiceNow/CyberArk incident records live in [C:\Users\chaus\dev\repos\servicenow-cyberark-evidence-pipeline\app\data\sample_pipeline_data.json](/C:/Users/chaus/dev/repos/servicenow-cyberark-evidence-pipeline/app/data/sample_pipeline_data.json).
2. Route handlers in [C:\Users\chaus\dev\repos\servicenow-cyberark-evidence-pipeline\app\main.py](/C:/Users/chaus/dev/repos/servicenow-cyberark-evidence-pipeline/app/main.py) expose HTML proof surfaces and JSON APIs.
3. Packaging and scoring logic in [C:\Users\chaus\dev\repos\servicenow-cyberark-evidence-pipeline\app\services\evidence_pipeline_service.py](/C:/Users/chaus/dev/repos/servicenow-cyberark-evidence-pipeline/app/services/evidence_pipeline_service.py) converts ticket priority, evidence age, artifacts, ownership quality, exception pressure, infrastructure load, and security posture into ranked operator context.
4. Render helpers in [C:\Users\chaus\dev\repos\servicenow-cyberark-evidence-pipeline\app\render.py](/C:/Users/chaus/dev/repos/servicenow-cyberark-evidence-pipeline/app/render.py) turn those packets into operator-readable HTML surfaces for dashboard, monitor, architecture, and audit review.
5. `scripts/render_readme_assets.py` produces README proof assets from the same underlying service data so the visual layer stays aligned with the app.

## Route surface

- `/` — pipeline overview and incident control plane
- `/pipeline-board` — ranked incident board
- `/bundles` — evidence packet and governance handoff view
- `/monitor` — resource telemetry and component health
- `/security-architecture` — security review surface for credentials, transit, and roles
- `/audit-log` — replayable log of pulls, enrichment, bundle failures, and escalation
- `/integrations` — ServiceNow, CyberArk, and downstream target posture
- `/methodology` — scoring and prioritization explanation
- `/docs` — route and payload summary
- `/api/*` — JSON routes for summary, incidents, bundles, audit events, health telemetry, security architecture, terminal feed, integrations, and sample payloads

## Design notes

- The data stays in memory on purpose so the evidence model, health posture, and architecture story are easy to inspect and reason about.
- The pipeline is opinionated about evidence quality because incident state alone does not tell reviewers whether a record is actually safe to close.
- The monitor and architecture views are intentionally product-like because enterprise readers need to see whether the bridge is trustworthy, not only whether it returns JSON.
