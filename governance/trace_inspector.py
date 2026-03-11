from typing import List, Set

from models.execution_trace import ExecutionTrace


class TraceInspector:
    """
    Analyzes the ExecutionTrace to produce behavioral metrics
    about how the research agent operated.
    """

    def inspect(self, trace: ExecutionTrace) -> dict:

        retrieval_quality = self._compute_retrieval_quality(trace)
        source_diversity = self._compute_source_diversity(trace)
        research_depth = len(trace.retrieval_steps)

        return {
            "retrieval_quality": retrieval_quality,
            "source_diversity": source_diversity,
            "research_depth": research_depth,
        }

    def _compute_retrieval_quality(self, trace: ExecutionTrace) -> float:
        """
        Measures how effectively the retriever selected useful documents.
        """

        total_returned = 0
        total_selected = 0

        for step in trace.retrieval_steps:
            total_returned += step.returned_documents
            total_selected += step.selected_documents

        if total_returned == 0:
            return 0.0

        return total_selected / total_returned

    def _compute_source_diversity(self, trace: ExecutionTrace) -> float:
        """
        Measures diversity of domains used in sources.
        """

        domains: Set[str] = set()

        for source in trace.sources:
            domains.add(source.domain)

        if len(trace.sources) == 0:
            return 0.0

        return len(domains) / len(trace.sources)
