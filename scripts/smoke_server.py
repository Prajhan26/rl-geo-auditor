from fastapi.testclient import TestClient

from server.app import app


def main() -> None:
    client = TestClient(app)

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy"}
    print("[OK] /health")

    metadata = client.get("/metadata")
    assert metadata.status_code == 200
    metadata_payload = metadata.json()
    assert metadata_payload["name"] == "geo-audit-env"
    assert "check_schema" in metadata_payload["available_actions"]
    print("[OK] /metadata")

    reset = client.post("/reset", json={"task_difficulty": "easy"})
    assert reset.status_code == 200
    reset_payload = reset.json()
    assert reset_payload["step_count"] == 0
    assert reset_payload["done"] is False
    print("[OK] /reset")

    flag = client.post(
        "/step",
        json={
            "action_type": "flag_issue",
            "issue_type": "missing_meta_description",
            "severity": "critical",
            "details": "Meta description is missing.",
        },
    )
    assert flag.status_code == 200
    flag_payload = flag.json()
    assert flag_payload["flagged_issues"][0]["type"] == "missing_meta_description"
    print("[OK] /step flag_issue")

    submit = client.post("/step", json={"action_type": "submit_report"})
    assert submit.status_code == 200
    submit_payload = submit.json()
    assert submit_payload["done"] is True
    assert 0.0 <= submit_payload["reward"] <= 1.0
    print("[OK] /step submit_report")

    print("[DONE] local server smoke flow passed")


if __name__ == "__main__":
    main()
