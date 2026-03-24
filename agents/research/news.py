from typing import List

from agents.state import AgentState, SourceDocument
from retrieval import default_pipeline


def news_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    news_tasks = [t for t in tasks if t["type"] == "market"]

    documents: List[SourceDocument] = []

    for task in news_tasks:
        docs = default_pipeline.fetch(task["query"], "market")
        documents.extend(docs)
        task["status"] = "complete"

    return {"raw_documents": documents}