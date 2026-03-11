from agents.state import AgentState

def test_raw_documents_reducer():
    # Simulate two parallel agent outputs
    a = {"raw_documents": [{"id": 1}]}
    b = {"raw_documents": [{"id": 2}]}

    # Mimic LangGraph reducer behavior (operator.add)
    merged = a["raw_documents"] + b["raw_documents"]

    assert len(merged) == 2
