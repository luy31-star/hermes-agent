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

