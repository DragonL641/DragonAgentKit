from __future__ import annotations
import os
import httpx
from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider

@register_provider
class SerperProvider(BaseProvider):
    name = "serper"
    api_key_env = "SEARCH_KEYS_SERPER"
    _base_url = "https://google.serper.dev/search"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        headers = {"X-API-KEY": os.environ[self.api_key_env], "Content-Type": "application/json"}
        body = {"q": query, "num": count, "gl": "us", "hl": "en"}
        async with httpx.AsyncClient(timeout=15) as client:
            resp = await client.post(self._base_url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("organic", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("link", ""),
                snippet=item.get("snippet", ""),
                source_provider=self.name,
                raw_data=item,
                credibility_hint=70,
            ))
        return results
