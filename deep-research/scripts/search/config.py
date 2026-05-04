from __future__ import annotations
from .providers.base import BaseProvider

MODE_PROVIDERS: dict[str, list[str]] = {
    "general":  ["tavily", "exa", "jina"],
    "news":     ["tavily"],
    "academic": ["exa", "tavily"],
    "deep":     ["tavily", "exa", "jina"],
    "people":   ["exa"],
}

_PROVIDERS: dict[str, type[BaseProvider]] = {}

def _load_providers() -> None:
    if _PROVIDERS:
        return
    try:
        from .providers import tavily
    except Exception:
        pass
    try:
        from .providers import exa
    except Exception:
        pass
    try:
        from .providers import jina
    except Exception:
        pass

def get_provider(name: str) -> BaseProvider | None:
    _load_providers()
    cls = _PROVIDERS.get(name)
    return cls() if cls else None

def register_provider(cls: type[BaseProvider]) -> type[BaseProvider]:
    _PROVIDERS[cls.name] = cls
    return cls
