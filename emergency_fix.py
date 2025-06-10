#!/usr/bin/env python3
"""
Emergency fix to stop message duplication
Run this to apply the nuclear option - disable all the broken shit
"""

import os
import sys

def apply_emergency_fixes():
    """Apply emergency fixes to stop duplication"""
    
    print("🚨 APPLYING EMERGENCY FIXES")
    print("=" * 50)
    
    # Fix 1: Gut the send_message method in channel_service.py
    print("\n1️⃣ Fixing channel_service.py send_message...")
    channel_service_path = "/Users/ttig/downloads/geminopus-branch/gemini_legion_backend/core/application/services/channel_service.py"
    
    # Read the file
    with open(channel_service_path, 'r') as f:
        content = f.read()
    
    # Find and replace the send_message method
    new_send_message = '''    async def send_message(
        self,
        channel_id: str,
        sender_id: str,
        content: str,
        message_type: str = "text",
        metadata: Optional[Dict[str, Any]] = None,
        parent_message_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        EMERGENCY FIX: Single path message sending only
        """
        channel = self.active_channels.get(channel_id)
        if not channel:
            raise ValueError(f"Channel {channel_id} not found")
        
        # Create message
        message = Message(
            message_id=f"{channel_id}_{datetime.now().timestamp()}",
            channel_id=channel_id,
            sender_id=sender_id,
            content=content,
            message_type=MessageType(message_type),
            timestamp=datetime.now(),
            metadata=metadata or {},
            parent_message_id=parent_message_id
        )
        
        # Add to buffer for persistence
        async with self._buffer_lock:
            self.message_buffer.append(message)
        
        # Update channel activity
        channel.last_activity = datetime.now()
        channel.message_count += 1
        
        # ONLY broadcast via WebSocket - single path
        message_dict = self._message_to_dict(message)
        await connection_manager.broadcast_service_event(
            "message_sent",
            {"channel_id": channel_id, "message": message_dict}
        )
        
        logger.debug(f"Message sent to {channel_id} by {sender_id} - SINGLE PATH")
        
        return message_dict'''
    
    # Find the method and replace it
    import re
    pattern = r'async def send_message\([\s\S]*?return self\._message_to_dict\(message\)'
    
    if re.search(pattern, content):
        content = re.sub(pattern, new_send_message, content)
        
        # Write back
        with open(channel_service_path, 'w') as f:
            f.write(content)
        print("✅ Fixed send_message method")
    else:
        print("❌ Could not find send_message method to replace")
    
    # Fix 2: Disable minion message processing
    print("\n2️⃣ Disabling minion auto-responses...")
    minion_agent_path = "/Users/ttig/downloads/geminopus-branch/gemini_legion_backend/core/infrastructure/adk/agents/minion_agent.py"
    
    with open(minion_agent_path, 'r') as f:
        content = f.read()
    
    # Find _process_messages_loop and disable it
    process_loop_disabled = '''    async def _process_messages_loop(self):
        """EMERGENCY DISABLED - Moving to event-driven architecture"""
        logger.warning(f"Message processing loop disabled for {self.minion_id} - refactoring in progress")
        return  # Disabled until proper ADK integration'''
    
    pattern = r'async def _process_messages_loop\(self\):[\s\S]*?except Exception as e:[\s\S]*?logger\.error.*?\n'
    
    if re.search(pattern, content):
        content = re.sub(pattern, process_loop_disabled + '\n', content)
        
        with open(minion_agent_path, 'w') as f:
            f.write(content)
        print("✅ Disabled minion auto-responses")
    else:
        print("⚠️  Could not find _process_messages_loop to disable")
    
    # Fix 3: Add a test endpoint
    print("\n3️⃣ Adding simple test endpoint...")
    channels_path = "/Users/ttig/downloads/geminopus-branch/gemini_legion_backend/api/rest/endpoints/channels.py"
    
    with open(channels_path, 'r') as f:
        content = f.read()
    
    # Add the test endpoint if not already there
    test_endpoint = '''

@router.post("/test_simple", response_model=Dict[str, Any])
async def test_simple_message(channel_id: str, content: str):
    """Simple test endpoint that only does WebSocket broadcast"""
    import uuid
    from datetime import datetime
    
    message_dict = {
        "message_id": str(uuid.uuid4()),
        "channel_id": channel_id,
        "sender_id": "TEST_USER",
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "message_type": "chat"
    }
    
    await connection_manager.broadcast_service_event(
        "message_sent",
        {"channel_id": channel_id, "message": message_dict}
    )
    
    return {"success": True, "message": message_dict}'''
    
    if "@router.post(\"/test_simple\"" not in content:
        # Add before the last function or at the end
        content = content.rstrip() + test_endpoint + '\n'
        
        with open(channels_path, 'w') as f:
            f.write(content)
        print("✅ Added test endpoint")
    else:
        print("ℹ️  Test endpoint already exists")
    
    print("\n" + "="*50)
    print("✅ EMERGENCY FIXES APPLIED")
    print("\nRestart the backend for changes to take effect:")
    print("  1. Kill the current process")
    print("  2. cd /Users/ttig/downloads/geminopus-branch")
    print("  3. python3 -m gemini_legion_backend.main")
    print("\nThen test with:")
    print("  curl -X POST http://localhost:8000/api/channels/test_simple \\")
    print("    -H 'Content-Type: application/json' \\")
    print("    -d '{\"channel_id\": \"general\", \"content\": \"Test message\"}'")

if __name__ == "__main__":
    print("🔧 GEMINI LEGION EMERGENCY FIX")
    print("This will disable the broken parts to stop duplication\n")
    
    response = input("Apply emergency fixes? (y/n): ")
    if response.lower() == 'y':
        apply_emergency_fixes()
    else:
        print("Cancelled")
