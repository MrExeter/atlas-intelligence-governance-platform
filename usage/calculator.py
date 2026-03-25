from typing import TYPE_CHECKING, Dict, Any

from usage.models import UsageMetrics

if TYPE_CHECKING:
    from usage.tracker import UsageTracker


class CostCalculator:
    """
    Converts recorded usage events into a UsageMetrics summary.
    Depends only on events and a pricing dict — no Atlas internals.
    """

    def __init__(self, pricing: Dict[str, Any]) -> None:
        self._pricing = pricing

    def compute(self, tracker: "UsageTracker") -> UsageMetrics:
        llm_input_tokens = 0
        llm_output_tokens = 0
        llm_cost = 0.0
        models_used = set()

        for event in tracker.llm_events:
            llm_input_tokens += event.input_tokens
            llm_output_tokens += event.output_tokens
            models_used.add(f"{event.provider}:{event.model}")

            key = f"{event.provider}:{event.model}"
            rates = self._pricing.get("llm", {}).get(key, {})
            input_cost = (event.input_tokens / 1000) * rates.get("input_per_1k", 0.0)
            output_cost = (event.output_tokens / 1000) * rates.get("output_per_1k", 0.0)
            llm_cost += input_cost + output_cost

        api_calls = 0
        api_cost = 0.0
        providers_used = set()

        for event in tracker.provider_events:
            api_calls += event.call_count
            providers_used.add(event.provider_name)

            rate = self._pricing.get("api", {}).get(event.provider_name, {})
            api_cost += event.call_count * rate.get("per_call", 0.0)

        return UsageMetrics(
            run_id=tracker.run_id,
            llm_input_tokens=llm_input_tokens,
            llm_output_tokens=llm_output_tokens,
            tokens_used=llm_input_tokens + llm_output_tokens,
            llm_cost_usd=round(llm_cost, 6),
            api_calls=api_calls,
            api_cost_usd=round(api_cost, 6),
            total_cost_usd=round(llm_cost + api_cost, 6),
            latency_ms=round(tracker.elapsed_ms, 1),
            providers_used=sorted(providers_used),
            models_used=sorted(models_used),
        )
