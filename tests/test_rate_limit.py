import pytest
from auth.token_validator import validate_token
from api.main import app
from fastapi import Request

async def mock_validate_token(request: Request):
    return None

@pytest.fixture(autouse=True)
def override_auth():
    async def mock_validate_token(request: Request):
        return None

    app.dependency_overrides[validate_token] = mock_validate_token
    yield
    app.dependency_overrides.clear()


def test_rate_limit_exceeded(client, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "2")

    headers = {"Authorization": "Bearer test-token"}

    client.post("/research/run", headers=headers, json={"topic": "A"})
    client.post("/research/run", headers=headers, json={"topic": "B"})
    r = client.post("/research/run", headers=headers, json={"topic": "C"})

    assert r.status_code == 429



def test_rate_limit_allows_under_limit(client, monkeypatch):
    monkeypatch.setenv("RATE_LIMIT_PER_MINUTE", "5")

    headers = {"Authorization": "Bearer test-token"}

    r = client.post("/research/run", headers=headers, json={"topic": "OK"})
    assert r.status_code == 200
