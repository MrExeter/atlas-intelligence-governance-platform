from typing import List

import httpx

from retrieval.base import SourceProvider
from retrieval.models import RawSource


class HackerNewsProvider(SourceProvider):
    name = "hackernews"
    _BASE_URL = "https://hn.algolia.com/api/v1/search"

    def fetch(self, query: str) -> List[RawSource]:
        try:
            resp = httpx.get(
                self._BASE_URL,
                params={"query": query, "tags": "story", "hitsPerPage": 5},
                timeout=10,
            )
            resp.raise_for_status()
            data = resp.json()

            results = []
            for hit in data.get("hits", []):
                url = hit.get("url") or (
                    f"https://news.ycombinator.com/item?id={hit.get('objectID', '')}"
                )
                title = hit.get("title", "").strip()
                content = (hit.get("story_text") or title).strip()

                if not content:
                    continue

                results.append(
                    RawSource(
                        url=url,
                        title=title,
                        content=content,
                        provider=self.name,
                        raw_metadata={
                            "points": hit.get("points", 0),
                            "num_comments": hit.get("num_comments", 0),
                        },
                    )
                )
            return results

        except Exception:
            return []