from __future__ import annotations
from urllib.parse import urlparse, urlunparse
from .types import SearchResult

def normalize_url(url: str) -> str:
    p = urlparse(url.lower())
    host = p.netloc.removeprefix("www.")
    path = p.path.rstrip("/")
    return urlunparse((p.scheme, host, path, "", "", ""))

def deduplicate(results: list[SearchResult]) -> list[SearchResult]:
    seen: set[str] = set()
    out: list[SearchResult] = []
    for r in results:
        key = normalize_url(r.url)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out
