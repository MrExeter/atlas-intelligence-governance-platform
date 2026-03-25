from fastapi import APIRouter, Depends, HTTPException, Query

from api.schemas.history import RunListResponse, RunSummary
from auth.token_validator import validate_token
from history.factory import get_history_store

router = APIRouter(prefix="/history", tags=["history"])

history_store = get_history_store()


@router.get("/runs", response_model=RunListResponse)
async def list_runs(
    limit: int = Query(default=20, ge=1, le=100),
    invite_token: str = Depends(validate_token),
):
    runs = history_store.list_runs(invite_token, limit=limit)
    return {"runs": runs, "count": len(runs)}


@router.get("/runs/{run_id}", response_model=RunSummary)
async def get_run(run_id: str, invite_token: str = Depends(validate_token)):
    run = history_store.get_run(run_id)
    if run is None:
        raise HTTPException(status_code=404, detail="Run not found")
    return run
