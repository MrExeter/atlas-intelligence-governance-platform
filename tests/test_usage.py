"""
Tests for the usage tracking module.

Covers:
- UsageTracker: record LLM calls, record provider calls, thread safety
- Registry: create, get, finish, cleanup, NoOp fallback
- PricingTable: structure validation
- CostCalculator: LLM cost, API cost, totals, unknown providers
- UsageMetrics: field correctness
"""

import threading

import pytest

from usage.models import LLMEvent, ProviderEvent, UsageMetrics
from usage.pricing import PRICING
from usage.calculator import CostCalculator
from usage.tracker import (
    UsageTracker,
    _NoOpTracker,
    create_tracker,
    get_tracker,
    finish_run,
    _registry,
    _registry_lock,
)


# ---------------------------------------------------------------------------
# UsageTracker
# ---------------------------------------------------------------------------

class TestUsageTracker:

    def test_records_llm_call(self):
        tracker = UsageTracker("run-1")
        tracker.record_llm_call("openai", "gpt-4o-mini", 500, 150)

        events = tracker.llm_events
        assert len(events) == 1
        assert events[0].provider == "openai"
        assert events[0].model == "gpt-4o-mini"
        assert events[0].input_tokens == 500
        assert events[0].output_tokens == 150

    def test_records_provider_call(self):
        tracker = UsageTracker("run-2")
        tracker.record_provider_call("tavily")

        events = tracker.provider_events
        assert len(events) == 1
        assert events[0].provider_name == "tavily"
        assert events[0].call_count == 1

    def test_records_multiple_events(self):
        tracker = UsageTracker("run-3")
        tracker.record_llm_call("openai", "gpt-4o-mini", 300, 100)
        tracker.record_llm_call("openai", "gpt-4o-mini", 400, 120)
        tracker.record_provider_call("tavily")
        tracker.record_provider_call("newsdata")

        assert len(tracker.llm_events) == 2
        assert len(tracker.provider_events) == 2

    def test_thread_safe_concurrent_recording(self):
        tracker = UsageTracker("run-thread")
        errors = []

        def record():
            try:
                for _ in range(50):
                    tracker.record_llm_call("openai", "gpt-4o-mini", 100, 50)
                    tracker.record_provider_call("tavily")
            except Exception as e:
                errors.append(e)

        threads = [threading.Thread(target=record) for _ in range(10)]
        for t in threads:
            t.start()
        for t in threads:
            t.join()

        assert errors == []
        assert len(tracker.llm_events) == 500
        assert len(tracker.provider_events) == 500

    def test_elapsed_ms_increases_over_time(self):
        import time
        tracker = UsageTracker("run-elapsed")
        time.sleep(0.05)
        assert tracker.elapsed_ms >= 40  # allow some tolerance


# ---------------------------------------------------------------------------
# Registry
# ---------------------------------------------------------------------------

class TestRegistry:

    def _cleanup(self, run_id: str):
        with _registry_lock:
            _registry.pop(run_id, None)

    def test_create_and_get_tracker(self):
        run_id = "reg-test-1"
        try:
            tracker = create_tracker(run_id)
            retrieved = get_tracker(run_id)
            assert tracker is retrieved
        finally:
            self._cleanup(run_id)

    def test_get_unknown_run_id_returns_noop(self):
        tracker = get_tracker("nonexistent-run-id")
        assert isinstance(tracker, _NoOpTracker)

    def test_finish_run_removes_from_registry(self):
        run_id = "reg-test-2"
        create_tracker(run_id)
        finish_run(run_id)
        with _registry_lock:
            assert run_id not in _registry

    def test_finish_run_returns_usage_metrics(self):
        run_id = "reg-test-3"
        tracker = create_tracker(run_id)
        tracker.record_llm_call("openai", "gpt-4o-mini", 400, 100)
        tracker.record_provider_call("tavily")
        metrics = finish_run(run_id)
        assert isinstance(metrics, UsageMetrics)
        assert metrics.run_id == run_id
        assert metrics.tokens_used == 500

    def test_finish_run_unknown_id_returns_empty_metrics(self):
        metrics = finish_run("never-created")
        assert isinstance(metrics, UsageMetrics)
        assert metrics.tokens_used == 0
        assert metrics.total_cost_usd == 0.0

    def test_noop_tracker_does_not_raise(self):
        noop = _NoOpTracker()
        noop.record_llm_call("openai", "gpt-4o-mini", 100, 50)
        noop.record_provider_call("tavily")
        assert noop.llm_events == []
        assert noop.provider_events == []


# ---------------------------------------------------------------------------
# PricingTable
# ---------------------------------------------------------------------------

class TestPricingTable:

    def test_has_llm_section(self):
        assert "llm" in PRICING

    def test_has_api_section(self):
        assert "api" in PRICING

    def test_gpt4o_mini_rates_correct(self):
        rates = PRICING["llm"]["openai:gpt-4o-mini"]
        assert rates["input_per_1k"] == 0.00015
        assert rates["output_per_1k"] == 0.00060

    def test_tavily_rate_correct(self):
        assert PRICING["api"]["tavily"]["per_call"] == 0.004

    def test_free_providers_have_zero_cost(self):
        assert PRICING["api"]["google_news_rss"]["per_call"] == 0.0
        assert PRICING["api"]["hackernews"]["per_call"] == 0.0

    def test_no_imports_or_logic(self):
        # PRICING is a plain dict — verifiable by checking its type
        assert isinstance(PRICING, dict)
        assert isinstance(PRICING["llm"], dict)
        assert isinstance(PRICING["api"], dict)


# ---------------------------------------------------------------------------
# CostCalculator
# ---------------------------------------------------------------------------

class TestCostCalculator:

    def _make_tracker(self, run_id="calc-test"):
        return UsageTracker(run_id)

    def test_llm_cost_calculated_correctly(self):
        tracker = self._make_tracker()
        # 1000 input tokens + 500 output tokens for gpt-4o-mini
        tracker.record_llm_call("openai", "gpt-4o-mini", 1000, 500)

        calc = CostCalculator(PRICING)
        metrics = calc.compute(tracker)

        expected_llm = (1000 / 1000) * 0.00015 + (500 / 1000) * 0.00060
        assert abs(metrics.llm_cost_usd - expected_llm) < 1e-9

    def test_api_cost_calculated_correctly(self):
        tracker = self._make_tracker()
        tracker.record_provider_call("tavily")  # $0.004
        tracker.record_provider_call("newsdata")  # $0.001

        calc = CostCalculator(PRICING)
        metrics = calc.compute(tracker)

        assert abs(metrics.api_cost_usd - 0.005) < 1e-9

    def test_free_providers_add_zero_cost(self):
        tracker = self._make_tracker()
        tracker.record_provider_call("google_news_rss")
        tracker.record_provider_call("hackernews")

        calc = CostCalculator(PRICING)
        metrics = calc.compute(tracker)

        assert metrics.api_cost_usd == 0.0

    def test_total_cost_is_sum(self):
        tracker = self._make_tracker()
        tracker.record_llm_call("openai", "gpt-4o-mini", 1000, 500)
        tracker.record_provider_call("tavily")

        calc = CostCalculator(PRICING)
        metrics = calc.compute(tracker)

        assert abs(metrics.total_cost_usd - (metrics.llm_cost_usd + metrics.api_cost_usd)) < 1e-9

    def test_unknown_provider_adds_zero_cost(self):
        tracker = self._make_tracker()
        tracker.record_provider_call("unknown_provider")

        calc = CostCalculator(PRICING)
        metrics = calc.compute(tracker)

        assert metrics.api_cost_usd == 0.0

    def test_tokens_used_is_input_plus_output(self):
        tracker = self._make_tracker()
        tracker.record_llm_call("openai", "gpt-4o-mini", 400, 150)

        calc = CostCalculator(PRICING)
        metrics = calc.compute(tracker)

        assert metrics.tokens_used == 550
        assert metrics.llm_input_tokens == 400
        assert metrics.llm_output_tokens == 150

    def test_providers_and_models_lists_populated(self):
        tracker = self._make_tracker()
        tracker.record_llm_call("openai", "gpt-4o-mini", 100, 50)
        tracker.record_provider_call("tavily")
        tracker.record_provider_call("newsdata")

        calc = CostCalculator(PRICING)
        metrics = calc.compute(tracker)

        assert "openai:gpt-4o-mini" in metrics.models_used
        assert "tavily" in metrics.providers_used
        assert "newsdata" in metrics.providers_used

    def test_empty_tracker_returns_zero_metrics(self):
        tracker = self._make_tracker()
        calc = CostCalculator(PRICING)
        metrics = calc.compute(tracker)

        assert metrics.tokens_used == 0
        assert metrics.total_cost_usd == 0.0
        assert metrics.providers_used == []
        assert metrics.models_used == []
