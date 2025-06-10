#!/usr/bin/env python3
import requests
import json
import time

BASE_URL = "http://localhost:8000"

print("🧪 CONTROLLED MESSAGE FLOW TEST")
print("=" * 50)

# Get current state
print("📊 Current State:")
health = requests.get(f"{BASE_URL}/api/health").json()
print(f"   Minions: {health['minion_count']}")
print(f"   Channels: {health['active_channels']}")

# Get the minion
minions_resp = requests.get(f"{BASE_URL}/api/minions").json()
if not minions_resp['minions']:
    print("❌ No minions found!")
    exit(1)

minion = minions_resp['minions'][0]
minion_id = minion['minion_id']
minion_name = minion.get('name', minion.get('persona', {}).get('name', 'Unknown'))
print(f"   Test Minion: {minion_name} ({minion_id})")

# Get channels
channels_resp = requests.get(f"{BASE_URL}/api/channels").json()
test_channels = [ch for ch in channels_resp['channels'] if minion_id in ch.get('members', [])]
if not test_channels:
    print("❌ Minion not in any channels!")
    exit(1)

test_channel = test_channels[0]
channel_id = test_channel['id']
channel_name = test_channel['name']
print(f"   Test Channel: {channel_name} ({channel_id})")

print(f"\n🎯 TESTING: Message from COMMANDER_PRIME to {channel_name}")
print(f"   Expected: {minion_name} should respond (rate limited to max 3 per minute)")

# Send test message
test_message = f"Hello {minion_name}, please respond with a simple acknowledgment."
print(f"\n📤 Sending message: '{test_message}'")

send_resp = requests.post(f"{BASE_URL}/api/channels/{channel_id}/send", json={
    "sender_id": "COMMANDER_PRIME",
    "content": test_message
})

if send_resp.status_code == 200:
    print("✅ Message sent successfully")
    msg_result = send_resp.json()
    print(f"   Message ID: {msg_result.get('message_id')}")
else:
    print(f"❌ Failed to send message: {send_resp.status_code}")
    print(f"   Error: {send_resp.text}")
    exit(1)

# Wait for minion response
print(f"\n⏳ Waiting 8 seconds for minion response...")
time.sleep(8)

# Check messages in channel
print(f"\n📥 Checking messages in {channel_name}:")
msgs_resp = requests.get(f"{BASE_URL}/api/channels/{channel_id}/messages?limit=5")
if msgs_resp.status_code == 200:
    messages = msgs_resp.json()
    print(f"   Found {len(messages)} recent messages:")
    
    commander_msgs = 0
    minion_msgs = 0
    
    for i, msg in enumerate(messages):
        sender = msg.get('sender_id', 'unknown')
        content = msg.get('content', '')[:80] + "..." if len(msg.get('content', '')) > 80 else msg.get('content', '')
        timestamp = msg.get('timestamp', '')[-8:]  # Last 8 chars (time)
        
        if sender == "COMMANDER_PRIME":
            commander_msgs += 1
            print(f"   [{i+1}] [{timestamp}] 👑 COMMANDER: {content}")
        elif sender == minion_id:
            minion_msgs += 1
            print(f"   [{i+1}] [{timestamp}] 🤖 {minion_name}: {content}")
        else:
            print(f"   [{i+1}] [{timestamp}] ❓ {sender}: {content}")
    
    print(f"\n📊 Message Analysis:")
    print(f"   Commander messages: {commander_msgs}")
    print(f"   {minion_name} responses: {minion_msgs}")
    
    if minion_msgs > 0:
        print("✅ SUCCESS: Minion responded to message!")
    else:
        print("❌ ISSUE: Minion did not respond")
        print("   Possible causes:")
        print("   - Rate limiting blocked response")
        print("   - WebSocket subscription issue")
        print("   - ADK integration problem")
        print("   - Communication system issue")
else:
    print(f"❌ Failed to get messages: {msgs_resp.status_code}")

print(f"\n🏁 Test completed")