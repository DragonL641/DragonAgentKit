---
name: stock-US-morning-brief
description: Generate and send personalized daily US stock market morning brief via email. Trigger when user asks for stock report, morning brief, market report, US market, or mentions /stock-US-morning-brief.
---

# stock-US-morning-brief

Generate and send personalized daily US stock market report via email to multiple recipients.

## Usage
- Manual trigger: `/stock-US-morning-brief`
- Scheduled trigger: Use Claude Code CronCreate or external cron to invoke at desired time

## Data Source

| Source | Tool | Data |
|--------|------|------|
| Stock Data | yfinance | Price, analyst targets, upgrades/downgrades, EPS, insider trades, fundamentals |
| News | Alpha Vantage | News with sentiment scoring |
| News fallback | Finnhub | Market news |
| News search | Tavily | Industry/market news search |

## Configuration

The skill reads from `config.json` with **per-recipient settings**.

**Sensitive credentials are stored in `.env` file (not committed to version control):**

```bash
# .env
DAILY_REPORT_FINNHUB_KEY=your-finnhub-key
DAILY_REPORT_ALPHAVANTAGE_KEY=your-alphavantage-key
DAILY_REPORT_TAVILY_KEY=your-tavily-key
DAILY_REPORT_SMTP_PASSWORD=your-smtp-app-password
```

**config.json structure (non-sensitive):**

```json
{
  "email_service": {
    "provider": "qq",
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender_email": "your@email.com",
    "sender_name": "美股日报"
  },
  "recipients": [
    {
      "id": 1,
      "email": "user@example.com",
      "name": "用户名",
      "active": true,
      "language": "zh-CN",
      "settings": {
        "industries": ["aerospace_defense", "semiconductor_ai"],
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

**Configuration Fields**:
- `industries`: Industries to filter news (aerospace_defense, semiconductor_ai, machinery, education)
- `holdings`: US stock holdings (standard symbols like AMD, NVDA, MU, TSLA)
- `news_count`: Max number of global news items

---

## Workflow

When this skill is invoked, follow these steps EXACTLY:

### Step 1: Load Configuration

Read `config.json` to get:
- Active recipients (filter by `active: true`)
- Each recipient's settings (holdings, industries, news_count)

### Step 2: Merge Recipient Settings (Union)

Calculate the union of all recipients' settings:

```python
holdings_union = []
max_news_count = 0
industries_union = set()

for r in recipients:
    settings = r.get("settings", {})
    holdings_union.extend(settings.get("holdings", []))
    industries_union.update(settings.get("industries", []))
    max_news_count = max(max_news_count, settings.get("news_count", 10))

# Deduplicate holdings by symbol
seen = set()
unique_holdings = []
for h in holdings_union:
    if h["symbol"] not in seen:
        seen.add(h["symbol"])
        unique_holdings.append(h)
```

### Step 3: Fetch Market Data

Use USMarketProvider to fetch data:

```python
from lib.market import USMarketProvider

provider = USMarketProvider()
holdings_symbols = [h["symbol"] for h in unique_holdings]
market_data = {
    "indices": provider.get_indices(),
    "holdings": provider.get_holdings_data(unique_holdings),
    "recommendations": provider.get_recommendations_from_industries(
        list(industries_union), holdings_symbols
    ),
}
```

**Data includes:**
- **Indices**: S&P 500, NASDAQ, Dow Jones, VIX
- **Per-stock**: Price, change%, market cap, P/E, beta, 52wk range, 50d MA, 6M chart
- **Analyst**: Price targets, rating distribution, upgrades/downgrades
- **Fundamentals**: EPS estimates, earnings history (surprise%), insider trades
- **Recommendations**: Top-rated stocks from industry watchlists (filtered by analyst buy % > 50%)

### Step 4: Fetch News

Use DataProvider for financial news:

```python
from lib.data_provider import DataProvider
dp = DataProvider(config)
tickers = [h["symbol"] for h in unique_holdings]
news = dp.get_financial_news(tickers=tickers, limit=max_news_count, user_tickers=tickers, industries=list(industries_union))
```

### Step 5: Build Global Metrics

Create global metrics from market indices:

```python
global_metrics = []
for idx in market_data.get("indices", []):
    global_metrics.append({
        "label": idx["name"],
        "value": f"{idx['change']:+.2f}%",
        "change": idx["change"]
    })
```

### Step 6: Generate Personalized Daily Summary

For EACH recipient, generate a summary based on:
- Their specific holdings
- Their language preference

Content should include:
- Market overview
- Holdings performance summary
- Key analyst highlights (real data from provider)

**IMPORTANT:** Generate content in Chinese. Translation is handled by send_report.py.

### Step 7: Build JSON Data Structure

Construct a JSON object:

```json
{
  "subject": "【美股早报】2026年4月17日",
  "data_time": "08:30:00",
  "global_metrics": [
    {"label": "S&P 500", "value": "+0.56%", "change": 0.56},
    {"label": "NASDAQ", "value": "+1.23%", "change": 1.23}
  ],
  "news": [
    {"title": "...", "summary": "...", "source": "Reuters", "time": "2小时前", "tag": "半导体AI"}
  ],
  "us": {
    "indices": [...],
    "holdings": [...],
    "recommendations": [...]
  },
  "daily_summary": "<p>...</p>"
}
```

**Key points:**
- No fabricated data — only include what the provider returns
- All content in Chinese — translation is automatic

### Step 8: Send Report to All Recipients

```bash
python lib/send_report.py --data-file report_data.json
```

The script will:
1. Load config.json for recipient list
2. Load base template (email_base.html)
3. For each active recipient:
   - Apply color/font settings based on language
   - Render market section using USMarketProvider
   - Translate entire HTML to target language via Claude API (for ko-KR)
   - Limit news by recipient's news_count
   - Send via SMTP

---

## Color Rules

| Language | Up | Down | Neutral |
|----------|----|----|---------|
| zh-CN | Red `#e74c3c` | Green `#27ae60` | Gray `#7f8c8d` |
| ko-KR | Red `#e74c3c` | Blue `#2980b9` | Gray `#7f8c8d` |

---

## Language Requirements

- **All content generated in Chinese first** — translation is handled by send_report.py
- **ko-KR recipients**: HTML translated to Korean via Claude API
- **Tags**: Use Chinese industry tags (半导体AI, 航空航天, 宏观经济)

---

## Template Architecture

```
templates/
└── email_base.html      # Frame (header, footer, global metrics, news, summary)
```

USMarketProvider renders the market section HTML, injected into `{{market_sections}}` placeholder.

---

## Error Handling

- **Single recipient failure**: Log error, continue with other recipients
- **Data fetch failure**: Show "数据获取中" placeholder
- **SMTP failure**: Log error with details

---

## Important Notes

1. **NEVER fabricate data** — only display what APIs actually return
2. **Check current date** — Use today's date for news searches
3. **All active recipients receive the report** — Process all recipients
4. **Clean up intermediate files** — Delete report_data.json and reports/ after sending

---

## Dependencies

```
pip install yfinance requests anthropic python-dotenv matplotlib
```
