from abc import ABC, abstractmethod
from typing import List

from retrieval.models import RawSource


class SourceProvider(ABC):
    name: str

    @abstractmethod
    def fetch(self, query: str) -> List[RawSource]:
        """Fetch raw sources for a query. Must not raise — return [] on failure."""
        ...