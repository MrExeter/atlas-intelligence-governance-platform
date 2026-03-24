import os
from typing import List

import httpx

from retrieval.base import SourceProvider
from retrieval.models import RawSource


class NewsDataProvider(SourceProvider):
    name = "newsdata"
    _BASE_URL = "https://newsdata.io/api/1/latest"

    def __init__(self) -> None:
        self._api_key = os.getenv("NEWSDATA_API_KEY", "")

    def fetch(self, query: str) -> List[RawSource]:
        if not self._api_key:
            return []

        try:
            resp = httpx.get(
                self._BASE_URL,
                params={
                    "apikey": self._api_key,
                    "q": query,
                    "language": "en",
                    "full_content": 1,
                },
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for article in data.get("results", [])[:5]:
                # Prefer full content, fall back to description snippet
                content = (
                    article.get("content")
                    or article.get("description")
                    or ""
                ).strip()

                url = article.get("link", "").strip()

                if not content or not url:
                    continue

                results.append(
                    RawSource(
                        url=url,
                        title=article.get("title", "").strip(),
                        content=content,
                        provider=self.name,
                        raw_metadata={"source_id": article.get("source_id", "")},
                    )
                )
            return results

        except Exception:
            return []
