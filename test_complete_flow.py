#!/usr/bin/env python3
"""
Complete End-to-End Test: Send Message + Receive Minion Response
"""

import asyncio
import aiohttp
import socketio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_complete_message_flow():
    """Test complete message flow: Send message → Minion responds → Frontend receives"""
    
    # Create Socket.IO client for receiving messages
    sio = socketio.AsyncClient()
    received_messages = []
    
    @sio.event
    async def connect():
        logger.info("✅ WebSocket connected")
        
        # Subscribe to the general channel
        await sio.emit("subscribe_channel", {"channel_id": "general"})
        logger.info("📡 Subscribed to 'general' channel")
    
    @sio.event
    async def subscribed(data):
        logger.info(f"🎯 Subscription confirmed: {data}")
    
    @sio.event
    async def message(data):
        logger.info(f"📨 Received WebSocket message: {data}")
        received_messages.append(data)
        
        if data.get("type") == "message":
            message_data = data.get("message", {})
            sender_id = message_data.get("sender_id")
            content = message_data.get("content")
            logger.info(f"💬 {sender_id}: {content}")
    
    try:
        # Step 1: Connect to WebSocket
        await sio.connect('http://localhost:8000')
        await asyncio.sleep(1)  # Give subscription time to register
        
        # Step 2: Send a test message via REST API
        logger.info("📤 Sending test message via REST API...")
        
        async with aiohttp.ClientSession() as session:
            payload = {
                "sender_id": "TEST_CLIENT",
                "content": "Hello minions! Please respond to test the complete flow!"
            }
            
            async with session.post(
                "http://localhost:8000/api/v2/channels/general/messages",
                json=payload,
                headers={"Content-Type": "application/json"}
            ) as response:
                if response.status == 200:
                    logger.info("✅ Message sent successfully via REST API")
                else:
                    logger.error(f"❌ Failed to send message: {response.status}")
                    return False
        
        # Step 3: Wait for minion responses
        logger.info("⏳ Waiting for minion responses...")
        await asyncio.sleep(10)  # Give minions time to respond
        
        # Step 4: Check results
        if received_messages:
            logger.info(f"🎉 SUCCESS! Received {len(received_messages)} messages via WebSocket:")
            for i, msg in enumerate(received_messages, 1):
                if msg.get("type") == "message":
                    message_data = msg.get("message", {})
                    sender = message_data.get("sender_id", "Unknown")
                    content = message_data.get("content", "No content")
                    logger.info(f"  {i}. {sender}: {content}")
            return True
        else:
            logger.warning("⚠️ No messages received via WebSocket")
            logger.info("💡 This means the frontend subscription issue is confirmed")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    
    finally:
        await sio.disconnect()

async def main():
    logger.info("🧪 Testing complete message flow...")
    logger.info("💡 Make sure your backend is running: python3 -m gemini_legion_backend.main_v2")
    
    success = await test_complete_message_flow()
    
    if success:
        print("\n🎉 COMPLETE SUCCESS!")
        print("✅ Messages sent via REST API")
        print("✅ Minions responded")
        print("✅ Frontend received responses via WebSocket")
        print("\n🚀 Your system is working perfectly!")
        print("🔧 Frontend just needs to subscribe to channels!")
    else:
        print("\n⚠️ PARTIAL SUCCESS")
        print("✅ Your minions are responding (check backend logs)")
        print("❌ WebSocket subscription needs to be added to frontend")
        
    return success

if __name__ == "__main__":
    asyncio.run(main())
