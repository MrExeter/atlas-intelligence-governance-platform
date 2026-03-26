import pytest
from fastapi import Request
from unittest.mock import MagicMock

from api.main import app
from auth.token_validator import validate_token
from history.factory import get_history_store
import api.routes.history as history_route


SAMPLE_RUN = {
    "run_id": "test-run-123",
    "timestamp": "2026-03-25T05:00:00+00:00",
    "topic": "AI in drones",
    "invite_token": "dev_abc123",
    "status": "completed",
    "governance": {
        "overall_score": 0.73,
        "policy_verdict": "WARN",
        "evidence_coverage": 0.67,
        "hallucination_rate": 0.33,
        "retrieval_relevance": 0.8,
        "sources_used": 15,
        "claims_evaluated": 24,
    },
    "metrics": {
        "tokens_used": 5608,
        "llm_cost_usd": 0.0012,
        "api_cost_usd": 0.013,
        "total_cost_usd": 0.0142,
        "latency_ms": 28849,
        "providers_used": ["tavily", "newsdata"],
        "models_used": ["openai:gpt-4o-mini"],
    },
    "result": {
        "executive_summary": "Test summary",
        "market_overview": "Test overview",
        "competitors": [{"name": "Acme", "summary": "Competitor"}],
        "opportunities": ["Opportunity A"],
        "risks": ["Risk A"],
    },
}


@pytest.fixture(autouse=True)
def override_auth():
    async def mock_validate_token(request: Request):
        return "dev_abc123"

    app.dependency_overrides[validate_token] = mock_validate_token
    yield
    app.dependency_overrides.clear()


@pytest.fixture(autouse=True)
def mock_history_store():
    store = MagicMock()
    store.list_runs.return_value = [SAMPLE_RUN]
    store.get_run.return_value = SAMPLE_RUN
    history_route.history_store = store
    yield store


def test_list_runs_returns_200(client):
    r = client.get("/history/runs")
    assert r.status_code == 200


def test_list_runs_response_shape(client):
    r = client.get("/history/runs")
    body = r.json()
    assert "runs" in body
    assert "count" in body
    assert body["count"] == 1
    run = body["runs"][0]
    assert run["run_id"] == "test-run-123"


def test_list_runs_flattened_fields(client):
    r = client.get("/history/runs")
    run = r.json()["runs"][0]
    assert run["governance_score"] == 0.73
    assert run["governance_verdict"] == "WARN"
    assert run["total_cost_usd"] == 0.0142
    assert run["tokens_used"] == 5608
    assert run["latency_ms"] == 28849


def test_list_runs_passes_limit(client, mock_history_store):
    client.get("/history/runs?limit=5")
    mock_history_store.list_runs.assert_called_once_with("dev_abc123", limit=5)


def test_get_run_returns_200(client):
    r = client.get("/history/runs/test-run-123")
    assert r.status_code == 200
    assert r.json()["topic"] == "AI in drones"


def test_get_run_includes_result(client):
    r = client.get("/history/runs/test-run-123")
    body = r.json()
    assert "result" in body
    assert body["result"]["executive_summary"] == "Test summary"


def test_list_runs_excludes_result(client):
    r = client.get("/history/runs")
    run = r.json()["runs"][0]
    assert "result" not in run


def test_get_run_not_found(client, mock_history_store):
    mock_history_store.get_run.return_value = None
    r = client.get("/history/runs/nonexistent")
    assert r.status_code == 404


def test_list_runs_requires_auth(client):
    app.dependency_overrides.clear()
    r = client.get("/history/runs")
    assert r.status_code == 401


def test_list_runs_excludes_non_completed(client, mock_history_store):
    incomplete = {**SAMPLE_RUN, "run_id": "incomplete-run", "status": "partial"}
    mock_history_store.list_runs.return_value = [SAMPLE_RUN, incomplete]
    r = client.get("/history/runs")
    runs = r.json()["runs"]
    statuses = [run["status"] for run in runs]
    assert "partial" not in statuses
    assert all(s == "completed" for s in statuses)
