from typing import List

from agents.state import AgentState, SourceDocument
from retrieval import default_pipeline


def hiring_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    hiring_tasks = [t for t in tasks if t["type"] == "hiring"]

    documents: List[SourceDocument] = []

    for task in hiring_tasks:
        docs = default_pipeline.fetch(task["query"], "hiring")
        documents.extend(docs)
        task["status"] = "complete"

    return {"raw_documents": documents}