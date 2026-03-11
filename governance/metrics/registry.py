from governance.metrics.source_reliability_metric import SourceReliabilityMetric
from governance.metrics.source_diversity_metric import SourceDiversityMetric


METRIC_REGISTRY = [
    SourceReliabilityMetric(),
    SourceDiversityMetric(),
]
