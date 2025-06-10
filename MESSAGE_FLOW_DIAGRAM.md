# Message Flow Comparison

## Current BROKEN Flow (Multiple Paths = Duplication)

```
User sends message via API
         |
         v
   ChannelService.send_message()
         |
         +------------------+------------------+
         |                  |                  |
         v                  v                  v
  comm_system.broadcast  _notify_active     (Sometimes also
  (Path 1)               minions            WebSocket direct)
         |                  |                  |
         v                  v                  v
  MessageRouter.route    Direct Queue      connection_manager
         |               Addition             |
         v                  |                  |
  _websocket_callback       v                  |
         |               Minion processes      |
         v               & responds            |
  WebSocket broadcast       |                  |
         |                  v                  |
         |               Another message       |
         |               through system        |
         |                  |                  |
         v                  v                  v
     [MESSAGE 1]       [MESSAGE 2]        [MESSAGE 3]
     
Result: SAME MESSAGE APPEARS 2-3 TIMES!
```

## Correct ADK Flow (Single Path = No Duplication)

```
User sends message via API
         |
         v
   ChannelService.send_message()
         |
         v
   Persist to Database
         |
         v
   event_bus.emit("channel.message", {...})
         |
         +------------------+
         |                  |
         v                  v
  WebSocket Handler    Minion Subscriber
  (broadcasts to GUI)  (if subscribed)
         |                  |
         |                  v
         |              agent.predict()
         |                  |
         |                  v
         |              Response via Tool
         |                  |
         v                  v
    [MESSAGE ONCE]    [RESPONSE ONCE]
    
Result: Each message appears EXACTLY ONCE!
```

## The Key Differences

### BROKEN (Current):
- Multiple parallel paths for the same message
- Direct queue manipulation
- Custom message routing
- Minions using fallback responses
- Turn-taking disabled

### CORRECT (Target):
- Single event-driven path
- ADK event bus handles distribution
- Subscribers choose to respond
- Minions use proper predict()
- ADK handles rate limiting

## Why It's Broken

1. **Trying to be "helpful"** by notifying minions directly AND through broadcast
2. **Not trusting ADK** to handle message distribution
3. **Building custom systems** instead of using ADK's built-in capabilities
4. **Fallback hacks** instead of proper integration

## The Fix

1. **Emergency**: Disable all paths except WebSocket broadcast
2. **Short-term**: Single event emission per message
3. **Long-term**: Full ADK event-driven architecture
