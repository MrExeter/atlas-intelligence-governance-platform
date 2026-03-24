from datetime import datetime, UTC

from governance.policy_engine import PolicyEngine
from models.evaluation_result import EvaluationResult, DimensionScores


def _make_evaluation(evidence_coverage, hallucination_rate, overall_score=0.75):
    scores = DimensionScores(
        evidence_coverage=evidence_coverage,
        source_reliability=0.8,
        source_diversity=0.7,
        retrieval_depth=0.5,
        retrieval_relevance=0.8,
        hallucination_rate=hallucination_rate,
        logical_consistency=0.8,
        evidence_density=0.7,
    )
    return EvaluationResult(
        run_id="test_run",
        timestamp=datetime.now(UTC),
        dimension_scores=scores,
        overall_score=overall_score,
    )


engine = PolicyEngine()


def test_pass_high_coverage_low_hallucination():
    decision = engine.evaluate_policy(_make_evaluation(0.9, 0.05, overall_score=0.85))
    assert decision.verdict == "PASS"
    assert decision.violations is None


def test_pass_requires_overall_score_above_threshold():
    # Both dimensions pass but overall score < 0.80 → WARN not PASS
    decision = engine.evaluate_policy(_make_evaluation(0.70, 0.25, overall_score=0.75))
    assert decision.verdict == "WARN"


def test_warn_low_evidence_coverage():
    # coverage in WARN band (0.50–0.65), hallucination fine
    decision = engine.evaluate_policy(_make_evaluation(0.60, 0.25))
    assert decision.verdict == "WARN"
    assert decision.violations is None


def test_warn_elevated_hallucination_rate():
    # hallucination in WARN band (0.35–0.50), coverage fine
    decision = engine.evaluate_policy(_make_evaluation(0.70, 0.40))
    assert decision.verdict == "WARN"
    assert decision.violations is None


def test_fail_insufficient_evidence_coverage():
    decision = engine.evaluate_policy(_make_evaluation(0.45, 0.25))
    assert decision.verdict == "FAIL"
    assert "insufficient_evidence_coverage" in decision.violations


def test_fail_hallucination_rate_exceeded():
    decision = engine.evaluate_policy(_make_evaluation(0.70, 0.55))
    assert decision.verdict == "FAIL"
    assert "hallucination_rate_exceeded" in decision.violations


def test_fail_both_dimensions_bad():
    decision = engine.evaluate_policy(_make_evaluation(0.40, 0.60))
    assert decision.verdict == "FAIL"
    assert "insufficient_evidence_coverage" in decision.violations
    assert "hallucination_rate_exceeded" in decision.violations


def test_boundary_coverage_exactly_at_fail_threshold():
    # 0.50 is NOT a fail (< 0.50 fails)
    decision = engine.evaluate_policy(_make_evaluation(0.50, 0.25))
    assert decision.verdict == "WARN"


def test_boundary_hallucination_exactly_at_fail_threshold():
    # 0.50 is NOT a fail (> 0.50 fails)
    decision = engine.evaluate_policy(_make_evaluation(0.70, 0.50))
    assert decision.verdict == "WARN"