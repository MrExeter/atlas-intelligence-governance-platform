from datetime import datetime, UTC
from typing import List

from claims.claim_model import Claim
from models.evaluation_result import EvaluationResult, DimensionScores
from governance.source_reliability import get_source_score
from governance.metrics.registry import METRIC_REGISTRY


class EvaluationEngine:
    """
    Computes evaluation scores for an Atlas run.
    """

    def evaluate(
        self,
        run_id: str,
        claims: List[Claim],
        sources: List[str],
        retrieval_relevance: float = 0.8,
        logical_consistency: float = 0.8,
    ) -> EvaluationResult:

        total_claims = len(claims)

        if total_claims == 0:
            evidence_coverage = 0.0
            hallucination_rate = 0.0
        else:
            supported = sum(1 for c in claims if c.verified)
            evidence_coverage = supported / total_claims
            hallucination_rate = (total_claims - supported) / total_claims

        retrieval_depth = self._compute_retrieval_depth(sources, claims)

        evidence_density = (
            len(sources) / total_claims if total_claims > 0 else 0.0
        )

        # For using Metric Registry
        metric_values = {}

        for metric in METRIC_REGISTRY:
            metric_values[metric.name] = metric.compute(claims, sources)

        dimension_scores = DimensionScores(
            evidence_coverage=evidence_coverage,
            source_reliability=metric_values.get("source_reliability", 0),
            source_diversity=metric_values.get("source_diversity", 0),
            retrieval_depth=retrieval_depth,
            retrieval_relevance=retrieval_relevance,
            hallucination_rate=hallucination_rate,
            logical_consistency=logical_consistency,
            evidence_density=min(evidence_density, 1.0),
        )

        overall_score = self._compute_overall_score(dimension_scores)

        return EvaluationResult(
            run_id=run_id,
            timestamp=datetime.now(UTC),
            dimension_scores=dimension_scores,
            overall_score=overall_score,
        )


    def _compute_source_reliability(self, sources: List[str]) -> float:
        """
        Compute average reliability score for the domains used.
        """
        if not sources:
            return 0.0

        scores = []

        for domain in sources:
            scores.append(get_source_score(domain))

        return sum(scores) / len(scores)


    def _compute_overall_score(self, scores: DimensionScores) -> float:
        """
        Weighted scoring model.
        """

        overall_score = (
                scores.evidence_coverage * 0.23
                + scores.source_reliability * 0.17
                + scores.source_diversity * 0.10
                + scores.retrieval_depth * 0.10
                + scores.retrieval_relevance * 0.15
                + (1 - scores.hallucination_rate) * 0.20
                + scores.logical_consistency * 0.04
                + scores.evidence_density * 0.01
        )

        return round(overall_score, 3)


    def _compute_source_diversity(self, sources: List[str]) -> float:
        """
        Reward diversity of domains used in research.
        """

        if not sources:
            return 0.0

        unique_domains = len(set(sources))

        # normalize assuming 5 independent sources is strong coverage
        return min(unique_domains / 5, 1.0)


    def _compute_retrieval_depth(self, sources: List[str], claims: List[Claim]) -> float:
        """
        Score depth of research based on sources and claims evaluated.
        """

        if not sources or not claims:
            return 0.0

        source_factor = min(len(set(sources)) / 5, 1.0)
        claim_factor = min(len(claims) / 10, 1.0)

        return (source_factor + claim_factor) / 2
