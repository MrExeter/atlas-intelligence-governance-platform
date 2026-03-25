from typing import Any, Dict, List, Optional
from pydantic import BaseModel


class RunSummary(BaseModel):
    run_id: str
    timestamp: str
    topic: str
    invite_token: Optional[str]
    status: str
    governance: Dict[str, Any]
    metrics: Dict[str, Any]


class RunListResponse(BaseModel):
    runs: List[RunSummary]
    count: int
