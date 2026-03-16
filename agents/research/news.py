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
    Fetches news articles from list of sources.
    :param query: query or phrase to search news articles for.
    :return: list of news articles.
    """

    documents: List[SourceDocument] = []

    for url in NEWS_SOURCES:
        try:
            r = requests.get(url, timeout=5)

            text = r.text[:2000]

            # Fast checks first
            if not text:
                continue

            if len(text) < 300:
                continue

            text_lower = text.lower()

            # Garbage filter
            if "<html" in text_lower:
                continue

            if "<!doctype" in text_lower:
                continue

            if "forbidden" in text_lower:
                continue

            # Keyword check (more expensive)
            keywords = query.lower().split()

            if not any(k in text_lower for k in keywords):
                continue

            documents.append(
                {
                    "id": str(uuid4()),
                    "title": f"{url}",
                    "url": url,
                    "content": text,
                    "metadata": {"source": "news"}
                }
            )

        except Exception:
            continue

    return documents


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
