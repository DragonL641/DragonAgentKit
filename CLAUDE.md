# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 项目概述

DragonSkills 是一个 AI Skill 集合仓库，包含数十个独立 skill 模块，用于扩展 Claude Code / Codex 等 AI 编码工具的能力。每个 skill 是一个自包含的文件夹，提供特定领域的知识、工作流和工具集成。

**这不是一个传统软件项目**——没有统一的 build/test/lint 流程。每个 skill 是独立的。

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

## Skill 分类

仓库中的 skill 涵盖多个领域：
- **内容创作**：ai-writing-assistant, blog-post-writer, content-digest, article-review 等
- **文档处理**：docx, pdf, pptx, xlsx
- **图像/设计**：frontend-ui-designer, canvas-design, image-generate, image-brand-to-logo 等
- **开发工具**：commitor, mcp-builder, playwright-cli, webapp-testing, project-checkup
- **数据/分析**：data-analysis, rss-aggregator, workingnomads-scraper, x-blogger-analyzer
- **个人知识管理**：mem-record, mem-query, mem-weekly, obsidian 等
- **播客/视频**：podcast-script-generator, podcast-workflow, remotion-video, youtube-transcript-cn

## Skill 开发规范

- **SKILL.md frontmatter** 必需字段为 `name` 和 `description`；部分 skill 额外使用 `version`、`metadata`、`allowed-tools`、`argument-hint` 等可选字段
- **description** 是触发机制，需同时描述 skill 功能和触发场景/关键词
- **脚本运行约定**：Python 脚本用 `uv run` 执行，TypeScript/JavaScript 脚本用 `npx -y bun` 执行
- **agents/openai.yaml**（可选）：为 Codex 提供 `display_name`、`short_description` 和 `default_prompt`
- **Progressive Disclosure**：SKILL.md 正文 <500 行，详细内容放 references/
- reference 文件保持一层深度，直接从 SKILL.md 引用
- 脚本必须实际运行测试，不能只写不测
- skill 命名：小写字母 + 数字 + 连字符，不超过 64 字符
- 不要在 skill 中创建 README.md、CHANGELOG.md 等辅助文档
- 使用祈使句/不定式形式编写指令

## 注意事项

- `.idea/` 目录是 IDE 配置，不需要关注
- `drawio` skill 包含 `.mcp.json` 配置，用于集成 `@next-ai-drawio/mcp-server`
- skill 中的脚本语言以 Python 为主，少量 TypeScript/JavaScript（drawio、image-generate、workingnomads-jobs）

## Plugin Marketplace

本仓库已注册为 Claude Code Plugin Marketplace，其他用户可以通过以下命令安装：

```bash
# 注册 marketplace
/plugin marketplace add DragonL641/DragonSkills

# 按类别安装 skill packs
/plugin install content-creation@dragon-skills
/plugin install image-design@dragon-skills
/plugin install dev-tools@dragon-skills
/plugin install data-analysis@dragon-skills
/plugin install knowledge-management@dragon-skills
/plugin install markdown-tools@dragon-skills
/plugin install multimedia-research@dragon-skills
```

可用的 7 个 plugin packs：content-creation、image-design、dev-tools、data-analysis、knowledge-management、markdown-tools、multimedia-research
