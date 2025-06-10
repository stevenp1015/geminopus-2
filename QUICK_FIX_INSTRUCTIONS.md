# Quick Fix for Message Duplication

## Step 1: Fix channel_service.py

In `/gemini_legion_backend/core/application/services/channel_service.py`, find the `send_message` method (around line 430) and comment out the duplicate notification:

```python
async def send_message(
    self,
    channel_id: str,
    sender_id: str,
    content: str,
    message_type: str = "text",
    metadata: Optional[Dict[str, Any]] = None,
    parent_message_id: Optional[str] = None
) -> Dict[str, Any]:
    # ... existing code ...
    
    # Single broadcast through communication system (which triggers WebSocket via callback)
    await self.comm_system.broadcast_message(
        channel_id,
        sender_id,
        content,
        metadata
    )
    
    # COMMENT OUT THIS LINE TO FIX DUPLICATION:
    # await self._notify_active_minions(channel_id, message)
    
    logger.debug(f"Message sent to {channel_id} by {sender_id}")
    
    # Return the message dict (WebSocket broadcast handled by comm_system callback)
    return self._message_to_dict(message)
```

## Step 2: Re-enable Turn Taking

In `/gemini_legion_backend/core/infrastructure/messaging/communication_system.py`, find the `send_message` method in `ConversationalLayer` (around line 140) and re-enable turn-taking:

```python
async def send_message(
    self,
    from_minion: str,
    to_channel: str,
    message: str,
    personality_modifiers: Optional[Dict[str, Any]] = None
) -> bool:
    """
    Send a conversational message with personality
    
    Returns:
        True if message sent, False if turn denied
    """
    # Apply turn-taking logic - RE-ENABLE THIS:
    can_speak = await self.turn_taking_engine.request_turn(
        from_minion, to_channel
    )
    
    if not can_speak:
        # Could queue or wait
        return False
    # Remove this line: can_speak = True  # Always allow speaking for testing
    
    try:
        # Route message
        msg = ConversationalMessage(
            sender=from_minion,
            channel=to_channel,
            content=message,
            personality_hints=personality_modifiers
        )
        await self.message_router.route(msg)
        
        return True
    finally:
        # Always release turn - RE-ENABLE THIS:
        self.turn_taking_engine.release_turn(from_minion, to_channel)
        # Remove: pass
```

## Step 3: Add Message Deduplication (Optional but Recommended)

Add this to `channel_service.py` in the `_websocket_broadcaster_callback` method:

```python
# Add at the beginning of the class
def __init__(self, ...):
    # ... existing init code ...
    # Add deduplication cache
    self._recent_messages = {}  # key: hash(content+sender+channel), value: timestamp
    self._dedup_window_seconds = 2.0

# In _websocket_broadcaster_callback method:
async def _websocket_broadcaster_callback(self, routed_message: ConversationalMessage):
    """
    Callback for MessageRouter with deduplication
    """
    try:
        # Create deduplication key
        dedup_key = f"{routed_message.channel}:{routed_message.sender}:{hash(routed_message.content)}"
        
        # Check if we've seen this message recently
        now = datetime.now()
        if dedup_key in self._recent_messages:
            last_seen = self._recent_messages[dedup_key]
            if (now - last_seen).total_seconds() < self._dedup_window_seconds:
                logger.debug(f"Duplicate message detected, skipping: {dedup_key}")
                return
        
        # Update deduplication cache
        self._recent_messages[dedup_key] = now
        
        # Clean old entries
        self._recent_messages = {
            k: v for k, v in self._recent_messages.items()
            if (now - v).total_seconds() < 60  # Keep 1 minute of history
        }
        
        # ... rest of the existing method ...
```

## Step 4: Restart the Backend

After making these changes:

```bash
# Kill the current backend process
# Then restart it
cd /Users/ttig/downloads/geminopus-branch
python3 -m gemini_legion_backend.main
```

## Expected Results

After applying these fixes:
1. Messages should only appear ONCE in channels
2. Minion responses should be properly throttled
3. No more duplicate WebSocket broadcasts
4. The test script should pass cleanly

## Testing

Run the test script again:
```bash
python3 test_message_flow.py
```

You should see:
- Single message sent
- Single response from minions (if any)
- No duplicates in the message list
