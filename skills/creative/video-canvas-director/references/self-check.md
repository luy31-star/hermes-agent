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
