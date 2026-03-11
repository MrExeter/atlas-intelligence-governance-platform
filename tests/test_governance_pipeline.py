from datetime import datetime, UTC
from email._header_value_parser import Domain

from governance.pipeline import GovernancePipeline
from models.execution_trace import ExecutionTrace, RetrievalStep, Source


def test_governance_pipeline_basic():

    trace = ExecutionTrace(
        run_id="test_run_001",
        timestamp=datetime.now(UTC),
        query="AI startup funding trends",
        research_plan="Investigate funding, hiring, and market growth.",
        retrieval_steps=[
            RetrievalStep(
                query="AI startup funding 2024",
                returned_documents=10,
                selected_documents=5,
            )
        ],
        sources=[
            Source(
                url="https://example.com/ai-funding",
                domain="example.com",
                title="AI Funding Growth"
            )
        ],
        reasoning_steps=[],
        final_output=(
            "AI startup funding increased significantly in 2024. "
            "Several companies raised over $100 million."
        ),
        domains=["example.com"],
        unique_domain_count=1,
    )

    pipeline = GovernancePipeline()

    decision, metrics = pipeline.run(trace)

    assert decision.run_id == trace.run_id
    assert metrics.run_id == trace.run_id

    assert decision.verdict in {"PASS", "WARN", "FAIL"}

    assert 0.0 <= metrics.overall_score <= 1.0
