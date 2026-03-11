import os
import sys
import pytest
from pathlib import Path
import json
# from types import SimpleNamespace

ROOT = Path(__file__).resolve().parents[1]
sys.path.append(str(ROOT))

# Force test env and provide required vars (dummy values)
os.environ["ENV"] = "test"
os.environ["OPENAI_API_KEY"] = "test-key"
os.environ["TOKEN_HASH_SALT"] = "test-salt"
os.environ["AWS_REGION"] = "us-west-1"
os.environ["DYNAMODB_TABLE_NAME"] = "test-table"


# ---- Patch langchain_openai.ChatOpenAI BEFORE app/agents import ----
import langchain_openai
from langchain_core.messages import AIMessage

class FakeChatOpenAI:
    def __init__(self, *args, **kwargs):
        pass


    def invoke(self, messages):
        text = ""
        for m in messages:
            if hasattr(m, "content"):
                text += m.content + " "
            elif isinstance(m, dict):
                text += m.get("content", "") + " "
            else:
                text += str(m)

        text = text.lower()

        if "hallucination_risk" in text:
            payload = {
                "executive_summary": 0.8,
                "market_overview": 0.8,
                "competitors": 0.8,
                "opportunities": 0.8,
                "risks": 0.8,
                "hallucination_risk": 0.1,
            }
            return AIMessage(content=json.dumps(payload))

        if "generate research tasks" in text:
            payload = [
                {"type": "market", "query": "market overview test"},
                {"type": "competitors", "query": "competitor analysis test"},
                {"type": "funding", "query": "recent funding test"},
                {"type": "hiring", "query": "hiring trends test"},
            ]
            return AIMessage(content=json.dumps(payload))

        payload = {
            "executive_summary": "Test executive summary",
            "market_overview": "Test market overview",
            "competitors": [
                {"name": "Test competitor A", "summary": "Test summary"},
                {"name": "Test competitor B", "summary": "Test summary"},
            ],
            "opportunities": ["Test opportunity A"],
            "risks": ["Test risk A"],
        }
        return AIMessage(content=json.dumps(payload))

langchain_openai.ChatOpenAI = FakeChatOpenAI

@pytest.fixture(autouse=True)
def mock_openai(monkeypatch):

    class FakeResponse:
        def __init__(self):
            self.output_text = "Fake response"

    class FakeClient:
        class responses:
            @staticmethod
            def create(*args, **kwargs):
                return FakeResponse()


from fastapi.testclient import TestClient

@pytest.fixture
def client():
    from api.main import app
    return TestClient(app)


@pytest.fixture(autouse=True)
def mock_dynamodb(monkeypatch):
    from auth import token_validator

    VALID_HASH = token_validator.hash_token("valid-token")

    class FakeTable:
        def get_item(self, Key):
            token_hash = Key.get("token_hash")

            if token_hash != VALID_HASH:
                return {}  # simulate not found

            return {
                "Item": {
                    "token_hash": token_hash,
                    "is_active": True,
                    "expires_at": "2999-01-01T00:00:00+00:00",
                }
            }

    monkeypatch.setattr(token_validator, "table", FakeTable())
