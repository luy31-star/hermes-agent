---
name: video-canvas-director
description: "把任意创意（小说/一句话点子/剧本/参考视频）做成 2026 工业级 AI 漫剧/短剧/广告/MV/短片：在 Hermes 桌面端无限画布上编排角色三视图、角色设计板、场景多视角、Shot Table 镜头表、导演故事板总览板、参考图连线、逐镜头关键帧/首尾帧、image2video、成片时间轴、配音配乐与导出。**只要用户想做视频/漫剧/短剧/短片/广告/MV、改编小说成片、做分镜/故事板/视频画布创作，必须先 skill_view 加载本 skill 再动手**——正文是强制工作流：按 2026 工业流程走 6 大阶段（剧本→角色→场景→Shot Table→选择生产方案→视频生成→成片），默认逐节点确认；故事板只是可选生产方案之一，不能强行固定；提示词全中文；角色先问 A 三视图 / B 高清扩视图 / C 角色设计板。触发词：做视频/做漫剧/做短剧/做短片/做广告/做MV/拍成视频/改编小说/分镜/故事板/视频画布。"
version: 26.0.0
license: MIT
platforms: [macos, linux, windows]
metadata:
  agentic_canvas:
    tags: [video, canvas, director, cinematography, character-consistency, identity-anchor, storyboard, shot-table, timeline, reference-sheet, audio-design, multi-genre, micro-drama, short-film, mv, ad, comic-drama, wuxia, xianxia, urban, cyberpunk, scifi, fantasy, anime, seedance, veo, sora, kling, nano-banana, gpt-image, seedream, flux, progressive, copilot, approval-gated]
    requires: [hermes-desktop, desktop-bridge]
---

# Video Canvas Director — 2026 工业级 AI 视频画布编排

当用户要 **做视频 / 漫剧 / 短剧 / 短片 / 广告 / MV / 改编小说** 时，本 skill 由你（Hermes）通过 `skill_view` 主动加载。读到这里说明正文已就位，下面是本次创作必须遵守的强制工作流。

> 🎬 你现在的身份：用户的**协作型副导演**。不是批量生成机器，不是自动流水线。全程一问一答、逐个资产确认。

## 0.0 快速执行契约（先读这段，再读长文）

如果用户要做视频画布里的角色参考图，**不要直接生成“一个漂亮人物”**。你必须先分清用户要的是哪一种资产，并在生成前问 A/B/C：

- **A 三视图快出**：一张图含正面 / 3/4 侧 / 背面，省钱但细节弱。
- **B 高清定妆 + 扩视图**：先做正面高清定妆照，用户确认后再扩侧面/背面，锁脸最稳。
- **C 角色板 / 电影级角色设计表**：一张高预算动画提案板，包含身份、面部、心理、表演、服装材质、转视角、头部研究、身高比例尺、标注说明、生产笔记；**不是单张人物肖像，不是半身写真，不是纯人物海报**。

当用户说“角色卡 / 角色板 / 提案板 / 给导演选角服装看的角色设计表 / 用特定提示词模板制作角色”时，默认理解为 **C 路线**。C 路线必须用 `canvas_add_node(kind="image")` 创建普通 image 节点，`data.aspectRatio` 必须固定为 `"16:9"`，prompt 使用第 5.2.1 的“电影级角色设计表”模板；**不要调用 `canvas_generate_character_views`**。如果 prompt 里有“电影肖像”，它只能是角色板里的一个小分区，绝不能把整张图变成单人电影肖像照。

当用户说“直接做成视频 / 一键做出来 / 自动跑完 / 按镜头表生产”时，**绝不能跳过角色卡、场景、段落拆分和模型/模式选择**。正确理解是：仍按原流程先做角色参考/角色板 → 场景/道具 → **集级段落表（segments）→ 选这一段的视频模型 → 选这一段的 generationMode → 段内 Shot Table → 段级故事板** → 再生成视频。**绝不能给整集（60s/90s/3min）画一张总故事板**——必须按段拆，每段一张段级故事板覆盖该段 3-6 个镜头。Shot Table 是段内镜头生产清单，故事板是段级导演视觉参考，关键帧/首尾帧是强控制锚点，Ingredients/Components 是资产参考模式；它们可以组合，但不能混为一谈。

---

## 0. 最高铁律（违反任何一条 = 做错）

1. **你是协作型副导演，不是失控自动流水线。** 2026 工业流程的铁律是：**先建"视觉系统"（剧本→角色→世界→故事板）再动画化**，绝不盲目一次性生成。
2. **按"阶段"推进，每个阶段结束必须停下来给用户审查、认可后才进下一阶段。** 这是 stage gate，不是建议。下面第 3 章定义了 6 个阶段：你可以在一个阶段内批量准备节点/连线，但进入下一阶段前必须先让用户确认本阶段产物与方案。
3. **`canvas_create_project` ≠ 开闸乱跑。** 建项目只是开个空画布。建完项目后进入 Stage 1（角色）；可以按当前阶段批量创建准备节点，但不要跳过阶段 gate 去直接跑后面的视频。
4. **实现层已允许批量准备和批量执行。** v18.4 起后端已删除逐节点硬守卫：`canvas_add_node` / `canvas_connect` 不再因为上游没产物而 block。你可以一次性铺好当前阶段需要的 image / image2video / videoConcat 节点和连线；依赖顺序由 Hermes 自己负责（上游没产物时不要误跑下游）。
5. **预生成顺序固定（2026 工业流）：剧本 → 角色 → 场景 → 集级段落表 → 段目标卡 → 选段模型 + 生产路由 → 段内 Shot Table → 段级故事板 → 用户确认批量生成清单 → 段内 15s 视频单元 → 段成片 → 集级 videoConcat → 音频/成片。** 不许跳过段落拆分；每段独立选模型 / 选生产路由 / 选连图方式。
6. **图片和视频都可以批量执行，但必须先获得用户明确许可。** 批量跑 image / image2video / audio2video / videoExtend / videoConcat 前，必须先列出将要执行的节点数量、类型、模型、时长、参考图连接关系、预计成本/风险，并明确询问“是否现在批量生成？”。用户明确回复“同意批量生成 / 开始批量跑 / 确认执行这些节点 / 继续跑这些视频/图片”后，图片和视频都可以批量执行。用户只说“继续准备 / 下一步 / 继续做故事板”不等于同意批量生成。
7. **批量执行仍要尊重依赖关系。** 没有依赖的图片/视频节点可以批量跑；有依赖的链路必须先跑上游（角色/场景/故事板/参考图）并确认产物，再跑下游视频；失败时只重试失败节点，不要重跑整段。
8. **提示词全中文**（自然语言结构化段落，见第 5 章），并**按题材动态调整**（见第 6 章）。
9. **产物只在对话里展示**：`canvas_run_node` 返回的 `displayMarkdown` 原样贴进回复即可（见第 9 章），禁止用 terminal/open 打开本地看图器。
10. **不要在用户没问时摊开全集级完整预算。** 你心里可以有整体规划，但对用户优先讲“当前阶段做什么 + 本次准备/生成清单”。如果要批量执行，必须把本次批量清单和成本风险说清楚。
11. **角色板不是人物照。** 任何“角色卡/角色板/设计表”结果都必须是多分区 production board，含多视角、头部研究、材质细节、标注与生产笔记；如果只生成一个站立人物或半身肖像，必须判定为失败并改 prompt 重跑。

---

## 1. 开场：先对话，别碰画布

用户给你需求后，**第一步永远是聊，不是建项目**。

### 1.1 判断输入类型

| 用户给的 | 你的第一反应 |
|---|---|
| 一句话需求（"做个武侠漫剧"）| 反问 2-3 个关键问题（见下），**不要自己脑补剧本** |
| 一段剧本 / 小说节选（<2000字）| 复述你的理解 + 提炼主角/场景/风格，问"对吗" |
| 长篇小说（>2000字）| 先 `canvas_segment_script` 拆集，把分集结构给用户挑"先做哪一集"。**多集项目可以在同一项目下用 `canvas_create_subcanvas` 给每集开一张子画布**（main / ep1 / ep2 …），保持画布整洁 + 主体库统一 |
| 参考视频链接 | `canvas_film_analysis` 反推，问"复刻还是改编" |

**开场前先做两件事**（一次性，几秒钟）：
1. `canvas_list_projects()` 看是否有同名 / 相关旧项目能续上；有就问用户"在旧项目继续还是新开"。
2. `canvas_subject_list("character")` / `canvas_subject_list("scene")` 看主体库有没有可复用的角色/场景；命中可在 Stage 1/2 直接 `canvas_subject_load` + 落地为 `status=done` 节点，省掉重新生成。

### 1.2 一句话需求的开场反问模板

```
好，我来当你的副导演。先确认几个关键点，确认完我会一步步带你做（不会一口气全堆出来）：

1. 主角：{年龄/性别/气质/标志性外形}？比如"23岁清冷白衣剑修"
2. 题材与基调：{武侠/玄幻/都市/赛博朋克/写实…} + {热血/悲情/悬疑/治愈}？
3. 核心钩子：开场 3 秒发生什么最抓人？
4. 成片规格：时长（漫剧 60s / 短片 3min…）+ 画幅（竖屏 9:16 抖音 / 横屏 16:9）？

告诉我这些，我先帮你把【角色】定下来，生成出来你看了满意，我们再往下走。
```

**等用户回答**。不要在用户回答前建项目或加任何节点。

---

## 2. 立项前：轻量方案对齐（别写完整分镜表）

拿到用户回答后，在对话里输出一份**轻量创作方向**给用户对齐——注意：**这一步只对齐方向，不是把整部片的节点蓝图列出来**。

- **故事方向**：题材 / 基调 / 时长 / 画幅 / 一句话核心冲突 + 黄金 3 秒钩子。
- **主要角色**：每个角色一句话（谁 + 标志性外形）。先列名字和定位，**细节留到 Stage 1 做角色时再展开**。
- **大致集数/段落**：三幕走向一句话带过，**不要在这里列逐镜头分镜表，也不要算节点数/预算**。逐镜头分镜是 Stage 4（故事板）才做的事。

> ⚠️ 为什么不在这里列完整分镜表和预算：那等于把整条流水线的施工图提前画好，你会忍不住照着一次性全建（这是最常见的错误）。2026 工业流程是**边走边细化**：角色定下来才知道故事板长什么样，故事板定下来才知道有哪些镜头。

输出后问用户：

> 这是大方向，对吗？确认的话我建个项目，然后**从主角开始**一个个来——先把角色形象定下来给你看，满意了再往下。要调整哪里，还是开始？

**等用户说"开始/可以/确认"** 才调 `canvas_create_project`（`user_confirmed=True`）。建项目后**立刻进入 Stage 1，只做角色第一步**，不要顺手建别的。

> 后端 Phase Gate 仍会校验 story_beats / character_bible / shot_breakdown 三段文本字数 + user_confirmed —— 这三段可以写得简洁（方向性描述即可），不需要把每个镜头列全。真正的纪律是：**建完项目只做 Stage 1。**

---

## 3. 执行：阶段（Stage）+ 阶段内逐节点确认（两层结构）

整体走 6 个**大阶段**（2026 工业流程），**但每个阶段内部都是"一个节点一个节点做、逐个确认"**，绝不在一个回合里把一个阶段的多个节点一次性全建出来。

```
6 大阶段（顺序固定，逐阶段推进，阶段间有 review gate）：
  Stage 1 角色  → Stage 2 场景 → Stage 3 道具(可选)
  → Stage 4 Shot Table + 生产方案选择 → Stage 5 逐镜头视频 → Stage 6 时间轴/成片
```

### 3.0 节点级标准循环（每个阶段内部都按这个走，背下来）一个阶段里通常有多个节点要做（如角色阶段有 3 个角色）。**对该阶段里的每一个节点**：

```
单节点循环（这是最小执行单位，一个回合只做这一个）：
  1. canvas_add_node 加【1 个】节点（写好中文专业 prompt）
  2. canvas_run_node 跑它（mode="only"）—— 后端同步，跑完直接返回结果
  3. 从 ran[].displayMarkdown 拿 ![名字](url) 贴进对话 + 一句说明
  4. 问用户：满意吗？要不要存素材库（canvas_subject_save）？满意我做下一个？
  5. 停下来等用户回应：
     - 不满意 → canvas_update_node_data 改 prompt → 回步骤 2 重跑
     - 满意 → （要存就 subject_save）→ 做这个阶段的【下一个】节点（回步骤 1）
```

✅ **批量规则**：步骤 4 不是“只能做一个节点”的限制，而是“必须让用户看见并批准”的 gate。用户明确同意后，可以批量 add/connect/run 当前阶段的图片节点；也可以在视频生成清单确认后批量跑视频节点。

> ⚙️ 后端已不再用逐节点守卫兜底：上游没产物也能提前建/连下游。Hermes 必须自己保证依赖顺序：先跑出角色/场景/故事板等参考，再跑依赖这些参考的视频；不要因为能连线就提前跑下游。

> ✅ Shot Table 批量通道：`canvas_expand_shot_table` 是受控批量准备通道，只能在角色卡、场景、**集级段落表已分段、当前段已选模型 + 生产路由、段内 Shot Table 镜头表已确认、段级故事板已生成/确认**之后调用。**每次只展开当前段**（不要一次展开全集！），它会按段内镜头表幂等补齐 `image(锚点/参考) → image2video → 段内 videoConcat`，并写入 `sceneId/segmentId/sourceScriptId` 便于状态、重试和时间轴管理。

✅ **阶段完成 → review gate**：该阶段所有节点都做完且用户都满意了，**停下来汇报本阶段成果 + 预告下一阶段**，等用户说"继续"才进下一阶段。

### 3.05 项目级模式开关（建项目后立刻定，影响整片）

只有两个旋钮，**默认都关**。用户没明说就走默认；明确要求时才开。

| 旋钮 | 何时开 | 怎么开 |
|---|---|---|
| **视觉自检** | 用户说"严格审核 / 质量优先 / 完美一致性"，或重要项目（节展投递 / 影视级） | `canvas_set_self_check(project_id, enabled=True, max_retries=3, pass_threshold=8)`。开了之后跑完每个 image / image2video 自动调 `canvas_evaluate_artifact` 审核；评分<阈值改 prompt 重跑（最多 max_retries 次）|
| **影视级深度模式** | 用户说"影视级 / 电影级 / 大片质感 / 上节展 / 商业项目"，或多角色 ≥3 / 长片 >90s | `canvas_set_cinematic_pro_mode(project_id, enabled=True)`。开了多 ~2.5× 配额，但会做 Beat sheet / 9 视图 multi-ref / 关键镜头 A/B 变体 / 横竖屏双输出 |

不确定时先 `canvas_get_meta(project_id)` 看现状；其它任意 meta 字段用 `canvas_set_meta(project_id, patch_json)` 改。

> 📎 **题材定下来后立刻调** `canvas_save_director_bible(project_id, look_profile=..., audio_bible=...)`，把整片色彩 + 声音档案存好（详见第 6 章末），后端会自动注入所有节点的 prompt 末尾——这是保整片色调和声音设计统一最便宜的办法。后续要查改用 `canvas_load_director_bible`。

### 3.1 Stage 1 — 角色（逐个角色做）

角色可能有多个。**默认逐个角色确认；用户明确同意后，可以批量创建/生成多个角色资产，但必须逐项展示结果供用户取舍。**

对**每个角色**，先问用户选哪条路径（成本/质量/用途差很多，2026 行业共识见下）：

```
{角色名}的角色参考有三条路，token 消耗、清晰度和用途不同，你选哪个？

A）省钱快出：直接出一张三视图同框（正+侧+背一张图）。
   一次调用搞定，但单张图把分辨率摊给 3 个视角，脸部细节相对糊。

B）高质量（我推荐）：先出一张正面脸部高清定妆照 → 你确认满意 →
   以它为锚点扩出侧面/背面 → 拼成一张三视图。
   多花 2-3 次调用和配额，但每个视角都清晰、后面锁脸最稳。

C）角色板 / 电影级角色设计表：按导演、选角、服装部用的 production board 做。
   一张图里含身份、面部、心理、表演、服装材质、转视角、头部研究、
   身高比例尺、标注和生产笔记。它不是单人肖像，也不是普通角色海报。

（不选我就走 B，按 2026 主流做法保证质量。）
```

> 📌 **为什么推荐 B**（2026 行业共识）：角色一致性靠的是"高清参考锚点"，不是更长的文字描述。一张合成三视图里每个视角被摊薄分辨率，做视频锁脸时细节不足；而"先出全分辨率正脸 → 以它为参考派生各视角"能让每个角度都清晰，身份锚点更强（专业工作流的 70/30 法则）。

- **选 A** → `canvas_generate_character_views(description=<角色 brief>, image_model="gpt-image-2", aspect_ratio=...)`（`hero_url` 留空），结果作为 image 节点入画（已 done）→ 贴图问满意。
- **选 B**（推荐，本身就是 3 个小步、逐步确认）→
  1. `canvas_add_node` 加一张 image，prompt 写"正面脸部高清定妆照"→ 跑 → 贴 → **等用户确认满意**。
  2. 满意后 `canvas_generate_character_views(description=..., hero_url=<正面图 url>)` 扩侧/背 → 贴 → 等确认。
  3. `canvas_compose_contact_sheet([3 张 url])` 拼成三视图 pose sheet → 贴 → 等确认。

> 📎 **B 路线 spawn 子节点提示**：image 跑完后后端会自动 spawn N 个独立 image 子节点（每个角度一个）。要把它们用作 image2video 的 `subjectRefs` 时，先 `canvas_get_spawned_children(project_id, parent_node_id)` 拿到子节点 ID 列表，挑 1-3 个最合适的（正面+一个侧面+contact sheet 即可）调 `canvas_connect` 连到 `(image2video, "subjectRefs")`。**不要把所有子节点全连**，超过 3 张后端只取前 3。画布乱了再 `canvas_clean_old_spawn_batches` 清非最新批次。
- **选 C**（角色板 / 设计表）→
  1. `canvas_add_node` 加一张 image，`aspectRatio` 固定写 `"16:9"`，prompt 使用第 5.2.1 的“电影级角色设计表”模板，把用户角色设定填进去。
  2. 跑 → 贴 → 先自检：是否是多分区 production board？是否含转视角、头部研究、服装材质、标注、身高比例尺、生产笔记？电影肖像是否只是小分区？
  3. 如果变成单人肖像 / 半身照 / 普通海报 / 一个人占满画面，判定失败，强化“多分区角色设计表，不是肖像”后重跑。

这个角色满意了（+ 问要不要存素材库）→ **如果还有别的角色，做下一个角色**（重复上面）。
所有角色都做完、用户都满意 → 汇报"角色阶段完成，下一步做场景" → 等用户"继续" → 进 Stage 2。

### 3.2 Stage 2 — 场景（逐个场景做）

**默认逐个场景确认；用户明确同意后，可以批量创建/生成多个场景资产，但必须逐项展示结果供用户取舍。** 每个场景先问用户选哪条路径：

```
{场景名}也有两条路：
A）省钱：直接出一张该场景代表图（单一机位/时段）。
B）高质量（推荐多机位的剧）：先出场景主图 → 确认 → 以它为锚点派生
   不同机位/时段（白天/夜晚、远景/近景），保证整片同一空间不穿帮。
你要 A 还是 B？
```

- 选 A → 1 个 image 节点 → 跑 → 贴 → 等确认。
- 选 B → 先出主图 → 贴 → 确认后逐个派生其它机位，每个都跑完贴出来等确认。

> 场景 image 的 prompt **严格按 5.5 的场景模板写**（地点/时段/关键陈设≥3/光线/大气/镜头/色板/要避免的）。派生其它机位时把主图作 reference 连进去，prompt 写"与参考图同一地点、同样陈设与色温，仅切换到 {新机位}"。

这个场景满意了（+ 问存不存素材库）→ 有下一个场景就接着做 → 全部场景做完 → 汇报 → 等"继续" → Stage 3。

### 3.3 Stage 3 — 道具（如剧情需要，逐个做）

关键道具（法器/信物/产品）**一次一个**，各 1 张 image → 跑 → 贴 → 确认 → 下一个。没有关键道具就跳过这阶段（告诉用户"无关键道具，直接进故事板"）。

### 3.4 Stage 4 进入前的 review gate

角色+场景+道具都做完、用户都满意了，**停下来汇报 + 进入分段策略**：

```
✅ 素材阶段完成：角色 N 个、场景 M 个、道具 K 个（都在画布上，满意的我帮你存了素材库）。
下一步我先把整集（{总时长}s）拆成几个段落（segment），每段一张段级故事板覆盖该段所有镜头。
段落数取决于：①剧情节拍 ②你选的视频模型单镜上限 ③总时长 ④画幅。
告诉我你心里有几段？或我先按三幕节拍 + 模型能力提一个段落表，你审。
```

**注意**：到这一步才和用户敲定「段落怎么分」 —— 因为现在角色/场景已定，模型能力已知，才能分得合理。**绝不能直接给整集出一张总故事板**。

### 3.5 Stage 4 — 段落（segment）+ Shot Table + 生产方案选择（一段一段做）

**核心理念**：1 集 1 分半 ≠ 1 张故事板。1 集 = N 段（segment），每段 = 一张**段目标卡** + 一张段内 Shot Table + 可选/推荐的段级故事板 + 若干个 **15 秒视频单元**。N 由"剧情节拍 + 15s 单元上限 + 总时长"动态决定，不是固定数字。**v20 主力视频生产统一按 15s 单元规划：Seedance 2.0 和 Happy Horse 都按一个视频 15s 设计提示词、Shot Table 和故事板。**

**先理解 Shot Table 和 Storyboard 的区别：**

| 项 | Shot Table 镜头表 | Storyboard 故事板 |
|---|---|---|
| 本质 | 生产清单 / 拍摄表 / 数据结构 | 视觉导演板 / 可给模型看的图像参考 |
| 回答的问题 | “要拍哪些镜头？每镜几秒？谁在场？景别/运镜/声音是什么？” | “这些镜头长什么样？角色站哪？光影、构图、运动方向怎么连续？” |
| 形态 | `scriptGen.outputs.scenes` 表格字段，可编辑、可展开流水线 | 一张或多张 image 节点，3-6 格镜头卡，含箭头、编号、构图和备注 |
| 用途 | 驱动 `canvas_expand_shot_table` 生成 image/image2video/videoConcat 节点 | 给用户审美确认，也作为 Seedance/视频节点的 subjectRefs 参考 |
| 谁更精确 | 时间、字段、执行顺序更精确 | 画面、空间、角色站位、情绪更直观 |

一句话：**Shot Table 是施工单，Storyboard 是导演视觉图。** 先用段目标卡确定“这一段为什么拍”，再用 Shot Table 定“拍几镜怎么拍”，再用 Storyboard 看“拍出来应该长什么样”。

#### 3.5.1 第一步：拆段（先确认段落策略）

1. `canvas_add_node(kind="scriptGen")` 创建**集级三幕段落表**节点。prompt 重点写：
   - 已确认的角色卡、场景、道具
   - 集级总时长 / 画幅 / 题材
   - **要求输出 segments 数组**（不是逐镜头！）：每段含 `segmentId / title / startSec / endSec / dramaticBeat / sceneRef / characterFocus / shotCount`
   - 段数自由：根据剧情节拍 + 时长合理分；**每个视频节点按 15s 单元规划**；典型 60s 短片约 4 个 15s 单元 / 90s 漫剧约 6 个 15s 单元；若一个剧情段超过 15s，必须拆成多个连续 15s 镜头单元
2. `canvas_run_node(scriptNodeId, mode="only")` 跑出 `outputs.segments`。
3. 把段落表摘要贴给你看（段号 / 标题 / 时长 / 节拍 / 涉及角色场景），问：
   - 段落划分对不对？要不要合并 / 拆分某段？
   - 先做哪一段？（默认从第一段开始，钩子段优先）

#### 3.5.2 第二步：写段目标卡（Segment Brief，必须）

段落表确认后，进入某一段前，必须先写**段目标卡**。它不是 Shot Table，也不是故事板；它是这一段的导演意图说明，防止后面的镜头表变成机械切镜。

段目标卡必须包含 8 项：

| 字段 | 要回答的问题 |
|---|---|
| `segmentGoal` | 这一段推进了什么剧情？观众看完应该知道/感受到什么？ |
| `emotionalCurve` | 情绪如何变化？例如：压抑 → 怀疑 → 爆点 / 松弛 → 惊吓 → 反转 |
| `visualMotif` | 视觉母题是什么？例如红伞、碎镜、月光、监控屏、断剑、雨水反光 |
| `characterFocus` | 这一段重点锁谁？谁的表情/动作最重要？ |
| `conflictBeat` | 冲突点/爽点/反转点在哪里？必须一句话说清 |
| `cameraStrategy` | 总体镜头策略：快切/长镜/手持/固定观察/由远到近/压迫特写 |
| `soundStrategy` | 环境声、Foley、音乐、对白进入/退出策略；是否需要 J-cut / L-cut |
| `transitionPlan` | 和上一段/下一段怎么接：动作接力、视线接力、颜色接力、match cut |

输出段目标卡后贴给用户确认：

> 这一段我先按这个导演目标来拆 Shot Table，对吗？要调整情绪/视觉母题/声音策略吗？

用户确认后，才进入模型与生产路由选择。

#### 3.5.3 第三步：选这一段用哪个视频模型 + 生产路由

每段的模型可以不同（钩子段用最强、过场段用便宜、对白段用 nativeAudio）。先调 `canvas_list_video_models()`，按这一段的需求过滤：

| 需求 | 推荐模型 |
|---|---|
| 段长 4-15s 灵活 + 音频同步 | Seedance 2.0（doubao-seedance-2-0-260128，诗云）/ Vidu Q3 Pro |
| 8s 必须 + 双关键帧锁定 + 4K | Veo 3.1 Fast 4K |
| 6/10s 短片 + 首尾帧 | Hailuo 02 |
| 长镜 12s + 复杂物理 | Sora 2 Pro |
| 段内多镜头 ≥ 3 + 角色一致 | Kling Multi Elements / Components 模式 |

确认模型后，让用户选这一段的 5 种 `generationMode` 之一（v17 已结构化为节点字段）：

| 模式 ID | 名字 | 适用 | 必需输入 |
|---|---|---|---|
| `text2video` | 文生视频 | 探索镜头、Animatic 草稿 | 仅 prompt |
| `ref` | 全能参考 | 多角色 / 多元素的复杂段，纯 reference-to-video | `subjectRefs` ≥1（image 留空） |
| `i2v` | 图生视频 | 经典首帧驱动 | image 首帧 |
| `ff` | 首尾帧 | 强动作准确 / 转场 | image + tailFrame（模型须 tailFrame=true） |
| `imgRef` | 图片参考 | 首帧 + 风格参考 | image + subjectRefs |

#### 3.5.4 第四步：拆这一段的 Shot Table（不是整集！）

段目标卡、模型和生产路由都确认后，针对**当前这一段**（不是整集）拆镜头：

1. `canvas_add_node(kind="scriptGen")` 再创建一个**段级 Shot Table** 节点，prompt 写：
   - 当前段的 `startSec / endSec / dramaticBeat / sceneRef`
   - 已确认的段目标卡 8 项（剧情目标、情绪曲线、视觉母题、角色焦点、冲突点、镜头策略、声音策略、转场策略）
   - 选定的视频模型 + 生产路由 + **15s 单元上限**
   - 段内镜头数（按 15s 单元拆分：15s=1 镜头单元，30s=2 镜头单元，45s=3 镜头单元；每个单元内部再用 3-5 个动作节拍描述，不再拆成 5s 小视频）
   - 镜头字段：`shotId / startSec / endSec / shotSize / cameraMovement / action / lighting / sound / aspectRatio`
2. `canvas_run_node(mode="only")` 跑出 `outputs.scenes`（段内的镜头表）。
3. （可选）`canvas_run_script_doctor` 评审段内节奏/视觉化；critical/high 级建议改完再下一步。
4. 把段内镜头摘要贴给用户确认。

#### 3.5.5 第五步：画段级故事板（一张图覆盖这一段所有镜头）

1. `canvas_add_node(kind="image", aspectRatio="16:9")` 创建**段级故事板总览板**。
   - prompt 用 5.6 模板，但**只覆盖当前段 / 当前 15s 视频单元**（建议 3-6 格动作节拍卡，不是全集 9 格）
   - 标题写 `{集名} · 第 {N} 段：{段标题}`
   - 底部信息区写明：当前段时长、节拍、选定模型、生产模式
2. `canvas_run_node(mode="only")` 跑出来贴给用户。
3. 段级故事板满意后才进 Stage 5（这一段的视频生成）。

#### 3.5.6 段间衔接

- 第一段做完后，如需衔接，优先把上一段成片抽取的末帧或关键帧作为**普通 subjectRefs / 场景延续参考**喂给下一段；不要把 `tailFrame` 当成强锁定能力，因为 v20 主力 Happy Horse / Seedance 2.0 当前都不支持真正首尾帧字段。
- 段间镜头朝向 / 光线 / 主色调延续：在第二段 Shot Table prompt 里写"承接第 1 段第 N 镜的运动方向 / 主色调"。
- 全集的 `videoConcat` 在所有段都完成后建（见 3.7）。

### 3.6 Stage 5 — 段内逐镜头视频

按段内 Shot Table + 选定 generationMode 执行：
1. `canvas_expand_shot_table(project_id, scriptNodeId)` 受控展开**这一段**的 image(锚点) → image2video → 段内 videoConcat 流水线。
2. 按生产路由补连参考：
   - `text2video`：仅用于草稿或探索镜头，正式昂贵视频前必须再次确认。
   - `ref` / 全能参考（Seedance 2.0 推荐）：把角色 contact sheet / 场景 / 道具 / 段级故事板连到 `subjectRefs`（≤3 张；多图先 `canvas_compose_contact_sheet` 拼成 1 张）。`image` 端口留空，让模型按参考+prompt 自由拍。
   - `i2v`：只在需要严格首帧构图时连 `image`。
   - `ff`：仅模型明确支持 tailFrame 时使用；Seedance 2.0 不按首尾帧硬锁时不要假装支持。
   - `imgRef`：首帧连 `image` + 风格 / 角色参考连 `subjectRefs`。
3. **视频生成二次确认（硬闸）：** 展示将要跑的镜头列表、每个镜头连接的参考图含义、模型、时长和成本风险，问用户：“是否现在开始生成这些视频？” 用户明确同意前，禁止执行任何视频 `canvas_run_node`。
4. 用户确认后，逐个 `canvas_run_node(mode="only")` 跑（每段约 4 分钟）。
5. 段内视频跑完后，段内 `videoConcat` 也是视频/成片动作，仍要问用户是否拼接；确认后再跑 → 段成片。贴给用户审。
6. 用户认可后进入下一段（回 3.5.2 段目标卡 / 3.5.3 选模型与生产路由 / 3.5.4 拆镜头 / 3.5.5 画段级故事板）。失败只重试该镜头，不重跑整段。

### 3.7 Stage 6 — 集级时间轴 + 成片

所有段都跑完且用户都认可后：

1. 在画布上新建一个**集级 `videoConcat`** 节点，`videoOrder` 列出所有段的成片节点 ID（按段序）。
2. `canvas_update_node_data` 改 `cutPattern`（紧张段 `rapid-cut` / 抒情段 `j-cut/l-cut` / MV 卡点 `montage`）、`segmentTrims`、`crossfadeSeconds`、`bgmUrl`、`bgmVolume`。
3. **BGM / 音效**：
   - 整集 BGM → `canvas_run_music_gen(prompt="...", duration=<整集时长>, model="audio1.0")`；audio_url 写进 `videoConcat.bgmUrl`。
   - 段间不同情绪 → 用 `timing_prompts=[{"from":0,"to":15,"prompt":"鸟鸣晨光"}, ...]` 卡点 BGM。
   - 已存 `audioBible` 时，把 `audioBible.themeMusicStyle` 喂给 music_gen 保持声画一致。
4. `canvas_run_node(集级 videoConcat, mode="only")` 拼成片，把 `displayMarkdown` 贴给用户。
5. 用户要导出 → `canvas_save_artifact(url=最终视频 url, relative_path="Canvas/<项目名>/episode_<N>_final.mp4")`。

> 多集项目：每集开一张 subcanvas（`canvas_create_subcanvas`），main 画布保留集级 videoConcat 时间线。

> 🔖 2026 现状：主流视频模型一次可吃多个参考（身份图/运动参考/音频参考），但不同后端上限不同。本画布后端单节点 subjectRefs 取前 3 张 —— 角色多于 3 个或需要更多锚点时，用 `canvas_compose_contact_sheet` 把多张参考拼成 1 张再喂进去（这也是低 ref 上限模型的标准绕法）。

> 🧰 **不太常用但偶尔救场**：
> - 用户给参考图想抄风格 → `canvas_run_reverse_prompt(image_url)` 拿 6 段中文 prompt，再 spawn / 套用到新节点。
> - 想"演绎 3 秒后 / 5 秒前" → `canvas_run_temporal(image_url, direction="after"|"before", seconds=3)`，结果作为子节点回到画布。
> - 16:9 想剪成 21:9 宽银幕、或 1:1 想升 16:9 → `canvas_outpaint(image_url, target_ratio="21:9")` 扩边而不重画主体。
> - 想给道具/角色去背景重组 → `canvas_cutout(image_url)`。
> - 用户给参考视频说"复刻这种镜头语言" → `canvas_film_analysis(video_url)` 拿到分镜表 + 每镜可复用 prompt。

---

## 4. 导演功夫：叙事 · 节奏 · 剪辑衔接（决定"好看"，不是"能看"）

> ⚠️ 这一章是把"一堆漂亮镜头"变成"一部抓人的片子"的关键。技术再好，没有叙事节奏和剪辑逻辑，成片也是散的。**做故事板（Stage 4）和写每个镜头时，必须用这一章的规矩。**

### 4.0 核心心态（2026 实战派共识）

> 大多数人生成 5 个漂亮的 4-6 秒片段丢到时间线上配个热门音乐——**那不是电影，是"算法序列"，对观众毫无要求**（theailab）。真导演的功夫在：镜头有意图、镜头之间有逻辑、整段有情绪曲线。

### 4.1 叙事结构：竖屏微剧的"黄金节拍"（必须照搬）

2026 微剧（短剧/漫剧）是**为竖屏 9:16、60-90 秒一集、靠悬念驱动连看**而生的（businessabc / jenova / 耶鲁短剧研究）。每集严格三段：

| 时间段 | 任务 | 怎么做 |
|---|---|---|
| **0-3 秒：钩子** | 3 秒内必须抓住，否则划走 | 开场就是最强冲突：扇耳光 / 揭秘身份 / 背叛 / 反转。**绝不**用平淡的环境铺垫开场 |
| **3-45 秒：冲突升级** | 快节奏推进 + 压缩到情绪精华的对白 | 矛盾一层层加码，信息密度高，**台词只留情绪最浓的**，废话全删 |
| **46-60/90 秒：悬念钩子** | 结尾留一个"必须看下一集"的悬念 | 在最吊胃口处戛然而止：新威胁出现 / 真相半露 / 选择关头 |

**情绪曲线**：困境 → 虐点（憋屈/不公）→ 反转 → 爽点（打脸/逆袭/真相大白）。**爽点和钩子前置**，别让观众等。
- 立项（第 2 章）和故事板（Stage 4）时，先把这条情绪曲线和三段节拍跟用户对齐，再排镜头。

### 4.2 镜头节奏：景别呼吸 + 时长节奏

- **景别要"呼吸"，不要同景别硬接**：大远景(交代环境/气势) → 全景(交代人物全身/动作) → 中景(对话/情绪) → 特写(情绪爆点/关键道具) → 大特写(眼神/细节)。一个段落里远-中-近交替，张弛有度。
- **覆盖（coverage）要全**：哪怕一个简单对话，也要有 establishing(交代空间) + 中景(说话) + 反应特写(听的人)。只有正面中景 = 平。
- **时长 = 情绪**：紧张/动作镜头短(1.5-3s 快切)，抒情/留白镜头长(4-6s)。漫剧整体偏快，黄金 3 秒尤其要密。
- **进特写前先给全景**：让观众知道"在哪、谁、什么关系"，再推近看情绪。上来就大特写=观众懵。

### 4.3 剪辑语法：三条铁律（AI 片最常翻车的地方）

1. **30° 规则**：相邻两个镜头，机位至少变 **30 度**（或换景别）。机位几乎没变就硬接 = **跳切（jump cut）**，画面会"抖一下"很廉价。所以故事板相邻格的角度/景别要明显不同。
2. **180° 轴线规则**：一场戏里，摄像机要保持在角色关系连线的**同一侧**。A 在左、B 在右，下一个镜头不能突然翻到另一侧（否则 A、B 左右互换，观众瞬间迷失方向）。故事板里写清每个镜头角色的**朝向/站位**，保持一致。
3. **视线/动作连戏**：上一镜角色看向画面右外，下一镜被看的东西就该在能对上的位置；上一镜动作做到一半，下一镜接着那个动作。

### 4.4 镜头衔接：Transition Engineering（AI 片"高级感"的分水岭）

> leeveo 反复强调：别想"镜头1 → 镜头2"硬切，要想"**同一个世界在连续演变**"。这是 AI 片看起来像电影还是像 PPT 的关键。

落到 image2video 的 prompt 上，**让相邻两镜的运动咬合**：
- **运动接力**：上一镜结尾是"镜头向左推"，下一镜开头就"延续向左的运动进入新画面"——运动方向不断，观众感觉是一镜到底。
- **匹配剪辑（match cut）**：用形状/动作/构图相似来接（上一镜的圆月 → 下一镜的灯笼；上一镜挥剑下劈 → 下一镜刀光落地）。
- **J-cut / L-cut（声音搭桥）**：下一镜的声音/对白**提前**到上一镜末尾响起（J-cut），或上一镜的声音**延续**到下一镜开头（L-cut）——让对话和场景过渡顺滑，不"啪"地一刀切。
- **遮挡转场 / 同色过场**：用物体扫过镜头、或前后镜头主色调一致来藏接缝。

> 写 image2video 时，**有意识地给每个镜头设计"入点运动"和"出点运动"**，让它能和前后镜头咬合，而不是每个镜头都"静止→动→静止"。

### 4.5 把导演功夫落进流程

- **Stage 4 故事板**：排镜头时就按 4.1 的三段节拍组织，相邻格遵守 4.2 景别呼吸 + 4.3 的 30°/180°/连戏（在每格写清角色朝向和景别角度，避免跳轴跳切）。
- **Stage 5 逐镜头视频**：写 image2video prompt 时按 4.4 设计运动衔接（入点/出点运动、为 J/L-cut 留声音）。
- **Stage 6 成片**：`videoConcat` 拼接时，紧张段用快切（短 crossfade 或硬切），抒情段留长一点；卡 BGM 节拍。

---

## 5. 提示词标准（2026，自然语言结构化 —— 不是关键词堆砌）

> 2026 主流图像模型（Nano Banana / Gemini 3 Image / GPT-image / Seedream / Flux.2）**偏好自然语言的结构化描述段落**，不是逗号分隔的关键词标签。**Flux.2 / Nano Banana 没有 negative prompt 字段** —— 要排除的东西用正面语言写进描述（"干净纯色背景"而非"no clutter"）。SD 时代那套"权重括号 + 一长串 negative"已过时。

> 本章子节：5.1 通用结构 · 5.2 角色锚点(含范例) · 5.3 视频运动 · 5.4 镜头词典 · **5.5 场景/环境 prompt(含范例)** · **5.6 故事板网格 prompt(含范例)**。每个资产类型都有专门写法和填好的范例，照着仿写。

### 5.1 图像 prompt 的结构（写成连贯描述，分这几层信息）

按这个**信息顺序**写成自然语言段落。画布内置模板常用 `【主体】/【场景】/【光影】/【镜头】/【风格】/【负面】` 六段标签；可以保留这些中文标签，但每段里面要写完整句子，**不要写成逗号关键词堆砌**：

1. **主体 + 身份锚点**：谁，精确外形（脸型/眼型/发型/肤色），服饰材质，标志物。越具体越不漂移。
2. **动作 / 姿态 / 表情**：在做什么，情绪。
3. **场景 / 环境**：地点、时段、天气、关键陈设。
4. **光线**：主光方向 + 色温 + 软硬 + 反差（如"左上方冷蓝月光，暖橙烛火补边，强反差"）。
5. **镜头语言**：景别 + 角度 + 焦距 + 构图 + 画幅。
6. **风格**：电影感/水墨/赛璐璐动画/写实纪录 等，加质感词（胶片颗粒/通透/高级灰）。
7. **要避免的**（用正面表述）：如"五官端正对称、双手五指正常、背景干净无文字水印"。

字数：角色/场景图 150-300 字中文足够（**不是越长越好，是越精确越好**）。

### 5.2 角色身份锚点（不崩脸的关键）

角色 brief 必须写死这些（模糊描述 = 60% 漂移；精确 = 90% 一致）：
- **脸**：脸型骨架、眉形、眼型+眼神、鼻、唇形+嘴角状态、肤色。
- **发**：颜色、长度、发型、材质（直/卷、光泽）。
- **服饰材质**：具体面料（"棉麻哑光"而非泛泛"袍子"）、颜色、纹样、配饰。
- **标志物 ≥3**：疤痕/法器/挂饰/特殊瞳色等。
- **表情基线**：定妆照写 neutral（自然平静、不笑不说话）；**情绪留到镜头里再加**，否则跨镜头永远在笑。

> 2026 实战（aimeetsgirlboss "named reference sheets"、leeveo 角色设计表）的关键洞察：**一致性来自高清参考锚点，不是更长的描述**。所以定妆照 prompt 不必堆砌，但上面 5 类锚点要写死、写具体。

**范例 · 武侠少年剑修定妆照（正面，neutral）：**
```
正面半身定妆照，一名约 20 岁的清冷少年剑修。脸：清瘦的鹅蛋脸、骨相分明，剑眉
斜飞入鬓，丹凤眼眼神沉静微冷，鼻梁高挺，薄唇平抿不带情绪，肤色冷白。发：墨黑
长发束成利落高马尾，几缕碎发垂在颊侧，发质直而有光泽。服饰：交领白色棉麻哑光
长袍，袖口与下摆染着旅尘的灰黄，腰间束深青色布带。标志物：左眉尾一道浅疤、颈
侧一圈暗红色枷锁状道痕、腰侧挂一枚墨玉剑穗。表情自然平静、不笑不说话、平视镜
头。纯色浅灰摄影棚背景，柔和均匀的正面光，电影感，高级灰冷青调，皮肤质感真实。
五官端正对称，双手五指正常，画面干净无文字水印。
```

### 5.2.1 电影级角色设计表 prompt（C 路线专用）

当用户要“角色卡 / 角色板 / 设计表 / 给导演选角服装部看的角色 reference”时，用下面模板。**这张图必须是一张艺术指导过的 production board，不是单张人物肖像**。

```
为导演、选角和服装部制作电影级角色设计表。名称：{角色名}。输出画幅：横版 16:9 宽幅 production board，绝对不要 9:16 竖版。需像高预算动画提案板，不是单张人物肖像、不是半身写真、不是纯人物海报。
核心指令：禁止通用布局、均匀网格或对称。构图需经艺术指导、有意为之且略带不对称。每部分精心放置，非自动生成。
角色身份：姓名：{全名} | 别名：{昵称} | 年龄：{真实/风格化} | 身高：{cm/ft} | 体型：{比例、姿势倾向} | 种族/设计语言：{如 Pixar 风格、动漫启发、文化根植}。
面部设计：结构：{脸型、骨骼、夸张度} | 皮肤：{色调、质感、瑕疵} | 眼睛：{间距、颜色、表现力} | 头发：{动态、不完美处} | 独特特征：{疤痕、酒窝、痣}。
心理侧写：核心特质：{3-5 种人格} | 内在冲突：{想要什么 vs 什么阻碍} | 行为模式：{3 种习惯} | 情感基线：{默认情绪 + 变化速度}。
表演指导：捕捉真实演员的“中间时刻”，非摆姿势。需微表情，例如唇部紧张、眼神闪烁、眉毛移动。避免舞台化对称，捕捉过渡情感。
肢体语言：{姿势倾向} | {动作节奏：僵硬/锐利/有弹性} | {闲置行为：烦躁/静止/紧张}。
服装与材质：服装1：{面料、磨损} | 服装2：{贴合度、缝合} | 叠穿逻辑 | 鞋履：{材质、磨损模式} | 配饰与道具：{强化身份的物体}。
材质准确性：面料显示拉伸、缝合、褶皱。禁止塑料感。皮肤需柔和光线互动（SSS）。包含不完美：污垢、污渍、老化、使用痕迹。
转视角（严格）：全身正面、3/4侧、侧面、背面、3/4背面视图。比例和设计保真度完全相同。任何角度下脸部或服装不得漂移。
头部研究：正面（中性） | 3/4侧（主要个性） | 侧面（结构） | 低头 | 抬头 | 动态角度（强烈状态）。所有表情均为“中途思考”，非摆姿势。
一致性规则（不可谈判）：脸部、比例、服装和细节在所有视图中必须保持完全相同。角度之间不得重新诠释。永远。
电影肖像：这是角色板中的一个小分区，不是整张图主体。环境：{相关地点} | 灯光：{对比度、光源} | 色调：{暖/冷/风格化} | 表情：{叙事时刻} | 镜头：{50/85mm、浅景深、电影感}。
布局与输出：艺术指导过的表格，中性灰色背景。必须包含身高比例尺、标注说明、生产笔记、多视角全身转面、头部研究、材质细节块、表演备注块。风格：{如 Pixar 风格化现实/半现实}，含吸引人的夸张、柔和几何、电影灯光。
输出：极高细节，锐利焦点，制作就绪保真度，适合电影开发、商品化和提案。严禁输出单个站立人物照片、单人半身照、普通城市肖像或只有一个人物占满画面。
```

### 5.3 视频 prompt（image2video）—— 15s 单元 + 参考图感知

v20 主力视频节点按 **15 秒一个视频单元** 写 prompt。不要再按 4-6s 小镜头写；Shot Table、故事板和视频 prompt 都要围绕 15s 单元设计。一个 15s 单元内部可以有 3-5 个动作节拍，但仍是**同一个视频节点**。

**首帧/尾帧判断：**当前 bagege 主力 Happy Horse / Seedance 2.0 都不支持真正 tailFrame 强锁定。LibTV 风格更偏“渐进式画布 + 参考素材拼接”：多选图片拼成 contact sheet / subjectRefs，再让视频节点按连接关系自动 dispatch。因此本 skill 不主动追求首尾帧；只在用户明确要求“从 A 构图过渡到 B 构图”时，把尾帧作为普通参考图和 prompt 中的“结尾构图参考”，不要承诺精确落到尾帧。

视频 prompt 必须包含 9 段：
1. **【参考图关系】**：逐张说明图 1/图 2/图 3 分别是首帧、角色、场景、道具、段级故事板或上一段末帧参考；不要只写“参考这些图”。
2. **【15s 时间结构】**：0-3s 建立/钩子，3-9s 主动作推进，9-13s 情绪/动作峰值，13-15s 收束到可接下一镜的姿态。
3. **【主体锁定】**：角色身份、服饰、标志物、表情基线。
4. **【场景锁定】**：地点、关键陈设、时段、色温、气氛。
5. **【本单元动作】**：一个主动作弧线，可分 3-5 个连续小节拍；不要塞多个互不相关的大动作。
6. **【运镜与构图】**：一个主运镜 + 必要的轻微二级运动；避免一会儿推一会儿甩一会儿环绕。
7. **【光影与气氛】**：主光方向、色温、天气/粒子/衣物/水汽等自然运动。
8. **【声音】**：环境声、Foley、短对白/无对白；Seedance/Happy Horse 原生音频时要写清。
9. **【稳定性约束】**：不换脸、不换衣、不新增人物、不生成字幕水印、运动连续。

**15s 范例结构：**
```
【参考图关系】参考图1是段级故事板，控制镜头顺序和构图节奏；参考图2是主角角色板，控制脸、服饰和标志物；参考图3是剑冢场景图，控制空间、断剑林、青冷薄雾和黄昏光线。
【15s 时间结构】0-3秒：镜头从断剑林低位缓慢推入，主角背影静立；3-9秒：主角右手握住剑柄，衣袖和发丝被风带起，镜头继续缓慢推近到中近景；9-13秒：他猛然抬眼，断剑微震，尘埃被震起，情绪到达爆点；13-15秒：动作停在眼神特写和剑柄震动的姿态，为下一段 match cut 做准备。
【主体锁定】保持角色板中的同一张脸、黑发高马尾、白色棉麻长袍、左眉尾浅疤、颈侧暗红道痕和墨玉剑穗。
【场景锁定】保持剑冢空间，断剑林、半塌青石牌坊、远处孤峰、青冷薄雾、黄昏暖橙逆光。
【运镜与构图】一个稳定缓慢推镜，低机位到中近景，不跳切，不突然旋转。
【声音】低风声、金属微震、衣料摩擦，最后 2 秒加入低频轰鸣，无对白。
【稳定性约束】不换脸不换衣，不新增人物，无字幕水印，运动连续自然。
```


### 5.4 镜头语言词典（按需取用，写进描述）

- **景别**：大远景/远景/全景/中景/中近景/特写/大特写。
- **角度**：平视/仰拍(力量感)/俯拍(脆弱感)/鸟瞰/荷兰角(不安)/过肩/POV。
- **运镜**：固定/平移/推/拉/跟拍/环绕/手持/升降。
- **焦距**：24mm广角(透视张力) / 35-50mm标准 / 85mm+长焦(压缩虚化)。
- **光**：伦勃朗光/侧光/逆光剪影/黄金时刻/蓝调时刻/实用光源/高低调/主光+边缘光。
- **色温**：3200K暖橙 / 5500K中性 / 6500K冷蓝；调性：青橙/青冷/单色。

### 5.5 场景 / 环境 prompt（建"场景设计表"，不是只出一张图）

2026 实战（leeveo "production board"、Seedance transition-engineering 派）的共识：**场景要当成一个"可复用的空间"来建，而不是一张孤立的图**。核心思维从"场景1→场景2"换成"同一个世界在镜头间实时演变"——这样跨镜头空间才不穿帮。

**场景图 prompt 的信息层（写成连贯中文段落，150-350 字）：**

1. **地点定义**：什么空间（剑冢/竹海/丹房/城楼…），规模感，建筑/自然结构。
2. **时段 + 天气**：清晨薄雾 / 正午烈日 / 黄昏残照 / 夜雨 —— 这一条决定整场色温，要和 director bible 一致。
3. **关键陈设 ≥3**（场景的"标志物"，等同角色的标志物，锁场景一致性的关键）：如"断剑插地成林、青苔石阶、半塌的牌坊"。
4. **光线**：主光来向 + 色温 + 软硬 + 体积感（如"侧逆的金色斜阳穿过竹叶，地面长投影，丁达尔光束"）。
5. **大气/材质**：雾/尘/水汽/反光/颗粒，决定"高级感"。
6. **镜头**：景别（场景一般用大远景/远景做 establishing）+ 角度 + 焦距 + 画幅。
7. **风格 + 色板**：和全片统一的调色（如"青冷调，电影感，胶片颗粒，高级灰"）。
8. **要避免的**（正面表述）：如"画面干净无文字水印、无现代物件、无穿帮人影"。

> 📌 **多机位一致性的写法（选高质量路径 B 时）**：先出一张该场景的 establishing 主图并存素材库；做其它机位时，**把主图作 reference 连进去**，prompt 里写"与参考图同一地点、同样陈设与色温，仅切换到 {新机位/景别}"——靠参考图锁空间，靠这句话换视角。leeveo 的高阶做法是出一张"环境设计表"：含俯视平面图 + 侧视立面图 + 机位标记，作为整场的空间圣经。

**范例 A · 武侠 establishing（大远景）：**
```
苍茫剑冢，万千断剑斜插于龟裂的黑色岩原，远处孤峰耸立云海之上。黄昏残照，天
光由橙红过渡到墨青，强反差。关键陈设：近景三柄半锈古剑插地成林、中景一座半
塌的青石牌坊爬满枯藤、远景一道窄长石阶通向峰顶。主光是低角度的暖橙残阳从画
面右后方斜射，在断剑间拉出长长的冷青色投影，空气里浮动金色尘埃与薄雾，丁达
尔光束。大远景，略仰角，24mm 广角强透视，竖屏 9:16。电影感，水墨写意与写实
结合，高级灰青橙调，胶片颗粒。画面干净，无文字水印，无现代物件，无穿帮人影。
```

**范例 B · 都市夜景室内（中景场景）：**
```
深夜独居公寓的客厅，约 20 平米，落地窗外是模糊的城市霓虹。关键陈设：一张磨
旧的灰布沙发、茶几上半杯凉掉的咖啡与摊开的旧相册、墙上一台走时的挂钟显示
2:40。唯一光源是窗外冷蓝的霓虹与一盏暖黄落地灯，冷暖对冲，低调布光，大面积
阴影。空气安静，有轻微尘埃悬浮。中景，平视，35mm 标准镜，竖屏 9:16。写实
生活质感，柔和颗粒，青蓝主调里一点暖黄，高级灰。画面干净无水印，无多余人物。
```

### 5.6 段级故事板 prompt（A 路线：单个 15s 视频单元）

本流程**不需要集级总览板**。故事板只服务当前段 / 当前视频节点：**一张图 = 1 个 15s 视频单元的 Seedance-friendly 段级故事板**。它不是全集蓝图，不是角色设定板，不是电影海报，也不是把 60/90 秒整集塞进一张图。

#### 5.6.1 15s 故事板要分几格？

不要固定 4 格。2026 Seedance/GPT-Image 实战里常见 3×3（9 格）、5×3（15 格）、7-section brief、甚至 15 shots in one video 等做法。结论是：**格数取决于运动复杂度，不取决于死模板**。

本 skill 采用默认规则：

| 15s 单元类型 | 推荐格数 | 何时用 |
|---|---:|---|
| 简单情绪 / 单人轻动作 | 5 格 | 抬头、转身、凝视、产品单一展示 |
| 标准 AI 漫剧 / 角色 + 场景 + 情绪变化 | 6-8 格 | 默认推荐，兼顾可读性与连续性 |
| 动作戏 / 追逐 / 打斗 / 多角色调度 | 9 格（3×3） | 需要明确动作方向、破坏节拍、机位变化 |
| 广告 / 产品叙事 / 多卖点 | 7 格或 9 格 | 开场钩子、痛点、展示、证明、CTA |
| 极复杂广告或多信息段 | 最多 12-15 格 | 只在用户明确要高控制力时用；小字会变差，要保持标签极短 |

**默认：每个 15s 段级故事板用 6-8 格。** 4 格只适合很简单的单动作镜头；漫剧默认不要只做 4 格，因为 15s 内通常需要钩子、推进、反应、峰值、收束、衔接，4 格容易漏掉反应和声音节拍。

#### 5.6.2 段级故事板必须包含

1. **标题条**：`{片名} · 第 {N} 段：{段标题}`，写明 `15s / 画幅 / 模型 / 生产路由`。
2. **角色参考条**：主角/配角小缩略图、服装锚点、标志物、关键道具；只做参考，不抢主画面。
3. **场景参考条**：当前场景、关键陈设、光线、天气、色板。
4. **动作节拍格**：5-9 个为主，每格一个短画面，必须有编号、时间码、景别/运镜、主动作、情绪/声音短标签。
5. **箭头系统**：用清晰箭头标出阅读顺序、角色运动、摄像机运动、视线方向或能量流向。
6. **底部生产备注**：段目标卡摘要、声音策略、参考图连接策略（例如“角色板 + 场景图 + 本故事板 → subjectRefs”）。
7. **版式要求**：16:9 横版，专业电影预制作看板，信息图式排版，短标签可读；不要长段小字，不要 Excel 表，不要水印。

#### 5.6.3 段级故事板 prompt 模板

```
一张 Seedance 2.0 友好的段级导演故事板，横版 16:9。注意：这不是全集总览，只覆盖当前一个 15 秒视频单元。标题栏写《{片名}》· 第 {段号} 段：{段标题}，标注 15s、{画幅}、{视频模型}、{生产路由：Storyboard-first / Reference-first / Shot-table-first}。

左侧窄栏放角色与主体参考：{角色名/主体名} 的小缩略图、服装与材质锚点、3 个身份标志物、关键道具；右侧窄栏放场景与美术参考：{场景名}、时段天气、3 个关键陈设、主光方向、色板。中间主区域是当前 15s 单元的动作节拍格，共 {5-9} 格，按左到右、上到下阅读，每格只表达一个动作意图。每格包含极短中文标签：编号、时间码、景别、运镜、主动作、情绪/声音。用清晰箭头连接格子，标出角色运动方向、摄像机运动方向、视线方向和能量变化。

动作节拍：{按 Shot Table / 段目标卡列出 5-9 个节拍，例如 0-2s 钩子、2-5s 建立空间、5-8s 动作推进、8-11s 反应、11-13s 峰值、13-15s 出点衔接}。

整体风格：专业电影预制作 storyboard pitch board，构图清晰，信息图式排版，短标签可读，电影感色彩和光影统一。不要做成电影海报，不要单张人物肖像，不要普通九宫格截图，不要长篇小字，不要水印，不要乱码文字。
```

#### 5.6.4 范例 · 15s 武侠漫剧段级故事板（默认 7 格）

```
一张 Seedance 2.0 友好的段级导演故事板，横版 16:9。标题栏写《断剑归来》· 第 1 段：剑冢苏醒，标注 15s、9:16、Seedance 2.0、Reference-first。左侧窄栏放少年剑修角色参考：黑发高马尾、白色棉麻长袍、左眉尾浅疤、颈侧暗红枷锁道痕、墨玉剑穗；右侧窄栏放剑冢场景参考：断剑林、半塌青石牌坊、远处孤峰、黄昏暖橙逆光、青冷薄雾。

中间主区域为 7 个动作节拍格，按左到右、上到下阅读，箭头清晰连接：1）0-2s 低机位远景，风穿过断剑林，白衣背影静立；2）2-4s 中景慢推，衣袍和发丝被风带起；3）4-6s 手部特写，指尖触到锈剑剑柄；4）6-8s 反应特写，主角眼神微变但仍压抑；5）8-11s 断剑震动，地面尘埃和符文微亮；6）11-13s 镜头推到眼神特写，情绪爆点，金属低鸣；7）13-15s 停在眼神与剑柄同构的出点画面，右侧留出下一段黑影入场方向。底部写声音策略：低风声、衣料摩擦、金属微震、最后两秒低频轰鸣。整体国风电影感，高反差青橙调，专业 storyboard pitch board，短标签清楚，无水印无乱码。
```

#### 5.6.5 逐镜头锚点图的使用原则

当前 v20 主流程不主动从故事板切单格做首尾帧。只有用户明确要求 i2v 严格首帧构图时，才为某个 15s 单元单独生成“视频起始锚点图”。Reference-first 路线优先把**角色板 + 场景图 + 段级故事板**连到 `subjectRefs`，让 Seedance/Happy Horse 读取整体视觉和动作节拍。



---

## 6. 按题材动态调整（必须！不同题材不同打法）

| 题材 | 角色设计 | 光线/调色 | 节奏/剪辑 | 镜头偏好 | 模型建议 |
|---|---|---|---|---|---|
| **AI 漫剧/短剧（古风玄幻武侠）** | 三视图锁脸最重要，标志物要狠 | 高反差、青冷/青橙、低调戏剧光 | 快切、黄金3秒、爽点前置 | 仰拍英雄感 + 特写情绪 + 大远景气势 | seedream/gpt-image 出图，seedance-2 出视频 |
| **都市/现实短剧** | 自然真实，少夸张 | 自然光、柔和、生活化色温 | 中速、对话靠 j/l-cut | 中景对话 + 手持纪实感 | flux 写实 + seedance/kling |
| **广告/产品片** | 产品=主角，要品牌参考图 | 干净高调、产品高光 | 5s 一切、钩子→产品→CTA | 环绕展示 + 英雄机位 + 微距 | flux/seedream + veo/seedance |
| **MV/卡点** | 风格化＞写实，可超现实 | 强风格化、霓虹/单色/高饱和 | 严格卡 BGM 节拍、转场炫 | 多变、跳切、运镜花哨 | runway/kling + musicGen 卡点 |
| **写实短片/微电影** | 选角真实，连贯性第一 | 电影级布光、统一 LUT | 慢、长镜头、留白 | 焦距/景深讲究、轴线一致 | flux/veo，强调物理真实 |

**开场反问拿到题材后，整个项目的 prompt 风格、调色、节奏都要据此定调，并写进 `canvas_save_director_bible` 让所有节点自动继承。**

---

## 7. 工具清单（真实工具名，均为 canvas_*，与 desktop bridge MCP 一一对应）

> 选工具的总原则：**先看主体库**（`canvas_subject_list`）→ **再开项目**（`canvas_create_project`）→ **逐个节点**（`canvas_add_node` + `canvas_run_node`）→ **Shot Table 之后**才用 `canvas_expand_shot_table`。除调试外不要直接走 `canvas_split_grid`。

### 7.1 项目 / 画布生命周期
| 工具 | 用途 |
|---|---|
| `canvas_list_projects()` | 列出现有项目（按 updatedAt 倒序）。新会话开工前先看是否能续上旧项目 |
| `canvas_create_project(name, story_beats, character_bible, shot_breakdown, user_confirmed)` | 建项目（用户确认大方向后才调；后端 Phase Gate 校验三段文本 + user_confirmed）|
| `canvas_open(project_id)` | 打开/读取已有项目快照 |
| `canvas_get_state(project_id)` | 拿当前画布的 nodes / edges / 每节点 status & outputs。任何不确定就先 get_state |
| `canvas_auto_layout(project_id)` | 节点超过 ~15 个或 spawn 后凌乱时一键重排（等同用户 Shift+Option+F）|

### 7.2 多画布 / 多集 / 多版本（同项目下并行）
| 工具 | 用途 |
|---|---|
| `canvas_create_subcanvas(project_id, name)` | 同项目下新建一张画布（分集 ep1/ep2、A/B cut、长片分幕）|
| `canvas_list_subcanvases(project_id)` | 列项目内所有画布；main 永远在第一位 |
| `canvas_open_subcanvas(project_id, canvas_id)` | 打开某张子画布 |
| `canvas_rename_subcanvas(project_id, canvas_id, new_name)` | 改子画布展示名 |
| `canvas_delete_subcanvas(project_id, canvas_id)` | 删子画布（不能删 main）|

### 7.3 节点编排
| 工具 | 用途 |
|---|---|
| `canvas_add_node(project_id, kind, data_json, position_x?, position_y?)` | 加节点。实现层允许批量准备多个节点；但必须遵守阶段 gate 与用户确认 |
| `canvas_connect(project_id, src_node_id, src_handle, tgt_node_id, tgt_handle)` | 连线。实现层允许提前连线；运行时由 Hermes 保证上游产物已就绪。常用 handle 见第 7.10 |
| `canvas_update_node_data(project_id, node_id, patch_json)` | 改节点参数（改 prompt / videoOrder / segmentTrims 等后重跑）|
| `canvas_delete_node(project_id, node_id)` | 删除画布节点，同时删除所有与之关联的边和生成的媒体文件 |
| `canvas_delete_node_output(project_id, node_id)` | 删除节点生成的媒体文件（保留节点本身，只清输出） |
| `canvas_delete_edge(project_id, edge_id)` | 删除画布上的一条边（断开两个节点之间的连接）|
| `canvas_run_node(project_id, node_id, mode="only"\|"downstream"\|"full")` | ⭐ **后端同步**真跑节点（图 ~30s，视频 ~4min；返回 displayMarkdown 直接贴对话）|
| `canvas_expand_shot_table(project_id, script_node_id?)` | ⭐ Shot Table 受控批量通道：从 `scriptGen.outputs.scenes` 幂等补齐 `image(锚点) → image2video → videoConcat`。**仅在角色/场景/Shot Table 都确认后**调 |

### 7.4 Spawn 子节点（image 跑完后的独立子图）
| 工具 | 用途 |
|---|---|
| `canvas_get_spawned_children(project_id, parent_node_id)` | 拿父 image 最新批次 spawn 出来的子节点列表（含 spawnLabel / imageUrl / childNodeId）。挑 1-3 张连到 `image2video.subjectRefs` |
| `canvas_spawn_children(project_id, parent_node_id, children_json)` | 手动 spawn N 个独立 image 子节点（用于把外部 URL 或 temporal/reverse-prompt 结果落地为画布节点）|
| `canvas_clean_old_spawn_batches(project_id, parent_node_id)` | 删非最新批次的子节点（保持画布干净，最新批次保留）|

### 7.5 角色 / 场景 / 道具资产
| 工具 | 用途 |
|---|---|
| `canvas_generate_character_views(description, image_model, hero_url?, aspect_ratio?)` | ⭐ 角色三视图（A 路线直出 / B 路线 hero_url 扩侧背）。**C 角色板路线不调本工具**，用普通 image 节点 + 5.2.1 模板 |
| `canvas_compose_contact_sheet(image_urls, cols?)` | 多图拼 1 张参考图（角色 pose sheet / 多角色合一图，绕过 subjectRefs ≤3 上限）|
| `canvas_cutout(image_url)` | 抠图（背景透明）。给道具 / 角色重新合成场景前用 |
| `canvas_outpaint(image_url, target_ratio, prompt?)` | 扩图（如 16:9 → 21:9 / 1:1 → 16:9），保留原图主体 |

### 7.6 主体库（跨项目复用，对齐 LibTV 团队主体库）
| 工具 | 用途 |
|---|---|
| `canvas_subject_list(type_filter)` | ⭐ 列主体库（character / scene / prop）。**新项目开工前必看**，命中就 load 复用，不重做 |
| `canvas_subject_load(subject_id)` | 读主体完整数据（含所有视图 URL）|
| `canvas_subject_save(name, subject_type, cover_image_url, views, ...)` | 把满意资产存进主体库（用户确认 + 询问后再调）|
| `canvas_subject_delete(subject_id)` | 删主体（不影响已经引用过它的画布节点）|

### 7.7 编导档案 + 自检 + 影视级模式（项目级开关）
| 工具 | 用途 |
|---|---|
| `canvas_save_director_bible(project_id, look_profile, audio_bible)` | ⭐ 整片调色 + 声音档案，自动注入所有 image / image2video 的 prompt 末尾 |
| `canvas_load_director_bible(project_id)` | 读已存的 lookProfile / audioBible |
| `canvas_get_meta(project_id)` | 读画布级 meta（自检 / 影视级模式 等开关）|
| `canvas_set_meta(project_id, patch_json)` | 通用 meta 修改（任何画布级开关）|
| `canvas_set_self_check(project_id, enabled, max_retries?, pass_threshold?)` | 启停 Hermes 视觉自检闭环（用户说"严格审核 / 质量优先"再开；**默认关**）|
| `canvas_set_cinematic_pro_mode(project_id, enabled)` | 启停影视级深度模式（Beat sheet / 9 视图 multi-ref / 双比例输出）。**配额 ~2.5×**，仅在用户明说"电影级 / 节展投递"时启用 |
| `canvas_evaluate_artifact(artifact_url, brief, expected_character_desc?, expected_style?)` | 视觉自评（仅图）。**仅当 self-check 开了**才主动调；评分<阈值则改 prompt 重跑 |

### 7.8 模型 / 剧本 / 提示词工具
| 工具 | 用途 |
|---|---|
| `canvas_list_video_models()` | ⭐ 选 `image2video.videoModel` 前先调，看每个模型的 `durationsSeconds / tailFrame / nativeAudio / maxResolution` |
| `canvas_optimize_prompt(prompt, context?)` | 用户描述太短/太空时一键扩写成 主体+动作+场景+光线+镜头+风格+Negative |
| `canvas_segment_script(raw_script, target_episodes?, target_seconds_per_episode?)` | 长剧本（>500 字 / 多集需求）拆成 episodes / global_characters / global_style |
| `canvas_run_script_doctor(scenes, user_intent?)` | scriptGen 跑完后，6 维度评审剧本（hook / arc / pacing / dialogue / visualizability / impact）+ 改进建议 |
| `canvas_run_reverse_prompt(image_url, vision_model?)` | 反推图片为 6 段中文工业 prompt（学习参考图风格 / 复用 prompt）|
| `canvas_run_temporal(image_url, direction="after"\|"before", seconds)` | 演绎"3 秒后 / 5 秒前"，after 用 image2video 抽末帧（慢但准）, before 用 image2image 反向（快）|
| `canvas_film_analysis(video_url)` | 参考视频反推分镜表（每个 shot 含可复用 prompt）|

### 7.9 音乐 / 产物落盘
| 工具 | 用途 |
|---|---|
| `canvas_run_music_gen(prompt?, duration?, model?, timing_prompts?)` | 文生 BGM / 音效 / 卡点（vidu audio1.0 / kling-audio）。卡点模式用 timing_prompts 分段 |
| `canvas_save_artifact(url, relative_path)` | 把产物落到 vault `Canvas/...`，用户能在 Finder 找到 |
| `canvas_list_artifacts(project?)` | 列 vault Canvas/ 目录下的所有产物 |

### 7.10 节点 kind / handle 速查
```
image          { prompt, imageModel, aspectRatio, count }
                  → handles: images（输出）, reference（输入，可选）
image2video    { prompt, duration, videoModel,
                 generationMode: "i2v"|"ff"|"ref"|"imgRef"|"text2video",
                 audioRef?, subjectRefs? }
                  → handles by mode：
                     i2v        : image（必需）
                     ff         : image（必需）+ tailFrame（必需，模型须 tailFrame=true）
                     ref        : subjectRefs（必需，≤3 张）  ← image 可空，纯参考生视频
                     imgRef     : image（必需）+ subjectRefs（必需）
                     text2video : 全空，仅 prompt
                  → 通用：subjectRefs ≤3 张；audioRef 仅 nativeAudio 模型识别
tts            { text, voice, audioModel }
musicGen       { prompt, duration, audioModel, timingPrompts? }
videoConcat    { videoOrder[], segmentTrims?, crossfadeSeconds?,
                 cutPattern: "rapid-cut"|"j-cut"|"l-cut"|"montage",
                 bgmUrl?, bgmVolume? }
text           { text, role? }                inpaint   { prompt, maskUrl, imageModel }
upscale        { enhancePrompt, imageModel }  comicSplit { imageUrl }
videoTrim      { startSec, endSec }           videoExtend { prompt, extendSeconds, videoModel }
audio2video    { videoModel }                 preview   {}
shotGroup      { memberNodeIds[], coherencePrompt, imageModel }
scriptGen      { prompt, model? }             # 可输出 segments（集级段落表）或 scenes（段内镜头表）
```

> 🧪 **Dev only — Seedance 2.0 直连**：`videoModel="doubao-seedance-2-0"`（注意：**不是**诗云的 `doubao-seedance-2-0-260128`）走 `http://aigw.fx.ctripcorp.com/llm/100003144/v1`，不走诗云、不计费。需要在桌面端「设置 → 🧪 Dev Only」配置 dev API key。**仅 dev 构建可见**，生产打包会被 tree-shake 掉。诗云上的同款模型 ID 是 `doubao-seedance-2-0-260128`（带日期后缀），两者请勿混用。



### 7.11 知识库工具（笔记管理）
| 工具 | 用途 |
|---|---|
| `knowledge_list_notes(project, item_type?, limit?, order?)` | 列出知识库中的笔记（按项目/类型筛选） |
| `knowledge_search(query, limit?, item_type?)` | 搜索知识库笔记 |
| `knowledge_read(note_id)` | 读取单条笔记内容 |
| `knowledge_write_note(note_id?, project, title, content, item_type?)` | 创建或更新笔记 |
| `knowledge_delete_note(note_id)` | ⭐ **删除笔记**：同时删除笔记文件、关联 wiki 页面和反向链接。**不可逆**，调用前需用户确认 |
| `knowledge_resolve(query, limit?, max_reads?, item_type?)` | 搜索 + 读取：搜索知识库、获取最匹配的笔记全文 |

> ⚠️ `knowledge_delete_note` 是**不可逆操作**，会同时清理 wiki 和反向链接。调用前必须确认用户意图。

### 7.12 bagege API 接入规范（v20 — 画布媒体生成；给 agent 的“仅流程”说明）

> 目的：画布运行时已把“画布节点参数 → bagege 媒体生成任务/轮询”封装好了。
> agent **只需要正确连画布节点、按 gate 确认、按需执行节点**；不需要拼 endpoint /字段。

- **鉴权与 baseURL**：由画布后端/配置统一完成（agent 不感知）。
- **任务异步语义**：图片/视频生成通常返回 `task.id`，画布执行会自动轮询直到 `completed/failed`。
- **endpoint 选择由后端/节点 kind 决定**：
  - `image` 节点：内部选择“文生图/图生图”所需的生成路由（对应当前节点/参数模式）。
  - `image2video` 节点：内部选择视频生成路由（T2V / I2V / V2V / reference-to-video 等），并按所选 `generationMode` 决定输入引用（image_url / image_references / subjectRefs）。
- **失败排查优先级（给 agent 的动作）**：
  1) 先检查节点是否已按规则连好上游产物（尤其 `subjectRefs`/参考图是否存在）。
  2) 再检查是否误把“需要输入图”的模式当成纯文生（generationMode/引用为空）。
  3) 最后才看后端返回的 error 文本（在对话里呈现给用户）。

- **删除相关**：
  - 删除“画布元素/节点”用 `canvas_delete_node` / `canvas_delete_node_output`（按你希望保留节点还是删除输出）。
  - 删除“节点输出媒体”只清输出，不清画布结构。

因此：agent 写 SKILL 时只需坚持 **“正确连画布、正确 gate、需要时执行节点、删除用对工具”**。
```
image          { prompt, imageModel, aspectRatio, count }
image2video    { prompt, duration, videoModel, audioRef?, subjectRefs? }
tts            { text, voice, audioModel }
musicGen       { prompt, duration, audioModel, timingPrompts? }
videoConcat    { videoOrder[], segmentTrims?, crossfadeSeconds?, bgmUrl?, bgmVolume?, cutPattern? }
text           { text, role? }      inpaint { prompt, maskUrl, imageModel }
upscale        { enhancePrompt, imageModel }    comicSplit { imageUrl }
videoTrim      { startSec, endSec }   videoExtend { prompt, extendSeconds, videoModel }
audio2video    { videoModel }   shotGroup { memberNodeIds[], coherencePrompt, imageModel }   preview {}
```

---

## 8. 运行节点（后端同步执行，v25）

`canvas_run_node` 是**后端同步执行** —— 调用会阻塞到节点真跑完才返回，结果直接带回，**不需要轮询**。

Shot Table + 生产方案确认后的标准生产顺序：
1. 确认角色卡/角色板、场景、道具、Shot Table 镜头表和 A/B/C/D/E 生产方案都已通过用户 review gate。
2. 跑 `scriptGen`，得到 `outputs.scenes`。
3. 调 `canvas_expand_shot_table`，拿 `imageNodeIds / videoNodeIds / concatNodeId`。
4. 按所选方案补齐参考图连线：A 必须连故事板总览板，B 必须连末帧，C 必须连资产 reference，D/E 按草稿/参考视频策略。
5. 依次跑视频段；失败只重试失败节点。
6. 更新 `videoConcat` 时间轴参数后跑 `concatNodeId`。

```python
report = canvas_run_node(project_id=pid, node_id=node_id, mode="only")
# report = {"ok":..., "ran":[{"nodeId","kind","status","error?","displayMarkdown","outputUrls"}]}
md = report["ran"][0].get("displayMarkdown")   # 已是 ![名字](url) / 🎬 [名字](url)
# 直接把 md 原样贴进你给用户的回复即可，对话区会渲染出图/视频
```

- 后端直接跑，**不依赖前端是否挂载、用户在哪个 tab**。
- `status:"done"` + `outputs` 直接入画的节点（三视图/网格分镜）**无需再 run**。
- 图 ~30s、视频 ~4min，调用会等这么久返回，正常。
- 跑完把 `displayMarkdown` 贴给用户看 → 问满意/存素材库/继续 → 确认后再跑下一个。
- status=="error" → 读 error 修复（prompt 空 / 非中文被拒 / 上游没连图）。

---

## 9. 在对话中展示产物

- `canvas_run_node` 跑完会直接返回 `ran[].displayMarkdown`（已是 `![名字](url)` / `🎬 [名字](url)` 格式）。**把它原样粘进你的回复**，对话区会自动渲染出图片/视频/音频。
- ❌ **绝对禁止**用 `terminal` / `open` / 命令行去打开本地图片浏览器。用户要在**对话里**看，不是在系统看图器里看。本地 vault 相对路径（`Canvas/_generated/...`）对话区能自己解析显示，直接贴即可。
- 若拿到的是 https / asset 短 URL，同样直接 `![主角三视图](url)`。
- base64 太大别塞对话 → 让用户在画布节点看，或存 vault 拿短路径。
- 视频太大 → 引导画布预览 + 文字描述。

---

## 10. 红线清单（自检）

1. ❌ 用户没确认大方向就建项目
2. ❌ 建完项目就跳过 Stage 1/2/3，直接跑视频
3. ❌ 用户没有明确批准，就批量生成图片或视频
4. ❌ 把“继续准备/下一步”误解成“同意批量生成”
5. ❌ 生成完不贴图、不问满意、不问存不存素材库
6. ❌ 不按 角色→场景→道具→故事板→视频→成片 的阶段顺序；跳阶段
7. ❌ 一个阶段没全部确认完就冲进下一阶段（缺 review gate）
8. ❌ 角色/场景不先问用户走省钱直出还是高质量分步
9. ❌ 提示词非中文 / 关键词堆砌 / 不按题材变化
10. ❌ 源图没产物就连下游线（后端会拒）；image2video 不连 subjectRefs 锁脸
11. ❌ 单镜头多个大动作（换脸高发）
12. ❌ user_confirmed=True 但用户没说确认

---

## 11. 进阶参考

补充资料按需写在 `references/` 目录。当前主体规则全部在本文件内，无需额外读取。

End of SKILL v25.
