from governance.metrics.base_metric import Metric


class SourceDiversityMetric(Metric):

    name = "source_diversity"

    def compute(self, claims, sources, trace=None):

        if not sources:
            return 0.0

        unique_domains = len(set(sources))

        return min(unique_domains / 5, 1.0)
