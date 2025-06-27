#!/usr/bin/env python3
"""Test minion response to see if using real Gemini"""

import requests
import json
import time

# First spawn a test minion
spawn_data = {
    "name": "TestBot",
    "personality": "enthusiastic",
    "quirks": ["loves exclamation marks", "always positive"],
    "catchphrases": ["Let's go!", "Amazing!"],
    "expertise": ["testing", "being helpful"]
}

# Spawn the minion
print("Spawning test minion...")
response = requests.post("http://localhost:8000/api/v2/minions/spawn", json=spawn_data)
if response.status_code != 200:
    print(f"Failed to spawn minion: {response.status_code} - {response.text}")
    exit(1)

minion = response.json()
print(f"Response: {json.dumps(minion, indent=2)}")
if 'persona' in minion and 'name' in minion['persona']:
    print(f"✅ Spawned minion: {minion['persona']['name']} ({minion['minion_id']})")
else:
    print(f"✅ Spawned minion: {minion.get('minion_id', 'unknown')}")

# Wait a moment for minion to initialize
time.sleep(2)

# Send a test message to general channel
message_data = {
    "content": "Hello minions! Can you tell me about your capabilities?",
    "sender": "test_user",
    "channel_id": "general"
}

print("\nSending test message to general channel...")
response = requests.post("http://localhost:8000/api/v2/channels/general/messages", json=message_data)
if response.status_code == 200:
    print("✅ Message sent successfully")
else:
    print(f"Failed to send message: {response.status_code} - {response.text}")

# Wait for response
print("\nWaiting for minion response...")
time.sleep(3)

# Get channel messages
response = requests.get("http://localhost:8000/api/v2/channels/general/messages?limit=10")
if response.status_code == 200:
    data = response.json()
    messages = data.get('messages', [])
    print(f"\nFound {len(messages)} messages in channel:")
    for msg in messages[-5:]:  # Show last 5 messages
        print(f"[{msg.get('sender_id', 'unknown')}]: {msg.get('content', '')[:100]}...")
else:
    print(f"Failed to get messages: {response.status_code}")
