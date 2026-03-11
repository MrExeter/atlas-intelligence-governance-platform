from datetime import datetime, UTC

from governance.policy_engine import PolicyEngine
from models.evaluation_result import EvaluationResult, DimensionScores


def test_policy_engine_pass():
    scores = DimensionScores(
        evidence_coverage=0.9,
        source_reliability=0.8,
        source_diversity=0.7,
        retrieval_depth=0.5,
        retrieval_relevance=0.8,
        hallucination_rate=0.05,
        logical_consistency=0.8,
        evidence_density=0.7,
    )

    evaluation = EvaluationResult(
        run_id="test_run",
        timestamp=datetime.now(UTC),
        dimension_scores=scores,
        overall_score=0.85,
    )

    engine = PolicyEngine()

    decision = engine.evaluate_policy(evaluation)

    assert decision.verdict == "PASS"
