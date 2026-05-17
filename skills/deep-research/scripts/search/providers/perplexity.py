from __future__ import annotations

import os

import httpx

from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider


@register_provider
class PerplexityProvider(BaseProvider):
    name = "perplexity"
    api_key_env = "SEARCH_KEYS_PERPLEXITY"
    _base_url = "https://api.perplexity.ai/chat/completions"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        headers = {"Authorization": f"Bearer {os.environ[self.api_key_env]}"}
        body = {
            "model": "sonar-pro",
            "messages": [{"role": "user", "content": query}],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self._base_url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        citations = data.get("citations", [])

        results = []
        for i, url in enumerate(citations):
            results.append(SearchResult(
                title="",
                url=url,
                snippet=content if i == 0 else "",
                source_provider=self.name,
                raw_data=data if i == 0 else {},
                credibility_hint=60,
            ))
        return results
