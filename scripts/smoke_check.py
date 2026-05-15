from __future__ import annotations

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from fastapi.testclient import TestClient

from app.main import app


def main() -> None:
    client = TestClient(app)
    routes = [
        "/",
        "/pipeline-board",
        "/bundles",
        "/audit-log",
        "/integrations",
        "/methodology",
        "/docs",
        "/api/dashboard/summary",
        "/api/incidents",
        "/api/pipeline-board",
        "/api/bundles",
        "/api/audit",
        "/api/integrations",
        "/api/sample",
    ]
    for route in routes:
        response = client.get(route)
        assert response.status_code == 200, f"{route} returned {response.status_code}"
    print("smoke-ok")


if __name__ == "__main__":
    main()
