from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class DimensionScores(BaseModel):
    evidence_coverage: float = Field(ge=0.0, le=1.0)
    source_reliability: float = Field(ge=0.0, le=1.0)
    source_diversity: float = Field(ge=0.0, le=1.0)
    retrieval_depth: float = Field(ge=0.0, le=1.0)
    retrieval_relevance: float = Field(ge=0.0, le=1.0)
    hallucination_rate: float = Field(ge=0.0, le=1.0)
    logical_consistency: float = Field(ge=0.0, le=1.0)
    evidence_density: float = Field(ge=0.0, le=1.0)


class EvaluationResult(BaseModel):
    run_id: str
    timestamp: datetime

    dimension_scores: DimensionScores

    overall_score: float = Field(ge=0.0, le=1.0)

    evaluation_notes: Optional[List[str]] = None
