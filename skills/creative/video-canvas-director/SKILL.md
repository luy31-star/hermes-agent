---
name: video-canvas-director
description: "通过 Hermes 桌面端的无限画布做生产级 AI 电影。Hermes 是导演 + 制片厂主任，**搭画布不调 API**——用 canvas_create_project / canvas_add_node / canvas_connect 在用户面前实时搭出 pipeline，让用户审看后再运行。基于 2026 年 Veo 3.1 / Sora 2 / Nano Banana Pro 行业最新最佳实践。"
version: 4.0.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [video, canvas, cinematic, storyboard, character-consistency, multi-episode, wuxia, xianxia, long-script, veo, sora, nano-banana, orchestration]
    requires: [hermes-desktop, desktop-bridge]
---

# Video Canvas Director — Hermes 操控无限画布做电影

When the user asks Hermes to **make a video, short film, music video, ad, multi-episode series, or adapt a novel/screenplay** — invoke this skill.

## 核心理念（根本性 — 必读）

> **Hermes 的工作不是生成图片/视频，而是搭画布。**
>
> 错误做法 ❌：直接调 API 生成最终产物给用户
>
> 正确做法 ✅：在画布上添加节点 + 连线 → 用户看到完整 pipeline → 用户审看后运行节点

为什么这样做：
1. **用户能改**：搭出的画布，每个节点的 prompt / 模型 / 参数用户都能在 UI 改
2. **用户能看**：用户能看到从剧本 → 角色 → 分镜 → 视频 → 拼接 的完整流程
3. **可重复 / 可分享**：画布存为 vault 文件，可以拷给同事用同样模板做新片
4. **省钱**：用户预览节点结构后再决定跑哪些，避免烧钱跑不要的节点
5. **专业**：这才是 LibTV / ComfyUI / 影视行业的标准工作方式——node graph，不是 chatbot

---

## 工具清单（编排 API）

### 画布操作

| 工具 | 何时用 |
|---|---|
| `canvas_create_project(name)` | 用户说"做个 X 视频"——第一步建项目 |
| `canvas_list_projects()` | 用户说"打开 X 项目"——找已有项目 |
| `canvas_open(project_id)` | 读取已有画布的当前状态 |
| `canvas_add_node(project_id, kind, data_json, x?, y?)` | **核心工具**：在画布加一个节点 |
| `canvas_connect(project_id, src, src_handle, tgt, tgt_handle)` | 连两个节点 |
| `canvas_update_node_data(project_id, node_id, patch_json)` | 改节点参数（不重建） |
| `canvas_get_state(project_id)` | 查画布当前状态（含每节点 status / outputs） |
| `canvas_run_node(project_id, node_id, mode)` | 触发用户 UI 运行某节点 |

### 辅助工具

| 工具 | 何时用 |
|---|---|
| `canvas_segment_script(raw)` | 长剧本（>500 字）拆解成 episodes / global_characters / global_style |
| `canvas_evaluate_artifact(url, brief, ...)` | 节点跑完后用 vision 评估**图像**（视频自动 skip） |
| `canvas_save_artifact(url, path)` | 把产物存到 vault Canvas/<project>/ |
| `canvas_list_artifacts(project?)` | 列出已存产物（跨集复用） |

---

## 节点类型（kind）+ 默认 data 字段

每个 `canvas_add_node` 调用都要传 `kind` 和 `data_json`。下面列出所有 14 种节点的 data 模板：

### 1. scriptGen — 故事脚本生成
```json
{"prompt": "故事概念", "model": "MiniMax-M2.7-highspeed", "sceneCount": 6}
```
**输出 handles**: `scenes` (分场列表), `rawText`

### 2. characterSheet — 角色立绘（identity anchor）
```json
{"name": "云清歌", "description": "晚唐女剑客，乌黑长发玉簪挽起，米白丝绸交领衫外披深青色斗篷，腰挂细长古剑", "imageModel": "gpt-image-2-all", "viewCount": 3}
```
- `viewCount`: 3（front/side/back，便宜）或 9（多角度，更稳但 3 倍配额）
- `description`: 80-120 字，含朝代/性别/年龄/服饰/武器/气质——**必须详细**
- **输出 handles**: `views` (角度图列表，带 angle 标签)

### 3. storyboard — 单场分镜
```json
{"sceneIndex": null, "style": "cinematic wuxia ink-wash, 35mm anamorphic, 2.39:1 widescreen, cool jade-blue palette, mist atmosphere", "imageModel": "gpt-image-2-all"}
```
- `sceneIndex`: 0-based，对应 scriptGen 的 scene 索引
- `style`: 整片风格句（详见"风格 Preset"）
- **输入 handles**: `scenes` (scriptGen), `characters` (characterSheet), `styleRef` (image)
- **输出 handles**: `boards`

### 4. image — 通用文生图
```json
{"prompt": "...", "imageModel": "gpt-image-2-all", "aspectRatio": "16:9", "count": 1}
```

### 5. inpaint — 局部修改
```json
{"prompt": "...", "maskUrl": "", "imageModel": "flux.1-kontext-pro"}
```

### 6. upscale — 高清化
```json
{"enhancePrompt": "增强细节、电影色调", "imageModel": "flux.1-kontext-pro"}
```

### 7. image2video — 图生视频
```json
{"prompt": "Wuxia swordswoman slowly raises her sword as luminous chi swirls...", "duration": 8, "videoModel": "veo3.1-fast"}
```
- **prompt 必须严格 7 部分公式**（详见下文）
- `duration`: 1-12 秒，veo 3.1 默认 8

### 8. audio2video — 音频生视频（口型同步）
```json
{"videoModel": "kling-avatar-image2video"}
```

### 9. tts — 文本转语音
```json
{"text": "...", "voice": "alloy", "audioModel": "tts-1-hd"}
```

### 10. videoConcat — 视频拼接成片
```json
{"crossfadeSeconds": 0.4, "bgmVolume": 0.35, "bgmUrl": null, "videoOrder": [], "reencode": true}
```

### 11. shotGroup — 多张分镜一致性协调
```json
{"coherencePrompt": "统一冷青色调，宋代气韵", "imageModel": "gpt-image-2-all"}
```

### 12. subtitleRemoval — 视频去字幕
```json
{"region": "auto"}
```

### 13. comicSplit — 漫画拆格
```json
{"imageUrl": "data:image/..."}
```

### 14. preview — 预览（终端节点）
```json
{}
```

---

## 合法连接规则（连错前端会拒）

`canvas_connect(project_id, src_node, src_handle, tgt_node, tgt_handle)` 必须满足：

| 源节点.handle | → | 目标节点.handle |
|---|---|---|
| scriptGen.scenes | → | storyboard.scenes |
| characterSheet.views | → | storyboard.characters |
| characterSheet.views | → | audio2video.character |
| storyboard.boards | → | image2video.image |
| storyboard.boards | → | shotGroup.boards_multi |
| shotGroup.boards | → | image2video.image |
| image.images | → | image2video.image / inpaint.image / upscale.image / storyboard.styleRef / shotGroup.boards_multi / comicSplit.image |
| inpaint.imageUrl | → | image2video.image / upscale.image / storyboard.styleRef / preview.any |
| upscale.imageUrl | → | image2video.image / inpaint.image / storyboard.styleRef / preview.any |
| tts.audioUrl | → | audio2video.audio / preview.any |
| image2video.videoUrl | → | videoConcat.videos_multi / subtitleRemoval.video / preview.any |
| audio2video.videoUrl | → | videoConcat.videos_multi / subtitleRemoval.video / preview.any |
| videoConcat.videoUrl | → | subtitleRemoval.video / preview.any |
| subtitleRemoval.videoUrl | → | videoConcat.videos_multi / preview.any |
| comicSplit.panels | → | image2video.image / shotGroup.boards_multi / preview.any |
| 任何带可视化输出 | → | preview.any（兜底） |

---

## 标准工作流模板

### 模板 A：短概念 短片（< 500 字 / 1 分钟）

用户说："做一个 60 秒武侠短片"

```python
# 1) 建项目
proj = canvas_create_project("武侠短片")
pid = proj.projectId

# 2) 加 scriptGen
script = canvas_add_node(pid, "scriptGen", json.dumps({
    "prompt": "云清歌竹林遇刺客 60 秒短片",
    "model": "MiniMax-M2.7-highspeed",
    "sceneCount": 6,  # 6 场 × 8s 中景 ~ 48s
}))

# 3) 加 characterSheet
hero = canvas_add_node(pid, "characterSheet", json.dumps({
    "name": "云清歌",
    "description": "晚唐女剑客，二十出头，乌黑长发以白玉簪挽起，米白色丝绸交领衫外披深青色斗篷，腰挂细长古剑，眉宇间英气与冷峻并存",
    "imageModel": "gpt-image-2-all",
    "viewCount": 3,
}))

# 4) 6 个 storyboard 节点（每个对应一个 scene）
boards = []
for i in range(6):
    b = canvas_add_node(pid, "storyboard", json.dumps({
        "sceneIndex": i,
        "style": "cinematic wuxia ink-wash, 35mm anamorphic, 2.39:1, cool jade-blue, mist atmosphere",
        "imageModel": "gpt-image-2-all",
    }))
    boards.append(b.nodeId)
    # 连 scriptGen → storyboard
    canvas_connect(pid, script.nodeId, "scenes", b.nodeId, "scenes")
    # 连 characterSheet → storyboard
    canvas_connect(pid, hero.nodeId, "views", b.nodeId, "characters")

# 5) 6 个 image2video 节点
videos = []
for i, b in enumerate(boards):
    v = canvas_add_node(pid, "image2video", json.dumps({
        "prompt": "[占位 — 用户运行前会改]",  # 用户运行前会按 7-part 公式改
        "duration": 8,
        "videoModel": "veo3.1-fast",
    }))
    videos.append(v.nodeId)
    canvas_connect(pid, b, "boards", v.nodeId, "image")

# 6) videoConcat 拼接
concat = canvas_add_node(pid, "videoConcat", json.dumps({
    "crossfadeSeconds": 0.4,
    "bgmVolume": 0.35,
}))
for v in videos:
    canvas_connect(pid, v, "videoUrl", concat.nodeId, "videos_multi")

# 7) preview 节点（终端）
preview = canvas_add_node(pid, "preview", "{}")
canvas_connect(pid, concat.nodeId, "videoUrl", preview.nodeId, "any")

# 8) 告诉用户："画布已搭好（共 16 个节点），请在桌面端打开项目检查后运行"
# 不要自己 canvas_run_node！让用户决定！
```

### 模板 B：中等剧本（500-8000 字 / 3-6 集）

```python
# 1) segment 拆集
seg = canvas_segment_script(raw_script)
# seg → episodes / global_characters / global_style

# 2) 一个项目一集
for ep in seg.episodes:
    proj = canvas_create_project(f"{seg.title}_第{ep.episode_number}集")
    pid = proj.projectId

    # 角色（每集复用 character bible 字符串！）
    char_nodes = {}
    for char in seg.global_characters:
        if char.name in ep.characters:
            cnode = canvas_add_node(pid, "characterSheet", json.dumps({
                "name": char.name,
                "description": char.description,  # 字符串原样！
                "imageModel": "gpt-image-2-all",
                "viewCount": 3,
            }))
            char_nodes[char.name] = cnode.nodeId

    # 每个 beat → storyboard → image2video
    boards = []
    videos = []
    for beat in ep.beats:
        b = canvas_add_node(pid, "storyboard", json.dumps({
            "sceneIndex": ep.beats.index(beat),
            "style": seg.global_style,  # 整剧通用风格句
            "imageModel": "gpt-image-2-all",
        }))
        boards.append(b.nodeId)
        # 连本场出场角色
        for char_name in beat.characters:
            if char_name in char_nodes:
                canvas_connect(pid, char_nodes[char_name], "views", b.nodeId, "characters")

        v = canvas_add_node(pid, "image2video", json.dumps({
            "prompt": format_veo_prompt(beat),  # 7-part 公式，见下
            "duration": beat_duration(beat.beat_type),
            "videoModel": "veo3.1-fast",
        }))
        canvas_connect(pid, b.nodeId, "boards", v.nodeId, "image")
        videos.append(v.nodeId)

    # videoConcat
    concat = canvas_add_node(pid, "videoConcat", json.dumps({"crossfadeSeconds": 0.4}))
    for v in videos:
        canvas_connect(pid, v, "videoUrl", concat.nodeId, "videos_multi")
```

### 模板 C：长剧本（8k-300k 字 / 12+ 集）

跟 B 类似，但 **强烈建议**：
1. 第 1 集**搭完 + 让用户跑通看效果**，再决定继续
2. 跨集复用 `characterSheet`：先 `canvas_list_projects` 找已有项目，复用 character description（同一字符串）
3. 每 3 集让用户审一次

---

## 2026 行业最佳实践（hermes 必须掌握）

### 1. Veo 3.1 / Sora 2 视频 Prompt — 7 部分公式

每个 `image2video` 节点的 `prompt` 字段必须按这 7 部分写，**100-150 词最佳**：

```
1. Subject     [谁/什么] 用 character bible 字符串 + 服饰
2. Action      [一个] 动作 + 节奏副词（slowly / quickly / suddenly）
3. Context     地点 + 时间 + 天气 + 环境
4. Style       视觉风格关键词 5-10 个 + 画幅 + 焦距 + 色调
5. Camera      shot type + movement + angle（电影术语）
6. Audio       对话 / 音效 / 环境声
7. Technical   negative: no subtitles, no watermark, no flicker, no distortion
```

#### Camera 词典（必用电影术语）

| 类型 | 缩写 | 用法 |
|---|---|---|
| Extreme Close-Up | ECU | 眼/手特写 |
| Close-Up | CU | 头部 — 情感峰值 |
| Medium Close-Up | MCU | 胸部以上 |
| Medium Shot | MS | 腰部以上 — 对话 |
| Wide Shot | WS | 全身 + 环境 |
| Extreme Wide | EWS | 微缩人物 |

| 运镜 | 用法 |
|---|---|
| `slow dolly-in` | 推近 — 情绪聚焦 |
| `tracking shot` | 跟拍 |
| `pan / tilt` | 横/上下摇 |
| `crane shot` | 大臂上升 — 史诗感 |
| `orbit` | 环绕 — 主体强调 |
| `handheld` | 手持 — 紧张 |
| `static` | 静止 — 凝重 |

#### 武侠 prompt 示例

```
Wuxia swordswoman Yun Qingge in flowing dark green silk robe with white inner layer, long jet-black hair tied with jade hairpin, slim ancient sword at her waist, calm cold determined expression. Slowly raises her ancient sword as luminous jade-blue chi swirls around the blade. Misty bamboo forest at dawn, cool fog drifting between bamboo stalks, dew-covered ground. Cinematic wuxia ink-wash, 35mm anamorphic, 2.39:1 widescreen, cool jade-blue palette, soft mist atmosphere, photorealistic with ethereal halo. Slow dolly-in tracking her gaze, low angle to emphasize stance. Guzheng plucking with bamboo flute undertone, soft wind through bamboo. No subtitles, no watermark, no on-screen text, stable frame, no flicker.
```

### 2. Storyboard Frame 数量（行业 sweet spot）

| 视频长度 | 帧数 | 平均每帧 | 用途 |
|---|---|---|---|
| 15-30s | 6-8 | 2.5-4s | 抖音/Reels 短 hook |
| 30-45s | **8-14**（甜区） | 2-4s | 短片/产品片 |
| 1-2 分钟 | 15-25 | 3-5s | 品牌片 / 短剧单集 |

### 3. Shot Rhythm 黄金分配（避免视觉疲劳）

| 类型 | 占比 |
|---|---|
| Wide / Establishing | 15-20% |
| Medium | 30-40% |
| Close-Up | 20-25% |
| Extreme Close-Up | 10-15% |
| Transition | 5-10% |

**节奏铁律**：避免 3 个同类型镜头连续。经典 breathing pattern：`Wide → Medium → CU → Medium → Wide`。

### 4. Beat Type 单段时长

| beat_type | duration |
|---|---|
| opening / 环境建立 | 6-8s |
| inciting / 触发事件 | 4-6s |
| rising / 升级冲突 | 6-8s |
| confrontation / 对峙打斗 | 8-10s |
| twist / 反转 | 4-6s |
| reflection / 余韵特写 | 8-12s |
| hook / 下集钩子 | 3-5s |

### 5. 角色一致性 — 三层锁死法

**Layer 1: Character Bible（identity anchor）**
80-120 词字符串，含 朝代/性别/年龄/体型/头发/服饰/武器/气质/标志记号。**字符串后续所有节点 prompt 必须原样粘贴**，连标点都不能改。

**Layer 2: Character Sheet 节点**
`canvas_add_node("characterSheet", ...)` 输出 3 或 9 角度立绘。

**Layer 3: 喂入 Storyboard**
每个 storyboard 节点都 `canvas_connect(characterSheet, "views", storyboard, "characters")`，让分镜模型能拿到角色参考图。

---

## 风格 Preset

### 武侠 Wuxia
```
global_style: "cinematic wuxia ink-wash, 35mm anamorphic, 2.39:1 widescreen, cool jade-blue palette dominated, mist atmosphere, fluid wirework, soft focus on hands and weapons, photorealistic with ethereal halo"
推荐运镜: slow dolly-in / tracking / orbit
推荐 BGM: guzheng + bamboo flute
```

### 玄幻 Xianxia
```
global_style: "xianxia luminous chi effects, golden and azure particle aura, ethereal lighting, cinematic 2.39:1, photorealistic with painterly highlights, slow-motion fabric flow, divine glow"
推荐运镜: rising aerial / slow rotation / parallax push-in
推荐 BGM: ethereal pads + chinese flute
```

### 现代都市 Urban
```
global_style: "contemporary cinematic, 35mm Master Prime, 2.39:1, low-key lighting, practical neons, shallow depth of field, photorealistic, film grain"
推荐运镜: handheld walking / dolly-in / static MS
推荐 BGM: ambient + light electronic
```

### 奇幻冒险 Fantasy
```
global_style: "epic fantasy, anamorphic lens flare, magic hour lighting, 35mm, painterly composition, photorealistic with concept-art quality, dramatic vista"
推荐运镜: crane / orbit / wide establishing
```

### 科幻 Sci-Fi
```
global_style: "sci-fi cinematic, 35mm, 2.39:1, neon-lit cool palette, volumetric fog, practical lighting, photorealistic, retrofuturism, lens flares"
推荐运镜: dolly-in / tracking / low-angle hero shot
```

---

## 当用户说……Hermes 应该

| 用户说 | hermes 做 |
|---|---|
| "做一个武侠短片" | 模板 A，Wuxia preset，10 节点 |
| "做一个一分钟玄幻打斗" | 模板 A，Xianxia preset，6 storyboard + 6 image2video + 1 concat |
| "把这 5 万字小说做成视频剧" | 先 `canvas_segment_script`，给用户看 episodes 列表，**等审批**，然后模板 B 每集一个项目 |
| "用我之前那个角色" | `canvas_list_projects` 找已有项目 → `canvas_open` 取出 character description → 新项目里用同一字符串 |
| "整组分镜风格不统一" | 在画布加一个 shotGroup 节点，连入所有 storyboard，用户运行后看协调效果 |
| "视频里有字幕想去掉" | 加 subtitleRemoval 节点 |
| "我有 6 格漫画想做视频" | 加 comicSplit 节点 → shotGroup → image2video |
| "改一下这场分镜的 style" | `canvas_update_node_data(pid, board_node, '{"style": "新风格句"}')` 然后让用户重跑 |
| "建好画布了，开始跑" | `canvas_run_node(pid, root_node, "full")` 触发 UI 跑全图 |

---

## 操作铁律（违反就重来）

1. **绝对不要直接调 API 生成图/视频**——只通过 add_node + connect 在画布上搭结构。
2. **建完画布要立即告诉用户**画布在哪、有几个节点、连成什么形状，让用户审看。
3. **不要自动 run_node**——让用户决定何时跑。除非用户明确说"建好就跑"。
4. **character description 字符串原样复用**——同一角色多个项目都用同一段文字，连标点都不变。
5. **prompt 必须按 7 部分公式**——image2video 的 prompt 缺哪部分就补哪部分。
6. **视觉自评只对图像有效**——视频质量交给用户人工判断。
7. **5 个 close-up 连续是大忌**——添加 storyboard 节点时按 shot rhythm 交替。
8. **每个高费用决策（>50 元）先告知用户**。

---

## Quality Checkpoint（hermes 给画布前自检）

- [ ] 项目创建成功，有 projectId
- [ ] characterSheet 节点的 description 是详细的 character bible 字符串
- [ ] storyboard 数量在 8-14 之间（30-45s 短片）
- [ ] shot rhythm 满足 W→M→CU→M→W 节奏，没有 3 个连续同类型
- [ ] 每个 storyboard 都连了 characterSheet（角色一致性）
- [ ] image2video 的 prompt 按 7 部分公式写
- [ ] 所有边都符合 edgeValidation 规则
- [ ] 终端有 preview 节点（用户能在 UI 看最终成片）

---

## 输出位置

```
<vault>/Canvas/<project_id>/
├── main.vcanvas.json     ← 画布快照（hermes 写的就是这个）
├── characters/           ← 用户手动 save_artifact 的角色立绘
├── boards/               ← 分镜
├── segments/             ← 视频段
└── final.mp4             ← 成片
```

---

## 参考 / 行业证据

- [Veo 3 7-Part Prompt Formula — frameo.ai](https://frameo.ai/blog/google-veo-3-prompt-guide-best-practices/)
- [Nano Banana Pro Storyboard — apiyi.com](https://help.apiyi.com/en/nano-banana-pro-ai-video-storyboard-character-consistency-guide-en.html)
- [Sora 2 Multi-Shot Consistency — aifreeapi.com](https://www.aifreeapi.com/en/posts/sora-2-multi-shot-prompts)
- [Veo 3.1 Multi-Prompt — skywork.ai](https://skywork.ai/blog/multi-prompt-multi-shot-consistency-veo-3-1-best-practices/)
- [LibTV 团队版 — toolin.ai](https://toolin.ai/blog/libtv-team-edition-ai-video-studio)（搭画布的标准工作流）

Content was synthesized from 2026 industry research; rephrased for compliance.

---

## 给 hermes 的最后忠告

不要怕慢——搭画布只要 1-2 分钟，但用户能看到、能改、能复用。
不要直接调 API——你不是 chatbot，你是导演。
不要自己拍板跑——让用户决定何时点运行。
不要忘了 character bible 字符串——一个标点都不能改。
不要凑分镜数——8-14 帧是行业 sweet spot，少了没节奏多了碎。
不要省 7 部分公式的任何一部分——Audio 和 Technical 是 Veo 3.1 最大区别。

你是导演，画布是你的剧组。
