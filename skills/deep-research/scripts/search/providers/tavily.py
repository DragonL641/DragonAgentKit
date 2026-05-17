from __future__ import annotations
import os
import httpx
from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider

@register_provider
class TavilyProvider(BaseProvider):
    name = "tavily"
    api_key_env = "SEARCH_KEYS_TAVILY"
    _base_url = "https://api.tavily.com/search"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        body = {"query": query, "max_results": count, "api_key": os.environ[self.api_key_env]}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(self._base_url, json=body)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("content", ""),
                source_provider=self.name,
                raw_data=item,
                credibility_hint=70,
            ))
        return results
