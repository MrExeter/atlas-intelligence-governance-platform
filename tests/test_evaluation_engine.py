from governance.evaluation_engine import EvaluationEngine
from claims.claim_model import Claim, ClaimType


def test_evaluation_engine_scoring():
    claims = [
        Claim(
            claim_id="c1",
            text="Claim A",
            claim_type=ClaimType.FACT,
            verified=True,
            support_score=1.0,
        ),
        Claim(
            claim_id="c2",
            text="Claim B",
            claim_type=ClaimType.FACT,
            verified=False,
            support_score=0.0,
        ),
    ]

    sources = [
        "https://example.com/source1",
        "https://example.com/source2",
    ]

    engine = EvaluationEngine()

    result = engine.evaluate(
        run_id="test_run",
        claims=claims,
        sources=sources,
    )

    assert 0.0 <= result.overall_score <= 1.0
    assert result.dimension_scores.evidence_coverage == 0.5
