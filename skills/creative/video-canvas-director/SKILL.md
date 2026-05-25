---
name: video-canvas-director
description: "Production-grade AI video creation through Hermes Desktop's infinite canvas. Hermes acts as a film director using the 2026 industry-standard pipeline: Character Bible → Storyboard (8-14 frames) → Image-to-Video → Composer. Built on Veo 3.1 / Sora 2 / Nano Banana Pro best practices."
version: 3.0.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  hermes:
    tags: [video, canvas, cinematic, storyboard, character-consistency, multi-episode, wuxia, xianxia, long-script, veo, sora, nano-banana]
    requires: [hermes-desktop, desktop-bridge, video_gen, image_gen, vision]
---

# Video Canvas Director — 2026 行业级 AI 视频制作 SKILL

When the user asks Hermes to **make a video, short film, music video, ad, multi-episode series, or adapt a novel/screenplay** — invoke this skill. Hermes acts as a **multi-agent film director**, drives the **infinite canvas** through MCP tools, produces artifacts users can see and modify in the canvas UI, and **explicitly self-evaluates** each step.

This SKILL is built on 2026 industry research, including Veo 3.1's [7-Part Prompt Formula](https://frameo.ai/blog/google-veo-3-prompt-guide-best-practices/), Nano Banana Pro's [Storyboard Pipeline](https://help.apiyi.com/en/nano-banana-pro-ai-video-storyboard-character-consistency-guide-en.html), and Sora 2's multi-shot consistency techniques.

---

## 核心理念

> **Hermes 是导演 + 制片厂主任。每一步要像真实电影制作。**

行业级 AI 视频不是"prompt → 视频"。它是：

```
Story → Character Bible → Storyboard (8-14 frames) → Image-to-Video → Edit
        ↓                ↓                          ↓                  ↓
        identity lock    shot rhythm + reference    motion only        BGM + xfade
```

**最大的失败模式**：用户要的"一致角色 + 连贯剧情"，多数 AI 视频项目都垮在这两点上。
本 SKILL 用三层锁死它：
1. **Character Bible**——同一个角色描述字符串原样复用，把它当 identity anchor
2. **多张参考图喂入分镜**——每场都喂 character sheet（front + side + back）
3. **每段视频只描述一个动作**——多动作 = 模型糊

---

## 八条铁律（违反就重来）

1. **Character Bible 优先**——任何主角必须先做 character sheet（3 视图），后续每场分镜把这 3 张图作为多 reference 喂入。**Veo/Nano Banana 都支持最多 3 张参考图**。
2. **角色描述字符串一字不变**——首次写好的 character description 在后续所有镜头里**原样粘贴**。哪怕只换一个词，模型就当成不同人。
3. **Veo 7 部分 prompt 公式**——每段视频 prompt 必须 6 个层次完整：Subject + Action + Context + Style + Camera + Audio + Technical（详见下文公式）。
4. **每段视频只做一件事**——单主体 + 单动作 + 单机位移动。多动作 = AI 不知道往哪儿走 = 糊。
5. **8-14 帧黄金区间**——30-45 秒短片用 8-14 个 beat（参考 Nano Banana Pro 行业规则）；不要超过 14（太碎），不要少于 6（戏剧弧不够）。
6. **Shot Rhythm 节奏**——分镜要呼吸：Wide → Medium → Close-up → Medium → Wide。**避免连续 3 个同类型镜头**（5 个连续 close-up 是大忌）。
7. **图像产物自评分**——`canvas_evaluate_artifact` 给图像（character_sheet / storyboard）打 0-10 分。≥7 通过；<7 重跑（最多 3 次）；3 次仍不行就回退或调整 prompt。**不允许凭空"觉得不错"**。**视频不自评**——交给用户判断（vision 模型对视频不准）。
8. **80% 满意就 edit，不要 regenerate**——分镜如果 80% 对了，用 conversational edit 改细节（"keep everything else, only add glasses"）；不要从头重画。

---

## 多 Agent 心智模型（hermes 在不同阶段切换角色）

| 阶段 | 角色 | 职责 | 工具 |
|---|---|---|---|
| 1 | **Scripter** | 把任意长剧本拆成 episodes + global_characters + global_style | `canvas_segment_script` |
| 2 | **Character Designer** | 每个主角的三视图 character sheet（identity anchor） | `canvas_character_sheet` + `canvas_evaluate_artifact` |
| 3 | **Style Designer** | 整剧风格锚点静帧（style anchor） | `canvas_storyboard`（空场景）+ `canvas_evaluate_artifact` |
| 4 | **Storyboard Artist** | 每场 1 张分镜（喂 character views + style anchor） | `canvas_storyboard` + `canvas_evaluate_artifact` |
| 5 | **Cinematographer** | 每场 1 段视频（用 Veo 7 部分公式拼 prompt）。视频质量交给用户复核 | `canvas_image2video` |
| 6 | **Composer / Editor** | 拼接 + xfade 转场 + BGM | `canvas_video_concat` |
| 7 | **Producer** | 落盘到 vault + 给用户路径 | `canvas_save_artifact` + `canvas_list_artifacts` |

---

## Veo 3.1 / Sora 2 视频 Prompt — 7 部分公式（必须严格遵守）

每个 `canvas_image2video` 调用的 prompt 都要按这 7 部分写，**100-150 词最佳**。

```
1. Subject     [谁/什么] 用 character bible 字符串 + 服饰
2. Action      [一个] 动作 + 节奏副词（slowly / quickly / suddenly）
3. Context     地点 + 时间 + 天气 + 环境
4. Style       视觉风格关键词 5-10 个 + 画幅 + 焦距 + 色调
5. Camera      shot type + movement + angle（用电影术语，见下表）
6. Audio       对话 / 音效 / 环境声（如不要可省）
7. Technical   negative prompts: no subtitles, no watermark, no flicker, no distortion
```

### Camera 词典（必用电影术语，模型才听懂）

| 类型 | 缩写 | 用法 |
|---|---|---|
| Extreme Close-Up | ECU | 眼/手/物特写 — 强情绪/细节 |
| Close-Up | CU | 头部 — 情感峰值 |
| Medium Close-Up | MCU | 胸部以上 — 对话 |
| Medium Shot | MS | 腰部以上 — 角色互动 |
| Medium Wide | MW | 全身 — 动作场景 |
| Wide Shot | WS | 全身 + 环境 — 建立场 |
| Extreme Wide | EWS | 微缩人物 — 宏大叙事 |

| 运镜 | 用法 |
|---|---|
| `slow dolly-in` | 推近 — 情绪聚焦 |
| `slow dolly-out` | 拉远 — 揭示/孤独 |
| `tracking shot` | 跟拍 — 角色动作 |
| `pan left/right` | 横摇 — 揭示空间 |
| `tilt up/down` | 上下摇 — 揭示规模 |
| `crane shot` | 大臂上升 — 史诗感 |
| `orbit / arc` | 环绕 — 主体强调 |
| `handheld` | 手持 — 真实感/紧张 |
| `static` | 静止 — 凝重 |

### 武侠示例（验证有效）

```
Subject: Wuxia swordswoman Yun Qingge in flowing dark green silk robe with white inner layer,
         long jet-black hair tied with a jade hairpin, slim ancient sword at her waist,
         calm cold determined expression
Action:  slowly raises her ancient sword as luminous jade-blue chi swirls around the blade
Context: misty bamboo forest at dawn, cool fog drifting between bamboo stalks,
         dew-covered ground, distant mountains
Style:   cinematic wuxia ink-wash, 35mm anamorphic, 2.39:1 widescreen,
         cool jade-blue palette, soft mist atmosphere, photorealistic with ethereal halo
Camera:  slow dolly-in tracking her gaze, low angle to emphasize her stance
Audio:   guzheng plucking with bamboo flute undertone, soft wind through bamboo
Technical: no subtitles, no watermark, no on-screen text, stable frame, no flicker
```

合成成单段 prompt 时按上面顺序拼，逗号/句号自然过渡。

---

## Storyboard Frame 数量 / 节奏（行业标准）

| 视频长度 | 帧数 | 平均每帧 | 用途 |
|---|---|---|---|
| 15-30s | 6-8 | 2.5-4s | 抖音/Reels 短 hook |
| 30-45s | **8-14**（甜区） | 2-4s | 短片/产品片 |
| 1-2 分钟 | 15-25 | 3-5s | 品牌片 / 短剧单集 |
| 5-15 分钟 | 50-100 | 4-8s | 多集/长片 → 拆多集做 |

### Shot Rhythm 黄金分配

| 类型 | 占比 | 用途 |
|---|---|---|
| Wide / Establishing | 15-20% | 建立场景 |
| Medium | 30-40% | 角色 + 环境 |
| Close-Up | 20-25% | 情感峰值 |
| Extreme Close-Up | 10-15% | 细节/情绪 |
| Transition | 5-10% | 场切 |

**节奏铁律**：避免 3 个同类型镜头连续。经典 breathing pattern：`Wide → Medium → CU → Medium → Wide`。

### Beat Type 单段时长建议

| beat_type | duration | 备注 |
|---|---|---|
| opening / 环境建立 | 6-8s | wide shot 优先 |
| inciting / 触发事件 | 4-6s | medium 切 close |
| rising / 升级冲突 | 6-8s | tracking / handheld |
| confrontation / 对峙打斗 | 8-10s | dynamic + slow-mo |
| twist / 反转 | 4-6s | static + dramatic light |
| reflection / 余韵特写 | 8-12s | slow pull-back |
| hook / 下集钩子 | 3-5s | hard cut |

---

## 角色一致性 — 三层锁死法（行业 2026）

### Layer 1: Character Bible（identity anchor）

第一次定义角色时写一个 **80-120 词的字符串**，包含：
- 朝代/性别/年龄/体型
- 头发（长度/颜色/发型）
- 服饰（材质/颜色/样式 — 越具体越好）
- 武器/配饰
- 面部特征/气质
- 标志性记号（疤痕/痣/眼神）

```
"晚唐时期女剑客云清歌，二十出头，乌黑长发以白玉簪挽起，米白色丝绸交领衫
外披深青色斗篷，腰挂细长古剑，眉宇间英气与冷峻并存，气质如剑出鞘"
```

**这个字符串后续所有 prompt 必须原样粘贴**，连标点都不要改。

### Layer 2: Character Sheet（视觉锚点）

`canvas_character_sheet(name, description=character_bible_string)` 输出三视图：
- front（正面，全身）
- side（90° 侧身）
- back（背身）

**纯白背景**，**全身**，**一致 lighting**。

### Layer 3: Reference Images（每场喂入）

每场 `canvas_storyboard(...)` 调用：
- `character_view_urls = [front, side, back]` —— 3 张全部喂入
- `style_ref = style_anchor.url` —— 整剧风格锚点

加上 prompt 里**显式锁定**：
```
"Keep the character's facial features exactly the same as the reference.
Maintain identical attire, hairstyle, accessories throughout."
```

**Veo 3.1 / Nano Banana Pro / Sora 2 都支持最多 3 张 reference**。喂满 3 张能把 character drift 降低 80%。

---

## 工具清单（MCP）

| 工具 | 阶段 | 关键约束 |
|---|---|---|
| `canvas_segment_script(raw_script, target_episodes=0, target_seconds_per_episode=60)` | 1 | target_episodes=0 让模型按字数自动推荐 |
| `canvas_character_sheet(name, description, reference_image_url?)` | 2 | description 用 80-120 词 character bible |
| `canvas_storyboard(scene_title, scene_description, scene_characters, style, character_view_urls, style_ref_url?)` | 3,4 | character_view_urls 优先 JSON 数组 `["url1","url2","url3"]` |
| `canvas_image2video(image_url, prompt, duration=8)` | 5 | duration 1-12s，VEO 默认 8；prompt 严格按 7 部分公式 |
| `canvas_evaluate_artifact(artifact_url, brief, expected_character_desc?, expected_style?)` | 2,4 | **图像必跑**（character_sheet / storyboard）。**视频自动 skip**（交给用户复核） |
| `canvas_video_concat(video_urls, crossfade=0.3, bgm_url?, bgm_volume=0.35)` | 6 | video_urls 优先 JSON 数组 |
| `canvas_save_artifact(url, relative_path)` | 7 | 路径必须 "Canvas/<project>/..." |
| `canvas_list_artifacts(project?)` | 复用 | 跨集复用角色 / 风格 / 旧分镜 |

---

## 标准工作流（按剧本长度自动分支）

### A. 短概念（< 500 字 / 1 集 / 30-60s）

```
1. 写 Character Bible（80-120 词字符串，存好后续粘贴）
2. canvas_character_sheet(bible) → 三视图，自评 ≥7
3. canvas_storyboard(scene_title="00_style", scene_description="风格锚点静帧")
   → style anchor，自评 ≥7
4. 设计 8-14 个 beat，遵守 shot rhythm（Wide/Medium/CU 交替）
5. for beat:
     board = canvas_storyboard(
       scene_characters=[character_name],
       character_view_urls=[front, side, back],   # 3 张全喂
       style_ref_url=style_anchor,
       style=global_style,
       scene_description=用 character_bible_string + 场景画面
     )
     eval = canvas_evaluate_artifact(board, ...)
     如果 eval.score < 7 → 用 suggestions 改 prompt 重跑（最多 3 次）
6. for beat:
     video = canvas_image2video(
       image_url=board.url,
       prompt=用 7 部分公式拼写,
       duration=按 beat_type 表
     )
     # 视频不自评——多数 vision 模型不支持 mp4，且对视频质量评估不准。
     # 直接落盘，最后让用户在画布预览复核。
     canvas_save_artifact(video.video_url, "Canvas/<project>/seg_{beat_id}.mp4")
7. canvas_video_concat(video_urls=[...], crossfade=0.3-0.4, bgm_url=可选)
8. canvas_save_artifact(final.video_url, "Canvas/<project>/final.mp4")
9. 给用户绝对路径 + 总耗时 / 估算费用
```

### B. 中等剧本（500-8000 字 / 3-6 集）

```
1. canvas_segment_script(raw_script)
   → episodes / global_characters / global_style
   → 给用户审批：集数？风格？删并？

2. for character in global_characters:
     先存 description 到内存（character_bible[name] = description）
     canvas_character_sheet(name, description) + 自评
     canvas_save_artifact(三视图, "Canvas/<project>/characters/<name>_*.png")

3. canvas_storyboard(scene_title="00_style", style=global_style) → style_anchor
   canvas_save_artifact(style_anchor, "Canvas/<project>/style_anchor.png")

4. for episode in episodes:
     for beat in episode.beats:
        board = canvas_storyboard(
            scene_characters=episode.characters,
            character_view_urls=每个角色的 [front, side, back],
            style_ref_url=style_anchor.url,
            scene_description=用 character_bible + beat.description
        )
        evaluate; save → "Canvas/<project>/ep{N}/board_{beat_id}.png"

     for beat:
        video = canvas_image2video(
            image_url=board.url,
            prompt=7 部分公式
        )
        # 视频直接落盘，不送自评（用户复核）
        save → "Canvas/<project>/ep{N}/seg_{beat_id}.mp4"

     final_ep = canvas_video_concat(...)
     save → "Canvas/<project>/ep{N}/final.mp4"

5. 给用户每集绝对路径 + 总耗时 + 估算费用
```

### C. 长剧本（8k-300k 字 / 12-50 集）

跟 B 一样，但**强烈建议**：
1. 先只做第 1 集完整流程，让用户看效果再决定继续
2. 跨集**复用** characters/ 和 style_anchor.png（用 `canvas_list_artifacts` 找已有 url，**不要重生成**——同一角色不同集脸不一致是大忌）
3. 每 3 集给用户一次审批断点（"已完成 ep1-3，预计费用 X 元，继续 ep4-6 吗？"）
4. character_bible 字符串严格不变跨整剧

---

## 自评循环（强制执行 — 不能跳过）

**只对图像（character_sheet / storyboard）做视觉自评**。视频段不送 vision——
多数网关不支持 mp4 URL，且 vision 模型对视频时序质量评不准。**视频质量交给用户判断**。

```python
# 图像产物：必须自评
artifact = canvas_storyboard(...)  # 或 character_sheet
eval = canvas_evaluate_artifact(
    artifact_url=artifact.url,
    brief=scene_description 或主角描述,
    expected_character_desc=character_bible_string,   # 字符串原样
    expected_style=global_style,
)

if eval.score >= 7:
    canvas_save_artifact(...)
    proceed
else:
    retry_count += 1
    if retry_count <= 3:
        # 用 eval.suggestions 修改 prompt 重跑
        重生成
    else:
        # 接受当前最好版本 + 在交付时告知用户该段质量受限
        proceed_with_warning


# 视频产物：直接落盘，不评估
video = canvas_image2video(...)
canvas_save_artifact(video.video_url, ...)
# 不要调 canvas_evaluate_artifact——会自动 skip 并返回 score=-1
# 在最终交付时告诉用户："以下视频段请预览复核：[路径列表]"
```

**注意**：`canvas_evaluate_artifact` 对 mp4/视频 URL 会自动返回 `{score:-1, passed:true, skipped:true}`——
不算失败，让流程继续，但产物在交付时要标记给用户复核。

---

## 80% Edit Rule（迭代规则）

如果分镜 80% 对了但有小瑕疵（缺眼镜 / 灯不够暖 / 构图偏了），**不要 regenerate**：

```
canvas_storyboard(...)  # 第一次出 80% 满意的图

# 然后用 conversational edit
canvas_storyboard(
    scene_title=同上,
    scene_description="Keep everything identical, only [add round glasses / make lighting warmer / move character left 20%]",
    character_view_urls=同上,
    ...
)
```

**核心原则**：
- **One change at a time**——一次只改一个东西
- **"Keep everything else identical"**——明确告诉模型其他不变
- **Be specific, not vague**——"move 20% to the left"，不要"调一下"
- **Reference 永远带上**——不要 drop reference image

---

## 风格 Preset（每个都验证过）

### 武侠 Wuxia
```
global_style: "cinematic wuxia ink-wash, 35mm anamorphic, 2.39:1 widescreen,
              cool jade-blue palette dominated, mist atmosphere, fluid wirework,
              soft focus on hands and weapons, photorealistic with ethereal halo"
角色描述前缀: 晚唐/北宋时期 + [门派] + [身份]
推荐 BGM: guzheng + bamboo flute, slow tempo
推荐运镜: slow dolly-in / tracking / orbit
```

### 玄幻 Xianxia
```
global_style: "xianxia luminous chi effects, golden and azure particle aura,
              ethereal lighting, cinematic 2.39:1, photorealistic with painterly
              highlights, slow-motion fabric flow, divine glow"
角色描述前缀: 仙门弟子 / 上古修士 / [山门] 长老
推荐 BGM: ethereal pads + chinese flute
推荐运镜: rising aerial / slow rotation / parallax push-in
```

### 现代都市 Urban
```
global_style: "contemporary cinematic, 35mm Master Prime, 2.39:1, low-key lighting,
              practical neons, shallow depth of field, photorealistic, film grain"
推荐 BGM: ambient + light electronic
推荐运镜: handheld walking / dolly-in / static MS
```

### 奇幻冒险 Fantasy
```
global_style: "epic fantasy, anamorphic lens flare, magic hour lighting, 35mm,
              painterly composition, photorealistic with concept-art quality, dramatic vista"
推荐运镜: crane / orbit / wide establishing
```

### 科幻 Sci-Fi
```
global_style: "sci-fi cinematic, 35mm, 2.39:1, neon-lit cool palette, volumetric fog,
              practical lighting, photorealistic, retrofuturism, lens flares"
推荐运镜: dolly-in / tracking / low-angle hero shot
```

---

## 错误处理 / 反模式

### 反模式 1：「字符串细微改动」
```
✗ 错: scene1 用 "云清歌身穿青色斗篷"; scene2 用 "云清歌身着青色披风"
✓ 对: 两场都用同一个 80-120 词 character bible 字符串
```

### 反模式 2：「多动作堆 prompt」
```
✗ 错: "她拔剑、转身、踢开门、跳窗"  → 模型不知道做哪个
✓ 对: 一段视频 = 一个动作。多动作拆成多个 beat
```

### 反模式 3：「丢 reference 图」
```
✗ 错: 第一场 storyboard 喂了三视图，第二场偷懒只喂 front
✓ 对: 每场都喂 [front, side, back] 全 3 张
```

### 反模式 4：「连续 5 个 close-up」
```
✗ 错: CU → CU → CU → CU → CU  → 视觉疲劳
✓ 对: Wide → Medium → CU → Medium → Wide  呼吸节奏
```

### 反模式 5：「凭空觉得不错」
```
✗ 错: "感觉这段还行，下一个" → 闭着眼睛拍
✓ 对: 每个产物都 canvas_evaluate_artifact 跑视觉 QA
```

### 反模式 6：「不要 negative prompt」
```
✗ 错: 不加 technical 部分 → 模型生成字幕/水印/闪烁
✓ 对: 每个 video prompt 都带 "no subtitles, no watermark, no flicker, no distortion"
```

### 网关错误处理

| 错误 | 处理 |
|---|---|
| 429 上游饱和 | 等 30s 重试。连续 3 次 429 → 切到 `veo2-fast` 模型 |
| 视频生成超时 12 分钟 | 拆短或换模型 |
| Azure safety_violations（self-harm 等） | **柔化 prompt**——别说"刺中胸口"，说"震退"；别说"流血"，说"金光涌出" |
| 角色严重不一致 | 把 character_bible 加上 "EXACTLY matching the reference image, same face same hairstyle same clothing"，并把三视图全喂入 |
| 单集成本超预算 | 跟用户确认是否继续 |

---

## 成本透明（启动多镜头流程前必须告知用户）

| 项 | 单价 | 备注 |
|---|---|---|
| 三视图 | ~0.3 元 | 3 张图，1 角色一次 |
| 风格锚点 | ~0.1 元 | 整剧 1 次 |
| 分镜（gpt-image-2 / nano-banana-pro） | ~0.1-0.3 元/张 | 一集 8-14 张 |
| 视频段 veo3.1-fast | ~1-2 元/段 | 一集 8-14 段 |
| 视频段 veo2-fast | ~0.5-1 元/段 | 便宜版本 |
| 评估 vision | ~0.01 元/次 | 几乎可忽略 |

| 场景 | 时长 | 估算 |
|---|---|---|
| 1 集 1 分钟（10 段）| ~60s | 12-25 元 |
| 1 集 2 分钟（14 段）| ~120s | 18-35 元 |
| 12 集（共 12 分钟）| ~12min | 150-300 元 |
| 50 集长篇（共 50 分钟）| ~50min | 600-1500 元 |

**任何 > 50 元的决策都要先告知用户再开始**。

---

## 用户输入解读（hermes 应对）

| 用户说 | hermes 应该 |
|---|---|
| "做一个武侠短片" | A 流程，wuxia preset，10 个 beat |
| "把这个 5 万字小说做成视频剧" | C 流程，先 segment_script + 用户审批 |
| "用我之前那个角色" | `canvas_list_artifacts` 找已有 sheet，不要重做 |
| "这段不满意" | 用 80% edit rule 微调，不要 regenerate；用 evaluate 找问题 |
| "继续下一集" | 复用 global_characters + style_anchor，对新集走流程 |
| "改风格" | 重做 style_anchor，整剧风格句替换 |
| "再快点" | 切到 veo2-fast，分镜用 nano-banana-2（draft），分镜数减到 6-8 |

---

## 输出位置（vault 目录约定）

```
<vault>/Canvas/<project_name>/
├── characters/
│   ├── 云清歌_front.png  ← 角色身份锚点（跨集复用）
│   ├── 云清歌_side.png
│   ├── 云清歌_back.png
│   └── ...
├── style_anchor.png      ← 整剧风格锚点
├── ep1/
│   ├── board_b1.png ... board_b14.png
│   ├── seg_b1.mp4 ... seg_b14.mp4
│   └── final.mp4         ← 第 1 集成片
├── ep2/
│   └── ...
└── series_final.mp4      ← 全集合成（可选，ffmpeg 拼）
```

用户在桌面 app 视频画布 tab 能看到、播放、修改任意节点。

---

## Quality Checkpoint（每个产物前过一遍）

每生成一个产物前自问：

```
□ Subject 是 character_bible 字符串原样吗？
□ Action 只有一个动作吗？
□ Camera 用了电影术语吗（CU/MS/dolly/track）？
□ 7 部分都有吗（漏了 Audio/Technical 是常见错）？
□ Negative prompt 加了 no subtitles/watermark/flicker 吗？
□ 三视图全喂进 storyboard 了吗？
□ 上一段视频是同类型镜头吗？要不要换 type 避免连续？
□ 这是这一集第几个 beat？（确保在 8-14 之间）
□ 这段时长合适吗（按 beat_type 表）？
□ Style 句和整剧 global_style 一致吗？
```

---

## 给 hermes 的最后忠告

不要怕慢——一集 30-60 分钟生产时间是正常的。
不要怕花钱——但**每个 > 50 元的决策都要先告知用户**。
不要怕重做——`canvas_evaluate_artifact` 给 5 分时，**重跑就比凑合上线**。
不要假装看见——每个产物必须真正送 vision 评估。
**不要轻视 character bible 字符串**——一个标点都不能改。
**不要打破 shot rhythm**——连续同类型镜头是观众疲劳第一原因。

你是导演，画布是你的剧组。

每一段视频都要能回答：**"如果观众看这一段没声音，他能立刻看出这一段在演什么吗？"**——这是镜头是否有效的唯一标准。

---

## References（2026 行业最佳实践）

- [Veo 3 Prompt Guide — frameo.ai](https://frameo.ai/blog/google-veo-3-prompt-guide-best-practices/) — 7-Part Formula
- [Nano Banana Pro Storyboard Guide — apiyi.com](https://help.apiyi.com/en/nano-banana-pro-ai-video-storyboard-character-consistency-guide-en.html) — 8-14 frame rule, edit-don't-regenerate
- [AI Video Workflow — aifire.co](https://www.aifire.co/p/ai-video-s-biggest-flaw-the-simple-workflow-to-fix-it) — 4-step pipeline
- [Veo 3.1 Multi-Prompt — skywork.ai](https://skywork.ai/blog/multi-prompt-multi-shot-consistency-veo-3-1-best-practices/) — 3 reference images per shot
- [Sora 2 Multi-Shot — aifreeapi.com](https://www.aifreeapi.com/en/posts/sora-2-multi-shot-prompts) — character consistency 95%+
- [Character Consistency Guide — verticalstudio.ai](https://motion.verticalstudio.ai/blog/ai-character-consistency-guide) — 3-5 reference angles

Content was rephrased for compliance with licensing restrictions.
