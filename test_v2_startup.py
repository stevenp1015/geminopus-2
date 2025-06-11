#!/usr/bin/env python3
"""
Quick V2 Backend Startup Test

This tests if the V2 backend can actually start without errors.
"""

import subprocess
import time
import requests
import sys
import os


def test_v2_startup():
    """Test if V2 backend starts successfully"""
    print("🚀 Testing Gemini Legion V2 Backend Startup...")
    
    # Start the backend
    backend_process = subprocess.Popen(
        [sys.executable, "-m", "gemini_legion_backend.main_v2"],
        cwd="/users/ttig/downloads/geminopus-branch",
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True
    )
    
    # Give it time to start
    print("⏳ Waiting for backend to initialize...")
    time.sleep(5)
    
    # Check if process is still running
    if backend_process.poll() is not None:
        # Process died, get error output
        stdout, stderr = backend_process.communicate()
        print("\n❌ Backend failed to start!")
        print("\nSTDOUT:")
        print(stdout)
        print("\nSTDERR:")
        print(stderr)
        return False
    
    # Try to hit the health endpoint
    try:
        response = requests.get("http://localhost:8000/api/v2/status")
        if response.status_code == 200:
            print("\n✅ Backend is running!")
            print(f"Response: {response.json()}")
            backend_process.terminate()
            return True
        else:
            print(f"\n⚠️ Backend responded but with status {response.status_code}")
            backend_process.terminate()
            return False
    except requests.ConnectionError:
        print("\n❌ Could not connect to backend")
        backend_process.terminate()
        return False
    except Exception as e:
        print(f"\n❌ Error testing backend: {e}")
        backend_process.terminate()
        return False


if __name__ == "__main__":
    os.chdir("/users/ttig/downloads/geminopus-branch")
    success = test_v2_startup()
    sys.exit(0 if success else 1)
