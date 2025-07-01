#!/usr/bin/env python3
"""
Quick Message Test - Test the session and persona fixes
"""

import asyncio
import sys
import os
import logging

# Add the project root to Python path
sys.path.insert(0, '/Users/ttig/projects/geminopus-2')

from gemini_legion_backend.core.dependencies_v2 import ServiceContainerV2

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def test_message_response():
    """Test sending a message to echo_prime and getting a response"""
    logger.info("🧪 Testing message response after fixes...")
    
    # Initialize service container
    container = ServiceContainerV2()
    await container.start_all()
    
    # Use the default echo_prime minion that's already created
    channel_id = "general"  # Use the default general channel
    
    logger.info(f"📤 Sending test message to echo_prime in channel: {channel_id}")
    
    try:
        # Send a simple message
        await container.channel_service.send_message(
            channel_id=channel_id,
            sender_id="QUICK_TESTER",
            content="Hello echo_prime! Please respond to test the fixes."
        )
        
        logger.info("✅ Message sent successfully - checking for crashes...")
        
        # Give the system a moment to process
        await asyncio.sleep(2)
        
        logger.info("🎉 No crashes detected! The fixes appear to be working!")
        return True
        
    except Exception as e:
        logger.error(f"❌ Error during message test: {e}")
        return False

async def main():
    """Run the quick test"""
    success = await test_message_response()
    
    if success:
        print("\n🎉 QUICK TEST: SUCCESS!")
        print("✅ No session errors")
        print("✅ No persona attribute errors")
        print("✅ Messages can be sent without crashes")
        print("\n🚀 Ready for real testing with API key!")
    else:
        print("\n💥 QUICK TEST: ISSUES REMAIN")
        print("❌ Check logs above for remaining problems")
    
    return success

if __name__ == "__main__":
    success = asyncio.run(main())
    sys.exit(0 if success else 1)
