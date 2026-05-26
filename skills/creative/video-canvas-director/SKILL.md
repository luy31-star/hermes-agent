---
name: video-canvas-director
description: "通过 Hermes 桌面端的无限画布做生产级 AI 电影。Hermes 是导演 + 制片厂主任，**搭画布不调 API**——按工作流 B（scriptGen → storyboard 风格锚 → 每镜头独立 image × 2 [首帧 + 末帧] → image2video → videoConcat）搭出可视化 pipeline，让用户看到每个镜头的独立分镜节点（占位 idle，运行后才出图）。基于 2026 年 Veo 3.1 / Sora 2 / Seedance 2.0 / Nano Banana Pro / Kling 2.6 工业实战。v7.2 强制 Phase Gates：剧本拆解 → 角色 Bible → 镜头规划 → 用户确认后才搭画布；时长按剧情节奏决定，不是模型上限填满。"
version: 7.2.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [video, canvas, cinematic, storyboard, character-consistency, dual-keyframe, audio-design, self-correcting, multi-genre, wuxia, xianxia, urban, cyberpunk, scifi, fantasy, mv, ad, anime, veo, sora, seedance, nano-banana, kling, orchestration, prompt-engineering]
    requires: [hermes-desktop, desktop-bridge]
---

# Video Canvas Director — 生产级 AI 视频画布编排（v7.2）

When the user asks Hermes to **make a video, short film, music video, ad, multi-episode series, or adapt a novel/screenplay** — invoke this skill.

> **v7.2 关键升级（2026 工业流）**
> 1. **强制 Phase Gates**：搭画布前必须先在 chat 输出 Phase 1 剧本拆解 + Phase 2 角色 Bible + Phase 3 镜头规划，等用户确认才能调 `canvas_*` 工具
> 2. **时长由剧情决定**：高潮镜头敢用 12s + 贵模型，过场镜头用便宜短模型，不是模型上限平均切
> 3. **多模型混用**：60s 成片可同时用 veo3.1-fast / sora-2-pro / seedance / vidu-q3，按镜头需求选
> 4. **双关键帧锁定**：每镜头首帧 + 末帧 image，都连进同一 image2video，角色绝不漂移

---

## ⛔ HARD GATE — 不读完这一节就不要建项目

**`canvas_create_project` 已加了运行时校验**：缺少 `story_beats / character_bible / shot_breakdown / user_confirmed=True` 任意一项就会**直接返回 phase_gate_failed**，画布不会建。

所以工作流是固定的：

```
USER: 给你一段剧本，搭画布
HERMES → chat 输出 Phase 1（剧本拆解，≥120 字）
HERMES → chat 输出 Phase 2（角色 Bible，每角色 ≥200 字）
HERMES → chat 输出 Phase 3（镜头规划表，≥200 字含每镜头时长 + 字段）
HERMES → 问「以上确认无误我开始搭画布？」
USER  → 确认（或微调，循环回到对应 phase）
HERMES → canvas_create_project(
           name="...",
           story_beats="<Phase 1 全文>",
           character_bible="<Phase 2 全文>",
           shot_breakdown="<Phase 3 全文>",
           user_confirmed=True
         )
HERMES → 后续 canvas_add_node / canvas_connect ...
```

**禁止**：
- 跳过 Phase 1/2/3 直接调 `canvas_create_project` → 工具拒绝
- 给 Phase 1/2/3 一个空字符串或几十字应付 → 工具拒绝（≥120/200/200 字硬阈值）
- 没等用户回复就 `user_confirmed=True` → 流程作弊；只能在用户明确说"确认 / 搭吧 / 继续 / yes / OK"等之后才设 True

**Phase 1-3 的输出格式 + 内容深度**详见下方 §强制 Phase Gates 章节，必须按那个模板出。

---

## 🔥 核心理念（必读，违反就是故障）

> **Hermes 的工作 = 搭画布 + 写工业级 prompt + 填结构化字段。不直接出图出视频。**

错误做法 ❌
1. 直接调 API 给用户出图出视频
2. 节点 prompt 一句话："白衣染尘、隐忍坚毅"——这是描述，不是 prompt
3. 一个 storyboard 节点出 3 张图就直接接 image2video（B 工作流要求每镜头一个独立 image 节点）
4. 把镜头/焦距/光线/比例全塞 prompt 字符串里，结构化字段（shotSize / cameraMovement / lighting / colorTone / aspectRatio）留空
5. 角色不锁脸、不锁服装、不写 negative prompt
6. 自己 canvas_run_node 跑节点

正确做法 ✅
1. **建项目** → **加角色立绘** → **加 scriptGen** → **加 storyboard 当风格锚** → **每镜头加独立 image 节点** → **每镜头加 image2video** → **拼接**
2. **每个节点的 prompt 都是工业级**（≥ 600/800/1000 字符，按节点类型）
3. **结构化字段独立填**：shotSize、cameraMovement、lighting、colorTone、aspectRatio 必须分别传，不要全堆 prompt 里
4. **角色锁死**：每个角色一个 characterSheet，所有下游节点 connect 到 .views
5. **negative prompt 必备**：每个图/视频节点都写
6. **占位策略**：所有 image / image2video 节点 status='idle'，**不要自己 run**，告诉用户审看后再点 ▶

为什么这样：
- 用户能改每张分镜的 prompt / 模型 / 镜头独立参数
- 用户能看到完整 pipeline，按需跑
- 单镜头出问题只重跑这一张，不动整组
- 这是 LibTV / Sora 故事板 / Runway Gen-3 / 影视行业的标准 node graph 工作流

---

## 工具清单（编排 API）

### 画布操作
| 工具 | 何时用 |
|---|---|
| `canvas_create_project(name)` | 第一步建项目 |
| `canvas_list_projects()` | 用户说"打开 X 项目" |
| `canvas_open(project_id)` | 读取已有画布 |
| `canvas_add_node(project_id, kind, data_json, x?, y?)` | **核心**：在画布加节点 |
| `canvas_connect(project_id, src, src_handle, tgt, tgt_handle)` | 连两个节点 |
| `canvas_update_node_data(project_id, node_id, patch_json)` | 改节点参数 |
| `canvas_get_state(project_id)` | 查画布当前状态 |
| `canvas_run_node(project_id, node_id, mode)` | 触发用户 UI 运行（**不要自己用**） |

### 画布 meta 设置（v7 新增）
| 工具 | 何时用 |
|---|---|
| `canvas_get_meta(project_id)` | 读当前画布开关（自检 / 影视级模式）|
| `canvas_set_self_check(project_id, enabled, max_retries, pass_threshold)` | 启停 vision 自检闭环 |
| `canvas_set_cinematic_pro_mode(project_id, enabled)` | 启停影视级深度模式 |
| `canvas_list_video_models()` | **必读**：拿所有视频模型的真实能力（duration / 首尾帧 / 音频 / 4K）|

### 辅助工具
| 工具 | 何时用 |
|---|---|
| `canvas_segment_script(raw)` | 长剧本（>500 字）拆解 |
| `canvas_evaluate_artifact(...)` | 自检（**仅当 selfCheckEnabled=true 时主动调**）|
| `canvas_save_artifact(...)` | 落盘到 vault |
| `canvas_list_artifacts(project?)` | 列出已存产物 |

---

## 🏗️ 工作流 B 架构图（必须遵循）

```
┌────────────────┐
│ characterSheet │  (角色 1，9 视图，identity anchor)
└────┬───────────┘
     │ views
     │
┌────▼───────┐         ┌─────────┐
│ scriptGen  │────────►│storyboard│  (整片风格锚，1 张总视觉，定 style/lighting)
└────┬───────┘ scenes  └────┬────┘
     │                      │ boards (style ref)
     │                      │
     │   ┌──────────────────┼─────────────────────┐
     │   │                  │                     │
     ▼   ▼                  ▼                     ▼
   ┌──────┐              ┌──────┐              ┌──────┐
   │image │  镜头1       │image │  镜头2        │image │  镜头N
   │ 全景 │              │ 中景 │              │ 特写 │
   │dolly │              │static│              │push  │
   └──┬───┘              └──┬───┘              └──┬───┘
      │ images              │                     │
      ▼                     ▼                     ▼
  ┌────────┐            ┌────────┐            ┌────────┐
  │image2  │ 8s         │image2  │ 6s          │image2  │ 4s
  │video   │            │video   │            │video   │
  └───┬────┘            └───┬────┘            └───┬────┘
      │                     │                     │
      └─────────────────────┼─────────────────────┘
                            │ videoUrl × N
                            ▼
                    ┌───────────────┐
                    │ videoConcat   │  → 成片
                    └───────────────┘
```

**关键**：
- **storyboard 节点只有 1 个**：定整片视觉锚（色调、镜头规格、灯光基调），不出最终分镜图
- **image 节点 N 个**：每个镜头一个，独立填 prompt + 镜头字段
- **image2video 节点 N 个**：和 image 节点一一对应
- **角色 connect 到每一个 image 和 image2video**：identity 跨节点锁死

---

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

## 📚 镜头字段词典（结构化字段必备词，从 promptLibrary 来）

hermes 填结构化字段时，**只从下面这些词里选**，模型才认。

### shotSize（景别）
| ID | 中文 | 英文 |
|---|---|---|
| extreme-wide | 超远景 | extreme wide shot |
| wide | 全景 | wide shot |
| medium-wide | 中远景 | medium wide shot |
| medium | 中景 | medium shot |
| close-up | 特写 | close-up |
| extreme-close-up | 大特写 | extreme close-up |
| over-shoulder | 过肩 | over-the-shoulder |
| pov | 主观 | POV |
| two-shot | 双人 | two-shot |

### cameraAngle（角度）
| ID | 中文 | 英文 |
|---|---|---|
| eye-level | 平视 | eye-level |
| low | 低角度仰拍 | low angle |
| high | 高角度俯拍 | high angle |
| birds-eye | 鸟瞰 | bird's-eye view |
| worms-eye | 蚁视 | worm's-eye view |
| dutch | 荷兰角倾斜 | Dutch angle |

### cameraMovement（运镜）
| ID | 中文 | 英文 |
|---|---|---|
| static | 固定 | static |
| pan | 横摇 | slow pan |
| tilt | 纵摇 | slow tilt |
| dolly-in | 推镜 | slow dolly in |
| dolly-out | 拉镜 | slow dolly out |
| tracking | 跟拍 | tracking shot |
| crane-up | 升镜 | crane up |
| crane-down | 降镜 | crane down |
| orbit | 环绕 | slow orbital |
| handheld | 手持 | handheld |
| zoom-in | 变焦推 | zoom in |
| whip-pan | 甩镜 | whip pan |

### lighting（光线）
| ID | 中文 | 英文 |
|---|---|---|
| natural | 自然光 | soft natural light |
| golden-hour | 黄金时刻暖光 | golden hour, warm directional |
| blue-hour | 蓝调时刻冷调 | blue hour, cool ambient |
| rembrandt | 伦勃朗光 | Rembrandt lighting |
| low-key | 低调暗光强对比 | low-key, high contrast |
| high-key | 高调亮光柔阴 | high-key, soft shadows |
| neon | 霓虹冷暖混合 | neon mixed cool-warm |
| backlit | 强逆光剪影 | strong backlight, silhouette |
| moonlight | 蓝调月光 | cold moonlight |
| candle | 暖色烛光 | warm candle light |

### lens（镜头规格）
| ID | 中文 | 英文 |
|---|---|---|
| 14mm | 14mm 超广 | 14mm ultra-wide |
| 24mm | 24mm 广角 | 24mm wide |
| 35mm | 35mm 标准 | 35mm prime |
| 50mm | 50mm 标头 | 50mm prime |
| 85mm | 85mm 人像浅景深 | 85mm portrait, shallow DoF |
| 100mm-macro | 100mm 微距 | 100mm macro |
| 135mm | 135mm 长焦 | 135mm telephoto |

### styleRef / 风格 preset
| ID | 中文 | 英文 |
|---|---|---|
| cinematic | 电影感写实 | cinematic, photorealistic |
| anamorphic | 宽银幕变形 | anamorphic widescreen 2.39:1 |
| documentary | 纪录片 | documentary |
| noir | 黑色电影黑白 | film noir, high contrast B&W |
| wong-kar-wai | 王家卫色调 | Wong Kar-wai inspired |
| wes-anderson | 韦斯安德森对称 | Wes Anderson symmetrical |
| studio-ghibli | 吉卜力 2D | Studio Ghibli 2D |
| pixar-3d | 皮克斯 3D | Pixar 3D |
| anime | 日系动漫赛璐璐 | Japanese cel-shaded anime |
| cyberpunk | 赛博朋克霓虹 | cyberpunk neon-lit future |
| claymation | 黏土定格 | claymation stop-motion |

### aspectRatio（比例）
- `16:9` — 横屏标准（默认）
- `9:16` — 竖屏（短视频/抖音/视频号）
- `1:1` — 方形（社媒）
- `2.39:1` — 电影宽银幕
- `21:9` — 超宽银幕

---

## 🎬 八大题材 prompt 模板库（每类含完整七要素 + 范例）

### 1. 古风武侠 Wuxia
```
风格锚（storyboard.style）:
"cinematic wuxia ink-wash painting style, 35mm anamorphic widescreen 2.39:1,
teal-amber color grade with cool jade-blue shadows, subtle film grain,
mist atmosphere, golden rim light through bamboo, traditional Chinese aesthetics,
Hou Hsiao-hsien / Wong Kar-wai inspired cinematography"

典型 image prompt 范例（一个镜头）:
"@character1 (白衣少年剑仙) — keep SAME face, SAME ivory white silk robe with
silver embroidery, SAME long black hair tied with white ribbon, SAME cracked
sword scabbard.

He kneels on a wind-swept cliff edge above a sea of clouds, sword stuck into
stone beside him, faint golden tribulation lightning crackling around his body.
Black storm clouds churning overhead with distant thunder.

Composition: rule of thirds, character in lower-left third, vast sky and clouds
filling upper two thirds. Wind sweeping his hair and robe to the right.

Mood: lonely, defiant, the calm before the storm.

NEGATIVE: no text, no watermark, no anime, no cartoon, no character drift,
no outfit drift, no modern elements, no plastic skin, no flat lighting."

视频 prompt 范例（10s 镜头）:
"KEYFRAME: @image_3 as starting frame.
CHARACTER LOCK: @character1.

STYLE: ultra-cinematic wuxia 8K, 35mm anamorphic, teal-amber grade.

DURATION: 10s.
[0-2s] Wind picks up violently, his hair and robe whip dramatically. Camera
       holds static then begins slow push-in.
[2-5s] He slowly raises his head, eyes opening to reveal cold determination.
       Golden tribulation lightning intensifies around him.
[5-8s] In one smooth motion he pulls the sword from the stone, blade emitting
       a crystalline metallic ring and glowing faintly cyan.
[8-10s] He stands fully, sword pointed at the sky, robe billowing. Camera
       freezes on the silhouette as lightning strikes behind him.

CAMERA: low-angle hero shot, 24mm wide, slow Steadicam push-in from
medium-wide to medium-close. 0.5x speed ramp on sword draw [5-8s].

AUDIO:
- Ambient: howling mountain wind, distant rolling thunder
- Key SFX: crisp metallic sword unsheathe at [5-8s], crackling
  lightning energy hum sustained
- Music: traditional erhu + drums building to cymbal crash at [8-10s]
- No dialogue

NEGATIVE: no text, no character drift, no costume drift, no extra fingers,
no warped sword, no flickering, no jump cuts."
```

### 2. 玄幻仙侠 Xianxia
```
风格锚:
"epic xianxia fantasy 8K hyper-realistic, Unreal Engine 5 quality rendering,
cool blue-purple-gold palette with magical light particles, volumetric god rays
through ancient ruins, glowing rune circles, dragon-scale texture details,
Marvel-meets-traditional-Chinese aesthetic"

关键词清单（hermes 把这些拼进每个 image prompt）:
- 灵气粒子 / qi particles flowing
- 法阵 / glowing rune circles, ancient seals
- 灵兽 / divine beasts (dragon, phoenix, qilin) with scale detail
- 神光 / volumetric godlight rays
- 渡劫雷 / heavenly tribulation lightning
- 神器 / artifact glow with engraved patterns

视频 prompt 必备:
- camera: dramatic crane shots, 360° orbit on power moments, slow-mo on impact
- audio: orchestral choir + thunder + dragon roar + jian-qi sword energy hum
```

### 3. 都市悬疑 Urban Thriller
```
风格锚:
"gritty urban thriller cinematography, 35mm with subtle handheld vibration,
teal-orange Hollywood color grade, wet-asphalt neon reflections, anamorphic
horizontal lens flare, motion blur on action, Fincher-meets-Villeneuve mood"

典型场景:
- 雨夜地铁站 / rainy subway platform with sodium-vapor lamps
- 高楼顶 / rooftop skyline at blue hour
- 审讯室 / interrogation room with single low-key spotlight
- 巷道追逐 / alley chase with flickering neon signs

image prompt 范例:
"Detective in rumpled trench coat stands at the edge of a rain-soaked rooftop
overlooking a sprawling Hong Kong skyline at blue hour. Distant neon billboards
reflect in puddles at his feet. Cigarette smoke curls past his face.

Composition: medium-wide shot, character in right third, vast city in left two
thirds with massive negative space.

Mood: weary, calculating, on the edge of a breakthrough.

NEGATIVE: no text, no watermark, no cartoon, no anime, no oversaturation,
no plastic skin, no flat lighting."

视频要点:
- camera: handheld documentary feel, whip-pans on tension, rapid intercut
- lighting: harsh sodium-vapor street lamps, neon billboards, headlight flashes
- audio: cinematic synth bed + tense low drones + sudden impact stings
```

### 4. 赛博朋克 Cyberpunk
```
风格锚:
"cyberpunk neon-lit future megacity, 8K hyper-realistic, magenta-cyan-violet
neon palette, holographic UI overlays, chromatic aberration on highlights,
volumetric fog with neon backlighting, Blade Runner 2049 + Ghost in the Shell
aesthetic, anamorphic horizontal flares"

视觉元素:
- 全息广告 / floating holographic billboards (with non-text alien glyphs)
- 飞行车 / sleek hovercars with light trails
- 义体改造 / cybernetic implants with subtle LED accents
- 霓虹雨 / neon rain reflecting on wet asphalt

image prompt 范例:
"@character_kira — keep SAME face, SAME magenta-tipped neon-blue undercut hair,
SAME black tactical jumpsuit with cyan circuitry glow on chest panels, SAME
chrome cybernetic right arm.

She sprints through a narrow alley packed with steaming food stalls under a
canopy of holographic billboards. Rain slicks the asphalt and reflects the
magenta-cyan neon. Sparks fly from her chrome heels on impact.

Composition: low-angle wide shot, 14mm ultra-wide, character charging toward
camera in extreme perspective, neon corridor framing her on both sides.

Mood: kinetic, hunted, defiant.

NEGATIVE: no text, no readable signage, no cartoon, no anime style (use
photoreal), no character drift, no extra fingers, no warped chrome arm."
```

### 5. 硬科幻 Hard Sci-Fi
```
风格锚:
"cinematic hard sci-fi, 8K photorealistic, cool blue-cyan + warning red palette,
chromatic aberration on holographic UI, subtle digital noise, NASA / SpaceX
documentary realism + Christopher Nolan epic scale, anamorphic widescreen"

视觉元素:
- 太空站内饰 / clean white modular space-station corridors
- 全息控制台 / floating holographic data displays
- 行星表面 / alien planet vistas with two suns or rings
- 太空服 / detailed EVA suit fabric folds and helmet reflections

视频要点:
- camera: smooth gimbal tracking, drone fly-throughs, FPV chase, dramatic dutch
  angles on tension moments
- lighting: cold LED practicals + holographic glow + dramatic rim from
  blue/red emergency strobes
- audio: synth bed + servo whines + holographic UI beeps + bass-heavy impact +
  ambient station hum
```

### 6. 奇幻冒险 Western Fantasy
```
风格锚:
"Hollywood epic fantasy, anamorphic widescreen 2.39:1, warm earth-tone palette
with magical accent colors (cyan, violet, gold), AAA film quality, painterly
atmospheric haze, Lord of the Rings + Witcher + How to Train Your Dragon
inspired"

视觉元素:
- 古老森林 / ancient forest with moss-covered ruins
- 龙 / dragons (use real-world physics for wing membrane)
- 火光 / firelight warm fill at night
- 飘扬旗帜 / banners flowing in wind on castle walls

image prompt 范例:
"A young dragon rider in worn leather armor stands atop a windswept cliff,
hand resting on the snout of an enormous obsidian-scaled dragon whose wings
fold protectively around them. Misty mountain peaks stretch to the horizon
behind. Golden hour sun breaks through clouds.

Composition: wide shot, 35mm, characters in lower-center third, dragon's
massive head dominates upper-right, vast landscape filling background.

Mood: bonded, awe-struck, the moment before a great journey begins.

NEGATIVE: no text, no watermark, no cartoon (use photoreal), no character
drift, no warped dragon anatomy, no extra wings, no flat lighting."

视频要点:
- camera: sweeping aerial drone, low-angle hero pose, smooth crane reveals
- audio: orchestral fantasy score + dragon/beast roars + magical chime tinkles
```

### 7. 纪录片 / 真实风 Documentary
```
风格锚:
"documentary realism, 35mm with handheld micro-shake, natural color grade
(no aggressive teal-orange), available natural light, shallow DoF on emotional
moments, Vice / Netflix-doc aesthetic"

视觉元素:
- 自然光 / window light, golden hour, no studio strobes
- 真实环境 / real lived-in spaces, not staged
- 主体直视 / occasional direct-to-camera glance
- 旁观视角 / fly-on-the-wall framing

image prompt 范例:
"A 58-year-old fisherman with weather-beaten face and salt-stained hands
mends a torn net at the edge of a wooden dock at sunrise. Mist drifts off the
calm harbor water. His expression is meditative, lost in the rhythm of the
work.

Composition: medium close-up, 50mm, shallow DoF, character in left third,
soft-focused boats and water filling background. Camera slightly below his
eye-line for intimacy.

Mood: dignified, contemplative, the quiet labor of a lifetime.

NEGATIVE: no text, no watermark, no cinematic teal-orange (keep natural),
no plastic skin, no fashion makeup, no studio lighting, no exaggerated grain."
```

### 8. 广告片 / 电商种草 Commercial Ad
```
风格锚:
"premium commercial photography, ultra-clean composition, soft directional
studio lighting, shallow DoF, macro detail on product texture, 8K hyper-real,
Apple keynote + luxury brand aesthetic"

结构（5 镜头模板，竖屏 9:16 短视频）:
1. 钩子（0-2s）— extreme close-up product detail + attention grabber
2. 痛点（2-5s）— problem montage, fast-cuts, relatable scene
3. 产品出场（5-8s）— hero shot, slow rotation, clean background
4. 卖点演示（8-12s）— product in use, satisfying motion
5. CTA（12-15s）— logo + clean copy space (no text rendered, leave room)

image prompt 范例（产品 hero shot）:
"A frosted glass bottle of premium serum stands centered on a polished marble
surface, single soft directional light from upper-left creating elegant
highlight on the glass curve. Subtle water droplets clinging to the bottle.
Soft pink rose petal floating in air mid-fall on the right.

Composition: centered hero shot, 9:16 vertical, 100mm macro lens, shallow DoF
with marble surface fading to soft bokeh.

Mood: premium, clean, aspirational.

NEGATIVE: no text on bottle (will be added in post), no watermark, no clutter,
no human hands in frame, no cartoon, no exaggerated saturation."
```

### 9. 音乐 MV
```
风格锚:
"music video aesthetic matching <genre>, dynamic editing rhythm sync to beat,
saturated mood-driven color grade, 50% slow-mo + 50% real-time mix,
A24 / Hiro Murai inspired"

要点:
- 镜头节奏 = 音乐 BPM
- 慢镜头用在情绪段（副歌前的静止 / 副歌爆发）
- color grade 跟着情绪段切换（A 段冷调 / 副歌暖调）
- 8 镜头模板：环境引入 / 主角入场 × 2 / 高潮慢镜 × 2 / 反转 / 收尾
```

### 10. 日系动漫 Anime
```
风格锚:
"Japanese cel-shaded anime, Makoto Shinkai-inspired backgrounds with
ultra-detailed light particles, cinematic camera but anime rendering, soft
lens bloom on bright sources, painterly clouds, hand-drawn line quality"

视觉元素:
- 闪烁阳光 / sunbeams through leaves with bokeh particles
- 校服细节 / detailed school uniform with realistic fabric folds
- 头发飘动 / dynamic hair physics (anime exaggerated but consistent)
- 雨滴 / individually rendered raindrops with reflections

image prompt 范例:
"A teenage boy in a navy-blue school uniform stands on a deserted train
platform at golden hour, gazing at his hand where a single sakura petal has
landed. Train tracks stretch into the distance behind him. Light flares
through his hair.

Composition: medium shot, 35mm, character in right third, leading lines from
the tracks pulling eye into deep background.

Mood: melancholic, suspended in time, on the verge of revelation.

Style: Makoto Shinkai-inspired anime cel-shaded with painterly background,
soft lens bloom, ultra-detailed lighting.

NEGATIVE: no text, no watermark, no realism (this is anime), no character
drift, no extra fingers, no warped uniform."
```

---

## 🔑 工业级 Prompt 公式速查

### image2video（视频片段）— 七要素结构
```
[Style] + [Duration breakdown] + [Scene] + [Character lock] +
[Action with physics] + [Camera] + [Audio] + [Negative]
```
**目标长度**：≥ 800 字符

时间戳分段（必加）：
```
DURATION: 10s.
[0-2s] hook + camera setup
[2-5s] rising + character reaction
[5-8s] climax + key SFX
[8-10s] payoff / final freeze
```

通用 negative：
```
no text, no watermark, no logo, no subtitles, no cartoon, no anime,
no CGI look, no extra limbs, no deformed hands, no face morphing,
no character drift, no outfit drift, no flickering, no warping,
no oversaturated colors, no plastic skin
```

### characterSheet（角色立绘）
```
[Identity 1 sentence] +
FACE LOCK: oval / hairstyle / eye shape / signature mole+expression
BODY LOCK: height / build / posture
HAIR LOCK: length / color / style detail
OUTFIT LOCK: every piece — top / bottom / shoes / belt / accessories
SIGNATURE ITEMS: weapon / pendant / amulet
POSE: stance + expression
VIEWS REQUIRED: front / side / back (or 9 views) — identical across all
STYLE: photorealistic concept art, neutral grey BG, soft studio light
NEGATIVE: ...
```
**目标长度**：≥ 800 字符

### image（每镜头分镜）
```
[Character lock 1 段] + [Scene] + [Composition] + [Mood] + [Negative]
+ 结构化字段独立填（shotSize / cameraAngle / cameraMovement /
                lighting / colorTone / lens / aspectRatio / styleRef）
```
**目标长度**：prompt 字段 ≥ 500 字符；结构化字段必须填齐

---

## 🎬 P0 进阶 #1 — 双关键帧锁定（Dual-Keyframe Lock）

**业界最强一致性技巧**。每个 image2video 节点除了首帧，再连一张末帧（character 同位姿/同光照、动作终态），模型在两端之间插值，**运动稳定 10×，角色完全不漂**。

### 工作流图（每镜头都这么搭）

```
┌──────────────────┐
│ image (首帧 t=0) │ — 角色起始姿态：剑入鞘、眼睛闭合
│  📸 dolly-in     │
└─────────┬────────┘
          │ images
          ▼
   ┌─────────────────┐
   │  image2video    │  插值生成 8 秒动作
   │  prompt 描述     │
   │  起始 → 终态过程 │
   └─────────────────┘
          ▲
          │ images (tailFrame handle)
┌─────────┴────────┐
│ image (末帧 t=8) │ — 角色终态：剑出鞘半挥、眼睛睁开冷视
│  📸 same lens   │
└──────────────────┘
```

### Hermes 的搭法（每个 image2video 都建两个 image 节点）

```python
for i, shot in enumerate(SHOTS):
    # 首帧（开始姿态）
    canvas_add_node(
      project_id, kind="image",
      data_json={
        "label": f"镜头 {i+1} 首帧（t=0）",
        "prompt": "<角色起始姿态描述 — eyes closed, sword sheathed, calm>",
        "imageModel": "gpt-image-2-all",
        "aspectRatio": "16:9",
        "shotSize": shot["shotSize"],
        "lighting": shot["lighting"],
        # ...
      },
      position_x=700 + i * 250, position_y=200
    ) → start_id
    
    # 末帧（终止姿态，相同景别 + 光线，只换角色姿态）
    canvas_add_node(
      project_id, kind="image",
      data_json={
        "label": f"镜头 {i+1} 末帧（t={duration}s）",
        "prompt": "<角色终止姿态描述 — eyes open, sword half-drawn, fierce>",
        "imageModel": "gpt-image-2-all",
        "aspectRatio": "16:9",
        "shotSize": shot["shotSize"],   # 跟首帧相同
        "lighting": shot["lighting"],   # 跟首帧相同
        # ...
      },
      position_x=700 + i * 250, position_y=300
    ) → tail_id
    
    # 视频节点
    canvas_add_node(project_id, kind="image2video", ...) → video_id
    
    canvas_connect(start_id, "images", video_id, "image")     # 首帧
    canvas_connect(tail_id, "images", video_id, "tailFrame")  # 末帧
```

### 末帧 prompt 写作要点

- **景别 / 光线 / 镜头规格 / color grade 必须跟首帧一致**（不一致就成两个镜头了）
- **只改角色姿态、表情、手部动作**
- **不引入新元素**（背景、配角、道具该是同一组）
- **negative prompt 强调"same camera angle as first frame, same lighting, same costume"**

### 模型支持矩阵（hermes 选模型时参考）

| 模型 | 双关键帧 | 备注 |
|---|---|---|
| Veo 3.1 | ✅ | 推荐，电影级 |
| Sora 2 Pro | ✅ | 长镜头最稳 |
| Kling 2.6 Pro | ✅ | 嘴型同步 + 双帧 |
| Seedance 2.0 | ✅ | 高性价比 |
| Pika 2.0 | ✅ | 风格化强 |
| Nano Banana Pro i2v | ⚠️ | 仅首帧，末帧会被忽略 |

**默认策略**：能填末帧就填。不填只在以下情况：
- 镜头是固定环境镜头（无角色）
- 镜头是 < 2s 的瞬间动作
- 用 Nano Banana 等不支持的模型

---

## 🔊 P0 进阶 #2 — 系统化音频设计（Audio Design）

**2026 顶级流程必备**。Veo 3.1 / Sora 2 / Kling 2.6 都是 native audio 模型，意味着 prompt 里写好的 SFX / ambient / music 会**同步**生成。不写 = 模型瞎给你配。

### 三层音轨结构（每个 image2video prompt 必须分这三层写）

```
AUDIO:
- Diegetic (场景内 / 物理可见声源):
  · 角色动作 → 脚步声 / 布料摩擦 / 武器交锋
  · 场景物理 → 风、雨、火、水流、玻璃碎裂
  · 对白 → "<台词>" by <character>, soft whispered tone
  
- Foley / SFX (强化情绪的非自然声效):
  · 慢镜头时刻：低频心跳鼓、抽真空感
  · 紧张时刻：金属高频嘶鸣、嗡嗡 drone
  · 释放时刻：cymbal crash + 大鼓
  
- Music / Score (情绪锚定):
  · 主题：<wuxia erhu | cyberpunk synth | orchestra epic>
  · 节奏：<slow building | pulsing 120 BPM | rising crescendo>
  · 情绪：<melancholy | tension | triumphant>
```

### 时间戳 SFX 节奏表（必加，跟时间戳 action 一一对应）

```
DURATION: 10s.
[0-2s] 动作: 角色缓缓抬头
       SFX:  轻微衣物摩擦, 远处风声渐起
       Music: 单一低音弦乐 sustain（C 低音，无主题）
       
[2-5s] 动作: 角色按上剑柄, 黄色雷电围绕
       SFX:  剑鞘金属嗡鸣, 雷电噼啪 crackle, 心跳低频开始 (60 BPM)
       Music: erhu 进入 piano 起调, 主题动机渐显
       
[5-8s] 动作: 拔剑出鞘, 一声金属脆鸣
       SFX:  ⚡ 关键击中: crisp metallic ring, sustain shimmer
              + 雷电 boom + 风骤起呼啸
       Music: ⚡ 主题爆发, drum hit, 全乐队 forte
       
[8-10s] 动作: 持剑站立 silhouette
       SFX:  剑光 hum 持续, 风渐弱
       Music: 单一弦乐 hold, 留白
       
关键 SFX hit 时刻 (与 action peak 同步): [5.0s] 拔剑金属声
```

### 各题材的 Audio Design preset

#### 古风武侠
```
Diegetic: wind through bamboo, fabric flutter, sword unsheathe ring,
          footsteps on wet stone, distant bird cry
Foley: low-frequency heart drum on tension, sub-bass rumble on impact,
       crisp shimmer on sword aura
Music: traditional erhu lead + bamboo flute + taiko drums + strings,
       sparse minimalist arrangement, building to single climactic hit
Vocals: optional brief whispered monologue, no opera-style singing
```

#### 玄幻仙侠
```
Diegetic: thunder crackle, qi-energy hum, dragon roar (deep + reverb),
          rune circle glow hum, robe whip in spirit wind
Foley: ethereal choir whoosh on power activation, deep bass sub-drop on impact
Music: full orchestral with epic choir (Latin/Sanskrit chant), traditional
       Chinese instruments layered (erhu, guzheng), rising 4-note motif
Sound design: heavy reverb tail on all impacts (cathedral hall), pitch-shift
              on supernatural elements
```

#### 都市悬疑
```
Diegetic: rain on metal, distant traffic, neon hum, footsteps on wet asphalt,
          phone vibrate, lighter flick
Foley: tense low drone bed continuous, heart-beat thud on stress,
       sudden silence drop before reveal
Music: minimal synth bed + cello sustain, building 90 BPM, sparse piano
Sound design: dry close-mic'd dialogue, ambient room tone present, no reverb
```

#### 赛博朋克
```
Diegetic: neon buzz, hovercar pass-by whoosh, holographic UI beeps,
          rain on plastic surfaces, crowd murmur with synthesized accent
Foley: synth zaps on cybernetic activation, glitch artifacts on reveal,
       sub-bass drone on tension
Music: synthwave / vaporwave 120 BPM, retro arpeggios, modulated lead,
       gated reverb snare
Vocals: optional vocoder/auto-tune treatment on dialogue
```

#### 硬科幻
```
Diegetic: spaceship hum, servo whines, holographic UI, EVA suit oxygen breath,
          radio chatter with static
Foley: bass drop on station maneuvers, sub-rumble for scale, beep cluster
       for tech systems
Music: orchestral + electronic hybrid, ambient pads, 4-note rising motif
       (à la Hans Zimmer / Ben Salisbury), no melody on tense moments
Sound design: heavy sub-bass for impact, near-silence in space, dialogue
              with slight comm-radio EQ
```

#### 奇幻冒险
```
Diegetic: dragon wing flap (low whoosh), forest ambient, fire crackle,
          armor clank, banner flap
Foley: low rumble on dragon footsteps, magical chime sparkle on enchantment,
       battle horn brass blow
Music: full orchestral fantasy (LotR-inspired), choir on hero moments,
       wooden flute on quiet moments, drum gallop on action
Sound design: rich reverb on grand spaces, intimate dry mix on quiet talk
```

#### 纪录片
```
Diegetic: real environmental ambience (no enhancement), natural breath,
          actual mechanical sounds of work
Foley: minimal — only enhance what's already there, no added drama
Music: sparse piano / acoustic guitar / single string instrument, quiet
       presence not foreground
Vocals: clean documentary-style voiceover, no character voices
```

#### 商业广告
```
Diegetic: clean product sounds (bottle pop, click, satisfying snap),
          minimal background
Foley: ✨ sparkle / chime on key moments, satisfying sound design beats
       on every action
Music: upbeat mainstream pop, brand-mood (luxury = piano, energy = drums),
       hooks at 5s / 10s / 15s for ad cuts
Vocals: clear professional voiceover, brand jingle optional
```

#### 音乐 MV
```
Music: <song reference / genre / BPM> — drives the cut rhythm
Diegetic: minimal — only when story-relevant
Foley: SFX hits matched to musical accents (kick / snare / cymbal)
Visual cuts: edit on beat — every shot change synced to musical phrase
```

#### 日系动漫
```
Diegetic: subtle natural sounds, anime-stylized whoosh on movement,
          school bell, train pass-by, sakura flutter
Foley: anime-style SFX hits ("shing!" on reveal, sparkle chime on emotional
       beat), exaggerated wind on dramatic moments
Music: anime J-pop / orchestral hybrid, piano lead on emotional moment,
       solo violin on melancholy, full ensemble on action peak
Vocals: optional Japanese dialogue with natural intonation
```

### 关键准则

1. **每个时间戳分段都要有声音**（不能写"0-2s 角色抬头"完事，必须 0-2s 也写 SFX）
2. **关键 SFX hit 时刻要明确**（"⚡ at [5.0s]: metallic sword ring"）
3. **音乐情绪曲线要画**（buildup → climax → release）
4. **不要写"epic music"这种空话**（要写"orchestral with rising 4-note motif building to cymbal crash at 8s"）

---

## 🔍 P0 进阶 #3 — Vision 自检闭环（Self-correcting Loop）

**让 hermes 自己审核分镜质量**。每个 image 节点跑完后调 `canvas_evaluate_artifact`，vision 模型给打分，不达标就改 prompt 重跑。

### ⚙️ 自检开关（用户可控）

**默认关闭**（标准模式不消耗 vision 配额）。开关存在画布 meta 里。

| 工具 | 用法 |
|---|---|
| `canvas_get_meta(project_id)` | 读当前开关状态 |
| `canvas_set_self_check(project_id, enabled, max_retries=3, pass_threshold=8)` | 启停自检 |
| `canvas_set_cinematic_pro_mode(project_id, enabled)` | 启停影视级深度模式 |

**何时启用自检**（hermes 自动判断）：
- 用户说"严格审核 / 质量优先 / 完美一致 / 不能漂"
- 用户说"上电影院 / 节展投递 / 商业项目"
- 启用了 cinematicProMode（影视级深度模式自动连带启用）

**何时关闭**（默认）：
- 用户没特别要求
- 用户说"快出 / 不用审 / 我自己看"
- vision 配额紧张

**hermes 启用自检的标准对话**：
```
我会启用 vision 自检（max_retries=3, pass_threshold=8）。
意思是每跑完一个 image / characterSheet / storyboard 节点后，
我会自动调 vision 模型审核：
- 角色一致性 (face/hair/outfit/signature 是否漂移)
- 镜头执行 (实际景别/角度/光是否匹配指定的)
- 风格统一 (跟整片风格锚是否对齐)
- Negative 违反 (字幕/水印/多手指等)

不达标会自动改 prompt 重跑（最多 3 次），3 次还不行会告诉你具体问题。
（这会消耗额外的 vision 配额，约为标准模式的 1.3-1.8×）

调用: canvas_set_self_check(project_id, enabled=true)
```

### 工作流

```
1. Hermes 搭画布完成
2. canvas_get_meta(project_id) → 读 selfCheckEnabled
3. 用户点 ▶ 跑某个 image 节点
4. image 跑完，produces image url
5. 仅当 selfCheckEnabled=true 时:
   调 canvas_evaluate_artifact(
       url=image_url,
       brief="检查角色是否与 character sheet 一致：
              face shape / hair / outfit / signature item，
              并按 1-10 分打分。
              失败项明确列出并指出哪个 lock 字段被漂移。",
       expected_character_desc=<character_sheet description>,
       expected_style=<storyboard anchor style>
   )
6. 拿到 evaluate 返回的 score + feedback
7a. score >= pass_threshold: 标记 done，告诉用户"质量合格，可继续下一节点"
7b. score < pass_threshold: hermes 自动:
    - 解析 feedback 找出哪个 lock 被漂移
    - 调 canvas_update_node_data(image_id, patch={
        "prompt": <补强 lock 关键词的 prompt 修订版>
      })
    - 调 canvas_run_node(image_id, mode="only") 重跑
    - GOTO 5
8. 重试达到 max_retries 仍不行 — 告诉用户"建议手动调整 reference image"
```

### Hermes 何时触发自检

**自动触发**（推荐默认行为）：
- 用户首次 run 一个 characterSheet 节点 → 出来后自检 face/outfit consistency
- 用户首次 run storyboard 风格锚 → 自检风格定位是否符合题材
- 用户跑某个 image 节点 → 自检 character lock 是否保持

**不自检**（避免烧 vision API）：
- 同一节点 ≥ 3 次重试已失败
- 用户明说"先别评估，我自己看"
- 视频节点（vision 模型对 mp4 url 经常 429）

### Hermes 调用模板

```python
# 等用户运行了 image_node_id 之后
state = canvas_get_state(project_id)
node = state["nodes"][image_node_id]
if node["data"]["status"] == "done" and node["data"]["outputs"].get("images"):
    image_url = node["data"]["outputs"]["images"][0]
    
    eval_result = canvas_evaluate_artifact(
        url=image_url,
        brief=f"""审核这张分镜图是否符合以下要求：
        
        1. 角色一致性: 跟 character_sheet @character1 完全一致
           - 脸型: {face_lock_summary}
           - 发型: {hair_lock_summary}
           - 服装: {outfit_lock_summary}
           - 标志物: {signature_lock_summary}
        
        2. 镜头语言: 实际呈现的景别 / 角度 / 运镜是否匹配指定的
           {shot_size} / {camera_angle} / {camera_movement}
        
        3. 风格一致性: 跟整片风格锚是否对齐 — 色调 / 灯光 / 质感
        
        4. 构图质量: 三分法 / 引导线 / 留白是否合理
        
        5. negative 列表是否被违反: 是否出现 字幕 / 水印 / 多手指 / 现代元素
        
        请按 1-10 分打分（>= 8 视为通过），并明确列出失败项。""",
        criteria_keywords=[
            "character consistency", "shot framing", 
            "style match", "composition quality"
        ]
    )
    
    if eval_result["score"] >= 8:
        # 通过，告诉用户可以下一步
        pass
    elif retry_count < 3:
        # 失败：根据 feedback 修订 prompt
        revised_prompt = revise_prompt_with_feedback(
            original=node["data"]["prompt"],
            failed_aspects=eval_result["failures"]
        )
        canvas_update_node_data(
            project_id, image_node_id, 
            patch={"prompt": revised_prompt}
        )
        canvas_run_node(project_id, image_node_id, "only")
        # 等运行完再次 evaluate
    else:
        # 重试次数用尽
        告诉用户："这个镜头连续 3 次自动修订仍未达标，
                   建议你手动调整 reference image 或 character sheet。
                   失败原因: {eval_result['failures']}"
```

### Vision 评估的 brief 写作要点

- **明确每一项要审什么**（不要写"质量好不好"，要写"face shape match? outfit identical?"）
- **打分阈值**（必须 ≥ 8 才通过，5-7 是边缘，< 5 一定失败）
- **失败项要可定位**（哪个 lock 被漂移，方便 hermes 修订对应 prompt 段）
- **关键词列表 criteria_keywords**（让 evaluate 内部用 keyword match 加权）

### 视频节点不做闭环（重要）

---

## 🚧 强制 Phase Gates（违反即故障）

**在调用任何 `canvas_*` 工具之前，hermes 必须先在 chat 里完成 Phase 1-3 的输出**。
**Phase 1-3 全部输出 + 用户确认后**，才能进入 Phase 4 搭画布。

如果用户说"直接做 / 直接搭 / 不要分析"，hermes 仍然必须**至少口头执行 Phase 1-3 的简化版**（哪怕一句话），不能跳。这是工业流程的底线。

---

### Phase 1 — 剧本拆解（Story Beats Analysis）

**MUST OUTPUT BEFORE ANY canvas_ tool call**：

输出格式（在 chat 里直接说，不调工具）：

```
## 📖 Phase 1 · 剧本拆解

【题材定位】古风武侠 + 玄幻渡劫 + 神龙斗法
【核心冲突】少年护龙 vs 魔尊夺龙魂；劫力濒溃 vs 龙息觉醒
【三幕结构】
  - Act 1 (Setup, 0-10s): 渡劫危机 — 立 stake "为何不退"
  - Act 2A (Rising, 11-25s): 反派近身打斗 — 主角力竭跌势
  - Act 2B (Midpoint+Bottom, 26-40s): 绝境流血 → 法阵激活 → 龙吟伏笔
  - Act 3 (Climax+Resolution, 41-60s): 神龙现世 + 人剑合一 + 收尾留白

【情绪曲线】凝重 ↗ 紧张 ↗ 绝望 ↘ 希望萌芽 ↗ 燃爆 ↘ 静谧悠远
【核心 motif】青色龙息光 / 金色劫雷 / 白衣飘零 / 黑雾压境
【钩子句】"百年渡劫，世人皆夺仙位，唯我，逆命护龙。"
【收尾句】"凡人执剑，可斩虚妄；真龙伴身，可逆苍天。"
```

每场必须有：beat label + emotional intent + key visual + 时间窗。

---

### Phase 2 — 角色性格分析（Character Bible）

**MUST OUTPUT BEFORE ANY canvas_ tool call**：

每个出场角色单独一段（≥ 200 字），包含：

```
## 🎭 Phase 2 · 角色 Bible（出场顺序）

### 🤍 白衣少年剑仙（主角）
- **背景**：百年道宗修士，承青龙血脉守护遗令；正在天劫破境
- **性格内核**：隐忍、孤勇、悲悯（不是"愤怒少年"也不是"冷酷剑客"）
- **当下情绪曲线**：起身决意 → 力竭隐忍 → 鲜血激法阵 → 借龙力人剑合一
- **行为动机**：护龙护苍生 > 渡劫成仙
- **标志气场**：金色劫光淡雅 + 白衣染尘 + 长剑插地（被动姿）
- **微表情设计**：眼神先垂后抬、嘴角紧抿、虎口溢血时仍稳呼吸
- **声音设计 (vocal tone)**：清冷低沉、短句、几乎不喊
- **Identity Lock 标志物**：枷锁道痕（脖颈/手腕）、长剑、淡金劫光晕

### 🖤 黑衣魔尊（反派）
- **背景**：魔道大能、嗜血夺天劫；嗅到龙脉
- **性格内核**：暴戾 + 诡谲（不是"冷漠反派"，是带笑的恶意）
- **行为动机**：夺龙魂强化己身
- **标志气场**：黑雾翻涌 + 利爪凝魔 + 踏空俯冲
- **微表情设计**：嘴角斜挑、瞳孔猩红、笑起来更凶
- **声音设计**：阴冷拖音、笑里带嘲讽
- **Identity Lock 标志物**：黑色高领斗篷、爪化黑雾、金线魔纹

### 🐲 远古青龙（神兽）
- **背景**：上古护脉灵龙、沉睡千年响应主角剑意
- **性格内核**：威严沉睡 → 觉醒后温顺护主
- **登场设计**：青碧光柱破云 + 龙须飘摇 + 龙瞳凛冽（出场即神性）
- **声音设计**：低沉古远龙吟（沉蛰）+ 出阵后浩荡龙息音
- **Identity Lock 标志物**：青碧色鳞片、长须、四爪持剑光
```

---

### Phase 3 — 镜头规划（Shot Breakdown）

**MUST OUTPUT BEFORE ANY canvas_ tool call**：

输出一个**镜头表**（不是节点表，节点之后才建）。每镜头一行：

```
## 🎬 Phase 3 · 镜头规划

| #  | 时长 | 节奏 | 时段     | 内容          | 景别       | 角度    | 运镜        | 光线         | 色调               | 焦距   | 主角姿态 → 终态        | SFX 关键点       |
|----|------|-----|----------|---------------|-----------|---------|-------------|--------------|---------------------|--------|------------------------|------------------|
| 1  | 4s   | 慢  | 0-4s     | 远景立崖       | extreme-wide | low | static      | 低沉雷光     | teal-amber          | 14mm   | 单膝跪地剑插地 → 同 | 风声+轻雷        |
| 2  | 6s   | 中  | 4-10s    | 主角中景定调   | medium    | eye-level | dolly-in   | 黄金时刻     | warm rim+jade shadow | 24mm   | 闭目低头 → 抬眼睁目  | 衣袍猎猎+剑鸣    |
| 3  | 5s   | 快  | 10-15s   | 反派近身切入   | close-up  | low | static     | low-key      | crimson+jade        | 85mm   | (反派) 阴影露半脸 → 露齿笑 | 黑雾凝聚音       |
| 4  | 10s  | 极快 | 15-25s  | 双方打斗       | medium-wide | tracking | natural | 高对比 | tea-amber          | 35mm   | 横剑格挡 → 兵刃迸火星 | 兵器交击+碎石    |
| 5  | 8s   | 慢  | 25-33s   | 鲜血激法阵     | extreme-close | static | rembrandt | warm gold+cool | warm gold | 100mm-macro | 鲜血滴剑身 → 龙纹激活 | 法阵嗡鸣+心跳    |
| 6  | 7s   | 中  | 33-40s   | 龙息苏醒伏笔   | low / worms-eye | crane-up | backlit | magical cyan-violet | 24mm    | 黑雾压境 → 青光柱破阵 | 古老龙吟（深沉） |
| 7  | 12s  | 燃爆 | 40-52s  | 神龙现世人剑合一 | wide | orbit | golden+lightning | epic gold-cyan | 35mm | 青龙破阵 → 人剑合一冲撞 | 龙息+剑啸+破空 |
| 8  | 8s   | 渐弱 | 52-60s  | 收尾留白       | medium    | eye-level | dolly-out | blue-hour | cool blue+amber | 35mm | 龙盘旋身后 → 双双俯瞰山河 | 清亮剑鸣+悠长龙吟 |

【时长设计逻辑】
- 镜头 1 (4s)：开场建立，不能太短否则张力没起来
- 镜头 4 (10s)：打斗动作群——必须长，让动作展开
- 镜头 7 (12s)：高潮——绝对不能短，神龙登场+人剑合一是全片 payoff
- 镜头 8 (8s)：收尾留白——不能过短，余韵需要

【节奏曲线】4s 慢 → 6s 中 → 5s 快 → 10s 极快 → 8s 慢 → 7s 中 → 12s 燃 → 8s 渐弱
（不是 8/8/8/8 平均切，是按内容情绪起伏动态分配）

【模型选择推理】
- 单镜头 ≤ 8s 的（1, 5, 6, 8）：用 veo3.1-fast（首尾帧 + 音频，$0.17/s）
- 单镜头 = 10s 的（4）：用 hailuo-02 或 kling-video（5/10 双档）
- 单镜头 = 12s 的（7）：用 sora-2-pro（4/8/12 三档，$0.58/s，但是高潮值得）
  或 viduq3-pro（1-16s 任意，$0.12/s，性价比更高）
- 镜头 3 (5s) → seedance-2-0-pro（4-15s 灵活，$0.07/s）

【预算估算】
60s 总时长 × 混合模型平均 ≈ $0.25/s × 60 = ~$15 + 16 张分镜图 ≈ $2 = 总 $17
```

**关键准则**：
- 时长**不**等于"模型上限填满"，而是**剧情节奏决定**
- 高潮镜头要敢用长（12s）+ 贵的模型（sora 2 pro / vidu q3 pro）
- 过场镜头要用便宜短的（seedance / hailuo / veo fast）
- 同一片子可以混用 3-5 个不同模型

---

### Phase 4 Gate — 用户确认

Phase 1-3 输出完后，hermes **必须**说一句类似：

> 以上是剧本拆解 + 角色 Bible + 镜头规划。**确认无误我开始搭画布**？或者你想先调整哪一段（比如某个镜头时长 / 某个角色性格 / 某个色调）？

**等用户确认或微调后**，才能进入 Phase 4。

如果用户没说话直接给新指令，按用户最新意图去做（不阻塞）。

---

### Phase 4 — 搭画布（按 Phase 3 镜头表 1:1 映射）

下面才是工具调用阶段。**每个 canvas_add_node 的 prompt / 结构化字段必须从 Phase 3 镜头表抄过来**，不能凭空生成。


### Step 1 — 解析意图
- 用户给了完整剧本？→ Step 2
- 只说"做个 X 视频"？→ 自己用最常见模板（60s / 1 主角 / 用户提到的题材）

### Step 2 — 长剧本拆解（>500 字才需要）
```
canvas_segment_script(raw)  → episodes / global_characters / global_style
```

### Step 3 — 建项目（必须传 Phase 1-3 全文 + user_confirmed）
```
canvas_create_project(
  name="<项目名>",
  story_beats="<Phase 1 输出，≥120 字>",
  character_bible="<Phase 2 输出，≥200 字>",
  shot_breakdown="<Phase 3 输出，≥200 字>",
  user_confirmed=True   # 用户在 chat 中确认后才能传 True
)
→ 拿到 projectId（保存）

# 缺少任一字段或 user_confirmed=False → 工具直接返回 phase_gate_failed，
# 必须先回到 chat 补足 Phase 1-3 + 等用户确认，再重试。
```

### Step 4 — 加角色立绘（每出场角色一个）
```
canvas_add_node(
  project_id, kind="characterSheet",
  data_json={
    "label": "角色：白衣剑仙",
    "name": "白衣少年剑仙",
    "description": "<≥ 800 字符工业级 prompt>",
    "imageModel": "gpt-image-2-all"
  },
  position_x=100, position_y=100
)
→ character_node_id_1

# 反派配角同样
canvas_add_node(...)  → character_node_id_2
```

### Step 5 — 加 scriptGen
```
canvas_add_node(
  project_id, kind="scriptGen",
  data_json={
    "label": "剧本：XXX",
    "prompt": "<把用户原始剧本完整放进来>",
    "model": "MiniMax-M2.7-highspeed",
    "sceneCount": 6,
    "styleHint": "<根据题材选风格关键词>"
  },
  position_x=100, position_y=400
)
→ scriptgen_id
```

### Step 6 — 加 storyboard（**整片风格锚，1 个**）
```
canvas_add_node(
  project_id, kind="storyboard",
  data_json={
    "label": "整片风格锚",
    "sceneIndex": null,
    "style": "<从八大题材模板里选对应风格锚 prompt>",
    "imageModel": "gpt-image-2-all"
  },
  position_x=400, position_y=400
)
→ storyboard_anchor_id

# 连
canvas_connect(project_id, scriptgen_id, "scenes", storyboard_anchor_id, "scenes")
canvas_connect(project_id, character_node_id_1, "views", storyboard_anchor_id, "characters")
```

### Step 7 — 加每镜头的 image 节点（**B 工作流核心 — 每镜头双关键帧**）

**v7 关键升级**：每个镜头现在建 **2 个 image 节点**：首帧（start pose）+ 末帧（end pose）。两个都连进同一个 image2video 节点。这是 2026 顶级影视流程的硬指标。

按 60s/8 镜头规划：
```python
SHOTS = [
  {"duration": 3, "label": "镜头 1：开场远景（0-3s）", "shotSize": "extreme-wide",
   "startPose": "lone figure standing still on cliff", 
   "endPose": "wind starts to pick up, hair lifts",
   ...},
  {"duration": 4, "label": "镜头 2：主角中景（3-7s）", "shotSize": "medium",
   "startPose": "character looking down at sword hilt", 
   "endPose": "character lifts head, eyes meeting camera",
   ...},
  ...
]

for i, shot in enumerate(SHOTS):
    # 首帧（start frame, t=0）
    canvas_add_node(
      project_id, kind="image",
      data_json={
        "label": f"镜头 {i+1} 首帧（t=0）",
        "prompt": f"<≥ 500 字符 — character lock + {shot['startPose']} + scene + composition + mood + negative>",
        "imageModel": "gpt-image-2-all",
        "aspectRatio": "16:9",
        "count": 1,
        "shotSize": shot["shotSize"],
        "cameraAngle": shot["cameraAngle"],
        "cameraMovement": shot["cameraMovement"],
        "lighting": shot["lighting"],
        "colorTone": shot["colorTone"],
        "lens": shot["lens"],
        "styleRef": "<从风格 preset 选>",
      },
      position_x=700 + i * 250, position_y=200
    )
    → start_image_id_i
    
    # 末帧（end frame, t=duration）— 跟首帧相同 shotSize/lighting/lens，
    # 只换角色姿态描述
    canvas_add_node(
      project_id, kind="image",
      data_json={
        "label": f"镜头 {i+1} 末帧（t={shot['duration']}s）",
        "prompt": f"<≥ 500 字符 — character lock (SAME face/hair/outfit) + {shot['endPose']} + same scene + same composition + same lighting as first frame + negative including 'no camera angle change, no lighting change'>",
        "imageModel": "gpt-image-2-all",
        "aspectRatio": "16:9",
        "count": 1,
        "shotSize": shot["shotSize"],         # 跟首帧相同
        "cameraAngle": shot["cameraAngle"],
        "cameraMovement": shot["cameraMovement"],
        "lighting": shot["lighting"],         # 跟首帧相同
        "colorTone": shot["colorTone"],       # 跟首帧相同
        "lens": shot["lens"],                 # 跟首帧相同
        "styleRef": "<同上>",
      },
      position_x=700 + i * 250, position_y=380
    )
    → tail_image_id_i
    
    # 风格锚 → 首帧 + 末帧
    canvas_connect(project_id, storyboard_anchor_id, "boards", start_image_id_i, "styleRef")
    canvas_connect(project_id, storyboard_anchor_id, "boards", tail_image_id_i, "styleRef")
    # 角色 → 首帧 + 末帧
    canvas_connect(project_id, character_node_id_1, "views", start_image_id_i, "reference")
    canvas_connect(project_id, character_node_id_1, "views", tail_image_id_i, "reference")
```

### Step 8 — 加每镜头的 image2video（接首帧 + 末帧）
```python
for i, shot in enumerate(SHOTS):
    canvas_add_node(
      project_id, kind="image2video",
      data_json={
        "label": f"视频镜头 {i+1}（{shot['duration']}s, 双关键帧）",
        "prompt": "<≥ 800 字符工业级视频 prompt — 七要素 + 时间戳分段 + 三层 audio design + negative>",
        "videoModel": "veo-3.1",
        "duration": shot["duration"],
        "aspectRatio": "16:9"
      },
      position_x=700 + i * 250, position_y=600
    )
    → video_node_id_i
    
    # 首帧 → image2video.image
    canvas_connect(project_id, start_image_ids[i], "images",
                   video_node_id_i, "image")
    # 末帧 → image2video.tailFrame（关键！）
    canvas_connect(project_id, tail_image_ids[i], "images",
                   video_node_id_i, "tailFrame")
```

### Step 9 — 加 videoConcat
```
canvas_add_node(
  project_id, kind="videoConcat",
  data_json={
    "label": "成片",
    "videoOrder": [],
    "crossfadeSeconds": 0.5,
    "reencode": True,
    "bgmVolume": 0.35
  },
  position_x=2200, position_y=500
)
→ concat_id

# 把所有 image2video.videoUrl 顺序连到 concat 的 videos_multi
for i, vid_id in enumerate(video_node_ids):
    canvas_connect(project_id, vid_id, "videoUrl", concat_id, "videos_multi")
```

### Step 10 — 告诉用户（**不要自己 run**）
```
画布已搭建完毕，共 N 个节点：
- 角色立绘 × M
- 1 个剧本节点
- 1 个整片风格锚 storyboard
- 16 个分镜节点（8 个首帧 + 8 个末帧）
- 8 个视频节点（image2video，双关键帧驱动）
- 1 个拼接节点

请在画布上：
1. 检查每个节点的 prompt 与镜头字段是否符合你的设想
2. 任何节点都能改：双击编辑 prompt，或调整景别/光线/比例下拉
3. 推荐运行顺序：
   ① 先跑【角色立绘】拿到 identity anchor
   ② 再跑【整片风格锚】定基调
   ③ 然后跑每镜头【首帧 image】 + 【末帧 image】
   ④ 每对首末帧满意后再跑对应的【视频】节点
   ⑤ 全部视频跑完后跑【拼接节点】出成片

任何一个镜头不满意，单独改 prompt 重跑该节点即可，不影响其他镜头。

[v7 新功能] 跑完每个节点后，hermes 会自动用 vision 模型审核：
   - 角色一致性（face/hair/outfit/signature 是否漂移）
   - 镜头执行（实际景别/角度/光是否匹配）
   - 风格统一（跟整片风格锚是否对齐）
   - 不达标会自动改 prompt 重跑（最多 3 次），3 次还不行会告诉你具体问题。
```

### Step 11（v7 新增）— 自动跑 Vision 自检（用户运行节点后触发）

**前置条件**：先调 `canvas_get_meta(project_id)` 看 `selfCheckEnabled` 是否为 true。**默认是 false**——只有用户明确要求"严格审核 / 高质量 / 影视级"时，hermes 才该主动调 `canvas_set_self_check(enabled=true)`，然后才走下面的循环。

每当用户点 ▶ 运行了某个 image / characterSheet / storyboard 节点：
```python
# 0. 先看自检是否启用（避免烧 vision 配额）
meta = canvas_get_meta(project_id)
if not meta.get("selfCheckEnabled"):
    return  # 不启用就跳过

threshold = meta.get("selfCheckPassThreshold", 8)
max_retries = meta.get("selfCheckMaxRetries", 3)

# 1. 等节点 status = "done" + outputs.images 不为空
state = canvas_get_state(project_id)
node = state["nodes"][image_node_id]
if node["data"]["status"] != "done":
    return  # 还没跑完
image_url = node["data"]["outputs"].get("images", [None])[0]
if not image_url:
    return  # 没产出

# 2. 调 vision 自检
brief = build_consistency_brief(node, character_sheet_data)
eval_result = canvas_evaluate_artifact(
    artifact_url=image_url,
    brief=brief,
    expected_character_desc=character_sheet["description"],
    expected_style=storyboard_anchor["style"]
)

# 3. 根据评分决定下一步
if eval_result["score"] >= threshold:
    告诉用户：f"✓ 镜头 {N} 自检通过（{eval_result['score']}/10）。可继续下个节点。"
elif retry_count < max_retries:
    revised = revise_prompt_with_feedback(node["data"]["prompt"], eval_result["issues"])
    canvas_update_node_data(project_id, image_node_id, patch_json=json.dumps({"prompt": revised}))
    canvas_run_node(project_id, image_node_id, "only")
    告诉用户：f"⚠ 镜头 {N} 自检 {eval_result['score']}/10，发现问题：{eval_result['issues']}。
            已自动补强 prompt 重跑（{retry_count+1}/{max_retries}），请等待。"
else:
    告诉用户：f"✗ 镜头 {N} 连续 {max_retries} 次自检失败。问题：{eval_result['issues']}。
            建议手动检查 reference image 或 character sheet。"
```

视频节点不做自检（vision 网关对 mp4 不稳定 + 视频质量主观）。

---

## ⚠️ 红线 / 常见错误

### ❌ prompt 写"白衣染尘、隐忍坚毅"就完事
✅ 写满 800/500/800 字符（角色/分镜/视频），含完整锁定细节。

### ❌ 把镜头/光线/比例全塞 prompt 字符串
✅ shotSize / cameraMovement / lighting / colorTone / lens / aspectRatio / styleRef **都是独立字段**，分别填。前端会自动拼合到最终 prompt。

### ❌ 一个 storyboard 节点出 N 张图直接接 image2video
✅ storyboard 只当**整片风格锚**（1 张总视觉）；每个镜头单独一个 **image 节点**。

### ❌ 视频 prompt 不分时间戳
✅ `[0-3s] / [3-7s] / [7-10s]`，每段一个 action + camera。

### ❌ 镜头描述抽象："cinematic shot"
✅ "low-angle wide shot, 24mm, slow Steadicam push-in from medium-wide to medium-close"。

### ❌ 没 negative prompt
✅ 每个图/视频节点都加，至少 7 项（无文字、无水印、无角色漂移、无变形手等）。

### ❌ 搭完自己 canvas_run_node
✅ 搭完告诉用户运行顺序，**不**自动跑。除非用户明说"全部 run"。

### ❌ 长剧本（>500 字）直接灌 scriptGen
✅ 先 canvas_segment_script，再分集搭。

### ❌ 跨节点不重复 character lock
✅ 每个 image / image2video prompt 都重复 ≥ 4 项 lock 关键词（脸/发/服/饰）。

---

## 📐 视频时长黄金律 + 模型选择

### 单镜头时长
- **3-5 秒**：动作类（打斗、追逐、爆发）
- **5-8 秒**：叙事类（对话、走位、情绪转换）— **甜区**
- **8-12 秒**：环境/情绪（风景、慢镜头、静止特写）
- **>15 秒**：建议拆。模型超时会编瞎、角色漂移
- **60 秒成片**：5-8 个镜头。**不超过 10 个**

### 镜头节奏（Shot Rhythm）
- 慢节奏：3-5s/镜头（情绪/风景/纪录片）
- 中节奏：1.5-3s/镜头（叙事/对话/Vlog）
- 快节奏：0.3-1s/镜头（动作/MV/广告钩子）

### 模型选择决策树（v7 真实能力对照）

**Hermes 选 image2video.videoModel 之前必须先调 `canvas_list_video_models()`** 拿真实
duration / tailFrame / nativeAudio / 4K 限制再决定。常见错误：
- 选了 `veo3.1-fast` 但传 `duration: 5` → 网关 422（Veo 只接受 8）
- 选了 `veo3.1-pro-4k` 还想用首尾帧 → tailFrame 字段被忽略，角色漂移
- 选了 `sora-2-pro` 传 `duration: 10` → API invalid_value（只接 4/8/12）

**速查表**（每个模型的硬限制）：

| 模型 | duration（秒） | 首尾帧 | 原生音频 | 最高分辨率 |
|---|---|---|---|---|
| **Veo 3.1 Fast** ⭐ | 8 固定 | ✅ | ✅ | 1080p |
| Veo 3.1 / Pro | 8 固定 | ✅ | ✅ | 1080p |
| Veo 3.1 Fast 4K | 8 固定 | ✅ | ✅ | **4K** |
| Veo 3.1 Pro 4K | 8 固定 | ❌ | ✅ | 4K |
| Veo 3.1 4K | 8 固定 | ❌ | ✅ | 4K |
| Veo 3.1 Components | 8 固定 | ❌ | ✅ | 1080p |
| Veo 2 / 2 Pro / 2 Fast | 5-8 | ❌ | ❌ | 1080p |
| **Sora 2 Pro** ⭐ | **4 / 8 / 12 三档** | ❌ | ✅ | 1080p |
| Sora 2 | 4 / 8 / 12 | ❌ | ✅ | 720p |
| **Seedance 2.0 Pro** ⭐ | **4-15 任意** | ✅ | ✅ | 1080p |
| Seedance 1.0 Pro | 5-15 | ✅ | ❌ | 1080p |
| Seedance 1.0 Lite | 5-10 | ❌ | ❌ | 720p |
| **Hailuo 02** ⭐ | **6 / 10** | ✅ | ❌ | 1080p |
| Hailuo 2.3 | 6 / 10 | ✅ | ❌ | 1080p |
| **Kling Video (2.6 Pro)** ⭐ | **5 / 10** | ✅ | ✅ + 嘴型同步 | 1080p |
| Kling Avatar | 跟音频 | ❌ | （音频驱动）| - |
| Wan 2.6 I2V | 5 固定 | ✅ | ❌ | 1080p |
| **Vidu Q3 Pro** ⭐ | **1-16 任意** | ✅ | ✅ | 1080p |
| Vidu Q3 / Q3 Turbo / Q3 Mix | 1-16 任意 | ✅ | ✅ | 1080p |
| Vidu Q2 / Q2 Pro | 5 / 8 | ✅ | ❌ | 1080p |
| Grok Video 3 (10s) | 10 固定 | ❌ | ❌ | 1080p |

**决策路径**：

```
1. 用户每镜头 ≤ 8 秒 + 双关键帧（推荐）
   → Veo 3.1 Fast（默认 ⭐）

2. 用户某镜头要 >10 秒
   → Vidu Q3 Pro（1-16s 任意）★ 业内最长
   或 Sora 2 Pro（12s）
   或 Seedance 2.0 Pro（15s）

3. 用户要 4K + 双关键帧
   → Veo 3.1 Fast 4K（注意 Pro 4K / 4K 不支持首尾帧）

4. 用户要嘴型同步对白
   → Kling 2.6 Pro（kling-video）
   或 audio2video 节点 + Kling Avatar

5. 性价比批量出
   → Seedance 2.0 Pro / Vidu Q3 Turbo

6. 复杂多角色 + 长镜头
   → Sora 2 Pro（4/8/12 三档，物理最稳）
```

**hermes 调用模板**：
```python
# 0. 拿模型清单
models = canvas_list_video_models()

# 1. 按用户需求过滤（举例：要 12s + 双关键帧）
candidates = [
    m for provider in models["providers"]
    for m in provider["models"]
    if 12 in m.get("durationsSeconds", [])
    and m.get("tailFrame") is True
]
# → Vidu Q3 Pro / Vidu Q3 Turbo / Seedance 2.0 Pro

# 2. 选第一个推荐的（标了 ⭐）
chosen = candidates[0]["id"]

# 3. 建 image2video 节点时填进去 + duration 用 clamp 后的值
canvas_add_node(kind="image2video", data_json=json.dumps({
    "videoModel": chosen,
    "duration": 12,
    ...
}))
```

### Character Bible 三层锁死
1. **画布层**：characterSheet 节点 = single source of truth
2. **Prompt 层**：每个下游 image / image2video prompt 都重复 ≥ 4 项 lock 关键词
3. **Edge 层**：每个用到角色的节点必须 connect 到 characterSheet.views

---

## 🎯 全流程示例：60 秒玄幻武侠（hermes 实际操作清单）

用户给的剧本（节选）：
> 60 秒。男主白衣少年剑仙渡劫，黑衣魔尊夺龙魂，远古青龙觉醒。
> 0-10s 崖顶渡劫 / 11-25s 反派近身打斗 / 26-40s 绝境龙息苏醒 /
> 41-52s 神龙现世人剑合一 / 53-60s 收尾留白。

**Hermes 的 MCP 工具调用路径**：

```
1. canvas_create_project(
     name="少年剑仙渡劫·神龙伴身",
     story_beats="<Phase 1 全文（已在 chat 输出）>",
     character_bible="<Phase 2 全文（已在 chat 输出）>",
     shot_breakdown="<Phase 3 全文（已在 chat 输出）>",
     user_confirmed=True   # 用户已在 chat 中确认
   )
   → projectId

2. canvas_add_node(kind="characterSheet", label="白衣剑仙", description=<800字符锁定>, imageModel="gpt-image-2-all", viewCount=9)
   → 白衣剑仙_id   位置(100, 100)

3. canvas_add_node(kind="characterSheet", label="黑衣魔尊", description=<800字符锁定>, imageModel="gpt-image-2-all")
   → 魔尊_id   位置(100, 350)

4. canvas_add_node(kind="characterSheet", label="远古青龙", description=<800字符 — 龙身设计>, imageModel="gpt-image-2-all")
   → 青龙_id   位置(100, 600)

5. canvas_add_node(kind="scriptGen", prompt=<完整剧本>, sceneCount=8, styleHint="古风武侠 + 玄幻渡劫 + 神龙斗法")
   → script_id   位置(400, 100)

6. canvas_add_node(kind="storyboard", label="整片风格锚", style="cinematic wuxia ink-wash 35mm anamorphic teal-amber mist god rays")
   → anchor_id   位置(400, 400)
   canvas_connect(script_id.scenes → anchor_id.scenes)
   canvas_connect(白衣剑仙_id.views → anchor_id.characters)

7. 8 镜头 × 2 image (首帧 + 末帧) = 16 个 image 节点
   + 8 个 image2video 节点（每个连首帧 + 末帧）

每个镜头按下面填结构化字段:
| #  | 时长 | 时间段   | shotSize     | cameraMovement | lighting       | colorTone               | lens   | 起始姿态 → 终止姿态 |
|----|------|----------|--------------|----------------|----------------|-------------------------|--------|----|
| 1  | 4s   | 0-4s     | extreme-wide | static         | golden-hour    | teal-amber              | 14mm   | 远景人影孤立 → 镜头中风云压境 |
| 2  | 6s   | 4-10s    | medium       | dolly-in       | golden-hour    | warm rim teal shadow    | 24mm   | 主角低头闭目 → 抬眼睁目冷视 |
| 3  | 5s   | 10-15s   | close-up     | static         | low-key        | cool jade-blue + crimson| 85mm   | 反派阴影中露半脸 → 全脸暴戾笑 |
| 4  | 10s  | 15-25s   | medium-wide  | tracking       | natural        | high contrast tea-amber | 35mm   | 双方对峙 → 兵刃相交火星迸 |
| 5  | 8s   | 25-33s   | extreme-close| static         | rembrandt      | warm gold + cool shadow | 100mm-macro | 鲜血滴落剑身 → 龙纹法阵激活 |
| 6  | 7s   | 33-40s   | low + worms  | crane-up       | backlit        | magical cyan-violet     | 24mm   | 黑雾凝聚 → 青光柱破阵 |
| 7  | 12s  | 40-52s   | wide         | orbit          | golden-hour+lightning | epic gold-cyan   | 35mm   | 青龙破阵而出 → 人剑合一冲魔尊 |
| 8  | 8s   | 52-60s   | medium       | dolly-out      | blue-hour      | cool blue + faint amber | 35mm   | 龙盘旋少年身后 → 双双俯瞰山河 |

每个镜头：
canvas_add_node(kind="image", label="镜头N首帧", prompt=<起始姿态>, ...)  → start_id_N
canvas_add_node(kind="image", label="镜头N末帧", prompt=<终止姿态, 同景别同光>, ...) → tail_id_N
canvas_add_node(kind="image2video", label="视频N", prompt=<七要素+时间戳+三层audio+continuity>, ...) → vid_id_N
canvas_connect(anchor_id.boards → start_id_N.styleRef)
canvas_connect(anchor_id.boards → tail_id_N.styleRef)
canvas_connect(白衣剑仙_id.views → start_id_N.reference)
canvas_connect(白衣剑仙_id.views → tail_id_N.reference)
canvas_connect(start_id_N.images → vid_id_N.image)
canvas_connect(tail_id_N.images → vid_id_N.tailFrame)

8. canvas_add_node(kind="videoConcat", crossfadeSeconds=0.6, bgmVolume=0.4)
   → concat_id   位置(2400, 700)
   for vid_id in 8 个视频节点:
     canvas_connect(vid_id.videoUrl → concat_id.videos_multi)

9. 告诉用户：画布已搭好，按推荐顺序运行；每跑一个 image / characterSheet 我会自动调 vision 自检。
```

**节点总数**：3 角色 + 1 script + 1 风格锚 + 16 image (8 首 + 8 末) + 8 image2video + 1 concat = **30 节点**
**connect 总数**：约 50 条
**MCP 调用次数**：约 90 次
**自检 evaluate 调用**：用户跑节点时 hermes 自动触发，每节点 1-3 次（看是否需要重试）

---

## 🎞️ P1 影视级深度模式（Cinematic Pro Mode）

**何时启用**：用户提到以下任一关键词时，hermes 自动切换到深度模式：
- "影视级" / "电影级" / "高质量大片"
- "完美一致性" / "演员级 identity lock"
- "导演工作流" / "professional film"
- "上电影院" / "提交节展"
- 时长 > 90 秒 / 多角色 ≥ 3 个 / 多镜头 ≥ 12 个

**深度模式额外做 6 件事**（P0 三项之外）：

### P1-1. Beat Sheet 前置规划
在 scriptGen 之前，先用 chat 把剧本结构化成节奏单：
```python
# 三幕结构 / Save the Cat 节奏单 / 英雄之旅 — 选一个最贴的
beat_sheet = {
    "act1": {"setup": "...", "inciting_incident": "...", "first_act_break": "..."},
    "act2a": {"fun_and_games": "...", "midpoint": "..."},
    "act2b": {"bad_guys_close_in": "...", "all_is_lost": "...", "dark_night_of_soul": "..."},
    "act3": {"climax": "...", "resolution": "...", "final_image": "..."},
}
# 把这个结构作为 styleHint 的一部分喂给 scriptGen
```

### P1-2. Multi-Reference Stack（角色一致性终极方案）
深度模式下，每个 image 节点不只接 character.views[0]，而是 stack 多张：
```python
# 把 9 视图全部注入下游 image
# 通过 update_node_data 在 prompt 里 reference 多张
canvas_update_node_data(image_node_id, patch={
    "prompt": prompt + "\n\nIDENTITY REFERENCES (use ALL):\n" +
              "\n".join([f"- @character.view_{i}" for i in range(9)])
})
# 模型会用所有视图做 face/outfit lock，远稳于单图
```

### P1-3. A/B Variants（每个关键镜头出 3 个变体）
关键镜头（hook、climax、final）每个建 3 个 image 节点，prompt 微调：
```python
# 镜头 5 是高潮，建三版
for variant in ["wide hero shot", "low-angle hero", "extreme close-up emotion"]:
    canvas_add_node(kind="image", data_json={
        "label": f"镜头 5（{variant} 变体）",
        ...
    })
# 用户挑最好的连进 image2video
```

### P1-4. 双比例双成片（社媒分发）
videoConcat 后再加一个 videoConcat（9:16 版），同样 8 段视频但 aspectRatio="9:16"：
```python
# 主成片 16:9
canvas_add_node(kind="videoConcat", label="院线版 16:9", ...) → concat_landscape

# 社媒成片 9:16（重新跑 image2video，aspectRatio="9:16"）
# 或用 ffmpeg crop concat 出 portrait 版
canvas_add_node(kind="videoConcat", label="抖音版 9:16", ...) → concat_portrait
```

### P1-5. Continuity Rules（专业剪辑规则）
深度模式下，每个 image2video prompt 末尾加 continuity 段落：
```
CONTINUITY:
- This shot continues from previous shot N-1 ({shot_n_minus_1_summary})
- Character entered from screen-{left|right} previously
- Eye-line match: character is looking {direction} (matching prev shot's POV)
- Action match: action concludes from {prev_action_state}
- Color grade continuous with anchor (NO grade shift mid-scene)
- 180° rule: camera stays on the {left|right} side of action axis
```

### P1-6. Look Dev 阶段（前期视觉迭代）
深度模式下，搭画布后增加一个 Look Dev 试拍循环：
1. 先只跑【角色立绘】+【整片风格锚】+【镜头 1 首帧】
2. 用户审 → 不满意调 prompt → 重跑
3. 直到 Look 通过审核（hermes 调 evaluate_artifact 打 ≥ 9 分）
4. 再批量跑剩余节点（这时风格已锁，节省配额）

### 深度模式启动确认

用户说"做个影视级武侠片"时，hermes 应回复：
```
检测到你需要影视级深度模式。我会额外做 6 件事：
1. Beat Sheet 三幕结构前置规划
2. 角色 9 视图全部注入下游（multi-reference stack）
3. 关键镜头每个 3 变体（A/B testing）
4. 横屏 + 竖屏双成片
5. 镜头连续性规则（180° / eye-line / action match）
6. Look Dev 试拍循环（先确认前 1-2 镜头风格再批量出）

预估节点数：40-60，配额消耗约为标准模式的 2.5×。
是否启动？（回复"启动"或"标准模式"）
```

---

- 用户说"做个武侠片"——直接搭，别问太多。中途解释每步。
- 用户中途："风格不对要更暗"——`canvas_update_node_data` 改 storyboard 锚的 style 就行（不用重建）。
- 用户："角色脸不对"——回去改 characterSheet.description 加更多 face lock 细节，重跑该节点。
- 用户："再来一段升龙"——`canvas_add_node(kind="image")` + `canvas_add_node(kind="image2video")`，连进现有 concat 的 videos_multi。
- 用户："风格统一吗"——可以加 `shotGroup` 节点挂在多个 image 后面跑一致性 pass。

---

End of SKILL v7.2.
