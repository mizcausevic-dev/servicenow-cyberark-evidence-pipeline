from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path
from statistics import mean


DATA_PATH = Path(__file__).resolve().parents[1] / "data" / "sample_pipeline_data.json"


@dataclass
class ServiceNowCyberArkEvidencePipelineService:
    incidents: list[dict]

    def summary(self) -> dict:
        catalog = self.incident_catalog()
        urgent = sum(1 for item in catalog if item["verdict"] == "critical")
        watch = sum(1 for item in catalog if item["verdict"] == "watch")
        review_ready = sum(1 for item in catalog if item["bundleReady"])
        stale = sum(1 for item in catalog if item["staleEvidence"])
        open_exceptions = sum(item["exceptionCount"] for item in self.incidents)
        highest = max(catalog, key=lambda item: item["riskScore"])
        monitor = self.health_monitor()
        return {
            "incidentCount": len(self.incidents),
            "urgentCount": urgent,
            "watchCount": watch,
            "bundleReadyCount": review_ready,
            "staleEvidenceCount": stale,
            "assignmentGroupCount": len({item["assignmentGroup"] for item in self.incidents}),
            "exceptionCount": open_exceptions,
            "averageRiskScore": round(mean(item["riskScore"] for item in catalog), 1),
            "averageEvidenceAge": round(mean(item["evidenceAgeDays"] for item in self.incidents), 1),
            "highestRiskIncident": highest["incidentId"],
            "leadRecommendation": self._lead_recommendation(catalog),
            "totalSyncs24h": monitor["totals"]["syncs24h"],
            "pipelineSuccess": monitor["totals"]["pipelineSuccess"],
            "cyberarkLatencyMs": monitor["totals"]["cyberarkLatencyMs"],
            "criticalAlerts": monitor["totals"]["criticalAlerts"],
        }

    def incident_catalog(self) -> list[dict]:
        rows = []
        for incident in self.incidents:
            evaluation = self._evaluate_incident(incident)
            rows.append({**incident, **evaluation})
        return sorted(rows, key=lambda row: (row["riskScore"], row["openedDaysAgo"]), reverse=True)

    def incident_detail(self, incident_id: str) -> dict | None:
        incident = next((item for item in self.incidents if item["incidentId"] == incident_id), None)
        if incident is None:
            return None
        evaluation = self._evaluate_incident(incident)
        return {
            **incident,
            **evaluation,
            "bundle": self._bundle_for(incident, evaluation),
        }

    def pipeline_board(self) -> list[dict]:
        return [item for item in self.incident_catalog() if item["verdict"] != "healthy"]

    def evidence_bundles(self) -> list[dict]:
        bundles = []
        for incident in self.incident_catalog():
            bundles.append(self._bundle_for(incident, incident))
        return bundles

    def sample_payload(self) -> dict:
        catalog = self.incident_catalog()
        return {
            "dashboard": self.summary(),
            "highestRiskIncident": catalog[0],
            "pipelineBoard": self.pipeline_board()[:4],
            "bundleExcerpt": self.evidence_bundles()[:3],
            "architecture": self.security_architecture(),
        }

    def sync_velocity(self) -> list[dict]:
        return [
            {"hour": "08:00", "syncs": 1284, "bundles": 4, "latencyMs": 118},
            {"hour": "10:00", "syncs": 1640, "bundles": 7, "latencyMs": 126},
            {"hour": "12:00", "syncs": 1492, "bundles": 9, "latencyMs": 122},
            {"hour": "14:00", "syncs": 1784, "bundles": 11, "latencyMs": 139},
            {"hour": "16:00", "syncs": 1926, "bundles": 13, "latencyMs": 142},
            {"hour": "18:00", "syncs": 1532, "bundles": 6, "latencyMs": 130},
            {"hour": "20:00", "syncs": 1328, "bundles": 5, "latencyMs": 120},
        ]

    def audit_log(self) -> list[dict]:
        highest = self.incident_catalog()[0]
        return [
            {
                "timestamp": "2026-05-15 09:10:12",
                "action": "INCIDENT_PULL_STARTED",
                "resource": "ServiceNow incident feed",
                "result": "Success",
                "latencyMs": 24,
                "detail": "Fresh incident set pulled for privileged-access evidence packaging.",
            },
            {
                "timestamp": "2026-05-15 09:12:01",
                "action": "CYBERARK_ENRICHMENT_ATTACHED",
                "resource": highest["accountName"],
                "result": "Success",
                "latencyMs": 142,
                "detail": "Vault metadata, safe ownership, and evidence age attached to the incident packet.",
            },
            {
                "timestamp": "2026-05-15 09:14:37",
                "action": "BUNDLE_GAP_FLAGGED",
                "resource": "Breakglass rotation exception",
                "result": "Failure",
                "latencyMs": 91,
                "detail": "Evidence packet still lacks approval artifacts and manager verification.",
            },
            {
                "timestamp": "2026-05-15 09:16:04",
                "action": "REVIEW_PACKET_EMITTED",
                "resource": "Quarterly certification export",
                "result": "Success",
                "latencyMs": 33,
                "detail": "Structured payload emitted for downstream governance and audit workflows.",
            },
            {
                "timestamp": "2026-05-15 09:17:42",
                "action": "OWNER_LANE_ESCALATED",
                "resource": "Non-Prod Hygiene",
                "result": "Failure",
                "latencyMs": 56,
                "detail": "Unassigned account evidence lane remains unresolved beyond the expected closure window.",
            },
        ]

    def terminal_feed(self) -> list[str]:
        return [
            "[boot] Evidence pipeline online. ServiceNow incident cursor resumed from 2026-05-15T08:58:11Z.",
            "[sync] Pulled 17 incident candidates from ServiceNow evidence lane.",
            "[ok] Attached CyberArk safe metadata to PROD-BREAKGLASS-API (latency 142ms).",
            "[warn] INC0021906 still missing manager attestation and second approval artifact.",
            "[emit] Quarterly certification packet refreshed for Q2 reviewer bundle.",
            "[alert] Non-prod orphaned admin account still lacks an accountable owner lane.",
        ]

    def health_monitor(self) -> dict:
        components = [
            {
                "name": "Source Ingestion",
                "icon": "ingest",
                "cpu": 21,
                "ramGb": 1.3,
                "networkMb": 15,
                "errorRate": 0.01,
                "status": "healthy",
            },
            {
                "name": "Vault Gateway",
                "icon": "vault",
                "cpu": 35,
                "ramGb": 2.6,
                "networkMb": 7,
                "errorRate": 0.0,
                "status": "healthy",
            },
            {
                "name": "Compute Cluster",
                "icon": "compute",
                "cpu": 76,
                "ramGb": 16.0,
                "networkMb": 123,
                "errorRate": 0.04,
                "status": "watch",
            },
            {
                "name": "Storage Sink",
                "icon": "storage",
                "cpu": 23,
                "ramGb": 0.7,
                "networkMb": 51,
                "errorRate": 0.0,
                "status": "healthy",
            },
        ]
        return {
            "totals": {
                "syncs24h": 12842,
                "cyberarkLatencyMs": 142,
                "pipelineSuccess": 99.98,
                "criticalAlerts": 0,
                "apiResponseMs": 24,
                "avgCpu": 42.8,
                "avgMemGb": 12.4,
                "totalNetIoMb": 192.4,
                "clusterNodes": 14,
                "activeProcesses": 42,
            },
            "components": components,
            "distribution": [
                {"name": "Worker Cluster A", "share": 68},
                {"name": "Worker Cluster B", "share": 42},
            ],
        }

    def security_architecture(self) -> dict:
        return {
            "nodes": [
                {
                    "name": "ServiceNow",
                    "type": "ITSM / GRC Module",
                    "summary": "Source of ticket state, workflow ownership, and audit handoff timing.",
                    "status": "online",
                },
                {
                    "name": "Evidence Pipeline",
                    "type": "FastAPI Core",
                    "summary": "Maps incidents, vault context, and review metadata into audit-ready bundles.",
                    "status": "active",
                },
                {
                    "name": "CyberArk Vault",
                    "type": "PAM Enterprise",
                    "summary": "Provides safe metadata, account posture, and privileged-action context.",
                    "status": "online",
                },
                {
                    "name": "Artifact Storage",
                    "type": "Evidence Archive",
                    "summary": "Stores structured exports for quarterly certification and audit replay.",
                    "status": "online",
                },
            ],
            "credentials": [
                {
                    "title": "Secret Masking",
                    "detail": "Credential material is modeled as vault-managed references, not plain-text runtime variables.",
                },
                {
                    "title": "Least Privilege",
                    "detail": "Service accounts stay restricted to evidence-safe APIs and GRC export surfaces only.",
                },
            ],
            "transitControls": [
                "Mutual TLS for API handshake",
                "AES-256 payload encryption",
                "SHA-256 integrity verification",
                "Isolated pipeline subnet",
            ],
            "accessRoles": [
                {
                    "name": "Pipeline Admin",
                    "detail": "Restricted to SSO-authenticated infrastructure owners with breakglass review rights.",
                },
                {
                    "name": "Audit / Read Only",
                    "detail": "Mapped to ServiceNow GRC reviewers and quarterly certification operators.",
                },
            ],
        }

    def integration_posture(self) -> dict:
        return {
            "servicenow": {
                "apiBaseUrl": "https://servicenow.internal/api/now/table/incident",
                "authType": "OAuth + certificate-bound integration user",
                "stateFilter": "Open, In Progress, Awaiting Evidence, Escalated, Ready for Review",
            },
            "cyberark": {
                "apiBaseUrl": "https://vault-access.internal/api",
                "authType": "CyberArk Identity + certificate",
                "safeOwnershipSync": True,
                "dualApprovalModel": "Preserved in evidence packet",
            },
            "pipeline": {
                "intervalMinutes": 30,
                "evidenceAgeThresholdDays": 45,
                "autoClosure": False,
                "bundleExportFormat": "JSON + markdown summary",
            },
            "targets": [
                {"name": "ServiceNow incident update", "type": "workflow", "enabled": True},
                {"name": "Quarterly certification pack", "type": "evidence export", "enabled": True},
                {"name": "Privileged access audit vault", "type": "governance archive", "enabled": True},
                {"name": "Auto-close stale incidents", "type": "remediation", "enabled": False},
            ],
        }

    def _evaluate_incident(self, incident: dict) -> dict:
        risk = 14

        if incident["priority"].startswith("1"):
            risk += 18
        elif incident["priority"].startswith("2"):
            risk += 11
        else:
            risk += 5

        if incident["evidenceAgeDays"] == 0:
            risk += 18
        elif incident["evidenceAgeDays"] > 90:
            risk += 14
        elif incident["evidenceAgeDays"] > 45:
            risk += 8

        if incident["approvalArtifacts"] == 0:
            risk += 16
        elif incident["approvalArtifacts"] == 1:
            risk += 7

        if not incident["managerVerified"]:
            risk += 14

        if incident["dualApprovalRequired"] and incident["ticketLinks"] == 0:
            risk += 12

        if incident["exceptionCount"] >= 3:
            risk += 12
        elif incident["exceptionCount"] >= 1:
            risk += 6

        if incident["openedDaysAgo"] > 7:
            risk += 10
        elif incident["openedDaysAgo"] > 3:
            risk += 5

        if incident["owner"] == "Unassigned":
            risk += 12

        risk = min(100, risk)
        stale_evidence = incident["evidenceAgeDays"] == 0 or incident["evidenceAgeDays"] > 45
        owner_gap = incident["owner"] == "Unassigned" or not incident["managerVerified"]
        bundle_ready = (
            incident["approvalArtifacts"] >= 2
            and incident["ticketLinks"] >= 1
            and incident["managerVerified"]
            and not stale_evidence
        )

        if risk >= 80:
            verdict = "critical"
            next_action = "Collect approval artifacts, verify the owner, and block closure until the evidence packet is defensible."
        elif risk >= 55:
            verdict = "watch"
            next_action = "Refresh the bundle before the incident silently ages into audit debt."
        else:
            verdict = "healthy"
            next_action = "Keep the incident in the standard packaging cadence and preserve the current evidence chain."

        return {
            "riskScore": risk,
            "verdict": verdict,
            "bundleReady": bundle_ready,
            "staleEvidence": stale_evidence,
            "ownerGap": owner_gap,
            "topConcern": self._top_concern(incident, stale_evidence, owner_gap),
            "nextAction": next_action,
        }

    def _top_concern(self, incident: dict, stale_evidence: bool, owner_gap: bool) -> str:
        if owner_gap and stale_evidence:
            return "The incident is carrying stale evidence and weak ownership, which makes the review packet hard to defend."
        if incident["approvalArtifacts"] == 0:
            return "No approval artifacts are attached yet, so the incident cannot close cleanly into an audit-safe record."
        if incident["dualApprovalRequired"] and incident["ticketLinks"] == 0:
            return "Dual approval is expected, but the ServiceNow packet does not yet prove that chain."
        if incident["exceptionCount"] >= 3:
            return "Exception pressure is stacking faster than the evidence lane is resolving it."
        if stale_evidence:
            return "The evidence packet is aging out of the review-ready lane."
        return "The incident is still healthy enough to stay in the standard packaging cadence."

    def _bundle_for(self, incident: dict, evaluation: dict) -> dict:
        return {
            "incidentId": incident["incidentId"],
            "accountName": incident["accountName"],
            "targetSystem": incident["targetSystem"],
            "assignmentGroup": incident["assignmentGroup"],
            "riskScore": evaluation["riskScore"],
            "verdict": evaluation["verdict"],
            "requiredEvidence": [
                "approval artifact chain",
                "manager attestation",
                "ticket linkage",
                "safe ownership snapshot",
            ],
            "bundleReady": evaluation["bundleReady"],
            "governanceTargets": [
                "ServiceNow incident note",
                "Privileged access audit vault",
                "Quarterly certification packet",
            ],
        }

    def _lead_recommendation(self, catalog: list[dict]) -> str:
        if any(item["verdict"] == "critical" for item in catalog):
            return "Force the stale or artifact-thin incidents through an evidence refresh before they can close into the next governance cycle."
        if any(item["verdict"] == "watch" for item in catalog):
            return "Prioritize owner verification and evidence refresh so the pipeline stays review-ready."
        return "The current incident surface is healthy enough to stay in the standard packaging cadence."


def build_service() -> ServiceNowCyberArkEvidencePipelineService:
    with DATA_PATH.open("r", encoding="utf-8") as handle:
        payload = json.load(handle)
    return ServiceNowCyberArkEvidencePipelineService(incidents=payload["incidents"])
