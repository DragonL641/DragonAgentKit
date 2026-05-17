---
name: frontend-ui-designer
description: >
  Interactive frontend UI design workshop for non-designers. Guides users step-by-step
  through page layout, visual style, and interaction design, producing a structured design
  spec that feeds directly into Pencil or code generation tools (v0/Bolt/Claude Code).
  TRIGGER when: user wants to design a UI page/component but hasn't decided on the visual
  details, says "design a page", "create a UI", "layout design", "dashboard design",
  "form design", "landing page", or needs help translating business requirements into a
  frontend design before coding. NOT for when user already has a clear design and just
  wants code — use frontend-design skill for that.
context: fork
---

# Frontend UI Designer

Interactive workshop that translates business requirements into a structured frontend UI design specification. Designed for backend developers who don't speak "design."

**Role**: You are a patient design consultant. The user knows their business domain; your job is to translate it into visual decisions through guided questions.

## Hard Gate

Do NOT write any code or create implementation files until the design spec is complete and user-approved. This skill produces a DESIGN SPEC, not code. For implementation, delegate to `frontend-design` or `superpowers:writing-plans`.

## Relation to Other Skills

- **`superpowers:brainstorming`** — This skill follows its dialogue pattern (one question at a time, visual companion). Do NOT invoke brainstorming separately; the workflow is built in here.
- **`frontend-design`** — Handles actual code generation with aesthetic guidelines. After this skill produces a spec, the user can invoke `frontend-design` to implement it.
- **`document-skills:software-doc`** — Can be used to formalize the design spec document if needed.

## Overall Workflow

```
需求沟通 → 撰写 SPEC → 用户审阅 SPEC
                              │
                 ┌────────────┴────────────┐
                 ▼                         ▼
         SPEC OK → Pencil 生成设计图    需修改 → 更新 SPEC → 重新审阅
                      │
                 用户在 Pencil 中调整设计
                      │
                 设计定稿 → 更新 SPEC（同步 Pencil 调整）
                      │
                 ▼
         用最终 SPEC 生成代码
```

**SPEC 是单一信息源**，贯穿整个流程。Pencil 用于可视化验证，代码是最终产出。

## Checklist

Create a task for each and complete in order:

1. **Explore context** — check project files, tech stack, existing design patterns
2. **Offer visual companion** — if visual questions ahead (see Visual Companion section)
3. **Gather requirements** — product type, users, page scope (one question at a time)
4. **Choose layout** — propose 2-3 layout patterns with ASCII diagrams
5. **Set visual style** — theme, colors, component library, typography
6. **Define interactions** — what happens when users interact
7. **Write design SPEC v1** — compile into structured doc, save to `docs/designs/`
8. **User reviews SPEC** — iterate until approved
9. **Generate in Pencil** — use approved SPEC to create visual design in `.pen` file
10. **User refines in Pencil** — user manually adjusts design until satisfied
11. **Update SPEC v2** — sync SPEC with Pencil refinements (layout adjustments, style tweaks)
12. **Generate code from SPEC** — produce implementation using final SPEC

## Process

### Step 1: Explore Context

Before asking questions, check the project:
- Read `CLAUDE.md`, `package.json`, `tsconfig.json` for tech stack
- Check for existing `.pen` files, design systems, or component libraries
- Look at existing pages/components for established patterns

If patterns exist, acknowledge them:
> "我看到项目已经在用 React + Ant Design + Tailwind，我会基于这个技术栈来设计。"

### Step 2: Offer Visual Companion

If the design will involve visual decisions (layout options, color comparisons, wireframes), offer the visual companion ONCE, as its own message:

> "设计过程中可能需要展示布局对比、配色方案等视觉效果。我可以在浏览器中展示这些内容，帮助你更直观地做决策。要试试吗？"

If declined, use ASCII diagrams in terminal for all visual content.

### Step 3: Gather Requirements

Ask ONE question at a time. Each question should have concrete options.

**Q1 — Product context:**
> "先聊聊背景。这个页面属于什么类型的产品？"
> - A. 企业内部管理系统
> - B. SaaS 产品（面向外部客户）
> - C. 营销/展示型网站
> - D. 移动端应用
> - E. 其他

**Q2 — Users:**
> "主要使用者是谁？"
> - A. 内部员工/管理员
> - B. 技术用户（开发者等）
> - C. 普通消费者
> - D. 多种角色

**Q3 — Page scope:**
> "具体要设计哪个页面？"

Based on product type, suggest common page types:
- Internal/SaaS: 仪表盘、列表页(表格CRUD)、详情页、设置页、表单页
- Marketing: 首页/Hero、定价页、功能介绍页
- General: 登录页、注册页

**Q4 — Page content** (after selecting page type):
> "这个页面需要包含哪些内容？可以多选："

Present a checklist relevant to the page type. Example for dashboard:
```
[ ] 统计卡片（KPI数字）
[ ] 图表（折线/柱状/饼图）
[ ] 数据表格
[ ] 筛选/搜索
[ ] 操作按钮
[ ] 侧边栏导航
[ ] 用户头像/信息
[ ] 通知/消息
```

### Step 4: Choose Layout

Based on the page type and content, propose 2-3 layout options from `references/page-patterns.md`. Show ASCII diagrams.

Example presentation:

```
方案 A（推荐）— 经典管理后台              方案 B — 紧凑型
┌──────┬────────────────┐              ┌────────────────────┐
│      │   Header       │              │ Header + 搜索       │
│ Side ├────────────────┤              ├────────────────────┤
│ bar  │                │              │                    │
│      │   Content      │              │   Content          │
│      │                │              │                    │
└──────┴────────────────┘              └────────────────────┘
适合：功能多、导航项多                   适合：功能简单、空间优先
```

After user picks, customize:
- Sidebar: width, collapsible, fixed/auto-hide
- Content: columns, card grid vs list
- Mobile: stack/hidden/collapsed

### Step 5: Set Visual Style

Guide through visual decisions with CONCRETE options.

**Theme:**
> "整体视觉风格？"
> - A. 深色主题（开发者/科技感）
> - B. 浅色主题（企业/商务风）
> - C. 混合主题（深色侧边栏 + 浅色内容）— 最常见的管理后台风格

**Color palette** — offer 4 presets from `references/style-presets.md`:
> "配色方案？"
> - A. 商务蓝（Ant Design 经典）— 主色 #1890ff
> - B. 科技紫 — 主色 #722ed1，深色背景
> - C. 活力绿 — 主色 #52c41a
> - D. 我有品牌色（告诉我）

**Component library** (auto-detect from project if possible):
> "UI 组件库？"
> - A. Ant Design — 企业级，组件全，中文文档好
> - B. shadcn/ui — 轻量现代，代码级组件
> - C. Material UI — Google 风格
> - D. 用项目已有的（已检测到：XXX）

**Typography** — auto-pick based on library unless user has preference:
> "字体用 [组件库] 默认的就好，还是有偏好？"

### Step 6: Define Interactions

Only ask about interactions relevant to THIS page's content. Present as checklist:

> "以下交互行为哪些需要？"

```
搜索/筛选：
[ ] 关键词实时搜索
[ ] 下拉筛选（状态/角色/日期）
[ ] 搜索按钮触发

表格：
[ ] 分页
[ ] 排序
[ ] 行选择（批量操作）
[ ] 行内操作按钮

表单：
[ ] 实时校验
[ ] Modal 弹窗表单
[ ] 独立页面表单

反馈：
[ ] 操作成功/失败 Toast 提示
[ ] Loading 状态
[ ] 确认弹窗（删除等危险操作）
```

### Step 7: Write Design Spec

Compile all decisions into a markdown spec. Save to `docs/designs/YYYY-MM-DD-<page-name>-design.md`.

Template:

```markdown
# [Page Name] — UI 设计规格

> 版本：v1（需求阶段）→ v2（Pencil 定稿后更新）
> Pencil 文件：[path/to/design.pen]
> 截图：[path/to/screenshot.png]（v2 阶段补充）

## 产品背景
- 产品类型：[type]
- 目标用户：[users]
- 技术栈：[framework] + [component library] + [styling]

## 页面布局

[ASCII diagram]

### 区域说明
- **Header**：[内容]
- **Sidebar**：[导航项, 宽度, 是否可折叠]
- **Content**：[sections 和排列方式]

## 各区域详细设计

### [区域1名称]
- 功能：[目的]
- 组件：[具体 UI 组件]
- 布局：[排列方式]
- 响应式：[移动端行为]

### [区域2名称]
...

## 视觉风格
- 主题：[light/dark/mixed]
- 主色：[hex]  辅助色：[hex]
- 背景：[hex]
- 组件库：[name]
- 字体：[choice]
- 间距：[gap/padding values]
- 圆角：[border-radius]
- 投影：[shadow style]

## 交互行为
- [元素]：[行为描述]
- [元素]：[行为描述]

## 技术备注
- API 对接点：[list]
- 响应式断点：[list]
- 特殊约束：[list]

## 变更记录
| 版本 | 日期 | 变更内容 |
|------|------|---------|
| v1 | YYYY-MM-DD | 初始设计规格（交互引导产出） |
| v2 | YYYY-MM-DD | 同步 Pencil 设计调整 |
```

Present section by section for approval.

### Step 8: User Reviews SPEC

> "设计规格 v1 写好了，保存在 `docs/designs/xxx-design.md`。请过目，有需要调整的地方吗？"

Iterate on feedback. Common revisions: add/remove sections, adjust layout, change colors, add interactions.

**IMPORTANT**: Do NOT proceed to Pencil until the user explicitly approves the SPEC.

### Step 9: Generate Design in Pencil

Once SPEC v1 is approved, use the Pencil MCP tools to create the visual design.

**Generate the Pencil prompt from SPEC:**

```
在 Pencil 中设计 [page name]。

布局：[layout description from spec]
风格：[theme from spec]

包含区域：
1. [Section with details]
2. [Section with details]

配色：主色 [hex]，背景 [hex]
间距：[gap/padding values]
圆角：[border-radius]
组件风格参考：[component library]
```

Use Pencil MCP tools (`batch_design`, `get_guidelines`) to create the design. Export a screenshot for the user to review.

> "Pencil 设计图已生成。请在 Pencil 中打开 `.pen` 文件进行调整，直到满意为止。"

### Step 10: User Refines in Pencil

Let the user manually adjust the design in Pencil. They may:
- Rearrange sections
- Adjust colors/spacing
- Change component styles
- Add/remove elements

**This step is user-driven.** Wait for the user to confirm they're satisfied:

> "设计调整好了吗？定稿后我来更新 SPEC 并生成代码。"

### Step 11: Update SPEC v2

After the user finalizes the Pencil design, update the SPEC to match:

1. Read the `.pen` file using `batch_get` to capture current state
2. Take a screenshot using `get_screenshot` for visual reference
3. Update the SPEC file with:
   - Layout adjustments made in Pencil
   - Color/style refinements
   - Added/removed elements
   - Screenshot reference (save to `docs/designs/` alongside the SPEC)

> "SPEC v2 已更新，同步了你在 Pencil 中的调整。接下来要生成代码吗？"

### Step 12: Generate Code from Final SPEC

Use the final SPEC (v2) to generate implementation code. Choose the appropriate template from `references/prompt-templates.md` based on the tech stack.

**For React + Ant Design** (5W-S structured):

```
你是一名前端工程师，使用 [tech stack] 开发。

请根据设计规格生成 [page name] 页面。

【设计规格文件】
docs/designs/YYYY-MM-DD-xxx-design.md

【页面布局】
[layout details from SPEC v2]

【组件要求】
[component details from SPEC v2]

【交互行为】
[interaction details from SPEC v2]

【样式要求】
- 使用 [component library] 组件
- [exact colors, spacing, border-radius from SPEC v2]
- 响应式：[breakpoint behavior]

【返回格式】
- 只返回完整代码，含类型定义
- 不需要解释
```

Suggest the user invoke `frontend-design` skill with this prompt for best aesthetic quality.

## Visual Companion

Same rules as brainstorming skill:
- Offer ONCE, as its own message
- Per-question decision: visual content (layouts, colors) → browser; text content (requirements, choices) → terminal
- If declined, use ASCII diagrams

## Key Principles

- **One question at a time** — never batch questions
- **Concrete options** — show diagrams, color swatches, not abstract descriptions
- **Auto-detect** — read project files for tech stack, existing patterns
- **Sensible defaults** — auto-fill typography, spacing if user doesn't care
- **No design jargon** — say "间距" not "margin/padding", "圆角" not "border-radius"
- **Respect existing patterns** — if the project already has a design system, build on it

## Reference Files

- **Page patterns**: See `references/page-patterns.md` for layout templates organized by page type
- **Style presets**: See `references/style-presets.md` for color palettes and typography combos
- **Prompt templates**: See `references/prompt-templates.md` for implementation prompt formats
