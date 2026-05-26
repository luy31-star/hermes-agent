## 🔊 P0 进阶 #2 — 系统化音频设计（Audio Design）

**2026 顶级流程必备**。Veo 3.1 / Sora 2 / Kling 2.6 都是 native audio 模型，意味着 prompt 里写好的 SFX / ambient / music 会**同步**生成。不写 = 模型瞎给你配。

### 三层音轨结构（每个 image2video prompt 必须分这三层写）

```
AUDIO:
- Diegetic (场景内 / 物理可见声源):
  · 角色动作 → 脚步声 / 布料摩擦 / 武器交锋
  · 场景物理 → 风、雨、火、水流、玻璃碎裂
  · 对白 → "<台词>" by <character>, soft whispered tone
  
- Foley / SFX (强化情绪的非自然声效):
  · 慢镜头时刻：低频心跳鼓、抽真空感
  · 紧张时刻：金属高频嘶鸣、嗡嗡 drone
  · 释放时刻：cymbal crash + 大鼓
  
- Music / Score (情绪锚定):
  · 主题：<wuxia erhu | cyberpunk synth | orchestra epic>
  · 节奏：<slow building | pulsing 120 BPM | rising crescendo>
  · 情绪：<melancholy | tension | triumphant>
```

### 时间戳 SFX 节奏表（必加，跟时间戳 action 一一对应）

```
DURATION: 10s.
[0-2s] 动作: 角色缓缓抬头
       SFX:  轻微衣物摩擦, 远处风声渐起
       Music: 单一低音弦乐 sustain（C 低音，无主题）
       
[2-5s] 动作: 角色按上剑柄, 黄色雷电围绕
       SFX:  剑鞘金属嗡鸣, 雷电噼啪 crackle, 心跳低频开始 (60 BPM)
       Music: erhu 进入 piano 起调, 主题动机渐显
       
[5-8s] 动作: 拔剑出鞘, 一声金属脆鸣
       SFX:  ⚡ 关键击中: crisp metallic ring, sustain shimmer
              + 雷电 boom + 风骤起呼啸
       Music: ⚡ 主题爆发, drum hit, 全乐队 forte
       
[8-10s] 动作: 持剑站立 silhouette
       SFX:  剑光 hum 持续, 风渐弱
       Music: 单一弦乐 hold, 留白
       
关键 SFX hit 时刻 (与 action peak 同步): [5.0s] 拔剑金属声
```

### 各题材的 Audio Design preset

#### 古风武侠
```
Diegetic: wind through bamboo, fabric flutter, sword unsheathe ring,
          footsteps on wet stone, distant bird cry
Foley: low-frequency heart drum on tension, sub-bass rumble on impact,
       crisp shimmer on sword aura
Music: traditional erhu lead + bamboo flute + taiko drums + strings,
       sparse minimalist arrangement, building to single climactic hit
Vocals: optional brief whispered monologue, no opera-style singing
```

#### 玄幻仙侠
```
Diegetic: thunder crackle, qi-energy hum, dragon roar (deep + reverb),
          rune circle glow hum, robe whip in spirit wind
Foley: ethereal choir whoosh on power activation, deep bass sub-drop on impact
Music: full orchestral with epic choir (Latin/Sanskrit chant), traditional
       Chinese instruments layered (erhu, guzheng), rising 4-note motif
Sound design: heavy reverb tail on all impacts (cathedral hall), pitch-shift
              on supernatural elements
```

#### 都市悬疑
```
Diegetic: rain on metal, distant traffic, neon hum, footsteps on wet asphalt,
          phone vibrate, lighter flick
Foley: tense low drone bed continuous, heart-beat thud on stress,
       sudden silence drop before reveal
Music: minimal synth bed + cello sustain, building 90 BPM, sparse piano
Sound design: dry close-mic'd dialogue, ambient room tone present, no reverb
```

#### 赛博朋克
```
Diegetic: neon buzz, hovercar pass-by whoosh, holographic UI beeps,
          rain on plastic surfaces, crowd murmur with synthesized accent
Foley: synth zaps on cybernetic activation, glitch artifacts on reveal,
       sub-bass drone on tension
Music: synthwave / vaporwave 120 BPM, retro arpeggios, modulated lead,
       gated reverb snare
Vocals: optional vocoder/auto-tune treatment on dialogue
```

#### 硬科幻
```
Diegetic: spaceship hum, servo whines, holographic UI, EVA suit oxygen breath,
          radio chatter with static
Foley: bass drop on station maneuvers, sub-rumble for scale, beep cluster
       for tech systems
Music: orchestral + electronic hybrid, ambient pads, 4-note rising motif
       (à la Hans Zimmer / Ben Salisbury), no melody on tense moments
Sound design: heavy sub-bass for impact, near-silence in space, dialogue
              with slight comm-radio EQ
```

#### 奇幻冒险
```
Diegetic: dragon wing flap (low whoosh), forest ambient, fire crackle,
          armor clank, banner flap
Foley: low rumble on dragon footsteps, magical chime sparkle on enchantment,
       battle horn brass blow
Music: full orchestral fantasy (LotR-inspired), choir on hero moments,
       wooden flute on quiet moments, drum gallop on action
Sound design: rich reverb on grand spaces, intimate dry mix on quiet talk
```

#### 纪录片
```
Diegetic: real environmental ambience (no enhancement), natural breath,
          actual mechanical sounds of work
Foley: minimal — only enhance what's already there, no added drama
Music: sparse piano / acoustic guitar / single string instrument, quiet
       presence not foreground
Vocals: clean documentary-style voiceover, no character voices
```

#### 商业广告
```
Diegetic: clean product sounds (bottle pop, click, satisfying snap),
          minimal background
Foley: ✨ sparkle / chime on key moments, satisfying sound design beats
       on every action
Music: upbeat mainstream pop, brand-mood (luxury = piano, energy = drums),
       hooks at 5s / 10s / 15s for ad cuts
Vocals: clear professional voiceover, brand jingle optional
```

#### 音乐 MV
```
Music: <song reference / genre / BPM> — drives the cut rhythm
Diegetic: minimal — only when story-relevant
Foley: SFX hits matched to musical accents (kick / snare / cymbal)
Visual cuts: edit on beat — every shot change synced to musical phrase
```

#### 日系动漫
```
Diegetic: subtle natural sounds, anime-stylized whoosh on movement,
          school bell, train pass-by, sakura flutter
Foley: anime-style SFX hits ("shing!" on reveal, sparkle chime on emotional
       beat), exaggerated wind on dramatic moments
Music: anime J-pop / orchestral hybrid, piano lead on emotional moment,
       solo violin on melancholy, full ensemble on action peak
Vocals: optional Japanese dialogue with natural intonation
```

### 关键准则

1. **每个时间戳分段都要有声音**（不能写"0-2s 角色抬头"完事，必须 0-2s 也写 SFX）
2. **关键 SFX hit 时刻要明确**（"⚡ at [5.0s]: metallic sword ring"）
3. **音乐情绪曲线要画**（buildup → climax → release）
4. **不要写"epic music"这种空话**（要写"orchestral with rising 4-note motif building to cymbal crash at 8s"）

---
