---
name: workingnomads-scraper
description: 从 Working Nomads 抓取远程开发职位，解析并生成格式化的 Markdown 报告。当用户提到 Working Nomads 职位抓取、远程工作爬取时触发。
context: fork
---

# Working Nomads 职位抓取器

从 Working Nomads API 抓取指定类别的远程职位，解析并生成 Markdown 格式的报告。

## 使用方式

当用户需要抓取远程开发职位时，运行以下脚本：

```bash
uv run scripts/main.py --category Development --size 50
```

### 参数

- `--category`: 职位类别（默认 `Development`），可选：Development, Design, Marketing, Sales 等
- `--size`: 抓取数量（默认 `50`）

## 脚本结构

- `scripts/main.py` — 入口，协调抓取流程
- `scripts/api_client.py` — API 请求封装
- `scripts/parse_jobs.py` — 职位数据解析
- `scripts/parser.py` — 通用解析工具
- `scripts/markdown_formatter.py` — Markdown 格式化输出

## 依赖

安装依赖：`uv pip install -r requirements.txt`
