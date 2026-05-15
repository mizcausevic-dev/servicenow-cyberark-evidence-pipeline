from __future__ import annotations

import unittest

from fastapi.testclient import TestClient

from app.main import app
from app.services.evidence_pipeline_service import build_service


class EvidencePipelineTests(unittest.TestCase):
    def test_summary_shape(self) -> None:
        summary = build_service().summary()
        self.assertEqual(summary["incidentCount"], 5)
        self.assertIn("leadRecommendation", summary)

    def test_bundle_shape(self) -> None:
        bundle = build_service().evidence_bundles()[0]
        self.assertIn("requiredEvidence", bundle)
        self.assertIn("governanceTargets", bundle)

    def test_incident_api(self) -> None:
        client = TestClient(app)
        response = client.get("/api/incidents")
        self.assertEqual(response.status_code, 200)
        body = response.json()
        self.assertGreaterEqual(len(body), 5)


if __name__ == "__main__":
    unittest.main()
