from governance.metrics.base_metric import Metric
from governance.source_reliability import get_source_score


class SourceReliabilityMetric(Metric):

    name = "source_reliability"

    def compute(self, claims, sources, trace=None):

        if not sources:
            return 0.0

        scores = [get_source_score(domain) for domain in sources]

        return sum(scores) / len(scores)
