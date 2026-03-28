from history.clustering import cluster_evidence


def _src(title, url="https://example.com"):
    return {"title": title, "url": url, "domain": "example.com"}


def test_empty_input():
    result = cluster_evidence([])
    assert result["evidence_clusters"] == []
    assert result["other_sources"] == []


def test_no_clusters_when_all_unique():
    evidence = [
        _src("Navi AI debuts new product"),
        _src("Robotics hiring trends surge"),
        _src("OpenAI releases update"),
    ]
    result = cluster_evidence(evidence)
    assert result["evidence_clusters"] == []
    assert len(result["other_sources"]) == 3


def test_basic_cluster_formed():
    evidence = [
        _src("Navi AI debuts new product"),
        _src("Navi AI raises funding round"),
        _src("Robotics hiring trends surge"),
    ]
    result = cluster_evidence(evidence)
    assert len(result["evidence_clusters"]) == 1
    assert result["evidence_clusters"][0]["label"] == "Navi AI"
    assert len(result["evidence_clusters"][0]["sources"]) == 2
    assert len(result["other_sources"]) == 1


def test_clustered_sources_not_in_other():
    evidence = [
        _src("Navi AI debuts"),
        _src("Navi AI raises"),
        _src("Other news"),
    ]
    result = cluster_evidence(evidence)
    cluster_titles = {s["title"] for s in result["evidence_clusters"][0]["sources"]}
    other_titles = {s["title"] for s in result["other_sources"]}
    assert cluster_titles.isdisjoint(other_titles)


def test_longer_entity_wins_over_generic():
    evidence = [
        _src("Navi AI debuts product"),
        _src("Navi AI raises round"),
        _src("AI hiring trends"),
        _src("AI market report"),
    ]
    result = cluster_evidence(evidence)
    labels = [c["label"] for c in result["evidence_clusters"]]
    # "Navi AI" (2 words) should win; "AI" alone should not form a cluster
    # because those sources were already claimed or AI is filtered
    assert "Navi AI" in labels


def test_cluster_ids_are_unique():
    evidence = [
        _src("Navi AI debuts"),
        _src("Navi AI raises"),
        _src("Autodesk Tool launches"),
        _src("Autodesk Tool update"),
    ]
    result = cluster_evidence(evidence)
    ids = [c["cluster_id"] for c in result["evidence_clusters"]]
    assert len(ids) == len(set(ids))


def test_preserves_all_sources():
    evidence = [
        _src("Navi AI debuts"),
        _src("Navi AI raises"),
        _src("Other news A"),
        _src("Other news B"),
    ]
    result = cluster_evidence(evidence)
    clustered = sum(len(c["sources"]) for c in result["evidence_clusters"])
    total = clustered + len(result["other_sources"])
    assert total == len(evidence)
