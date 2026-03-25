import logging
import time
import uuid
from datetime import UTC, datetime

from fastapi import APIRouter, Depends

from agents.graph import build_graph
from api.middleware.rate_limit import rate_limit
from api.schemas.research import ResearchRequest, ResearchResponse
from auth.token_validator import validate_token
from governance.pipeline import GovernancePipeline
from governance.trace_builder import build_execution_trace
from usage import create_tracker, finish_run

logger = logging.getLogger("atlas")

router = APIRouter(prefix="/research", tags=["research"])

graph = build_graph()
governance_pipeline = GovernancePipeline()


@router.post(
    "/run",
    response_model=ResearchResponse,
    dependencies=[Depends(rate_limit)],
)
async def run_research(req: ResearchRequest, _: None = Depends(validate_token)):
# async def run_research(req: ResearchRequest):
    run_id = str(uuid.uuid4())
    start_time = time.time()

    create_tracker(run_id)

    initial_state = {
        "run_id": run_id,
        "topic": req.topic,
        "raw_documents": [],
        "retrieved_chunks": [],
        "started_at": datetime.now(UTC),
    }

    result = graph.invoke(initial_state)
    trace = build_execution_trace(result, req.topic)

    # Run governance pipeline
    decision, governance_metrics = governance_pipeline.run(trace)

    # Finalise usage tracking
    usage_metrics = finish_run(run_id)
    latency_ms = int((time.time() - start_time) * 1000)

    logger.info(
        {
            "topic": req.topic,
            "governance_verdict": decision.verdict,
            "governance_score": decision.overall_score,
            "latency_ms": latency_ms,
            "tokens_used": usage_metrics.tokens_used,
            "total_cost_usd": usage_metrics.total_cost_usd,
        }
    )

    return {
        "executive_summary": result.get("executive_summary"),
        "market_overview": result.get("market_overview"),
        "competitors": result.get("competitors"),
        "opportunities": result.get("opportunities"),
        "risks": result.get("risks"),
        "latency": latency_ms,
        "governance_verdict": decision.verdict,
        "governance_score": decision.overall_score,
        "governance_metrics": governance_metrics.model_dump(),
        "metrics": {
            "tokens_used": usage_metrics.tokens_used,
            "llm_input_tokens": usage_metrics.llm_input_tokens,
            "llm_output_tokens": usage_metrics.llm_output_tokens,
            "llm_cost_usd": usage_metrics.llm_cost_usd,
            "api_calls": usage_metrics.api_calls,
            "api_cost_usd": usage_metrics.api_cost_usd,
            "total_cost_usd": usage_metrics.total_cost_usd,
            "latency_ms": latency_ms,
            "providers_used": usage_metrics.providers_used,
            "models_used": usage_metrics.models_used,
        },
    }
