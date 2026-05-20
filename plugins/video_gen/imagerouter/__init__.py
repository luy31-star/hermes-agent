"""ImageRouter video generation provider plugin."""

from __future__ import annotations

import os
from typing import Any, Dict, List, Optional

from agent.video_gen_provider import (
    VideoGenProvider,
    error_response,
    success_response,
)


class ImageRouterVideoGenProvider(VideoGenProvider):
    """ImageRouter provider for video generation.
    
    Routes to multiple video generation models through a unified API.
    """

    @property
    def name(self) -> str:
        return "imagerouter"

    @property
    def display_name(self) -> str:
        return "ImageRouter"

    def is_available(self) -> bool:
        """Check if ImageRouter API key is configured."""
        return bool(os.environ.get("IMAGEROUTER_API_KEY", "").strip())

    def list_models(self) -> List[Dict[str, Any]]:
        """Return available ImageRouter video models (诗云API支持的所有模型)."""
        return [
            # ===== 诗云 API 托管模型 (Hermes Hosted) =====
            {
                "id": "doubao-seedance-1-0-pro-fast-251015",
                "display": "Doubao Seedance Pro",
                "speed": "fast",
                "strengths": "Fast t2v / i2v",
                "modalities": ["text", "image"],
                "price": "积分计费",
            },
            {
                "id": "sora-2",
                "display": "Sora 2",
                "speed": "medium",
                "strengths": "High quality text-to-video",
                "modalities": ["text"],
                "price": "积分计费",
            },
            {
                "id": "sora-2-pro",
                "display": "Sora 2 Pro",
                "speed": "slow",
                "strengths": "Highest quality",
                "modalities": ["text"],
                "price": "积分计费",
            },
            {
                "id": "MiniMax-Hailuo-02",
                "display": "Hailuo 02",
                "speed": "medium",
                "strengths": "MiniMax video, t2v + i2v",
                "modalities": ["text", "image"],
                "price": "积分计费",
            },
            {
                "id": "wan2.6-i2v",
                "display": "Wan 2.6 I2V",
                "speed": "fast",
                "strengths": "Tongyi Wanxiang image-to-video",
                "modalities": ["image"],
                "price": "积分计费",
            },
            
            # ===== Kling 系列 (诗云托管) =====
            {
                "id": "kling-video",
                "display": "Kling Text to Video",
                "speed": "medium",
                "strengths": "Text-to-video",
                "modalities": ["text"],
                "price": "积分计费",
            },
            {
                "id": "kling-image2video",
                "display": "Kling Image to Video",
                "speed": "medium",
                "strengths": "Image-to-video",
                "modalities": ["image"],
                "price": "积分计费",
            },
            {
                "id": "kling-multi-image2video",
                "display": "Kling Multi Image to Video",
                "speed": "medium",
                "strengths": "Multiple images to video",
                "modalities": ["image"],
                "price": "积分计费",
            },
            {
                "id": "kling-omni-video",
                "display": "Kling Omni Video",
                "speed": "medium",
                "strengths": "Omnidirectional video generation",
                "modalities": ["text", "image"],
                "price": "积分计费",
            },
            {
                "id": "kling-2.0",
                "display": "Kling 2.0",
                "speed": "medium",
                "strengths": "Kuaishou latest",
                "modalities": ["text", "image"],
                "price": "积分计费",
            },
            {
                "id": "kling-1.6",
                "display": "Kling 1.6",
                "speed": "medium",
                "strengths": "Kuaishou",
                "modalities": ["text", "image"],
                "price": "积分计费",
            },
            {
                "id": "kling-1.5",
                "display": "Kling 1.5",
                "speed": "medium",
                "strengths": "Kuaishou",
                "modalities": ["text", "image"],
                "price": "积分计费",
            },
            
            # ===== Google Veo 系列 =====
            {
                "id": "veo3.1-fast",
                "display": "Veo 3.1 Fast",
                "speed": "fast",
                "strengths": "Fast, via FAL",
                "modalities": ["text"],
                "price": "积分计费",
            },
            {
                "id": "veo3.1",
                "display": "Veo 3.1",
                "speed": "medium",
                "strengths": "High quality, via FAL",
                "modalities": ["text"],
                "price": "积分计费",
            },
            {
                "id": "veo-3",
                "display": "Veo 3",
                "speed": "medium",
                "strengths": "Google sound-on",
                "modalities": ["text"],
                "audio": True,
                "price": "积分计费",
            },
            {
                "id": "veo-2",
                "display": "Veo 2",
                "speed": "medium",
                "strengths": "Google",
                "modalities": ["text"],
                "price": "积分计费",
            },
            
            # ===== Vidu =====
            {
                "id": "vidu2.0",
                "display": "Vidu 2.0",
                "speed": "medium",
                "strengths": "Vidu video generation",
                "modalities": ["text"],
                "price": "积分计费",
            },
            
            # ===== Volcengine Seedance 系列 =====
            {
                "id": "doubao-seedance-2-0-260128",
                "display": "Seedance 2.0",
                "speed": "medium",
                "strengths": "ByteDance t2v + i2v + audio",
                "modalities": ["text", "image"],
                "audio": True,
                "price": "积分计费",
            },
            {
                "id": "doubao-seedance-2-0-fast-260128",
                "display": "Seedance 2.0 Fast",
                "speed": "fast",
                "strengths": "ByteDance faster, cheaper",
                "modalities": ["text", "image"],
                "audio": True,
                "price": "积分计费",
            },
            {
                "id": "doubao-seedance-1-0-pro-250528",
                "display": "Seedance 1.0 Pro",
                "speed": "medium",
                "strengths": "ByteDance 1.0",
                "modalities": ["text", "image"],
                "price": "积分计费",
            },
            {
                "id": "doubao-seedance-1-0-lite-i2v-250428",
                "display": "Seedance 1.0 Lite I2V",
                "speed": "fast",
                "strengths": "ByteDance image-to-video",
                "modalities": ["image"],
                "price": "积分计费",
            },
            {
                "id": "doubao-seedance-1-0-lite-t2v-250428",
                "display": "Seedance 1.0 Lite T2V",
                "speed": "fast",
                "strengths": "ByteDance text-to-video",
                "modalities": ["text"],
                "price": "积分计费",
            },
            
            # ===== xAI Grok =====
            {
                "id": "grok-imagine-video",
                "display": "Grok Imagine Video",
                "speed": "medium",
                "strengths": "720p t2v + i2v + native audio",
                "modalities": ["text", "image"],
                "audio": True,
                "price": "积分计费",
            },
            {
                "id": "xAI/grok-imagine-video",
                "display": "xAI Grok Imagine Video (路由)",
                "speed": "medium",
                "strengths": "High quality, supports audio",
                "modalities": ["text", "image"],
                "audio": True,
                "price": "$0.10/s",
            },
            
            # ===== MiniMax =====
            {
                "id": "minimax-video-01",
                "display": "MiniMax Video 01",
                "speed": "medium",
                "strengths": "MiniMax Hailuo",
                "modalities": ["text", "image"],
                "price": "积分计费",
            },
            
            # ===== 其他路由模型 =====
            {
                "id": "bytedance/seedance-1.5-pro",
                "display": "Seedance 1.5 Pro (路由)",
                "speed": "fast",
                "strengths": "Fast, good motion",
                "modalities": ["text"],
                "price": "$0.08/s",
            },
            {
                "id": "google/veo-3.1-lite",
                "display": "Veo 3.1 Lite (路由)",
                "speed": "fast",
                "strengths": "Fast, lightweight",
                "modalities": ["text"],
                "price": "$0.05/s",
            },
        ]

    def default_model(self) -> Optional[str]:
        return "doubao-seedance-1-0-pro-fast-251015"

    def capabilities(self) -> Dict[str, Any]:
        return {
            "modalities": ["text", "image"],
            "aspect_ratios": ["16:9", "9:16", "1:1"],
            "resolutions": ["720p", "1080p"],
            "min_duration": 1,
            "max_duration": 10,
            "supports_audio": True,
            "supports_negative_prompt": False,
            "max_reference_images": 0,
        }

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "ImageRouter (诗云API)",
            "badge": "paid",
            "tag": "统一视频生成API - 支持15+模型",
            "env_vars": [
                {
                    "key": "IMAGEROUTER_API_KEY",
                    "prompt": "诗云API密钥 / ImageRouter API key",
                    "url": "https://api.imagerouter.io",
                },
            ],
        }

    def generate(
        self,
        prompt: str,
        *,
        model: Optional[str] = None,
        image_url: Optional[str] = None,
        duration: Optional[int] = None,
        aspect_ratio: str = "16:9",
        resolution: str = "720p",
        audio: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate a video using ImageRouter API."""
        import httpx

        api_key = os.environ.get("IMAGEROUTER_API_KEY", "").strip()
        if not api_key:
            return error_response(
                error="IMAGEROUTER_API_KEY not configured",
                error_type="missing_credentials",
                provider=self.name,
                model=model or "",
                prompt=prompt,
            )

        base_url = os.environ.get(
            "IMAGEROUTER_BASE_URL",
            "https://api.imagerouter.io/v1/openai"
        ).rstrip("/")

        model_id = model or self.default_model()

        # Map aspect ratio to size
        size_map = {
            "1:1": "1024x1024",
            "16:9": "1792x1024",
            "9:16": "1024x1792",
        }
        size = size_map.get(aspect_ratio, "1792x1024")

        # Determine modality
        modality = "image" if image_url else "text"

        try:
            payload: Dict[str, Any] = {
                "model": model_id,
                "prompt": prompt,
                "size": size,
                "response_format": "b64_json",
            }

            if image_url:
                payload["image_url"] = image_url

            if duration:
                payload["seconds"] = duration
            else:
                payload["seconds"] = "auto"

            if audio is not None:
                payload["audio"] = audio

            response = httpx.post(
                f"{base_url}/videos/generations",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json=payload,
                timeout=120.0,
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("data"):
                return error_response(
                    error="No video data in response",
                    error_type="api_error",
                    provider=self.name,
                    model=model_id,
                    prompt=prompt,
                )

            b64_data = data["data"][0].get("b64_json")
            if not b64_data:
                return error_response(
                    error="No b64_json in response",
                    error_type="api_error",
                    provider=self.name,
                    model=model_id,
                    prompt=prompt,
                )

            # Save to cache
            from tools.video_generation_tool import save_b64_video
            video_path = save_b64_video(b64_data)

            return success_response(
                video=video_path,
                model=model_id,
                prompt=prompt,
                modality=modality,
                aspect_ratio=aspect_ratio,
                duration=duration or 5,
                provider=self.name,
            )

        except httpx.HTTPError as e:
            return error_response(
                error=f"ImageRouter API error: {str(e)}",
                error_type="api_error",
                provider=self.name,
                model=model_id,
                prompt=prompt,
            )


def register(ctx) -> None:
    """Register ImageRouter video generation provider."""
    ctx.register_video_gen_provider(ImageRouterVideoGenProvider())
