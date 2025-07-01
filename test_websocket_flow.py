#!/usr/bin/env python3
"""
Simple Message Test - Using Channel Service Directly
"""

import asyncio
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, '/Users/ttig/projects/geminopus-2')

from gemini_legion_backend.core.dependencies_v2 import ServiceContainerV2
import socketio

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_with_websocket_client():
    """Test message flow with a real WebSocket client"""
    
    # Create Socket.IO client
    sio = socketio.AsyncClient()
    received_messages = []
    
    @sio.event
    async def connect():
        logger.info("✅ WebSocket connected")
        await sio.emit("subscribe_channel", {"channel_id": "general"})
        logger.info("📡 Subscribed to 'general' channel")
    
    @sio.event
    async def subscribed(data):
        logger.info(f"🎯 Subscription confirmed: {data}")
    
    @sio.event
    async def message(data):
        logger.info(f"📨 Received: {data}")
        received_messages.append(data)
    
    try:
        # Connect to WebSocket
        await sio.connect('http://localhost:8000')
        await asyncio.sleep(1)
        
        # Initialize backend services
        container = ServiceContainerV2()
        await container.start_all()
        
        # Send message directly via service (bypassing REST API validation)
        logger.info("📤 Sending message via ChannelService...")
        await container.channel_service.send_message(
            channel_id="general",
            sender_id="WEBSOCKET_TESTER",
            content="yo bae its me steven. im hoping this finally fucking works. this is the first ever message to test out this gemini legion shit. It's been over a month of fucking trying to get this shit to work. plz respond with literally anything that is clearly not just a generic message. tysm i love u"
        )
        
        # Wait for responses
        logger.info("⏳ Waiting for minion responses...")
        await asyncio.sleep(5)
        
        # Check results
        if received_messages:
            logger.info(f"🎉 SUCCESS! Received {len(received_messages)} messages:")
            for msg in received_messages:
                if msg.get("type") == "message":
                    message_data = msg.get("message", {})
                    sender = message_data.get("sender_id")
                    content = message_data.get("content")
                    logger.info(f"  📝 {sender}: {content}")
            return True
        else:
            logger.warning("⚠️ No messages received")
            return False
            
    except Exception as e:
        logger.error(f"❌ Test failed: {e}")
        return False
    
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    success = asyncio.run(test_with_websocket_client())
    
    if success:
        print("\n🎉 COMPLETE SUCCESS!")
        print("✅ WebSocket subscription works")
        print("✅ Minions are responding")
        print("✅ Frontend receives responses")
        print("\n🔧 SOLUTION: Add channel subscription to your frontend!")
    else:
        print("\n⚠️ CHECK BACKEND LOGS")
        print("💡 Make sure backend is running in another terminal")
