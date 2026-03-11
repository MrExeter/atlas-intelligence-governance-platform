from pydantic import BaseModel, Field
from datetime import datetime


class RunMetrics(BaseModel):
    run_id: str
    timestamp: datetime

    overall_score: float = Field(ge=0.0, le=1.0)

    policy_verdict: str

    evidence_coverage: float = Field(ge=0.0, le=1.0)
    hallucination_rate: float = Field(ge=0.0, le=1.0)
    retrieval_relevance: float = Field(ge=0.0, le=1.0)

    sources_used: int = Field(ge=0)
    claims_evaluated: int = Field(ge=0)
