from datetime import datetime, UTC
from typing import List

from claims.claim_model import Claim
from models.evaluation_result import EvaluationResult
from models.policy_decision import PolicyDecision
from models.run_metrics import RunMetrics


class ReliabilityMetrics:
    """
    Converts a completed run into a RunMetrics record
    for long-term reliability tracking.
    """

    def generate_metrics(
        self,
        evaluation: EvaluationResult,
        policy: PolicyDecision,
        claims: List[Claim],
        sources: List[str],
    ) -> RunMetrics:

        total_claims = len(claims)
        supported_claims = len([c for c in claims if c.verified])

        evidence_coverage = (
            supported_claims / total_claims if total_claims > 0 else 0.0
        )

        hallucination_rate = (
            (total_claims - supported_claims) / total_claims
            if total_claims > 0
            else 0.0
        )

        retrieval_relevance = evaluation.dimension_scores.retrieval_relevance

        return RunMetrics(
            run_id=evaluation.run_id,
            timestamp=datetime.now(UTC),
            overall_score=evaluation.overall_score,
            policy_verdict=policy.verdict.value,
            evidence_coverage=evidence_coverage,
            hallucination_rate=hallucination_rate,
            retrieval_relevance=retrieval_relevance,
            sources_used=len(sources),
            claims_evaluated=total_claims,
        )
