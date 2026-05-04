from __future__ import annotations
import os
from abc import ABC, abstractmethod
from ..types import SearchResult

class BaseProvider(ABC):
    name: str
    api_key_env: str

    def is_configured(self) -> bool:
        return bool(os.environ.get(self.api_key_env))

    @abstractmethod
    async def search(self, query: str, count: int = 10) -> list[SearchResult]: ...

    async def safe_search(self, query: str, count: int = 10) -> list[SearchResult]:
        if not self.is_configured():
            return []
        try:
            return await self.search(query, count)
        except Exception:
            return []
