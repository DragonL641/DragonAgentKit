---
name: find-skills
description: 搜索和评估外部 Claude Code Skills（仅 Skills，不含 MCP Servers）。从 skillstore.io 获取候选列表，结合安全审计和 GitHub 健康度自动打分，输出 Top N 供用户选择。当用户说"找一个 skill"、"搜索 skills"、"推荐 skill"、"找 TDD skill"、"有没有 XX 技能"、"发现 skills"、"find skill"时触发。注意：如果用户要找 MCP Server，应使用 find-mcps skill 而非本 skill。
---

# FindSkills — Skill 质量评估与推荐

搜索外部 Claude Code **Skills**（不含 MCP Servers），自动评分，输出 Top N 供选择。

## 输入解析

从用户消息中提取：
1. **搜索关键词**（必需）：如 "TDD"、"video generation"、"debugging"
2. **分类过滤**（可选）：coding / devops / writing / documentation / productivity / office / data / research / communication / design / security / legal
3. **Top N**（可选，默认 3）

如果用户只给关键词，不指定分类。如果用户说"推荐 N 个"，取 N。

## 工作流程

### Phase 1: 搜索候选

调用 skillstore.io API 获取候选列表：

```bash
# 按关键词搜索（注意：参数名是 q，不是 search）
curl -s "https://skillstore.io/api/skills?q={keyword}&limit=20"

# 按分类搜索（用户指定分类时）
curl -s "https://skillstore.io/api/skills?category={category}&limit=20"

# 关键词 + 分类组合
curl -s "https://skillstore.io/api/skills?q={keyword}&category={category}&limit=20"
```

解析返回的 `data` 数组，提取每个候选的 `slug`、`displayName`、`description`、`repo`。

如果结果不足 10 个且使用了分类过滤，去掉分类限制重新搜索一次，合并去重。

**验证**：如果 API 返回空或报错，告知用户"未找到匹配的 Skills，请换个关键词试试"并停止。

### Phase 2: 评估每个候选

对每个候选**并行**获取详细数据：

**Step A: skillstore 详情（必须）**

```bash
curl -s "https://skillstore.io/api/skills/{slug}"
```

提取：
- `qualityScore` (0-100)
- `qualityBreakdown`: specCompliance, architecture, security, content, community, maintainability
- `securityAudit.risk_level`: safe / low / high
- `securityAudit.critical_findings` / `high_findings` / `medium_findings` 的数量
- `stats`: viewCount, downloadCount, favoriteCount
- `repo`: GitHub 仓库 URL

**Step B: GitHub 健康度（必须）**

从 `repo` 字段解析 `owner/repo`。

注意：skillstore 返回的 repo URL 格式为 `https://github.com/{owner}/{repo}/tree/{ref}/...`，需要提取 `owner/repo` 部分（取 URL path 的前两段）。

```bash
# 提取 owner/repo
echo "https://github.com/foo/bar/tree/main/skills/xyz" | sed 's|https://github.com/||' | cut -d'/' -f1,2
# → foo/bar

# 获取仓库信息
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, pushed: .pushed_at, license: (.license.spdx_id // "None")}'

# 获取 contributor 数量
gh api repos/{owner}/{repo}/contributors?per_page=1" --include 2>&1 | grep -i 'link:' | grep -o 'page=[0-9]*>' | tail -1 | grep -o '[0-9]*'
# 或简单取前 100 个 contributors 数量
gh api "repos/{owner}/{repo}/contributors?per_page=100" --jq 'length'
```

提取：star 数、最后 push 时间、contributor 数、license。

### Phase 3: 计算评分

每个候选计算四维分数，总分 0-100：

#### 质量分 (0-100)

直接使用 skillstore 的 `qualityScore`。

#### 安全分 (0-100)

```
基础分：safe → 90, low → 70, high → 30
扣分：critical_finding × (-10), high_finding × (-5), medium_finding × (-2)
下限为 0
```

#### 社区分 (0-100)

```
downloadCount: ≥100→30, ≥50→20, ≥10→10, else→0
favoriteCount: ≥10→20, ≥5→10, else→0
viewCount:     ≥500→20, ≥100→10, else→0
communityBreakdown 百分比 × 30（取 qualityBreakdown.communityDetails 中 passed points / maxPoints × 30）
```

#### 健康分 (0-100)

```
Stars:       ≥5000→30, ≥1000→20, ≥200→12, ≥50→6, else→0
Last push:   ≤30天→30, ≤90天→20, ≤180天→10, ≤365天→5, else→0
Contributors:≥10→25, ≥5→15, ≥2→8, 1→2
License:     MIT/Apache→15, 有其他→8, 无→0
```

#### 总分

```
总分 = 质量分 × 0.25 + 安全分 × 0.30 + 社区分 × 0.10 + 健康分 × 0.35
```

四舍五入取整。

### Phase 4: 生成报告

按总分降序排列，取 Top N。

**报告格式**：

```
## FindSkills 评估报告

搜索「{关键词}」，评估了 {总数} 个候选。以下为 Top {N}：

### 🥇 {名称} — 总分 {总分}/100
- 📦 https://skillstore.io/skills/{slug}
- ⭐ GitHub: {stars} stars | 更新于 {last_push} | {contributors} 人维护 | {license}
- 📊 健康:{健康分} | 安全:{安全分} | 质量:{质量分} | 社区:{社区分}
- 🔒 安全等级: {safe/low/high}（{findings摘要，如"无风险"或"2 high findings: command injection"}）
- 📥 {downloads} 次下载 · {favorites} 收藏
- 💡 {description 的前80字}

### 🥈 {名称} — 总分 {总分}/100
...（同上格式）

### 🥉 {名称} — 总分 {总分}/100
...（同上格式）
```

**安全警告**：如果任何候选的 `securityAudit.risk_level` 为 `high`，在报告末尾追加：

```
⚠️ 安全提示：标有「high」风险的 Skill 存在已知安全问题（如命令注入、凭证暴露），安装前请仔细审查源码。
```

**安装指引**：报告末尾追加：

```
## 安装方式

选择你想安装的 Skill，告诉我序号（🥇🥈🥉），我会自动下载并安装到 ~/.claude/skills/。

安装命令模板：
curl -sL "{repo}" 的 SKILL.md → ~/.claude/skills/{name}/SKILL.md
```

### Phase 5: 用户选择

等待用户选择序号，然后：

1. 从选中的 skill 的 `repo` URL 下载 SKILL.md（及 references/ 等辅助目录）
2. 保存到 `~/.claude/skills/{name}/`
3. 确认安装成功

## 边界情况

- **API 限流**：skillstore.io 无已知限流。GitHub API 未认证 60次/小时，使用 `gh` CLI 走 OAuth 认证则 5000次/小时
- **repo URL 解析失败**：该候选的健康分记为 0，继续评估其他维度
- **无 GitHub 仓库**：某些 skill 可能没有 repo 字段，健康分记为 0
- **搜索结果为空**：提示用户换关键词，停止
- **所有候选总分都很低（<40）**：在报告中提醒"当前搜索结果整体质量较低，建议换关键词"
