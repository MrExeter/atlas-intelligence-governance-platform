SOURCE_RELIABILITY = {
    "nytimes.com": 0.95,
    "wsj.com": 0.95,
    "reuters.com": 0.94,
    "bloomberg.com": 0.94,
    "arxiv.org": 0.90,
    "nature.com": 0.90,
    "techcrunch.com": 0.85,
    "theverge.com": 0.80,
    "medium.com": 0.60,
    "substack.com": 0.55,
    "reddit.com": 0.30,
    "twitter.com": 0.25,
}


def get_source_score(domain: str) -> float:
    return SOURCE_RELIABILITY.get(domain, 0.5)
