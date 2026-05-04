from __future__ import annotations

from ..types import SearchResult
from .base import BaseProvider
from ..config import register_provider

try:
    from curl_cffi import requests as cffi_requests
    HAS_CURL_CFFI = True
except ImportError:
    cffi_requests = None  # type: ignore[assignment]
    HAS_CURL_CFFI = False


@register_provider
class StealthProvider(BaseProvider):
    name = "stealth"
    api_key_env = "SEARCH_KEYS_STEALTH"

    def is_configured(self) -> bool:
        return HAS_CURL_CFFI

    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        resp = cffi_requests.get(query, impersonate="chrome136", timeout=20)
        text = resp.text[:2000]
        return [SearchResult(
            title="",
            url=query,
            snippet=text,
            source_provider=self.name,
            credibility_hint=40,
        )]
