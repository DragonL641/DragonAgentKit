# 教程类视频架构（场景驱动）

教程、讲解类视频的核心架构：**音频驱动场景切换**。

## 架构概览

```
音频脚本 → TTS 生成 → audioConfig.ts → 场景组件 → 视频渲染
```

关键思想：
1. **音频决定时长**：每个场景的持续时间由音频长度决定
2. **场景即章节**：一个概念 = 一个场景 = 一段音频
3. **配置即真理**：`audioConfig.ts` 是音画同步的单一数据源

### audioConfig.ts 模板

```ts
import { SceneConfig } from "./types";

export const SCENES: SceneConfig[] = [
  { id: "01-intro", title: "开场", audioFile: "01-intro.mp3", durationInFrames: 450 },
  { id: "02-concept", title: "核心概念", audioFile: "02-concept.mp3", durationInFrames: 600 },
  { id: "03-demo", title: "演示", audioFile: "03-demo.mp3", durationInFrames: 900 },
  { id: "04-summary", title: "总结", audioFile: "04-summary.mp3", durationInFrames: 300 },
];

export const FPS = 30;

// 计算每个场景的起始帧
export const getSceneStart = (index: number): number => {
  let start = 0;
  for (let i = 0; i < index; i++) {
    start += SCENES[i].durationInFrames;
  }
  return start;
};

export const TOTAL_FRAMES = SCENES.reduce((sum, s) => sum + s.durationInFrames, 0);
```

### 场景切换 Hook

```tsx
import { useCurrentFrame } from "remotion";
import { SCENES } from "./audioConfig";

const useCurrentSceneIndex = () => {
  const frame = useCurrentFrame();
  let accumulated = 0;
  for (let i = 0; i < SCENES.length; i++) {
    accumulated += SCENES[i].durationInFrames;
    if (frame < accumulated) return i;
  }
  return SCENES.length - 1;
};
```

### 主场景组件模式

```tsx
import { AbsoluteFill, Audio, Sequence, staticFile, useVideoConfig } from "remotion";
import { ThreeCanvas } from "@remotion/three";
import { SCENES, getSceneStart, TOTAL_FRAMES } from "./audioConfig";

export const TutorialVideo: React.FC = () => {
  const { width, height } = useVideoConfig();
  const sceneIndex = useCurrentSceneIndex();
  const currentScene = SCENES[sceneIndex];

  return (
    <AbsoluteFill style={{ backgroundColor: "#1a1a2e" }}>
      {/* 3D 内容 — 根据 sceneIndex 条件渲染，同时只有一个 */}
      <ThreeCanvas width={width} height={height} camera={{ position: [0, 0, 4], fov: 50 }}>
        {sceneIndex === 0 && <Scene01Intro />}
        {sceneIndex === 1 && <Scene02Concept />}
        {sceneIndex === 2 && <Scene03Demo />}
      </ThreeCanvas>

      {/* 音频同步 — 每个场景一个 Sequence */}
      {SCENES.map((scene, idx) => (
        <Sequence key={scene.id} from={getSceneStart(idx)} durationInFrames={scene.durationInFrames}>
          <Audio src={staticFile(`audio/${scene.audioFile}`)} />
        </Sequence>
      ))}

      {/* UI 层：标题 + 进度 */}
      <div style={{ position: "absolute", top: 40, left: 0, right: 0, textAlign: "center" }}>
        <h1 style={{ color: "white", fontSize: 42 }}>教程标题</h1>
      </div>
      <div style={{ position: "absolute", bottom: 60, left: 60 }}>
        <span style={{ color: "white" }}>{currentScene?.title}</span>
      </div>
      <div style={{ position: "absolute", bottom: 30, left: 60, right: 60, height: 4, backgroundColor: "rgba(255,255,255,0.2)" }}>
        <div style={{ width: `${((sceneIndex + 1) / SCENES.length) * 100}%`, height: "100%", backgroundColor: "#3498DB" }} />
      </div>
    </AbsoluteFill>
  );
};
```

### Root.tsx 动态帧数

```tsx
import { Composition } from "remotion";
import { TutorialVideo } from "./TutorialVideo";
import { TOTAL_FRAMES } from "./audioConfig";

export const RemotionRoot: React.FC = () => (
  <Composition
    id="Tutorial"
    component={TutorialVideo}
    fps={30}
    durationInFrames={TOTAL_FRAMES}
    width={1920}
    height={1080}
  />
);
```

## 踩坑经验

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 场景切换生硬 | 直接切换无过渡 | 用 spring/interpolate 添加入场动画 |
| 3D 内容与音频不同步 | 硬编码帧数 | 所有时长从 audioConfig 读取 |
| 渲染时 WebGL 崩溃 | 多个 ThreeCanvas 同时存在 | 用 sceneIndex 条件渲染，同时只有一个 3D 场景 |
| 视频太简略 | 只有一个大场景 | **一个概念 = 一个场景组件**，分层讲解 |

## 场景组件设计原则

1. **单一职责**：每个场景组件只负责一个概念
2. **独立动画**：每个场景有自己的 useCurrentFrame()，动画从 0 开始
3. **延迟出现**：用 delay 参数控制元素依次出现
4. **相机适配**：不同场景可能需要不同相机位置

## 相机控制器

```tsx
import { useThree } from "@react-three/fiber";

// 推荐：直接设置相机位置，避免插值导致的持续抖动
const CameraController: React.FC<{ sceneIndex: number }> = ({ sceneIndex }) => {
  const { camera } = useThree();

  const cameraSettings: Record<number, [number, number, number]> = {
    0: [0, 0, 4],      // 开场：正面
    1: [0, 0, 3],      // 输入层：靠近
    2: [-0.5, 0, 3.5], // 卷积：偏左
    3: [0, 0, 5],      // 总结：拉远全景
  };

  const target = cameraSettings[sceneIndex] || [0, 0, 4];
  camera.position.set(target[0], target[1], target[2]);
  camera.lookAt(0, 0, 0);
  return null;
};
```

**不要用 `position += (target - position) * factor` 这种写法**，永远无法精确收敛，会导致画面持续抖动。
