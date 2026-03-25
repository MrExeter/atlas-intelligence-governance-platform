from typing import List

from agents.state import AgentState, SourceDocument
from retrieval import default_pipeline
from usage import get_tracker


def competitors_node(state: AgentState) -> AgentState:
    tasks = state.get("tasks", [])
    competitor_tasks = [t for t in tasks if t["type"] == "competitors"]

    documents: List[SourceDocument] = []
    tracker = get_tracker(state.get("run_id", ""))

    for task in competitor_tasks:
        docs = default_pipeline.fetch(task["query"], "competitors")
        documents.extend(docs)
        task["status"] = "complete"
        for provider_name in default_pipeline.providers_for("competitors"):
            tracker.record_provider_call(provider_name)

    return {"raw_documents": documents}
