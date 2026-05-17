# 过程动画模式（Process Animation）

**核心理念**：不只展示「是什么」，更要展示「怎么算」。让观众亲眼看到数据如何流动、计算如何发生。

## 适用场景

| 场景 | 说明 | 示例 |
|------|------|------|
| 算法可视化 | 展示每一步操作 | 排序、搜索、图遍历 |
| 数学公式推导 | 逐项展开计算 | 矩阵乘法、卷积运算 |
| 数据处理流程 | 输入→变换→输出 | CNN 前向传播、数据清洗 |
| 决策过程 | 比较、筛选、最终选择 | 池化取最大值、softmax |

## 动画层级

```
静态展示 → 结构动画 → 过程动画
   ↓           ↓           ↓
  截图      元素出现     计算过程
            淡入淡出     数据流动
            相机移动     结果写入
```

## 组件库

### 1. 计算步骤展示（StepByStep）

逐步显示计算过程：

```tsx
const StepByStepCalc: React.FC<{
  steps: string[];      // ["1×0.5", "+ 0×0.3", "+ 1×(-0.2)", "= 0.3"]
  startFrame: number;
  framesPerStep?: number;
}> = ({ steps, startFrame, framesPerStep = 20 }) => {
  const frame = useCurrentFrame();

  return (
    <div style={{ fontFamily: "monospace", fontSize: 24, color: "white" }}>
      {steps.map((step, i) => {
        const stepStart = startFrame + i * framesPerStep;
        const opacity = interpolate(frame, [stepStart, stepStart + 10], [0, 1], {
          extrapolateLeft: "clamp",
          extrapolateRight: "clamp",
        });
        const isResult = i === steps.length - 1;

        return (
          <span key={i} style={{
            opacity,
            color: isResult ? COLORS.result : COLORS.text,
            fontWeight: isResult ? "bold" : "normal",
          }}>
            {step}{" "}
          </span>
        );
      })}
    </div>
  );
};
```

### 2. 数值飞入动画（ValueFlyIn）

计算结果飞入目标位置：

```tsx
const ValueFlyIn: React.FC<{
  value: number;
  from: [number, number, number];
  to: [number, number, number];
  startFrame: number;
  duration?: number;
}> = ({ value, from, to, startFrame, duration = 30 }) => {
  const frame = useCurrentFrame();
  const { fps } = useVideoConfig();

  const progress = spring({
    frame: frame - startFrame,
    fps,
    config: { damping: 15, stiffness: 80 },
  });

  if (frame < startFrame) return null;

  const position: [number, number, number] = [
    from[0] + (to[0] - from[0]) * progress,
    from[1] + (to[1] - from[1]) * progress,
    from[2] + (to[2] - from[2]) * progress,
  ];

  const scale = 1.5 - 0.5 * progress;

  return (
    <Text position={position} fontSize={0.12 * scale} color={COLORS.result}
          anchorX="center" anchorY="middle">
      {value.toFixed(1)}
    </Text>
  );
};
```

### 3. 区域高亮比较（CompareHighlight）

多个值依次比较，胜出者高亮：

```tsx
const CompareHighlight: React.FC<{
  values: number[];
  positions: [number, number, number][];
  startFrame: number;
  framesPerCompare?: number;
}> = ({ values, positions, startFrame, framesPerCompare = 15 }) => {
  const frame = useCurrentFrame();
  const compareIndex = Math.floor((frame - startFrame) / framesPerCompare);
  const maxIndex = values.indexOf(Math.max(...values));

  return (
    <>
      {values.map((value, i) => {
        const isComparing = i <= compareIndex && i <= maxIndex;
        const isWinner = compareIndex >= values.length - 1 && i === maxIndex;

        return (
          <group key={i} position={positions[i]}>
            <mesh>
              <boxGeometry args={[0.2, 0.2, 0.02]} />
              <meshStandardMaterial
                color={isWinner ? COLORS.result : isComparing ? COLORS.highlight : COLORS.dim}
                emissive={isWinner ? COLORS.result : "#000"}
                emissiveIntensity={isWinner ? 0.5 : 0}
              />
            </mesh>
            <Text position={[0, 0, 0.02]} fontSize={0.08} color="#000">{value}</Text>
          </group>
        );
      })}
    </>
  );
};
```

### 4. 滑动窗口（SlidingWindow）

卷积核/池化窗口滑动：

```tsx
const SlidingWindow: React.FC<{
  gridSize: number;
  windowSize: number;
  stride: number;
  currentStep: number;
}> = ({ gridSize, windowSize, stride, currentStep }) => {
  const outputSize = Math.floor((gridSize - windowSize) / stride) + 1;
  const totalSteps = outputSize * outputSize;
  const step = Math.min(currentStep, totalSteps - 1);

  const row = Math.floor(step / outputSize) * stride;
  const col = (step % outputSize) * stride;

  const pixelSize = 0.12;
  const gap = 0.01;
  const offset = (gridSize / 2 - 0.5) * (pixelSize + gap);
  const windowOffset = (windowSize / 2 - 0.5) * (pixelSize + gap);

  const x = col * (pixelSize + gap) - offset + windowOffset;
  const y = row * (pixelSize + gap) - offset + windowOffset;

  return (
    <mesh position={[x, y, 0.05]}>
      <boxGeometry args={[windowSize * pixelSize + (windowSize - 1) * gap,
                          windowSize * pixelSize + (windowSize - 1) * gap, 0.02]} />
      <meshStandardMaterial
        color={COLORS.negative} transparent opacity={0.6}
        emissive={COLORS.negative} emissiveIntensity={0.3}
      />
    </mesh>
  );
};
```

## 脚本撰写指南（过程动画版）

**关键转变**：脚本需要配合动画节奏，给动画「留白时间」。

**避免信息密集**：
```
"卷积核在图像上滑动，每到一个位置就做点乘运算，得到一个数值。"
（一句话带过，观众还没看清发生了什么）
```

**推荐留白配合**：
```
"让我们看看卷积是怎么计算的。"
（停顿 - 窗口移动到位置）

"卷积核覆盖了这 9 个像素。"
（停顿 - 高亮 3x3 区域）

"我们把每个像素值，和对应的权重相乘..."
（停顿 - 逐步显示乘法）

"然后把所有结果加起来。"
（停顿 - 显示求和过程）

"得到的这个数字，就写入特征图的对应位置。"
（停顿 - 结果飞入）

"第一个位置完成了。接下来，窗口向右滑动一格..."
（加速展示后续步骤）
```

## 时间分配建议

| 详细程度 | 首次完整展示 | 重复加速 | 适用场景 |
|----------|--------------|----------|----------|
| 极详细 | 3-4 秒/步 | 0.5 秒/步 | 核心概念首次出现 |
| 中等 | 2 秒/步 | 0.3 秒/步 | 辅助概念 |
| 快速 | 1 秒/步 | 闪过 | 已解释过的重复 |

**示例：卷积场景时间分配（总时长 ~25 秒）**：
- 0-3s：引入
- 3-12s：第 1 次卷积（完整详细展示）
- 12-18s：第 2-3 次卷积（中等速度）
- 18-23s：剩余位置（快速滑动）
- 23-25s：展示完整特征图

## 踩坑经验

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| 动画太快看不清 | 时间分配不足 | 增加关键步骤的帧数 |
| 解说与动画不同步 | 脚本没有留白 | 重写脚本，加入停顿标记 |
| 信息过载 | 一次展示太多 | 分阶段：先结构，再过程 |
| 重复内容无聊 | 每次都详细展示 | 首次详细 + 后续加速 |
| 数值太小看不见 | 3D 文字渲染问题 | 用 2D HTML overlay |
| 进度显示异常 | progress 变量未 clamp | `Math.min(1, (frame - start) / duration)` |
| 特征图只有色块无数值 | 组件缺少数值显示 | 添加 `values` + `showValues` 参数 |
