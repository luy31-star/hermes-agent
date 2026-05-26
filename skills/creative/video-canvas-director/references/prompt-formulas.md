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

