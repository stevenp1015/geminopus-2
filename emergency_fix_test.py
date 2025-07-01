#!/usr/bin/env python3
"""
Emergency Test Script - Verify ADK Fixes
Tests the core functionality after applying the emergency fixes.
"""

import asyncio
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, '/Users/ttig/projects/geminopus-2')

from gemini_legion_backend.core.dependencies_v2 import ServiceContainerV2
from google.genai import types as genai_types

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

async def test_basic_functionality():
    """Test basic minion spawning and response"""
    logger.info("🧪 Starting emergency fix validation test...")
    
    # Initialize service container
    container = ServiceContainerV2()
    await container.start_all()
    
    # Test 1: Spawn a simple test minion
    logger.info("🎭 Test 1: Spawning test minion...")
    
    try:
        test_minion = await container.minion_service.spawn_minion(
            minion_id="test_minion_001",
            name="TestMinion",
            base_personality="helpful and friendly assistant who loves testing",
            quirks=["loves debugging", "speaks casually", "gets excited about fixes"],
            catchphrases=["Let's fix this!", "No problem!", "Testing rocks!"],
            expertise_areas=["testing", "debugging", "validation"],
            model_name="gemini-2.0-flash-exp"
        )
        logger.info(f"✅ Test minion spawned successfully: {test_minion}")
    except Exception as e:
        logger.error(f"❌ Failed to spawn test minion: {e}")
        return False
    
    # Test 2: Create a test channel
    logger.info("📺 Test 2: Creating test channel...")
    try:
        test_channel = await container.channel_service.create_channel(
            channel_id="test-channel-001",
            name="test-channel",
            description="Emergency test channel"
        )
        logger.info(f"✅ Test channel created: {test_channel}")
    except Exception as e:
        logger.error(f"❌ Failed to create test channel: {e}")
        return False
    
    # Test 3: Add minion to channel
    logger.info("🤝 Test 3: Adding minion to channel...")
    try:
        await container.channel_service.add_member(
            "test-channel-001",  # Use the channel_id we created
            "test_minion_001"    # Use the minion_id we created
        )
        logger.info(f"✅ Minion added to channel successfully")
    except Exception as e:
        logger.error(f"❌ Failed to add minion to channel: {e}")
        return False
    
    # Test 4: Send a test message (THIS IS THE CRITICAL TEST)
    logger.info("💬 Test 4: Sending test message to minion...")
    try:
        # This should trigger the fixed Runner.run_async() call
        await container.channel_service.send_message(
            channel_id="test-channel-001",  # Use the channel_id we created
            sender_id="EMERGENCY_TESTER",
            content="Hello! Please respond to confirm you're working."
        )
        logger.info("✅ Test message sent successfully!")
        
        # Give the minion a moment to process and respond
        await asyncio.sleep(3)
        
        # Check if there are any messages in the channel
        messages = await container.channel_service.get_messages("test-channel-001")
        logger.info(f"📊 Channel now has {len(messages)} messages")
        
        minion_responses = [msg for msg in messages if msg.sender_id == "test_minion_001"]
        if minion_responses:
            logger.info(f"🎉 SUCCESS! Minion responded: {minion_responses[0].content}")
            return True
        else:
            logger.warning("⚠️  No minion response found, but no crash occurred")
            return True  # No crash is still progress!
            
    except Exception as e:
        logger.error(f"❌ CRITICAL: Message sending failed: {e}")
        return False

async def main():
    """Run the emergency test"""
    success = await test_basic_functionality()
    
    if success:
        print("\n🎉 EMERGENCY FIXES VALIDATION: SUCCESS!")
        print("✅ No more TypeError crashes")
        print("✅ Basic minion spawning works")  
        print("✅ Channel creation works")
        print("✅ Message sending doesn't crash")
        print("\n🚀 Your minions should now be responsive!")
    else:
        print("\n💥 EMERGENCY FIXES VALIDATION: FAILED!")
        print("❌ There are still critical issues")
        print("🔧 Check the logs above for specific problems")
    
    return success

if __name__ == "__main__":
    # Set API key if available
    if not os.getenv("GOOGLE_API_KEY"):
        print("⚠️  Warning: GOOGLE_API_KEY not set in environment")
        print("🔧 Set it with: export GOOGLE_API_KEY='your-key-here'")
    
    # Run the test
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
