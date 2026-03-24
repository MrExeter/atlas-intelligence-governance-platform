from typing import List

from agents.state import AgentState, SourceDocument
from retrieval import default_pipeline


def funding_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    funding_tasks = [t for t in tasks if t["type"] == "funding"]

    documents: List[SourceDocument] = []

    for task in funding_tasks:
        docs = default_pipeline.fetch(task["query"], "funding")
        documents.extend(docs)
        task["status"] = "complete"

    return {"raw_documents": documents}