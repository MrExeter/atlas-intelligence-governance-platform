from typing import Dict, List

from retrieval.base import SourceProvider


class ProviderRegistry:
    def __init__(self) -> None:
        self._providers: Dict[str, SourceProvider] = {}

    def register(self, provider: SourceProvider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str) -> SourceProvider:
        return self._providers[name]

    def all(self) -> List[SourceProvider]:
        return list(self._providers.values())