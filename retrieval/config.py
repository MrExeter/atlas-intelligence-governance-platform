from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class AgentConfig:
    """Maps research task types to the ordered list of provider names to use."""

    provider_map: Dict[str, List[str]] = field(
        default_factory=lambda: {
            "market":      ["newsdata", "google_news_rss", "hackernews"],
            "funding":     ["tavily"],
            "hiring":      ["hackernews", "tavily"],
            "competitors": ["tavily"],
        }
    )
    max_results_per_provider: int = 5