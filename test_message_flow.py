#!/usr/bin/env python3
"""
Simple test script to verify message flow mechanics
Run this AFTER restarting the backend to test systematically
"""
import asyncio
import aiohttp
import json
from datetime import datetime

BASE_URL = "http://localhost:8000"

async def test_basic_flow():
    """Test the most basic message flow possible"""
    
    print("🔍 TESTING BASIC MESSAGE FLOW")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        
        # Step 1: Check health
        print("1️⃣ Testing backend health...")
        async with session.get(f"{BASE_URL}/api/health") as resp:
            if resp.status == 200:
                data = await resp.json()
                print(f"✅ Backend healthy: {data['minion_count']} minions, {data['active_channels']} channels")
            else:
                print(f"❌ Backend unhealthy: {resp.status}")
                return
        
        # Step 2: List channels
        print("\n2️⃣ Listing channels...")
        async with session.get(f"{BASE_URL}/api/channels") as resp:
            if resp.status == 200:
                channels = await resp.json()
                print(f"✅ Found {len(channels)} channels:")
                for i, ch in enumerate(channels):
                    if i >= 3: break  # Show first 3
                    print(f"   - {ch['name']} ({ch['channel_id']}) - {len(ch.get('members', []))} members")
            else:
                print(f"❌ Failed to get channels: {resp.status}")
                return
        
        # Step 3: List minions  
        print("\n3️⃣ Listing minions...")
        async with session.get(f"{BASE_URL}/api/minions") as resp:
            if resp.status == 200:
                minions = await resp.json()
                print(f"✅ Found {len(minions)} minions:")
                for i, m in enumerate(minions):
                    if i >= 3: break  # Show first 3
                    print(f"   - {m['name']} ({m['minion_id']}) - Status: {m.get('status', 'unknown')}")
            else:
                print(f"❌ Failed to get minions: {resp.status}")
                return
        
        # Step 4: Create test channel if needed
        test_channel_name = f"test_channel_{datetime.now().strftime('%H%M%S')}"
        print(f"\n4️⃣ Creating test channel: {test_channel_name}")
        async with session.post(f"{BASE_URL}/api/channels", json={
            "name": test_channel_name,
            "channel_type": "public",
            "description": "Test channel for debugging"
        }) as resp:
            if resp.status == 200:
                test_channel = await resp.json()
                test_channel_id = test_channel['channel_id']
                print(f"✅ Test channel created: {test_channel_id}")
            else:
                print(f"❌ Failed to create test channel: {resp.status}")
                return
        
        # Step 5: Add first minion to test channel (if any exist)
        if minions:
            first_minion = minions[0]
            minion_id = first_minion['minion_id']
            print(f"\n5️⃣ Adding minion {first_minion['name']} to test channel...")
            async with session.post(f"{BASE_URL}/api/channels/{test_channel_id}/members", json={
                "member_id": minion_id
            }) as resp:
                if resp.status == 200:
                    print(f"✅ Minion added to channel")
                else:
                    print(f"❌ Failed to add minion: {resp.status}")
        
        # Step 6: Send test message
        print(f"\n6️⃣ Sending test message to channel...")
        test_message = f"Test message at {datetime.now().strftime('%H:%M:%S')}"
        async with session.post(f"{BASE_URL}/api/channels/{test_channel_id}/send", json={
            "sender_id": "COMMANDER_PRIME", 
            "content": test_message
        }) as resp:
            if resp.status == 200:
                result = await resp.json()
                print(f"✅ Message sent successfully")
                print(f"   Message ID: {result.get('message_id')}")
            else:
                print(f"❌ Failed to send message: {resp.status}")
                error_text = await resp.text()
                print(f"   Error: {error_text}")
        
        # Step 7: Wait and check for responses
        print(f"\n7️⃣ Waiting 5 seconds for minion responses...")
        await asyncio.sleep(5)
        
        # Step 8: Fetch messages to see what happened
        print(f"\n8️⃣ Fetching messages from test channel...")
        async with session.get(f"{BASE_URL}/api/channels/{test_channel_id}/messages?limit=10") as resp:
            if resp.status == 200:
                messages = await resp.json()
                print(f"✅ Found {len(messages)} messages in channel:")
                for msg in messages:
                    sender = msg.get('sender_id', 'unknown')
                    content = msg.get('content', '')[:50] + "..." if len(msg.get('content', '')) > 50 else msg.get('content', '')
                    timestamp = msg.get('timestamp', '')
                    print(f"   [{timestamp}] {sender}: {content}")
            else:
                print(f"❌ Failed to fetch messages: {resp.status}")

if __name__ == "__main__":
    print("🧪 SYSTEMATIC MESSAGE FLOW TEST")
    print("Make sure backend is running on localhost:8000")
    print("This will create a test channel and verify basic mechanics\n")
    
    try:
        asyncio.run(test_basic_flow())
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
    
    print(f"\n🏁 Test completed at {datetime.now()}")