#!/usr/bin/env python3
"""
Whisper API Test Script
Tests audio transcription against the whisper-server with GPU monitoring
"""

import requests
import json
import subprocess
import time
from pathlib import Path
import sys


class WhisperTester:
    def __init__(self, audio_file="test.wav", model="whisper-1", url="http://localhost:9090/v1/audio/transcriptions"):
        self.audio_file = Path(audio_file)
        self.model = model
        self.url = url
        self.timeout = 120  # 2 minutes timeout for transcription

    def check_file(self):
        """Verify audio file exists"""
        if not self.audio_file.exists():
            print(f"❌ Error: Audio file not found: {self.audio_file}")
            return False
        print(f"✓ Audio file found: {self.audio_file}")
        print(f"  Size: {self.audio_file.stat().st_size / 1024 / 1024:.2f}MB")
        return True

    def get_gpu_status(self):
        """Get current GPU status using nvidia-smi"""
        try:
            result = subprocess.run(
                ["nvidia-smi", "--query-gpu=index,name,memory.used,memory.total,temperature.gpu,utilization.gpu",
                 "--format=csv,noheader,nounits"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"⚠️  Could not get GPU status: {e}")
        return None

    def get_docker_logs(self, lines=10):
        """Get recent docker container logs"""
        try:
            result = subprocess.run(
                ["docker", "logs", "--tail", str(lines), "whisper-server"],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except Exception as e:
            print(f"⚠️  Could not get docker logs: {e}")
        return None

    def test_connectivity(self):
        """Test if the API endpoint is reachable"""
        try:
            response = requests.get(f"{self.url.rsplit('/', 1)[0]}/health", timeout=5)
            print(f"✓ API endpoint accessible (status: {response.status_code})")
            return True
        except requests.exceptions.ConnectionError:
            print(f"❌ Cannot connect to {self.url}")
            return False
        except Exception as e:
            print(f"⚠️  API connectivity check failed: {e}")
            return False

    def transcribe(self):
        """Send transcription request to the server"""
        try:
            print(f"\n🚀 Sending {self.audio_file.name} to whisper-server...")
            print(f"   Model: {self.model}")

            start_time = time.time()

            with open(self.audio_file, 'rb') as f:
                files = {'file': (self.audio_file.name, f, 'audio/wav')}
                data = {'model': self.model}

                response = requests.post(
                    self.url,
                    files=files,
                    data=data,
                    timeout=self.timeout
                )

            duration = time.time() - start_time

            if response.status_code == 200:
                result = response.json()
                print(f"\n✅ Success! (took {duration:.2f}s)")
                print(f"\n📝 Transcription:")
                print(f"   {result.get('text', 'No text returned')}")
                return result
            else:
                print(f"\n❌ Error: HTTP {response.status_code}")
                print(f"   Response: {response.text}")
                return None

        except requests.exceptions.Timeout:
            print(f"❌ Request timed out after {self.timeout}s")
            return None
        except Exception as e:
            print(f"❌ Error during transcription: {e}")
            return None

    def run(self):
        """Run full test suite"""
        print("=" * 50)
        print("🎤 Whisper Server Test Suite")
        print("=" * 50)
        print()

        # Pre-flight checks
        print("📋 Pre-flight checks:")
        if not self.check_file():
            return False

        print(f"\n📊 GPU Status (BEFORE):")
        gpu_before = self.get_gpu_status()
        if gpu_before:
            print(f"   {gpu_before}")
        else:
            print("   (GPU info unavailable)")

        print(f"\n🔌 API Status:")
        if not self.test_connectivity():
            print("   Trying to start docker-compose...")
            try:
                subprocess.run(
                    ["docker-compose", "up", "-d"],
                    cwd="docker",
                    timeout=60
                )
                time.sleep(5)
                if not self.test_connectivity():
                    return False
            except Exception as e:
                print(f"❌ Could not start docker-compose: {e}")
                return False

        print(f"\n📋 Recent Server Logs:")
        logs = self.get_docker_logs(5)
        if logs:
            for line in logs.split('\n'):
                print(f"   {line}")

        # Run transcription
        result = self.transcribe()

        print(f"\n📊 GPU Status (AFTER):")
        gpu_after = self.get_gpu_status()
        if gpu_after:
            print(f"   {gpu_after}")
        else:
            print("   (GPU info unavailable)")

        print()
        print("=" * 50)
        print("✨ Test complete!")
        print("=" * 50)

        return result is not None


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Test Whisper transcription server")
    parser.add_argument("--audio", default="test.wav", help="Path to audio file (default: test.wav)")
    parser.add_argument("--model", default="whisper-1", help="Model name (default: whisper-1)")
    parser.add_argument("--url", default="http://localhost:9090/v1/audio/transcriptions",
                       help="API endpoint URL")

    args = parser.parse_args()

    tester = WhisperTester(audio_file=args.audio, model=args.model, url=args.url)
    success = tester.run()

    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
