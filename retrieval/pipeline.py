from typing import List
from urllib.parse import urlparse
from uuid import uuid4

from agents.state import SourceDocument
from retrieval.config import AgentConfig
from retrieval.models import RawSource
from retrieval.registry import ProviderRegistry


class RetrievalPipeline:
    def __init__(self, registry: ProviderRegistry, config: AgentConfig) -> None:
        self._registry = registry
        self._config = config

    def providers_for(self, task_type: str) -> List[str]:
        """Return the provider names configured for a task type."""
        return list(self._config.provider_map.get(task_type, []))

    def fetch(self, query: str, task_type: str) -> List[SourceDocument]:
        provider_names = self._config.provider_map.get(task_type, [])
        raw_sources: List[RawSource] = []

        for name in provider_names:
            try:
                provider = self._registry.get(name)
                results = provider.fetch(query)
                raw_sources.extend(results)
            except Exception:
                continue

        return [
            self._normalize(raw, task_type)
            for raw in raw_sources
            if raw.content.strip()
        ]

    def _normalize(self, raw: RawSource, task_type: str) -> SourceDocument:
        domain = urlparse(raw.url).netloc or raw.provider
        return {
            "id": str(uuid4()),
            "title": raw.title,
            "url": raw.url,
            "content": raw.content[:3000],
            "metadata": {
                "source": raw.provider,
                "task_type": task_type,
                "domain": domain,
                **raw.raw_metadata,
            },
        }