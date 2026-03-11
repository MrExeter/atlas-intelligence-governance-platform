from typing import List
from uuid import uuid4

from agents.state import AgentState, SourceDocument


def fetch_competitors(query: str) -> List[SourceDocument]:
    """
    Placeholder competitors fetcher.
    Later: SimilarWeb, G2, Crunchbase, direct product scraping, etc.
    """

    return [
        {
            "id": str(uuid4()),
            "title": f"Competitors in {query}",
            "url": "https://example.com",
            "content": f"Major competitors and alternative products in {query}.",
            "metadata": {"source": "mock_competitors"}
        }
    ]


def competitors_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    competitor_tasks = [t for t in tasks if t["type"] == "competitors"]

    documents: List[SourceDocument] = []

    for task in competitor_tasks:
        docs = fetch_competitors(task["query"])
        documents.extend(docs)
        task["status"] = "complete"

    existing = state.get("raw_documents", [])

    return {
        "raw_documents": documents
    }
