from pydantic import BaseModel, Field
from typing import List, Optional
from enum import Enum


class ClaimType(str, Enum):
    FACT = "fact"
    STATISTIC = "statistic"
    INFERENCE = "inference"
    PREDICTION = "prediction"


class Claim(BaseModel):
    claim_id: str
    text: str
    claim_type: ClaimType
    supporting_sources: Optional[List[str]] = None
    verified: Optional[bool] = None
    support_score: Optional[float] = None
