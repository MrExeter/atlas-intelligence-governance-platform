from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from enum import Enum


class PolicyVerdict(str, Enum):
    PASS = "PASS"
    WARN = "WARN"
    FAIL = "FAIL"


class PolicyDecision(BaseModel):
    run_id: str
    timestamp: datetime

    verdict: PolicyVerdict

    overall_score: float = Field(ge=0.0, le=1.0)

    violations: Optional[List[str]] = None
