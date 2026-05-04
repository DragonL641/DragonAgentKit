from __future__ import annotations
import os
import httpx
from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider

@register_provider
class JinaProvider(BaseProvider):
    name = "jina"
    api_key_env = "SEARCH_KEYS_JINA"
    _search_url = "https://s.jina.ai/"
    _reader_url = "https://r.jina.ai/"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        headers = {"Accept": "application/json"}
        key = os.environ.get(self.api_key_env)
        if key:
            headers["Authorization"] = f"Bearer {key}"
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.get(f"{self._search_url}{query}", headers=headers, params={"num": count})
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("data", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("description", "") or (item.get("content", "")[:300]),
                source_provider=self.name,
                raw_data=item,
                credibility_hint=60,
            ))
        return results
