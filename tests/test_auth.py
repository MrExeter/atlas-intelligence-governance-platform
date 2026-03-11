def test_missing_token(client):
    resp = client.post("/research/run", json={"topic": "AI tools"})
    assert resp.status_code == 401


def test_invalid_token(client):
    resp = client.post(
        "/research/run",
        headers={"Authorization": "Bearer invalid"},
        json={"topic": "AI tools"},
    )
    assert resp.status_code == 401

