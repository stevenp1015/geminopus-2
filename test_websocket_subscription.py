#!/usr/bin/env python3
"""
Test WebSocket Subscription and Message Flow
"""

import asyncio
import socketio
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_websocket_message_flow():
    """Test WebSocket subscription and message reception"""
    
    # Create Socket.IO client
    sio = socketio.AsyncClient()
    
    @sio.event
    async def connect():
        logger.info("✅ Connected to WebSocket server")
        
        # Subscribe to the general channel
        await sio.emit("subscribe_channel", {"channel_id": "general"})
        logger.info("📡 Subscribed to 'general' channel")
    
    @sio.event
    async def subscribed(data):
        logger.info(f"🎯 Subscription confirmed: {data}")
    
    @sio.event
    async def message(data):
        logger.info(f"📨 Received message: {data}")
        
        # Extract message details
        if data.get("type") == "message":
            channel_id = data.get("channel_id")
            message_data = data.get("message", {})
            sender_id = message_data.get("sender_id")
            content = message_data.get("content")
            
            logger.info(f"💬 From {sender_id} in {channel_id}: {content}")
    
    @sio.event
    async def disconnect():
        logger.info("❌ Disconnected from WebSocket server")
    
    try:
        # Connect to the server
        await sio.connect('http://localhost:8000')
        
        # Keep connection alive for a bit
        logger.info("🔄 Listening for messages for 30 seconds...")
        logger.info("💡 Now send a message from your frontend to test!")
        
        await asyncio.sleep(30)
        
    except Exception as e:
        logger.error(f"Connection failed: {e}")
        logger.info("💡 Make sure your backend is running: python3 -m gemini_legion_backend.main_v2")
    
    finally:
        await sio.disconnect()

if __name__ == "__main__":
    asyncio.run(test_websocket_message_flow())
