import os
from typing import List

import httpx

from retrieval.base import SourceProvider
from retrieval.models import RawSource


class TavilyProvider(SourceProvider):
    name = "tavily"
    _BASE_URL = "https://api.tavily.com/search"

    def __init__(self) -> None:
        self._api_key = os.getenv("TAVILY_API_KEY", "")

    def fetch(self, query: str) -> List[RawSource]:
        if not self._api_key:
            return []

        try:
            resp = httpx.post(
                self._BASE_URL,
                json={
                    "api_key": self._api_key,
                    "query": query,
                    "search_depth": "basic",
                    "max_results": 5,
                    "include_raw_content": True,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for r in data.get("results", []):
                content = (r.get("raw_content") or r.get("content", "")).strip()
                if not content:
                    continue
                results.append(
                    RawSource(
                        url=r.get("url", ""),
                        title=r.get("title", ""),
                        content=content,
                        provider=self.name,
                        raw_metadata={"score": r.get("score", 0.0)},
                    )
                )
            return results

        except Exception:
            return []
