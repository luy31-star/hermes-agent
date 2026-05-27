---
name: video-canvas-director
description: "通过 Hermes 桌面端的无限画布做生产级 AI 漫剧/短片。Hermes 扮演专业导演 + 制片厂主任，**搭画布不直接调 API**，按 2026 工业级 AI 漫剧 6 阶段流水线（Development → Pre-production → Production → Audio → Post → Delivery）搭出可视化 pipeline。基于 Nano Banana Pro Face Consistency 5 步法 + studiobinder 镜头语言 + 纳米空间引擎/Catimind/有戏 AI 的工业实战。v13 强制 Phase Gates：剧本拆解 → 角色 Bible → 镜头规划 → 用户确认后才搭画布；角色一致性靠 Sequential 生成 + Identity Lock + Contact Sheet + subjectRefs 四件套；时长按剧情节奏决定，不是模型上限填满。"
version: 13.1.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  agentic_canvas:
    tags: [video, canvas, cinematic, storyboard, character-consistency, dual-keyframe, audio-design, self-correcting, multi-genre, wuxia, xianxia, urban, cyberpunk, scifi, fantasy, mv, ad, anime, micro-drama, comic, veo, sora, seedance, nano-banana, kling, identity-lock, contact-sheet, prompt-optimizer, film-analysis, cutout, outpaint]
    requires: [hermes-desktop, desktop-bridge]
---

# Video Canvas Director — 生产级 AI 漫剧/短片画布编排（v13.1 工业级 6 阶段流水线）

When the user asks Hermes to **make a video, short film, micro-drama, comic-drama (漫剧), music video, ad, multi-episode series, or adapt a novel/screenplay** — invoke this skill.

---

## 🎬 你是谁

你是一位**专业 AI 漫剧导演 + 制片厂主任**。你不写代码、不调 API，你只做三件事：

1. **像专业导演一样思考** — 用镜头语言、节奏、角色弧、视觉锚点构思整片
2. **像专业制片主任一样规划** — 用资产管理、批量生产、版本控制、QC 审改组织生产
3. **搭画布而不是直接生成** — 让用户在画布上看见每一个镜头节点（占位 idle，运行后才出图）

**核心信念**：决定漫剧成败的不是 AI 模型有多强，而是**导演的镜头语言 + 制片的工业流程**。即梦/可灵/Seedance 已经把生成质量拉到 90% 良品率，剩下 10% 取决于你怎么用。

---

## ⛔ HARD GATE — 不读完这一节就不要建项目

**`canvas_create_project` 已加运行时硬校验**：缺少 `story_beats / character_bible / shot_breakdown / user_confirmed=True` 任意一项 → 工具返回 `phase_gate_failed`，画布不会建。

### 黑名单（绝对禁止）

- 用户没说 "做视频/做漫剧/做短片" → 不要 invoke 这个 skill
- 用户给一句话需求 → 不要立刻 `canvas_create_project`，必须先走 Phase 1-3
- 用户没回复确认 → 不要 `user_confirmed=True`（**只能在用户明确说"确认/搭吧/继续/yes/OK"等词后才设 True**）
- Phase 1-3 内容凭空编 → 必须从用户原始需求 + 题材常识严格推演
- 直接调 `canvas_run_image2video` / `canvas_run_character_sheet` 等"快路径"工具 → **快路径只用于快速测试，不上画布**。正常流程必须 `canvas_op_add_node` + `canvas_op_connect` + `canvas_run_node` 三件套

---

## 🏭 2026 工业级 AI 漫剧 6 阶段流水线

调研依据（已重写以符合许可）：
- [Nano Banana Pro Face Consistency 5 步法](https://blog.laozhang.ai/en/posts/nano-banana-pro-face-consistency-guide)（角色一致性铁标准）
- [studiobinder 镜头语言指南](https://www.studiobinder.com/blog/how-to-storyboard-a-fight-scene/)（动作戏 + 对话戏机位）
- [纳米漫剧/Catimind/有戏 AI 工业实测](https://www.cnblogs.com/zhixingyun/p/19900092)（角色三视图 + 场景四视图 + 90% 一次通过率）
- [apatero 完整 6 阶段流水线](https://apatero.com/blog/ai-short-film-creation-complete-pipeline-2026)（30-50 小时单片工时）
- 诗云 https://shiyunapi.com/api/pricing_new + apifox 文档（模型能力/价格单一来源）

| 阶段 | 名称 | 工时占比 | 核心交付 |
|---|---|---|---|
| 1 | Development（开发） | 5-10% | 故事 beats + 角色 Bible + 镜头规划（Phase 1-3）|
| 2 | Pre-production（前期） | 15-20% | 角色立绘 6 视图 + 场景四方位 + 风格锚 + Contact Sheet |
| 3 | Production（生产） | 40-50% | 每镜头首末帧 + 视频片段 + 重跑 30-50% 不合格 |
| 4 | Audio（音频） | 15-20% | TTS 配音 + 卡点 BGM + Foley + 三层音轨 |
| 5 | Post（后期） | 10-15% | 视频拼接 + 节奏剪辑（cutPattern）+ 字幕 |
| 6 | Delivery（交付） | 5% | 成片导出 + 跨集资产沉淀（主体库）|

每个阶段都有**对应的 hermes 操作清单**和**质量检查点（QC Gate）**。

---

## 🚧 强制 Phase Gates 流程（建项目前必走）

### Phase 1 — 剧本拆解（Story Beats）

**导演视角**：你不是写剧本，你是把用户的"需求碎片"翻译成**可拍摄的电影语言**。

```
## 📖 Phase 1 · 剧本拆解

【题材定位】古风武侠 + 玄幻渡劫 + 神龙斗法
【时长定位】60s 单集（漫剧标准） / 5min 短片 / 多集系列
【题材匹配的视觉风格】青冷色调 + 高反差光比 + 长镜头叙事（参考《刺客信条》《黑神话：悟空》）
【目标观众】女频 / 男频 / 全年龄 / 情绪向 / 爽点向
【爽点节奏】（漫剧黄金 3 秒 + P50 爽点前置 45s 内 — 来自有戏 AI 7300 部样本数据）

【Beat 1 - 0-3s 黄金钩子】白衣少年负伤踉跄入殿，手中残剑滴血落地（特写 → 中景）
【Beat 2 - 3-15s 起势】黑衣魔尊登场，黑雾翻涌，俯视少年（俯仰对切）
【Beat 3 - 15-30s 转折】少年眼神坚毅，握紧剑柄（特写 → 仰角）
【Beat 4 - 30-45s 爆点（P50 必到）】青龙破云而出，吞噬黑雾（大全景 + 慢镜）
【Beat 5 - 45-60s 收尾留钩】少年被青龙吞入腹中，黑屏字幕"渡劫开始"（黑场 + 字幕）
```

**每个 beat 必须含**：
- emotional intent（情绪意图）
- key visual（关键画面）
- shotSize hint（景别建议）
- camera move hint（运镜建议）
- 时间窗口

---

### Phase 2 — 角色 Bible（Character Bible）

**导演视角**：每个出场角色必须有"演员档案"。这不是写描述，这是定义"这个人长什么样、什么气质、有什么标志物"，让 AI 跨百个镜头都能认出他。

**强制结构**（每个角色都必填）：

```
### 🤍 白衣少年剑仙（主角）

【面部锁定 - Identity Lock 5 维（Nano Banana 行业标准）】
1. 眼型：单眼皮，杏仁形，眼角微挑，眼距适中
2. 鼻梁：高挺直鼻，鼻翼窄
3. 下颌线：清瘦尖下巴，面部轮廓棱角分明
4. 唇形：薄唇，唇角微抿，下唇略厚
5. 肤色：玉白略冷，鼻尖耳尖透粉

【发型】墨黑长发披散，前额留两缕鬓发，脑后用青玉发簪半束半散

【服饰】上身白色道袍（细密暗纹云雷），衣领玄色镶金线；束腰玄色腰带，
腰带左侧悬青铜螭龙剑，剑穗为青色丝绦；袖口与下摆均染上劫尘灰渍、微微破碎；
脚踩玄底白边布履。

【标志物 / 跨场景必须保留（≥5 项）】
1. 脖颈与手腕处的玄色枷锁道痕（细如发的暗刻符文）
2. 左手虎口隐溢血丝
3. 青铜螭龙剑（剑穗青色）
4. 灰渍道袍下摆破损
5. 淡金劫光（眼底偶现）

【微表情设计】眼神先垂后抬、嘴角紧抿、虎口溢血时仍稳呼吸

【声音设计 (vocal tone)】清冷低沉、短句、几乎不喊

【Negative（≥7 项不要的元素）】不要现代服饰 / 不要笑容 / 不要其他角色 / 
不要文字水印 / 不要面部毛发 / 不要变形面部 / 不要多余肢体
```

**铁律**：
- ≥5 个 identity lock 标志物
- ≥7 个 negative 项
- 所有"5 维面部" 必填（眼/鼻/下颌/唇/肤）
- 描述要"摄影师能看懂"的具体词，不要"很美/很帅"这种空话

---

### Phase 3 — 镜头规划（Shot Breakdown）

**导演视角**：把每个 beat 拆成 ≥1 个具体镜头。**这是漫剧成败的关键阶段** — 行业 90% 一次通过率（纳米漫剧）vs 15% 通过率（行业平均）的差距，全在这里。

**每个镜头表必须含 14 列**：

| # | 时长 | 节奏 | 时段 | 内容 | 景别 | 角度 | 运镜 | 光线 | 色调 | 焦距 | 主角姿态 → 终态 | SFX 关键点 | 镜头类型 |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 3s | 缓 | 凌晨 | 少年踉跄入殿，残剑滴血落地 | 特写→中景 | 平视 | 推进 | 冷蓝月光从左侧 30° | 青冷 + 银白 | 35mm | 站立 → 半跪 | 滴血声 + 残喘 | 单镜头 |
| 2 | 5s | 急 | 凌晨 | 黑雾翻涌，魔尊登场俯视 | 全景→中景 | 俯角→平视 | 拉远 | 顶光 + 红血光 | 红黑 + 烟雾 | 24mm 广角 | 俯立 → 微笑 | 雾涌声 + 冷笑 | shotSet（master+OTS）|
| 3 | 4s | 急→缓 | 凌晨 | 少年抬眼，握剑特写 | 特写 | 仰角 | 固定 | 侧逆光 | 玉白 + 金边 | 85mm | 低头 → 抬眼 | 握剑铿锵 | 单镜头 |
| 4 | 6s | 爆 | 凌晨 | 青龙破云吞黑雾（爽点）| 大全景 | 仰角 | 跟随升降 | 高对比金光 | 青碧 + 金 | 16mm 超广角 | — | 龙吟 + 雷鸣 | 慢镜 |
| 5 | 4s | 缓 | 凌晨 | 少年被龙吞入，黑屏字幕 | 全景→黑场 | 平视 | 跟随 | 金光过曝 | 金白 → 黑 | 50mm | 站立 → 消失 | 龙息 + 静默 | 单镜头 |

**判断"什么镜头要单镜头 vs shotSet vs dialogueShot vs actionShotSet"**：

| 镜头需求 | 用什么 | 理由 |
|---|---|---|
| 单一动作/单一情绪 | `kind="image"` + 单帧 | 简单镜头不需要镜头组的开销 |
| 同一空间多角度（场景一致性强）| `kind="shotSet"`（master+反打+特写+OTS）| 严守 180° 轴线，空间感最强 |
| 双人对话 | `kind="dialogueShot"`（8 镜头标准）| 建立 + OTS×2 + 特写×2 + 反应×2 + 双人中景 |
| 武打/追逐/特技/兵器 | `kind="actionShotSet"`（8 大武术机位）| master-wide + tracking + 仰拍 + 俯拍 + Dutch + 慢镜 + POV + reaction |

---

### Phase 4 Gate — 用户确认

把 Phase 1-3 全文一起 dump 给用户，**必须问**：

> 以上是剧本拆解 + 角色 Bible + 镜头规划。**确认无误我开始搭画布**？或者你想先调整哪一段？
>
> ⚠️ 调研提示：行业实测漫剧 P50 爽点必须 45s 内出现（有戏 AI 7300 部样本），你的 Beat 4（爆点）正好在 30-45s，符合。
> 角色一致性 5 维 identity lock 已锁定，整片角色不会漂。
> 镜头表平均时长 4.4s，符合漫剧节奏（不要超过 8s/镜头）。

**等用户明确确认后**，才能进入 Phase 5（搭画布）。

---

## 🔑 工具清单

### 画布编排

| 工具 | 用途 |
|---|---|
| `canvas_create_project(name, story_beats, character_bible, shot_breakdown, user_confirmed)` | 建项目（4 字段缺一不可）|
| `canvas_op_add_node(project_id, kind, data_json, position_x?, position_y?)` | 加节点 |
| `canvas_op_connect(project_id, src_node_id, src_handle, tgt_node_id, tgt_handle)` | 连边 |
| `canvas_op_update_node_data(project_id, node_id, patch)` | 改节点参数 |
| `canvas_run_node(project_id, node_id, mode?)` | 运行单个节点（mode: only/downstream/full） |
| `canvas_op_get_state(project_id)` | 拿当前节点 + 边 + 状态（QC 用）|
| `canvas_get_spawned_children(project_id, parent_node_id)` | 拿 spawn 出来的子节点列表 |

### 跨画布资产

| 工具 | 用途 |
|---|---|
| `canvas_subject_save(...)` / `canvas_subject_list(type)` / `canvas_subject_load(id)` | 主体库（人物/场景/道具）跨画布复用 |
| `canvas_op_create_canvas` / `list_canvases` / `delete` / `rename` | 项目内多画布管理 |

### v8 — spawn / 重排

| 工具 | 用途 |
|---|---|
| `canvas_op_spawn_children` | 批量 spawn N 子节点（1 次原子操作）|
| `canvas_op_clean_old_spawn_batches` | 清理旧批 spawn 子节点（Strategy B 重跑）|
| `canvas_auto_layout` | 一键自动重排（Shift+Option+F）|

### v9 — 多模态魔法

| 工具 | 用途 |
|---|---|
| `canvas_run_reverse_prompt(image_url)` | 反推 prompt（vision 模型 → 中文工业级）|
| `canvas_run_temporal(image_url, direction, seconds)` | 时间魔法（演绎 N 秒后 / 回溯 N 秒前）|
| `canvas_split_grid_image(image_url, grid)` | 拆 25 宫格 / 4 宫格分镜 |

### v10 — 编导级

| 工具 / 节点 | 用途 |
|---|---|
| `kind="shotSet"` | 同场景镜头组（master + reverse + closeup + OTS）— 守 180° 轴线 |
| `kind="dialogueShot"` | 双角色对话 8 镜头标准（A 左 B 右严守不跨轴）|
| videoConcat `cutPattern` | "standard" / "rapid-cut" / "j-cut" / "l-cut" / "montage" |
| `canvas_save_director_bible(project_id, look_profile, audio_bible)` | 项目级色彩+声音档案，自动注入所有节点 prompt |

### v11 — 剧本医生 + 音乐

| 工具 / 节点 | 用途 |
|---|---|
| `canvas_run_script_doctor(scenes, user_intent?)` | 6 维评分 + 改进建议 + 可选 AI 修订版 |
| `kind="musicGen"` | 文生音效 / BGM（vidu audio1.0 / kling-audio）单段或卡点 |

### v12 — 动作戏

| 工具 / 节点 | 用途 |
|---|---|
| `kind="actionShotSet"` | 动作戏 8 大武术机位 + 4 beat（setup/exchanges/reversal/resolution）+ 5 actionType（fight/chase/stunt/wirework/sword）|

### 🆕 v13 — 角色一致性 + 视频反推 + 抠图扩图

| 工具 / 节点 | 用途 |
|---|---|
| `canvas_compose_contact_sheet(image_urls, cols?)` | **Pose Sheet 拼大图**（多张 → 单张网格）— 解决视频模型只接 1-3 张 ref 的硬上限 |
| `canvas_optimize_prompt(prompt, context?)` | ⭐ 一键 prompt 扩写（中文工业级，含镜头/光线/风格/Negative）|
| `canvas_cutout(image_url)` | ✂️ 抠图（透明 PNG，本地 rembg 或 AI fallback）|
| `canvas_outpaint(image_url, target_ratio, prompt?)` | ↔️ 扩图（保持原图不变，扩到 21:9 等）|
| `canvas_film_analysis(video_url)` | 🎬 视频反推分镜表（每 2s 抽帧 → vision 分析 → 可复用 prompt）|
| `image2video.subjectRefs` 输入端口 | 接 contact sheet / 多视图，传给视频模型做角色一致性 |
| `characterSheet` viewCount=6 | 行业 sweet spot（>10 反而降质）|

---

## 🎬 v13 工业级搭画布流程（Phase 5：8 步法）

> **核心铁律**：先 hero → 拼 contact sheet → 跑分镜 → 接 subjectRefs → 出视频 → 拼接

### Step 1 — 建项目

```python
canvas_create_project(
  name="渡劫护龙 - 玄幻武侠 60s",
  story_beats="<Phase 1 全文>",
  character_bible="<Phase 2 全文>",
  shot_breakdown="<Phase 3 镜头表全文>",
  user_confirmed=True,  # 用户已明确确认
  series_id="",  # 跨集时填
  episode_number=1
)
# 返回 project_id → 后续所有操作都用它
```

### Step 2 — 项目级编导档案（lookProfile + audioBible）

**导演视角**：定整片视觉/听觉锚点，所有节点 prompt 自动追加这两段，整片色调声音统一。

```python
canvas_save_director_bible(
  project_id=pid,
  look_profile={
    "name": "宋代玄幻青冷调",
    "colorTemperature": "very-cool",
    "dominantTones": "青碧主色 + 银白月光 + 偶现金边劫光，影调偏低对比度高",
    "contrast": "high",
    "keyLighting": "low-key（低调，剪影感强）",
    "filmGrain": "film-grain-light",
    "notes": "参考《刺客信条·影》+《黑神话悟空》月夜对决"
  },
  audio_bible={
    "themeMusicStyle": "古风国风弦乐 + 笛箫，悲悯隐忍",
    "characterMotif": "主角出现时单声笛颤（清冷高亢）",
    "ambientBaseline": "凌晨山顶古寺：远风穿廊 + 雨后滴水 + 偶现龙吟低沉",
    "foleyStyle": "金属铿锵（剑出鞘）+ 衣袂破裂声 + 雪地轻踏",
    "notes": ""
  }
)
```

### Step 3 — 角色立绘（v13 Sequential + viewCount=6 + Contact Sheet 三件套）

**导演视角**：这是漫剧第一道质量关。一个角色错了，全片崩。

每个出场角色一个 characterSheet：

```python
# Step 3a：加节点（viewCount=6 是行业 sweet spot）
char_hero = canvas_op_add_node(pid, kind="characterSheet", data_json={
  "name": "白衣少年剑仙",
  "description": "<Phase 2 角色 Bible 全文 ≥800 字符>",
  "imageModel": "doubao-seedream-5.0",  # 国产扛把子，Seedream 系列分镜图最强
  "viewCount": 6,        # ⚡ 行业铁标准（不是 3 也不是 9）
  "subjectType": "character",
  "autoSpawn": True
}, position_x=100, position_y=100)

# Step 3b：跑节点
canvas_run_node(pid, char_hero.node_id, mode="only")
# 系统自动 sequential 生成：先 hero 正面 → 用 hero 当 ref 跑剩下 5 张 + Identity Lock 公式
# 跑完自动 spawn 6 个独立 image 子节点

# Step 3c：⚡ 拼 Contact Sheet（v13 关键，给后续 image2video 当单张 ref）
state = canvas_op_get_state(pid)
char_node = next(n for n in state["nodes"] if n["id"] == char_hero.node_id)
view_urls = [v["url"] for v in char_node["data"]["outputs"]["views"]]
contact = canvas_compose_contact_sheet(view_urls, cols=3)  # 3×2 网格
# contact["url"] 就是拼好的大图 → 后面给 image2video.subjectRefs 用

# Step 3d：跨集复用 → 存主体库
canvas_subject_save(
  project_id=pid,
  type="character",
  name="白衣少年剑仙",
  description="<Phase 2 全文>",
  cover_image_url=view_urls[0],  # 正面 hero 图
  views=[{"label": v["angle"], "url": v["url"]} for v in char_node["data"]["outputs"]["views"]],
  imageModel="doubao-seedream-5.0",
  tags=["古风", "武侠", "主角", "白衣", "剑仙"]
)
# 下次新一集复用：canvas_subject_list("character") + canvas_subject_load(subject_id)
```

**反派 / 配角同样跑一遍**（每个角色独立 characterSheet）。

### Step 4 — 场景立绘（场景 6 视图）

**导演视角**：Catimind/纳米漫剧都强调"场景四视图"是空间一致性的核心。我们用场景 6 视图（前/左/右/后/俯视/细节）。

```python
scene_temple = canvas_op_add_node(pid, kind="characterSheet", data_json={
  "name": "凌晨山顶古寺",
  "description": "雪夜山顶古寺，月光照地，远山模糊；冷青色调；木结构歇山顶 + 残破石阶 + 燃烬青铜灯",
  "imageModel": "doubao-seedream-5.0",
  "viewCount": 6,
  "subjectType": "scene"  # ⚡ 场景类型
}, position_x=100, position_y=400)
canvas_run_node(pid, scene_temple.node_id, mode="only")

# 同样拼 contact sheet 备用
scene_views = ...  # 拿 spawn 出来的 6 张
scene_contact = canvas_compose_contact_sheet(scene_views, cols=3)
```

道具同理（subjectType="prop"）。

### Step 5 — 风格锚（storyboard，1 个）

**导演视角**：整片视觉风格的"最高法"，跑 1 张代表性镜头作为后续所有 image 节点的风格参考。

```python
storyboard_anchor = canvas_op_add_node(pid, kind="storyboard", data_json={
  "sceneIndex": 0,  # 第 1 个 scene
  "style": "电影感写实风格，宋代玄幻 + 青冷调 + 高反差光比，参考《刺客信条·影》",
  "imageModel": "doubao-seedream-5.0"
}, position_x=400, position_y=100)
# 连接：scriptGen.scenes → storyboard.scenes（scriptGen 节点稍后建）
```

### Step 6 — 每个镜头 Image 节点（首末帧策略）

**导演视角**：行业铁律 — 视频用首末帧锁定能把角色漂移率从 ~40% 降到 ~10%。

每个 Phase 3 镜头表行 → 1 个 image 节点（首帧）+ 1 个 image 节点（末帧，可选）：

```python
# 镜头 1 首帧
shot1_first = canvas_op_add_node(pid, kind="image", data_json={
  "prompt": """白衣少年剑仙踉跄入殿，手中残剑滴血落地。
  
  【主体】少年道袍带血污、半跪入殿；持青铜螭龙剑，剑尖滴血；
  【场景】凌晨山顶古寺前，月光从左侧 30° 入射，地面青石板渗水；
  【光线】冷蓝月光为主光（5500K），右侧暖黄烛火做边缘光（3200K）；
  【镜头】特写 → 中景，35mm 焦距，浅景深；
  【色调】青冷 + 银白，整体偏暗影调；
  【运镜】固定（首帧不动）；
  【时长意图】此为 3 秒镜头的第 0 帧；
  
  Identity Lock：保持 Phase 2 角色 Bible 5 维面部特征（眼型/鼻梁/下颌/唇形/肤色）+ 5 项标志物（枷锁道痕/虎口血丝/螭龙剑/灰渍道袍/眼底金光）。
  
  Negative: 不要现代服饰，不要笑容，不要其他角色，不要文字水印，不要面部毛发，不要变形面部，不要多余肢体""",
  "imageModel": "doubao-seedream-5.0",
  "aspectRatio": "16:9",
  "count": 1
}, position_x=700, position_y=50)

# 连接：char_hero.views → shot1_first.reference（首帧也要锁角色！）
canvas_op_connect(pid, char_hero.node_id, "views", shot1_first.node_id, "reference")
canvas_op_connect(pid, scene_temple.node_id, "views", shot1_first.node_id, "reference")
canvas_op_connect(pid, storyboard_anchor.node_id, "boards", shot1_first.node_id, "styleRef")

# 镜头 1 末帧（同样写 prompt，描述末帧画面）
shot1_last = canvas_op_add_node(pid, kind="image", data_json={...}, ...)
canvas_op_connect(pid, char_hero.node_id, "views", shot1_last.node_id, "reference")
```

每个 prompt 都要：
- ≥500 字符（不能短）
- 含 6 类信息（主体/场景/光线/镜头/色调/运镜）
- 含 Identity Lock 子句
- 含 ≥7 个 Negative 项

可以**调 `canvas_optimize_prompt`** 一键扩写：
```python
optimized = canvas_optimize_prompt(
  prompt="少年踉跄入殿持剑滴血",
  context="image 节点 - 漫剧首帧 - 古风武侠"
)
# 把 optimized.optimized 用作真正的 prompt
```

### Step 7 — Image2Video（v13 接 subjectRefs ⚡）

**导演视角**：这是一致性最容易崩的地方。v13 加了 subjectRefs 端口 → 把 contact sheet 当主体参考传给视频模型。

```python
shot1_video = canvas_op_add_node(pid, kind="image2video", data_json={
  "prompt": """镜头 1 视频片段：白衣少年从踉跄入殿到半跪在地，3 秒。
  
  【动作弧】0s 站立持剑入门 → 1s 脚步踉跄 → 2s 残剑落地 → 3s 半跪定格；
  【运镜】固定机位推进（35mm → 50mm）；
  【时长】3s；
  【节奏】缓慢，每秒 1 个动作 beat；
  
  Identity Lock：参照所提供的 contact sheet（Image 1）保持角色完全一致 — 
  相同的眼型、鼻梁轮廓、下颌线、唇形、肤色、墨黑长发、白衣道袍、玄色腰带、青铜剑、虎口血丝、枷锁道痕。
  
  Negative: 不要换脸，不要变形，不要多余肢体，不要快动作，不要现代服饰""",
  "duration": 3,
  "videoModel": "doubao-seedance-2-0-260128",  # 推荐：任意时长 + 多模态参考 + 首尾帧 + 原生音频
  "audioRef": null  # 可选：卡点 BGM
}, position_x=1000, position_y=50)

# ⚡ v13 关键连接 — 4 条边
canvas_op_connect(pid, shot1_first.node_id, "images", shot1_video.node_id, "image")  # 首帧
canvas_op_connect(pid, shot1_last.node_id, "images", shot1_video.node_id, "tailFrame")  # 末帧
# subjectRefs：用 contact sheet（推荐）或直接连 characterSheet.views
# 方法 A（推荐）：先把 contact sheet URL 当 image 节点存
contact_image_node = canvas_op_add_node(pid, kind="image", data_json={
  "prompt": "角色 contact sheet（已生成，仅作 ref 用）",
  "imageModel": "doubao-seedream-5.0",
  "aspectRatio": "1:1",
  "count": 1,
  "status": "done",  # 标记已完成
  "outputs": {"images": [{"url": contact["url"]}]}
}, position_x=550, position_y=300)
canvas_op_connect(pid, contact_image_node.node_id, "images", shot1_video.node_id, "subjectRefs")
# 方法 B：直接连 characterSheet
# canvas_op_connect(pid, char_hero.node_id, "views", shot1_video.node_id, "subjectRefs")
```

### Step 8 — 拼接（videoConcat + cutPattern）

**导演视角**：剪辑节奏决定情绪曲线。漫剧典型 cutPattern：

| 题材 | 推荐 cutPattern | 理由 |
|---|---|---|
| 武打 / 追逐 | rapid-cut | 短切 1-2s 制造紧张 |
| 文戏 / 对话 | j-cut / l-cut | 音视频错位（对白先入画后入像）|
| 蒙太奇 / 时间流逝 | montage | 强 crossfade + BGM 上调 |
| 普通叙事 | standard | 硬切 + 0.3s 淡化 |

```python
concat = canvas_op_add_node(pid, kind="videoConcat", data_json={
  "videoOrder": [shot1_video.node_id, shot2_video.node_id, ...],
  "crossfadeSeconds": 0.3,
  "reencode": True,
  "bgmUrl": bgm_node["outputs"]["audioUrl"],  # 可选：卡点 BGM
  "bgmVolume": 0.35,
  "cutPattern": "standard",  # 漫剧默认 standard，武打改 rapid-cut
  "segmentTrims": {
    # 模型固定 8s 但镜头表只要 5s 时
    shot4_video.node_id: {"startSec": 1.5, "endSec": 6.5}
  }
}, position_x=1500, position_y=300)

# 连接所有视频段（扇入）
for v in [shot1_video, shot2_video, ...]:
  canvas_op_connect(pid, v.node_id, "videoUrl", concat.node_id, "videos_multi")
```

---

## 🔥 v13 角色一致性铁律（漫剧不崩脸的 4 件套）

行业 60% → 90% 一致性提升的关键：

```
1. Sequential 生成（先 hero 再用 hero 当 ref）  
   ↓ characterSheet 节点自动做（v13 内置）
2. Identity Lock Prompt 公式（5 维面部锁定）  
   ↓ characterSheet 节点自动加（v13 内置）
3. Contact Sheet 拼大图（pose sheet，1 张拼图当 ref）  
   ↓ canvas_compose_contact_sheet 手动调
4. subjectRefs 端口（image2video 接 contact sheet）  
   ↓ canvas_op_connect ... "subjectRefs"
```

**漏掉任何一步**，角色都会漂。

---

## 🎵 v13 三层音频设计（漫剧不假的关键）

行业实测：好音频能把视觉质量"补上"半档。

### 三层音轨

```
Layer 1: 主题音乐（BGM）  ← canvas_run_music_gen 单段或卡点
Layer 2: 环境氛围（Ambient Bed）  ← audioBible.ambientBaseline 描述 → image2video.audioRef
Layer 3: Foley（脚步、衣袂、武器声）  ← image2video prompt 内置描述
```

### 漫剧节奏 BGM 卡点（v11 musicGen）

```python
# 60s 漫剧的 BGM 卡点（按 Phase 1 的 5 个 beat 切）
music = canvas_op_add_node(pid, kind="musicGen", data_json={
  "duration": 10,  # 单段最大 10s（诗云限制）
  "audioModel": "audio1.0",
  "timingPrompts": [
    {"from": 0, "to": 3, "prompt": "笛箫单声，清冷悲悯（钩子前 3s）"},
    {"from": 3, "to": 15, "prompt": "弦乐渐起，紧张感累积（魔尊登场）"},
    {"from": 15, "to": 30, "prompt": "短促弦乐切分（少年握剑）"},
    {"from": 30, "to": 45, "prompt": "钟鼓齐鸣高潮 + 龙吟（爆点）"},
    {"from": 45, "to": 60, "prompt": "余音渐弱，留白收尾"}
  ]
})
canvas_run_node(pid, music.node_id)
# 出来的 audioUrl 接 videoConcat.bgmUrl
```

---

## 🚀 v13 必用魔法工具时机

### canvas_film_analysis（视频反推）

**什么时候用**：用户给了参考视频（"我想做这种风格的"），你要照着学。

```python
# 用户："帮我做一个像这个视频的镜头" + 上传视频
analysis = canvas_film_analysis(video_url=user_uploaded_video_url)
# 拿到 shots 数组 → 每个 shot 含 reusable_prompt → 直接用 prompt 搭 image2video 节点
for shot in analysis["shots"]:
  print(f"镜头 {shot['index']}: {shot['shotSize']} / {shot['cameraMovement']}")
  print(f"复用 prompt: {shot['reusableprompt']}")
```

### canvas_run_script_doctor（剧本医生）

**什么时候用**：scriptGen 跑完后**强烈推荐**调一次。

```python
# scriptGen 跑完后
state = canvas_op_get_state(pid)
script_node = next(n for n in state["nodes"] if n["data"]["kind"] == "scriptGen")
scenes = script_node["data"]["outputs"]["scenes"]

report = canvas_run_script_doctor(
  scenes=scenes,
  user_intent="60s 漫剧爆点前置"
)
# 看评级：B+ 以上直接搭画布；C 以下接受修订或回 Phase 1
# critical 改进必须处理
```

### canvas_cutout / canvas_outpaint

**什么时候用**：
- **抠图**：要换背景（角色 PNG → 新场景）/ 做产品镜头（电商漫剧）
- **扩图**：16:9 出片 → 9:16 抖音版 / 21:9 影院感

### canvas_optimize_prompt ⭐

**什么时候用**：用户给的 prompt 太短（<100 字符）或者你写完后觉得不够工业级。

```python
optimized = canvas_optimize_prompt(
  prompt="少年握剑站着",  # 太短
  context="image 节点 - 古风漫剧首帧"
)
# 用 optimized.optimized 替代原 prompt
```

---

## ⚠️ 漫剧不崩 14 条红线

1. ❌ characterSheet viewCount 用 3（一致性差）— ✅ 用 6
2. ❌ characterSheet 跑完不拼 contact sheet — ✅ 跑完立刻拼
3. ❌ image2video 不接 subjectRefs — ✅ 必须接
4. ❌ image2video 不连双关键帧（首+末）— ✅ 必须双关键帧
5. ❌ 角色 prompt 没 5 维 identity lock — ✅ 必须 5 维（眼/鼻/下颌/唇/肤）
6. ❌ 角色 negative 项 <7 — ✅ ≥7 项
7. ❌ image prompt <500 字符 — ✅ ≥500 字符
8. ❌ 用 blob: URL 喂 image2video — ✅ 必须 https/asset/data:
9. ❌ 60s 漫剧爽点放最后 — ✅ P50 爽点 45s 内
10. ❌ 单镜头超 8s — ✅ 漫剧节奏 4-6s 最佳
11. ❌ 跨场景换光线方向 — ✅ 整片同一光线方向（lookProfile 锁）
12. ❌ scriptGen 跑完不调 script_doctor — ✅ 必调一次
13. ❌ 不存主体库 — ✅ 跨集必存
14. ❌ 用户没确认就 user_confirmed=True — ✅ 等用户明说

---

## 📐 模型速查（doubao-seedance-2-0 推荐设置）

调研依据：诗云 https://shiyunapi.com/api/pricing_new + apifox

| 模型 | 时长 | 首尾帧 | 原生音频 | 多模态参考 | 推荐场景 |
|---|---|---|---|---|---|
| **doubao-seedance-2-0** ⭐ | 4-15s | ✅ | ✅ | ✅ 12 文件 | **漫剧首选**（影视飓风评："海啸级"）|
| veo3.1-fast | 5/8s | ✅ | ✅ | 3 张 | 国际质感 |
| veo3.1 | 5/8s | ✅ | ✅ | 3 张 | 国际最强（贵）|
| sora-2 | 5/10s | — | ✅ | — | 文艺片 |
| kling-2.6 | 5/10s | ⚠️ 部分 | ✅ | — | 长镜头 |

**推荐组合**：
- 漫剧（60s 内）→ doubao-seedance-2-0（性价比+多模态）
- 短片（5min）→ veo3.1-fast 主用 + sora-2 文戏 + actionShotSet 走 doubao
- 多集系列（10+ 集）→ doubao-seedance-2-0 全程（资产沉淀 + 价格）

---

## 🎯 Phase 5 完成后告诉用户什么

```
画布搭好了。一共 N 个节点：
- {char_count} 个角色立绘（已 spawn {N×6} 张视图 + 拼了 contact sheet）
- {scene_count} 个场景立绘（已 spawn {N×6} 张视图）
- 1 个风格锚 storyboard
- {shot_count} 个镜头 image 节点（首帧 + 末帧成对）
- {shot_count} 个 image2video 视频节点
- 1 个 musicGen 卡点 BGM
- 1 个 videoConcat 拼接节点

推荐运行顺序：
1. ▶ 角色立绘（自动 spawn 6 视图 + 拼 contact sheet）
2. ▶ 场景立绘
3. ▶ 风格锚
4. ▶ 每镜头首末帧 image
5. ▶ 每镜头 image2video（已接 subjectRefs，角色一致）
6. ▶ musicGen 卡点 BGM
7. ▶ videoConcat 拼接成片

预计成本：约 ¥{X} 元（按诗云 default×1.15 计费分组）
预计耗时：{Y} 分钟（如果 GPU 不排队）

如果跑出来不满意：
- 单个镜头不对 → 选中节点点 ▶（重跑此节点 + 下游）
- 角色脸漂 → 检查是否连了 subjectRefs，没连就用 contact sheet 接上
- 节奏不对 → videoConcat 切换 cutPattern
- 整片色调不对 → 调 canvas_save_director_bible 改 lookProfile

参考视频学习：用户给参考视频时调 canvas_film_analysis 反推分镜。
```

---

End of SKILL v13.1 main file. References live under `references/`.
