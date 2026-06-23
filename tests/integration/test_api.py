"""API integration tests across the main routers."""

from __future__ import annotations


def test_health(client):
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json()["status"] == "ok"


def test_list_top_level_clauses(client):
    resp = client.get("/api/v1/clauses", params={"top_level_only": True})
    assert resp.status_code == 200
    numbers = [c["clause_number"] for c in resp.json()]
    assert numbers == ["4", "5", "6", "7", "8"]


def test_clause_search(client):
    resp = client.get("/api/v1/clauses/search", params={"q": "corrective"})
    assert resp.status_code == 200
    assert len(resp.json()) >= 1


def test_samd_classify(client):
    resp = client.post(
        "/api/v1/ml-audit/samd-classify",
        json={"significance": "treat_diagnose", "healthcare_situation": "critical"},
    )
    assert resp.status_code == 200
    assert resp.json()["risk_category"] == "IV"


def test_samd_classify_invalid(client):
    resp = client.post(
        "/api/v1/ml-audit/samd-classify",
        json={"significance": "bogus", "healthcare_situation": "critical"},
    )
    assert resp.status_code == 400


def test_audit_checklist_and_finding_flow(client):
    # Create audit
    resp = client.post("/api/v1/audits", json={"title": "API Audit", "audit_type": "internal"})
    assert resp.status_code == 201
    audit_id = resp.json()["id"]

    # Generate checklist from a clause
    resp = client.post(
        f"/api/v1/audits/{audit_id}/checklists", json={"clause_numbers": ["7.3.1"]}
    )
    assert resp.status_code == 201
    assert len(resp.json()["items"]) >= 1

    # Create a finding
    resp = client.post(
        "/api/v1/findings",
        json={
            "audit_id": audit_id,
            "title": "Missing design plan",
            "description": "No documented design plan.",
            "severity": "major_nonconformity",
        },
    )
    assert resp.status_code == 201
    finding_id = resp.json()["id"]

    # Summary reflects the finding
    resp = client.get(f"/api/v1/audits/{audit_id}/summary")
    assert resp.status_code == 200
    assert resp.json()["findings_count"] == 1

    # Create a CAPA for the finding
    resp = client.post("/api/v1/capa", json={"finding_id": finding_id})
    assert resp.status_code == 201
    assert resp.json()["capa_number"].startswith("CAPA-")


def test_capa_invalid_transition_returns_400(client):
    resp = client.post("/api/v1/audits", json={"title": "A"})
    audit_id = resp.json()["id"]
    resp = client.post(
        "/api/v1/findings",
        json={"audit_id": audit_id, "title": "NC", "description": "x"},
    )
    finding_id = resp.json()["id"]
    capa_id = client.post("/api/v1/capa", json={"finding_id": finding_id}).json()["id"]
    # Jump straight to closed - illegal.
    resp = client.patch(f"/api/v1/capa/{capa_id}", json={"status": "closed"})
    assert resp.status_code == 400


def test_ml_model_registration_and_bias(client):
    resp = client.post(
        "/api/v1/ml-audit/models",
        json={"name": "Model X", "model_type": "classification"},
    )
    assert resp.status_code == 201
    model_id = resp.json()["id"]

    resp = client.post(
        f"/api/v1/ml-audit/models/{model_id}/bias-check",
        json={
            "predictions": [1, 1, 0, 0],
            "labels": [1, 0, 0, 0],
            "protected_attributes": {"sex": ["M", "M", "F", "F"]},
        },
    )
    assert resp.status_code == 200
    body = resp.json()
    assert "overall_passed" in body
    assert len(body["results"]) >= 1
