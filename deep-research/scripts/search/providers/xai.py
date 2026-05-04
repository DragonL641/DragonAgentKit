from __future__ import annotations

import os

import httpx

from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider


@register_provider
class XaiProvider(BaseProvider):
    name = "xai"
    api_key_env = "SEARCH_KEYS_XAI"
    _base_url = "https://api.x.ai/v1/chat/completions"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        headers = {"Authorization": f"Bearer {os.environ[self.api_key_env]}"}
        body = {
            "model": "grok-3",
            "messages": [{"role": "user", "content": query}],
        }
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self._base_url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

        content = data["choices"][0]["message"]["content"]
        citations = data.get("citations", [])

        if not citations:
            return [SearchResult(
                title="",
                url="",
                snippet=content,
                source_provider=self.name,
                raw_data=data,
                credibility_hint=50,
            )]

        results = []
        for url in citations:
            results.append(SearchResult(
                title="",
                url=url,
                snippet=content,
                source_provider=self.name,
                raw_data={},
                credibility_hint=50,
            ))
        return results
