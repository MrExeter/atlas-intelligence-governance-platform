from typing import List
from uuid import uuid4
import requests

from agents.state import AgentState, SourceDocument


NEWS_SOURCES = [
    "https://news.ycombinator.com/",
    "https://techcrunch.com/",
    "https://www.theverge.com/"
]


def fetch_news(query: str) -> List[SourceDocument]:
    """
    Very simple placeholder fetcher.
    Replace later with proper search APIs.
    """

    # For now: fake documents so pipeline works end-to-end
    return [
        {
            "id": str(uuid4()),
            "title": f"News about {query}",
            "url": "https://example.com",
            "content": f"Recent developments regarding {query}.",
            "metadata": {"source": "mock"}
        }
    ]


def news_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    news_tasks = [t for t in tasks if t["type"] == "market"]

    documents: List[SourceDocument] = []

    for task in news_tasks:
        docs = fetch_news(task["query"])
        documents.extend(docs)
        task["status"] = "complete"

    existing = state.get("raw_documents", [])

    return {
        "raw_documents": documents
    }
