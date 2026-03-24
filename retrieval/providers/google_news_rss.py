import xml.etree.ElementTree as ET
from typing import List
from urllib.parse import quote_plus

import httpx

from retrieval.base import SourceProvider
from retrieval.models import RawSource


class GoogleNewsRSSProvider(SourceProvider):
    name = "google_news_rss"
    _BASE_URL = "https://news.google.com/rss/search"

    def fetch(self, query: str) -> List[RawSource]:
        url = f"{self._BASE_URL}?q={quote_plus(query)}&hl=en-US&gl=US&ceid=US:en"

        try:
            resp = httpx.get(url, timeout=10, follow_redirects=True)
            resp.raise_for_status()

            root = ET.fromstring(resp.text)
            items = root.findall(".//item")

            results = []
            for item in items[:5]:
                title = item.findtext("title", "").strip()
                link = item.findtext("link", "").strip()
                # description contains a brief snippet; strip HTML tags simply
                desc = item.findtext("description", "").strip()
                desc = ET.tostring(
                    ET.fromstring(f"<d>{desc}</d>"), encoding="unicode", method="text"
                ) if desc else title

                if not link:
                    continue

                results.append(
                    RawSource(
                        url=link,
                        title=title,
                        content=desc or title,
                        provider=self.name,
                    )
                )
            return results

        except Exception:
            return []
