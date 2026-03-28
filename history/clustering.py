import re
from collections import defaultdict

# Generic terms that should never form a cluster on their own
STOPWORDS = {
    "ai", "the", "top", "best", "new", "latest", "report", "data",
    "news", "tech", "market", "how", "why", "what", "when", "its",
    "and", "for", "with", "from", "that", "this", "are", "was",
    "says", "says", "will", "has", "have", "can", "not", "but",
}


def _extract_entities(title: str) -> list[str]:
    """Extract capitalized word sequences (1–3 words) from a title."""
    tokens = re.findall(r"[A-Z][a-zA-Z0-9]*(?:\s+[A-Z][a-zA-Z0-9]*){0,2}", title)
    entities = []
    for token in tokens:
        words = token.split()
        # Filter out entries that are entirely stopwords
        meaningful = [w for w in words if w.lower() not in STOPWORDS]
        if meaningful:
            entities.append(token)
    return entities


def cluster_evidence(evidence: list[dict]) -> dict:
    """
    Group evidence into clusters by shared keyword overlap.
    Returns: {"evidence_clusters": [...], "other_sources": [...]}
    """
    if not evidence:
        return {"evidence_clusters": [], "other_sources": []}

    # Build entity -> list of source indices
    entity_to_indices: dict[str, list[int]] = defaultdict(list)
    source_entities: list[list[str]] = []

    for idx, item in enumerate(evidence):
        title = item.get("title") or item.get("url", "")
        entities = _extract_entities(title)
        source_entities.append(entities)
        for entity in entities:
            entity_to_indices[entity].append(idx)

    # Keep only entities shared by ≥ 2 sources
    qualifying = {
        entity: indices
        for entity, indices in entity_to_indices.items()
        if len(indices) >= 2
    }

    # Sort by entity length descending so "Navi AI" wins over "AI"
    ranked = sorted(qualifying.items(), key=lambda x: len(x[0].split()), reverse=True)

    assigned: set[int] = set()
    clusters = []

    for cluster_num, (entity, indices) in enumerate(ranked, start=1):
        members = [i for i in indices if i not in assigned]
        if len(members) < 2:
            continue
        for i in members:
            assigned.add(i)
        clusters.append({
            "cluster_id": f"cluster_{cluster_num}",
            "label": entity,
            "sources": [evidence[i] for i in members],
        })

    other_sources = [evidence[i] for i in range(len(evidence)) if i not in assigned]

    return {"evidence_clusters": clusters, "other_sources": other_sources}
