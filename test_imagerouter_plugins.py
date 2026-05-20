#!/usr/bin/env python3
"""Test ImageRouter plugins for image and video generation."""

import os
import sys

# Mock environment for testing
os.environ["IMAGEROUTER_API_KEY"] = "test-key-12345"
os.environ["IMAGEROUTER_BASE_URL"] = "https://api.imagerouter.io/v1/openai"

def test_image_plugin():
    """Test ImageRouter image generation plugin."""
    print("=" * 60)
    print("Testing ImageRouter Image Generation Plugin")
    print("=" * 60)
    
    try:
        # Import the plugin
        from plugins.image_gen.imagerouter import ImageRouterImageGenProvider
        
        provider = ImageRouterImageGenProvider()
        
        # Test basic properties
        print(f"✓ Plugin name: {provider.name}")
        print(f"✓ Display name: {provider.display_name}")
        print(f"✓ Is available: {provider.is_available()}")
        print(f"✓ Default model: {provider.default_model()}")
        
        # Test model list
        models = provider.list_models()
        print(f"✓ Available models: {len(models)}")
        for model in models:
            print(f"  - {model['id']}: {model['display']} ({model['price']})")
        
        # Test setup schema
        setup = provider.get_setup_schema()
        print(f"✓ Setup schema: {setup['name']} ({setup['badge']})")
        
        print("\n✅ Image plugin structure is valid!")
        return True
        
    except Exception as e:
        print(f"\n❌ Image plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_video_plugin():
    """Test ImageRouter video generation plugin."""
    print("\n" + "=" * 60)
    print("Testing ImageRouter Video Generation Plugin")
    print("=" * 60)
    
    try:
        # Import the plugin
        from plugins.video_gen.imagerouter import ImageRouterVideoGenProvider
        
        provider = ImageRouterVideoGenProvider()
        
        # Test basic properties
        print(f"✓ Plugin name: {provider.name}")
        print(f"✓ Display name: {provider.display_name}")
        print(f"✓ Is available: {provider.is_available()}")
        print(f"✓ Default model: {provider.default_model()}")
        
        # Test model list
        models = provider.list_models()
        print(f"✓ Available models: {len(models)}")
        for model in models:
            modalities = ", ".join(model.get('modalities', []))
            print(f"  - {model['id']}: {model['display']} ({modalities})")
        
        # Test capabilities
        caps = provider.capabilities()
        print(f"✓ Capabilities:")
        print(f"  - Modalities: {', '.join(caps['modalities'])}")
        print(f"  - Aspect ratios: {', '.join(caps['aspect_ratios'])}")
        print(f"  - Duration: {caps['min_duration']}-{caps['max_duration']}s")
        print(f"  - Audio support: {caps['supports_audio']}")
        
        # Test setup schema
        setup = provider.get_setup_schema()
        print(f"✓ Setup schema: {setup['name']} ({setup['badge']})")
        
        print("\n✅ Video plugin structure is valid!")
        return True
        
    except Exception as e:
        print(f"\n❌ Video plugin test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_plugin_registration():
    """Test plugin registration mechanism."""
    print("\n" + "=" * 60)
    print("Testing Plugin Registration")
    print("=" * 60)
    
    try:
        # Mock registration context
        class MockContext:
            def __init__(self):
                self.image_providers = []
                self.video_providers = []
            
            def register_image_gen_provider(self, provider):
                self.image_providers.append(provider)
                print(f"✓ Registered image provider: {provider.name}")
            
            def register_video_gen_provider(self, provider):
                self.video_providers.append(provider)
                print(f"✓ Registered video provider: {provider.name}")
        
        ctx = MockContext()
        
        # Test image plugin registration
        from plugins.image_gen.imagerouter import register as register_image
        register_image(ctx)
        
        # Test video plugin registration
        from plugins.video_gen.imagerouter import register as register_video
        register_video(ctx)
        
        print(f"\n✓ Total image providers registered: {len(ctx.image_providers)}")
        print(f"✓ Total video providers registered: {len(ctx.video_providers)}")
        
        print("\n✅ Plugin registration works correctly!")
        return True
        
    except Exception as e:
        print(f"\n❌ Plugin registration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_yaml_config():
    """Test plugin YAML configuration files."""
    print("\n" + "=" * 60)
    print("Testing Plugin YAML Configuration")
    print("=" * 60)
    
    try:
        import yaml
        
        # Test image plugin YAML
        with open("plugins/image_gen/imagerouter/plugin.yaml", "r") as f:
            image_config = yaml.safe_load(f)
        
        print("✓ Image plugin YAML:")
        print(f"  - name: {image_config['name']}")
        print(f"  - version: {image_config['version']}")
        print(f"  - kind: {image_config['kind']}")
        print(f"  - requires_env: {image_config['requires_env']}")
        
        # Test video plugin YAML
        with open("plugins/video_gen/imagerouter/plugin.yaml", "r") as f:
            video_config = yaml.safe_load(f)
        
        print("\n✓ Video plugin YAML:")
        print(f"  - name: {video_config['name']}")
        print(f"  - version: {video_config['version']}")
        print(f"  - kind: {video_config['kind']}")
        print(f"  - requires_env: {video_config['requires_env']}")
        
        print("\n✅ YAML configuration is valid!")
        return True
        
    except Exception as e:
        print(f"\n❌ YAML configuration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("\n🧪 ImageRouter Plugin Test Suite")
    print("=" * 60)
    
    results = []
    
    # Run tests
    results.append(("YAML Configuration", test_yaml_config()))
    results.append(("Image Plugin", test_image_plugin()))
    results.append(("Video Plugin", test_video_plugin()))
    results.append(("Plugin Registration", test_plugin_registration()))
    
    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print(f"\nTotal: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed!")
        return 0
    else:
        print(f"\n⚠️  {total - passed} test(s) failed")
        return 1


if __name__ == "__main__":
    sys.exit(main())
