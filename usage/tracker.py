import threading
import time
from typing import Dict, List, Optional

from usage.models import LLMEvent, ProviderEvent, UsageMetrics
from usage.calculator import CostCalculator
from usage.pricing import PRICING


# ---------------------------------------------------------------------------
# Internal registry — never import _registry outside this module
# ---------------------------------------------------------------------------

_registry: Dict[str, "UsageTracker"] = {}
_registry_lock = threading.Lock()


def create_tracker(run_id: str) -> "UsageTracker":
    """Create and register a tracker for a new run."""
    with _registry_lock:
        tracker = UsageTracker(run_id)
        _registry[run_id] = tracker
        return tracker


def get_tracker(run_id: str) -> "UsageTracker":
    """Return the tracker for run_id, or a no-op tracker if not found."""
    with _registry_lock:
        return _registry.get(run_id, _NoOpTracker())


def finish_run(run_id: str) -> UsageMetrics:
    """Finalise the run, compute metrics, remove from registry, return UsageMetrics."""
    with _registry_lock:
        tracker = _registry.pop(run_id, None)

    if tracker is None:
        return _empty_metrics(run_id)

    tracker._end_time = time.monotonic()
    calculator = CostCalculator(PRICING)
    return calculator.compute(tracker)


# ---------------------------------------------------------------------------
# UsageTracker
# ---------------------------------------------------------------------------

class UsageTracker:
    def __init__(self, run_id: str) -> None:
        self.run_id = run_id
        self._llm_events: List[LLMEvent] = []
        self._provider_events: List[ProviderEvent] = []
        self._start_time: float = time.monotonic()
        self._end_time: Optional[float] = None
        self._lock = threading.Lock()

    def record_llm_call(
        self,
        provider: str,
        model: str,
        input_tokens: int,
        output_tokens: int,
        latency_ms: float = 0.0,
    ) -> None:
        event = LLMEvent(
            provider=provider,
            model=model,
            input_tokens=input_tokens,
            output_tokens=output_tokens,
            latency_ms=latency_ms,
        )
        with self._lock:
            self._llm_events.append(event)

    def record_provider_call(
        self,
        provider_name: str,
        call_count: int = 1,
        latency_ms: float = 0.0,
    ) -> None:
        event = ProviderEvent(
            provider_name=provider_name,
            call_count=call_count,
            latency_ms=latency_ms,
        )
        with self._lock:
            self._provider_events.append(event)

    @property
    def llm_events(self) -> List[LLMEvent]:
        with self._lock:
            return list(self._llm_events)

    @property
    def provider_events(self) -> List[ProviderEvent]:
        with self._lock:
            return list(self._provider_events)

    @property
    def elapsed_ms(self) -> float:
        end = self._end_time or time.monotonic()
        return (end - self._start_time) * 1000


# ---------------------------------------------------------------------------
# _NoOpTracker — returned when run_id is not found, silently discards events
# ---------------------------------------------------------------------------

class _NoOpTracker(UsageTracker):
    def __init__(self) -> None:
        super().__init__(run_id="noop")

    def record_llm_call(self, *args, **kwargs) -> None:
        pass

    def record_provider_call(self, *args, **kwargs) -> None:
        pass


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _empty_metrics(run_id: str) -> UsageMetrics:
    return UsageMetrics(
        run_id=run_id,
        llm_input_tokens=0,
        llm_output_tokens=0,
        tokens_used=0,
        llm_cost_usd=0.0,
        api_calls=0,
        api_cost_usd=0.0,
        total_cost_usd=0.0,
        latency_ms=0.0,
        providers_used=[],
        models_used=[],
    )
