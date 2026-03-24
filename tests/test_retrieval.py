"""
Tests for the retrieval provider architecture.

Covers:
- TavilyProvider: successful fetch, empty API key, HTTP error
- GoogleNewsRSSProvider: successful fetch, malformed XML
- HackerNewsProvider: successful fetch, HTTP error
- NewsDataProvider: successful fetch, empty API key, HTTP error, missing fields
- RetrievalPipeline: normalization, task-type routing, empty-content filtering
- rag_node: relevance scoring, empty-content filtering
- Research nodes: wiring to default_pipeline
"""

import json
import xml.etree.ElementTree as ET
from unittest.mock import MagicMock, patch

import pytest

from retrieval.models import RawSource
from retrieval.providers.newsdata import NewsDataProvider
from retrieval.providers.tavily import TavilyProvider
from retrieval.providers.google_news_rss import GoogleNewsRSSProvider
from retrieval.providers.hackernews import HackerNewsProvider
from retrieval.registry import ProviderRegistry
from retrieval.config import AgentConfig
from retrieval.pipeline import RetrievalPipeline
from rag.retriever import rag_node


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _make_httpx_response(status_code: int, body):
    resp = MagicMock()
    resp.status_code = status_code
    if isinstance(body, str):
        resp.text = body
        resp.json.return_value = json.loads(body)
    else:
        resp.text = json.dumps(body)
        resp.json.return_value = body
    resp.raise_for_status = MagicMock(
        side_effect=None if status_code < 400 else Exception(f"HTTP {status_code}")
    )
    return resp


# ---------------------------------------------------------------------------
# TavilyProvider
# ---------------------------------------------------------------------------

class TestTavilyProvider:

    def test_returns_sources_on_success(self, monkeypatch):
        monkeypatch.setenv("TAVILY_API_KEY", "test-key")

        payload = {
            "results": [
                {"url": "https://example.com/a", "title": "Article A", "content": "Content about AI agents.", "score": 0.9},
                {"url": "https://example.com/b", "title": "Article B", "content": "More AI content.", "score": 0.7},
            ]
        }
        mock_resp = _make_httpx_response(200, payload)

        with patch("retrieval.providers.tavily.httpx.post", return_value=mock_resp):
            provider = TavilyProvider()
            results = provider.fetch("AI agents")

        assert len(results) == 2
        assert all(isinstance(r, RawSource) for r in results)
        assert results[0].url == "https://example.com/a"
        assert results[0].provider == "tavily"
        assert results[0].raw_metadata["score"] == 0.9

    def test_returns_empty_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("TAVILY_API_KEY", raising=False)
        provider = TavilyProvider()
        assert provider.fetch("anything") == []

    def test_returns_empty_on_http_error(self, monkeypatch):
        monkeypatch.setenv("TAVILY_API_KEY", "test-key")
        with patch("retrieval.providers.tavily.httpx.post", side_effect=Exception("timeout")):
            provider = TavilyProvider()
            assert provider.fetch("AI agents") == []

    def test_skips_results_with_empty_content(self, monkeypatch):
        monkeypatch.setenv("TAVILY_API_KEY", "test-key")
        payload = {
            "results": [
                {"url": "https://example.com/a", "title": "Article A", "content": "", "score": 0.9},
                {"url": "https://example.com/b", "title": "Article B", "content": "Real content.", "score": 0.7},
            ]
        }
        mock_resp = _make_httpx_response(200, payload)

        with patch("retrieval.providers.tavily.httpx.post", return_value=mock_resp):
            provider = TavilyProvider()
            results = provider.fetch("AI agents")

        assert len(results) == 1
        assert results[0].url == "https://example.com/b"


# ---------------------------------------------------------------------------
# GoogleNewsRSSProvider
# ---------------------------------------------------------------------------

RSS_XML = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Google News</title>
    <item>
      <title>AI startup raises $50M</title>
      <link>https://techcrunch.com/ai-startup</link>
      <description>An AI startup raised $50M in Series B.</description>
    </item>
    <item>
      <title>New LLM benchmark released</title>
      <link>https://venturebeat.com/llm-benchmark</link>
      <description>Researchers released a new LLM evaluation benchmark.</description>
    </item>
  </channel>
</rss>"""


class TestGoogleNewsRSSProvider:

    def test_returns_sources_on_success(self):
        mock_resp = MagicMock()
        mock_resp.text = RSS_XML
        mock_resp.raise_for_status = MagicMock()

        with patch("retrieval.providers.google_news_rss.httpx.get", return_value=mock_resp):
            provider = GoogleNewsRSSProvider()
            results = provider.fetch("AI funding")

        assert len(results) == 2
        assert results[0].url == "https://techcrunch.com/ai-startup"
        assert results[0].title == "AI startup raises $50M"
        assert results[0].provider == "google_news_rss"

    def test_returns_empty_on_http_error(self):
        with patch("retrieval.providers.google_news_rss.httpx.get", side_effect=Exception("timeout")):
            provider = GoogleNewsRSSProvider()
            assert provider.fetch("AI funding") == []

    def test_returns_empty_on_malformed_xml(self):
        mock_resp = MagicMock()
        mock_resp.text = "this is not xml <<<<"
        mock_resp.raise_for_status = MagicMock()

        with patch("retrieval.providers.google_news_rss.httpx.get", return_value=mock_resp):
            provider = GoogleNewsRSSProvider()
            assert provider.fetch("AI funding") == []


# ---------------------------------------------------------------------------
# HackerNewsProvider
# ---------------------------------------------------------------------------

HN_PAYLOAD = {
    "hits": [
        {
            "objectID": "12345",
            "url": "https://example.com/hn-article",
            "title": "Ask HN: Who is hiring? (March 2025)",
            "story_text": "Companies hiring AI engineers this quarter.",
            "points": 300,
            "num_comments": 150,
        },
        {
            "objectID": "67890",
            "url": None,  # no URL — should fall back to HN item link
            "title": "Show HN: New AI tool for research",
            "story_text": "We built an AI research tool.",
            "points": 120,
            "num_comments": 45,
        },
    ]
}


class TestHackerNewsProvider:

    def test_returns_sources_on_success(self):
        mock_resp = _make_httpx_response(200, HN_PAYLOAD)

        with patch("retrieval.providers.hackernews.httpx.get", return_value=mock_resp):
            provider = HackerNewsProvider()
            results = provider.fetch("AI hiring")

        assert len(results) == 2
        assert results[0].url == "https://example.com/hn-article"
        assert results[0].provider == "hackernews"
        assert results[0].raw_metadata["points"] == 300

    def test_falls_back_to_hn_url_when_no_article_url(self):
        mock_resp = _make_httpx_response(200, HN_PAYLOAD)

        with patch("retrieval.providers.hackernews.httpx.get", return_value=mock_resp):
            provider = HackerNewsProvider()
            results = provider.fetch("AI hiring")

        assert "news.ycombinator.com/item?id=67890" in results[1].url

    def test_returns_empty_on_http_error(self):
        with patch("retrieval.providers.hackernews.httpx.get", side_effect=Exception("timeout")):
            provider = HackerNewsProvider()
            assert provider.fetch("AI hiring") == []


# ---------------------------------------------------------------------------
# NewsDataProvider
# ---------------------------------------------------------------------------

NEWSDATA_PAYLOAD = {
    "status": "success",
    "results": [
        {
            "title": "AI drone market to reach $51B by 2033",
            "link": "https://techcrunch.com/ai-drones-market",
            "content": "The global AI in drones market is projected to reach USD 51 billion by 2033, growing at a CAGR of 17.9%. Military and agricultural applications are driving adoption.",
            "description": "AI drone market growth overview.",
            "source_id": "techcrunch",
        },
        {
            "title": "DJI leads autonomous drone segment",
            "link": "https://venturebeat.com/dji-autonomous",
            "content": "DJI continues to dominate the consumer and commercial drone market, integrating advanced AI navigation and obstacle avoidance systems.",
            "description": "DJI market leadership analysis.",
            "source_id": "venturebeat",
        },
    ],
}


class TestNewsDataProvider:

    def test_returns_sources_on_success(self, monkeypatch):
        monkeypatch.setenv("NEWSDATA_API_KEY", "test-key")
        mock_resp = _make_httpx_response(200, NEWSDATA_PAYLOAD)

        with patch("retrieval.providers.newsdata.httpx.get", return_value=mock_resp):
            provider = NewsDataProvider()
            results = provider.fetch("AI drones market")

        assert len(results) == 2
        assert all(isinstance(r, RawSource) for r in results)
        assert results[0].url == "https://techcrunch.com/ai-drones-market"
        assert results[0].provider == "newsdata"
        assert "51 billion" in results[0].content

    def test_prefers_full_content_over_description(self, monkeypatch):
        monkeypatch.setenv("NEWSDATA_API_KEY", "test-key")
        payload = {
            "results": [{
                "title": "Article",
                "link": "https://example.com/article",
                "content": "This is the full article content with much more detail.",
                "description": "Short snippet.",
                "source_id": "example",
            }]
        }
        mock_resp = _make_httpx_response(200, payload)

        with patch("retrieval.providers.newsdata.httpx.get", return_value=mock_resp):
            provider = NewsDataProvider()
            results = provider.fetch("AI")

        assert "full article content" in results[0].content

    def test_falls_back_to_description_when_no_content(self, monkeypatch):
        monkeypatch.setenv("NEWSDATA_API_KEY", "test-key")
        payload = {
            "results": [{
                "title": "Article",
                "link": "https://example.com/article",
                "content": None,
                "description": "Short snippet only.",
                "source_id": "example",
            }]
        }
        mock_resp = _make_httpx_response(200, payload)

        with patch("retrieval.providers.newsdata.httpx.get", return_value=mock_resp):
            provider = NewsDataProvider()
            results = provider.fetch("AI")

        assert results[0].content == "Short snippet only."

    def test_returns_empty_when_no_api_key(self, monkeypatch):
        monkeypatch.delenv("NEWSDATA_API_KEY", raising=False)
        provider = NewsDataProvider()
        assert provider.fetch("AI drones") == []

    def test_returns_empty_on_http_error(self, monkeypatch):
        monkeypatch.setenv("NEWSDATA_API_KEY", "test-key")
        with patch("retrieval.providers.newsdata.httpx.get", side_effect=Exception("timeout")):
            provider = NewsDataProvider()
            assert provider.fetch("AI drones") == []

    def test_skips_articles_with_no_url(self, monkeypatch):
        monkeypatch.setenv("NEWSDATA_API_KEY", "test-key")
        payload = {
            "results": [
                {"title": "No URL", "link": "", "content": "Some content.", "source_id": "x"},
                {"title": "Has URL", "link": "https://example.com", "content": "Good content.", "source_id": "y"},
            ]
        }
        mock_resp = _make_httpx_response(200, payload)

        with patch("retrieval.providers.newsdata.httpx.get", return_value=mock_resp):
            provider = NewsDataProvider()
            results = provider.fetch("AI")

        assert len(results) == 1
        assert results[0].url == "https://example.com"


# ---------------------------------------------------------------------------
# RetrievalPipeline
# ---------------------------------------------------------------------------

def _make_provider(name: str, sources):
    provider = MagicMock()
    provider.name = name
    provider.fetch.return_value = sources
    return provider


class TestRetrievalPipeline:

    def _build_pipeline(self, providers, provider_map=None):
        registry = ProviderRegistry()
        for p in providers:
            registry.register(p)
        config = AgentConfig(
            provider_map=provider_map or {
                "market": ["mock_provider"],
                "funding": ["mock_provider"],
            }
        )
        return RetrievalPipeline(registry, config)

    def test_normalizes_raw_source_to_source_document(self):
        raw = RawSource(url="https://techcrunch.com/article", title="TC Article", content="Some content.", provider="mock_provider")
        provider = _make_provider("mock_provider", [raw])
        pipeline = self._build_pipeline([provider])

        docs = pipeline.fetch("AI tools", "market")

        assert len(docs) == 1
        doc = docs[0]
        assert doc["url"] == "https://techcrunch.com/article"
        assert doc["title"] == "TC Article"
        assert doc["content"] == "Some content."
        assert doc["metadata"]["source"] == "mock_provider"
        assert doc["metadata"]["domain"] == "techcrunch.com"
        assert doc["metadata"]["task_type"] == "market"
        assert "id" in doc

    def test_filters_out_empty_content(self):
        sources = [
            RawSource(url="https://a.com", title="A", content="  ", provider="mock_provider"),
            RawSource(url="https://b.com", title="B", content="Real content.", provider="mock_provider"),
        ]
        provider = _make_provider("mock_provider", sources)
        pipeline = self._build_pipeline([provider])

        docs = pipeline.fetch("query", "market")

        assert len(docs) == 1
        assert docs[0]["url"] == "https://b.com"

    def test_truncates_content_to_3000_chars(self):
        long_content = "x" * 5000
        raw = RawSource(url="https://a.com", title="A", content=long_content, provider="mock_provider")
        provider = _make_provider("mock_provider", [raw])
        pipeline = self._build_pipeline([provider])

        docs = pipeline.fetch("query", "market")

        assert len(docs[0]["content"]) == 3000

    def test_routes_to_correct_providers_for_task_type(self):
        news_provider = _make_provider("news_p", [
            RawSource(url="https://news.com/a", title="News", content="News content.", provider="news_p")
        ])
        funding_provider = _make_provider("funding_p", [
            RawSource(url="https://funding.com/b", title="Funding", content="Funding content.", provider="funding_p")
        ])
        registry = ProviderRegistry()
        registry.register(news_provider)
        registry.register(funding_provider)
        config = AgentConfig(provider_map={"market": ["news_p"], "funding": ["funding_p"]})
        pipeline = RetrievalPipeline(registry, config)

        market_docs = pipeline.fetch("AI", "market")
        funding_docs = pipeline.fetch("AI", "funding")

        assert market_docs[0]["metadata"]["source"] == "news_p"
        assert funding_docs[0]["metadata"]["source"] == "funding_p"
        news_provider.fetch.assert_called_once()
        funding_provider.fetch.assert_called_once()

    def test_continues_if_one_provider_raises(self):
        bad_provider = _make_provider("bad_p", [])
        bad_provider.fetch.side_effect = Exception("boom")
        good_provider = _make_provider("good_p", [
            RawSource(url="https://good.com", title="Good", content="Good content.", provider="good_p")
        ])
        registry = ProviderRegistry()
        registry.register(bad_provider)
        registry.register(good_provider)
        config = AgentConfig(provider_map={"market": ["bad_p", "good_p"]})
        pipeline = RetrievalPipeline(registry, config)

        docs = pipeline.fetch("query", "market")

        assert len(docs) == 1
        assert docs[0]["metadata"]["source"] == "good_p"

    def test_returns_empty_for_unknown_task_type(self):
        provider = _make_provider("mock_provider", [])
        pipeline = self._build_pipeline([provider])
        assert pipeline.fetch("query", "unknown_type") == []


# ---------------------------------------------------------------------------
# rag_node
# ---------------------------------------------------------------------------

class TestRagNode:

    def _make_doc(self, title, content, url="https://example.com"):
        return {"id": "1", "title": title, "url": url, "content": content, "metadata": {}}

    def test_returns_top_5_by_relevance(self):
        docs = [
            self._make_doc("Unrelated", "This is about cooking recipes."),
            self._make_doc("AI Tools", "AI tools for developers are growing fast."),
            self._make_doc("Funding", "AI startup funding rounds increased this year."),
            self._make_doc("Hiring", "Companies are hiring AI engineers."),
            self._make_doc("Market", "The AI market is expanding rapidly."),
            self._make_doc("Irrelevant", "Sports news and weather updates."),
        ]
        state = {"topic": "AI market", "raw_documents": docs}

        result = rag_node(state)
        chunks = result["retrieved_chunks"]

        assert len(chunks) == 5
        # The irrelevant cooking/sports docs should rank lowest
        top_titles = [d["title"] for d in chunks]
        assert "Unrelated" not in top_titles or "Irrelevant" not in top_titles

    def test_filters_empty_content(self):
        docs = [
            self._make_doc("Empty", ""),
            self._make_doc("Whitespace", "   "),
            self._make_doc("Valid", "This has real content about AI."),
        ]
        state = {"topic": "AI", "raw_documents": docs}

        result = rag_node(state)
        chunks = result["retrieved_chunks"]

        assert len(chunks) == 1
        assert chunks[0]["title"] == "Valid"

    def test_handles_empty_document_list(self):
        state = {"topic": "AI", "raw_documents": []}
        result = rag_node(state)
        assert result["retrieved_chunks"] == []

    def test_handles_missing_topic(self):
        docs = [self._make_doc("Article", "Some content about technology.")]
        state = {"raw_documents": docs}
        result = rag_node(state)
        assert len(result["retrieved_chunks"]) == 1