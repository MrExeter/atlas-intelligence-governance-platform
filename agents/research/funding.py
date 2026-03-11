from typing import List
from uuid import uuid4

from agents.state import AgentState, SourceDocument


def fetch_funding(query: str) -> List[SourceDocument]:
    """
    Placeholder funding fetcher.
    Replace later with Crunchbase / Clearbit / SerpAPI, etc.
    """

    return [
        {
            "id": str(uuid4()),
            "title": f"Funding activity for {query}",
            "url": "https://example.com",
            "content": f"Recent funding rounds related to {query}.",
            "metadata": {"source": "mock_funding"}
        }
    ]


def funding_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    funding_tasks = [t for t in tasks if t["type"] == "funding"]

    documents: List[SourceDocument] = []

    for task in funding_tasks:
        docs = fetch_funding(task["query"])
        documents.extend(docs)
        task["status"] = "complete"

    existing = state.get("raw_documents", [])

    return {
        "raw_documents": documents
    }
