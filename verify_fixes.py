#!/usr/bin/env python3
"""
Quick verification script for message duplication fixes
"""
import asyncio
import aiohttp
import json
from datetime import datetime
import time

BASE_URL = "http://localhost:8000"

async def verify_fixes():
    """Verify that message duplication is fixed"""
    
    print("🔍 VERIFYING MESSAGE DUPLICATION FIXES")
    print("=" * 50)
    
    async with aiohttp.ClientSession() as session:
        # Create a unique test channel
        test_channel_name = f"fix_test_{int(time.time())}"
        print(f"\n1️⃣ Creating test channel: {test_channel_name}")
        
        async with session.post(f"{BASE_URL}/api/channels/create", json={
            "name": test_channel_name,
            "channel_type": "public",
            "description": "Testing message duplication fix"
        }) as resp:
            if resp.status != 200:
                print(f"❌ Failed to create channel: {resp.status}")
                return
            channel_data = await resp.json()
            channel_id = channel_data['id']
            print(f"✅ Channel created: {channel_id}")
        
        # Send a test message
        test_message = f"Fix verification message at {datetime.now().strftime('%H:%M:%S.%f')}"
        print(f"\n2️⃣ Sending test message: {test_message}")
        
        async with session.post(f"{BASE_URL}/api/channels/{channel_id}/send", json={
            "sender": "COMMANDER_PRIME",
            "content": test_message
        }) as resp:
            if resp.status != 200:
                print(f"❌ Failed to send message: {resp.status}")
                error = await resp.text()
                print(f"   Error: {error}")
                return
            print("✅ Message sent successfully")
        
        # Wait for processing
        print("\n3️⃣ Waiting 3 seconds for message processing...")
        await asyncio.sleep(3)
        
        # Fetch messages
        print("\n4️⃣ Fetching messages to check for duplicates...")
        async with session.get(f"{BASE_URL}/api/channels/{channel_id}/messages?limit=20") as resp:
            if resp.status != 200:
                print(f"❌ Failed to fetch messages: {resp.status}")
                return
            
            data = await resp.json()
            messages = data.get('messages', [])
            
            print(f"✅ Found {len(messages)} total messages")
            
            # Check for duplicates
            commander_messages = [m for m in messages if m['sender'] == 'COMMANDER_PRIME' and test_message in m['content']]
            minion_messages = [m for m in messages if m['sender'] != 'COMMANDER_PRIME' and m['sender'] != 'system']
            
            print(f"\n📊 Analysis:")
            print(f"   - Commander messages with test content: {len(commander_messages)}")
            print(f"   - Minion responses: {len(minion_messages)}")
            
            if len(commander_messages) > 1:
                print(f"\n❌ DUPLICATION DETECTED: Found {len(commander_messages)} copies of the test message!")
                for i, msg in enumerate(commander_messages):
                    print(f"   Copy {i+1}: {msg['timestamp']} - {msg['content'][:50]}...")
            else:
                print("\n✅ NO DUPLICATION: Test message appears only once!")
            
            # Check minion responses
            if minion_messages:
                print(f"\n🤖 Minion Responses:")
                for msg in minion_messages[:3]:  # Show first 3
                    print(f"   [{msg['sender']}]: {msg['content'][:100]}...")
                    
                # Check for placeholder responses
                placeholder_count = sum(1 for m in minion_messages if "ADK integration needs some work" in m['content'])
                if placeholder_count > 0:
                    print(f"\n⚠️  WARNING: Found {placeholder_count} placeholder responses - ADK integration needs attention")
                else:
                    print("\n✅ No placeholder responses detected")
            
            # Final verdict
            print("\n" + "="*50)
            if len(commander_messages) == 1 and placeholder_count == 0:
                print("✅ ALL FIXES WORKING CORRECTLY!")
            else:
                issues = []
                if len(commander_messages) > 1:
                    issues.append("Message duplication still occurring")
                if placeholder_count > 0:
                    issues.append("ADK integration using placeholders")
                print(f"❌ ISSUES REMAIN: {', '.join(issues)}")

if __name__ == "__main__":
    print("🔧 MESSAGE DUPLICATION FIX VERIFICATION")
    print("Make sure backend is running on localhost:8000")
    print("This will create a test channel and verify fixes\n")
    
    try:
        asyncio.run(verify_fixes())
    except Exception as e:
        print(f"❌ Verification failed with error: {e}")
    
    print(f"\n✅ Verification completed at {datetime.now()}")
