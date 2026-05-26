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
