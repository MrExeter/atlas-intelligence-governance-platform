from typing import List

from agents.state import AgentState, SourceDocument
from retrieval import default_pipeline


def competitors_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    competitor_tasks = [t for t in tasks if t["type"] == "competitors"]

    documents: List[SourceDocument] = []

    for task in competitor_tasks:
        docs = default_pipeline.fetch(task["query"], "competitors")
        documents.extend(docs)
        task["status"] = "complete"

    return {"raw_documents": documents}