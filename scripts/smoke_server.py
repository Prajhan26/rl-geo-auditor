from fastapi.testclient import TestClient

from server.app import app


def main() -> None:
    client = TestClient(app)

    root = client.get("/")
    assert root.status_code == 200
    root_payload = root.json()
    assert root_payload["name"] == "geo-audit-env"
    assert root_payload["routes"]["docs"] == "/docs"
    print("[OK] /")

    health = client.get("/health")
    assert health.status_code == 200
    assert health.json() == {"status": "healthy"}
    print("[OK] /health")

    metadata = client.get("/metadata")
    assert metadata.status_code == 200
    metadata_payload = metadata.json()
    assert metadata_payload["name"] == "geo-audit-env"
    assert "check_schema" in metadata_payload["available_actions"]
    assert "mark_positive" in metadata_payload["available_actions"]
    assert "has_sources" in metadata_payload["positive_types"]
    print("[OK] /metadata")

    state_before_reset = client.get("/state")
    assert state_before_reset.status_code == 200
    assert state_before_reset.json()["message"].startswith("No active episode")
    print("[OK] /state before reset")

    reset = client.post("/reset", json={"task_difficulty": "easy"})
    assert reset.status_code == 200
    reset_payload = reset.json()
    assert reset_payload["step_count"] == 0
    assert reset_payload["done"] is False
    print("[OK] /reset")

    state_after_reset = client.get("/state")
    assert state_after_reset.status_code == 200
    assert state_after_reset.json()["page"]["url"] == reset_payload["page"]["url"]
    print("[OK] /state after reset")

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

    positive = client.post(
        "/step",
        json={
            "action_type": "mark_positive",
            "positive_type": "good_heading_structure",
            "details": "The page has a readable heading structure.",
        },
    )
    assert positive.status_code == 200
    positive_payload = positive.json()
    assert positive_payload["marked_positives"][0]["type"] == "good_heading_structure"
    print("[OK] /step mark_positive")

    submit = client.post("/step", json={"action_type": "submit_report"})
    assert submit.status_code == 200
    submit_payload = submit.json()
    assert submit_payload["done"] is True
    assert 0.0 <= submit_payload["reward"] <= 1.0
    print("[OK] /step submit_report")

    print("[DONE] local server smoke flow passed")


if __name__ == "__main__":
    main()
