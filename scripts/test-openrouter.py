#!/usr/bin/env python3
"""
Simple OpenRouter API test script.
Tests if the API key is valid and can make a basic request.
"""

import os
import sys
import json
import requests
from pathlib import Path

def load_api_key():
    """Load API key from environment or mellona config."""
    # Try environment first
    api_key = os.environ.get('OPENROUTER_API_KEY')
    if api_key:
        print("✓ Found API key in OPENROUTER_API_KEY environment variable")
        return api_key

    # Try mellona config
    mellona_config_path = Path.home() / '.config' / 'mellona' / 'config.yaml'
    if mellona_config_path.exists():
        print(f"⚠️  Found mellona config at {mellona_config_path}")
        print(f"   (Credentials are managed by mellona, not second_voice)")

    print("❌ No API key found in environment")
    print(f"   To configure OpenRouter credentials:")
    print(f"   1. Set OPENROUTER_API_KEY environment variable, OR")
    print(f"   2. Configure mellona in ~/.config/mellona/config.yaml")
    print(f"   3. Run: mellona config --provider openrouter --api-key YOUR_KEY")
    return None


def test_api_key(api_key):
    """Test the API key with a simple request."""
    print(f"\n📋 Testing API key: {api_key[:10]}...{api_key[-5:]}")

    # Test models in order of preference (verified free models)
    models_to_test = [
        'meta-llama/llama-3.3-70b-instruct',
        'nousresearch/hermes-3-llama-3.1-405b',
        'google/gemma-3-27b-it',
        'qwen/qwen3-next-80b-a3b-instruct',
        'openai/gpt-oss-120b',
        'google/gemma-3-12b-it',
        'mistralai/mistral-small-3.1-24b-instruct',
        'meta-llama/llama-3.2-3b-instruct',
        'arcee-ai/trinity-large-preview',
        'upstage/solar-pro-3',
    ]

    for model in models_to_test:
        print(f"\n🧪 Testing model: {model}")

        try:
            response = requests.post(
                'https://openrouter.ai/api/v1/chat/completions',
                headers={
                    'Authorization': f'Bearer {api_key}',
                    'Content-Type': 'application/json'
                },
                json={
                    'model': model,
                    'messages': [
                        {
                            'role': 'user',
                            'content': 'Say "test ok" and nothing else.'
                        }
                    ]
                },
                timeout=30
            )

            status = response.status_code
            print(f"   Status: {status}")

            if status == 200:
                data = response.json()
                content = data['choices'][0]['message']['content']
                print(f"   ✅ SUCCESS!")
                print(f"   Response: {content[:100]}")
                return True

            elif status == 401:
                print(f"   ❌ Authentication failed (401)")
                print(f"   Error: Invalid or missing API key")
                return False

            elif status == 429:
                print(f"   ⏱️  Rate limited (429)")
                print(f"   This model may be rate limited, trying next...")
                continue

            elif status == 404:
                print(f"   ⚠️  Model not found (404)")
                print(f"   This model may be unavailable, trying next...")
                continue

            else:
                print(f"   ❌ Error {status}")
                try:
                    error_data = response.json()
                    print(f"   Details: {json.dumps(error_data, indent=2)}")
                except:
                    print(f"   Response: {response.text[:200]}")
                continue

        except requests.Timeout:
            print(f"   ⏱️  Timeout (30s)")
            print(f"   Network too slow, trying next...")
            continue

        except requests.ConnectionError as e:
            print(f"   ❌ Connection failed: {e}")
            return False

        except Exception as e:
            print(f"   ❌ Unexpected error: {type(e).__name__}: {e}")
            return False

    print(f"\n❌ All models failed or were rate limited")
    return False


def main():
    print("=" * 60)
    print("OpenRouter API Key Validator")
    print("=" * 60)

    api_key = load_api_key()
    if not api_key:
        print("\n❌ Cannot proceed without API key")
        return 1

    # Validate key format
    if len(api_key) < 10:
        print(f"❌ API key appears invalid (too short: {len(api_key)} chars)")
        return 1

    # Test the key
    success = test_api_key(api_key)

    print("\n" + "=" * 60)
    if success:
        print("✅ API key is valid and working!")
        print("=" * 60)
        return 0
    else:
        print("❌ API key validation failed")
        print("=" * 60)
        print("\nTroubleshooting:")
        print("  1. Check that OPENROUTER_API_KEY is set correctly")
        print("  2. Visit https://openrouter.ai/settings/integrations to verify")
        print("  3. Ensure you have API credits available")
        print("  4. Check that free models are available in your region")
        return 1


if __name__ == '__main__':
    sys.exit(main())
