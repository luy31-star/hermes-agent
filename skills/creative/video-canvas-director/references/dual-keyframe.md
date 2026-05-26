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

