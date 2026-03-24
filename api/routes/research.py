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

logger = logging.getLogger("atlas")

router = APIRouter(prefix="/research", tags=["research"])

graph = build_graph()
governance_pipeline = GovernancePipeline()


@router.post(
    "/run",
    response_model=ResearchResponse,
    dependencies=[Depends(rate_limit)],
)
# async def run_research(req: ResearchRequest, _: None = Depends(validate_token)):
async def run_research(req: ResearchRequest):
    start_time = time.time()

    initial_state = {
        "topic": req.topic,
        "raw_documents": [],
        "retrieved_chunks": [],
        "started_at": datetime.now(UTC),
        "metrics": {
            "tokens_used": 0,
            "latency_ms": 0.0,
            "cost_usd": 0.0,
        },
    }

    result = graph.invoke(initial_state)
    trace = build_execution_trace(result, req.topic)



    # Run governance pipeline
    decision, governance_metrics = governance_pipeline.run(trace)

    # Runtime metrics
    latency_ms = int((time.time() - start_time) * 1000)
    runtime_metrics = result.get("metrics", {})
    runtime_metrics["latency_ms"] = latency_ms

    logger.info(
        {
            "topic": req.topic,
            "governance_verdict": decision.verdict,
            "governance_score": decision.overall_score,
            "latency_ms": latency_ms,
            "tokens_used": runtime_metrics.get("tokens_used"),
            "cost_usd": runtime_metrics.get("cost_usd"),
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
        "metrics": runtime_metrics,
    }