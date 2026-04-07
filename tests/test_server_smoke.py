from fastapi.testclient import TestClient

from server.app import app


def test_health_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json() == {"status": "healthy"}


def test_metadata_endpoint() -> None:
    client = TestClient(app)
    response = client.get("/metadata")

    assert response.status_code == 200
    payload = response.json()
    assert payload["name"] == "geo-audit-env"
    assert "check_schema" in payload["available_actions"]


def test_reset_endpoint_returns_observation() -> None:
    client = TestClient(app)
    response = client.post("/reset", json={"task_difficulty": "easy"})

    assert response.status_code == 200
    payload = response.json()

    assert payload["page"]["url"]
    assert payload["page"]["target_query"]
    assert payload["step_count"] == 0
    assert payload["done"] is False
    assert "submit_report" in payload["available_actions"]


def test_step_endpoint_flags_issue_and_submits_report() -> None:
    client = TestClient(app)
    client.post("/reset", json={"task_difficulty": "easy"})

    flag_response = client.post(
        "/step",
        json={
            "action_type": "flag_issue",
            "issue_type": "missing_meta_description",
            "severity": "critical",
            "details": "Meta description is missing.",
        },
    )
    flag_payload = flag_response.json()

    assert flag_response.status_code == 200
    assert flag_payload["flagged_issues"][0]["type"] == "missing_meta_description"

    submit_response = client.post("/step", json={"action_type": "submit_report"})
    submit_payload = submit_response.json()

    assert submit_response.status_code == 200
    assert submit_payload["done"] is True
    assert 0.0 <= submit_payload["reward"] <= 1.0
