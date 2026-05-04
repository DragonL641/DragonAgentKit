from __future__ import annotations

import os

import httpx

from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider


@register_provider
class FirecrawlProvider(BaseProvider):
    name = "firecrawl"
    api_key_env = "SEARCH_KEYS_FIRECRAWL"
    _base_url = "https://api.firecrawl.dev/v1/scrape"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        headers = {"Authorization": f"Bearer {os.environ[self.api_key_env]}"}
        body = {"url": query, "formats": ["markdown"]}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(self._base_url, headers=headers, json=body)
            resp.raise_for_status()
            data = resp.json()

        markdown = data.get("data", {}).get("markdown", "")
        return [SearchResult(
            title="",
            url=query,
            snippet=markdown,
            source_provider=self.name,
            raw_data=data,
            credibility_hint=50,
        )]
