import pytest
from fastapi import Request
from fastapi.testclient import TestClient
from auth.token_validator import validate_token
from api.main import app

client = TestClient(app)

@pytest.fixture(autouse=True)
def override_auth():
    async def mock_validate_token(request: Request):
        return None

    app.dependency_overrides[validate_token] = mock_validate_token
    yield
    app.dependency_overrides.clear()


def test_research_run_contract(client):
    r = client.post(
        "/research/run",
        json={"topic": "AI developer tools"},
    )
    assert r.status_code == 200
