# Prompt Templates

Ready-to-use prompt templates for generating frontend code from design specs.

## Table of Contents
1. [Pencil Design Prompt](#pencil-design-prompt)
2. [React + Ant Design Page](#react--ant-design-page)
3. [React + shadcn/ui Page](#react--shadcnui-page)
4. [Vue + Element Plus Page](#vue--element-plus-page)
5. [Pure HTML/CSS Page](#pure-htmlcss-page)
6. [Component Generation](#component-generation)

---

## Pencil Design Prompt

For use in Pencil canvas via `Cmd+K` or `pencil` CLI.

```
在 Pencil 中设计 [页面名称]。

布局：
[布局描述，参考设计规格中的 ASCII 图]

包含区域：
1. [区域1名称] — [包含的元素、组件]
2. [区域2名称] — [包含的元素、组件]
3. [区域3名称] — [包含的元素、组件]

风格：
- 主题：[深色/浅色/混合]
- 主色：[hex]  辅助色：[hex]
- 背景：[hex]
- 参考组件库：[Ant Design / shadcn UI / Material UI]
- 圆角：[8px / 12px / 16px]
- 间距：[8px / 16px / 24px]
- 投影：[subtle / medium / strong]
```

---

## React + Ant Design Page

5W-S structured prompt for React + Ant Design + TypeScript.

```
你是一名前端工程师，使用 React + TypeScript + Ant Design 开发。

请生成一个[页面名称]页面，用于[产品类型]的[位置]。
目的是让[用户角色]能够[业务目的]。

【页面布局】
- 整体：[布局模式，如"左侧固定侧边栏 + 右侧内容区"]
- 顶部：[Header 内容]
- 内容区：[各区域排列方式]
  - 区域1：[描述]
  - 区域2：[描述]

【组件要求】
- 使用 Ant Design 组件：[Table / Form / Modal / Card / Statistic / ...]
- 表格列：[列定义]
- 表单项：[字段定义]
- 弹窗内容：[描述]

【交互行为】
- 搜索：[实时 / 提交触发]
- 分页：[前端 / 后端]
- [操作按钮]：[行为描述，如"点击删除 → 确认弹窗 → 调用 API → 刷新列表"]
- 表单校验：[时机和规则]

【样式要求】
- 主题：[light / dark / compact]
- 主色：[hex]
- 表格行 hover 高亮
- 状态标签颜色：[映射关系]

【API 对接】
- GET /api/xxx — 获取列表，参数：[params]
- POST /api/xxx — 创建，body：[fields]
- PUT /api/xxx/:id — 更新
- DELETE /api/xxx/:id — 删除

【返回格式】
- 只返回完整 TSX 代码，含类型定义
- 不需要解释和安装指令
```

---

## React + shadcn/ui Page

```
你是一名前端工程师，使用 React + TypeScript + shadcn/ui + Tailwind CSS 开发。

请生成一个[页面名称]页面。

【页面布局】
[布局描述]

【组件要求】
- 使用 shadcn/ui 组件
- [具体组件列表]

【样式要求】
- Tailwind CSS 类名
- [主题 / 配色 / 间距]

【交互行为】
[交互描述]

【返回格式】
- 完整 TSX 代码
- 使用 Tailwind 类名
- 不需要解释
```

---

## Vue + Element Plus Page

```
你是一名前端工程师，使用 Vue 3 + TypeScript + Element Plus 开发。

请生成一个[页面名称]页面，用于[场景]。

【页面布局】
[布局描述]

【组件要求】
- Element Plus 组件：[列表]
- [具体细节]

【交互行为】
[交互描述]

【返回格式】
- Vue 3 SFC (<script setup lang="ts">)
- 不需要解释
```

---

## Pure HTML/CSS Page

```
请生成一个完整的 HTML 页面，包含内联 CSS 样式。

页面：[页面名称]
目的：[描述]

【布局】
[布局描述]

【样式要求】
- 配色：[hex values]
- 字体：[Google Fonts 链接]
- 响应式：[断点描述]

【内容区域】
1. [区域1]
2. [区域2]

【返回】
- 单个 HTML 文件，CSS 写在 <style> 中
- 包含 Google Fonts 引用
```

---

## Component Generation

通用组件生成 prompt。

```
请生成一个 [框架] + TypeScript 的可复用组件。

【组件名】[ComponentName]
【功能】[一段描述]
【Props】
  - [propName]: [type] — [说明] (默认值: [value])
  - [propName]: [type] — [说明]
【事件】
  - on[Event]: [触发时机]
【样式】
  - 使用 [组件库] 的 [具体组件] 作为基础
  - [自定义样式要求]
【状态】
  - loading: [描述]
  - empty: [描述]
  - error: [描述]
【返回】
  - 完整组件代码 + Props 接口定义
  - 不需要使用示例
```
