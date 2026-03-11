from typing import List
from uuid import uuid4

from agents.state import AgentState, SourceDocument


def fetch_hiring(query: str) -> List[SourceDocument]:
    """
    Placeholder hiring fetcher.
    Later: LinkedIn Jobs, Indeed, company career pages, etc.
    """

    return [
        {
            "id": str(uuid4()),
            "title": f"Hiring trends for {query}",
            "url": "https://example.com",
            "content": f"Companies hiring related to {query}, showing growth signals.",
            "metadata": {"source": "mock_hiring"}
        }
    ]


def hiring_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    hiring_tasks = [t for t in tasks if t["type"] == "hiring"]

    documents: List[SourceDocument] = []

    for task in hiring_tasks:
        docs = fetch_hiring(task["query"])
        documents.extend(docs)
        task["status"] = "complete"

    existing = state.get("raw_documents", [])

    return {
        "raw_documents": documents
    }
