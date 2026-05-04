# invest-brief Migration Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Migrate `stock-US-morning-brief` from DragonSkills skill to standalone project `invest-brief` at `/Users/liuziyi/Projects/invest-brief/`, with Docker deployment support and built-in scheduler.

**Architecture:** Copy existing Python code into a new project directory, update config paths from `.dragonskills/` to project-local, add `croniter`-based scheduler to `run.py`, and wrap in Docker for NAS deployment.

**Tech Stack:** Python 3.12, uv, yfinance, anthropic, croniter, Docker

---

## File Map

| Action | File | Responsibility |
|--------|------|----------------|
| Create | `pyproject.toml` | Dependency management, project metadata |
| Create | `run.py` | Entry point with scheduler + run-once modes |
| Create | `config.example.json` | Non-sensitive config template |
| Create | `.env.example` | Environment variable template |
| Create | `.gitignore` | Ignore logs, .env, __pycache__ |
| Create | `Dockerfile` | Docker image build |
| Create | `docker-compose.yml` | Docker Compose service definition |
| Copy | `lib/__init__.py` | Module exports (unchanged) |
| Copy+Modify | `lib/api_clients.py` | Change env var names + .env path |
| Copy | `lib/charts.py` | Chart generation (unchanged) |
| Copy+Modify | `lib/data_provider.py` | Minor: no direct changes, inherits from api_clients |
| Copy | `lib/market.py` | USMarketProvider (unchanged) |
| Copy+Modify | `lib/send_report.py` | Change config path |
| Copy+Modify | `lib/smtp_client.py` | Change env var name + config path |
| Copy | `lib/watchlists.py` | Industry watchlists (unchanged) |
| Copy | `templates/email_base.html` | Email template (unchanged) |
| Copy | `doc/*` | Documentation files (unchanged) |

---

### Task 1: Create project skeleton with git init and pyproject.toml

**Files:**
- Create: `/Users/liuziyi/Projects/invest-brief/pyproject.toml`

- [ ] **Step 1: Create project directory and init git**

```bash
mkdir -p /Users/liuziyi/Projects/invest-brief
cd /Users/liuziyi/Projects/invest-brief
git init
```

- [ ] **Step 2: Create pyproject.toml**

Migrate dependencies from `run.py` inline script metadata. Add `croniter` for scheduler.

```toml
[project]
name = "invest-brief"
version = "0.1.0"
description = "Personalized investment briefing via email"
requires-python = ">=3.10"
dependencies = [
    "yfinance",
    "requests",
    "anthropic",
    "python-dotenv",
    "matplotlib",
    "croniter",
]

[project.scripts]
invest-brief = "run:main"
```

- [ ] **Step 3: Create .gitignore**

```gitignore
.env
__pycache__/
.DS_Store
report_data.json
reports/
logs/
*.pyc
```

- [ ] **Step 4: Commit skeleton**

```bash
cd /Users/liuziyi/Projects/invest-brief
git add pyproject.toml .gitignore
git commit -m "chore: init project skeleton"
```

---

### Task 2: Copy lib/, templates/, doc/ (unchanged files)

**Files:**
- Copy: `lib/__init__.py`, `lib/charts.py`, `lib/data_provider.py`, `lib/market.py`, `lib/watchlists.py`
- Copy: `templates/email_base.html`
- Copy: `doc/*`

- [ ] **Step 1: Create directories and copy files**

```bash
cd /Users/liuziyi/Projects/invest-brief
mkdir -p lib templates doc logs

# lib (unchanged files)
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/lib/__init__.py lib/
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/lib/charts.py lib/
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/lib/data_provider.py lib/
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/lib/market.py lib/
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/lib/watchlists.py lib/

# templates
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/templates/email_base.html templates/

# doc
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/doc/* doc/
```

- [ ] **Step 2: Commit copied files**

```bash
cd /Users/liuziyi/Projects/invest-brief
git add lib/__init__.py lib/charts.py lib/data_provider.py lib/market.py lib/watchlists.py templates/ doc/
git commit -m "chore: copy unchanged lib, templates, doc files"
```

---

### Task 3: Migrate api_clients.py — update env var names and .env path

**Files:**
- Create: `/Users/liuziyi/Projects/invest-brief/lib/api_clients.py` (copy + modify)

- [ ] **Step 1: Copy file**

```bash
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/lib/api_clients.py /Users/liuziyi/Projects/invest-brief/lib/api_clients.py
```

- [ ] **Step 2: Update .env loading path**

In `/Users/liuziyi/Projects/invest-brief/lib/api_clients.py`, change lines 19-20 from:

```python
# Load credentials from centralized .dragonskills directory
load_dotenv(Path(__file__).resolve().parents[2] / ".dragonskills" / "stock-US-morning-brief.env", override=False)
```

to:

```python
# Load credentials from project root .env
load_dotenv(Path(__file__).resolve().parent.parent / ".env", override=False)
```

- [ ] **Step 3: Update env var names in ENV_KEYS**

In `/Users/liuziyi/Projects/invest-brief/lib/api_clients.py`, change lines 25-29 from:

```python
ENV_KEYS = {
    "finnhub": "DAILY_REPORT_FINNHUB_KEY",
    "alphavantage": "DAILY_REPORT_ALPHAVANTAGE_KEY",
    "tavily": "DAILY_REPORT_TAVILY_KEY",
}
```

to:

```python
ENV_KEYS = {
    "finnhub": "FINNHUB_KEY",
    "alphavantage": "ALPHAVANTAGE_KEY",
    "tavily": "TAVILY_KEY",
}
```

- [ ] **Step 4: Commit**

```bash
cd /Users/liuziyi/Projects/invest-brief
git add lib/api_clients.py
git commit -m "feat: migrate api_clients with updated env vars"
```

---

### Task 4: Migrate smtp_client.py — update env var name and config path

**Files:**
- Create: `/Users/liuziyi/Projects/invest-brief/lib/smtp_client.py` (copy + modify)

- [ ] **Step 1: Copy file**

```bash
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/lib/smtp_client.py /Users/liuziyi/Projects/invest-brief/lib/smtp_client.py
```

- [ ] **Step 2: Update default config path in __init__**

In `/Users/liuziyi/Projects/invest-brief/lib/smtp_client.py`, change lines 53-54 from:

```python
        if config_path is None:
            config_path = Path(__file__).resolve().parents[2] / ".dragonskills" / "stock-US-morning-brief.json"
```

to:

```python
        if config_path is None:
            config_path = Path(__file__).resolve().parent.parent / "config.json"
```

- [ ] **Step 3: Update SMTP password env var name (3 occurrences)**

Change all 3 occurrences of `'DAILY_REPORT_SMTP_PASSWORD'` to `'SMTP_PASSWORD'`:

- Line 75: `self.app_password = os.environ.get('SMTP_PASSWORD') or email_config.get('app_password', '')`
- Line 235: `server.login(email_config['sender_email'], os.environ.get('SMTP_PASSWORD') or email_config.get('app_password', ''))`
- Line 241: `server.login(email_config['sender_email'], os.environ.get('SMTP_PASSWORD') or email_config.get('app_password', ''))`

- [ ] **Step 4: Commit**

```bash
cd /Users/liuziyi/Projects/invest-brief
git add lib/smtp_client.py
git commit -m "feat: migrate smtp_client with updated env vars and config path"
```

---

### Task 5: Migrate send_report.py — update config path

**Files:**
- Create: `/Users/liuziyi/Projects/invest-brief/lib/send_report.py` (copy + modify)

- [ ] **Step 1: Copy file**

```bash
cp /Users/liuziyi/Projects/DragonSkills/stock-US-morning-brief/lib/send_report.py /Users/liuziyi/Projects/invest-brief/lib/send_report.py
```

- [ ] **Step 2: Update _resolve_config_path**

In `/Users/liuziyi/Projects/invest-brief/lib/send_report.py`, change lines 69-71 from:

```python
def _resolve_config_path() -> Path:
    """Resolve config path from centralized .dragonskills directory"""
    return Path(__file__).resolve().parents[2] / ".dragonskills" / "stock-US-morning-brief.json"
```

to:

```python
def _resolve_config_path() -> Path:
    """Resolve config path from project root"""
    return Path(__file__).resolve().parent.parent / "config.json"
```

- [ ] **Step 3: Commit**

```bash
cd /Users/liuziyi/Projects/invest-brief
git add lib/send_report.py
git commit -m "feat: migrate send_report with updated config path"
```

---

### Task 6: Create run.py with scheduler

**Files:**
- Create: `/Users/liuziyi/Projects/invest-brief/run.py`

This is the most substantial change. The new `run.py` merges the existing logic with a `croniter`-based scheduler.

- [ ] **Step 1: Write run.py**

Key changes from original:
1. Remove `DRAGONSKILLS_DIR`/`ENV_FILE`/`CONFIG_FILE` — use project-root paths
2. Add `--now` flag for immediate execution
3. Add scheduler loop using `croniter`
4. Add SIGTERM signal handler for graceful shutdown

```python
# /// script
# requires-python = ">=3.10"
# dependencies = [
#   "yfinance",
#   "requests",
#   "anthropic",
#   "python-dotenv",
#   "matplotlib",
#   "croniter",
# ]
# ///

"""
invest-brief — Personalized investment briefing via email.

Usage:
    uv run run.py --now [--dry-run] [--skip-summary]  # Run once immediately
    uv run run.py                                      # Start scheduler
"""

import sys
import json
import os
import argparse
import logging
import signal
import time
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

sys.path.insert(0, str(Path(__file__).parent))

from dotenv import load_dotenv

PROJECT_DIR = Path(__file__).resolve().parent
ENV_FILE = PROJECT_DIR / ".env"
CONFIG_FILE = PROJECT_DIR / "config.json"

load_dotenv(ENV_FILE, override=False)

# Ensure ANTHROPIC_AUTH_TOKEN is available as ANTHROPIC_API_KEY for anthropic SDK
if not os.environ.get("ANTHROPIC_API_KEY") and os.environ.get("ANTHROPIC_AUTH_TOKEN"):
    os.environ["ANTHROPIC_API_KEY"] = os.environ["ANTHROPIC_AUTH_TOKEN"]

logger = logging.getLogger("run")

# Shutdown flag for scheduler
_shutdown = False


def _signal_handler(signum, frame):
    global _shutdown
    logger.info("Received shutdown signal, exiting gracefully...")
    _shutdown = True


signal.signal(signal.SIGTERM, _signal_handler)
signal.signal(signal.SIGINT, _signal_handler)


# ============================================================================
# Configuration
# ============================================================================

def load_config() -> dict:
    with open(CONFIG_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


# ============================================================================
# Merge Recipient Settings
# ============================================================================

NEWS_LIMIT = 5


def merge_recipient_settings(recipients: list) -> tuple:
    holdings_union = []
    industries_union = set()

    for r in recipients:
        settings = r.get("settings", {})
        holdings_union.extend(settings.get("holdings", []))
        industries_union.update(settings.get("industries", []))

    seen = set()
    unique_holdings = []
    for h in holdings_union:
        if h["symbol"] not in seen:
            seen.add(h["symbol"])
            unique_holdings.append(h)

    return unique_holdings, industries_union, NEWS_LIMIT


# ============================================================================
# Fetch Market Data
# ============================================================================

def fetch_market_data(unique_holdings, industries_union, holdings_symbols):
    from lib.market import USMarketProvider

    provider = USMarketProvider()
    return {
        "indices": provider.get_indices(),
        "holdings": provider.get_holdings_data(unique_holdings),
        "recommendations": provider.get_recommendations_from_industries(
            list(industries_union), holdings_symbols
        ),
    }


# ============================================================================
# Fetch News
# ============================================================================

def fetch_news(config, tickers, max_news_count, industries_union):
    from lib.data_provider import DataProvider

    dp = DataProvider(config)
    return dp.get_financial_news(
        tickers=tickers,
        limit=max_news_count,
        user_tickers=tickers,
        industries=list(industries_union),
    )


# ============================================================================
# News Summarization via Claude API
# ============================================================================

NEWS_SUMMARY_PROMPT = """你是财经新闻编辑。阅读以下新闻，为每条新闻生成中文标题和简明摘要。

规则：
1. 标题：用中文概括核心事件，10-20字，保留关键公司名/股票代码（英文）
2. 摘要：1-2句中文，说明影响什么、为什么重要，不要废话
3. 严格按 JSON 数组格式返回，每项包含 title 和 summary 字段
4. 数量与输入一致，顺序与输入一致
5. 不要加 markdown 代码块标记"""


def summarize_news(news: list) -> list:
    if not news:
        return news

    news = news[:NEWS_LIMIT]

    try:
        import anthropic
        import re

        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            base_url=os.environ.get("ANTHROPIC_BASE_URL"),
        )

        items_text = "\n".join(
            f"{i+1}. Title: {n.get('title', '')}\n   Content: {n.get('summary', '')[:500]}"
            for i, n in enumerate(news)
        )

        user_message = f"请为以下 {len(news)} 条新闻生成中文标题和摘要：\n\n{items_text}"

        response = client.messages.create(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            temperature=0.2,
            system=NEWS_SUMMARY_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        )

        text = response.content[0].text.strip()
        text = re.sub(r"^\s*```(?:json)?\s*\n?", "", text)
        text = re.sub(r"\n?\s*```\s*$", "", text)

        summaries = json.loads(text)
        if not isinstance(summaries, list) or len(summaries) != len(news):
            logger.warning(f"News summary count mismatch: got {len(summaries) if isinstance(summaries, list) else 'non-list'}, expected {len(news)}")
            return news

        for i, s in enumerate(summaries):
            if isinstance(s, dict):
                news[i]["title"] = s.get("title", news[i].get("title", ""))
                news[i]["summary"] = s.get("summary", "")

        logger.info(f"Summarized {len(news)} news items")
        return news

    except Exception as e:
        logger.warning(f"News summarization failed: {e}")
        return news


# ============================================================================
# Build Global Metrics
# ============================================================================

def build_global_metrics(indices):
    metrics = []
    for idx in indices:
        metrics.append({
            "label": idx["name"],
            "value": f"{idx['change']:+.2f}%",
            "change": idx["change"],
        })
    return metrics


# ============================================================================
# Generate Daily Summary via Claude API
# ============================================================================

SYSTEM_PROMPT = """你是一个专业的美股市场分析师。根据提供的市场数据和新闻，撰写一份简明扼要的每日投资简报总结。

要求：
1. 输出纯 HTML 段落（<p>标签），不包含任何 markdown
2. 使用中文撰写
3. 内容结构建议：
   - 第一段：市场整体表现（结合指数涨跌）
   - 第二段：持仓股票要点（关注涨跌幅较大的个股、关键分析师评级变动、财报表现）
   - 第三段：行业/板块动态（结合新闻中与持仓相关的信息）
   - 第四段（可选）：风险提示或值得关注的事件
4. 每段 2-3 句话，总字数 200-400 字
5. 只使用提供的数据，不要编造数字
6. 对关键数字使用 <strong> 标签突出显示
7. 不要使用列表或标题，只用段落"""


def _serialize_market_context(market_data, news, unique_holdings):
    lines = []

    lines.append("## 市场指数")
    for idx in market_data.get("indices", []):
        lines.append(f"- {idx['name']}: {idx['point']:.2f} ({idx['change']:+.2f}%)")

    lines.append("\n## 持仓股票")
    for h in market_data.get("holdings", []):
        symbol = h.get("symbol", "")
        name = h.get("name", symbol)
        price = h.get("price", 0)
        change = h.get("change", 0)
        info = h.get("info", {})
        lines.append(f"- {symbol} ({name}): ${price:.2f} ({change:+.2f}%)")
        if info.get("pe"):
            lines.append(f"  P/E: {info['pe']:.1f}")
        targets = h.get("targets", {})
        if targets.get("mean"):
            upside = h.get("upside_pct")
            lines.append(f"  目标价: ${targets['mean']:.2f} (上涨空间: {upside:+.1f}%)" if upside else f"  目标价: ${targets['mean']:.2f}")
        for ug in h.get("upgrades", [])[:3]:
            firm = ug.get("firm", "")
            grade = ug.get("to_grade", "")
            date = ug.get("date", "")
            lines.append(f"  评级变动: {firm} → {grade} ({date})")
        for eh in h.get("earnings_history", [])[:2]:
            surprise = eh.get("surprise_pct")
            if surprise is not None:
                lines.append(f"  财报惊喜: {surprise:+.1f}%")

    lines.append("\n## 推荐关注")
    for r in market_data.get("recommendations", []):
        symbol = r.get("symbol", "")
        buy_pct = r.get("buy_pct", 0)
        industry = r.get("industry", "")
        lines.append(f"- {symbol}: 买入评级 {buy_pct:.0f}%, 行业: {industry}")

    lines.append("\n## 重要新闻")
    for n in news[:5]:
        title = n.get("title", "")
        source = n.get("source", "")
        t = n.get("time", "")
        lines.append(f"- {title} ({source}, {t})")

    return "\n".join(lines)


def generate_daily_summary(market_data, news, unique_holdings):
    try:
        import anthropic

        client = anthropic.Anthropic(
            api_key=os.environ.get("ANTHROPIC_API_KEY"),
            base_url=os.environ.get("ANTHROPIC_BASE_URL"),
        )

        context = _serialize_market_context(market_data, news, unique_holdings)
        holdings_symbols = ", ".join(h["symbol"] for h in unique_holdings)

        user_message = f"当前持仓: {holdings_symbols}\n\n{context}"

        with client.messages.stream(
            model="claude-sonnet-4-6",
            max_tokens=2048,
            temperature=0.3,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_message}],
        ) as stream:
            summary = ""
            for text in stream.text_stream:
                summary += text

        import re
        summary = re.sub(r"^\s*```(?:html)?\s*\n?", "", summary)
        summary = re.sub(r"\n?\s*```\s*$", "", summary)
        return summary.strip()

    except Exception as e:
        logger.warning(f"Claude API summary failed: {e}")
        return "<p>今日市场数据已更新，请查看上方详情。</p>"


# ============================================================================
# Build Report Data
# ============================================================================

def build_report_data(market_data, news, global_metrics, daily_summary):
    now = datetime.now()
    return {
        "subject": f"【美股日报】{now.strftime('%Y年%-m月%-d日')}",
        "data_time": now.strftime("%H:%M:%S"),
        "global_metrics": global_metrics,
        "news": news,
        "us": {
            "indices": market_data.get("indices", []),
            "holdings": market_data.get("holdings", []),
            "recommendations": market_data.get("recommendations", []),
        },
        "daily_summary": daily_summary,
    }


# ============================================================================
# Send Report
# ============================================================================

def send_report(report_data):
    from lib.send_report import (
        load_config as sr_load_config,
        load_template,
        render_template,
        translate_html,
    )
    from lib.smtp_client import EmailSender

    config = sr_load_config()
    template = load_template()
    active_recipients = [r for r in config.get("recipients", []) if r.get("active", True)]

    if not active_recipients:
        logger.error("No active recipients found")
        return

    sender = EmailSender(str(CONFIG_FILE))

    for recipient in active_recipients:
        email = recipient["email"]
        name = recipient.get("name", email)
        language = recipient.get("language", "zh-CN")
        settings = recipient.get("settings", {})

        logger.info(f"Processing: {name} ({email}) - Language: {language}")

        html = render_template(template, report_data, language, settings)
        if language != "zh-CN":
            html = translate_html(html, language)

        subject = report_data.get("subject", f"【美股日报】{datetime.now().strftime('%Y年%m月%d日')}")

        try:
            sender.send(email, subject, html)
            logger.info(f"Sent successfully to {email}")
        except Exception as e:
            logger.error(f"Failed to send to {email}: {e}")


# ============================================================================
# Run Once
# ============================================================================

def run_once(args):
    """Execute a single report run."""
    logger.info("=" * 60)
    logger.info("invest-brief - Starting run")

    # Check weekend
    et = ZoneInfo("America/New_York")
    now_et = datetime.now(et)
    if now_et.weekday() >= 5:
        logger.info(f"Today is {now_et.strftime('%A')} in US Eastern time, market closed. Skipping.")
        return

    # Step 1: Load config
    logger.info("Step 1: Loading configuration")
    config = load_config()
    recipients = [r for r in config.get("recipients", []) if r.get("active", True)]
    if not recipients:
        logger.error("No active recipients found")
        sys.exit(1)
    logger.info(f"Found {len(recipients)} active recipient(s)")

    # Step 2: Merge settings
    logger.info("Step 2: Merging recipient settings")
    unique_holdings, industries_union, max_news_count = merge_recipient_settings(recipients)
    holdings_symbols = [h["symbol"] for h in unique_holdings]
    logger.info(f"Holdings: {holdings_symbols}, Industries: {industries_union}, Max news: {max_news_count}")

    # Step 3: Fetch market data
    logger.info("Step 3: Fetching market data")
    try:
        market_data = fetch_market_data(unique_holdings, industries_union, holdings_symbols)
        logger.info(f"Got {len(market_data.get('holdings', []))} holdings, {len(market_data.get('indices', []))} indices")
    except Exception as e:
        logger.warning(f"Market data fetch failed: {e}")
        market_data = {"indices": [], "holdings": [], "recommendations": []}

    # Step 4: Fetch news
    logger.info("Step 4: Fetching news")
    try:
        news = fetch_news(config, holdings_symbols, max_news_count, industries_union)
        logger.info(f"Got {len(news)} news items")
    except Exception as e:
        logger.warning(f"News fetch failed: {e}")
        news = []

    # Step 5: Build global metrics
    logger.info("Step 5: Building global metrics")
    global_metrics = build_global_metrics(market_data.get("indices", []))

    # Step 5.5: Summarize news
    if news and not args.skip_summary:
        logger.info("Step 5.5: Summarizing news via Claude API")
        news = summarize_news(news)
    else:
        logger.info("Step 5.5: Skipping news summary")

    # Step 6: Generate daily summary
    if args.skip_summary:
        logger.info("Step 6: Skipping summary (--skip-summary)")
        daily_summary = "<p>今日市场数据已更新，请查看上方详情。</p>"
    else:
        logger.info("Step 6: Generating daily summary via Claude API")
        daily_summary = generate_daily_summary(market_data, news, unique_holdings)
        logger.info(f"Summary generated: {len(daily_summary)} chars")

    # Step 7: Build report data
    logger.info("Step 7: Building report data")
    report_data = build_report_data(market_data, news, global_metrics, daily_summary)

    if args.dry_run:
        logger.info("Dry run - outputting report data to stdout")
        print(json.dumps(report_data, ensure_ascii=False, indent=2, default=str))
        logger.info("Dry run complete")
        return

    # Step 8: Send report
    logger.info("Step 8: Sending report")
    send_report(report_data)
    logger.info("Report sending complete")


# ============================================================================
# Scheduler
# ============================================================================

def run_scheduler(config):
    """Run as a long-lived scheduler process."""
    from croniter import croniter

    schedule_cfg = config.get("schedule", {})
    cron_expr = schedule_cfg.get("cron", "0 23 * * 1-5")
    tz = ZoneInfo("Asia/Shanghai")

    logger.info(f"Scheduler started with cron: '{cron_expr}' (timezone: Asia/Shanghai)")

    base = datetime.now(tz)
    cron = croniter(cron_expr, base)
    next_run = cron.get_next(datetime)

    logger.info(f"Next run scheduled at: {next_run.isoformat()}")

    while not _shutdown:
        now = datetime.now(tz)
        if now >= next_run:
            logger.info("Scheduled run triggered")
            try:
                run_once_inner = lambda: None  # dummy for args
                class FakeArgs:
                    dry_run = False
                    skip_summary = False
                run_once(FakeArgs())
            except Exception as e:
                logger.error(f"Scheduled run failed: {e}")

            next_run = cron.get_next(datetime)
            logger.info(f"Next run scheduled at: {next_run.isoformat()}")

        time.sleep(60)  # Check every minute

    logger.info("Scheduler stopped")


# ============================================================================
# Main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="invest-brief — Personalized investment briefing")
    parser.add_argument("--now", action="store_true", help="Run once immediately (do not start scheduler)")
    parser.add_argument("--dry-run", action="store_true", help="Build report, output to stdout, do not send email")
    parser.add_argument("--skip-summary", action="store_true", help="Skip Claude API summary, use placeholder")
    parser.add_argument("--log-level", default="INFO", help="Log level (DEBUG, INFO, WARNING, ERROR)")
    args = parser.parse_args()

    # Setup logging
    log_dir = PROJECT_DIR / "logs"
    log_dir.mkdir(exist_ok=True)

    logging.basicConfig(
        level=getattr(logging, args.log_level.upper(), logging.INFO),
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[
            logging.FileHandler(log_dir / "run.log", encoding="utf-8"),
            logging.StreamHandler(),
        ],
    )

    config = load_config()
    schedule_cfg = config.get("schedule", {})
    schedule_enabled = schedule_cfg.get("enabled", True)

    if args.now or not schedule_enabled:
        run_once(args)
    else:
        run_scheduler(config)


if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Verify run.py parses correctly**

```bash
cd /Users/liuziyi/Projects/invest-brief
python -c "import ast; ast.parse(open('run.py').read()); print('OK')"
```

Expected: `OK`

- [ ] **Step 3: Commit**

```bash
cd /Users/liuziyi/Projects/invest-brief
git add run.py
git commit -m "feat: add run.py with scheduler and run-once modes"
```

---

### Task 7: Create config templates and Docker files

**Files:**
- Create: `/Users/liuziyi/Projects/invest-brief/config.example.json`
- Create: `/Users/liuziyi/Projects/invest-brief/.env.example`
- Create: `/Users/liuziyi/Projects/invest-brief/Dockerfile`
- Create: `/Users/liuziyi/Projects/invest-brief/docker-compose.yml`

- [ ] **Step 1: Create config.example.json**

```json
{
  "schedule": {
    "enabled": true,
    "cron": "0 23 * * 1-5"
  },
  "email_service": {
    "provider": "qq",
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender_email": "YOUR_EMAIL@qq.com",
    "sender_name": "投资简报"
  },
  "recipients": [
    {
      "id": 1,
      "email": "recipient@example.com",
      "name": "Recipient1",
      "active": true,
      "language": "zh-CN",
      "settings": {
        "industries": ["semiconductor_ai", "aerospace_defense"],
        "holdings": [
          {"symbol": "AMD", "name": "AMD"},
          {"symbol": "NVDA", "name": "NVIDIA"}
        ],
        "news_count": 10
      }
    }
  ]
}
```

- [ ] **Step 2: Create .env.example**

```bash
# API Keys
FINNHUB_KEY=
ALPHAVANTAGE_KEY=
TAVILY_KEY=

# SMTP
SMTP_PASSWORD=

# Claude API
ANTHROPIC_API_KEY=
ANTHROPIC_BASE_URL=
```

- [ ] **Step 3: Create Dockerfile**

```dockerfile
FROM python:3.12-slim

# System deps for matplotlib
RUN apt-get update && apt-get install -y --no-install-recommends \
    libfreetype6-dev && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Install uv for dependency management
RUN pip install --no-cache-dir uv

# Copy dependency declaration first (layer caching)
COPY pyproject.toml .

# Copy application code
COPY run.py .
COPY lib/ lib/
COPY templates/ templates/

# Install dependencies
RUN uv sync

# Config and data mounted at runtime
VOLUME /app/config.json
VOLUME /app/.env
VOLUME /app/logs

ENTRYPOINT ["uv", "run", "run.py"]
```

- [ ] **Step 4: Create docker-compose.yml**

```yaml
services:
  invest-brief:
    build: .
    container_name: invest-brief
    volumes:
      - ./config.json:/app/config.json:ro
      - ./.env:/app/.env:ro
      - ./logs:/app/logs
    environment:
      - TZ=Asia/Shanghai
    restart: unless-stopped
```

- [ ] **Step 5: Commit**

```bash
cd /Users/liuziyi/Projects/invest-brief
git add config.example.json .env.example Dockerfile docker-compose.yml
git commit -m "feat: add config templates and Docker deployment files"
```

---

### Task 8: Migrate actual configuration and verify locally

**Files:**
- Create: `/Users/liuziyi/Projects/invest-brief/config.json` (from `.dragonskills/stock-US-morning-brief.json`)
- Create: `/Users/liuziyi/Projects/invest-brief/.env` (from `.dragonskills/stock-US-morning-brief.env`)

- [ ] **Step 1: Copy actual config files (do NOT commit these)**

```bash
cd /Users/liuziyi/Projects/invest-brief

# Copy and adapt config
cp /Users/liuziyi/.dragonskills/stock-US-morning-brief.json config.json
```

Then manually edit `config.json` to add the `schedule` field:

```json
{
  "schedule": {
    "enabled": true,
    "cron": "0 23 * * 1-5"
  },
  ...existing config...
}
```

```bash
# Copy .env and update var names
cat /Users/liuziyi/.dragonskills/stock-US-morning-brief.env | \
  sed 's/DAILY_REPORT_FINNHUB_KEY/FINNHUB_KEY/' | \
  sed 's/DAILY_REPORT_ALPHAVANTAGE_KEY/ALPHAVANTAGE_KEY/' | \
  sed 's/DAILY_REPORT_TAVILY_KEY/TAVILY_KEY/' | \
  sed 's/DAILY_REPORT_SMTP_PASSWORD/SMTP_PASSWORD/' \
  > .env
```

- [ ] **Step 2: Verify .env has correct variable names**

```bash
cd /Users/liuziyi/Projects/invest-brief
grep -E "^(FINNHUB_KEY|ALPHAVANTAGE_KEY|TAVILY_KEY|SMTP_PASSWORD|ANTHROPIC)" .env
```

Expected: Lines starting with `FINNHUB_KEY=`, `ALPHAVANTAGE_KEY=`, `TAVILY_KEY=`, `SMTP_PASSWORD=`, possibly `ANTHROPIC_API_KEY=` or `ANTHROPIC_BASE_URL=`. No `DAILY_REPORT_` prefix should remain.

- [ ] **Step 3: Run dry-run to verify data fetching works**

```bash
cd /Users/liuziyi/Projects/invest-brief
uv run run.py --now --dry-run --log-level DEBUG
```

Expected: JSON output to stdout with market data. Check for no import errors or config path errors.

- [ ] **Step 4: If dry-run succeeds, also test scheduler startup briefly**

```bash
cd /Users/liuziyi/Projects/invest-brief
timeout 5 uv run run.py --log-level INFO || true
```

Expected: Log output showing "Scheduler started with cron" and "Next run scheduled at" within 5 seconds, then timeout kills the process.

---

### Task 9: Docker build and verify

**Files:** None (validation only)

- [ ] **Step 1: Build Docker image**

```bash
cd /Users/liuziyi/Projects/invest-brief
docker compose build
```

Expected: Successful build with no errors.

- [ ] **Step 2: Run dry-run in Docker**

```bash
cd /Users/liuziyi/Projects/invest-brief
docker compose run --rm invest-brief --now --dry-run
```

Expected: JSON output with market data, same as local dry-run.

- [ ] **Step 3: Verify Docker cleanup**

```bash
docker compose down
```

---

### Task 10: Cleanup old macOS launchd task

**Files:** None (system cleanup)

- [ ] **Step 1: Unload and remove macOS launchd plist**

```bash
launchctl unload ~/Library/LaunchAgents/com.dragonskills.stock-us-morning-brief.plist 2>/dev/null || echo "Already unloaded"
rm -f ~/Library/LaunchAgents/com.dragonskills.stock-us-morning-brief.plist
```

- [ ] **Step 2: Verify it's gone**

```bash
launchctl list | grep dragonskills || echo "No dragonskills tasks found (expected)"
```

Expected: "No dragonskills tasks found (expected)"

---

### Task 11: Final commit and tag

- [ ] **Step 1: Add any remaining files and make final commit**

```bash
cd /Users/liuziyi/Projects/invest-brief
git add -A
git status  # Review: should only show files we want, NOT .env or config.json with real data
git commit -m "chore: finalize invest-brief migration"
```

- [ ] **Step 2: Tag initial release**

```bash
cd /Users/liuziyi/Projects/invest-brief
git tag v0.1.0
```

---

## Self-Review

**Spec coverage check:**

| Spec Requirement | Task |
|---|---|
| Create project at `/Users/liuziyi/Projects/invest-brief/` | Task 1 |
| `pyproject.toml` with dependencies | Task 1 |
| Config paths from `.dragonskills/` → project root | Tasks 3, 4, 5, 6 |
| Env var `DAILY_REPORT_*` → no prefix | Tasks 3, 4, 8 |
| Built-in scheduler with `croniter` | Task 6 |
| `--now` / `--dry-run` / `--skip-summary` flags | Task 6 |
| `Dockerfile` + `docker-compose.yml` | Task 7 |
| `config.example.json` + `.env.example` | Task 7 |
| Copy actual config and verify | Task 8 |
| Docker build and verify | Task 9 |
| Cleanup macOS launchd | Task 10 |
| `ANTHROPIC_AUTH_TOKEN` → `ANTHROPIC_API_KEY` compat | Task 6 (preserved) |
| matplotlib Docker deps | Task 7 (`libfreetype6-dev`) |
| Git init + tag | Tasks 1, 11 |

**Placeholder scan:** No TBD/TODO found. All steps have exact code.

**Type consistency:** All env var names (`FINNHUB_KEY`, `ALPHAVANTAGE_KEY`, `TAVILY_KEY`, `SMTP_PASSWORD`) are consistent across Tasks 3, 4, 7, 8. Config path resolution uses `Path(__file__).resolve().parent.parent / "config.json"` consistently in Tasks 4, 5.
