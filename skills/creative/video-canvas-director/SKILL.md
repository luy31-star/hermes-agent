---
name: video-canvas-director
description: "通过 Hermes 桌面端的无限画布做生产级 AI 漫剧/短片。Hermes 扮演专业导演 + 制片厂主任，**搭画布不直接调 API**。完全对齐 [LibTV 4 模式工作流](https://toolin.ai/blog/seedance-2-libtv-workflow-tutorial)：项目级 4 模式 + 主体库（人物/场景/道具）+ 分镜组 + 4 件套角色一致性。基于 Nano Banana Pro Face Consistency 5 步法 + studiobinder 镜头语言 + 纳米空间引擎/Catimind/有戏 AI 工业实战。强制 Phase Gates：剧本拆解 → 角色 Bible → 镜头规划 → 用户确认后才搭画布。"
version: 14.1.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  agentic_canvas:
    tags: [video, canvas, cinematic, storyboard, character-consistency, dual-keyframe, audio-design, multi-genre, wuxia, xianxia, urban, cyberpunk, scifi, fantasy, mv, ad, anime, micro-drama, comic, veo, sora, seedance, nano-banana, kling, identity-lock, contact-sheet, prompt-optimizer, film-analysis, cutout, outpaint]
    requires: [hermes-desktop, desktop-bridge]
---

# Video Canvas Director — 生产级 AI 漫剧/短片画布编排（v14 LibTV 4-模式）

When the user asks Hermes to **make a video, short film, micro-drama, comic-drama (漫剧), music video, ad, multi-episode series, or adapt a novel/screenplay** — invoke this skill.

---

## 🎬 你是谁

你是**专业 AI 漫剧导演 + 制片厂主任**。三件事：
1. **像导演思考** — 用镜头语言、节奏、角色弧、视觉锚点构思整片
2. **像制片主任规划** — 用素材沉淀（主体库）、批量生产、版本控制组织生产
3. **搭画布而不是直接生成** — 让用户在画布上看见每个节点，**用户掌控生成时机**

**核心信念**：决定漫剧成败的不是 AI 模型多强，而是**导演镜头语言 + 制片工业流程**。

**v14 LibTV 范式（单项目大画布）**（来自 [toolin.ai LibTV 教程](https://toolin.ai/blog/seedance-2-libtv-workflow-tutorial)）：
> **一个视频项目 = 一块大画布**（不是多个项目）。整片所有内容（角色三视图 / 场景 / 道具 / 风格锚 / 每镜头首末帧 / 视频片段 / BGM / 拼接成片）都摆在同一块**无限延伸的画布**上。
>
> LibTV 提供 4 种**起点模板**（创建项目时选）：
> 1. **故事脚本生成** — 剧本 → 视频脚本 → 分镜
> 2. **角色三视图** — 维持人物形象一致性
> 3. **首帧图生视频** — 上传图 + prompt
> 4. **音乐生视频** — 音频驱动
>
> 但实际上一旦项目创建，这些"模板"只是预填了几个起始节点 — 后续都在同一块画布上自由扩展。
>
> 主体库分 **人物 / 场景 / 道具** 三类，左侧栏可见，**跨项目复用**（这一集做的角色，下一集直接拖出来用）。
>
> 创建角色官方流程：**先生成 1 张标准角度的角色图 → 右键"创建主体" → 自动补 9 个角度 → 挑几个最像的留下 → 进入主体库**。

---

## 🚨 全局铁律

### 1. **中文 prompt 强制**

所有节点的 `prompt` / `description` 字段**必须用中文**写。白名单只允许以下英文：
- 镜头术语缩写：`shotSize / cameraAngle` 等无法翻译的术语 — 但应优先翻译成"特写 / 中景 / 仰角"等
- 比例：`16:9 / 9:16 / 21:9 / 1:1`（数字）
- 风格 modifier：`cinematic / wuxia / ink-wash / steadicam` 等行业通用词（可中英混写如"ink-wash 水墨风"）
- Negative 关键词：可以 `不要换脸 / no face swap` 双语

**禁止**整段英文 prompt（如 "a young man with sword in moonlight..."）— 中文模型对中文 prompt 表现更好（豆包/即梦/可灵都是国产）。

### 2. **节点字段严格对照（不要乱塞字段）**

`canvas_add_node` 的 `data_json` **只能用各 kind 实际定义的字段**。塞了不存在的字段会被服务器忽略，导致镜头参数没生效。

**镜头参数（景别/角度/运镜/光线/色调/焦距）= 写进 prompt 文本**，**不是**当字段塞 data_json。

### 3. **节点真实字段速查**

| kind | 必填字段 | 可选字段 |
|---|---|---|
| `image` | `prompt`(中文≥500字)、`imageModel`、`aspectRatio`、`count` | — |
| `characterSheet` | `name`、`description`(中文≥800字 含 5维 identity lock)、`imageModel` | `referenceImage`、`viewCount`(3/6/9)、`subjectType`("character"/"scene"/"prop"/"face")、`autoSpawn`(默认true) |
| `storyboard` | `label`、`style`(中文)、`imageModel` | `mode`("single"/"25-grid"/"4-panel-story") |
| `shotSet` | `description`(中文)、`imageModel` | `shotTypes`(["master","reverse","closeup","ots-a"])、`characterAAxisSide`("left"/"right") |
| `dialogueShot` | `characterAName`、`characterBName`、`sceneDescription`(中文)、`imageModel` | `dialogue`、`shotSet`(8 镜头 ID 数组) |
| `actionShotSet` | `description`(中文)、`imageModel` | `actionType`("fight"/"chase"/"stunt"/"wirework"/"sword")、`pacing`("rapid"/"methodical"/"slow-mo")、`chaosLevel`("steadicam"/"handheld")、`axisRule`("preserve"/"break")、`beat`("setup"/"exchanges"/"reversal"/"resolution") |
| `image2video` | `prompt`(中文≥500字)、`videoModel`、`duration`、`aspectRatio` | `audioRef`、`subjectRefs`(数组) |
| `tts` | `text`(中文)、`audioModel`、`voice` | — |
| `musicGen` | `audioModel`、`duration`(2-10s) | `prompt`(中文)、`timingPrompts`([{from,to,prompt}]) |
| `videoConcat` | `videoOrder`(数组) | `crossfadeSeconds`、`reencode`、`bgmUrl`、`bgmVolume`、`cutPattern`("standard"/"rapid-cut"/"j-cut"/"l-cut"/"montage") |

### 4. **prompt 工业级公式（必背）**

每个 image / image2video 节点的 prompt 必须按以下顺序写**6 段中文**：

```
【主体动作】少年道袍带血污、半跪入殿；持青铜螭龙剑，剑尖滴血
【场景环境】凌晨山顶古寺前，月光从左侧 30° 入射，地面青石板渗水
【光线设计】冷蓝月光为主光（5500K），右侧暖黄烛火做边缘光（3200K）
【镜头语言】特写→中景，35mm 焦距，浅景深，平视微仰
【色调氛围】青冷 + 银白，整体偏暗影调，颗粒感 film-grain-light
【运镜节奏】固定（首帧不动）→ 1s 后慢速推进；3 秒镜头第 0 帧

Identity Lock：保持 Phase 2 角色 Bible 5 维面部特征
（单眼皮杏仁眼、高挺直鼻、清瘦尖下巴、薄唇、玉白肤色）
+ 5 项标志物（脖颈枷锁道痕、虎口血丝、青铜螭龙剑、灰渍道袍、眼底金光）

Negative：不要现代服饰、不要笑容、不要其他角色、不要文字水印、
不要面部毛发、不要变形面部、不要多余肢体
```

**字符数**：image ≥500，image2video ≥800（视频还要含动作弧 + 时长意图 + Foley 音效描述）。

### 5. **不预跑、不预连**（v14 LibTV 协作铁律）

- ❌ 不调 `canvas_run_node` 主动跑生图/生视频节点
- ❌ 不调 `canvas_connect` 预连下游线
- ✅ 只 add_node + 写好 prompt
- ✅ 让用户点 ▶ 跑节点、挑满意结果、手动拉线到下游

OK 工具：`canvas_segment_script / canvas_run_script_doctor / canvas_optimize_prompt / canvas_compose_contact_sheet / canvas_film_analysis`（这些是分析/工具调用，不烧生成配额）。

---

## ⛔ HARD GATE — 不读完这一节就不要建项目

**`canvas_create_project` 已加运行时硬校验**：缺少 `story_beats / character_bible / shot_breakdown / user_confirmed=True` 任意一项 → 工具返回 `phase_gate_failed`，画布不会建。

### 黑名单（绝对禁止）

- 用户没说"做视频/做漫剧/做短片" → 不要 invoke 这个 skill
- 用户给一句话需求 → 不要立刻 `canvas_create_project`，必须先走 Phase 1-3
- 用户没回复确认 → 不要 `user_confirmed=True`
- Phase 1-3 内容凭空编 → 必须从用户原始需求严格推演
- **直接调"快路径"工具**（`canvas_run_action_shot_set` 等）→ 这些只用于 hermes 内部测试；正常流程必须 `canvas_add_node` + 让用户运行

---

## 🏭 2026 工业级 AI 漫剧 6 阶段流水线

| 阶段 | 工时 | 核心交付 |
|---|---|---|
| 1 Development（开发） | 5-10% | 故事 beats + 角色 Bible + 镜头规划（Phase 1-3）|
| 2 Pre-production（前期） | 15-20% | **角色三视图（主体库）+ 场景四视图（主体库）+ 道具（主体库）**+ 风格锚 |
| 3 Production（生产） | 40-50% | 每镜头首末帧 + 视频片段 |
| 4 Audio（音频） | 15-20% | TTS + 卡点 BGM + Foley |
| 5 Post（后期） | 10-15% | videoConcat + cutPattern + 字幕 |
| 6 Delivery（交付） | 5% | 成片 + 主体库沉淀（跨集复用）|

---

## 🚧 强制 Phase Gates（建项目前必走）

### Phase 1 — 剧本拆解（Story Beats）

**导演视角**：把"需求碎片"翻译成**可拍摄的电影语言**。

```
## 📖 Phase 1 · 剧本拆解
【题材定位】古风武侠 + 玄幻渡劫 + 神龙斗法
【时长定位】60s 单集（漫剧标准） / 5min 短片 / 多集系列
【题材匹配的视觉风格】青冷色调 + 高反差光比 + 长镜头叙事
【目标观众】女频 / 男频 / 全年龄
【爽点节奏】（漫剧黄金 3 秒 + P50 爽点前置 45s 内）
【Beat 1 - 0-3s 黄金钩子】白衣少年负伤踉跄入殿，残剑滴血落地（特写→中景）
【Beat 2 - 3-15s 起势】黑衣魔尊登场，黑雾翻涌（俯仰对切）
【Beat 3 - 15-30s 转折】少年眼神坚毅，握紧剑柄（特写→仰角）
【Beat 4 - 30-45s 爆点（P50 必到）】青龙破云吞黑雾（大全景+慢镜）
【Beat 5 - 45-60s 收尾】少年被青龙吞入，黑屏字幕"渡劫开始"
```

每个 beat 必须含：emotional intent / key visual / shotSize / camera move / 时间窗口

### Phase 2 — 角色 Bible（每个出场角色都必填）

**🚨 关键 — Phase 2 还要列**：
- 出场角色清单（≥1）
- 主要场景清单（≥1）— 漫剧场景一致性同样重要
- 关键道具清单（如剑、宝物、信物）

```
### 🤍 白衣少年剑仙（主角）
【面部锁定 - Identity Lock 5 维（Nano Banana 行业标准）】
1. 眼型：单眼皮，杏仁形，眼角微挑
2. 鼻梁：高挺直鼻，鼻翼窄
3. 下颌线：清瘦尖下巴，棱角分明
4. 唇形：薄唇，唇角微抿，下唇略厚
5. 肤色：玉白略冷，鼻尖耳尖透粉
【发型】墨黑长发披散，前额留两缕鬓发，脑后用青玉发簪半束半散
【服饰】白色道袍（暗纹云雷）+ 玄色腰带 + 青铜螭龙剑 + 灰渍下摆
【标志物 ≥5】枷锁道痕 / 虎口血丝 / 螭龙剑 / 灰渍道袍 / 眼底金光
【Negative ≥7】不要现代服饰 / 不要笑容 / 不要其他角色 / 不要文字水印 / 不要面部毛发 / 不要变形面部 / 不要多余肢体

### 📍 主要场景：凌晨山顶古寺
【环境】青石板渗水 / 月光左侧 30° 入射 / 远风穿廊
【光线】冷蓝月光（5500K）+ 暖黄烛火（3200K）边缘光
【色调】青冷 + 银白

### ⚔️ 关键道具：青铜螭龙剑
【外观】青铜剑身 + 螭龙吞口 + 青色丝绦剑穗
【标志】剑尖滴血 / 虎口紧握
```

### Phase 3 — 镜头规划

每个 beat → ≥1 个具体镜头。**14 列表**：# / 时长 / 节奏 / 时段 / 内容 / 景别 / 角度 / 运镜 / 光线 / 色调 / 焦距 / 主角姿态 / SFX / 镜头类型。

| 镜头需求 | 镜头类型 | 用什么 kind |
|---|---|---|
| 单一动作/单一情绪 | 单镜头 | `kind="image"` |
| 同一空间多角度（守 180° 轴线）| 镜头组 4 件套 | `kind="shotSet"` |
| 双人对话 | 8 镜头标准 | `kind="dialogueShot"` |
| 武打/追逐/特技 | 8 大武术机位 | `kind="actionShotSet"` |
| 整片视觉风格锚 | 1 张代表作 | `kind="storyboard"` |

### Phase 4 Gate — 用户确认

把 Phase 1-3 全文 dump，必须问：

> 以上是剧本拆解 + 角色 Bible + 镜头规划。**确认无误我开始搭画布**？或者先调整哪一段？

**等用户明确确认**才能进 Phase 5。

---

## 🔑 工具清单（v14 真实工具名）

> ⚠️ MCP 工具名：`canvas_*`（不是 `canvas_op_*`）

### 画布编排（最常用）

| 工具 | 用途 |
|---|---|
| `canvas_create_project(name, story_beats, character_bible, shot_breakdown, user_confirmed)` | 建项目（4 字段缺一不可）|
| `canvas_add_node(project_id, kind, data_json, position_x?, position_y?)` | 加节点 |
| `canvas_connect(project_id, src, src_handle, tgt, tgt_handle)` | 连边 |
| `canvas_update_node_data(project_id, node_id, patch_json)` | 改节点参数 |
| `canvas_get_state(project_id)` | 拿当前节点 + 边（QC 用）|

### 主体库（v8 跨画布资产 — **优先复用**）

| 工具 | 用途 |
|---|---|
| `canvas_subject_list(type_filter)` | 列主体（`character`/`scene`/`prop`/空=全部）|
| `canvas_subject_load(subject_id)` | 读单个主体 |
| `canvas_subject_save(name, subject_type, cover_image_url, views, ...)` | 存主体（用户确认满意后）|

### v13 — 角色一致性 + 视频反推 + 抠图扩图

| 工具 | 用途 |
|---|---|
| `canvas_compose_contact_sheet(image_urls, cols?)` | Pose Sheet 拼大图 |
| `canvas_optimize_prompt(prompt, context?)` | ⭐ 一键 prompt 扩写 |
| `canvas_film_analysis(video_url)` | 🎬 视频反推分镜 |

### 编导级（v10）

| 工具 | 用途 |
|---|---|
| `canvas_save_director_bible(project_id, look_profile, audio_bible)` | 项目级色彩+声音档案 |
| `canvas_run_script_doctor(scenes, user_intent?)` | 6 维评分剧本医生 |
| `canvas_run_music_gen(prompt, duration, model, timing_prompts?)` | 文生音效/BGM |

### 节点 kind 速查

| kind | 用途 | 跑完后行为 |
|---|---|---|
| `image` | 通用文生图（**hero 主图、首末帧、风格参考**都用它）| 显示生成图，选中后顶部 ImageMagicToolbar 浮出 |
| `characterSheet` | **角色三视图节点**（LibTV 模式 2）— 跑完 spawn N 视图子节点 + hero 显示在父节点 | 父节点显示 hero 参考图 + spawn N 子图 |
| `storyboard` | 整片风格锚（25 宫格 / 4 联画 / 单图风格代表）| 显示分镜 |
| `shotSet` | 同场景镜头组（master+OTS+特写+反打）— 跑完 spawn 4-8 子节点 | 守 180° 轴线 |
| `dialogueShot` | 双人对话 8 镜头标准 — 跑完 spawn 8 子节点 | A 在画面左 / B 在右严守 |
| `actionShotSet` | 动作戏 8 大武术机位 — 跑完 spawn 8 子节点 | 基于 studiobinder fight 教程 |
| `image2video` | 图生视频（首末帧 + subjectRefs）| 显示视频 |
| `audio2video` | 音频生视频（口型同步）| 显示视频 |
| `tts` | 文本转语音 | 显示音频 |
| `musicGen` | 文生音效 / BGM（单段或卡点）| 显示音频 |
| `videoConcat` | 视频拼接（含 cutPattern）| 显示拼接视频 |
| `videoTrim` / `videoExtend` | 视频剪辑/续接 | 显示视频 |
| `inpaint` / `upscale` | 局部修改 / 高清化 | 显示图 |
| `subtitleRemoval` | 视频去字幕 | 显示视频 |
| `comicSplit` | 漫画拆格 | 显示拆格图 |
| `text` | 文本节点 | 文本块 |
| `preview` | 任意上游输出预览 | 预览块 |
| `scriptGen` | 故事脚本生成 | 输出分场列表 |

---

## 🎬 v14 工业级搭画布流程（Phase 5）

> **核心铁律 — Hermes 只 add_node + 写好 prompt，不主动 run、不预连下游线**：让用户掌控生成时机 + 挑满意结果 + 再连线（LibTV "先跑 → 后挑 → 再连" 工作流）。

### Step 1 — 建项目

```python
canvas_create_project(
  name="渡劫护龙 - 玄幻武侠 60s",
  story_beats="<Phase 1 全文>",
  character_bible="<Phase 2 全文>",
  shot_breakdown="<Phase 3 镜头表全文>",
  user_confirmed=True
)
# → project_id
```

### Step 2 — 编导档案（lookProfile + audioBible）

整片视觉/听觉锚点，所有节点 prompt 自动追加。

```python
canvas_save_director_bible(
  project_id=pid,
  look_profile={
    "name": "宋代玄幻青冷调",
    "colorTemperature": "very-cool",
    "dominantTones": "青碧主色 + 银白月光 + 偶现金边劫光",
    "contrast": "high",
    "keyLighting": "low-key",
    "filmGrain": "film-grain-light",
    "notes": "参考《刺客信条·影》"
  },
  audio_bible={
    "themeMusicStyle": "古风国风弦乐 + 笛箫，悲悯隐忍",
    "characterMotif": "主角出现时单声笛颤",
    "ambientBaseline": "凌晨山顶古寺：远风穿廊 + 雨后滴水",
    "foleyStyle": "金属铿锵 + 衣袂破裂 + 雪地轻踏"
  }
)
```

### Step 3 — Pre-production：建素材库（人物 / 场景 / 道具）

**🚨 关键步骤 — 这是漫剧第一道质量关。素材必须先做，**才能在镜头里复用。

#### 3a — 角色（每个出场角色一个 characterSheet 节点）

`characterSheet` 是 LibTV 4 模式之一，专门为角色一致性设计。**Hermes 只创建节点，不主动 run**。用户在 UI 上：
1. 点 ▶ 跑节点（执行器 sequential 生成 + Identity Lock + 自动 spawn N 个独立 image 子节点）
2. 父节点显示 hero 大图，子节点是 N 张多角度
3. 用户挑满意的留下，删/重跑不满意的
4. 用户点节点底部「🎭 存为主体」→ 入主体库（跨集复用）

```python
# 先去主体库找现成角色（跨集复用）
existing = canvas_subject_list(type_filter="character")
# 命中 → canvas_subject_load 拿 views URL，
# 然后 canvas_add_node(kind="characterSheet", data 含 status=done + outputs.views=[...])
# 跳过下面的生成

# 没现成的 → 加 characterSheet 节点（不预跑）
hero_node = canvas_add_node(
  project_id=pid,
  kind="characterSheet",
  data_json=json.dumps({
    "name": "白衣少年剑仙",
    "description": "<Phase 2 角色 Bible 全文 ≥800 字符 — 含 5 维 identity lock + ≥7 项 negative>",
    "imageModel": "doubao-seedream-5.0",
    "viewCount": 6,  # 行业 sweet spot
    "subjectType": "character"
  }),
  position_x=100, position_y=100
)
# ⛔ 不主动跑！让用户点 ▶ 跑节点（用户掌控配额）
```

#### 3b — 场景（每个主要场景一个 characterSheet 节点）

```python
scene_temple = canvas_add_node(
  project_id=pid,
  kind="characterSheet",
  data_json=json.dumps({
    "name": "凌晨山顶古寺",
    "description": "<Phase 2 场景全文：环境 + 光线 + 色调>",
    "imageModel": "doubao-seedream-5.0",
    "viewCount": 6,  # 前/左/右/后/俯视/细节
    "subjectType": "scene"
  }),
  position_x=100, position_y=400
)
```

#### 3c — 关键道具

```python
prop_sword = canvas_add_node(
  project_id=pid,
  kind="characterSheet",
  data_json=json.dumps({
    "name": "青铜螭龙剑",
    "description": "<Phase 2 道具全文>",
    "imageModel": "doubao-seedream-5.0",
    "viewCount": 4,
    "subjectType": "prop"
  }),
  position_x=100, position_y=700
)
```

#### 3d — 风格锚（storyboard 节点）

整片视觉风格的"最高法"。1 张代表性镜头作为后续所有节点的风格参考。

```python
style_anchor = canvas_add_node(
  project_id=pid,
  kind="storyboard",
  data_json=json.dumps({
    "label": "整片风格锚",
    "style": "<整片风格描述：电影感写实 + 宋代玄幻青冷 + 高反差光比，参考《刺客信条·影》>",
    "imageModel": "doubao-seedream-5.0",
    "mode": "single"
  }),
  position_x=400, position_y=100
)
```

### Step 4 — 镜头规划（每个镜头一个节点）

**🚨 Hermes 只 add_node + 写好 prompt，不预连下游线**。让用户先跑素材 + 挑满意 + 手动连线。

#### 简单单镜头：`kind="image"`

```python
shot1_first = canvas_add_node(
  project_id=pid,
  kind="image",
  data_json=json.dumps({
    "prompt": """【主体动作】白衣少年剑仙踉跄入殿，半跪在地，残剑滴血；
【场景环境】凌晨山顶古寺前，月光从左侧 30° 入射，地面青石板渗水；
【光线设计】冷蓝月光为主光（5500K），右侧暖黄烛火做边缘光（3200K）；
【镜头语言】特写→中景，35mm 焦距，浅景深，平视微仰；
【色调氛围】青冷 + 银白，整体偏暗影调，电影感 ink-wash 水墨风；
【运镜节奏】固定（首帧不动），3 秒镜头的第 0 帧；

Identity Lock：保持白衣少年剑仙的 5 维面部特征（单眼皮杏仁眼、高挺直鼻、清瘦尖下巴、薄唇、玉白肤色）+ 5 项标志物（脖颈枷锁道痕、虎口血丝、青铜螭龙剑、灰渍道袍、眼底金光）；

Negative：不要现代服饰、不要笑容、不要其他角色、不要文字水印、不要面部毛发、不要变形面部、不要多余肢体""",
    "imageModel": "doubao-seedream-5.0",
    "aspectRatio": "16:9",
    "count": 1
  }),
  position_x=700, position_y=50
)
# ⛔ 不预连线！让用户先跑素材库 → 挑满意 → 拉线到 shot1_first.reference
```

#### 同场景镜头组：`kind="shotSet"`

```python
shot1_set = canvas_add_node(
  project_id=pid,
  kind="shotSet",
  data_json=json.dumps({
    "description": "<场景描述 + 双方关系 + 上下文>",
    "shotTypes": ["master", "reverse", "closeup", "ots-a"],
    "characterAAxisSide": "left",
    "imageModel": "doubao-seedream-5.0"
  }),
  position_x=700, position_y=300
)
```

#### 双人对话：`kind="dialogueShot"`

```python
dialogue1 = canvas_add_node(
  project_id=pid,
  kind="dialogueShot",
  data_json=json.dumps({
    "characterAName": "白衣少年剑仙",
    "characterBName": "黑衣魔尊",
    "dialogue": "<对白节奏参考>",
    "sceneDescription": "<场景描述>",
    "shotSet": ["establishing", "two-shot", "ots-a-to-b", "ots-b-to-a", "close-a", "close-b", "reaction-a", "reaction-b"],
    "imageModel": "doubao-seedream-5.0"
  }),
  position_x=700, position_y=600
)
```

#### 动作戏：`kind="actionShotSet"`

```python
action1 = canvas_add_node(
  project_id=pid,
  kind="actionShotSet",
  data_json=json.dumps({
    "description": "<场景描述>",
    "actionType": "fight",  # fight/chase/stunt/wirework/sword
    "pacing": "rapid",  # rapid/methodical/slow-mo
    "chaosLevel": "steadicam",  # steadicam/handheld
    "axisRule": "preserve",  # preserve/break
    "imageModel": "doubao-seedream-5.0"
  }),
  position_x=700, position_y=900
)
```

### Step 5 — 视频节点（image2video）

```python
shot1_video = canvas_add_node(
  project_id=pid,
  kind="image2video",
  data_json=json.dumps({
    "prompt": "<≥500 字符视频 prompt：动作弧 + 运镜 + 时长意图 + identity lock>",
    "duration": 3,
    "videoModel": "doubao-seedance-2-0-260128",
    "aspectRatio": "16:9"
  }),
  position_x=1000, position_y=50
)
# ⛔ 不预连线！等用户跑完 shot1_first / shot1_last 满意，再手动拉线：
#   shot1_first.images → shot1_video.image       （首帧）
#   shot1_last.images  → shot1_video.tailFrame   （末帧）
#   contact_sheet      → shot1_video.subjectRefs （锁角色）
```

### Step 6 — 音频（musicGen 卡点 BGM）

```python
music = canvas_add_node(
  project_id=pid,
  kind="musicGen",
  data_json=json.dumps({
    "duration": 10,
    "audioModel": "audio1.0",
    "timingPrompts": [
      {"from": 0, "to": 3, "prompt": "笛箫单声，清冷悲悯（钩子前 3s）"},
      {"from": 3, "to": 15, "prompt": "弦乐渐起，紧张感累积"},
      {"from": 15, "to": 30, "prompt": "短促弦乐切分"},
      {"from": 30, "to": 45, "prompt": "钟鼓齐鸣高潮 + 龙吟（爆点）"},
      {"from": 45, "to": 60, "prompt": "余音渐弱，留白"}
    ]
  }),
  position_x=400, position_y=1200
)
```

### Step 7 — 拼接（videoConcat + cutPattern）

| 题材 | cutPattern | 理由 |
|---|---|---|
| 武打/追逐 | rapid-cut | 短切 1-2s |
| 文戏/对话 | j-cut / l-cut | 音视频错位 |
| 蒙太奇/时间流逝 | montage | 强 crossfade + BGM 上调 |
| 普通叙事 | standard | 硬切 + 0.3s 淡化 |

```python
concat = canvas_add_node(
  project_id=pid,
  kind="videoConcat",
  data_json=json.dumps({
    "videoOrder": [shot1_video["nodeId"], shot2_video["nodeId"]],
    "crossfadeSeconds": 0.3,
    "reencode": True,
    "bgmVolume": 0.35,
    "cutPattern": "standard"
  }),
  position_x=1500, position_y=300
)
# ⛔ 不预连！用户先跑视频，再连：
#   shot1_video.videoUrl → concat.videos_multi
#   music.audioUrl → concat.bgmUrl
```

---

## 🔥 角色一致性 4 件套（漫剧不崩脸的关键）

行业 60% → 90% 一致性提升：

```
1. Sequential 生成（先 hero 再用 hero 当 ref）
   ↓ characterSheet 节点执行器自动做
2. Identity Lock Prompt（5 维面部锁定：眼/鼻/下颌/唇/肤）
   ↓ characterSheet 节点 + Phase 2 角色 Bible
3. Contact Sheet 拼大图（多视图 → 1 张拼图当 ref）
   ↓ canvas_compose_contact_sheet
4. subjectRefs 端口（image2video 接 contact sheet）
   ↓ canvas_connect ... "subjectRefs"
```

漏掉任何一步 — 角色都会漂。

---

## 🎵 三层音频设计

```
Layer 1 主题音乐（BGM）  ← canvas_run_music_gen
Layer 2 环境氛围      ← audioBible.ambientBaseline → image2video.audioRef
Layer 3 Foley 音效    ← image2video prompt 内置描述
```

---

## 🚀 必用魔法工具

| 时机 | 工具 |
|---|---|
| 用户给参考视频要复刻镜头 | `canvas_film_analysis` |
| scriptGen 跑完 | `canvas_run_script_doctor`（6 维评分必调）|
| prompt < 100 字符 / 不够工业级 | `canvas_optimize_prompt` ⭐ |
| 16:9 → 9:16 抖音版 / 21:9 影院 | `canvas_outpaint` |
| 角色 PNG → 新背景 | `canvas_cutout` |

---

## ⚠️ 漫剧不崩 14 条红线

1. ❌ characterSheet viewCount=3（一致性差）— ✅ ≥6
2. ❌ 跑完不拼 contact sheet — ✅ 立刻拼
3. ❌ image2video 不接 subjectRefs — ✅ 必接
4. ❌ image2video 不连双关键帧 — ✅ 必连首+末
5. ❌ 角色 prompt 没 5 维 identity lock — ✅ 必填
6. ❌ negative <7 — ✅ ≥7 项
7. ❌ image prompt <500 字符 — ✅ ≥500
8. ❌ 用 blob: URL 喂 image2video — ✅ 必须 https/asset/data:
9. ❌ 60s 漫剧爽点放最后 — ✅ P50 < 45s
10. ❌ 单镜头 >8s — ✅ 漫剧 4-6s 最佳
11. ❌ 跨场景换光线方向 — ✅ lookProfile 锁
12. ❌ scriptGen 跑完不调 script_doctor — ✅ 必调
13. ❌ 不存主体库 — ✅ 跨集必存
14. ❌ user_confirmed=True 用户没确认就传 — ✅ 等明说

---

## 📐 模型速查（doubao-seedance-2-0 推荐）

| 模型 | 时长 | 首尾帧 | 原生音频 | 多模态参考 | 推荐 |
|---|---|---|---|---|---|
| **doubao-seedance-2-0** ⭐ | 4-15s | ✅ | ✅ | ✅ 12 文件 | **漫剧首选** |
| veo3.1-fast | 5/8s | ✅ | ✅ | 3 张 | 国际质感 |
| veo3.1 | 5/8s | ✅ | ✅ | 3 张 | 国际最强（贵）|
| sora-2 | 5/10s | — | ✅ | — | 文艺片 |
| kling-2.6 | 5/10s | ⚠️ | ✅ | — | 长镜头 |

---

## 🎯 Phase 5 完成后告诉用户什么

```
画布搭好了，N 个节点：
- {char_count} 个 characterSheet（角色/场景/道具，跑完会自动 spawn N 视图子节点）
- 1 个 storyboard（整片风格锚）
- {shot_count} 个镜头节点（image / shotSet / dialogueShot / actionShotSet）
- {shot_count} 个 image2video 视频节点
- 1 个 musicGen 卡点 BGM
- 1 个 videoConcat 拼接节点

⚠️ 我没有连下游线，你来主导：

推荐运行顺序：
1. ▶ 先跑左侧素材（角色/场景/道具）— 看效果，不满意改 prompt 重跑
2. 满意的素材右下角点「🎭 存为主体」→ 进主体库（跨集复用）
3. ▶ 跑风格锚 storyboard → 用作每镜头 image 的 styleRef
4. ▶ 跑每镜头 image（首末帧）— 满意了拉线到 image2video
5. ▶ 跑每个 image2video（最久 1-3 分钟）
6. ▶ 跑 musicGen 卡点 BGM
7. ▶ 拉线到 videoConcat 拼成成片

预计成本：约 ¥{X}（按诗云 default×1.15 计费分组）

不满意就重跑：
- 单镜头不对 → 选中节点点 ▶
- 角色脸漂 → 检查是否连了 subjectRefs，没连接上 contact sheet
- 节奏不对 → videoConcat 切换 cutPattern
- 整片色调不对 → canvas_save_director_bible 改 lookProfile
```

---

End of SKILL v14 main file.
