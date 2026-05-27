---
name: video-canvas-director
description: "通过 Hermes 桌面端的无限画布做生产级 AI 电影。Hermes 是导演 + 制片厂主任，**搭画布不调 API**——按工作流 B（scriptGen → storyboard 风格锚 → 每镜头独立 image × 2 [首帧 + 末帧] → image2video → videoConcat）搭出可视化 pipeline，让用户看到每个镜头的独立分镜节点（占位 idle，运行后才出图）。基于 2026 年 Veo 3.1 / Sora 2 / Seedance 2.0 / Kling 2.6 工业实战。v7.3 强制 Phase Gates：剧本拆解 → 角色 Bible → 镜头规划 → 用户确认后才搭画布；时长按剧情节奏决定，不是模型上限填满。v12 加动作戏 8 大武术机位（actionShotSet）。专业知识（题材模板/音频/双关键帧）按需 skill_view 子文件加载。"
version: 12.0.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [video, canvas, cinematic, storyboard, character-consistency, dual-keyframe, audio-design, self-correcting, multi-genre, wuxia, xianxia, urban, cyberpunk, scifi, fantasy, mv, ad, anime, veo, sora, seedance, nano-banana, kling, orchestration, prompt-engineering]
    requires: [hermes-desktop, desktop-bridge]
---

# Video Canvas Director — 生产级 AI 视频画布编排（v12.0 动作戏八大武术机位）

When the user asks Hermes to **make a video, short film, music video, ad, multi-episode series, or adapt a novel/screenplay** — invoke this skill.

> **v12.0 关键升级**
>
> 1. **动作戏专用节点 `actionShotSet`**：基于 [studiobinder fight scene 经典指南](https://www.studiobinder.com/blog/how-to-storyboard-a-fight-scene/) + cinemadrop 4-beat 拆解，自动出 8 大武术机位（master-wide / tracking / low-angle / high-angle / Dutch tilt / slow-motion / POV / reaction），覆盖徒手武打、追逐戏、特技戏、吊威亚、兵器对打 5 种 actionType；自动 spawn 8 张独立 image 子节点。
>
> **v11.0 升级**
> 1. **剧本医生（`canvas_run_script_doctor`）**：scriptGen 跑完后调，调 vision 模型按 6 维评分（钩子 / 角色弧 / 节奏 / 对白 / 视觉化 / 情感张力），输出整体评级 + 具体改进建议（critical/high/medium/low）+ 可选 AI 修订版 scenes。
> 2. **音乐 / 音效节点（`musicGen`）**：用诗云 vidu audio1.0 / kling-audio 文生音效，单段 BGM（10s 内）或卡点分段时间戳。输出 audioUrl，可接 image2video.audioRef / videoConcat.bgmUrl / audio2video.audio。
> 3. v10 的 shotSet / dialogueShot / cutPattern / 项目编导档案 全部保留。

---

## ⛔ HARD GATE — 不读完这一节就不要建项目

**`canvas_create_project` 已加运行时硬校验**：缺少 `story_beats / character_bible / shot_breakdown / user_confirmed=True` 任意一项 → 工具返回 `phase_gate_failed`，画布不会建。

**所以工作流是固定的**：

```
USER → 给一段剧本，搭画布
HERMES → chat 输出 Phase 1 剧本拆解（≥120 字）
HERMES → chat 输出 Phase 2 角色 Bible（每角色 ≥200 字）
HERMES → chat 输出 Phase 3 镜头规划表（≥200 字含每镜头时长 + 字段）
HERMES → 问「以上确认无误我开始搭画布？」
USER → 确认（或微调，循环回到对应 phase）
HERMES → canvas_create_project(name, story_beats, character_bible, shot_breakdown, user_confirmed=True)
HERMES → 后续 canvas_add_node / canvas_connect ...
```

**禁止**：
- 跳过 Phase 1/2/3 直接调 `canvas_create_project` → 工具拒绝
- 给 Phase 1/2/3 一个空字符串或几十字应付 → 工具拒绝（≥120/200/200 字硬阈值）
- 没等用户回复就 `user_confirmed=True` → 流程作弊；只能在用户明确说"确认 / 搭吧 / 继续 / yes / OK"等之后才设 True

---

## 🔥 核心理念

> **Hermes 的工作 = 搭画布 + 写工业级 prompt + 填结构化字段。不直接出图出视频。**

### 🚨 中文 Prompt 强制规则（v7.4 新增）

**所有节点的 prompt 字段统一用中文写**，**不**写英文（除了下面允许的术语白名单）。

理由：
1. 用户是中文创作者，prompt 直接影响人物服饰 / 场景 / 动作描述，中文表达更精准（例："白衣染尘、剑眉星目、淡金劫光"）
2. 2026 年的中文图像 / 视频模型（豆包、Seedance、可灵、Veo 3.1 Pro 中文支持、GPT Image 2）对中文理解 ≥ 英文
3. 英文写"cinematic xianxia dying golden light dim blood"模型只会渲染抽象气氛，**画不出"枷锁道痕"这种具体特征**

**英文术语白名单**（这些保留英文，因为是行业标准词）：
- 镜头：`extreme-wide / medium / close-up / low-angle / dolly-in / tracking / 35mm` 等（§镜头字段词典）
- 比例：`16:9 / 9:16`
- 风格 modifier：`cinematic / film grain / anamorphic / volumetric` 这种 1-2 词的修饰
- negative prompt：`no text, no watermark, no extra fingers` 这种禁用项

**正确示例**（角色 prompt，约 850 字符）：

```
白衣少年剑仙——百年道宗承龙脉嫡传弟子，正值天劫破境第七重。
【面部】剑眉星目，瞳色淡金（劫光余韵），鼻梁高挺，薄唇紧抿，下颌线分明；左眉骨上有一道细疤（前世渡劫旧伤）；
肤色冷白偏青（劫光淬体痕迹），脸颊有未擦净的血痕；眼神隐忍坚毅、孤勇悲悯，绝不是愤怒少年。
【发型】乌黑长发束玄铁束发冠，几缕散发垂落额前；发丝末端因劫风半干、有银灰色尘渍。
【服饰】上身白色道袍（细密暗纹云雷），衣领玄色镶金线；束腰玄色腰带，腰带左侧悬青铜螭龙剑，剑穗为青色丝绦；
袖口与下摆均染上劫尘灰渍、微微破碎；脚踩玄底白边布履。
【标志物 / Identity Lock】（每张分镜都必须保留这五项）：
1. 脖颈与手腕处的玄色枷锁道痕（细如发的暗刻符文）
2. 左手虎口隐溢血丝
3. 右手握剑、剑身环绕青色龙鳞光晕
4. 头顶半丈高处悬浮一缕淡金色劫雷余息
5. 整体气场带"承重之沉"，身后地面青石微裂
【风格关键词】中国玄幻武侠水墨电影感 + 35mm anamorphic + teal-amber 调色 + god rays 神性侧逆光 + film grain 颗粒
【negative】no text, no watermark, no modern objects, no extra fingers, no deformed hands, no face drift, no outfit change, 不要现代元素，不要异色瞳，不要双角色
```

写 prompt 时**必须**包含这 6 类信息：
1. 角色基础（一句话定性）
2. 面部细节（眉/眼/鼻/唇/疤/肤色/眼神）
3. 发型（颜色 + 长度 + 束法 + 散发处理）
4. 服饰（材质 + 主色 + 暗纹 + 破损 + 配件）
5. **Identity Lock 标志物**（≥5 项，跨节点必须保留）
6. negative prompt（≥7 项）

**字符数硬阈值**（hermes 写 prompt 时自查）：
| 节点 | 最低字符数 |
|---|---|
| characterSheet | ≥ 800 字符 |
| storyboard（整片风格锚）| ≥ 400 字符 |
| image（每镜头分镜）| ≥ 500 字符 |
| image2video（每镜头视频）| ≥ 800 字符 |

如果你写完不到这个数字，**重写一遍**，不要建节点。

### ⚠️ 错误做法（hermes 必须避免）

错误做法 ❌
1. 直接调 API 给用户出图出视频
2. 节点 prompt 一句话："白衣染尘、隐忍坚毅"——这是描述，不是 prompt
3. 用英文短句"cinematic xianxia dying golden light"代替中文详细描述
4. 一个 storyboard 节点出 N 张图就直接接 image2video（B 工作流要求每镜头一个独立 image 节点）
5. 把镜头/焦距/光线/比例全塞 prompt 字符串里，结构化字段（shotSize / cameraMovement / lighting / colorTone / aspectRatio）留空
6. 角色不锁脸、不锁服装、不写 negative prompt
7. 自己 canvas_run_node 跑节点

正确做法 ✅
1. **建项目**（带 Phase 1-3 全文）→ **加角色立绘** → **加 scriptGen** → **加 storyboard 当风格锚** → **每镜头加双关键帧 image 节点（首+末）** → **每镜头加 image2video** → **videoConcat 拼接**
2. **每个节点的 prompt 都是工业级中文**（≥ 800/500/800 字符，按节点类型；含 6 类信息 + Identity Lock + negative）
3. **结构化字段独立填**：shotSize / cameraMovement / lighting / colorTone / aspectRatio 必须分别传，不要全堆 prompt 里
4. **角色锁死**：每个角色一个 characterSheet，所有下游节点 connect 到 .views
5. **negative prompt 必备**：每个图/视频节点都写
6. **占位策略**：所有 image / image2video 节点 status='idle'，**不要自己 run**，告诉用户审看后再点 ▶

---

## 🚧 强制 Phase Gates 流程

### Phase 1 — 剧本拆解（Story Beats Analysis）

**MUST OUTPUT BEFORE ANY canvas_ tool call**。chat 里直接说，不调工具。

输出格式：

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

### Phase 2 — 角色 Bible（Character Bible）

**MUST OUTPUT BEFORE ANY canvas_ tool call**。每个出场角色单独一段（≥ 200 字）：

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
- **登场设计**：青碧光柱破云 + 龙须飘摇 + 龙瞳凛冽
- **声音设计**：低沉古远龙吟（沉蛰）+ 出阵后浩荡龙息音
- **Identity Lock 标志物**：青碧色鳞片、长须、四爪持剑光
```

---

### Phase 3 — 镜头规划（Shot Breakdown）

**MUST OUTPUT BEFORE ANY canvas_ tool call**。

⚠️ **每个镜头必须用 §镜头字段词典 里的标准词**，**不能**写"中景一点"、"一个特写"这种笼统话——必须写 `medium` / `close-up` 这种 SKILL 已经定义的词。

**强制使用以下专业字段（每个值都从 §镜头字段词典 选）**：

| 字段 | 必须从这些值里选 |
|---|---|
| 景别 (shotSize) | extreme-wide / wide / medium-wide / medium / medium-close / close-up / extreme-close / over-the-shoulder |
| 角度 (cameraAngle) | eye-level / low / high / dutch / worms-eye / birds-eye / over-shoulder / pov |
| 运镜 (cameraMovement) | static / dolly-in / dolly-out / tracking / pan-left / pan-right / tilt-up / tilt-down / orbit / crane-up / crane-down / handheld / steadicam-push |
| 光线 (lighting) | golden-hour / blue-hour / low-key / high-key / rembrandt / backlit / hard-noon / overcast / neon-night / candle-light / moonlight / volumetric / god-rays / magical |
| 焦距 (lens) | 14mm / 24mm / 35mm / 50mm / 85mm / 100mm-macro / 135mm / 200mm-tele / 24-70mm / anamorphic |
| 节奏 (pacing) | 慢 (3-5s) / 中 (5-8s) / 快 (1.5-3s) / 极快 (≤1s) / 燃爆 / 渐弱 |
| 色调 (colorTone) | 自由组合，例 "teal-amber"、"warm rim + jade shadow"、"crimson + jade"、"epic gold-cyan" |

输出一个**镜头表**：

```
## 🎬 Phase 3 · 镜头规划

| #  | 时长 | 节奏 | 时段     | 内容          | 景别       | 角度    | 运镜        | 光线         | 色调               | 焦距   | 主角姿态 → 终态        | SFX 关键点       |
|----|------|-----|----------|---------------|-----------|---------|-------------|--------------|---------------------|--------|------------------------|------------------|
| 1  | 4s   | 慢  | 0-4s     | 远景立崖       | extreme-wide | low | static      | low-key 雷光     | teal-amber          | 14mm   | 单膝跪地剑插地 → 同 | 风声+轻雷        |
| 2  | 6s   | 中  | 4-10s    | 主角中景定调   | medium    | eye-level | dolly-in   | golden-hour     | warm rim+jade shadow | 24mm   | 闭目低头 → 抬眼睁目  | 衣袍猎猎+剑鸣    |
| 3  | 5s   | 快  | 10-15s   | 反派近身切入   | close-up  | low | static     | low-key      | crimson+jade        | 85mm   | (反派) 阴影露半脸 → 露齿笑 | 黑雾凝聚音       |
| 4  | 10s  | 极快 | 15-25s  | 双方打斗       | medium-wide | tracking | hard-noon | tea-amber          | 35mm   | 横剑格挡 → 兵刃迸火星 | 兵器交击+碎石    |
| 5  | 8s   | 慢  | 25-33s   | 鲜血激法阵     | extreme-close | static | rembrandt | warm gold | 100mm-macro | 鲜血滴剑身 → 龙纹激活 | 法阵嗡鸣+心跳    |
| 6  | 7s   | 中  | 33-40s   | 龙息苏醒伏笔   | wide | crane-up | backlit | magical cyan-violet | 24mm    | 黑雾压境 → 青光柱破阵 | 古老龙吟（深沉） |
| 7  | 12s  | 燃爆 | 40-52s  | 神龙现世人剑合一 | wide | orbit | volumetric | epic gold-cyan | 35mm | 青龙破阵 → 人剑合一冲撞 | 龙息+剑啸+破空 |
| 8  | 8s   | 渐弱 | 52-60s  | 收尾留白       | medium    | eye-level | dolly-out | blue-hour | cool blue+amber | 35mm | 龙盘旋身后 → 双双俯瞰山河 | 清亮剑鸣+悠长龙吟 |

【时长设计逻辑】
- 镜头 1 (4s)：开场建立，张力起步
- 镜头 4 (10s)：打斗群——必须长，让动作展开
- 镜头 7 (12s)：高潮——绝对不能短，神龙登场是全片 payoff
- 镜头 8 (8s)：收尾留白——余韵需要

【节奏曲线】4s 慢 → 6s 中 → 5s 快 → 10s 极快 → 8s 慢 → 7s 中 → 12s 燃 → 8s 渐弱（按情绪起伏动态分配，不是平均切）

【模型选择】
- 单镜头 ≤ 8s：veo3.1-fast（首尾帧 + 音频，$0.17/s）
- 单镜头 = 10s：MiniMax-Hailuo-02（6/10s）或 kling-video（5/10/15s）
- 单镜头 = 12s：sora-2-pro（4/8/12 三档，$0.58/s）或 viduq3-pro（1-16s 任意，$0.12/s）
- 任意秒数：doubao-seedance-2-0-260128（4-15 任意，$0.07/s 性价比）

【时长不匹配的处理】
- 镜头 5 (8s) 用 veo3.1-fast 正好 → 不用后期
- 镜头 3 用 veo3.1-fast（8s 固定）但只要 5s → 加 videoTrim 节点（startSec=1.5, endSec=6.5）
- 镜头 7 (12s) 想用 kling-video → 出 10s（kling 上限）+ videoExtend 节点续 2s（注意 videoExtend 仅 kling-* 模型可用，因为接口要 video_id）

【预算估算】
60s × 混合模型平均 ≈ $0.25/s × 60 = ~$15 + 16 张分镜图 ≈ $2 = 总 $17
```

---

### Phase 4 Gate — 用户确认

Phase 1-3 输出完后，hermes **必须**说：

> 以上是剧本拆解 + 角色 Bible + 镜头规划。**确认无误我开始搭画布**？或者你想先调整哪一段？

**等用户明确确认或微调后**，才能进入 Phase 5（搭画布）。如果用户没说话直接给新指令，按用户最新意图处理（不阻塞）。

---

## 🔑 工具清单

### 画布编排
| 工具 | 何时用 |
|---|---|
| `canvas_create_project(name, story_beats, character_bible, shot_breakdown, user_confirmed=True)` | Phase 4 后建项目 |
| `canvas_list_projects()` | 用户说"打开 X 项目" |
| `canvas_open(project_id)` | 读取已有画布 |
| `canvas_add_node(project_id, kind, data_json, x?, y?)` | **核心**：在画布加节点 |
| `canvas_connect(project_id, src, src_handle, tgt, tgt_handle)` | 连两个节点 |
| `canvas_update_node_data(project_id, node_id, patch_json)` | 改节点参数 |
| `canvas_get_state(project_id)` | 查画布当前状态 |
| `canvas_run_node(project_id, node_id, mode)` | 触发用户 UI 运行（**不要自己用**） |

### 画布 meta
| 工具 | 何时用 |
|---|---|
| `canvas_get_meta(project_id)` | 读当前画布开关 |
| `canvas_set_self_check(project_id, enabled, ...)` | 启停 vision 自检（详见 `references/self-check.md`）|
| `canvas_set_cinematic_pro_mode(project_id, enabled)` | 启停影视级深度模式（详见 `references/cinematic-pro.md`）|
| `canvas_list_video_models()` | **必读**：拿所有视频模型的真实能力（duration / 首尾帧 / 音频 / 4K） |

### 辅助
| 工具 | 何时用 |
|---|---|
| `canvas_segment_script(raw)` | 长剧本（>500 字）拆解 |
| `canvas_evaluate_artifact(...)` | 自检（仅当 selfCheckEnabled=true）|
| `canvas_save_artifact(...)` | 落盘到 vault |
| `canvas_list_artifacts(project?)` | 列出已存产物 |

### 🆕 v8 — Spawn 子节点 / 主体库 / 一键重排（LibTV 范式）
| 工具 | 何时用 |
|---|---|
| `canvas_get_spawned_children(project_id, parent_node_id)` | **必用**：跑完 characterSheet/storyboard 后拿子节点列表（含 childNodeId / spawnLabel / imageUrl） |
| `canvas_clean_old_spawn_batches(project_id, parent_node_id)` | 父节点重跑后画布乱了，清非最新批次 |
| `canvas_auto_layout(project_id)` | 画布超 15 节点 / spawn 后凌乱，一键重排（同 Shift+Option+F）|
| `canvas_subject_list(type_filter?)` | **搭画布前先调**，检索 character/scene/prop 主体看是否可复用 |
| `canvas_subject_load(subject_id)` | 拿主体完整数据（含 9 视图 url）落地 |
| `canvas_subject_save(name, subject_type, cover_image_url, views, ...)` | 把当前画布上做出的角色/场景/道具存成跨画布资产 |
| `canvas_subject_delete(subject_id)` | 清主体 |

### 🆕 v9 — image 魔法 / 多画布 / 文本节点
| 工具 | 何时用 |
|---|---|
| `canvas_run_reverse_prompt(image_url, vision_model?)` | 任意图反推中文工业级 prompt（用于 prompt 复用 / 风格学习） |
| `canvas_run_temporal(image_url, direction, seconds)` | 演绎画面：after=N 秒后（image2video 抽末帧）/ before=N 秒前（image2image 反向） |
| `canvas_create_subcanvas(project_id, name)` | 项目内新建一张画布（短剧分集 / 多版本 / 分幕） |
| `canvas_list_subcanvases(project_id)` | 列项目内所有画布（main 永远第一）|
| `canvas_open_subcanvas(project_id, canvas_id)` | 拿某张画布的完整 nodes/edges |
| `canvas_rename_subcanvas` / `canvas_delete_subcanvas` | 改名 / 删除（main 不能删） |

### 🆕 v9 — 节点新参数
| 节点 | 新字段 | 取值 |
|---|---|---|
| characterSheet | `subject_type` | "character"（人物全身, default）/ "face"（脸部三视图）/ "scene"（场景四方位）/ "prop"（产品三视图） |
| storyboard | `mode` | "normal"（默认）/ "25-grid"（5×5 大网格自动拆 25 张）/ "4-panel-story"（2×2 剧情四宫格自动拆 4 张） |
| image2video | `audioRef` | 音频 URL（卡点视频，仅 nativeAudio 模型识别） |
| 新节点 | `kind="text"` | 独立文本节点，输出 `text` 给下游 image/storyboard/image2video 的 prompt 输入端口 |

### 🆕 v10 — 编导级专业能力
| 工具 / 节点 | 用途 |
|---|---|
| `kind="shotSet"` | 同场景的镜头组（master + reverse + closeup + OTS）— 守 180° 轴线 |
| `kind="dialogueShot"` | 双角色对话 8 镜头标准（A 左 B 右严守不跨轴）|
| videoConcat `cutPattern` | "standard" / "rapid-cut" / "j-cut" / "l-cut" / "montage" |
| `canvas_save_director_bible(project_id, look_profile, audio_bible)` | 保存项目级色彩+声音档案，自动注入所有节点 prompt |
| `canvas_load_director_bible(project_id)` | 读项目档案 |

### 🆕 v11 — 剧本医生 + 音乐生成
| 工具 / 节点 | 用途 |
|---|---|
| `canvas_run_script_doctor(scenes, user_intent?)` | scriptGen 跑完后调，按 6 维评分 + 改进建议（critical/high/medium/low）+ 可选 AI 修订版 |
| `kind="musicGen"` | 文生音效 / BGM（vidu audio1.0 / kling-audio）；单段或卡点分段 |

### 🆕 v12 — 动作戏（八大武术机位）
| 工具 / 节点 | 用途 |
|---|---|
| `kind="actionShotSet"` | 动作戏 8 大武术机位（master-wide / tracking / 仰拍 / 俯拍 / Dutch / 慢镜 / POV / 反应）；支持 4 beat（setup/exchanges/reversal/resolution）+ 5 actionType（fight/chase/stunt/wirework/sword）|
| `canvas_run_action_shot_set(description, master_image_url, image_model, ...)` | 直接调（不用画布的快路径） |

---

## 🆕 v9 — image 魔法工具栏工作流

任意 image 节点（含 spawn 出来的子节点）选中后，顶部出现 6 个魔法按钮。所有按钮都会自动 spawn 子节点（不修改原图）：

```
[选中 image 节点]
       ↓
       ▼ 顶部工具栏 ▼
┌─────────────────────────────────────────────────┐
│ 📝 反推 │ 🔄 多角度 │ ✨ 高清 │ ⏩ 3s 后 │ ⏪ 5s 前 │
└─────────────────────────────────────────────────┘

📝 反推 → spawn 1 个 text 子节点（role=reverse-prompt，含 6 段中文 prompt）
🔄 多角度 → spawn 3/6/9 个 image 子节点（同物体不同角度）
✨ 高清 → spawn 1 个 image 子节点（原图高清版）
⏩ 演绎 3 秒后 → spawn 1 个 image 子节点（视频抽帧）
⏪ 回溯 5 秒前 → spawn 1 个 image 子节点（image2image 反向）
```

hermes 用 MCP 工具触发：
- `canvas_run_reverse_prompt(image_url)` 反推
- `canvas_run_temporal(image_url, "after", 3)` 演绎
- 多角度：调 `canvas_run_character_sheet(subject_type="character" | "scene", reference_image=image_url, view_count=3/6/9)`，跑完用 `canvas_get_spawned_children` 拿子节点

---

## 🆕 v9 — 多画布管理工作流

```
项目"红楼梦短剧"/
  ├─ main.vcanvas.json   ← 默认画布
  ├─ ep1.vcanvas.json    ← canvas_create_subcanvas("红楼梦短剧", "ep1")
  ├─ ep2.vcanvas.json    ← canvas_create_subcanvas("红楼梦短剧", "ep2")
  └─ pilot.vcanvas.json  ← 试拍版本
```

**关键：主体库跨画布共享**，所以同一角色 / 场景 / 道具在所有画布都能复用，不需要每集重做。

hermes 工作流：
1. 用户说"做第二集" → `canvas_list_subcanvases` 看是否已有 ep2 → 没有就 `canvas_create_subcanvas`
2. 在 ep2 画布上工作时，`canvas_subject_list` 检索 ep1 已存的角色 / 场景 / 道具 → 命中就 load + add_node 落地
3. 跨集只新做新增的角色 / 场景

---

## 🆕 v9 — 分镜表格视图

用户切换"⊞ 表格 / ⊟ 画布"后，表格视图渲染当前画布所有 scriptGen.outputs.scenes：
- 行：每个 scene
- 列：序号 / 时长 / 剧情 / 角色 / 镜头缩略图 / 景别 / 运镜 / 灯光 / 色调 / 音效 / 视频状态 / 操作
- 双击单元格 → 编辑 → 自动写回 scriptGen.outputs.scenes[i]
- 行操作：🎯 跳到画布定位 / ↻ 重跑该格

hermes 不需要直接操作表格 UI（用户层用），但需要知道**当用户改了表格里某行的 cameraMovement 字段后，对应 storyboard 节点会自动重跑那一格**。

---

## 🆕 v9 — characterSheet subjectType 工作流

```
用户："给我做个院子的多方位场景"
  ↓
hermes 调 canvas_op_add_node(kind="characterSheet", data={
  name: "古风院子",
  description: "宋代庭院, 假山曲径, 月夜, 微风…（≥200 字）",
  subjectType: "scene",
  viewCount: 4,    // scene mode 默认 4 方位（前/左/右/后）；6 方位加俯视/细节
})
  ↓
跑完 spawn 4 张独立 image 子节点（前/左/右/后）
  ↓
canvas_get_spawned_children → 拿 4 个子节点 id
  ↓
hermes 把不同方位连给不同镜头的 image2video（保证场景空间一致性）
```

同理：
- `subject_type="face"`：脸部三视图（正脸/45°/纯侧脸），用于换脸 / 数字人
- `subject_type="prop"`：产品三/六视图（电商详情页风格）

---

## 🆕 v9 — storyboard mode 工作流

```
mode="normal"（默认）：N 个 scene → spawn N 张分镜（v8 行为）
mode="25-grid"：1 次调用 → 5×5 大网格图 → 后端拆 25 张 → spawn 25 张独立子节点
mode="4-panel-story"：1 次调用 → 2×2 剧情四宫格 → 拆 4 张 → spawn 4 张子节点
```

什么时候用 25-grid / 4-panel-story：
- 用户说"给我 4 张图把这场戏讲完"→ 4-panel-story
- 用户说"密集的连续分镜，节奏紧"→ 25-grid
- 标准长篇剧情 → normal（每 scene 独立精修空间大）

---

---

## 🆕 v10 — 镜头组（shotSet）：场景空间一致性

```
[image / storyboard] 主参考图
        ↓
shotSet description="..." shotTypes=[master,reverse,closeup,ots-a]
        ↓ 跑完 spawn 4 张子节点（轴线一致 / 同灯光 / 同色调）
```

为什么需要 shotSet：同一参考图作为输入 → 模型理解"这是同一个空间"；严格 prompt → 强制 180° 轴线规则。

## 🆕 v10 — 对话场景（dialogueShot）

剧情片 70% 镜头是对话。dialogueShot 是双人对话场景的标准 8 镜头：

```
characterSheet A（屏幕左）+ characterSheet B（屏幕右）+ 场景图
        ↓
dialogueShot characterAName/characterBName/sceneDescription/dialogue
        ↓ spawn 8 张：
  establishing / two-shot / ots-a-to-b / ots-b-to-a
  / close-a / close-b / reaction-a / reaction-b
```

A 永远屏幕左、B 永远屏幕右，杜绝跨轴。

## 🆕 v10 — videoConcat cutPattern

| pattern | 适用 |
|---|---|
| standard | 默认 |
| rapid-cut | 动作戏 / 卡点（每段 ≤1s） |
| j-cut | 对话戏 / 情感转场（声音先入） |
| l-cut | 连续氛围 |
| montage | 时间流逝（强 crossfade + BGM 上调） |

## 🆕 v10 — 项目级编导档案（lookProfile + audioBible）

**Phase 4 建项目时，第 1 件事**调 `canvas_save_director_bible` 定档案。之后所有 image / image2video / storyboard / shotSet / dialogueShot 节点跑时，**自动注入 prompt 末尾**。

```python
canvas_save_director_bible(
  project_id=...,
  look_profile={
    "name":"宋代古风冷青调",
    "colorTemperature":"cool",
    "dominantTones":"青灰偏冷，月夜银白点缀",
    "contrast":"high",
    "keyLighting":"low-key 低调",
    "filmGrain":"film-grain-light"
  },
  audio_bible={
    "themeMusicStyle":"古风弦乐 + 笛箫",
    "characterMotif":"男主 motif：古琴单音 + 弦乐渐起",
    "ambientBaseline":"雨夜：雨声 + 远处更夫梆子",
    "foleyStyle":"极简"
  }
)
```

整片色调 + 声音设计自动统一，hermes 不用每个节点重复写。

---

## 🆕 v11 — 剧本医生（Script Doctor）

scriptGen 跑完后**强烈推荐**调一次剧本医生：

```python
report = canvas_run_script_doctor(
  scenes=scriptGen.outputs.scenes,
  user_intent="<story_beats 概要>"
)
# report.grade ∈ A+/A/B+/B/C+/C/D
# report.scores: 6 维评分（0-10）
# report.improvements: critical/high/medium/low 改进建议
# report.revisedScenes: 可选 AI 修订版（接受就用 update_node_data 写回）
```

**6 维度**：hook（钩子）/ characterArc（角色弧）/ pacing（节奏）/ dialogue（对白）/ visualizability（视觉化）/ emotionalImpact（情感张力）

**门槛**：B+ 以上直接搭画布；C 以下接受修订或回 Phase 1 重写；critical 改进必须处理。

---

## 🆕 v11 — 音乐 / 音效（musicGen）

诗云接的 vidu audio1.0 / kling-audio，duration 2-10 秒：

### 单段 BGM
```python
canvas_op_add_node(kind="musicGen", data_json={
  "prompt": "古风弦乐 + 笛箫，悲悯隐忍；雨夜环境氛围",
  "duration": 10,
  "audioModel": "audio1.0"
})
# audioUrl → videoConcat.bgmUrl
```

### 卡点分段（每段独立 prompt）
```python
canvas_op_add_node(kind="musicGen", data_json={
  "duration": 10,
  "audioModel": "audio1.0",
  "timingPrompts": [
    {"from": 0, "to": 3, "prompt": "鸟鸣晨光，笛声渐起"},
    {"from": 3, "to": 6, "prompt": "雨声渐起，弦乐转沉"},
    {"from": 5, "to": 9.5, "prompt": "钟鼓齐鸣，高潮"}
  ]
})
```

**接入位置**：
- 整片 BGM → videoConcat.bgmUrl
- 单镜卡点 → image2video.audioRef（仅 nativeAudio 模型识别）

⚠️ duration ≤ 10s；超过分多段 musicGen + 后期拼接。

---

## 🆕 v12 — 动作戏（actionShotSet）：八大武术机位

> **调研依据**：[studiobinder.com — How to Storyboard a Fight Scene](https://www.studiobinder.com/blog/how-to-storyboard-a-fight-scene/) + cinemadrop fight-scene beat 拆解。原文要点已重写以符合许可。

### 行业准则（来自调研）

1. **不同景别组合**（wide / medium / close）— 全用 medium 会显得重复，wide 让观众重新定位空间
2. **机位角度切换 power shifts** — high angle 显弱势 / low angle 显强势 / Dutch angle 制造失衡
3. **deep depth of field** — 动作戏快速运动需要深景深保持焦点
4. **camera movement 三种** — handheld（混乱）/ Steadicam（流畅 John Wick 风）/ tracking dolly
5. **slow motion 标志性瞬间** — Matrix / Gladiator / Deadpool 都用过，需高 FPS
6. **lens 选择** — wide-angle 强调动作和空间感，telephoto 压缩空间让招式看起来更接触
7. **构图卖招式** — profile shot 卖钩拳（藏空间），over-shoulder 卖正面踢腿

### 8 大武术 / 动作戏机位（actionShotSet 默认全开）

| 机位 key | 中文 | 用途 |
|---|---|---|
| `master-wide` | 主大全 | 建立空间 + choreography 全貌（Steadicam 风） |
| `tracking-follow` | 跟拍 | dolly / Steadicam 跟随主体动作 |
| `low-angle-power` | 仰拍 | 强势方 power up（看上去高大压迫） |
| `high-angle-fall` | 俯拍 | 弱势方 power down（被压制 / 渺小） |
| `dutch-tilt` | 倾斜 | Dutch angle 失衡瞬间（混乱 / 反转） |
| `slow-motion-impact` | 慢镜 | 标志性接触瞬间（高 FPS）|
| `pov-attacker` | POV | 攻击者第一视角（沉浸威胁感） |
| `reaction-defender` | 反应 | 防守者面部反应特写 |

### 4 beat 节奏拆解（cinemadrop 标准）

按一场打戏内部时间顺序：

| beat | 含义 | 推荐机位组合 |
|---|---|---|
| `setup`（铺垫） | 交手前的紧张静默：对峙、距离评估、肢体微动 | master-wide + low-angle-power（强势方）+ reaction-defender |
| `exchanges`（交锋） | 招式来回连续交替；动态最强 | tracking-follow + slow-motion-impact + pov-attacker |
| `reversal`（反转） | 胜势翻转的关键瞬间；表情从胜券在握转震惊 | high-angle-fall（原强势变弱势）+ dutch-tilt + slow-motion-impact |
| `resolution`（收势） | 定胜负后的余韵 | master-wide + reaction（双方）+ low-angle-power（胜者） |

### actionType 5 种用例

| actionType | 适用 | 关键调度 |
|---|---|---|
| `fight`（默认） | 徒手武打 | profile + over-shoulder 卖招式 |
| `chase` | 追逐戏 | tracking-follow 占主导 + 频繁切机位制造紧张 |
| `stunt` | 特技戏 | slow-motion-impact 慢镜密集 + 多机位安全冗余 |
| `wirework` | 吊威亚飞行打斗 | low-angle-power 仰拍夸张飞行高度 + Dutch tilt |
| `sword` | 兵器对打 | profile shot + slow-mo 卖刃刃相接 + 火花反光 |

### chaosLevel 摄影风格

- `steadicam`（默认 John Wick 风）：干净、连续、舞蹈式调度，**适合**：表现专业、克制、高水准武术
- `handheld`（混乱风）：贴身、抖动、浑浊，**适合**：街斗、求生混战、被动挨揍

### axisRule 轴线

- `preserve`（默认）：守 180° 轴线（攻防双方左右关系不跨轴）
- `break`：可破轴 — **仅在**多人混战 / 乱斗为表现混乱才用，否则观众会迷向

### 工作流示例

**短篇武术片 — 一场两人决斗：**
```python
# 1. 角色三视图（主角 + 反派各一个 characterSheet）
char_hero = canvas_op_add_node(kind="characterSheet", data_json={
  "name": "夜枭", "subjectType": "character", "viewCount": 9,
  "description": "宋代刺客，黑衣斗篷，单刀"
})
char_villain = canvas_op_add_node(kind="characterSheet", data_json={
  "name": "鬼面", "subjectType": "character", "viewCount": 9,
  "description": "鬼面具甲士，长枪"
})

# 2. 场景图（决斗场地）
scene = canvas_op_add_node(kind="image", data_json={
  "prompt": "雪夜山顶古寺前，月光照地，远山模糊；冷青色调",
  "imageModel": "seedream-4.0", "aspectRatio": "16:9"
})

# 3. 一场两人决斗 → 4 个 actionShotSet 节点（4 个 beat 各一个）
for beat in ["setup", "exchanges", "reversal", "resolution"]:
  canvas_op_add_node(kind="actionShotSet", data_json={
    "description": "雪夜山顶古寺前，夜枭单刀对鬼面长枪。气氛凝重，月光照刃。",
    "actionType": "sword",       # 兵器对打
    "pacing": "methodical",      # 节制重击
    "chaosLevel": "steadicam",   # 流畅
    "axisRule": "preserve",      # 守轴
    "beat": beat,
    "imageModel": "seedream-4.0"
  })
  # 连主参考图（场景）+ 角色多视图
  canvas_op_connect(scene_id, "images", action_id, "master")
  canvas_op_connect(char_hero_id, "views", action_id, "characters")
```

跑完每个 actionShotSet 都自动 spawn 8 张独立 image 子节点 → 用户挑出最满意的几张 → 接 image2video → videoConcat 用 `cutPattern="rapid-cut"` 紧张感成片。

### MCP 工具

| 工具 | 说明 |
|---|---|
| `canvas_op_add_node(kind="actionShotSet", data_json={...})` | 加节点 |
| `canvas_run_action_shot_set(...)` | 直接调（不用画布的快路径） |

### Edge 规则

- 输入：`image.images` 或 `storyboard.boards` → `actionShotSet.master`（必填）
- 输入：`characterSheet.views` → `actionShotSet.characters`（可选，强烈推荐）
- 输出：`actionShotSet.shots` → `image2video.image` / `shotGroup.boards_multi` / `preview.any`

---

## 🆕 v9 — text 节点工作流（独立 prompt）

```
[text 节点] (用户写: "雪夜古风长街…")
        ↓
        ↓ 输出 text
        ↓
[image 节点] ← 上游 text 覆盖本地 prompt
        ↓
        ↓ 输出 images
        ↓
[image2video 节点]
```

适用场景：
- 同一个 prompt 想给多个生成节点共用 → 一个 text 节点连 N 个下游
- "反推 prompt" 自动落地的 text 子节点 → 用户直接连给新的 image 节点复刻原图风格
- 长 prompt 不想塞进 image 节点的字段里 → 单独一张 text 卡片更清楚

---

## 🆕 v8 — LibTV 范式：spawn + 主体库工作流图

```
开工 → canvas_subject_list("character")  ← 先查有无可复用主体
                ↓ 命中
                canvas_subject_load(subj_xxx)
                canvas_op_add_node(kind="characterSheet", data={status:done, outputs:{views:[...]}})
                                          ↓ 跳过 character generation
                                          ↓
                                  characterSheet（已 done，已带 N 视图）
                                          ↓ 自动 spawn 9 个独立 image 子节点
                                          ↓
                ↓ 没命中
                canvas_op_add_node(kind="characterSheet", data={status:idle, ...})
                canvas_run_node(project_id, char_id, "downstream")
                                          ↓ 跑完自动 spawn N 个独立 image 子节点
                                          ↓
                                  ★ canvas_get_spawned_children(project_id, char_id)
                                  ★ 拿到 [{childNodeId, spawnLabel, imageUrl}]
                                          ↓
                                  ★ 你挑 3 张最佳的 child id
                                          ↓
                                  canvas_subject_save(name, "character", cover, views=挑的3-9张)
                                  ★ 这样下个画布能复用！

storyboard 同理：跑完自动 spawn N 个分镜独立 image 节点；
canvas_get_spawned_children 拿子节点 → 逐个连到 image2video 做视频
```

### 关键约束（v8）

- **不要**自己手动 add_node 创建 image 节点去引用 characterSheet 的 view —— 它们已经被 auto-spawn 了，重复创建会污染画布
- **每跑完一个 characterSheet / storyboard，必调 `canvas_get_spawned_children` 一次**，拿子节点 id 后才能精准连下游
- 如果 `canvas_get_spawned_children` 返回 `children: []`（说明 spawn 失败 fallback 到 v7 旧行为），降级用父节点的 `outputs.views[]` / `outputs.boards[]`
- 画布超 15 节点 / spawn 后凌乱，**主动调** `canvas_auto_layout` —— 用户体验更好
- 搭画布**第一步**应该是 `canvas_subject_list("character")` 检索可复用主体，命中复用比新生成强得多

---

## 🏗️ 工作流 B 架构图（v8）

```
┌────────────────┐
│ characterSheet │  (角色 1，9 视图，identity anchor)
└────┬───────────┘
     │ views
     │
┌────▼───────┐         ┌─────────┐
│ scriptGen  │────────►│storyboard│  (整片风格锚，1 张总视觉)
└────┬───────┘ scenes  └────┬────┘
     │                      │ boards (style ref)
     │   ┌──────────────────┼─────────────────────┐
     ▼   ▼                  ▼                     ▼
   首帧+末帧 image       首帧+末帧 image       首帧+末帧 image
   (镜头1)               (镜头2)              (镜头N)
      │                     │                     │
      ▼                     ▼                     ▼
  image2video × N    （时长固定不匹配 → videoTrim 后期裁剪）
      │                     │                     │
      └─────────────────────┼─────────────────────┘
                            ▼
                    ┌───────────────┐
                    │ videoConcat   │  → 成片
                    └───────────────┘
```

**关键**：
- **storyboard 节点只有 1 个**：定整片视觉锚，不出最终分镜图
- **每镜头 image 节点 × 2**：首帧 + 末帧（双关键帧锁定）
- **image2video 节点 × N**：和镜头一一对应
- **角色 connect 到每一个 image 和 image2video**：identity 跨节点锁死

详细的双关键帧搭法见 **`references/dual-keyframe.md`**。

---

## 📚 镜头字段词典（结构化字段必备词）

### shotSize（景别，对应 prompt 关键词）
- `extreme-wide` (extreme wide shot, EWS)：全景史诗、地理 epic
- `wide` (wide shot, WS)：人在环境里、动作展开
- `medium-wide` (medium wide / cowboy)：腰以上、对话和走位
- `medium` (medium shot, MS)：胸以上、叙事甜区
- `medium-close` (medium close-up, MCU)：肩以上、情绪起步
- `close-up` (close-up, CU)：脸/手特写、细节情绪
- `extreme-close` (extreme close-up, ECU)：眼睛/嘴角等局部
- `over-the-shoulder` (OTS)：对话标准镜

### cameraAngle（角度）
- `eye-level`：中性叙事
- `low`：低角度仰拍——表现强大 / 压迫
- `high`：俯拍——脆弱 / 渺小
- `dutch` (dutch tilt)：失衡 / 紧张 / 醉酒
- `worms-eye`：贴地极仰，神性 / 巨物
- `birds-eye`：垂直俯瞰
- `over-shoulder`：人物侧后视角
- `pov`：第一人称视角

### cameraMovement（运镜）
- `static`：固定镜头
- `dolly-in / dolly-out`：推 / 拉
- `tracking`：跟拍（侧向）
- `pan-left / pan-right`：左右摇
- `tilt-up / tilt-down`：上下摇
- `orbit`：360 环绕
- `crane-up / crane-down`：升 / 降
- `handheld`：手持纪录感
- `steadicam-push`：平稳跟推

### lighting（光线）
- `golden-hour`：日出/日落黄金时段
- `blue-hour`：蓝调时段
- `low-key`：暗调（黑色电影）
- `high-key`：亮调（广告 / 商业）
- `rembrandt`：伦勃朗光（侧前 45°）
- `backlit`：逆光剪影
- `hard-noon`：硬正午光
- `overcast`：阴天柔光
- `neon-night`：霓虹夜
- `candle-light` / `moonlight`：烛光 / 月光
- `volumetric`：体积光（光柱可见）
- `god-rays`：耶稣光
- `magical`：魔幻光（玄幻 / 科幻必备）

### lens（焦距）
- `14mm` / `24mm`：广角，建立场景
- `35mm`：标准电影焦段
- `50mm`：人眼透视
- `85mm` / `135mm`：人像焦段
- `100mm-macro`：微距特写（血滴、龙纹）
- `200mm-tele`：长焦压缩
- `24-70mm`：标准变焦
- `anamorphic`：变形宽银幕（电影感）

### styleRef / 风格 preset（题材锚定）
| 题材 | style 关键词 |
|---|---|
| 武侠 | `cinematic wuxia ink-wash 35mm anamorphic teal-amber mist god rays` |
| 玄幻仙侠 | `epic xianxia magical cyan-gold volumetric mist celestial` |
| 都市悬疑 | `urban thriller neo-noir teal-orange shallow depth of field` |
| 赛博朋克 | `cyberpunk neon-pink-cyan night rain reflective wet streets` |
| 硬科幻 | `hard sci-fi sleek industrial cyan-cobalt clinical lighting` |
| 奇幻冒险 | `western fantasy painterly amber-emerald god rays mist` |
| 纪录片 | `documentary natural overcast handheld 35mm` |
| 商业广告 | `commercial high-key clean white background 50mm` |
| 音乐 MV | `MV stylized neon high-contrast color-blocking` |
| 日系动漫 | `anime ghibli-pastel sky soft cell-shaded` |

完整 prompt 模板见 **`references/genres.md`**。

### aspectRatio（比例）
- `16:9`：电影 / YouTube / 横屏
- `9:16`：竖屏 / 抖音 / Reels
- `1:1`：Instagram / 方形
- `4:3`：复古电视 / 文艺片
- `21:9`：超宽 / 院线感

---

## 📐 模型速查表（数据来自诗云 /api/pricing_new + apifox）

| 模型 ID | duration（秒）| 首尾帧 | 原生音频 | 最高分辨率 |
|---|---|---|---|---|
| **doubao-seedance-2-0-260128** ⭐ | **4-15 任意** | ✅ | ✅ | 1080p |
| **veo3.1-fast** ⭐ | 8 固定 | ✅ | ✅ | 1080p |
| **veo_3_1-fast-4K** ⭐ | 8 固定 | ✅ | ✅ | 4K |
| veo3.1 / veo_3_1 / veo3.1-pro | 8 固定 | ✅ | ✅ | 1080p |
| veo3.1-pro-4k / veo3.1-4k | 8 固定 | ✅ | ✅ | 4K |
| veo3.1-components / -4k | 8 固定 | ❌（仅首帧）| ✅ | 1080p / 4K |
| **sora-2-pro** ⭐ | **4 / 8 / 12** | ❌ | ✅ | 1080p |
| sora-2 | 4 / 8 / 12 | ❌ | ✅ | 720p |
| **doubao-seedance-1-5-pro-251215** ⭐ | 4-12 任意（--dur） | ✅ | ✅ | 1080p |
| doubao-seedance-1-0-pro-250528 | 5-15 | ✅ | ❌ | 1080p |
| **MiniMax-Hailuo-02** ⭐ | **6 / 10** | ✅ | ❌ | 1080p |
| MiniMax-Hailuo-2.3 | 6 / 10 | ✅ | ❌ | 1080p |
| **kling-video** ⭐ | **5 / 10 / 15** | ❌ | ✅（部分版本）| 1080p |
| kling-video-extend | 续接 5s | ❌ | ❌ | 1080p（仅 kling-* 模型可续接）|
| wan2.6-i2v | 5 固定 | ❌（仅首帧）| ✅ | 1080p |
| **viduq3-pro** ⭐ | **4-16 任意** | ✅ | ✅ | 1080p |
| viduq3-turbo | 4-16 任意 | ✅ | ✅ | 1080p |
| viduq3 / viduq3-mix | 4-8 | ❌ | ❌ | 1080p |
| viduq2-pro / -turbo | 4-8 | ✅ | ❌ | 1080p |
| omni-flash-components | 6 / 8 / 10 | ❌ | ✅ | 1080p |
| grok-video-3 / -10s | 6 / 10 固定 | ❌ | ❌（10s 有音频）| 1080p |

> **必须先调 `canvas_list_video_models`** 拿运行时真实数据，不要凭这表死记硬背。

---

## ⏱️ 时长 ≠ 模型上限：剧情节奏决定，必要时用剪辑/续接节点

按以下顺序选策略：

#### A. 选时长灵活的模型（首选 ★）
- 任意 4-15：`doubao-seedance-2-0-260128` / `viduq3-pro` / `viduq3-turbo`
- 6 / 10：`MiniMax-Hailuo-02`
- 4 / 8 / 12：`sora-2-pro`

#### B. videoTrim 节点 — 后期裁剪
模型固定 8s 但镜头表只要 5s：
```python
canvas_add_node(kind="image2video", data_json={"videoModel": "veo3.1-fast", "duration": 8, ...}) → vid_8s
canvas_add_node(kind="videoTrim", data_json={"startSec": 1.5, "endSec": 6.5}) → trim_id
canvas_connect(project_id, vid_8s, "videoUrl", trim_id, "video")
canvas_connect(project_id, trim_id, "videoUrl", concat_id, "videos_multi")
```

#### B'. videoConcat.segmentTrims — 一站式
```python
canvas_add_node(kind="videoConcat", data_json={
    "videoOrder": [vid_8s_a, vid_8s_b],
    "segmentTrims": {
        vid_8s_a: {"startSec": 1.5, "endSec": 6.5},
        vid_8s_b: {"startSec": 0,   "endSec": 4.2}
    }
})
```

> **何时用 videoTrim 节点 vs segmentTrims**：
> - 只为最终成片精确 → 用 segmentTrims（少一层节点）
> - 中间产物要送给下游（videoExtend / subtitleRemoval）→ 用 videoTrim 节点

#### C. videoExtend 节点 — 续接（≥ 模型上限时）
```python
canvas_add_node(kind="image2video", data_json={"videoModel": "kling-video", "duration": 10, ...}) → vid_10s
canvas_add_node(kind="videoExtend", data_json={
    "extendSeconds": 5,
    "videoModel": "kling-video-extend",
    "prompt": "继续上一秒动作，平滑过渡"
}) → ext_id
canvas_connect(project_id, vid_10s, "videoUrl", ext_id, "video")
```

⚠️ **可灵 video-extend 接口要 video_id（非 URL），所以 videoExtend 节点的上游 image2video 必须用 kling-* 系列模型**（其他模型的 task_id 不能被可灵接受）。

**推荐排序**：A > B > B' > C。

---

## 🎬 搭画布步骤（Phase 4-5）

### Step 1 — 解析意图
- 用户给完整剧本？→ Step 2
- 只说"做个 X 视频"？→ 用最常见模板（60s / 1 主角 / 用户提到题材）

### Step 2 — 长剧本拆解（>500 字才需要）
```
canvas_segment_script(raw)  → episodes / global_characters / global_style
```

### Step 3 — 建项目（必须传 Phase 1-3 全文 + user_confirmed）
```
canvas_create_project(
  name="<项目名>",
  story_beats="<Phase 1 全文，≥120 字>",
  character_bible="<Phase 2 全文，≥200 字>",
  shot_breakdown="<Phase 3 全文，≥200 字>",
  user_confirmed=True
)
→ projectId
# 缺任一字段或 user_confirmed=False → 工具返回 phase_gate_failed
```

### Step 4 — 加角色立绘（每出场角色一个）
```
canvas_add_node(project_id, kind="characterSheet", data_json={
  "label": "角色：白衣剑仙",
  "name": "白衣少年剑仙",
  "description": "<≥ 800 字符工业级 prompt，含 face / hair / outfit / signature 锁定>",
  "imageModel": "gpt-image-2-all"
}, position_x=100, position_y=100)
```

### Step 5 — 加 scriptGen
```
canvas_add_node(project_id, kind="scriptGen", data_json={
  "label": "剧本：XXX",
  "prompt": "<把用户原始剧本完整放进来>",
  "model": "MiniMax-M2.7-highspeed",
  "sceneCount": 6,
  "styleHint": "<根据题材选风格关键词，参考 §styleRef preset>"
}, position_x=100, position_y=400)
```

### Step 6 — 加 storyboard（**整片风格锚，1 个**）
```
canvas_add_node(project_id, kind="storyboard", data_json={
  "label": "整片风格锚",
  "sceneIndex": null,
  "style": "<从 §styleRef preset 选>",
  "imageModel": "gpt-image-2-all"
}, position_x=400, position_y=400)

canvas_connect(project_id, scriptgen_id, "scenes", anchor_id, "scenes")
canvas_connect(project_id, character_node_id_1, "views", anchor_id, "characters")
```

### Step 7 — 每镜头双关键帧（首帧 + 末帧 image）
按 Phase 3 镜头表，每镜头建 2 个 image 节点：

```python
for i, shot in enumerate(SHOTS):
    # 首帧
    canvas_add_node(kind="image", data_json={
      "label": f"镜头 {i+1} 首帧（t=0）",
      "prompt": f"<≥500 字符 — character lock + {shot['startPose']} + scene + composition + mood + negative>",
      "imageModel": "gpt-image-2-all",
      "aspectRatio": "16:9",
      "shotSize": shot["shotSize"],         # 从 §镜头字段词典 选
      "cameraAngle": shot["cameraAngle"],
      "cameraMovement": shot["cameraMovement"],
      "lighting": shot["lighting"],
      "colorTone": shot["colorTone"],
      "lens": shot["lens"],
      "styleRef": shot["styleRef"]
    }) → start_id

    # 末帧（同景别同光，仅换姿态）
    canvas_add_node(kind="image", data_json={
      "label": f"镜头 {i+1} 末帧（t={shot['duration']}s）",
      "prompt": f"<同上 character lock + {shot['endPose']} + same scene + same lighting + 'no camera angle change'>",
      "imageModel": "gpt-image-2-all",
      ...同首帧的 shotSize/lens/lighting/colorTone...
    }) → tail_id

    # 风格锚 + 角色 → 首末帧
    canvas_connect(project_id, anchor_id, "boards", start_id, "styleRef")
    canvas_connect(project_id, anchor_id, "boards", tail_id, "styleRef")
    canvas_connect(project_id, character_id, "views", start_id, "reference")
    canvas_connect(project_id, character_id, "views", tail_id, "reference")
```

### Step 8 — 每镜头 image2video（接首帧 + 末帧）
```python
for i, shot in enumerate(SHOTS):
    image2video_data = {
      "label": f"视频镜头 {i+1}（{shot['duration']}s, 双关键帧）",
      "prompt": "<≥800 字符 — 七要素 + 时间戳分段 + 三层 audio design + negative>",
      "videoModel": shot["model"],   # 从 §模型速查表 选
      "duration": shot["duration"],
      "aspectRatio": "16:9",
    }
    # 🆕 v8 — 音乐驱动卡点：MV / 卡点视频 / 节奏强相关镜头
    # 仅 nativeAudio 模型识别（Seedance 2.0 / Veo 3.1 / Sora 2 / Wan 2.6 等）
    if shot.get("audio_ref_url") and is_native_audio_model(shot["model"]):
        image2video_data["audioRef"] = shot["audio_ref_url"]
    canvas_add_node(kind="image2video", data_json=image2video_data) → vid_id
    canvas_connect(project_id, start_id, "images", vid_id, "image")
    canvas_connect(project_id, tail_id, "images", vid_id, "tailFrame")
```

### Step 9 — 时长不匹配处理（按需加 videoTrim / videoExtend）
按 Phase 3 镜头表里【时长不匹配的处理】小节执行。

### Step 10 — videoConcat
```python
canvas_add_node(kind="videoConcat", data_json={
  "label": "成片",
  "videoOrder": [],
  "crossfadeSeconds": 0.5,
  "reencode": True,
  "bgmVolume": 0.35
}) → concat_id

for vid_id in video_node_ids:
    canvas_connect(project_id, vid_id, "videoUrl", concat_id, "videos_multi")
```

### Step 11 — 🆕 v8 画布整理 + 主体归档
```python
# 节点超 15 个时主动重排（用户体验）
canvas_auto_layout(project_id)

# 跑完 characterSheet 后，挑 3 张最佳归档为主体（下次复用）
children = canvas_get_spawned_children(project_id, char_node_id)
best_3 = pick_best_views(children["children"])  # hermes 自己挑
canvas_subject_save(
    name="<主角名>",
    subject_type="character",
    cover_image_url=best_3[0]["imageUrl"],
    views=[{"label": c["spawnLabel"], "url": c["imageUrl"]} for c in best_3],
    description="<角色 Bible 简版>",
    image_model=character_image_model,
    tags=["<题材>", "<风格>"],
    source_project_id=project_id,
    source_node_id=char_node_id,
)
```

### Step 12 — 告诉用户（**不要自己 run**）
告诉用户：画布搭好；推荐运行顺序：① 角色立绘（跑完会自动 spawn 9 张独立子节点，可挑选 / 局部修改）→ ② 风格锚 → ③ 每镜头首末帧 image → ④ 每镜头视频 → ⑤ 拼接。如果之前已经存过该角色为主体，跳过 ①。

---

## 🔑 工业级 Prompt 公式速查

### image2video（视频片段）— 七要素结构
```
[CHARACTER LOCK 前 4 项]
- Subject: <白衣少年剑仙，承青龙血脉，面容清冷>
- Face: <剑眉、星目、薄唇、肤色淡白>
- Hair: <长发束乌玉冠、几缕散落额前>
- Outfit: <白色道袍、玄色腰带、淡金劫光晕、脖颈枷锁道痕>

[SCENE / 场景描述]
- Setting: <悬崖之巅、黑云压顶、天雷滚动、地面碎石>
- Mood: <凝重、孤勇、绝境希望>

[ACTION / 动作分时间戳]
- [0-3s] character 单膝跪地，长剑插地，闭目低头
- [3-7s] 抬眼睁目，眼神由垂转抬，金色劫光自天而降
- [7-10s] 衣袍鼓荡，剑鸣三响

[CAMERA / 摄影]
- ShotSize: medium → medium-close (dolly-in)
- Angle: eye-level, low
- Lens: 24mm → 35mm
- Movement: slow Steadicam push-in

[LIGHTING / 光线]
- Type: golden-hour + magical cyan rim light
- Intensity: warm gold key + cool jade fill, contrast 4:1

[STYLE / 风格锚]
- cinematic wuxia ink-wash 35mm anamorphic teal-amber mist god rays
- 16:9 aspect, film grain, deep shadows

[AUDIO / 三层]
- Diegetic: wind, sword hum, fabric flap
- Foley: footstep on stone, sword scrape
- Music: low strings + erhu melody, swelling at 7s

[NEGATIVE / 必备]
- no text, no watermark, no extra characters, no deformed hands,
  no face drift, no outfit change, no modern objects
```

详细模板按题材见 `references/prompt-formulas.md` + `references/genres.md`。

---

## ⚠️ 红线 / 常见错误

### ❌ prompt 写"白衣染尘、隐忍坚毅"就完事
✅ 写满 800/500/800 字符（角色/分镜/视频），含完整锁定细节。

### ❌ 把镜头/光线/比例全塞 prompt 字符串
✅ shotSize / cameraMovement / lighting / colorTone / lens / aspectRatio / styleRef **都是独立字段**，分别填。

### ❌ 一个 storyboard 节点出 N 张图直接接 image2video
✅ storyboard 只当**整片风格锚**（1 张总视觉）；每个镜头单独 **image 节点 × 2**（首末帧）。

### ❌ 视频 prompt 不分时间戳
✅ `[0-3s] / [3-7s] / [7-10s]`，每段一个 action + camera。

### ❌ 镜头描述抽象："cinematic shot"
✅ "low-angle wide shot, 24mm, slow Steadicam push-in from medium-wide to medium-close"。

### ❌ 没 negative prompt
✅ 每个图/视频节点都加，至少 7 项。

### ❌ 搭完自己 canvas_run_node
✅ 搭完告诉用户运行顺序，**不**自动跑。除非用户明说"全部 run"。

### ❌ 长剧本（>500 字）直接灌 scriptGen
✅ 先 canvas_segment_script，再分集搭。

### ❌ 跨节点不重复 character lock
✅ 每个 image / image2video prompt 都重复 ≥ 4 项 lock 关键词（脸/发/服/饰）。

### ❌ 镜头时长按模型上限平均切（8/8/8/8/8/8/8/8）
✅ 按 Phase 3 节奏曲线动态分配（4/6/5/10/8/7/12/8 这种）；模型不匹配用 videoTrim / videoExtend 调整。

### ❌ 跳过 Phase 1-3 直接搭画布
✅ canvas_create_project 工具会硬拒绝；必须先 chat 输出 Phase 1-3 + 等用户确认。

### ❌ 调 videoExtend 但上游不是 kling-* 模型
✅ kling video-extend 接口要 video_id，仅可灵任务才有；其它模型用 videoTrim 或换时长灵活模型。

---

## 📂 子文件参考（按需 skill_view 加载）

本 SKILL.md 只放触发流程必需内容。专业知识拆到子文件，hermes 在需要时加载：

```
skill_view(name="video-canvas-director", file_path="references/<file>")
```

| 子文件 | 加载时机 |
|---|---|
| `references/genres.md` | 用户确定题材后，加载该题材的完整 prompt 模板（10 题材） |
| `references/dual-keyframe.md` | 搭 image2video 节点时（详细的双关键帧工作流 + 模型支持矩阵） |
| `references/audio-design.md` | 写 image2video prompt 的 [AUDIO] 段时（三层音轨 + 题材 preset） |
| `references/prompt-formulas.md` | 写 character / image / image2video prompt 时（公式 + 字符长度要求） |
| `references/node-fields.md` | 第一次搭某种节点时（每种节点 data 字段的完整速查） |
| `references/self-check.md` | 用户要求"严格审核 / 高质量 / 影视级"，需要启用 vision 自检闭环 |
| `references/cinematic-pro.md` | 用户提"影视级 / 大片 / 节展"等关键词，启用 P1 影视级深度模式 |
| `references/example-wuxia.md` | 需要完整范例（60s 玄幻武侠端到端 hermes 调用清单） |

**典型加载序**（60s 武侠片）：
1. 用户给剧本 → Phase 1/2/3 输出（不需加载子文件）
2. Phase 3 写 storyboard.style 时 → `skill_view(file_path="references/genres.md")` 拿武侠 preset
3. Phase 4 后建 image / image2video → `skill_view(file_path="references/dual-keyframe.md")` 拿搭法 + `skill_view(file_path="references/audio-design.md")` 拿三层音轨
4. 用户说"严格审核"→ `skill_view(file_path="references/self-check.md")` 拿启用步骤

---

End of SKILL v12.0 main file. References live under `references/`.
