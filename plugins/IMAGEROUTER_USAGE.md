# ImageRouter Plugin Usage Guide

## 📦 What is ImageRouter?

ImageRouter is a unified API gateway that routes image and video generation requests to multiple AI models through an OpenAI-compatible interface.

## ✅ Test Results

All tests passed successfully:
- ✅ Plugin structure validation
- ✅ YAML configuration
- ✅ Registry integration
- ✅ Model catalog
- ✅ Plugin context registration

## 🚀 Quick Start

### 1. Set up API Key

```bash
export IMAGEROUTER_API_KEY="your-api-key-here"
```

### 2. Configure Hermes

Edit `~/.hermes/config.yaml`:

```yaml
# For image generation
image_gen:
  provider: imagerouter
  model: openai/gpt-image-2

# For video generation
video_gen:
  provider: imagerouter
  model: xAI/grok-imagine-video
```

### 3. Use in Hermes Chat

```bash
hermes
```

Then in the chat:

```
You: Generate an image of a cat wearing a hat
Hermes: [calls image_generate tool with ImageRouter]

You: Create a 5-second video of waves crashing
Hermes: [calls video_generate tool with ImageRouter]
```

## 📋 Available Models

### Image Generation Models

| Model ID | Description | Price |
|----------|-------------|-------|
| `openai/gpt-image-2` | GPT Image 2 - High quality, versatile | $0.04/image |
| `openai/gpt-image-1.5` | GPT Image 1.5 - Balanced quality and speed | $0.02/image |
| `black-forest-labs/FLUX-1.1-pro` | FLUX 1.1 Pro - Photorealistic, detailed | $0.04/image |

### Video Generation Models

| Model ID | Description | Modalities | Price |
|----------|-------------|------------|-------|
| `xAI/grok-imagine-video` | Grok Imagine Video - High quality, supports audio | text, image | $0.10/s |
| `bytedance/seedance-1.5-pro` | Seedance 1.5 Pro - Fast, good motion | text | $0.08/s |
| `google/veo-3.1-lite` | Veo 3.1 Lite - Fast, lightweight | text | $0.05/s |

## 🎨 Image Generation Examples

### Basic Text-to-Image

```python
# Hermes will call:
image_generate(
    prompt="A serene mountain landscape at sunset",
    aspect_ratio="16:9"
)
```

### Custom Model

```python
image_generate(
    prompt="A futuristic city skyline",
    model="black-forest-labs/FLUX-1.1-pro",
    aspect_ratio="1:1"
)
```

## 🎬 Video Generation Examples

### Text-to-Video

```python
# Hermes will call:
video_generate(
    prompt="A cat playing with a ball of yarn",
    duration=5,
    aspect_ratio="16:9"
)
```

### Image-to-Video (Animate an Image)

```python
video_generate(
    prompt="Add gentle motion to this landscape",
    image_url="https://example.com/landscape.jpg",
    duration=5,
    aspect_ratio="16:9"
)
```

### With Audio

```python
video_generate(
    prompt="A bustling city street with traffic sounds",
    duration=10,
    audio=True,
    model="xAI/grok-imagine-video"
)
```

## 🔧 Advanced Configuration

### Custom Base URL

If you're using a self-hosted ImageRouter instance:

```bash
export IMAGEROUTER_BASE_URL="https://your-instance.com/v1/openai"
```

### Aspect Ratios

Supported aspect ratios:
- `1:1` - Square (1024x1024)
- `16:9` - Landscape (1792x1024)
- `9:16` - Portrait (1024x1792)
- `4:3` - Standard (1536x1152)
- `3:4` - Portrait (1152x1536)

### Video Durations

- Minimum: 1 second
- Maximum: 10 seconds
- Default: 5 seconds (when not specified)

## 🐛 Troubleshooting

### Plugin Not Found

```bash
# Check if plugins are discovered
cd /path/to/hermes-agent
python3 -c "
from plugins.image_gen.imagerouter import ImageRouterImageGenProvider
print('Image plugin OK')
from plugins.video_gen.imagerouter import ImageRouterVideoGenProvider
print('Video plugin OK')
"
```

### API Key Not Working

```bash
# Verify API key is set
echo $IMAGEROUTER_API_KEY

# Test availability
python3 -c "
import os
os.environ['IMAGEROUTER_API_KEY'] = 'your-key'
from plugins.image_gen.imagerouter import ImageRouterImageGenProvider
provider = ImageRouterImageGenProvider()
print(f'Available: {provider.is_available()}')
"
```

### Check Provider Registration

```bash
# In Hermes CLI
hermes tools

# Look for "ImageRouter" in the image/video generation sections
```

## 📚 Integration with Open Design

ImageRouter is also integrated in Open Design for project-based workflows:

```typescript
// Open Design uses the same ImageRouter API
// Located in: integrations/open-design/apps/daemon/src/media.ts

// Image generation
await generateMedia({
  surface: 'image',
  provider: 'imagerouter',
  model: 'openai/gpt-image-2',
  prompt: 'A beautiful sunset'
});

// Video generation
await generateMedia({
  surface: 'video',
  provider: 'imagerouter',
  model: 'xAI/grok-imagine-video',
  prompt: 'Waves crashing on the beach',
  duration: 5
});
```

## 🔗 Related Files

- Image plugin: `plugins/image_gen/imagerouter/`
- Video plugin: `plugins/video_gen/imagerouter/`
- Open Design integration: `integrations/open-design/apps/daemon/src/media.ts`
- Tests: `test_imagerouter_plugins.py`, `test_plugin_integration.py`

## 📝 Next Steps

1. **Commit the plugins**:
   ```bash
   cd hermes-agent
   git add plugins/image_gen/imagerouter plugins/video_gen/imagerouter
   git commit -m "feat: add ImageRouter image and video generation plugins"
   ```

2. **Sync to your main project**:
   ```bash
   # The sync will copy to src-tauri/hermes-source/
   ```

3. **Configure and test**:
   ```bash
   export IMAGEROUTER_API_KEY="your-key"
   hermes tools
   # Select imagerouter as provider
   ```

4. **Use in conversations**:
   ```bash
   hermes
   # Ask Hermes to generate images or videos
   ```

## 🎉 Success!

You now have a unified image and video generation system that works in:
- ✅ Hermes Agent conversations (via plugins)
- ✅ Open Design projects (via media.ts)
- ✅ Both using the same ImageRouter API

Enjoy creating! 🚀
