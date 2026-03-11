from typing import List

from agents.state import AgentState, SourceDocument


def rag_node(state: AgentState) -> AgentState:
    """
    Temporary RAG node.

    Later this becomes:
    - chunking
    - embeddings
    - hybrid retrieval
    - reranking

    For now: pass through top documents.
    """

    documents = state.get("raw_documents", [])

    # Simple relevance heuristic (placeholder)
    retrieved: List[SourceDocument] = documents[:5]

    return {
        "retrieved_chunks": retrieved
    }
