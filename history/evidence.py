from urllib.parse import urlparse


def normalize_sources(sources: list, limit: int = 25) -> list[dict]:
    """
    Normalize ExecutionTrace sources to EvidenceItem dicts.
    Dedupes by URL, prioritizes unique domains, caps at limit.
    """
    seen_urls: set[str] = set()
    seen_domains: set[str] = set()
    unique_domain: list[dict] = []
    repeat_domain: list[dict] = []

    for source in sources:
        url = getattr(source, "url", None) or source.get("url") if isinstance(source, dict) else source.url
        if not url:
            continue
        if url in seen_urls:
            continue
        seen_urls.add(url)

        domain = (
            getattr(source, "domain", None) or source.get("domain")
            if isinstance(source, dict)
            else source.domain
        ) or urlparse(url).netloc

        title = (
            getattr(source, "title", None) or source.get("title")
            if isinstance(source, dict)
            else source.title
        ) or url

        item = {"title": title, "url": url, "domain": domain}

        if domain not in seen_domains:
            seen_domains.add(domain)
            unique_domain.append(item)
        else:
            repeat_domain.append(item)

    return (unique_domain + repeat_domain)[:limit]
