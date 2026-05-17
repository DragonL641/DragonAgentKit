# AI 语音解说集成

为视频添加 AI 语音解说，实现音视频同步。

## 方案对比

| 方案 | 优点 | 缺点 | 硬件要求 | 推荐度 |
|------|------|------|----------|--------|
| **MiniMax TTS** | 云端克隆、速度极快（<3秒）、音质优秀 | 按字符计费 | 无 | 首选 |
| **Edge TTS** | 零配置、免费 | 固定音色、无法自定义 | 无 | 备选 |

### 选择流程

```
1. 首选 MiniMax TTS → 检测 API Key 是否配置 → 测试调用是否正常
2. MiniMax 不可用时 → 退回 Edge TTS（使用预设音色 zh-CN-YunyangNeural）
```

---

## MiniMax TTS（推荐）

### 配置

1. 注册 https://www.minimax.io （国际版）或 https://platform.minimaxi.com （国内版）
2. 获取 API Key
3. 在 MiniMax Audio 上传音频克隆音色，获取 voice_id

### API 差异

| 版本 | API 域名 | 说明 |
|------|----------|------|
| 国际版 | `api.minimax.io` | 推荐，稳定 |
| 国内版 | `api.minimaxi.com` | 需国内账号 |

**常见错误**：`api.minimax.chat` 是**错误的域名**，会返回 "invalid api key"。

### 价格参考

| 模型 | 价格 |
|------|------|
| speech-02-hd | ¥0.1/千字符 |
| speech-02-turbo | ¥0.05/千字符 |

### 踩坑经验

| 问题 | 原因 | 解决方案 |
|------|------|----------|
| `invalid api key` | 使用了错误的 API 域名 | 国际版用 `api.minimax.io`，国内版用 `api.minimaxi.com` |
| config.ts 语法错误 `Syntax error "n"` | Python 脚本在 f-string 中用 `",\\n".join()` 产生了字面量 `\n` 而非真正换行 | 见下方「Python 生成 TypeScript 注意事项」 |

### Python 生成 TypeScript 注意事项

```python
# 错误：在 f-string 中使用 \n 会产生字面量字符
content = f'export const SCENES = [{",\\n".join(items)}];'

# 正确：先在外面拼接，再放入模板
scenes_content = ",\n".join(items)
content = f'''export const SCENES = [
{scenes_content}
];'''
```

---

## Edge TTS（备选）

### 安装

```bash
pip install edge-tts
```

### 推荐语音

| 语音 ID | 名称 | 风格 |
|---------|------|------|
| zh-CN-YunyangNeural | 云扬 | 专业播音腔（推荐） |
| zh-CN-XiaoxiaoNeural | 晓晓 | 温暖自然 |
| zh-CN-YunxiNeural | 云希 | 阳光少年 |

---

## Remotion 音频同步模式

```tsx
import { Audio, Sequence, staticFile } from "remotion";

const audioConfig = [
  { id: "01-intro", file: "01-intro.mp3", frames: 450 },
  { id: "02-main", file: "02-main.mp3", frames: 600 },
];

const sceneStarts = audioConfig.reduce((acc, _, i) => {
  if (i === 0) return [0];
  return [...acc, acc[i - 1] + audioConfig[i - 1].frames];
}, [] as number[]);

{audioConfig.map((scene, i) => (
  <Sequence key={scene.id} from={sceneStarts[i]} durationInFrames={scene.frames}>
    <SceneComponent />
    <Audio src={staticFile(scene.file)} />
  </Sequence>
))}
```
