from pydantic import BaseModel
from typing import Any, Dict, List, Optional


class ResearchRequest(BaseModel):
    topic: str


class Competitor(BaseModel):
    name: str
    summary: str


class ResearchResponse(BaseModel):

    executive_summary: Optional[str]
    market_overview: Optional[str]
    competitors: Optional[List[Competitor]]
    opportunities: Optional[List[str]]
    risks: Optional[List[str]]

    # performance metadata
    latency: int

    governance_verdict: Optional[str]
    governance_score: Optional[float]
    governance_metrics: Optional[Dict[str, Any]]

    # keep for future extensibility
    metrics: Optional[Dict[str, Any]]

    evidence: Optional[List[Dict[str, Any]]] = None
    evidence_clusters: Optional[List[Dict[str, Any]]] = None
    other_sources: Optional[List[Dict[str, Any]]] = None

