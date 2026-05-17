from __future__ import annotations
import os
import httpx
from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider

@register_provider
class BraveProvider(BaseProvider):
    name = "brave"
    api_key_env = "SEARCH_KEYS_BRAVE"
    _base_url = "https://api.search.brave.com/res/v1/web/search"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        headers = {"X-Subscription-Token": os.environ[self.api_key_env]}
        params = {"q": query, "count": count}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.get(self._base_url, headers=headers, params=params)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("web", {}).get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", ""),
                source_provider=self.name,
                raw_data=item,
                credibility_hint=70,
            ))
        return results
