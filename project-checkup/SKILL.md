---
name: project-checkup
description: Comprehensive project health check across 15 dimensions. Analyzes code for functional defects, error handling, simplification opportunities, architecture consistency, code standards, performance, resource management, cross-platform compatibility, dependency management, build/CI, documentation consistency, configuration management, API design, user experience, and test quality. Outputs a severity-sorted report with optional persistent file, then optionally enters interactive confirmation to generate a fix plan.
---

# Project Checkup — 全面项目健康检查

对项目进行多维度的全面审查，发现功能缺陷、性能问题、架构不一致等各类问题，并协助用户制定修复方案。

## 触发方式

```
/project-checkup                          # 全量审查（默认）
/project-checkup 只查依赖和构建            # 自然语言限定范围
```

用户可用自然语言限定审查范围或聚焦特定维度。如未限定，则弹出选择让用户确认。

## 核心原则

- **通用性**：不预设技术栈，动态适配任何项目类型（Python/Node/Rust/Go/Java 等）
- **项目自适应**：Phase 1 检测项目特征后，动态决定适用维度和审查策略
- **报告按严重等级排序**：HIGH → MEDIUM → LOW，维度作为标签而非分组依据
- **用户主导**：维度选择、报告格式、是否交互确认均由用户在执行过程中决定

## 15 审查维度与评级标准

每个维度预定义 HIGH/MEDIUM/LOW 评级标准，确保审查结果一致性。

| # | 维度 | HIGH | MEDIUM | LOW |
|---|------|------|--------|-----|
| 1 | 功能缺陷 | crash/数据丢失/错误结果 | 边界未处理但低概率触发 | 极端 edge case |
| 2 | 错误处理 | 异常吞没导致静默失败 | 错误信息不充分 | 非关键路径缺日志 |
| 3 | 代码简化 | 大量重复/死代码影响可维护性 | 中等冗余/可合并逻辑 | 微小简化机会 |
| 4 | 架构一致性 | 跨层直接调用/职责混乱 | 轻微模式不一致 | 命名不完全统一 |
| 5 | 代码规范 | 普遍违反最佳实践/类型安全缺失 | 部分命名不一致 | 个别风格问题 |
| 6 | 性能瓶颈 | 同步阻塞关键路径/明显内存泄漏 | 不必要重复计算/IO | 微优化机会 |
| 7 | 资源管理 | 资源未释放/生命周期管理缺失 | 清理不完整但不致命 | 理论风险 |
| 8 | 跨平台兼容 | 某平台完全无法运行 | 某功能在某平台异常 | 路径风格等小问题 |
| 9 | 依赖管理 | 安全漏洞/废弃依赖 | 未使用依赖/版本过旧 | 次要版本落后 |
| 10 | 构建与 CI | 构建失败/CI 覆盖缺失 | 非关键步骤缺失 | 配置可优化 |
| 11 | 文档一致性 | 文档与代码行为严重不符 | 参数/配置项文档遗漏 | 措辞不准确 |
| 12 | 配置管理 | 配置不生效/默认值危险 | 配置冗余/缺少校验 | 命名不一致 |
| 13 | API 设计 | 接口 breaking/数据格式错误 | 响应不完整/缺校验 | 命名/风格问题 |
| 14 | 用户体验 | 核心流程 UX 严重缺陷 | API UX 不友好/可观测性不足 | 轻微 UX 优化 |
| 15 | 测试质量 | 关键路径零测试 | 覆盖率低/测试质量差 | 个别测试可优化 |

## 工作流

### Phase 1: 项目识别与自适应

**目标**：检测项目特征，动态决定审查策略。

**执行步骤**：
1. 扫描项目根目录，检测项目类型（通过文件特征推断）：
   - Python: `pyproject.toml` / `setup.py` / `requirements.txt`
   - Node.js: `package.json` / `pnpm-lock.yaml` / `yarn.lock`
   - Rust: `Cargo.toml`
   - Go: `go.mod`
   - Java: `pom.xml` / `build.gradle`
   - 混合项目：同时存在多种配置文件
2. 读取项目文档：CLAUDE.md（如有）、README.md（如有）
3. 分析目录结构，识别关键模块和层级
4. **动态决定适用维度**：
   - 所有项目默认启用：功能缺陷、错误处理、代码简化、架构一致性、代码规范、性能瓶颈、依赖管理
   - 有 ML 模型/数据库/长生命周期资源 → 启用"资源管理"
   - 项目声明多平台支持或有多平台构建配置 → 启用"跨平台兼容"
   - 有构建脚本或 CI 配置 → 启用"构建与 CI"
   - 有 CLAUDE.md 或 README → 启用"文档一致性"
   - 有配置系统（配置文件、环境变量） → 启用"配置管理"
   - 有 API 层（HTTP/WebSocket/CLI/SDK） → 启用"API 设计"
   - 有前端代码或 CLI 界面 → 启用"用户体验"
   - 有测试目录或测试框架 → 启用"测试质量"

### Phase 1+: 用户选择

**使用 AskUserQuestion 询问用户两个问题**：

**Q1: 审查维度**
- 展示动态检测到的适用维度列表
- 选项：`全量审查（N 个维度）(Recommended)` / `自定义维度`
- 如果用户选择自定义，提示用户用自然语言指定要检查的维度

**Q2: 报告格式**
- 选项：`对话内输出 (Recommended)` / `生成报告文件（PROJECT_CHECKUP_REPORT.md）`
- 如果选择生成报告文件，分析完成后将报告写入项目根目录

### Phase 2: 架构理解

**目标**：建立架构层 + 模式层两层理解（不需要逐行通读）。

**启动 3 个并行 Explore agent**：

**Agent 1 — 架构层**：
- 分析目录结构和模块划分
- 识别层边界和数据流
- 找到核心接口/协议定义
- 理解模块间依赖关系

**Agent 2 — 模式层**：
- 识别错误处理惯例（try/catch 模式、错误传播方式）
- 识别异步/并发模式
- 识别配置流转方式
- 识别测试覆盖模式和约定
- 每个模块读 1-2 个代表文件即可

**Agent 3 — 基础设施**：
- 读取依赖文件和版本信息
- 读取 CI/CD 配置
- 读取构建脚本
- 读取环境配置

### Phase 3: 维度审查

**目标**：按维度分组执行审查，发现问题。

**启动 4 个并行 agent**（每个 agent 可使用 Explore 或 general-purpose 类型）：

| Agent | 覆盖维度 | 搜索策略 |
|-------|---------|---------|
| A - 代码质量 | 功能缺陷、错误处理、代码简化、架构一致性、代码规范 | 定向读关键路径代码，trace 调用链，检查边界条件和代码规范 |
| B - 性能资源 | 性能瓶颈、资源管理 | 搜索 IO 操作、阻塞调用、大对象分配、连接/资源加载模式 |
| C - 平台基建 | 跨平台、依赖管理、构建 CI、配置管理 | 读配置文件、构建脚本、CI YAML、lock 文件，检查平台特定代码 |
| D - 接口文档 | 文档一致性、API 设计、用户体验、测试质量 | 对比文档描述 vs 代码实际行为，检查接口定义和实现，评估 UX 和测试覆盖 |

**每个 agent 的输出要求**：
- 每个发现的问题必须包含：维度标签、文件路径:行号、问题描述、严重程度（按评级标准判定）、初步解决方案
- 不要报告不确定的问题，只报告有足够证据的发现

### Phase 4: 报告输出

**目标**：汇总所有发现，按严重等级全局排序输出报告。

**根据 Phase 1+ Q2 用户选择决定输出方式**：

#### 方式 A：对话内输出（默认）

直接在对话中输出报告，格式如下。

#### 方式 B：生成报告文件

将报告写入项目根目录 `PROJECT_CHECKUP_REPORT.md`，同时在对话中展示摘要。

#### 报告格式

```markdown
# Project Checkup Report

**Generated**: {timestamp}
**Project type**: {动态检测的项目类型}
**Git commit**: {commit hash}

## Summary
- **Total issues**: N (HIGH: X, MEDIUM: Y, LOW: Z)
- **Dimensions checked**: [适用维度数] / Skipped: [跳过维度数]

---

## 🔴 HIGH (X issues)

### 1. [功能缺陷] 简短问题标题
- **File**: path/to/file:42
- **Problem**: 一句话描述
- **Solution**: 初步方案描述

### 2. [错误处理] 另一个问题
- **File**: path/to/file:100
- **Problem**: ...
- **Solutions**:
  - A: 方案A描述
  - B: 方案B描述

## 🟡 MEDIUM (Y issues)

### 3. [依赖管理] 问题描述
...

## 🟢 LOW (Z issues)

### N. [文档一致性] 问题描述
...
```

**关键规则**：
- 全局按严重等级排序（HIGH → MEDIUM → LOW），同一等级内按维度编号排序
- 维度作为标签放在问题标题前（如 `[功能缺陷]`），不作为分组依据
- 每个问题编号连续，方便后续确认时引用

### Phase 4+: 是否进入交互确认

**报告输出后，使用 AskUserQuestion 询问用户**：

- 选项：`逐个确认并生成修复方案 (Recommended)` / `查看报告即可`

### Phase 5: 交互确认 → 修复方案（仅在用户选择时进入）

**目标**：批量收集用户对每个问题的处理决策，一次性生成最终修复方案。

#### Step 1: 批量收集决策

**按严重等级分批**（从 HIGH 开始），使用 AskUserQuestion 一次性展示最多 4 个问题，让用户快速选择：

对于每个问题，根据方案数量提供选项：
- **单方案问题**：`修复` / `暂缓` / `忽略`
- **多方案问题**：`方案A` / `方案B` / `暂缓` / `忽略`

**关键**：每批最多 4 个问题（工具限制），尽量一批内收齐所有问题。如果问题总数 ≤4，一次收齐。如果 >4，按 HIGH → MEDIUM → LOW 顺序分批，确保 HIGH 问题优先确认。

#### Step 2: 生成修复方案

收集完所有决策后，**一次性**输出最终修复方案：

```markdown
# Fix Plan

## Summary
- Fix: X issues
- Defer: Y issues
- Ignore: Z issues

## Fix Plan (按执行顺序)

### 1. [功能缺陷] 问题标题
- **File**: path/to/file:42
- **Action**: 方案A描述（用户选择）
- **Steps**:
  1. 具体步骤
  2. ...

### 2. ...

## Deferred Issues
| # | Problem | Dimension | Reason |
|---|---------|-----------|--------|
| 3 | ... | ... | 用户选择暂缓 |

## Ignored Issues
| # | Problem | Dimension |
|---|---------|-----------|
| 5 | ... | ... |
```

**关键原则**：用户做一轮快速选择 → 一次性输出最终方案，不反复刷新。
