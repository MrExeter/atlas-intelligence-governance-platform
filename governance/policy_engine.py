from datetime import datetime, UTC
from typing import List, Optional

from models.evaluation_result import EvaluationResult
from models.policy_decision import PolicyDecision, PolicyVerdict


class PolicyEngine:
    """
    Applies governance rules to an EvaluationResult
    and determines PASS / WARN / FAIL.

    Thresholds (per dimension):

    Evidence Coverage:
        < 0.50  → FAIL
        < 0.65  → WARN
        >= 0.65 → PASS

    Hallucination Rate:
        > 0.50  → FAIL
        > 0.35  → WARN
        <= 0.35 → PASS

    Final verdict: worst result across all dimensions.
    If all dimensions PASS, fall back to overall_score for final call.
    """

    def evaluate_policy(self, evaluation: EvaluationResult) -> PolicyDecision:
        scores = evaluation.dimension_scores

        fail_reasons: List[str] = []
        warn_reasons: List[str] = []

        # Evidence coverage
        if scores.evidence_coverage < 0.50:
            fail_reasons.append("insufficient_evidence_coverage")
        elif scores.evidence_coverage < 0.65:
            warn_reasons.append("low_evidence_coverage")

        # Hallucination rate
        if scores.hallucination_rate > 0.50:
            fail_reasons.append("hallucination_rate_exceeded")
        elif scores.hallucination_rate > 0.35:
            warn_reasons.append("elevated_hallucination_rate")

        # Determine verdict — worst dimension wins
        if fail_reasons:
            verdict = PolicyVerdict.FAIL
        elif warn_reasons:
            verdict = PolicyVerdict.WARN
        elif evaluation.overall_score >= 0.80:
            verdict = PolicyVerdict.PASS
        else:
            verdict = PolicyVerdict.WARN

        return PolicyDecision(
            run_id=evaluation.run_id,
            timestamp=datetime.now(UTC),
            verdict=verdict,
            overall_score=evaluation.overall_score,
            violations=fail_reasons if fail_reasons else None,
        )