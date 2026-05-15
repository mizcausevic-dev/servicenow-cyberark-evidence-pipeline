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
        }

    def sync_velocity(self) -> list[dict]:
        return [
            {"day": "Mon", "bundles": 4, "closures": 1},
            {"day": "Tue", "bundles": 7, "closures": 2},
            {"day": "Wed", "bundles": 9, "closures": 2},
            {"day": "Thu", "bundles": 11, "closures": 3},
            {"day": "Fri", "bundles": 13, "closures": 4},
            {"day": "Sat", "bundles": 6, "closures": 1},
            {"day": "Sun", "bundles": 5, "closures": 1}
        ]

    def audit_log(self) -> list[dict]:
        highest = self.incident_catalog()[0]
        return [
            {
                "timestamp": "2026-05-15 09:10:12",
                "action": "INCIDENT_PULL_STARTED",
                "resource": "ServiceNow incident feed",
                "result": "Success",
                "detail": "Fresh incident set pulled for privileged-access evidence packaging.",
            },
            {
                "timestamp": "2026-05-15 09:12:01",
                "action": "CYBERARK_ENRICHMENT_ATTACHED",
                "resource": highest["accountName"],
                "result": "Success",
                "detail": "Vault metadata, safe ownership, and evidence age attached to the incident packet.",
            },
            {
                "timestamp": "2026-05-15 09:14:37",
                "action": "BUNDLE_GAP_FLAGGED",
                "resource": "Breakglass rotation exception",
                "result": "Failure",
                "detail": "Evidence packet still lacks approval artifacts and manager verification.",
            },
            {
                "timestamp": "2026-05-15 09:16:04",
                "action": "REVIEW_PACKET_EMITTED",
                "resource": "Quarterly certification export",
                "result": "Success",
                "detail": "Structured payload emitted for downstream governance and audit workflows.",
            },
            {
                "timestamp": "2026-05-15 09:17:42",
                "action": "OWNER_LANE_ESCALATED",
                "resource": "Non-Prod Hygiene",
                "result": "Failure",
                "detail": "Unassigned account evidence lane remains unresolved beyond the expected closure window.",
            },
        ]

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
                {"name": "Auto-close stale incidents", "type": "remediation", "enabled": False}
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
