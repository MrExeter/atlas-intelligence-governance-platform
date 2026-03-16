from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime


class RetrievalStep(BaseModel):
    query: str
    returned_documents: int
    selected_documents: int


class Source(BaseModel):
    url: str
    domain: str
    title: Optional[str] = None
    content: Optional[str] = None


class ReasoningStep(BaseModel):
    step_id: int
    description: str


class ExecutionTrace(BaseModel):
    run_id: str
    timestamp: datetime
    query: str
    research_plan: Optional[str] = None
    retrieval_steps: List[RetrievalStep] = Field(default_factory=list)
    sources: List[Source] = Field(default_factory=list)
    reasoning_steps: List[ReasoningStep] = Field(default_factory=list)
    final_output: str
    domains: List[str]
    unique_domain_count: int
