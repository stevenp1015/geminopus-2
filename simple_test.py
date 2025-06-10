#!/usr/bin/env python3
import requests
import json

BASE_URL = "http://localhost:8000"

print("=== SIMPLE DIAGNOSTIC TEST ===")

# Test 1: Health
print("1. Backend health:")
resp = requests.get(f"{BASE_URL}/api/health")
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text}")

# Test 2: Channels
print("\n2. Channels:")
resp = requests.get(f"{BASE_URL}/api/channels")
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text[:200]}...")

# Test 3: Minions
print("\n3. Minions:")
resp = requests.get(f"{BASE_URL}/api/minions")
print(f"   Status: {resp.status_code}")
print(f"   Response: {resp.text[:200]}...")