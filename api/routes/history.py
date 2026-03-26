from fastapi import APIRouter, Depends, HTTPException, Query

from api.schemas.history import RunDetail, RunListResponse, RunSummary
from auth.token_validator import validate_token
from history.factory import get_history_store

router = APIRouter(prefix="/history", tags=["history"])

history_store = get_history_store()


def _flatten(record: dict) -> dict:
    gov = record.get("governance", {})
    met = record.get("metrics", {})
    return {
        **record,
        "governance_score": gov.get("overall_score"),
        "governance_verdict": gov.get("policy_verdict"),
        "total_cost_usd": met.get("total_cost_usd"),
        "tokens_used": met.get("tokens_used"),
        "latency_ms": met.get("latency_ms"),
    }


@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    limit: int = Query(default=20, ge=1, le=100),
    invite_token: str = Depends(validate_token),
):
    runs = history_store.list_runs(invite_token, limit=limit)
    summaries = [_flatten(r) for r in runs if r.get("status") == "completed"]
    return {"runs": summaries, "count": len(summaries)}


@router.get("/runs/{run_id}", response_model=RunDetail)
async def get_run(run_id: str, invite_token: str = Depends(validate_token)):
    run = history_store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
