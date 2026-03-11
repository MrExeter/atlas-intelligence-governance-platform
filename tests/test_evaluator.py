from agents.evaluator import evaluator_node

def test_eval_scores_range():
    state = {
        "executive_summary": "x",
        "market_overview": "x",
        "competitors": [],
        "opportunities": [],
        "risks": []
    }

    out = evaluator_node(state)

    scores = out["eval_scores"]

    for v in scores.values():
        assert 0 <= v <= 1
