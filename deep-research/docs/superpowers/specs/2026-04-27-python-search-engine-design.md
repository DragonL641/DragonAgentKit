# Python Search Engine for Deep Research Skill

**Date:** 2026-04-27
**Status:** Draft

## Context

deep-research skill 的 Phase 3 (RETRIEVE) 依赖多源搜索来收集证据。当前方案是外挂 Rust 编写的 search-cli 二进制工具，但存在几个问题：

1. **外部依赖**：需要单独安装 Rust 二进制，增加用户配置负担
2. **skill 内代码不一致**：`research_engine.py` 仍引用 WebSearch 为主力，`methodology.md` 已改为 search-cli 为主
3. **无法深度整合**：作为外部 CLI，skill 无法在搜索过程中做细粒度控制（如按 claim 补充搜索、动态调整 Provider）

解决方案：用 Python 重写 search-cli 的核心搜索逻辑，作为 skill 的内部模块，消除外部二进制依赖。

## Scope

**做**：
- Python 多源搜索库（~1,500 行），覆盖 search-cli 的核心功能
- CLI 入口脚本，输出格式与原版 search-cli 兼容
- 修改 skill 的 methodology/research_engine 以使用新搜索库
- 更新 requirements.txt

**不做**：
- 完整 CLI 工具（不复制原版的终端美化、配置文件管理、self-update 等）
- Stealth Provider 的高级 TLS 指纹伪装（用 curl_cffi 基础实现，不追求完美）
- 邮箱验证等非搜索功能

## Architecture

### 目录结构

```
scripts/
├── search/                     # 新增：搜索库
│   ├── __init__.py             # 对外接口：search(), is_available()
│   ├── cli.py                  # Bash 入口（argparse）
│   ├── providers/              # 各搜索 Provider 适配器
│   │   ├── __init__.py
│   │   ├── base.py             # BaseProvider 抽象类
│   │   ├── brave.py
│   │   ├── serper.py
│   │   ├── exa.py
│   │   ├── jina.py
│   │   ├── firecrawl.py
│   │   ├── tavily.py
│   │   ├── serpapi.py
│   │   ├── perplexity.py
│   │   ├── xai.py
│   │   ├── browserless.py
│   │   └── stealth.py          # curl_cffi 实现，缺失时自动跳过
│   ├── classifier.py           # 正则意图分类（query → mode）
│   ├── dedup.py                # URL 归一化 + 去重
│   ├── config.py               # 环境变量读取 API keys
│   └── types.py                # SearchResult dataclass, 统一格式
├── research_engine.py          # 修改：Phase 3 指令
├── citation_manager.py         # 不改
└── ...
```

### 核心数据类型

```python
# scripts/search/types.py
from dataclasses import dataclass, field

@dataclass
class SearchResult:
    title: str
    url: str
    snippet: str
    source_provider: str       # "brave", "serper", etc.
    raw_data: dict = field(default_factory=dict)
    credibility_hint: int = 50  # 0-100

@dataclass
class SearchResponse:
    status: str                # "success" | "error" | "partial"
    query: str
    mode: str
    results: list[SearchResult]
    metadata: dict             # elapsed_ms, result_count, providers_queried, errors
```

### Provider 抽象

```python
# scripts/search/providers/base.py
from abc import ABC, abstractmethod

class BaseProvider(ABC):
    name: str
    api_key_env: str           # e.g. "SEARCH_KEYS_BRAVE"

    def is_configured(self) -> bool:
        return bool(os.environ.get(self.api_key_env))

    @abstractmethod
    async def search(self, query: str, count: int = 10) -> list[SearchResult]:
        """Execute search and return normalized results."""
        ...

    async def safe_search(self, query: str, count: int = 10) -> list[SearchResult]:
        """Wrapper with error handling — never raises."""
        if not self.is_configured():
            return []
        try:
            return await self.search(query, count)
        except Exception:
            return []
```

### 意图分类

从 search-cli 移植正则规则，将 query 文本分类为搜索模式：

```python
# scripts/search/classifier.py
PATTERNS = {
    "news":      [r"\b(news|breaking|latest|today|this week|current)\b"],
    "academic":  [r"\b(paper|study|research|arxiv|doi|journal|citation)\b"],
    "scholar":   [r"\b(scholar|google scholar|citation count|h-index)\b"],
    "patents":   [r"\b(patent|patent number|USPTO|WIPO|invention)\b"],
    "people":    [r"\b(who is|CEO|founder|linkedin|profile|bio of)\b"],
    "social":    [r"\b(tweet|twitter|X\.com|thread|mastodon)\b"],
    "deep":      [r"\b(in-depth|comprehensive|deep dive|exhaustive)\b"],
    "general":   [r"."],  # fallback
}

def classify(query: str) -> str:
    ql = query.lower()
    for mode, patterns in PATTERNS.items():
        if mode == "general":
            continue
        for p in patterns:
            if re.search(p, ql):
                return mode
    return "general"
```

### 模式 → Provider 映射

```python
MODE_PROVIDERS = {
    "general":   ["brave", "serper", "exa", "jina", "tavily"],
    "news":      ["brave", "serper", "tavily"],
    "academic":  ["exa", "serper", "tavily"],
    "scholar":   ["serper", "serpapi"],
    "deep":      ["brave", "exa", "serper", "tavily", "perplexity"],
    "people":    ["exa"],
    "patents":   ["serper"],
    "social":    ["xai"],
    "extract":   ["jina", "firecrawl", "browserless", "stealth"],
}
```

### 并发执行

```python
# scripts/search/__init__.py
import asyncio
from .classifier import classify
from .config import get_provider
from .dedup import deduplicate

async def search(query: str, mode: str = "auto",
                 providers: list[str] | None = None,
                 count: int = 10) -> SearchResponse:
    if mode == "auto":
        mode = classify(query)

    provider_names = providers or MODE_PROVIDERS.get(mode, MODE_PROVIDERS["general"])

    tasks = []
    for name in provider_names:
        provider = get_provider(name)
        if provider and provider.is_configured():
            tasks.append(provider.safe_search(query, count))

    if not tasks:
        return SearchResponse(status="error", query=query, mode=mode,
                              results=[], metadata={"error": "no providers configured"})

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
            "providers_queried": provider_names,
        }
    )
```

### URL 去重

```python
# scripts/search/dedup.py
from urllib.parse import urlparse, urlunparse

def normalize_url(url: str) -> str:
    p = urlparse(url.lower().rstrip("/"))
    # 去掉 www.、tracking 参数、fragment
    host = p.netloc.removeprefix("www.")
    return urlunparse((p.scheme, host, p.path, "", "", ""))

def deduplicate(results: list[SearchResult]) -> list[SearchResult]:
    seen = set()
    out = []
    for r in results:
        key = normalize_url(r.url)
        if key not in seen:
            seen.add(key)
            out.append(r)
    return out
```

### CLI 入口

```python
# scripts/search/cli.py
# 输出 JSON envelope，与原版 search-cli 兼容
# 语义 exit codes: 0=success, 1=error, 2=config, 3=auth_missing, 4=rate_limited

if __name__ == "__main__":
    # argparse: query, --mode, --providers, --count, --json
    resp = asyncio.run(search(args.query, args.mode, args.providers, args.count))
    print(json.dumps(dataclasses_asdict(resp), indent=2))
    sys.exit(exit_code(resp))
```

## Skill 集成改动

### 修改 `reference/methodology.md`

Phase 3 搜索指令改为：

```
Primary: python scripts/search/cli.py "query" --mode <mode> --json -c <count>
Fallback: WebSearch (if httpx not installed)
Optional: Exa MCP (if configured, for semantic search)
```

### 修改 `scripts/research_engine.py`

Phase 3 嵌入指令（~line 213-241）从 WebSearch 改为内置搜索库。

### 修改 `requirements.txt`

```
httpx>=0.27       # 异步 HTTP，搜索库核心依赖
curl_cffi>=0.7    # 可选，stealth provider TLS 伪装
```

### 不改的文件

- `schemas/` — 数据结构不变
- `templates/` — 报告模板不变
- `reference/quality-gates.md` — 质量标准不变
- `scripts/citation_manager.py`, `evidence_store.py` — 不变
- `SKILL.md` — 已正确

## Dependencies

| 依赖 | 用途 | 必须？ |
|------|------|--------|
| `httpx` | 异步 HTTP 请求所有 Provider | 是 |
| `curl_cffi` | Stealth Provider TLS 指纹伪装 | 否（缺失时跳过 stealth） |
| Python stdlib `asyncio`, `re`, `json`, `urllib`, `dataclasses` | 核心逻辑 | 是（内置） |

## Provider 实现清单

11 个 Provider，每个实现 `BaseProvider` 的 `search()` 方法：

| Provider | API 端点 | 认证方式 | 复杂度 |
|----------|----------|----------|--------|
| Brave | `api.search.brave.com/res/v1/web/search` | `X-Subscription-Token` header | 低 |
| Serper | `google.serper.dev/search` | `X-API-KEY` header | 低 |
| Exa | `api.exa.ai/search` | `x-api-key` header | 中（有 category/semantic 选项） |
| Jina | `s.jina.ai/{url}` | `Authorization: Bearer` | 低（URL → markdown） |
| Firecrawl | `api.firecrawl.dev/v1/scrape` | `Bearer` token | 中（支持 JS 渲染） |
| Tavily | `api.tavily.com/search` | `api_key` body field | 低 |
| SerpApi | `serpapi.com/search` | `api_key` query param | 中（多引擎支持） |
| Perplexity | `api.perplexity.ai/chat/completions` | `Authorization: Bearer` | 中（Sonar Pro 模型） |
| xAI | `api.x.ai/...` | `Bearer` token | 低 |
| Browserless | `chrome.browserless.io/...` | `Bearer` token | 中（浏览器控制） |
| Stealth | 直接 HTTP 请求 | 无 | 中（curl_cffi TLS 指纹） |

## Verification

1. **单元测试**：每个 Provider 的请求构造和响应解析
2. **集成测试**：`python scripts/search/cli.py "test query" --json` 端到端运行
3. **兼容性**：输出 JSON 格式与原版 search-cli 兼容
4. **Fallback 验证**：卸载 httpx 后 skill 能 fallback 到 WebSearch
5. **Skill 全流程**：用 `/deep-research` 运行一次 quick mode，确认 Phase 3 使用新搜索库

## Implementation Phases

| Phase | 内容 | 预估 |
|-------|------|------|
| 1 | 框架：types.py, base.py, classifier.py, dedup.py, config.py, __init__.py | 4h |
| 2 | 核心 Providers：brave, serper, exa, jina, tavily (5 个最常用的) | 6h |
| 3 | 补全 Providers：firecrawl, serpapi, perplexity, xai, browserless, stealth | 6h |
| 4 | CLI 入口 + skill 集成改动（methodology.md, research_engine.py, requirements.txt） | 4h |
| **Total** | | **~20h** |
