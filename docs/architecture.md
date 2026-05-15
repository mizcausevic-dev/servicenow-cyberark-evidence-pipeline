# Architecture

ServiceNow CyberArk Evidence Pipeline is a Python + FastAPI service that models privileged-review evidence packaging as an operator-facing workflow instead of leaving it split between ticketing, vault metadata, and audit follow-up.

## Core flow

1. Sample ServiceNow/CyberArk incident records live in [C:\Users\chaus\dev\repos\servicenow-cyberark-evidence-pipeline\app\data\sample_pipeline_data.json](/C:/Users/chaus/dev/repos/servicenow-cyberark-evidence-pipeline/app/data/sample_pipeline_data.json).
2. Route handlers in [C:\Users\chaus\dev\repos\servicenow-cyberark-evidence-pipeline\app\main.py](/C:/Users/chaus/dev/repos/servicenow-cyberark-evidence-pipeline/app/main.py) expose HTML proof surfaces and JSON APIs.
3. Packaging and scoring logic in [C:\Users\chaus\dev\repos\servicenow-cyberark-evidence-pipeline\app\services\evidence_pipeline_service.py](/C:/Users/chaus/dev/repos/servicenow-cyberark-evidence-pipeline/app/services/evidence_pipeline_service.py) converts ticket priority, evidence age, artifacts, ownership quality, and exception pressure into ranked incident posture.
4. Render helpers in [C:\Users\chaus\dev\repos\servicenow-cyberark-evidence-pipeline\app\render.py](/C:/Users/chaus/dev/repos/servicenow-cyberark-evidence-pipeline/app/render.py) turn those packets into operator-readable HTML surfaces.
5. `scripts/render_readme_assets.py` produces real README proof assets from the same underlying service data.

## Route surface

- `/` — pipeline overview and incident control plane
- `/pipeline-board` — ranked incident board
- `/bundles` — evidence packet and governance handoff view
- `/audit-log` — replayable log of pulls, enrichment, bundle failures, and escalation
- `/integrations` — ServiceNow, CyberArk, and downstream target posture
- `/methodology` — scoring and prioritization explanation
- `/docs` — route and payload summary
- `/api/*` — JSON routes for summary, incidents, bundles, audit events, integrations, and sample payloads

## Design notes

- The data stays in memory on purpose so the evidence model is easy to inspect and reason about.
- The pipeline is opinionated about evidence quality because incident state alone does not tell reviewers whether a record is actually safe to close.
- The proof surfaces exist to keep the repo legible to IAM, security operations, and governance readers who need the operating story, not just the JSON output.
