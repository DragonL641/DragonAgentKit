# Daily Report Skill

每日投资简报邮件推送 Skill

## 目录结构

```
daily-report/
├── skill.md              # Skill 主文件
├── config.json           # 配置文件
├── templates/
│   ├── email_cn.html     # 中文邮件模板
│   └── email_kr.html     # 韩文邮件模板
├── lib/
│   ├── __init__.py
│   ├── smtp_client.py    # SMTP 邮件发送
│   ├── api_clients.py    # 外部 API 客户端
│   └── data_provider.py  # 统一数据获取层
└── reports/              # 报告存档目录
```

## 配置步骤

### 1. 配置 API 密钥（可选）

编辑 `config.json`，添加外部 API 密钥以获取更好的数据质量：

```json
{
  "api_keys": {
    "finnhub": "YOUR_FINNHUB_API_KEY",
    "alphavantage": "YOUR_ALPHAVANTAGE_API_KEY",
    "tavily": "YOUR_TAVILY_API_KEY"
  }
}
```

**API 密钥获取：**

| API | 用途 | 免费额度 | 获取链接 |
|-----|------|----------|----------|
| Finnhub | 股价、分析师推荐 | 60 calls/min | https://finnhub.io/register |
| Alpha Vantage | 技术指标、历史数据 | 25 calls/day | https://www.alphavantage.co/support/#api-key |
| Tavily | 新闻搜索 | 1000 calls/month | https://tavily.com/ |

**注意：** 如果不配置 API 密钥，系统会自动使用 WebSearch 作为数据源。

### 2. 配置邮箱服务

编辑 `config.json`，填写邮箱信息：

```json
{
  "email_service": {
    "provider": "qq",
    "smtp_server": "smtp.qq.com",
    "smtp_port": 465,
    "sender_email": "your_email@qq.com",
    "sender_name": "投资日报",
    "app_password": "YOUR_APP_PASSWORD"
  }
}
```

**QQ邮箱应用密码获取：**
1. 访问 https://mail.qq.com
2. 设置 → 账户 → POP3/SMTP服务
3. 开启服务并生成授权码

### 3. 配置收件人

在 `recipients` 数组中添加收件人：

```json
{
  "id": 1,
  "email": "recipient@example.com",
  "name": "张三",
  "active": true,
  "language": "zh-CN",
  "settings": {
    "markets": ["cn", "us", "kr"],
    "industries": ["semiconductor_ai", "aerospace_defense"],
    "holdings": {
      "us": [{"symbol": "AMD", "name": "AMD"}],
      "cn": [],
      "kr": []
    }
  }
}
```

**注意：** `markets` 数组的顺序决定了邮件中各国市场的显示顺序。

支持的语言：
- `zh-CN` - 中文
- `ko-KR` - 韩文

### 4. 配置持仓股票

在 `settings.holdings` 中添加关注的股票：

```json
"holdings": {
  "us": [
    {"symbol": "AMD", "name": "AMD"},
    {"symbol": "NVDA", "name": "NVIDIA"}
  ],
  "cn": [],
  "kr": []
}
```

## 使用方法

### 手动触发

```
/daily-report
```

### 定时触发（launchd）

通过 macOS launchd 每天北京时间 23:00 自动执行，对应美东时间 10:00-11:00 AM（开盘后 0.5-1.5 小时）。周末自动跳过。

**触发时间对照：**

| 季节 | 北京 23:00 = 美东时间 | 距开盘 |
|------|----------------------|--------|
| 夏令时 (EDT, ~3月-11月) | 11:00 AM | 1.5h |
| 冬令时 (EST, ~11月-3月) | 10:00 AM | 0.5h |

**配置文件：** `~/Library/LaunchAgents/com.dragonskills.stock-us-morning-brief.plist`

**常用命令：**

```bash
# 加载定时任务（开机后只需执行一次）
launchctl load ~/Library/LaunchAgents/com.dragonskills.stock-us-morning-brief.plist

# 卸载定时任务
launchctl unload ~/Library/LaunchAgents/com.dragonskills.stock-us-morning-brief.plist

# 手动触发一次（不等待定时）
launchctl start com.dragonskills.stock-us-morning-brief

# 查看运行状态
launchctl list | grep dragonskills
```

**独立运行脚本（不依赖 Claude Code）：**

```bash
# 完整运行（获取数据 + 生成摘要 + 发送邮件）
uv run run.py

# Dry-run（只获取数据，不发送邮件）
uv run run.py --dry-run

# 跳过 Claude API 摘要生成（节省 API 费用，测试用）
uv run run.py --skip-summary

# 调试模式
uv run run.py --dry-run --log-level DEBUG
```

**日志文件：**

```
stock-US-morning-brief/
└── logs/
    ├── run.log      # 运行日志
    └── error.log    # 错误日志
```

**环境变量要求：**

除了 `.dragonskills/stock-US-morning-brief.env` 中的 API 密钥外，还需要 Claude API 用于摘要生成：

- `ANTHROPIC_AUTH_TOKEN` 或 `ANTHROPIC_API_KEY` — Claude API 密钥
- `ANTHROPIC_BASE_URL` — API 代理地址（可选，国内用户通常需要）

## 数据源优先级

系统按以下优先级获取数据：

| 数据类型 | 优先级 1 | 优先级 2 | 兜底 |
|----------|----------|----------|------|
| 股价 | Finnhub | Alpha Vantage | WebSearch/yfinance |
| 新闻 | Tavily | Finnhub | WebSearch |
| 分析师推荐 | Finnhub | - | WebSearch |
| 技术指标 | Alpha Vantage | - | WebSearch |

### 使用 DataProvider

```python
from lib import DataProvider

# 初始化
dp = DataProvider(config)

# 获取股价
price = dp.get_stock_price("AMD")
# {"symbol": "AMD", "price": 178.50, "change": -0.85, ...}

# 获取分析师推荐
rec = dp.get_analyst_recommendation("AMD")
# {"symbol": "AMD", "consensus": "buy", "buy": 15, ...}

# 获取价格目标
target = dp.get_price_target("AMD")
# {"symbol": "AMD", "target_mean": 195.0, ...}

# 获取新闻
news = dp.search_news("semiconductor news", max_results=10)

# 检查是否需要 WebSearch 兜底
fallback = dp.should_use_websearch()
# {"stock_prices": False, "news": True, "analyst_recs": False}
```

## 测试

### 测试 SMTP 连接

```bash
cd ~/.claude/skills/daily-report/lib
python smtp_client.py
```

### 测试 API 连接

```bash
cd ~/.claude/skills/daily-report/lib
python -c "from api_clients import FinnhubClient; c = FinnhubClient('your_key'); print(c.get_quote('AAPL'))"
```

### 测试 DataProvider

```bash
cd ~/.claude/skills/daily-report/lib
python -c "from data_provider import create_provider; dp = create_provider(config_path='../config.json'); print(dp.get_status())"
```

## 注意事项

- API 密钥是可选的，不配置也能正常使用（使用 WebSearch 兜底）
- Alpha Vantage 免费版有调用频率限制（25次/天）
- Outlook SMTP 每日发送限制约 300 封
- 建议使用应用密码而非账户密码
