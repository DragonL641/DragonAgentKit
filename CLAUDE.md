# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DragonAgentKit 是一个跨平台 AI Skill 集合仓库，包含 43 个独立模块，兼容 Claude Code、Codex CLI、OpenCode、Gemini CLI 等 AI 编码工具。每个模块是自包含的文件夹，提供特定领域的知识、工作流和工具集成。

**这不是一个传统软件项目**——没有统一的 build/test/lint 流程。每个模块是独立的。

## 仓库结构

```
DragonAgentKit/
├── skills/            # 所有模块（SKILL.md 格式，agentskills.io 标准）
│   ├── 知识型/        # 17 个：Claude 自动触发，注入知识/指南
│   ├── 动作型/        # 17 个：用户 /name 主动调用，执行具体动作
│   └── 流水线型/      # 9 个：可作子 agent 运行，多阶段复杂流水线
├── external/          # 非原创的外部集成
│   └── playwright-cli/# Playwright 浏览器自动化
├── docs/              # 项目文档
└── .claude-plugin/
    └── marketplace.json
```

## Skill 三层分层

所有模块使用 SKILL.md 格式（agentskills.io 标准），通过 frontmatter 字段控制调用方式：

| 属性 | 知识型 | 动作型 | 流水线型 |
|---|---|---|---|
| **调用方式** | Claude 自动触发 | 用户 `/name` 主动调用 | 可作为子 agent 运行 |
| **核心价值** | 注入知识/指南 | 执行动作产出文件 | 多阶段复杂流水线 |
| **Frontmatter** | 默认（无特殊字段） | `disable-model-invocation: true` + `argument-hint` | `context: fork` |

### 知识型（17 个）

ai-writing-assistant, article-review, branded-content, commercial-brief, content-rewriting-2601, podcast-script-generator, topic-spinoff, your-tech-panel, cs-knowledge-doc, my-product-manager, product-strategy-analyzer, mem-query, mem-file-scan, mem-weekly, mem-monthly, find-skills, smart-draw-skill

### 动作型（17 个）

blog-post-writer, content-digest, topic-scout, image-generate, image-article-to-cover, image-article-to-illustration, image-brand-to-logo, image-content-to-infographic, image-content-to-slides, image-content-to-xhs, image-story-to-comic, image-story-to-storyboard, md-cjk-layout-optimize, md-optimized-to-html, data-analysis, ops-assistant, find-mcps

### 流水线型（9 个）

deep-research, image-skill-factory, remotion-video, rss-aggregator, workingnomads-jobs, workingnomads-scraper, mem-record, project-checkup, frontend-ui-designer

## Skill 架构

### 标准结构

```
skill-name/
├── SKILL.md          # 必需：YAML frontmatter (name, description) + Markdown 指令
├── agents/           # 可选：openai.yaml（Codex UI 元数据）
├── scripts/          # 可选：Python/Bash 可执行脚本
├── references/       # 可选：按需加载的参考文档
└── assets/           # 可选：模板、图标等输出资源
```

### Frontmatter 字段

| 字段 | 必需 | 说明 |
|---|---|---|
| `name` | 是 | 模块名，小写+连字符，≤64字符 |
| `description` | 是 | 功能描述+触发场景/关键词，≤1024字符 |
| `disable-model-invocation` | 否 | `true` 时禁止 Claude 自动触发，仅用户手动调用 |
| `argument-hint` | 否 | 参数提示，帮助用户了解调用方式 |
| `context` | 否 | `fork` 时以子 agent 上下文运行 |

## 跨平台兼容

所有模块遵循 agentskills.io 标准（SKILL.md 格式），兼容以下平台：

- **Claude Code** — 完整 frontmatter 支持
- **Codex CLI** — SKILL.md 直接可用，agents/openai.yaml 提供 UI 优化
- **OpenCode** — 6 个发现路径，最广兼容性
- **Gemini CLI** — `.agents/skills/` 路径自动发现

## Plugin Pack 分类

分类与 `.claude-plugin/marketplace.json` 定义的 plugin pack 对应：

- **内容创作** (11): ai-writing-assistant, blog-post-writer, content-digest, article-review, branded-content, commercial-brief, content-rewriting-2601, podcast-script-generator, topic-scout, topic-spinoff, your-tech-panel
- **图像/设计** (11): image-generate, image-brand-to-logo, image-article-to-cover, image-article-to-illustration, image-content-to-infographic, image-content-to-slides, image-content-to-xhs, image-story-to-comic, image-story-to-storyboard, image-skill-factory, frontend-ui-designer
- **开发工具** (4): project-checkup, ops-assistant, my-product-manager, cs-knowledge-doc
- **数据/分析** (5): data-analysis, rss-aggregator, workingnomads-jobs, workingnomads-scraper, product-strategy-analyzer
- **知识管理** (5): mem-record, mem-query, mem-file-scan, mem-weekly, mem-monthly
- **Markdown 工具** (2): md-cjk-layout-optimize, md-optimized-to-html
- **多媒体/研究** (4): deep-research, find-skills, find-mcps, remotion-video
- **外部工具** (1): playwright-cli

## Skill 开发规范

- **SKILL.md frontmatter** 必需字段为 `name` 和 `description`
- **description** 是触发机制，需同时描述 skill 功能和触发场景/关键词
- **脚本运行约定**：Python 脚本用 `uv run` 执行，TypeScript/JavaScript 脚本用 `npx -y bun` 执行
- **Progressive Disclosure**：SKILL.md 正文 <500 行，详细内容放 references/
- reference 文件保持一层深度，直接从 SKILL.md 引用
- 脚本必须实际运行测试，不能只写不测
- skill 命名：小写字母 + 数字 + 连字符，不超过 64 字符
- 不要在 skill 中创建 README.md、CHANGELOG.md 等辅助文档
- 使用祈使句/不定式形式编写指令

## 注意事项

- `.idea/` 目录是 IDE 配置，不需要关注
- `.dragonskills/` 目录用于集中管理 API 密钥和凭证（已 gitignore）
- `.claude-plugin/marketplace.json` 是 Plugin Marketplace 注册配置，定义了 8 个 plugin pack
- skill 中的脚本语言以 Python 为主，少量 TypeScript/JavaScript（image-generate、workingnomads-jobs）

## Plugin Marketplace

本仓库已注册为 Claude Code Plugin Marketplace，其他用户可以通过以下命令安装：

```bash
# 注册 marketplace
/plugin marketplace add DragonL641/DragonAgentKit

# 按类别安装 plugin packs
/plugin install content-creation@dragon-agent-kit
/plugin install image-design@dragon-agent-kit
/plugin install dev-tools@dragon-agent-kit
/plugin install data-analysis@dragon-agent-kit
/plugin install knowledge-management@dragon-agent-kit
/plugin install markdown-tools@dragon-agent-kit
/plugin install multimedia-research@dragon-agent-kit
/plugin install external-tools@dragon-agent-kit
```

可用的 8 个 plugin packs：content-creation、image-design、dev-tools、data-analysis、knowledge-management、markdown-tools、multimedia-research、external-tools
