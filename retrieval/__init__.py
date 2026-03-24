from retrieval.config import AgentConfig
from retrieval.pipeline import RetrievalPipeline
from retrieval.providers.google_news_rss import GoogleNewsRSSProvider
from retrieval.providers.hackernews import HackerNewsProvider
from retrieval.providers.newsdata import NewsDataProvider
from retrieval.providers.tavily import TavilyProvider
from retrieval.registry import ProviderRegistry


def build_default_pipeline() -> RetrievalPipeline:
    registry = ProviderRegistry()
    registry.register(TavilyProvider())
    registry.register(GoogleNewsRSSProvider())
    registry.register(HackerNewsProvider())
    registry.register(NewsDataProvider())
    return RetrievalPipeline(registry, AgentConfig())


default_pipeline = build_default_pipeline()