"""Built-in multi-provider search engine for deep-research skill."""
from __future__ import annotations
import time
import asyncio
from .types import SearchResponse, SearchResult
from .classifier import classify
from .config import get_provider, MODE_PROVIDERS
from .dedup import deduplicate

async def search(
    query: str,
    mode: str = "auto",
    providers: list[str] | None = None,
    count: int = 10,
) -> SearchResponse:
    if mode == "auto":
        mode = classify(query)

    provider_names = providers or MODE_PROVIDERS.get(mode, MODE_PROVIDERS["general"])

    tasks = []
    names_queried = []
    for name in provider_names:
        provider = get_provider(name)
        if provider and provider.is_configured():
            tasks.append(provider.safe_search(query, count))
            names_queried.append(name)

    if not tasks:
        return SearchResponse(
            status="error", query=query, mode=mode,
            metadata={"error": "no providers configured"},
        )

    start = time.monotonic()
    results_lists = await asyncio.gather(*tasks)
    elapsed = int((time.monotonic() - start) * 1000)

    all_results = [r for batch in results_lists for r in batch]
    deduped = deduplicate(all_results)

    return SearchResponse(
        status="success",
        query=query,
        mode=mode,
        results=deduped[:count],
        metadata={
            "elapsed_ms": elapsed,
            "result_count": len(deduped),
            "providers_queried": names_queried,
        },
    )
