from typing import List

from agents.state import AgentState, SourceDocument

_MAX_RETRIEVED = 5


def _relevance_score(doc: SourceDocument, topic: str) -> float:
    keywords = set(topic.lower().split())
    if not keywords:
        return 0.0
    text = (doc.get("title", "") + " " + doc.get("content", "")).lower()
    matches = sum(1 for k in keywords if k in text)
    return matches / len(keywords)


def rag_node(state: AgentState) -> AgentState:
    documents = state.get("raw_documents", [])
    topic = state.get("topic", "")

    valid = [d for d in documents if d.get("content", "").strip()]

    scored = sorted(valid, key=lambda d: _relevance_score(d, topic), reverse=True)

    return {"retrieved_chunks": scored[:_MAX_RETRIEVED]}