from abc import ABC, abstractmethod


class Metric(ABC):
    """
    Base class for evaluation metrics.
    """

    name: str

    @abstractmethod
    def compute(self, claims, sources, trace=None) -> float:
        pass
