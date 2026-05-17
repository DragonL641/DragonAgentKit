from __future__ import annotations
import re

PATTERNS: dict[str, list[str]] = {
    "news":     [r"\b(news|breaking|latest|today|this week|current)\b"],
    "academic": [r"\b(paper|study|research|arxiv|doi|journal|citation)\b"],
    "people":   [r"\b(who is|CEO|founder|linkedin|profile|bio of)\b"],
    "deep":     [r"\b(in-depth|comprehensive|deep dive|exhaustive)\b"],
}

def classify(query: str) -> str:
    ql = query.lower()
    for mode, patterns in PATTERNS.items():
        for p in patterns:
            if re.search(p, ql):
                return mode
    return "general"
