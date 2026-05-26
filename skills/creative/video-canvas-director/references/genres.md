## 🎬 八大题材 prompt 模板库（每类含完整七要素 + 范例）

### 1. 古风武侠 Wuxia
```
风格锚（storyboard.style）:
"cinematic wuxia ink-wash painting style, 35mm anamorphic widescreen 2.39:1,
teal-amber color grade with cool jade-blue shadows, subtle film grain,
mist atmosphere, golden rim light through bamboo, traditional Chinese aesthetics,
Hou Hsiao-hsien / Wong Kar-wai inspired cinematography"

典型 image prompt 范例（一个镜头）:
"@character1 (白衣少年剑仙) — keep SAME face, SAME ivory white silk robe with
silver embroidery, SAME long black hair tied with white ribbon, SAME cracked
sword scabbard.

He kneels on a wind-swept cliff edge above a sea of clouds, sword stuck into
stone beside him, faint golden tribulation lightning crackling around his body.
Black storm clouds churning overhead with distant thunder.

Composition: rule of thirds, character in lower-left third, vast sky and clouds
filling upper two thirds. Wind sweeping his hair and robe to the right.

Mood: lonely, defiant, the calm before the storm.

NEGATIVE: no text, no watermark, no anime, no cartoon, no character drift,
no outfit drift, no modern elements, no plastic skin, no flat lighting."

视频 prompt 范例（10s 镜头）:
"KEYFRAME: @image_3 as starting frame.
CHARACTER LOCK: @character1.

STYLE: ultra-cinematic wuxia 8K, 35mm anamorphic, teal-amber grade.

DURATION: 10s.
[0-2s] Wind picks up violently, his hair and robe whip dramatically. Camera
       holds static then begins slow push-in.
[2-5s] He slowly raises his head, eyes opening to reveal cold determination.
       Golden tribulation lightning intensifies around him.
[5-8s] In one smooth motion he pulls the sword from the stone, blade emitting
       a crystalline metallic ring and glowing faintly cyan.
[8-10s] He stands fully, sword pointed at the sky, robe billowing. Camera
       freezes on the silhouette as lightning strikes behind him.

CAMERA: low-angle hero shot, 24mm wide, slow Steadicam push-in from
medium-wide to medium-close. 0.5x speed ramp on sword draw [5-8s].

AUDIO:
- Ambient: howling mountain wind, distant rolling thunder
- Key SFX: crisp metallic sword unsheathe at [5-8s], crackling
  lightning energy hum sustained
- Music: traditional erhu + drums building to cymbal crash at [8-10s]
- No dialogue

NEGATIVE: no text, no character drift, no costume drift, no extra fingers,
no warped sword, no flickering, no jump cuts."
```

### 2. 玄幻仙侠 Xianxia
```
风格锚:
"epic xianxia fantasy 8K hyper-realistic, Unreal Engine 5 quality rendering,
cool blue-purple-gold palette with magical light particles, volumetric god rays
through ancient ruins, glowing rune circles, dragon-scale texture details,
Marvel-meets-traditional-Chinese aesthetic"

关键词清单（hermes 把这些拼进每个 image prompt）:
- 灵气粒子 / qi particles flowing
- 法阵 / glowing rune circles, ancient seals
- 灵兽 / divine beasts (dragon, phoenix, qilin) with scale detail
- 神光 / volumetric godlight rays
- 渡劫雷 / heavenly tribulation lightning
- 神器 / artifact glow with engraved patterns

视频 prompt 必备:
- camera: dramatic crane shots, 360° orbit on power moments, slow-mo on impact
- audio: orchestral choir + thunder + dragon roar + jian-qi sword energy hum
```

### 3. 都市悬疑 Urban Thriller
```
风格锚:
"gritty urban thriller cinematography, 35mm with subtle handheld vibration,
teal-orange Hollywood color grade, wet-asphalt neon reflections, anamorphic
horizontal lens flare, motion blur on action, Fincher-meets-Villeneuve mood"

典型场景:
- 雨夜地铁站 / rainy subway platform with sodium-vapor lamps
- 高楼顶 / rooftop skyline at blue hour
- 审讯室 / interrogation room with single low-key spotlight
- 巷道追逐 / alley chase with flickering neon signs

image prompt 范例:
"Detective in rumpled trench coat stands at the edge of a rain-soaked rooftop
overlooking a sprawling Hong Kong skyline at blue hour. Distant neon billboards
reflect in puddles at his feet. Cigarette smoke curls past his face.

Composition: medium-wide shot, character in right third, vast city in left two
thirds with massive negative space.

Mood: weary, calculating, on the edge of a breakthrough.

NEGATIVE: no text, no watermark, no cartoon, no anime, no oversaturation,
no plastic skin, no flat lighting."

视频要点:
- camera: handheld documentary feel, whip-pans on tension, rapid intercut
- lighting: harsh sodium-vapor street lamps, neon billboards, headlight flashes
- audio: cinematic synth bed + tense low drones + sudden impact stings
```

### 4. 赛博朋克 Cyberpunk
```
风格锚:
"cyberpunk neon-lit future megacity, 8K hyper-realistic, magenta-cyan-violet
neon palette, holographic UI overlays, chromatic aberration on highlights,
volumetric fog with neon backlighting, Blade Runner 2049 + Ghost in the Shell
aesthetic, anamorphic horizontal flares"

视觉元素:
- 全息广告 / floating holographic billboards (with non-text alien glyphs)
- 飞行车 / sleek hovercars with light trails
- 义体改造 / cybernetic implants with subtle LED accents
- 霓虹雨 / neon rain reflecting on wet asphalt

image prompt 范例:
"@character_kira — keep SAME face, SAME magenta-tipped neon-blue undercut hair,
SAME black tactical jumpsuit with cyan circuitry glow on chest panels, SAME
chrome cybernetic right arm.

She sprints through a narrow alley packed with steaming food stalls under a
canopy of holographic billboards. Rain slicks the asphalt and reflects the
magenta-cyan neon. Sparks fly from her chrome heels on impact.

Composition: low-angle wide shot, 14mm ultra-wide, character charging toward
camera in extreme perspective, neon corridor framing her on both sides.

Mood: kinetic, hunted, defiant.

NEGATIVE: no text, no readable signage, no cartoon, no anime style (use
photoreal), no character drift, no extra fingers, no warped chrome arm."
```

### 5. 硬科幻 Hard Sci-Fi
```
风格锚:
"cinematic hard sci-fi, 8K photorealistic, cool blue-cyan + warning red palette,
chromatic aberration on holographic UI, subtle digital noise, NASA / SpaceX
documentary realism + Christopher Nolan epic scale, anamorphic widescreen"

视觉元素:
- 太空站内饰 / clean white modular space-station corridors
- 全息控制台 / floating holographic data displays
- 行星表面 / alien planet vistas with two suns or rings
- 太空服 / detailed EVA suit fabric folds and helmet reflections

视频要点:
- camera: smooth gimbal tracking, drone fly-throughs, FPV chase, dramatic dutch
  angles on tension moments
- lighting: cold LED practicals + holographic glow + dramatic rim from
  blue/red emergency strobes
- audio: synth bed + servo whines + holographic UI beeps + bass-heavy impact +
  ambient station hum
```

### 6. 奇幻冒险 Western Fantasy
```
风格锚:
"Hollywood epic fantasy, anamorphic widescreen 2.39:1, warm earth-tone palette
with magical accent colors (cyan, violet, gold), AAA film quality, painterly
atmospheric haze, Lord of the Rings + Witcher + How to Train Your Dragon
inspired"

视觉元素:
- 古老森林 / ancient forest with moss-covered ruins
- 龙 / dragons (use real-world physics for wing membrane)
- 火光 / firelight warm fill at night
- 飘扬旗帜 / banners flowing in wind on castle walls

image prompt 范例:
"A young dragon rider in worn leather armor stands atop a windswept cliff,
hand resting on the snout of an enormous obsidian-scaled dragon whose wings
fold protectively around them. Misty mountain peaks stretch to the horizon
behind. Golden hour sun breaks through clouds.

Composition: wide shot, 35mm, characters in lower-center third, dragon's
massive head dominates upper-right, vast landscape filling background.

Mood: bonded, awe-struck, the moment before a great journey begins.

NEGATIVE: no text, no watermark, no cartoon (use photoreal), no character
drift, no warped dragon anatomy, no extra wings, no flat lighting."

视频要点:
- camera: sweeping aerial drone, low-angle hero pose, smooth crane reveals
- audio: orchestral fantasy score + dragon/beast roars + magical chime tinkles
```

### 7. 纪录片 / 真实风 Documentary
```
风格锚:
"documentary realism, 35mm with handheld micro-shake, natural color grade
(no aggressive teal-orange), available natural light, shallow DoF on emotional
moments, Vice / Netflix-doc aesthetic"

视觉元素:
- 自然光 / window light, golden hour, no studio strobes
- 真实环境 / real lived-in spaces, not staged
- 主体直视 / occasional direct-to-camera glance
- 旁观视角 / fly-on-the-wall framing

image prompt 范例:
"A 58-year-old fisherman with weather-beaten face and salt-stained hands
mends a torn net at the edge of a wooden dock at sunrise. Mist drifts off the
calm harbor water. His expression is meditative, lost in the rhythm of the
work.

Composition: medium close-up, 50mm, shallow DoF, character in left third,
soft-focused boats and water filling background. Camera slightly below his
eye-line for intimacy.

Mood: dignified, contemplative, the quiet labor of a lifetime.

NEGATIVE: no text, no watermark, no cinematic teal-orange (keep natural),
no plastic skin, no fashion makeup, no studio lighting, no exaggerated grain."
```

### 8. 广告片 / 电商种草 Commercial Ad
```
风格锚:
"premium commercial photography, ultra-clean composition, soft directional
studio lighting, shallow DoF, macro detail on product texture, 8K hyper-real,
Apple keynote + luxury brand aesthetic"

结构（5 镜头模板，竖屏 9:16 短视频）:
1. 钩子（0-2s）— extreme close-up product detail + attention grabber
2. 痛点（2-5s）— problem montage, fast-cuts, relatable scene
3. 产品出场（5-8s）— hero shot, slow rotation, clean background
4. 卖点演示（8-12s）— product in use, satisfying motion
5. CTA（12-15s）— logo + clean copy space (no text rendered, leave room)

image prompt 范例（产品 hero shot）:
"A frosted glass bottle of premium serum stands centered on a polished marble
surface, single soft directional light from upper-left creating elegant
highlight on the glass curve. Subtle water droplets clinging to the bottle.
Soft pink rose petal floating in air mid-fall on the right.

Composition: centered hero shot, 9:16 vertical, 100mm macro lens, shallow DoF
with marble surface fading to soft bokeh.

Mood: premium, clean, aspirational.

NEGATIVE: no text on bottle (will be added in post), no watermark, no clutter,
no human hands in frame, no cartoon, no exaggerated saturation."
```

### 9. 音乐 MV
```
风格锚:
"music video aesthetic matching <genre>, dynamic editing rhythm sync to beat,
saturated mood-driven color grade, 50% slow-mo + 50% real-time mix,
A24 / Hiro Murai inspired"

要点:
- 镜头节奏 = 音乐 BPM
- 慢镜头用在情绪段（副歌前的静止 / 副歌爆发）
- color grade 跟着情绪段切换（A 段冷调 / 副歌暖调）
- 8 镜头模板：环境引入 / 主角入场 × 2 / 高潮慢镜 × 2 / 反转 / 收尾
```

### 10. 日系动漫 Anime
```
风格锚:
"Japanese cel-shaded anime, Makoto Shinkai-inspired backgrounds with
ultra-detailed light particles, cinematic camera but anime rendering, soft
lens bloom on bright sources, painterly clouds, hand-drawn line quality"

视觉元素:
- 闪烁阳光 / sunbeams through leaves with bokeh particles
- 校服细节 / detailed school uniform with realistic fabric folds
- 头发飘动 / dynamic hair physics (anime exaggerated but consistent)
- 雨滴 / individually rendered raindrops with reflections

image prompt 范例:
"A teenage boy in a navy-blue school uniform stands on a deserted train
platform at golden hour, gazing at his hand where a single sakura petal has
landed. Train tracks stretch into the distance behind him. Light flares
through his hair.

Composition: medium shot, 35mm, character in right third, leading lines from
the tracks pulling eye into deep background.

Mood: melancholic, suspended in time, on the verge of revelation.

Style: Makoto Shinkai-inspired anime cel-shaded with painterly background,
soft lens bloom, ultra-detailed lighting.

NEGATIVE: no text, no watermark, no realism (this is anime), no character
drift, no extra fingers, no warped uniform."
```

---

