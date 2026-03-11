from datetime import datetime, UTC
from typing import List

from models.evaluation_result import EvaluationResult
from models.policy_decision import PolicyDecision, PolicyVerdict


class PolicyEngine:
    """
    Applies governance rules to an EvaluationResult
    and determines PASS / WARN / FAIL.
    """

    def evaluate_policy(self, evaluation: EvaluationResult) -> PolicyDecision:

        violations: List[str] = []

        scores = evaluation.dimension_scores
        overall_score = evaluation.overall_score

        # Critical safeguards
        if scores.hallucination_rate > 0.30:
            violations.append("hallucination_rate_exceeded")

        if scores.evidence_coverage < 0.50:
            violations.append("insufficient_evidence_coverage")

        # Determine verdict
        if violations:
            verdict = PolicyVerdict.FAIL

        elif overall_score >= 0.80:
            verdict = PolicyVerdict.PASS

        elif overall_score >= 0.60:
            verdict = PolicyVerdict.WARN

        else:
            verdict = PolicyVerdict.FAIL

        return PolicyDecision(
            run_id=evaluation.run_id,
            timestamp=datetime.now(UTC),
            verdict=verdict,
            overall_score=overall_score,
            violations=violations if violations else None,
        )
