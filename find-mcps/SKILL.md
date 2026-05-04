---
name: find-mcps
description: 搜索和评估外部 MCP Servers（仅 MCP，不含 Skills）。从 Smithery 和 MCP 官方 Registry 获取候选列表，结合使用量、验证状态和 GitHub 健康度自动打分，输出 Top N 供用户选择。当用户说"找一个 MCP"、"搜索 MCP server"、"推荐 MCP"、"有没有 XX MCP"、"发现 MCP"、"find MCP"时触发。注意：如果用户要找 Skill，应使用 find-skills skill 而非本 skill。
---

# FindMCPs — MCP Server 质量评估与推荐

搜索外部 **MCP Servers**（不含 Skills），自动评分，输出 Top N 供选择。

## 数据源

| 来源 | 用途 | API |
|------|------|-----|
| **Smithery** | 主数据源：搜索 + 使用量 + 验证状态 | `https://registry.smithery.ai/servers?q={keyword}&pageSize=20` |
| **MCP 官方 Registry** | 补充：已发布状态 + 发布时间 | `https://registry.modelcontextprotocol.io/v0.1/servers?limit=30`（仅分页，无搜索） |
| **GitHub** | 健康度：star / commit / contributors | `gh api repos/{owner}/{repo}` |

Smithery 是主数据源（4845+ servers，支持搜索、useCount、verified 标记、部署状态）。
MCP 官方 Registry 无搜索功能，仅作为补充验证。

## 输入解析

从用户消息中提取：
1. **搜索关键词**（必需）：如 "database"、"video"、"github"
2. **Top N**（可选，默认 3）

## 工作流程

### Phase 1: 搜索候选

```bash
curl -s "https://registry.smithery.ai/servers?q={keyword}&pageSize=20"
```

解析返回的 `servers` 数组和 `pagination`。

每个候选提取：
- `qualifiedName` — 唯一标识
- `displayName` — 显示名
- `description` — 描述
- `verified` — 是否经过 Smithery 验证
- `useCount` — 使用次数
- `remote` / `isDeployed` — 是否远程可用
- `createdAt` — 创建时间
- `score` — Smithery 内置评分

**验证**：如果搜索结果为空，告知用户"未找到匹配的 MCP Servers，请换个关键词试试"并停止。

### Phase 2: 评估每个候选

对 Top 20 候选**并行**获取详细数据：

**Step A: Smithery 详情（必须）**

```bash
curl -s "https://registry.smithery.ai/servers/{qualifiedName}"
```

提取：
- `tools` — 暴露的工具列表（名称、描述）
- `security` — 安全信息（如有）
- `deploymentUrl` — 部署地址
- `connections` — 连接方式（http / stdio）
- `resources` — 暴露的资源

**Step B: GitHub 健康度（如果能找到仓库）**

Smithery 详情中不直接包含 GitHub URL。获取方式：
1. 用 `qualifiedName` 去 MCP 官方 Registry 查找对应的 `repository.url`
2. 如果找不到，用 `gh search repos "{displayName} mcp server" --limit=3` 搜索
3. 如果仍找不到，该候选的健康分记为 0

找到仓库后：

```bash
# 提取 owner/repo
echo "{repo_url}" | sed 's|https://github.com/||' | cut -d'/' -f1,2

# 获取仓库信息
gh api repos/{owner}/{repo} --jq '{stars: .stargazers_count, pushed: .pushed_at, license: (.license.spdx_id // "None")}'

# 获取 contributor 数量
gh api "repos/{owner}/{repo}/contributors?per_page=100" --jq 'length'
```

### Phase 3: 计算评分

每个候选计算四维分数，总分 0-100：

#### 质量分 (0-100)

```
Smithery score 归一化到 0-100：score × 1000（Smithery score 通常在 0.01-0.1 之间）
上限 100。
如果无 score → 50（默认值）
```

#### 安全分 (0-100)

MCP Server 的安全评估数据远不如 skillstore.io 丰富。基于可用信号：

```
基础分：60
verified=true          → +20
security 字段有内容     → +10（说明有安全说明）
remote=true + isDeployed=true → +5（远程部署比本地安装更安全，沙箱化）
无 security 且 verified=false → -10
每个暴露的工具如果有描述 → +1（上限 +5）
```

#### 社区分 (0-100)

```
useCount: ≥500→35, ≥100→25, ≥50→15, ≥10→8, else→0
createdAt 距今: <30天→20, <90天→15, <180天→10, <365天→5, else→0（越新越好说明活跃）
verified: +20（Smithery 验证通过），否 → 0
其余: 25分按比例分配
```

#### 健康分 (0-100)（来自 GitHub）

```
Stars:       ≥5000→30, ≥1000→20, ≥200→12, ≥50→6, else→0
Last push:   ≤30天→30, ≤90天→20, ≤180天→10, ≤365天→5, else→0
Contributors:≥10→25, ≥5→15, ≥2→8, 1→2
License:     MIT/Apache→15, 有其他→8, 无→0

无 GitHub 仓库时：健康分 = 0
```

#### 总分

```
总分 = 质量分 × 0.20 + 安全分 × 0.30 + 社区分 × 0.20 + 健康分 × 0.30
```

四舍五入取整。

**注意**：如果某候选无 GitHub 仓库，健康分为 0，此时其他维度权重不变（不重新分配），总分自然偏低。

### Phase 4: 生成报告

按总分降序排列，取 Top N。

**报告格式**：

```
## FindMCPs 评估报告

搜索「{关键词}」，评估了 {总数} 个候选。以下为 Top {N}：

### 🥇 {displayName} — 总分 {总分}/100
- 🔗 https://smithery.ai/servers/{qualifiedName}
- ⭐ GitHub: {stars} stars | 更新于 {last_push} | {contributors} 人维护 | {license}
- 📊 健康:{健康分} | 安全:{安全分} | 质量:{质量分} | 社区:{社区分}
- 🔒 验证: {已验证✓ / 未验证} | 部署: {已部署/未部署} | 安全说明: {有/无}
- 📥 {useCount} 次使用
- 🛠️ 工具: {tool1}, {tool2}, {tool3}...（共 {N} 个）
- 💡 {description 的前100字}

### 🥈 {displayName} — 总分 {总分}/100
...

### 🥉 {displayName} — 总分 {总分}/100
...
```

**注意**：如果多数候选无 GitHub 仓库（健康分为 0），在报告末尾说明：

```
ℹ️ 部分 MCP Server 无关联的 GitHub 仓库，健康分默认为 0。评分主要基于安全性和社区使用量。
```

**安装指引**：报告末尾追加：

```
## 安装方式

MCP Server 安装到 Claude Code 需要添加到 ~/.claude/settings.json 或项目 .claude/settings.json 的 mcpServers 配置中。
选择你想安装的 MCP Server，告诉我序号（🥇🥈🥉），我会生成对应的配置并帮你安装。
```

### Phase 5: 用户选择

等待用户选择序号，然后：

1. 获取选中 MCP Server 的 `connections` 配置
2. 生成 `mcpServers` 配置片段
3. 提示用户确认后写入 settings.json

**配置模板**：

远程 MCP（推荐）：
```json
{
  "mcpServers": {
    "{name}": {
      "url": "{deploymentUrl}/mcp"
    }
  }
}
```

本地 MCP（如果有 stdio 连接方式）：
```json
{
  "mcpServers": {
    "{name}": {
      "command": "npx",
      "args": ["-y", "{package}"]
    }
  }
}
```

## 边界情况

- **Smithery API 限流**：暂无已知限流，但如果 429 则等待后重试
- **无 GitHub 仓库**：健康分 = 0，不影响其他维度评分
- **GitHub 搜索无结果**：尝试用 `displayName` 搜索，再用 `description` 中的关键词搜索
- **搜索结果为空**：提示用户换关键词，停止
- **所有候选总分都很低（<40）**：提醒"当前搜索结果整体质量较低，建议换关键词"
- **安全信息缺失**：MCP 生态的安全审计数据远不如 Skills 生态完善，需向用户明确说明这一局限性
