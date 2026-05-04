from __future__ import annotations

import os

import httpx

from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider


@register_provider
class SerpApiProvider(BaseProvider):
    name = "serpapi"
    api_key_env = "SEARCH_KEYS_SERPAPI"
    _base_url = "https://serpapi.com/search"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        params = {"q": query, "api_key": os.environ[self.api_key_env], "num": count}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(self._base_url, params=params)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("organic_results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source_provider=self.name,
                raw_data=item,
                credibility_hint=70,
            ))
        return results
