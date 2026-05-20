#!/usr/bin/env python3
"""Integration test for ImageRouter plugins with Hermes registries."""

import os
import sys

# Mock environment
os.environ["IMAGEROUTER_API_KEY"] = "test-key-12345"

def test_image_gen_registry():
    """Test ImageRouter plugin with image generation registry."""
    print("=" * 60)
    print("Testing Image Generation Registry Integration")
    print("=" * 60)
    
    try:
        from agent.image_gen_registry import (
            register_provider,
            get_provider,
            list_providers,
        )
        from plugins.image_gen.imagerouter import ImageRouterImageGenProvider
        
        # Register the provider
        provider = ImageRouterImageGenProvider()
        register_provider(provider)
        print(f"✓ Registered provider: {provider.name}")
        
        # Retrieve it from registry
        retrieved = get_provider("imagerouter")
        if retrieved:
            print(f"✓ Retrieved provider from registry: {retrieved.name}")
            print(f"  - Display name: {retrieved.display_name}")
            print(f"  - Available: {retrieved.is_available()}")
        else:
            print("❌ Failed to retrieve provider from registry")
            return False
        
        # List all providers
        all_providers = list_providers()
        imagerouter_found = any(p.name == "imagerouter" for p in all_providers)
        print(f"✓ Total providers in registry: {len(all_providers)}")
        print(f"✓ ImageRouter in registry: {imagerouter_found}")
        
        print("\n✅ Image generation registry integration successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Image generation registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_video_gen_registry():
    """Test ImageRouter plugin with video generation registry."""
    print("\n" + "=" * 60)
    print("Testing Video Generation Registry Integration")
    print("=" * 60)
    
    try:
        from agent.video_gen_registry import (
            register_provider,
            get_provider,
            list_providers,
        )
        from plugins.video_gen.imagerouter import ImageRouterVideoGenProvider
        
        # Register the provider
        provider = ImageRouterVideoGenProvider()
        register_provider(provider)
        print(f"✓ Registered provider: {provider.name}")
        
        # Retrieve it from registry
        retrieved = get_provider("imagerouter")
        if retrieved:
            print(f"✓ Retrieved provider from registry: {retrieved.name}")
            print(f"  - Display name: {retrieved.display_name}")
            print(f"  - Available: {retrieved.is_available()}")
            
            # Test capabilities
            caps = retrieved.capabilities()
            print(f"  - Modalities: {', '.join(caps['modalities'])}")
            print(f"  - Duration range: {caps['min_duration']}-{caps['max_duration']}s")
        else:
            print("❌ Failed to retrieve provider from registry")
            return False
        
        # List all providers
        all_providers = list_providers()
        imagerouter_found = any(p.name == "imagerouter" for p in all_providers)
        print(f"✓ Total providers in registry: {len(all_providers)}")
        print(f"✓ ImageRouter in registry: {imagerouter_found}")
        
        print("\n✅ Video generation registry integration successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Video generation registry test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plugin_context():
    """Test plugin registration through PluginContext."""
    print("\n" + "=" * 60)
    print("Testing Plugin Context Registration")
    print("=" * 60)
    
    try:
        # Import registries first to ensure they're initialized
        from agent import image_gen_registry, video_gen_registry
        
        # Create a mock plugin context
        class PluginContext:
            def register_image_gen_provider(self, provider):
                image_gen_registry.register_provider(provider)
                print(f"✓ Registered image provider via context: {provider.name}")
            
            def register_video_gen_provider(self, provider):
                video_gen_registry.register_provider(provider)
                print(f"✓ Registered video provider via context: {provider.name}")
        
        ctx = PluginContext()
        
        # Test image plugin registration
        from plugins.image_gen.imagerouter import register as register_image
        register_image(ctx)
        
        # Test video plugin registration
        from plugins.video_gen.imagerouter import register as register_video
        register_video(ctx)
        
        # Verify registration
        image_provider = image_gen_registry.get_provider("imagerouter")
        video_provider = video_gen_registry.get_provider("imagerouter")
        
        print(f"\n✓ Image provider registered: {image_provider is not None}")
        print(f"✓ Video provider registered: {video_provider is not None}")
        
        print("\n✅ Plugin context registration successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Plugin context test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_model_catalog():
    """Test that models are properly listed."""
    print("\n" + "=" * 60)
    print("Testing Model Catalog")
    print("=" * 60)
    
    try:
        from plugins.image_gen.imagerouter import ImageRouterImageGenProvider
        from plugins.video_gen.imagerouter import ImageRouterVideoGenProvider
        
        image_provider = ImageRouterImageGenProvider()
        video_provider = ImageRouterVideoGenProvider()
        
        # Test image models
        image_models = image_provider.list_models()
        print(f"✓ Image models available: {len(image_models)}")
        for model in image_models:
            print(f"  - {model['id']}")
            assert 'display' in model
            assert 'price' in model
        
        # Test video models
        video_models = video_provider.list_models()
        print(f"\n✓ Video models available: {len(video_models)}")
        for model in video_models:
            print(f"  - {model['id']}")
            assert 'display' in model
            assert 'modalities' in model
        
        print("\n✅ Model catalog test successful!")
        return True
        
    except Exception as e:
        print(f"\n❌ Model catalog test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all integration tests."""
    print("\n🧪 ImageRouter Plugin Integration Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("Model Catalog", test_model_catalog()))
    results.append(("Image Registry", test_image_gen_registry()))
    results.append(("Video Registry", test_video_gen_registry()))
    results.append(("Plugin Context", test_plugin_context()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Integration Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All integration tests passed!")
        print("\n📝 Next steps:")
        print("  1. Commit the plugins to your hermes-agent repository")
        print("  2. Sync to src-tauri/hermes-source/")
        print("  3. Configure IMAGEROUTER_API_KEY in your environment")
        print("  4. Run: hermes tools")
        print("  5. Select 'imagerouter' as your image/video provider")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
