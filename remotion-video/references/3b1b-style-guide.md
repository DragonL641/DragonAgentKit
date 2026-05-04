# 3Blue1Brown 风格指南

针对教程、讲解类视频的可视化设计原则。

## 核心理念

```
3B1B 内核：让观众「自己发现」，而不是「被告知答案」
```

| 原则 | 说明 | 示例 |
|------|------|------|
| **Why → What** | 先提问为什么，再展示是什么 | "如何识别手写数字？" → 展示神经网络 |
| **逐步构建** | 元素一个个出现，不要整体淡入 | 神经元依次点亮，而非同时出现 |
| **颜色有语义** | 颜色传达信息，不是装饰 | 蓝=正、红=负、黄=高亮 |
| **数值具象化** | 显示具体数字让抽象概念落地 | 像素值 0.7、激活值 0.92 |
| **2D 优先** | 清晰优先于炫酷，必要时才用 3D | 网络结构用 2D，空间数据用 3D |

## 配色方案

```tsx
const COLORS_3B1B = {
  background: "#000000",     // 纯黑背景
  positive: "#58C4DD",       // 蓝色 - 正权重/正向
  negative: "#FF6B6B",       // 红色 - 负权重/负向
  highlight: "#FFFF00",      // 黄色 - 当前焦点/高亮
  result: "#83C167",         // 绿色 - 结果/正确
  text: "#FFFFFF",           // 白色 - 文字
  neutral: "#888888",        // 灰色 - 中性/未激活
  accent: "#FF8C00",         // 橙色 - 强调
};
```

## 2D/3D 混合策略

| 内容类型 | 推荐维度 | 原因 |
|----------|----------|------|
| 网络结构图 | 2D | 层次清晰，易于标注 |
| 数据流向 | 2D + 动画箭头 | 强调顺序和因果 |
| 卷积操作 | 2D 俯视图 | 网格对齐，数值可见 |
| 特征图堆叠 | 2.5D（透视） | 展示深度/通道数 |
| 3D 物体识别 | 3D | 内容本身是 3D |

2D 模式实现：正交相机 + 扁平几何体

```tsx
import { OrthographicCamera } from "@react-three/drei";

<OrthographicCamera makeDefault position={[0, 0, 10]} zoom={100} />

<mesh>
  <planeGeometry args={[1, 1]} />
  <meshBasicMaterial color={color} />
</mesh>
```

## 逐步构建动画

用 `delay` 参数控制元素依次出现：

```tsx
const StaggeredGroup: React.FC<{
  children: React.ReactNode[];
  delayPerItem?: number
}> = ({ children, delayPerItem = 8 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  return (
    <>
      {React.Children.map(children, (child, i) => {
        const delay = i * delayPerItem;
        const progress = spring({
          frame: frame - delay,
          fps,
          config: { damping: 12, stiffness: 100 },
        });

        if (frame < delay) return null;

        return (
          <group scale={Math.max(0, progress)} opacity={progress}>
            {child}
          </group>
        );
      })}
    </>
  );
};
```

## 数值标签组件

```tsx
import { Text } from "@react-three/drei";

const ValueLabel: React.FC<{
  value: number;
  position: [number, number, number];
  fontSize?: number;
}> = ({ value, position, fontSize = 0.15 }) => {
  const color = value > 0.5 ? COLORS_3B1B.positive :
                value < -0.5 ? COLORS_3B1B.negative :
                COLORS_3B1B.neutral;

  return (
    <Text
      position={position}
      fontSize={fontSize}
      color={color}
      anchorX="center"
      anchorY="middle"
      font="/fonts/JetBrainsMono-Regular.ttf"
    >
      {value.toFixed(2)}
    </Text>
  );
};
```

## 高亮焦点组件

```tsx
const FocusBox: React.FC<{
  position: [number, number, number];
  size: [number, number];
  label?: string;
}> = ({ position, size, label }) => {
  const frame = useCurrentFrame();
  const pulse = 1 + Math.sin(frame * 0.15) * 0.08;

  return (
    <group position={position}>
      <mesh scale={[pulse, pulse, 1]}>
        <planeGeometry args={size} />
        <meshBasicMaterial color={COLORS_3B1B.highlight} transparent opacity={0.2} />
      </mesh>
      <lineSegments>
        <edgesGeometry args={[new THREE.PlaneGeometry(...size)]} />
        <lineBasicMaterial color={COLORS_3B1B.highlight} linewidth={2} />
      </lineSegments>
      {label && (
        <Text position={[0, size[1] / 2 + 0.2, 0]} fontSize={0.12} color={COLORS_3B1B.highlight}>
          {label}
        </Text>
      )}
    </group>
  );
};
```

## 脚本撰写指南

**避免宣读式**：
```
"首先是输入层。图像是一个数字矩阵。"
```

**推荐探索式**：
```
"你能轻松认出这是数字 7，但你能描述你是怎么做到的吗？
（停顿 1 秒）
这正是神经网络要解决的问题。

让我们先看看计算机「看到」的是什么——
（数字网格逐个显示）
不是图像，而是 784 个数字。

那么问题来了：如何从这堆数字中识别出 7？"
```

**脚本结构模板**：
```
1. 提出问题（10%）— 用观众能共鸣的问题开场
2. 直觉猜测（15%）— 引导观众思考可能的方案
3. 逐步验证（50%）— 一步步展示机制，每步回答「为什么这样设计」
4. 形式化（15%）— 展示数学公式（可选）
5. 回顾总结（10%）— 完整流程快速回放，强调核心洞见
```

## 常见误区

| 误区 | 问题 | 改进 |
|------|------|------|
| 3D 炫技 | 旋转、透视分散注意力 | 用最简单的视角表达 |
| 颜色随意 | 红绿蓝只是装饰 | 建立颜色-含义映射 |
| 整体出现 | 观众不知道看哪里 | 逐个元素 + 高亮引导 |
| 只说 What | 观众不理解设计动机 | 先问 Why 再展示 What |
| 信息过载 | 一个场景塞太多概念 | 一个场景一个概念 |
