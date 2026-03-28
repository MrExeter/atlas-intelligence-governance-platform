from history.evidence import normalize_sources


def _src(url, domain=None, title=None):
    """Helper to build a dict source."""
    return {"url": url, "domain": domain or url, "title": title}


def test_basic_normalization():
    sources = [_src("https://example.com/a", "example.com", "Article A")]
    result = normalize_sources(sources)
    assert len(result) == 1
    assert result[0]["title"] == "Article A"
    assert result[0]["domain"] == "example.com"


def test_title_fallback_to_url():
    sources = [_src("https://example.com/a", "example.com", title=None)]
    result = normalize_sources(sources)
    assert result[0]["title"] == "https://example.com/a"


def test_dedupes_by_url():
    sources = [
        _src("https://example.com/a", "example.com", "A"),
        _src("https://example.com/a", "example.com", "A duplicate"),
    ]
    result = normalize_sources(sources)
    assert len(result) == 1


def test_unique_domains_sorted_first():
    sources = [
        _src("https://site-a.com/1", "site-a.com", "A1"),
        _src("https://site-a.com/2", "site-a.com", "A2"),
        _src("https://site-b.com/1", "site-b.com", "B1"),
    ]
    result = normalize_sources(sources)
    domains = [r["domain"] for r in result]
    # Both unique domains should appear before the repeat
    assert domains[0] in ("site-a.com", "site-b.com")
    assert domains[1] in ("site-a.com", "site-b.com")
    assert domains[2] == "site-a.com"


def test_respects_limit():
    sources = [_src(f"https://site-{i}.com/", f"site-{i}.com", f"Title {i}") for i in range(50)]
    result = normalize_sources(sources, limit=25)
    assert len(result) == 25


def test_skips_missing_url():
    sources = [{"url": None, "domain": "example.com", "title": "No URL"}]
    result = normalize_sources(sources)
    assert len(result) == 0


def test_empty_sources():
    assert normalize_sources([]) == []
