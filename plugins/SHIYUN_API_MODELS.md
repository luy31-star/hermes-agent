# 诗云 API 支持的模型列表

## 📊 模型统计

- **图片生成**: 22 个模型
- **视频生成**: 27 个模型
- **总计**: 49 个模型

---

## 🎨 图片生成模型 (22个)

### 诗云托管模型 (6个)
通过诗云 API 直接访问，按积分计费

| 模型 ID | 显示名称 | 速度 | 特点 |
|---------|----------|------|------|
| `gpt-image-2` | GPT Image 2 | 快速 | 4K, 多模态, 修复 |
| `gpt-image-1` | GPT Image 1 | 中等 | 经典图片模型 |
| `doubao-seedream-3-0-t2i-250415` | Seedream 3.0 | 快速 | 字节跳动 Doubao |
| `doubao-seededit-3-0-i2i-250628` | Seededit 3.0 | 快速 | 图片编辑 |
| `grok-imagine-image` | Grok Imagine Image | 快速 | 2K, 11+宽高比 |
| `gemini-3.1-flash-image-preview` | Nano Banana 2 | 快速 | 文本生成图片 |

### OpenAI 官方 API (6个)

| 模型 ID | 显示名称 | 速度 | 价格 |
|---------|----------|------|------|
| `openai/gpt-image-2` | OpenAI GPT Image 2 | 快速 | $0.04/image |
| `openai/gpt-image-1.5` | OpenAI GPT Image 1.5 | 快速 | $0.02/image |
| `openai/gpt-image-1` | OpenAI GPT Image 1 | 中等 | $0.03/image |
| `openai/gpt-image-1-mini` | OpenAI GPT Image 1 Mini | 快速 | $0.01/image |
| `openai/dall-e-3` | DALL-E 3 | 中等 | $0.04/image |
| `openai/dall-e-2` | DALL-E 2 | 快速 | $0.02/image |

### FLUX 系列 (4个)

| 模型 ID | 显示名称 | 速度 | 价格 |
|---------|----------|------|------|
| `black-forest-labs/FLUX-1.1-pro` | FLUX 1.1 Pro | 中等 | $0.04/image |
| `flux-pro` | FLUX Pro | 中等 | $0.05/image |
| `flux-dev` | FLUX Dev | 快速 | $0.025/image |
| `flux-schnell` | FLUX Schnell | 极快 | $0.003/image |

### Google 系列 (2个)

| 模型 ID | 显示名称 | 速度 | 价格 |
|---------|----------|------|------|
| `imagen-4` | Imagen 4 | 中等 | $0.04/image |
| `imagen-3` | Imagen 3 | 中等 | $0.03/image |

### Stable Diffusion (2个)

| 模型 ID | 显示名称 | 速度 | 价格 |
|---------|----------|------|------|
| `sd-3.5` | Stable Diffusion 3.5 | 快速 | $0.01/image |
| `sdxl` | Stable Diffusion XL | 快速 | $0.01/image |

### 其他 (2个)

| 模型 ID | 显示名称 | 特点 |
|---------|----------|------|
| `midjourney-v7` | Midjourney v7 | 艺术风格，高质量 |
| `ideogram-v2` | Ideogram v2 | 文字渲染专家 |

---

## 🎬 视频生成模型 (27个)

### Sora 系列 (2个)
OpenAI 的视频生成模型

| 模型 ID | 显示名称 | 速度 | 模态 |
|---------|----------|------|------|
| `sora-2` | Sora 2 | 中等 | 文本 |
| `sora-2-pro` | Sora 2 Pro | 慢速 | 文本 |

### Kling 系列 (7个)
快手 Kling 视频生成

| 模型 ID | 显示名称 | 速度 | 模态 |
|---------|----------|------|------|
| `kling-video` | Kling Text to Video | 中等 | 文本 |
| `kling-image2video` | Kling Image to Video | 中等 | 图片 |
| `kling-multi-image2video` | Kling Multi Image to Video | 中等 | 图片 |
| `kling-omni-video` | Kling Omni Video | 中等 | 文本+图片 |
| `kling-2.0` | Kling 2.0 | 中等 | 文本+图片 |
| `kling-1.6` | Kling 1.6 | 中等 | 文本+图片 |
| `kling-1.5` | Kling 1.5 | 中等 | 文本+图片 |

### Seedance 系列 (6个)
字节跳动 Doubao Seedance

| 模型 ID | 显示名称 | 速度 | 模态 | 音频 |
|---------|----------|------|------|------|
| `doubao-seedance-1-0-pro-fast-251015` | Doubao Seedance Pro | 快速 | 文本+图片 | ❌ |
| `doubao-seedance-2-0-260128` | Seedance 2.0 | 中等 | 文本+图片 | ✅ |
| `doubao-seedance-2-0-fast-260128` | Seedance 2.0 Fast | 快速 | 文本+图片 | ✅ |
| `doubao-seedance-1-0-pro-250528` | Seedance 1.0 Pro | 中等 | 文本+图片 | ❌ |
| `doubao-seedance-1-0-lite-i2v-250428` | Seedance 1.0 Lite I2V | 快速 | 图片 | ❌ |
| `doubao-seedance-1-0-lite-t2v-250428` | Seedance 1.0 Lite T2V | 快速 | 文本 | ❌ |

### Google Veo 系列 (4个)

| 模型 ID | 显示名称 | 速度 | 模态 | 音频 |
|---------|----------|------|------|------|
| `veo3.1-fast` | Veo 3.1 Fast | 快速 | 文本 | ❌ |
| `veo3.1` | Veo 3.1 | 中等 | 文本 | ❌ |
| `veo-3` | Veo 3 | 中等 | 文本 | ✅ |
| `veo-2` | Veo 2 | 中等 | 文本 | ❌ |

### xAI Grok (1个)

| 模型 ID | 显示名称 | 速度 | 模态 | 音频 |
|---------|----------|------|------|------|
| `grok-imagine-video` | Grok Imagine Video | 中等 | 文本+图片 | ✅ |

### 其他诗云托管 (4个)

| 模型 ID | 显示名称 | 速度 | 模态 |
|---------|----------|------|------|
| `MiniMax-Hailuo-02` | Hailuo 02 | 中等 | 文本+图片 |
| `wan2.6-i2v` | Wan 2.6 I2V | 快速 | 图片 |
| `vidu2.0` | Vidu 2.0 | 中等 | 文本 |
| `minimax-video-01` | MiniMax Video 01 | 中等 | 文本+图片 |

### 路由模型 (3个)
通过其他 API 路由

| 模型 ID | 显示名称 | 价格 |
|---------|----------|------|
| `xAI/grok-imagine-video` | xAI Grok Imagine Video | $0.10/s |
| `bytedance/seedance-1.5-pro` | Seedance 1.5 Pro | $0.08/s |
| `google/veo-3.1-lite` | Veo 3.1 Lite | $0.05/s |

---

## 📈 能力统计

### 视频生成模态支持

| 模态类型 | 模型数量 |
|----------|----------|
| 仅文本 (T2V) | 11 个 |
| 仅图片 (I2V) | 4 个 |
| 文本+图片 | 12 个 |
| **总计** | **27 个** |

### 音频支持

| 功能 | 模型数量 |
|------|----------|
| 支持原生音频 | 5 个 |
| 不支持音频 | 22 个 |

支持音频的模型：
- `doubao-seedance-2-0-260128`
- `doubao-seedance-2-0-fast-260128`
- `grok-imagine-video`
- `veo-3`
- `xAI/grok-imagine-video`

---

## 🚀 使用示例

### 图片生成

```python
# 使用诗云托管的 GPT Image 2
hermes> Generate an image of a cat wearing a hat
# 自动调用: image_generate(prompt="...", model="gpt-image-2")

# 使用 FLUX 1.1 Pro
hermes> Generate a photorealistic portrait using FLUX
# 调用: image_generate(prompt="...", model="black-forest-labs/FLUX-1.1-pro")
```

### 视频生成

```python
# 使用 Sora 2 生成视频
hermes> Create a 5-second video of ocean waves
# 调用: video_generate(prompt="...", model="sora-2", duration=5)

# 使用 Kling 将图片转视频
hermes> Animate this image with gentle motion
# 调用: video_generate(prompt="...", model="kling-image2video", image_url="...")

# 使用 Seedance 2.0 生成带音频的视频
hermes> Generate a video with background music
# 调用: video_generate(prompt="...", model="doubao-seedance-2-0-260128", audio=True)
```

---

## ⚙️ 配置

### 环境变量

```bash
# 诗云 API 密钥
export IMAGEROUTER_API_KEY="your-shiyun-api-key"

# 可选：自定义 API 端点
export IMAGEROUTER_BASE_URL="https://shiyunapi.com/v1"
```

### Hermes 配置

```yaml
# ~/.hermes/config.yaml

image_gen:
  provider: imagerouter
  model: gpt-image-2  # 默认图片模型

video_gen:
  provider: imagerouter
  model: doubao-seedance-1-0-pro-fast-251015  # 默认视频模型
```

---

## 📝 模型选择建议

### 图片生成

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 通用高质量 | `gpt-image-2` | 4K分辨率，多模态支持 |
| 快速原型 | `flux-schnell` | 极快速度，低成本 |
| 照片级真实 | `flux-pro` | 最佳真实感 |
| 文字渲染 | `ideogram-v2` | 专门优化文字 |
| 艺术风格 | `midjourney-v7` | 艺术化效果 |

### 视频生成

| 场景 | 推荐模型 | 原因 |
|------|----------|------|
| 高质量文本生成 | `sora-2-pro` | 最高质量 |
| 快速生成 | `doubao-seedance-1-0-pro-fast-251015` | 速度快 |
| 图片转视频 | `kling-image2video` | 专门优化 I2V |
| 需要音频 | `doubao-seedance-2-0-260128` | 原生音频支持 |
| 多模态 | `kling-omni-video` | 支持多种输入 |

---

## 🔗 相关链接

- [诗云 API 文档](https://shiyunapi.apifox.cn/)
- [ImageRouter 插件代码](./image_gen/imagerouter/)
- [VideoRouter 插件代码](./video_gen/imagerouter/)
- [使用指南](./IMAGEROUTER_USAGE.md)

---

**最后更新**: 2026-05-20  
**插件版本**: 1.0.0  
**支持的模型总数**: 49 个 (图片22 + 视频27)
