from enum import Enum
from typing import Dict


RISK_KEYS = {
    "hallucination_risk",
}

PASS_THRESHOLD = 0.75
WARN_THRESHOLD = 0.5


class EvalVerdict(str, Enum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


def normalize_scores(scores: Dict[str, float]) -> Dict[str, float]:
    """
    Normalize evaluation scores so that all values follow
    a higher-is-better convention.

    Risk metrics (e.g. hallucination_risk) are inverted.
    """
    normalized = {}

    for key, value in scores.items():
        if key in RISK_KEYS:
            normalized[key] = 1.0 - value
        else:
            normalized[key] = value

    return normalized


def derive_verdict(scores: Dict[str, float]) -> EvalVerdict:
    """
    Derive an overall verdict from evaluation scores.
    Strategy: use the minimum score as the limiting factor.
    """

    if not scores:
        return EvalVerdict.FAIL

    worst_score = min(scores.values())

    if worst_score >= PASS_THRESHOLD:
        return EvalVerdict.PASS

    if worst_score >= WARN_THRESHOLD:
        return EvalVerdict.WARN

    return EvalVerdict.FAIL
