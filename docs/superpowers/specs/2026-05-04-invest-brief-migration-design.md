# invest-brief: DragonSkills Skill 迁移为独立项目

> 日期：2026-05-04
> 状态：Approved

## 背景

`stock-US-morning-brief` 是 DragonSkills 仓库中的一个 Skill，用于生成美股每日投资简报并通过邮件发送。当前已具备独立运行能力（`run.py` 支持 `uv run`），但配置依赖 `.dragonskills/` 目录，且没有 Docker 支持。

## 目标

将 `stock-US-morning-brief` 从 DragonSkills skill 迁移为独立项目 `invest-brief`，部署到绿联 NAS 的 Docker 环境中，使用内置调度器自动运行。

## 范围

### In Scope

- 代码迁移至 `/Users/liuziyi/Projects/invest-brief/`
- 配置从 `.dragonskills/` 迁移到项目本地
- 添加 `pyproject.toml`、`Dockerfile`、`docker-compose.yml`
- 添加内置调度器（基于 cron 表达式，长驻进程模式）
- 清理 macOS launchd 定时任务
- 初始化 git 仓库

### Out of Scope

- A 股模块（后续迭代）
- 竞品分析中 Tier 1-3 功能增强（后续迭代）
- 代码重构或重命名（保持最小改动）
- 抽取 `BaseMarketProvider` 抽象类（等有第二个 provider 时再做）

## 项目结构

```
invest-brief/
├── run.py                    # 入口（调度器 + 执行逻辑）
├── config.json               # 非敏感配置
├── config.example.json       # 配置模板
├── .env.example              # 环境变量模板
├── .env                      # 实际环境变量（git-ignored）
├── .gitignore
├── pyproject.toml            # 依赖管理
├── Dockerfile
├── docker-compose.yml
├── lib/
│   ├── __init__.py
│   ├── api_clients.py
│   ├── charts.py
│   ├── data_provider.py
│   ├── market.py
│   ├── send_report.py
│   ├── smtp_client.py
│   └── watchlists.py
├── templates/
│   └── email_base.html
├── logs/                     # git-ignored
└── doc/
    ├── 竞品借鉴分析.md
    ├── 美股早报使用指南_中文版.docx
    └── 미국주식모닝브리프_사용가이드_한국어판.docx
```

## 配置变更

### 环境变量（.env）

从 `.dragonskills/stock-US-morning-brief.env` 迁移，去掉 `DAILY_REPORT_` 前缀：

```bash
# API Keys（原样迁移值）
FINNHUB_KEY=
ALPHAVANTAGE_KEY=
TAVILY_KEY=

# SMTP
SMTP_PASSWORD=

# Claude API
ANTHROPIC_API_KEY=
ANTHROPIC_BASE_URL=
```

### config.json

新增 `schedule` 字段：

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
    "sender_email": "",
    "sender_name": "投资简报"
  },
  "recipients": [...]
}
```

### run.py 变更

- 移除 `DRAGONSKILLS_DIR` 和 `ENV_FILE`/`CONFIG_FILE` 的 `.dragonskills` 路径逻辑
- 改为从项目根目录读取 `.env` 和 `config.json`
- 环境变量名去掉 `DAILY_REPORT_` 前缀（对应 `api_clients.py`、`data_provider.py` 中的引用也要同步更新）
- 新增调度器模式：默认启动时长驻进程，按 cron 表达式调度执行

## Docker 部署

### Dockerfile

```dockerfile
FROM python:3.12-slim

WORKDIR /app
COPY pyproject.toml .
COPY run.py .
COPY lib/ lib/
COPY templates/ templates/

RUN pip install uv && uv sync

VOLUME /app/config.json
VOLUME /app/.env
VOLUME /app/logs

ENTRYPOINT ["uv", "run", "run.py"]
```

### docker-compose.yml

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

### 运行方式

```bash
# 启动调度器（长驻进程，按 cron 配置自动执行）
docker compose up -d

# 手动执行一次
docker compose run --rm invest-brief --now

# Dry-run
docker compose run --rm invest-brief --now --dry-run

# 查看日志
docker compose logs -f invest-brief
```

## 内置调度器

### 设计

- 使用 `croniter` 库解析 cron 表达式
- 主循环：计算下次执行时间 → sleep → 执行 → 重复
- 支持信号处理（SIGTERM 优雅退出）
- `schedule.enabled: false` 时跳过调度，仅支持手动执行

### run.py 入口变更

```python
# 新增命令行参数
--now          # 立即执行一次（不启动调度器）
--schedule     # 启动调度器模式（默认行为）
--dry-run      # 不发送邮件
--skip-summary # 跳过 AI 摘要

# 启动逻辑
if args.now or not schedule_enabled:
    run_once(args)
else:
    run_scheduler(config)
```

## 迁移步骤

1. 创建 `/Users/liuziyi/Projects/invest-brief/`，初始化 git 仓库
2. 创建 `pyproject.toml`（从 `run.py` 的 inline script metadata 迁移依赖声明）
3. 复制 `lib/`、`templates/`、`doc/`
4. 迁移 `run.py`，修改配置路径和环境变量名
5. 更新 `lib/` 中所有引用 `DAILY_REPORT_*` 环境变量的地方
6. 添加内置调度器逻辑
7. 创建 `config.example.json`、`.env.example`、`.gitignore`
8. 创建 `Dockerfile`、`docker-compose.yml`
9. 从 `.dragonskills/` 复制 API keys 和收件人配置到新配置文件
10. 本地验证：`uv run run.py --now --dry-run`
11. Docker 验证：`docker compose run --rm invest-brief --now --dry-run`
12. 清理旧环境：`launchctl unload ~/Library/LaunchAgents/com.dragonskills.stock-us-morning-brief.plist && rm ~/Library/LaunchAgents/com.dragonskills.stock-us-morning-brief.plist`
13. 初始 commit

## 风险与注意事项

- 环境变量重命名需要全局搜索 `DAILY_REPORT_` 确保不遗漏
- `ANTHROPIC_AUTH_TOKEN` → `ANTHROPIC_API_KEY` 的兼容逻辑保留（run.py 中的映射代码）
- NAS Docker 环境的时区配置（`TZ=Asia/Shanghai`）确保调度时间正确
- matplotlib 在 Docker slim 镜像中可能需要额外系统依赖（如 libfreetype），构建时注意测试
