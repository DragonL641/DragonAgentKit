from __future__ import annotations

import os

import httpx

from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider


@register_provider
class BrowserlessProvider(BaseProvider):
    name = "browserless"
    api_key_env = "SEARCH_KEYS_BROWSERLESS"
    _base_url = "https://chrome.browserless.io/content"

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        key = os.environ[self.api_key_env]
        body = {"url": query}
        async with httpx.AsyncClient(timeout=30) as client:
            resp = await client.post(
                f"{self._base_url}?token={key}", json=body,
            )
            resp.raise_for_status()
            text = resp.text[:2000]

        return [SearchResult(
            title="",
            url=query,
            snippet=text,
            source_provider=self.name,
            raw_data={},
            credibility_hint=40,
        )]
