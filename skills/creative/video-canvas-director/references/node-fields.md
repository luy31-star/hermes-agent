## 🔑 节点 data 字段速查表（hermes 必须按字段填，不能全塞 prompt）

### scriptGen（剧本生成）
```json
{
  "kind": "scriptGen",
  "label": "剧本：XXX",
  "prompt": "用户的故事概念 + 时长 + 风格",
  "model": "MiniMax-M2.7-highspeed",
  "sceneCount": 6,
  "styleHint": "古风武侠 / 玄幻渡劫 / 反转剧情"
}
```

### characterSheet（角色立绘）
```json
{
  "kind": "characterSheet",
  "label": "角色：白衣剑仙",
  "name": "白衣少年剑仙",
  "description": "<≥ 800 字符工业级 prompt：face/hair/outfit/signature/style/negative 全锁>",
  "imageModel": "gpt-image-2-all"
}
```
**说明**：`description` 字段就是工业级 prompt 整体。该节点产出 3/9 视图。

### storyboard（整片风格锚）
**v6 新角色**：1 张总视觉，作为 style ref 喂给所有下游 image 节点。**不**对应单镜头。
```json
{
  "kind": "storyboard",
  "label": "整片风格锚 / Style Anchor",
  "sceneIndex": null,
  "style": "cinematic wuxia ink-wash painting, 35mm anamorphic, teal-amber color grade, mist atmosphere, golden rim light, 2.39:1 widescreen",
  "imageModel": "gpt-image-2-all"
}
```

### image（每镜头独立分镜图 — **B 工作流核心**）
```json
{
  "kind": "image",
  "label": "镜头 1：开场远景（0-3s）",
  "prompt": "<≥ 500 字符工业级镜头 prompt，含 character lock + scene + composition + mood + negative>",
  "imageModel": "gpt-image-2-all",
  "aspectRatio": "16:9",
  "count": 1,
  
  "// 结构化字段 — 这些不要塞 prompt，分开填 //": "",
  "shotSize": "wide shot",
  "cameraAngle": "low angle",
  "cameraMovement": "static",
  "lighting": "golden hour, warm directional light",
  "colorTone": "teal-amber, cool jade-blue shadows",
  "lens": "24mm wide-angle",
  "styleRef": "cinematic wuxia ink-wash"
}
```

**hermes 要做的**：从 promptLibrary 选项里挑 ID（见后面"镜头字段词典"），然后把对应的 `zh` 中文短语填进结构化字段。`prompt` 字段写**剧情/构图/角色**，**不要重复**镜头/光/焦距（这些靠结构化字段，前端会自动拼接）。

### image2video（每镜头视频）
```json
{
  "kind": "image2video",
  "label": "视频镜头 1：开场（0-3s）",
  "prompt": "<≥ 800 字符工业级 prompt，含 keyframe ref + character lock + 时间戳分段 + audio + negative>",
  "videoModel": "veo-3.1",
  "duration": 3,
  "aspectRatio": "16:9"
}
```

**v7 新增**：image2video 节点现在有**两个图片输入**：
- `image`（首帧，必填）
- `tailFrame`（末帧，**强烈推荐**填，可大幅减少角色漂移和运动跳变）

**双关键帧策略**：每个镜头至少做两张分镜图（开始姿势 / 结束姿势），都连进同一个 image2video 节点。模型在两端之间插值，运动稳定 10×。Sora 2 / Veo 3.1 / Kling 2.6 / Pika 2 都支持。

### videoConcat（成片）
```json
{
  "kind": "videoConcat",
  "label": "成片",
  "videoOrder": [],
  "crossfadeSeconds": 0.5,
  "reencode": true,
  "bgmVolume": 0.35
}
```

### 其他节点（按需用）
- `characterSheet` 默认 3 视图。需要 9 角度：`viewCount: 9`
- `inpaint` — 局部重绘（image 跑出来不满意时，挂在 image 后面修脸/手）
- `upscale` — 4K 提升（连在 image 之后做最终高清）
- `audio2video` — 数字人对白
- `tts` — 文字配音
- `shotGroup` — 多镜头一致性 pass（多张分镜风格不连贯时，挂在 image 后面统一调）
- `subtitleRemoval` — 视频去字幕
- `comicSplit` — 漫画拆分镜
- `preview` — 终端节点
- `audio2video` / `tts` — 配音工作流

---

