from __future__ import annotations
import os
import httpx
from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider

@register_provider
class ExaProvider(BaseProvider):
    name = "exa"
    api_key_env = "SEARCH_KEYS_EXA"
    _base_url = "https://api.exa.ai/search"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        headers = {"x-api-key": os.environ[self.api_key_env], "Content-Type": "application/json"}
        body = {"query": query, "numResults": count, "type": "neural", "contents": {"text": {"maxCharacters": 500}}}
        async with httpx.AsyncClient(timeout=20) as client:
            resp = await client.post(self._base_url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

        results = []
        for item in data.get("results", []):
            results.append(SearchResult(
                title=item.get("title", ""),
                url=item.get("url", ""),
                snippet=item.get("text", "")[:300],
                source_provider=self.name,
                raw_data=item,
                credibility_hint=80,
            ))
        return results
