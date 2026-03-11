from agents.synthesizer import synthesizer_node

def test_synthesizer_contract():
    state = {
        "retrieved_chunks": [{"content": "test"}]
    }

    out = synthesizer_node(state)

    for key in [
        "executive_summary",
        "market_overview",
        "competitors",
        "opportunities",
        "risks",
    ]:
        assert key in out
