from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class RunSummary(BaseModel):
    """Summary fields returned by GET /history/runs (list view)."""
    run_id: str
    timestamp: str
    topic: str
    invite_token: Optional[str]
    status: str

    governance: Dict[str, Any]
    metrics: Dict[str, Any]

    governance_score: Optional[float] = None
    governance_verdict: Optional[str] = None
    total_cost_usd: Optional[float] = None
    tokens_used: Optional[int] = None
    latency_ms: Optional[int] = None


class RunDetail(RunSummary):
    """Full record returned by GET /history/runs/{run_id} (detail view)."""
    result: Optional[Dict[str, Any]] = None
    evidence: Optional[List[Dict[str, Any]]] = None
    evidence_clusters: Optional[List[Dict[str, Any]]] = None
    other_sources: Optional[List[Dict[str, Any]]] = None


class RunListResponse(BaseModel):
    runs: List[RunSummary]
    count: int
