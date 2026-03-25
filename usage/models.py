from dataclasses import dataclass, field
from typing import List


@dataclass
class LLMEvent:
    provider: str
    model: str
    input_tokens: int
    output_tokens: int
    latency_ms: float = 0.0


@dataclass
class ProviderEvent:
    provider_name: str
    call_count: int = 1
    latency_ms: float = 0.0


@dataclass
class UsageMetrics:
    run_id: str
    llm_input_tokens: int
    llm_output_tokens: int
    tokens_used: int
    llm_cost_usd: float
    api_calls: int
    api_cost_usd: float
    total_cost_usd: float
    latency_ms: float
    providers_used: List[str]
    models_used: List[str]
