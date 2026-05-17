from __future__ import annotations
from dataclasses import dataclass, field

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source_provider: str
    raw_data: dict = field(default_factory=dict)
    credibility_hint: int = 50

@dataclass
class SearchResponse:
    status: str  # "success" | "error" | "partial"
    query: str
    mode: str
    results: list[SearchResult] = field(default_factory=list)
    metadata: dict = field(default_factory=dict)
