# 3D 视频制作（@remotion/three）

使用 React Three Fiber 在 Remotion 中创建 3D 动画视频。

## 适用场景

| 场景 | 说明 | 示例 |
|------|------|------|
| 产品展示 | 3D 模型旋转、拆解动画 | 手机产品宣传片 |
| 角色动画 | 卡通角色讲解、故事叙述 | 育儿科普视频 |
| 数据可视化 | 3D 图表、空间数据 | 地理信息、建筑展示 |
| Logo 动画 | 品牌 3D Logo 入场 | 片头片尾 |

## 安装

```bash
npm i three @react-three/fiber @remotion/three @types/three
npm i @react-three/drei  # 工具库（GLTF、Text 等）

# 官方模板
npx create-video@latest --template three
```

## 基础示例

```tsx
import { ThreeCanvas } from "@remotion/three";
import { useCurrentFrame, useVideoConfig, interpolate, spring } from "remotion";
import { useThree } from "@react-three/fiber";

const My3DScene = () => {
  const frame = useCurrentFrame();
  const { fps, durationInFrames } = useVideoConfig();
  const camera = useThree((state) => state.camera);

  useEffect(() => {
    camera.position.set(0, 0, 5);
    camera.lookAt(0, 0, 0);
  }, [camera]);

  const rotation = interpolate(frame, [0, durationInFrames], [0, Math.PI * 2]);
  const scale = spring({ frame, fps, config: { damping: 10, stiffness: 100 } });

  return (
    <mesh rotation={[0, rotation, 0]} scale={scale}>
      <boxGeometry args={[1, 1, 1]} />
      <meshStandardMaterial color="royalblue" />
    </mesh>
  );
};

export const My3DVideo = () => {
  const { width, height } = useVideoConfig();
  return (
    <ThreeCanvas width={width} height={height}>
      <ambientLight intensity={0.5} />
      <pointLight position={[10, 10, 10]} />
      <My3DScene />
    </ThreeCanvas>
  );
};
```

## 加载 GLTF 模型

```tsx
import { useGLTF } from "@react-three/drei";

const Model = () => {
  const frame = useCurrentFrame();
  const { scene } = useGLTF("/models/character.glb");
  const rotation = interpolate(frame, [0, 150], [0, Math.PI * 2]);

  return <primitive object={scene} rotation={[0, rotation, 0]} scale={0.5} />;
};

// 命令行转换 GLTF → React 组件
// npx gltfjsx model.glb
```

## 视频作为 3D 纹理

```tsx
import { useOffthreadVideoTexture } from "@remotion/three";
import { staticFile } from "remotion";

// 推荐：帧精确
const texture = useOffthreadVideoTexture({ src: staticFile("/video.mp4") });

<mesh>
  <planeGeometry args={[4, 3]} />
  {texture && <meshBasicMaterial map={texture} />}
</mesh>
```

## 3D 角色组合（基础几何体）

```tsx
const CartoonCharacter = ({ emotion = "happy" }) => {
  const frame = useCurrentFrame();
  const eyeScale = emotion === "happy" ? 1 : 0.5;
  const legSwing = Math.sin(frame * 0.2) * 0.3;

  return (
    <group>
      {/* 头部 */}
      <mesh position={[0, 1.5, 0]}>
        <sphereGeometry args={[0.5, 32, 32]} />
        <meshStandardMaterial color="#FFE4C4" />
      </mesh>
      {/* 身体 */}
      <mesh position={[0, 0.5, 0]}>
        <capsuleGeometry args={[0.3, 0.8, 16, 32]} />
        <meshStandardMaterial color="#4169E1" />
      </mesh>
      {/* 左腿 */}
      <mesh position={[-0.15, -0.3, 0]} rotation={[legSwing, 0, 0]}>
        <cylinderGeometry args={[0.08, 0.08, 0.6]} />
        <meshStandardMaterial color="#333" />
      </mesh>
      {/* 右腿 */}
      <mesh position={[0.15, -0.3, 0]} rotation={[-legSwing, 0, 0]}>
        <cylinderGeometry args={[0.08, 0.08, 0.6]} />
        <meshStandardMaterial color="#333" />
      </mesh>
    </group>
  );
};
```

## 踩坑经验

### WebGL 上下文溢出

**症状**：多个 3D 场景同时渲染时报错 `Error creating WebGL context`

**原因**：浏览器限制 WebGL 上下文数量（通常 8-16 个）

**解决方案**：

1. 渲染配置使用 `angle` OpenGL 引擎：

```ts
// remotion.config.ts
export default {
  chromiumOptions: { gl: "angle" },
};
// 或 CLI：npx remotion render --gl=angle MyVideo out.mp4
```

2. 懒加载场景 — 只渲染当前帧附近的 3D 内容：

```tsx
const LazyScene = ({ sceneStart, sceneDuration, children }) => {
  const frame = useCurrentFrame();
  const buffer = 30;
  const shouldRender = frame >= sceneStart - buffer &&
                        frame <= sceneStart + sceneDuration + buffer;
  if (!shouldRender) return null;
  return <>{children}</>;
};
```

### 相机持续抖动

**错误写法** — 永远无法精确到达目标：
```tsx
useEffect(() => {
  camera.position.z += (targetZ - camera.position.z) * 0.05;
}, [frame]);
```

**正确方案 A**：spring 动画
```tsx
const z = spring({
  frame: frame - transitionFrame, fps,
  from: camera.position.z, to: targetZ,
  config: { damping: 20, stiffness: 100 },
});
camera.position.z = z;
```

**正确方案 B**：直接设置（无过渡）
```tsx
camera.position.set(0, 0, targetZ);
camera.lookAt(0, 0, 0);
```

### 网格图像旋转 90 度

**根因**：`row` 对应 y 轴，`col` 对应 x 轴，映射反了。

```tsx
// 错误：row→x, col→y
const x = (row - size/2) * cellSize;  // 错！
const y = (col - size/2) * cellSize;  // 错！

// 正确：col→x, row→y（且 y 要翻转）
const x = (col - size/2 + 0.5) * cellSize;
const y = ((size - 1 - row) - size/2 + 0.5) * cellSize;
```

**记忆口诀**：
- 图像坐标：`image[row][col]` = `image[y][x]`
- 3D 坐标：x 向右，y 向上
- 翻转 row：图像 row=0 在顶部，3D y=max 在顶部

### Sequence 内的 useCurrentFrame

`<Sequence>` 内部的 `useCurrentFrame()` 返回**相对于 Sequence 开始的帧号**，不是全局帧号。

```tsx
<Sequence from={60} durationInFrames={90}>
  <MyScene />  {/* 这里 useCurrentFrame() 从 0 开始，不是 60 */}
</Sequence>
```

### 服务端渲染必须配置 gl

```ts
await renderMedia({
  composition, serveUrl, outputLocation: "out.mp4",
  chromiumOptions: { gl: "angle" },
});
```

## 进阶资源

| 资源 | 用途 | 链接 |
|------|------|------|
| Mixamo | 免费骨骼动画库 | https://www.mixamo.com |
| Sketchfab | 免费/付费 3D 模型 | https://sketchfab.com |
| Ready Player Me | 虚拟人物生成 | https://readyplayer.me |
| Spline | 在线 3D 设计工具 | https://spline.design |
| gltfjsx | GLTF 转 React 组件 | `npx gltfjsx model.glb` |

### 进阶方向

1. **Blender → GLTF**：用 Blender 建模，导出 GLTF 格式，用 `useGLTF` 加载
2. **Mixamo 动画**：下载 FBX 动画，转换为 GLTF，用 `useAnimations` 播放
3. **Spline 设计**：在 Spline 设计 3D 场景，用 `@splinetool/r3f-spline` 导入
