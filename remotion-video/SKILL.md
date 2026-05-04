---
name: remotion-video
description: 使用 Remotion 框架以编程方式创建视频。Remotion 让你用 React 组件定义视频内容，支持动画、字幕、音乐可视化、3D 视频、教程讲解视频等。适用于程序化视频、批量生成、数据驱动视频、音乐可视化、自动字幕等场景。触发词："做个视频"、"生成视频"、"制作教程视频"、"Remotion视频"、"编程式视频"。
---

# Remotion Video

用 React 以编程方式创建 MP4 视频。

## 辅助工具

使用 Remotion 创建视频时，推荐配合以下工具获取更好的文档支持：

### @remotion/mcp（文档检索）

MIT 开源，当前免费使用。提供 Remotion 文档的语义搜索能力：

```json
{
  "mcpServers": {
    "remotion-documentation": {
      "command": "npx",
      "args": ["@remotion/mcp@latest"]
    }
  }
}
```

当需要查阅 Remotion API 细节（如 `<Sequence>` 的 props、`interpolate` 的配置项等）时，优先使用此 MCP 获取最新官方文档。

### Remotion Agent Skills（领域知识）

```bash
npx skills add remotion-dev/skills
```

加载 40+ 个 Remotion 领域的最佳实践规则文件（动画、音频、字幕、3D、图表等）。

## 快速开始

```bash
# 创建新项目
npx create-video@latest

# 开发预览
npm run dev

# 渲染输出
npx remotion render MyVideo out/video.mp4
```

### 项目结构

```
my-video/
├── src/
│   ├── Root.tsx           # 注册所有 Composition
│   ├── HelloWorld.tsx     # 视频组件
│   └── index.ts           # 入口
├── public/                # 静态资源（音频、图片）
├── remotion.config.ts     # 配置文件
└── package.json
```

## 推荐工作流：教程类视频

教程、讲解类视频的核心架构是**音频驱动场景切换**：

```
音频脚本 → TTS 生成 → audioConfig.ts → 场景组件 → 视频渲染
```

详细架构和代码模板见 [references/tutorial-architecture.md](references/tutorial-architecture.md)。

AI 语音解说集成（MiniMax TTS + Edge TTS）见 [references/audio-sync.md](references/audio-sync.md)。

## 参考文件

| 文件 | 用途 | 何时读取 |
|------|------|---------|
| references/audio-sync.md | AI 语音解说集成（MiniMax + Edge TTS） | 需要添加语音解说时 |
| references/tutorial-architecture.md | 教程类视频架构（场景驱动） | 制作教程/讲解视频时 |
| references/3b1b-style-guide.md | 3Blue1Brown 可视化风格指南 | 制作教育类/讲解类视频时 |
| references/process-animation.md | 过程动画组件库 | 需要展示计算过程、数据流动时 |
| references/3d-video.md | 3D 视频制作 + 踩坑经验 | 需要 3D 内容时 |

## 3B1B 风格

制作教育类视频时，遵循 3Blue1Brown 的可视化原则：

- **Why → What**：先提问为什么，再展示是什么
- **逐步构建**：元素一个个出现，不要整体淡入
- **颜色有语义**：蓝=正、红=负、黄=高亮、绿=结果
- **2D 优先**：清晰优先于炫酷，必要时才用 3D

详细的配色方案、组件模板和脚本撰写指南见 [references/3b1b-style-guide.md](references/3b1b-style-guide.md)。

## 过程动画

展示「怎么算」而非只展示「是什么」。提供了 4 个可复用的组件：

- **StepByStep** — 逐步显示计算过程
- **ValueFlyIn** — 计算结果飞入目标位置
- **CompareHighlight** — 多个值依次比较，胜出者高亮
- **SlidingWindow** — 卷积核/池化窗口滑动

详细代码和使用方式见 [references/process-animation.md](references/process-animation.md)。

## 3D 视频

使用 `@remotion/three` + React Three Fiber 创建 3D 动画。支持 GLTF 模型加载、视频纹理、角色动画等。

注意 WebGL 上下文限制和相机控制陷阱。详见 [references/3d-video.md](references/3d-video.md)。

## 工作流最佳实践

### npm scripts 配置

```json
{
  "scripts": {
    "dev": "remotion studio",
    "render": "remotion render MyVideo out/video.mp4"
  }
}
```

### 断点续作设计原则

长时间任务应支持断点续作：
1. **检查已存在文件**：跳过已完成的项目
2. **原子操作**：单个文件生成失败不影响已完成的
3. **进度保存**：失败时保留已完成的部分
4. **幂等执行**：重复运行产生相同结果

### 调试技巧

1. **Studio 热重载**：`npm run dev` 实时预览
2. **逐帧检查**：Studio 中拖动时间轴
3. **性能优化**：避免在组件内做重计算，用 `useMemo`
4. **静态文件**：放在 `public/` 目录，用 `staticFile()` 引用
