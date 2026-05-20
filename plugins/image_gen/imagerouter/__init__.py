"""ImageRouter image generation provider plugin."""

from __future__ import annotations

import base64
import os
from typing import Any, Dict, List, Optional

from agent.image_gen_provider import ImageGenProvider


class ImageRouterImageGenProvider(ImageGenProvider):
    """ImageRouter provider for image generation.
    
    Routes to multiple image generation models through a unified API.
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
        """Return available ImageRouter image models (诗云API支持的所有模型)."""
        return [
            # ===== 诗云 API 托管模型 (Hermes Hosted) =====
            {
                "id": "gpt-image-2",
                "display": "GPT Image 2",
                "speed": "fast",
                "strengths": "4K, native multimodal, inpainting",
                "price": "积分计费",
            },
            {
                "id": "gpt-image-1",
                "display": "GPT Image 1",
                "speed": "medium",
                "strengths": "Classic image model",
                "price": "积分计费",
            },
            
            # ===== OpenAI 官方 API =====
            {
                "id": "openai/gpt-image-2",
                "display": "OpenAI GPT Image 2",
                "speed": "fast",
                "strengths": "High quality, versatile",
                "price": "$0.04/image",
            },
            {
                "id": "openai/gpt-image-1.5",
                "display": "OpenAI GPT Image 1.5",
                "speed": "fast",
                "strengths": "4× faster than gpt-image-1",
                "price": "$0.02/image",
            },
            {
                "id": "openai/gpt-image-1",
                "display": "OpenAI GPT Image 1",
                "speed": "medium",
                "strengths": "ChatGPT native",
                "price": "$0.03/image",
            },
            {
                "id": "openai/gpt-image-1-mini",
                "display": "OpenAI GPT Image 1 Mini",
                "speed": "fast",
                "strengths": "Low-cost variant",
                "price": "$0.01/image",
            },
            {
                "id": "openai/dall-e-3",
                "display": "DALL-E 3",
                "speed": "medium",
                "strengths": "Classic OpenAI model",
                "price": "$0.04/image",
            },
            {
                "id": "openai/dall-e-2",
                "display": "DALL-E 2",
                "speed": "fast",
                "strengths": "Legacy model",
                "price": "$0.02/image",
            },
            
            # ===== Black Forest Labs FLUX =====
            {
                "id": "black-forest-labs/FLUX-1.1-pro",
                "display": "FLUX 1.1 Pro",
                "speed": "medium",
                "strengths": "Photorealistic, detailed",
                "price": "$0.04/image",
            },
            {
                "id": "flux-pro",
                "display": "FLUX Pro",
                "speed": "medium",
                "strengths": "High quality",
                "price": "$0.05/image",
            },
            {
                "id": "flux-dev",
                "display": "FLUX Dev",
                "speed": "fast",
                "strengths": "Open weights",
                "price": "$0.025/image",
            },
            {
                "id": "flux-schnell",
                "display": "FLUX Schnell",
                "speed": "very fast",
                "strengths": "Speed optimized",
                "price": "$0.003/image",
            },
            
            # ===== Volcengine (ByteDance Doubao) =====
            {
                "id": "doubao-seedream-3-0-t2i-250415",
                "display": "Seedream 3.0",
                "speed": "fast",
                "strengths": "ByteDance Doubao image",
                "price": "积分计费",
            },
            {
                "id": "doubao-seededit-3-0-i2i-250628",
                "display": "Seededit 3.0",
                "speed": "fast",
                "strengths": "ByteDance image edit",
                "price": "积分计费",
            },
            
            # ===== xAI Grok =====
            {
                "id": "grok-imagine-image",
                "display": "Grok Imagine Image",
                "speed": "fast",
                "strengths": "2K text-to-image, 11+ aspect ratios",
                "price": "积分计费",
            },
            
            # ===== Google =====
            {
                "id": "imagen-4",
                "display": "Imagen 4",
                "speed": "medium",
                "strengths": "Google latest",
                "price": "$0.04/image",
            },
            {
                "id": "imagen-3",
                "display": "Imagen 3",
                "speed": "medium",
                "strengths": "Google",
                "price": "$0.03/image",
            },
            {
                "id": "gemini-3.1-flash-image-preview",
                "display": "Nano Banana 2",
                "speed": "fast",
                "strengths": "Nano Banana text-to-image",
                "price": "积分计费",
            },
            
            # ===== Midjourney =====
            {
                "id": "midjourney-v7",
                "display": "Midjourney v7",
                "speed": "medium",
                "strengths": "Artistic, high quality",
                "price": "via proxy",
            },
            
            # ===== Stable Diffusion =====
            {
                "id": "sd-3.5",
                "display": "Stable Diffusion 3.5",
                "speed": "fast",
                "strengths": "Open source",
                "price": "$0.01/image",
            },
            {
                "id": "sdxl",
                "display": "Stable Diffusion XL",
                "speed": "fast",
                "strengths": "SDXL",
                "price": "$0.01/image",
            },
            
            # ===== Ideogram =====
            {
                "id": "ideogram-v2",
                "display": "Ideogram v2",
                "speed": "medium",
                "strengths": "Typography, text rendering",
                "price": "$0.08/image",
            },
        ]

    def default_model(self) -> Optional[str]:
        return "gpt-image-2"  # 诗云托管的默认模型

    def get_setup_schema(self) -> Dict[str, Any]:
        return {
            "name": "ImageRouter (诗云API)",
            "badge": "paid",
            "tag": "统一图片生成API - 支持30+模型",
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
        aspect_ratio: str = "1:1",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Generate an image using ImageRouter API."""
        import httpx

        api_key = os.environ.get("IMAGEROUTER_API_KEY", "").strip()
        if not api_key:
            return {
                "success": False,
                "image": None,
                "error": "IMAGEROUTER_API_KEY not configured",
                "error_type": "missing_credentials",
            }

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
            "4:3": "1536x1152",
            "3:4": "1152x1536",
        }
        size = size_map.get(aspect_ratio, "1024x1024")

        try:
            response = httpx.post(
                f"{base_url}/images/generations",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "model": model_id,
                    "prompt": prompt,
                    "size": size,
                    "response_format": "b64_json",
                    "output_format": "png",
                },
                timeout=60.0,
            )
            response.raise_for_status()
            data = response.json()

            if not data.get("data"):
                return {
                    "success": False,
                    "image": None,
                    "error": "No image data in response",
                    "error_type": "api_error",
                }

            b64_data = data["data"][0].get("b64_json")
            if not b64_data:
                return {
                    "success": False,
                    "image": None,
                    "error": "No b64_json in response",
                    "error_type": "api_error",
                }

            # Save to cache
            from tools.image_generation_tool import save_b64_image
            image_path = save_b64_image(b64_data)

            return {
                "success": True,
                "image": image_path,
                "model": model_id,
                "prompt": prompt,
                "aspect_ratio": aspect_ratio,
                "provider": self.name,
            }

        except httpx.HTTPError as e:
            return {
                "success": False,
                "image": None,
                "error": f"ImageRouter API error: {str(e)}",
                "error_type": "api_error",
                "model": model_id,
                "prompt": prompt,
            }


def register(ctx) -> None:
    """Register ImageRouter image generation provider."""
    ctx.register_image_gen_provider(ImageRouterImageGenProvider())
