from agents.planner import planner_node

def test_planner_returns_tasks():
    state = {"topic": "AI developer tools"}
    out = planner_node(state)

    assert "tasks" in out
    assert len(out["tasks"]) > 0
