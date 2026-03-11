from typing import TypedDict, List, Dict, Any, Optional, Annotated
import operator
from datetime import datetime


class ResearchTask(TypedDict):
    id: str
    type: str  # "market", "funding", "hiring", "competitors"
    query: str
    status: str


class SourceDocument(TypedDict):
    id: str
    title: str
    url: str
    content: str
    metadata: Dict[str, Any]


class AgentMetrics(TypedDict):
    tokens_used: int
    latency_ms: float
    cost_usd: float


class AgentState(TypedDict, total=False):

    # Input
    topic: str

    # Planner output
    tasks: List[ResearchTask]

    # Research phase
    raw_documents: Annotated[list[SourceDocument], operator.add]


    # RAG phase
    retrieved_chunks: List[SourceDocument]

    # Synthesis output
    executive_summary: Optional[str]
    market_overview: Optional[str]
    competitors: Optional[List[Dict[str, Any]]]
    opportunities: Optional[List[str]]
    risks: Optional[List[str]]

    # Evaluation
    eval_scores: Optional[Dict[str, float]]

    # Costs
    tokens_used: int
    cost_usd: float

    # Observability
    metrics: AgentMetrics

    # Lifecycle
    started_at: datetime
    completed_at: Optional[datetime]
